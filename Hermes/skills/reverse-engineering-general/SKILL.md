---
name: reverse-engineering-general
description: 通用逆向工程技能集合。8个逆向子技能：函数符号分析(rev-symbol)、数据结构重建(rev-struct)、Frida Hook脚本(rev-frida)、Unicorn模拟器调试(rev-unicorn-debug)、DEX内存dump脱壳(rev-dex-dumper)、Unity IL2CPP C#符号提取(rev-u3d-dump)、IDAPython脚本参考(rev-idapython)、APK纯Python静态分析(apk-static-analysis)。来自P4nda0s/reverse-skills。
category: reverse-engineering
subdomain: reverse
---

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

### Structure Recovery Steps

#### Step 1: Read Target Function
1. Based on the user-provided address, read `decompile/<address>.c`
2. Parse function metadata, extract callers and callees lists
3. Identify pointer parameters in the function (potential structure pointers)

#### Step 2: Collect Memory Access Patterns

Search for the following patterns in the target function:

**Direct offset access:**
```c
*(a1 + 0x10)           // offset 0x10
*(_DWORD *)(a1 + 8)    // offset 0x8, DWORD type
*(_QWORD *)(a1 + 0x20) // offset 0x20, QWORD type
*(_BYTE *)(a1 + 4)     // offset 0x4, BYTE type
```

**Array access:**
```c
*(a1 + 8 * i)          // array, element size 8 bytes
a1[i]                  // array access
```

**Nested structures:**
```c
*(*a1 + 0x10)          // first field of struct pointed by a1 is a pointer
```

**Record format:**
```
offset=0x00, size=8, access=read/write, type=QWORD
offset=0x08, size=4, access=read, type=DWORD
...
```

#### Step 3: Traverse Callers for Analysis

Read each caller function and analyze:
1. **Parameter passing**: What is passed when calling?
2. **Operations before/after the call**: allocation, initialization patterns
3. **Collect more offset accesses**

#### Step 4: Traverse Callees for Analysis

Read each callee function and analyze:
1. **How parameters are used**
2. **Passed to other functions**

#### Step 5: Aggregate and Infer

1. **Merge all offset information**, sort by offset
2. **Calculate struct size**: max(offset) + last_field_size
3. **Infer field types**:
   - Called as function pointer → function pointer
   - Passed to `strlen`/`printf` → string pointer
   - Compared with constants → enum/flags
   - Increment/decrement operations → counter/index
4. **Identify common patterns**:
   - Offset 0 is a function pointer table → vtable (C++ object)
   - next/prev pointers → linked list node
   - refcount field → reference counted object

### Output Format

```c
/*
 * Structure Recovery Analysis
 * Source function: <func_address>
 * Analysis scope: <number of callers/callees analyzed>
 */

// Estimated size: 0x48 bytes
// Confidence: High / Medium / Low

struct suggested_name {
    /* 0x00 */ void *vtable;           // vtable pointer
    /* 0x08 */ int refcount;           // reference count
    /* 0x0C */ int flags;              // flags
    /* 0x10 */ char *name;             // string
    /* 0x18 */ void *data;             // data pointer
    /* 0x20 */ size_t size;            // size field
    /* 0x28 */ struct node *next;      // linked list next
    /* 0x30 */ struct node *prev;      // linked list prev
    /* 0x38 */ callback_fn handler;    // callback function
    /* 0x40 */ void *user_data;        // user data
};
```

---

## Sub-Skill: rev-frida — Frida Script Generator

Generate Frida instrumentation scripts for dynamic analysis, hooking, and runtime inspection.

### Overview

Use Frida for:
- native export hooks
- Java or ObjC method hooks
- runtime tracing
- argument or return-value capture
- memory dumping
- loader-aware native instrumentation

### Important: Modern Frida CLI

The modern Frida CLI does not use `--no-pause`. A spawned process resumes after the script is loaded.

```bash
# Spawn and hook
frida -U -f com.example.app -l hook.js

# Attach to running process
frida -U com.example.app -l hook.js

# Attach by PID
frida -U -p 1234 -l hook.js
```

### Modern API Reference

**Module & Symbol Lookup:**
```javascript
const mod = Process.getModuleByName("libssl.so");
mod.name; mod.base; mod.size; mod.path;
const ptr = mod.getExportByName("SSL_read");
Process.enumerateModules();
mod.enumerateExports();
mod.enumerateImports();
```

**Interceptor:**
```javascript
Interceptor.attach(ptr, {
    onEnter(args) { console.log("arg0:", args[0].toInt32()); },
    onLeave(retval) { console.log("ret:", retval.toInt32()); }
});
Interceptor.replace(ptr, new NativeCallback(function (a0, a1) {
    return 0;
}, "int", ["pointer", "int"]));
```

**NativeFunction & NativeCallback:**
```javascript
const open = new NativeFunction(
    Module.getExportByName(null, "open"), "int", ["pointer", "int"]
);
const fd = open(Memory.allocUtf8String("/etc/hosts"), 0);
```

**Memory Operations:**
```javascript
ptr(addr).readByteArray(size);
ptr(addr).readUtf8String();
ptr(addr).readU32();
ptr(addr).readPointer();
Memory.scan(mod.base, mod.size, "48 89 5C 24 ??", { onMatch(address, size) {}, onComplete() {} });
```

**ObjC:**
```javascript
if (ObjC.available) {
    const hook = ObjC.classes.ClassName["- methodName:"];
    Interceptor.attach(hook.implementation, { onEnter(args) { ... } });
}
```

**Java:**
```javascript
if (Java.available) {
    Java.perform(function () {
        const Activity = Java.use("android.app.Activity");
        Activity.onCreate.implementation = function (bundle) {
            return this.onCreate(bundle);
        };
    });
}
```

### Script Generation Guidelines

1. Always use the modern API such as `Process.getModuleByName()` and `mod.getExportByName()`.
2. Do not use `--no-pause`.
3. Prefer load-event-driven native hooking over polling.
4. Print pointers and buffers in readable form.
5. Wrap risky hooks in `try/catch`.
6. Use `hexdump()` for binary inspection.

### Handle Native Module Load Timing

Do not assume a target `.so` is already loaded. Preferred order:
1. Hook `android_dlopen_ext` or `dlopen` and install hooks when the target library loads.
2. Use an immediate `Process.findModuleByName()` check for already-loaded modules.
3. Use polling only as a fallback.

Default helper:
```javascript
function hookModuleLoad(moduleName, callback) {
    const dlopen = Module.findGlobalExportByName("android_dlopen_ext")
        || Module.findGlobalExportByName("dlopen");
    const hooked = new Set();
    Interceptor.attach(dlopen, {
        onEnter(args) { this.path = args[0].isNull() ? null : args[0].readCString(); this.shouldHook = this.path && this.path.indexOf(moduleName) !== -1; },
        onLeave(retval) { if (!this.shouldHook || retval.isNull()) return; const mod = Process.findModuleByName(moduleName); if (!mod) return; const key = mod.base.toString(); if (hooked.has(key)) return; hooked.add(key); callback(mod); }
    });
}
```

### Do Not Blindly Hook init Series Functions

Prefer this order:
1. hook a stable exported function after module load
2. hook `RegisterNatives`, `dlsym`, or the first real business function
3. hook `JNI_OnLoad` only if native registration or anti-debug setup happens there
4. hook constructors or `.init_array` only if there is strong evidence that the critical logic is there

---

## Sub-Skill: rev-unicorn-debug — Unicorn Emulation Debugger

Debug and emulate specific code fragments or functions using the Unicorn engine.

### Core Principles

1. **Load file raw first** — do NOT parse ELF/PE/Mach-O headers. Read the file as raw bytes and map directly into Unicorn memory.
2. **Identify context dependencies** — analyze the target code for external calls (JNI, syscalls, libc, imports) and hook them to provide simulated responses.
3. **Use callbacks extensively** — leverage Unicorn's hook system for debugging, tracing, error recovery, and environment simulation.
4. **Iterative fix** — when emulation crashes, use the callback info to diagnose and fix.
5. **Minimal trace output** — prefer block-level tracing over instruction-level.

### Environment Simulation Strategy

| Category | Examples | Simulation Strategy |
|----------|----------|-------------------|
| libc | `malloc`, `free`, `memcpy`, `strlen`, `printf` | Hook address, implement logic in Python (bump allocator for malloc) |
| JNI | `GetStringUTFChars`, `FindClass`, `GetMethodID` | Build fake JNIEnv function table in UC memory |
| Syscalls | `read`, `write`, `mmap`, `ioctl` | Hook `UC_HOOK_INTR`, dispatch by syscall number |
| C++ runtime | `operator new`, `__cxa_throw` | Hook and simulate |
| Library calls | `pthread_mutex_lock`, `dlopen` | Hook and return success/stub |

### Callback Types to Use

| Callback | Purpose |
|----------|---------|
| `UC_HOOK_CODE` | Intercept import calls by address; instruction-level trace |
| `UC_HOOK_BLOCK` | Block-level trace (preferred over instruction trace) |
| `UC_HOOK_MEM_UNMAPPED` | Auto-map missing pages to recover from unmapped access errors |
| `UC_HOOK_MEM_READ \| UC_HOOK_MEM_WRITE` | Trace memory access on targeted data ranges only |
| `UC_HOOK_INTR` | Intercept SVC/INT for syscall simulation |

### Iterative Debugging Workflow

1. **Run** — start emulation, let it crash
2. **Read callback output** — which address faulted? What type?
3. **Diagnose**: unmapped memory → map it; import stub → add simulation; infinite loop → add counter
4. **Fix** — add the hook / map the memory / adjust registers
5. **Re-run** — repeat until the target function completes

### Architecture Quick Reference

| Arch | Uc Const | Mode | SP | LR | Args | Return | Syscall |
|------|----------|------|----|----|------|--------|---------|
| ARM64 | `UC_ARCH_ARM64` | `UC_MODE_LITTLE_ENDIAN` | SP | X30 | X0-X7 | X0 | X8 + SVC #0 |
| ARM32 | `UC_ARCH_ARM` | `UC_MODE_THUMB` / `UC_MODE_ARM` | SP | LR | R0-R3 | R0 | R7 + SVC #0 |
| x86-64 | `UC_ARCH_X86` | `UC_MODE_64` | RSP | (stack) | RDI,RSI,RDX,RCX,R8,R9 | RAX | RAX + syscall |
| x86-32 | `UC_ARCH_X86` | `UC_MODE_32` | ESP | (stack) | (stack) | EAX | EAX + int 0x80 |
| MIPS32 | `UC_ARCH_MIPS` | `UC_MODE_MIPS32 + UC_MODE_BIG_ENDIAN` | $sp | $ra | $a0-$a3 | $v0 | $v0 + syscall |

---

## Sub-Skill: rev-dex-dumper — Android DEX Dumper

Dump DEX files from a running Android application's memory using `panda-dex-dumper` via ADB.

### Workflow

1. **Push the tool to device:**
```bash
adb push <path-to>/panda-dex-dumper /data/local/tmp/
adb shell chmod +x /data/local/tmp/panda-dex-dumper
```

2. **Determine target package name** (if not provided):
```bash
adb shell dumpsys activity top | grep 'ACTIVITY' | tail -1 | awk '{print $2}' | cut -d/ -f1
```

3. **Run the dumper:**
```bash
adb shell "cd /data/local/tmp && ./panda-dex-dumper -p $(adb shell pidof <package_name>)"
```

4. **Pull DEX files to host:**
```bash
adb pull /data/local/tmp/panda/ ./
```

5. **Clean up device cache:**
```bash
adb shell rm -rf /data/local/tmp/panda/
adb shell rm /data/local/tmp/panda-dex-dumper
```

### Guidelines

1. **Always verify ADB connection first** — run `adb devices`
2. **Root may be required** — `panda-dex-dumper` uses `ptrace` to attach
3. **Wait for app to fully load** — the real DEX is only available after the packer has decrypted it
4. **Handle pidof failure** — launch the app with `adb shell monkey -p <package_name> -c android.intent.category.LAUNCHER 1`
5. **Multiple DEX files are normal** — packed apps often produce several DEX files
6. **Always clean up** — remove both the dumped DEX files and the tool binary from the device

---

## Sub-Skill: rev-u3d-dump — Unity IL2CPP Symbol Dumper

Extract C# method names, addresses, and type definitions from Unity IL2CPP builds for IDA/Ghidra analysis.

### Key Files in Unity Build

| File | Location | Purpose |
|------|----------|---------|
| Native binary | iOS: `Frameworks/UnityFramework.framework/UnityFramework` / Android: `lib/{arch}/libil2cpp.so` | Compiled C# code |
| Metadata | `Data/Managed/Metadata/global-metadata.dat` | All type/method/string info |

### Tool Selection

- **Il2CppDumper v39 fork** (recommended for metadata v39+): `https://github.com/roytu/Il2CppDumper` (branch: `v39`), supports metadata v24–v39
- **Original Il2CppDumper**: `https://github.com/Perfare/Il2CppDumper`, only supports up to v29
- **Cpp2IL** (alternative): `https://github.com/SamboyCoding/Cpp2IL`, supports metadata v39

### Step-by-Step Workflow

**Step 1: Locate IL2CPP Files** (unzip IPA/APK, find binary + metadata)

**Step 2: Check Metadata Version:**
```bash
xxd -l 8 "$METADATA"
# Expected: af1b b1fa 2700 0000 → version = 0x27 = 39
```

| Version | Unity | Tool |
|---------|-------|------|
| ≤ 29 | Unity 2021 and earlier | Original Il2CppDumper |
| 31 | Unity 2022 | Original Il2CppDumper (partial) |
| 39 | Unity 6 (6000.x) | **roytu/Il2CppDumper v39 fork** |

**Step 3: Build & Run Il2CppDumper (v39 fork):**
```bash
git clone -b v39 https://github.com/roytu/Il2CppDumper.git
cd Il2CppDumper
DOTNET_ROLL_FORWARD=LatestMajor dotnet build -c Release
DOTNET_ROLL_FORWARD=LatestMajor dotnet run \
  --project Il2CppDumper/Il2CppDumper.csproj \
  -c Release --framework net8.0 \
  -- "$BINARY" "$METADATA" output_dir
```

**Step 4: Verify Output** — Successful run produces `script.json`, `dump.cs`, `il2cpp.h`, `ida_py3.py`

**Step 5: Import into IDA** — Open binary in IDA, run `ida_py3.py` script with `script.json` in same directory

**Step 5 (alt): Import into Ghidra** — Use `ghidra.py` or `ghidra_with_struct.py` script

### Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `not a supported version[39]` | Using original Il2CppDumper | Switch to v39 fork |
| Exit code 137 (SIGKILL) | macOS unsigned binary | `codesign -s - <binary>` |
| `Cannot read keys` (exit 134) | Non-interactive console | Ignore — dump completed |
| `DOTNET_ROLL_FORWARD` error | .NET version mismatch | Set `DOTNET_ROLL_FORWARD=LatestMajor` |
| Empty output | Wrong binary/metadata pair | Verify both files are from the same build |

---

## Sub-Skill: rev-idapython — IDAPython / IDALib Script Reference

IDAPython script snippets for IDA interactive use and IDALib headless analysis.

- **IDAPython**: scripts run inside IDA GUI (Script Command, plugin, or IDC console)
- **IDALib**: headless mode introduced in IDA 9.0 — run analysis scripts without opening the IDA GUI

### Common API

**Register Operations:**
```python
idc.get_reg_value('rax')
idaapi.set_reg_val("rax", 1234)
```

**Debug Memory Operations:**
```python
idc.read_dbg_byte(addr)
idc.read_dbg_memory(addr, size)
idc.read_dbg_dword(addr)
idc.read_dbg_qword(addr)
idc.patch_dbg_byte(addr, val)
idc.add_bpt(0x409437)
idaapi.get_imagebase()
```

**Local Memory Operations (modifies IDB database):**
```python
idc.get_qword(addr)
idc.patch_qword(addr, val)
idc.patch_dword(addr, val)
idc.patch_word(addr, val)
idc.patch_byte(addr, val)
idc.get_db_byte(addr)
idc.get_bytes(addr, size)
idaapi.get_dword(addr)
idc.get_strlit_contents
```

**Disassembly:**
```python
GetDisasm(addr)
idc.next_head(ea)
idc.create_insn(addr)
ida_bytes.create_strlit
ida_funcs.add_func(addr)
idc.del_items(addr)
```

**Function Operations:**
```python
ida_funcs.get_func(ea)
for func in idautils.Functions():
    print("0x%x, %s" % (func, idc.get_func_name(func)))
```

### Key Code Snippets

**Byte Pattern Search:**
```python
def find_bytes_list(bytes_pattern):
    ea = -1
    result = []
    while True:
        ea = idc.find_bytes(bytes_pattern, ea + 1)
        if ea == ida_idaapi.BADADDR:
            break
        result.append(ea)
    return result
```

**Cross References:**
```python
for ref in idautils.XrefsTo(ea):
    print(hex(ref.frm))
```

**Basic Block Traversal:**
```python
fn = 0x4800
f_blocks = idaapi.FlowChart(idaapi.get_func(fn), flags=idaapi.FC_PREDS)
for block in f_blocks:
    print(hex(block.start_ea))
```

**Decompile a Function:**
```python
dec = ida_hexrays.decompile(func_addr)
print(str(dec))
```

**Hex-Rays Microcode at Different Maturity Levels:**
```python
def print_microcode(func_ea):
    maturity = ida_hexrays.MMAT_GLBOPT3
    hf = ida_hexrays.hexrays_failure_t()
    pfn = idaapi.get_func(func_ea)
    rng = ida_hexrays.mba_ranges_t(pfn)
    mba = ida_hexrays.gen_microcode(rng, hf, None, ida_hexrays.DECOMP_WARNINGS, maturity)
    vp = ida_hexrays.vd_printer_t()
    mba._print(vp)
```

**OLLVM - Set Breakpoints on Real Blocks:**
```python
fn = 0x401F60
ollvm_tail = 0x405D4B
f_blocks = idaapi.FlowChart(idaapi.get_func(fn), flags=idaapi.FC_PREDS)
for block in f_blocks:
    for succ in block.succs():
        if succ.start_ea == ollvm_tail:
            print(hex(block.start_ea))
            idc.add_bpt(block.start_ea)
```

**NOP Function:**
```python
def nop_func(addr_func, arch='arm'):
    func = ida_funcs.get_func(addr_func)
    start, end = func.start_ea, func.end_ea
    nop_bytes = [0x90] if arch == 'x86' else [0x1F, 0x20, 0x03, 0xD5]
    ea = start
    while ea < end:
        insn = ida_ua.insn_t()
        length = ida_ua.decode_insn(insn, ea)
        for i in range(0, length, len(nop_bytes)):
            for j in range(len(nop_bytes)):
                if i + j < length:
                    idc.patch_byte(ea + i + j, nop_bytes[j])
        ea += length
```

### IDALib (Headless IDA, IDA 9.0+)

```python
import idapro
import idautils
import idc

ida.open_database("samples/patch.so", True)
for func in idautils.Functions():
    func_name = idc.get_func_name(func)
    print("Function Name: {}, Address: {}".format(func_name, hex(func)))
ida.close_database(save=True)
```

**Batch Decompile to JSON:**
```python
import idapro, ida_hexrays, idautils, idc, json

def _decompile_internal():
    result = []
    for func in idautils.Functions():
        func_name = idc.get_func_name(func)
        dec_obj = ida_hexrays.decompile(func)
        if dec_obj is None: continue
        result.append({'name': func_name, 'address': hex(func), 'decompiled': str(dec_obj)})
    return result

def decomple_export(file, out_file):
    ida.open_database(file, True)
    r = _decompile_internal()
    ida.close_database(save=False)
    open(out_file, "w").write(json.dumps(r, indent=4))
```

### Import Table Enumeration

```python
import ida_nalt
nimps = ida_nalt.get_import_module_qty()
for i in range(nimps):
    name = ida_nalt.get_import_module_name(i)
    def imp_cb(ea, name, ordinal):
        if not name: print("%08x: ordinal #%d" % (ea, ordinal))
        else: print("%08x: %s (ordinal #%d)" % (ea, name, ordinal))
        return True
    ida_nalt.enum_import_names(i, imp_cb)
```

### Type Information

```python
def extract_struct_members(type_name):
    fields = []
    tif = ida_typeinf.tinfo_t()
    if tif.get_named_type(None, type_name):
        for iter in tif.iter_struct():
            fsize = iter.type.get_size()
            fields.append({"offset": iter.offset // 8, "size": fsize, "type": iter.type._print()})
    return fields
```
