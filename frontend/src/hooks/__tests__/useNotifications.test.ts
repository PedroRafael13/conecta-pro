import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import React from 'react';

// Mock do customInstance - definido antes de qualquer import
const mockCustomInstance = vi.fn();

vi.mock('@/lib/api-client', () => ({
  customInstance: (...args: any[]) => mockCustomInstance(...args),
}));

// Agora importar o hook depois do mock
import {
  useNotifications,
  useUnreadCount,
  useAlerts,
  useUserAlerts,
} from '../useNotifications';

import { afterEach } from 'vitest';

function createTestWrapper() {
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement('div', null, children);
}

// Ensure fake timers never leak between tests
afterEach(() => {
  vi.useRealTimers();
});

describe('useNotifications', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('error handling branches', () => {
    it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const wrapper = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro ao carregar notificações');
      });
      expect(result.current.notifications).toEqual([]);
    });

    it('deve retornar mensagem de erro quando é Error instance', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Erro específico'));

      const wrapper = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro específico');
      });
    });
  });

  describe('autoLoad branches', () => {
    it('não deve carregar quando autoLoad é false', async () => {
      const wrapper = createTestWrapper();
      renderHook(() => useNotifications({ autoLoad: false }), { wrapper });

      await new Promise(resolve => setTimeout(resolve, 100));
      expect(mockCustomInstance).not.toHaveBeenCalled();
    });
  });

  describe('deleteNotification branches', () => {
    it('deve retornar true e remover notificação quando deleteNotification sucede', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1' }, { id: '2' }], total: 2, total_pages: 1 })
        .mockResolvedValueOnce(undefined);

      const wrapper = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => expect(result.current.isLoading).toBe(false));
      expect(result.current.notifications).toHaveLength(2);

      let success: boolean;
      await act(async () => {
        success = await result.current.deleteNotification('1');
      });

      expect(success!).toBe(true);
      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.total).toBe(1);
    });

    it('deve retornar false quando deleteNotification falha', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1' }], total: 1, total_pages: 1 })
        .mockRejectedValueOnce(new Error('Falha'));

      const wrapper = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      let success: boolean;
      await act(async () => {
        success = await result.current.deleteNotification('1');
      });

      expect(success!).toBe(false);
    });
  });

  describe('markAllAsRead branches', () => {
    it('deve retornar true e marcar todas como lidas', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1', is_read: false }, { id: '2', is_read: false }], total: 2, total_pages: 1 })
        .mockResolvedValueOnce({ success: true, count: 2 });

      const wrapper = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      let success: boolean;
      await act(async () => {
        success = await result.current.markAllAsRead();
      });

      expect(success!).toBe(true);
      expect(result.current.notifications.every(n => n.is_read)).toBe(true);
    });

    it('deve retornar false quando markAllAsRead falha', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1' }], total: 1, total_pages: 1 })
        .mockRejectedValueOnce(new Error('Falha'));

      const wrapper = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      let success: boolean;
      await act(async () => {
        success = await result.current.markAllAsRead();
      });

      expect(success!).toBe(false);
    });
  });

  describe('pollInterval branches', () => {
    it('deve criar intervalo de polling quando pollInterval > 0', async () => {
      const setIntervalSpy = vi.spyOn(global, 'setInterval');
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const wrapper = createTestWrapper();
      const { result, unmount } = renderHook(() => useNotifications({ autoLoad: true, pollInterval: 5000 }), { wrapper });

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      // Verificar que setInterval foi chamado com o pollInterval
      expect(setIntervalSpy).toHaveBeenCalledWith(expect.any(Function), 5000);
      setIntervalSpy.mockRestore();
      unmount();
    });
  });

  describe('markAsRead branches', () => {
    it('deve retornar true quando markAsRead sucede', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1', is_read: false }], total: 1, total_pages: 1 })
        .mockResolvedValueOnce({});

      const wrapper = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      let success: boolean;
      await act(async () => {
        success = await result.current.markAsRead('1');
      });

      expect(success!).toBe(true);
    });

    it('deve retornar false quando markAsRead falha', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1' }], total: 1, total_pages: 1 })
        .mockRejectedValueOnce(new Error('Falha'));

      const wrapper = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      let success: boolean;
      await act(async () => {
        success = await result.current.markAsRead('1');
      });

      expect(success!).toBe(false);
    });
  });

  describe('setFilters', () => {
    it('deve resetar para página 1 quando filtros são alterados', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const wrapper = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      act(() => {
        result.current.setPage(3);
      });

      expect(result.current.page).toBe(3);

      act(() => {
        result.current.setFilters({ is_read: true });
      });

      expect(result.current.page).toBe(1);
    });
  });
});

describe('useUnreadCount', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve usar valores padrão quando count é null', async () => {
    mockCustomInstance.mockResolvedValueOnce(null);

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useUnreadCount(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.total).toBe(0);
    expect(result.current.byType).toEqual({});
  });

  it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
    mockCustomInstance.mockRejectedValueOnce('erro string');

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useUnreadCount(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toBe('Erro ao carregar contagem');
  });

  it('não deve criar intervalo quando pollInterval é 0', async () => {
    mockCustomInstance.mockResolvedValueOnce({ total: 5 });

    const wrapper = createTestWrapper();
    renderHook(() => useUnreadCount(0), { wrapper });

    await waitFor(() => expect(mockCustomInstance).toHaveBeenCalledTimes(1));

    await new Promise(resolve => setTimeout(resolve, 200));
    expect(mockCustomInstance).toHaveBeenCalledTimes(1);
  });

  it('deve criar intervalo quando pollInterval > 0', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockCustomInstance.mockResolvedValue({ total: 5, by_type: { info: 3 } });

    const wrapper = createTestWrapper();
    renderHook(() => useUnreadCount(10000), { wrapper });

    // Wait for initial fetch with shouldAdvanceTime allowing promises to resolve
    await vi.waitFor(() => expect(mockCustomInstance).toHaveBeenCalledTimes(1));

    await act(async () => {
      await vi.advanceTimersByTimeAsync(10000);
    });

    expect(mockCustomInstance).toHaveBeenCalledTimes(2);
  });
});

describe('useAlerts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve usar query string vazia quando filters é undefined', async () => {
    mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0 });

    const wrapper = createTestWrapper();
    renderHook(() => useAlerts({ autoLoad: true }), { wrapper });

    await waitFor(() => {
      expect(mockCustomInstance).toHaveBeenCalledWith(expect.objectContaining({
        url: '/api/v1/operacional/comunicacao/alertas',
      }));
    });
  });

  it('deve usar query string quando filters é definido', async () => {
    mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0 });

    const wrapper = createTestWrapper();
    renderHook(() => useAlerts({ autoLoad: true, filters: { alert_type: 'seguranca' } }), { wrapper });

    await waitFor(() => {
      expect(mockCustomInstance).toHaveBeenCalledWith(expect.objectContaining({
        url: expect.stringContaining('alert_type=seguranca'),
      }));
    });
  });

  it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
    mockCustomInstance.mockRejectedValueOnce('erro string');

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useAlerts({ autoLoad: true, pollInterval: 0 }), { wrapper });

    await waitFor(() => {
      expect(result.current.error).toBe('Erro ao carregar alertas');
    });
  });

  it('deve retornar false quando acknowledge falha', async () => {
    mockCustomInstance
      .mockResolvedValueOnce({ items: [{ id: '1' }], total: 1 })
      .mockRejectedValueOnce(new Error('Falha'));

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useAlerts({ autoLoad: true, pollInterval: 0 }), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    let success: boolean;
    await act(async () => {
      success = await result.current.acknowledge('1');
    });

    expect(success!).toBe(false);
  });

  it('deve retornar null quando createAlert falha', async () => {
    mockCustomInstance
      .mockResolvedValueOnce({ items: [], total: 0 })
      .mockRejectedValueOnce(new Error('Falha'));

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useAlerts({ autoLoad: true, pollInterval: 0 }), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    let alert: unknown;
    await act(async () => {
      alert = await result.current.createAlert({ message: 'Test' } as any);
    });

    expect(alert).toBeNull();
  });
});

describe('useUserAlerts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve calcular criticalCount corretamente', async () => {
    mockCustomInstance.mockResolvedValueOnce({
      items: [
        { id: '1', is_critical: true },
        { id: '2', is_critical: false },
        { id: '3', is_critical: true },
      ],
    });

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useUserAlerts(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.criticalCount).toBe(2);
    expect(result.current.total).toBe(3);
  });

  it('deve ter criticalCount 0 quando alerts é vazio', async () => {
    mockCustomInstance.mockResolvedValueOnce({ items: [] });

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useUserAlerts(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.criticalCount).toBe(0);
    expect(result.current.total).toBe(0);
  });

  it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
    mockCustomInstance.mockRejectedValueOnce('erro string');

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useUserAlerts(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toBe('Erro ao carregar alertas');
  });

  it('deve retornar false quando acknowledge falha', async () => {
    mockCustomInstance
      .mockResolvedValueOnce({ items: [{ id: '1' }] })
      .mockRejectedValueOnce(new Error('Falha'));

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useUserAlerts(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    let success: boolean;
    await act(async () => {
      success = await result.current.acknowledge('1');
    });

    expect(success!).toBe(false);
  });

  it('deve retornar true e remover alerta quando acknowledge tem sucesso', async () => {
    mockCustomInstance
      .mockResolvedValueOnce({ items: [{ id: '1' }, { id: '2' }] })
      .mockResolvedValueOnce({});

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useUserAlerts(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.alerts).toHaveLength(2);

    let success: boolean;
    await act(async () => {
      success = await result.current.acknowledge('1');
    });

    expect(success!).toBe(true);
    expect(result.current.alerts).toHaveLength(1);
    expect(result.current.alerts[0]!.id).toBe('2');
  });

  it('deve criar intervalo quando pollInterval > 0', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockCustomInstance.mockResolvedValue({ items: [{ id: '1', is_critical: false }] });

    const wrapper = createTestWrapper();
    renderHook(() => useUserAlerts(5000), { wrapper });

    await vi.waitFor(() => expect(mockCustomInstance).toHaveBeenCalledTimes(1));

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5000);
    });

    expect(mockCustomInstance).toHaveBeenCalledTimes(2);
  });

  it('deve retornar mensagem de Error quando erro é Error instance', async () => {
    mockCustomInstance.mockRejectedValueOnce(new Error('Erro específico'));

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useUserAlerts(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toBe('Erro específico');
  });
});

describe('useAlerts - fetchData e operações', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve chamar fetchData com sucesso', async () => {
    mockCustomInstance.mockResolvedValueOnce({
      items: [{ id: '1', message: 'Alert 1' }],
      total: 1,
    });

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useAlerts({ autoLoad: true, pollInterval: 0 }), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.alerts).toHaveLength(1);
    expect(result.current.total).toBe(1);
  });

  it('deve acknowledge com sucesso', async () => {
    mockCustomInstance
      .mockResolvedValueOnce({ items: [{ id: '1' }], total: 1 })
      .mockResolvedValueOnce({});

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useAlerts({ autoLoad: true, pollInterval: 0 }), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    let success: boolean;
    await act(async () => {
      success = await result.current.acknowledge('1');
    });

    expect(success!).toBe(true);
    expect(result.current.alerts).toHaveLength(0);
  });

  it('deve criar alert com sucesso', async () => {
    mockCustomInstance
      .mockResolvedValueOnce({ items: [], total: 0 })
      .mockResolvedValueOnce({ id: '1', message: 'New alert' });

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useAlerts({ autoLoad: true, pollInterval: 0 }), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    let alert: unknown;
    await act(async () => {
      alert = await result.current.createAlert({ message: 'New alert' } as any);
    });

    expect(alert).toEqual({ id: '1', message: 'New alert' });
    expect(result.current.alerts).toHaveLength(1);
  });

  it('deve retornar mensagem de erro quando é Error instance', async () => {
    mockCustomInstance.mockRejectedValueOnce(new Error('Erro específico de alerta'));

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useAlerts({ autoLoad: true, pollInterval: 0 }), { wrapper });

    await waitFor(() => {
      expect(result.current.error).toBe('Erro específico de alerta');
    });
  });

  it('deve chamar refresh e recarregar alertas', async () => {
    // Provide enough mock values for potential re-renders
    mockCustomInstance
      .mockResolvedValueOnce({ items: [{ id: '1' }], total: 1 })
      .mockResolvedValueOnce({ items: [{ id: '1' }], total: 1 })
      .mockResolvedValueOnce({ items: [{ id: '1' }, { id: '2' }], total: 2 })
      .mockResolvedValue({ items: [{ id: '1' }, { id: '2' }], total: 2 });

    const wrapper = createTestWrapper();
    const { result } = renderHook(() => useAlerts({ autoLoad: true, pollInterval: 0 }), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.refresh();
    });

    await waitFor(() => {
      expect(result.current.alerts.length).toBeGreaterThanOrEqual(1);
    });
  }, 10000);
});
