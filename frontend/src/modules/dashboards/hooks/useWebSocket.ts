import { useState, useEffect, useCallback, useRef } from 'react';
import type { WebSocketMessage } from '../types/dashboard.types';

interface UseWebSocketOptions {
  url?: string;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

interface UseWebSocketReturn {
  connected: boolean;
  connecting: boolean;
  lastMessage: WebSocketMessage | null;
  send: (data: unknown) => void;
  disconnect: () => void;
  reconnect: () => void;
}

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export function useWebSocket(
  channel: string,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    url = WS_URL,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    heartbeatInterval = 30000,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
  } = options;

  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const heartbeatRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const connectRef = useRef<() => void>(() => {});

  const clearTimers = useCallback(() => {
    if (heartbeatRef.current) {
      clearInterval(heartbeatRef.current);
      heartbeatRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnecting(true);

    try {
      const wsUrl = `${url}/${channel}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setConnected(true);
        setConnecting(false);
        reconnectCountRef.current = 0;
        onConnect?.();

        // Start heartbeat
        heartbeatRef.current = setInterval(() => {
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'ping' }));
          }
        }, heartbeatInterval);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          // Handle heartbeat response
          if (message.type === 'heartbeat') return;

          setLastMessage(message);
          onMessage?.(message);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      wsRef.current.onclose = () => {
        setConnected(false);
        setConnecting(false);
        clearTimers();
        onDisconnect?.();

        // Attempt reconnect
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            connectRef.current();
          }, reconnectInterval);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setConnecting(false);
    }
  }, [
    url,
    channel,
    reconnectAttempts,
    reconnectInterval,
    heartbeatInterval,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    clearTimers,
  ]);

  // Update ref to point to current connect function
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  const disconnect = useCallback(() => {
    clearTimers();
    reconnectCountRef.current = reconnectAttempts; // Prevent reconnect
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
  }, [clearTimers, reconnectAttempts]);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectCountRef.current = 0;
    connect();
  }, [disconnect, connect]);

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // Connect on mount
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    connected,
    connecting,
    lastMessage,
    send,
    disconnect,
    reconnect,
  };
}

// Simulated WebSocket for development
export function useSimulatedWebSocket(channel: string): UseWebSocketReturn {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  useEffect(() => {
    // Simulate connection
    const connectTimeout = setTimeout(() => {
      setConnected(true);
    }, 500);

    // Simulate periodic messages
    const messageInterval = setInterval(() => {
      const messages: WebSocketMessage[] = [
        {
          type: 'metric.update',
          data: { key: 'active_users', value: Math.floor(Math.random() * 50) + 30 },
          timestamp: new Date().toISOString(),
        },
        {
          type: 'metric.update',
          data: { key: 'api_requests', value: Math.floor(Math.random() * 200) + 100 },
          timestamp: new Date().toISOString(),
        },
        {
          type: 'activity',
          data: {
            user: ['Maria', 'Joao', 'Ana', 'Pedro'][Math.floor(Math.random() * 4)],
            action: ['criou documento', 'aprovou proposta', 'finalizou tarefa'][
              Math.floor(Math.random() * 3)
            ],
          },
          timestamp: new Date().toISOString(),
        },
      ];

      const randomMessage = messages[Math.floor(Math.random() * messages.length)];
      setLastMessage(randomMessage);
    }, 3000);

    return () => {
      clearTimeout(connectTimeout);
      clearInterval(messageInterval);
    };
  }, [channel]);

  return {
    connected,
    connecting: false,
    lastMessage,
    send: () => {},
    disconnect: () => setConnected(false),
    reconnect: () => setConnected(true),
  };
}

export default useWebSocket;
