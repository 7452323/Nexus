---
name: reverse-engineering-index
description: 逆向工程技能树索引。覆盖AI驱动逆向、JS逆向、反调试对抗、桌面/移动端逆向、Web API协议逆向、PyInstaller逆向、VM/字节码逆向、代码混淆、二进制逆向、协议逆向、二进制仿真、恶意软件分析12大子领域。
metadata:
  display_name: "🔧 逆向工程技能树"
  intent_patterns: "逆向,反编译,脱壳,JS逆向,反调试,Frida,Ghidra,IDA,解混淆,二进制,协议逆向,签名还原,补环境,AST,Unicorn,Android逆向,iOS逆向,小程序逆向,Cloudflare绕过"
---

# 🔧 逆向工程技能树

> 逆向是你最关键的。所有逆向任务优先投入资源，持续进化。

逆向工程 = 从编译产物还原逻辑。覆盖 Web JS 到 Native SO、二进制到协议的全栈逆向场景。

## 📂 子领域索引

### 1. AI 驱动逆向
| 工具 | 用途 |
|------|------|
| **LaurieWired/GhidraMCP** | Ghidra MCP 服务器，LLM 自动反编译/分析/重命名 |
| **bethington/ghidra-mcp** | 另一个 Ghidra MCP，245 个工具，支持 P-code 模拟 |

### 2. JS 逆向核心
| 入口 | 用途 |
|------|------|
| `jsvmp-reverse` | JS VM虚拟机逆向——TikTok栈式VM(77 opcode)案例 |
| `find-crypto-entry` | 定位加密参数生成入口 |
| `env-patch` | JS补环境——Node.js引擎+策略分离 |
| `ast-deobfuscation` | Babel AST分层定向反混淆 |
| `algorithm-reverse` | JS逆向算法还原——签名/混合加密 |
| `anti-debug` | JS反调试对抗 + 二进制反调试 |
| **kuizuo/js-deobfuscator** | 自动化 JS 反混淆（Babel AST） |

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
| **v-y-archive/Jailbreak-detection** | 越狱检测绕过（Snapchat/Pokemon Go） |
| OWASP MASTG Frida Gadget | 非越狱 Frida Gadget 注入 IPA |

### 6. Web API 协议逆向 + Cloudflare 绕过 + 小程序
| 入口 | 用途 |
|------|------|
| `web-api-protocol-reverse` | Web API 协议逆向——ChatGPT/OpenAI等接口 |
| `har-to-proxy-script` | HAR抓包→代理脚本 |
| **YangChengTeam/wxappUnpacker** | 微信小程序反编译（wxapkg 还原源码） |

**Cloudflare 绕过矩阵：**

| 等级 | 防护 | 绕过 | 实测 |
|------|------|------|------|
| L0 无防护 | 直接返回 | 任意 HTTP 库 | ✅ |
| L1 IUAM | "Just a moment..." | cloudscraper / curl_cffi / FlareSolverr | ✅ |
| L2 JS Challenge | `/cdn-cgi/challenge-platform/` | FlareSolverr / Playwright+stealth | ✅ |
| **L3 Turnstile + JS** | 双重验证 | ❌ 需住宅代理 | ❌ |
| L4 WAF + 指纹 | 完整检测链 | 反检测浏览器 + 住宅代理 | ❌ |

> 无住宅代理时 L3 不可破。优先找无 CF 子域名或中转缓存。

### 7. PyInstaller 逆向
| 入口 | 用途 |
|------|------|
| `pyinstaller-reverse` | PyInstaller 打包应用逆向——pyinstxtractor+pycdc 全流程 |

### 8. 代码混淆/反混淆
| 入口 | 用途 |
|------|------|
| `deobfuscator` | JS反混淆——jsjiami/sojson/obfuscator.io/JSFuck/Packer |
| `ast-deobfuscation` | Babel AST反混淆 |
| **Owl4444/jsdeob-workbench** | 可视化反混淆工作台 |
| **mandiant/flare-floss** | 二进制混淆字符串自动提取 |

### 9. API Key/Token 扫描
| 工具 | 用途 |
|------|------|
| `api-key-hunter` | 多源多厂商 Key 泄露扫描器 |

### 10. 二进制仿真
| 工具 | 用途 |
|------|------|
| **qilingframework/qiling** | 可插桩二进制仿真框架（Unicorn底层） |
| **unicorn-engine/unicorn** | CPU 模拟器，指令级调试任意架构 |

### 11. 逆向工具箱
| 工具 | 说明 |
|------|------|
| **y9nhjy/RE_Tools** | 全网逆向工具全集 |
| **tylerha97/awesome-reversing** | 精选逆向资源列表 |

### 12. 其他
| 入口 | 用途 |
|------|------|
| `binary-diffing` | 二进制Diffing+补丁分析 |
| `book-source-master` | Legado阅读3.0书源编写 |
| `qx-script-master` | Quantumult X/Surge脚本 |

## 🔀 典型工作流

### Web JS 逆向
```
anti-debug → find-crypto-entry → env-patch → ast-deobfuscation → algorithm-reverse
```

### AI 驱动二进制逆向
```
GhidraMCP → 自动反编译 → LLM分析函数 → 自动重命名 → 提取协议/算法
```

### 二进制仿真
```
Qiling + Unicorn → 加载未知二进制 → 插桩跟踪 → 记录API调用 → 还原协议
```

### 桌面 App 逆向
```
desktop-app-reverse → 识别技术栈 → 提取资源 → 分析认证逻辑
```

### ChatGPT Web API 协议逆向
```
OpenAIBackendAPI → fingerprint伪造 → PoW/Turnstile绕过 → conversation协议 → image_gen协议
```

### PyInstaller 逆向
```
strings识别 → pyinstxtractor解包 → pycdc反编译 → 提取API key/逻辑
```

### 1-day漏洞研究
```
binary-diffing → 定位修改函数 → 分析修改内容
```
