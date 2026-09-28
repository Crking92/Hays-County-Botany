const CACHE_NAME = "hays-botany-field-v12-github";
const scopedUrl = (path = "") => new URL(path, self.registration.scope).href;
const HOME_URL = scopedUrl();
const APP_SHELL = [
  "",
  "manifest.webmanifest",
  "favicon.svg",
  "downloads/Hays_Botany_Image_Registry.xlsx",
  "downloads/Hays_County_Botany_Master_List.xlsx",
  "images/ut-study/tetragonotheca-phyllaries.jpg",
  "images/ut-study/brickellia-fruiting-heads.jpg",
  "images/ut-study/arundo-node-open-sheath.jpg",
  "images/ut-study/bothriochloa-awns.jpg",
  "images/ut-study/medicago-stipules.jpg",
  "images/ut-study/chamaecrista-legume.jpg",
  "images/ut-study/euphorbia-bicolor-cyathia.jpg",
  "images/ut-study/croton-fruit-stigmas.jpg",
  "images/ut-study/monarda-bilabiate-corolla.jpg",
  "images/ut-study/trichostema-flower-calyx.jpg",
  "images/ut-study/cyperus-triangular-culm.jpg",
  "images/ut-study/cyperus-spikelets.jpg",
].map(scopedUrl);

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key !== CACHE_NAME)
            .map((key) => caches.delete(key)),
        ),
      )
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(HOME_URL, copy));
          return response;
        })
        .catch(() => caches.match(HOME_URL)),
    );
    return;
  }

  if (["style", "script", "font", "image"].includes(request.destination)) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((response) => {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
            return response;
          }),
      ),
    );
  }
});
