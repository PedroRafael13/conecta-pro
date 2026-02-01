/**
 * Hooks para o modulo de Comunicados
 * @author Conecta PRO Team
 * @date 2026-01-28
 *
 * Usa customInstance + React Query diretamente (sem Orval gerado para comunicados)
 */

import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';
import type {
  Announcement,
  AnnouncementFilter,
  AnnouncementCreate,
  AnnouncementUpdate,
  AnnouncementReadStats,
  AnnouncementListResponse,
} from '@/lib/services/announcements';

const BASE_URL = '/api/v1/operacional/comunicacao/comunicados';

const announcementKeys = {
  all: ['announcements'] as const,
  lists: () => [...announcementKeys.all, 'list'] as const,
  list: (params?: object) => [...announcementKeys.lists(), params] as const,
  unread: (params?: object) => [...announcementKeys.all, 'unread', params] as const,
  details: () => [...announcementKeys.all, 'detail'] as const,
  detail: (id: string) => [...announcementKeys.details(), id] as const,
  readStats: (id: string) => [...announcementKeys.all, 'read-stats', id] as const,
};

function buildParams(obj: Record<string, unknown>): string {
  const params = new URLSearchParams();
  Object.entries(obj).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, String(value));
    }
  });
  return params.toString();
}

function fetchAnnouncementsList(page: number, pageSize: number, filters?: AnnouncementFilter) {
  const qs = buildParams({ page, page_size: pageSize, ...filters });
  return customInstance<AnnouncementListResponse>({ url: `${BASE_URL}?${qs}`, method: 'GET' });
}

function fetchUnreadAnnouncements(page: number, pageSize: number) {
  const qs = buildParams({ page, page_size: pageSize });
  return customInstance<AnnouncementListResponse>({ url: `${BASE_URL}/nao-lidos?${qs}`, method: 'GET' });
}

function fetchAnnouncementById(id: string) {
  return customInstance<Announcement>({ url: `${BASE_URL}/${id}`, method: 'GET' });
}

function fetchReadStats(id: string) {
  return customInstance<AnnouncementReadStats>({ url: `${BASE_URL}/${id}/leituras`, method: 'GET' });
}

function createAnnouncementApi(data: AnnouncementCreate) {
  return customInstance<Announcement>({ url: BASE_URL, method: 'POST', headers: { 'Content-Type': 'application/json' }, data });
}

function updateAnnouncementApi(id: string, data: AnnouncementUpdate) {
  return customInstance<Announcement>({ url: `${BASE_URL}/${id}`, method: 'PATCH', headers: { 'Content-Type': 'application/json' }, data });
}

function publishAnnouncementApi(id: string, scheduleAt?: string) {
  return customInstance<Announcement>({ url: `${BASE_URL}/${id}/publicar`, method: 'POST', headers: { 'Content-Type': 'application/json' }, data: { schedule_at: scheduleAt } });
}

function acknowledgeAnnouncementApi(id: string) {
  return customInstance<{ success: boolean; acknowledged_at: string }>({ url: `${BASE_URL}/${id}/confirmar`, method: 'POST', headers: { 'Content-Type': 'application/json' }, data: {} });
}

function deleteAnnouncementApi(id: string) {
  return customInstance<void>({ url: `${BASE_URL}/${id}`, method: 'DELETE' });
}

interface UseAnnouncementsOptions {
  initialPageSize?: number;
  autoLoad?: boolean;
  initialFilters?: AnnouncementFilter;
}

interface UseAnnouncementsReturn {
  announcements: Announcement[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: AnnouncementFilter;
  setFilters: (filters: AnnouncementFilter) => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  refresh: () => Promise<void>;
}

export function useAnnouncements(options: UseAnnouncementsOptions = {}): UseAnnouncementsReturn {
  const { initialPageSize = 10, autoLoad = true, initialFilters = {} } = options;

  const [page, setPageState] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [filters, setFiltersState] = useState<AnnouncementFilter>(initialFilters);

  const query = useQuery({
    queryKey: announcementKeys.list({ page, pageSize, ...filters }),
    queryFn: () => fetchAnnouncementsList(page, pageSize, filters),
    enabled: autoLoad,
  });

  const setFilters = useCallback((newFilters: AnnouncementFilter) => {
    setFiltersState(newFilters);
    setPageState(1);
  }, []);

  const setPage = useCallback((p: number) => {
    setPageState(p);
  }, []);

  const refresh = useCallback(async () => {
    await query.refetch();
  }, [query]);

  return {
    announcements: query.data?.items ?? [],
    total: query.data?.total ?? 0,
    page,
    pageSize,
    totalPages: query.data?.total_pages ?? 0,
    isLoading: query.isLoading,
    error: query.error ? (query.error as Error).message || 'Erro ao carregar comunicados' : null,
    filters,
    setFilters,
    setPage,
    setPageSize,
    refresh,
  };
}

export function useUnreadAnnouncements(options: { initialPageSize?: number } = {}) {
  const { initialPageSize = 20 } = options;

  const [page, setPage] = useState(1);
  const [pageSize] = useState(initialPageSize);

  const query = useQuery({
    queryKey: announcementKeys.unread({ page, pageSize }),
    queryFn: () => fetchUnreadAnnouncements(page, pageSize),
  });

  const refresh = useCallback(async () => {
    await query.refetch();
  }, [query]);

  return {
    announcements: query.data?.items ?? [],
    total: query.data?.total ?? 0,
    page,
    pageSize,
    totalPages: query.data?.total_pages ?? 0,
    isLoading: query.isLoading,
    error: query.error ? (query.error as Error).message || 'Erro ao carregar comunicados' : null,
    setPage,
    refresh,
  };
}

export function useAnnouncementDetail(id: string | null) {
  const query = useQuery({
    queryKey: announcementKeys.detail(id ?? ''),
    queryFn: () => fetchAnnouncementById(id!),
    enabled: !!id,
  });

  const refresh = useCallback(async () => {
    await query.refetch();
  }, [query]);

  return {
    announcement: query.data ?? null,
    isLoading: query.isLoading,
    error: query.error ? (query.error as Error).message || 'Erro ao carregar comunicado' : null,
    refresh,
  };
}

export function useAnnouncementReadStats(id: string | null) {
  const query = useQuery({
    queryKey: announcementKeys.readStats(id ?? ''),
    queryFn: () => fetchReadStats(id!),
    enabled: !!id,
  });

  const refresh = useCallback(async () => {
    await query.refetch();
  }, [query]);

  return {
    stats: query.data ?? null,
    isLoading: query.isLoading,
    error: query.error ? (query.error as Error).message || 'Erro ao carregar estatisticas' : null,
    refresh,
  };
}

export function useAnnouncementMutations() {
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: AnnouncementCreate) => createAnnouncementApi(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: announcementKeys.lists() });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: AnnouncementUpdate }) => updateAnnouncementApi(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: announcementKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: announcementKeys.lists() });
    },
  });

  const publishMutation = useMutation({
    mutationFn: ({ id, scheduleAt }: { id: string; scheduleAt?: string }) => publishAnnouncementApi(id, scheduleAt),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: announcementKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: announcementKeys.lists() });
    },
  });

  const acknowledgeMutation = useMutation({
    mutationFn: (id: string) => acknowledgeAnnouncementApi(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: announcementKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: announcementKeys.all });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteAnnouncementApi(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: announcementKeys.lists() });
    },
  });

  const isLoading =
    createMutation.isPending ||
    updateMutation.isPending ||
    publishMutation.isPending ||
    acknowledgeMutation.isPending ||
    deleteMutation.isPending;

  const error =
    createMutation.error?.message ||
    updateMutation.error?.message ||
    publishMutation.error?.message ||
    acknowledgeMutation.error?.message ||
    deleteMutation.error?.message ||
    null;

  const createAnnouncement = useCallback(
    async (data: AnnouncementCreate): Promise<Announcement | null> => {
      try {
        return await createMutation.mutateAsync(data);
      } catch {
        return null;
      }
    },
    [createMutation]
  );

  const updateAnnouncement = useCallback(
    async (id: string, data: AnnouncementUpdate): Promise<Announcement | null> => {
      try {
        return await updateMutation.mutateAsync({ id, data });
      } catch {
        return null;
      }
    },
    [updateMutation]
  );

  const publishAnnouncement = useCallback(
    async (id: string, scheduleAt?: string): Promise<Announcement | null> => {
      try {
        return await publishMutation.mutateAsync({ id, scheduleAt });
      } catch {
        return null;
      }
    },
    [publishMutation]
  );

  const acknowledgeAnnouncement = useCallback(
    async (id: string): Promise<boolean> => {
      try {
        await acknowledgeMutation.mutateAsync(id);
        return true;
      } catch {
        return false;
      }
    },
    [acknowledgeMutation]
  );

  const deleteAnnouncement = useCallback(
    async (id: string): Promise<boolean> => {
      try {
        await deleteMutation.mutateAsync(id);
        return true;
      } catch {
        return false;
      }
    },
    [deleteMutation]
  );

  return {
    isLoading,
    error,
    createAnnouncement,
    updateAnnouncement,
    publishAnnouncement,
    acknowledgeAnnouncement,
    deleteAnnouncement,
  };
}
