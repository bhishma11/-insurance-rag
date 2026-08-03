// src/services/auth.ts
import axios from 'axios';

// ✅ Use environment variable with fallback to localhost
// ✅ Include /api in the base URL
const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8001') + '/api';

export interface User {
  user_id: string;
  email: string;
  name: string;
  company: string;
  status: 'PENDING' | 'ACTIVE' | 'REJECTED';
}

export interface LoginResponse {
  success: boolean;
  token: string;
  user: User;
}

export interface SignupResponse {
  success: boolean;
  user_id: string;
  status: string;
  message: string;
}

const authApi = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export const authService = {
  signup: async (data: { name: string; email: string; company?: string }) => {
    const response = await authApi.post<SignupResponse>('/auth/signup', data);
    return response.data;
  },

  login: async (data: { email: string; password: string }) => {
    const response = await authApi.post<LoginResponse>('/auth/login', data);
    if (response.data.success) {
      console.log('🔑 Storing token:', response.data.token);
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  // ✅ FIX: Redirect to '/' instead of '/login'
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';  // ✅ This fixes the 404!
  },

  getCurrentUser: (): User | null => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  isAuthenticated: (): boolean => {
    const token = localStorage.getItem('token');
    console.log('🔑 Token exists:', !!token);
    return !!token;
  },
};

// Add token to all requests
authApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default authApi;