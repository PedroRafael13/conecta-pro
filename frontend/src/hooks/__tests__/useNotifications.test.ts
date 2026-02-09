import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import {
  useNotifications,
  useUnreadCount,
  useAlerts,
  useUserAlerts,
} from '../useNotifications';

// Mock do api-client
const mockCustomInstance = vi.fn();

vi.mock('@/lib/api-client', () => ({
  customInstance: (...args: unknown[]) => mockCustomInstance(...args),
}));

// Helper to flush promises
const flushPromises = () => new Promise(resolve => setTimeout(resolve, 0));

describe('useNotifications', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('useNotifications - Estado Inicial', () => {
    it('deve iniciar com valores padrão', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [],
        total: 0,
        total_pages: 0,
      });

      const { result } = renderHook(() => useNotifications());

      expect(result.current.isLoading).toBe(true);
      expect(result.current.notifications).toEqual([]);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(20);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });

    it('deve aceitar opções personalizadas', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() =>
        useNotifications({
          initialPageSize: 50,
          autoLoad: false,
          initialFilters: { is_read: false },
        })
      );

      expect(result.current.pageSize).toBe(50);
      expect(result.current.filters).toEqual({ is_read: false });
      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('useNotifications - Fetch', () => {
    it('deve buscar notificações', async () => {
      mockCustomInstance.mockImplementation(() =>
        Promise.resolve({
          items: [
            { id: '1', message: 'Test 1', is_read: false },
            { id: '2', message: 'Test 2', is_read: true },
          ],
          total: 2,
          total_pages: 1,
        })
      );

      const { result } = renderHook(() => useNotifications());

      // Wait for isLoading to be false (data loaded)
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockCustomInstance).toHaveBeenCalledWith(
        expect.objectContaining({
          url: expect.stringContaining('/api/v1/operacional/comunicacao/notificacoes'),
          method: 'GET',
        })
      );
    });

    it('deve passar filtros na URL', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      renderHook(() =>
        useNotifications({
          initialFilters: { is_read: false, type: 'sistema' },
        })
      );

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledWith(
          expect.objectContaining({
            url: expect.stringContaining('is_read'),
          })
        );
      });
    });
  });

  describe('useNotifications - Paginação', () => {
    it('deve atualizar página', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useNotifications());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        result.current.setPage(3);
      });

      await waitFor(() => {
        expect(result.current.page).toBe(3);
      });
    });

    it('deve atualizar pageSize', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useNotifications());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        result.current.setPageSize(100);
      });

      await waitFor(() => {
        expect(result.current.pageSize).toBe(100);
      });
    });

    it('deve resetar página ao atualizar filtros', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useNotifications({ initialPageSize: 20 }));

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      // Primeiro muda para página 3
      await act(async () => {
        result.current.setPage(3);
      });

      await waitFor(() => expect(result.current.page).toBe(3));

      // Agora atualiza filtros - deve resetar para página 1
      await act(async () => {
        result.current.setFilters({ is_read: true });
      });

      await waitFor(() => {
        expect(result.current.page).toBe(1);
      });
    });
  });

  describe('useNotifications - Ações', () => {
    it('deve marcar notificação como lida', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1', is_read: false }], total: 1, total_pages: 1 })
        .mockResolvedValueOnce({});

      const { result } = renderHook(() => useNotifications());

      await waitFor(() => expect(result.current.notifications).toHaveLength(1));

      let success: boolean;
      await act(async () => {
        success = await result.current.markAsRead('1');
      });

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledWith(
          expect.objectContaining({
            url: expect.stringContaining('/1/lida'),
            method: 'POST',
          })
        );
      });
    });

    it('deve marcar todas como lidas', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1', is_read: false }], total: 1, total_pages: 1 })
        .mockResolvedValueOnce({ success: true, count: 1 });

      const { result } = renderHook(() => useNotifications());

      await waitFor(() => expect(result.current.notifications).toHaveLength(1));

      await act(async () => {
        await result.current.markAllAsRead();
      });

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledWith(
          expect.objectContaining({
            url: expect.stringContaining('/marcar-todas'),
            method: 'POST',
          })
        );
      });
    });

    it('deve deletar notificação', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1' }, { id: '2' }], total: 2, total_pages: 1 })
        .mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useNotifications());

      await waitFor(() => expect(result.current.notifications).toHaveLength(2));

      await act(async () => {
        await result.current.deleteNotification('1');
      });

      await waitFor(() => {
        expect(result.current.total).toBe(1);
      });
    });

    it('deve retornar false quando ação falha', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1' }], total: 1, total_pages: 1 })
        .mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => useNotifications());

      await waitFor(() => expect(result.current.notifications).toHaveLength(1));

      let success: boolean;
      await act(async () => {
        success = await result.current.markAsRead('1');
      });

      await waitFor(() => {
        expect(success).toBe(false);
      });
    });
  });

  describe('useNotifications - Polling', () => {
    it('deve fazer polling quando pollInterval é definido', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      renderHook(() => useNotifications({ pollInterval: 5000 }));

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledTimes(1);
      });

      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('useUnreadCount', () => {
    it('deve carregar contagem de não lidas', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        total: 5,
        by_type: { system: 3, message: 2 },
      });

      const { result } = renderHook(() => useUnreadCount());

      await waitFor(() => {
        expect(result.current.count).not.toBeNull();
      });

      expect(result.current.total).toBe(5);
      expect(result.current.byType).toEqual({ system: 3, message: 2 });
    });

    it('deve fazer polling', async () => {
      mockCustomInstance.mockResolvedValue({ total: 0, by_type: {} });

      renderHook(() => useUnreadCount(5000));

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledTimes(1);
      });

      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('useAlerts', () => {
    it('deve carregar alertas', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [{ id: '1', severity: 'high' }],
        total: 1,
      });

      const { result } = renderHook(() => useAlerts());

      await waitFor(() => {
        expect(result.current.alerts).toHaveLength(1);
      });

      expect(result.current.total).toBe(1);
    });

    it('deve acknowledge alert', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1', is_critical: true }], total: 1 })
        .mockResolvedValueOnce({});

      const { result } = renderHook(() => useAlerts());

      await waitFor(() => expect(result.current.alerts).toHaveLength(1));

      await act(async () => {
        await result.current.acknowledge('1');
      });

      await waitFor(() => {
        expect(result.current.total).toBe(0);
      });
    });

    it('deve criar alerta', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [], total: 0 })
        .mockResolvedValueOnce({ id: '1', message: 'New' });

      const { result } = renderHook(() => useAlerts());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        await result.current.createAlert({
          message: 'New',
          severity: 'medium',
        } as any);
      });

      await waitFor(() => {
        expect(result.current.total).toBe(1);
      });
    });
  });

  describe('useUserAlerts', () => {
    it('deve carregar alertas do usuário', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [
          { id: '1', is_critical: true },
          { id: '2', is_critical: false },
        ],
        total: 2,
      });

      const { result } = renderHook(() => useUserAlerts());

      await waitFor(() => {
        expect(result.current.alerts).toHaveLength(2);
      });

      expect(result.current.criticalCount).toBe(1);
    });

    it('deve acknowledge e remover alerta', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1' }], total: 1 })
        .mockResolvedValueOnce({});

      const { result } = renderHook(() => useUserAlerts());

      await waitFor(() => expect(result.current.alerts).toHaveLength(1));

      await act(async () => {
        await result.current.acknowledge('1');
      });

      await waitFor(() => {
        expect(result.current.alerts).toHaveLength(0);
      });
    });
  });

  describe('Error Handling', () => {
    it('deve capturar erro ao carregar notificações', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => useNotifications());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Failed');
    });
  });
});
