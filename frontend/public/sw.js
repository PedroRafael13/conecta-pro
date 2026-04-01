/**
 * Service Worker - Cache Buster v3
 * Limpa todos os caches e se auto-desregistra
 */

// Na instalação: pula espera e ativa imediatamente
self.addEventListener('install', () => {
  self.skipWaiting();
});

// Na ativação: limpa TODOS os caches e desregistra
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) => {
      return Promise.all(names.map((name) => caches.delete(name)));
    }).then(() => {
      return self.registration.unregister();
    }).then(() => {
      return self.clients.matchAll({ type: 'window' });
    }).then((clients) => {
      clients.forEach((client) => client.navigate(client.url));
    })
  );
});

// Não intercepta nenhum fetch — tudo vai direto para a rede
