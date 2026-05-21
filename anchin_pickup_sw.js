// ==========================================
// NewCore 安親接車系統 — Service Worker
// ==========================================

const CACHE_NAME = 'anchin-pickup-v1';

// 靜態資源：離線也能開啟
const STATIC_ASSETS = [
  '/newcore-pro/anchin_pickup.html',
  '/newcore-pro/anchin_pickup_manifest.json',
];

// ── 安裝：預先快取靜態資源 ──
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[SW] 預快取靜態資源');
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// ── 啟用：清除舊版快取 ──
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => {
            console.log('[SW] 清除舊快取：', key);
            return caches.delete(key);
          })
      )
    )
  );
  self.clients.claim();
});

// ── Fetch 攔截：分兩種策略 ──
self.addEventListener('fetch', event => {
  const url = event.request.url;

  // GAS API → Network First（有網路就抓最新，失敗才用快取）
  if (
    url.includes('script.google.com') ||
    url.includes('googleapis.com')
  ) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // 靜態資源 → Cache First（離線也能開啟）
  event.respondWith(cacheFirst(event.request));
});

// Network First 策略
async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch {
    console.log('[SW] 離線，使用快取資料：', request.url);
    const cached = await cache.match(request);
    return cached || new Response(
      JSON.stringify({ error: '離線且無快取資料' }),
      { headers: { 'Content-Type': 'application/json' } }
    );
  }
}

// Cache First 策略
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch {
    return new Response('離線中，資源無法載入', { status: 503 });
  }
}
