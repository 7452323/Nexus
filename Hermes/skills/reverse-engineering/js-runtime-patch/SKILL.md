---
name: js-runtime-patch
category: reverse-engineering
description: >-
  Merged skill combining: env-patch, encrypted-api-protocol-reverse.
version: "1.0"
sources:
  - env-patch
  - encrypted-api-protocol-reverse
tags: [reverse-engineering, merged]
---

# js-runtime-patch

> **Merged from**: env-patch, encrypted-api-protocol-reverse
> **Source count**: 2

---

## Table of Contents

1. [env-patch](#env-patch)
2. [encrypted-api-protocol-reverse](#encrypted-api-protocol-reverse)

---

## env-patch

# Env Patch — JS补环境统一技能

## 补环境策略分层

| 层级 | 方法 | 适用场景 | 性能 |
|------|------|----------|------|
| L1 通用代理 | 全局 Proxy | 大多数网站 | 最快 |
| L2 特征补丁 | 具体属性/方法覆盖 | 检测较严的网站 | 中等 |
| L3 环境快照 | 浏览器真实环境导出 | 最严格的检测 | 最慢 |

## 4种注入方式

| 方式 | 方法 | 适用 |
|------|------|------|
| 文件注入 | 在 JS 代码前插入补丁 | Node.js 本地运行 |
| URL 重写 | 拦截 HTTP 请求插入补丁 | 远程加载场景 |
| eval 注入 | eval/Function 前插入补丁 | 动态执行场景 |
| Proxy | 用 Proxy 接管全局对象 | 通用代理场景 |

## 引擎选择

| 引擎 | 适用场景 | 限制 |
|------|----------|------|
| Node.js + jsdom | 大多数 Web 逆向 | 无浏览器 API |
| playwright + Firefox | 需要浏览器环境 | 较慢 |
| sdenv（纯 Node.js） | RS 412 等强检测 | 兼容性有限 |

## 常用补丁清单

- navigator / window / document / location
- localStorage / sessionStorage / Cookie
- WebGL / Canvas / AudioContext
- plugins / mimeTypes / fonts
- screen / history / performance
- setTimeout / setInterval / Date
- XMLHttpRequest / fetch / WebSocket

---

## encrypted-api-protocol-reverse

# Encrypted API Protocol Reverse

逆向全加密 API（请求+响应均为 AES-CBC/ECB 密文）的系统方法论。

## When to use

- API 请求和响应 body 都是密文（hex/base64），非 JSON
- 签名 = `md5(timestamp + key)` 或 `md5(query_string)` 模式
- 密钥/IV 在 webpack 模块闭包中（`_0x182b3c`、`_0x451b34` 等混淆变量）
- fetch/XHR hook 因页面导航时机丢失
- 从 Playwright `page.evaluate()` 发 fetch 返回 CORS 错误/503
- 需要区分 XOR 流加密 vs AES-CBC（密文长度可能相同）

## 5-Phase Workflow

### Phase 1: Static Analysis — JS Bundle Triage

```bash
# 下载所有 JS chunk
curl -sL "https://target.com/assets/app.*.js" -o app.js
curl -sL "https://target.com/assets/chunk-common.*.js" -o common.js

# 提取字符串池（Webpack 混淆后的 API 端点）
python3 -c "
import re
with open('app.js') as f: js = f.read()
for m in re.finditer(r'[\"\\x27](/[a-z_/A-Z]+)[\"\\x27]', js):
    print(m.group(1))
for kw in ['sign', 'encrypt', 'decrypt', 'md5', 'AES', 'DES', 'CryptoJS']:
    if kw.lower() in js.lower():
        print(f'FOUND: {kw}')
"
```

### Phase 2: Playwright CDP Interception (NOT fetch hook)

**为什么不用 fetch/XHR hook**: 页面导航会清空注入的 hook，SPA 在初始化早期就发送 API 请求。

**正确方法 — `page.route()` 或 `page.on('response')`**:

```python
from playwright.async_api import async_playwright
import asyncio

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 方法 1: route 拦截（捕获请求 body）
        captured_requests = []
        async def handle_route(route):
            if 'pwa.php' in route.request.url:
                captured_requests.append({
                    'url': route.request.url,
                    'method': route.request.method,
                    'postData': route.request.post_data
                })
            await route.continue_()
        await page.route('**/*', handle_route)
        
        # 方法 2: response 监听（捕获响应 body）
        captured_responses = []
        async def handle_response(response):
            if 'pwa.php' in response.url:
                body = await response.text()
                captured_responses.append({
                    'url': response.url,
                    'status': response.status,
                    'body': body[:500]
                })
        page.on('response', handle_response)
        
        await page.goto('https://target.com/#/home', wait_until='networkidle')
        await asyncio.sleep(5)
        
        print(f"Requests: {len(captured_requests)}, Responses: {len(captured_responses)}")
        await browser.close()

asyncio.run(main())
```

### Phase 3: Encryption Algorithm Diagnosis

**关键诊断问题**: 密文长度 = 明文长度，是 XOR 流加密还是 AES-CBC？

**诊断方法 — 多 block PT-CT 对比**:

```python
# 在 Playwright 中生成多组 PT-CT 对
result = await page.evaluate('''() => {
    const cd = window.CryptoData;
    return {
        "A16": cd.Encrypt("A".repeat(16)),
        "B16": cd.Encrypt("B".repeat(16)),
        "A32": cd.Encrypt("A".repeat(32)),
        "json46": cd.Encrypt('{"type":"getFeaturedList","page":1,"limit":20}'),
    };
}''')
```

**分析**:
```python
# XOR 模型: 对所有 PT，keystream 应该相同
# CBC 模型: 第 1 个 block 的 keystream 相同，第 2+ block 不同

ks_a32 = bytes(b ^ 0x41 for b in bytes.fromhex(a32_ct))
ks_json = bytes(a ^ b for a, b in zip(bytes.fromhex(json_ct), json_pt))

# 如果 ks_a32[16:32] != ks_json[16:32] → AES-CBC
# 如果 ks_a32[16:32] == ks_json[16:32] → XOR stream cipher
```

**诊断决策树**:
```
密文长度 == 明文长度？
├── 是 → 可能是 XOR 流加密或 AES-CBC (NoPadding)
│   ├── 多 block PT-CT keystream 一致 → XOR 流加密 ✓
│   └── 第 16 字节后 keystream 分歧 → AES-CBC ✓
├── 是 16 的倍数，且 ≥ 明文长度 → AES-CBC + PKCS7 padding
└── 是 Base64，长度 ≈ 明文 × 1.33 → AES-ECB/CBC + Base64
```

### Phase 4: Response Decryption

**模式 1: 响应可直接解密**

```javascript
const cd = window.CryptoData;
const json = JSON.parse(responseBody);
const decrypted = cd.Decrypt(json.data);  // 返回 JSON 对象
```

**模式 2: 响应二次加密**

某些 API 的 `data` 字段本身是再次加密的 base64，需两次 Decrypt:
```javascript
const first = cd.Decrypt(response.data);  // {data: "base64..."}
const second = cd.Decrypt(first.data);     // 实际数据
```

### Phase 5: Webpack Module Closure Extraction

通过 `webpackChunk_*` 数组提取模块源码：

```javascript
const wp = window.webpackChunk_91pron;  // webpackChunk_{appName}
for (let i = 0; i < wp.length; i++) {
    const chunk = wp[i];
    if (!Array.isArray(chunk) || chunk.length < 2) continue;
    const modules = chunk[1];
    for (const [id, fn] of Object.entries(modules)) {
        const src = fn.toString();
        if (src.includes('CryptoData')) {
            console.log(`Module ${id}: ${src.length} bytes`);
        }
    }
}
```

## CORS / Same-Origin Pitfall

**症状**: Playwright `page.evaluate()` 中 `fetch()` pwa.php 返回 503，但页面内部 XHR 正常。

**原因**: 页面请求是 same-origin（通过 Service Worker），`page.evaluate()` 的 `fetch()` 受 CORS 限制。

**解决**: 用 `page.route()` 或 `page.on('response')`，不要用 `page.evaluate()` 中的 `fetch()`。

## ForwardWidget Integration

### 方案 A: Playwright 代理服务（已验证可用）

**用 aiohttp，不是 http.server** — Playwright 和 HTTP server 必须在同一个 asyncio event loop。`http.server` 在独立线程运行会导致阻塞。

```python
# proxy_server.py — 完整的加密代理服务
import asyncio, json
from playwright.async_api import async_playwright
from aiohttp import web

PORT = 19191
PAGE = None

async def init_browser():
    global PAGE
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    PAGE = await context.new_page()
    await PAGE.goto('https://TARGET_SITE.com', wait_until='networkidle', timeout=30000)
    await asyncio.sleep(3)

async def do_encrypt(payload_str):
    try:
        return await PAGE.evaluate('''(payload) => {
            const cd = window.CryptoData;
            const enc = cd.Encrypt(payload);
            const p = new URLSearchParams(enc);
            return {dataHex: p.get("data"), sign: p.get("sign"),
                    timestamp: p.get("timestamp"), body: enc};
        }''', payload_str)
    except Exception as e:
        print(f"Encrypt error: {e}, reloading page...")
        await PAGE.goto('https://TARGET_SITE.com', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)
        return await do_encrypt(payload_str)

async def do_decrypt(data_hex):
    try:
        return await PAGE.evaluate(
            '(dataHex) => window.CryptoData.Decrypt(dataHex)', data_hex)
    except Exception as e:
        print(f"Decrypt error: {e}, reloading page...")
        await PAGE.goto('https://TARGET_SITE.com', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)
        return await do_decrypt(data_hex)

async def handle_encrypt(request):
    data = await request.json()
    result = await do_encrypt(data.get('payload', ''))
    return web.json_response(result)

async def handle_decrypt(request):
    data = await request.json()
    result = await do_decrypt(data.get('data', ''))
    return web.json_response({'result': result})

async def main():
    await init_browser()
    app = web.Application()
    app.router.add_post('/encrypt', handle_encrypt)
    app.router.add_post('/decrypt', handle_decrypt)
    app.router.add_get('/health', lambda r: web.json_response({'status': 'ok'}))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()
    print(f"Listening on http://0.0.0.0:{PORT}")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
```

**启动和测试**:
```bash
pip install --break-system-packages aiohttp playwright
playwright install chromium
python3 proxy_server.py &

# 测试
curl http://127.0.0.1:19191/health
curl -X POST http://127.0.0.1:19191/encrypt -H 'Content-Type: application/json' -d '{"payload":"test"}'
curl -X POST http://127.0.0.1:19191/decrypt -H 'Content-Type: application/json' -d '{"data":"<hex>"}'
```

**ForwardWidget 客户端**:
```javascript
var PROXY_URL = "http://127.0.0.1:19191";

async function proxyEncrypt(payload) {
  var payloadJson = typeof payload === 'string' ? payload : JSON.stringify(payload);
  var res = await Widget.http.post(PROXY_URL + "/encrypt",
    JSON.stringify({payload: payloadJson}),
    {headers: {"Content-Type": "application/json"}});
  return res.data;  // {dataHex, sign, timestamp, body}
}

async function proxyDecrypt(dataHex) {
  var res = await Widget.http.post(PROXY_URL + "/decrypt",
    JSON.stringify({data: dataHex}),
    {headers: {"Content-Type": "application/json"}});
  return res.data.result;
}
```

**陷阱**: 短密文（如 "test" 的 4 字节密文）解密会失败——`Decrypt` 内部 `JSON.parse("test")` 报错。这是预期行为，真实 API payload 都是 JSON。

### 方案 B: 预计算加密数据（轻量级）

用 Playwright 批量生成常用 payload 的加密数据，硬编码到 ForwardWidget。限制：只能请求预计算范围内的 page/keyword。

## Pitfalls

1. **fetch/XHR hook 时机问题** — SPA 初始化早期发请求，hook 注入太晚。用 CDP 层 `page.route()`
2. **密文长度 = 明文长度 ≠ XOR** — 是 NoPadding AES-CBC，用多 block PT-CT 对比验证
3. **单 block keystream 匹配的陷阱** — `"A"*16` 和 `"B"*16` 的 keystream 可能巧合相同，必须用 ≥2 blocks
4. **CORS 导致 503** — 不是服务端错误，是 CORS 拦截。用 `page.route()` 代替
5. **webpackChunk 名称因应用而异** — 从页面全局变量动态获取
8. **短密文 Decrypt 报 JSON.parse 错误** — `Decrypt("test")` 返回字符串 "test"，`JSON.parse("test")` 抛出 SyntaxError。真实 API payload 都是 JSON 对象，短字符串仅用于测试验证加密算法。代理服务的 `/decrypt` 端点需要 try/catch 处理此类情况
9. **Vue 3 prod 模式不暴露 `_instance`** — 无法遍历组件获取 `$api` 配置
10. **响应 data 可能二次加密** — 解密后检查 `typeof dec.data === 'string'`
11. **ForwardWidget 的 Widget.http.post 直接发到目标 API** — 加密代理只负责加解密，不中继请求。ForwardWidget 拿到 `{body}` 后自己 POST 到 pwa.php
12. **ForwardWidget MD5 必须纯 JS 实现** — ForwardWidget 运行在 JS bridge 中，没有 Node.js `crypto` 模块。需要内嵌纯 JS MD5（约 60 行）

## Reference Case

- `references/91porn-pwa-aes-cbc-reverse.md` — 91Porn PWA 完整逆向案例
- `templates/91porn-forwardwidget.js` — 91Porn ForwardWidget 模块（含 MD5 纯 JS 实现 + CryptoData 代理客户端）

---
