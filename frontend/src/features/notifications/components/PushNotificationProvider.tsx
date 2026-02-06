/**
 * PushNotificationProvider - Provider para inicializar push notifications
 *
 * Sprint: Módulo Operacional - Sistema de Notificações Push
 */

'use client';

import { useEffect } from 'react';
import { usePushNotifications } from '../hooks/usePushNotifications';

interface PushNotificationProviderProps {
  children: React.ReactNode;
}

/**
 * Provider que inicializa automaticamente push notifications
 * Deve ser colocado no providers.tsx para carregar globalmente
 */
export function PushNotificationProvider({ children }: PushNotificationProviderProps) {
  const { isSupported, permission } = usePushNotifications();

  useEffect(() => {
    if (isSupported) {
      console.log('[PushNotifications] Sistema inicializado');
      console.log('[PushNotifications] Permissão atual:', permission);
    } else {
      console.log('[PushNotifications] Não suportado neste navegador');
    }
  }, [isSupported, permission]);

  return <>{children}</>;
}
