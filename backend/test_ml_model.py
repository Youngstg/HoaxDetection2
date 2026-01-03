"""
Test script untuk ML model
"""
import os
os.environ["USE_ML_MODEL"] = "true"
os.environ["MODEL_PATH"] = "./hoax_model"

from app.services.hoax_detector import hoax_detector

# Test cases
test_cases = [
    {
        "title": "WAJIB SHARE! Fakta Mengejutkan yang Harus Anda Tahu!!!",
        "content": "Kabar mengejutkan! Menurut penelitian terbaru, ternyata ada rahasia tersembunyi yang tidak akan Anda percaya. SEGERA SEBARKAN sebelum terlambat! 100% terbukti ampuh tanpa efek samping.",
        "expected": "hoax"
    },
    {
        "title": "Presiden Umumkan Kebijakan Baru di Bidang Ekonomi",
        "content": "Jakarta - Presiden Indonesia mengumumkan kebijakan ekonomi baru dalam konferensi pers di Istana Negara hari ini. Kebijakan ini bertujuan untuk meningkatkan pertumbuhan ekonomi dan kesejahteraan masyarakat.",
        "expected": "non-hoax"
    },
    {
        "title": "BAHAYA! Minuman Ini Dapat Menyebabkan Kematian Mendadak",
        "content": "WAJIB TAHU!!! Info terbaru dari ahli kesehatan mengatakan bahwa minuman yang sering kita konsumsi ini ternyata sangat berbahaya. Dijamin pasti benar! Hati-hati jangan sampai menyesal!",
        "expected": "hoax"
    },
    {
        "title": "Bank Indonesia Tetapkan Suku Bunga Acuan 5.75 Persen",
        "content": "Bank Indonesia (BI) memutuskan untuk mempertahankan suku bunga acuan BI 7-Day Reverse Repo Rate (BI7DRR) sebesar 5,75 persen. Keputusan ini diambil dalam Rapat Dewan Gubernur BI.",
        "expected": "non-hoax"
    }
]

print("=" * 70)
print("Testing ML-based Hoax Detection Model")
print("=" * 70)

for i, test in enumerate(test_cases, 1):
    text = f"{test['title']}. {test['content']}"

    print(f"\n[Test {i}]")
    print(f"Title: {test['title']}")
    print(f"Expected: {test['expected']}")

    prediction = hoax_detector.predict(text)

    print(f"Predicted: {prediction.label}")
    print(f"Confidence: {prediction.confidence:.4f}")

    # Check if prediction matches expected
    match = "✓" if prediction.label == test['expected'] else "✗"
    print(f"Result: {match}")

print("\n" + "=" * 70)
print("Testing completed!")
print("=" * 70)
