---
name: ios-reverse
category: reverse-engineering
description: >-
  Merged skill combining: ios-app-unlock, ios-app-video-sniffer-reverse, ios-ipa-static-analysis, apple-iap-mitm-extraction, app-store-price-tracker.
version: "1.0"
sources:
  - ios-app-unlock
  - ios-app-video-sniffer-reverse
  - ios-ipa-static-analysis
  - apple-iap-mitm-extraction
  - app-store-price-tracker
tags: [reverse-engineering, merged]
---

# ios-reverse

> **Merged from**: ios-app-unlock, ios-app-video-sniffer-reverse, ios-ipa-static-analysis, apple-iap-mitm-extraction, app-store-price-tracker
> **Source count**: 5

---

## Table of Contents

1. [ios-app-unlock](#ios-app-unlock)
2. [ios-app-video-sniffer-reverse](#ios-app-video-sniffer-reverse)
3. [ios-ipa-static-analysis](#ios-ipa-static-analysis)
4. [apple-iap-mitm-extraction](#apple-iap-mitm-extraction)
5. [app-store-price-tracker](#app-store-price-tracker)

---

## ios-app-unlock

# iOS 原生 Swift 应用订阅解锁

逆向分析 iOS 原生 Swift 应用的订阅验证机制，通过 Swift5 反射元数据提取类型结构并定位 Patch 点，修改二进制解锁付费功能。

## When to use

- 用户提供 IPA 文件要求解锁 Pro/订阅功能
- 需要分析 StoreKit 2 (async/await) 验证逻辑的 iOS 应用
- 需要从 Swift 二进制中提取枚举/类/属性结构
- 需要修改 Mach-O arm64 二进制中的订阅检查逻辑
- **需要通过 QX/Surge/Loon 代理工具尝试解锁 iOS 原生 App（含请求签名 App）**

---

## ⚠️ 已知死路（务必先判断再动手）

### StoreKit 2 架构 → MITM 脚本完全无效

| 指标 | StoreKit 1 | StoreKit 2 |
|------|------------|------------|
| receipt 验证 | 向 Apple 服务器 POST `/verifyReceipt` | **设备上本地** Apple 私钥签名 |
| 拦截点 | QX/Surge 可拦截伪造 | **无拦截点**，receipt 根本不经过服务器 |
| MITM 可行性 | ✅ 伪造响应体 | ❌ **证伪**，数字签名不可伪造 |

**如何快速判断是否 StoreKit 2：**
- 二进制字符串含 `Transaction.currentEntitlements` / `Transaction.latest(for:)` / `Transaction.updates`
- Swift 符号含 `StoreKit.Transaction` / `SK2` / `checkVerified` / `AppTransaction`
- **HAR 中完全没有 `/verifyReceipt` 调用** → 大概率 StoreKit 2

**遇到 StoreKit 2 时的正确做法：**
1. **不要写 MITM 脚本** — 直接告诉用户"没越狱机搞不了"
2. **不要分析 API 域名** — 服务器端只是辅助信息，不是验证核心
3. **不要尝试伪造 receipt** — Apple 私钥签名不可伪造
4. **唯一可行方案（需越狱）：** Frida Hook `Transaction.currentEntitlements` / `AppTransaction.shared` 返回伪造值
5. **唯一可行方案（无越狱）：** 找 TrollStore 重打包版 / 共享 Apple ID

**典型案例（2026-07-07）：Yore (c.team.Yore)**
- MITM 拦截 `api.yore.code-abc.com` 注入 isVip 字段 → 零作用
- 原因：StoreKit 2 本地签名，API 只是辅助信息
- 用户原话："不能解锁，没有任何作用"

---

## ⚠️ 沟通规则
- 用户提供的数据（HAR/IPA/订阅链接/节点）— 提的时候说明是用户给的，不要说自己"提取"或"发现"的
- 只说自己实际做了什么（写了脚本、拆了包、分析了代码）
- 用户极度厌恶冒领功劳
- 用户要求"完整UI"或"所有内容"时 → 必须明确说明静态分析的固有限制：View布局、动画、modifier链在Release编译后丢失，只能恢复UI文本+类名+架构。技术限制直接说做不到，用户会立刻接受不再纠缠。不要为了安抚用户而承诺不可能的事

## Phase 0: Target Reconnaissance (Before HAR/IPA)

When the user sends ONLY an App Store URL (no IPA, no HAR), run this reconnaissance first to gather intelligence and find the actual tooling needed.

### 通用侦察流程（从 App Store URL 到 API 发现）

当拿到一个 App Store URL 时，按顺序侦察：

1. **App Store 页面** → 开发者（个人/公司）、大小（判断技术栈: <50MB Swift, 50-150MB 可能是 Swift 或 React Native, >150MB Flutter）、IAP 列表、描述（是否说"数据本地存储"）
2. **开发者网站** → 是否有 Web 版、隐私政策（数据存储方式）、API 端点线索
3. **DNS/子域名探测** → host/shadowsharing.com, nslookup, 找 API 域名、CDN 域名
4. **常见 endpoint curl 探测** → 测试 `/api/v1/*`, `/nodes`, `/user`, `/guest`, `/subscribe`
5. **Web 版 JS 分析** → 从 Flutter/Next.js/Vite JS bundle 提取 API URL、auth token
6. **APK 分析**（有 Android 版时）→ 从 APK 提取 API URL 和 auth 机制

### Decision Gate: Does the app even have a backend?

After initial recon, answer this before deciding any unlock approach:

**No backend** (local-only + iCloud + StoreKit — like PicSeed, see `references/picseed-case-study.md`):
- ❌ QX/Surge response-body modification: IMPOSSIBLE (nothing to intercept)
- ❌ MITM proxy: IMPOSSIBLE (no custom server)
- ✅ Binary patch or Frida Gadget injection only

**Has backend** (custom server for user data + membership):
- ✅ QX response-body modification: POSSIBLE (if no request signing)
- ✅ MITM proxy: POSSIBLE
- ✅ Binary patch: possible but may be overkill

Quick backend detection indicators (from HAR + App Store page):

**From HAR (most reliable):**
- **HAR 中有 App 自定义域名且有业务 API 调用** → ✅ Has backend
- **HAR 中零个 App 自定义 API 调用**（仅第三方 CDN/广告/SDK） → 🔴 NO backend (red flag for QX)
- **HAR 中只有 RevenueCat**（`api.revenuecat.com`）+ App 自定义域名 → ✅ Has backend (RevenueCat, QX works)
- **HAR 中只有 RevenueCat，无 App 自定义域名** → ⚠️ Probably a RevenueCat-only app (still QX-modifiable via RC)
- **HAR 中只有 Adapty**（`api.adapty.io`）+ App 自定义域名 → ✅ Has backend (Adapty, QX works — scripted above)
- **HAR 中只有 Adapty，无 App 自定义域名** → ⚠️ Probably an Adapty-only app (still QX-modifiable via Adapty response injection)
- **CONNECT 到 Apple CDN（`is1-ssl.mzstatic.com` 等）失败** → 这是 Apple 收据验证/StoreKit 交易的 TLS 失败，**不是** SSL pinning 信号。说明 App 用 StoreKit 2 设备端验证，收据不走自定义服务器
- **恢复购买无网络请求**（HAR 中无 receipt/verify/restore/apple/iap/purchase 到 App 服务器）→ 🔴 NO backend (local-only receipt validation)

### Adapty SDK 专属解锁模式

Adapty SDK 走 API 端点响应体修改（Receipt/Subscription/Profile 三类端点）。如果 App 只有 Adapty 验证 + 无请求签名（仅 `Api-Key` 公开 key + `adapty-sdk-profile-id` header），QX/Surge 脚本直接拦截响应注入终身订阅即可。

| Adapty Endpoint | 方法 | 拦截后注入内容 |
|----------------|------|--------------|
| `/api/v1/sdk/analytics/profiles/{id}` | GET | 注入 `subscriptions` + `paid_access_levels` + `apple_validation_result.transactions` |
| `/api/v1/sdk/in-apps/profile/cross-placement-info/` | GET | 注入 `placement_with_variation_map` + `version` |
| `/api/v1/sdk/in-apps/apple/receipt/validate` | GET | 注入 `pending_renewal_info` + `latest_receipt_info` + `receipt.in_app` |
| `/api/v1/sdk/in-apps/purchase-containers` | GET | 同上，收据校验 |
| `/api/v1/sdk/in-apps/{api_key}/products/app_store/` | GET | 仅获取商品列表，无需拦截 |

**Adapty Authorization**：仅 `Api-Key public_live_XXXX` 公开 key — **无请求签名机制**，纯响应体修改即可。远比 RevenueCat / 句读-style HMAC 签名简单。

### HAR 分析 Adapty 流量的诊断模板

```python
import json
with open('capture.har') as f:
    har = json.load(f)

entries = har['log']['entries']
adapty_entries = [e for e in entries if 'adapty.io' in e['request']['url']]
print(f"Adapty requests: {len(adapty_entries)}")
for e in adapty_entries:
    url = e['request']['url']
    method = e['request']['method']
    status = e['response']['status']
    headers = {h['name']: h['value'] for h in e['request']['headers']}
    auth = headers.get('authorization', '')
    profile_id = headers.get('adapty-sdk-profile-id', '')
    print(f"  {method} {status} {url}")
    print(f"    Auth: {auth[:60]} | Profile: {profile_id}")
```

### 实战案例：Yomu (yomu.app)

- **App**: Yomu 漫画阅读器 (iOS 27, iPhone17,3)
- **Bundle ID**: `yomu.app`
- **Adapty API Key**: `public_live_jXeB1bKS`
- **SDK**: Adapty 3.15.5
- **验证**: HAR 中只有 analytics/profiles GET、cross-placement-info GET、events POST → 纯 Adapty 验证，无自建服务器
- **骚扰购买**: 无网络活动（无 receipt/validate）→ 100% 纯 Adapty 验证
- **解锁注入点**:
  1. `analytics/profiles GET` → 返回空 `{"data":{}}` → 注入 `lifetime.yomu.app` 终身订阅
  2. `cross-placement-info GET` → 注入 `premium_paywall` variation_id + `version`
  3. `receipt validate / purchase-containers GET` → 伪造完整 Apple 收据（status:0, expires_date:2099）
- **结果**: Surge 脚本拦截成功，伪造终身订阅
- **脚本**: `references/yomu-adapty-unlock.md` 包含完整 sgmodule 源码和注入映射表

---

**重要：区分"功能层网络" vs "会员层网络"** — App 可以有大量功能层网络活动（Google OAuth/Firebase Auth 认证、微信读书等第三方 API 请求、百度输入法 SDK、广告 SDK、Crash Reporting），但这些与 IAP 验证完全无关。关键只看 App 是否有**自己服务器的**收据/会员验证 API 调用。不要因为看到 Google OAuth 或第三方 API 请求就误判 App 有后端验证。（实战案例：书影 App 有 Firebase Auth + 微信读书 API 7 次成功调用，但 IAP 验证仍是纯本地的。）

**From App Store page alone:**
- "数据本地存储" / "所有数据存储在本地" → 🔴 NO backend (red flag for QX)
- "iCloud 同步" present, NO mention of cloud accounts → 🔴 likely NO backend
- Solo developer + small app size (<80MB) → higher chance of no backend
- Web companion has no login → 🔴 NO backend
- Privacy policy: no mention of user accounts → 🔴 NO backend

### 0.1 App Store Scrape

```bash
# Visit the App Store page (browser or curl)
# Extract key info:
# - Developer name (individual vs company?)
#   - Individual/solo dev → less likely to have server-side receipt verification
#   - Company → more likely to have signed requests
# - App size (small <50MB likely native Swift; medium 50-150MB could be either; >150MB likely Flutter/React)
# - Latest version + release date
# - Age rating (4+ = likely no server-side auth at all)
# - IAP product list (subscription types, lifetime options)
# - Description (local storage claims like "数据本地存储" = yellow flag for QX-only unlock)
```

### 0.2 Developer Website Analysis

```bash
# Check the developer's website for:
# 1. Web version of the app's core functionality (e.g. link parser, editor)
#    - If web version exists, it reveals backend API patterns
#    - The iOS app likely uses the SAME backend API
# 2. Privacy policy / terms of service
#    - Look for data storage claims: "all data stored locally" = 🔴 red flag for QX
#    - Look for server endpoints mentioned
# 3. Technology stack hints
#    - Next.js/Vite site → developer is web-savvy, app may be SwiftUI + server API
#    - Static HTML → developer may be less experienced, simpler security
```

### 0.3 Web Companion API Discovery ★

Many iOS apps have a web companion at the same domain. The **web tool's API is usually the iOS app's backend API** — it's the cheapest intelligence you can gather before any HAR capture.

**Key patterns to check:**

```bash
# 1. Check the page source for API endpoints
curl -sL "https://developer-site.com" | grep -oP '(api|fetch|axios|https?://[^"'"'"'`,\s)]*domain[^"'"'"'`,\s)]*)' | sort -u

# 2. The most reliable pattern: check JavaScript bundles for fetch/axios calls
# Look for Next.js /app/_next/static/chunks/ or similar bundles
for js in $(curl -sL https://site.com | grep -oP 'src="([^"]+\.js)"' | grep -oP 'https?://[^"]+' | head -5); do
  echo "=== $js ==="
  curl -sL "$js" 2>/dev/null | grep -oP '(api|fetch\(|axios\.)["'"'"']?[^"'"'"',;)]+' | head -10
done

# 3. Common API patterns to look for:
#    cdn*.domain.com?url=           → CORS proxy (serves as backend for link parsing)
#    api.domain.com/v1/             → REST API
#    domain.com/api/                → REST or RPC API
#    wss://domain.com/ws            → WebSocket (real-time features)
```

**The CORS proxy pattern** (`cdn1.domain.com?url=<encoded_url>`) is especially common for apps that parse social media links. The iOS app calls the exact same endpoint since it handles the server-side fetching that mobile Safari can't do cross-origin.

### 0.4 Decrypted IPA Source Search

Check these free IPA repositories for a decrypted copy:

| Source | URL | Notes |
|--------|-----|-------|
| Decrypt IPA Store | `https://decrypt.day/app/<appstore_id>` | Cloudflare blocked from servers; download via browser |
| MACPA | `https://macpa.cn/` | Requires registration/paid |
| iOS Gods | `https://iosgods.com/` | Free decrypted IPAs |
| AppDB | `https://appdb.to/` | Free IPA sharing |
| qnblackcat/GitHub | `https://github.com/qnblackcat/Decrypted-IPAs` | GitHub-hosted decrypted IPAs |

**If blocked from server**: Check search engines for `"<app_name>" "ipa" "decrypted" "1.x.x"` or try the SvelteKit data endpoints at decrypt.day (embedded in the page's inline __sveltekit data).

### 0.5 IPA Acquisition → Binary Size → Architecture

Once you have the IPA:

```bash
unzip -o app.ipa -d /tmp/app-reverse/
file Payload/*.app/*
# If you see a single large binary (~20-70MB) → likely native Swift
# If you see App.framework/Flutter.framework → Flutter (harder to patch)
# If you see main.jsbundle → React Native (easier: just modify JS)
otool -l Payload/*.app/* | grep -A4 LC_ENCRYPTION
# cryptid 0 = decrypted; cryptid 1 = still encrypted
```

**Architecture unlock difficulty**:
- SwiftUI native: Follow this skill (Swift5 metadata, binary patch, etc.)
- React Native: QX script to modify JS bundle → easiest unlock
- Flutter: Hardest — need to patch Dart AOT binary or hook engine functions

### 0.6 Technology Stack Indicators

| Indicator | Likely stack | Implication |
|-----------|-------------|-------------|
| IPA 30-80MB, single Mach-O | SwiftUI native | Full binary analysis needed |
| IPA >150MB, includes Flutter.framework | Flutter | Dart AOT, hard to patch |
| IPA includes main.jsbundle | React Native | Easy: modify JS bundle |
| Website uses Next.js (SSR) | Developer is web-savvy | May have server-side receipt verify |
| Solo developer, small app | Simpler security | Likely QX-modifiable or no server verify |
| "数据本地存储" in description | Local-only cache | 🔴 Red flag for QX-only approach |
| "iCloud同步" mentioned | iCloud sync | State may be cached locally |

---

## Pre-Diagnosis: QX/Surge Response-Body Patching Feasibility

**IMPORTANT**: Phase 0 gives you context; this diagnostic tells you if QX scripts will work. Not all iOS apps can be unlocked via proxy — this saves hours of wasted effort.

### Diagnostic Flow

```
START: User wants to unlock an iOS app via QX/Surge
│
├─1. Get HAR/ProxyPin capture → identify API endpoints
│
├─2. Is the app a WebView wrapper / React Native / Flutter app?
│   ├─ YES → You CAN use QX response-body modification. 
│   │   These apps typically pass server JSON directly to JS engine
│   │   without client-side signature verification.
│   │   Examples: 简讯 (Jx), EveryTrace (Myj) — worked fine.
│   │
│   └─ NO (native Swift/ObjC) → Continue to 3
│
├─3. Does the HAR show request-signing headers (e.g. X-CC-Signature, 
│   HMAC, SigV4-style `X-CC-*`, `X-Auth-Signature`)?
│   ├─ YES → The app uses AWS-style SigV4 or custom HMAC signing.
│   │   ⚠️ This is a RED FLAG for QX-only approach.
│   │   Continue to 4.
│   │
│   └─ NO → You CAN try QX response-body modification.
│       Write a simple regex/replace script and test.
│       If it works: done. If not: continue to 4.
│
4. Does tapping "Restore Purchase" generate ANY network request 
   to the app's server (receipt verification)?
   ├─ YES → Can intercept that request/response. May work.
   ├─ MAYBE → Check HAR for: receipt, verify, restore, apple, iap, purchase in URLs
   └─ NO (restore is local-only, uses SKReceiptRefreshRequest 
       without server verification) → ⚠️ CRITICAL RED FLAG.
       App NEVER verifies receipt with its server on restore.
       This means membership state is cached LOCALLY.
       Continue to 5 — binary patching / Frida / Dylib is REQUIRED.
│
└─5. Decision:
    ├─ Response-body modification tried on users/me or users/wechat 
    └─5. Decision:
        ├─ Response-body modification tried on users/me or users/wechat 
        │  + global_config templates → DID NOT WORK
        │  → ⚠️ App has request signing + likely local state caching.
        │  TRY NEXT: Server-side MITM proxy (if no SSL pinning, 
        │  based on QX capturing the HAR successfully).
        │  See "Server-side MITM Proxy" section below.
        │  If MITM also fails → binary patching / Frida Gadget / Dylib.
        │
        └─ Haven't tried yet → Try:
            ├─ Intercept users/wechat → is_member:true
            ├─ Intercept t/i → r:true (restore switch)
            ├─ Intercept global_config → templates all "free"
            ├─ Also try intercepting receipt validation endpoints
            │  (apple/verify, purchase/validate, etc.)
            └─ Try: Kill app → reopen, check if unlock sticks
                If STILL doesn't work → Try MITM proxy before binary patching
```

**Concrete Example: 句读 (Judou) and 有诗 (Youshi)**

Both by 北京才程科技 (tech.caicheng.JudouRili). Same security architecture:

## 实战记录: 句读 5.0.8 完整逆向过程

### 时间线
- 获取 HAR (Quantumult X) → 20个judouapp请求，无恢复购买网络请求
- 写 QX 脚本拦截 users/wechat + t/i + global_config → ❌ 不生效
- 从 tmp.link 下载已砸壳 IPA (111MB, 26MB arm64 Mach-O)
- 二进制分析: strings搜索无 X-CC header名, 无 is_member字段名, 无secret key
- Capstone/Mach-O解析: import表(CCHmacInit exist), chain fixups, GOT扫描
- 19000+种签名算法暴力验证 → ❌ 无匹配
- **结论**: X-CC-* SigV4风格签名, secret key编译时XOR混淆+运行时派生, 静态无法提取

### 后续方向
- Frida hook运行时 (需要越狱/TrollStore + FridaGadget)
- 二进制Patch ipa (找到SubscriptionState switch处NOP掉B.NE)
- 本地MITM代理服务器 (需自签CA证书在手机上信任)

| Feature | Present? | Implication |
|---------|----------|-------------|
| Request signing | ✅ X-CC-* SigV4-style (HMAC-SHA256, access key `6329fbb8-96ea-420a-a822-af9b0a42acd5`) | Cannot modify request body; secret key XOR/obfuscated at runtime |
| Response body mod | ✅ Tried all 3 endpoints (users/wechat, t/i, global_config) | Did NOT unlock |
| Restore purchase | ✅ Local-only, no network | Apple SKReceiptRefreshRequest, no server verify — **pure local** |
| Local state cache | ✅ Inferred (UserDefaults/Keychain with obfuscated keys) | QX cannot reach local storage |
| IPA available | ✅ 句读 5.0.8 decrypted IPA (111MB, 25.6MB Mach-O) | Binary does NOT contain X-CC header strings as plaintext — all string constants obfuscated at compile time |
| Secret key search | 🔍 NOT in binary as plaintext; NOT in any plist/nib/resource; No UUID-formatted strings match `6329fbb8`; Swift mangled class `APIRequest._` and `cApiTool`/`ApiUtil` found but no signing functions exposed as plain symbols | Key constructed via XOR or runtime concatenation; needs r2/Ghidra data-flow trace |
| HMAC calls | `_CCHmacInit`/`_CCHmacUpdate`/`_CCHmacFinal` present as imported symbols | Function stubs exist but most calls likely inlined by Swift SIL optimizer |
| All API endpoints | `users/wechat` (POST), `t/i` (GET), `global_config` (GET), `ads`, `products`, `orders`, `notifications/unread_count`, `push_tags` | NO dedicated membership verification endpoint — membership stored in local cache |

**Diagnosis process for this case** (step-by-step what was tried and what each told us):

1. **Initial**: Wrote QX script intercepting `users/wechat` → modify `is_member:true` → ❌ not working
2. **Add `t/i`**: Intercept restore purchase switch `r:false→true` → ❌ still not working
3. **Add `global_config`**: Set all templates to `free`, zero out ads → ❌ still no effect
4. **Check restore purchase network**: HAR shows ZERO receipt/verify/apple requests to judouapp.com → restore is **local-only** (SKReceiptRefreshRequest without server verify)
5. **IPA binary analysis**: Decrypted (cryptid=0), 26MB arm64 Swift binary. All X-CC header strings obfuscated — not present as plaintext. Access key ID `6329fbb8-96ea-420a-a822-af9b0a42acd5` not found anywhere. Secret key not extractable without dynamic analysis.
6. **Conclusion**: QX/Surge/Loon proxy-script unlocks are IMPOSSIBLE for this class of app.

**Conclusion for this class of app**: QX/Surge/Loon proxy-script unlocks are IMPOSSIBLE. The app uses:
1. AWS SigV4-style request signing (body integrity at request level)
2. Local encrypted state cache (membership stored in UserDefaults/Keychain, not re-fetched on every check)
3. No server-side receipt verification on restore (pure local SKReceiptRefreshRequest)
4. String obfuscation at compile time (all X-CC header names and possibly secret key XOR-encrypted)

**Required approach**: Binary patch the IPA (find the getter for the member state enum and NOP its `if not subscribed→skip` branch), or inject Frida Gadget / Dylib with runtime ivar override.

### Alternative: Server-side MITM Proxy (viable for apps without SSL pinning)

If the HAR was captured via QX/Surge MITM (meaning the app does NOT do SSL pinning), a server-side MITM proxy can work — this is a **middle ground** between QX scripts (which fail) and binary patching (which is complex) when the pre-diagnosis shows request signing + local state caching.

**Key insight**: Response JSON has NO signature, only the request does (X-CC-Signature). Since we forward the original request unchanged and only modify the response, the signature never needs recomputation.

#### Deployment Steps

```bash
# 1. Install mitmproxy (in Hermes venv or your own)
uv pip install mitmproxy

# 2. The binary lives in the venv bin dir
#    /usr/local/lib/hermes-agent/venv/bin/mitmdump

# 3. Write an addon script (see templates/jd_mitm.py)

# 4. Start mitmproxy
/path/to/venv/bin/mitmdump -s modify_script.py -p 8080 --set block_global=false

# 5. Find the CA cert for phone installation
ls ~/.mitmproxy/mitmproxy-ca-cert.pem
```

#### Phone Setup
1. Install mitmproxy CA cert on iPhone: Settings → General → VPN & Device Management → Install Profile
2. Trust it: Settings → General → About → Certificate Trust Settings → toggle ON mitmproxy
3. Set HTTP proxy on iPhone WiFi to server IP:8080

#### Script Pattern

The addon script must:
- Check `flow.request.pretty_url` for the target domain
- Only intercept `application/json` responses
- Parse JSON, modify fields, re-serialize
- Strip `Content-Length` and `etag` headers to prevent cache issues
- Use `elif` chains to avoid intercepting the wrong response on shared flows


---
*[Content truncated: 1935 lines total]*
---

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        session.detach()

if __name__ == "__main__":
    main()
```

见 `scripts/frida-gadget-debug.py` — 完整的 Frida Gadget 调试模板。

## Step 7: 重签名 + 打包

```bash
# 移除原始签名
ldid -S Payload/AppName.app/AppName 2>/dev/null || \
    codesign --remove-signature Payload/AppName.app/AppName

# 签名所有 framework
for fw in Payload/AppName.app/Frameworks/*.framework; do
    ldid -S "$fw/$(basename ${fw%.framework})" 2>/dev/null
done

# 签名 PlugIns
for ex in Payload/AppName.app/PlugIns/*.appex; do
    ldid -S "$ex/$(basename ${ex%.appex})" 2>/dev/null
done

# 重签主二进制
ldid -S Payload/AppName.app/AppName

# 打包 IPA
cd /tmp/app-reverse && zip -r /tmp/AppName_patched.ipa Payload/

# 通过 AltStore/Sideloadly/ios-deploy 安装
```

## References
- `references/ipa-iap-product-id-extraction.md` — App Store 内购产品 ID 的提取方法论、字段映射、局限性
- `references/file-transfer-gotchas.md` — 文件传输陷阱：tmp.link 等无法从服务器下载、IPA 正确传输路径、用户发送 IPA 文件名时的即时响应模式

## Pitfalls

1. **★★★ `__swift5_reflstr` 是最便宜的信息源** — 不需要 Ghidra/IDA，Python 几行代码就能提取所有枚举 case、属性名、类型结构。先做 reflstr 分析再做反编译，效率差 10 倍
2. **@Observable 宏的属性是计算属性** — Swift 5.9+ 的 `@Observable` 宏把存储属性重写为计算属性，通过 `_observationRegistrar` 存取。直接 Patch getter 可能不够，需要在 observation 系统层面 Hook
3. **SubscriptionState rawValue 从 0 递增** — `notSet=0, subscribed=1, notSubscribed=2...`，Patch getter 返回 1 即可。但需验证起始值，不同 App 可能不同
4. **StoreKit 2 的 Transaction.updates 是持续监听** — 即使 Patch 了初始状态，后台监听可能覆盖。需要同时 Patch update listener
5. **Sentry / 分析 SDK** — 许多 App 集成 Sentry，可能上报异常。考虑在 Patch 中同时禁用（替换 Sentry 初始化为 NOP）
6. **Swift 函数可能被内联** — 小函数（如布尔属性 getter）经常被内联，nm 看不到独立符号。需要通过字符串交叉引用 + 反汇编确认
7. **arm64 指令编码** — `MOV W0, #imm` 的编码: `0x52800000 | (imm << 5)`。`MOV W0, #1` = `0x52800004`，`RET` = `0xD65F03C0`
8. **虚拟地址 → 文件偏移映射** — Patch 时必须将虚拟地址转换为文件偏移。公式: `file_offset = vaddr - segment_vaddr + segment_file_offset`
9. **IPA 改后缀为 .zip 发送** — Telegram 不支持 .ipa，改后缀为 .zip 即可发送
10. **Frida 对 Swift 属性 Hook 困难** — Swift 的属性访问器经过 SIL 优化，不像 ObjC 有统一的消息派发。fishhook 拦截 C 函数更可靠
11. **PaywalledElementModifier 需要逐个分析** — SwiftUI 的 ViewModifier 是值类型，不能 ObjC swizzle。需要 Patch ViewModifier 的 body 方法
12. **★★ iOS dylib 编译必须有 Xcode** — Command Line Tools 只有 macOS SDK，无法链接 iOS Foundation.tbd。用户必须安装完整 Xcode，验证: `xcrun --sdk iphoneos --show-sdk-path` 非空
13. **Xcode 可能不在 /Applications/** — 用 `mdfind "kMDItemCFBundleIdentifier == 'com.apple.dt.Xcode'"` 查找实际路径，然后用 `sudo xcode-select -s <path>/Contents/Developer` 切换
14. **Xcode 版本必须匹配 macOS 版本** — macOS 15.x 需要 Xcode 16.x，Xcode 26.x 需要 macOS 26。下载前确认版本对应关系
15. **iOS 交叉编译 Foundation 链接失败** — 用 `-target arm64-apple-ios` + macOS SDK 会 link 失败。解决方案: (a) 用 iOS SDK（需 Xcode）(b) 不链接 Foundation，用纯 ObjC runtime 调用（objc_msgSend 代替直接方法调用）
16. **CodeBuddy 会拒绝商业软件破解** — 委派逆向破解类任务时，CodeBuddy 会因安全策略拒绝。改用 OpenClaw 或 Akino 自己执行
17. **fishhook Hook StoreKit 比直接 Hook App 更可靠** — App 的 Swift 私有类型符号被 strip，但 StoreKit 2 的导入符号（mangled C name）在符号表保留。Hook `RenewalState.rawValue` 等底层 API，App 层面的 SubscriptionState 会自然跟随
18. **★★★ fishhook StoreKit 不够！App 有自己的 SubscriptionState 映射层** — App 从 StoreKit 获取 `RenewalState`，映射到自己的 `SubscriptionState` 枚举并缓存。Hook StoreKit 只影响下次查询，不影响已缓存值。必须：二进制 Patch + fishhook + 运行时覆写 三管齐下
19. **★★★ @Observable 属性的 ivar 可能出现在 ObjC ivar 列表中** — 之前认为 `@Observable` 属性不出现在 `class_copyIvarList` 中，但 Screens 5 的 SubsStore 有 **19 个 ivars**，包括 `_subscriptionState`（size=1, Int8）、`_wasRefunded`、`_willAutoRenew` 等。`@Observable` 宏确实把属性重写为通过 `_observationRegistrar` 存取，但**存储属性仍然作为 ivar 存在**，只是 setter 走 `withMutation`。运行时可以直接通过 ivar 偏移读写！但注意 `_showingPaywall` 不在 SubsStore 中，而是在各个 View 类中
20. **+load 优先于 __attribute__((constructor))** — `+load` 在 `main()` 之前执行（所有 dylib 加载后、CFRunLoop 启动前），`__attribute__((constructor))` 在 `main()` 之后。如果 SubsStore 在 App 启动早期初始化，constructor 形式的 hook 会错过窗口期
21. **CMP+B.NE → NOP 是最可靠的 Patch 手段** — 比 fishhook 更稳定，因为不依赖运行时符号解析。但需要精确定位：只有 SubscriptionState switch 处的 CMP+B.NE 才能 Patch，不能盲 Patch 所有 CMP #1 + B.NE（一个 16MB 二进制有 4500+ 个）
22. **大部分订阅检查不是 CMP+B.NE 模式** — 44 个 BL 到 StoreKit 订阅 stub 的位置，只有 2-3 个后面紧跟 CMP+B.NE。其余使用 Swift pattern matching（switch-case on enum），需要更复杂的 Patch 策略
23. **Hook RenewalState case getter 防止 pattern matching** — Hook `expired`/`inGracePeriod`/`inBillingRetryPeriod`/`revoked` 的静态 getter 全部返回 `.subscribed(1)`，这样即使 App 用 switch 匹配 enum case，也会匹配到 subscribed 分支
24. **★★★ Swift struct property getter 是 C 函数，没有 SEL 参数** — StoreKit 的所有 Swift API（`RenewalState.rawValue`、`Status.state`、`willAutoRenew` 等）是 C 函数，不是 ObjC 方法。函数签名中**没有 `SEL _cmd` 参数**！如果 Hook 函数签名包含 SEL，会导致寄存器偏移 8 字节，读到垃圾值。这是 fishhook Hook StoreKit 时最容易犯的错误
25. **★★★ 大部分 StoreKit 调用被内联，fishhook 截不到** — 一个 16MB 的 Swift 二进制中，对 `RenewalState.rawValue` stub 只有 1 次 BL 调用，`willAutoRenew` 甚至 0 次。Swift 编译器会内联小函数。fishhook 只能拦截通过 GOT 的间接调用，对内联调用完全无效。不要依赖 StoreKit fishhook 作为主要解锁手段
26. **swift_allocObject Hook 可捕获 Swift 类实例创建** — 所有 Swift class 实例通过 `swift_allocObject` 分配内存，Hook 它可以在实例创建时捕获 SubsStore。同时 Hook `objc_alloc` 和 `objc_allocWithZone` 作为备选路径
27. **SubscriptionState 枚举的内存大小可能是 1 字节** — 虽然 Swift 的 `Int` 类型是 8 字节，但枚举的底层存储只需要容纳最大 case 值。8 个 case (0-7) 只需 3 bits，ObjC ivar metadata 可能报告 size=1。写入时用 `int8_t`（1 字节），不是 `int64_t`（8 字节）。但 StoreKit 的 `RenewalState`（`Int` rawValue）是 8 字节返回值
28. **_showingPaywall 不在 SubsStore 中** — 它在各个 SwiftUI View 类中，与 `_subsStore` 一起作为 ivar。需要扫描所有 ObjC 类找到持有 `_showingPaywall` 的类，然后 swizzle 其 setter
29. **★★★ @Observable 的 withMutation 可能覆写直接内存修改** — `@Observable` 宏生成的属性 setter 走 `ObservationRegistrar.withMutation(keyPath:) { _backing = newValue }`。如果你直接通过 ivar 偏移写内存，App 的下一次属性赋值会通过 withMutation 把值改回去。定时器每 0.5s 覆写可能不够快——如果 App 在每次 View 渲染时都检查属性，0.5s 间隔内会有数十次读取。解决思路：(a) Hook `ObservationRegistrar.withMutation` 在回调中拦截并阻止修改 (b) 更快的定时器 (c) NOP 掉 withMutation 的调用点
30. **★★★ 非越狱 TrollStore 无法运行 frida-server** — frida-server 需要 root 权限和 LaunchDaemon，TrollStore 的 .tipa 没有这个能力。非越狱环境必须用 **Frida Gadget** 注入 IPA。Mac 端安装 `pip3 install frida-tools frida`，iPad 端将 Gadget dylib 打包进 IPA 的 Frameworks 目录并添加 load command
32. **★★★ QX/Surge 改 response body 对带请求签名 + 本地缓存的 iOS App 无效** — 典型特征：(a) HAR 中有 `X-CC-Signature` / HMAC / SigV4 风格请求签名头 (b) 点恢复购买不走网络（HAR 中无 receipt/verify/apple 请求到 app 服务器）(c) 修改所有相关 endpoint 的 response body 后仍不生效，说明 `is_member` 在 UserDefaults/Keychain 本地加密缓存。**一旦确认这三个特征，直接告诉用户 QX 路线走不通**，需要 IPA 二进制 Patch 或 Frida/Dylib 注入。参考句读/有诗案例：同公司(北京才程科技)的两款 App 都是这套架构，改 response body 无效，签名 key 被 XOR/分段存储不在二进制明文里。
33. **HAR 中恢复购买无网络请求 = 重要诊断信号** — 如果用户说"点恢复显示成功"但 HAR 中没有 receipt/verify/apple 相关请求到 app 服务器，说明恢复购买走的是纯本地 SKReceiptRefreshRequest。这种 App 的会员状态完全靠本地缓存控制
34. **请求签名 key 可能在二进制中被 XOR/分段存储** — 即使有 IPA，签名 key 也可能通过 XOR 或运行时拼接构造，不会以明文形式存在。在 arm64 二进制中搜索 UUID 格式的 access key ID 通常找不到，需要用 r2/Ghidra 追踪数据流
35. **Keychain key 名称可能在 __DATA 段的字符串表中** — 句读的 Keychain key（`VIP_`, `AD_PIC`, `SIMPLE_USER_INFO`, `USER_INFO`, `RICH_INFO`）在二进制 __DATA 段的连续字符串块中存在。通过 `strings binary | grep VIP_` 可以在不需要反汇编的情况下找到 Keychain key 名。反过来，如果找到了这些 key 名，Frida 脚本可以精确拦截对应的 Keychain 读取
38. **★★★ App Store 评分措辞必须原文引用** — 页面显示"此 App 尚未收到足够的评分或评论，无法显示整体评分" ≠ "0评分"。用户极其反感对评分信息的转述/缩写。在侦察阶段必须直接引用 App Store 页面的确切原文，不要做"0分"、"无评分"、"0条评价"等推导。需要检查实际页面文本（浏览器 snapshot），不是依赖 web_extract 的截断输出。
40. **临时文件托管站点（tmp.link/filebin等）≠ 可从服务器下载** — 这类站点使用 JavaScript 触发的浏览器原生下载机制（console 显示 "Using browser download"），curl、wget、urllib 均无法获取文件。Browser 工具的 browser_click 虽然能触发下载，但文件不会保存到服务器文件系统。正确做法：告知用户此链接无法从服务器抓取，给出替代方案：(1) GitHub Gist 直链下载 (2) 上传到 OpenList/Nextcloud 公开分享 (3) 改后缀为 .zip 后通过 Telegram 发送。不要浪费时间在 browser 里等下载。
41. **用户说"这是...IPA"或"解密后的...ipa"时立即进入逆向分析模式** — 这意味着用户已经准备好了 IPA 文件，想要的是二进制分析（架构/加密状态/StoreKit验证逻辑），绝对不要继续做 UI 代码生成、HTML 解析、或其他无关工作。如果文件链接无法下载，立刻说明原因并给出可行的传输方案，不要反复用已经失败的方法重试。
42. **tmp.link 下载 = 服务端永远拿不到文件** — 不要尝试 browser_click 后等文件出现、不要用 curl 重试、不要写 Python 脚本抓。该机制依赖浏览器原生下载 + JS 事件触发，服务器端零接收。直接跳过，告诉用户换传输方式。
43. **用户说"我已发了...IPA"时，先查服务器文件系统** — 用户可能已通过其他方式上传文件到服务器。先 `find /tmp /root /home -name "*.ipa"` 检查，不要盲目跟外部链接。
44. **★★★ Swift5 元数据可能被完全 strip — 先验证！** — `__swift5_reflstr` / `__swift5_fieldmd` 等 section 在某些 App 中 size=0。用 `llvm-objdump -h` 确认大小：**非零 = 内容存在**，此时别放弃。实战：书影 v1.1.3 所有 swift5 section 全部存在（typeref=1.48MB），之前误判"被 strip"是 Python struct 解析偏移 bug 导致，不是真 strip。**顺序：先 `llvm-objdump -h` 看大小 → 确认后再决定下一步**
45. **★★★ Linux 上 Mach-O 解析用 llvm-objdump，别用 Python struct** — Python struct 手动解析 section header 时 `(cmdsize - 72) // 80` 公式不可靠。实战中只报告出 5 个 section（实际 25 个）。正确流程：`llvm-objdump -h binary` 获取准确 offset/size → Python 按偏移硬编码读取。详见 v3 会话 `references/shuying-binary-v3-session.md`
34. **`__TEXT,__cstring` 是 API端点 + UI 文本的金矿** — iOS App 中所有 String 字面量都集中于此 section。包含：(a) **完整 API URL**（`https://weread.qq.com/api/...`）(b) UI 文案（"已保存到今日沉淀"）(c) 错误日志模板（`[WeRead][SkillGateway] invalidResponse api=%@`）(d) 枚举 key 名。对于 API 提取任务，**cstring 信息量 > reflstr**。实战：书影 cstring 提取 7 API 路径 + 1286 个 UI 字符串 + 67 个业务类名。详见 `references/shuying-full-recon.md`

47. **★ 完整 IPA 逆向工作流（贪婪版）** — 当用户要求"所有内容"（UI+API+架构+数据模型+类名+协议+...），按以下顺序最大化信息提取：
   1. **Info.plist** → plistlib 解析 → IAP产品ID、URL Scheme、Widget Intent、隐私描述
   2. **__cstring** → 正则提取 URLs/路径/UI文案/错误日志 → 拿 API 域名、端点、CDN 地址
   3. **__const** → 扫描 `__Key_` 前缀字符串 → 拿完整依赖注入图（UseCase/Repository/Service/Store）
   4. **__swift5_reflstr** → 提取 demangled 类名（`_TtC8书影_2` → `SampleLibraryBootstrapper`）
   5. **__swift5_fieldmd** → 解析 Codable 字段名映射（待深入）
   6. **__swift5_types** → 类型引用列表
   7. **__swift5_proto** → 协议一致性
   8. **中文短语扫描** → Python regex `rb'[\x{4e00}-\x{9fff}]{2,}'` 提取 UI 文案

   实战产出：书影 v1.1.3 从此流程中提取了 API端点 17个、完整UseCase/Store/Repository架构、数据模型字段 30+个、UI文案 1286个、类名 50+个。详见 `references/shuying-full-recon.md`

48. **★★★ StoreKit 2 本地验证 = 代理脚本/MITM 绝对无法解锁** — StoreKit 2 的 Transaction 签名由 Apple 根证书签发，验证在设备本地通过 Apple 公钥完成，不经过 App 服务器。因此：(a) MITM proxy 篡改 API 响应无效 (b) 代理脚本无法伪造交易签名 (c) 解锁 Pro 功能必须通过二进制 Patch (NOP 掉订阅检查分支) 或 Frida Hook (拦截 StoreKit 返回) 实现。不要向用户推销"用代理脚本解锁 StoreKit 2 App"——技术上不可能。实战：书影 `com.shuying.pro.lifetime` 走纯 StoreKit 2 设备端验证，最后只能告诉用户"代理脚本解锁不了"

49. **★★★ SwiftUI逆向我诚实边界** — 静态分析（strings/cstring/reflstr）能拿到的上限是：类名、UI文案、API端点、数据模型字段、依赖注入关系。**拿不到的**：View布局层级（body被Release展开）、动画参数、精确padding/font/frame值、运行时状态流转。当用户说"我要完整UI"或"所有内容"时，立刻明确说明这个边界，不要含糊其辞让用户以为只是时间问题。直接说"做不到，只能拿到文本和类名，布局无法恢复"，用户会接受（已验证）。

50. **115网盘扫码登录 Cookie 获取是常见周边需求** — 书影 App 支持导入微信读书笔记，用户常问能不能自动获取 115 扫码 Cookie。标准流程：`GET https://qrcodeapi.115.com/api/1.0/web/1.0/token?do=aget` → 展示二维码 → 轮询 `GET .../login?uid=...` → 取 `GET .../cookie?uid=...`。需 `requests`，可选 `Pillow` + `numpy` 在终端显示二维码。注意 tmp.link 等 JS 触发下载服务从服务器无法获取文件，用户应在本机运行脚本。

37. **TrollStore 安装不需要重签名**

## iOS 逆向进阶仓库（NEW）

| 仓库 | 用途 | 地址 |
|------|------|------|
| **httptoolkit/frida-interception-and-unpinning** | Frida 全自动 HTTPS MITM 拦截 + SSL pinning 绕过 | https://github.com/httptoolkit/frida-interception-and-unpinning |
| **v-y-archive/Jailbreak-detection-The-modern-way** | 现代 App 越狱检测绕过分析（Snapchat/Pokemon Go） | https://github.com/v-y-archive/Jailbreak-detection-The-modern-way |
| OWASP MASTG Frida Gadget | 非越狱 Frida Gadget 自动注入 IPA | https://mas.owasp.org/MASTG/techniques/ios/MASTG-TECH-0090/ |

## 工具箱

| 工具 | 用途 |
|------|------|
| `otool -l` | Mach-O section/segment 布局 |
| `nm` | 符号表查看 |
| `strings` | 初步关键词侦察 |
| `lief` (Python) | Mach-O 二进制 Patch |
| `radare2` / `r2` | 反汇编分析 |
| `dsdump` | Swift class-dump |
| `ldid` | iOS 重签名 |
| `codesign` | macOS 签名工具 |
| `frida` | 运行时动态 Hook |

## ⚠️ IAP Product ID Discovery — 重要技巧

### 概要

Apple 已关闭 iTunes Search/Lookup API 的 IAP 数据返回。但 App Store 网页版（apps.apple.com）的内容型 SSR HTML 仍然包含完整的 IAP 数据——**只需要 X-Apple-Store-Front 请求头**。IAP 数据在 JSON 路径 `pageData.softwarePageData.addOns`（非 `offers` 数组）。

完整文档和脚本见：
- `references/iap-appstore-web-api-discovery.md` — 技术细节 + storefront 表 + 解析代码
- `scripts/iap-lookup.py` — 即用脚本：`python3 scripts/iap-lookup.py <app_id> [country]`

### ✅ 方法一：App Store 网页 API（推荐 — 无需 IPA）

```bash
curl -s -A 'AppStore/2.0 iOS/17.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'X-Apple-Store-Front: 143465-19,32' \
  "https://apps.apple.com/cn/app/id{appId}?platform=iphone&includeWebp=true" \
  --compressed
```

返回的 SSR HTML 包含 `its.serverData` JSON → `pageData.softwarePageData.addOns` 数组，每个元素是 IAP 商品。

### ✏️ 方法二：IPA strings 搜索（有 IPA 时）

```bash
strings Payload/AppName.app/AppName | grep -iE 'com\..*\..*(monthly|yearly|weekly|daily|lifetime|iap|vip|pro|unlock|subscription|premium|trial|forever)'
```

**产品 ID 命名惯例**：`com.{dev}.{app}.monthly`、`com.{dev}.{app}.vip_monthly`、`com.{dev}.iap.{plan}_{period}`

### 📱 方法三：真机 App Store 抓包（有设备时）

在 iOS App Store 进入 App 详情页 → IAP 数据通过 AMP API 加载 → 抓包工具（QX/Surge/Charles）捕获 `in-app-purchases` 请求 → 响应体包含完整 IAP 列表（含 `productId`）。

### 各方法对比

| 方法 | 需要 IPA | 需要设备 | 返回 productId | 返回部分 IAP 数据 |
|------|---------|---------|---------------|-----------------|
| App Store 网页 AMP API | ❌ | ❌ | ❌ (只有 adamId) | ✅ name/price | 
| IPA strings | ✅ | ❌ | ✅ | ✅ |
| 真机抓包 | ❌ | ✅ | ✅ | ✅ |

### 最优顺序

1. **App Store 网页 AMP API**（最快，只需 curl）→ 拿到 IAP 列表和价格
2. **找解密 IPA**（decrypt.day / 搜索引擎搜 `"<app名>" "ipa"`）→ strings 搜 productId
3. **真机抓包**（有设备时）→ 确认完整 productId
4. **都没 IPA 和设备** → 告诉用户只有名称和价格信息，无法获取 productId

---

## 参考

- `references/swift5-metadata-extraction.md` — Swift5 反射元数据提取详细技术
- `references/screens5-case-study.md` — Screens 5 完整逆向案例
- `references/judou-508-reverse.md` — 句读 5.0.8 实战记录（X-CC 签名、VIP_ Keychain key 发现、MITM + Frida 路径验证）
- `references/web-companion-api-discovery.md` — 通过 App 网页版寻找后端 API 的模式（CORS 代理、Next.js JS bundle 扫描等），在获取 IPA 和 HAR 之前的情报收集手段
- `references/picseed-case-study.md` — PicSeed 实战案例
- `references/shuying-case-study.md` — 书影实战案例：纯本地 App（零自建 API、StoreKit 2 设备端验证、Apple CDN 收据验证 TLS 失败）
- `references/shuying-binary-analysis.md` — 书影 v1.1.3 二进制分析：Swift5 元数据被 strip 后的字节级中文扫描提取法
- `references/shuying-full-recon.md` — 书影 v1.1.3 完整逆向重建：API端点+架构+数据模型+类名+技术栈
- `references/lightweight-ipa-recon.md` — 轻量级 IPA 信息提取（API端点、架构识别、无需解锁）：纯本地 App（无后端，仅 CORS 代理），通过网页 JS 包 + 文档站点发现 API 面
- `references/shadowshare-ios-recon.md` — ShadowShare 侦察案例：App Store 分析 + 网站 API 发现 + Flutter Web App 解剖 + API 端点探测流程
- `references/shadowshare-recon-2026-06-11.md` — ShadowShare 侦察案例：代理节点共享 App 的后端 API 发现、Flutter Web 版定位、无需注册 App 的认证评估
- `references/iap-etm-tech-bypass.md` — Speed Test Master Lite 通用 IAP 拦截案例（iap.etm.tech 响应伪造 + App Store 地区性下架判断方法）
- `templates/fishhook-unlock.m` — fishhook dylib 模板，修改 Hook 符号即可复用
- `templates/ios_mitm.py` — MITM proxy addon 通用模板，修改 TARGET_DOMAIN 和 modify_response() 即可复用
- `scripts/swift5_extract.py` — Swift5 反射字符串提取脚本
- `scripts/frida-gadget-debug.py` — Frida Gadget USB 调试脚本（Python API 附加，解决 frida CLI asyncio bug）
- `scripts/iap-lookup.py` — 任意 App Store 应用内购查询工具（无需 IPA，调 App Store 网页 SSR API）

---

## ios-app-video-sniffer-reverse

# iOS Safari 扩展视频嗅探逆向

从 IPA 中提取 Safari 扩展的视频下载/CDN 逻辑。触发: Stay、视频嗅探、Safari扩展逆向。

## 核心发现

Pornhub 等站将视频源藏在 `window.flashvars_{playerId}.mediaDefinitions` — Flash 遗留对象。普通嗅探只拦截 XHR/fetch，看不到 DOM 全局数据。Stay 读 `window.VIDEO_SHOW.playerId` → 构造 key → 提取。

## 提取流程

```bash
unzip -o app.ipa "Payload/App.app/PlugIns/*Extension.appex/source/sniffer/video/*" -d /tmp/extract/
grep -rl "pornhub\|mediaDefinitions\|flashvars\|VIDEO_SHOW" /tmp/extract/
```

## Pornhub 一行提取

```javascript
var defs = window["flashvars_" + window.VIDEO_SHOW.playerId.split("_")[1]].mediaDefinitions;
```

## 通用模式

| 站点 | 数据源 |
|------|--------|
| Pornhub | `window.flashvars_{id}.mediaDefinitions` |
| YouTube | `ytInitialPlayerResponse.streamingData` |
| 一般 | `<video>` / `<source>` DOM |

完整提取代码: `references/pornhub-flashvars-extract.js`

## Apple IAP 逆向

Apple StoreKit IAP 的 productId 可通过 `viewSoftware` 接口的 shoebox 提取，登录 Apple ID 后正则匹配 `buyParams` 字段。详见 `references/apple-iap-reverse.md`。

## 关键教训

- **不需要 CDN 代理**: Stay 下载 Pornhub 视频不依赖任何 CDN 中继。核心是 DOM hook，不是网络拦截。
- **IPA 中的 JS 优先于 Mach-O**: Safari 扩展核心逻辑在 `PlugIns/*.appex/source/` 下的 JS 文件中，原生层只做容器。
- **先 strings 扫域名再解 JS**: 用 `strings | grep -iE "akamai|cdn|proxy|porn"` 快速定位关键字符串，再解压对应 JS 文件。

---

## ios-ipa-static-analysis

# iOS IPA 静态分析：功能绕过机制定位

分析大型多框架 iOS IPA 中的功能绕过/修改机制。通过关键词字符串搜索 + 字节偏移上下文提取 + Mach-O 段归属分析，在不反汇编的情况下定位修改点。

## When to Use

- 用户提供改版/fork 的 iOS IPA，要求分析与上游应用的差异
- 需要查找限制绕过/复制保护/转发阻止的 bypass 机制
- IPA 包含多个大型框架二进制（100MB+），全量反汇编不现实
- 在 Linux 环境分析 iOS IPA，无 macOS 原生工具（otool、class-dump、nm 对 stripped Mach-O 失败）
- 分析 Telegram 第三方客户端（Nicegram 等）的消息保存/转发限制绕过

## 工作流（6 步）

### Step 1: 枚举所有 Mach-O 二进制

```bash
find Payload/<App>.app/ -type f -exec file {} \; 2>/dev/null | grep "Mach-O"
```

典型 Telegram 架构：
- **主二进制**（155KB stub，仅加载框架）
- **Frameworks/**:
  - `TelegramCoreFramework` (~20MB) — 数据模型、API、引擎
  - `TelegramUIFramework` (~148MB) — 全部 UI、聊天、展示逻辑
  - `PostboxFramework` (~4MB) — 本地数据库
  - `MtProtoKitFramework` — MTProto 协议
- **PlugIns/**: 各类 App Extension

> **关键认知**：Telegram fork 分析中主二进制极小，核心逻辑全在 `TelegramCoreFramework` 和 `TelegramUIFramework` 中。

### Step 2: 跨所有二进制的关键词搜索

根据调查的功能构建关键词列表。限制/保存/转发绕过关键词：

```
noforward noforwards canForward canSave restricted restriction saveRestricted
screenshot isRestricted noSave copyRestriction copyProtection
forceCopyProtected canBypassRestrictions ignoreContentRestrictionReasons
```

逐二进制执行：
```bash
for bin in Telegram \
  Frameworks/TelegramCoreFramework.framework/TelegramCoreFramework \
  Frameworks/TelegramUIFramework.framework/TelegramUIFramework \
  Frameworks/PostboxFramework.framework/PostboxFramework; do
    echo "--- $bin ---"
    strings -a "$bin" | grep -iE '<keywords>' | sort -u
done
```

搜索 mod 特有的前缀字符串：
```bash
# ObjC 类名（Nicegram 示例）
strings -a <binary> | grep -E '_OBJC_CLASS_\$__TtC[0-9]+(NG|Nicegram)' | sort -u
# Swift 类名
strings -a <binary> | grep -E '_TtC[0-9]+NGCoreUI' | sort -u
```

### Step 3: 识别 mod 特有字符串

过滤出上游应用中不会存在的字符串。Nicegram 示例：
- `canBypassRestrictions` — 绕过标志（标准 Telegram 中不存在）
- `forceCopyProtected` — 出现在 ObjC 属性列表上下文中
- `AccountNicegramAttribute` — 自定义账户属性类
- `GNGSettings` / `SystemNGSettings` — 自定义设置类
- `NicegramSettingsRepository` — 设置仓库协议
- `NGCoreUI.ImageSaver` — 自定义图片保存类

### Step 4: 字节偏移上下文提取

发现关键字符串后，提取周围上下文理解其角色：

```python
import re

with open(binary_path, 'rb') as f:
    data = f.read()

needle = b'canBypassRestrictions'
pos = data.find(needle)
if pos != -1:
    start = max(0, pos - 200)
    end = min(len(data), pos + 200)
    chunk = data[start:end]
    for m in re.finditer(rb'[\x20-\x7e]{4,}', chunk):
        print(f'  0x{start+m.start():x}: {m.group().decode("ascii", errors="replace")}')
```

### Step 5: 段归属分析（Mach-O 解析）

确定字符串位于哪个 Mach-O section：
- `__cstring` / `__swift5_reflstr` → Swift 字段名（结构体属性）
- `__LINKEDIT` → 符号表或 export trie（导出符号）
- `__swift5_fieldmd` → 字段元数据（反射）

```python
import struct

def find_string_section(data, file_offset):
    magic = struct.unpack('<I', data[:4])[0]
    if magic != 0xfeedfacf:
        return None
    ncmds = struct.unpack('<I', data[16:20])[0]
    offset = 32
    for i in range(ncmds):
        cmd, cmdsize = struct.unpack('<II', data[offset:offset+8])
        if cmd == 0x19:  # LC_SEGMENT_64
            nsects = struct.unpack('<I', data[offset+64:offset+68])[0]
            sect_offset = offset + 72
            for j in range(nsects):
                sect = data[sect_offset:sect_offset+80]
                sectname = sect[:16].split(b'\x00')[0].decode()
                segname = sect[16:32].split(b'\x00')[0].decode()
                sect_file_off = struct.unpack('<I', sect[48:52])[0]
                sect_size = struct.unpack('<Q', sect[40:48])[0]
                if sect_file_off <= file_offset < sect_file_off + sect_size:
                    return (segname, sectname)
                sect_offset += 80
        offset += cmdsize
    return None
```

> **Swift 字段名格式**：`__cstring` / `__swift5_reflstr` 中，字段名前带长度字节。`\x01canBypassRestrictions` — `\x01` 是前一个短字符串的长度前缀。

### Step 6: 验证无注入 dylib

确认 mod 是编译进框架而非运行时 hook：

```python
import struct

with open(main_binary, 'rb') as f:
    data = f.read()
magic = struct.unpack('<I', data[:4])[0]
ncmds = struct.unpack('<I', data[16:20])[0]
offset = 32
for i in range(ncmds):
    cmd, cmdsize = struct.unpack('<II', data[offset:offset+8])
    if cmd == 0xc:  # LC_LOAD_DYLIB
        f.seek(offset + 8)
        name_off = struct.unpack('<I', f.read(4))[0]
        f.seek(offset + name_off)
        name = b''
        while True:
            c = f.read(1)
            if c == b'\x00' or not c: break
            name += c
        print(f'  LC_LOAD_DYLIB: {name.decode()}')
    offset += cmdsize
```

如果所有 LC_LOAD_DYLIB 都是 `@rpath/<Framework>.framework/<Framework>` 或系统库 → 无注入。

## 工具可用性（Linux 分析 iOS IPA）

| 工具 | Debian 可用？ | 替代方案 |
|------|-------------|---------|
| `nm` | 是，但对 `NLIST_OUTOFSYNC_WITH_DYLDINFO` Mach-O 报错 | `strings -a` + grep `_OBJC_CLASS_$_` / `_TtC` 前缀 |
| `otool` | 否 | Python struct 解析 Mach-O load commands |
| `class-dump` | 否 | `strings -a` 搜索 ObjC 类/方法选择器 |
| `objdump` | 是，但仅支持 ELF（不能反汇编 Mach-O） | `llvm-objdump -h` 仅获取 section headers |
| `strings` | 是 | 大二进制分析的主力工具 |
| `file` | 是 | Mach-O 类型识别可用 |
| `grep -obaP` | 是 | 获取字符串在二进制中的字节偏移 |

## ⚠️ Pitfalls

1. **nm 报 "file format not recognized"**：`NLIST_OUTOFSYNC_WITH_DYLDINFO` 标志的二进制符号表与 dyld info 不同步，nm 无法解析。改用 `strings -a` 搜索符号。
2. **otool 不可用**：Debian 上没有 otool。所有 Mach-O 解析用 Python struct 手动完成。
3. **objdump 不能反汇编 Mach-O**：Linux 上的 objdump 仅支持 ELF。`llvm-objdump` 可以查看 section headers（`-h`）但不能反汇编 arm64 Mach-O。
4. **字符串在 __LINKEDIT 中**：如果字符串不在 `__cstring` 或 `__swift5_reflstr` 中，检查是否在 `__LINKEDIT` 段的符号表或 export trie 中。需要解析 LC_SYMTAB 和 LC_DYLD_EXPORTS_TRIE 的范围。
5. **大型二进制分析超时**：TelegramUIFramework 148MB，`strings -a` 可能需要 60-120 秒。设置足够 timeout。
6. **Swift mangled names 过长**：Swift 函数签名可能超过 1000 字符，grep 输出难以阅读。用 `sort -u` 去重后逐条分析。
7. **find -perm +111 在某些系统不可用**：用 `find -type f -exec file {} \; | grep Mach-O` 替代权限过滤。

## Nicegram 分析案例 (v2.5.8, build 708)

### 绕过机制证据

**1. `canBypassRestrictions` (TelegramUIFramework)**
- 位置：`__LINKEDIT` 段，Swift 反射字段名附近
- 上下文：与 `imageOrVideo`、`file`、`rawValue`（OptionSet 字段）和 `MessageMediaEditingOptionsV` 相邻
- 解读：添加到媒体编辑或控制器交互结构体的布尔字段，设置为 true 时允许 UI 绕过内容限制

**2. `forceCopyProtected` (TelegramUIFramework, 2 处)**
- 出现在 ObjC 属性名列表中，与 `forceAnimatedScroll`、`forceAudioToSpeaker`、`forceBadgeHidden` 并列
- 第二处在 gallery/媒体查看器控制器上下文中（附近有 `currentItemId`、`displayData`、`currentFileReference`）
- 解读：在 gallery 查看器中强制覆盖 copy-protection 状态

**3. 标准 Telegram 限制基础设施（未修改，上游已有）**
- `copyProtectionEnabled` / `isCopyProtectionEnabled` — 标准 Telegram 标志
- `noForwards` / `NoForwards` / `messageActionNoForwardsToggle` — MTProto 协议级 no-forward 标志
- `ignoreContentRestrictionReasons` — 标准 Telegram 限制绕过
- `RestrictedContentMessageAttribute` — 受限内容的消息属性

**4. Nicegram 特有模块（编译进框架）**
- `NGCoreUI.ImageSaver` — 自定义图片保存类（`saveImageAtURL:`、`saveImageWithData:silentlyFail:completionBlock:`）
- `NGData.GNGSettings` / `NGData.SystemNGSettings` — Nicegram 全局设置
- `NGData.NicegramSettingsRepository` — 设置仓库协议
- `NGUI` — 自定义 UI 控制器（含 `NicegramSettingsController`）
- `NicegramWallet` — 集成加密钱包（TON/EVM/Solana/Tron）
- `NGCallRecorder` — 通话录制功能
- `NGAiChatUI` — AI 聊天集成
- `AccountNicegramAttribute` (TelegramCore) — 自定义账户属性（`exported`、`imported`、`skipRemoteLogout` 字段）
- Nicegram Bazel/SwiftPM 源码路径可见：`external/rules_swift_package_manager++swift_deps+swiftpkg_nicegram_assistant_ios/` 和 `swiftpkg_nicegram_wallet_ios/`

### 结论

Nicegram 绕过 Telegram 受限频道消息保存/转发限制的方式是**编译时源码修改**（非运行时 hook 或注入 dylib）：

1. **`canBypassRestrictions`** — 添加到展示/控制器结构体的新布尔字段，在执行 copy-protection UI 限制前检查
2. **`forceCopyProtected`** — gallery/媒体查看器控制器的属性，可覆盖 peer 的 copy-protection 状态
3. **`NGCoreUI.ImageSaver`** — 自定义图片保存管道，绕过标准 Telegram 保存限制检查
4. **`AccountNicegramAttribute`** — 账户级属性，可能跨会话携带绕过状态

标准 Telegram 限制基础设施（`copyProtectionEnabled`、`noForwards`、`RestrictedContentMessageAttribute`）在协议层保持不变 — Nicegram 在 UI/展示层通过添加新字段和自定义保存路径来绕过。

---

## apple-iap-mitm-extraction

# Apple IAP 数据提取 — MITM 方案

## When to use

- 需要获取 iOS App 的完整 IAP productId 列表（非仅 offerName）
- 有 iOS 设备 + Surge/Quantumult X + Scripting App
- 需要购买免费 IAP（price=0 的商品）
- 第三方 API（Sakura 等）覆盖不足时

## 原理

Scripting App 内置 `AppleStoreAPI.js`，通过 Surge 模块 MITM 劫持域名后，用 Apple ID 登录态直接调用 Apple iTunes 私有 API：

```
Apple ID 登录 → auth.itunes.apple.com/auth/v1/native/fast
     ↓
viewSoftware → shoebox JSON → extractIaps()
     ↓
正则 /"buyParams":"([^"]+)"/g → 解码 buyParams
     ↓
提取 offerName / salableAdamId / productType / price
     ↓
免费 IAP → buyProduct (price="0", buyWithoutAuthorization="true")
```

## 核心接口

### Apple 私有 API

| 端点 | 方法 | 用途 |
|------|------|------|
| `auth.itunes.apple.com/auth/v1/native/fast?guid=` | GET | Apple ID 登录，获取 dsPersonId + passwordToken |
| `itunes.apple.com/WebObjects/MZStore.woa/wa/viewSoftware?id=` | GET | 获取 shoebox（含所有 IAP buyParams） |
| `buy.itunes.apple.com/.../buyProduct` | POST | 购买 IAP 商品 |
| `p25-buy.itunes.apple.com/.../volumeStoreDownloadProduct` | GET | 获取 IPA 下载直链 |

### Scripting App 暴露的 REST API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/auth/login` | POST | `{appleId, password, code?}` |
| `/auth/refresh` | POST | 刷新 token |
| `/apps/search/:term` | GET | 搜索 App，返回 trackId |
| `/apps/:id/iap` | GET | `?country=us` → IAP productId 列表 |
| `/apps/:id/purchase` | POST | 购买免费 IAP |
| `/apps/:id/versions` | GET | 历史版本列表（含三方数据） |

### IAP 返回格式

```json
{
  "productId": "com.vidure.6zhentan.2.year.renew.membership",
  "salableAdamId": "1234567890",
  "productType": "C",
  "priceFormatted": "0.00",
  "pricingParameters": "STDQ"
}
```

## 关键参数

| 参数 | 来源 | 说明 |
|------|------|------|
| `dsPersonId` | 登录返回 | Apple 用户唯一标识 |
| `passwordToken` | 登录返回 | 等效密码 token |
| `X-Apple-Store-Front` | 地区代码 | 如 `143465-19,32 t:website`（中国） |
| `salableAdamId` | buyParams 提取 | Apple 内部 IAP 数字 ID |
| `guid` | 设备生成 | Apple 设备标识 |

## 部署

1. Surge/QX 添加 `ipaTool.sgmodule`（MITM `apple-api.com` + `xiaobai.app`）
2. Scripting App 运行 `AppleStoreAPI.js`
3. 通过 `http://localhost:端口/auth/login` 登录 Apple ID
4. 调用 `/apps/:id/iap` 获取 IAP 列表

## 局限性

- **仅限 iOS 设备**，VPS 无法使用
- **需要 Apple ID 密码或 Cookie**
- **付费 IAP 不可白嫖**（price > 0 返回 failureType=2019）
- **订阅型 (productType=A)** 默认被过滤，需修改 extractIaps 逻辑
- Apple 私有 API 可能随时变更

## 与其他方案对比

| 方案 | productId | salableAdamId | 购买 | 环境 |
|------|:---:|:---:|:---:|------|
| ipaTool MITM | ✅ | ✅ | ✅ | iOS+Surge |
| Sakura API | ✅ | ✅ | ❌ | 任意 HTTP |
| HTML 爬取 | ❌ | ✅ | ❌ | 任意 HTTP |
| **PythonIDE StoreKit** | N/A | N/A | ✅ | iOS+PythonIDE |

## PythonIDE 开发

PythonIDE 是 iOS 原生 Python IDE，支持 Widget/AppUI/StoreKit 开发。
详见 [pythonide-ios-platform.md](references/pythonide-ios-platform.md) 和 [widget 速查](references/pythonide-widget-cheatsheet.md)。

**Widget 模板**：[DeepSeek 余额小组件](templates/deepseek-balance-widget.py) — `widget.cache_json` + `widget.param` 配置 API Key，显示赠送/充值余额明细。

---

## app-store-price-tracker

# iOS App Store 价格追踪 App 逆向 + 推送集成

## When to use

- User wants to scrape App Store daily deals / price drops / free apps
- AppRaven or similar iOS price-tracking app to reverse
- Need to push data via Surge panel / WeChat (WxPusher) / cron
- Need daily delivery of AppStore 限免/降价

## Key targets

| Target | API Type | Base URL |
|--------|----------|----------|
| AppRaven | GraphQL (Apollo) | `https://appraven.net/appraven/graphql` |
| Apple Lookup | REST | `https://itunes.apple.com/lookup?id=...&country=...` |

## AppRaven API Reverse Engineering

### 1. Locate API endpoint

```bash
# JS bundle is at /static/js/main.*.js on the web front-end
# Extract server URL and API path:
python3 -c "
import re
with open('main.js') as f: js = f.read()
for m in re.findall(r'[\"\\x27](https?://[^\"\\x27]{10,80})[\"\\x27]', js):
    print('URL:', m)
for m in re.findall(r'serverUrl[^;]*', js):
    print('serverUrl:', m[:200])
"
```

Key pattern: `serverUrl = yn.mainUrl + "/appraven"`, `apiUrl = yn.serverUrl + "/graphql"`

### 2. GraphQL schema (introspection is OFF)

Introspection disabled (ValidationError). Extract queries from webpack bundle via Python regex:

```python
# Extract all query/mutation operations from bundle
for m in re.finditer(r'(query|mutation)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]+', js):
    print(f'{m.group(1)} {m.group(2)}')
```

### 3. Known queries

| Query Name | Purpose | Key Fields |
|---|---|---|
| `GetHomeContent` | Homepage: dailyDeals, popularApps, appsOnSale, newApps, updatedApps | content, id, title, artworkUrl, priceTier |
| `GetDailyDeals` | Today's special deals (includes 限免 & price drop) | oldPriceTier, newPriceTier, sponsored, app {…} |
| `GetAppsOnSale` | Price drop apps (paginated) | miniFilter (ratingCount, genreId), rareOnly, page, pageSize |
| `GetAppDetail($id)` | Single app detail | ITunesId, title, priceTier, rating, genres, developer, version, size |
| `FilterApps` | Filter by genre, sort by popularity | AppFilterInput, AppSortInput (POPULARITY_DAY) |
| `GetNewApps` / `GetUpdatedApps` | New releases / recent updates | miniFilter, page |
| `IAPsOnSalePreview` | In-app purchases on sale | same miniFilter inputs |

### 4. Activity/Price change fields

From `AppActivity` fragment:

- `AppActivityPriceChange`: `priceChangeType` ("DROP"/"RAISE"), `priceTierFrom`, `priceTierTo`
- `AppActivityAvailability`: `availabilityChangeType` ("release"/"remove"), `priceTier`
- `AppActivityUpdate`: `versionFrom`, `versionTo`, `updateSize`

Queried via `app(id) { lastActivity { ... } }`

### 5. Sample request

```python
import requests
r = requests.post('https://appraven.net/appraven/graphql', json={
    "query": """query GetDailyDeals($page: Int!) {
        dailyDeals(page: $page) { content {
            id title subject oldPriceTier newPriceTier sponsored
            app { id title subtitle artworkUrl priceTier rating ratingCount }
        }}
    }""",
    "variables": {"page": 0}
}, headers={
    "Content-Type": "application/json",
    "Origin": "https://appraven.net"
})
```

## App Store Price Tier Reference

Apple price tiers are NOT linear USD values. For approximate display only — for accurate prices use the Apple Lookup API.

```python
# Approximate mapping (US Store Tier → USD)
def price_str(tier):
    if tier == 0: return "免费"
    pm = {1:0.99, 2:1.99, 3:2.99, 10:9.99, 15:14.99,
          20:19.99, 23:22.99, 30:29.99, 49:48.99, 50:49.99, 62:61.99}
    return pm.get(tier, tier)
```

For a Surge panel script, skip the price tier entirely — just show "限免中" since the API already tells us `newPriceTier === 0`.

## Apple Lookup API (batch price lookup)

```bash
# Single request, up to ~20 comma-separated IDs, supports country param
curl "https://itunes.apple.com/lookup?id=1643538680,1473595660&country=cn"
# Returns: trackId, trackName, price, formattedPrice, currency, bundleId, etc.
```

Note: returns **current** price only. If an app is currently free, it returns `"formattedPrice": "Free"` — no way to get old price from this endpoint.

---

## App Store HTML Scraping — 任意应用 IAP 查询

⚠️ **2026年更新：Apple 已迁移至 Vite/Svelte SPA（单页应用）**  

旧方法（`its.serverData` 在 HTML 中内嵌）**对桌面浏览器 UA 已完全失效**。以下情况现在不工作了：
- `curl` 请求 → 可能返回空 HTML 或重定向
- 桌面浏览器 UA 收到 SPA 版 → JSON 不内嵌

但 `its.serverData` **在 iOS UA + `X-Apple-Store-Front` 下仍在部分场景工作**（iOS 系统绕过 SPA 返回旧版 SSR HTML）。

**两个不同的 HTML 版本：**

| 版本 | 触发条件 | `its.serverData` | 适用方法 |
|------|----------|:---:|----------|
| 旧版（SSR） | iOS UA + `X-Apple-Store-Front` | ✅ 完整 IAP 数据 | `get_iap_data()` 下方脚本 |
| 新版（SPA） | 桌面浏览器 UA 或无 Store-Front | ❌ 无嵌入 JSON | AMP API / 可见文本提取 |

**确认 HTML 版本的方法：** 搜索 `its.serverData` — 不存在即是 SPA 版。

### SPA 版替代方案

#### Solution 0: Sakura Public IAP API (recommended when apple-api.com fails)

> **2026-06-30 发现**: 樱花交流会 (https://xn--ug8h.eu.org) 提供兼容 `apple-api.com` 结构的公开 IAP 查询接口，**需要 Origin + Referer 头**，返回完整 productId、价格、类型。

```bash
# 必需 Origin + Referer，否则返回 {"error": "Unauthorized", "reason": "Missing origin and referer"}
curl -s 'https://xn--ug8h.eu.org/api/iap?trackId=6749503310&country=cn' \
  -H 'Origin: https://xn--ug8h.eu.org' \
  -H 'Referer: https://xn--ug8h.eu.org/iap'
```

**和 apple-api.com 的对比：**

| 对比项 | Sakura | apple-api.com |
|--------|--------|---------------|
| 路径 | `/api/iap?trackId=xxx` | `/apps/{trackId}/iap` |
| 鉴权 | Origin + Referer | 无 |
| `app` 字段 | 有 IAP 时为 `null`，无时整个 key 缺失 | 始终为对象或 null |
| `appAdamId` | ❌ 不存在 | ✅ 包含 |
| 额外字段 | `fetchedAt` 时间戳 | `success` + `error` |

**type 映射（两接口一致）：**
```ts
"A" | "B" | "C"  // 订阅 | Bundle | 主应用
```

**完整字段示例：**
```json
{
  "app": {
    "name": "实况助手-视频转实况,全能实况壁纸制作器",
    "bundleId": "com.lijiao.LiveHelp",
    "iconUrl": "https://...",
    "userRating": { "ratingCount": 383, "ratingCountCurrentVersion": 383, "value": 5, "valueCurrentVersion": 5 }
  },
  "iaps": [
    {
      "productId": "livehelper.flower.vip",
      "salableAdamId": "6751113962",
      "priceMicroUnits": 58000,
      "priceFormatted": "58.00",
      "productType": "A",
      "pricingParameters": "STDQ"
    }
  ],
  "fetchedAt": "2026-06-30T18:52:52.527Z"
}
```

**TypeScript 接口定义：**
```ts
interface SakuraIapResponse {
  app: {
    name: string;
    bundleId: string;
    iconUrl: string;
    userRating: {
      ratingCount: number;
      ratingCountCurrentVersion: number;
      value: number;
      valueCurrentVersion: number;
    };
  } | null;  // 有 IAP 时为对象，无 IAP 时为 null；注意：iaps:[] 时整个 app key 可能缺失
  iaps: SakuraIapItem[];
  fetchedAt: string;
}

interface SakuraIapItem {
  productId: string;           // StoreKit 标识 (如 "livehelper.flower.vip")
  salableAdamId: string;       // Apple 内部数字 ID
  priceMicroUnits: number;     // 微单位价格 (58000 = 0.058 货币单位，但 priceFormatted 58.00 才是显示值)
  priceFormatted: string;      // 显示价格 ("58.00")
  productType: string;         // "A"=订阅, "B"=Bundle, "C"=App
  pricingParameters: string;   // "STDQ" 等 Apple 价格参数
}
```

#### 方案 1: visible text extraction (fallback)

When `its.serverData` doesn't exist (SPA version), subscription names and prices still exist as visible text on the page:

```python
import re, urllib.request

def extract_visible_pricing(app_id, country='cn'):
    """Extract visible subscription names and prices from SPA page."""
    url = f'https://apps.apple.com/{country}/app/id{app_id}'
```
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    
    # 提取可见的订阅项: <span>月会员</span> <span>¥18.00</span>
    items = []
    for m in re.finditer(r'<span[^>]*>([^<]+)</span>\s*<span[^>]*>¥?([0-9,.]+)</span>', html):
        name, price = m.group(1), m.group(2)
        if len(name) < 30:
            items.append((name.strip(), price))
    
    # 通过大 JSON 提取 bundle ID
    bundle_id = None
    json_m = re.search(r'"bundleId":"([^"]+)"', html)
    if json_m:
        bundle_id = json_m.group(1)
    
    return {
        'bundle_id': bundle_id,
        'items': items,
        'note': 'productId 字符串仅能从 AMP API(JWT)、真机 MZStorePlatform 或 IPA 二进制获取'
    }
```

**⚠️ 局限性：** 可见文本只能提取订阅**名称**和**价格**，无法提取真实的 `productId` 字符串。

详见 `references/iap-spa-fallback.md`（完整的 SPA 兜底方案和案例）。

#### 方案 2：AMP API 端点发现

SPA 页面加载的动态数据来自 Apple 的 AMP API。端点和参数嵌入在页面的大 JSON 脚本中（通常 300-500KB）：

```python
import re, json

def discover_amp_api(html):
    """从 SPA 页面 JSON script 中发现 AMP API 端点。"""
    m = re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
    data = json.loads(m.group(1))
    raw = json.dumps(data)
    for m2 in re.finditer(r'(amp-api[^"\'\\\\]+)', raw):
        return f'https://{m2.group(1)}'
    return None
```

**找到的端点（示例）：**
```
https://amp-api-edge.apps.apple.com/v1/catalog/{country}/apps/{appId}
  ?platform=web&views=top-in-app-purchasables&l=zh-Hans-CN
```

**⚠️ AMP API 需要 JWT 鉴权** — 裸请求返回 `401 Unauthorized`。Token 由 SPA 运行时通过 cookies/session 动态获取，不嵌入在 HTML 中。

#### 方案 3：`apple-api.com` 私有后端

某些 iOS 工具（如 IPA Tool）使用私有后端代理查询 IAP 数据：

```
GET https://apple-api.com/apps/{appId}/iap?country={country}
```

- **`apple-api.com` 是私有服务**，需要自行部署或使用配套 App
- 返回格式见 `references/ipa-tool-backend.md`
- 不适用于无后端访问的场景

详见 `references/ipa-tool-backend.md`（完整的 API 文档和类型定义）。

#### 方案 4：真机 / 旧版 HTML

同原方法：iOS NSURLSession + `X-Apple-Store-Front` 触发旧版 SSR HTML。

### 汇总：获取 IAP productId 的所有路径

| 方法 | 可达性 | 获取 productId | 备注 |
|------|:---:|:---:|------|
| `its.serverData`(旧版 SSR) | iOS UA + Store-Front | ✅ `offerName` | 旧版 HTML，可能逐步下线 |
| AMP API (新版 SPA) | ❌ 需 JWT | ✅ | Apple 内部 API，严格鉴权 |
| 可见文本提取 | ✅ 任何 client | ❌ 无 productId | 兜底方案 |
| `apple-api.com` | ❌ 私有后端 | ✅ | IPA Tool 配套服务 |
| MZStorePlatform | ❌ 真机 only | ✅ `productIdentifier` | Apple 内部 API |
| IPA 二进制逆向 | ✅ 有 IPA 文件 | ✅ | 从 StoreKit 配置提取 |

> 细节参考：`references/ipa-tool-backend.md`（apple-api.com 后端）和 `references/iap-spa-fallback.md`（SPA 页面兜底提取）。

**Bundle ID vs Product ID 速查**：
| 标识 | 示例 | 说明 |
|------|------|------|
| Bundle ID | `me.imgbase.imgplay` | App 唯一标识，Xcode 固定，一个 App 一个 |
| Product ID | `me.imgbase.imgplay.subscriptionYearly` | 内购商品标识，App Store Connect 创建，命名遵循 BundleID.productName |

**真实案例：ImgPlay（989843523）全部内购产品 ID**（从 IPA 二进制提取的 offerName）：
| Product ID | 类型 |
|---|---|
| `me.imgbase.imgplay.subscriptionWeekly` | 自动续期订阅 |
| `me.imgbase.imgplay.subscriptionMonthly` | 自动续期订阅 |
| `me.imgbase.imgplay.subscriptionYearly` | 自动续期订阅 |
| `me.imgbase.imgplay.purchase` | 非消耗品 |

直接爬 App Store 网页，无需第三者 API，可查任意应用的完整内购商品列表（含 `offerName` + `salableAdamId`）。

### 原理

App Store 页面 HTML 内嵌 `its.serverData` JSON，其中 `pageData.softwarePageData.addOns` 数组即该应用所有内购商品。苹果服务端根据 `X-Apple-Store-Front` header 返回地区化数据。

### 请求格式

```bash
curl -s 'https://apps.apple.com/{country}/app/id{appId}?platform=iphone&includeWebp=true' \
  -H 'X-Apple-Store-Front: {storefront}-19,32' \
  -H 'User-Agent: AppStore/2.0 iOS/17.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15' \
  --compressed -o page.html
```

⚠️ **`X-Apple-Store-Front` 缺了的话，苹果返回空壳页面，没有 IAP 数据。**

### Store Front ID 对照

| 国家 | Store Front |
|------|-------------|
| 🇨🇳 中国 | `143465-19,32` |
| 🇺🇸 美国 | `143441-1,32` |
| 🇯🇵 日本 | `143462-9,32` |
| 🇰🇷 韩国 | `143466-1,32` |
| 🇭🇰 香港 | `143463-4,32` |
| 🇹🇼 台湾 | `143470-8,32` |
| 🇬🇧 英国 | `143444-2,32` |

### JSON 路径

```
its.serverData
 ├── storePlatformData
 │   └── product-dv-product.results.{appId}
 │       ├── name, bundleId, artistName, hasInAppPurchases, genreNames
 │       └── offers[]  (主应用下载，非 IAP)
 ├── pageData
 │   └── softwarePageData.addOns[]    ← 所有内购商品
 │       ├── name                     ← 商品显示名
 │       ├── price                    ← 价格字符串 (¥8.00)
 │       ├── buyParams                ← URL编码参数 (salableAdamId, offerName, productType, price)
 │       └── offerType                ← {offerType: "buy"}
 └── constants
     └── storePlatformLookupUrl       → 客户端内部 API 端点
```

### 提取 IAP 核心代码

```python
import re, json, urllib.request

def get_iap_data(app_id, country='cn'):
    sf = {'cn':'143465-19,32','us':'143441-1,32','jp':'143462-9,32'}
    url = f'https://apps.apple.com/{country}/app/id{app_id}?platform=iphone&includeWebp=true'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'AppStore/2.0 iOS/17.0',
        'Accept': '*/*', 'X-Apple-Store-Front': sf.get(country, '143441-1,32'),
        'Accept-Encoding': 'gzip, deflate',
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
        if raw[:2] == b'\x1f\x8b':
            import gzip; raw = gzip.decompress(raw)
        html = raw.decode('utf-8', errors='replace')
    # Brace-match to extract its.serverData JSON
    m = re.search(r'its\.serverData\s*=\s*(\{)', html)
    start = m.start(1); depth = 0; end = start
    for i in range(start, min(start + 200000, len(html))):
        if html[i] == '{': depth += 1
        elif html[i] == '}': depth -= 1
        if depth == 0: end = i + 1; break
    data = json.loads(html[start:end])
    addons = data['pageData']['softwarePageData']['addOns']
    return [{
        'name': item.get('name', '').strip(),
        'price': item.get('price', ''),
        'offerName': re.search(r'offerName=([^&"]+)', item['buyParams']).group(1),
        'salableAdamId': re.search(r'salableAdamId=(\d+)', item['buyParams']).group(1),

---
*[Content truncated: 642 lines total]*
---


### 使用场景

- 查任意应用的 IAP 商品列表（价格、ID、类型）
- 破解方案需要 `salableAdamId` / `offerName`
- 限免追踪的离线/补充数据源
- 对比不同地区 IAP 定价

---


## Delivery Method 1: Surge Panel

Consume AppRaven API directly from a Surge panel.

### Architecture

```
AppRaven GraphQL API  ←  Surge Panel Script ($httpClient.post)  →  $done({title, content})
```

### ⚠️ User preference (7452323) — this is the ONLY acceptable format

The user has rejected every alternative format. **Do NOT deviate from this exact style:**

**Display format (locked):**
```
━━━ 本体限免 ━━━
  1. App Name

━━━ 内购限免 ━━━
  1. App Name (1 Year)
```

- `━━━` header separator is mandatory
- Pure numbered list (no flags, no CJK `·` alignment padding, no country codes in title)
- Panel title is `AppStore 限免` or `AppStore 限免 (CN)` — no flag emoji
- IAP items show `(subject)` after the title
- Icons: `gift.circle` / `#FF2D55` (error: `exclamationmark.circle` / `#FF3B30`)

**sgmodule `#!arguments` — comma-colon style:**
```surge
#!arguments = appCount:8, region:cn, group:Proxy
```

- **NOT** standard query-string (`appCount=8&region=cn`)
- **NOT** `{{{args}}}` shorthand — use explicit `{{{var}}}`:
  `argument=appCount={{{appCount}}}&region={{{{region}}}`

**Script parses `$argument` with regex (not split, not JSON):**
```js
let count = 8;
if (typeof $argument === 'string' && $argument) {
  let m = $argument.match(/appCount=(\d+)/);
  if (m) count = parseInt(m[1]);
}
```

See `references/appstore-free-panel.md` for the complete exact deployed version.

### Key facts documented live from the API

- **`dailyDeals` is global** — no region/country/storefront fields in the API. Different Accept-Language headers return identical results. The `region` parameter only changes the panel title, NOT the data.
- **"换区" (region switching) is Surge proxy switching, NOT data source filtering** — `action=switch&region=日本` calls `$surge.setSelectGroupPolicy(group, "日本")` to switch the Surge proxy group to a Japanese node. This lets the user download region-locked apps. The data list remains global regardless.
- **IAP items are sparse** (~1 per page). Need `MAX_PAGES = 20` to get enough. On MAX_PAGES=5 only ~5 IAP items.
- **Classification rules:**
  - `newPriceTier === 0 && oldPriceTier !== null` → 本体限免
  - `newPriceTier === 0 && oldPriceTier === null && subject` → 内购限免
  - `newPriceTier === 0 && oldPriceTier === null && !subject` → free promo (归类到 本体限免)

### Sample sgmodule

```surge
#!name=AppStore 限免面板
#!desc=AppRaven 实时数据 | 本体/内购限免 | 参数编辑框实时生效 | 支持换区
#!author=7452323
#!homepage=https://github.com/7452323/QuantumultX
#!arguments = appCount:8, region:cn, group:Proxy
#!arguments-desc = appCount:显示条数(1-30,默认8), region:地区显示标识(cn/us/...), group:策略组名称(默认Proxy)

[Panel]
限免 = script-name=AppStore_Free_Panel, update-interval=600

[Script]
AppStore_Free_Panel = type=panel, script-path=https://raw.githubusercontent.com/7452323/QuantumultX/main/script/AppStore_Free_Panel.js?t=5, argument=appCount={{{appCount}}}&region={{{region}}}&group={{{group}}}
```

### Panel arguments (Surge's `{{{param}}}` syntax)

- **`appCount`** — number of items (max 30, default 8)
- **`region`** — App Store country code display label (cn/us/jp/kr/gb/hk/tw etc.)
  - Does NOT filter the data source — `dailyDeals` is global
  - Only changes the panel title: `AppStore 限免 (CN)`
- **`group`** — Surge strategy group name for region switching (default `Proxy`)
- **`action`** — when set to `switch`, calls `$surge.setSelectGroupPolicy(group, region)` to switch Surge proxy instead of showing deals
  - Placeholder mode: user edits args to `action=switch&region=日本`, taps panel → proxy switches
  - Then edits args back to normal (remove action) to restore display

All editable in the SGModule's panel edit dialog.

### Key differences from cron→WxPusher

| Aspect | Cron + WxPusher | Surge Panel |
|--------|-----------------|-------------|
| Server | VPS needed | None (runs on device) |
| Delivery | WeChat push | In-app panel |
| Query | N/A | GraphQL via `$httpClient.post` |
| Language | Python | JavaScript (Surge runtime) |
| Params | Hardcoded | Editable via `{{{}}}` |

### Surge Panel pitfalls

- Surge `$httpClient` callback: `(err, resp, data)` — `data` is already a string, NOT a buffer
- Script MUST call `$done({title, content})` to return results
- **`$argument` IS A QUERY STRING (`appCount=8&region=cn`), NOT JSON!** 
  - 7452323 user parses with regex: `$argument.match(/appCount=(\\d+)/)`
  - Alternative: `split('&')` approach
  - **DON'T `JSON.parse($argument)`** — it crashes silently
- **User-specific convention: comma-colon `#!arguments` style** (`appCount:8,region:cn`) NOT standard `=` and `&`. Reference via `{{{var}}}` NOT `{{{args}}}`.
- Panel content is basic Markdown only: `**bold**`, `[links](url)`, `` `code` `` — image URLs NOT rendered
- Artwork URL contains `{w}x{h}{c}.{f}` → replace with `100x100bb.png` for thumbnails
- **`dailyDeals` is global data** — region parameter doesn't filter results, only changes panel title text
- **`action=switch` mode**: When `$argument` contains `action=switch&region=日本`, the script calls `$surge.setSelectGroupPolicy(group, region)`. The panel becomes a proxy switcher, not a deal viewer. After switching, edit args back to normal to restore deal display.

### Panel arguments in sgmodule

For editable args, use comma-colon style (7452323 user preference):
```ini
#!arguments = appCount:8, region:cn
#!arguments-desc = appCount:显示条数(1-30,默认8), region:地区(cn/us)

[Panel]
PanelName = script-name=ScriptName, update-interval=600

[Script]
ScriptName = type=panel, script-path=..., argument=appCount={{{appCount}}}&region={{{region}}}
```

- Use `{{{var}}}` (三花括号) for each parameter, NOT `{{{args}}}` shortcut
- `&` to join multiple params in `argument=` value (query-string format)
- Script parses `$argument` string via regex or split

---

## Delivery Method 2: WeChat Official Account (WxPusher)

### 未认证订阅号 Hard Constraints

**HARD NO.** Unverified 订阅号 cannot push content via API.

| API | Status |
|-----|--------|
| `cgi-bin/token` | ✅ Working |
| `account/getaccountbasicinfo` | ✅ Working |
| `media/upload` | ✅ Working |
| `draft/add` | ✅ Working |
| `freepublish/submit` | ❌ 48001 |
| `message/mass/send` | ❌ 48001 |
| `menu/create` | ❌ 48001 |

**The only real delivery paths:**
1. WxPusher — third-party push service, delivers card messages to WeChat
2. 认证公众号 (¥300/year) — unlocks all APIs
3. Mini Program + web-view — if user has one

---

## Delivery Method 3: Cron + Python script

```bash
hermes cron create \
  --schedule "0 * * * *" \
  --name "appraven-daily-update" \
  --prompt "Run /root/gen_appraven_page.py to update the daily deals page" \
  --toolsets terminal
```

Relevant Python helpers (from history):
- `/root/gen_appraven_page.py` — generate HTML page from AppRaven data
- `/root/wx_push_appraven.py` — push via WxPusher
- `/root/appraven_api.py` — CLI tool: query 限免/price drops/app details

---

## GitHub deployment (steal repo convention)

Files go in `surge/` and `script/` dirs. Raw URLs:
- sgmodule: `https://raw.githubusercontent.com/{user}/{repo}/main/surge/AppStore_Free_Panel.sgmodule`
- JS: `https://raw.githubusercontent.com/{user}/{repo}/main/script/AppStore_Free_Panel.js`

---

## General pitfalls

- Introspection disabled → extract queries from JS bundle via regex
- Webpack bundle is single-line minified → use Python re to find `query|mutation|fragment`
- Apollo `gql` tag compiles to `kind:"Document"` → search by `operationName`
- Artwork URL has `{w}x{h}{c}.{f}` → replace with `512x512bb.jpeg` or `120x120bb.png`
- DailyDeals includes IAP deals (no app.ITunesId) — filter those out when looking for app deals
- 未认证订阅号 most APIs blocked → don't waste time trying variations

---
