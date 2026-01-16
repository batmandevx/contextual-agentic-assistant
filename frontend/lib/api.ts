/**
 * API client for backend communication
 */
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://r6vbn1vjpl.execute-api.us-east-1.amazonaws.com';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async () => {
    const response = await api.post('/api/auth/login');
    return response.data;
  },

  logout: async (token: string) => {
    const response = await api.post('/api/auth/logout', { token });
    return response.data;
  },

  getStatus: async (token: string) => {
    const response = await api.get(`/api/auth/status?token=${token}`);
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (message: string, conversationId?: string) => {
    const response = await api.post('/api/chat/message', {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  },

  getHistory: async (conversationId: string) => {
    const response = await api.get(`/api/chat/history/${conversationId}`);
    return response.data;
  },

  listConversations: async () => {
    const response = await api.get('/api/chat/conversations');
    return response.data;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await axios.get(`${API_URL}/api/health`);
  return response.data;
};

export default api;
