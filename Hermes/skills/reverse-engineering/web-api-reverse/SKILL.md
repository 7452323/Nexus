---
name: web-api-reverse
category: reverse-engineering
description: >-
  Merged skill combining: web-api-protocol-reverse, web-api-reverse-engineering, web-tool-reverse-engineer, novel-platform-api-reverse, simple-php-site-reverse, site-wide-exhaustive-reverse.
version: "1.0"
sources:
  - web-api-protocol-reverse
  - web-api-reverse-engineering
  - web-tool-reverse-engineer
  - novel-platform-api-reverse
  - simple-php-site-reverse
  - site-wide-exhaustive-reverse
tags: [reverse-engineering, merged]
---

# web-api-reverse

> **Merged from**: web-api-protocol-reverse, web-api-reverse-engineering, web-tool-reverse-engineer, novel-platform-api-reverse, simple-php-site-reverse, site-wide-exhaustive-reverse
> **Source count**: 6

---

## Table of Contents

1. [web-api-protocol-reverse](#web-api-protocol-reverse)
2. [web-api-reverse-engineering](#web-api-reverse-engineering)
3. [web-tool-reverse-engineer](#web-tool-reverse-engineer)
4. [novel-platform-api-reverse](#novel-platform-api-reverse)
5. [simple-php-site-reverse](#simple-php-site-reverse)
6. [site-wide-exhaustive-reverse](#site-wide-exhaustive-reverse)

---

## web-api-protocol-reverse

# Web API Protocol Reverse — Web API 协议逆向

## 适用场景

- 目标使用**私有/未公开 API 协议**（非标准 REST/GraphQL）
- 目标前端 SPA 与后端之间有**抗爬虫机制**（PoW、Turnstile、签名）
- 需要将私有 API 包装为**标准 OpenAI 兼容接口**
- 目标有**access_token + refresh_token** 认证体系
- 需要从 Web 版 JS bundle 发现隐藏 API（无 IPA/APK 可用时）

### SPA JS Bundle API 发现方法

当没有 IPA/APK/二进制，只能访问 Web 版时，通过分析 JS bundle 直接发现隐藏 API。

参见参考文档: `references/picseed-api-reverse.md`

### Pitfall: 付费资源站点的「假」下载链接

很多小说/资源站（如 zxcstxt.com）详情页显示"ZIP大小: X MB"，但**实际下载链接在付费墙后面**。

**识别特征：**
- HTML含 `class="pay-resource"` 或文字 "付费资源，请付费后查看"
- 站点以 WordPress 构建（REST API: `/wp-json/wp/v2/posts`），书籍 attachments 不在本书媒体库中而是分散在全站附件列表
- 详情页 `window._win.imgbox_down` 为空字符串（无直接下载地址）
- 全站附件 API 返回的是最新上传的20个文件，**不按 post_id 关联**

**处理策略：**
1. 先用 WP REST API 获取完整列表：`/wp-json/wp/v2/posts?per_page=100&orderby=id&order=asc`
2. 解析每本书的 content.rendered 字段，找是否有网盘URL（pan.baidu / lanzou / 115 / aliyun）
3. **如果所有书都穿付费墙且无外部网盘URL → 直接放弃，付费是业务壁垒，非技术**
4. 如果有外部网盘URL（如 pan.baidu），则直接转存到115
5. 如果有 lanzou.com 等免费网盘，可以用 scrapling 的 Fetcher 下载附件直链到临时文件，再上传到目标网盘

**红旗信号（付费墙特征，看到就放弃强制爬取）：**
- HTML中多处出现 "付费资源" 文字
- 页面上 `download` 按钮点击后弹出支付宝/微信二维码
- 文件直链需要特定 token 且 token 与 post_id 绑定

### SPA 全路径 200 Fallback 陷阱 — 数据文件藏在 inline JS 中

很多 SPA/PWA（React/Vue）站点配置了 **History API Fallback**（SPA 路由），导致所有 GET 路径都返回同一个 HTML 壳（通常是 200）。

**识别特征：**
- 所有 `/api/xxx` 路径都返回 HTML（title 而不是 JSON）
- 没有独立的后端路由（纯静态托管 / GitHub Pages / Cloudflare Pages）

**提取策略（按效率递减）：**

1. **grep `DATA_FILE` / `API_PATH` / `CACHE_CONFIG`** — 数据端点通常是 inline JS 中硬编码的常量：
   ```bash
   curl -s 'https://site/' | grep -oP 'DATA_FILE:\s*["'"'"']([^"'"'"']+)["'"'"']'
   curl -s 'https://site/' | grep -oP 'CACHE_CONFIG[^;]+'
   curl -s 'https://site/' | grep -oP 'fetch\([^)]+\)'
   ```

2. **grep `manifest.json`** — PWA 站点的 manifest 常暴露应用名、图标，有时还有数据文件路径

3. **遍历 `/data/*.json`** — Next.js SSG 常见构建时缓存模式：
   ```bash
   for f in plugins list data items pages; do
     code=$(curl -s -o /dev/null -w '%{http_code}' "https://site/data/${f}.json")
     [ "$code" = "200" ] && curl -s "https://site/data/${f}.json" | head -c 500
   done
   ```

4. **Service Worker 访问模式** — 检查 `sw.js` 看它预缓存了哪些 JSON 文件

**实战案例（hub.kelee.one — Loon 插件中心 2026-07-14）：**
- 所有 `/api/*` 路径 200 返回 HTML（SPA fallback）
- grep `DATA_FILE: 'list.json'` 在 inline JS 中找到真实数据端点
- `GET /list.json` → 直接返回明文插件目录 JSON（含 `loon://import?plugin=...` 下载链接）
- **无任何认证即可完整抓取所有插件元数据**

### 实战案例：纯 SPA 落地页 — 接口只在 APP 里（黄果短剧 huangguo.com — 2026-07-15）

某些 App-first 平台（短剧/小说/成人内容/工具类）的 Web 端是纯 SPA 落地页，**Web 端不暴露任何业务 API**。

**识别特征：**
- 所有 GET 路径（含 `/api/*`）均返回 `200 + index.html`（History API Fallback）
- 只有 1-2 个路由（`/` 和 `/h5-install`）
- 页面内容是营销落地页（下载引导/社群入口）
- 前端 JS bundle 中找不到任何业务 API 端点
- APK 镜像站（APKPure/Evozi 等）通常被 CF 从 VPS 封锁

**黄果短剧实测结果：**
- 落地页路由：`/`（PC 展示）+ `/h5-install`（移动端安装引导）
- 前端 JS（86KB + 114KB）仅含 Vue 3 渲染逻辑 + 埋点 SDK，**零业务接口**
- `landing-sdk-v1.1.0.js`（12KB）含埋点上报端点：`/api/eventTracking/report.json`、`/api/eventTracking/batchReport.json` — 这些是 SDK 级 analytics，非业务 API
- 设备 ID 生成密钥硬编码：`device_id_secret_key_v1`（在 SDK 中）
- 社交账号：`@huangguodrama`（Telegram/X/TikTok）— App-first 平台常以 Telegram 为主阵地

**处理策略（按效率递减）：**
1. **APK 下载 + 静态分析** — 从 APKPure/Evozi/F-Droid 等镜像下载（需住宅代理绕 CF），用 jadx/GDA 反搜 API
2. **代理抓包** — 在已安装 APP 的设备上配置 HTTP 代理（mitmproxy/Charles）抓真实请求
3. **Telegram Bot/社群侦察** — 很多 App-first 平台的 API 文档/内测/故障通告在 Telegram 群里
4. **提供 IP 池** — 如用户自己抓包或提供 APK，可协助逆向

**红旗信号（落地页模式识别，看到就按 APP 逆向处理，不再死磕 Web）：**
- 所有 API 路径 200 返回 HTML
- 前端 JS 只有 vendor + chunk 无业务代码
- 页面只有下载引导/社群链接无实际数据展示
- APK 镜像站均从 VPS 返回 403

详见 `references/huangguo-landing-page-no-api.md`

### Pitfall: Turbopack/Next.js 混淆的 bundles 中可能不含字面路径

某些使用 Turbopack 编译的 Next.js 15+ 应用（如 Sakura `xn--ug8h.eu.org`），路由路径（如 `/api/appfree`、`/api/iap`）不会作为字符串字面量出现在 JS chunks 中——它们是内部 route table 的引用，被编译为整数 index。

**结果：`grep -oP '/api/[^"]+' bundle.js` 找不到任何端点路径。**

**绕法（按效率递减）：**

1. **curl 暴力枚举已知页面路由** — `curl -s 'site/api/{appfree,iap,daily,price,search}'` 直接试，响应最快
2. **查静态 JSON 备份** — Next.js SSG 常生成 `/data/{name}.json` 作为 `/api/{name}` 的构建时缓存（如 `data/appfree.json` = `api/appfree` 的快照）
3. **页面前端反向映射** — Nav 栏的每个路由名 = 大概率对应同名 API
4. **浏览器 Performance API** — 每个页面 navigate 后抓 `performance.getEntriesByType('resource')` 看到实际请求的 URL
5. **放弃静态分析** — 如果上面 4 步啥也没捞到，不要死磕 JS 反混淆，直接问用户看 Network 面板截图

### 方法论

```
1. 确定目标 App 的 Web 站
2. 识别前端框架（Next.js -> _next/static/、React SPA、Vue 等）
3. 下载所有 JS bundle
4. 对每个 bundle 搜索 API 特征
5. 提取请求参数和响应结构
6. 测试每个端点
7. 文档化完整 API 面
```

### Browser Performance API 快速API发现

在已知页面路由后，直接在各页面使用浏览器 Performance API 比下载所有 JS bundle 更高效：

```javascript
// 列出当前页面的所有API请求
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('api'))
  .map(r => ({ url: r.name, type: r.initiatorType, duration: r.duration }))

// 按域名过滤
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('your-target.com'))
  .map(r => r.name)
```

**优势**：无需下载/分析 JS bundle，直接看到实际请求的 API 端点、参数、耗时。
**配合**：导航到每个子路由后重复执行，发现各页面独有的 API 端点。

### 系统化多页面路由扫描

对于Next.js/SPA站点的完整API发现流程：

```
1. 从侧边栏/导航菜单识别所有路由（accounts, price, proxy, switch, etc.）
2. 用 browser_navigate 依次访问每个路由
3. 每次导航后用 performance API 捕获该页面发起的 API 请求
4. 合并去重得到完整 API 面
5. 对每个端点添加 Origin+Referer 头测试（见下文）
6. 检查 static data 路径（如 /data/countries.json）
```

### Next.js RSC vs REST API 区分

Next.js 页面使用 **RSC (React Server Components)** 流渲染时，数据在服务端直取，浏览器侧只能看到 `?_rsc=xxx` 的 RSC 流请求——**这些不是 REST API**，无法直接 curl 复用。如何区分：

| 特征 | RSC 流数据 | REST API |
|------|-----------|----------|
| URL 模式 | `页面路由?_rsc=hash` | `/api/xxx` |
| 响应类型 | RSC payload（二进制编码） | JSON / text |
| 是否可独立调用 | ❌ 不可直接curl解析 | ✅ 可直接curl调用 |
| 浏览器端如何发现 | 检查 `self.__next_f` RSC数组 | 检查 network 请求列表 |

**判断方法**：
- 页面加载后，检查 `self.__next_f` 是否包含数据（RSC流数据存于此）
- 同时检查 network 请求，如果只有 `?_rsc=` 请求而无 `/api/xxx` 请求，说明数据是服务端渲染的，不暴露 REST API
- 如有 `/api/proxy?page=N` 等清晰 REST 端点，才是可调用的 API

### 浏览器预注入 Hook 捕获 API 调用

当页面在客户端懒加载数据时，可以预注入 fetch 拦截器在导航前捕获 API：

```javascript
// 导航前在 console 执行
const origFetch = window.fetch;
window._apiCalls = [];
window.fetch = function(...args) {
  window._apiCalls.push(typeof args[0] === 'string' ? args[0] : args[0].url);
  return origFetch.apply(this, args);
};
// 然后 navigate/reload，再检查 window._apiCalls
```

### Origin + Referer 反爬校验（Next.js 常见）

部分 Next.js API 端点检验 `Origin` 和 `Referer` 头——缺失时返回 401/403 或自定义错误：

```
Missing origin and referer  ← 典型反爬提示
```

**必须同时添加两个头才能绕过**：
```bash
curl -s 'https://target.com/api/proxy?page=1&pageSize=40' \
  -H 'Origin: https://target.com' \
  -H 'Referer: https://target.com/proxy'
```

### 隐藏字段 Reveal 端点模式

Next.js 应用常在前端显示隐藏数据（`•••••••`），但后端有独立的 **reveal 端点**暴露实际值：

```
/api/accounts          → 返回列表（password: "•••••••", email: "sq***@outlook.com"）
/api/accounts/reveal?id=1-1 → 返回实际密码（password: "Mbb6UwkXuX"）
```

**关键陷阱：reveal 不一定暴露所有字段** — 有些 API 设计只 reveal 密码（可复制用于登录），**邮箱掩码可能永远不可逆**。邮箱掩码通常是服务端 API Route 做的（`email.replace(/(?<=.{2}).(?=.*@)/g, '*')`），不是前端做的。没有任何客户端参数可绕过。

**判断方法**：如果列表接口和 reveal 接口都不返回完整邮箱，说明掩码是数据库层或 API Route 层的安全决策。此时要么找到 MongoDB 凭据直接查库，要么找到上游数据源。

**搜索 JS bundle 找 reveal 模式**：
```bash
grep -oP '/api/[a-zA-Z0-9_/?=&%-]*reveal[^"' ]+' bundle.js
```

### Parse Server API 发现（POST body 认证模式）

当后端为 Parse Server 时，JS SDK **不把密钥放 HTTP Header**，而是嵌入 POST body：
```json
{"_method":"GET", "_ApplicationId":"...", "_JavaScriptKey":"...", "_ClientVersion":"...", "_InstallationId":"..."}
```

静态分析可能找不到密钥（环境变量/运行时注入）。使用 Playwright 拦截实际请求从 POST body 提取。

详见 `references/parse-server-api-discovery.md`

### Next.js Server Action 特殊处理

详见 `references/nextjs-server-action-discovery.md`

Next.js 15+ 用 Server Actions 处理表单提交（登录、注册等），action hash 通过 `next-action` HTTP header 传递。关键难点：

- **Login page chunk 懒加载**：页面级 chunk 通过 `self.__next_f` RSC payload 引用，**不在** `<script src>` HTML 标签中
- **必须同时解析两个来源**：`<script src>` 得到共享 chunk，RSC payload 得到页面级 chunk
- **优先扫描 login chunk**：路径含 `/login/` 的 chunk 优先下载
- **匹配模式**：`createServerReference)("hash_44chars", callServer, void 0, findSourceMapURL, "action_name")`
- **hash 长度限定 `{40,}`** 防止误匹配内嵌 hex

### 关键搜索词

```bash
# 搜索 API 路径
grep -oP '/v[0-9]+/[^"'"'"'`,\s)]+' bundle.js
grep -oP '/api/[^"'"'"'`,\s)]+' bundle.js

# 搜索认证密钥
grep -oP 'auth_key[^"'"'"'`,\s)]+' bundle.js
grep -oP 's_key[^"'"'"'`,\s)]+' bundle.js

# 搜索 URL 模式
grep -oP 'encodeURIComponent[^)]+' bundle.js
grep -oP 'URLSearchParams[^)]+' bundle.js

# 搜索域名
grep -oP 'https?://[^"'"'"'`,\s)]+' bundle.js | sort -u
```

## 通用技巧

### 认证边界测试 (Auth Boundary Testing)

在逆向任何 API 时，**必须测试3种认证状态**来区分不同的封锁层：

| 状态 | 测试方式 | 能揭示什么 |
|------|----------|-----------|
| No auth | 完全不加任何认证头/cookie | 平台是否允许匿名访问；是否需要登录才能使用 |
| Personal auth | 加上自己的合法 token | 个人是否有权限；限制是平台级还是分享者级 |
| Target's auth | 模拟目标系统的 token | 服务端是否区分不同用户的权限；限制是否在目标侧 |

**实战案例（123pan）**：没有 auth → 5112 "需要登录"；personal auth → 5113 "分享方流量不足" → 说明限制在分享者侧，完全不可绕过。

### 负面知识方法论

**负面知识（Negative Knowledge）和正面知识同等重要：**

- 记录所有试过但失败的 API 路径和方法（如 `/a/api/` vs `/b/api/` vs 旧版 `/api/`）
- 记录所有试过但失败的绕过方式（如 Alist 签名被检测、预览端点不支持、m3u8 直链不存在）
- 区分"技术可绕过"和"业务不可绕过"的封锁
  - **技术封锁**：签名校验、CSRF token、CF 防护 → 通常可绕过
  - **业务封锁**：付费流量包耗尽、分享过期 → **无法通过技术手段绕过**
- 将测试矩阵文档化：在什么状态下哪个 API 返回什么错误

### 从 OpenList / Alist 提取目标凭据

当目标数据已经在 Alist/OpenList 中配置时，可以直接从 SQLite 数据库提取 token：
```bash
# 列出所有存储
sqlite3 /path/to/data.db "SELECT id, driver, mount_path FROM x_storages;"
# 提取特定存储的 AccessToken
sqlite3 /path/to/data.db "SELECT json_extract(addition, '\$.AccessToken') FROM x_storages WHERE id={id};"
# 提取 123PanShare 配置
sqlite3 /path/to/data.db "SELECT mount_path, json_extract(addition, '\$.AccessToken'), json_extract(addition, '\$.ShareKey') FROM x_storages WHERE driver='123PanShare';"
```

### 付费分享流量模型（通用概念）

某些云盘平台（123pan 等）支持"分享者付费下载"模式。关键概念：

- **分享者流量包（Traffic Pool）**：分享者提前购买下载流量，分享给他人下载时消耗分享者的流量
- **下载者自有流量**：下载者即使有 VIP/流量，也无法用自己的流量下载付费分享的内容
- **业务壁垒**：这是平台计费架构决定的，不是技术限制。没有 API 可以绕过
- **区分方式**：如果带个人 token 仍然返回"流量不足/余额不足"，而文件列表正常返回，说明是分享者侧的流量限制

逆向时 MUST 先判断业务模型：如果是分享者付费型，且分享者流量耗尽，**直接放弃**——没有 API 层面的绕过方案。

### Pitfall: VPS IP 被 403 封锁 — 需TLS指纹或代理

部分 API（如 MiMoCode `api.xiaomimimo.com`）在 chat 层对 VPS/数据中心 IP 段实施封锁 — JWT 认证通过但请求仍返回 `403 Illegal access`。

**识别特征：**
- Bootstrap/认证端点通（200），业务端点（chat）403
- 从家庭宽带/手机流量正常，从 VPS 不通
- 错误 body 含 `Illegal access` / `forbidden`

**解决路径（按效率递减）：**
1. **Cloudflare Worker / 住宅代理中转** — 用住宅IP作为中继
2. **TLS 指纹伪造** — JA3/JA4 握手特征模仿 Chrome/Edge（需要 curl-impersonate 或 utls 库）
3. **移动网络** — 手机热点本机测试 + 抓取请求头
4. **问用户提供** — 让用户从家庭网络抓包提供完整请求特征

### Pitfall: API 签名算法过期 — 旧域名已废弃（sc.o3.hk 七猫小说 — 2026-07-22 更新）

**2026-07-22 状态变更**：上一轮会话（2026-07-21）曾完全破解签名算法并用 `api-bc.wtzw.com`/`api-ks.wtzw.com` 域名成功调用4个端点。本轮再次尝试时，**旧域名已返回 `{"Status":"Unauthorized"}`**——API 已迁移至新域名。

**新域名体系（从 sc.o3.hk main.dart.js 中提取）**：
| 旧域名（已废弃） | 新域名（当前） | 用途 |
|---|---|---|
| `api-bc.wtzw.com` | `api-bc-wtzw.o3.hk` | 搜索 + 下载 |
| `api-ks.wtzw.com` | `api-ks-wtzw.o3.hk` | 详情 + 章节列表 |

**新域名实测状态（2026-07-22）**：
- `api-bc-wtzw.o3.hk/search/v1/words`（GET）→ `{"errors":{"code":"44010102","title":"参数错误"}}` — 端点存活，但参数格式可能变更
- `api-ks-wtzw.o3.hk/api/v4/book/detail`（POST）→ `{"errors":{"code":"44010120","title":"验签失败"}}` — 端点存活，签名算法未知

**已知仍有效的信息**：
- 签名密钥 `d3dGiJc651gSQ8w1` 仍存在于 `sc.o3.hk/main.dart.js` 中
- 错误码 44010120 = 验签失败，44010102 = 参数错误

**上一轮曾成功使用的算法（记录作对比参考，新域名已不适用）**：
```python
# 此算法对旧域名有效，对新域名已失效
def sign(params):
    keys = sorted(params.keys())
    s = "".join(f"{k}={params[k]}" for k in keys) + "d3dGiJc651gSQ8w1"
    return hashlib.md5(s.encode()).hexdigest()
```

**诊断路径（按优先级）**：
1. **下载新 IPA 分析** — 用户确认"IPA是正常的"，应获取最新七猫小说 IPA 提取新签名逻辑
2. **下载新版 main.dart.js** — 新域名 `api-bc-wtzw.o3.hk` 对应的 Flutter JS 可能有完整签名函数
3. **参数对比** — 新旧域名报错不同（参数错误 vs 验签失败），说明参数格式已调整
4. **Frida Hook 真实客户端** — 安装最新版七猫小说 App + Frida 抓签名

### Pitfall: 签名算法暴力破解死胡同（sc.o3.hk 七猫小说 — 2026-07-21）

当签名密钥已知但算法未知时（sc.o3.hk 密钥 `d3dGiJc651gSQ8w1`），**不要暴力枚举 MD5/HMAC 变体**——已测试 15+ 种组合全部失败，是浪费时间。

**失败清单**：`md5(kv&... + secret)` / `md5(secret + kv&...)` / `md5(kv + secret)` / `md5(kv&...)` / `md5(kv_concat + secret)` / `HMAC-MD5` / `HMAC-SHA256` / `md5(json_body + secret)` / `md5(md5(x) + secret)` / 时间戳变体等 → **全部 #44010120 验签失败**

**正确路径**（必须获取真实样本后反推）：
1. **抓包**：Charles/mitmproxy 拦截真实客户端请求，拿 sign 值对比参数
2. **Frida Hook**：Hook 签名函数（如 `vI`），直接 dump 输出
3. **静态分析**：`libapp.so` 原生库中搜索签名函数
4. **多样本对比**：多次请求同一参数，观察 sign 变化规律（时间戳/随机数/设备指纹）

**核心原则**：签名算法如果是标准 MD5 早被试出来了——试了 15+ 种都不对说明是**非标准变换**（自定义字符替换、位移、分段加密等），靠猜永远猜不到。

详见 `references/sc-o3hk-qimao-novel-api-reverse.md`

### Pitfall: 用户说"发了已经"但 agent 说"没收到" — 立即找替代路径（2026-07-22）

当用户说文件已经发送但 agent 未收到时，**不要说"没收到"或让用户重发/粘贴**——这会让用户极度愤怒。

**正确路径**：
1. 用户提供了URL → **直接 curl 下载**，不要等用户再发
2. 用户说"下载发给我" → 立即执行下载 + 发送，不要问问题
3. 下载后通过 Bot API `sendDocument` 发送（token 已配置），不要用 MEDIA 标签

**典型错误**（本会话真实发生）：
- 用户发 GitHub 链接说"下载发给我" → agent 说"没收到文件" → 用户："老子不是发的107.6吗"
- 用户多次发文件 → agent 反复说"没收到" → 用户："草泥马的多大都可以，别怪tg，找找自己的原因"

**铁律**：用户说已经发了 = 用户已经发了。立即用工具获取，而不是让用户证明。

### Pitfall: Docker 部署的 Node.js CLI 在无 X11 下崩溃

某些项目（如 `Sliverkiss/mimocode2api`）依赖 `@mimo-ai/cli` 的 `mimo serve` 命令。该 CLI 在无 X11 / headless 环境下静默退出（exit 0），无日志。

**应对：** 绕过 CLI，直接用 HTTP 请求调用上游 API。本项目中 Docker 是过度封装层。

## 逆向方法论

### 阶段一：协议侦察

```bash
# 1. 捕获关键请求
# - 认证：login / oauth / token refresh
# - 核心业务：conversation / completion / generation
# - 辅助：chat-requirements / sentinel / captcha
```

### 阶段二：指纹伪造（以 ChatGPT 为例）

```python
fingerprint = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Edge/143.0.0.0",
    "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", ...',
    "sec-ch-ua-platform": '"Windows"',
    "oai-device-id": uuid4(),
    "oai-session-id": uuid4(),
    "oai-client-version": "prod-a194cd...",
}
```

### 阶段三：抗爬虫绕过

### 阶段四：核心协议分析

### 阶段五：认证管理

## Chrome DevTools MCP 协议逆向辅助

### 预注入 Hook 探针

```javascript
navigate_page(initScript=`
  const origFetch = window.fetch;
  window.fetch = function() { trace.push(arguments); return origFetch.apply(this, arguments); };
`);
```

### Webpack 模块自动发现

## 数据源追溯（Data Source Tracing）

当目标 API 背后还有多层数据源（DB → 代理 → 上游）时，需要系统性追溯完整数据链。

### 三层追溯法

```
第一层（显示层）:  前端 JS 调用的 API 端点 → 确认请求/响应格式
第二层（中间层）:  API 后端的基础设施 → GitHub Recon / Vercel 识别
第三层（源头层）:  数据来源 → 数据库 / Telegram / 第三方 API
```

### GitHub 作者侦察（Author Reconnaissance）

当 API 的开发者有公开 GitHub 账号时，侦察其仓库可以发现后端基础设施：

**执行步骤：**

1. **识别作者** — 从 API 域名、页面 footer 的版权信息、JS 注释等找到作者名
2. **搜索 GitHub** — `gh repo list <author> --limit 80` 列出所有仓库
3. **关注关键仓库类型**：
   - **DB 代理/API 代理** — 如 `mongodb_altas`（Hono/MongoDB REST 代理，暴露 MongoDB URI 模式）
   - **Telegram Bot 框架** — 如 `telebot`（数据库名可能暗示数据源如 `telegram`）
   - **领域相关工具** — 如 `Provision`（Apple 设备签名，确认作者有 Apple 生态经验）
   - **Next.js 项目** — 直接包含 API Route 源码
4. **提取关键信息**：
   - MongoDB URI 模式：`mongodb+srv://${USER}:${PASS}@<cluster>.mongodb.net/${DB}`
   - 数据库名和集合名（可能在 env 示例中）
   - API 端点结构（Hono/Express 路由定义）
   - Vercel 配置（`vercel.json` 中的环境变量名）

**提示**：用户名通常可从以下位置提取：
- 网站 footer: `© 2026 Sakura` → 搜 `Sakura github`
- API 域名: `sliverkiss-psi.vercel.app` → 搜 `Sliverkiss github`
- CSS/JS 注释中可能包含开发者署名

### Vercel 部署识别

从 API 响应头识别 Vercel 部署：

```http
server: Vercel
x-vercel-id: cle1::vgqmw-1782480885216-113daf04d025
x-vercel-cache: HIT/MISS
```

Vercel 项目名可以从子域名推断：`<project>-<hash>.vercel.app`。

### 数据链重构模式

典型的数据流链条：

```
前端 SPA/静态页
  ↓ fetch/axios（可能需 Origin+Referer）
Next.js API Route（Vercel Serverless）
  ↓ 内部调用
MongoDB/其他 DB 代理（可能是另一个 Vercel 项目）
  ↓ CRUD
数据库（MongoDB Atlas / PostgreSQL / SQLite）
  ↑ 写入
上游数据源（Telegram bot / 爬虫脚本 / 手动录入）
```

### 数据掩码决策边界

遇到客户端无法获取完整数据时，判断掩码在哪个层级：

| 掩码位置 | 是否可以绕过 | 绕过方法 |
|----------|-------------|---------|
| 前端 JS 显示层 | ✅ 可绕过 | Hook `maskEmail()` 函数，或将 API 响应劫持到本地 decode |
| API Route 响应层 | ❌ 不可绕过 | 需要直接查 DB（需要凭据） |
| 数据库层 | ❌ 不可绕过 | 需要更新数据库（不可能从客户端） |

**判断方法**：用 curl 直接请求 API，如果返回的数据仍然掩码，说明掩码在服务端。如果页面显示掩码但 API 返回明文（前端做的脱敏），则来自 JS 显示层。

### ⚠️ 渲染验证优先原则（Render-First Verification）

**致命坑**：发现 API 返回掩码后，直接默认"页面也显示掩码"，然后去折腾 JS 反混淆/查 DB，**结果用户告诉你页面显示的就是明文**。

**真相**：SSR (Server-Side Rendering / Next.js RSC / diy.js) 可能在服务端直接把完整数据嵌进 HTML，或者 JS bundle 有独立的 unmasked 数据源。前端 API 可能仅仅是用于密码 reveal——邮箱数据根本不经过 API。

**必须做的事**：

```
0. ⭐ 先用浏览器打开页面看实际渲染的 DOM
   不要默认 API 返回 = 页面显示
   不要只看 Network 面板就下结论
   SSR 场景下数据可能直接在 HTML/__next_f 里，完全不经过客户端 API
1. curl API → 看返回是否掩码
2. 浏览器打开页面 → 看 DOM 实际显示什么
3. DOM 明文但 API 掩码 → SSR 嵌入了完整数据
4. DOM 也掩码 → 确认掩码在服务端 API Route 层
```

**典型教训（正是本技能来源的案例）**：
- `curl /api/accounts` → 邮箱掩码 → 错误结论："邮箱不可恢复"
- 实际浏览器页面 → 邮箱明文显示（diy.js 有独立的数据获取逻辑）
- 弯路：花了大量时间做 JS 反混淆、枚举 API、搜 GitHub，没先打开页面看一眼

**判定流程图**：

```
API 返回掩码
  ↓
用浏览器看页面 DOM
  ↓
DOM 显示明文 ←── 服务器无浏览器？→ 让用户截图/描述
  ↓
SSR/JS 带完整数据 → 查 __next_f / diy.js / HTML 源码
```

### 多域名校验（Multi-Domain Verification）

同一个站点可能有**多个域名指向不同服务器**——CN 主域名和 EU 备用域名可能完全不同部署：

| 发现 | 含义 |
|------|------|
| `free.338558.xyz → 154.205.155.252` | 国内 VPS + nginx 反代 |
| `xn--ug8h.eu.org → Vercel CDN` | Vercel 部署 |

**为什么重要**：同一个应用部署在两套基础设施上，行为可能完全不同：
- 一个版本可能带邮箱掩码，另一个版本不带
- 一个版本过 nginx/Cloudflare 限速，另一个直连 Vercel
- 部署版本号不同，API 行为不同

**必须做的步骤**：

```
1. ⭐ 确认你从哪个域名/服务器获取的数据
2. 用 dig/host 检查多个域名是否指向同一 IP
   → `dig +short free.338558.xyz xn--ug8h.eu.org`
3. 如果指向不同服务器，逐个测试
4. 如果主域名限速/封 IP，备用域名可能可用
5. 收到用户反馈时，先确认自己测试的是正确域名
   → 用户说某个行为是假的，可能是你测了不同版本
```

**关键洞察**：
- **API 密码 Reveal 端点 + SSR/JS 邮箱渲染**是常见组合：邮箱在 SSR 或 diy.js 阶段直接渲染（完整），密码走独立 API
- 即使 API 加了反爬（Origin+Referer/CF/限速），也要用浏览器验证页面渲染
- 服务器 IP 被限速时，让用户截图是最快方案——不要死磕代码分析
- **用户说页面显示和API返回不一致时，先 DNS 检查再反驳**——你分析的版本可能不是用户用的版本

### 参考案例

- `references/sakura-api-data-chain.md` — 樱花交流会 Sakura 完整数据链追溯案例：jsjiami v7 混淆脱壳 → API 发现 → GitHub 作者侦察 → MongoDB Atlas 代理识别 → 数据链重构
- `references/zxcstxt-paid-wall-case.md` — 知轩藏书 zxcstxt.com 逆向案例：WordPress 付费资源站的付费墙识别清单、"假下载"按钮的HTML特征、放弃爬取的红旗判断标准
- `references/mimocode-free-api-reverse.md` — MiMoCode (小米 MiMo) 免费 API 逆向案例：JWT 认证、代理实现、VPS IP 被 403 的现象记录
- `templates/mimo-proxy.py` — 纯 stdlib MiMo 代理（215行，零依赖），启动 OpenAI 兼容服务

### 引用
- Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp/
- PicSeed API 案例: references/picseed-api-reverse.md
- Apple App Store AMP API: references/apple-app-store-amp-api.md
- Next.js Server Action next-action hash 自动发现: references/nextjs-server-action-discovery.md
- 123Pan Share API 协议逆向: references/123pan-share-api-reverse.md
- 3.44v.top 祝福卡片平台逆向（微信小程序生态、77+模板系统、纯前端密码、免鉴权 API 直创建片）: references/greeting-card-platform-reverse.md
- Parse Server API 发现（POST body 认证模式 + Playwright 拦截提取）: references/parse-server-api-discovery.md
- Starline 番茄小说下载服务（异步任务队列 + 307 重定向链 + HTML 状态页无 JSON API）: references/starline-novel-download-reverse.md
- sc.o3.hk 七猫小说 API 逆向（Flutter JS 编译 + 签名密钥已知/算法未知 + 15+ 变体全失败清单）: references/sc-o3hk-qimao-novel-api-reverse.md

---

## web-api-reverse-engineering

# Web API 逆向工程

系统性逆向分析 Web 应用的后端 API——从前端代码反编译、网络请求探测到协议文档输出。

## 技能分工

本技能是 JS 逆向领域的**API 协议层**，只负责协议格式逆向和兼容代理构建。

| 你需要的 | 应该用 |
|---------|--------|
| API 端点发现、请求/响应格式提取、协议兼容对比、OpenAI 代理构建 | → **本技能** (web-api-reverse-engineering) |
| 完整逆向工作流（Observe→Patch→PureExtraction→Port）、补环境、纯算法提纯 | → **js-reverse-engineering** |
| CDP 断点、单步追踪、callFrame 求值、反调试 | → **cdp-debug-reverse** |

**协作模式**：本技能的 Step 2（前端 JS 分析）可引用 cdp-debug-reverse 做源码搜索；如果分析发现 API 需要签名参数，转交 js-reverse-engineering 处理签名逻辑的逆向。

## When to use

- 用户提供网站 URL，要求逆向分析其 API 接口
- 需要研究某个 Web 应用的 API 是否兼容特定协议（如 OpenAI Chat Completions）
- 需要从前端 JS 代码中提取 API 端点、请求格式、认证方式
- 需要构建 API 兼容代理（将私有协议转换为标准协议）
- 微信小程序 wxapkg 认证/登录流程逆向（token 机制、替代登录路径、续期逻辑）
- 目标站点使用 Next.js SSR（RSC 流式渲染），需要解析服务端渲染的 HTML 中的 API 数据

Nuxt.js SSR 站点 API 逆向方法论](references/nextjs-ssr-api-reversal.md)  \n- Nuxt 3 加密 Payload 绕过（XChaCha20-Poly1305）](references/nuxt3-encrypted-payload-bypass-tingyoufm.md)  \n- Next.js App Router (Turbopack) RSC 纯 SSR 站点逆向](references/nextjs-app-router-rsc-reversal.md)  \n- Venera 漫画源域名维护与修复](references/venera-source-maintenance.md)  \n- PicSeed 社交解析 API 逆向案例](references/picseed-api-reverse.md)

## GraphQL API 逆向（Introspection 关闭）

当目标使用 GraphQL 且 introspection 关闭（`{__schema{types{name}}}` 返回 `FieldUndefined`），只能从前端 JS 源码提取查询结构。

### 提取方法

1. **下载前端 JS bundle** — SPA 的 JS 在 HTML 的 `<script src>` 中
2. **搜索 `gql` 标签模板** — 搜 `gql\`` 字符串模板内容
3. **搜索 `fragment`/`query`/`mutation` 定义** — webpack 打包后这些关键词在字符串常量中保留
4. **提取 Apollo Document 对象** — 搜 `kind:"Document"` 或 `operation:` + `name:{value:"Xxx"}`
5. **从 mangle 后的代码恢复** — 搜属性名 `operation`、`name`、`value`、`definitions`、`selectionSet`
6. **提取片段结构** — `fragment Xxx on Yyy { fields }` 可反推 type 定义
7. **搜索 `__typename`** 和 union/interface 类型声明 — 搜 union 定义字符串

### 关键搜索模式

```python
import re
with open('bundle.js') as f:
    js = f.read()

# 提取所有片段
for m in re.findall(r'fragment\s+(\w+)\s+on\s+(\w+)\s*\{([^}]+)', js):
    print(f'Frag {m[0]} on {m[1]}: {m[2][:80]}')

# 提取所有操作
for m in re.finditer(r'(query|mutation)\s+(\w+)\s*\(([^)]*)\)\s*\{', js):
    print(f'{m.group(1)} {m.group(2)}({m.group(3)[:100]})')

# 提取 serverUrl/apiUrl (从配置字符串)
for m in re.findall(r'serverUrl[^;]*', js):
    print('URL config:', m[:200])

# 提取 Apollo typePolicies (查询的关键参数)
for m in re.findall(r'typePolicies[^}]+}', js):
    print('TypePolicies:', m[:500])
```

### 已知来源
- `references/appraven-graphql-api-reverse.md` — AppRaven 完整 GraphQL 逆向案例（含所有查询、fragment、PriceTier 映射、活动枚举、Python 请求示例、App Store 链接格式、实际数据快照）
- `references/appraven-wechat-push.md` — AppRaven 数据 → 微信公众号/WxPusher 推送集成：公众号基础信息、WxPusher API、自建 HTML 页面、IP 白名单、定时更新 cron、Python 代码片段
  - 推荐考察：这是标准的「API 逆向 → 数据整合 → 渠道分发」端到端参考。

### Pitfalls 补充

1. **`app.id` ≠ `app.ITunesId`** — AppRaven 内部 ID 和 Apple App Store ID 是不同的。推送到 App Store 必须用 `ITunesId`。这个坑在对接到公众号/推送时尤其重要。
2. **Artwork URL 含模板占位符** — `{w}x{h}{c}.{f}` 必须替换为实际值（如 `512x512bb.png`）才能显示图片。
3. **PriceTier 202+ 不是标准 App Store 价格** — 这些大数值表示内购优惠码或订阅优惠，不能直接用 tier 映射表。
4. **sponsored=true 表示推广内容** — 这些 sponsored deal 是付费推广不是真正的限免，展示时建议标注。

## FastAPI OpenAPI Spec Discovery（黄金捷径）

当目标站点基于 FastAPI / OpenAPI 框架时，**最终API规范文件暴露了全部端点、参数schema和响应格式**——比分析JS bundle快10倍。

### 识别特征

- 后端框架是 FastAPI（Python）
- 页面HTML中有 FastAPI 风格特征（如 `uvicorn` server头）
- 常见规范文件路径：`/openapi.json`、`/docs`、`/redoc`

### 探测流程

```bash
# Step 1: 探测规范文件
for path in /openapi.json /docs /redoc /api/openapi.json /api/docs; do
  code=$(curl -sS -o /dev/null -w "%{http_code}" "https://target.com${path}")
  echo "${path} -> ${code}"
done

# Step 2: 提取完整API规范
curl -sL "https://target.com/openapi.json" | python3 -m json.tool
```

### 从规范中提取的关键信息

1. **所有端点路径** — `paths` 字典的 keys
2. **HTTP方法** — 每个 path 下的 `get`/`post`/`put`/`delete`
3. **参数位置** — `path`/`query`/`header`/`cookie` + schema.type
4. **请求体格式** — `content.application/json.schema`
5. **响应格式** — `responses.200.content.application/json.schema`
6. **认证方式** — `securitySchemes`（Bearer/Cookie/API Key）
7. **字段约束** — `pattern`（正则）、`minLength`、`maxLength`、`enum`

### 实测验证（从规范到curl）

```bash
# 从规范中直接构造测试请求
curl -sS -X POST "https://target.com/tasks" \
  -H "Content-Type: application/json" \
  -d '{"book_id":"123456"}'

curl -sS "https://target.com/tasks/{task_id}"
```

### ⚠️ 规范不完整的情况

- 很多站点关闭 `/docs` 但忘记关闭 `/openapi.json`（低级错误）
- 有些站点只暴露了公开端点，内部API不在规范中
- 规范可能与实际行为不一致（字段名、必填项），需实测验证

### Pitfall

1. **规范是生成时的快照** — 不代表运行时行为。字段名需实测，schema中 `required` 可能过期
2. **动态参数命名** — 如 `book_id` vs `id` vs `novel_id`，规范中路径参数名可能与实际不符
3. **认证在规范外** — 有些API实际需要Cookie/Token但规范中未声明 `security`

## 完整工作流

### Step 1: 前端页面结构探测

用 Lightpanda MCP 工具快速探测目标网站：

```
1. goto(url, waitUntil="networkidle")
2. semantic_tree(maxDepth=5) — 页面结构
3. structuredData() — JSON-LD / OpenGraph 元数据
4. links() — 外部链接
5. evaluate(JS) — 提取 script 标签、全局变量
```

**关键提取项**：
- 所有 `<script src>` URL（前端 JS chunk 列表）
- inline script 中的配置/初始化代码
- meta 标签中的描述、关联域名
- 页面错误信息（如客户端渲染失败）

### Step 2: 下载并分析前端 JS

```bash
# 下载所有 JS chunk
for chunk in <chunk_list>; do
  curl -sL "https://<domain>/_next/static/chunks/${chunk}.js" -o "chunk-${chunk}.js"
done
```

**分析技巧**：
- 用 `tr ';' '\n'` 或 `tr ',' '\n'` 拆分超长单行代码
- 用 `grep -iE` 搜索关键词：`api`, `fetch`, `model`, `chat`, `stream`, `token`, `auth`
- 注意 macOS 的 `grep` 不支持 `-P`（Perl 正则），用 `-E` 替代
- Vercel AI SDK 项目搜索 `vercel.ai.error`、`useChat`、`sendMessage`、`transport`、`streamProtocol`
- React/Next.js 项目搜索 `__next_f`、`webpackChunk_N_E`、`ClientPageRoot`

**常见前端框架识别**：

| 框架 | 特征标记 |
|------|---------|
| Next.js | `__next_f`、`/_next/static/chunks/`、`webpackChunk_N_E` |
| Vercel AI SDK | `vercel.ai.error`、`useChat`、`transport: new K({api:...})` |
| Nuxt.js | `__NUXT__`、`/_nuxt/` |
| Vite + React | `@vite/client`、`/assets/` |

### Step 3: 提取 API 协议

从前端代码中提取核心 API 信息：

1. **端点 URL**：搜索 `api:`, `url:`, `endpoint:`, `fetch(` 等模式
2. **请求格式**：搜索 `body:`, `JSON.stringify`, `method: "POST"` 等
3. **消息格式**：搜索 `role`, `content`, `parts`, `messages` 等
4. **认证方式**：搜索 `Authorization`, `Bearer`, `Cookie`, `x-api-key`, token 相关
5. **流式协议**：搜索 `stream`, `SSE`, `event-stream`, `onChunk`, `delta` 等
6. **模型列表**：搜索 `model`, `value:`, 选择器选项数组

**Vercel AI SDK 特殊处理**：

Vercel AI SDK 的 `useChat` 使用自定义 transport 类，核心格式：

```javascript
// 请求
POST /api/chat
Headers: { "Content-Type": "application/json", "x-ai-sdk-chat-version": "1" }
Body: {
  id: "session-id",
  messages: [{ id: "msg-id", role: "user", parts: [{ type: "text", text: "..." }] }],
  trigger: "submit-message",
  messageId: "msg-id",
  model: "model-id",
  ...extraBodyFields
}

// 响应（SSE 流）
data: {"type":"start","messageId":"..."}
data: {"type":"start-step"}
data: {"type":"text-delta","id":"...","delta":"文本片段"}
data: {"type":"reasoning-delta","id":"...","delta":"思考片段"}
data: {"type":"source-url","sourceId":"...","url":"...","title":"..."}
data: {"type":"finish-step"}
data: {"type":"finish","messageId":"..."}
```

### Step 4: API 实测验证

用 curl 实际调用 API，验证分析结果：

```bash
# 基础请求测试
curl -s '<api_url>' \
  -H 'Content-Type: application/json' \
  -H 'x-ai-sdk-chat-version: 1' \
  -d '<request_body>'

# 流式响应测试
curl -sN '<api_url>' \
  -H 'Content-Type: application/json' \
  -d '<request_body>' | head -50
```

**测试矩阵**：
- ✅ 最小有效请求
- ✅ 不同模型参数
- ✅ 流式 vs 非流式
- ✅ 多轮对话（messages 数组多条）
- ✅ 错误请求（缺失字段、无效模型）
- ✅ 认证需求（无 auth vs 需要 auth）
- ✅ 速率限制行为

### Step 5: 协议对比与兼容性分析

如果目标是构建兼容代理（如 OpenAI 兼容），做详细对比：

**请求格式对比维度**：

| 维度 | OpenAI 格式 | 目标格式 | 转换难度 |
|------|------------|---------|---------|
| 端点路径 | `/v1/chat/completions` | ? | - |
| messages 格式 | `content: string` | ? | - |
| 流式协议 | `data: {"choices":[{"delta":{}}]}` | ? | - |
| 认证方式 | `Authorization: Bearer <key>` | ? | - |
| model 参数 | `gpt-4o` 等 | ? | - |
| 特殊参数 | `temperature`, `max_tokens` | ? | - |

**响应格式对比维度**：

| 维度 | OpenAI 格式 | 目标格式 | 转换策略 |
|------|------------|---------|---------|
| 内容增量 | `choices[0].delta.content` | ? | - |
| 思考/推理 | 无标准 | ? | - |
| 来源引用 | 无标准 | ? | - |
| 结束标记 | `finish_reason: "stop"` | ? | - |
| 用量统计 | `usage.prompt_tokens` 等 | ? | - |

### Step 6: 保存逆向成果到知识库

**所有逆向成果必须持久化保存**，方便后续复用和 AI 代理索引。

**目录结构**：`<工作目录>/web-reverse/<网站名>/`

```
web-reverse/
└── <网站名>/
    ├── knowledge-base.md      # LLM 可索引的结构化知识库（必须）
    ├── <site>-page.js         # 原始前端 JS chunk
    ├── <site>-layout.js       # 其他原始文件...
    └── ...
```

**knowledge-base.md 必须包含**：
1. 网站概述（URL、技术栈、功能定位）
2. API 端点（URL、Method、Headers、请求体、响应格式）
3. 请求参数说明（字段名、类型、默认值、说明）
4. 可用模型列表（显示名、内部 ID、推理服务商）
5. SSE 事件类型（type、字段映射）
6. 认证方式（API Key / Cookie / OAuth / 无认证）
7. 特殊处理逻辑（广告过滤、格式差异、已知陷阱）
8. 上游特有参数（翻译、搜索、方言等扩展字段）

**同时保存原始文件**：前端 JS chunk、HAR 抓包文件、curl 测试记录等，供后续深入分析。

### Step 7: 写分析报告并委派实现

将完整分析写入 `/tmp/codebuddy-tasks/ref.md`，包含：
1. 执行摘要（结论先行）
2. API 协议详细对比
3. 转换层设计（请求转换 + 响应转换）
4. 边界情况处理策略
5. 风险评估
6. 可行性结论
7. 概念代码（如可行）

然后委派 CodeBuddy 后台执行实现：

```
terminal(
  command="codebuddy -p -y '<任务描述，引用 /tmp/codebuddy-tasks/ref.md>'",
  workdir="<项目路径>",
  background=true,
  notify_on_complete=true,
  timeout=600
)
```

## 加密API协议逆向（AES-ECB + 时间戳签名 — JMComic 模式）

当目标站点的API请求和响应body都是AES-ECB密文 + MD5时间戳签名认证时（如禁漫天堂JMComic移动端API），使用以下完整工作流。

### 识别特征

- 响应body是Base64密文（AES-ECB加密后的数据），嵌套在 `{"data": "base64..."}` 中
- 请求头含 `token`（MD5哈希值）和 `tokenparam`（时间戳+版本号）
- 前端`get()`方法：取时间戳 → 算token → 请求 → 响应 `data` 字段是Base64密文 → AES-ECB解密 → JSON解析
- 密钥硬编码在前端JS中（如 `"18comicAPPContent"` 和 `"185Hcomic3PAPP7R"`）
- App版本号也在前端JS中（如 `"2.0.24"`）

### 加密机制详解（JMComic案例）

```
Token生成:
  token = MD5(hex)(时间戳 + "18comicAPPContent")
  tokenparam = "时间戳,APP版本号"

HTTP响应解密:
  key = MD5(hex)(时间戳 + "185Hcomic3PAPP7R")  → 转UTF-8 bytes
  encrypted = base64_decode(response.data)
  decrypted = AES_ECB_decrypt(encrypted, key)   → 去掉PKCS7 padding
  JSON.parse(decrypted)
```

**密钥来源**：通过 pip 安装 `jmcomic` Python包，查看 `JmMagicConstants` 类。

### 完整工作流：API逆向→Python Proxy→Legado书源

最实用的方案是**在服务器上起一个Python PyCC中转服务**，负责AES解密，让Legado/栖阅客户端直接请求解密后的JSON。原因是Legado的JS环境没有原生AES支持（缺少 `Crypto` / `crypto-js` 等库）。

#### Step 1: 逆向API端点

用 `jmcomic` Python包验证所有接口：

```python
from jmcomic import JmOption
option = JmOption.default()
client = option.new_jm_client()

# 自动获取最新域名和版本号
# domains: ['www.cdnhjk.net', 'www.cdngwc.cc', ...]
# version: 2.0.24
```

**关键API端点**（JMComic移动端）：

| 端点 | 参数 | 说明 |
|------|------|------|
| `/search` | `search_query`, `page`, `main_tag`, `o`, `t` | 搜索漫画 |
| `/album` | `id` | 漫画详情（含series章节列表、tags、author） |
| `/chapter` | `id` | 章节图片列表（`images`数组，图片文件名） |
| `/categories/filter` | `c`, `o`, `page` | 分类浏览 |
| `/setting` | 无 | 获取最新配置 |

**图片URL构造**：
```
https://cdn-msp.jmapinodeudzn.net/media/photos/{ep_id}/{image_filename}
https://cdn-msp.jmapinodeudzn.net/media/albums/{album_id}_3x4.jpg  # 封面
```

#### Step 2: Python Proxy 实现（Flask）

核心解密函数：
```python
def decrypt(data, ts):
    data_b64 = base64.b64decode(data)
    key = md5(f'{ts}{DATA_SECRET}'.encode('utf-8')).hexdigest().encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(data_b64)
    pad_len = decrypted[-1]
    return json.loads(decrypted[:-pad_len].decode('utf-8'))
```

**Flask路由设计**（运行在 `0.0.0.0:5200`）：
- `/jm/search?key=xxx&page=1` → 搜索
- `/jm/detail?book_id=xxx` → 详情+目录合并（chapters数组）
- `/jm/chapter?item_id=xxx` → 章节图片HTML
- `/jm/discover?category=xxx&o=mr&page=1` → 分类浏览

#### Step 3: Legado 书源配置


---
*[Content truncated: 1228 lines total]*
---

    - 实际解析可能另有独立的带认证解析 API（如 `/v1/parser`），CDN 代理仅用于图片/视频下载

35. **独立 iOS App 的无后端评估** — 当目标 iOS App 由独立开发者开发且数据存本地时：
    - 检查隐私政策和应用描述中是否声明"数据存储在本地设备"——如果是，通常没有自建后端
    - iCloud 同步通过 Apple NSPersistentCloudKitContainer，不可抓包修改
    - 付费验证走纯 StoreKit 2，无服务器收据验证
    - **"无服务器架构"的 App 所有内容解析都在设备端完成**（WebView JS注入），唯一的远程调用是 StoreKit 验证和第三方内容代理（如 fxtwitter）
    - 如果 `strings` 二进制后 grep 外部 URL 结果很少（<20个），且都是知名服务（apple.com、googleapis.com、fxtwitter.com 等），则该 App 是纯本地解析器

    **辨别方法**: `strings binary | grep -iE "https?://[^\"'\`]+(com|net|org|io|app)" | grep -v apple | grep -v google | grep -v akamai | grep -v cloudflare` — 如果结果只有知名第三方服务域名，无自建 API，即为无服务器架构

    **典型案例 (Procut)**: 逆向该 IPA 后发现它是纯本地解析器：
    - 所有多平台（小红书、抖音、微博、Twitter 等）内容解析均通过 WebView JS 注入在设备端完成
    - 唯一远程 API: StoreKit `verifyReceipt` (Apple) 和 `api.fxtwitter.com` (Twitter 视频代理)
    - `__INITIAL_STATE__` / `__NUXT__` 等 SSR 数据在前端提取 → 水印是客户端叠加，CDN 原图无水印
    - 此类 App 无法通过抓包/MITM 获取"API 接口"——根本没有独立后端 API

    **应对策略**：如果 `host` 被设为 `hidden.example.com`：
    - **VLESS Reality 节点**：从 `tls_settings` 提取 `public_key`（Reality public key）、`short_id`、`server_port`（默认 443）、`server_name`（伪装 SNI），结合 `flow: xtls-rprx-vision`，可以构造标准 VLESS Reality 链接。`hidden.example.com` 不影响 Reality 连接（Reality 不需要真实 IP）。
    - **Trojan/Hysteria 节点**：真实地址只通过订阅链接下发，`fetch` API 不暴露。`hidden.example.com` 是数据库层面的保护（V2Board ServerTrojan 模型直接返回 `$server['host']`），不是 API 的掩码层。
    - **订阅链接**：V2Board 的 `isAvailable()` 检查不可绕过。立即报告结果给用户，不要花时间试图从 fetch 响应中提取节点 IP。
    - **VLESS vs trojan 区别关键**：VLESS 节点的 `tls_settings` 包含 Reality 配置（public_key + short_id），不需要真实 host 就能连；trojan/hysteria 需要真实 IP，`tls_settings` 不包含 IP 信息。
    - **SSRDOG 的 `user/server/fetch` 在过期账号下仍返回节点数据** — 和标准 V2Board 不同，SSRDOG 魔改版不检查 `isAvailable()`。但标准 subscribe 端点严格执行。fetch 有数据但订阅为空 = 套餐过期。

32. **SSRDOG/Mala-Pro 面板的响应体加密** — 所有 API 响应经过 10 层自定义字符映射表编码（非标准 base64）。映射表为两组 68 字符的 base64 解码结果。前端 axios 的 `validateStatus: () => true` 配置意味着所有 HTTP 状态码都走 `.then` 分支，不会 reject。这影响了请求重试和错误处理逻辑。

    **解密实现**：在 `v2board-ssrdog-reverse.md` 参考文件中有完整的 Python 解密代码。

33. **VLESS Reality 节点从 `tls_settings` 构造方法**：
    - `server_name`（`tls_settings` 中）= 伪装 SNI 域名（如 `d1.awsstatic.com`）
    - `public_key`（`tls_settings` 中）= Reality public key（Base64 编码）
    - `short_id`（`tls_settings` 中）= Reality short ID
    - `server_port`（`tls_settings` 中）= 目标端口（通常 443）
    - `flow` = `xtls-rprx-vision`
    - `host` = `hidden.example.com`（没问题，Reality 不用 host）
    - `uuid` = 用户 UUID（从 `user/info` 获取）
    - 标准 VLESS Reality 链接格式：`vless://UUID@hidden.example.com:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=SERVER_NAME&fp=chrome&pbk=PUBLIC_KEY&sid=SHORT_ID&type=tcp&headerType=none#NODE_NAME`
    - **注意**：日本 VLESS 节点中，只有子节点（有 `parent_id`）才包含完整的 Reality 配置（public_key + short_id），父节点可能只含基础 tls 配置（无 Reality 参数）。

## 微信小程序认证逆向

当目标是微信小程序（wxapkg）时，使用专门的工作流：解包→定位认证模块→分析登录流程→提取替代登录路径→Token 续期分析。

**两种框架模式**：

| 框架 | 文件结构 | 认证定位方法 | 参考案例 |
|------|---------|-------------|---------|
| 原生小程序 | `app-service.js` 单文件 | 搜索 token/cookie 名称 | 唯品会（references/wechat-miniprogram-auth-reverse.md） |
| Taro/uni-app | `app.js` + `common.js` + `vendors.js` | 搜索 `DI.login.` 容器标识 | 万家乐（references/wanjiade-taro-miniprogram-auth.md） |

详见 **references/wechat-miniprogram-auth-reverse.md** — 覆盖 wxapkg 解包、认证模块定位、多登录路径发现（wx.login / 手机号短信 / 密码）、Token 续期机制分析、Cookie/Storage 结构提取。含唯品会小程序完整案例。

**Taro 框架小程序**需用不同的定位策略（DI 容器 + webpack 分包）：详见 **references/wanjiade-taro-miniprogram-auth.md** — 双层认证架构（sessionId Cookie + CSP Token）、DI 依赖注入模式（`DI.login.*`）、401 自动重登机制、**服务端 getCode 接口续期（无需 wx.login）**、Taro 特有的文件结构。含万家乐会员俱乐部小程序完整案例。

**触发词**：小程序、wxapkg、小程序登录、小程序 token、小程序认证、mini-program auth、Taro 小程序、sessionId、cspLoginInfo

35. **Playwright Proxy 冷启动慢（~30秒）** — 基于 Playwright 的解密代理脚本（如 Nuxt 加密站点的 proxy）通常在 `init()` 中启动浏览器 + 导航页面后才 `server.listen()`。cron 检查时不能 `sleep 2` 就检查端口——必须轮询等待。详见 `references/nuxt3-encrypted-payload-bypass-tingyoufm.md` 的「Playwright Proxy 部署运维」节
36. **V2Board / SSRDOG 面板逆向

V2Board 是一套开源的机场管理面板（SSRDOG 是商业版），使用 Laravel 后端 + Vite/Vue3 前端。以下是完整的逆向方法。

### 识别特征

- 前端页面有登录页、仪表盘、节点地图、订阅配置等功能
- 使用 `passport/auth/login`、`user/server/fetch`、`user/getSubscribe` 等 V2Board 标准 API
- 前端使用 Vuetify 组件库（`v-btn`、`v-card` 等）
- JS 中有 `window.APP_CONFIG` 配置对象
- 通常部署在 `love.*.com` 或 `www.*.cc` 格式域名

### API 端点发现

1. **下载所有 JS chunk** — SPA 的 JS 通过 `<link rel="modulepreload">` 和 `<script type="module">` 加载
2. **搜索 `axios.create`、`e.create` 或 `baseURL`** — 定位 API base URL 和 axios 实例
3. **典型的 V2Board API 配置**：
   ```javascript
   const api = axios.create({
     baseURL: (localStorage.getItem("api_base_url") || "https://api123.example.xyz")
       .replace(/\/+$/, "") + "/api/v1",
     timeout: 10000,
     validateStatus: function(e) { return true; }
   });
   ```
4. **API base URL 可被 `localStorage` 覆盖** — `localStorage.setItem("api_base_url", "...")` 可动态修改

### 响应解密算法

V2Board/SSRDOG 对 API 响应做了 10 层映射表加密：

```python
import base64, json

# 固定的映射表（base64解码后的68字符字符串）
s = base64.b64decode("bnN6e2dBV3JrWGx4MDhKNkVx...").decode()
t = base64.b64decode("YWJjZGVmZ2hpamtsbW5vcHFy...").decode()

def r(e):
    return "".join(t[s.index(ch)] if ch in s else ch for ch in e)

def decode_response(text):
    a = base64.b64decode(text).decode()
    for i in range(10):
        a = r(a)
    return json.loads(a)
```

### CF WAF 绕过

SSRDOG 面板通常在 Cloudflare 后。关键发现：**添加 `theme-ua: mala-pro` 请求头后 CF 放行**。这是前端 JS 的 axios 拦截器自动添加的请求头，CF WAF 识别后认为是正常浏览器请求。

```python
headers = {
    "User-Agent": "Mozilla/5.0",
    "theme-ua": "mala-pro",  # 关键！CF WAF 绕过
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://love.example.cc",
    "Referer": "https://love.example.cc/",
}
```

### 完整 API 调用链

#### 1. 登录（FormData 格式）

```python
login_data = {"email": "xxx@example.com", "password": "xxx"}
resp = session.post(f"{API_BASE}/passport/auth/login", data=login_data, headers=headers)
decoded = decode_response(resp.text)
# decoded = { "data": { "token": "...", "auth_data": "JWT_TOKEN" } }
```

**注意**：登录请求使用 `FormData`（`Content-Type: multipart/form-data`）而非 JSON。

#### 2. 认证后的请求

```python
auth_headers = headers.copy()
auth_headers["Authorization"] = auth_data  # JWT token
# 后续所有请求带此 header
```

#### 3. 关键 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/passport/auth/login` | POST | 登录（FormData: email + password） |
| `/user/info` | GET | 用户信息（邮箱、余额、到期时间、UUID） |
| `/user/getSubscribe` | GET | 订阅信息（套餐、流量、订阅URL） |
| `/user/server/fetch` | GET | 服务器/节点列表（类型、SNI、速率等） |
| `/guest/comm/config` | GET | 公共配置（验证码、支付方式） |
| `/user/comm/config` | GET | 用户配置（Telegram、提现方式） |
| `/user/plan/fetch` | GET | 套餐列表 |
| `/user/order/fetch` | GET | 订单列表 |
| `/user/server/fetch?all=1` | GET | 完整服务器列表（包含隐藏节点） |

#### 4. 节点配置注意事项

- V2Board 的 `user/server/fetch` 返回的 `host` 字段可能是 `hidden.example.com`（配置保护）
- 真正的节点地址通过**订阅链接**下发（`user/getSubscribe` 返回的 `subscribe_url`）
- 订阅链接使用标准格式：`https://DOMAIN/api/v1/client/subscribe?token=TOKEN`
- 订阅链接返回的数据经过 base64 编码（标准 Clash/v2ray 格式）
- **订阅链接返回空（content-length: 0）的根因通常是套餐过期** — V2Board 的 `isAvailable()` 检查 `expired_at > time()`。用 `user/getSubscribe` 获取的 `expired_at` 时间戳与当前时间对比确认。SSRDOG 魔改版对 `user/server/fetch` 不检查可用性（仍返回节点元数据），但标准的 `/client/subscribe` 严格执行 `isAvailable()`。fetch 有数据 + 订阅空 = 套餐过期
- **VLESS Reality 节点例外**：即使 host 被隐藏，从 `tls_settings` 提取 public_key、short_id、server_name 可以构造标准 VLESS Reality 链接（Reality 不需要真实 host）

### Pitfalls

1. **`theme-ua: mala-pro` 是关键** — 没有此 header，所有请求被 CF 拦截返回 403
2. **邮箱白名单（SSRDOG特有）** — 从 `/guest/comm/config` 发现邮箱后缀白名单（qq.com, gmail.com等）。非白名单邮箱返回 422「邮箱格式不正确」。调用登录前先确认邮箱后缀在白名单内
3. **登录用 FormData 不是 JSON** — 使用 `data=` 参数（`requests`）而非 `json=`
4. **响应 interceptor 是 10 层映射表** — 不是简单的 base64
5. **节点配置可能隐藏** — 实际地址只通过订阅链接下发，API 返回 `hidden.example.com`
6. **订阅链接空响应的真正原因：套餐过期** — V2Board 的 `isAvailable()` 检查 `expired_at > time()`，如果过期则 subscribe 返回 content-length: 0，但 `user/server/fetch` 可能仍返回节点元数据（SSRDOG 魔改版行为）。**先检查 `expired_at`** 确认套餐是否有效，不要死磕订阅链接\n6. **`user/server/fetch` 返回的 host 可能全是 `hidden.example.com`** — 这是管理员的配置保护机制，不是标准 V2Board 行为。即使 fetch 返回节点列表，实际地址仍只通过订阅下发。**不要浪费时间试图从 fetch 响应中提取节点 IP**\n7. **遇到死路先查已有工具库** — 用户有 36+ 个逆向技能在私有 Gist，有 Nexus 仓库含多工具集。在尝试新逆向方法前，先检查已有技能和工具是否覆盖了当前问题。不要重复发明轮子\n8. **`validateStatus: function(e) { return true; }`** — axios 配置了不按状态码 reject，所以 400/500 也会进入 `.then`\n\n### 参考案例\n\n- **宝可梦加速器/52Pokemon**（本会话）：V2Board 标准面板，42个节点（trojan/hysteria/vless），入门精灵球套餐60G/月。关键发现：`theme-ua: mala-pro` 绕过 CF WAF、10层映射表解密、订阅空响应的根本原因是套餐过期而非API问题

## 案例参考

- **references/v2board-ssrdog-reverse.md** — V2Board / SSRDOG 机场面板逆向完整参考：10层映射表解密、CF WAF 绕过（`theme-ua: mala-pro`）、FormData 登录、节点分类、订阅链接提取。基于宝可梦加速器（52Pokemon）案例
- **references/aes-encrypted-vpn-node-extraction.md** — AES-256-CBC 加密 VPN 节点提取：OSS 动态 API 发现、端到端 AES 加解密、免注册登录、node_list 提取。基于 Traveler VPN 案例
- **references/json-api-vpn-anonymous-registration.md** — 纯 JSON API 免付费匿名注册 VPN 节点提取：随机 UUID 注册→自动送试用→拉取节点列表。基于拉条云 (latiaoyun.org) 案例，24 个 hysteria2 节点。✅ 已实战验证（2026-06-06，Python 脚本全自动跑通，24 节点全部提取成功）
- **references/mergeek-polling-ai-search.md** — Mergeek AI 搜索逆向案例：轮询式 AI 搜索（POST 发起 + GET 轮询），非 SSE/WS 模式。包含 7 个 API 端点、认证机制、对话上下文、CDN 下载技巧
- **references/wechat-miniprogram-auth-reverse.md** — 微信小程序认证体系逆向：wxapkg 解包→认证模块定位→多登录路径发现→Token 续期分析（唯品会案例）
- **references/wanjiade-taro-miniprogram-auth.md** — Taro 框架小程序认证逆向：DI 容器定位→双层 sessionId/CSP Token→401 自动重登→全量 API 端点（万家乐案例）

- `templates/anonymous-registration-vpn-extract.py` — 匿名注册→拉节点通用模板。修改 API_BASE、headers、注册 payload、节点格式即可适配其他机场
- `references/appraven-graphql-api-reverse.md` — AppRaven GraphQL 逆向案例：从 JS bundle 提取 query/mutation（introspection 关闭）、PriceTier 映射、请求示例，可复用模式

### 案例参考

- `references/procut-no-server-architecture.md` — Procut IPA 逆向：无服务器架构识别、WebView JS注入、`initState=null` 诊断
- `references/kuwo-music-upgrade-api-reverse.md` — 酷我音乐 App 升级系统接口逆向：HAR 包分析、新旧两套任务系统（积分 vs 成长值）、全部 API 端点文档、等级对照表。含 Quantumult X HAR 包分析要点和 Python 分析脚本模式。

## 工具箱

| 工具 | 用途 |
|------|------|
| Lightpanda MCP (`mcp_lightpanda_markdown`) | 页面文本提取、结构化数据 |
| Lightpanda MCP (`mcp_lightpanda_eval`) | JS 执行、DOM 数据提取、函数体提取 |
| Lightpanda MCP (`mcp_lightpanda_structuredData`) | JSON-LD / OpenGraph 元数据 |
| curl (terminal) | API 实测验证（Lightpanda 内 fetch 受 CORS 限制，必须用 curl） |
| `tr` + `grep` | minified JS 拆分搜索 |
| OpenClaw (后台) | 长分析任务（注意 content_filter 可能阻断敏感任务） |
| `strings` 命令 | 从二进制/压缩文件提取可读字符串 |

---

## web-tool-reverse-engineer

# Web Tool Reverse Engineer — Web 在线工具逆向

## 适用场景

- 目标是一个在线工具集合（如 tools.miku.ac、在线转换工具站）
- 需要批量提取每个工具的实现逻辑
- 目标是本地复用/离线化/集成到自有系统
- 前端 SPA + 后端 API 的工具站架构

## 总览

```
┌── 任务定义 ──────────────────────────────┐
│  逆向 tools.miku.ac 等在线工具站           │
│  收集所有工具的实现方法                     │
│  按工具创建子文件夹                         │
│  每个子文件夹放:                            │
│    ├── README.md    ← 工具描述 + 图标链接  │
│    └── implement/   ← 实现代码 + 逻辑文档  │
└──────────────────────────────────────────┘
```

## 逆向方法论

### 阶段一：全站侦察

```bash
# 1. 先尝试工具列表 API（Nuxt/Next.js 常用）
# 很多工具站有隐藏的 /api/tools 端点
curl -sL --compressed 'https://target.com/api/tools' \
  -H 'User-Agent: Mozilla/5.0' \
  -H 'Accept: application/json'

# 2. 如果 API 可用，直接拿到完整工具列表（无需爬 HTML）
# tools.miku.ac 的 /api/tools 返回:
# { "success": true, "data": { "tools": [{ "slug": "...", "usage_count": N, "status": "active" }] } }
# 共 145 个工具，含 slug + 使用量，无需解析 HTML

# 3. 如果没 API → 爬首页找 JS bundle
# Nuxt 3 CSR 页面 curl 取到的 HTML 几乎全空（只有骨架 CSS）
# 必须用 --compressed 参数（Nuxt 默认 gzip 压缩响应）
curl -sL --compressed 'https://target.com/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# 4. 分析页面结构，识别工具分类
# 常见工具类型：
# - 图片处理（压缩/裁剪/格式转换/去背景）
# - 编码解码（Base64/URL/Hex）
# - 文本处理（JSON/Markdown/格式化）
# - 加密解密（AES/RSA/哈希）
# - 开发者工具（正则/CSS/格式化）
# - 音视频（压缩/转换/提取）

# 5. 抓取每个工具页面的 HTML/JS
# Nuxt 3 CSR: 页面内容是空的，JS bundle 渲染一切
# 不要浪费时间解析首页 HTML，直接找 JS bundle 或 API

# ⚠️ 实战陷阱：Nuxt 3 CSR 页面
# - curl 拿到的 HTML 除了骨架 <style> 和 <div id="__nuxt"> 外**没有任何工具数据**
# - 所有工具名、描述、分类全靠 JS bundle 初始化
# - 所以「grep 首页 HTML 提取工具列表」在 Nuxt 3 上完全失效
# - 替代方案：找 /api/tools 端点，或者用 browser_navigate 等待 JS 渲染
```

### 阶段一.b：JS Bundle 发现（Nuxt 3 特化）

```bash
# Nuxt 3 的 JS bundle 路径模式：/_nuxt/{hash}.js
# 从首页 HTML 提取 script src:
curl -sL --compressed 'https://target.com/' | grep -oP 'src="[^"]+' | sort -u

# tools.miku.ac 实际结果：assets 托管在二级域名
# JS bundle: https://okmiku.com/_nuxt/wa80Tw6d.js (425KB)
# 注意：CDN 域名可能跟主域名不同（多域名部署）

# 下载 JS bundle
curl -sL --compressed 'https://okmiku.com/_nuxt/wa80Tw6d.js' -o bundle.js

# 但注意：Nuxt 3 将每个工具组件拆分为异步 chunk（懒加载）
# 实际实现代码可能不在主 bundle 中，而分布在多个 /_nuxt/{slug}.hash.js 中
# 如果主 bundle 里搜不到工具实现，需要抓工具页面的 JS
```

### 阶段二：API 协议逆向

```javascript
// 1. 打开浏览器 DevTools → Network 面板
// 2. 触发工具功能，捕获请求
// 3. 分析请求结构：

// 典型工具 API 结构
{
  method: 'POST',  // 或 GET
  url: '/api/tool/encode',
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  body: {
    input: '待处理数据',
    options: { /* 工具特有的选项 */ }
  }
}

// 4. 识别前端 JS 中 API endpoint 的构造逻辑
// 搜索关键字：fetch、axios、ajax、apiUrl、endpoint
```

### 阶段三：前端 JS 逻辑提取

```bash
# 1. 下载所有 JS bundle
curl -sL https://tools.miku.ac/assets/index-*.js > bundle.js

# 2. 格式化并搜索工具实现
# 漂亮的格式化
npx prettier bundle.js > bundle.formatted.js

# 3. 搜索关键模式
grep -oP '(?<=function )\w+' bundle.formatted.js | sort | uniq -c | sort -rn
grep -n "tool\|convert\|encode\|decode\|compress\|resize" bundle.formatted.js | head -50

# 4. 提取每种工具的核心逻辑
# 注意：可能会被混淆（使用 AST 反混淆先处理）
```

### 阶段四：每个工具的输出格式

```
utils/
├── tool-name/                    # 工具名（英文小写+连字符）
│   ├── README.md                 # 工具描述
│   │   ├── 图标链接              # 来自页面的 favicon/icon URL
│   │   ├── 功能介绍              # 中文描述
│   │   ├── API 说明              # 请求/响应格式
│   │   └── 使用示例              # curl/Python 调用示例
│   └── implement/               # 实现代码
│       ├── api.py                # API 调用封装（Python）
│       ├── logic.py              # 核心逻辑复现（纯算法实现）
│       ├── index.js              # 原始 JS 逻辑（提取自 bundle）
│       └── README.md             # 实现逻辑说明
│
├── another-tool/                 # 另一个工具
│   └── ...
│
└── README.md                     # 根目录索引
```

### README.md 模板

```markdown
# {工具名}

## 基础信息
- **类型**: {图片处理/编码解码/文本处理/加密解密/开发者工具/音视频}
- **图标**: ![icon]({icon_url})
- **页面**: {page_url}
- **API**: {api_endpoint}

## 功能介绍
{中文描述}

## API 说明
### 请求
```http
{method} {url}
Content-Type: {content_type}

{request_body_example}
```

### 响应
```json
{response_example}
```

### 选项参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| input | string | 是 | 输入数据 |
| option1 | string | 否 | 选项说明 |

## 使用示例
```bash
curl -s {example_command}
```

```python
# Python 调用示例
import requests

def convert(data, option="default"):
    ...
```

## 实现逻辑
{核心算法/逻辑说明}
```

## 区分：前端实现 vs 后端 API

很多工具是**纯前端实现**（计算在浏览器 JS 中完成，无服务器交互）。

**识别步骤**（每步必做）：

```bash
# Step 1: 用 browser_console 抓取触发时的网络请求
window._captured = [];
const origFetch = window.fetch;
window.fetch = async function(...args) {
    window._captured.push({url: typeof args[0]==='string'?args[0]:''});
    return origFetch.apply(this, args);
};
# ... 触发工具功能后检查 window._captured

# Step 2: 直接 curl 端点确认是否存在
curl -s 'https://tools.miku.ac/api/t/{slug}' -H 'User-Agent: Mozilla/5.0' \
  -H 'Content-Type: application/json' -d '{"expression":"test"}'

# Step 3: 在 async chunk 中搜 fetch/axios
grep -c 'fetch\|axios' /tmp/tool-chunk.js
# 结果为0 → 极可能纯前端实现
```

**结论处理**：
- 确认纯前端 → 直接给出实现库名 + input/output schema + 行为描述
- 不要浪费时间在不存在 API 的平台上
- 复制到本地复现时，按用户技术栈选库（Python→cronstrue/croner的pip等价，Node.js→直接装cronstrue）

## 技术要点

### 图标提取
```bash
# 方法一：从页面提取
curl -sL https://tools.miku.ac | grep -oP 'icon|favicon|apple-touch-icon"[^>]*href="([^"]+)"'

# 方法二：从 JS 资源映射
grep -oP 'icon.*?https?://[^"\']+' bundle.js

# 方法三：DevTools 直接查看 elements 面板
```

### API 端点发现
```bash
# 从 JS bundle 搜索 API 路径
grep -oP '/api/[a-z/-]+' bundle.formatted.js | sort -u

# 搜索 fetch 调用中的 URL
grep -oP 'fetch\(["'"'"']([^"'"'"']+)["'"'"']' bundle.formatted.js | sort -u

# 搜索 axios 调用
grep -oP 'axios\.[a-z]+\(["'"'"']([^"'"'"']+)["'"'"']' bundle.formatted.js | sort -u
```

## 自动化工作流

```bash
# 全自动工具站逆向脚本
#!/bin/bash
TARGET_URL="$1"
OUTPUT_DIR="./utils"

# === 核心原理 ===
# Nuxt 3 CSR 框架：curl 首页 HTML 只有骨架 CSS + <div id="__nuxt"> 
# 工具数据在客户端 JS bundle 中渲染，所以不能靠 grep HTML 获取工具列表
# 正确做法：优先找后端 API 端点
# Nuxt 3 /api/ 路由默认自动暴露 Nitro server routes

# 1. 优先尝试 API 端点（Nuxt/Next.js 常用）
API_TOOLS=$(curl -sL --compressed "$TARGET_URL/api/tools" -H 'Accept: application/json')
if echo "$API_TOOLS" | grep -q '"tools"'; then
    echo "$API_TOOLS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
tools = data['data']['tools'] if 'data' in data else data['tools']
for t in tools:
    print(t['slug'] if 'slug' in t else t['name'])
" > tool_list.txt
    echo "从 API 获取到 $(wc -l < tool_list.txt) 个工具"
else
    # Fallback: 下载首页并尝试解析
    curl -sL --compressed "$TARGET_URL" -o /tmp/index.html
    # Nuxt 3 SSR 时 __NUXT__ 对象可能包含初始状态
    grep -oP 'window\.__NUXT__\s*=\s*\{[^}]+}' /tmp/index.html | head -1
    # 提取 JS bundle URL
    BUNDLE_URL=$(grep -oP 'src="[^"]*_nuxt/[^"]+\.js"' /tmp/index.html | head -1 | grep -oP 'https?://[^"]+')
    if [ -n "$BUNDLE_URL" ]; then
        curl -sL --compressed "$BUNDLE_URL" -o bundle.js
        grep -oP 'slug:"[^"]+"' bundle.js | sort -u | grep -oP '"[^"]+"' | tr -d '"' > tool_list.txt
    fi
fi

# 2. 对每个工具生成目录
while IFS= read -r name; do
    [ -z "$name" ] && continue
    mkdir -p "$OUTPUT_DIR/$name"
    
    # 封面图 URL（可构造的，不需要抓取）
    COVER_URL="${TARGET_URL}/public/t/${name}/cover.png"
    
    # 生成 README
    cat > "$OUTPUT_DIR/$name/README.md" << README
# ${name}

## 基础信息
- **页面**: ${TARGET_URL}/tool/${name}
- **封面**: ${COVER_URL}
- **类型**: TODO
- **API**: 待分析

## 功能介绍
TODO

## API 说明
TODO
README

    echo "  [OK] $name"
done < tool_list.txt

# 3. 生成 INDEX
python3 -c "
import os
tools = sorted([d for d in os.listdir('$OUTPUT_DIR') if os.path.isdir(os.path.join('$OUTPUT_DIR', d))])
with open(os.path.join('$OUTPUT_DIR', 'INDEX.md'), 'w') as f:
    f.write('# 工具集索引\n\n')
    f.write(f'总数: {len(tools)}\n')
    f.write(f'来源: $TARGET_URL\n\n')
    for t in tools:
        f.write(f'- [{t}]({t}/README.md)\n')
print(f'INDEX 生成: {len(tools)} 条')
"
```

## 验证清单
- [ ] 工具发现完整（没有遗漏）
- [ ] 每个工具的 API 端点已确认
- [ ] 前端逻辑已提取（JS bundle 中对应函数）
- [ ] 后端 API 可独立调用（不依赖前端环境）
- [ ] 核心算法可本地复现（Python/Node.js）
- [ ] README 中包含图标链接
- [ ] 所有工具按规范归档

## 纯前端工具的本地复现（自建实现模板）

当工具确认无 API 且目标只是在自有系统中复现相同功能时，直接用模板开写：

- `templates/cron-parser.py` — 零依赖 Python cron 解析器（5/6字段、L/W/#、DOM/DOW OR、MON-SUN/月份缩写、ASCII图、前后次枚举），300行内直接可用
- 选型参考：Python 用此模板（不用 cronstrue 等 npm 库）；Node.js 直装 cronstrue + croner；iOS Swift 用 CronExpression（系统框架）

## 实战案例参考
- `references/tools-miku-actual-findings.md` — tools.miku.ac 实战提取记录（145个工具）
- `references/cron-parser-no-api.md` — Case Study: 纯前端工具逆向（无 API 时的处理方式）
- `reverse-playbook` → `references/mikutools-case-study.md` — 批量逆向的关键发现和最佳路径

---

## novel-platform-api-reverse

# 中文小说平台 API 逆向方法论

> 中文小说平台的 API 逆向有独特套路：字表编码、独立搜索 API、SSR 内联数据、AES+MD5 签名、登录墙（滑块验证）。
> 本章从实战出发，提炼可复用的方法论。

---

## 适用场景

- 目标：番茄小说、七猫小说、番派、中文在线、起点等中文小说/内容平台
- 目标：短剧/流媒体平台（M3U播放列表逆向，提取HLS播放接口和封面CDN结构）
- 任务：逆向搜索接口、还原目录结构、提取章节内容
- 特征：字表编码、独立搜索域名、Next.js/Nuxt SSR、AES-CBC 加密响应、滑块验证登录墙、M3U/HLS 播放列表

---

## 核心方法论

### 阶段一：侦察与域名发现

中文小说平台常有**独立搜索域名**（非主站域名）：

```
主站: fanqienovel.com → 落地页/详情页
搜索: qkfqapi.vv9v.cn → 独立搜索API (wrapper)
备用: fqweb.jsj66.com, fanqie.mduge.com, 101.35.133.34:5000 → 私有 wrapper
MCP:  fysh1010/mcp-server-fanqie → Node.js MCP 客户端 (反推API面)
```

**策略**：
1. 先 `web_search` 搜 `平台名 api 接口 github` 找开源实现
2. 再 `github code search` 搜 `平台域名` 找第三方爬虫
3. 搜 `mcp-server-fanqie` 找 MCP 客户端（TypeScript 直接暴露 API 路径）
4. 最后直接 `curl` 测试常见路径（`/api/v1/search`, `/api/search`）

### 阶段二：接口分类测试

| 接口类型 | 常见路径 | 认证要求 | 优先级 |
|---------|---------|---------|--------|
| 搜索 | `/api/v1/search?query=XXX` | 通常无 | ⭐⭐⭐ 第一优先 |
| 书籍详情 | `/page/{book_id}` | Cookie | ⭐⭐ |
| 目录 | `/api/reader/directory/detail?bookId=XXX` | Cookie | ⭐⭐ |
| 章节内容 | `/api/reader/full?itemId=XXX` | **滑块验证** | ⚠️ 最难点 |
| 分类 | `/api/category/list` | 无 | ⭐⭐ |

**铁律**：内容接口（章节正文）几乎都有登录墙/滑块验证，公开能跑的只有搜索+目录。

### 阶段三：数据提取技术

#### 1. `window.__INITIAL_STATE__`（Next.js SSR 金矿）

中文小说平台大量使用 Next.js SSR，服务端直接把数据嵌进 HTML：

```python
import re, json
match = re.search(r'window.__INITIAL_STATE__=(.+?});', html)
state = json.loads(match.group(1).replace('undefined', 'null'))
page = state['page']
```

常见数据位置：
- `state.page.bookName` — 书名
- `state.page.chapterListWithVolume` — 目录（需展平）
- `state.page.abstract` — 简介
- `state.reader.chapterData` — 章节内容（**通常为空**，需JS动态加载或登录）

**注意**：番茄小说的 `chapterListWithVolume` 仅在**桌面版 Chrome UA** 返回，iPhone UA 返回空列表。

#### 1a. UA 选择陷阱（番茄小说）

| UA | 目录数据 | 搜索 | 内容 |
|----|---------|------|------|
| Windows Chrome | ✅ 完整 | ✅ | ❌ 字体反爬 |
| iPhone Safari | ❌ 空 | ✅ | ❌ |
| Android Chrome | ✅ 完整 | ✅ | ❌ |

**原因**：番茄小说对移动版 UA 返回精简 SSR 数据（目录为空），迫使用户用 APP 读正文。桌面版返回完整目录是因为 PC Web 端需要展示目录树。

#### 2. 字表编码解码（番茄小说特色）

番茄小说的搜索结果使用**自定义字表编码**，不是Base64，看起来像乱码：

```python
import re

def decode_text(text, charset):
    """字表解码: %uE{hex} → charset[hex-1000]"""
    if not text:
        return ""
    text_escape = text.encode('unicode_escape').decode('ascii')
    reg = re.compile(r'%uE([0-9a-fA-F]{3})', 'gi')
    def replace_match(m):
        idx = int(m.group(1), 16) - 1000
        if 0 <= idx < len(charset):
            return charset[idx]
        return m.group(0)
    result = reg.sub(replace_match, text_escape)
    try:
        return result.encode('ascii').decode('unicode_escape')
    except:
        return result
```

三个字表（来源：`zourjke/drpy-node` 仓库 spider/js/番茄小说[书].js）：
- `CHARSET_CONTENT` — 章节内容（68字符映射表）
- `CHARSET_SEARCH` — 搜索结果（68字符映射表）
- `CHARSET_LEVEL0` — 备用/旧版

#### 3. AES-CBC 解密（章节内容）

```python
from Crypto.Cipher import AES
import base64

def decrypt_aes(ciphertext_b64, key, iv):
    raw = base64.b64decode(ciphertext_b64)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(raw)
    pad_len = decrypted[-1]
    return decrypted[:-pad_len].decode('utf-8')
```

**注意**：不同平台密钥不同，甚至同一公司不同产品（番茄 vs 番派）密钥也不同。

#### 4. 滑块验证识别（番茄小说内容端）

番茄小说 `/api/reader/full` 内容接口的封锁特征：
- 返回 HTTP 200 但 body 为 **0 字节**
- 响应头含 `bdturing-verify: {"code":"10000","subtype":"slide","login_status":0,...}`
- 含义：触发滑块验证，cookie 不够，需浏览器自动化或 APP 端签名绕过

```python
# 检测滑块验证
r = requests.get(url)
if r.status_code == 200 and len(r.text) == 0:
    verify_header = r.headers.get('bdturing-verify', '')
    if 'slide' in verify_header:
        print("触发滑块验证，需浏览器自动化")
```

### 阶段四：第三方源码溯源

中文小说平台爬虫在 GitHub 有一定生态：

| 仓库类型 | 代表 | 价值 |
|---------|------|------|
| MCP 客户端 | fysh1010/mcp-server-fanqie | ⭐⭐⭐ 最高，TypeScript 暴露14个API端点 |
| drpy-node 爬虫 | zourjke/drpy-node | ⭐⭐⭐ 最高，含完整字表和接口 |
| 下载器 | POf-L Fanqie-novel-Downloader | ⭐⭐ 公开版无核心 |
| 安卓客户端 | hunyanjie/FQWeb | ❌ 不是服务器 |
| 服务器实现 | — | 私有，不在GitHub |

**关键洞察**：服务器实现几乎都是私有的，能找到的最高价值源码是爬虫和 MCP 客户端。

---

## 番茄小说 API 面（MCP 客户端反推 + 实测 2026-07-27）

从 `fysh1010/mcp-server-fanqie` 的 `FanQieApi.ts` 反推的完整 API 面（14个端点）：

```
GET /api/search?key=X&tab_type=3&offset=0      → 搜索（3=小说 2=听书 8=漫画 11=短剧）
GET /api/detail?book_id=X                        → 书籍详情
GET /api/book?book_id=X                          → 目录（含卷）
GET /api/directory?book_id=X                     → 简化目录
GET /api/content?tab=小说&item_id=X               → 章节内容
GET /api/content?tab=download&book_id=X          → 整本下载
GET /api/content?tab=batch&item_ids=X,Y&book_id=Z → 批量章节
GET /api/content?tab=audiobook&item_id=X         → 有声书音频
GET /api/content?tab=comic&item_id=X             → 漫画图片
GET /api/raw_full?item_id=X                      → 原始内容（HTML）
GET /api/comment?book_id=X&count=20&offset=0     → 评论
GET /api/device/pool                             → 设备池状态
GET /api/device/register?platform=android        → 注册设备
GET /api/ios/content?item_id=X                   → iOS 内容
GET /api/ios/register                            → 注册 iOS 设备
```

### 可用 ✅

| 接口 | URL | 说明 |
|------|-----|------|
| 搜索 | `GET https://qkfqapi.vv9v.cn/api/v1/search?query=关键词` | 返回 600KB+，需字表解码 |
| 书籍详情+目录 | `GET https://fanqienovel.com/page/{book_id}` | HTML 提取 `__INITIAL_STATE__` |
| 目录 API | `GET https://fanqienovel.com/api/reader/directory/detail?itemId=X&bookId=Y` | 返回 allItemIds + chapterListWithVolume |

### 受限 ⚠️

| 接口 | 问题 |
|------|------|
| `fanqienovel.com/api/reader/full` | 返回 0 字节 + 滑块验证 (`bdturing-verify`) |
| `fanqienovel.com/api/reader/book/read_item_list` | 返回 "请先登录" |
| `api5-normal-sinfonlineb.fanqienovel.com` | VPS IP 不可达，需住宅 IP |
| `qkfqapi.vv9v.cn/api/v1/content` | 404 |

### 私有 wrapper（不公开源码，但可用）

| 服务器 | 用途 | 状态 |
|--------|------|------|
| `101.35.133.34:5000` | 私有 API wrapper | 搜索通，内容需滑块 |
| `qkfqapi.vv9v.cn` | 前端 wrapper | ✅ 搜索可用 |
| `103.236.91.147:9999` | 另一个私有 wrapper | 未测 |

**自建 wrapper 参考架构**：搜索走 `qkfqapi.vv9v.cn`，目录走 `fanqienovel.com/page/{book_id}` HTML 提取，内容需 APP 端签名或 Playwright 过滑块。

---

## FanParty（番派）API 面

| 维度 | 详情 |
|------|------|
| 域名 | api.fanparty.top |
| 技术栈 | Flutter/Dart iOS |
| 认证 | appauthorization (session token) + sign (MD5) + timestamp |
| 加密 | AES-CBC，固定 IV `236f9c3c721517e1dc83297298e436c9` |
| 密钥 | 未知（与番茄小说不同） |
| 服务端 | 未公开，GitHub 零源码 |
| sign 算法推测 | 同 timestamp 同 sign → `MD5(timestamp + STATIC_SECRET)` |

**关键结论**：番茄小说 ≠ FanParty，完全独立系统。番茄小说密钥无法解密 FanParty HAR。

---

## 中文小说平台逆向 Checklist

```
[ ] 搜索 GitHub 找第三方爬虫/下载器/MCP客户端
[ ] 识别主域名 vs 搜索域名 vs MCP 客户端仓库
[ ] 测试搜索API（通常无认证）
[ ] 分析响应编码（Base64？字表？明文？）
[ ] 测试详情页（HTML SSR数据提取 __INITIAL_STATE__）
[ ] 测试目录API（注意桌面版 Chrome UA 才能拿到数据）
[ ] 测试章节内容API（检查 bdturing-verify 头判断是否滑块验证）
[ ] 检查字体反爬（PUA 字符映射）
[ ] 检查是否有独立APP（HAR抓包）
[ ] 区分同一公司不同产品的密钥独立性
[ ] 如果内容端有滑块验证 → 要么Playwright，要么APP签名，要么放弃
```

---

## 常见编码/加密方式

| 平台 | 编码方式 | 解密方法 |
|------|---------|---------|
| 番茄小说 | 字表编码（%uEXXX） | 68字符映射表 |
| 七猫小说 | 明文 或 AES | Frida hook 提取密钥 |
| 番派 | AES-CBC + MD5签名 | Frida hook 提取密钥 |
| 中文在线 | Base64变种 | 自定义字符表 |

---

## 字体反爬机制（番茄小说章节内容 — 2026-07-27 新发现）

番茄小说 `fanqienovel.com/reader/{item_id}` 的章节正文使用**自定义字体反爬**，这是独立于滑块验证的另一层防护。

### 机制详解

| 维度 | 详情 |
|------|------|
| 字体文件 | `https://lf6-awef.bytetos.com/obj/awesome-font/c/dc027189e0ba4cd.woff2` |
| 字体名 | `DNMrHsV173Pd4pgy`（SourceHanSansSC 子集） |
| 反爬方式 | 标准汉字 → PUA 区码点（U+E000+）映射 |
| PUA 字符数 | 362 个 |
| Glyph 索引范围 | gid58344 - gid58715 |
| 字体格式 | woff2, 47564 bytes |

### 提取与解码

```python
from fontTools.ttLib import TTFont

# 1. 加载字体
font = TTFont('/tmp/fq_font.woff2')
cmap = font.getBestCmap()

# 2. 收集 PUA 映射
pua_map = {}
for cp, name in cmap.items():
    if 0xE000 <= cp <= 0xF8FF:
        pua_map[chr(cp)] = name  # glyph name like 'gid58344'

# 3. 需要完整 SourceHanSansSC 字体按 glyph 顺序匹配
# 子集字体保持原始 glyph 顺序 → gid 编号对应完整字体的 glyph 索引
```

### 章节内容提取

```python
# 正确 URL: /reader/{item_id} (不是 /page/{item_id})
r = requests.get(f'https://fanqienovel.com/reader/{item_id}',
                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'})
html = r.text

# 提取 __INITIAL_STATE__
# reader.chapterData 是 dict（非字符串）
# 含 content, title, itemId, needPay, isChapterLock 等字段
# content 是 HTML 实体编码: \u003Cp\u003E... → <p>...
```

### Playwright 渲染的局限

```python
# 即使 Playwright 渲染后读 innerText，字体文件不加载 → 仍是乱码
# headless Chromium 不加载 @font-face 的 woff2 文件
# 需要手动注入字体映射表才能还原
```

### 字体文件 URL 动态生成

字体 URL 在 HTML 的 `@font-face` 声明中动态生成，每次可能不同。需要：
1. 从 HTML 提取 `@font-face` 的 `src:url(...)`
2. 下载对应 woff2 文件
3. 建立映射表
4. 解码正文

## Pitfalls

1. **搜索API ≠ 内容API** — 搜索通常公开，内容几乎都要登录/滑块验证
2. **主域名 ≠ 搜索域名** — 中文小说平台常有独立搜索服务
3. **字表编码不是Base64** — 看起来像乱码的文本是 `%uEXXX` 编码的汉字
4. **同一公司 ≠ 共享密钥** — 番茄小说和番派密钥完全不同
5. **服务器源码私有** — 不要期待在GitHub找到后端实现，从 MCP 客户端/爬虫反推
6. **`chapterData` 在SSR中为空** — Next.js 的章节内容通过JS动态加载
7. **暴力枚举内容路径是徒劳** — 中文小说平台内容路径通常是内部路由
8. **滑块验证无解** — cookie 无法通过内容端，必须浏览器自动化或 APP 端签名
9. **MCP 客户端是金矿** — TypeScript 源码直接暴露完整 API 面和参数
10. **0 字节响应 + bdturing-verify 头 = 滑块验证** — 立即识别，不再浪费 header 测试
11. **字体反爬独立于滑块验证** — 即使过了滑块，正文仍是乱码，需字体映射还原
12. **桌面版 Chrome UA 才能拿到目录** — iPhone UA 返回空 chapterListWithVolume
13. **章节内容 URL 是 `/reader/{item_id}`** — 不是 `/page/{item_id}`

---

## 参考工具

- `fysh1010/mcp-server-fanqie` — MCP 客户端，14个API端点（GitHub）
- `zourjke/drpy-node` — 中文小说爬虫合集，含字表（GitHub）
- `duongden/cachua` — 番茄小说AES解密（GitHub）
- `jadx` — APK反编译，找硬编码密钥
- `Frida` — Hook AES加密函数提取密钥
- `HAR` — 抓包分析真实请求
- `Playwright` — 浏览器自动化过滑块

---

## 相关技能

- `web-api-protocol-reverse` — 通用Web API协议逆向（含Next.js SSR）
- `web-api-reverse-engineering` — Web API逆向工程方法论
- `reverse-playbook` — 通用逆向实战框架
- `so-native-analysis` — SO原生库分析（密钥提取）

## 参考案例

- `references/fanqie-novel-api-reverse.md` — 番茄小说完整逆向案例（2026-07-27实测数据+接口状态+字表解码+API面）
- `references/m3u-playlist-api-extraction.md` — M3U播放列表逆向（黄豆短剧案例：HLS播放接口提取、封面CDN分离、MongoDB ObjectId、CDN sinkhole检测、播放器JSON生成）
- `references/sc-o3hk-qimao-novel-api-reverse.md` — 七猫小说签名算法逆向

---

## simple-php-site-reverse

# 纯 PHP 无框架站点 — 秒杀模式

当目标站点满足以下条件时，不要走完整的 7 步逆向工作流——这是浪费时间。

## 识别特征

- 单文件 PHP（如 `index.php` / `sscj.php` / `list.php`）
- 页面内联 JS 在 `<script>` 标签中（非 SPA 框架，无 webpack/vite/React/Vue）
- 无外部 JS chunk（或只有 CDN 的 font-awesome/bootstrap）
- AJAX 通过 URL 参数 `ajax=1` 切换 JSON/HTML 输出
- 无 Token/Cookie/签名认证
- CF 防护级别低（无 Turnstile、无 JS Challenge）时 curl + 标准 UA 即可过，不算排除条件
- 典型托管：serv00 / 虚拟主机 / cPanel

## 秒杀流程（3 步）

```
Step 1: curl 首页 → 看 HTML 内联 JS → 找到 AJAX 参数和 API 端点
Step 2: curl AJAX 端点 → 看 JSON 结构 → 确定分页参数（pagecount/total）
Step 3: curl 详情页 → grep 视频/图片/关键数据 → 确定提取正则
```

**别做的事**：别用 Lightpanda，别分析 JS bundle，别抓包——直接 curl + grep 就够了。

## 视频内容站常见模式

```
列表: ?type_id=X&page=N&ajax=1 → JSON {list: [{art_id, art_name, art_pic}], pagecount, total}
详情: ?id=art_id → HTML 含 <iframe src="解析器?url=真实m3u8">
视频: 两层嵌套 — 外层解析器域名 + 内层 CDN 直链 m3u8
```

## 批量提取模板

```python
import requests, re

# 1. 获取总页数
data = requests.get(f'{BASE}?type_id={tid}&page=1&ajax=1').json()
for page in range(1, data['pagecount'] + 1):
    arts = requests.get(f'{BASE}?type_id={tid}&page={page}&ajax=1').json()['list']
    for art in arts:
        html = requests.get(f'{BASE}?id={art["art_id"]}').text
        m3u8 = re.search(r'url=(https?://[^&"\s<>]+\.m3u8[^&"\s<>]*)', html)
        if m3u8:
            print(m3u8.group(1))
```

## 交付铁律

**文件发不出去时，优先级：**

1. **MTProto 直接上传** — `python3 /root/tg_file.py upload /path/file <chat_id> "caption"`，200KB~2GB 都行，不需要开端口
2. **MEDIA: 直接发送** — 小文件（<20MB）直接用 MEDIA: 路径
3. **截取前N条贴聊天** — 文本文件太大时截取
4. **问用户** — 以上都不行时，问用户要什么方式

**绝对禁止：**
- ❌ `python3 -m http.server` 开端口暴露文件 → 安全隐患 + 端口暴露 + 用户不会去下载
- ❌ 任何形式的 HTTP/FTP/NC 临时服务暴露 VPS 端口

## 参考案例

- `references/zhangqun1818-case-study.md` — serv00 PHP 资讯站，AJAX JSON API 模式
- `references/hsex-icu-case-study.md` — CF 保护但低级别的纯 PHP 视频站，全 HTML 渲染，无 API

## Pitfalls

1. **CF 保护 ≠ 不能秒杀** — hsex.icu 有 CF 但无 Turnstile/JS Challenge，curl + Mozilla UA 直接 200。先试最简单路径，别看到 CF 就上 scrapling/FlareSolverr
2. **serv00 免费主机可能限速** — 请求间 sleep 0.2-0.5s，否则可能触发临时 ban
2. **HTML 解析优先于 JSON** — 详情页返回完整 HTML，视频在 `<iframe>` 里，不要试图找 JSON API
3. **视频链接两层嵌套** — 外层是解析器代理（浏览器用），内层是真实 CDN（VLC 直接播）。提取内层即可
4. **`author`/`from`/`remarks` 可能始终为空** — 后端未填充这些字段，不要纠结
5. **分页边界检查** — 最后一页可能不满 20 条，`pagecount` 是可靠的

---

## site-wide-exhaustive-reverse

# 网站全量逆向 — 穷举交付标准

## 触发条件

用户要求逆向某个网站的所有接口、拿到完整数据、只要网站有的都逆向给我时触发。

## 用户铁律（来自三次明确纠正）

1. "个个菜单的目录的收藏的喜欢的标签的，之类的这些逆向中写了吗" — 交付物必须覆盖每个菜单
2. "给你说了完整的逆向数据，我没提到的，只要网站有的都逆向给我" — 穷举所有功能，不遗漏
3. "绕过cf" — 用户纠正：在开始逆向前**必须先确认 CF 是否已绕过**，不要跳过这步直接写文档

不要替用户判断哪些重要。只要网站有的功能，全部逆向、全部写入文档。

## 逆向工作流

### Phase 0: CF 检测（必做，不可跳过）

```
1. curl -sI -L --max-time 15 https://target.com/ → 检查 HTTP 状态码
2. curl -sL --max-time 15 -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" https://target.com/ → 拿 HTML
3. 判断 CF 级别：
   - 200 + 完整 HTML → 无 CF 或最低级别，curl 直接过
   - 403 + "Just a moment" → JS Challenge，用 curl_cffi 或 cloudscraper
   - 403 + Turnstile widget → 需浏览器自动化 (scrapling/pydoll)
   - 空响应 / CF 5秒盾 → 中等保护，先试 curl_cffi chrome131
4. **确认 CF 已过再开始逆向**，不要边绕边写文档
```

### Phase 0.5: 技术栈识别

```
1. 检查 HTML 中是否有 React/Vue/Angular 根节点 → SPA
2. 检查是否有 <script src="...webpack..."> 或 inline __NUXT__ / __NEXT_DATA__ → SSR SPA
3. 检查是否纯 PHP 渲染 (无 JS 框架、数据在 HTML 属性中) → 传统 SSR
4. 纯 PHP SSR 站点特征：
   - 无 API 端点，数据全在 HTML 中
   - 无 JS 加密/签名
   - 无 SPA 路由 (#/hash 或 pushState)
   - 翻页是 ?page=N 或 -N.htm 格式
   - 直接解析 HTML 提取字段即可，无需抓包分析
```

## 交付检查清单

### 页面路由（穷举）
- 所有顶层路由（含内部路由参数如 DM ID）
- 所有子路由
- 所有专区路由
- 所有特殊页面路由（排行、字幕专区、VR、直播等）

### 画质/分辨率（穷举）
- 所有可用画质层级
- 每层画质是否需要登录/付费
- **⚠️ 不能仅靠未登录 API 测试断言画质** — 高画质可能需登录才返回，应从 yt-dlp 等开源工具交叉验证
- 画质排序（如 yt-dlp 的 `qualities([...])`）

### 筛选/排序参数（穷举所有枚举值）
- 所有 filter 枚举值
- 所有 sort 枚举值
- 特殊筛选参数（如演员的身高/罩杯/年龄/出道）

### 枚举/分类（穷举）
- 所有 type/category 枚举
- 每个枚举对应的页面路由和内部ID
- 分类列表的响应格式

### 认证体系
- 登录接口（URL, Method, Body, Cookie结构）
- 登录态检测方法
- 需登录功能列表

### 用户功能
- 收藏/喜欢
- 播放列表 CRUD
- 观看历史
- 评论

### 详情页字段（穷举）
- OG meta 标签
- HTML 解析字段
- 列表项字段

### 分页格式
- 所有列表页的分页参数和响应格式

### 数据流架构
- 数据来源架构图
- 哪些需要过防护，哪些不需要
- 多数据源的互补关系

## 反模式

❌ "这是主要接口，其他类似" — 每个接口单独列出
❌ "筛选器支持多种值" — 列出所有枚举值
❌ "和其他页面一样的分页" — 每个页面单独列
❌ 只写 API 不写 HTML 解析 — 两个都要

## 参考案例

- missav.ai 完整逆向：12 type枚举 + 30+路由分10组 + 11详情字段 + 5演员筛选参数 + 6播放列表接口 + 14无码专区 + 8排序+4筛选器。
- `references/iwara-quality-trap.md`
- `references/m3u-playlist-parsing.md` — M3U/M3U8 播放列表批量解析（IPTV/短剧合集，多分片合并+去重+按剧分组导出JSON）

---
