---
name: reverse-engineering-index
description: 逆向工程技能树索引。覆盖AI驱动逆向、JS逆向、反调试对抗、桌面/移动端逆向、Web API协议逆向、PyInstaller逆向、VM/字节码逆向、代码混淆、二进制逆向、协议逆向、二进制仿真、恶意软件分析12大子领域。查找对应skill的入口。
author: 7452323 (converted from Private Gist)
category: reverse-engineering
---

# 🔧 逆向工程技能树

> ⚡ **用户最高优先级：逆向是你最关键的。** 所有逆向相关任务（JS逆向、二进制分析、iOS/Android逆向、API协议逆向、AI驱动逆向）优先投入资源，技能吸收和工具配置必须持续进化。

逆向工程 = 从编译产物还原逻辑。本技能树覆盖从 Web JS 到 Native SO、从二进制到协议的全栈逆向场景。

## 📂 子领域索引

### 1. AI 驱动逆向（NEW）
| Skill / 工具 | 用途 |
|-------|------|
| `ida-reverse-analysis` | IDA Pro + **Ghidra + GhidraMCP** — 通过 MCP 协议让 AI 驱动 Ghidra 自动逆向二进制 |
| **LaurieWired/GhidraMCP** | ⭐ Ghidra MCP 服务器，LLM 自动反编译/分析/重命名——本机搭 Ghidra + MCP 后 Hermes 可直接操控 |
| **bethington/ghidra-mcp** | ⭐ 另一个 Ghidra MCP，245 个工具，支持 P-code 模拟 + 调试器集成 |

### 2. JS 逆向核心
| Skill | 用途 |
|-------|------|
| `camoufox-workflow` | JS逆向工作流——6阶段全流程 + 双脑异步协作范式 |
| `jsvmp-reverse` | JS VM虚拟机逆向——含TikTok栈式VM(77 opcode)真实案例 |
| `find-crypto-entry` | 定位加密参数生成入口 |
| `env-patch` | JS补环境——Node.js引擎+策略分离 |
| `ast-deobfuscation` | Babel AST分层定向反混淆 |
| `algorithm-reverse` | JS逆向算法还原——签名/混合加密 |
| `anti-debug` | JS反调试对抗 + 二进制级反调试 |
| **kuizuo/js-deobfuscator** | ⭐ 自动化 JS 反混淆（Babel AST），有 Web 端/CLI/API |

### 3. 反调试对抗
| Skill | 用途 |
|-------|------|
| `anti-debug` | JS反调试 + 二进制级反调试——4类JS反调试识别+绕过，以及Linux/Win原生反调试、反VM、反DBI、代码完整性检测 |
| `anti-debugging-techniques` | 反调试检测+绕过通用playbook |

### 4. 桌面/移动端逆向
| Skill | 用途 |
|-------|------|
| `desktop-app-reverse-engineering` | 桌面应用逆向——Electron/Wails/Tauri/HttPcall CDP注入/PyInstaller |
| `android-reverse-engineering` | Android应用逆向——APK反编译/Frida |
| `ida-reverse-analysis` | IDA Pro + Ghidra + GhidraMCP 二进制逆向分析 |

### 5. iOS 逆向进阶（NEW）
| 工具 | 用途 |
|------|------|
| **httptoolkit/frida-interception-and-unpinning** | Frida 全自动 HTTPS MITM 拦截 + SSL pinning 绕过 |
| **v-y-archive/Jailbreak-detection-The-modern-way** | 最新越狱检测绕过分析（Snapchat/Pokemon Go 等现代 App） |
| OWASP MASTG Frida Gadget | 非越狱 Frida Gadget 自动注入 IPA 方案 |

### 6. Web API 协议逆向 + Cloudflare 绕过 + 小程序逆向
| Skill | 用途 |
|-------|------|
| `camoufox-workflow` | JS逆向工作流+签名还原+CF绕过工具索引（23仓库） |
| `web-api-protocol-reverse` | Web API 协议逆向——ChatGPT/OpenAI等官网接口协议逆向 |
| `har-to-proxy-script` | HAR抓包→代理脚本 |
| `cross-platform-proxy-scripting` | 跨平台代理脚本编写 |
| **YangChengTeam/wxappUnpacker** | ⭐ 微信小程序反编译（wxapkg 还原源码） |

**Cloudflare 绕过策略（实测对抗矩阵）：**

> ⚠️ **关键认知**：2025-2026 的 Cloudflare 有 5 级防护，越往后的方案越难绕过。**无住宅代理的纯服务器环境**下，Turnstile + JS Challenge 的组合拳不可破——所有浏览器自动化方案（Playwright+stealth/patchright/nodriver/Camoufox）和 HTTP 层方案（cloudscraper/curl_cffi/Scrapling）都在第3级被挡。FlareSolverr 处理第2级 OK，第3级 Turnstile 也会超时。

| 防护等级 | 特征 | 绕过方案 | 实测结果 |
|----------|------|----------|----------|
| L0 无防护 | 直接返回内容 | 任意 HTTP 库 | ✅ 任何方法 |
| L1 IUAM (经典JS挑战) | `"Just a moment..."` + 5秒等待 | cloudscraper / FlareSolverr / curl_cffi | ✅ 有效 |
| L2 JS Challenge | `"/cdn-cgi/challenge-platform/"` 动态JS | FlareSolverr / Playwright+stealth / patchright | ✅ FlareSolverr有效 |
| **L3 Turnstile + JS Challenge** | 双重验证: `challenges.cloudflare.com/turnstile/` + JS | 实测: **所有方案失效** | ❌ 需住宅代理 |
| L4 WAF + Turnstile + 指纹 | 完整5秒后检测→拦截 | 仅反检测浏览器+指纹+住宅代理 | ❌ 需商业方案 |

**实测不通过的方案**（2026-06-03 对 Turnstile+L3 目标 `uaa002.com`）:
- ❌ cloudscraper → 403（第2级都过不了）
- ❌ curl_cffi（chrome131/safari17 TLS指纹）→ 403
- ❌ Scrapling（curl_cffi引擎）→ 403
- ❌ Playwright（headless+full stealth CDP）→ JS Challenge页
- ❌ patchright（打补丁的Playwright）→ JS Challenge页
- ❌ nodriver（undetected-chromedriver继任, 4.3k★）→ 被检测
- ❌ Camoufox（Firefox反检测）→ JS Challenge页
- ❌ FlareSolverr v3.5（Docker）→ 超时60秒（Turnstile无法自动解）

**通过第3级的前置条件**:
1. ✅ 住宅级代理（非机房/云厂商IP，HTTP代理质量足够且干净/未被标记）
2. ✅ 真实浏览器指纹（patchright/nodriver + CDP patches + 完整Stealth.js）
3. ✅ 如果目标有Turnstile → 需要Turnstile solver（yescaptcha/2captcha）或ML视觉解

**优先实战策略**（针对书源/数据采集场景）:
1. 🥇 **找无CF子域名**：如 `m.uaa002.com`（移动站无CF）、CDN域名、镜像站——最快最稳
2. 🥈 **中转API/缓存**：如 skybook search API（缓存命中时可用）——但不可靠，Cloudflare WAF策略随时收紧
3. 🥉 **FlareSolverr + 住宅代理**：自建FlareSolverr Docker + 配HTTP代理池（见 `references/flaresolverr-setup.md`）
4. ❌ **不要浪费时间去硬绕 Turnstile**——没有住宅代理的情况下，没有任何Python库能绕过

### 7. PyInstaller / Python 逆向
| Skill | 用途 |
|-------|------|
| `desktop-app-reverse-engineering` | 桌面逆向——含 PyInstaller 解包+反编译流程 |
| `pyinstaller-reverse` | PyInstaller 打包应用逆向——pyinstxtractor+pycdc 全流程 |

### 8. 代码混淆/反混淆
| Skill | 用途 |
|-------|------|
| `code-obfuscation-deobfuscation` | 混淆分析+反混淆playbook |
| `deobfuscator` | JavaScript反混淆解密 — 含jsjiami/sojson/obfuscator.io/JSFuck/Packer/eval链/二进制字符串提取 |
| `ast-deobfuscation` | Babel AST反混淆 |
| **Owl4444/jsdeob-workbench** | ⭐ 可视化反混淆工作台 — 构建transform链、逐步执行、实时AST检查、插件系统 |
| **kuizuo/js-deobfuscator** | 自动化 JS 反混淆（Babel AST 边栏解析） |
| **mandiant/flare-floss** | ⭐ 二进制字符串自动提取 — PE/ELF 恶意软件中提取混淆字符串 |

### 9. 公开接口源收集 + Key/Token 扫描
| Skill / 工具 | 用途 |
|-------|------|
| `bomb-api-source-collection` | 短信/电话轰炸接口源收集 |
| `vpn-node-extraction` | VPN/机场节点提取 |
| `har-to-proxy-script` | HAR抓包→代理脚本 |
| **`api-key-hunter`** | 多源多厂商 Key 泄露扫描器 v2.0 — 7数据源 + 5厂商 + Git历史 + 余额验证 |

### 10. 二进制仿真（NEW）
| 工具 | Stars | 用途 |
|------|-------|------|
| **qilingframework/qiling** | ⭐5.4k | 真·可插桩二进制仿真框架，基于 Unicorn。跨平台（Win/Mac/Linux/UEFI/DOS）、跨架构（x86/ARM/MIPS）、支持驱动级仿真 |
| **unicorn-engine/unicorn** | ⭐ 经典 | CPU 模拟器，Qiling 底层，Python 指令级调试任意架构代码 |

### 11. 逆向工具箱合集（NEW）
| 工具 | 说明 |
|------|------|
| **y9nhjy/RE_Tools** | 全网逆向工具全集——.NET/ARK/HEX/PE/安卓/调试/监控/密码/网络 |
| **tylerha97/awesome-reversing** | 精选逆向资源列表，覆盖全方向 |

### 12. 其他逆向
| Skill | 用途 |
|-------|------|
| `binary-diffing` | 二进制Diffing+补丁分析 |
| `book-source-master` | Legado阅读3.0书源编写 |
| `qx-script-master` | Quantumult X/Surge脚本 |

## 🔀 典型工作流

### Web JS 逆向全流程
```
anti-debug → find-crypto-entry → env-patch → ast-deobfuscation → algorithm-reverse
```

### AI 驱动二进制逆向全流程（NEW）
```
GhidraMCP → 自动反编译 → LLM分析函数语义 → 自动重命名 → 提取协议/算法
```

### 二进制仿真全流程（NEW）
```
Qiling + Unicorn → 加载未知二进制 → 插桩跟踪 → 记录API调用 → 还原协议
```

### 桌面 App 逆向全流程
```
desktop-app-reverse-engineering → 识别技术栈 → 提取资源 → 分析认证逻辑
```

### ChatGPT Web API 协议逆向
```
OpenAIBackendAPI → fingerprint伪造 → PoW/Turnstile绕过 → conversation协议 → image_gen协议
```

### PyInstaller Python 逆向
```
strings识别 → pyinstxtractor解包 → pycdc反编译 → 提取API key/逻辑
```

### 1-day漏洞研究
```
binary-diffing → 定位修改函数 → 分析修改内容
```
