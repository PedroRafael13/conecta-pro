/**
 * Hooks para o módulo de Notificações e Alertas
 * @author Conecta PRO Team
 * @date 2026-01-28
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  notificationsService,
  alertsService,
  type Notification,
  type NotificationFilter,
  type NotificationUnreadCount,
  type Alert,
  type AlertCreate,
  type AlertType,
  type AlertSeverity,
} from '@/lib/services/notifications';
import { getErrorMessage } from '@/lib/api';

interface UseNotificationsOptions {
  initialPageSize?: number;
  autoLoad?: boolean;
  initialFilters?: NotificationFilter;
  pollInterval?: number; // Intervalo de polling em ms (0 = desabilitado)
}

interface UseNotificationsReturn {
  notifications: Notification[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: NotificationFilter;
  setFilters: (filters: NotificationFilter) => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  refresh: () => Promise<void>;
  markAsRead: (id: string) => Promise<boolean>;
  markAllAsRead: () => Promise<boolean>;
  deleteNotification: (id: string) => Promise<boolean>;
}

/**
 * Hook para listar notificações com paginação e filtros
 */
export function useNotifications(options: UseNotificationsOptions = {}): UseNotificationsReturn {
  const { initialPageSize = 20, autoLoad = true, initialFilters = {}, pollInterval = 0 } = options;

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFiltersState] = useState<NotificationFilter>(initialFilters);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await notificationsService.list(page, pageSize, filters);
      setNotifications(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
      setNotifications([]);
    } finally {
      setIsLoading(false);
    }
  }, [filters, page, pageSize]);

  useEffect(() => {
    if (autoLoad) {
      fetchData();
    }
  }, [fetchData, autoLoad]);

  // Polling interval
  useEffect(() => {
    if (pollInterval > 0) {
      const interval = setInterval(fetchData, pollInterval);
      return () => clearInterval(interval);
    }
  }, [pollInterval, fetchData]);

  const setFilters = useCallback((newFilters: NotificationFilter) => {
    setFiltersState(newFilters);
    setPage(1);
  }, []);

  const markAsRead = useCallback(async (id: string): Promise<boolean> => {
    try {
      await notificationsService.markAsRead(id);
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n)
      );
      return true;
    } catch {
      return false;
    }
  }, []);

  const markAllAsRead = useCallback(async (): Promise<boolean> => {
    try {
      await notificationsService.markAllAsRead();
      setNotifications(prev =>
        prev.map(n => ({ ...n, is_read: true, read_at: new Date().toISOString() }))
      );
      return true;
    } catch {
      return false;
    }
  }, []);

  const deleteNotification = useCallback(async (id: string): Promise<boolean> => {
    try {
      await notificationsService.delete(id);
      setNotifications(prev => prev.filter(n => n.id !== id));
      setTotal(prev => prev - 1);
      return true;
    } catch {
      return false;
    }
  }, []);

  return {
    notifications,
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
    markAsRead,
    markAllAsRead,
    deleteNotification,
  };
}

/**
 * Hook para contagem de notificações não lidas
 */
export function useUnreadCount(pollInterval: number = 30000) {
  const [count, setCount] = useState<NotificationUnreadCount | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCount = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await notificationsService.getUnreadCount();
      setCount(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCount();

    if (pollInterval > 0) {
      const interval = setInterval(fetchCount, pollInterval);
      return () => clearInterval(interval);
    }
  }, [fetchCount, pollInterval]);

  return {
    count,
    total: count?.total ?? 0,
    byType: count?.by_type ?? {},
    isLoading,
    error,
    refresh: fetchCount,
  };
}

// =============================================================================
// ALERTAS
// =============================================================================

interface UseAlertsOptions {
  autoLoad?: boolean;
  pollInterval?: number;
  filters?: {
    alert_type?: AlertType;
    severity?: AlertSeverity;
    reference_type?: string;
  };
}

interface UseAlertsReturn {
  alerts: Alert[];
  total: number;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  acknowledge: (id: string) => Promise<boolean>;
  createAlert: (data: AlertCreate) => Promise<Alert | null>;
}

/**
 * Hook para listar alertas ativos
 */
export function useAlerts(options: UseAlertsOptions = {}): UseAlertsReturn {
  const { autoLoad = true, pollInterval = 30000, filters } = options;

  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await alertsService.listActive(filters);
      setAlerts(response.items);
      setTotal(response.total);
    } catch (err) {
      setError(getErrorMessage(err));
      setAlerts([]);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    if (autoLoad) {
      fetchData();
    }
  }, [fetchData, autoLoad]);

  // Polling interval
  useEffect(() => {
    if (pollInterval > 0) {
      const interval = setInterval(fetchData, pollInterval);
      return () => clearInterval(interval);
    }
  }, [pollInterval, fetchData]);

  const acknowledge = useCallback(async (id: string): Promise<boolean> => {
    try {
      await alertsService.acknowledge(id);
      setAlerts(prev => prev.filter(a => a.id !== id));
      setTotal(prev => prev - 1);
      return true;
    } catch {
      return false;
    }
  }, []);

  const createAlert = useCallback(async (data: AlertCreate): Promise<Alert | null> => {
    try {
      const alert = await alertsService.create(data);
      setAlerts(prev => [alert, ...prev]);
      setTotal(prev => prev + 1);
      return alert;
    } catch {
      return null;
    }
  }, []);

  return {
    alerts,
    total,
    isLoading,
    error,
    refresh: fetchData,
    acknowledge,
    createAlert,
  };
}

/**
 * Hook para alertas do usuário atual
 */
export function useUserAlerts(pollInterval: number = 30000) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await alertsService.listUserAlerts();
      setAlerts(response.items);
    } catch (err) {
      setError(getErrorMessage(err));
      setAlerts([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();

    if (pollInterval > 0) {
      const interval = setInterval(fetchData, pollInterval);
      return () => clearInterval(interval);
    }
  }, [fetchData, pollInterval]);

  const acknowledge = useCallback(async (id: string): Promise<boolean> => {
    try {
      await alertsService.acknowledge(id);
      setAlerts(prev => prev.filter(a => a.id !== id));
      return true;
    } catch {
      return false;
    }
  }, []);

  return {
    alerts,
    total: alerts.length,
    criticalCount: alerts.filter(a => a.is_critical).length,
    isLoading,
    error,
    refresh: fetchData,
    acknowledge,
  };
}
