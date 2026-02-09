import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useReimbursements,
  useReimbursementStats,
  useReimbursementDetail,
  usePendingApprovals,
  useReimbursementCategories,
  useReadyForPayment,
} from '../useReimbursement';
import React from 'react';

// Mocks
const mockRefetch = vi.fn();

vi.mock('@/hooks/reimbursement', () => ({
  useReimbursementRequests: vi.fn((params, options) => ({
    data: options?.enabled !== false && params ? {
      items: [{ id: '1', amount: 100, status: 'pending' }],
      total: 1,
      total_pages: 1,
    } : undefined,
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  useMyReimbursementRequests: vi.fn((params, options) => ({
    data: options?.enabled !== false && params ? {
      items: [{ id: '2', amount: 200 }],
      total: 1,
      total_pages: 1,
    } : { items: [], total: 0, total_pages: 0 },
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  useReimbursementRequest: vi.fn((id, options) => ({
    data: options?.enabled !== false ? { id, amount: 100 } : undefined,
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  useReimbursementStats: vi.fn((myOnly, options) => ({
    data: options?.enabled !== false ? { total: 10, pending: 3 } : undefined,
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  useExpenseCategories: vi.fn(() => ({
    data: [{ id: '1', name: 'Transporte' }, { id: '2', name: 'Alimentação' }],
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  usePendingReimbursementApprovals: vi.fn((params, options) => ({
    data: options?.enabled !== false ? {
      items: [{ id: '1', status: 'pending_approval' }],
      total: 1,
      total_pages: 1,
    } : undefined,
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  useReadyForPaymentReimbursements: vi.fn((params, options) => ({
    data: options?.enabled !== false ? {
      items: [{ id: '1', status: 'approved' }],
      total: 1,
      total_pages: 1,
    } : undefined,
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
}));

describe('useReimbursement', () => {
  let queryClient: QueryClient;

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    React.createElement(QueryClientProvider, { client: queryClient }, children)
  );

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  describe('useReimbursements', () => {
    it('deve carregar todos os reembolsos por padrão', () => {
      const { result } = renderHook(() => useReimbursements(), { wrapper });

      expect(result.current.requests).toHaveLength(1);
      expect(result.current.total).toBe(1);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(20);
    });

    it('deve carregar apenas meus reembolsos quando myOnly é true', () => {
      const { result } = renderHook(() => useReimbursements({ myOnly: true }), { wrapper });

      expect(result.current.requests).toHaveLength(1);
    });

    it('deve aplicar filtros', () => {
      const { result } = renderHook(
        () => useReimbursements({ initialPageSize: 50 }),
        { wrapper }
      );

      expect(result.current.pageSize).toBe(50);
    });

    it('deve atualizar filtros e resetar página', async () => {
      const { result } = renderHook(() => useReimbursements(), { wrapper });

      await act(async () => {
        result.current.setPage(3);
      });

      await waitFor(() => {
        expect(result.current.page).toBe(3);
      });

      await act(async () => {
        result.current.setFilters({ status: 'aprovado' });
      });

      await waitFor(() => {
        expect(result.current.filters).toEqual({ status: 'aprovado' });
        expect(result.current.page).toBe(1);
      });
    });

    it('deve chamar refresh', async () => {
      const { result } = renderHook(() => useReimbursements(), { wrapper });

      await act(async () => {
        result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('useReimbursementStats', () => {
    it('deve carregar estatísticas gerais', () => {
      const { result } = renderHook(() => useReimbursementStats(), { wrapper });

      expect(result.current.stats).toEqual({ total: 10, pending: 3 });
      expect(result.current.isLoading).toBe(false);
    });

    it('deve carregar estatísticas pessoais quando myOnly é true', () => {
      const { result } = renderHook(() => useReimbursementStats({ myOnly: true }), { wrapper });

      expect(result.current.stats).toEqual({ total: 10, pending: 3 });
    });

    it('deve chamar refresh', async () => {
      const { result } = renderHook(() => useReimbursementStats(), { wrapper });

      await act(async () => {
        result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('useReimbursementDetail', () => {
    it('deve retornar null quando id é null', () => {
      const { result } = renderHook(() => useReimbursementDetail(null), { wrapper });

      expect(result.current.request).toBeNull();
      expect(result.current.isLoading).toBe(false);
    });

    it('deve carregar detalhes quando id é fornecido', () => {
      const { result } = renderHook(() => useReimbursementDetail('123'), { wrapper });

      expect(result.current.request).toEqual({ id: '123', amount: 100 });
    });

    it('deve chamar refresh', async () => {
      const { result } = renderHook(() => useReimbursementDetail('123'), { wrapper });

      await act(async () => {
        result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('usePendingApprovals', () => {
    it('deve carregar aprovações pendentes', () => {
      const { result } = renderHook(() => usePendingApprovals(), { wrapper });

      expect(result.current.requests).toHaveLength(1);
      expect(result.current.total).toBe(1);
      expect(result.current.page).toBe(1);
    });

    it('deve aceitar nível de aprovação inicial', () => {
      const { result } = renderHook(
        () => usePendingApprovals({ approvalLevel: 'manager' }),
        { wrapper }
      );

      expect(result.current.approvalLevel).toBe('manager');
    });

    it('deve atualizar nível de aprovação', async () => {
      const { result } = renderHook(() => usePendingApprovals(), { wrapper });

      await act(async () => {
        result.current.setApprovalLevel('director');
      });

      await waitFor(() => {
        expect(result.current.approvalLevel).toBe('director');
        expect(result.current.page).toBe(1);
      });
    });

    it('deve atualizar página', async () => {
      const { result } = renderHook(() => usePendingApprovals(), { wrapper });

      await act(async () => {
        result.current.setPage(2);
      });

      await waitFor(() => {
        expect(result.current.page).toBe(2);
      });
    });
  });

  describe('useReimbursementCategories', () => {
    it('deve carregar categorias', () => {
      const { result } = renderHook(() => useReimbursementCategories(), { wrapper });

      expect(result.current.categories).toHaveLength(2);
      expect(result.current.categories[0]?.name).toBe('Transporte');
      expect(result.current.isLoading).toBe(false);
    });

    it('deve chamar refresh', async () => {
      const { result } = renderHook(() => useReimbursementCategories(), { wrapper });

      await act(async () => {
        result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('useReadyForPayment', () => {
    it('deve carregar reembolsos prontos para pagamento', () => {
      const { result } = renderHook(() => useReadyForPayment(), { wrapper });

      expect(result.current.requests).toHaveLength(1);
      expect(result.current.total).toBe(1);
      expect(result.current.page).toBe(1);
    });

    it('deve aceitar pageSize inicial', () => {
      const { result } = renderHook(
        () => useReadyForPayment({ initialPageSize: 50 }),
        { wrapper }
      );

      expect(result.current.pageSize).toBe(50);
    });

    it('deve atualizar página', async () => {
      const { result } = renderHook(() => useReadyForPayment(), { wrapper });

      await act(async () => {
        result.current.setPage(3);
      });

      await waitFor(() => {
        expect(result.current.page).toBe(3);
      });
    });
  });

  describe('Error Handling', () => {
    it('deve retornar estado de erro quando configurado', () => {
      // Verifica que o hook retorna estrutura correta para erros
      const { result } = renderHook(() => useReimbursements(), { wrapper });

      // O hook deve retornar uma estrutura válida
      expect(result.current).toHaveProperty('requests');
      expect(result.current).toHaveProperty('error');
      expect(Array.isArray(result.current.requests)).toBe(true);
    });
  });
});
