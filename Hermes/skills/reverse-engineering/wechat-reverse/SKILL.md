---
name: wechat-reverse
category: reverse-engineering
description: >-
  Merged skill combining: wechat-code-reverse, wechat-mini-program-automation, wechat-miniapp-automation.
version: "1.0"
sources:
  - wechat-code-reverse
  - wechat-mini-program-automation
  - wechat-miniapp-automation
tags: [reverse-engineering, merged]
---

# wechat-reverse

> **Merged from**: wechat-code-reverse, wechat-mini-program-automation, wechat-miniapp-automation
> **Source count**: 3

---

## Table of Contents

1. [wechat-code-reverse](#wechat-code-reverse)
2. [wechat-mini-program-automation](#wechat-mini-program-automation)
3. [wechat-miniapp-automation](#wechat-miniapp-automation)

---

## wechat-code-reverse

# 微信 Code 获取站逆向

## 概述

微信扫码登录 code 获取站通常提供三步流程：
1. **验证** — 人机验证（极验/滑块/CAPTCHA）
2. **扫码** — 显示微信登录二维码，轮询扫码状态
3. **获取 Code** — 扫码确认后返回 `wx_code`

## 典型接口模式

### 无防护站（如 yx520.ltd）

纯 PHP 后端，无签名无防重放，3 个 GET 接口即可完成：

```bash
# 1. 获取二维码
curl "https://yx520.ltd/code/code.php?action=get_qr"
# → {"code":200, "data":{"uuid":"xxx", "qr_data":"http://weixin.qq.com/x/xxx"}}

# 2. 轮询扫码状态（每2秒）
curl "https://yx520.ltd/code/code.php?action=check_qr&uuid=xxx"
# → code:200=扫码成功, code:202=等待中

# 3. 获取最终 code
curl "https://yx520.ltd/code/code.php?action=login&wxid=xxx"
# → {"code":200, "data":{"wx_code":"xxx"}}
```

### 带极验站（如 hc.wwszxc.tax:20308 — QQ经典农场）

前端用 Geetest v4 滑块验证，通过后调后端接口。Node.js 后端，接口带固定 auth header。

**关键参数：**
- captcha_id: `548f70bc9ea9fe2c7a2d2bfe8ffebb03`
- auth header: `0dc4f132be5555063793663035b5fb42`（固定值，硬编码在 app.js）
- appid: `wx5306c5978fdb76e4`（默认微信 appid，用户可 localStorage 覆盖）
- 轮询间隔: 2 秒, 二维码过期: 180 秒

**接口：**
| 接口 | 方法 | Body | 返回 |
|------|------|------|------|
| `/api/qr/start` | POST | `{geetest: result}` | 二维码 URL + uuid |
| `/api/qr/status?uuid=xxx` | GET | — | 扫码状态（scanned/confirmed/expired） |
| `/api/accounts/add` | POST | `{displayName, code}` | 保存账号 → openid |
| `/wx/code` | POST | `{openid, appid}` | 最终 code |

### 腾讯云 API + 极验站（如 hc.wwszxc.tax 另一版本）

部分站点后端架在腾讯云 API 网关（tcapi 域名），app.js 中的某些 API 域名可被 localStorage 覆盖：
```javascript
// app.js 中的服务端配置
function getServer() {
    return '';  // 空 = 同域
}
```

### 固定 token 站（如部分 PHP 站）

auth header 硬编码在 JS 中，可用固定 token 直接调用所有接口。

## 逆向步骤

### 1. 打开页面看 JS 源码
- 检查 `<script>` 标签找 API base URL、captcha_id、auth token
- 找 `fetch()` 调用看完整请求格式
- 找轮询间隔（通常 2 秒）
- 找 localStorage 存储的配置（如 auth token、appid）
- 找用户代理函数（`getServer()` 等）

### 2. 抓取核心请求
- 极验站点需先通过滑块验证才能看到后端接口
- 用浏览器工具看网络请求面板
- 记录所有 fetch/XHR 请求的 URL、method、headers、body
- 注意观察 auth header 是否是固定值

### 3. 区分防护等级

| 防护 | 特征 | 可自动化？ |
|------|------|-----------|
| 无防护 | 直接 curl GET，返回 JSON | ✅ 纯脚本 |
| 固定 token | auth header 硬编码在 JS 中 | ✅ 纯脚本（如果极验也能过） |
| 动态签名 | 每个请求 token 不同 | ⚠️ 需浏览器 |
| 极验 v4 | 滑块验证 | ⚠️ 需过滑块，headless可能失败 |
| 极验+Cloudflare | 双重防护 | ❌ |

## 注意

- `wx_code` 和 `openid` 是敏感数据，不要泄露到公开 Gist
- 极验 v4 滑块在 headless 浏览器中可能加载失败（baidu 离线宝也如此）
- 默认 appid 和 auth token 通常硬编码在 app.js 中
- 部分站点支持 localStorage 覆盖默认参数（appid、auth、server API）
- 扫码二维码过期时间通常 3-5 分钟，轮询间隔 2 秒
- QQ经典农场站的 `getServer()` 返回空字符串 = API 同域，不留 server 端修改空间
- Stash APP 中有 `wxCode: any[]` 等微信 code 相关变量，可用作搜索关键词

---

## wechat-mini-program-automation

# WeChat Mini-Program Automation

## 适用场景

- 需要自动化多个微信小程序的签到/任务/查询
- 多账号批量操作，每个账号需要独立的微信登录态
- 希望登录态可跨脚本复用，不用每个脚本自己处理微信登录
- 需要 token 缓存 + 自动续命机制，避免频繁手动授权

## 核心架构：登录态即服务

```
微信账号 ──扫码绑定──→ 集中式登录代理 (YYB Go / 自托管)
                            │
                            ├── /accounts          → 列出所有已绑定账号
                            ├── /accounts/refresh  → 主动刷新登录态
                            ├── /wxapp/getCode     → 取 code
                            └── /wxapp/getPhoneNumber → 取手机号加密数据
                                  │
                                  ↓
                      多个自动化脚本共享同一套登录基础设施
                            │
                            ├── 用 code → 换业务 token
                            ├── 用 token → 签到/任务/查询
                            └── token 失效 → 自动重登
```

## YYB Go 模式详解

### 什么是 YYB Go

YYB Go 是**自托管 Go 服务**，利用**应用宝协议**获取微信小程序的登录 code，通过 HTTP API 暴露给自动化脚本。

**为什么不是公共平台：** 微信账号是你自己的，YYB Go 实例也是你自己部署的。不存在"公共 YYB"。

### 环境变量格式

```
YYB_GO=服务器IP或域名@账号标识
```

多行换行分隔，支持批量：
```
YYB_GO=1.2.3.4:8000@openid_xxx
YYB_GO=1.2.3.4:8000@openid_yyy
```

### GitHub 仓库索引

| 仓库 | 语言 | 说明 |
|------|------|------|
| wyd3325/YYB_GO | Go | 原始仓库 |
| Aoluis1005/yyb-go | Go | Go 重写版，部署简单 |
| SuperNaiBA/YYB_GO | Go | 应用宝协议实现 |
| juelianxyt/YYB-GO-Script | JavaScript | 脚本集合 |

## Token 缓存模式（跨脚本通用）

所有 YYB Go 驱动的脚本都采用相同的缓存策略：

```json
// token_caches/xxx_token_cache.json
{
  "账号标识(ref)": {
    "token": "eyJ...",
    "userId": "12345",
    "userName": "昵称",
    "updatedAt": "2026-07-24T10:00:00"
  }
}
```

### 失效检测（两种方式）

**被动检测（最常用）：**
- 调业务 API 返回 `40001` / `401` / "请重新登录" → 标记失效
- 静默标记，交由主流程重新登录

**主动探测：**
- `/api/member/signin/getSignInfo` 等探活接口返回 200 → token 仍有效
- 星妈优选脚本采用此方式

### 刷新流程

```
1. 读本地缓存 token
2. 用 token 探活 → 有效则直接用
3. 失效 → 调 YYB Go /wxapp/getCode 取新 code
4. 用 code 换 token → 更新缓存
```

### 准永久 Cookie 真相

YYB Go **做不到永久 token**：
- 服务端 token 有效期通常 7天~数月不等
- 缓存 + 自动重登让体验上接近"永久"
- `/accounts/refresh` 可主动刷新，但受限于微信侧 code 本身的有效期

**本质：** YYB Go 把"每天输密码"变成"偶尔换票"，是**自动续命**而非永久。

## 脚本类型与 YYB Go 兼容性

### 两种脚本架构

| 类型 | 运行环境 | 能否调 YYB Go | 典型代表 |
|------|----------|---------------|----------|
| **iOS 代理脚本** | Surge/QX/Loon (手机) | ❌ 不能 | tlyj.js (天龙驿站) |
| **Node.js 脚本** | 服务器/青龙 | ✅ 能 | uicbox.js, t3dc.js, xmyx.py |

### 为什么 iOS 代理脚本不能调 YYB Go

1. **运行位置**：iOS 代理脚本在手机端运行，拦截的是小程序与服务器之间的 HTTP 流量
2. **数据可见性**：脚本只能看到请求/响应中的数据，openid 只存在 YYB Go 数据库里，不会出现在业务 API 的响应 body 中
3. **网络限制**：iOS 代理脚本无法直接发起新的 HTTP 请求到 YYB Go 服务

### iOS 代理脚本的可用标识

iOS 代理脚本只能用**业务 API 返回的字段**作为账号标识：
- `mobile` — 手机号（天龙驿站 customer/detail 接口返回）
- `nickname` / `nickName` — 昵称
- `userId` — 用户 ID

**无法获取 openid**，因为 openid 是微信侧的，只存在于 YYB Go 数据库中。

### 用户偏好：优先用 openid 做标识

当脚本运行在 Node.js 环境时，优先使用 openid 作为账号标识（通过 YYB Go ref 传入），而非昵称。

```
YYB_GO=23.254.212.223:8000@owNAX6nwf04xcY9rmY46sXJp63FI
```

## 跨脚本架构对比

| 维度 | 优宠盒子 (uicbox.js) | T3打车 (t3dc.js) | 星妈优选 (xmyx.py) | 天龙驿站 (tlyj.js) |
|------|---------------------|-------------------|---------------------|---------------------|
| 类型 | Node.js | Node.js | Python | iOS 代理脚本 |
| AppID | wxf5694d269139b767 | wxe241a1d8464bc578 | wx4205ec55b793245e | wx692c4fa7343becd4 |
| HOST | server.uicbox.cn | passenger.t3go.cn | www.feihevip.com | myx.tlyzclub.com |
| 登录方式 | code + 手机号密文 | code only | code only | 拦截响应取 token |
| YYB Go | ✅ | ✅ | ✅ | ❌ |
| 标识字段 | openid (ref) | openid (ref) | openid (ref) | mobile / nickname |
| 任务复杂度 | 签到+查积分 | 签到+任务中心+活动 | 签到+日常任务(多次) | 签到+点赞+视频+分享+游戏 |
| 通知 | 企业微信 webhook | 企业微信 webhook | notify.py | 内置 notify |

## 风控头处理策略

T3打车脚本的风控头全部环境变量化，**留空也能跑**：

```javascript
const RISK_DEVICE_TOKEN = process.env.T3_RISK_TOKEN || "";
const NONCE_STR = process.env.T3_NONCE || "gtrgtr";
const SIGN = process.env.T3_SIGN || "";
```

**原则：** 不内置任何抓包数据，遇到"操作存在风险"再用自己抓包的值设置对应环境变量。

星妈优选的 MD5 签名则需要内置密钥（`TwUQ01lKS1Km5zlV2f7amsZc5EQYkTbv`），因为服务端强校验。

## 部署注意事项

1. **YYB Go 实例必须自己部署**，不要暴露到公网
2. 微信账号绑定在 YYB Go 中，实例被入侵 = 微信登录态泄露
3. 应用宝协议本身非官方，存在被腾讯封堵的风险
4. 建议内网部署 + IP 白名单
5. token 缓存文件不要提交到公开仓库

## Pitfalls

### 1. 并发取码被风控

YYB Go 服务端对同一个 ref 的并发取码有限制。所有脚本都在请求前加了随机延迟：
```javascript
const delay = Math.floor(Math.random() * 5000) + 5000; // 5-10s
await new Promise(r => setTimeout(r, delay));
```

### 2. 手机号授权过期

优宠盒子需要手机号加密数据（encryptedData + iv）。如果用户未在 YYB 端为该账号完成手机号授权：
```javascript
// 提示：手机号未授权，请在 yyb 端为该账号完成手机号授权后重试
```

### 3. 积分接口滞后

查询积分时可能拿到旧数据。兜底策略：
```javascript
// 积分接口滞后时，用签到/任务返回的 award 兜底
if (gained == 0 && (sign_award || task_award)) {
    gained = int(sign_award || 0) + int(task_award || 0);
}
```

### 4. token 缓存文件损坏

所有脚本都有 try/catch 保护：
```javascript
try { fs.mkdirSync(path.dirname(TOKEN_CACHE_FILE), { recursive: true }); } catch (e) {}
```

## 协作链

```
部署 YYB Go → 绑定微信账号 → 编写业务脚本 → 设置 YYB_GO 环境变量 → 定时运行
```

## 相关技能

- `web-api-protocol-reverse` — 当需要逆向业务 API 的签名/加密时
- `reverse-playbook` — 当目标 App 本身需要逆向时
- `algorithm-reverse` — 当需要还原业务 API 的签名算法时

## 参考文档

- `references/tianlong-yizhan-ios-proxy.md` — 天龙驿站 iOS 代理脚本分析（不能接入 YYB Go 的原因）
- `references/yyb-go-repos.md` — YYB Go 仓库索引

---

## wechat-miniapp-automation

# WeChat Mini-Program Automation

## Ecosystem Overview

Most 微信签到 scripts share a common architecture:

```
[YYB-Go Service] ←→ [WeChat MMTLS] ←→ [WeChat Servers]
       ↑
  /wxapp/getCode      ← script calls this, gets fresh code
  /wxapp/getPhoneNumber
       ↓
[Sign-in Script] ←→ [Mini-program API] ←→ [business server]
```

**YYB-Go** is a self-hosted Go service that manages WeChat login state. It:
- Stores `login_buffer` (long-lived credential from QR scan)
- Talks MMTLS (ECDH + shortlink) to WeChat servers
- Exchanges login_buffer → fresh `code` on demand
- Refreshes expired login_buffers via `/accounts/refresh`

## Script Anatomy (3 known variants)

### 1. JS variant (uicbox.js, t3dc.js)
```
YYB_GO injection block  ← hooks console.log + process.exit, pushes to 企业微信 webhook
ServerInfo parsing       ← "host@ref" format, ref = openid or YYB identifier
getCode(server)          ← POST to http://host/wxapp/getCode with {ref, app_id}
getPhoneNumber(server)   ← POST /wxapp/getPhoneNumber (some mini-programs need this)
Login flow               ← code + encryptedData + iv → exchange for accessToken
Token cache              ← local JSON file, keyed by ref/openid
Task loop                ← sign-in → task list → receive → finish → activity
```

**YYB_GO injection** (uniform across JS scripts):
```javascript
// Hooks console.log/error, buffers last 500 lines
// On process.exit / beforeExit → flush() →
//   1. require('./sendNotify') → call sendNotify(title, body)
//   2. fallback: curl POST to qyapi.weixin.qq.com/cgi-bin/webhook/send?key=QYWX_KEY
```

**Token caching pattern** (t3dc.js `Task` class):
```javascript
// 1. read token_caches/<script>_token_cache.json
// 2. if cached.token → checkToken() via /user/passengerInfoNew
// 3. if 401 / "请重新登录" → removeCachedToken() → login()
// 4. login() → getCode() → /login/loginThirdMini → applyToken() → saveCachedToken()
```

**Request signing** (t3dc.js):
- Headers: `fhAppid`, `fhNonceStr`, `fhTimestamp`, `sign`, `riskdevicetoken`, `noncestr`
- `sign = MD5(sort([fhAppid, fhNonceStr, fhTimestamp, dataSignValue]) + APP_KEY).upper()`
- All risk headers are env-var driven, can be left empty if server doesn't enforce

### 2. Python variant (xmyx.py)
```
YYB HTTP API layer       ← direct calls to YYB-GO service (no local require)
Account filtering        ← whitelist/blacklist by openid or nickname
Signature (MD5)          ← same algorithm as JS variant
Token probing            ← checkToken via getSignInfo before using cached token
Task system              ← getTaskList → loop: tofinish → wait → completeTask
Skip task types          ← YXXD (purchase), 6 (group), YXBQ (re-sign), YXDZP (wheel), YXDY (subscribe)
```

**Signature detail** (xmyx.py):
```python
sign_keys = sorted(["fhAppid", "fhNonceStr", "fhTimestamp", data_sign])
text = ""
for key in sign_keys:
    if key in headers:
        text += key + str(headers[key])
    else:
        text += key
sign = md5((text + FH_APP_KEY).encode()).hexdigest().upper()
```

**YYB HTTP API** (Python variant):
- `GET /accounts` → list all accounts with status alive/expired
- `POST /accounts/refresh` → refresh login_buffer (single or all)
- `POST /wxapp/getCode` → `{ref, app_id}` → code

### 3. "suntory" variant (suntory-yyb.js)\n```\nyyb env = just server address (no @openid), multi-line\n↓\nGET /accounts → list all accounts with {openid, alias, nickname, status}\n↓\nfor each account → POST /wxapp/getCode with its openid → login\n```\nKey difference from mql.js: uses `/accounts` to pull accounts dynamically from YYB server, then iterates. The `yyb` env var contains only addresses, not `host:port@openid`.\n\n### 4. Go (YYB-Go server itself)\nSee `references/yyb-go-architecture.md` for full source review.

## Common API Patterns

| Operation | Endpoint | Notes |
|-----------|----------|-------|
| Code exchange | `/wxapp/getCode` | `{ref, app_id}` → `data.result.code` |
| Phone number | `/wxapp/getPhoneNumber` | returns `encryptedData + iv` |
| Login | `/uac/wxMini/callback` or `/login/loginThirdMini` | code + iv + encryptedData → accessToken |
| Sign-in | `.../sign/signIn` or `.../saveUserScore` | type=2 for daily check-in |
| Token refresh | `POST /accounts/refresh` | refreshes login_buffer on YYB side |

## Token Lifecycle

1. **QR scan** → YYB captures `login_buffer` (long-lived, days to weeks)
2. **Code exchange** → script calls `/wxapp/getCode` → YYB uses MMTLS to get fresh code (5-min TTL)
3. **Login** → code + encryptedData → business server issues `accessToken` (7-day to months TTL)
4. **Cache** → accessToken stored locally, reused until 401/40001
5. **Refresh** → when accessToken expires, go back to step 2 (not step 1)

## Risk Headers

Common anti-bot headers seen in these scripts:
- `riskdevicetoken` — device fingerprint
- `sign` / `fhSign` — request signature
- `noncestr` / `fhNonceStr` — replay nonce
- `graybuild` / `grayversion` — client version fingerprint

**Rule of thumb**: most servers don't strictly validate these if you leave them empty/default. Only set from your own packet capture if you hit "操作存在风险".

## YYB Keepalive Script

A separate cron script that calls `POST /accounts/refresh` periodically to maintain MMTLS session freshness. See `references/yyb-keepalive-pattern.md`.

## Notification Patterns

1. **企业微信 webhook** (JS): `curl POST qyapi.weixin.qq.com/cgi-bin/webhook/send?key=XXX`
2. **sendNotify.js** (JS): standard 青龙面板 notification module
3. **notify.py** (Python): same concept, Python ecosystem

## YYB_GO-Only Workflow (Primary Pattern)

**This user's preferred workflow** — NOT multi-platform adaptation:

1. Take the original JS script (already has YYB_GO notify injection + console hooks)
2. **Only change**: fill in the `YYB_GO` default value: `process.env.YYB_GO || "host:port@ref"`
3. Deliver the file unchanged otherwise
4. No Surge/Loon/QX runtime adapter, no pure-JS AES fallback, no `$.done()` injection
5. Scripts run on Node/青龙 only — that's the intended runtime

**When to offer multi-platform**: only if the user explicitly asks for Surge/Loon/QX support. Default is Node-only.

**TLYJ_ENC_KEY** is a separate env var for AES key, not related to YYB_GO.

## References

- `references/yyb-go-architecture.md` — full YYB-Go source review (protocol, store, httpapi)
- `references/script-patterns.md` — common code snippets across variants (includes Pattern 13: Multi-Platform adapter)
- `references/tlyj-cst-scripts.md` — specific details for 天龙驿站 and 城市通 scripts
- `references/michelin-analysis.md` — 米其林会员俱乐部 script analysis (wx14413dafd16b9540, two-step refresh→access token, questionnaire task system)
- `templates/unified-adapter.js` — reusable multi-platform runtime adapter for Surge/Loon/QX + Node (use only on demand)

## 🚨 Critical Pitfalls

### No Hardcoded Server IPs
**NEVER** embed the YYB server IP/port as a default value in any script meant for sharing. `process.env.YYB_BH || '1.2.3.4:8000'` exposes the user's infrastructure. Env vars must be **required with no fallback** — the user sets them in their own environment.

### Keepalive Notification Format
Must be exact: success → `「昵称」保活成功`, failure → `《账号过期》重新扫码`. Not "YYB保活失败" or freeform variations.

---
