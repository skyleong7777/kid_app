/* Little Learning Garden service worker: instant start and offline use after the first visit. Content files stay encrypted in the cache. */
const VERSION = "14.15", SHELL = 'llg-shell-' + VERSION, DATA = 'llg-data-1';
self.addEventListener('install', e => { e.waitUntil(caches.open(SHELL).then(c => c.addAll(['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png'])).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('llg-') && k !== SHELL && k !== DATA).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
const keep = (name, req, res) => { if (res && res.ok && res.type === 'basic') { const copy = res.clone(); caches.open(name).then(c => c.put(req, copy)); } return res; };
self.addEventListener('message', e => { const list = e.data && e.data.keep; if (!Array.isArray(list)) return;
  e.waitUntil(caches.open(DATA).then(async c => { for (const u of list) { if (/-[0-9a-f]{8}\.bin$/.test(u) && !(await c.match(u))) { try { await c.add(u); } catch (_) {} } } })); });
self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;
  // content-addressed encrypted files never change: cache first, kept across app versions
  if (/\/d\/.+-[0-9a-f]{8}\.bin$/.test(url.pathname)) { e.respondWith(caches.open(DATA).then(c => c.match(req).then(hit => hit || fetch(req).then(r => keep(DATA, req, r))))); return; }
  // everything else is small: network first so updates appear straight away, cached copy when offline
  e.respondWith(fetch(req).then(r => keep(SHELL, req, r)).catch(() => caches.match(req).then(hit => hit || (req.mode === 'navigate' ? caches.match('index.html') : Response.error()))));
});
