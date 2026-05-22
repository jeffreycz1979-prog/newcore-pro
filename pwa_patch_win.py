# Windows 版 PWA Patch 腳本 v2
# 使用方式：放到 newcore-pro 資料夾，執行 python3 pwa_patch_win.py

# 讀檔時統一換行符號
with open('index.html', 'r', encoding='utf-8', newline='') as f:
    html = f.read()

# 統一成 \n（處理 Windows \r\n 問題）
html = html.replace('\r\n', '\n').replace('\r', '\n')

original_length = len(html.splitlines())
print(f"原版行數：{original_length}")

changes = 0

# ① PWA meta tags
old = '<title>NewCore \u8a9e\u97f3\u9ede\u540d</title>\n<style>'
new = '''<title>NewCore \u8a9e\u97f3\u9ede\u540d</title>

<!-- \u2550\u2550 PWA \u2550\u2550 -->
<link rel="manifest" href="/newcore-pro/newcore_manifest.json">
<meta name="theme-color" content="#274e13">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="NewCore">

<style>'''
if old in html:
    html = html.replace(old, new, 1)
    changes += 1
    print("✓ ① PWA meta tags 插入成功")
else:
    print("✗ ① 找不到錨點：title+style")

# ② 離線橫幅 CSS
old = '  * { box-sizing: border-box; margin: 0; padding: 0; }'
new = '''  /* \u2500\u2500 \u96e2\u7dda\u6a6b\u5e45 \u2500\u2500 */
  #sw-offline-banner {
    display: none;
    position: fixed; top: 0; left: 0; right: 0;
    background: #ff6b35; color: white;
    text-align: center; padding: 10px 16px;
    font-size: 13px; z-index: 9999;
    font-family: 'Segoe UI', sans-serif;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }'''
if old in html:
    html = html.replace(old, new, 1)
    changes += 1
    print("✓ ② 離線橫幅 CSS 插入成功")
else:
    print("✗ ② 找不到錨點：* box-sizing")

# ③ 離線橫幅 div
old = '<div id="login-screen" class="login-wrap">'
new = '''<!-- \u2550\u2550 \u96e2\u7dda\u63d0\u793a\u6a6b\u5e45 \u2550\u2550 -->
<div id="sw-offline-banner">\u26a0\ufe0f \u76ee\u524d\u96e2\u7dda \u2014 \u4f7f\u7528\u4e0a\u6b21\u767b\u5165\u8cc7\u6599\uff0c\u5132\u5b58\u64cd\u4f5c\u9700\u9023\u7db2\u624d\u751f\u6548</div>

<div id="login-screen" class="login-wrap">'''
if old in html:
    html = html.replace(old, new, 1)
    changes += 1
    print("✓ ③ 離線橫幅 div 插入成功")
else:
    print("✗ ③ 找不到錨點：login-screen")

# ④ autoLogin 離線優先
old = "function autoLogin() {\n  document.getElementById('login-btn').disabled = true;\n  document.getElementById('login-err').textContent = '\u81ea\u52d5\u767b\u5165\u4e2d...';"
new = """// \u2500\u2500 \u96e2\u7dda\u6a6b\u5e45\u63a7\u5236 \u2500\u2500
function showOfflineBanner() {
  var b = document.getElementById('sw-offline-banner');
  if (b) b.style.display = 'block';
}
function hideOfflineBanner() {
  var b = document.getElementById('sw-offline-banner');
  if (b) b.style.display = 'none';
}

function autoLogin() {
  document.getElementById('login-btn').disabled = true;
  document.getElementById('login-err').textContent = '\u9a57\u8b49\u4e2d...';

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
    document.getElementById('login-err').textContent = '\u26a0\ufe0f \u96e2\u7dda\u4e2d\uff0c\u8acb\u5148\u9023\u7db2\u767b\u5165\u4e00\u6b21';
    return;
  }"""
if "function autoLogin() {\n  document.getElementById('login-btn').disabled = true;\n  document.getElementById('login-err').textContent = '\u81ea\u52d5\u767b\u5165\u4e2d...';" in html:
    html = html.replace(old, new, 1)
    # 繼續替換 autoLogin 的後半部
    old2 = "  jsonpCall({ action: 'verifyAuth', authCode: AUTH_CODE }, function(err, data) {\n    document.getElementById('login-btn').disabled = false;\n    if (err || !data || !data.ok) {\n      localStorage.removeItem('nc_auth_code');\n      AUTH_CODE = '';\n      document.getElementById('login-err').textContent = '';\n      return;\n    }\n    onLoginSuccess(data);\n  });\n}"
    new2 = """
  jsonpCall({ action: 'verifyAuth', authCode: AUTH_CODE }, function(err, data) {
    document.getElementById('login-btn').disabled = false;
    if (err || !data || !data.ok) {
      var savedName = localStorage.getItem('nc_user_name');
      if (savedName) {
        document.getElementById('login-err').textContent = '';
        onLoginSuccess({ name: savedName, role: localStorage.getItem('nc_user_role') || 'teacher' }, null, true);
        showToast('\u26a0\ufe0f \u9a57\u8b49\u7570\u5e38\uff0c\u4ee5\u96e2\u7dda\u6a21\u5f0f\u9032\u5165');
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
    if old2 in html:
        html = html.replace(old2, new2, 1)
    changes += 1
    print("✓ ④ autoLogin 離線優先插入成功")
else:
    print("✗ ④ 找不到錨點：autoLogin")

# ⑤ window load 加離線偵測
old = "  // \u5617\u8a66\u81ea\u52d5\u767b\u5165\n  if (SHEET_ID && AUTH_CODE && API_URL) autoLogin();"
new = """  // \u96e2\u7dda\u5075\u6e2c
  if (!navigator.onLine) showOfflineBanner();
  window.addEventListener('offline', showOfflineBanner);
  window.addEventListener('online', function() {
    hideOfflineBanner();
    if (AUTH_CODE && SHEET_ID && API_URL) {
      jsonpCall({ action: 'verifyAuth', authCode: AUTH_CODE }, function(err, data) {
        if (err || !data || !data.ok) showToast('\u26a0\ufe0f \u9023\u7dda\u6062\u5fa9\u4f46\u9a57\u8b49\u5931\u6557\uff0c\u8acb\u91cd\u65b0\u767b\u5165');
      });
    }
  });

  // \u5617\u8a66\u81ea\u52d5\u767b\u5165
  if (SHEET_ID && AUTH_CODE && API_URL) autoLogin();"""
if old in html:
    html = html.replace(old, new, 1)
    changes += 1
    print("✓ ⑤ 離線偵測插入成功")
else:
    print("✗ ⑤ 找不到錨點：嘗試自動登入")

# ⑥ onLoginSuccess 加 isOffline
old = "function onLoginSuccess(data, licData) {"
if old in html:
    html = html.replace(old, "function onLoginSuccess(data, licData, isOffline) {", 1)
    changes += 1
    print("✓ ⑥ onLoginSuccess isOffline 參數插入成功")
else:
    print("✗ ⑥ 找不到錨點：onLoginSuccess")

# ⑦ 儲存使用者資料
old = "  currentUser = data;\n  if (licData && licData.plan) currentUser.plan = licData.plan;\n\n  // Trial \u5230\u671f\u9396\u5b9a"
new = """  currentUser = data;
  if (licData && licData.plan) currentUser.plan = licData.plan;

  // \u2500\u2500 \u5132\u5b58\u4f7f\u7528\u8005\u8cc7\u6599\u4f9b\u96e2\u7dda\u4f7f\u7528 \u2500\u2500
  localStorage.setItem('nc_user_name', data.name);
  localStorage.setItem('nc_user_role', data.role || 'teacher');
  if (isOffline) showOfflineBanner();

  // Trial \u5230\u671f\u9396\u5b9a"""
if old in html:
    html = html.replace(old, new, 1)
    changes += 1
    print("✓ ⑦ 儲存使用者資料插入成功")
else:
    print("✗ ⑦ 找不到錨點：currentUser = data")

# ⑧ doLogout 清除快取
old = "  localStorage.removeItem('nc_auth_code');\n  localStorage.removeItem('nc_sheet_id');\n  document.getElementById('login-screen').style.display = 'flex';"
new = """  localStorage.removeItem('nc_auth_code');
  localStorage.removeItem('nc_sheet_id');
  localStorage.removeItem('nc_user_name');
  localStorage.removeItem('nc_user_role');
  hideOfflineBanner();
  document.getElementById('login-screen').style.display = 'flex';"""
if old in html:
    html = html.replace(old, new, 1)
    changes += 1
    print("✓ ⑧ doLogout 清除快取插入成功")
else:
    print("✗ ⑧ 找不到錨點：doLogout localStorage")

# ⑨ SW 註冊
old = '</body>\n</html>'
new = '''
<!-- \u2550\u2550 PWA\uff1aService Worker \u8a3b\u518a \u2550\u2550 -->
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker
        .register('/newcore-pro/newcore_sw.js', { scope: '/newcore-pro/' })
        .then(function(reg) { console.log('[PWA] SW \u5df2\u8a3b\u518a\uff0cscope\uff1a', reg.scope); })
        .catch(function(err) { console.warn('[PWA] SW \u8a3b\u518a\u5931\u6557\uff1a', err); });
    });
  }
</script>
</body>
</html>'''
if old in html:
    html = html.replace(old, new, 1)
    changes += 1
    print("✓ ⑨ SW 註冊插入成功")
else:
    print("✗ ⑨ 找不到錨點：</body></html>")

# 寫出結果
with open('index_pwa.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)

new_length = len(html.splitlines())
diff = new_length - original_length
print(f"\n原版：{original_length} 行 → 修改後：{new_length} 行（新增 {diff} 行）")
print(f"成功替換：{changes}/9 個位置")

if changes >= 7:
    print("\n✅ 成功！執行以下指令取代原版：")
    print("   mv index_pwa.html index.html   (Mac/Linux)")
    print("   move index_pwa.html index.html  (Windows)")
else:
    print(f"\n⚠️  只有 {changes}/9 個替換成功，請截圖給 Claude 看")