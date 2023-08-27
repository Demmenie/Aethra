// 21/12/2022
// Chico Demmenie
// Aethra/web/static/serviceWorker.js

// You need to declare a cache name
const cacheName = "aethra"

// Pages and files that will be stored in cache
const precache_assets = [
    "/",
    "/offline",
    "/about",
    "/url_deny",
    "/aethra.webmanifest",
    "/assets/bmc_icon.png",
    "/assets/favicon.ico",
    "/assets/icon-256.png",
    "/assets/icon-128.png",
    "/assets/icon-64.png",
    "/assets/icon-32.png",
    "/assets/twitterLogo.png",
    "/static/organise.js",
    "/static/widgets.js",
    "/static/css/extraStyle.css",
    "/static/css/searchStyle.css",
    "/static/css/style.css",
    // "https://pyscript.net/alpha/pyscript.css"
]

// Runs on service worker install
self.addEventListener('install', e => {
    console.log('[Service Worker] install')

    // Wait for cache to be open and then add all files in precache_assets
    const addToCache = async () => {
        const cache = await caches.open(cacheName);
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


/* Fetch event, for each request, the SW will try to fetch the file and chache
    it; if the fetch fails then a cached version is returned.*/
self.addEventListener("fetch", evt => {
    console.log("fetch event", evt);
    try{
    evt.respondWith(
     caches.match(evt.request).then(cacheRes => {
         return cacheRes || fetch(evt.request).then(fetchRes =>{
             return caches.open(cacheName).then(cache =>{
                 cache.put(evt.request.url, fetchRes.clone());
                 return fetchRes;
             })
         });
     }))
     } catch {
         return caches.match("/views/main/fallback.ejs");
     }
 });


// Two other versions of the above section which didn't work too well.
/*
// Runs when the service worker fetches a file
self.addEventListener("fetch", e => {
    e.respondWith(
        async () => {
            try{
                // First see if the response is cached
                const cache = await caches.open(cacheName);
                console.log('[Service Worker] Fetching resource:',
                    e.request.url);
                let cachedRes = await cache.match(e.response);

                if (cachedRes) {
                    console.log('[Service Worker] Returning cached result');
                    const cachedRes = caches.match(e.request);
                    console.log(cachedRes)
                    return cachedRes;
                } else {
                    console.log('[Service Worker] Caching new resource:',
                        e.request.url);
                    const networkRes = await fetch(e.request);
                    await cache.put(e.request, networkRes.clone());
                    console.log(networkRes)
                    return networkRes;
                }
            } catch (error) {
                console.log('[Service Worker] Error:', error)
                const cachedRes = cache.match("/offline")
                console.log(cachedRes)
                return cachedRes;
            }
        }

        // A different version of the fetch section which worked roughly the same.
        
        async () => {
            const cache = await caches.open(cacheName);
            cache.match(e.request).then(function (r) {
                console.log('[Service Worker] Fetching resource:', e.request.url);
                return r || fetch(e.request).then(async (response) => {
                    return await caches.open(cacheName).then(async (cache) => {
                        console.log('[Service Worker] Caching new resource:',
                            e.request.url);
                        await cache.put(e.request, response.clone());
                        return response;
                    });
                });
            })
        }
        
    );
}); */