---
name: cf-bypass-master
category: reverse-engineering
description: >-
  Merged skill combining: cf-bypass, cloudflare-api-bypass, cloudflare-pages-reverse, cf-pages-reverse, cf-pages-deploy, saas-api-bypass, saas-backend-api-discovery.
version: "1.0"
sources:
  - cf-bypass
  - cloudflare-api-bypass
  - cloudflare-pages-reverse
  - cf-pages-reverse
  - cf-pages-deploy
  - saas-api-bypass
  - saas-backend-api-discovery
tags: [reverse-engineering, merged]
---

# cf-bypass-master

> **Merged from**: cf-bypass, cloudflare-api-bypass, cloudflare-pages-reverse, cf-pages-reverse, cf-pages-deploy, saas-api-bypass, saas-backend-api-discovery
> **Source count**: 7

---

## Table of Contents

1. [cf-bypass](#cf-bypass)
2. [cloudflare-api-bypass](#cloudflare-api-bypass)
3. [cloudflare-pages-reverse](#cloudflare-pages-reverse)
4. [cf-pages-reverse](#cf-pages-reverse)
5. [cf-pages-deploy](#cf-pages-deploy)
6. [saas-api-bypass](#saas-api-bypass)
7. [saas-backend-api-discovery](#saas-backend-api-discovery)

---

## cf-bypass

# Cloudflare Bypass 技能

来源: https://github.com/Esonhugh/pydoll-cf-waf-bypasser-skills（Pydoll Antibot Bypasser）

## 行为准则（用户偏好）

**用户表达强烈不满时（如"滚你妈的""废物玩意""每次不难的东西硬是让你说成这也不行那也不行"）：**

1. **停止自我辩解和过度道歉** — 不要写"是我在原地转圈""是我废物""是我之前认输太早"等。用户厌恶这种自我贬低式回应。
2. **直接给结论或方案** — 要么立即尝试新路径，要么明确说"做不到"。不要铺垫、不要解释为什么之前失败、不要分析自己的心理过程。
3. **先试最简单的路径** — 用户说"这不难"时，先试最直接的方法（curl raw GitHub、web_search、web_fetch），不要上来就绕 CF/换代理/换 IP。
4. **不要提前宣告失败** — 在穷尽所有选项之前，不要说"没办法""搞不了""只能用户自己操作"。

---

## Pydoll 集成（推荐首选）

Pydoll 是**异步原生、零 WebDriver 依赖**的 Chromium 自动化库，内置 Cloudflare Turnstile 自动处理。
通过 `tab.expect_and_bypass_cloudflare_captcha()` 一行代码绕过 CF。

### Pydoll 2.x 导入变更

⚠️ Pydoll >= 2.0 的导入路径变了：

```python
# Pydoll 1.x（旧版）
from pydoll import Browser                        # ❌ 不存在
from pydoll.browser import Chrome                 # ✅ 正确

# Pydoll 2.x（当前安装的版本 2.23.0）
from pydoll.browser import Chrome                 # ✅ 
from pydoll.browser.options import ChromiumOptions # ✅
```

关键区别：
- `pydoll/__init__.py` 是**空的** — 不导出任何东西
- `Browser` 类在 `pydoll.browser.chromium.chrome.Chrome`
- `binary_location` 通过 `ChromiumOptions` 设置，**不是**构造函数参数
- `expect_and_bypass_cloudflare_captcha()` 返回 **context manager**，必须 `async with ... as wait:` + `await wait`
- Pydoll 2.x 启动 Chrome 失败频率高于 1.x — 如果 `browser.start()` 超时，尝试用不同 Chrome 版本（Puppeteer cache 中的 Chromium 148 可能比 Playwright 的 1223 更稳定）

详见 `references/pydoll-bypass-guide.md`、`references/scrapling-fetch-patterns.md`。

## 环境现状

| 工具 | 状态 | 版本 | 路径 | Chrome 路径 |
|------|------|------|------|-------------|
| pydoll-python | ✅ 已装 | 2.23.0 | pip | `/root/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome` |
| turnstile_solver | ✅ 已装 | 3.16b | pip git | 同上 |
| cloudscraper | ✅ 已装 | 1.2.71 | pip | — |
| curl_cffi | ✅ 已装 | 0.15.0 | pip | — |
| patchright | ✅ 已装 | 1.60.0 | pip | 同上 |
| nodriver | ✅ 已装 | 0.50.3 | pip |
| camoufox | ✅ 已装 | latest | pip |
| camofox-browser | ✅ 已装 | latest | pip |
| scrapling | ✅ 已装 | 0.4.8 | pip |
| FlareSolverr | ✅ 已部署 | 3.5.0 | Docker: `localhost:8191` |
| undetected-chromedriver | ✅ 已装 | 3.5.5 | pip |
| cloudflare-turnstile-solver | ✅ 已装 | latest | pip |
| Turnstile-Solver (Theyka) | ✅ 已装 | latest | pip |
| 可用 Chrome | ✅ | 131.0.6778.204 / 148.0.7778.96 | Playwright/Puppeteer cache |

## 实战测试结果（目标: uaa002.com）

### ❌ 失败的方案（uaa002.com 双重重保护）

| 方法 | 结果 | 原因 |
|------|------|------|
| cloudscraper | 403 | 仅过基础 IUAM，Turnstile 无效 |
| curl_cffi (chrome131/safari17) | 403 TLS 指纹不够，Turnstile+JS Challenge 无法仅靠 TLS 绕过 |
| Scrapling (curl_cffi引擎) | 403 | 同上 |
| Playwright headless | Challenge | 无 stealth 直接被检测 |
| Playwright + CDP stealth | Challenge | 纯 JS 补丁不够，缺指纹 |
| patchright | Challenge | 打补丁的 Playwright 仍被检测 |
| nodriver | Challenge | undetected-chromedriver 后继者也被检测 |
| Camoufox (Firefox) | Challenge | Firefox 指纹更易被 CF 标记 |
| FlareSolverr 3.5.0 | Timeout 60s | Turnstile + JS Challenge 双重重压，纯 HTTP 解法不够 |
| POST /login API 直接请求 | 403 CF | 即使走 API 接口，CF 全面保护所有端点 |
| tesseract OCR（验证码识别） | 失败 | 验证码强抗OCR，无字符识别输出 |
| Pydoll expect_and_bypass_cloudflare | ❌ 超时 | `span.cb-i` shadow root 找不到，Turnstile 版本不兼容 |
| turnstile_solver | ❌ 超时 | sitekey 动态生成，不在初始 HTML 中 |
| 直接暴力破解 4位验证码 | ❌ 0-200 失败 | 无写死默认验证码，必须精确匹配 |
| **Hermes 内置 browser 工具 (stealth模式)** | **✅ 成功渲染页面** | 唯一能在 www.uaa002.com 上执行 JS 的工具（真实 Chrome + CDP，绕 CF JS Challenge） |

### ⚠️ 关键发现：CF 覆盖范围

**之前的错误认知**：只有前端页面被 CF 保护，API 接口不受影响。

**实测证明**：当 CF 保护级别为 **Turnstile + Managed Challenge** 时，**全站所有端点都受保护**，包括：
- `/login` POST API
- `/novel/list` 搜索 POST
- `/novel/chapter` 正文接口
- `/novel/intro` 详情接口
- `/email/captcha` 验证码接口

这意味着基于 HTTP 请求的书源在全面 CF 保护的站上**完全无法工作**。即使配置了 loginUrl，login 请求也会被 CF 挡住。唯一能绕过的是 Hermes 的 browser 工具（stealth Chrome + CDP 模式），但这就需要用户交互了。

### ✅ 测试中与 uaa002.com 的 CF 对抗结果

**关键发现**: www.uaa002.com 是 **Turnstile + JS Challenge 双重保护**，不是简单的 "I'm Under Attack Mode"。机房 IP + 无代理 + 纯 HTTP 的方案都过不了。

## 多层绕过方案

### Level 0: Pydoll 一键绕过（推荐首选）

```python
import asyncio
from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions

async def main():
    options = ChromiumOptions()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.webrtc_leak_protection = True
    options.binary_location = '/root/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome'

    async with Chrome(options=options) as browser:
        tab = await browser.start()
        async with tab.expect_and_bypass_cloudflare_captcha() as wait:
            await tab.go_to('https://target.com')
            await wait  # 等待 CF 验证完成
        print(await tab.title)

asyncio.run(main())
```

> ⚠️ Pydoll >= 2.x: `from pydoll.browser import Chrome`。`__init__.py` 为空，`binary_location` 通过 `ChromiumOptions` 设置。`expect_and_bypass_cloudflare_captcha()` 返回 context manager，需要 `async with ... as wait:` + `await wait`。

内置方法：`tab.expect_and_bypass_cloudflare_captcha()` / `tab.enable_auto_solve_cloudflare_captcha()`

> ✅ nowsecure.nl 测试通过 | ❌ uaa002.com 超时（Turnstile+JS Challenge 双重重）

### Level 0.5: turnstile_solver（patchright 引擎）

```bash
# 已安装
solver --port 8088 --secret your_secret --browser chrome \
  --browser-executable-path /root/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome \
  --browser-position

# 调用
curl -X GET "http://127.0.0.1:8088/solve" \
  -H "secret: your_secret" \
  -H "Content-Type: application/json" \
  -d '{"site_url": "https://target.com", "site_key": "0x4AAAAAAAByvC31sFG0MSlp"}'
```

> 需要 sitekey（动态网站需先自动提取）。对 uaa002.com 也超时。

### Level 1: TLS 指纹层（最轻量）

```python
from curl_cffi import requests

r = requests.get('https://target.com', impersonate='chrome131')
```

局限性: 仅过 TLS 指纹检测，Turnstile/JS Challenge 无效。

### Level 2: 浏览器自动化层

```python
# Playwright + stealth CDP patches + xvfb
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
        locale='zh-CN', timezone_id='Asia/Shanghai',
    )
    page = context.new_page()
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN','zh','en'] });
        window.chrome = { runtime: {} };
    """)
    page.goto('https://target.com', wait_until='domcontentloaded')
```

局限性: 需要 xvfb。机房 IP 下仍然可能被挑战。

### Level 3: Turnstile 解法（当前最优方案）

使用 turnstile_solver（基于 patchright）:

```bash
# 安装
pip install git+https://github.com/odell0111/turnstile_solver@main
patchright install chrome

# 运行 solver 服务
solver --port 8088 --secret YOUR_SECRET --browser-position --max-attempts 3
```

```python
# 获取 token
import requests
resp = requests.get('http://127.0.0.1:8088/solve', headers={
    'secret': 'YOUR_SECRET',
    'Content-Type': 'application/json'
}, json={
    "site_url": "https://target.com",
    "site_key": "0x4AAAAAAAByvC31sFG0MSlp"
})
token = resp.json()['token']
```

### Level 4: FlareSolverr + 代理（已部署）

```bash
# FlareSolverr 已在 localhost:8191 运行
# 需要配合合格代理使用
```

```python
import requests
payload = {
    "cmd": "request.get",
    "url": "https://target.com",
    "maxTimeout": 60000,
    "proxy": {"url": "http://user:pass@proxy:port"}  # 住宅代理
}
r = requests.post('http://localhost:8191/v1', json=payload)
```

### Level 5: Scraply StealthyFetcher（已验证可绕过 Turnstile）

**2026-07-10 实测确认**: Scraply 的 `StealthyFetcher` 配合 `solve_cloudflare=True` 参数可以成功绕过 Cloudflare Turnstile，直接导航到目标页面的真实登录页（非 challenge 页面）。

#### 安装
```bash
pip install --break-system-packages scrapling
playwright install chromium
```

#### 基础用法：一键绕过 CF 获取页面
```python
from scrapling.fetchers import StealthyFetcher

# 自动解决 CF challenge，返回渲染后的 Response 对象
resp = StealthyFetcher.fetch(
    "https://claude.ai/",
    headless=True,
    solve_cloudflare=True,       # 关键参数，自动解 CF Turnstile
    humanize=True,               # 人类化延迟
    allow_webgl=True,
    block_webrtc=True,
    locale="en-US",
    # ...
)
print("URL:", resp.url)          # https://claude.ai/login
print("Status:", resp.status_code)  # 200
print("Body:", resp.html_content)  # 真实页面 HTML（属性，非方法）
```

#### Scraply Response 对象接口（2026-07-10 实测确认）

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| `resp.url` | str | 最终 URL（重定向后） |
| `resp.status_code` | int | HTTP 状态码 |
| `resp.html_content` | str | 页面 HTML（属性，**非方法**） |
| `resp.text()` | str | 文本内容（**方法调用**） |
| `resp.content` | bytes | 原始字节内容 |
| `resp.cookies` | list[dict] | Cookie 列表 |
| `resp.headers` | dict | 响应头 |

> ⚠️ 常见错误：`resp.html_content` 是**属性**不是方法，调用 `resp.html_content()` 会报 TypeError。`resp.text()` 才是方法。

#### 在浏览器上下文内执行 API 调用

```python
from scrapling.engines._browsers._stealth import StealthySession

with StealthySession(
    headless=True,
    solve_cloudflare=True,
    proxy="socks5://127.0.0.1:1080"
) as ste:
    # page_action 在页面加载后执行
    def api_call():
        js = """async () => {
            const r = await fetch("https://target.com/api/endpoint", {
                method: "POST",
                headers: {"content-type": "application/json"},
                body: JSON.stringify({...}),
                credentials: "include"
            });
            return JSON.stringify({status: r.status, body: await r.text()});
        }"""
        return ste.context.pages[0].evaluate(js)
    
    # 先导航过 CF，再在页面内执行 API
    resp = ste.fetch("https://target.com/", page_action=api_call)
```

#### 关键注意事项

1. **proxy 格式**: 只能用 `socks5://host:port`，**不能用 `socks5h://`**。
   scrapling 内部的 `construct_proxy_dict()` 不支持 `socks5h` scheme，会报 `ValueError: Invalid proxy string!`
   
2. **page_action 执行时机**: callback 在 `fetch()` 完成后执行，此时页面已加载。可通过 `ste.context.pages[0]` 访问 Playwright Page 对象调用 `evaluate()`。
   
3. **性能**: Stealthly 自带浏览器复用的，但每个 fetch 仍需要重新渲染页面。对于高频调用，考虑使用 `StealthySession` 上下文管理器，在同一个浏览器会话内多次操作。

4. **exit IP 问题**: 即使完美绕过 CF，某些服务（如 Claude.ai）仍可通过其他信号识别并返回 403。这不是 CF 问题，是后端风控策略。

#### 实测结果（claude.ai，UK 住宅代理 212.135.127.172 via Easinet UK）

| 目标 | 结果 | 说明 |
|------|------|------|
| GET claude.ai/login | ✅ 200 | Title: "Sign in - Claude"，无 challenge |
| GET claude.ai/register | ✅ 200 | 页面仅含 Cookie 设置按钮，无注册表单 |
| POST /api/auth/send_magic_link | ✅ CF bypassed | API 返回 403 `signups_disabled` |

### ⚠️ 重要：绕过 CF ≠ 绕过所有访问控制

**IP 被 CF 拉黑（Banned）的检测特征**：

当 CF 不仅返回 challenge，而是直接在封禁层面拒绝时：
- FlareSolverr 报错: *"Cloudflare has blocked this request. Probably your IP is banned for this site"*
- 所有绕过工具（curl_cffi、cloudscraper、scrapling、patchright）均返回 403，无 challenge
- scrapling `solve_cloudflare=True` 日志显示 `ERROR: No Cloudflare challenge found` → 直接 403
- **机房 IP 是重灾区**：大多数 Cloudflare 保护站点对 VPS/数据中心 IP 段默认封禁

**处理流程**：
```
所有工具返回 403
  ↓
检查 FlareSolverr 日志
  ↓
含 "blocked" / "IP is banned" → IP 被拉黑
  ↓
所有基于本地 IP 的绕过手段均无效
  ↓
需要：换 IP（住宅代理 / 机场 / 其他 VPS）
```

某些服务在 CF 之外仍有独立的**后端风控**。即便完美绕过 CF，API 仍可能返回 403。

#### 场景：claude.ai 注册关闭（2026-07-10 实测）

- scrapling `solve_cloudflare=True` + 英国住宅代理 → 完美绕过 CF → 进入 `Sign in - Claude` 登录页（Title 正确）
- 直接 POST `/api/auth/send_magic_link` → 仍返回 `HTTP 403 signups_disabled`
- 原因：**Anthropic 关闭了公开注册**，与 IP/CF/代理无关
- 机房 IP + UK 住宅 IP 均不行

**教训**：绕过 CF 后仍 403 时，首先确认是否为**后端业务策略限制**（注册转邀请制、地区法规限制等），而非继续死磕代理/CF。

#### 检测流程

```
CF Bypassed → API 仍 403 → 检查响应 body
  - 含 "signups_disabled" / "registration_disabled" → 后端策略，代理/CF 无法解决
  - 含 "Just a moment" / "Checking your browser" → CF 未完全过，需调整绕过参数
  - 含 "Access denied" + HTML → CF UA/指纹被识别，换路径
```

### Level 4.5: CF Cookie Harvesting（大容量爬取首选）

**核心思路**：只用 FlareSolverr 拿一次 `cf_clearance` cookie，然后全程用 `requests` 批量请求。

**适用场景**：CF 保护级别为 JS Challenge（非 Turnstile）的站点，需要在数千页上做大规模爬取。

```python
import requests
from bs4 import BeautifulSoup

FS_URL = 'http://localhost:8191/v1'

# Step 1: 通过 FS 获取 cf_clearance cookie
resp = requests.post(FS_URL, json={
    "cmd": "request.get",
    "url": "https://target.com/p/all.html",
    "session": f"harvest_{int(time.time())}",
    "maxTimeout": 60000,
}, timeout=70)
data = resp.json()
sr = data['solution']

cookies = {c['name']: c['value'] for c in sr['cookies']}
ua = sr['userAgent']

# Step 2: 用 cookie + UA 创建 requests session（可复用数千次）
s = requests.Session()
s.headers['User-Agent'] = ua
for k, v in cookies.items():
    s.cookies.set(k, v)

# Step 3: 直接 requests 批量请求（避免每次走慢速 FS）
r = s.get('https://target.com/search/label/标签?max-results=9999', timeout=20)
```

**关键点**：

---
*[Content truncated: 786 lines total]*
---

   a. GitHub raw 镜像（fz200/wool_scripts, Moli-X/Tool 等）→ 首选（100%成功）
   b. 用户从 Loon 安装后导出 .lpx

4. 大规模爬取（JS Challenge 级别 CF，非 Turnstile）:
   a. FlareSolverr cookie harvesting → 拿 cf_clearance 后转 requests 批量

5. uaa002.com 级别双重重保护:
   a. 配住宅代理 (BrightData/IPRoyal)
   b. 部署 turnstile_solver (patchright 引擎)
   c. 或 FlareSolverr + 代理

6. IP 被 CF Ban → 所有本地方案无效，必须换 IP
   - 免费代理池（geonode/proxyscrape/clarketm/Tor）实测全部失败
   - 付费机场节点（HK/US/SG/JP/KR/UK/DE/VN 等所有 IDC IP）也全部 403
   - 只有**住宅 IP（ISP 段 IP）+ scrapling StealthyFetcher** 才能过
   - 快速测试多个机场节点：用 xray 客户端配置 socks5 输出（参见局限第13条）
   - 详见 `references/kelee-cf-ip-ban-case.md`

7. 轻量级 TLS 绕过: curl_cffi (chrome131 指纹)
```

---

## 外部开源 CF 绕过项目（2026年搜寻）

### ⭐ munew/cloudflare-turnstile-solver — 纯请求级 Turnstile 解法

**仓库**: https://github.com/munew/cloudflare-turnstile-solver
**特点**: 完全逆向 Cloudflare Turnstile，纯 HTTP 请求解法，**无需浏览器自动化**
**原理**: 通过逆向 Turnstile 的 JS challenge 算法，直接构造合法 token

```python
# 安装
pip install cloudflare-turnstile-solver

# 使用
from cloudflare_turnstile_solver import solve_turnstile

token = solve_turnstile(
    site_url="https://target.com",
    site_key="0x4AAAAAAAByvC31sFG0MSlp"
)
```

> ⚠️ 优势：无浏览器依赖、速度快、适合服务端部署
> ⚠️ 风险：CF 更新算法后可能失效，需关注仓库更新

### ⭐ D4Vinci/Scrapling — 自适应爬虫框架（70k+ stars）

**仓库**: https://github.com/D4Vinci/Scrapling
**特点**: 内置 Cloudflare Turnstile 绕过、MCP Server 集成、自适应页面变化

```python
from scrapling.fetchers import StealthyFetcher

resp = StealthyFetcher.fetch(
    "https://target.com",
    headless=True,
    solve_cloudflare=True,
    humanize=True,
)
```

> 已集成到 Level 5 方案。2026年最火 Python 爬虫框架。

### jo-inc/camofox-browser — AI Agent 专用隐身浏览器

**仓库**: https://github.com/jo-inc/camofox-browser
**Stars**: ~8k
**特点**: 基于 Camoufox（Firefox C++ 级指纹伪装），Puppeteer/Playwright 替代品

```bash
npm install camofox-browser
```

> 比 Camoufox Python 包更稳定，提供 REST API 给 AI Agent 调用

### sarperavci/CloudflareBypassForScraping — 纯请求绕过

**仓库**: https://github.com/sarperavci/CloudflareBypassForScraping
**Stars**: ~2.1k
**特点**: 纯 Python 请求，无需浏览器，通过请求镜像 + cookie 生成绕过

```python
from cloudflare_bypass import CloudflareBypass

bypass = CloudflareBypass()
response = bypass.get("https://target.com")
```

> 适合简单 IUAM 模式，对 Turnstile 效果有限

### x404xx/Turnstile-Solver — REST API Token 服务

**仓库**: https://github.com/x404xx/Turnstile-Solver
**特点**: 基于 Quart/ASGI 的 REST API 服务，检测 CF 保护并返回 token

```bash
# 部署
python app.py  # 启动后访问 http://localhost:3000/

# 调用
curl "http://localhost:3000/check_cf?target_url=https://target.com"
curl "http://localhost:3000/solve?site_url=https://target.com&site_key=0x4AAAA..."
```

> 注意：Public archive 状态，可能已停止维护

### Theyka/Turnstile-Solver — Patchright 多线程解法

**仓库**: https://github.com/Theyka/Turnstile-Solver
**特点**: 基于 patchright（Playwright 补丁版），支持多线程、多浏览器

```python
from turnstile_solver import TurnstileSolver

solver = TurnstileSolver(browser="chrome", headless=True)
token = solver.solve(site_url="https://target.com", site_key="0x4...")
```

> 多线程场景下性能优于单 patchright 实例

### NopeCHALLC/nopecha-extension — 浏览器扩展 + API

**仓库**: https://github.com/NopeCHALLC/nopecha-extension
**特点**: 浏览器自动化扩展，支持 Selenium/Puppeteer/Playwright 集成

```python
import nopecha

nopecha.api_key = "YOUR_KEY"
token = nopecha.Token.solve(
    type="turnstile",
    sitekey="0x4AAAA...",
    url="https://target.com"
)
```

> 付费服务，但有免费额度

---

## 新增绕过方案

### Level 6: cloudflare-turnstile-solver（纯请求，2026新）

```python
from cloudflare_turnstile_solver import solve_turnstile

# 纯 HTTP 请求，无需浏览器
token = solve_turnstile(
    site_url="https://target.com",
    site_key="0x4AAAAAAAByvC31sFG0MSlp"
)

# 使用 token 发送请求
import requests
resp = requests.post("https://target.com/api/login", data={
    "cf-turnstile-response": token,
    "username": "...",
    "password": "..."
})
```

**优势对比**:
| 方案 | 需要浏览器 | 速度 | 稳定性 | 适用场景 |
|------|-----------|------|--------|---------|
| scrapling StealthyFetcher | ✅ | 慢(3-10s) | 高 | 复杂 Turnstile |
| cloudflare-turnstile-solver | ❌ | 快(<1s) | 中 | 标准 Turnstile |
| turnstile_solver (patchright) | ✅ | 中(5-15s) | 中 | 自动化集成 |
| FlareSolverr | ✅ | 慢(15-60s) | 高 | 全站绕过 |

脚本 `scripts/scrapling_api_client.py` 提供一站式封装：

```bash
python3 scripts/scrapling_api_client.py \
    https://target.com/ \
    'async () => { const r = await fetch("/api/do", {method:"POST", body:"{\"x\"}"}); return await r.text(); }' \
    socks5h://127.0.0.1:1080
```

## 安装 & 部署参考

### FlareSolverr（已部署）
```bash
docker run -d --name flaresolverr -p 8191:8191 \
  ghcr.io/flaresolverr/flaresolverr:latest
```

### turnstile_solver（未部署，需要时安装）
```bash
pip install git+https://github.com/odell0111/turnstile_solver@main
patchright install chrome
```

### scrapling（已部署）
```bash
pip install --break-system-packages scrapling
playwright install chromium
```

---

## cloudflare-api-bypass

# Cloudflare API Bypass

When the target's API subdomain has CF Turnstile and raw curl returns CF HTML.

## Strategy Matrix

| Scenario | Solution |
|----------|----------|
| API subdomain has CF, main site works in browser | `cloudscraper` (first choice) |
| Whole site including main page has CF | Browser tools + route interception |
| SPA loads API from same origin | Browser console fetch (no CORS) |
| Cross-origin API blocked by CORS | cloudscraper or Playwright |

## cloudscraper (Fastest)

```python
import cloudscraper
scraper = cloudscraper.create_scraper()
r = scraper.get('https://api.target.tv/endpoint', params={...})
```

**Real case**: iwara.tv — `api.iwara.tv` has CF Turnstile, main site doesn't. cloudscraper bypasses.

## GitHub Source as Proxy

When direct access is blocked, clone open-source downloaders for the target.

**Real case**: missav — Recombee search API bypassed CF as third-party backend. Found via `EchterAlsFake/missav_api`.

## Pitfalls

1. **cloudscraper needs `--break-system-packages` on Debian** (PEP 668)
2. **API subdomain may have different CF settings** than main site
3. **Browser console fetch blocked by CORS** for cross-origin APIs
4. **Rate limiting** — add delays if cloudscraper works then fails

---

## cloudflare-pages-reverse

# Cloudflare Pages 逆向侦察

## 架构

CF Pages = 静态站点 + 可选 Functions 后端（`/functions/` 目录编译为 Workers）。

## 认证模式

| 模式 | 示例 |
|------|------|
| GET 参数 | `/?key=SECRET` |
| Cookie | 首次 Set-Cookie，后续靠 Cookie |
| Header | `Authorization: Bearer TOKEN` |
| 路径参数 | `/sub?token=TOKEN` |

## 侦察清单（按优先级）

### P0: 域名关联链侦察（最快！）

CF Pages 站点常有关联的父域名或其他子域名，这是获取上下文最快的路径：
```bash
# 去掉子域名前缀，访问上级域名
curl -s "https://PARENT.pages.dev/" | head -5
# 可能发现重定向到实际业务站点（机场面板等）
curl -sv "https://PARENT.pages.dev/" 2>&1 | grep -i "refresh\|redirect\|location"

# 示例: byg-sub.pages.dev → byg.pages.dev → bygcloud.com (白月光机场)
```

从关联站点获取的上下文直接缩小 key 猜测范围：
- 面板类型（V2Board/SSRDOG/自建）
- 注册链接中的邀请码（可能是 key 或 key 的一部分）
- 公开的订阅格式/路径模式

### P1: GitHub 源码搜索
搜索域名/项目名 + `pages.dev key` 关键词。

### P2: 浏览器实测
排除 CF 反爬干扰——curl 可能被拦截但浏览器正常。

### P3: 配置文件泄漏
```bash
curl -s "https://TARGET/_redirects"
curl -s "https://TARGET/_headers"
curl -s "https://TARGET/_routes.json"
curl -s "https://TARGET/wrangler.toml"
```

### P3: Functions 端点枚举
```bash
curl -s "https://TARGET/api/"
curl -s "https://TARGET/api/verify"
curl -s "https://TARGET/functions/%5B%5Bpath%5D%5D.js"
```

### P5: 认证方式切换 + ffuf 爆破
```bash
# GET → POST → Cookie → Header
curl -s "https://TARGET/?key=TEST" | md5sum
curl -s -X POST "https://TARGET/" -d "key=TEST" | md5sum
curl -s -b "key=TEST" "https://TARGET/" | md5sum
curl -s -H "Authorization: Bearer TEST" "https://TARGET/" | md5sum

# ffuf 按响应大小过滤（最有效的批量爆破方式）
baseline_size=840  # 错误 key 的响应大小
ffuf -u "https://TARGET/?key=FUZZ" \
  -w /tmp/dict.txt -fs $baseline_size \
  -mc all -t 10 -timeout 5
```

## Functions 是否工作的判断

| 信号 | 含义 |
|------|------|
| 不同 key 不同 MD5 | ✅ 在工作 |
| 不同 key 不同响应体大小 | ✅ 在工作（YAML vs HTML 差异大） |
| Set-Cookie | ✅ 在工作 |
| 302/301 | ✅ 在工作 |
| 401/403 | ✅ 在工作 |
| 非 GET 方法 400 | ⚠️ Functions 可能只注册了 onRequestGet |
| 所有 key 相同 MD5 | ⚠️ 可能未部署，也可能是正确 key 难猜 |

**重要**：当用户坚持"站点完整"时，不要过早下结论。正确 key 返回的可能是完全不同的内容类型（如 HTML→YAML），应：
1. 用 `-w "%{size_download}"` 检测响应体大小差异，而非只靠 MD5
2. 如果已知正确响应的格式（如 Clash YAML），用 `-H "Accept: text/yaml"` 测试
3. 询问用户正确响应的特征来校准检测标准

## Pitfalls

1. **curl 被 CF 反爬** — 用浏览器实测确认
2. **`_redirects` 不支持 `?key=` 匹配** — 只能匹配路径
3. **过早下结论** — 用户有外部信息时优先搜源码 + 浏览器实测
4. **仅靠 MD5 判"未部署"** — 正确 key 难猜时所有错误 key 返回相同 HTML 是正常的。先问用户正确响应的格式/大小，校准检测标准后再下结论
5. **非 GET 方法 400 不是 Functions 不存在的证据** — Functions 可能只注册了 `onRequestGet`，GET 才是正确入口
6. **无声 fallback 模式** — CF Pages Functions 对错误 key 的典型行为是 fallback 到静态 HTML，所有错误 key 返回完全相同大小和 MD5。这不是"Functions 未部署"的信号，正确 key 的响应可能完全不同（如 YAML vs HTML）。识别方法：① 用 `-w "%{size_download}"` 检测大小差异 ② 用 MD5 baseline 批量对比 ③ `ffuf -fs <baseline_size>` 过滤
7. **特殊字符导致假阳性** — key 含 `@`、`#`、`/`、`-` 等特殊字符时，URL 编码可能导致响应体有 ~36B 差异但内容相同。用 `head -c 100` 确认内容而非仅靠 size/MD5
8. **爆破陷入死循环** — 当 3 轮以上爆破无结果时，停下来请求用户提供更多上下文（正确响应的格式、来源渠道等），而非继续扩大字典

## 案例参考

- `references/byg-sub-case.md` — byg-sub.pages.dev 完整逆向过程（域名关联链、无声 fallback、ffuf 爆破）

---

## cf-pages-reverse

# Cloudflare Pages 逆向分析

判断 `.pages.dev` 站点是否部署了 Functions 后端，还是纯静态壳。

## 触发条件

- `*.pages.dev` 域名
- 有表单但提交无变化
- 需要判断 Functions 是否工作

## 多维验证矩阵

1. **建立基线** — `curl -s "?key=wrong" | md5sum` + `wc -c`
2. **GET 参数差异化** — 不同 key 不同 MD5 = Functions 在线
3. **HTTP 方法** — 非 GET 返回非 404 = Functions 在线
4. **路径枚举** — `/api/` `/functions/` 非 404 = Functions 在线
5. **响应头** — Set-Cookie/Location = 认证机制存在
6. **浏览器交互** — 页面变化/重定向 = 前端逻辑或 Functions 响应
7. **ffuf 大小过滤** — `ffuf -u "?key=FUZZ" -w dict.txt -fs <baseline_size>`

### ffuf 关键命令

```bash
ffuf -u "https://target.pages.dev/?key=FUZZ" \
  -w /tmp/dict.txt -fs <baseline_size> \
  -mc all -t 10 -timeout 5
```

### 父域名 pivot

```bash
curl -s "https://PARENT.pages.dev/" | grep -i "refresh\|redirect"
```

## Pitfalls

1. 基线相同别爆破，先确认 Functions 在线
2. 特殊字符导致 ~36B 差异但内容相同，用 `head -c 100` 确认
3. `.pages.dev` ≠ `.workers.dev`
4. Functions 可能只在特定路径工作，先全面枚举
5. **爆破死循环** — 3轮以上无果时停下来请求更多上下文（正确响应格式、来源渠道），不要无限扩大字典
6. **无声 fallback** — 所有错误 key 返回相同 HTML 不是"未部署"的信号，正确 key 的响应可能完全不同（如 YAML）

## 案例参考

- `references/byg-sub-case-study.md` — byg-sub.pages.dev 完整分析过程

---

## cf-pages-deploy

# CF Pages 部署（Next.js + Wrangler）

## 凭据识别

| 类型 | 前缀 | 认证头 | 获取路径 |
|------|------|--------|----------|
| API Token | `cfat_` | `Authorization: Bearer <token>` | Dash → My Profile → API Tokens → Create Token |
| User Token | `cfut_` | `Authorization: Bearer <token>` | Dash → My Profile → API Tokens（用户级 token，权限范围不同） |
| Global API Key | `cfk_` 或小写hex | `X-Auth-Email` + `X-Auth-Key` | Dash → My Profile → API Tokens → Global API Key → View |

**验证方法（按顺序尝试，不要假设）**：
1. `GET /user` → `X-Auth-Email` + `X-Auth-Key`（适用于 Global Key）
2. `GET /user/tokens/verify` → `Authorization: Bearer`（适用于 API Token）
3. `GET /accounts` → `Authorization: Bearer`（列出账户确认 Account ID）
4. wrangler CLI 验证：`CLOUDFLARE_API_KEY=xxx CLOUDFLARE_EMAIL=yyy npx wrangler whoami` 或 `CLOUDFLARE_API_TOKEN=xxx npx wrangler whoami`

**常见坑**：
- 用户给的可能是 Global Key 但说"API Token"，或反过来。`cfat_` 前缀 = API Token。`cfk_` 前缀 = Global API Key。`cfut_` = User Token（也是 Bearer 认证）。
- Global Key 用 `Authorization: Bearer` → 9109 "Invalid access token"；API Token 用 `X-Auth-Key` → 9103。
- **API Token 权限不足时返回 10000 "Authentication error" 而不是 403** — 不要被误导成 token 无效，可能是权限不够。Global Key 没有权限限制。
- **User Token (cfut_) 验证成功 (/user/tokens/verify → active) 但操作 Zone Settings 返回 9109** — User Token 的权限范围可能只有 Account 级（读用户信息、管理 Workers），没有 Zone 级（SSL、DNS 编辑）权限。Global Key 是唯一保证全权限的凭据类型。
- 用户可能搞混登录邮箱。CF 账户邮箱 ≠ 通知邮箱。先问清楚 dash.cloudflare.com 右上角显示的邮箱。**同一个 Gmail 可能绑定多个 CF 账户，每个有不同的 Key。**

## 部署路径

### 路径 A：Docker Compose（首选 — 无 CF 限制，最稳定）

**Step 1: 安装 Docker**
```bash
curl -fsSL https://get.docker.com | bash
```

**Step 2: 部署**
```bash
mkdir -p /opt/moontv && cat > /opt/moontv/docker-compose.yml << 'EOF'
services:
  moontv-core:
    image: ghcr.io/mtvpls/moontvplus:latest
    container_name: moontv-core
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - USERNAME=admin
      - PASSWORD=your_password
      - NEXT_PUBLIC_STORAGE_TYPE=redis
      - REDIS_URL=redis://moontv-redis:6379
      - CONFIG_SUBSCRIPTION_URL=https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.txt
      - TMDB_API_KEY=your_tmdb_api_key
      - TMDB_ACCESS_TOKEN=your_tmdb_jwt_token
    depends_on:
      - moontv-redis
    networks:
      - moontv-network

  moontv-redis:
    image: redis:alpine
    container_name: moontv-redis
    restart: unless-stopped
    volumes:
      - /opt/moontv/data:/data
    networks:
      - moontv-network

networks:
  moontv-network:
    driver: bridge
EOF
cd /opt/moontv && docker compose pull && docker compose up -d
```

**Step 3: Nginx 反代（CF Proxy 回源必需）**

CF Proxy 回源默认走 80 端口，不会直接到 3000。需 Nginx 反代：

```bash
apt-get install -y nginx
cat > /etc/nginx/sites-available/moontv << 'EOF'
server {
    listen 80;
    server_name moon.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
ln -sf /etc/nginx/sites-available/moontv /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

**Step 4: CF 域名 DNS + SSL**

1. DNS：A 记录 `moon.yourdomain.com` → 服务器 IP，`proxied: true`（橙色云朵）
2. **CF SSL/TLS 设为 Flexible**（CF ↔ 用户 HTTPS，CF ↔ 服务器 HTTP）。没有 HTTPS 证书的服务端必须用 Flexible，否则 CF 用 HTTPS 回源 → 400 Invalid URL
3. 如果 Token 没 `Zone.Settings` 权限，手动去 CF Dashboard → 域名 → SSL/TLS → 改为 Flexible

**CF Proxy 回源端口排查（新增）**：
- CF Proxy 默认回源到 **80 端口（HTTP）或 443 端口（HTTPS）**，不会到 3000 等自定义端口
- Docker 映射 `80:3000` 可以直接让 CF 回源到 80（需 nginx 未占用 80）
- 如果 443 被 xray/v2ray 占用，只能监听 80 + Flexible SSL
- **Nginx 反代方案**（推荐，解耦 Docker 端口和 CF 回源）：
  ```bash
  apt-get install -y nginx
  cat > /etc/nginx/sites-available/moontv << 'EOF'
  server {
      listen 80;
      server_name moon.yourdomain.com;
      location / {
          proxy_pass http://127.0.0.1:3000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  EOF
  ln -sf /etc/nginx/sites-available/moontv /etc/nginx/sites-enabled/
  rm -f /etc/nginx/sites-enabled/default
  nginx -t && systemctl restart nginx
  ```
- **端口冲突排查**：`ss -tlnp | grep -E "(80|443|3000)"` 检查端口占用
- **Docker 80:3000 与 Nginx 冲突**：如果之前把 Docker 端口改成了 `80:3000`，Nginx 启动会 `bind() to 0.0.0.0:80 failed (98: Address already in use)`。必须先 `sed -i 's/80:3000/3000:3000/' docker-compose.yml && docker compose up -d --force-recreate moontv-core` 释放 80，再启动 Nginx。**用 `ss -tlnp` 确认 80 已释放再启动 Nginx**。
- CF Proxy 回源到无 Host header 的请求 → Next.js 返回 `Invalid URL [no URL]`。确认 Nginx 已设 `proxy_set_header Host $host`

**优势**：Redis 持久化（`/opt/moontv/data`），升级重拉镜像即可，不丢数据。2GB 内存服务器足够。无跨账户 1014 问题。

### 免登录观看 + 管理面板锁定

**需求**：访客免登录观看，管理员配置受保护。

**⚠️ 坑**：`PASSWORD=""` 空密码**不行** — MoonTVPlus middleware 检测到无密码会强制跳转 `/warning` 页面（404），不是免登录。必须设一个弱密码。

**方案**：Nginx htpasswd 锁 `/admin` 路径 + 弱密码公开。

```bash
# 1. 生成 htpasswd（管理员认证）
apt-get install -y apache2-utils
htpasswd -cb /etc/nginx/.htpasswd admin 7452322

# 2. Nginx 配置
cat > /etc/nginx/sites-available/moontv << 'EOF'
server {
    listen 80;
    server_name moon.yourdomain.com;

    location /admin {
        auth_basic "Admin Area";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
nginx -t && systemctl reload nginx

# 3. Docker 设弱密码（不能空！空密码→/warning 页面）
sed -i 's/PASSWORD=.*/PASSWORD=visitor/' docker-compose.yml
docker compose up -d --force-recreate moontv-core
```

**效果**：访客登录页输 `visitor` → 正常观看。进 `/admin` → Nginx 弹窗 admin/7452322。TMDB Key、视频源等全部锁死。

**TG Bot 替代方案**：MoonTVPlus 内置 TG Bot 登录功能，用户扫码/点链接 → TG Bot 确认 → 自动登录网站。配置后可直接用 TG 登录，连 visitor 密码都不需要。管理面板 → Telegram 配置 → 填入 Bot Token。

### 路径 B：GitHub Actions
1. 设 secrets：`CLOUDFLARE_API_TOKEN`、`CLOUDFLARE_ACCOUNT_ID`、`PASSWORD`、`USERNAME`
2. 用 libsodium 加密 secret value 后 PUT `/repos/{owner}/{repo}/actions/secrets/{name}`
3. 触发 `workflow_dispatch`：POST `/repos/{owner}/{repo}/actions/workflows/{id}/dispatches`
4. 坑：workflow 需先在 GitHub 被索引（确认 Actions 已启用）

### 路径 B：本地构建 + wrangler

**注意**：Next.js `@opennextjs/cloudflare` 项目 build 后部署到 **Workers**（不是 Pages）。wrangler.toml 的 `main` 指向 `.open-next/worker.js`。

```bash
git clone && pnpm install --frozen-lockfile
# 修改 wrangler.toml：去 D1，加 [vars] 环境变量

# 先验证凭据
npx wrangler whoami
# Global Key 用: CLOUDFLARE_API_KEY + CLOUDFLARE_EMAIL
# API Token 用: CLOUDFLARE_API_TOKEN

# 构建 + 部署
CLOUDFLARE_API_KEY=cfk_xxx CLOUDFLARE_EMAIL=xxx@gmail.com \
  CLOUDFLARE_ACCOUNT_ID=xxx pnpm run build:cloudflare
npx wrangler deploy
```

**wrangler 环境变量对照**：
- Global Key → `CLOUDFLARE_API_KEY` + `CLOUDFLARE_EMAIL`
- API Token → `CLOUDFLARE_API_TOKEN`
- 两者都需要 `CLOUDFLARE_ACCOUNT_ID`

## MoonTVPlus 特殊配置

### 环境变量
- 存储：`localstorage`（非 D1），设 `NEXT_PUBLIC_STORAGE_TYPE=localstorage`
- wrangler.toml 需删 `[[d1_databases]]` 块
- 必设：`USERNAME`、`PASSWORD`
- 视频源订阅：`CONFIG_SUBSCRIPTION_URL` — Base58 编码的配置 URL

### TMDB 配置

TMDB 提供影片封面、评分、简介。需在 https://www.themoviedb.org/settings/api 申请。

两个环境变量都加上：
- `TMDB_API_KEY` — API 密钥（短字符串，如 `091246c70f20fe1fb6ef85ef9041f532`）
- `TMDB_ACCESS_TOKEN` — API 读访问令牌（JWT 长字符串，Bearer token 格式）

Docker 示例：
```yaml
environment:
  - TMDB_API_KEY=your_api_key
  - TMDB_ACCESS_TOKEN=your_jwt_token
```

### 注册功能开启

MoonTVPlus 默认关闭注册。**不要改源码或瞎折腾**，用项目已有的机制：

**方法 1：管理面板（推荐）**
- 登录 admin → `/admin` → 站点设置 → 开启注册
- 需要 Redis 模式 + USERNAME 环境变量（`USERNAME=admin`）

**方法 2：直接改 Redis（无 admin 账号时的死锁解法）**
```bash
# Redis 模式下，admin 用户需先注册。但注册功能没开 → 死锁。
# 直接改 Redis 里的 admin:config
docker exec moontv-redis redis-cli -a moontv-redis-2024 GET "admin:config" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); d['SiteConfig']['EnableRegistration']=True; print(json.dumps(d,ensure_ascii=False))" | \
  docker exec -i moontv-redis redis-cli -a moontv-redis-2024 -x SET "admin:config"
docker restart moontv-core
```
改完后用户可自行注册，admin 先注册后成为 owner。

**⚠️ 教训**：成熟项目有自己的机制，别自己造轮子。用户说"不要瞎改"时立即回滚多余改动，恢复项目原生行为。

### 视频源 vs Pansou 网盘搜索
- **视频源**：`CONFIG_SUBSCRIPTION_URL`，在线直接播放，搜索即看
- **Pansou**：网盘搜索（阿里云盘/夸克/百度），需额外部署 `fish2018/pansou`，搜到的是网盘链接需转存
- 大多数人用视频源就够了，Pansou 需在管理面板单独填 API 地址

### 公开视频源

**hafrey1/LunaTV-config**（最活跃，每日自动检测 API 状态）：
- `https://pz.v88.qzz.io?format=2&source=jingjian` — 61 个（精简+成人，推荐）
- `https://pz.v88.qzz.io?format=2&source=jin18` — 31 个（纯普通）
- `https://pz.v88.qzz.io?format=2&source=full` — 88 个（完整）
- 输出格式：`format=2` = Base58 编码（适合 `CONFIG_SUBSCRIPTION_URL`），`format=1` = 带代理前缀 JSON
- 也可用 raw URL（不依赖第三方 Worker）：`https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.txt`（88 个完整版）、`jingjian.txt`（61 个）、`jin18.txt`（31 个）
- **建议直接用 raw URL**：`https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.txt` — 不依赖 pz.v88.qzz.io 第三方代理，最稳定。**实战验证**：raw URL 和 proxy URL 均可正常拉取（200），raw URL 零依赖更可靠。

**其他活跃仓库**：
- qianqikun/LunaTV-config：`https://raw.githubusercontent.com/qianqikun/LunaTV-config/refs/heads/main/jingjian.txt`（★49，2026-08 更新）
- fmynj/lunatv-config：同 hafrey1 fork
- DUQIA/LunaTV-config：同 hafrey1 fork
- 完整视频源仓库列表：`references/lunatv-video-sources.md`

### 更新 Worker 环境变量
不能直接 PATCH settings 端点（405）。重新 `wrangler deploy` 最快：
1. 改 wrangler.toml 的 `[vars]`
2. `pnpm run build:cloudflare && npx wrangler deploy`

### 完整部署实录
- `references/moontvplus-deploy.md` — CF Workers 部署 + Docker 部署全程实录（含认证排查、跨账户域名 1014 处理、GitHub API 头要求）

## 自定义域名绑定

### 同账户
直接 Workers → Triggers → Routes 或 Custom Domains 绑定。

### 跨账户 CNAME（域名在另一个 CF 账户）
1. 在域名所在账户加 CNAME 记录：`sub.domain.com` → `worker-name.username.workers.dev`
2. 设置 `proxied: true`（橙色云朵）
3. **关键**：在 Worker 所在账户绑定自定义域名：
   `PUT /accounts/{worker_acct}/workers/domains` → `{"hostname":"sub.domain.com","service":"worker-name","environment":"production"}`
4. 不绑定 Workers 域名直接 CNAME → CF 返回 1014（CNAME cross-account blocked）
5. 需要域名账户的 API Token 有 `Zone.DNS:Edit` 权限
6. 实战案例：`moon.1314k.eu.org` CNAME → `moontv.q429475645.workers.dev`，两个不同 CF 账户，需先绑定 Workers 域名再改 CNAME 为 proxied

## 故障速查

| 症状 | 原因 |
|------|------|
| wrangler 认证失败 | 先用 `wrangler whoami` 验证 — Global Key 用 `CLOUDFLARE_API_KEY`+`CLOUDFLARE_EMAIL`，API Token 用 `CLOUDFLARE_API_TOKEN` |
| GitHub API → 401 "Bad credentials" | 缺少 `Accept: application/vnd.github+json` + `X-GitHub-Api-Version: 2022-11-28` 头（即使 token 有效）。**所有 GitHub REST API 调用必须加这两个头**，否则 PAT 返回 401。先 `/user` 验证 token+头组合正确再操作。 |
| API Token → 1000 "Invalid API Token" | Token 过期/无效 |
| API Token → 10000 "Authentication error" | 权限不足或 Account ID 不对，也可能是用了 `Authorization: Bearer` 但实际是 Global Key |
| Global Key → 9103 "Unknown X-Auth-Key or X-Auth-Email" | Email 或 Key 错误；`cfk_` 开头的 key 必须配 `X-Auth-Email` 不能用 `Bearer` |
| workflow dispatch → 404 | workflow 未被 GitHub 索引（Actions 未启用或 workflow 文件未被扫描） |
| Worker 域名访问 403 error 1014 | 跨账户 CNAME 到 Workers 被拦截。**修复顺序**：①Worker 账户 `PUT /workers/domains` 绑定自定义域名 → ②域名账户 CNAME 设 `proxied:true`。只做 CNAME 不绑 Workers domain 必 1014。绑定后可能仍需几分钟 DNS 传播。 |
| GitHub REST API → 401 \"Bad credentials\" 即使 token 有效 | **所有 GitHub REST API 调用必须加 `Accept: application/vnd.github+json` + `X-GitHub-Api-Version: 2022-11-28` 头**。不加这两个头 PAT 返回 401。验证方法：`curl -H \"Authorization: Bearer <token>\" -H \"Accept: application/vnd.github+json\" -H \"X-GitHub-Api-Version: 2022-11-28\" https://api.github.com/user` |
| CNAME proxied=true 导致 403（非 1014） | CF Proxy 可能拦截 Workers 的响应。先试 proxied=false 确认 DNS 直通再开 proxied。Worker 内部 307 重定向被 CF Proxy 转 403 的常见原因：SSL 模式不匹配、WAF 规则触发、或**未先在 Worker 账户绑定域名**（此时表现为 1014，不是 403。若已是 403 可能是 DNS 缓存残留或 Worker 绑定未生效，等几分钟再试） |
| 403 error code: 1014 跨账户 | **修复顺序**：①Worker 账户 `PUT /workers/domains` 绑定自定义域名 → ②域名账户 CNAME 设 `proxied:true`。只做 CNAME 不绑 Workers domain 必 1014。绑定后可能仍需几分钟 DNS 传播。**若 proxied=false 仍 1014，说明域名 Zone 开启了 proxy flattening，先确保 Workers 绑定成功后再改 proxied=true** |
| Docker + CF Proxy 返回 400 Invalid URL | SSL/TLS 模式不对。CF 用 HTTPS 回源但服务器只监听 HTTP。**改为 Flexible SSL**（CF Dashboard → 域名 → SSL/TLS → Flexible）。Token 无 Zone.Settings 权限时需手动操作。 |
| CF Proxy + Docker 回源端口不对 | CF Proxy 默认回源 80(HTTP) 或 443(HTTPS)，不会到 3000。方案：①Docker 映射 80:3000 + Flexible SSL；②Nginx 反代 80→3000；③Origin Rules 改回源端口（需 Zone 权限）。优先用 Nginx 方案，最灵活。 |
| 443 端口被 xray/v2ray 占用 | 无法监听 443 做 HTTPS 回源。只能用 Flexible SSL + 80 端口回源。Nginx 只监听 80，CF 用 HTTP 回源。**注意**：如果 Docker 已经映射了 80 端口（如 `80:3000`），Nginx 会 bind 失败。必须先把 Docker 端口改回 `3000:3000` 再启动 Nginx。用 `ss -tlnp` 检查占用。 |

---

## saas-api-bypass

# SaaS API Bypass Pattern

When a site is behind Cloudflare but uses a third-party SaaS for data queries, the SaaS API often has a **public token** hardcoded in frontend JS. Call it directly — no CF needed.

## Discovery Flow

1. **GitHub search**: `site:github.com <target> scraper api` → find third-party clients
2. **Frontend JS search**: grep for `recombee.com`, `algolia.net`, `firebaseio.com`, `supabase.co`
3. **Extract public token**: search for `publicToken`, `searchOnlyKey`, `apiKey`, `appId`
4. **Verify permissions**: public tokens often restricted to search-only

## Recombee (missav.ai case)

### Auth: HMAC-SHA1

```python
import time, hmac, hashlib

def sign(path, database, public_token):
    ts = int(time.time())
    uri = f"/{database}{path}"
    uri += f"{'&' if '?' in uri else '?'}frontend_timestamp={ts}"
    sig = hmac.new(public_token.encode(), uri.encode(), hashlib.sha1).hexdigest()
    return uri + f"&frontend_sign={sig}"
```

### Endpoint

```
POST /{database}/search/users/{userId}/items/
Body: {"searchQuery": "...", "count": N, "cascadeCreate": true, "returnProperties": true}
```

Returns: id, title (multi-lang), duration, actresses, genres, poster, images, score.

### Limits

| Feature | Status |
|---------|--------|
| Search | ✅ Public token |
| Metadata | ✅ returnProperties |
| Images | ✅ Separate CDN, no auth |
| Recommendations | ❌ 405 |
| Detail API | ❌ Needs private token |

### Response Field Reference (missav)

```json
{
  "id": "ssis-001",
  "values": {
    "title": "日文标题",
    "title_en": "English", "title_cn": "中文", "title_zh": "繁体", "title_ko": "韩文",
    "actresses": ["演员"],
    "genres": ["标签"],
    "labels": ["厂商"],
    "markers": ["系列"],
    "directors": ["导演"],
    "duration": 7200,
    "released_at": 1616112000.0,
    "img_url": "海报URL",
    "has_chinese_subtitle": true,
    "is_uncensored_leak": false,
    "type": "normal"
  }
}
```

### type Enumeration

| type | 说明 |
|------|------|
| `normal` | 有码 |
| `uncensored-leak` | 无码泄露 |
| `fc2` | FC2 |
| `tokyohot` | Tokyo Hot |
| `1pondo` | 一本道 |
| `caribbeancom` | 加勒比 |
| `heyzo` | HEYZO |
| `madou` | 麻豆 |
| `twav` | 台湾AV |

### m3u8 Extraction (CF-protected HTML only)

```python
import re
regex_m3u8 = re.compile(r"'m3u8(.*?)video")

def extract_m3u8(html: str) -> str:
    """Extract m3u8 from missav video page HTML."""
    match = regex_m3u8.search(html)
    if not match:
        raise ValueError("m3u8 pattern not found")
    parts = match.group(1).split("|")[::-1]  # reverse
    # parts: ["", seg5, seg4, seg3, seg2, seg1, domain, subdomain, protocol]
    return f"{parts[1]}://{parts[2]}.{parts[3]}/{parts[4]}-{parts[5]}-{parts[6]}-{parts[7]}-{parts[8]}/playlist.m3u8"
```

### Player Integration Flow

```
Recombee search (no CF) → get video list with metadata
  → user clicks → browser opens missav.ws/en/{id} (CF-protected)
  → extract m3u8 from HTML → hls.js/video.js playback
```

## Algolia

```python
headers = {"X-Algolia-Application-Id": app_id, "X-Algolia-API-Key": search_only_key}
# POST https://{app_id}-dsn.algolia.net/1/indexes/{index}/query
```

## Pitfalls

1. **Public token permissions vary** — missav locks to search-only.
2. **Token rotation** — site can change token anytime.
3. **Not all data is in SaaS** — missav's homepage and m3u8 URLs come from SSR HTML (CF-protected).
4. **GitHub-first search** — check for existing third-party clients before analyzing JS bundles.
5. **`cascadeCreate` may be required** — missing it can cause 404 on search (Recombee-specific).
6. **Proxy pool ≠ usable proxies** — GitHub IP lists are often bare IPs for Z-Library/other services, not SOCKS/HTTP proxies. Verify protocol and port before assuming they work.

## Reference

- missav.ai: EchterAlsFake/unofficial-api-for-missav (GitHub)
- Recombee docs: https://docs.recombee.com/api

---

## saas-backend-api-discovery

# SaaS 后端 API 发现

当目标站点使用第三方 SaaS（Recombee、Algolia、Typesense、Firebase 等）作为数据后端时，核心 API 在 SaaS 托管域名上运行，**通常不经过站点自己的 CF/WAF**。

## 核心思路

> 不要死磕过 CF。搜 GitHub 找第三方客户端 → 提取 public token/signature → 直接打 SaaS API。

## 通用工作流

### Step 1: 识别 SaaS 后端

- 浏览器 DevTools Network 标签 → 过滤 XHR/Fetch
- 找非本站域名的 API 请求：`algolia.net`、`recombee.com`、`typesense`、`firebaseio.com`
- JS bundle 搜索：`algolia`、`recombee`、`typesense`、`firebase`

### Step 2: 搜索 GitHub 第三方实现

```bash
gh search repos "<site> api" --sort=updated
gh search code "<saas_domain>" "<site>" --language=python
```

**开源项目的价值**：提取 public token、database ID、签名算法、端点路径。比自己从混淆 JS 中分析快 10 倍。

### Step 3: 提取认证参数

从开源项目或 JS bundle 中提取：
- Public token / API key
- Database / index / app ID
- 签名算法（如有）
- 端点路径

### Step 4: 实测验证

```bash
curl -s "https://saas-api.example.com/indexes/xxx/search" \
  -H "X-Algolia-API-Key: xxx" \
  -H "X-Algolia-Application-Id: xxx" \
  -d '{"query": "test"}'
```

### Step 5: 确定权限边界

SaaS public token 通常有限制。测试：
- 搜索 ✅（通常开放）
- 推荐/列表 ⚠️（可能 405/401）
- 详情/写操作 ❌（通常需要 private token）

## Recombee 专项

### 签名算法

```python
import time, hmac, hashlib

DATABASE = "xxx"
PUBLIC_TOKEN = "xxx"

def sign(path):
    ts = int(time.time())
    uri = f"/{DATABASE}{path}"
    uri += f"{'&' if '?' in uri else '?'}frontend_timestamp={ts}"
    sig = hmac.new(PUBLIC_TOKEN.encode(), uri.encode(), hashlib.sha1).hexdigest()
    return uri + f"&frontend_sign={sig}"
```

### 搜索端点

```
POST https://client-rapi-{name}.recombee.com/{signed_path}
Body: {"searchQuery": "...", "count": 20, "cascadeCreate": true, "returnProperties": true}
```

### 权限模型

| 端点 | Public Token | Private Token |
|------|-------------|---------------|
| `/search/users/{uid}/items/` | ✅ | ✅ |
| `/recommendations/` | ⚠️ 405 | ✅ |
| `/items/{id}` | ❌ 401 | ✅ |
| `/items/list/` | ❌ 401 | ✅ |

## Algolia 专项

```python
headers = {
    "X-Algolia-API-Key": "xxx",
    "X-Algolia-Application-Id": "xxx"
}
# POST https://{app_id}-dsn.algolia.net/1/indexes/{index}/query
# Body: {"query": "...", "hitsPerPage": 20}
```

## 代理池测试

```python
import asyncio, aiohttp

async def test_socks5(ip, port=1080):
    proxy = f"socks5://{ip}:{port}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("https://target.com", proxy=proxy, timeout=aiohttp.ClientTimeout(total=10)) as r:
                text = await r.text()
                return ip, "OK" if "target_content" in text else "CF_BLOCKED"
    except:
        return ip, "FAIL"

results = await asyncio.gather(*[test_socks5(ip) for ip in ips])
```

## 参考案例

- **references/missav-recombee-api.md** — missav.ai 完整 Recombee API 逆向：HMAC-SHA1 签名、搜索端点、多语言元数据、m3u8 提取、Web 路由映射、用户 API、**Recombee filter 实现全部频道/分类/标签/演员/厂商筛选**、收藏/播放列表 API。已验证 public token 绕过 CF。

## Pitfalls

1. **GitHub 项目可能过时** — 优先按 `updated_at` 排序，选最近的
2. **Public token 权限可能缩紧** — 实际测试每个端点，不要假设
3. **SaaS API 可能有速率限制** — 注意 `X-RateLimit-*` 响应头
4. **代理池质量参差** — 免费 IP 列表（GitHub raw txt）通常全是机房 IP，无法过 Turnstile。且 IP 列表 ≠ 代理 — 需先确认端口和协议（SOCKS/HTTP），裸 IP 不可直接用。本 session 实测 7452323/ip 仓库 60 个 IP 全不通（Z-Library 出口 IP，非 SOCKS/HTTP 代理）
5. **封面/图片 CDN 通常无认证** — 从 SaaS API 拿到数据后，图片 URL 可直接 HTTP GET
6. **Recombee `cascadeCreate` 参数** — 某些数据库要求 `cascadeCreate: true`，缺少会 404（如 missav）
7. **签名时间戳有效期短** — HMAC-SHA1 签名的 `frontend_timestamp` 通常只有几分钟窗口，不要复用旧签名
8. **优先 Recombee 而非硬刚 CF** — missav 模式：Recombee 拿元数据（100% 数据覆盖）→ 只在需要 m3u8 时才过 CF。不要在没有 SaaS 后端的情况下死磕 Turnstile
9. **用户强调"必须破解所有算法"时** — 先确认是否有 SaaS 后端可绕过 CF。如果有，报告"已破解所有数据层算法，仅视频层需 CF"而不是"CF 过不了放弃"
10. **用户要求"全部接口/收藏/标签/分类"时** — 主动列出 Recombee filter 能实现的所有频道、分类、标签、演员、厂商筛选。不要只写搜索和路由。收藏/播放列表需说明 public token 权限限制

---
