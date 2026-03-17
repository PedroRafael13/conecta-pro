import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mocks dos serviços
const mockListLogs = vi.fn();
const mockGetLog = vi.fn();
const mockGetStats = vi.fn();
const mockCreateLog = vi.fn();
const mockCompleteReview = vi.fn();

vi.mock('@/services/audit/auditLogService', () => ({
  auditLogService: {
    listLogs: (...args: unknown[]) => mockListLogs(...args),
    getLog: (...args: unknown[]) => mockGetLog(...args),
    getStats: (...args: unknown[]) => mockGetStats(...args),
    createLog: (...args: unknown[]) => mockCreateLog(...args),
    completeReview: (...args: unknown[]) => mockCompleteReview(...args),
  },
}));

import {
  auditLogKeys,
  useAuditLogs,
  useAuditLog,
  useAuditStats,
  useCreateAuditLog,
  useCompleteReview,
} from '../useAuditLogs';

const createTestQueryClient = () =>
  new QueryClient({ defaultOptions: { queries: { retry: false } } });

const createWrapper = () => {
  const queryClient = createTestQueryClient();
  function TestWrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  }
  return TestWrapper;
};

describe('auditLogKeys', () => {
  it('deve gerar query keys corretas', () => {
    expect(auditLogKeys.all).toEqual(['audit', 'logs']);
    expect(auditLogKeys.lists()).toEqual(['audit', 'logs', 'list']);
    expect(auditLogKeys.list()).toEqual(['audit', 'logs', 'list', undefined]);
    expect(auditLogKeys.list({ action: 'LOGIN' })).toEqual([
      'audit', 'logs', 'list', { action: 'LOGIN' },
    ]);
    expect(auditLogKeys.details()).toEqual(['audit', 'logs', 'detail']);
    expect(auditLogKeys.detail('log-1')).toEqual(['audit', 'logs', 'detail', 'log-1']);
    expect(auditLogKeys.stats()).toEqual(['audit', 'logs', 'stats', undefined, undefined]);
    expect(auditLogKeys.stats('2026-01-01', '2026-01-31')).toEqual([
      'audit', 'logs', 'stats', '2026-01-01', '2026-01-31',
    ]);
  });
});

describe('useAuditLogs', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve listar logs de auditoria sem filtros', async () => {
    const mockData = { items: [{ id: 'l1', action: 'LOGIN' }], total: 1 };
    mockListLogs.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useAuditLogs(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockListLogs).toHaveBeenCalledWith(undefined);
  });

  it('deve listar logs de auditoria com filtros', async () => {
    const filters = { action: 'LOGIN', user_id: 'u1' };
    const mockData = { items: [], total: 0 };
    mockListLogs.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useAuditLogs(filters), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockListLogs).toHaveBeenCalledWith(filters);
  });

  it('deve retornar erro quando listagem falhar', async () => {
    mockListLogs.mockRejectedValueOnce(new Error('Unauthorized'));

    const { result } = renderHook(() => useAuditLogs(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toBe('Unauthorized');
  });
});

describe('useAuditLog', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve buscar log específico por ID', async () => {
    const mockLog = { id: 'l1', action: 'LOGIN', user_id: 'u1' };
    mockGetLog.mockResolvedValueOnce(mockLog);

    const { result } = renderHook(() => useAuditLog('l1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockLog);
    expect(mockGetLog).toHaveBeenCalledWith('l1');
  });

  it('deve não executar query quando logId é string vazia (enabled: !!logId = false)', () => {
    const { result } = renderHook(() => useAuditLog(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.fetchStatus).toBe('idle');
    expect(mockGetLog).not.toHaveBeenCalled();
  });

  it('deve retornar erro quando busca por ID falhar', async () => {
    mockGetLog.mockRejectedValueOnce(new Error('Not found'));

    const { result } = renderHook(() => useAuditLog('bad-id'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toBe('Not found');
  });
});

describe('useAuditStats', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve buscar estatísticas de auditoria sem período', async () => {
    const mockStats = { total_logs: 200, logins: 50 };
    mockGetStats.mockResolvedValueOnce(mockStats);

    const { result } = renderHook(() => useAuditStats(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockStats);
    expect(mockGetStats).toHaveBeenCalledWith(undefined, undefined);
  });

  it('deve buscar estatísticas com período definido', async () => {
    const mockStats = { total_logs: 100 };
    mockGetStats.mockResolvedValueOnce(mockStats);

    const { result } = renderHook(
      () => useAuditStats('2026-01-01', '2026-01-31'),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockGetStats).toHaveBeenCalledWith('2026-01-01', '2026-01-31');
  });

  it('deve retornar erro quando busca de stats falhar', async () => {
    mockGetStats.mockRejectedValueOnce(new Error('Server error'));

    const { result } = renderHook(() => useAuditStats(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useCreateAuditLog', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve criar log de auditoria com sucesso', async () => {
    const mockResponse = { id: 'l1', action: 'LOGIN', user_id: 'u1' };
    mockCreateLog.mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useCreateAuditLog(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({
        action: 'LOGIN',
        user_id: 'u1',
        resource_type: 'auth',
      } as unknown as Parameters<typeof result.current.mutateAsync>[0]);
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockCreateLog).toHaveBeenCalledWith({
      action: 'LOGIN',
      user_id: 'u1',
      resource_type: 'auth',
    });
  });

  it('deve retornar erro quando criação de log falhar', async () => {
    mockCreateLog.mockRejectedValueOnce(new Error('Forbidden'));

    const { result } = renderHook(() => useCreateAuditLog(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      try {
        await result.current.mutateAsync({} as Parameters<typeof result.current.mutateAsync>[0]);
      } catch {
        // erro esperado
      }
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toBe('Forbidden');
  });
});

describe('useCompleteReview', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve completar revisão de log com sucesso', async () => {
    const mockResponse = { id: 'l1', action: 'LOGIN', reviewed: true };
    mockCompleteReview.mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useCompleteReview(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({ logId: 'l1', notes: 'Revisado OK' });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockCompleteReview).toHaveBeenCalledWith('l1', 'Revisado OK');
  });

  it('deve completar revisão sem notas (notes é opcional)', async () => {
    const mockResponse = { id: 'l2', action: 'LOGOUT', reviewed: true };
    mockCompleteReview.mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useCompleteReview(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({ logId: 'l2' });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockCompleteReview).toHaveBeenCalledWith('l2', undefined);
  });

  it('deve retornar erro quando revisão falhar', async () => {
    mockCompleteReview.mockRejectedValueOnce(new Error('Not found'));

    const { result } = renderHook(() => useCompleteReview(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      try {
        await result.current.mutateAsync({ logId: 'bad-id' });
      } catch {
        // erro esperado
      }
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});
