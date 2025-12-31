import React, { useState, useEffect } from 'react';
import NewsList from './components/NewsList';
import { newsAPI } from './services/api';

function App() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fetching, setFetching] = useState(false);

  const loadNews = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await newsAPI.getAllNews();
      setNews(data.news || []);
    } catch (err) {
      setError('Gagal memuat berita. Pastikan server backend berjalan.');
      console.error('Error loading news:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchNewNews = async () => {
    try {
      setFetching(true);
      setError(null);
      const result = await newsAPI.fetchRSS();
      alert(`${result.message}\nBerhasil: ${result.processed}, Dilewati: ${result.skipped}`);
      await loadNews();
    } catch (err) {
      setError('Gagal mengambil berita baru dari RSS.');
      console.error('Error fetching RSS:', err);
    } finally {
      setFetching(false);
    }
  };

  useEffect(() => {
    loadNews();
  }, []);

  return (
    <div className="App">
      <header className="header">
        <h1>Hoax Detection News App</h1>
        <p>Sistem Deteksi Berita Hoaks Indonesia</p>
      </header>

      <div className="container">
        <button
          className="refresh-button"
          onClick={fetchNewNews}
          disabled={fetching}
        >
          {fetching ? 'Mengambil berita...' : 'Ambil Berita Baru dari RSS'}
        </button>

        <NewsList news={news} loading={loading} error={error} />
      </div>
    </div>
  );
}

export default App;
