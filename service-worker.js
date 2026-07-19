// Service Worker de POCUS Cardíaco para soporte sin conexión (Offline)
const CACHE_NAME = 'pocus-cardiaco-cache-v7';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.webmanifest',
  './assets/css/styles.css',
  './assets/js/app.js',
  './assets/js/data-loader.js',
  './assets/js/storage.js',
  './assets/js/theme.js',
  './assets/js/search.js',
  './assets/js/router.js',
  './data/sections.json',
  './data/measurements.json',
  './data/glossary.json',
  './data/abbreviations.json',
  './data/classifications.json',
  './data/minimum_pocus_set.json',
  './data/unit_warnings.json',
  './data/references.json',
  './data/metadata.json',
  './data/windows.json',
  './assets/images/pocus_fusion_branding.png',
  './assets/icons/icon-192.png',
  './assets/icons/icon-512.png',
  './assets/icons/icon-maskable-512.png'
];

// Evento de instalación: cachear recursos estáticos y data clínica
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Service Worker: Guardando recursos estáticos en caché');
      return cache.addAll(ASSETS_TO_CACHE);
    }).then(() => self.skipWaiting())
  );
});

// Evento de activación: limpiar cachés obsoletas
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('Service Worker: Eliminando caché obsoleta', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Evento de recuperación (Fetch): Estrategia Cache-First (Red de respaldo)
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // Retornar recurso cacheado si existe
      if (cachedResponse) {
        return cachedResponse;
      }
      
      // De lo contrario, intentar ir a la red
      return fetch(event.request).then((networkResponse) => {
        // Validar que la respuesta sea correcta y provenga de nuestro sitio
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
          return networkResponse;
        }

        // Clonar la respuesta para guardarla en caché dinámicamente
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });

        return networkResponse;
      }).catch(() => {
        // Si no hay internet y no está en caché, retornar error silencioso o fallback simple
        console.log('Recurso no disponible sin conexión:', event.request.url);
      });
    })
  );
});
