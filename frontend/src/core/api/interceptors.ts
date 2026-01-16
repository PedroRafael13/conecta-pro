import type { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { apiClient, setAuthToken } from './client';
import type { ApiError } from '@core/types/api.types';

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: Error) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null): void => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
};

const getStoredToken = (): string | null => {
  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      const parsed = JSON.parse(authStorage);
      return parsed.state?.token || null;
    }
  } catch {
    // Ignore parse errors
  }
  return null;
};

const getRefreshToken = (): string | null => {
  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      const parsed = JSON.parse(authStorage);
      return parsed.state?.refreshToken || null;
    }
  } catch {
    // Ignore parse errors
  }
  return null;
};

export const setupInterceptors = (): void => {
  // Request interceptor - Add token to requests
  apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = getStoredToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error: AxiosError) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor - Handle errors and token refresh
  apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError<ApiError>) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean;
      };

      // Handle 401 Unauthorized
      if (error.response?.status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({
              resolve: (token: string) => {
                if (originalRequest.headers) {
                  originalRequest.headers.Authorization = `Bearer ${token}`;
                }
                resolve(apiClient(originalRequest));
              },
              reject,
            });
          });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        const refreshToken = getRefreshToken();

        if (!refreshToken) {
          isRefreshing = false;
          // Clear storage and redirect to login
          localStorage.removeItem('auth-storage');
          setAuthToken(null);
          window.location.href = '/login';
          return Promise.reject(error);
        }

        try {
          const response = await apiClient.post('/auth/refresh', {
            refresh_token: refreshToken,
          });

          const { token } = response.data;

          // Update token in storage
          const authStorage = localStorage.getItem('auth-storage');
          if (authStorage) {
            const parsed = JSON.parse(authStorage);
            parsed.state.token = token;
            localStorage.setItem('auth-storage', JSON.stringify(parsed));
          }

          setAuthToken(token);
          processQueue(null, token);

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }

          return apiClient(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError as Error, null);
          localStorage.removeItem('auth-storage');
          setAuthToken(null);
          window.location.href = '/login';
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      // Transform error for consistent handling
      const apiError: ApiError = {
        message:
          error.response?.data?.message ||
          error.message ||
          'Erro desconhecido',
        code: error.response?.data?.code || 'UNKNOWN_ERROR',
        status: error.response?.status || 500,
        details: error.response?.data?.details,
      };

      return Promise.reject(apiError);
    }
  );
};

export default setupInterceptors;
