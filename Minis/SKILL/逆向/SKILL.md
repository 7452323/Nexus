---
name: reverse-engineering-index
description: 逆向工程技能树索引。覆盖AI驱动逆向、JS逆向、反调试对抗、桌面/移动端逆向、Web API协议逆向、PyInstaller逆向、VM/字节码逆向、代码混淆、二进制逆向、协议逆向、二进制仿真、恶意软件分析12大子领域。
metadata:
  display_name: "🔧 逆向工程技能树"
  intent_patterns: "逆向,反编译,脱壳,JS逆向,反调试,Frida,Ghidra,IDA,解混淆,二进制,协议逆向,签名还原,补环境,AST,Unicorn,Android逆向,iOS逆向,小程序逆向,Cloudflare绕过"
---

# Purpose

逆向工程 = 从编译产物还原逻辑。覆盖 Web JS 到 Native SO、二进制到协议的全栈逆向场景。当用户提到任何逆向相关需求时触发本技能选择对应子领域入口。

# How to Use

## 子领域索引（12个）

### 1. AI 驱动逆向
| Skill / 工具 | 用途 |
|-------|------|
| `ida-reverse-analysis` | IDA Pro + Ghidra + GhidraMCP — 通过 MCP 协议让 AI 驱动 Ghidra 自动逆向 |
| **LaurieWired/GhidraMCP** | Ghidra MCP 服务器，LLM 自动反编译/分析/重命名 |
| **bethington/ghidra-mcp** | 另一个 Ghidra MCP，245 个工具，支持 P-code 模拟 |

### 2. JS 逆向核心
| Skill | 用途 |
|-------|------|
| `camoufox-workflow` | JS逆向工作流——6阶段全流程 |
| `jsvmp-reverse` | JS VM虚拟机逆向——TikTok栈式VM案例 |
| `find-crypto-entry` | 定位加密参数生成入口 |
| `env-patch` | JS补环境——Node.js引擎+策略分离 |
| `ast-deobfuscation` | Babel AST分层定向反混淆 |
| `algorithm-reverse` | JS逆向算法还原——签名/混合加密 |
| `anti-debug` | JS反调试对抗 + 二进制级反调试 |
| **kuizuo/js-deobfuscator** | 自动化 JS 反混淆（Babel AST） |

### 3. 反调试对抗
| Skill | 用途 |
|-------|------|
| `anti-debug` | JS反调试 + 二进制反调试——4类JS反调试+Linux/Win原生 |
| `anti-debugging-techniques` | 反调试检测+绕过通用playbook |

### 4. 桌面/移动端逆向
| Skill | 用途 |
|-------|------|
| `desktop-app-reverse-engineering` | 桌面逆向——Electron/Wails/Tauri/PyInstaller |
| `android-reverse-engineering` | Android逆向——APK反编译/Frida |
| `ida-reverse-analysis` | IDA Pro + Ghidra 二进制分析 |

### 5. iOS 逆向进阶
| 工具 | 用途 |
|------|------|
| **httptoolkit/frida-interception-and-unpinning** | Frida 全自动 HTTPS MITM + SSL pinning 绕过 |
| **v-y-archive/Jailbreak-detection-The-modern-way** | 越狱检测绕过分析 |
| OWASP MASTG Frida Gadget | 非越狱 Frida Gadget 注入 IPA |

### 6. Web API 协议逆向 + CF 绕过
| Skill | 用途 |
|-------|------|
| `web-api-protocol-reverse` | Web API 协议逆向 |
| `har-to-proxy-script` | HAR抓包→代理脚本 |
| **YangChengTeam/wxappUnpacker** | 微信小程序反编译 |
| **CF 绕过矩阵** | 见 Cloudflare 5 级防护策略 |

### 7. PyInstaller / Python 逆向
| Skill | 用途 |
|-------|------|
| `pyinstaller-reverse` | PyInstaller 解包+反编译全流程 |

### 8. 代码混淆/反混淆
| Skill | 用途 |
|-------|------|
| `code-obfuscation-deobfuscation` | 混淆分析+反混淆playbook |
| `deobfuscator` | JS反混淆——jsjiami/sojson/obfuscator.io等 |
| `ast-deobfuscation` | Babel AST反混淆 |
| **Owl4444/jsdeob-workbench** | 可视化反混淆工作台 |
| **mandiant/flare-floss** | 二进制字符串自动提取 |

### 9. Key/Token 扫描
| 工具 | 用途 |
|------|------|
| **api-key-hunter** | 多源多厂商 Key 泄露扫描器 |

### 10. 二进制仿真
| 工具 | 用途 |
|------|------|
| **qilingframework/qiling** | 可插桩二进制仿真框架（Unicorn底层） |
| **unicorn-engine/unicorn** | CPU 模拟器，指令级调试任意架构 |

### 11. 逆向工具箱合集
| 工具 | 说明 |
|------|------|
| **y9nhjy/RE_Tools** | 全网逆向工具全集 |
| **tylerha97/awesome-reversing** | 精选逆向资源列表 |

### 12. 其他逆向
| Skill | 用途 |
|-------|------|
| `binary-diffing` | 二进制Diffing+补丁分析 |
| `book-source-master` | Legado阅读书源编写 |
| `qx-script-master` | Quantumult X/Surge脚本 |

## 典型工作流

### Web JS 逆向 🔄
```
anti-debug → find-crypto-entry → env-patch → ast-deobfuscation → algorithm-reverse
```

### AI 驱动二进制逆向 🆕
```
GhidraMCP → 自动反编译 → LLM分析函数语义 → 自动重命名 → 提取协议
```

### 二进制仿真 🆕
```
Qiling + Unicorn → 加载未知二进制 → 插桩跟踪 → 记录API调用 → 还原协议
```

### 桌面 App 逆向
```
desktop-app-reverse → 识别技术栈 → 提取资源 → 分析认证逻辑
```

### PyInstaller 逆向
```
strings识别 → pyinstxtractor解包 → pycdc反编译 → 提取API key/逻辑
```

## Cloudflare 绕过矩阵

| 等级 | 防护 | 绕过 | 实测 |
|------|------|------|------|
| L0 无防护 | 直接返回 | 任意HTTP库 | ✅ |
| L1 IUAM | "Just a moment" | cloudscraper/curl_cffi | ✅ |
| L2 JS Challenge | `/cdn-cgi/challenge` | FlareSolverr/Playwright+stealth | ✅ |
| **L3 Turnstile+JS** | 双重验证 | ❌ 需住宅代理 | ❌ |
| L4 WAF+指纹 | 完整检测 | 反检测浏览器+住宅代理 | ❌ |

> **核心认知**：无住宅代理时 L3 起步的 CF 不可破。优先找无 CF 子域名或中转缓存。
