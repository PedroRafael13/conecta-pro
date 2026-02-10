/**
 * usePushNotifications Hook - Hook para inicializar push notifications
 *
 * Sprint: Módulo Operacional - Sistema de Notificações Push
 */

'use client';

import { useEffect, useState, useCallback } from 'react';
import { registerServiceWorker, subscribeToPushNotifications } from '../services/registerServiceWorker';
import { useNotifications } from './useNotifications';

interface UsePushNotificationsReturn {
  isSupported: boolean;
  isSubscribed: boolean;
  permission: NotificationPermission;
  subscribe: () => Promise<void>;
  unsubscribe: () => Promise<void>;
}

// Check support synchronously
const checkSupport = (): boolean => {
  if (typeof window === 'undefined') return false;
  return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
};

// Get initial permission state
const getInitialPermission = (): NotificationPermission => {
  if (typeof window === 'undefined') return 'default';
  return Notification.permission;
};

export function usePushNotifications(): UsePushNotificationsReturn {
  // Use lazy initialization to avoid setState in effect
  const [isSupported] = useState<boolean>(checkSupport);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission>(getInitialPermission);
  const { subscribeToPush } = useNotifications();

  // Declarar checkSubscription antes do useEffect usando useCallback
  const checkSubscription = useCallback(async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      setIsSubscribed(!!subscription);
    } catch (error) {
      console.error('Erro ao verificar subscrição:', error);
    }
  }, []);

  useEffect(() => {
    if (!isSupported) {
      return;
    }

    // Registra Service Worker
    registerServiceWorker();

    // Verifica permissão e subscrição de forma assíncrona
    const initializePush = async () => {
      // Atualiza permissão atual
      setPermission(Notification.permission);
      // Verifica se já está subscrito
      await checkSubscription();
    };

    initializePush();
  }, [isSupported, checkSubscription]);

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
