// Service Worker - Conecta PRO PWA
const CACHE_NAME = 'conecta-pro-v1';
const STATIC_CACHE = 'conecta-pro-static-v1';
const DYNAMIC_CACHE = 'conecta-pro-dynamic-v1';

// Arquivos para cache estático
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logo-conecta-pro.svg',
  '/icons/icon-72x72.png',
  '/icons/icon-96x96.png',
  '/icons/icon-128x128.png',
  '/icons/icon-144x144.png',
  '/icons/icon-152x152.png',
  '/icons/icon-192x192.png',
  '/icons/icon-384x384.png',
  '/icons/icon-512x512.png',
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[SW] Caching static assets...');
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== STATIC_CACHE && name !== DYNAMIC_CACHE)
          .map((name) => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    })
  );
  self.clients.claim();
});

// Interceptar requisições
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignorar requisições não-GET
  if (request.method !== 'GET') return;

  // Ignorar extensões do Chrome e outras URLs externas
  if (!url.origin.includes(self.location.origin)) return;

  // Estratégia: Network First para API
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Estratégia: Cache First para assets estáticos
  if (
    request.destination === 'image' ||
    request.destination === 'font' ||
    request.destination === 'style' ||
    url.pathname.match(/\.(js|css|png|jpg|jpeg|gif|svg|woff|woff2)$/)
  ) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Estratégia: Network First para páginas HTML
  event.respondWith(networkFirst(request));
});

// Estratégia: Cache First
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('[SW] Fetch failed:', error);
    return new Response('Offline', { status: 503 });
  }
}

// Estratégia: Network First
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', error);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Retornar página offline para navegação
    if (request.destination === 'document') {
      return caches.match('/index.html');
    }

    return new Response('Offline', { status: 503 });
  }
}

// Mensagens do cliente
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});

console.log('[SW] Service Worker loaded');
