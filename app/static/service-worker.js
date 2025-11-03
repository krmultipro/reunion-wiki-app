const CACHE_NAME = "reunionwiki-cache-v7";

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
  const url = new URL(event.request.url);
  
  // Ignorer les requêtes vers des domaines externes (CDN, APIs, etc.)
  // Ne gérer que les requêtes vers notre propre origine
  if (url.origin !== self.location.origin) {
    // Laisser passer les requêtes externes sans interception
    return;
  }

  // Pour les requêtes de navigation (pages HTML)
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Ne mettre en cache que les réponses valides
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // En cas d'erreur, essayer de récupérer depuis le cache
          return caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // Si aucun cache, retourner une réponse d'erreur
            return new Response("Ressource non disponible hors ligne", {
              status: 503,
              statusText: "Service Unavailable",
              headers: new Headers({ "Content-Type": "text/plain" }),
            });
          });
        })
    );
    return;
  }

  // Pour les autres requêtes (assets statiques)
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      // Si pas en cache, faire une requête réseau
      return fetch(event.request)
        .then((response) => {
          // Ne mettre en cache que les réponses valides
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Si la requête échoue, retourner une réponse d'erreur au lieu de undefined
          return new Response("Ressource non disponible hors ligne", {
            status: 503,
            statusText: "Service Unavailable",
            headers: new Headers({ "Content-Type": "text/plain" }),
          });
        });
    })
  );
});
