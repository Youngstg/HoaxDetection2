import React from 'react';

const NewsCard = ({ news }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Tanggal tidak tersedia';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return 'Tanggal tidak valid';
    }
  };

  const getConfidencePercentage = (confidence) => {
    return (confidence * 100).toFixed(1);
  };

  return (
    <div className={`news-card ${news.hoax_label || ''}`}>
      <h3>{news.title}</h3>

      <div className="news-meta">
        <span>{news.source || 'Sumber tidak diketahui'}</span>
        <span className={`hoax-badge ${news.hoax_label || ''}`}>
          {news.hoax_label === 'hoax' ? 'Hoax' : 'Non-Hoax'}
        </span>
      </div>

      <p className="news-content">
        {news.content?.substring(0, 200)}
        {news.content?.length > 200 ? '...' : ''}
      </p>

      {news.confidence && (
        <div className="confidence">
          <span className="confidence-label">Tingkat Keyakinan: </span>
          <span>{getConfidencePercentage(news.confidence)}%</span>
        </div>
      )}

      <div style={{ marginTop: '15px', fontSize: '0.85em', color: '#7f8c8d' }}>
        {formatDate(news.published_time || news.created_at)}
      </div>

      <a
        href={news.link}
        target="_blank"
        rel="noopener noreferrer"
        className="read-more"
      >
        Baca Selengkapnya →
      </a>
    </div>
  );
};

export default NewsCard;
