import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuth } from '../useAuth';
import api from '@/lib/api';

// Mock do api
vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
  getErrorMessage: vi.fn((error) => error?.message || 'Erro desconhecido'),
}));

// Mock do next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
  redirect: vi.fn(),
}));

describe('useAuth', () => {
  const mockUser = {
    id: 'user-123',
    email: 'test@example.com',
    name: 'Test User',
    role: 'admin',
    is_active: true,
  };

  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Estado Inicial', () => {
    it('deve iniciar com estado não autenticado quando não há token', async () => {
      const { result } = renderHook(() => useAuth());

      // Aguardar verificação inicial
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('deve verificar autenticação quando há token no localStorage', async () => {
      localStorage.setItem('access_token', 'valid-token');

      vi.mocked(api.get).mockResolvedValueOnce({ data: mockUser });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('deve limpar tokens quando a verificação falhar', async () => {
      localStorage.setItem('access_token', 'invalid-token');
      localStorage.setItem('refresh_token', 'invalid-refresh');

      vi.mocked(api.get).mockRejectedValueOnce(new Error('Unauthorized'));

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
    });
  });

  describe('Login', () => {
    it('deve enviar credenciais no formato correto (form-urlencoded)', async () => {
      const loginResponse = {
        access_token: 'token',
        refresh_token: 'refresh',
        token_type: 'bearer',
      };

      vi.mocked(api.post)
        .mockResolvedValueOnce({ data: loginResponse })
        .mockResolvedValueOnce({ data: mockUser });

      const { result } = renderHook(() => useAuth());
      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        await result.current.login({
          email: 'test@example.com',
          password: 'password123',
        });
      });

      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/auth/login',
        expect.any(URLSearchParams),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      const formData = vi.mocked(api.post).mock.calls[0]![1] as URLSearchParams;
      expect(formData.get('username')).toBe('test@example.com');
      expect(formData.get('password')).toBe('password123');
    });

    it('deve retornar erro quando login falhar', async () => {
      vi.mocked(api.post).mockRejectedValueOnce(new Error('Invalid credentials'));

      const { result } = renderHook(() => useAuth());
      await waitFor(() => expect(result.current.isLoading).toBe(false));

      let loginResult: { success: boolean; error?: string } = { success: true };

      await act(async () => {
        loginResult = await result.current.login({
          email: 'test@example.com',
          password: 'wrong-password',
        });
      });

      expect(loginResult.success).toBe(false);
      expect(loginResult.error).toBeDefined();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('Logout', () => {
    it('deve fazer logout e limpar tokens', async () => {
      localStorage.setItem('access_token', 'token');
      localStorage.setItem('refresh_token', 'refresh');

      vi.mocked(api.get).mockResolvedValueOnce({ data: mockUser });
      vi.mocked(api.post).mockResolvedValueOnce({});

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
    });

    it('deve limpar tokens mesmo quando a API de logout falhar', async () => {
      localStorage.setItem('access_token', 'token');
      localStorage.setItem('refresh_token', 'refresh');

      vi.mocked(api.get).mockResolvedValueOnce({ data: mockUser });
      vi.mocked(api.post).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(localStorage.getItem('access_token')).toBeNull();
    });
  });
});
