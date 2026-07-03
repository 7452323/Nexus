---
name: cf-bypass
description: Cloudflare 绕过全套方案 — 从请求层(TLS指纹)到浏览器层(Playwright/patchright/nodriver)到Turnstile解法。包含实战测试过的方案和已知局限性。
category: reverse-engineering
triggers:
  - cf bypass
  - cloudflare 绕过
  - turnstile solver
  - flare solverr
  - curl_cffi
  - scrapling
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

# Cloudflare Bypass 技能

来源: https://github.com/Esonhugh/pydoll-cf-waf-bypasser-skills（Pydoll Antibot Bypasser）

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

详见 `references/pydoll-bypass-guide.md`。

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

详见 `references/pydoll-bypass-guide.md`。

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
| scrapling | ✅ 已装 | 0.4.8 | pip |
| FlareSolverr | ✅ 已部署 | 3.5.0 | Docker: `localhost:8191` |
| undetected-chromedriver | ✅ 已装 | 3.5.5 | pip |
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

## Turnstile 用户脚本绕过模式（Tampermonkey/Greasemonkey）

对于 Turnstile 启用的站点，可以编写用户脚本（Userscript）在浏览器环境中自动完成验证并获取 token。

### 原理

用户脚本通过以下步骤在浏览器中绕过 Turnstile：

1. **创建隐藏 iframe** — 加载 challenges.cloudflare.com/turnstile/v0/api.js
2. **注入 Turnstile widget** — iframe 内添加 `<div class="cf-turnstile" data-sitekey="xxx">`，api.js 自动渲染并验证
3. **事件伪造** — 拦截 `isTrusted` 事件属性，设 `isTrusted: true` 使得 Turnstile 认为用户真实交互
4. **MutationObserver 捕获 token** — 监控 `<input name="cf-turnstile-response">` 的值变化，获取生成的 token
5. **postMessage 返回** — 通过 window.postMessage 将 token 送回主页面

### 关键代码模式

```javascript
// 1. 修改 Turnstile 的 iframe 监听，拦截 isTrusted
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

// 2. 创建带 Turnstile widget 的 iframe
const iframe = document.createElement('iframe');
iframe.srcdoc = `<div class="cf-turnstile" data-sitekey="${sitekey}"></div>
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" defer></script>`;

// 3. MutationObserver 捕获 token
const observer = new MutationObserver(() => {
    const input = document.querySelector('input[name="cf-turnstile-response"]');
    if (input && input.value) {
        console.log('Turnstile token:', input.value);
    }
});
observer.observe(document, { attributes: true, attributeFilter: ['value'], subtree: true });
```

### 局限性

- 需要浏览器环境（Chrome/Firefox + Tampermonkey/Greasemonkey）
- 在 QX/Surge 脚本环境中**不可行**（无 DOM、无 iframe、无 MutationObserver）
- 纯 HTTP 脚本（curl/requests）无法获取 token — Turnstile 需要在真实浏览器中执行 JS

### Surge/QX 签到脚本场景下的 Turnstile 壁垒

当站点的签到/积分接口加了 Turnstile 验证：

1. **POST /api/.../check-in** 必须携带 `{"turnstileToken":"..."}` 参数
2. **token 必须有效** — 空 token、过期 token 都返回 400
3. **token 与 cf_clearance cookie 绑定** — IP/会话变了也不行
4. **token 有效期极短** — 几分钟后过期（实测不到10分钟）
5. **cURL 等纯 HTTP 库无法获取** — Turnstile 是完整的客户端 JS 验证
6. **复用 token 不可行** — 每次签到需要新的有效 token

**此场景下唯一可行的方案：**\\n- 部署基于 Playwright/Patchright 的 token 生成服务（如 `turnstile_solver` pip 包）— ⚠️ **2026-06-08 全方案实测失败**\\n- 或彻底放弃脚本签到，改用浏览器自动化\\n\\n**唯一已知可行的路径（非脚本）：**\\n1. **Tampermonkey 用户脚本** — 在真实浏览器上运行 Greasyfork #502601（CloudFlare Turnstile Token Generator），通过 iframe + 事件伪造获取 token\\n2. **付费解验证码服务** — 2captcha / CapSolver / Anti-Captcha API\\n3. **手动操作** — 用户打开签到页面完成验证，脚本拦截 token 后自动签到\\n\\n**不可行的方案（均已实测失败）：**\\n- 空 token / 空字符串 / null\\n- 带 cf_clearance cookie（不够，Turnstile token 是独立验证）\\n- 从不同 IP 尝试无验证签到（服务端全局强制）\\n- 复用抓包中的历史 token（已过期）\\n- ❌部署 Playwright/Patchright/Camoufox 自动化 token 生成服务（2026-06-08 全方案实测）

## 已知局限

1. **Turnstile + JS Challenge 双重重保护** — 当前环境无代理时无解
2. **需要住宅代理** — 机房 IP 被 CF 标记，所有方案都受限
3. **动态 sitekey** — uaa002.com 每次刷新 sitekey 不同，无法硬编码
4. **Hermes 内置 browser 工具 (CDP) 有时可绕过 JS Challenge** — 非 Turnstile 强保护的 CF 站可能渲染成功。但只能作为"数据观察窗口"使用，无法替代自动化的跨域 HTTP 请求书源。拿到 HTML 后需手动提取。
4. **FlareSolverr 3.5.0** — 无代理时对 Turnstile 超时
5. **Pydoll 版本导入变更** ≥2.x 时 `from pydoll.browser import Chrome`（不是 `from pydoll import Browser`）。`__init__.py` 为空
6. **Pydoll binary_location** 通过 `ChromiumOptions` 传递，不能直接传构造函数
7. **Camoufox (Firefox)** 需要 `xvfb` 运行 headed 模式，headless 模式下 CF 仍然检测为机器人
8. **Turnstile token 自动化获取全方案失败** — 2026-06-08 实战测试（目标：console.lyrebirdemby.com, sitekey: `0x4AAAAAACMZLvSu_zM8QCKA` / 0x4AAAAA 测试级 sitekey）：\n   - ❌ patchright Chromium headless — Turnstile iframe 加载但无 token\n   - ❌ xvfb + patchright Chromium headed — 同样不产生 token\n   - ❌ Camoufox headless — iframe 正常加载，checkbox 找不到\n   - ❌ Camoufox + xvfb headed — 同样失败\n   - ❌ puppeteer-extra + stealth-plugin — Chromium headless，iframe 交互无结果\n   - ❌ Turnstile API 服务自建（Quart HTTP + Camoufox）— token 生成 API 持续返回 timeout\n   - ❌ Themka/Turnstile-Solver 项目 — `api_solver.py` 用 Camoufox 也能启动，但同样拿不到 token\n   - **结论**：即使是 `0x4AAAAA` 开头的测试 sitekey，**所有自动化浏览器方案均无法获取 Turnstile token**

## 推荐策略

```
1. m.uaa002.com (无CF) → 直接用 requests 爬取 ← 当前已使用
2. 如果必须过 www.uaa002.com:
   a. 配住宅代理 (BrightData/IPRoyal)
   b. 部署 turnstile_solver (patchright 引擎)
   c. 或 FlareSolverr + 代理
3. 轻量级 TLS 绕过: curl_cffi (chrome131 指纹)
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
