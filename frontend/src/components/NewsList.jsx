import React from 'react';
import NewsCard from './NewsCard';

const NewsList = ({ news, loading, error }) => {
  if (loading) {
    return <div className="loading">Memuat berita...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!news || news.length === 0) {
    return (
      <div className="error" style={{ backgroundColor: '#fff3cd', color: '#856404' }}>
        Tidak ada berita yang tersedia. Klik tombol "Ambil Berita Baru" untuk memulai.
      </div>
    );
  }

  return (
    <div className="news-grid">
      {news.map((item) => (
        <NewsCard key={item.id} news={item} />
      ))}
    </div>
  );
};

export default NewsList;
