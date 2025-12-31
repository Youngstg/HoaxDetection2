import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const newsAPI = {
  getAllNews: async (limit = 50) => {
    const response = await api.get(`/news/?limit=${limit}`);
    return response.data;
  },

  getNewsById: async (id) => {
    const response = await api.get(`/news/${id}`);
    return response.data;
  },

  fetchRSS: async () => {
    const response = await api.post('/news/fetch-rss');
    return response.data;
  },
};

export default api;
