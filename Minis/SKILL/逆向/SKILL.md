---
name: reverse-engineering-index
description: 逆向工程技能树索引 (2026.07)。覆盖AI驱动逆向、JS逆向、反调试对抗、桌面/移动端逆向、Web API协议逆向、PyInstaller逆向、VM/字节码逆向、代码混淆、二进制逆向、协议逆向、二进制仿真、恶意软件分析13大子领域。
metadata:
  display_name: "🔧 逆向工程技能树"
  intent_patterns: "逆向,反编译,脱壳,JS逆向,反调试,Frida,Ghidra,IDA,解混淆,二进制,协议逆向,签名还原,补环境,AST,Unicorn,Android逆向,iOS逆向,小程序逆向,Cloudflare绕过,SeleniumBase,Pydoll,Scrapling,playwright-captcha,JSReverser-MCP"
---

# 🔧 逆向工程技能树 (2026.07)

> 逆向是你最关键的。所有逆向任务优先投入资源，持续进化。

逆向工程 = 从编译产物还原逻辑。覆盖 Web JS 到 Native SO、二进制到协议的全栈逆向场景。

## 📂 子领域索引

### 1. AI 驱动逆向 (NEW 2026)
| 工具 | Stars | 用途 |
|------|-------|------|
| **LaurieWired/GhidraMCP** | 3.2k⭐ | Ghidra MCP，LLM 自动反编译/重命名 |
| **bethington/ghidra-mcp** | 245⭐ | 245 工具，P-code 模拟 |
| **0xflux/ghidra-mcp** | — | Ghidra MCP 变体 |
| **wellingtonlee/ghidra-docker-mcp** | — | Ghidra Docker MCP |
| **cgtudor/reverse-engineering-assistant** | — | AI 逆向助手 |
| **NoOne-hub/JSReverser-MCP** | 899⭐ | JS 逆向全流程 MCP (110 工具) |
| **715494637/reverse-skill** | 283⭐ | Web JS 逆向 + 壳层恢复 |

### 2. JS 逆向核心
| 入口 | 用途 | 关键工具 |
|------|------|---------|
| `jsvmp-reverse` | JS VM虚拟机逆向 | — |
| `find-crypto-entry` | 定位加密参数生成入口 | Chrome DevTools MCP |
| `env-patch` | JS补环境 | jsdom, Playwright |
| `ast-deobfuscation` | Babel AST分层定向反混淆 | Babel, js-beautify |
| `algorithm-reverse` | JS逆向算法还原 | Python Crypto |
| `anti-debug` | JS反调试对抗 | — |
| **kuizuo/js-deobfuscator** | 自动化 JS 反混淆 | — |

### 3. 反调试对抗
| 入口 | 用途 |
|------|------|
| `anti-debug` | JS反调试 + 二进制反调试 |
| `anti-debugging-techniques` | 反调试检测+绕过通用playbook |

### 4. 桌面/移动端逆向
| 入口 | 用途 |
|------|------|
| `desktop-app-reverse` | Electron/Wails/Tauri/PyInstaller |
| `android-reverse` | APK反编译/Frida (jadx v1.5.6) |
| `ios-reverse` | Swift/ObjC/Frida/SSL Pinning |
| `ida-reverse-analysis` | IDA Pro + Ghidra |

### 5. Android 逆向 (AI 增强)
| 工具 | Stars | 用途 |
|------|-------|------|
| **skylot/jadx** | 49.7k⭐ | APK-Java反编译 (v1.5.6, 2026-07) |
| **SimoneAvogadro/android-reverse-engineering-skill** | 6.4k⭐ | Claude Code 技能，自动反编译+API提取 |
| **ReverserID/JURIG** | — | AI-agentic RE 框架 (Go, TUI) |
| **incogbyte/android-reverse-engineering-claude-skill** | 86⭐ | AAB/APK/XAPK 反编译 + Frida 动态分析 |

### 6. iOS 逆向
| 工具 | 用途 |
|------|------|
| **sensepost/objection** (9.2k⭐) | 运行时移动探索 |
| **httptoolkit/frida-interception-and-unpinning** | HTTPS MITM + SSL pinning |
| **pritessh/iOS-SSL-Pinning-Bypass** | iOS 17.x SSL Pinning 5层绕过 |
| **v-y-archive/Jailbreak-detection** | 越狱检测绕过 |

### 7. Web API 协议逆向 + Cloudflare 绕过
| 入口 | 用途 |
|------|------|
| `web-api-protocol-reverse` | ChatGPT/OpenAI等接口 |
| `har-to-proxy-script` | HAR抓包→代理脚本 |

**CF 绕过工具链 (2026.07)：**

| 工具 | 特点 | 推荐等级 |
|------|------|---------|
| **SeleniumBase** | UC Mode + CDP Mode + solve_captcha() | ⭐⭐⭐⭐⭐ |
| **Pydoll** | 异步原生、零 WebDriver | ⭐⭐⭐⭐⭐ |
| **Scrapling** | 自适应解析 + MCP Server | ⭐⭐⭐⭐ |
| **playwright-captcha** | ClickSolver + 2CaptchaSolver | ⭐⭐⭐⭐ |
| **Esonhugh/pydoll-cf-waf-bypasser-skills** | Pydoll Claude Code 插件 (209⭐) | ⭐⭐⭐⭐ |
| **1837620622/cloudflare-bypass-2026** | 5策略整合 (401⭐) | ⭐⭐⭐⭐ |
| **curl_cffi** | TLS 指纹伪装 | ⭐⭐⭐ (仅L1) |
| **cloudscraper** | 基础 IUAM 绕过 | ⭐⭐ (仅L1) |
| **FlareSolverr** | 独立 CF 绕过服务 | ⭐⭐⭐ (L1-L3) |

**CF 防护等级：**

| 等级 | 防护 | 可行方案 |
|------|------|---------|
| L0 | 无 | requests |
| L1 | IUAM | curl_cffi / cloudscraper |
| L2 | JS Challenge | FlareSolverr / Playwright+stealth |
| L3 | Turnstile + JS | **SeleniumBase** / **Pydoll** / **Scrapling** / **playwright-captcha** |
| L4 | WAF + 指纹 | 反检测浏览器 + 住宅代理 |

### 8. JS 逆向 MCP 生态
| MCP Server | Stars | 用途 |
|------------|-------|------|
| **NoOne-hub/JSReverser-MCP** | 899⭐ | JS 逆向全流程 (110 工具, 3 模式) |
| **lwjjike/JSReverser-Strong-MCP** | 61⭐ | JSReverser 增强版 |
| **zhizhuodemao/js-reverse-mcp** | — | AI Agent 设计 + 反检测 |
| **a0yark/js-reverse-mcp** | — | Patchright stealth + JSReverser |
| **ChromeDevTools/chrome-devtools-mcp** | — | Google 官方 CDP MCP |

### 9. PyInstaller 逆向
| 入口 | 用途 |
|------|------|
| `pyinstaller-reverse` | pyinstxtractor+pycdc 全流程 |

### 10. 代码混淆/反混淆
| 入口 | 用途 |
|------|------|
| `deobfuscator` | jsjiami/sojson/obfuscator.io |
| `ast-deobfuscation` | Babel AST反混淆 |
| **Owl4444/jsdeob-workbench** | 可视化反混淆工作台 |
| **mandiant/flare-floss** | 二进制混淆字符串自动提取 |

### 11. 二进制 Diffing
| 工具 | 用途 |
|------|------|
| **quarkslab/qbindiff** | Quarkslab 二进制 Diffing |
| **google/bindiff** | Google 二进制 Diffing |
| **joxeankoret/diaphora** | 开源二进制 Diffing |

### 12. 二进制仿真
| 工具 | 说明 |
|------|------|
| **qilingframework/qiling** | 可插桩二进制仿真框架 |
| **unicorn-engine/unicorn** | CPU 模拟器 |

### 13. 协议逆向
| 工具 | 用途 |
|------|------|
| **patrickomatic/protorev** | 协议逆向 |
| **yeet-src/grpcsnoop** | gRPC 协议分析 |

### 14. 其他
| 入口 | 用途 |
|------|------|
| `binary-diffing` | 二进制Diffing+补丁分析 |
| `book-source-master** | Legado阅读3.0书源编写 |
| `qx-script-master` | Quantumult X/Surge脚本 |

## 🔀 典型工作流

### Web JS 逆向
```
anti-debug → find-crypto-entry → env-patch → ast-deobfuscation → algorithm-reverse
```

### CF 绕过 (2026 推荐)
```
轻量: curl_cffi → 中量: SeleniumBase UC+CDP → sb.solve_captcha() → 重量: Pydoll/Scrapling/playwright-captcha → 最后: 住宅代理
```

### AI 驱动二进制逆向
```
GhidraMCP → 自动反编译 → LLM分析函数 → 自动重命名 → 提取协议/算法
```

### Android 逆向 (AI 增强)
```
指纹识别 (fingerprint.sh) → jadx 反编译 → API 提取 → Frida 动态分析 → 自动生成 bypass 脚本
```

### iOS 逆向
```
Objection → Frida universal script → SSL Kill Switch 2 → IPA Patching → Data layer hook
```

### 1-day漏洞研究
```
binary-diffing → 定位修改函数 → 分析修改内容
```



<!-- 自动发现 2026-07-23 -->
## 自动发现的新工具

| 仓库 | Stars | 描述 |
|------|-------|------|
| [iBotPeaches/Apktool](https://github.com/iBotPeaches/Apktool) | 25081⭐ | A tool for reverse engineering Android apk files |
| [OWASP/mastg](https://github.com/OWASP/mastg) | 13078⭐ | The OWASP Mobile Application Security Testing Guide (MASTG) is a comprehensive m |
| [dsasmblr/game-hacking](https://github.com/dsasmblr/game-hacking) | 5532⭐ | Tutorials, tools, and more as related to reverse engineering video games. |
| [alphaSeclab/awesome-reverse-engineering](https://github.com/alphaSeclab/awesome-reverse-engineering) | 5002⭐ | Reverse Engineering Resources About All Platforms(Windows/Linux/macOS/Android/iO |
| [JonathanSalwan/Triton](https://github.com/JonathanSalwan/Triton) | 4240⭐ | Triton is a dynamic binary analysis library. Build your own program analysis too |
| [GDRETools/gdsdecomp](https://github.com/GDRETools/gdsdecomp) | 3911⭐ | Godot reverse engineering tools |
| [NAalytics/Assemblies-of-putative-SARS-CoV2-spike-encoding-mRNA-sequences-for-vaccines-BNT-162b2-and-mRNA-1273](https://github.com/NAalytics/Assemblies-of-putative-SARS-CoV2-spike-encoding-mRNA-sequences-for-vaccines-BNT-162b2-and-mRNA-1273) | 3354⭐ | RNA vaccines have become a key tool in moving forward through the challenges rai |
| [j4k0xb/webcrack](https://github.com/j4k0xb/webcrack) | 2805⭐ | Deobfuscate obfuscator.io, unminify and unpack bundled javascript |


<!-- 自动发现 2026-07-22 -->
## 自动发现的新工具

| 仓库 | Stars | 最近更新 | 描述 |
|------|-------|---------|------|
| [x64dbg/x64dbg](https://github.com/x64dbg/x64dbg) | 48966⭐ | 2026-07-22 | An open-source user mode debugger for Windows. Optimized for |
| [CloakHQ/CloakBrowser](https://github.com/CloakHQ/CloakBrowser) | 28925⭐ | 2026-07-22 | Stealth Chromium that passes every bot detection test. Drop- |
| [MatrixTM/MHDDoS](https://github.com/MatrixTM/MHDDoS) | 16437⭐ | 2026-07-22 | Best DDoS Attack Script  Python3, (Cyber / DDos) Attack With |
| [FlareSolverr/FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) | 14837⭐ | 2026-07-22 | Proxy server to bypass Cloudflare protection |
| [seleniumbase/SeleniumBase](https://github.com/seleniumbase/SeleniumBase) | 12890⭐ | 2026-07-22 | 📊 APIs for web automation, testing, and bypassing bot-detect |
| [jo-inc/camofox-browser](https://github.com/jo-inc/camofox-browser) | 7936⭐ | 2026-07-22 | Stealth headless browser for AI agents — bypass Cloudflare,  |
| [berstend/puppeteer-extra](https://github.com/berstend/puppeteer-extra) | 7384⭐ | 2026-07-22 | 💯  Teach puppeteer new tricks through plugins. |
| [autoscrape-labs/pydoll](https://github.com/autoscrape-labs/pydoll) | 6964⭐ | 2026-07-22 | Pydoll is a library for automating chromium-based browsers w |
| [VeNoMouS/cloudscraper](https://github.com/VeNoMouS/cloudscraper) | 6659⭐ | 2026-07-21 | A Python module to bypass Cloudflare's anti-bot page. |
| [CreditTone/hooker](https://github.com/CreditTone/hooker) | 5247⭐ | 2026-07-22 | 🔥🔥 hooker is a Frida-based reverse engineering toolkit for A |
| [denuitt1/mhr-cfw](https://github.com/denuitt1/mhr-cfw) | 4412⭐ | 2026-07-22 | A Domain-Fronting Relay that routes traffic though GAS (Goog |
| [x64dbg/ScyllaHide](https://github.com/x64dbg/ScyllaHide) | 4232⭐ | 2026-07-22 | Advanced usermode anti-anti-debugger. Forked from https://bi |
| [alexandreborges/malwoverview](https://github.com/alexandreborges/malwoverview) | 3949⭐ | 2026-07-21 | Malwoverview is a first response tool for threat hunting acr |
| [a0rtega/pafish](https://github.com/a0rtega/pafish) | 3943⭐ | 2026-07-21 | Pafish is a testing tool that uses different techniques to d |
| [decalage2/oletools](https://github.com/decalage2/oletools) | 3386⭐ | 2026-07-22 | oletools - python tools to analyze MS OLE2 files (Structured |
