import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mocks dos serviços
const mockList = vi.fn();
const mockGetById = vi.fn();
const mockCreate = vi.fn();
const mockUpdate = vi.fn();
const mockActivate = vi.fn();
const mockDelete = vi.fn();

vi.mock('@/services/audit/complianceRuleService', () => ({
  complianceRuleService: {
    list: (...args: unknown[]) => mockList(...args),
    getById: (...args: unknown[]) => mockGetById(...args),
    create: (...args: unknown[]) => mockCreate(...args),
    update: (...args: unknown[]) => mockUpdate(...args),
    activate: (...args: unknown[]) => mockActivate(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
}));

import {
  complianceRuleKeys,
  useComplianceRules,
  useComplianceRule,
  useCreateComplianceRule,
  useUpdateComplianceRule,
  useActivateRule,
  useDeleteRule,
} from '../useComplianceRules';

const createTestQueryClient = () =>
  new QueryClient({ defaultOptions: { queries: { retry: false } } });

const createWrapper = () => {
  const queryClient = createTestQueryClient();
  function TestWrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  }
  return TestWrapper;
};

describe('complianceRuleKeys', () => {
  it('deve gerar query keys corretas', () => {
    expect(complianceRuleKeys.all).toEqual(['audit', 'compliance-rules']);
    expect(complianceRuleKeys.lists()).toEqual(['audit', 'compliance-rules', 'list']);
    expect(complianceRuleKeys.list()).toEqual(['audit', 'compliance-rules', 'list', undefined]);
    expect(complianceRuleKeys.list({ framework: 'LGPD' })).toEqual([
      'audit', 'compliance-rules', 'list', { framework: 'LGPD' },
    ]);
    expect(complianceRuleKeys.details()).toEqual(['audit', 'compliance-rules', 'detail']);
    expect(complianceRuleKeys.detail('r1')).toEqual(['audit', 'compliance-rules', 'detail', 'r1']);
  });
});

describe('useComplianceRules', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve listar regras sem filtros', async () => {
    const mockData = { items: [{ id: 'r1', name: 'Regra LGPD' }], total: 1 };
    mockList.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useComplianceRules(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockList).toHaveBeenCalledWith(undefined);
  });

  it('deve listar regras com filtros', async () => {
    const filters = { framework: 'LGPD', is_active: true };
    const mockData = { items: [], total: 0 };
    mockList.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useComplianceRules(filters), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockList).toHaveBeenCalledWith(filters);
  });

  it('deve retornar erro quando listagem falhar', async () => {
    mockList.mockRejectedValueOnce(new Error('Forbidden'));

    const { result } = renderHook(() => useComplianceRules(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useComplianceRule', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve buscar regra específica por ID', async () => {
    const mockRule = { id: 'r1', name: 'Regra LGPD', framework: 'LGPD' };
    mockGetById.mockResolvedValueOnce(mockRule);

    const { result } = renderHook(() => useComplianceRule('r1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockRule);
  });

  it('deve não executar query quando ruleId é string vazia (enabled: !!ruleId = false)', () => {
    const { result } = renderHook(() => useComplianceRule(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.fetchStatus).toBe('idle');
    expect(mockGetById).not.toHaveBeenCalled();
  });

  it('deve retornar erro quando busca por ID falhar', async () => {
    mockGetById.mockRejectedValueOnce(new Error('Not found'));

    const { result } = renderHook(() => useComplianceRule('invalid'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toBe('Not found');
  });
});

describe('useCreateComplianceRule', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve criar regra de compliance com sucesso', async () => {
    const newRule = { id: 'r1', name: 'Nova Regra', framework: 'ISO27001' };
    mockCreate.mockResolvedValueOnce(newRule);

    const { result } = renderHook(() => useCreateComplianceRule(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({
        name: 'Nova Regra',
        framework: 'ISO27001',
      } as unknown as Parameters<typeof result.current.mutateAsync>[0]);
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockCreate).toHaveBeenCalledWith({ name: 'Nova Regra', framework: 'ISO27001' });
  });

  it('deve retornar erro quando criação falhar', async () => {
    mockCreate.mockRejectedValueOnce(new Error('Validation error'));

    const { result } = renderHook(() => useCreateComplianceRule(), {
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
  });
});

describe('useUpdateComplianceRule', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve atualizar regra de compliance com sucesso', async () => {
    const updated = { id: 'r1', name: 'Regra Atualizada', framework: 'LGPD' };
    mockUpdate.mockResolvedValueOnce(updated);

    const { result } = renderHook(() => useUpdateComplianceRule(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({
        ruleId: 'r1',
        data: { name: 'Regra Atualizada' } as Parameters<typeof result.current.mutateAsync>[0]['data'],
      });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockUpdate).toHaveBeenCalledWith('r1', { name: 'Regra Atualizada' });
  });

  it('deve retornar erro quando atualização falhar', async () => {
    mockUpdate.mockRejectedValueOnce(new Error('Not found'));

    const { result } = renderHook(() => useUpdateComplianceRule(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      try {
        await result.current.mutateAsync({
          ruleId: 'bad-id',
          data: {} as Parameters<typeof result.current.mutateAsync>[0]['data'],
        });
      } catch {
        // erro esperado
      }
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useActivateRule', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve ativar regra com sucesso', async () => {
    const activated = { id: 'r1', is_active: true };
    mockActivate.mockResolvedValueOnce(activated);

    const { result } = renderHook(() => useActivateRule(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync('r1');
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockActivate).toHaveBeenCalledWith('r1');
  });

  it('deve retornar erro quando ativação falhar', async () => {
    mockActivate.mockRejectedValueOnce(new Error('Rule not found'));

    const { result } = renderHook(() => useActivateRule(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      try {
        await result.current.mutateAsync('bad-id');
      } catch {
        // erro esperado
      }
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useDeleteRule', () => {
  beforeEach(() => vi.clearAllMocks());

  it('deve deletar regra com sucesso', async () => {
    mockDelete.mockResolvedValueOnce(undefined);

    const { result } = renderHook(() => useDeleteRule(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync('r1');
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockDelete).toHaveBeenCalledWith('r1');
  });

  it('deve retornar erro quando exclusão falhar', async () => {
    mockDelete.mockRejectedValueOnce(new Error('Cannot delete active rule'));

    const { result } = renderHook(() => useDeleteRule(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      try {
        await result.current.mutateAsync('r1');
      } catch {
        // erro esperado
      }
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toBe('Cannot delete active rule');
  });
});
