/**
 * useNotificationWebSocket Hook
 *
 * Hook para gerenciamento de notificações em tempo real via WebSocket
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { notificationKeys } from './useNotifications';
import { pushKeys } from './usePush';

export interface NotificationEvent {
  type: 'notification' | 'status_update' | 'queue_update' | 'campaign_update';
  data: unknown;
  timestamp: string;
}

export interface WebSocketOptions {
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onNotification?: (event: NotificationEvent) => void;
}

/**
 * Hook para conexão WebSocket de notificações em tempo real
 */
export function useNotificationWebSocket(options: WebSocketOptions = {}) {
  const {
    autoConnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
    onConnect,
    onDisconnect,
    onError,
    onNotification,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<NotificationEvent | null>(null);
  const [reconnectTrigger, setReconnectTrigger] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const queryClient = useQueryClient();
  const handleEventUpdateRef = useRef<((event: NotificationEvent) => void) | undefined>(undefined);

  /**
   * Obtém URL do WebSocket baseado no ambiente
   */
  const getWebSocketUrl = useCallback(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || window.location.origin;
    const parsed = new URL(apiUrl);
    const protocol = parsed.protocol === 'https:' ? 'wss:' : 'ws:';

    return `${protocol}//${parsed.host}/ws/notifications`;
  }, []);

  /**
   * Trata atualização de eventos e invalida cache
   */
  const handleEventUpdate = useCallback(
    (event: NotificationEvent) => {
      switch (event.type) {
        case 'notification':
          // Nova notificação recebida
          queryClient.invalidateQueries({ queryKey: notificationKeys.queue() });
          queryClient.invalidateQueries({ queryKey: pushKeys.notifications('') });
          break;

        case 'status_update':
          // Status de notificação atualizado
          queryClient.invalidateQueries({ queryKey: notificationKeys.queue() });
          queryClient.invalidateQueries({ queryKey: notificationKeys.queueStats() });
          break;

        case 'queue_update':
          // Fila de notificações atualizada
          queryClient.invalidateQueries({ queryKey: notificationKeys.queue() });
          queryClient.invalidateQueries({ queryKey: notificationKeys.queueStats() });
          break;

        case 'campaign_update':
          // Campanha atualizada
          queryClient.invalidateQueries({ queryKey: pushKeys.campaigns('') });
          break;

        default:
          break;
      }
    },
    [queryClient]
  );

  // Atualiza refs sempre que callbacks mudam
  useEffect(() => {
    handleEventUpdateRef.current = handleEventUpdate;
  }, [handleEventUpdate]);

  /**
   * Conecta ao WebSocket
   */
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Já conectado
    }

    try {
      const token = localStorage.getItem('access_token');
      const url = `${getWebSocketUrl()}?token=${token}`;

      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        reconnectCountRef.current = 0;
        onConnect?.();
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        onDisconnect?.();

        // Tentar reconectar
        if (
          autoConnect &&
          reconnectCountRef.current < maxReconnectAttempts
        ) {
          reconnectCountRef.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectTrigger(prev => prev + 1);
          }, reconnectInterval);
        }
      };

      wsRef.current.onerror = (error) => {
        onError?.(error);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const notificationEvent: NotificationEvent = JSON.parse(event.data);
          setLastEvent(notificationEvent);
          onNotification?.(notificationEvent);

          // Invalidar queries relevantes baseado no tipo do evento
          handleEventUpdateRef.current?.(notificationEvent);
        } catch (error) {
          // message parse error - silently ignored
        }
      };
    } catch (error) {
      // connection failed - will retry via reconnect
    }
  }, [
    getWebSocketUrl,
    autoConnect,
    maxReconnectAttempts,
    reconnectInterval,
    onConnect,
    onDisconnect,
    onError,
    onNotification,
  ]);

  /**
   * Desconecta do WebSocket
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  /**
   * Envia mensagem pelo WebSocket
   */
  const send = useCallback((message: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  /**
   * Inscreve em tópico específico
   */
  const subscribe = useCallback(
    (topic: string) => {
      send({
        type: 'subscribe',
        topic,
      });
    },
    [send]
  );

  /**
   * Remove inscrição de tópico
   */
  const unsubscribe = useCallback(
    (topic: string) => {
      send({
        type: 'unsubscribe',
        topic,
      });
    },
    [send]
  );

  // Conectar automaticamente ao montar ou quando reconnectTrigger mudar
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect, reconnectTrigger]);

  return {
    isConnected,
    lastEvent,
    connect,
    disconnect,
    send,
    subscribe,
    unsubscribe,
  };
}

/**
 * Hook para escutar eventos específicos do WebSocket
 */
export function useNotificationEvents(
  eventType: NotificationEvent['type'],
  callback: (data: unknown) => void
) {
  const { lastEvent } = useNotificationWebSocket({ autoConnect: true });

  useEffect(() => {
    if (lastEvent && lastEvent.type === eventType) {
      callback(lastEvent.data);
    }
  }, [lastEvent, eventType, callback]);
}

/**
 * Hook para contador de notificações não lidas em tempo real
 */
export function useUnreadCount() {
  const [count, setCount] = useState(0);

  useNotificationEvents('notification', (data: any) => {
    if (data?.unread_count !== undefined) {
      setCount(data.unread_count);
    } else {
      setCount((prev) => prev + 1);
    }
  });

  return count;
}
