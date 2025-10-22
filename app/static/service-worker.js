const CACHE_NAME = "reunionwiki-cache-v6";

// Liste des fichiers à mettre en cache
const urlsToCache = [
  "/static/style.css", // ton fichier CSS principal
  "/static/icons/icon-192x192.png", // corriger le nom
  "/static/icons/icon-512x512.png", // corriger le nom
];

// Installation du service worker
self.addEventListener("install", (event) => {
  console.log("[SW] Installation en cours...");
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[SW] Mise en cache initiale...");
      return cache.addAll(urlsToCache);
    })
  );
  // Force l’activation immédiate du nouveau SW
  self.skipWaiting();
});

// Activation et suppression des anciens caches
self.addEventListener("activate", (event) => {
  console.log("[SW] Activation en cours...");
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log("[SW] Suppression du cache :", name);
            return caches.delete(name);
          })
      )
    )
  );
  // Prend immédiatement le contrôle des pages ouvertes
  self.clients.claim();
});

// Interception des requêtes réseau
self.addEventListener("fetch", (event) => {
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
          return response;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((response) => {
      return (
        response ||
        fetch(event.request).catch(() => {
          // Optionnel : fallback si la requête échoue (ex : offline)
        })
      );
    })
  );
});
