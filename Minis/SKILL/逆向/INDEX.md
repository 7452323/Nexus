---
name: reverse-engineering-index
description: 逆向工程技能树索引。覆盖AI驱动逆向、JS逆向、反调试对抗、桌面/移动端逆向、Web API逆向、PyInstaller逆向、VM/字节码逆向、代码混淆、二进制逆向、协议逆向、二进制仿真、恶意软件分析13大子领域。
category: reverse-engineering
---

# 🔧 逆向工程技能树

## 领域总览

逆向工程 = 从编译产物还原逻辑。本技能树覆盖从 Web JS 到 Native SO、从二进制到协议的全栈逆向场景。

**环境**: iSH Alpine Linux aarch64 — 优先浏览器取证 + Python/Node 本地复现。

---

## 📂 子领域索引

### 1. AI 驱动逆向 (NEW 2026)
| 工具 | 用途 | Stars |
|------|------|-------|
| **LaurieWired/GhidraMCP** | Ghidra MCP 服务器，LLM 自动反编译/分析/重命名 | 3.2k |
| **bethington/ghidra-mcp** | 245 个工具，支持 P-code 模拟 | 245 |
| **semba/llm-reverse** | LLM 辅助反编译，自动识别加密算法 | 1.1k |
| **abstract-state/symbolic-execution-mcp** | 符号执行 MCP | new |

### 2. JS 逆向核心
| 入口 | 用途 | 关键工具 |
|------|------|---------|
| `jsvmp-reverse` | JS VM虚拟机逆向——TikTok栈式VM(77 opcode)案例 | — |
| `find-crypto-entry` | 定位加密参数生成入口 | Chrome DevTools MCP |
| `env-patch` | JS补环境——Node.js引擎+策略分离 | jsdom, Playwright |
| `ast-deobfuscation` | Babel AST分层定向反混淆 | Babel, js-beautify |
| `algorithm-reverse` | JS逆向算法还原——签名/混合加密 | Python Crypto |
| `anti-debug` | JS反调试对抗 + 二进制反调试 | — |
| **kuizuo/js-deobfuscator** | 自动化 JS 反混淆（Babel AST） | — |

### 3. 反调试对抗
| 入口 | 用途 |
|------|------|
| `anti-debug` | JS反调试 + 二进制反调试——4类JS反调试绕过+Linux/Win原生反调试、反VM、反DBI |
| `anti-debugging-techniques` | 反调试检测+绕过通用playbook |

### 4. 桌面/移动端逆向
| 入口 | 用途 |
|------|------|
| `desktop-app-reverse` | 桌面应用逆向——Electron/Wails/Tauri/PyInstaller |
| `android-reverse` | Android逆向——APK反编译/Frida |
| `ida-reverse-analysis` | IDA Pro + Ghidra 二进制分析 |

### 5. iOS 逆向
| 工具 | 用途 |
|------|------|
| **httptoolkit/frida-interception-and-unpinning** | Frida 全自动 HTTPS MITM + SSL pinning 绕过 |
| **v-y-archive/Jailbreak-detection** | 越狱检测绕过 |
| OWASP MASTG Frida Gadget | 非越狱 Frida Gadget 注入 |

### 6. Web API 协议逆向 + Cloudflare 绕过

**CF 绕过工具链 (2026)：**

| 工具 | 特点 | 推荐等级 |
|------|------|---------|
| **SeleniumBase** | UC Mode + CDP Mode + solve_captcha() | ⭐⭐⭐⭐⭐ |
| **Pydoll** | 异步原生、零 WebDriver、内置 Turnstile | ⭐⭐⭐⭐⭐ |
| **Scrapling** | 自适应解析 + MCP Server + StealthyFetcher | ⭐⭐⭐⭐ |
| **Esonhugh/pydoll-cf-waf-bypasser-skills** | Pydoll Claude Code 插件，8模板 | ⭐⭐⭐⭐ |
| **curl_cffi** | TLS 指纹伪装 | ⭐⭐⭐ (仅L1) |
| **cloudscraper** | 基础 IUAM 绕过 | ⭐⭐ (仅L1) |
| **FlareSolverr** | 独立服务部署 | ⭐⭐⭐ (L1-L3) |

**CF 防护等级：**

| 等级 | 防护 | 可行方案 |
|------|------|---------|
| L0 | 无 | requests |
| L1 | IUAM | curl_cffi / cloudscraper |
| L2 | JS Challenge | FlareSolverr / Playwright+stealth |
| L3 | Turnstile + JS | **SeleniumBase** / **Pydoll** / **Scrapling** |
| L4 | WAF + 指纹 | 反检测浏览器 + 住宅代理 |

### 7. PyInstaller 逆向
| 入口 | 用途 |
|------|------|
| `pyinstaller-reverse` | pyinstxtractor+pycdc 全流程 |

### 8. 代码混淆/反混淆
| 入口 | 用途 |
|------|------|
| `deobfuscator` | JS反混淆——jsjiami/sojson/obfuscator.io |
| `ast-deobfuscation` | Babel AST反混淆 |
| **Owl4444/jsdeob-workbench** | 可视化反混淆工作台 |
| **mandiant/flare-floss** | 二进制混淆字符串自动提取 |

### 9. 二进制仿真
| 工具 | 说明 |
|------|------|
| **qilingframework/qiling** | 可插桩二进制仿真框架（Unicorn底层） |
| **unicorn-engine/unicorn** | CPU 模拟器，指令级调试任意架构 |

### 10. 其他
| 入口 | 用途 |
|------|------|
| `binary-diffing` | 二进制Diffing+补丁分析 |
| `book-source-master` | Legado阅读3.0书源编写 |
| `qx-script-master` | Quantumult X/Surge脚本 |

---

## 🔀 跨领域关联

- **JS逆向 + 反调试**：env-patch 和 anti-debug 常配合使用——先绕反调试，再补环境
- **JS逆向 + Web API逆向**：find-crypto-entry 定位入口 → web-api-reverse-engineering 构建协议
- **桌面逆向 + SO分析**：desktop-app-unlock 可能需要 so-native-analysis 分析底层 .so
- **VM逆向 + AST反混淆**：jsvmp-reverse 还原VMP时常需 ast-deobfuscation 预处理
- **二进制逆向 + 协议逆向**：先用protocol-re逆向协议格式，再用binary-diffing对比协议变化
- **Android逆向 + SO分析**：android-reverse-engineering 分析Java层，so-native-analysis分析Native层
- **AI + 逆向**：GhidraMCP + LLM 自动反编译，效率提升10倍

---

## 📖 典型工作流

### Web JS 逆向全流程
```
anti-debug（绕反调试）→ find-crypto-entry（定位入口）→ env-patch（补环境）
→ ast-deobfuscation（反混淆）→ algorithm-reverse（还原算法）
→ web-api-to-openai-proxy（构建代理）
```

### CF 绕过 (2026 推荐)
```
轻量: curl_cffi (chrome131 指纹) → 不行则
中量: SeleniumBase UC+CDP Mode → sb.solve_captcha() → 不行则
重量: Pydoll async + Turnstile solver / Scrapling StealthyFetcher → 不行则
最后: 住宅代理 + 反检测浏览器 (BrightData/IPRoyal)
```

### AI 驱动二进制逆向
```
GhidraMCP → 自动反编译 → LLM分析函数 → 自动重命名 → 提取协议/算法
```

### 移动端逆向全流程
```
android-reverse-engineering（APK反编译）→ so-native-analysis（SO分析）
→ ida-reverse-analysis（IDA深入）→ reverse-engineering-general（Frida Hook）
```

### VMP 逆向全流程
```
anti-debug（绕反调试）→ ast-deobfuscation（预处理）→ jsvmp-reverse（VMP还原）
→ algorithm-reverse（算法提取）
```

### 1-day漏洞研究全流程
```
binary-diffing（对比新旧版本）→ 定位修改函数 → 分析修改内容 → 还原漏洞
```

### 协议逆向全流程
```
protocol-reverse-engineering（抓包+分析）→ 识别消息格式 → 推断状态机
→ web-api-reverse-engineering（构建自动化）
```

---

## 🗄️ 知识库

### 工具可用性清单（iSH 环境）

| 场景 | 可用工具 | 不可用 |
|------|---------|--------|
| 页面取证 | ✅ Minis 浏览器 | — |
| JS 拦截 | ✅ execute_js | — |
| Cookie 提取 | ✅ get_cookies | — |
| 本地复现 | ✅ Python3 / Node.js | — |
| HTTP 请求 | ✅ curl / wget | — |
| 加解密 | ✅ openssl / Python crypto | — |
| CF 绕过 | ✅ Minis 浏览器 / SeleniumBase / Pydoll / Scrapling | — |
| 二进制分析 | ❌ 无 IDA/Ghidra | 在线沙箱 |
| APK 分析 | ❌ 无 jadx/JDK | 在线反编译 |
| 动态 Hook | ❌ 无 Frida | 浏览器 CDP |

### 推荐工具链

| 场景 | 推荐 |
|------|------|
| CF L1 绕过 | curl_cffi / cloudscraper |
| CF L2 绕过 | FlareSolverr |
| CF L3 Turnstile | SeleniumBase / Pydoll / Scrapling |
| CF L4 全指纹 | 住宅代理 + 反检测浏览器 |
| JS 反混淆 | Babel AST / kuizuo/js-deobfuscator |
| JS 补环境 | Node.js + jsdom |
| 二进制分析 | Ghidra + GhidraMCP |
| 符号执行 | angr / Triton |
| 二进制仿真 | Qiling / Unicorn |
| 协议逆向 | protobuf-inspector / netzob |

