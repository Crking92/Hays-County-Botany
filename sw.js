const CACHE_NAME = "hays-botany-v49";
const CORE = [
  "./",
  "./index.html",
  "./assets/js/learner-glossary.js",
  "./assets/js/glossary-photo-media.js",
  "./assets/css/learner-glossary.css",
  "./field-id.html",
  "./field-id-classic.html",
  "./assets/js/field-id-tiles.js",
  "./assets/css/field-id-tiles.css",
  "./data/field-id-index.json",
  "./quiz.html",
  "./quiz-classic.html",
  "./assets/js/quiz-tiles.js",
  "./assets/js/reed-quiz.js",
  "./assets/css/quiz-tiles.css",
  "./manifest.webmanifest",
  "./assets/app-icon.svg",
  "./assets/css/styles.css",
  "./assets/js/app.js",
  "./data/manifest.json",
  "./data/learner-search-index.json",
  "./data/project.json",
  "./data/learning-layer.json"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      Promise.allSettled(CORE.map(url => cache.add(url)))
    )
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Photo Lab is an actively changing review gallery. Never silently serve a
  // cached old batch: always request the deployed version from the network.
  // It is intentionally not pre-cached for offline use.
  if (url.pathname.endsWith("/photo-review.html")) {
    event.respondWith(fetch(request, { cache: "no-store" }));
    return;
  }

  event.respondWith(
    fetch(request)
      .then(response => {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        }
        return response;
      })
      .catch(async () => {
        const cached = await caches.match(request);
        if (cached) return cached;
        if (request.mode === "navigate") {
          return caches.match("./index.html");
        }
        throw new Error("Offline and resource not cached");
      })
  );
});
