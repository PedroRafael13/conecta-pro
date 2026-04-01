/**
 * Service Worker para Ponto Eletronico - Conecta PRO
 * Funcionalidades:
 * - Cache de assets para offline
 * - Armazena batidas offline em IndexedDB
 * - Sync automatico quando volta online
 * - Push notifications
 */

const CACHE_NAME = 'conecta-ponto-v1';
const CACHE_ASSETS = [
  '/modulos/gestao-pessoas/ponto',
  '/modulos/gestao-pessoas/ponto/batida',
];

// IndexedDB config
const DB_NAME = 'conecta_ponto_offline';
const DB_VERSION = 1;
const STORE_PUNCHES = 'pending_punches';
const STORE_EMPLOYEE = 'cached_employee';
const STORE_SCHEDULE = 'cached_schedule';
const STORE_SYNC = 'sync_metadata';

// ==========================================
// INSTALL
// ==========================================
self.addEventListener('install', (event) => {
  console.log('[SW Ponto] Install');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CACHE_ASSETS).catch(() => {
        console.log('[SW Ponto] Cache parcial (alguns assets nao encontrados)');
      });
    })
  );
  self.skipWaiting();
});

// ==========================================
// ACTIVATE
// ==========================================
self.addEventListener('activate', (event) => {
  console.log('[SW Ponto] Activate');
  event.waitUntil(
    caches.keys().then((names) => {
      return Promise.all(
        names
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// ==========================================
// FETCH (Offline support)
// ==========================================
self.addEventListener('fetch', (event) => {
  // Apenas intercepta GET requests para pages
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Clone e cache
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone);
          });
        }
        return response;
      })
      .catch(() => {
        // Offline: retorna do cache
        return caches.match(event.request).then((cached) => {
          return cached || new Response('Offline', { status: 503 });
        });
      })
  );
});

// ==========================================
// SYNC (Background sync para batidas offline)
// ==========================================
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-punches') {
    console.log('[SW Ponto] Background sync: punches');
    event.waitUntil(syncPendingPunches());
  }
});

// ==========================================
// MESSAGE (Comunicacao com o client)
// ==========================================
self.addEventListener('message', (event) => {
  const { type, data } = event.data || {};

  switch (type) {
    case 'SAVE_PUNCH_OFFLINE':
      savePunchOffline(data).then(() => {
        event.source.postMessage({ type: 'PUNCH_SAVED_OFFLINE', data });
      });
      break;

    case 'GET_PENDING_COUNT':
      getPendingCount().then((count) => {
        event.source.postMessage({ type: 'PENDING_COUNT', count });
      });
      break;

    case 'FORCE_SYNC':
      syncPendingPunches().then((result) => {
        event.source.postMessage({ type: 'SYNC_COMPLETE', result });
      });
      break;
  }
});

// ==========================================
// INDEXEDDB HELPERS
// ==========================================

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_PUNCHES)) {
        const store = db.createObjectStore(STORE_PUNCHES, { keyPath: 'punch_id' });
        store.createIndex('employee_id', 'employee_id');
        store.createIndex('timestamp', 'timestamp');
        store.createIndex('synced', 'synced');
      }
      if (!db.objectStoreNames.contains(STORE_EMPLOYEE)) {
        db.createObjectStore(STORE_EMPLOYEE, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORE_SCHEDULE)) {
        db.createObjectStore(STORE_SCHEDULE, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(STORE_SYNC)) {
        db.createObjectStore(STORE_SYNC, { keyPath: 'key' });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function savePunchOffline(punchData) {
  const db = await openDB();
  const tx = db.transaction(STORE_PUNCHES, 'readwrite');
  const store = tx.objectStore(STORE_PUNCHES);

  const punch = {
    ...punchData,
    punch_id: punchData.punch_id || crypto.randomUUID(),
    synced: false,
    saved_at: new Date().toISOString(),
  };

  store.put(punch);
  return new Promise((resolve) => {
    tx.oncomplete = () => resolve(punch);
  });
}

async function getPendingPunches() {
  const db = await openDB();
  const tx = db.transaction(STORE_PUNCHES, 'readonly');
  const store = tx.objectStore(STORE_PUNCHES);
  const index = store.index('synced');

  return new Promise((resolve) => {
    const request = index.getAll(false);
    request.onsuccess = () => resolve(request.result || []);
    request.onerror = () => resolve([]);
  });
}

async function getPendingCount() {
  const pending = await getPendingPunches();
  return pending.length;
}

async function markAsSynced(punchIds) {
  const db = await openDB();
  const tx = db.transaction(STORE_PUNCHES, 'readwrite');
  const store = tx.objectStore(STORE_PUNCHES);

  for (const id of punchIds) {
    const request = store.get(id);
    request.onsuccess = () => {
      const punch = request.result;
      if (punch) {
        punch.synced = true;
        punch.synced_at = new Date().toISOString();
        store.put(punch);
      }
    };
  }

  return new Promise((resolve) => {
    tx.oncomplete = () => resolve(true);
  });
}

// ==========================================
// SYNC LOGIC
// ==========================================

async function syncPendingPunches() {
  const pending = await getPendingPunches();
  if (pending.length === 0) {
    console.log('[SW Ponto] Nenhuma batida pendente');
    return { synced: 0, errors: 0 };
  }

  console.log(`[SW Ponto] Sincronizando ${pending.length} batidas`);

  // Batch de 20
  const batchSize = 20;
  let totalSynced = 0;
  let totalErrors = 0;

  for (let i = 0; i < pending.length; i += batchSize) {
    const batch = pending.slice(i, i + batchSize);

    try {
      const response = await fetch('/api/v1/people-management/ponto/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          punches: batch.map((p) => ({
            employee_id: p.employee_id,
            punch_type: p.punch_type,
            timestamp: p.timestamp,
            is_offline: true,
            device_type: p.device_type || 'pwa',
            location: p.location,
            facial: p.facial,
          })),
        }),
      });

      if (response.ok) {
        const result = await response.json();
        totalSynced += result.total_synced;
        await markAsSynced(batch.map((p) => p.punch_id));
      } else {
        totalErrors += batch.length;
      }
    } catch (err) {
      console.error('[SW Ponto] Erro no sync:', err);
      totalErrors += batch.length;
    }
  }

  console.log(`[SW Ponto] Sync completo: ${totalSynced} ok, ${totalErrors} erros`);

  // Notifica clients
  const clients = await self.clients.matchAll();
  clients.forEach((client) => {
    client.postMessage({
      type: 'SYNC_COMPLETE',
      result: { synced: totalSynced, errors: totalErrors },
    });
  });

  return { synced: totalSynced, errors: totalErrors };
}

// ==========================================
// ONLINE/OFFLINE DETECTION
// ==========================================

self.addEventListener('online', () => {
  console.log('[SW Ponto] Voltou online - iniciando sync');
  syncPendingPunches();
});

console.log('[SW Ponto] Service Worker carregado');
