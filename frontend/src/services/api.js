/**
 * API service for backend communication
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: async (username, password) => {
    const response = await api.post('/auth/register', { username, password });
    return response.data;
  },

  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Chat endpoints
export const chatAPI = {
  getContacts: async () => {
    const response = await api.get('/api/contacts');
    return response.data;
  },

  addContact: async (userId) => {
    const response = await api.post(`/api/contacts/${userId}`);
    return response.data;
  },

  getChatHistory: async (userId, limit = 50, offset = 0) => {
    const response = await api.get(`/api/chat/${userId}`, {
      params: { limit, offset },
    });
    return response.data;
  },

  getRecentMessages: async (limit = 20) => {
    const response = await api.get('/api/messages/recent', {
      params: { limit },
    });
    return response.data;
  },

  searchUsers: async (query, limit = 10) => {
    const response = await api.get('/api/users/search', {
      params: { query, limit },
    });
    return response.data;
  },
};

// Verification endpoints
export const verificationAPI = {
  verifyMessage: async (messageId) => {
    const response = await api.get(`/api/verify/${messageId}`);
    return response.data;
  },

  notarizeMessage: async (messageId) => {
    const response = await api.post(`/api/notarize/${messageId}`);
    return response.data;
  },

  getHashInfo: async (messageId) => {
    const response = await api.get(`/api/hash-info/${messageId}`);
    return response.data;
  },
};

// WebSocket endpoints
export const websocketAPI = {
  getOnlineUsers: async () => {
    const response = await api.get('/ws/online');
    return response.data;
  },
};

export default api;
