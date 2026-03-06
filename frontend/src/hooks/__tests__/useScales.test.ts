import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import {
  useScales,
  useScale,
  useScaleOperations,
  useCurrentMonthScales,
  useScaleStats,
} from '../useScales';

// Mock do api-client
const mockCustomInstance = vi.fn();

vi.mock('@/lib/api-client', () => ({
  customInstance: (...args: unknown[]) => mockCustomInstance(...args),
}));

describe('useScales', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('useScales - Estado Inicial', () => {
    it('deve iniciar com valores padrão', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [],
        total: 0,
        total_pages: 0,
      });

      const { result } = renderHook(() => useScales());

      expect(result.current.isLoading).toBe(true);
      expect(result.current.scales).toEqual([]);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(20);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });

    it('deve aceitar valores iniciais', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useScales(2, 50, { status: 'draft' }));

      expect(result.current.page).toBe(2);
      expect(result.current.pageSize).toBe(50);
      expect(result.current.filters).toEqual({ status: 'draft' });
    });
  });

  describe('useScales - Fetch', () => {
    it('deve construir URL com parâmetros corretos', async () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      renderHook(() => useScales(2, 30, { status: 'pending_approval' }));

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledWith(
          expect.objectContaining({
            url: expect.stringContaining('/api/v1/operacional/scales'),
          })
        );
      });
    });
  });

  describe('useScales - Paginação', () => {
    it('deve atualizar página', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useScales());

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

      const { result } = renderHook(() => useScales());

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

      const { result } = renderHook(() => useScales(3, 50));

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        result.current.setFilters({ status: 'approved' });
      });

      await waitFor(() => {
        expect(result.current.page).toBe(1);
      });
    });
  });

  describe('useScales - Refresh', () => {
    it('deve recarregar escalas', async () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useScales());

      await waitFor(() => expect(result.current.isLoading).toBe(false));

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockCustomInstance).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('useScale', () => {
    it('deve retornar null quando id é null', async () => {
      const { result } = renderHook(() => useScale(null));

      expect(result.current.scale).toBeNull();
      expect(result.current.isLoading).toBe(false);
    });

    it('deve carregar escala quando id é fornecido', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '123',
        name: 'Escala Teste',
      });

      const { result } = renderHook(() => useScale('123'));

      await waitFor(() => {
        expect(result.current.scale).not.toBeNull();
      });

      expect(result.current.scale?.name).toBe('Escala Teste');
    });

    it('deve limpar dados quando id muda para null', async () => {
      mockCustomInstance.mockResolvedValue({
        id: '123',
        name: 'Escala Teste',
      });

      const { result, rerender } = renderHook(({ id }) => useScale(id), {
        initialProps: { id: '123' as string | null },
      });

      await waitFor(() => expect(result.current.scale).not.toBeNull());

      rerender({ id: null });

      expect(result.current.scale).toBeNull();
    });

    it('deve capturar erro ao carregar escala individual', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Not found'));

      const { result } = renderHook(() => useScale('999'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Erro ao carregar escala');
      expect(result.current.scale).toBeNull();
    });
  });

  describe('useScaleOperations', () => {
    it('deve gerar escala', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '1',
        status: 'draft',
      });

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.generateScale({
          post_id: 'post-1',
          month: 1,
          year: 2026,
        } as any);
      });

      expect(scale).toEqual({ id: '1', status: 'draft' });
      expect(mockCustomInstance).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/api/v1/operacional/scales/generate',
          method: 'POST',
        })
      );
    });

    it('deve enviar para aprovação', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '1',
        status: 'pending_approval',
      });

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.submitForApproval('1');
      });

      expect(scale).toEqual({ id: '1', status: 'pending_approval' });
    });

    it('deve aprovar escala', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '1',
        status: 'approved',
      });

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.approveScale('1', 'Aprovado');
      });

      expect(scale).toEqual({ id: '1', status: 'approved' });
    });

    it('deve publicar escala', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '1',
        status: 'published',
      });

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.publishScale('1', true);
      });

      expect(scale).toEqual({ id: '1', status: 'published' });
    });

    it('deve deletar escala', async () => {
      mockCustomInstance.mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useScaleOperations());

      let deleted: boolean;
      await act(async () => {
        deleted = await result.current.deleteScale('1');
      });

      await waitFor(() => {
        expect(deleted).toBe(true);
      });
    });

    it('deve retornar null e setar erro quando operação falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.generateScale({} as any);
      });

      await waitFor(() => {
        expect(scale).toBeNull();
      });
      expect(result.current.error).toBe('Failed');
    });

    it('deve usar mensagem padrão quando generateScale falha com erro não-Error', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.generateScale({} as any);
      });

      await waitFor(() => {
        expect(scale).toBeNull();
      });
      expect(result.current.error).toBe('Erro ao gerar escala');
    });

    it('deve retornar null quando submitForApproval falha com Error', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Submit failed'));

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.submitForApproval('1');
      });

      await waitFor(() => {
        expect(scale).toBeNull();
      });
      expect(result.current.error).toBe('Submit failed');
    });

    it('deve usar mensagem padrão quando submitForApproval falha com erro não-Error', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.submitForApproval('1');
      });

      await waitFor(() => {
        expect(scale).toBeNull();
      });
      expect(result.current.error).toBe('Erro ao enviar para aprovação');
    });

    it('deve refletir estado de loading', async () => {
      mockCustomInstance.mockImplementation(() => new Promise(() => {}));

      const { result } = renderHook(() => useScaleOperations());

      // Iniciar operação
      act(() => {
        result.current.generateScale({} as any);
      });

      expect(result.current.isLoading).toBe(true);
    });
  });

  describe('useCurrentMonthScales', () => {
    it('deve carregar escalas do mês atual', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [{ id: '1', month: 1 }],
        total: 1,
      });

      const { result } = renderHook(() => useCurrentMonthScales());

      await waitFor(() => {
        expect(result.current.scales).toHaveLength(1);
      });

      expect(mockCustomInstance).toHaveBeenCalledWith(
        expect.objectContaining({
          url: expect.stringContaining('is_current_month'),
        })
      );
    });
  });

  describe('useCurrentMonthScales - Error Handling', () => {
    it('deve capturar erro ao carregar escalas do mês', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Month fetch failed'));

      const { result } = renderHook(() => useCurrentMonthScales());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Erro ao carregar escalas');
      expect(result.current.scales).toEqual([]);
    });
  });

  describe('useScaleStats', () => {
    it('deve carregar estatísticas', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        total: 50,
        by_status: { draft: 10, published: 40 },
      });

      const { result } = renderHook(() => useScaleStats());

      await waitFor(() => {
        expect(result.current.stats).not.toBeNull();
      });

      expect(result.current.stats?.total).toBe(50);
    });

    it('deve capturar erro ao carregar estatísticas', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => useScaleStats());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Erro ao carregar estatísticas');
    });
  });

  describe('Error Handling', () => {
    it('deve capturar erro ao carregar escalas', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useScales());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Erro ao carregar escalas');
    });
  });

  describe('useScaleOperations - Operações adicionais', () => {
    it('deve retornar null quando approveScale falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.approveScale('1', 'Notas');
      });

      await waitFor(() => {
        expect(scale).toBeNull();
      });
      expect(result.current.error).toBe('Failed');
    });

    it('deve retornar null quando publishScale falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Publish failed'));

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.publishScale('1', false);
      });

      await waitFor(() => {
        expect(scale).toBeNull();
      });
      expect(result.current.error).toBe('Publish failed');
    });

    it('deve retornar false quando deleteScale falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Delete failed'));

      const { result } = renderHook(() => useScaleOperations());

      let deleted: boolean;
      await act(async () => {
        deleted = await result.current.deleteScale('1');
      });

      await waitFor(() => {
        expect(deleted).toBe(false);
      });
      expect(result.current.error).toBe('Delete failed');
    });

    it('deve retornar null e usar mensagem padrão quando approveScale falha com erro não-Error', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.approveScale('1', 'Notas');
      });

      await waitFor(() => {
        expect(scale).toBeNull();
      });
      expect(result.current.error).toBe('Erro ao aprovar escala');
    });

    it('deve retornar null e usar mensagem padrão quando publishScale falha com erro não-Error', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useScaleOperations());

      let scale: unknown;
      await act(async () => {
        scale = await result.current.publishScale('1', true);
      });

      await waitFor(() => {
        expect(scale).toBeNull();
      });
      expect(result.current.error).toBe('Erro ao publicar escala');
    });

    it('deve retornar false e usar mensagem padrão quando deleteScale falha com erro não-Error', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useScaleOperations());

      let deleted: boolean;
      await act(async () => {
        deleted = await result.current.deleteScale('1');
      });

      await waitFor(() => {
        expect(deleted).toBe(false);
      });
      expect(result.current.error).toBe('Erro ao deletar escala');
    });
  });

  describe('useScaleStats - Error Handling', () => {
    it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useScaleStats());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Erro ao carregar estatísticas');
    });
  });
});
