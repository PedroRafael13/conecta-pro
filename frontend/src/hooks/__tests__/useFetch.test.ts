import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useFetch, clearCache, invalidateCache } from '../useFetch';

describe('useFetch', () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    global.fetch = mockFetch;
    clearCache();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('GET, POST, PUT, DELETE', () => {
    it('deve fazer requisição GET por padrão', async () => {
      const mockData = { id: 1, name: 'Test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      } as Response);

      const { result } = renderHook(() => useFetch('/api/test'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/test', expect.any(Object));
      expect(result.current.data).toEqual(mockData);
    });

    it('deve fazer requisição POST', async () => {
      const mockData = { id: 1, created: true };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      } as Response);

      const { result } = renderHook(() =>
        useFetch('/api/test', {
          method: 'POST',
          body: JSON.stringify({ name: 'Test' }),
        })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/test', expect.objectContaining({
        method: 'POST',
      }));
    });

    it('deve fazer requisição PUT', async () => {
      const mockData = { id: 1, updated: true };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      } as Response);

      const { result } = renderHook(() =>
        useFetch('/api/test/1', {
          method: 'PUT',
          body: JSON.stringify({ name: 'Updated' }),
        })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/test/1', expect.objectContaining({
        method: 'PUT',
      }));
    });

    it('deve fazer requisição DELETE', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ deleted: true }),
      } as Response);

      const { result } = renderHook(() =>
        useFetch('/api/test/1', { method: 'DELETE' })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/test/1', expect.objectContaining({
        method: 'DELETE',
      }));
    });
  });

  describe('Loading State', () => {
    it('deve iniciar com isLoading true', () => {
      mockFetch.mockImplementation(() => new Promise(() => {}));

      const { result } = renderHook(() => useFetch('/api/test'));

      expect(result.current.isLoading).toBe(true);
    });

    it('deve setar isLoading para false após sucesso', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'test' }),
      } as Response);

      const { result } = renderHook(() => useFetch('/api/test'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.isSuccess).toBe(true);
    });

    it('deve setar isLoading para false após erro', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useFetch('/api/test'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).not.toBeNull();
    });

    it('não deve fazer fetch quando enabled é false', () => {
      const { result } = renderHook(() =>
        useFetch('/api/test', { enabled: false })
      );

      expect(mockFetch).not.toHaveBeenCalled();
      expect(result.current.isLoading).toBe(false);
    });

    it('não deve fazer fetch quando URL é null', () => {
      const { result } = renderHook(() => useFetch(null));

      expect(mockFetch).not.toHaveBeenCalled();
      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Error Handling', () => {
    it('deve capturar erro de HTTP', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      } as Response);

      const { result } = renderHook(() => useFetch('/api/test'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toContain('404');
      expect(result.current.isSuccess).toBe(false);
    });

    it('deve capturar erro de rede', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useFetch('/api/test'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.data).toBeNull();
    });

    it('deve chamar onError callback quando há erro', async () => {
      const onError = vi.fn();
      mockFetch.mockRejectedValueOnce(new Error('Test error'));

      renderHook(() => useFetch('/api/test', { onError }));

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(expect.any(Error));
      });
    });

    it('deve chamar onSuccess callback quando sucesso', async () => {
      const onSuccess = vi.fn();
      const mockData = { success: true };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      } as Response);

      renderHook(() => useFetch('/api/test', { onSuccess }));

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalledWith(mockData);
      });
    });
  });

  describe('Cache', () => {
    it('deve usar cache quando habilitado', async () => {
      const mockData = { cached: true };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      } as Response);

      const { rerender } = renderHook(
        ({ url }) => useFetch(url, { useCache: true }),
        { initialProps: { url: '/api/cached' } }
      );

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(1);
      });

      // Mudar URL e voltar
      rerender({ url: '/api/other' });
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(2);
      });

      rerender({ url: '/api/cached' });
      // Não deve fazer nova requisição (cache)
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    it('deve invalidar cache específico', async () => {
      const mockData = { data: 'test' };
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockData,
      } as Response);

      const { rerender } = renderHook(
        ({ url }) => useFetch(url, { useCache: true }),
        { initialProps: { url: '/api/test' } }
      );

      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(1));

      invalidateCache('/api/test');

      rerender({ url: '/api/other' });
      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(2));

      rerender({ url: '/api/test' });
      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(3));
    });

    it('deve limpar todo o cache', async () => {
      const mockData = { data: 'test' };
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockData,
      } as Response);

      const { rerender } = renderHook(
        ({ url }) => useFetch(url, { useCache: true }),
        { initialProps: { url: '/api/test' } }
      );

      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(1));

      clearCache();

      rerender({ url: '/api/other' });
      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(2));

      rerender({ url: '/api/test' });
      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(3));
    });
  });

  describe('Refetch', () => {
    it('deve refetch limpando cache', async () => {
      const mockData = { data: 'test' };
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockData,
      } as Response);

      const { result } = renderHook(() =>
        useFetch('/api/test', { useCache: true })
      );

      await waitFor(() => expect(result.current.isLoading).toBe(false));
      expect(mockFetch).toHaveBeenCalledTimes(1);

      await result.current.refetch();

      await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(2));
    });

    it('deve atualizar dados com mutate', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'original' }),
      } as Response);

      const { result } = renderHook(() => useFetch('/api/test'));

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      result.current.mutate({ data: 'updated' });

      expect(result.current.data).toEqual({ data: 'updated' });
    });
  });
});
