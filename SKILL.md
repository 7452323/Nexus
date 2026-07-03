---
name: reverse-engineering-index
description: 逆向工程技能树索引。覆盖JS逆向、二进制逆向、移动端、Web API、反调试、混淆对抗、协议还原等。
metadata:
  display_name: "🔧 Akino 逆向工程技能树"
  intent_patterns: "逆向,反编译,JS逆向,反调试,Frida,Ghidra,IDA,解混淆,二进制,签名还原,补环境,AST,Android,iOS,小程序,CF绕过"
---

# 🔧 Akino 逆向工程技能树

逆向工程 = 从编译产物还原逻辑。覆盖 Web JS 到 Native SO、二进制到协议的全栈逆向。

## 📂 核心入口

| 入口 | 用途 |
|------|------|
| `index_current.md` | 📌 总入口 - 逆向全流程导航 |
| `camoufox-workflow.md` | 📌 JS逆向 6 阶段工作流 |
| `reverse-playbook.md` | 📌 逆向实战 Playbook |
| `curr_index.md` | 📌 当前索引状态 |

## 🔍 子领域

### JS 逆向核心
| 文件 | 用途 |
|------|------|
| `algorithm-reverse.md` | 签名/混合加密算法还原 |
| `anti-debug.md` | JS反调试 + 二进制反调试 |
| `ast-deobfuscation.md` | Babel AST反混淆 |
| `deobfuscator.md` | JS反混淆（jsjiami/sojson/obfuscator.io） |
| `env-patch.md` | JS补环境 Node.js引擎 |
| `find-crypto-entry.md` | 定位加密参数入口 |
| `code-obfuscation-deobfuscation.md` | 混淆分析+反混淆playbook |
| `jsrpc-auto-reverse.md` | jsRPC 自动逆向 |
| `context-optimizer.md` | 上下文优化器 |

### 移动端逆向
| 文件 | 用途 |
|------|------|
| `android-reverse-engineering.md` | APK反编译+Frida |
| `ida-reverse-analysis.md` | IDA Pro + Ghidra 分析 |
| `analyzing-android-malware-with-apktool.md` | Android恶意APK分析 |
| `analyzing-ios-app-security-with-objection.md` | iOS 安全分析 Objection |
| `analyzing-golang-malware-with-ghidra.md` | Go 恶意软件 Ghidra 分析 |

### 桌面端逆向
| 文件 | 用途 |
|------|------|
| `desktop-app-reverse-engineering.md` | Electron/Wails/Tauri/PyInstaller |

### Web API 协议逆向
| 文件 | 用途 |
|------|------|
| `web-api-protocol-reverse.md` | Web API 协议逆向 |
| `har-to-proxy-script.md` | HAR抓包→代理脚本 |
| `cross-platform-proxy-scripting.md` | 跨平台代理脚本 |
| `cf-bypass.md` | Cloudflare 绕过策略 |

### 工具脚本
| 文件 | 用途 |
|------|------|
| `qx-script-master.md` | Quantumult X/Surge 脚本 |
| `book-source-master.md` | Legado 阅读书源 |
| `bomb-api-source-collection.md` | 接口源收集 |
| `binary-diffing.md` | 二进制 Diffing |
| `deobfuscating-javascript-malware.md` | JS恶意软件反混淆 |
| `deobfuscating-powershell-obfuscated-malware.md` | PS混淆恶意软件分析 |
| `app-store-price-tracker.md` | App Store 价格追踪 |

### API 安全（Hermes Agent）
| 文件 | 用途 |
|------|------|
| `detecting-api-enumeration-attacks.md` | 检测API枚举攻击 |
| `detecting-shadow-api-endpoints.md` | 检测影子API端点 |
| `exploiting-api-injection-vulnerabilities.md` | 利用API注入漏洞 |
| `exploiting-excessive-data-exposure-in-api.md` | 利用API过度数据暴露 |
| `exploiting-insecure-data-storage-in-mobile.md` | 移动端不安全存储利用 |

## 🔄 典型工作流

### Web JS 逆向
```
find-crypto-entry → env-patch → ast-deobfuscation → algorithm-reverse
```

### 桌面 App 逆向
```
desktop-app-reverse → 识别技术栈 → 提取资源 → 分析认证逻辑
```

### Mobile 逆向
```
android-reverse / objecting → Frida Hook → 协议还原
```

### AI 驱动逆向
```
GhidraMCP → 自动反编译 → LLM分析 → 提取协议/算法
```

### Cloudflare 绕过
```
cf-bypass → 分级策略 → 找无CF子域名 → 中转缓存 → FlareSolverr+代理
```

## 📁 仓库结构

```
Minis/SKILL/逆向/
├── SKILL.md                    ← 本索引（入口）
├── skill.json                  ← 图标配置
├── index_current.md            ← 总导航
├── camoufox-workflow.md        ← JS逆向核心工作流
├── reverse-playbook.md         ← 实战playbook
├── *.md                        ← 各子领域技能
├── references/                 ← 参考文件
│   ├── camoufox-workflow--ref-*.md
│   └── ast-deobfuscation--ref-*.md
└── agents/                     ← Hermes Agent 脚本
    └── *--agent.py / *--process.py
```
