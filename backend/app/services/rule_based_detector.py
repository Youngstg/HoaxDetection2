"""
Rule-based Hoax Detector (Temporary Solution)
Menggunakan pattern matching dan keyword analysis untuk deteksi hoax sementara
sambil menunggu model ML di-train.
"""

import re
from typing import Dict, Tuple
from app.models import HoaxPrediction


class RuleBasedHoaxDetector:
    def __init__(self):
        # Keywords yang sering muncul di hoax
        self.hoax_keywords = [
            # Sensasional
            "wajib share", "wajib tahu", "viral", "breaking news",
            "segera sebarkan", "harus dibaca", "jangan sampai",

            # Clickbait
            "mengejutkan", "mencengangkan", "tidak akan percaya",
            "ternyata", "rahasia", "fakta mengejutkan",

            # Klaim absolut
            "100% terbukti", "dijamin", "pasti sembuh", "ampuh",
            "terbukti ilmiah", "tanpa efek samping",

            # Provokasi
            "bahaya", "awas", "hati-hati", "jangan",
            "menyesatkan", "konspirasi",

            # Sumber tidak jelas
            "kata dokter", "menurut penelitian", "ahli mengatakan",
            "berdasarkan info", "kabar terbaru",
        ]

        # Trusted media sources (media terpercaya)
        self.trusted_sources = [
            "kompas.com", "tempo.co", "detik.com", "antaranews.com",
            "cnn.com", "bbc.com", "liputan6.com", "tribunnews.com",
            "republika.co.id", "mediaindonesia.com", "suara.com",
            "cnnindonesia.com", "viva.co.id", "merdeka.com"
        ]

        # Hoax indicators patterns
        self.hoax_patterns = [
            r'\b(WAJIB|HARUS|SEGERA)\s+(SHARE|TAHU|BACA|SEBARKAN)\b',
            r'\b\d+%\s+(terbukti|ampuh|efektif)\b',
            r'\b(rahasia|fakta)\s+(tersembunyi|mengejutkan|mencengangkan)\b',
            r'\b(tanpa|bebas)\s+efek\s+samping\b',
            r'!!!+',  # Multiple exclamation marks
            r'\bDIBANNED\b|\bDICENSOR\b|\bDISEMBUNYIKAN\b',
        ]

    def analyze_text(self, text: str, source: str = "") -> Dict[str, float]:
        """
        Analyze text untuk berbagai indikator hoax

        Returns:
            Dict dengan score untuk setiap kategori
        """
        text_lower = text.lower()

        scores = {
            "keyword_score": 0.0,
            "pattern_score": 0.0,
            "source_score": 0.0,
            "caps_score": 0.0,
            "punctuation_score": 0.0
        }

        # 1. Keyword matching
        keyword_matches = sum(1 for keyword in self.hoax_keywords if keyword in text_lower)
        scores["keyword_score"] = min(keyword_matches * 0.1, 1.0)

        # 2. Pattern matching
        pattern_matches = sum(1 for pattern in self.hoax_patterns if re.search(pattern, text, re.IGNORECASE))
        scores["pattern_score"] = min(pattern_matches * 0.15, 1.0)

        # 3. Source credibility
        if source:
            source_lower = source.lower()
            is_trusted = any(trusted in source_lower for trusted in self.trusted_sources)
            scores["source_score"] = 0.0 if is_trusted else 0.3

        # 4. Excessive capitalization
        if len(text) > 0:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.3:  # More than 30% uppercase
                scores["caps_score"] = min(caps_ratio, 1.0)

        # 5. Excessive punctuation
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            scores["punctuation_score"] = min(exclamation_count * 0.1, 1.0)

        return scores

    def predict(self, text: str, source: str = "") -> HoaxPrediction:
        """
        Predict apakah text adalah hoax atau non-hoax

        Args:
            text: Konten berita
            source: Sumber berita (URL atau nama media)

        Returns:
            HoaxPrediction object
        """
        # Analyze text
        scores = self.analyze_text(text, source)

        # Calculate weighted score
        weights = {
            "keyword_score": 0.3,
            "pattern_score": 0.25,
            "source_score": 0.25,
            "caps_score": 0.1,
            "punctuation_score": 0.1
        }

        hoax_probability = sum(scores[key] * weights[key] for key in weights)

        # Threshold: 0.4
        # Jika hoax_probability > 0.4, maka dianggap hoax
        if hoax_probability > 0.4:
            label = "hoax"
            confidence = min(hoax_probability, 0.95)  # Max 95% confidence for rule-based
        else:
            label = "non-hoax"
            confidence = min(1.0 - hoax_probability, 0.95)

        return HoaxPrediction(
            label=label,
            confidence=round(confidence, 4)
        )

    def get_explanation(self, text: str, source: str = "") -> Dict:
        """
        Memberikan penjelasan detail kenapa dianggap hoax/non-hoax
        """
        scores = self.analyze_text(text, source)
        prediction = self.predict(text, source)

        return {
            "prediction": prediction.label,
            "confidence": prediction.confidence,
            "detailed_scores": scores,
            "indicators": {
                "high_risk": [k for k, v in scores.items() if v > 0.5],
                "medium_risk": [k for k, v in scores.items() if 0.2 < v <= 0.5],
                "low_risk": [k for k, v in scores.items() if v <= 0.2]
            }
        }


# Global instance
rule_based_detector = RuleBasedHoaxDetector()
