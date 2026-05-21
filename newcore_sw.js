// ==========================================
// NewCore 班級管理系統 — Service Worker
// ==========================================

const CACHE_NAME = 'newcore-v1';

// 靜態資源：登入畫面離線也能顯示
const STATIC_ASSETS = [
  '/newcore-attendance/index.html',
  '/newcore-attendance/newcore_manifest.json',
];

// 永遠需要網路的網域（授權 + GAS）
const NETWORK_ONLY_PATTERNS = [
  'script.google.com',
  'googleapis.com',
  'generativelanguage.googleapis.com',
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

// ── Fetch 攔截 ──
self.addEventListener('fetch', event => {
  const url = event.request.url;

  // 授權中心 / GAS / Gemini → 永遠走網路，不快取
  if (NETWORK_ONLY_PATTERNS.some(p => url.includes(p))) {
    event.respondWith(
      fetch(event.request).catch(() =>
        new Response(
          JSON.stringify({ ok: false, error: '離線中，無法連線至伺服器' }),
          { headers: { 'Content-Type': 'application/json' } }
        )
      )
    );
    return;
  }

  // 靜態資源 → Cache First（離線也能開啟）
  event.respondWith(cacheFirst(event.request));
});

// Cache First 策略
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch {
    return new Response('離線中，資源無法載入', { status: 503 });
  }
}
