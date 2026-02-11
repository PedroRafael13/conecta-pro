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

function createTestWrapper() {
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement('div', null, children);
}

describe('useNotifications', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('error handling branches', () => {
    it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const { wrapper } = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro ao carregar notificações');
      });
      expect(result.current.notifications).toEqual([]);
    });

    it('deve retornar mensagem de erro quando é Error instance', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Erro específico'));

      const { wrapper } = createTestWrapper();
      const { result } = renderHook(() => useNotifications({ autoLoad: true }), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro específico');
      });
    });
  });

  describe('autoLoad branches', () => {
    it('não deve carregar quando autoLoad é false', async () => {
      const { wrapper } = createTestWrapper();
      renderHook(() => useNotifications({ autoLoad: false }), { wrapper });

      await new Promise(resolve => setTimeout(resolve, 100));
      expect(mockCustomInstance).not.toHaveBeenCalled();
    });
  });

  describe('markAsRead branches', () => {
    it('deve retornar true quando markAsRead sucede', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ items: [{ id: '1', is_read: false }], total: 1, total_pages: 1 })
        .mockResolvedValueOnce({});

      const { wrapper } = createTestWrapper();
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

      const { wrapper } = createTestWrapper();
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

      const { wrapper } = createTestWrapper();
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

    const { wrapper } = createTestWrapper();
    const { result } = renderHook(() => useUnreadCount(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.total).toBe(0);
    expect(result.current.byType).toEqual({});
  });

  it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
    mockCustomInstance.mockRejectedValueOnce('erro string');

    const { wrapper } = createTestWrapper();
    const { result } = renderHook(() => useUnreadCount(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toBe('Erro ao carregar contagem');
  });

  it('não deve criar intervalo quando pollInterval é 0', async () => {
    mockCustomInstance.mockResolvedValueOnce({ total: 5 });

    const { wrapper } = createTestWrapper();
    renderHook(() => useUnreadCount(0), { wrapper });

    await waitFor(() => expect(mockCustomInstance).toHaveBeenCalledTimes(1));

    await new Promise(resolve => setTimeout(resolve, 200));
    expect(mockCustomInstance).toHaveBeenCalledTimes(1);
  });
});

describe('useAlerts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve usar query string vazia quando filters é undefined', async () => {
    mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0 });

    const { wrapper } = createTestWrapper();
    renderHook(() => useAlerts({ autoLoad: true }), { wrapper });

    await waitFor(() => {
      expect(mockCustomInstance).toHaveBeenCalledWith(expect.objectContaining({
        url: '/api/v1/operacional/comunicacao/alertas',
      }));
    });
  });

  it('deve usar query string quando filters é definido', async () => {
    mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0 });

    const { wrapper } = createTestWrapper();
    renderHook(() => useAlerts({ autoLoad: true, filters: { alert_type: 'warning' } }), { wrapper });

    await waitFor(() => {
      expect(mockCustomInstance).toHaveBeenCalledWith(expect.objectContaining({
        url: expect.stringContaining('alert_type=warning'),
      }));
    });
  });

  it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
    mockCustomInstance.mockRejectedValueOnce('erro string');

    const { wrapper } = createTestWrapper();
    const { result } = renderHook(() => useAlerts({ autoLoad: true, pollInterval: 0 }), { wrapper });

    await waitFor(() => {
      expect(result.current.error).toBe('Erro ao carregar alertas');
    });
  });

  it('deve retornar false quando acknowledge falha', async () => {
    mockCustomInstance
      .mockResolvedValueOnce({ items: [{ id: '1' }], total: 1 })
      .mockRejectedValueOnce(new Error('Falha'));

    const { wrapper } = createTestWrapper();
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

    const { wrapper } = createTestWrapper();
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

    const { wrapper } = createTestWrapper();
    const { result } = renderHook(() => useUserAlerts(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.criticalCount).toBe(2);
    expect(result.current.total).toBe(3);
  });

  it('deve ter criticalCount 0 quando alerts é vazio', async () => {
    mockCustomInstance.mockResolvedValueOnce({ items: [] });

    const { wrapper } = createTestWrapper();
    const { result } = renderHook(() => useUserAlerts(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.criticalCount).toBe(0);
    expect(result.current.total).toBe(0);
  });

  it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
    mockCustomInstance.mockRejectedValueOnce('erro string');

    const { wrapper } = createTestWrapper();
    const { result } = renderHook(() => useUserAlerts(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toBe('Erro ao carregar alertas');
  });

  it('deve retornar false quando acknowledge falha', async () => {
    mockCustomInstance
      .mockResolvedValueOnce({ items: [{ id: '1' }] })
      .mockRejectedValueOnce(new Error('Falha'));

    const { wrapper } = createTestWrapper();
    const { result } = renderHook(() => useUserAlerts(0), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    let success: boolean;
    await act(async () => {
      success = await result.current.acknowledge('1');
    });

    expect(success!).toBe(false);
  });
});
