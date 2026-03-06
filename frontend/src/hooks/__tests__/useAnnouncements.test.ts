import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useAnnouncements,
  useUnreadAnnouncements,
  useAnnouncementDetail,
  useAnnouncementReadStats,
  useAnnouncementMutations,
} from '../useAnnouncements';
import type { AnnouncementPriority, AnnouncementStatus } from '@/lib/services/announcements';
import React from 'react';

// Mock do api-client
const mockCustomInstance = vi.fn();

vi.mock('@/lib/api-client', () => ({
  customInstance: (...args: unknown[]) => mockCustomInstance(...args),
}));

describe('useAnnouncements', () => {
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

  describe('useAnnouncements - Estado Inicial', () => {
    it('deve retornar valores iniciais', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [],
        total: 0,
        total_pages: 0,
      });

      const { result } = renderHook(() => useAnnouncements(), { wrapper });

      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.announcements).toEqual([]);
      expect(result.current.total).toBe(0);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(10);
    });

    it('deve aceitar opções personalizadas', () => {
      mockCustomInstance.mockResolvedValueOnce({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(
        () =>
          useAnnouncements({
            initialPageSize: 25,
            autoLoad: false,
            initialFilters: { priority: 'alta' as AnnouncementPriority },
          }),
        { wrapper }
      );

      expect(result.current.pageSize).toBe(25);
      expect(result.current.filters).toEqual({ priority: 'alta' });
    });
  });

  describe('useAnnouncements - Paginação e Filtros', () => {
    it('deve atualizar página', () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(() => useAnnouncements(), { wrapper });

      act(() => {
        result.current.setPage(3);
      });

      expect(result.current.page).toBe(3);
    });

    it('deve atualizar filtros e resetar página', () => {
      mockCustomInstance.mockResolvedValue({ items: [], total: 0, total_pages: 0 });

      const { result } = renderHook(
        () => useAnnouncements({ initialFilters: { status: 'rascunho' as AnnouncementStatus } }),
        { wrapper }
      );

      act(() => {
        result.current.setFilters({ status: 'publicado' as AnnouncementStatus });
      });

      expect(result.current.filters).toEqual({ status: 'publicado' });
      expect(result.current.page).toBe(1);
    });
  });

  describe('useUnreadAnnouncements', () => {
    it('deve carregar apenas comunicados não lidos', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        items: [{ id: '1', title: 'Unread 1' }],
        total: 1,
        total_pages: 1,
      });

      const { result } = renderHook(() => useUnreadAnnouncements(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.announcements).toHaveLength(1);
      expect(mockCustomInstance).toHaveBeenCalledWith(
        expect.objectContaining({
          url: expect.stringContaining('/nao-lidos'),
        })
      );
    });
  });

  describe('useAnnouncementDetail', () => {
    it('deve retornar null quando id é null', () => {
      const { result } = renderHook(() => useAnnouncementDetail(null), { wrapper });

      expect(result.current.announcement).toBeNull();
      expect(result.current.isLoading).toBe(false);
    });

    it('deve carregar detalhes quando id é fornecido', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        id: '1',
        title: 'Test Announcement',
        content: 'Content',
      });

      const { result } = renderHook(() => useAnnouncementDetail('1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.announcement).toEqual({
        id: '1',
        title: 'Test Announcement',
        content: 'Content',
      });
    });
  });

  describe('useAnnouncementReadStats', () => {
    it('deve carregar estatísticas de leitura', async () => {
      mockCustomInstance.mockResolvedValueOnce({
        total_recipients: 10,
        read_count: 7,
        read_percentage: 70,
      });

      const { result } = renderHook(() => useAnnouncementReadStats('1'), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.stats).toEqual({
        total_recipients: 10,
        read_count: 7,
        read_percentage: 70,
      });
    });
  });

  describe('useAnnouncementMutations', () => {
    it('deve criar comunicado', async () => {
      mockCustomInstance.mockResolvedValueOnce({ id: '1', title: 'New' });

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const created = await result.current.createAnnouncement({
        title: 'New',
        content: 'Content',
      } as any);

      expect(created).toEqual({ id: '1', title: 'New' });
    });

    it('deve retornar null quando criação falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const created = await result.current.createAnnouncement({
        title: 'New',
      } as any);

      expect(created).toBeNull();
    });

    it('deve atualizar comunicado', async () => {
      mockCustomInstance.mockResolvedValueOnce({ id: '1', title: 'Updated' });

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const updated = await result.current.updateAnnouncement('1', { title: 'Updated' } as any);

      expect(updated).toEqual({ id: '1', title: 'Updated' });
    });

    it('deve retornar null quando update falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Update failed'));

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const updated = await result.current.updateAnnouncement('1', { title: 'Updated' } as any);

      expect(updated).toBeNull();
    });

    it('deve publicar comunicado', async () => {
      mockCustomInstance.mockResolvedValueOnce({ id: '1', status: 'published' });

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const published = await result.current.publishAnnouncement('1');

      expect(published).toEqual({ id: '1', status: 'published' });
    });

    it('deve retornar null quando publish falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Publish failed'));

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const published = await result.current.publishAnnouncement('1');

      expect(published).toBeNull();
    });

    it('deve agendar publicação', async () => {
      mockCustomInstance.mockResolvedValueOnce({ id: '1', status: 'scheduled' });

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const scheduled = await result.current.publishAnnouncement('1', '2026-01-01T00:00:00');

      expect(scheduled).toEqual({ id: '1', status: 'scheduled' });
    });

    it('deve confirmar leitura', async () => {
      mockCustomInstance.mockResolvedValueOnce({ success: true });

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const confirmed = await result.current.acknowledgeAnnouncement('1');

      expect(confirmed).toBe(true);
    });

    it('deve retornar false quando confirm falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Confirm failed'));

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const confirmed = await result.current.acknowledgeAnnouncement('1');

      expect(confirmed).toBe(false);
    });

    it('deve deletar comunicado', async () => {
      mockCustomInstance.mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const deleted = await result.current.deleteAnnouncement('1');

      expect(deleted).toBe(true);
    });

    it('deve retornar false quando delete falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Delete failed'));

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      const deleted = await result.current.deleteAnnouncement('1');

      expect(deleted).toBe(false);
    });

    it('deve refletir loading state', async () => {
      mockCustomInstance.mockImplementation(() => new Promise(() => {}));

      const { result } = renderHook(() => useAnnouncementMutations(), { wrapper });

      // Iniciar uma mutação
      result.current.createAnnouncement({ title: 'New' } as any);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(true);
      });
    });
  });

  describe('useUnreadAnnouncements - Error Handling', () => {
    it('deve retornar mensagem de erro quando falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Erro ao carregar não lidos'));

      const { result } = renderHook(() => useUnreadAnnouncements(), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro ao carregar não lidos');
      });
    });

    it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useUnreadAnnouncements(), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro ao carregar comunicados');
      });
    });
  });

  describe('useAnnouncementDetail - Error Handling', () => {
    it('deve retornar mensagem de erro quando falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Erro ao carregar detalhe'));

      const { result } = renderHook(() => useAnnouncementDetail('1'), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro ao carregar detalhe');
      });
    });

    it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useAnnouncementDetail('1'), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro ao carregar comunicado');
      });
    });
  });

  describe('useAnnouncementReadStats - Error Handling', () => {
    it('deve retornar mensagem de erro quando falha', async () => {
      mockCustomInstance.mockRejectedValueOnce(new Error('Erro ao carregar stats'));

      const { result } = renderHook(() => useAnnouncementReadStats('1'), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro ao carregar stats');
      });
    });

    it('deve retornar mensagem padrão quando erro não é Error instance', async () => {
      mockCustomInstance.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useAnnouncementReadStats('1'), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro ao carregar estatisticas');
      });
    });
  });
});
