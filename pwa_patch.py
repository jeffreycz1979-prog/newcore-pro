# 從 stdin 讀取原版 HTML，做精準替換後輸出

import sys
html = sys.stdin.read()

# ===== ① PWA meta tags =====
html = html.replace(
    '<title>NewCore 語音點名</title>\n<style>',
    '''<title>NewCore 語音點名</title>

<!-- ══ PWA ══ -->
<link rel="manifest" href="/newcore-attendance/newcore_manifest.json">
<meta name="theme-color" content="#274e13">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="NewCore">

<style>'''
)

# ===== ② 離線橫幅 CSS =====
html = html.replace(
    '  * { box-sizing: border-box; margin: 0; padding: 0; }',
    '''  /* ── 離線橫幅 ── */
  #sw-offline-banner {
    display: none;
    position: fixed; top: 0; left: 0; right: 0;
    background: #ff6b35; color: white;
    text-align: center; padding: 10px 16px;
    font-size: 13px; z-index: 9999;
    font-family: 'Segoe UI', sans-serif;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }'''
)

# ===== ③ 離線橫幅 div =====
html = html.replace(
    '<div id="login-screen" class="login-wrap">',
    '''<!-- ══ 離線提示橫幅 ══ -->
<div id="sw-offline-banner">⚠️ 目前離線 — 使用上次登入資料，儲存操作需連網才生效</div>

<div id="login-screen" class="login-wrap">'''
)

# ===== ④ autoLogin — 離線優先 =====
html = html.replace(
    """function autoLogin() {
  document.getElementById('login-btn').disabled = true;
  document.getElementById('login-err').textContent = '自動登入中...';
  jsonpCall({ action: 'verifyAuth', authCode: AUTH_CODE }, function(err, data) {
    document.getElementById('login-btn').disabled = false;
    if (err || !data || !data.ok) {
      localStorage.removeItem('nc_auth_code');
      AUTH_CODE = '';
      document.getElementById('login-err').textContent = '';
      return;
    }
    onLoginSuccess(data);
  });
}""",
    """// ── 離線橫幅控制 ──
function showOfflineBanner() {
  var b = document.getElementById('sw-offline-banner');
  if (b) { b.style.display = 'block'; document.querySelector('.body') && (document.querySelector('.body').style.paddingTop = '40px'); }
}
function hideOfflineBanner() {
  var b = document.getElementById('sw-offline-banner');
  if (b) { b.style.display = 'none'; document.querySelector('.body') && (document.querySelector('.body').style.paddingTop = ''); }
}

function autoLogin() {
  document.getElementById('login-btn').disabled = true;
  document.getElementById('login-err').textContent = '驗證中...';

  // ── 離線優先：沒網路時直接用 localStorage 資料進入 ──
  if (!navigator.onLine) {
    var savedName = localStorage.getItem('nc_user_name');
    var savedRole = localStorage.getItem('nc_user_role');
    if (savedName) {
      document.getElementById('login-btn').disabled = false;
      document.getElementById('login-err').textContent = '';
      onLoginSuccess({ name: savedName, role: savedRole || 'teacher' }, null, true);
      return;
    }
    document.getElementById('login-btn').disabled = false;
    document.getElementById('login-err').textContent = '⚠️ 離線中，請先連網登入一次';
    return;
  }

  // ── 有網路：正常驗證 ──
  jsonpCall({ action: 'verifyAuth', authCode: AUTH_CODE }, function(err, data) {
    document.getElementById('login-btn').disabled = false;
    if (err || !data || !data.ok) {
      var savedName = localStorage.getItem('nc_user_name');
      if (savedName) {
        document.getElementById('login-err').textContent = '';
        onLoginSuccess({ name: savedName, role: localStorage.getItem('nc_user_role') || 'teacher' }, null, true);
        showToast('⚠️ 驗證異常，以離線模式進入');
        return;
      }
      localStorage.removeItem('nc_auth_code');
      AUTH_CODE = '';
      document.getElementById('login-err').textContent = '';
      return;
    }
    onLoginSuccess(data);
  });
}"""
)

# ===== ⑤ window load 加離線偵測 =====
html = html.replace(
    """  // 嘗試自動登入
  if (SHEET_ID && AUTH_CODE && API_URL) autoLogin();""",
    """  // 離線偵測
  if (!navigator.onLine) showOfflineBanner();
  window.addEventListener('offline', showOfflineBanner);
  window.addEventListener('online', function() {
    hideOfflineBanner();
    if (AUTH_CODE && SHEET_ID && API_URL) {
      jsonpCall({ action: 'verifyAuth', authCode: AUTH_CODE }, function(err, data) {
        if (err || !data || !data.ok) showToast('⚠️ 連線恢復但驗證失敗，請重新登入');
      });
    }
  });

  // 嘗試自動登入
  if (SHEET_ID && AUTH_CODE && API_URL) autoLogin();"""
)

# ===== ⑥ onLoginSuccess 加 isOffline 參數 + 儲存使用者資料 =====
html = html.replace(
    "function onLoginSuccess(data, licData) {",
    "function onLoginSuccess(data, licData, isOffline) {"
)
html = html.replace(
    """  currentUser = data;
  if (licData && licData.plan) currentUser.plan = licData.plan;

  // Trial 到期鎖定
  if (licData && licData.trialDaysLeft !== null && licData.trialDaysLeft !== undefined) {""",
    """  currentUser = data;
  if (licData && licData.plan) currentUser.plan = licData.plan;

  // ── 儲存使用者資料供離線使用 ──
  localStorage.setItem('nc_user_name', data.name);
  localStorage.setItem('nc_user_role', data.role || 'teacher');

  // 離線模式顯示橫幅
  if (isOffline) showOfflineBanner();

  // Trial 到期鎖定（離線模式略過）
  if (!isOffline && licData && licData.trialDaysLeft !== null && licData.trialDaysLeft !== undefined) {"""
)
# 修正：離線時略過 isGrace
html = html.replace(
    "  // 寬限期警告（Standard/Pro 到期）\n  if (licData && licData.isGrace) showToast('⚠️ ' + licData.message);",
    "  // 寬限期警告（Standard/Pro 到期）\n  if (!isOffline && licData && licData.isGrace) showToast('⚠️ ' + licData.message);"
)
html = html.replace(
    "  // Trial 剩餘天數提示（7天內顯示橫幅）\n  if (licData && licData.trialDaysLeft !== null && licData.trialDaysLeft !== undefined) {\n    if (licData.trialDaysLeft <= 7) showTrialBanner(licData.trialDaysLeft);\n  }\n  if (licData && licData.isGrace) showToast('⚠️ ' + licData.message);",
    "  // Trial 剩餘天數提示（7天內顯示橫幅）\n  if (!isOffline && licData && licData.trialDaysLeft !== null && licData.trialDaysLeft !== undefined) {\n    if (licData.trialDaysLeft <= 7) showTrialBanner(licData.trialDaysLeft);\n  }\n  if (!isOffline && licData && licData.isGrace) showToast('⚠️ ' + licData.message);"
)

# ===== ⑦ doLogout 加清除離線快取 =====
html = html.replace(
    """  localStorage.removeItem('nc_auth_code');
  localStorage.removeItem('nc_sheet_id');
  document.getElementById('login-screen').style.display = 'flex';""",
    """  localStorage.removeItem('nc_auth_code');
  localStorage.removeItem('nc_sheet_id');
  localStorage.removeItem('nc_user_name');
  localStorage.removeItem('nc_user_role');
  hideOfflineBanner();
  document.getElementById('login-screen').style.display = 'flex';"""
)

# ===== ⑧ </body> 前加 SW 註冊 =====
html = html.replace(
    '</body>\n</html>',
    '''
<!-- ══ PWA：Service Worker 註冊 ══ -->
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker
        .register('/newcore-attendance/newcore_sw.js', { scope: '/newcore-attendance/' })
        .then(function(reg) { console.log('[PWA] SW 已註冊，scope：', reg.scope); })
        .catch(function(err) { console.warn('[PWA] SW 註冊失敗：', err); });
    });
  }
</script>
</body>
</html>'''
)

print(html, end='')
