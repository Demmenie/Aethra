// Service workers are a pain in my ass
// you're all welcome xxxx

// You need to declare a cache name
const cacheName = "aethra"

// Pages and files that will be stored in cache
const precache_assets = [
    "/",
    "/about",
    "/url_deny",
    "/assets/bmc_icon.png",
    "/assets/favicon.ico",
    "/assets/icon.png",
    "/assets/twitterLogo.png",
    "/static/aethra.webmanifest",
    "/static/organise.js",
    "/static/widgets.js",
    "/static/css/extraStyle.css",
    "/static/css/searchStyle.css",
    "/static/css/style.css"
]

// Runs on service worker install
self.addEventListener('install', e => {
    console.log('[Service Worker] install')

    // Wait for cache to be open and then add all files in precache_assets
    const addToCache = async () => {
        const cache = await caches.open("aethra");
        console.log("[Service Worker] Caching")
        await cache.addAll(precache_assets)
    }

    // Use waitUntil to ensure the service worker doesn't shut
    // down until files have been added to cache
    e.waitUntil(addToCache())
});

// Runs of service worker activation
self.addEventListener('activate', e => {
    console.log("[Service Worker] Activating")

    // Claims the browser window without having to reload the page
    e.waitUntil(clients.claim())
});

// Runs when the service worker fetches a file
self.addEventListener("fetch", e => {
    console.log("[Service Worker] Fetching");

    const response = async () => {
        const cache = await caches.open("aethra");

        // If file is in cache, then serve that file
        const cachedResponse = await cache.match(e.request);
        if(cachedResponse){
            console.log("[Service Worker] Sending file from cache");
            return cachedResponse;
        }

        // Fetch the file from the server
        const response = await fetch(e.request);

        // Return file if found in server
        if(!response || response.status !== 200 || response.type !== "basic"){
            console.log("[Service Worker] Sending file from server");
            return response
        }

        console.error(`[Service Worker] ERR: file not found / invalid`);
        return response
    }

    // Respond to fetch request with whatever is returned from func
    e.respondWith(response());
})