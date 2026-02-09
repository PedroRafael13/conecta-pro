/**
 * Register Service Worker - Registra Service Worker para Push Notifications
 *
 * Sprint: Módulo Operacional - Sistema de Notificações Push
 */

export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!('serviceWorker' in navigator)) {
    console.warn('Service Worker não suportado neste navegador');
    return null;
  }

  if (!('PushManager' in window)) {
    console.warn('Push Notifications não suportado neste navegador');
    return null;
  }

  try {
    // Registra o Service Worker
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
    });

    // Aguarda o Service Worker estar ativo
    await navigator.serviceWorker.ready;

    return registration;
  } catch (error) {
    console.error('Erro ao registrar Service Worker:', error);
    return null;
  }
}

export async function unregisterServiceWorker(): Promise<boolean> {
  if (!('serviceWorker' in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const unregistered = await registration.unregister();
    return unregistered;
  } catch (error) {
    console.error('Erro ao desregistrar Service Worker:', error);
    return false;
  }
}

export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!('Notification' in window)) {
    console.warn('Notificações não suportadas neste navegador');
    return 'denied';
  }

  // Verifica se já tem permissão
  if (Notification.permission === 'granted') {
    return 'granted';
  }

  // Verifica se já foi negado
  if (Notification.permission === 'denied') {
    return 'denied';
  }

  // Solicita permissão
  try {
    const permission = await Notification.requestPermission();
    return permission;
  } catch (error) {
    console.error('Erro ao solicitar permissão:', error);
    return 'denied';
  }
}

export async function subscribeToPushNotifications(): Promise<string | null> {
  try {
    // Registra Service Worker
    const registration = await registerServiceWorker();
    if (!registration) {
      return null;
    }

    // Solicita permissão
    const permission = await requestNotificationPermission();
    if (permission !== 'granted') {
      console.warn('Permissão de notificação negada');
      return null;
    }

    // Verifica se já existe uma subscrição
    let subscription = await registration.pushManager.getSubscription();

    if (!subscription) {
      // Cria uma nova subscrição
      // IMPORTANTE: Em produção, você deve usar suas próprias VAPID keys
      // Gere com: npx web-push generate-vapid-keys
      const vapidPublicKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || '';

      if (!vapidPublicKey) {
        console.warn('VAPID public key não configurada');
        // Por enquanto, retorna token mock para desenvolvimento
        return 'development-token-' + Date.now();
      }

      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey) as BufferSource,
      });
    }

    // Retorna o endpoint como token
    return subscription.endpoint;
  } catch (error) {
    console.error('Erro ao subscrever push notifications:', error);
    return null;
  }
}

export async function unsubscribeFromPushNotifications(): Promise<boolean> {
  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();

    if (subscription) {
      const unsubscribed = await subscription.unsubscribe();
      return unsubscribed;
    }

    return false;
  } catch (error) {
    console.error('Erro ao desinscrever push notifications:', error);
    return false;
  }
}

// Helper para converter VAPID key
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

// Testa se pode mostrar notificação
export async function testNotification(): Promise<boolean> {
  if (!('Notification' in window)) {
    return false;
  }

  const permission = await requestNotificationPermission();
  if (permission !== 'granted') {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    await registration.showNotification('Conecta PRO', {
      body: 'Notificações push ativadas com sucesso!',
      icon: '/apple-touch-icon.png',
      badge: '/favicon.ico',
      tag: 'test-notification',
    });
    return true;
  } catch (error) {
    console.error('Erro ao testar notificação:', error);
    return false;
  }
}
