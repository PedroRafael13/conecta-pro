import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { usePosts, usePostStats, usePost } from '../usePosts';

// Mock do api-client
const mockCustomInstance = vi.fn();

vi.mock('@/lib/api-client', () => ({
  customInstance: (...args: unknown[]) => mockCustomInstance(...args),
}));

describe('usePosts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('usePosts - Estado Inicial', () => {
    it('deve iniciar com valores padrão', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [],
        total: 0,
        total_pages: 0,
      });

      const { result } = renderHook(() => usePosts());

      expect(result.current.isLoading).toBe(true);
      expect(result.current.posts).toEqual([]);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(20);
      expect(result.current.filters).toEqual({});

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });

    it('deve aceitar opções personalizadas', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() =>
        usePosts({
          initialPage: 2,
          initialPageSize: 50,
          initialFilters: { status: 'active' },
        })
      );

      expect(result.current.page).toBe(2);
      expect(result.current.pageSize).toBe(50);
      expect(result.current.filters).toEqual({ status: 'active' });
    });

    it('não deve carregar quando autoLoad é false', () => {
      const { result } = renderHook(() => usePosts({ autoLoad: false }));

      expect(result.current.isLoading).toBe(false);
      expect(mockCustomInstance).not.toHaveBeenCalled();
    });
  });

  describe('usePosts - Fetch', () => {
    it('deve construir URL corretamente', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      renderHook(() =>
        usePosts({
          initialPage: 2,
          initialPageSize: 30,
          initialFilters: { status: 'active', post_type: 'vigilante' },
        })
      );

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledWith(
          expect.objectContaining({
            url: expect.stringContaining('page=2'),
            method: 'GET',
          })
        );
      });

      expect(mockCustomInstance).toHaveBeenCalledWith(
        expect.objectContaining({
          url: expect.stringContaining('page_size=30'),
        })
      );
    });

    it('deve ignorar filtros vazios na URL', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      renderHook(() =>
        usePosts({
          initialFilters: { status: 'active' },
        })
      );

      await waitFor(() => {
        const url = mockCustomInstance.mock.calls[0]?.[0]?.url as string;
        expect(url).toContain('status=active');
        expect(url).not.toContain('empty=');
        expect(url).not.toContain('nullValue');
        expect(url).not.toContain('undefinedValue');
      });
    });
  });

  describe('usePosts - Paginação', () => {
    it('deve atualizar página', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => usePosts());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        result.current.setPage(5);
      });

      await waitFor(() => {
        expect(result.current.page).toBe(5);
      });
    });

    it('deve atualizar pageSize', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => usePosts());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        result.current.setPageSize(100);
      });

      await waitFor(() => {
        expect(result.current.pageSize).toBe(100);
      });
    });

    it('deve evitar requisições duplicadas', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => usePosts());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      // Agora deve fazer nova requisição ao mudar página
      await act(async () => {
        result.current.setPage(2);
      });

      await waitFor(() => {
        // 1 inicial + 1 após mudança de página
        expect(mockCustomInstance).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('usePosts - Filtros', () => {
    it('deve atualizar filtros', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => usePosts());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        result.current.setFilters({ status: 'inactive' });
      });

      await waitFor(() => {
        expect(result.current.filters).toEqual({ status: 'inactive' });
      });
    });
  });

  describe('usePosts - Error Handling', () => {
    it('deve capturar erro', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => usePosts());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Network error');
      expect(result.current.posts).toEqual([]);
    });

    it('deve implementar backoff em erros consecutivos', async () => {
      mockCustomInstance.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => usePosts());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      // Tentar refresh imediato
      await act(async () => {
        await result.current.refresh();
      });

      // Não deve fazer nova requisição devido ao backoff
      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('usePostStats', () => {
    it('deve carregar estatísticas', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        total: 50,
        by_status: { active: 45, inactive: 5 },
        by_type: { vigilante: 30, porteiro: 20 },
        by_shift: { diurno: 25, noturno: 25 },
        filled: 40,
        with_vacancy: 10,
        total_headcount: 80,
        total_allocated: 75,
        total_monthly_cost: 150000,
      });

      const { result } = renderHook(() => usePostStats());

      await waitFor(() => {
        expect(result.current.stats).not.toBeNull();
      });

      expect(result.current.stats?.total).toBe(50);
      expect(result.current.stats?.by_status?.active).toBe(45);
    });

    it('deve capturar erro ao carregar estatísticas', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => usePostStats());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Failed');
    });
  });

  describe('usePost', () => {
    it('deve retornar null quando id é null', async () => {
      const { result } = renderHook(() => usePost(null));

      expect(result.current.post).toBeNull();
      expect(result.current.isLoading).toBe(false);
    });

    it('deve carregar posto quando id é fornecido', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '123',
        name: 'Posto Teste',
        status: 'active',
      });

      const { result } = renderHook(() => usePost('123'));

      await waitFor(() => {
        expect(result.current.post).not.toBeNull();
      });

      expect(result.current.post?.name).toBe('Posto Teste');
    });

    it('deve limpar dados quando id muda para null', async () => {
      mockCustomInstance.mockResolvedValue({
        id: '123',
        name: 'Posto Teste',
      });

      const { result, rerender } = renderHook(({ id }) => usePost(id), {
        initialProps: { id: '123' as string | null },
      });

      await waitFor(() => expect(result.current.post).not.toBeNull());

      rerender({ id: null });

      expect(result.current.post).toBeNull();
    });
  });
});
