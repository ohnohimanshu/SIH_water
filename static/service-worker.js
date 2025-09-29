// Cloudburst Alert System - Service Worker
// Caches core assets and supports offline fallback. Includes push notification hooks.

const CACHE_VERSION = 'v1.0.0';
const APP_CACHE = `cloudburst-app-${CACHE_VERSION}`;
const RUNTIME_CACHE = `cloudburst-runtime-${CACHE_VERSION}`;

// Core assets to precache (add more assets/routes as needed)
const PRECACHE_URLS = [
  '/',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(APP_CACHE).then((cache) => cache.addAll(PRECACHE_URLS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.map((key) => {
      if (![APP_CACHE, RUNTIME_CACHE].includes(key)) {
        return caches.delete(key);
      }
    }))).then(() => self.clients.claim())
  );
});

// Strategy: network-first for navigation requests; cache-first for static assets
self.addEventListener('fetch', (event) => {
  const request = event.request;

  // Bypass non-GET
  if (request.method !== 'GET') return;

  // HTML navigation requests -> network-first with offline fallback
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(RUNTIME_CACHE).then((cache) => cache.put(request, copy));
          return response;
        })
        .catch(() => caches.match(request).then((cached) => cached || caches.match('/pwa/offline/')))
    );
    return;
  }

  // Static assets -> cache-first
  const url = new URL(request.url);
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then((cached) => cached || fetch(request).then((response) => {
        const copy = response.clone();
        caches.open(APP_CACHE).then((cache) => cache.put(request, copy));
        return response;
      }))
    );
    return;
  }
});

// Optional: Push notifications handler (requires server-side Web Push setup)
self.addEventListener('push', (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (e) {}
  const title = data.title || 'Cloudburst Alert';
  const options = {
    body: data.body || 'You have a new notification.',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-192x192.png',
    data: data.data || {},
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = (event.notification.data && event.notification.data.url) || '/';
  event.waitUntil(clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
    for (const client of clientList) {
      if ('focus' in client) return client.focus();
    }
    if (clients.openWindow) return clients.openWindow(targetUrl);
  }));
});


