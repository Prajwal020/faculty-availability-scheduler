import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { ApiErrorResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach token
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: normalize errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    if (error.response) {
      // 401 Unauthorized: clear token
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        // If not already on /login, redirect
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }

      // Return normalized error data if available
      const errorData = error.response.data?.error;
      if (errorData) {
        return Promise.reject(errorData);
      }
    }

    return Promise.reject({
      code: 'NETWORK_ERROR',
      message: error.message || 'A network error occurred. Please try again.',
    });
  }
);
