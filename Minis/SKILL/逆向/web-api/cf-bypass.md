---
name: cf-bypass
description: Cloudflare 绕过全套方案 (2026 更新) — 从请求层(TLS指纹)到浏览器层(SeleniumBase/Pydoll/Scrapling)到Turnstile解法。整合实战测试过的方案和已知局限性。
category: reverse-engineering
triggers:
  - cf bypass
  - cloudflare 绕过
  - turnstile solver
  - flare solverr
  - curl_cffi
  - scrapling
  - seleniumbase
  - pydoll
  - Just a moment
  - Checking your browser
  - Attention Required
  - cf-browser-verification
  - cf-chl-bypass
  - _cf_chl_opt
  - turnstile captcha
  - 403 forbidden cloudflare
  - cloudflare challenge
reference: sk:/reverse-engineering/cf-bypass
---

# Cloudflare Bypass 技能 (2026 更新)

## CF 防护等级矩阵

| 等级 | 防护 | 表现 | 绕过难度 | 推荐工具 |
|------|------|------|---------|---------|
| L0 | 无防护 | 直接返回 | ⭐ | requests / curl |
| L1 | IUAM | "Just a moment..." 5秒盾 | ⭐⭐ | cloudscraper / curl_cffi / FlareSolverr |
| L2 | JS Challenge | `/cdn-cgi/challenge-platform/` | ⭐⭐⭐ | FlareSolverr / Playwright+stealth |
| **L3** | **Turnstile + JS Challenge** | 双重验证 | ⭐⭐⭐⭐ | **SeleniumBase** / **Pydoll** / **Scrapling** |
| L4 | WAF + 完整指纹链 | 全站检测 | ⭐⭐⭐⭐⭐ | 反检测浏览器 + 住宅代理 |

## 新一代 CF 绕过工具 (2026)

### 1. SeleniumBase (推荐首选)

**特点**: UC Mode + CDP Mode + `sb.solve_captcha()`，一键绕过

```python
from seleniumbase import SB

# UC + CDP Mode 绕过 CF Turnstile
with SB(uc=True, test=True, locale="en") as sb:
    url = "https://gitlab.com/users/sign_in"
    sb.activate_cdp_mode(url)
    sb.sleep(2)
    sb.solve_captcha()  # 自动处理未被绕过的 CAPTCHA
    # 继续操作...
    sb.assert_text("Username", '[for="user_login"]', timeout=3)
```

**安装**: `pip install seleniumbase`

**关键特性**:
- `uc=True` — Undetected-Chromedriver 模式
- `activate_cdp_mode()` — CDP 隐蔽模式
- `sb.solve_captcha()` — 自动解决 CAPTCHA
- 支持 Chrome-for-Testing / Edge / Brave 多浏览器

### 2. Pydoll (异步原生)

**特点**: 零 WebDriver 依赖，异步原生，内置 Turnstile 处理

```python
import asyncio
from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions

async def main():
    options = ChromiumOptions()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.webrtc_leak_protection = True

    async with Chrome(options=options) as browser:
        tab = await browser.start()
        # 一行绕过 CF
        async with tab.expect_and_bypass_cloudflare_captcha() as wait:
            await tab.go_to('https://protected-site.com')
            await wait
        print(await tab.title)

asyncio.run(main())
```

**安装**: `pip install pydoll`

**关键特性**:
- `expect_and_bypass_cloudflare_captcha()` — 自动绕过
- `enable_auto_solve_cloudflare_captcha()` — 持续自动解决
- `humanize=True` — 贝塞尔曲线鼠标轨迹 + 打字错误模拟
- 零 WebDriver → `navigator.webdriver` 为 undefined（不是 false）

### 3. Scrapling (自适应 + MCP)

**特点**: 自适应解析 + MCP Server + StealthyFetcher

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

# 一键绕过 Cloudflare
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare')
    data = page.css('#padded_content a').getall()

# 自适应模式（网站结构变化后自动重定位元素）
StealthyFetcher.adaptive = True
page = StealthyFetcher.fetch('https://example.com', headless=True)
products = p.css('.product', auto_save=True, adaptive=True)
```

**安装**: `pip install scrapling`

**关键特性**:
- `StealthyFetcher` — 内置 CF Turnstile 绕过
- `adaptive=True` — 网站结构变化后自动重定位
- MCP Server — AI 辅助爬取
- `ProxyRotator` — 内置代理轮换

### 4. Esonhugh Pydoll CF WAF Bypasser

Claude Code 插件，8 个即用模板：

```bash
# 安装
/plugin marketplace add esonhugh/pydoll-cf-waf-bypasser-skills
/plugin install pydoll-antibot-bypasser@pydoll-cf-waf-bypasser-skills

# 或手动
git clone https://github.com/Esonhugh/pydoll-cf-waf-bypasser-skills.git
```

模板列表：`basic_browser`, `bypass_cloudflare`, `web_scraping`, `form_filling`, `hybrid_automation`, `screenshot`, `concurrent_scraping`, `stealth_browser`

## 传统方案（仍有效）

### Level 1: TLS 指纹层（最轻量）

```python
from curl_cffi import requests

r = requests.get('https://target.com', impersonate='chrome131')
```

局限性: 仅过 TLS 指纹检测，Turnstile/JS Challenge 无效。

### Level 2: cloudscraper

```python
import cloudscraper
scraper = cloudscraper.create_scraper()
r = scraper.get('https://target.com')
```

局限性: 仅过基础 IUAM，Turnstile 无效。

### Level 3: FlareSolverr

```python
import requests
payload = {
    "cmd": "request.get",
    "url": "https://target.com",
    "maxTimeout": 60000,
    "proxy": {"url": "http://user:pass@proxy:port"}
}
r = requests.post('http://localhost:8191/v1', json=payload)
```

部署: `docker run -d -p 8191:8191 ghcr.io/flaresolverr/flaresolverr:latest`

### Level 4: Playwright + stealth

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        '--no-sandbox', '--disable-blink-features=AutomationControlled'
    ])
    context = browser.new_context(
        user_agent='Mozilla/5.0 ...',
        locale='zh-CN', timezone_id='Asia/Shanghai'
    )
    page = context.new_page()
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.chrome = { runtime: {} };
    """)
    page.goto('https://target.com', wait_until='domcontentloaded')
```

## Turnstile 绕过详解

### Turnstile 本质

Cloudflare Turnstile 是替代 reCAPTCHA 的验证码系统，通过 JavaScript 挑战 + 行为分析判断用户是否为机器人。

### Turnstile token 获取方式

| 方式 | 可行性 | 说明 |
|------|--------|------|
| SeleniumBase `solve_captcha()` | ✅ 推荐 | 内置一键解决 |
| Pydoll `expect_and_bypass_cloudflare_captcha()` |✅ 推荐 | 原生异步 |
| Scrapling `solve_cloudflare=True` | ✅ 推荐 | 自适应框架 |
| 第三方 solver (2captcha/CapSolver) | ⚠️ 需费用 | API 调用 |
| turnstile_solver (patchright) | ⚠️ 不稳定 | 动态 sitekey 问题 |
| 纯 HTTP 库 (curl/requests) | ❌ 不可能 | 需浏览器 JS 执行 |
| 复用 token | ❌ 不可能 | token 绑定 IP+会话，有效期极短 |

### 动态 sitekey 处理

```python
# Pydoll 自动提取 sitekey
from pydoll.browser import Chrome

async with Chrome(options=options) as browser:
    tab = await browser.start()
    await tab.go_to(url)
    # 自动从页面提取 Turnstile sitekey
    # expect_and_bypass_cloudflare_captcha() 内部处理
```

### Turnstile 用户脚本绕过（Tampermonkey）

```javascript
// 1. 拦截 isTrusted
Element.prototype._addEventListener = Element.prototype.addEventListener;
Element.prototype.addEventListener = function () {
    let args = [...arguments];
    let temp = args[1];
    args[1] = function () {
        let args2 = [...arguments];
        args2[0] = new EventModifier(args2[0], { isTrusted: true });
        return temp(...args2);
    };
    return this._addEventListener(...args);
};

// 2. 创建 Turnstile iframe
const iframe = document.createElement('iframe');
iframe.srcdoc = `<div class="cf-turnstile" data-sitekey="${sitekey}"></div>
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" defer></script>`;

// 3. MutationObserver 捕获 token
const observer = new MutationObserver(() => {
    const input = document.querySelector('input[name="cf-turnstile-response"]');
    if (input && input.value) console.log('Token:', input.value);
});
observer.observe(document, { attributes: true, attributeFilter: ['value'], subtree: true });
```

## 辅助绕过策略

### 策略 1：找无 CF 子域名

```bash
# 主站有 CF，API 子域名可能没有
# 检查 api. / m. / app. 子域名
dig api.target.com
dig m.target.com
```

### 策略 2：中转缓存

- Google 缓存: `https://webcache.googleusercontent.com/search?q=cache:target.com`
- Wayback Machine: `https://web.archive.org/web/*/target.com`

### 策略 3：Minis 浏览器自动验证

Minis 浏览器基于 WebKit，天然支持 Turnstile 自动渲染和验证：

```
browser_use navigate → Turnstile 自动渲染 → 验证通过 → get_cookies 提取 cf_clearance → curl 复用
```

## 推荐策略决策树

```
遇到 CF 保护 →
├── 只需 TLS 指纹绕过？
│   └── curl_cffi (impersonate='chrome131')
│
├── 只需过 IUAM/JS Challenge？
│   ├── cloudscraper（轻量）
│   ├── FlareSolverr（部署即用）
│   └── Playwright + stealth
│
├── 需要过 Turnstile？
│   ├── SeleniumBase UC+CDP（推荐，最稳定）
│   ├── Pydoll async（高性能异步）
│   ├── Scrapling StealthyFetcher（大规模+自适应）
│   └── FlareSolverr + 住宅代理
│
├── 全站 CF 保护（含 API）？
│   ├── 找 m./api. 子域名（无 CF 版本）
│   ├── 住宅代理 + 反检测浏览器
│   └── Minis 浏览器自动验证 → Cookie 复用
│
└── Turnstile + JS Challenge 双重保护？
    ├── 住宅代理 (BrightData/IPRoyal) + SeleniumBase
    └── 或放弃纯自动化，改浏览器自动化 + 人工
```

## 已知局限

1. **Turnstile + JS Challenge 双重重保护** — 无机房 IP 时需住宅代理
2. **需要住宅代理** — 机房 IP 被 CF 标记，所有方案都受限
3. **动态 sitekey** — 每次刷新不同，无法硬编码
4. **Token 有效期极短** — 几分钟后过期，不可复用
5. **全站 CF 保护** — API 端点也被保护，纯 HTTP 方案无效
6. **Turnstile token 自动化** — 仅浏览器自动化可获取，纯 HTTP 不可能

## 代理推荐

| 代理 | 类型 | 价格 | 特点 |
|------|------|------|------|
| BrightData | 住宅/数据中心 | $0.6/GB起 | 最大网络，7200万+ IP |
| IPRoyal | 住宅 | $0.8/GB起 | 性价比高 |
| Swiftproxy | 住宅 | $0.49/GB起 | 8000万+ IP |
| NodeMaven | 住宅 | $0.6/GB起 | 高质量 IP |

