import { useEffect, useRef, useState, useCallback } from 'react';

interface DisputeEvent {
  event: string;
  data: any;
  timestamp: string;
}

interface UseDisputeWebSocketOptions {
  sessaoId: string;
  onLanceEnviado?: (data: any) => void;
  onLanceCoberto?: (data: any) => void;
  onMelhorColocado?: (data: any) => void;
  onConvocacao?: (data: any) => void;
  onFimDisputa?: (data: any) => void;
  onStatusUpdate?: (data: any) => void;
  onError?: (error: any) => void;
}

export function useDisputeWebSocket({
  sessaoId,
  onLanceEnviado,
  onLanceCoberto,
  onMelhorColocado,
  onConvocacao,
  onFimDisputa,
  onStatusUpdate,
  onError,
}: UseDisputeWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<DisputeEvent | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!sessaoId) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/licitacoes/ws/disputas/${sessaoId}`;

    try {
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setIsConnected(true);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: DisputeEvent = JSON.parse(event.data);
          setLastEvent(message);

          switch (message.event) {
            case 'lance_enviado':
              onLanceEnviado?.(message.data);
              break;
            case 'lance_coberto':
              onLanceCoberto?.(message.data);
              break;
            case 'melhor_colocado':
              onMelhorColocado?.(message.data);
              break;
            case 'convocacao':
              onConvocacao?.(message.data);
              // Notificação sonora para convocação
              if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('Convocação!', {
                  body: message.data.mensagem,
                  icon: '/favicon.ico',
                  requireInteraction: true,
                });
              }
              break;
            case 'fim_disputa':
              onFimDisputa?.(message.data);
              break;
            case 'status_update':
              onStatusUpdate?.(message.data);
              break;
            case 'ping':
              // Responde ao ping do servidor
              wsRef.current?.send(JSON.stringify({ event: 'pong' }));
              break;
          }
        } catch (e) {
          // message parse error - silently ignored
        }
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);

        // Reconectar após 3 segundos
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };

      wsRef.current.onerror = (error) => {
        onError?.(error);
      };
    } catch (error) {
      onError?.(error);
    }
  }, [sessaoId, onLanceEnviado, onLanceCoberto, onMelhorColocado, onConvocacao, onFimDisputa, onStatusUpdate, onError]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const requestStatus = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ event: 'request_status' }));
    }
  }, []);

  useEffect(() => {
    connect();

    // Solicitar permissão de notificação
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastEvent,
    requestStatus,
    disconnect,
    reconnect: connect,
  };
}
