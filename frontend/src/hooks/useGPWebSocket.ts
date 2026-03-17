'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

interface GPEvent {
  event_id: string;
  event_type: string;
  payload: Record<string, any>;
  source_module: string;
  priority: number;
  timestamp: string;
}

interface UseGPWebSocketOptions {
  userId: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onEvent?: (event: GPEvent) => void;
}

interface UseGPWebSocketReturn {
  connected: boolean;
  lastEvent: GPEvent | null;
  events: GPEvent[];
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: Record<string, any>) => void;
}

export function useGPWebSocket({
  userId,
  autoConnect = true,
  reconnectInterval = 5000,
  maxReconnectAttempts = 10,
  onEvent,
}: UseGPWebSocketOptions): UseGPWebSocketReturn {
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<GPEvent | null>(null);
  const [events, setEvents] = useState<GPEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);

  const getWsUrl = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NEXT_PUBLIC_WS_HOST || window.location.host;
    return `${protocol}//${host}/api/v1/people-management/ws/gp/${userId}`;
  }, [userId]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(getWsUrl());

      ws.onopen = () => {
        setConnected(true);
        reconnectCountRef.current = 0;
        console.log('[GP WebSocket] Conectado');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as GPEvent;

          // Ignora mensagens de controle (pong, subscribed)
          if ('type' in data && (data as any).type === 'pong') return;

          setLastEvent(data);
          setEvents((prev) => [...prev.slice(-99), data]); // Max 100 events
          onEvent?.(data);
        } catch {
          // Mensagem nao-JSON, ignorar
        }
      };

      ws.onclose = () => {
        setConnected(false);
        console.log('[GP WebSocket] Desconectado');

        // Reconnect automatico
        if (reconnectCountRef.current < maxReconnectAttempts) {
          reconnectTimerRef.current = setTimeout(() => {
            reconnectCountRef.current += 1;
            console.log(`[GP WebSocket] Reconnect ${reconnectCountRef.current}/${maxReconnectAttempts}`);
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = () => {
        console.error('[GP WebSocket] Erro de conexao');
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('[GP WebSocket] Falha ao conectar:', err);
    }
  }, [getWsUrl, onEvent, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
    }
    reconnectCountRef.current = maxReconnectAttempts; // Prevent reconnect
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, [maxReconnectAttempts]);

  const sendMessage = useCallback((message: Record<string, any>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Heartbeat ping every 30s
  useEffect(() => {
    if (!connected) return;
    const interval = setInterval(() => {
      sendMessage({ type: 'ping' });
    }, 30000);
    return () => clearInterval(interval);
  }, [connected, sendMessage]);

  return { connected, lastEvent, events, connect, disconnect, sendMessage };
}
