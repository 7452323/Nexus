---
name: reverse-engineering
description: "逆向工程技能树索引。覆盖JS逆向、反调试对抗、桌面/移动端逆向、Web API协议逆向、PyInstaller逆向、VM/字节码逆向、代码混淆、二进制逆向、协议逆向、二进制仿真、EDR对抗、LLM+MCP逆向、Flutter/RN/WASM逆向、Android脱壳、iOS逆向全栈30+子领域。"
author: 7452323
version: 3.0.0
tags: [reverse-engineering, javascript, android, ios, binary, protocol, edr, mcp, frida, ghidra]
---

# 🔧 逆向工程技能树

逆向工程 = 从编译产物还原逻辑。本技能树覆盖从 Web JS 到 Native SO、从二进制到协议的全栈逆向场景。

## 子领域索引

### 1. AI 驱动逆向

| 工具 | 用途 |
|------|------|
| **LaurieWired/GhidraMCP** ⭐5.5k | Ghidra MCP 服务器，LLM 自动反编译/分析/重命名 |
| **bethington/ghidra-mcp** | 272 MCP工具，P-code仿真+live调试+跨二进制匹配 |
| **cyberkaida/reverse-engineering-assistant** | AI-first推理链+工具驱动分析(ReVa) |
| **black-widow (Karadul)** | 6阶段自动化RE pipeline：Identify→Static→Deobfuscate→Reconstruct→Report |

**LLM RE工作流：**
```
binary → GhidraMCP加载 → LLM分析decompiled C → 自动命名FUN_函数 → 算法识别 → 注释 → 报告
```

### 2. LLM+MCP逆向工具生态

| 类别 | MCP服务器 | 功能 |
|------|----------|------|
| **IDA Pro** | mrexodia/ida-pro-mcp | 20+工具，函数分析/反编译 |
| | taida957789/ida-mcp-server-plugin | SSE协议+Claude/Cursor实时集成 |
| | cnitlrt/headless-ida-mcp-server | Headless CI/CD批处理 |
| **Ghidra** | LaurieWired/GhidraMCP ⭐5.5k | 最全面，多客户端支持 |
| | bethington/ghidra-mcp | **272 MCP工具**，P-code仿真+调试器 |
| **Binary Ninja** | fosdickio/binary_ninja_mcp | Claude Desktop无缝集成 |
| **radare2** | radareorg/radare2-mcp 官方 | 26+工具 STDIO传输 |
| **x64dbg** | Wasdubya/x64dbgMCP | 40+ SDK工具 Windows调试 |
| **LLDB** | 官方原生MCP (2025.6+) | 内置支持 |
| **Frida** | dnakov/frida-mcp | 进程管理/脚本注入/实时instrumentation |
| **Jadx** | mobilehackinglab/Jadx-MCP-Plugin | AI辅助Android反编译 |
| **apktool** | zinja-coder/apktool-mcp-server | APK操作分析 |
| **Wireshark** | 0xKoda/WireMCP | 抓包+威胁检测 |
| **Burp Suite** | PortSwigger/mcp-server 官方 | 官方MCP |
| **YARA** | ThreatFlux/YaraFlux | 恶意软件检测/签名匹配 |
| **unidbg** | zhkl0228/unidbg + MCP | Android native库仿真 |

### 3. JS 逆向核心

| 技能 | 用途 |
|------|------|
| `camoufox-workflow` | JS逆向6阶段全流程+双脑异步协作 |
| `jsvmp-reverse` | JS VM虚拟机逆向（含TikTok栈式VM 77 opcode） |
| `find-crypto-entry` | 定位加密参数生成入口 |
| `env-patch` | JS补环境——Node.js引擎+策略分离 |
| `ast-deobfuscation` | Babel AST分层定向反混淆 |
| `algorithm-reverse` | JS逆向算法还原——签名/混合加密 |
| `anti-debug` | JS反调试+二进制级反调试 |

**JS反混淆工具集：**
| 工具 | 用途 |
|------|------|
| **j4k0xb/webcrack** ⭐2.7k | obfuscator.io反混淆+webpack解包+unminify |
| **ben-sb/javascript-deobfuscator** | obfuscator.io专用（Babel AST） |
| **deobfuscate.relative.im** | 一键JS反混淆 |
| **mandiant/flare-floss** | 二进制字符串自动提取 |

### 4. 反调试对抗

| 技术 | 检测方法 | 绕过 |
|------|---------|------|
| **JS无限debugger** | `debugger`语句循环 | Function构造器重写/条件BP跳过 |
| **DevTools检测** | window尺寸差/console.log getter | 重写getter/固定尺寸 |
| **ptrace(PT_DENY_ATTACH)** | grep PT_DENY_ATTACH | Hook ptrace返回0 |
| **sysctl P_TRACED** | grep KERN_PROC/P_TRACED | Hook sysctl清除P_TRACED |
| **mach_absolute_time** | 机器码时间差检测单步 | Hook时间API |
| **Anti-Frida** | /proc/maps扫描+端口27042+文件检查 | Hook fopen过滤/fri-server改名 |

**Anti-Frida检测7种手段+绕过：**
| 检测手段 | 绕过 |
|---------|------|
| `/proc/self/maps`扫描frida字符串 | Hook fopen/open过滤内容 |
| 端口27042探测 | frida-server改名/改端口 |
| 内存扫描gadget特征 | 内存内容过滤 |
| 文件系统检查frida-server | Hook stat/access |
| 线程名检查gum-js-loop | Hook prctl改线程名 |
| CPU指令breakpoint检测 | Hook tgkill |
| inotify监控/proc | Hook inotify_add_watch |

### 5. iOS 逆向

| 工具 | 用途 | 需要越狱 |
|------|------|---------|
| **AloneMonkey/frida-ios-dump** | Frida运行时拉取解密IPA | 是 |
| **bagbak** | 从越狱设备提取已安装App | 是 |
| **ipatool** | 用Apple ID从App Store下载加密IPA | 否 |
| **TrollStore** | 永久签名+提取已安装App | 否 |
| **httptoolkit/frida-interception-and-unpinning** | 全自动HTTPS MITM+SSL pinning绕过 | 是 |

**iOS逆向全流程：**
```
获取IPA → 脱壳(frida-ios-dump/bagbak) → class-dump/llvm-objdump → 
strings提取 → Frida动态Hook → API还原
```

**iOS反篡改检测矩阵：**
| 类别 | 技术 | 检测方法 |
|------|------|----------|
| 混淆 | iXGuard/SwiftShield/OLLVM/Arxan | 短类名比例>30%、字符串解密函数、switch-dispatch平坦化 |
| 反调试 | ptrace(PT_DENY_ATTACH) | grep PT_DENY_ATTACH |
| 反调试 | sysctl P_TRACED | grep KERN_PROC\|P_TRACED |
| 反调试 | mach_absolute_time | 机器码时间差 |
| 反Frida | 端口扫描27042 | 反Frida脚本需先绕过 |

**iOS ObjC SDK类前缀指纹表：**
| 前缀 | SDK | 前缀 | SDK |
|------|-----|------|-----|
| AF | AFNetworking | FIR | Firebase |
| GMS | Google Maps | SD | SDWebImage |
| RCT | React Native | WK | WebView |
| FBSDK | Facebook | MMP | Mixpanel |
| AWV | AppsFlyer | BTG | BugTag |

### 6. Android 逆向

| 工具 | 用途 |
|------|------|
| **jadx** | APK→Java反编译（标准工具） |
| **apktool** | APK反编译+重打包 |
| **FridaBypassKit** | Root+SSL+模拟器+反调试一体绕过 |
| **0xCD4/SSL-bypass** | 通用非定制SSL绕过Frida脚本 |
| **frida-dexdump** | Frida注入+内存搜索Dex magic |
| **LLeavesG/eBPFDexDumper** | eBPF内核级Dex dump，绕过用户态所有反调试 |

**Android脱壳工具选型：**
| 工具 | 原理 | 适用场景 |
|------|------|---------|
| eBPFDexDumper | eBPF内核级dump | 对抗强保护壳 |
| FART | ART环境主动调用+dump | 常规加固壳 |
| frida-dexdump | Frida注入+内存搜索 | 简单壳 |
| BlackDex | 黑名单检测+Dex提取 | 常规壳 |

**Frida绕过工具选型矩阵：**
| 场景 | 首选工具 |
|------|----------|
| 全自动HTTPS MITM拦截 | httptoolkit/frida-interception-and-unpinning |
| Root+SSL+模拟器+反调试一体 | FridaBypassKit |
| 仅SSL Pinning绕过 | 0xCD4/SSL-bypass |
| Flutter证书校验绕过 | httptoolkit的android-disable-flutter-certificate-pinning.js |
| 反Frida检测绕过 | CodeShare: enovella/anti-frida-bypass |

### 7. Android Native仿真（unidbg）

**unidbg** — 基于Unicorn的Android native库仿真框架

| 特性 | 说明 |
|------|------|
| JNI仿真 | 模拟JNI调用API，可调用JNI_OnLoad |
| Hook支持 | xHook(Android) / fishhook(iOS) / substrate / whale |
| 调试 | console debugger / gdb stub / 指令trace / 内存读写trace |
| 架构 | ARM32 + ARM64 |

**典型用途：** 脱离Android环境调用so库函数（签名算法/加密函数），直接在JVM中执行native代码

### 8. Flutter 逆向

| 工具 | 用途 |
|------|------|
| **worawit/blutter** ⭐2k+ | Flutter逆向核心工具，恢复Dart类/方法/字段名 |

**blutter工作流：**
```bash
python3 blutter.py path/to/app/lib/arm64-v8a out_dir
# 输出：asm/*（带符号反汇编）+ blutter_frida.js（Frida脚本模板）+ objs.txt
```

### 9. React Native / Hermes 逆向

| 工具 | 用途 |
|------|------|
| **P1sec/hermes-dec** | Hermes VM字节码(HBC)反汇编+反编译 |
| **Pilfer/heresy** | Hook RN Bundle加载器，注入自定义JS |
| **metro-symbolicate** | React Native stack trace反混淆 |

**RN逆向流程：**
```
APK/IPA → 提取index.android.bundle → hermes-dec反编译HBC → 恢复JS源码
```

### 10. WASM 逆向

| 工具 | 用途 |
|------|------|
| **wabt/wasm2wat** | WASM→WAT文本格式 |
| **wabt/wasm-decompile** | WASM→类C可读伪代码 |
| **wwwg/wasmdec** | WASM→C反编译器 |

### 11. 桌面应用逆向

| 技术栈 | 工具/方法 |
|--------|----------|
| **Electron** | `npx @electron/asar extract app.asar .` |
| **Tauri/Wails** | 前端资源提取+Rust/Go二进制分析 |
| **PyInstaller** | pyinstxtractor → .pyc → pycdc反编译 |

### 12. 协议逆向

| 工具 | 用途 |
|------|------|
| **mitmproxy** | 可编程HTTPS代理，Python addon |
| **blackboxprotobuf** | 未知Protobuf逆向（无需.proto） |
| **Kaitai Struct** | 二进制协议结构定义+多语言解析器 |
| **ImHex / 010 Editor** | 十六进制结构模板 |

**Protobuf逆向流程：**
```
PCAP采集 → tshark字段提取 → blackboxprotobuf盲解析 → 状态机绘制 → 重放验证
```

### 13. 二进制仿真与自动化分析

| 工具 | Stars | 用途 |
|------|-------|------|
| **qilingframework/qiling** | ⭐5.4k | 二进制仿真框架，跨平台跨架构 |
| **unicorn-engine/unicorn** | ⭐ | CPU模拟器，Qiling底层 |
| **angr/angr** | ⭐7k+ | 符号执行框架，CTF自动化解题 |

### 14. EDR/AV对抗

| 技术 | 工具/参考 |
|------|----------|
| Unhook (ntdll重映射) | Peruns Fart |
| 直接syscall | SysWhispers3 (klezVirus/SysWhispers3) |
| 间接syscall | SysWhispers3 --mode jumper |
| SSN动态解析 | Hell's Gate / Halo's Gate / Tartarus Gate |
| Call Stack Spoof | CallStackSpoofer / SilentMoonwalk |
| ETW Patch | EtwEventWrite head patch |
| AMSI Patch | AmsiScanBuffer head patch |

**EDR对抗实战链：** Halo's Gate → indirect syscall → CallStackSpoofer → ETW/AMSI patch

### 15. 打包器/保护器检测与脱壳

| 打包器 | 检测特征 | 脱壳方法 |
|--------|---------|---------|
| **UPX** | UPX0/UPX1 section, `UPX!` magic | `upx -d`（95%有效） |
| **Themida** | `.themida`/`.oreans` section | HW BP on VirtualAlloc → OEP → Scylla |
| **VMProtect** | `.vmp0/1/2` section | VM handler识别→trace-based devirtualization |
| **Enigma** | `.enigma1/2/3` section | 运行时dump + Scylla |
| **PyInstaller** | PYZ archive, MEI loader | pyinstxtractor → .pyc → uncompyle6 |
| **Electron ASAR** | app.asar文件 | `npx @electron/asar extract` |

**OLLVM混淆技术（10种）：**
CFF控制流平坦化 / BCF虚假控制流 / 指令替换 / 字符串加密 / 不透明谓词 / 死代码插入 / 寄存器重映射 / MBA混合布尔算术 / 常量展开 / VM混淆

### 16. 固件/IoT逆向

| 工具 | 用途 |
|------|------|
| **binwalk** | 固件提取+分析 |
| **firmadyne** | Linux固件全系统仿真 |
| **EMBA** | 固件自动化安全分析 |
| **QEMU** | 跨架构仿真（ARM/MIPS） |

### 17. Cloudflare 绕过

| 防护等级 | 特征 | 绕过方案 |
|----------|------|----------|
| L0 无防护 | 直接返回 | 任意HTTP库 |
| L1 IUAM | "Just a moment..." + 5秒 | cloudscraper / FlareSolverr |
| L2 JS Challenge | 动态JS | FlareSolverr / Playwright+stealth |
| **L3 Turnstile** | 双重验证 | ❌ 需住宅代理+Turnstile solver |
| L4 WAF+Turnstile | 完整检测 | ❌ 需商业方案 |

### 18. OWASP MASTG 移动安全测试

- MASVS: 移动应用安全验证标准
- MASTG: 测试指南（技术+工具+测试用例）
- MAS Crackmes: 逆向工程挑战练习

### 19. CTF逆向方法论

| 方向 | 核心流程 |
|------|---------|
| **Crypto+Mobile** | container→compression→encoding→xor→crypto→integrity→parse |
| **PCAP协议** | 流重组→帧恢复→方向→完整性→解码→行为关联 |
| **自定义协议重放** | 角色+流ID+握手边界→帧边界→方向序列→完整性 |
| **Bundle/SourceMap** | HTML入口→script tags→manifests→chunk registries→source map URLs |
| **iOS Runtime** | 静态映射→Hook边界(请求构建器/加密helper/trust evaluator) |
| **Android Hooking** | 静态映射→Hook边界(JNI/signer/crypto/keystore/WebView bridge) |

**通用CTF原则：** 静态映射先行 → Hook最窄边界 → 证据三元组（静态位置+动态证明+状态依赖）

### 20. 逆向工具箱合集

| 工具 | 说明 |
|------|------|
| **y9nhjy/RE_Tools** | 全网逆向工具全集 |
| **tylerha97/awesome-reversing** | 精选逆向资源列表 |
| **alphaSeclab/awesome-reverse-engineering** | 逆向大合集 |

## 典型工作流

### Web JS 逆向
```
anti-debug → find-crypto-entry → env-patch → ast-deobfuscation → algorithm-reverse
```

### AI 驱动二进制逆向
```
GhidraMCP → 自动反编译 → LLM分析函数语义 → 自动重命名 → 提取协议/算法
```

### 二进制仿真
```
Qiling + Unicorn → 加载未知二进制 → 插桩跟踪 → 记录API调用 → 还原协议
```

### EDR对抗
```
指纹识别 → ntdll hook检测 → Halo's Gate解析SSN → indirect syscall → CallStackSpoof → ETW/AMSI patch
```

### 固件逆向
```
binwalk提取 → 文件系统挂载 → strings/EMBA扫描 → QEMU仿真 → Ghidra反编译 → 漏洞定位
```

### iOS反篡改检测
```
ipsw class-dump → 短类名比例检查 → grep PT_DENY_ATTACH/sysctl → iXGuard/OLLVM识别 → Frida注入绕过
```
