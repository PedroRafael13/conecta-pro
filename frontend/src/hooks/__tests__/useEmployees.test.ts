import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useEmployees } from '../useEmployees';

// Mock do api-client
const mockCustomInstance = vi.fn();

vi.mock('@/lib/api-client', () => ({
  customInstance: (...args: unknown[]) => mockCustomInstance(...args),
}));

describe('useEmployees', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Estado Inicial', () => {
    it('deve iniciar com valores padrão', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [],
        total: 0,
        page: 1,
        page_size: 100,
        total_pages: 0,
      });

      const { result } = renderHook(() => useEmployees());

      expect(result.current.isLoading).toBe(true);
      expect(result.current.employees).toEqual([]);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(100);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });

    it('deve aceitar opções personalizadas', () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() =>
        useEmployees({
          initialPage: 2,
          initialPageSize: 50,
          initialStatus: 'inactive',
        })
      );

      expect(result.current.page).toBe(2);
      expect(result.current.pageSize).toBe(50);
    });

    it('não deve carregar quando autoLoad é false', () => {
      const { result } = renderHook(() => useEmployees({ autoLoad: false }));

      expect(result.current.isLoading).toBe(false);
      expect(mockCustomInstance).not.toHaveBeenCalled();
    });
  });

  describe('Fetch de Dados', () => {
    it('deve mapear dados do backend corretamente', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [
          { id: '1', nome: 'John Doe', email: 'john@example.com', matricula: '123', status: 'ativo' },
          { id: '2', nome: 'Jane Smith', email: null, matricula: null, status: null },
        ],
        total: 2,
        page: 1,
        page_size: 100,
        total_pages: 1,
      });

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => {
        expect(result.current.employees).toHaveLength(2);
      });

      expect(result.current.employees[0]).toEqual({
        id: '1',
        full_name: 'John Doe',
        name: 'John Doe',
        email: 'john@example.com',
        registration: '123',
        status: 'ativo',
      });

      expect(result.current.employees[1]).toEqual({
        id: '2',
        full_name: 'Jane Smith',
        name: 'Jane Smith',
        email: undefined,
        registration: undefined,
        status: undefined,
      });
    });

    it('deve lidar com resposta em array', async () => {
      mockCustomInstance.mockResolvedValueOnce([
        { id: '1', nome: 'John' },
        { id: '2', nome: 'Jane' },
      ]);

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => {
        expect(result.current.employees).toHaveLength(2);
      });

      expect(result.current.total).toBe(2);
      expect(result.current.totalPages).toBe(1);
    });

    it('deve passar parâmetros corretos para a API', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      renderHook(() => useEmployees({ initialPage: 2, initialPageSize: 50 }));

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledWith(
          expect.objectContaining({
            url: '/api/v1/operacional/employees/',
            method: 'GET',
            params: { page: 2, page_size: 50, status: 'ativo' },
          })
        );
      });
    });
  });

  describe('Error Handling', () => {
    it('deve capturar erro quando requisição falhar', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Network error');
      expect(result.current.employees).toEqual([]);
    });

    it('deve retornar erro genérico quando não há mensagem', async () => {
      mockCustomInstance.mockRejectedValueOnce('Unknown error');

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Erro ao carregar funcionários');
    });
  });

  describe('Paginação', () => {
    it('deve atualizar página', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      act(() => {
        result.current.setPage(3);
      });

      expect(result.current.page).toBe(3);
    });

    it('deve recarregar dados quando página muda', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      act(() => {
        result.current.setPage(2);
      });

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Refresh', () => {
    it('deve recarregar dados quando refresh é chamado', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await result.current.refresh();

      expect(mockCustomInstance).toHaveBeenCalledTimes(2);
    });
  });

  describe('Resposta Inválida', () => {
    it('deve lidar com resposta inválida', async () => {
      mockCustomInstance.mockResolvedValueOnce(null);

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.employees).toEqual([]);
      expect(result.current.total).toBe(0);
    });

    it('deve lidar com resposta vazia/undefined', async () => {
      mockCustomInstance.mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.employees).toEqual([]);
      expect(result.current.total).toBe(0);
    });

    it('deve mapear employee com nome vazio como undefined', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [
          { id: '1', nome: '', email: '', matricula: '', status: '' },
        ],
        total: 1,
        page: 1,
        page_size: 100,
        total_pages: 1,
      });

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => {
        expect(result.current.employees).toHaveLength(1);
      });

      // nome falsy ('') => || undefined
      expect(result.current.employees[0]?.full_name).toBeUndefined();
      expect(result.current.employees[0]?.name).toBeUndefined();
      expect(result.current.employees[0]?.email).toBeUndefined();
      expect(result.current.employees[0]?.registration).toBeUndefined();
      expect(result.current.employees[0]?.status).toBeUndefined();
    });

    it('deve usar fallback quando response.items é undefined', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        total: 5,
        page: 1,
        page_size: 100,
        total_pages: 1,
        // items ausente
      });

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // normalizeEmployeesResponse vai entrar no fallback pois payload.items não é array
      expect(result.current.employees).toEqual([]);
      expect(result.current.total).toBe(0);
    });

    it('deve lidar com resposta em array direto sem paginação', async () => {
      mockCustomInstance.mockResolvedValueOnce([
        { id: '1', nome: 'John' },
        { id: '2', nome: 'Jane' },
      ]);

      const { result } = renderHook(() => useEmployees());

      await waitFor(() => {
        expect(result.current.employees).toHaveLength(2);
      });

      expect(result.current.total).toBe(2);
      expect(result.current.totalPages).toBe(1);
      expect(result.current.employees[0]?.full_name).toBe('John');
    });
  });
});
