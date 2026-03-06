import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mocks dos serviços
const mockList = vi.fn();
const mockGetById = vi.fn();
const mockGetStats = vi.fn();
const mockGetUserHistory = vi.fn();
const mockRecord = vi.fn();

vi.mock('@/services/audit/accessHistoryService', () => ({
  accessHistoryService: {
    list: (...args: unknown[]) => mockList(...args),
    getById: (...args: unknown[]) => mockGetById(...args),
    getStats: (...args: unknown[]) => mockGetStats(...args),
    getUserHistory: (...args: unknown[]) => mockGetUserHistory(...args),
    record: (...args: unknown[]) => mockRecord(...args),
  },
}));

import {
  accessHistoryKeys,
  useAccessHistory,
  useAccessHistoryItem,
  useAccessStats,
  useUserAccessHistory,
  useRecordAccess,
} from '../useAccessHistory';

const createTestQueryClient = () =>
  new QueryClient({ defaultOptions: { queries: { retry: false } } });

const createWrapper = () => {
  const queryClient = createTestQueryClient();
  function TestWrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  }
  return TestWrapper;
};

describe('accessHistoryKeys', () => {
  it('deve gerar query keys corretas', () => {
    expect(accessHistoryKeys.all).toEqual(['audit', 'access-history']);
    expect(accessHistoryKeys.lists()).toEqual(['audit', 'access-history', 'list']);
    expect(accessHistoryKeys.list()).toEqual(['audit', 'access-history', 'list', undefined]);
    expect(accessHistoryKeys.list({ user_id: 'u1' })).toEqual([
      'audit', 'access-history', 'list', { user_id: 'u1' },
    ]);
    expect(accessHistoryKeys.detail('abc')).toEqual([
      'audit', 'access-history', 'detail', 'abc',
    ]);
    expect(accessHistoryKeys.stats()).toEqual([
      'audit', 'access-history', 'stats', undefined, undefined,
    ]);
    expect(accessHistoryKeys.stats('2026-01-01', '2026-01-31')).toEqual([
      'audit', 'access-history', 'stats', '2026-01-01', '2026-01-31',
    ]);
    expect(accessHistoryKeys.userHistory('u1', 10)).toEqual([
      'audit', 'access-history', 'user', 'u1', 10,
    ]);
  });
});

describe('useAccessHistory', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve listar histórico de acessos sem filtros', async () => {
    const mockData = { items: [{ id: 'a1', user_id: 'u1' }], total: 1 };
    mockList.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useAccessHistory(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockList).toHaveBeenCalledWith(undefined);
  });

  it('deve listar histórico de acessos com filtros', async () => {
    const filters = { user_id: 'u1', page: 1 };
    const mockData = { items: [], total: 0 };
    mockList.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useAccessHistory(filters), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockList).toHaveBeenCalledWith(filters);
  });

  it('deve retornar erro quando a listagem falhar', async () => {
    mockList.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useAccessHistory(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toBe('Network error');
  });
});

describe('useAccessHistoryItem', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve buscar item específico quando accessId é fornecido', async () => {
    const mockItem = { id: 'a1', user_id: 'u1', action: 'LOGIN' };
    mockGetById.mockResolvedValueOnce(mockItem);

    const { result } = renderHook(() => useAccessHistoryItem('a1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockItem);
    expect(mockGetById).toHaveBeenCalledWith('a1');
  });

  it('deve não executar query quando accessId é string vazia (enabled: !!accessId = false)', () => {
    const { result } = renderHook(() => useAccessHistoryItem(''), {
      wrapper: createWrapper(),
    });

    // Quando disabled, status é 'pending' e fetchStatus é 'idle'
    expect(result.current.fetchStatus).toBe('idle');
    expect(mockGetById).not.toHaveBeenCalled();
  });

  it('deve retornar erro quando busca por ID falhar', async () => {
    mockGetById.mockRejectedValueOnce(new Error('Not found'));

    const { result } = renderHook(() => useAccessHistoryItem('bad-id'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toBe('Not found');
  });
});

describe('useAccessStats', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve buscar estatísticas sem datas', async () => {
    const mockStats = { total_accesses: 100, unique_users: 10 };
    mockGetStats.mockResolvedValueOnce(mockStats);

    const { result } = renderHook(() => useAccessStats(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockStats);
    expect(mockGetStats).toHaveBeenCalledWith(undefined, undefined);
  });

  it('deve buscar estatísticas com período definido', async () => {
    const mockStats = { total_accesses: 50, unique_users: 5 };
    mockGetStats.mockResolvedValueOnce(mockStats);

    const { result } = renderHook(() => useAccessStats('2026-01-01', '2026-01-31'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockGetStats).toHaveBeenCalledWith('2026-01-01', '2026-01-31');
  });

  it('deve retornar erro quando busca de stats falhar', async () => {
    mockGetStats.mockRejectedValueOnce(new Error('Server error'));

    const { result } = renderHook(() => useAccessStats(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useUserAccessHistory', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve buscar histórico do usuário com userId e limit padrão', async () => {
    const mockHistory = [{ id: 'a1', action: 'LOGIN' }];
    mockGetUserHistory.mockResolvedValueOnce(mockHistory);

    const { result } = renderHook(() => useUserAccessHistory('u1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockHistory);
    expect(mockGetUserHistory).toHaveBeenCalledWith('u1', 50);
  });

  it('deve buscar histórico do usuário com limit customizado', async () => {
    const mockHistory = [{ id: 'a1', action: 'LOGIN' }];
    mockGetUserHistory.mockResolvedValueOnce(mockHistory);

    const { result } = renderHook(() => useUserAccessHistory('u1', 10), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockGetUserHistory).toHaveBeenCalledWith('u1', 10);
  });

  it('deve não executar query quando userId é string vazia (enabled: !!userId = false)', () => {
    const { result } = renderHook(() => useUserAccessHistory(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.fetchStatus).toBe('idle');
    expect(mockGetUserHistory).not.toHaveBeenCalled();
  });
});

describe('useRecordAccess', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve registrar acesso com sucesso', async () => {
    const mockResponse = { id: 'a1', user_id: 'u1', action: 'LOGIN' };
    mockRecord.mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useRecordAccess(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({
        user_id: 'u1',
        action: 'LOGIN',
        resource_type: 'auth',
      } as Parameters<typeof result.current.mutateAsync>[0]);
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockRecord).toHaveBeenCalledWith({
      user_id: 'u1',
      action: 'LOGIN',
      resource_type: 'auth',
    });
  });

  it('deve retornar erro quando registro falhar', async () => {
    mockRecord.mockRejectedValueOnce(new Error('Forbidden'));

    const { result } = renderHook(() => useRecordAccess(), {
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
