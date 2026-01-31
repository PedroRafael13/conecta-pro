/**
 * Service Worker - PWA + Push Notifications
 *
 * Sprint 21: PWA Mode + Offline Support
 */

const CACHE_VERSION = 'v2';
const CACHE_NAME = `conecta-pro-${CACHE_VERSION}`;

// Assets para cache offline
const STATIC_ASSETS = [
  '/',
  '/dashboard',
  '/offline',
  '/manifest.json',
  '/favicon.ico',
  '/apple-touch-icon.png',
];

// Instalacao do Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Instalando...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Cacheando assets estaticos');
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[Service Worker] Falha ao cachear alguns assets:', err);
      });
    })
  );
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

// Fetch - Network First com fallback para cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignora requisicoes nao-GET e APIs
  if (request.method !== 'GET') return;
  if (url.pathname.startsWith('/api/')) return;
  if (url.pathname.startsWith('/_next/')) return;

  // Network First strategy
  event.respondWith(
    fetch(request)
      .then((response) => {
        // Cacheia resposta bem sucedida
        if (response.ok && response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return response;
      })
      .catch(async () => {
        // Fallback para cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
          return cachedResponse;
        }

        // Se for navegacao, mostra pagina offline
        if (request.mode === 'navigate') {
          const offlinePage = await caches.match('/offline');
          if (offlinePage) return offlinePage;
        }

        // Retorna erro generico
        return new Response('Offline', {
          status: 503,
          statusText: 'Service Unavailable',
        });
      })
  );
});
