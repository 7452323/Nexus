---
name: android-reverse
category: reverse-engineering
description: >-
  Merged skill combining: android-reverse-engineering, reverse-engineering-general.
version: "1.0"
sources:
  - android-reverse-engineering
  - reverse-engineering-general
tags: [reverse-engineering, merged]
---

# android-reverse

> **Merged from**: android-reverse-engineering, reverse-engineering-general
> **Source count**: 2

---

## Table of Contents

1. [android-reverse-engineering](#android-reverse-engineering)
2. [reverse-engineering-general](#reverse-engineering-general)

---

## android-reverse-engineering

1|---
2|name: android-reverse-engineering
3|description: Android应用逆向技能。APK反编译/smali修改/Frida Hook/JNI分析/脱壳/重打包签名全流程。
4|author: 7452323 (converted from Private Gist)
5|tags:
6|  - android
7|  - apk
8|  - smali
9|  - frida
10|  - reverse-engineering
11|  - mobile-security
12|---
13|
14|# Android Reverse Engineering — Android应用逆向技能
15|
16|## 工具链
17|
18|| 工具 | 用途 |
19||------|------|
20|| apktool | APK 反编译/重打包 |
21|| jadx-gui | Java 源码反编译 |
22|| FRIDA | 动态 Hook |
23|| objection | 移动端安全测试 |
24|| Android Studio | JNI 分析、动态调试 |
25|| Ghidra | SO 原生库分析 |
26|
27|## 通用流程
28|
29|### 1. 静态分析
30|```
31|APK → jadx 查看 Java 层 → apktool 提取 smali → 搜索关键字符串/URL/Key
32|```
33|
34|### 2. 动态 Hook
35|```
36|Frida 注入 → Java.perform → 定位类/方法 → Hook onEnter/onLeave
37|```
38|
39|### 3. JNI 分析
40|```
41|找到 System.loadLibrary → 定位 native 方法 → IDA/Ghidra 分析 SO
42|```
43|
44|### 4. 脱壳
45|```
46|检测壳类型 → dump dex → 修复 dex → jadx 查看
47|```
48|
49|### 5. 重打包签名
50|```
51|apktool b → jarsigner/apksigner → 安装测试
52|```
53|
54|## Frida 常用脚本模板
55|
56|```javascript
57|// Hook Java 方法
58|Java.perform(function() {
59|    var cls = Java.use('com.example.ClassName');
60|    cls.methodName.implementation = function() {
61|        console.log('called');
62|        return this.methodName();
63|    };
64|});
65|
66|// 打印参数和返回值
67|Java.perform(function() {
68|    var cls = Java.use('com.example.ClassName');
69|    cls.methodName.overload('java.lang.String').implementation = function(s) {
70|        console.log('arg:', s);
71|        var ret = this.methodName(s);
72|        console.log('ret:', ret);
73|        return ret;
74|    };
75|});
76|```
77|
## Flutter 应用逆向专项

### 识别
```bash
# Flutter APK 特征
unzip -l app.apk | grep "libapp.so"      # Flutter engine
unzip -l app.apk | grep "flutter"          # Flutter 相关文件
unzip -l app.apk | grep "icudtl.dat"       # ICU 数据（Flutter 特征）

# 目录结构特征
# Flutter APK: lib/arm64-v8a/libapp.so + libflutter.so
# 原生 APK: lib/arm64-v8a/*.so (业务代码在多个 so 中)
```

### 工具链
| 工具 | 安装方式 | 用途 |
|------|---------|------|
| **Blutter** | `pip install blutter` 或从源码编译 | Flutter `libapp.so` 反编译 → Dart 汇编 + 伪代码 |
| **strings + grep** | 系统自带 | 搜索 Key/IV/Salt/URL 等常量 |
| **Playwright** | `pip install playwright` | Flutter Web 版网络请求拦截 + JS 代码提取 |
| **HAR 抓包文件** | 直接使用 | 已有抓包数据快速验证签名算法 |

> ⚡ Blutter 无需预装！遇到 Flutter 逆向任务时自动安装。

### 核心方法：Blutter 反编译

```bash
# 0. 自动安装 Blutter（遇到 Flutter 任务时 Hermes 自动执行）
pip install blutter 2>/dev/null || {
    git clone https://github.com/nicknisi/blutter.git /tmp/blutter
    cd /tmp/blutter && pip install -e .
}

# 1. 反编译 libapp.so
blutter path/to/libapp.so output_dir/

# 2. 输出内容
# output_dir/objs/  — Dart 汇编 .S 文件
# output_dir/ida/   — IDA Pro 脚本
# output_dir/blutter_output.txt — 字符串表 + 函数索引

# 3. 搜索关键常量（优先级排序）
grep -ri "http" output_dir/ | head -30          # API URL
grep -ri "aes\|encrypt\|decrypt" output_dir/ | head -20  # 加解密
grep -ri "sign" output_dir/ | head -20          # 签名
grep -ri "token\|jwt" output_dir/ | head -20  # Token
grep -ri "key\|iv\|salt" output_dir/ | head -20  # 密钥
```

### 典型逆向路径：ONE App 案例

```
┌── Step 1: Blutter libapp.so ──────────────────────┐
│  → 找到 AES Key: "l*bv%Ziq000Biaog"                │
│     AES IV:  "8597506002939249"                    │
│     Sign Salt: "m4n2hjPeYWkD6tFpqKF^3HO^h24P@idT" │
│     API Version: "v2.5"                             │
│     (都在 app_container.dart 构造函数中)             │
└───────────────────────────────────────────────────┘
    │
    ▼
┌── Step 2: 分析请求/响应格式 ─────────────────────┐
│  → net_manager.dart 的 createHeaders 方法          │
│  → 请求: 明文body → AES-CBC → Base64 → POST body  │
│  → 响应: Base64 → AES-CBC → unpad → JSON          │
│  → Content-Type: application/x-www-form-urlencoded │
└───────────────────────────────────────────────────┘
    │
    ▼
┌── Step 3: 破解签名算法 ──────────────────────────┐
│  → 拼接: {ip}.{platform}.{timestamp}.{userKey}.{uuid}  │
│  → 签名: MD5(MD5(拼接字符串) + salt)                   │
│  → 验证: 用 HAR 抓包文件的 sign 值对比                 │
│  → ⚠ 注意: Web 版和原生版可能算法不同！                │
└───────────────────────────────────────────────────┘
    │
    ▼
┌── Step 4: 找到无Token入口点 ────────────────────┐
│  → 搜索 bootstrap、init、guest 等关键词              │
│  → 发现 /v2.5/bootstrap 不需要 JWT Token！           │
│  → 只需要 uuid + user-key + signature                 │
│  → 返回全新 JWT Token → 破解了认证死循环              │
└───────────────────────────────────────────────────┘
    │
    ▼
┌── Step 5: 破解 CDN 图片加密 ────────────────────┐
│  → 图片 URL 路径已知但 API 域名返回 500               │
│  → Playwright 打开 Flutter Web 版 (j7tu.com)          │
│  → 拦截网络请求 → 发现真正的 CDN 域名                 │
│  → 拦截 main.dart.js → 搜索已知 Key → 找到图片解密 Key │
│  → 图片解密: AES-128-CBC(key, iv) → 标准 JPEG         │
└───────────────────────────────────────────────────┘
```

### 关键发现（ONE App 案例参数）

| 参数 | 值 |
|------|-----|
| AES Key | `l*bv%Ziq000Biaog` |
| AES IV | `8597506002939249` |
| 模式 | AES-128-CBC + PKCS7 |
| Sign Salt | `m4n2hjPeYWkD6tFpqKF^3HO^h24P@idT` |
| Sign 算法 | `MD5(MD5(ip.platform.ts.uk.uuid) + salt)` |
| 拼接格式 | `{ip}.{platform}.{ts}.{userKey}.{uuid}` |
| CDN 图片 Key | `saIZXc4yMvq0Iz56` |
| CDN 图片 IV | `kbJYtBJUECT0oyjo` |
| API Version | `v2.5` |
| Response 解密 | `unpad(AES-CBC.decrypt(b64decode(resp)))` |

### Flutter Web 版辅助分析

```bash
# Flutter Web 编译为 main.dart.js（~6.6MB）
# 代码极混淆，但字符串常量保留

# 方法一：字符串搜索（不依赖反编译）
grep -oP '.{0,20}(key|iv|salt|aes|token).{0,20}' main.dart.js | sort -u

# 方法二：Playwright 网络请求拦截
# from playwright.sync_api import sync_playwright
# with sync_playwright() as p:
#     browser = p.chromium.launch()
#     page = browser.new_page()
#     page.on("response", lambda resp: print(resp.url, resp.status))
#     page.goto("https://target.com")

# 方法三：HAR 文件验证（已有抓包记录）
# 直接对比签名字符串验证算法正确性
```

### AES-128-CBC 解密模板

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64, json

def decrypt_response(encrypted_b64: str, key: bytes, iv: bytes) -> dict:
    """解密 API 响应"""
    raw = base64.b64decode(encrypted_b64)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(raw), 16)
    return json.loads(decrypted)

def decrypt_image(encrypted_data: bytes, key: bytes, iv: bytes) -> bytes:
    """解密 CDN 加密图片"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_data)
    # 去除 PKCS7 填充
    pad_len = decrypted[-1]
    if 1 <= pad_len <= 16:
        decrypted = decrypted[:-pad_len]
    return decrypted
```

### 签名生成模板

```python
import hashlib, time

def generate_sign(ip: str, platform: str, ts: str, user_key: str, uuid: str, salt: str) -> str:
    """生成 API 签名"""
    raw = f"{ip}.{platform}.{ts}.{user_key}.{uuid}"
    first_md5 = hashlib.md5(raw.encode()).hexdigest()
    return hashlib.md5((first_md5 + salt).encode()).hexdigest()
```

### 常见陷阱

| 问题 | 原因 | 解决 |
|------|------|------|
| 签名不匹配 | platform 值不同（Web vs iOS） | 确认当前是哪个平台请求 |
| JWT 401 | token 过期或 IP 绑定 | re-bootstrap 拿新 JWT |
| CDN 图片 500 | 路由不存在 | 图片 URL 拼的是错误的域名 |
| 解密后乱码 | Key/IV 或模式错误 | 验证 AES-128-CBC + PKCS7 |
| Bootstrap 失效 | 服务器更新 | 重新反编译找新端点 |

---

## reverse-engineering-general

[English](README_EN.md) | 中文

# 逆向工程技能集 (Reverse Engineering Skills)

逆向工程分析技能，支持 40+ 种 AI 编程工具。

**专为 [IDA-NO-MCP](https://github.com/P4nda0s/IDA-NO-MCP) 设计** - 从 IDA 导出反编译结果，然后使用 AI 编程工具进行分析。

## 包含的技能

| 技能 | 描述 |
|------|------|
| `rev-symbol` | 从导出表/导入表或反编译代码分析函数符号 |
| `rev-struct` | 从反编译函数重建数据结构 |
| `rev-frida` | 使用现代 Frida API 生成动态插桩脚本 |
| `rev-unicorn-debug` | 使用 Unicorn 引擎模拟执行和调试指定代码片段 |
| `rev-dex-dumper` | 从运行中的 Android 应用内存中 dump DEX 文件，用于整体加固脱壳 |
| `rev-u3d-dump` | 从 Unity IL2CPP 构建中提取 C# 符号地址，生成 IDA/Ghidra 导入脚本 |
| `rev-idapython` | IDAPython / IDALib 脚本参考，涵盖调试、内存操作、反编译、混淆辅助、批量分析等 |
| `apk-static-analysis` | **纯 Python APK 静态分析**（androguard + lief + zipfile），无需 Java/JADX。覆盖 DEX 类发现、SO 符号提取、常见框架识别（sing-box/Clash/V2rayNG）、节点/订阅提取、AES-CBC 加密还原、DNS TXT 端点发现、fetchNodesFromApi 调用链追踪。详见 [references/apk-static-analysis.md](references/apk-static-analysis.md) |
| `wechat-miniprogram-reverse` | **微信小程序 .wxapkg 逆向**：V1MMWX 加密解密（PBKDF2+AES-CBC+XOR）、解包、源码分析、登录凭证机制分析。详见 [references/wechat-miniprogram-reverse.md](references/wechat-miniprogram-reverse.md) |
| `pyinstaller-exe-reverse` | **PyInstaller EXE 逆向 + 跨平台移植**：识别打包器→pyinstxtractor提取→.pyc反编译→源码分析→macOS/Linux移植。详见 [references/pyinstaller-exe-reverse.md](references/pyinstaller-exe-reverse.md) |
| `stripped-swift-binary` | **Stripped Swift 二进制分析**：当主二进制被 strip、strings/otool 返回空时的应对方法。Mach-O Load Command 解析、Xcode Preview 存根识别、.debug.dylib 定位、__cstring 段提取。详见 [references/stripped-swift-binary-analysis.md](references/stripped-swift-binary-analysis.md) |
| `ios-binary-api-reconstruction` | **iOS Swift 二进制 API 接口重建**：从 .debug.dylib 中重建完整的 API 接口列表——六步流程（URL→正则→JSON键→类层次→方法签名→数据流），覆盖纯 strings+grep 无 class-dump 的分析方法。详见 [references/ios-binary-api-reconstruction.md](references/ios-binary-api-reconstruction.md) |
| `ios-swift-binary-ui-reconstruction` | **iOS Swift 二进制 UI 重建**：纯Python + llvm-objdump从解密IPA重建完整SwiftUI代码（类名+UI字符串+Swift5反射）——6阶段流程（解压→llvm-objdump定位sections→提取__swift5_reflstr字段→提取__cstring中文UI文本→重建架构→生成SwiftUI代码）。当otool/class-dump/swift-demangle不可用时，用llvm-objdump -h获取section表，再用Python read_bytes直接在各section内提取null-terminated字符串。详见 [references/ios-swift-binary-ui-reconstruction.md](references/ios-swift-binary-ui-reconstruction.md) |
| `ios-production-binary-api-reconstruction` | **iOS 生产构建 API 接口重建**：无 .debug.dylib 时，从主二进制直接提取所有 API — 区分 A(真实HTTP)/B(WebView+远程页面)/C(WebView+直接解析)三类调用，CloudKit检测判断有无自建后端，嵌入式JS scraping scripts提取（覆盖小红书/Instagram/Threads等16+平台）。Procut v1.3.4 实测：纯客户端零服务器架构。含抖音去水印完整实现（API端点+参数+JS注入+ObjC符号表+域名白名单）和 B站去水印完整实现（两步API + WebView兜底 + ObjC符号表）。详见 [references/ios-production-binary-api-reconstruction.md](references/ios-production-binary-api-reconstruction.md) |
| `xhs-troubleshooting-2026` | **小红书下载失败排查**：Procut iPad 端 XHS 图片/笔记下载失败的根因分析——Cookie分组特性（移动端vs桌面端Session）、地理限制（geo-restriction）、CDN URL规律、Procut WebView请求环境指纹要求。含实测 cookie 对比数据和排查命令模板。详见 [references/xhs-troubleshooting-2026.md](references/xhs-troubleshooting-2026.md) |
| `hermes-runtime-security-2026` | **Hermes Agent 安全机制关闭记录**：Gateway Lifecycle Guard / Approvals Mode / Secret Redaction / Tirith 等安全层的关闭方法、恢复方法和快照机制。含一键恢复脚本。由用户明确要求关闭，记录以备后续 session 快速恢复。详见 [references/hermes-runtime-security-2026.md](references/hermes-runtime-security-2026.md) |
| `wechat-plugin-hook-analysis` | **iOS 微信插件逆向分析**：越狱 Tweak / .dylib 注入插件的逆向方法论——hook ObjC 方法还原、消息拦截调用链重建、AI 视频生成接口定位、安全风险审计。覆盖 PKCWeChatTools v0.9-8 实战案例（hook BaseMsgContentLogicController → pkcAIVideoGenMsg → AddVideoMsg → sendVideo 完整链路）。详见 [references/wechat-plugin-hook-analysis.md](references/wechat-plugin-hook-analysis.md) |

## 安装

```bash
npx skills add P4nda0s/reverse-skills
```

### 更新与卸载

```bash
# 检查更新
npx skills check

# 更新
npx skills update

# 卸载
npx skills remove rev-symbol rev-struct
```

## 许可证

MIT

---

## Sub-Skill: apk-static-analysis — Android APK Static Analysis (Python-Only)

Pure Python pipeline for static APK analysis when Java/JADX are unavailable. Uses `androguard` (DEX), `lief` (SO), and `zipfile` (extraction).

**Full methodology and code examples**: [references/apk-static-analysis.md](references/apk-static-analysis.md)

### When to Use

- User provides an APK file for reverse engineering
- No Java runtime available (can't use JADX/apktool)
- Need quick class/symbol reconnaissance before deeper analysis
- Analyzing proxy/VPN apps (sing-box, Clash, V2rayNG) for node/subscription extraction

### Quick Start

```python
from androguard.misc import AnalyzeAPK
a, d, dx = AnalyzeAPK("app.apk")
# Suppress verbose logging:
# import logging; logging.getLogger('androguard').setLevel(logging.WARNING)
```

### Pipeline Phases

1. **Quick Recon** — zipfile structure, tech stack detection (Flutter/RN/sing-box)
2. **DEX Analysis** — androguard class discovery + method disassembly
3. **SO Analysis** — lief symbol extraction, Go/JNI bridge identification
4. **Framework ID** — match against known proxy app frameworks
5. **Node Extraction** — trace subscription fetch → decrypt → store pipeline

### Common Proxy App Frameworks

| Framework | Signals | Key Classes |
|-----------|---------|-------------|
| sing-box (SFA) | `libbox.so`, `io.nekohasekai.*` | `BoxService`, `ProfileDecoder`, `ImportRemoteProfile` |
| Clash/CMFA | `libclash.so`, `com.github.kr328.clash.*` | `ClashService`, `ProfileProvider` |
| V2rayNG | `libv2ray.so`, `com.v2ray.ang.*` | `V2RayServiceManager` |

### Pitfalls

- Androguard is verbose — suppress DEBUG logging before use
- No full Java decompilation without JADX — androguard gives disassembly only
- Go SO files (libbox.so) have 1000+ exports — filter by `Java_` prefix for JNI bridges
- Python 3.9 on macOS system — don't use 3.10+ syntax

---

## Sub-Skill: rev-symbol — Symbol Recovery

Analyze function code characteristics to recover/identify function symbols and names.

### Pre-check

**Determine which IDA access method is available:**

**Option A — IDA Pro MCP (preferred if connected):**
Check if the IDA Pro MCP server is connected (look for an active `ida-pro` or equivalent MCP connection). If connected, you can query IDA directly via MCP tools — no exported files needed. Proceed with the analysis using MCP.

**Option B — IDA-NO-MCP exported data:**
If MCP is not connected, check if IDA-NO-MCP exported data exists in the current directory:

1. Check if `decompile/` directory exists
2. Check if there are `.c` files inside

If neither MCP nor exported data is available, prompt the user:
```
No IDA access method detected. Choose one of the following:

Option A — IDA Pro MCP (recommended):
  Connect the IDA Pro MCP server so Claude can query IDA directly.

Option B — IDA-NO-MCP export:
  1. Download plugin: https://github.com/P4nda0s/IDA-NO-MCP
  2. Copy INP.py to IDA plugins directory
  3. Press Ctrl-Shift-E in IDA to export
  4. Open the exported directory with Claude Code
```

### Export Directory Structure

```
./
├── decompile/              # Decompiled C code directory
│   ├── 0x401000.c          # One file per function, named by hex address
│   ├── 0x401234.c
│   └── ...
├── decompile_failed.txt    # Failed decompilation list
├── decompile_skipped.txt   # Skipped functions list
├── strings.txt             # String table (address, length, type, content)
├── imports.txt             # Import table (address:function_name)
├── exports.txt             # Export table (address:function_name)
└── memory/                 # Memory hexdump (1MB chunks)
```

### Function File Format (decompile/*.c)

Each `.c` file contains function metadata comments and decompiled code:

```c
/*
 * func-name: sub_401000
 * func-address: 0x401000
 * callers: 0x402000, 0x403000    // List of functions that call this function
 * callees: 0x404000, 0x405000    // List of functions called by this function
 */

int __fastcall sub_401000(int a1, int a2)
{
    // Decompiled code...
}
```

### Symbol Recovery Steps

#### Step 1: Analyze Internal Characteristics

Carefully examine the target function for:

- **String constants**: Strings used in the function may reveal its purpose
- **Numeric constants / Magic Numbers**: 
  - MD5: `0x67452301`, `0xEFCDAB89`, `0x98BADCFE`, `0x10325476`
  - CRC32: `0xEDB88320`
  - Base64 charset: `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/`
  - AES S-Box: `0x63, 0x7C, 0x77, 0x7B...`
  - Zlib: `0x78`, `0x9C` (compression header)
  - other constants/magic numbers...
- **Code structure**: Loop patterns, bitwise operations, specific algorithm flows

If you can identify a known algorithm through constants/structure, tell the user directly.

#### Step 2: Analyze Cross-References

**Analyze Callees (called functions):**
- Read functions in the callees list
- For each callee, check if its address exists in `imports.txt`
- Recognize call patterns even when symbols are missing

**Analyze Callers (calling functions):**
- Read functions in the callers list
- If a caller has a symbol (check exports.txt), infer the callee's purpose from context
- Recursive check: trace up the call chain until you find a function with a symbol
- Analyze how the return value is used by callers

#### Step 3: Information Gathering and Search

Collect the following information:
- Strings in the function (check `strings.txt` for addresses used in the function)
- Magic Numbers / constants
- Known imports called (cross-reference callees with `imports.txt`)
- Caller/callee symbols from `exports.txt`
- Paired function patterns identified

Based on collected information:
1. First attempt local reasoning based on function signature, paired call patterns, known imports, code structure similarity
2. If uncertain, use **Web Search** to search Magic Numbers, code patterns, unique strings, parameter patterns

### Output Format

```
## Symbol Recovery Analysis: <function_address>

### Function Characteristics
- Strings: <list discovered strings>
- Constants: <list key constants>
- Called imports: <list>

### Cross-Reference Analysis
- Callers: <callers and their symbols>
- Callees: <callees and their symbols>

### Inference Result
- **Suggested symbol name**: <suggested_name>
- **Confidence**: High / Medium / Low
- **Reasoning**: <explain why this name is suggested>

### Similar Open Source Implementation
- <if similar open source code is found, provide link>
```

---

## Sub-Skill: rev-struct — Structure Recovery

Recover data structure definitions by analyzing memory access patterns in functions and their call chains.

### Pre-check

Same as rev-symbol (IDA Pro MCP or IDA-NO-MCP exported data).

### Recovery Steps

1. Based on user-provided address, read `decompile/<address>.c` and extract callers/callees
2. Collect memory access patterns (direct offset, array, nested struct)
3. Traverse callers for parameter passing and initialization patterns
4. Traverse callees for parameter usage
5. Aggregate all offset information, calculate struct size, infer field types

### Output Format

The recovered struct definition.

---

## Sub-Skill: rev-frida — Frida Script Generator

Generate Frida instrumentation scripts for dynamic analysis. See full reference above in the main skill table.

---

## Sub-Skill: rev-unicorn-debug — Unicorn Emulation Debugger

Emulate code with Unicorn engine. See full reference above.

---

## Sub-Skill: rev-dex-dumper — Android DEX Dumper

Dump DEX from running Android app. See full reference above.

---

## Sub-Skill: rev-u3d-dump — Unity IL2CPP Symbol Dumper

Dump C# symbols from Unity IL2CPP builds. See full reference above.

---

## Sub-Skill: rev-idapython — IDAPython Scripts

Script snippets for IDA. See full reference above.

---

## Sub-Skill: ios-swift-binary-ui-reconstruction — iOS Swift Binary UI Reconstruction

Reverse-engineer a Swift iOS app's complete UI from a decrypted IPA's Mach-O binary using Python + llvm-objdump. Covers UUID extraction, section mapping, Chinese UI text extraction, Swift5 reflection string parsing, and SwiftUI code generation. See [references/ios-swift-binary-ui-reconstruction.md](references/ios-swift-binary-ui-reconstruction.md) for the full 6-phase workflow.

### When to Use

- User provides a decrypted .ipa and wants the actual UI code (not description)
- `otool`/`class-dump`/`swift-demangle` unavailable on a Linux analysis box
- Swift5 metadata sections are present and symbols are in `__swift5_reflstr`
- Need to reconstruct app architecture from class names alone

### Core Insight

`llvm-objdump` (from LLVM toolchain, NOT standard Linux `objdump`) can read arm64 Mach-O on Linux. Combined with Python `read_bytes()`, you can directly extract ALL strings from `__swift5_reflstr` (Swift class/field names) and `__cstring` (literal UI text including Chinese). This replaces the entire class-dump / strings / otool workflow on platforms where those tools don't exist.

### Quick Path

```bash
# 1. Extract the IPA (it's a zip)
unzip -q "App.ipa" -d /tmp/ipa_payload

# 2. Get section table (this is the critical step)
llvm-objdump -h "Payload/App.app/App" | grep -E "(swift5_reflstr|cstring|typeref|fieldmd|types|proto)"

# 3. In Python, exec:
data = open("Payload/App.app/App", "rb").read()
# Use offsets from (2) to slice null-terminated strings
```

**Do NOT** try to parse Mach-O load commands with Python `struct`. Use `llvm-objdump` for section headers, then use the `size` column as the hard read limit in Python.

---
