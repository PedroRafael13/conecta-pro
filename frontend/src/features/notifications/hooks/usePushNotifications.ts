/**
 * usePushNotifications Hook - Hook para inicializar push notifications
 *
 * Sprint: Módulo Operacional - Sistema de Notificações Push
 */

'use client';

import { useEffect, useState } from 'react';
import { registerServiceWorker, subscribeToPushNotifications } from '../services/registerServiceWorker';
import { useNotifications } from './useNotifications';

interface UsePushNotificationsReturn {
  isSupported: boolean;
  isSubscribed: boolean;
  permission: NotificationPermission;
  subscribe: () => Promise<void>;
  unsubscribe: () => Promise<void>;
}

export function usePushNotifications(): UsePushNotificationsReturn {
  const [isSupported, setIsSupported] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const { subscribeToPush } = useNotifications();

  useEffect(() => {
    // Verifica suporte
    const supported = 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
    setIsSupported(supported);

    if (!supported) {
      return;
    }

    // Verifica permissão atual
    setPermission(Notification.permission);

    // Registra Service Worker
    registerServiceWorker();

    // Verifica se já está subscrito
    checkSubscription();
  }, []);

  const checkSubscription = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      setIsSubscribed(!!subscription);
    } catch (error) {
      console.error('Erro ao verificar subscrição:', error);
    }
  };

  const subscribe = async () => {
    try {
      const token = await subscribeToPushNotifications();
      if (token) {
        // Registra no backend
        await subscribeToPush(token, 'web');
        setIsSubscribed(true);
        setPermission(Notification.permission);
      }
    } catch (error) {
      console.error('Erro ao subscrever:', error);
    }
  };

  const unsubscribe = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();

      if (subscription) {
        await subscription.unsubscribe();
        setIsSubscribed(false);
      }
    } catch (error) {
      console.error('Erro ao desinscrever:', error);
    }
  };

  return {
    isSupported,
    isSubscribed,
    permission,
    subscribe,
    unsubscribe,
  };
}
