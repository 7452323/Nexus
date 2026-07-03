---
name: reverse-engineering-index
description: 逆向工程技能树索引。覆盖AI驱动逆向、JS逆向、反调试对抗、桌面/移动端逆向、Web API协议逆向、PyInstaller逆向、VM/字节码逆向、代码混淆、二进制逆向、协议逆向、二进制仿真、恶意软件分析12大子领域。查找对应skill的入口。
metadata:
  display_name: "🔧 逆向工程技能树"
  intent_patterns: "逆向,反编译,脱壳,JS逆向,反调试,Frida,Ghidra,IDA,解混淆,二进制,协议逆向,签名还原,补环境,AST,Unicorn,Android逆向,iOS逆向,小程序逆向,Cloudflare绕过"
---

# Purpose

逆向工程 = 从编译产物还原逻辑。覆盖 Web JS 到 Native SO、二进制到协议的全栈逆向场景。用户提到任何逆向需求时触发，根据问题类型选择对应子领域入口。

# How to Use

## 触发方式
用户说：逆向、反编译、脱壳、JS逆向、Frida、Ghidra、Python逆向、APK、IPA、协议还原、签名算法、补环境、解混淆、AST、二进制、so文件、小程序、Cloudflare

## 实战能力速查

### 用户说「帮我逆向这个」
→ 先识别类型再选入口

| 场景 | 选什么 | 输出什么 |
|------|--------|----------|
| 浏览器JS加密参数 | JS逆向 → 定位加密入口 → 补环境 / 算法还原 | Python/JS 还原代码 |
| Web端请求签名 | HAR抓包 → 定位算法 → 还原签名 | 签名生成脚本 |
| APP抓不到包(SLL pinning) | Frida Hook → 绕过证书绑定 | Frida 脚本 |
| 爬虫被Cloudflare拦截 | CF绕过矩阵 → 分级策略 | 绕过方案（含住宅代理推荐） |
| 小程序加密参数 | 反编译wxapkg → 定位加密逻辑 | 反编译源码 + 还原脚本 |
| exe/dmg安装包 | PyInstaller/Electron识别 → 解包/反编译 | 源码/配置文件 |
| APK登录协议 | 反编译APK → Frida Hook → 协议还原 | Hook脚本 + 协议文档 |
| SO层加密算法 | Ghidra反编译 → 定位算法函数 | 伪代码 + 算法说明 |
| 某IP被封/IP查询 | 自动切换代理 / IP源采集 | 可用代理池 |
| JS代码被混淆 | AST反混淆 → 清除控制流平坦化/字符串编码 | 可读js源码 |
| 解析一个未知文件格式 | 010 Editor模板 / 二进制分析 | 格式结构说明 |
| 脱掉UPX/Themida壳 | 脱壳工具链 → 手动修复IAT | 脱壳后PE |
| 镜像/虚拟机文件分析 | Qiling/Unicorn仿真执行 → 插桩分析 | API调用日志 + 行为分析 |

### 用户说「分析这个加密参数」
→ 进入 `jsvmp-reverse` 或 `find-crypto-entry` 流程

### 用户说「过Cloudflare」
→ 执行 CF 绕过矩阵（见下方）

## Cloudflare 绕过矩阵

| 等级 | 防护 | 绕过方案 | 实测 |
|------|------|----------|------|
| L0 无防护 | 直接返回内容 | 任意 HTTP 库 | ✅ |
| L1 IUAM | "Just a moment..." | cloudscraper / curl_cffi / FlareSolverr | ✅ |
| L2 JS Challenge | `/cdn-cgi/challenge-platform/` | FlareSolverr / Playwright+stealth | ✅ |
| **L3 Turnstile + JS** | 双重验证 | ❌ **需要住宅代理** | ❌ |
| L4 WAF + 指纹 | 完整检测链 | 反检测浏览器 + 住宅代理 | ❌ |

> 核心认知：无住宅代理时 L3 起步的 CF 不可破。优先找无 CF 子域名或中转缓存。

## 子领域索引（12个）

### 1. AI 驱动逆向
| 工具 | 用途 |
|------|------|
| **LaurieWired/GhidraMCP** | Ghidra MCP 服务器，LLM 自动反编译/分析/重命名 |
| **bethington/ghidra-mcp** | 另一个 Ghidra MCP，245 个工具，支持 P-code 模拟 |

### 2. JS 逆向核心
| 入口 | 用途 |
|------|------|
| `jsvmp-reverse` | JS VM虚拟机逆向（TikTok栈式VM案例） |
| `find-crypto-entry` | 定位加密参数生成入口 |
| `env-patch` | JS补环境——Node.js引擎+策略分离 |
| `ast-deobfuscation` | Babel AST分层定向反混淆 |
| `algorithm-reverse` | 签名/混合加密算法还原 |
| `anti-debug` | JS反调试对抗 |
| **kuizuo/js-deobfuscator** | 自动化 JS 反混淆 |

### 3. 反调试对抗
| 入口 | 用途 |
|------|------|
| `anti-debug` | 4类JS反调试+Linux/Win原生反调试 |
| `anti-debugging-techniques` | 反调试检测+绕过通用playbook |

### 4. 桌面/移动端逆向
| 入口 | 用途 |
|------|------|
| `desktop-app-reverse` | Electron/Wails/Tauri/PyInstaller |
| `android-reverse` | APK反编译+Frida Hook |
| `ida-reverse-analysis` | IDA Pro + Ghidra 二进制分析 |

### 5. iOS 逆向
| 工具 | 用途 |
|------|------|
| **httptoolkit/frida-interception-and-unpinning** | Frida HTTPS MITM + SSL pinning 绕过 |
| **v-y-archive/Jailbreak-detection** | 越狱检测绕过 |
| OWASP MASTG Frida Gadget | 非越狱 IPA Frida 注入 |

### 6. Web API 协议逆向 + 小程序
| 入口 | 用途 |
|------|------|
| `web-api-protocol-reverse` | API协议逆向 |
| `har-to-proxy-script` | HAR抓包→代理脚本 |
| **YangChengTeam/wxappUnpacker** | 微信小程序反编译 |

### 7. PyInstaller 逆向
| 入口 | 用途 |
|------|------|
| `pyinstaller-reverse` | pyinstxtractor+pycdc 全流程 |

### 8. 代码混淆/反混淆
| 入口 | 用途 |
|------|------|
| `deobfuscator` | jsjiami/sojson/obfuscator.io 等反混淆 |
| **mandiant/flare-floss** | 二进制混淆字符串自动提取 |

### 9. API Key/Token 扫描
| 工具 | 用途 |
|------|------|
| `api-key-hunter` | 多源多厂商 Key 泄露扫描 |

### 10. 二进制仿真
| 工具 | 用途 |
|------|------|
| **qilingframework/qiling** | 可插桩二进制仿真（Unicorn底层） |
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
