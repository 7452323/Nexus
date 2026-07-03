---
name: reverse-engineering-index
description: 逆向工程技能树索引。覆盖JS逆向、反调试对抗、桌面/移动端逆向、Web API逆向、VM/字节码逆向、代码混淆、二进制逆向、协议逆向、恶意软件分析9大子领域。
category: reverse-engineering
---

# 🔧 逆向工程技能树

## 领域总览

逆向工程 = 从编译产物还原逻辑。本技能树覆盖从 Web JS 到 Native SO、从二进制到协议的全栈逆向场景。

---

## 📂 子领域索引

### 1. JS 逆向核心
Web 前端 JavaScript 的逆向分析——签名还原、补环境、反混淆、VMP还原。

| Skill | 用途 |
|-------|------|
| `js-reverse-engineering` | JS逆向总纲——6阶段全流程（Observe→Capture→Rebuild→Patch→PureExt→Auto） |
| `js-reverse-mcp-integration` | JS逆向MCP集成——Patchright反检测引擎+23种工具 |
| `find-crypto-entry` | 定位加密参数生成入口（函数位置+调用链）——L0基础层 |
| `env-patch` | JS补环境统一技能——Node.js引擎+策略分离架构 |
| `ast-deobfuscation` | Babel AST分层定向反混淆——7步流程 |
| `jsvmp-reverse` | JSVMP/VMP虚拟机逆向——数据驱动+AST反编译双路线 |
| `algorithm-reverse` | JS逆向算法还原统一技能——签名/混合加密/Cookie签名 |
| `webpack-unpack` | Webpack打包模块提取+还原独立可运行JS |

### 2. 反调试对抗
识别并绕过反调试手段——无限 debugger、DevTools 检测等。

| Skill | 用途 |
|-------|------|
| `anti-debug` | JS反调试对抗——4类反调试识别+绕过 |
| `anti-debugging-techniques` | 反调试检测+绕过通用playbook |

### 3. 桌面/移动端逆向
Native 二进制、桌面应用、移动端 App 的逆向分析。

| Skill | 用途 |
|-------|------|
| `reverse-engineering-general` | 通用逆向框架——8个子技能（rev-symbol/struct/frida/unicorn/dex-dump/u3d-dump/idapython/apk-static） |
| `desktop-app-reverse-engineering` | 桌面应用逆向——静态分析+前端资源提取+AI prompt提取 |
| `desktop-app-unlock` | 桌面应用订阅/付费解锁——Wails/Electron/Tauri本地注入 |
| `android-reverse-engineering` | Android应用逆向——APK反编译/smali/Frida Hook/JNI分析/脱壳 🆕 |
| `ios-app-unlock` | iOS原生Swift应用逆向——Swift5反射+二进制Hook |
| `so-native-analysis` | SO原生库分析——30种工具覆盖基本分析+Flutter专项 |
| `ida-reverse-analysis` | IDA Pro逆向分析——IDAPython脚本+加密识别+DLL导出 |

### 4. Web API 逆向
从 Web 接口协议逆向到代理构建。

| Skill | 用途 |
|-------|------|
| `web-api-reverse-engineering` | Web API协议逆向通用方法论 |
| `web-api-to-openai-proxy` | Web API逆向→OpenAI兼容代理服务构建 |
| `camoufox-workflow` | JS逆向工作流——Node.js/Python接口自动化+签名还原 |
| `ruishu-reverse` | 瑞数反爬纯算逆向——Cookie T生成+URL后缀 |
| `har-to-proxy-script` | HAR抓包→QuantumultX/Surge代理脚本 |
| `wechat-mini-login` | 微信小程序免Code登录凭证获取——服务端getCode/session续期分析 🆕 |

### 5. VM/字节码逆向
虚拟机和字节码层面的逆向分析。

| Skill | 用途 |
|-------|------|
| `vm-and-bytecode-reverse` | 自定义VM+字节码逆向通用playbook |
| `symbolic-execution-tools` | 符号执行+约束求解工具链 |

### 6. 代码混淆/反混淆
混淆识别与还原——跨平台通用。

| Skill | 用途 |
|-------|------|
| `code-obfuscation-deobfuscation` | 代码混淆分析+反混淆playbook |

### 7. 二进制Diffing 🆕
二进制对比分析——补丁分析、1-day漏洞研究。

| Skill | 用途 |
|-------|------|
| `binary-diffing` | 二进制Diffing——Diaphora/BinDiff对比+补丁分析+1-day漏洞研究 |

### 8. 协议逆向 🆕
网络协议逆向工程——消息格式分析、状态机推断。

| Skill | 用途 |
|-------|------|
| `protocol-reverse-engineering` | 协议逆向——protobuf-inspector/netzob/Wireshark+消息格式分析 |

### 9. 恶意软件分析（跨领域引用）
恶意软件分析技能，主要在cybersecurity领域，逆向工程提供工具支撑。

| Skill | 所属领域 | 与逆向的关系 |
|-------|---------|-------------|
| `malware-analysis` | cybersecurity | 静态分析依赖IDA/Ghidra，动态分析依赖Frida/调试器 |

---

## 🔀 跨领域关联

- **JS逆向 + 反调试**：env-patch 和 anti-debug 常配合使用——先绕反调试，再补环境
- **JS逆向 + Web API逆向**：find-crypto-entry 定位入口 → web-api-reverse-engineering 构建协议
- **桌面逆向 + SO分析**：desktop-app-unlock 可能需要 so-native-analysis 分析底层 .so
- **VM逆向 + AST反混淆**：jsvmp-reverse 还原VMP时常需 ast-deobfuscation 预处理
- **二进制逆向 + 协议逆向**：先用protocol-re逆向协议格式，再用binary-diffing对比协议变化
- **Android逆向 + SO分析**：android-reverse-engineering 分析Java层，so-native-analysis分析Native层
- **恶意软件 + 二进制**：malware-analysis 用binary-diffing对比变体差异

---

## 📖 典型工作流

### Web JS 逆向全流程
```
anti-debug（绕反调试）→ find-crypto-entry（定位入口）→ env-patch（补环境）
→ ast-deobfuscation（反混淆）→ algorithm-reverse（还原算法）
→ web-api-to-openai-proxy（构建代理）
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

### 架构总览

```
逆向工程知识库 (~/.hermes/knowledge/re-engineering/)
├── ctf-skills/          — CTF逆向技能库（19个文件，9411行）
│   ├── patterns.md      — 逆向模式库（VM/XOR/LLVM混淆/SECCOMP/BPF）
│   ├── patterns-ctf*.md — CTF实战模式（2024-2026赛题）
│   ├── tools.md         — 静态工具速查（GDB/r2/Ghidra/Unicorn）
│   ├── tools-dynamic.md — 动态工具速查（Frida/angr/lldb/x64dbg）
│   ├── platforms.md     — 平台特化（macOS/iOS/内核/嵌入式）
│   ├── languages.md     — 语言特化（Python/Go/Rust/WASM/.NET）
│   ├── anti-analysis*.md— 反分析技术
│   └── field-notes.md   — 60+条实战笔记
├── android-re/          — Android逆向资源库（⭐2.2k）
├── ghidra-scripts/      — Ghidra脚本集（ninja + 0xdea）
├── binary-diffing/      — 二进制Diffing工具（Diaphora + BinExport）
├── protocol-re/         — 协议逆向工具（protobuf-inspector + netzob）
├── malware-re/          — 恶意软件分析工具（FLARE FLOSS + Refinery）
└── tools-reference/     — 工具参考（reversingBits + awesome-re 5k⭐）
```

### 知识库与Skill速查

| 知识库 | 内容 | 配合Skill |
|--------|------|----------|
| ctf-skills | 9411行逆向模式+工具+实战 | 所有逆向skill |
| android-re | Android逆向培训+工具+资源 | android-reverse-engineering |
| ghidra-scripts | Ghidra自动化脚本 | ida-reverse-analysis（Ghidra补充） |
| binary-diffing | Diaphora+BinExport工具 | binary-diffing |
| protocol-re | protobuf-inspector+netzob | protocol-reverse-engineering |
| malware-re | FLOSS字符串提取+Refinery数据处理 | malware-analysis（cybersecurity） |
| tools-reference | 3500+工具+2300+文章总索引 | 所有逆向skill |

### 使用方式

- **遇到具体工具问题** → 查 `tools-reference/reversingBits/` 速查表
- **需要找特定平台工具** → 查 `tools-reference/awesome-re/` 总索引
- **CTF逆向题目** → 查 `ctf-skills/patterns*.md` 找匹配模式
- **语言特化逆向** → 查 `ctf-skills/languages*.md` 找对应方法
- **平台特化逆向** → 查 `ctf-skills/platforms.md` 找平台指南
