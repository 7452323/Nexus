---
name: reverse-engineering-index
description: 逆向工程技能树索引。覆盖AI驱动逆向、JS逆向、反调试对抗、桌面/移动端逆向、Web API协议逆向、PyInstaller逆向、VM/字节码逆向、代码混淆、二进制逆向、协议逆向、二进制仿真、恶意软件分析13大子领域。
---

# 🔧 逆向工程技能树

> 逆向工程 = 从编译产物还原逻辑。覆盖 Web JS 到 Native SO、二进制到协议的全栈逆向场景。
> **环境**: iSH Alpine Linux aarch64 — 优先浏览器取证 + Python/Node 本地复现。

## ⚡ 快速入口

| 文件 | 用途 |
|------|------|
| **[SKILL.md](SKILL.md)** | 📌 主索引 + 工作流 + 工具矩阵 |
| **[INDEX.md](INDEX.md)** | 📌 完整目录索引 + 知识库 |
| **[cf-bypass.md](web-api/cf-bypass.md)** | 📌 Cloudflare 绕过全套方案 (2026) |

## 📂 子领域速查

| 领域 | 入口 | 关键工具 |
|------|------|---------|
| **AI 驱动逆向** | [ai-driven-reverse.md](ai-driven-reverse.md) | GhidraMCP, LLM, 符号执行 MCP |
| **JS 逆向** | [js-reverse/](js-reverse/) | Babel AST, JSRPC, Node 补环境 |
| **反调试对抗** | [js-reverse/anti-debug.md](js-reverse/anti-debug.md) | 4类JS反调试+二进制反调试 |
| **Web API 逆向** | [web-api/](web-api/) | ChatGPT协议, PoW/Turnstile |
| **CF 绕过** | [web-api/cf-bypass.md](web-api/cf-bypass.md) | SeleniumBase, Pydoll, Scrapling |
| **桌面逆向** | [desktop/desktop-app-reverse.md](desktop/desktop-app-reverse.md) | Wails, Electron, Tauri |
| **Android 逆向** | [mobile/android-reverse.md](mobile/android-reverse.md) | jadx, apktool, Frida |
| **iOS 逆向** | [SKILL.md#5-ios-逆向](SKILL.md) | Frida, SSL pinning bypass |
| **二进制逆向** | [binary/ida-reverse.md](binary/ida-reverse.md) | IDA, Ghidra, Unicorn |
| **代码混淆** | [js-reverse/ast-deobfuscation.md](js-reverse/ast-deobfuscation.md) | Babel, deobfuscator |
| **安全研究** | [security/](security/) | 恶意软件, API安全 |
| **代理脚本** | [proxy-script/](proxy-script/) | QX, Surge, Loon |

## 🔀 典型工作流

### Web JS 逆向
```
anti-debug → find-crypto-entry → env-patch → ast-deobfuscation → algorithm-reverse
```

### CF 绕过 (2026 推荐)
```
轻量: curl_cffi → 中量: SeleniumBase UC+CDP → 重量: Pydoll/Scrapling → 最后: 住宅代理
```

### AI 驱动二进制逆向
```
GhidraMCP → 自动反编译 → LLM分析函数 → 自动重命名 → 提取协议/算法
```

## 🆕 2026 更新

- **AI 驱动逆向** — GhidraMCP + LLM 自动反编译/重命名
- **CF 绕过** — SeleniumBase / Pydoll / Scrapling 新一代工具
- **符号执行 MCP** — angr + taint analysis 集成
- **JSRPC 全自动** — 不补环境、不还原算法

## 📊 仓库统计

- **文件数**: 98+
- **子领域**: 13
- **工作流**: 8+
- **工具链**: 50+

## 关联技能

| 技能 | 路径 |
|------|------|
| 解密技能 | `/var/minis/skills/解密/` |
| 浏览器工具 | Minis browser_use |
| App Store 价格 | `/var/minis/skills/appstoreprice-hub/` |

