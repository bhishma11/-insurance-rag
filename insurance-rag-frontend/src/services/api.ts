// src/services/api.ts
import axios from 'axios';
import { ChatRequest, ChatResponse, DashboardStats, AnalyticsStats } from '../types';

// ✅ Use environment variable with fallback to localhost
// ✅ Include /api in the base URL
const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8001') + '/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const api = {
  // ============ Chat Endpoints ============
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/chat', request);
    return response.data;
  },

  // ============ Premium Calculator ============
  calculatePremium: async (age: number, carValue: number, deductible: number) => {
    const response = await apiClient.post('/premium/calculate', {
      age,
      car_value: carValue,
      deductible
    });
    return response.data;
  },

  // ============ Session Management ============
  getSessions: async () => {
    const response = await apiClient.get('/sessions');
    return response.data;
  },

  getHistory: async (sessionId: string) => {
    const response = await apiClient.get(`/history/${sessionId}`);
    return response.data;
  },

  deleteSession: async (sessionId: string) => {
    const response = await apiClient.delete(`/sessions/${sessionId}`);
    return response.data;
  },

  // ============ Document Intelligence ============
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getSupportedFormats: async () => {
    const response = await apiClient.get('/documents/supported-formats');
    return response.data;
  },

  classifyDocument: async (text: string) => {
    const response = await apiClient.post('/documents/classify', { text });
    return response.data;
  },

  // ============ Vision Endpoints ============
  analyzeImage: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/vision/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    });
    return response.data;
  },

  classifyImage: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/vision/classify', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getVisionStatus: async () => {
    const response = await apiClient.get('/vision/status');
    return response.data;
  },

  // ============ Users ============
  getUsers: async () => {
    const response = await apiClient.get('/admin/users');
    return response.data;
  },

  // ============ Dashboard Endpoints ============
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get('/dashboard/stats');
    return response.data;
  },

  getGovernanceReports: async () => {
    const response = await apiClient.get('/dashboard/governance');
    return response.data;
  },

  getMCPAnalytics: async () => {
    const response = await apiClient.get('/dashboard/mcp');
    return response.data;
  },

  getSystemHealth: async () => {
    const response = await apiClient.get('/dashboard/health');
    return response.data;
  },

  getAuditLogs: async (limit: number = 100) => {
    const response = await apiClient.get(`/dashboard/audit?limit=${limit}`);
    return response.data;
  },

  // ============ Analytics Endpoints ============
  getAnalyticsStats: async (): Promise<AnalyticsStats> => {
    const response = await apiClient.get('/analytics/stats');
    return response.data;
  },

  getAnalyticsUsers: async () => {
    const response = await apiClient.get('/analytics/users');
    return response.data;
  },

  getAnalyticsFeatures: async () => {
    const response = await apiClient.get('/analytics/features');
    return response.data;
  },

  getAnalyticsQueries: async () => {
    const response = await apiClient.get('/analytics/queries');
    return response.data;
  },

  getAnalyticsCost: async () => {
    const response = await apiClient.get('/analytics/cost');
    return response.data;
  },

  getAnalyticsPerformance: async () => {
    const response = await apiClient.get('/analytics/performance');
    return response.data;
  },

  // ============ Health Check ============
  healthCheck: async () => {
    const response = await apiClient.get('/');
    return response.data;
  },
};

export default api;