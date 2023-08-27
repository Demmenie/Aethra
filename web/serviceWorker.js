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

                console.log(`[Service Worker] ${evt.request.url} Returning cache.`)
                return cacheRes.then(cacheRes =>{ 
                        fetch(evt.request).then(fetchRes =>{
                        
                        console.log(`[Service Worker] ${evt.request.url} Requesting page`)
                        return caches.open(cacheName).then(cache =>{
                            
                            console.log(`[Service Worker] ${evt.request.url} Checking cache against new page`)
                            
                            if (toString(fetchRes) === toString(cacheRes)) {
                                console.log(`[Service Worker] ${evt.request.url} New page was the same`)
                            
                            } else {
                                console.log(`[Service Worker] ${evt.request.url} New page was different, caching and returning`)
                                
                                cache.put(evt.request.url, fetchRes.clone());
                                return fetchRes;
                            }
                        })
                    });
                })
            }))
     } catch {
        return caches.match("/views/main/fallback.ejs");
     }
 });