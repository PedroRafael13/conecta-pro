/**
 * Service Worker - Push Notifications
 *
 * Sprint: Módulo Operacional - Sistema de Notificações Push
 */

const CACHE_VERSION = 'v1';
const CACHE_NAME = `conecta-pro-${CACHE_VERSION}`;

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Instalando...');
  self.skipWaiting();
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Ativando...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  return self.clients.claim();
});

// Recebimento de Push Notification
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push recebido:', event);

  let notificationData = {
    title: 'Nova Notificação',
    body: 'Você tem uma nova notificação',
    icon: '/apple-touch-icon.png',
    badge: '/favicon.ico',
    data: {},
  };

  // Parse dos dados do push
  if (event.data) {
    try {
      const data = event.data.json();
      notificationData = {
        title: data.title || notificationData.title,
        body: data.body || notificationData.body,
        icon: data.icon || notificationData.icon,
        badge: data.badge || notificationData.badge,
        data: data.data || {},
      };
    } catch (e) {
      console.error('[Service Worker] Erro ao parsear dados do push:', e);
    }
  }

  const options = {
    body: notificationData.body,
    icon: notificationData.icon,
    badge: notificationData.badge,
    vibrate: [200, 100, 200],
    tag: notificationData.data.type || 'notification',
    requireInteraction: false,
    data: notificationData.data,
    actions: [
      {
        action: 'open',
        title: 'Abrir',
      },
      {
        action: 'close',
        title: 'Fechar',
      },
    ],
  };

  event.waitUntil(
    self.registration.showNotification(notificationData.title, options)
  );
});

// Click na notificação
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notificação clicada:', event);

  event.notification.close();

  if (event.action === 'close') {
    return;
  }

  // Abre ou foca na janela
  const urlToOpen = event.notification.data?.action_url || '/modulos/operacional';

  event.waitUntil(
    clients
      .matchAll({
        type: 'window',
        includeUncontrolled: true,
      })
      .then((clientList) => {
        // Verifica se já existe uma janela aberta
        for (const client of clientList) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }

        // Se não existe, abre uma nova
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// Fechamento da notificação
self.addEventListener('notificationclose', (event) => {
  console.log('[Service Worker] Notificação fechada:', event);
});

// Fetch - Não implementamos cache de requisições por enquanto
self.addEventListener('fetch', (event) => {
  // Deixamos passar todas as requisições sem interceptar
  return;
});
