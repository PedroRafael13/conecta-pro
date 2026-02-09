/**
 * useNotifications Hook - Hook para gerenciar notificações push
 *
 * Sprint: Módulo Operacional - Sistema de Notificações Push
 */

'use client';

import { useEffect, useState, useCallback } from 'react';

interface Notification {
  id: string;
  title: string;
  body: string;
  data?: Record<string, any>;
  read: boolean;
  created_at: string;
  opened_at?: string;
  action_url?: string;
}

interface UseNotificationsReturn {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  markAsRead: (notificationId: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  subscribeToPush: (deviceToken: string, platform: string) => Promise<void>;
}

export function useNotifications(): UseNotificationsReturn {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = useCallback(async () => {
    // Skip se push notifications desabilitado
    if (process.env.NEXT_PUBLIC_ENABLE_PUSH_NOTIFICATIONS === 'false') {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/v1/notifications/push', {
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        // Se endpoint não existe (404), apenas skip silenciosamente
        if (response.status === 404) {
          setLoading(false);
          return;
        }
        throw new Error('Erro ao buscar notificações');
      }

      const data = await response.json();
      setNotifications(data.notifications || []);
      setUnreadCount(data.unread_count || 0);
    } catch (err) {
      // Não logar erro se for 404 ou feature desabilitada
      if (err instanceof Error && !err.message.includes('404')) {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const markAsRead = useCallback(async (notificationId: string) => {
    try {
      const response = await fetch(`/api/v1/notifications/push/${notificationId}/read`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Erro ao marcar notificação como lida');
      }

      // Atualiza estado local
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId ? { ...n, read: true, opened_at: new Date().toISOString() } : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Erro ao marcar como lida:', err);
    }
  }, []);

  const markAllAsRead = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/notifications/push/read-all', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Erro ao marcar todas como lidas');
      }

      // Atualiza estado local
      setNotifications(prev =>
        prev.map(n => ({ ...n, read: true, opened_at: new Date().toISOString() }))
      );
      setUnreadCount(0);
    } catch (err) {
      console.error('Erro ao marcar todas como lidas:', err);
    }
  }, []);

  const subscribeToPush = useCallback(async (deviceToken: string, platform: string) => {
    try {
      const response = await fetch('/api/v1/notifications/push/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          device_token: deviceToken,
          platform,
          device_info: {
            user_agent: navigator.userAgent,
            screen: {
              width: window.screen.width,
              height: window.screen.height,
            },
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Erro ao registrar dispositivo');
      }
    } catch (err) {
      console.error('Erro ao registrar dispositivo:', err);
    }
  }, []);

  useEffect(() => {
    // Skip se push notifications desabilitado
    if (process.env.NEXT_PUBLIC_ENABLE_PUSH_NOTIFICATIONS === 'false') {
      return;
    }

    fetchNotifications();

    // Atualiza notificações a cada 30 segundos
    const interval = setInterval(fetchNotifications, 30000);

    return () => clearInterval(interval);
  }, [fetchNotifications]);

  return {
    notifications,
    unreadCount,
    loading,
    error,
    refresh: fetchNotifications,
    markAsRead,
    markAllAsRead,
    subscribeToPush,
  };
}
