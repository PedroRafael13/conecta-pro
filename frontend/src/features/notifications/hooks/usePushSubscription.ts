/**
 * usePushSubscription Hook - Gerencia subscription de Push Notifications
 *
 * Sprint: Módulo Operacional - Sistema de Notificações Push
 */

'use client';

import { useEffect, useState, useCallback } from 'react';

interface UsePushSubscriptionReturn {
  isSupported: boolean;
  isSubscribed: boolean;
  isPermissionGranted: boolean;
  subscribe: () => Promise<void>;
  unsubscribe: () => Promise<void>;
  requestPermission: () => Promise<NotificationPermission>;
}

// Converte base64 URL-safe para Uint8Array
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function usePushSubscription(): UsePushSubscriptionReturn {
  const [isSupported, setIsSupported] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isPermissionGranted, setIsPermissionGranted] = useState(false);

  // Verifica suporte do navegador
  useEffect(() => {
    const checkSupport = () => {
      const supported =
        'serviceWorker' in navigator &&
        'PushManager' in window &&
        'Notification' in window;
      setIsSupported(supported);

      if (supported && Notification.permission === 'granted') {
        setIsPermissionGranted(true);
      }
    };

    checkSupport();
  }, []);

  // Verifica se já está inscrito
  useEffect(() => {
    const checkSubscription = async () => {
      if (!isSupported) return;

      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        setIsSubscribed(!!subscription);
      } catch (error) {
        console.error('Erro ao verificar subscription:', error);
      }
    };

    checkSubscription();
  }, [isSupported]);

  const requestPermission = useCallback(async (): Promise<NotificationPermission> => {
    if (!isSupported) {
      return 'denied';
    }

    try {
      const permission = await Notification.requestPermission();
      setIsPermissionGranted(permission === 'granted');
      return permission;
    } catch (error) {
      console.error('Erro ao solicitar permissão:', error);
      return 'denied';
    }
  }, [isSupported]);

  const subscribe = useCallback(async () => {
    if (!isSupported) {
      throw new Error('Push notifications não suportadas neste navegador');
    }

    try {
      // Solicita permissão se necessário
      if (Notification.permission !== 'granted') {
        const permission = await requestPermission();
        if (permission !== 'granted') {
          throw new Error('Permissão negada');
        }
      }

      // Registra Service Worker
      const registration = await navigator.serviceWorker.register('/sw.js');
      await navigator.serviceWorker.ready;

      // Obtém chave pública VAPID
      const vapidPublicKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;
      if (!vapidPublicKey) {
        throw new Error('Chave VAPID não configurada');
      }

      // Inscreve para Push Notifications
      const applicationServerKey = urlBase64ToUint8Array(vapidPublicKey);
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey as unknown as BufferSource,
      });

      // Envia subscription para backend
      const response = await fetch('/api/v1/notifications/push/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          subscription: subscription.toJSON(),
          device_info: {
            user_agent: navigator.userAgent,
            platform: navigator.platform,
            screen: {
              width: window.screen.width,
              height: window.screen.height,
            },
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Erro ao registrar subscription no backend');
      }

      setIsSubscribed(true);
      console.log('Push notification subscription successful');
    } catch (error) {
      console.error('Erro ao fazer subscription:', error);
      throw error;
    }
  }, [isSupported, requestPermission]);

  const unsubscribe = useCallback(async () => {
    if (!isSupported) {
      throw new Error('Push notifications não suportadas neste navegador');
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();

      if (!subscription) {
        setIsSubscribed(false);
        return;
      }

      // Remove subscription do backend
      await fetch('/api/v1/notifications/push/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          endpoint: subscription.endpoint,
        }),
      });

      // Remove subscription do navegador
      await subscription.unsubscribe();
      setIsSubscribed(false);

      console.log('Push notification unsubscribed');
    } catch (error) {
      console.error('Erro ao cancelar subscription:', error);
      throw error;
    }
  }, [isSupported]);

  return {
    isSupported,
    isSubscribed,
    isPermissionGranted,
    subscribe,
    unsubscribe,
    requestPermission,
  };
}
