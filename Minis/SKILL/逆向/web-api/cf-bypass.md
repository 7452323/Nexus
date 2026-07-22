---
name: cf-bypass
description: Cloudflare 绕过全套方案 (2026.07 更新) — 从请求层(TLS指纹)到浏览器层(SeleniumBase/Pydoll/Scrapling/playwright-captcha)到Turnstile解法。整合实战测试过的方案和已知局限性。
category: reverse-engineering
triggers:
  - cf bypass, cloudflare 绕过, turnstile solver, flare solverr, curl_cffi, scrapling,
  - seleniumbase, pydoll, playwright-captcha, ClickSolver, Just a moment,
  - Checking your browser, Attention Required, cf-browser-verification, cf-chl-bypass,
  - _cf_chl_opt, turnstile captcha, 403 forbidden cloudflare, cloudflare challenge
---

# Cloudflare Bypass 技能 (2026.07 更新)

## CF 防护等级矩阵

| 等级 | 防护 | 表现 | 推荐工具 |
|------|------|------|---------|
| L0 | 无防护 | 直接返回 | requests / curl |
| L1 | IUAM | "Just a moment" 5秒盾 | cloudscraper / curl_cffi / FlareSolverr |
| L2 | JS Challenge | `/cdn-cgi/challenge-platform/` | FlareSolverr / Playwright+stealth |
| L3 | Turnstile + JS Challenge | 双重验证 | **SeleniumBase** / **Pydoll** / **Scrapling** / **playwright-captcha** |
| L4 | WAF + 完整指纹链 | 全站检测 | 反检测浏览器 + 住宅代理 |

## 新一代 CF 绕过工具 (2026.07)

### 1. SeleniumBase (推荐首选)
**特点**: UC Mode + CDP Mode + `sb.solve_captcha()`，一键绕过

```python
from seleniumbase import SB
with SB(uc=True, test=True, locale="en") as sb:
    sb.activate_cdp_mode("https://gitlab.com/users/sign_in")
    sb.sleep(2)
    sb.solve_captcha()  # 自动处理未被绕过的 CAPTCHA
```

### 2. Pydoll (异步原生)
**特点**: 零 WebDriver 依赖，内置 Turnstile 处理

```python
import asyncio
from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions

async def main():
    options = ChromiumOptions()
    options.headless = True
    options.webrtc_leak_protection = True
    async with Chrome(options=options) as browser:
        tab = await browser.start()
        async with tab.expect_and_bypass_cloudflare_captcha() as wait:
            await tab.go_to('https://protected-site.com')
            await wait
asyncio.run(main())
```

### 3. Scrapling (自适应 + MCP)
**特点**: 自适应解析 + MCP Server + StealthyFetcher

```python
from scrapling.fetchers import StealthyFetcher, StealthySession
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare')
    data = page.css('#padded_content a').getall()
```

### 4. playwright-captcha (ClickSolver + TwoCaptchaSolver) (NEW)
**特点**: 基于 Patchright/Camoufox 的 Turnstile 自动点击 + 2Captcha API 双模式

```python
from playwright.sync_api import sync_playwright
from playwright_captcha import ClickSolver, CaptchaType, FrameworkType

async def solve_turnstile():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        framework = FrameworkType.PLAYWRIGHT
        # 使用 Patchright 推荐（绕过 CF 指纹检测）
        async with ClickSolver(framework=framework, page=page) as solver:
            await page.goto('https://2captcha.com/demo/cloudflare-turnstile')
            await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE
            )
```

**两种模式对比**：
| | Click Solver | 2Captcha API |
|---|---|---|
| 费用 | 免费 | ~$3/1000次 |
| 速度 | 2-5秒 | 10-30秒 |
| 需要 stealth browser | 是 (Patchright/Camoufox) | 否 |
| 可靠性 | 高 | 极高 |

**Patchright 集成**（推荐 Turnstile）：
```python
from patchright.sync_api import sync_playwright  # 替换 playwright
# Patchright 是 Playwright 的反检测 fork，更深层次修补 Chrome
async with ClickSolver(framework=FrameworkType.PATCHRIGHT, page=page) as solver:
    await solver.solve_captcha(captcha_container=page, captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE)
```

**Camoufox 集成**（Firefox 反检测）：
```python
from camoufox.sync_api import AsyncCamoufox
async with AsyncCamoufox(headless=False, geoip=True, humanize=True, main_world_eval=True) as browser:
    page = await browser.new_page()
    async with ClickSolver(framework=FrameworkType.CAMOUFOX, page=page) as solver:
        await solver.solve_captcha(captcha_container=page, captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE)
```

### 5. cloudflare-bypass-2026 (5策略整合) (NEW)
**仓库**: https://github.com/1837620622/cloudflare-bypass-2026 (401⭐)

5 种策略：
| # | 脚本 | 策略 | Turnstile | 适用场景 |
|---|------|------|-----------|---------|
| 1 | `bypass.py` | SeleniumBase UC Mode | Yes | 默认单会话 |
| 2 | `simple_bypass.py` | UC + 并行/代理轮换 | Yes | 批量任务 |
| 3 | `bypass_nodriver.py` | nodriver 纯 CDP | Yes | 无 chromedriver |
| 4 | `bypass_curl_cffi.py` | TLS 指纹/Cookie 复用 | No | 旧版 Challenge |
| 5 | `bypass_cdp.py` | SeleniumBase CDP Mode | Yes | 2026 升级路径 |

### 6. Esonhugh Pydoll CF WAF Bypasser
**仓库**: https://github.com/Esonhugh/pydoll-cf-waf-bypasser-skills (209⭐)
Claude Code 插件，8 个即用模板

## 传统方案（仍有效）

### Level 1: TLS 指纹层
```python
from curl_cffi import requests
r = requests.get('https://target.com', impersonate='chrome131')
```

### Level 2: cloudscraper
```python
import cloudscraper
scraper = cloudscraper.create_scraper()
r = scraper.get('https://target.com')
```

### Level 3: FlareSolverr
```python
import requests
payload = {"cmd": "request.get", "url": "https://target.com", "maxTimeout": 60000}
r = requests.post('http://localhost:8191/v1', json=payload)
```

## Turnstile 绕过详解

### token 获取方式

| 方式 | 可行性 | 说明 |
|------|--------|------|
| SeleniumBase `solve_captcha()` | ✅ 推荐 | 内置一键解决 |
| Pydoll `expect_and_bypass_cloudflare_captcha()` | ✅ 推荐 | 原生异步 |
| Scrapling `solve_cloudflare=True` | ✅ 推荐 | 自适应框架 |
| playwright-captcha ClickSolver | ✅ 推荐 | 免费，需 stealth |
| playwright-captcha TwoCaptchaSolver | ✅ 付费 | API 模式 |
| 第三方 solver (2captcha/CapSolver) | ⚠️ 需费用 | API 调用 |
| turnstile_solver (patchright) | ⚠️ 不稳定 | 动态 sitekey |
| 纯 HTTP 库 | ❌ 不可能 | 需浏览器 JS |
| 复用 token | ❌ 不可能 | 绑定 IP+会话 |

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

## 推荐策略决策树
```
遇到 CF 保护 →
├── 只需 TLS 指纹？ → curl_cffi (impersonate='chrome131')
├── 只需过 IUAM/JS？ → cloudscraper / FlareSolverr
├── 需要过 Turnstile？
│   ├── SeleniumBase UC+CDP（最稳定）
│   ├── Pydoll async（高性能异步）
│   ├── Scrapling StealthyFetcher（大规模+自适应）
│   ├── playwright-captcha + Patchright（免费 ClickSolver）
│   └── playwright-captcha + 2Captcha API（付费可靠）
├── 全站 CF 保护？
│   ├── 找 m./api. 子域名
│   ├── 住宅代理 + 反检测浏览器
│   └── Minis 浏览器自动验证 → Cookie 复用
└── Turnstile + JS 双重？
    ├── 住宅代理 + SeleniumBase
    └── 或放弃纯自动化，改浏览器自动化
```

## 已知局限
1. **Turnstile + JS Challenge 双重** — 无机房 IP 时需住宅代理
2. **需要住宅代理** — 机房 IP 被 CF 标记
3. **动态 sitekey** — 每次刷新不同，无法硬编码
4. **Token 有效期极短** — 不可复用
5. **全站 CF 保护** — API 端点也被保护
6. **Camoufox (Firefox)** 需要 xvfb 运行 headed 模式

