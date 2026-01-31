/**
 * Hooks para o módulo de Comunicados
 * @author Conecta PRO Team
 * @date 2026-01-28
 */

import { useState, useEffect, useCallback } from 'react';
import {
  announcementsService,
  type Announcement,
  type AnnouncementFilter,
  type AnnouncementCreate,
  type AnnouncementUpdate,
  type AnnouncementReadStats,
} from '@/lib/services/announcements';
import { getErrorMessage } from '@/lib/api';

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

/**
 * Hook para listar comunicados com paginação e filtros
 */
export function useAnnouncements(options: UseAnnouncementsOptions = {}): UseAnnouncementsReturn {
  const { initialPageSize = 10, autoLoad = true, initialFilters = {} } = options;

  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFiltersState] = useState<AnnouncementFilter>(initialFilters);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await announcementsService.list(page, pageSize, filters);
      setAnnouncements(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
      setAnnouncements([]);
    } finally {
      setIsLoading(false);
    }
  }, [filters, page, pageSize]);

  useEffect(() => {
    if (autoLoad) {
      fetchData();
    }
  }, [fetchData, autoLoad]);

  const setFilters = useCallback((newFilters: AnnouncementFilter) => {
    setFiltersState(newFilters);
    setPage(1);
  }, []);

  return {
    announcements,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    filters,
    setFilters,
    setPage,
    setPageSize,
    refresh: fetchData,
  };
}

/**
 * Hook para comunicados não lidos
 */
export function useUnreadAnnouncements(options: { initialPageSize?: number } = {}) {
  const { initialPageSize = 20 } = options;

  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await announcementsService.listUnread(page, pageSize);
      setAnnouncements(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
      setAnnouncements([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    announcements,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    setPage,
    refresh: fetchData,
  };
}

/**
 * Hook para detalhes de um comunicado
 */
export function useAnnouncementDetail(id: string | null) {
  const [announcement, setAnnouncement] = useState<Announcement | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnnouncement = useCallback(async () => {
    if (!id) {
      setAnnouncement(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await announcementsService.getById(id);
      setAnnouncement(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchAnnouncement();
  }, [fetchAnnouncement]);

  return {
    announcement,
    isLoading,
    error,
    refresh: fetchAnnouncement,
  };
}

/**
 * Hook para estatísticas de leitura de um comunicado
 */
export function useAnnouncementReadStats(id: string | null) {
  const [stats, setStats] = useState<AnnouncementReadStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    if (!id) {
      setStats(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await announcementsService.getReadStats(id);
      setStats(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    isLoading,
    error,
    refresh: fetchStats,
  };
}

/**
 * Hook para mutations de comunicados (criar, atualizar, publicar, etc.)
 */
export function useAnnouncementMutations() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createAnnouncement = useCallback(async (data: AnnouncementCreate): Promise<Announcement | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await announcementsService.create(data);
      return result;
    } catch (err) {
      setError(getErrorMessage(err));
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateAnnouncement = useCallback(async (id: string, data: AnnouncementUpdate): Promise<Announcement | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await announcementsService.update(id, data);
      return result;
    } catch (err) {
      setError(getErrorMessage(err));
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const publishAnnouncement = useCallback(async (id: string, scheduleAt?: string): Promise<Announcement | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await announcementsService.publish(id, scheduleAt);
      return result;
    } catch (err) {
      setError(getErrorMessage(err));
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const acknowledgeAnnouncement = useCallback(async (id: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      await announcementsService.acknowledge(id);
      return true;
    } catch (err) {
      setError(getErrorMessage(err));
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteAnnouncement = useCallback(async (id: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      await announcementsService.delete(id);
      return true;
    } catch (err) {
      setError(getErrorMessage(err));
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

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
