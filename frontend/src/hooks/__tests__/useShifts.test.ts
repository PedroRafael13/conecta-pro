import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useShifts, useTodayShifts, useShiftOperations } from '../useShifts';

// Mock do api-client
const mockCustomInstance = vi.fn();

vi.mock('@/lib/api-client', () => ({
  customInstance: (...args: unknown[]) => mockCustomInstance(...args),
}));

describe('useShifts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('useShifts - Estado Inicial', () => {
    it('deve iniciar com valores padrão', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [],
        total: 0,
        total_pages: 0,
      });

      const { result } = renderHook(() => useShifts());

      expect(result.current.isLoading).toBe(true);
      expect(result.current.shifts).toEqual([]);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(50);
      expect(result.current.filters).toEqual({});

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });

    it('deve aceitar opções personalizadas', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() =>
        useShifts({
          autoLoad: false,
          initialPage: 2,
          initialPageSize: 100,
          initialFilters: { status: 'scheduled' },
        })
      );

      expect(result.current.page).toBe(2);
      expect(result.current.pageSize).toBe(100);
      expect(result.current.filters).toEqual({ status: 'scheduled' });
      expect(result.current.isLoading).toBe(false);
    });

    it('deve iniciar loading quando autoLoad é true', async () => {
      mockCustomInstance.mockImplementation(() =>
        new Promise(resolve =>
          setTimeout(() => resolve({
            items: [{ id: '1', status: 'scheduled' }],
            total: 1,
            total_pages: 1,
          }), 10)
        )
      );

      const { result } = renderHook(() => useShifts({ autoLoad: true }));

      // Should start loading
      expect(result.current.isLoading).toBe(true);

      // Wait for loading to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      }, { timeout: 1000 });
    });
  });

  describe('useShifts - Fetch', () => {
    it('deve construir URL com parâmetros', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      renderHook(() =>
        useShifts({
          initialPage: 2,
          initialPageSize: 30,
          initialFilters: { status: 'scheduled' },
        })
      );

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledWith(
          expect.objectContaining({
            url: expect.stringContaining('/api/v1/operacional/shifts'),
            method: 'GET',
          })
        );
      });
    });

    it('deve ignorar filtros vazios', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      renderHook(() =>
        useShifts({
          initialFilters: {
            status: 'scheduled',
            post_id: '',
          },
        })
      );

      await waitFor(() => {
        const url = (mockCustomInstance.mock.calls[0]?.[0] as { url: string })?.url;
        expect(url).toContain('status=scheduled');
        expect(url).not.toContain('post_id=');
      });
    });
  });

  describe('useShifts - Paginação', () => {
    it('deve atualizar página', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useShifts());

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

      const { result } = renderHook(() => useShifts());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        result.current.setPageSize(200);
      });

      await waitFor(() => {
        expect(result.current.pageSize).toBe(200);
      });
    });

    it('deve recarregar ao mudar página', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useShifts());

      await waitFor(() => expect(mockCustomInstance).toHaveBeenCalledTimes(1));

      await act(async () => {
        result.current.setPage(2);
      });

      await waitFor(() => expect(mockCustomInstance).toHaveBeenCalledTimes(2));
    });
  });

  describe('useShifts - Filtros', () => {
    it('deve atualizar filtros', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useShifts());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        result.current.setFilters({ post_id: '123', status: 'scheduled' });
      });

      await waitFor(() => {
        expect(result.current.filters).toEqual({ post_id: '123', status: 'scheduled' });
      });
    });
  });

  describe('useShifts - Refresh', () => {
    it('deve recarregar turnos', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useShifts());

      await waitFor(() => expect(mockCustomInstance).toHaveBeenCalledTimes(1));

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('useTodayShifts', () => {
    it('deve carregar turnos de hoje', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [{ id: '1', start_time: '08:00' }],
        total: 1,
      });

      const { result } = renderHook(() => useTodayShifts());

      await waitFor(() => {
        expect(result.current.shifts).toHaveLength(1);
      });

      expect(mockCustomInstance).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/api/v1/operacional/shifts/today',
        })
      );
    });

    it('deve filtrar por posto quando postId é fornecido', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0 });

      renderHook(() => useTodayShifts('post-123'));

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledWith(
          expect.objectContaining({
            url: expect.stringContaining('post_id=post-123'),
          })
        );
      });
    });

    it('deve capturar erro', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => useTodayShifts());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Failed');
    });
  });

  describe('useShiftOperations', () => {
    it('deve criar turno', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '1',
        post_id: 'post-1',
        start_time: '08:00',
      });

      const { result } = renderHook(() => useShiftOperations());

      let shift: unknown;
      await act(async () => {
        shift = await result.current.createShift({
          post_id: 'post-1',
          start_time: '08:00',
        } as any);
      });

      expect(shift).toEqual({ id: '1', post_id: 'post-1', start_time: '08:00' });
      expect(mockCustomInstance).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/api/v1/operacional/shifts/',
          method: 'POST',
        })
      );
    });

    it('deve atualizar turno', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '1',
        start_time: '09:00',
      });

      const { result } = renderHook(() => useShiftOperations());

      let shift: unknown;
      await act(async () => {
        shift = await result.current.updateShift('1', { start_time: '09:00' } as any);
      });

      expect(shift).toEqual({ id: '1', start_time: '09:00' });
    });

    it('deve deletar turno', async () => {
      mockCustomInstance.mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useShiftOperations());

      let deleted: boolean;
      await act(async () => {
        deleted = await result.current.deleteShift('1');
      });

      await waitFor(() => {
        expect(deleted).toBe(true);
      });
    });

    it('deve registrar check-in', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '1',
        check_in: '08:05',
        status: 'in_progress',
      });

      const { result } = renderHook(() => useShiftOperations());

      let shift: unknown;
      await act(async () => {
        shift = await result.current.checkIn('1', {
          latitude: -23.5,
          longitude: -46.6,
        } as any);
      });

      expect(shift).toEqual({
        id: '1',
        check_in: '08:05',
        status: 'in_progress',
      });
    });

    it('deve registrar check-out', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '1',
        check_out: '17:05',
        status: 'completed',
      });

      const { result } = renderHook(() => useShiftOperations());

      let shift: unknown;
      await act(async () => {
        shift = await result.current.checkOut('1', {
          latitude: -23.5,
          longitude: -46.6,
        } as any);
      });

      expect(shift).toEqual({
        id: '1',
        check_out: '17:05',
        status: 'completed',
      });
    });

    it('deve retornar null e setar erro quando operação falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => useShiftOperations());

      let shift: unknown;
      await act(async () => {
        shift = await result.current.createShift({} as any);
      });

      await waitFor(() => {
        expect(shift).toBeNull();
      });
      expect(result.current.error).toBe('Failed');
    });

    it('deve refletir estado de loading', async () => {
      mockCustomInstance.mockImplementation(() => new Promise(() => {}));

      const { result } = renderHook(() => useShiftOperations());

      // Iniciar operação
      act(() => {
        result.current.createShift({} as any);
      });

      expect(result.current.isLoading).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('deve capturar erro ao carregar turnos', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useShifts());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Network error');
      expect(result.current.shifts).toEqual([]);
    });

    it('deve retornar erro genérico quando não há mensagem', async () => {
      mockCustomInstance.mockRejectedValueOnce('Unknown error');

      const { result } = renderHook(() => useShifts());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Erro ao carregar turnos');
    });
  });
});
