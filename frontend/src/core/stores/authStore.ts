import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api, setAuthToken, API_ENDPOINTS } from '@core/api';
import type {
  AuthResponse,
  LoginCredentials,
  User,
} from '@core/types/auth.types';

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  doRefreshToken: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  setUser: (user: User) => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });

        const email = credentials.email.trim().toLowerCase();
        const password = credentials.password;

        try {
          // OAuth2 login - form-urlencoded format
          const formData = new URLSearchParams();
          formData.append('username', email);
          formData.append('password', password);

          const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
          });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Credenciais invalidas');
          }

          const data = await response.json();
          const accessToken = data.access_token;
          const refreshTokenValue = data.refresh_token;

          setAuthToken(accessToken);

          // Decode JWT to get user info
          const payload = JSON.parse(atob(accessToken.split('.')[1]));

          set({
            user: {
              id: payload.sub,
              name: payload.email.split('@')[0].charAt(0).toUpperCase() +
                    payload.email.split('@')[0].slice(1),
              email: payload.email,
              role: payload.role || 'user',
              permissions: payload.role === 'admin' ? ['*'] : ['read', 'write'],
            },
            token: accessToken,
            refreshToken: refreshTokenValue,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          // Credenciais invalidas
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Erro ao fazer login',
            isAuthenticated: false,
            user: null,
            token: null,
            refreshToken: null,
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await api.post(API_ENDPOINTS.AUTH.LOGOUT);
        } catch {
          // Ignore logout errors
        } finally {
          setAuthToken(null);
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
            error: null,
          });
        }
      },

      doRefreshToken: async () => {
        const { refreshToken } = get();

        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        try {
          const response = await api.post<{ token: string }>(
            API_ENDPOINTS.AUTH.REFRESH,
            { refresh_token: refreshToken }
          );

          setAuthToken(response.token);
          set({ token: response.token });
        } catch (error) {
          // If refresh fails, logout
          get().logout();
          throw error;
        }
      },

      checkAuth: async () => {
        const { token } = get();

        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }

        set({ isLoading: true });

        try {
          setAuthToken(token);
          const user = await api.get<User>(API_ENDPOINTS.AUTH.ME);

          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch {
          setAuthToken(null);
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      clearError: () => set({ error: null }),

      setUser: (user: User) => set({ user }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
);

export default useAuthStore;
