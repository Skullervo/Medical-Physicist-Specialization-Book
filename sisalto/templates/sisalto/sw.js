const CACHE_NAME = 'erikoistuminen-v2';
const OFFLINE_URL = '/offline/';

// Cache offline page on install
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll([OFFLINE_URL]))
            .then(() => self.skipWaiting())
    );
});

// Clean old caches on activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
            )
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // Never cache API or auth endpoints
    if (url.pathname.startsWith('/api/') ||
        url.pathname.startsWith('/quiz/api/') ||
        url.pathname.startsWith('/exam/') ||
        url.pathname.startsWith('/modaliteetit/api/') ||
        url.pathname.startsWith('/login') ||
        url.pathname.startsWith('/logout') ||
        url.pathname.startsWith('/admin')) {
        return;
    }

    // Cache-first for static assets (CSS, JS, fonts, images)
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(event.request).then(cached => {
                if (cached) return cached;
                return fetch(event.request).then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    }
                    return response;
                });
            })
        );
        return;
    }

    // Network-first for navigation requests, offline fallback
    // Use cache: 'no-cache' to bypass browser HTTP cache and always revalidate with server
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request, { cache: 'no-cache' }).catch(() => caches.match(OFFLINE_URL))
        );
    }
});
