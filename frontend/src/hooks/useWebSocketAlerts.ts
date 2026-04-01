import { useWebSocketContext } from '@/components/WebSocketProvider';

export function useWebSocketAlerts() {
  return useWebSocketContext();
}
