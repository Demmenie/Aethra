//22/12/2022
// Chico Demmenie
// Aethra/web/static/app.js

// Registers the service worker in the browser.
if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register('/serviceWorker.js')
        .then(reg => console.log("service worker registered"))
        .catch(err => console.log("service worker not registered", err))
}
