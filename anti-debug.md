---
name: anti-debug
description: JS反调试对抗 + 二进制级反调试技能。识别并绕过4类JS反调试手段（无限debugger、DevTools检测、时间检测、属性检测。统一5步流程），以及Linux/Windows原生反调试、反VM、反DBI、代码完整性检测。
author: 7452323 (converted from Private Gist)
tags:
  - anti-debug
  - anti-devtools
  - debugger
  - js-reverse
---

# Anti-Debug — JS反调试对抗技能

## 4类反调试

### 1. 无限 debugger

| 模式 | 特征 | 绕过方式 |
|------|------|----------|
| constructor | `function(){}["constructor"](...)` | 重写 constructor |
| setInterval | 定时触发 debugger | 拦截 setInterval |
| eval | eval 中注入 debugger | 重写 eval |
| Function | new Function('debugger') | 重写 Function |
| Object.defineProperty | getter/setter 触发 | 提前 Hook |
| iframe | 子页面 debugger | 拦截 iframe 创建 |
| worker | Web Worker debugger | 拦截 Worker |
| catch 异常触发 | try-catch 触发 | Hook 异常 |
| Date 定时 | Date.now 差值检测 | 覆盖 Date.now |

### 2. DevTools 检测 + 额外反调试类型

- 元素检测：`toString.call(element)`
- 控制台检测：`console.log` 是否被重写
- 窗口大小检测
- 颜色格式检测

额外反调试类型：

| 类型 | 常见实现 | 检测方法 | 绕过方式 |
|------|---------|---------|----------|
| 抗格式化(tamper) | 代码被格式化后自毁 | 正则/Token验证 | 运行时Hook `toString` |
| anti-Selenium | 检测`navigator.webdriver`等 | 属性检测 | 修复webdriver+伪造指纹 |
| 域名验证 | 检测域名不匹配则卡死 | `location.hostname` | mock域名+阻断死循环 |

### 3. 时间检测
- `Date.now` / `performance.now` 差值
- setTimeout 延迟分析

### 4. 属性检测
- `element[n]` 访问
- 原型链遍历
- 异常消息解析

## 统一5步流程

1. 识别反调试类型（断点定位触发点）
2. Hook 关键函数（constructor/setInterval/eval/Function）
3. 替换实现（返回无操作的 stub）
4. 验证绕过（确认代码正常运行）
5. 固化补丁（保存到环境补丁中）

---

## Binary-Level Anti-Debug & Anti-Analysis (absorbed from reverse-skill)

Covers anti-debug, anti-VM, anti-DBI, and integrity checks at the native binary level (ELF/PE). Applicable when reversing compiled targets, not JS.

### Linux Anti-Debug

#### ptrace-Based Detection

```c
if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) exit(1); // debugger present
```

**Bypasses:**
- `LD_PRELOAD=./hook.so ./binary` (hook ptrace to return 0)
- Patch binary with pwntools: `elf.asm(elf.symbols.ptrace, 'xor eax, eax; ret')`
- GDB: `catch syscall ptrace` → `set $rax = 0` → `continue`
- Kernel config: `echo 0 > /proc/sys/kernel/yama/ptrace_scope`

**Double-ptrace pattern:** Fork child `ptrace(ATTACH)` to parent → blocks other debuggers. Bypass: kill the watchdog child.

#### `/proc` Filesystem Checks

- `TracerPid` in `/proc/self/status` (non-zero → debugger)
- `readlink("/proc/self/exe")` – some debuggers alter the link
- Grep `/proc/self/maps` for `frida` / `gadget`

**Bypasses:**
- `LD_PRELOAD` hook `fopen`/`fread` to fake contents
- Mount namespace: `unshare -m bash -c 'mount --bind /dev/null /proc/self/status && ./binary'`
- GDB: set break at `fopen`, change filename argument to `"/dev/null"`

#### Timing-Based Detection

```c
uint64_t delta = __rdtsc() - start; // too slow → debugger
```

**Bypasses:**
- Frida hook on `clock_gettime`
- GDB: NOP `rdtsc` instructions
- Pin tool to fix TSC reads
- `LD_PRELOAD` with `faketime`

#### Signal-Based Anti-Debug

- `SIGTRAP` handler + `int3` – if debugger catches `int3`, handler never runs
- `SIGALRM` alarm as timeout
- `SIGSEGV` handler that executes real code (deliberate null-pointer deref)

**Bypass (GDB):** `handle SIGTRAP nostop pass`, `handle SIGALRM ignore`, `handle SIGSEGV nostop pass`

#### Syscall-Level Evasion

Direct syscall (e.g. ptrace syscall 101 on x86_64) bypasses `LD_PRELOAD`.
Bypass: patch binary or use GDB `catch syscall 101` → set `$rax = 0`.

---

### Windows Anti-Debug

#### PEB Checks

```c
bool debugged = NtCurrentPeb()->BeingDebugged;
DWORD flags = *(DWORD*)((BYTE*)NtCurrentPeb() + 0xBC); // 64-bit NtGlobalFlag
if (flags & 0x70) exit(1);
```

**Bypass:** ScyllaHide plugin auto-patches PEB; manual: zero BeingDebugged and NtGlobalFlag.

#### NtQueryInformationProcess

Checks `ProcessDebugPort` (0x7), `ProcessDebugObjectHandle` (0x1E), `ProcessDebugFlags` (0x1F).
Bypass: hook function or use ScyllaHide.

#### Heap Flags

`GetProcessHeap()` – under debugger, `Flags` and `ForceFlags` differ from expected (0x2 and 0).
Bypass: ScyllaHide.

#### TLS Callbacks

Execute **before** `main()`. Registered in PE TLS directory → `AddressOfCallBacks`.
Detection in IDA/Ghidra: check TLS directory.
Bypass: break on TLS in x64dbg (Options→Events→TLS Callbacks), or patch directory.

#### Hardware Breakpoint Detection

```c
GetThreadContext(GetCurrentThread(), &ctx);
if (ctx.Dr0 || ctx.Dr1 || ctx.Dr2 || ctx.Dr3) exit(1);
```

Bypass: use software breakpoints, or hook `GetThreadContext`.

#### Software Breakpoint Detection (INT3 scan)

CRC/hash over code section; if any byte == 0xCC, exit.
Bypass: use hardware breakpoints (DR0-DR3).

#### Exception-Based

- `SetUnhandledExceptionFilter` + `RaiseException` – if filter runs → no debugger
- `INT 2D` – debugger silently consumes exception, program continues → debugger present

#### Thread Hiding (NtSetInformationThread)

```c
NtSIT(GetCurrentThread(), 0x11 /*ThreadHideFromDebugger*/, NULL, 0);
```
Bypass: hook `NtSetInformationThread` to ignore class 0x11.

---

### Anti-VM / Anti-Sandbox

| Check | Mechanism | Bypass |
|---|---|---|
| CPUID bit 31 of ECX | Hypervisor present | Patch cpuid results; `cpuid.rcx=0` in QEMU |
| MAC prefix | VMware `00:0C:29`, VirtualBox `08:00:27`, Hyper-V `00:15:5D` | Change MAC in VM settings |
| Timing: `rdtsc` around `cpuid` | VM exit is slow → large delta | Patch rdtsc return values |
| Artifact files | Specific registry keys, processes, `/sys/class/dmi/id/product_name` | Run on bare metal or well-configured VM |
| Resource checks | CPU < 2, RAM < 2GB, disk < 60GB → exit | Configure VM with 4+ CPUs, 8GB+ RAM |

---

### Anti-DBI (Dynamic Binary Instrumentation)

#### Frida Detection

- Scan `/proc/self/maps` for `frida`/`gadget` strings
- Try connect to port 27042 (Frida default)
- Check first bytes of libc functions for JMP hooks (`0xE9` or `0xFF`)
- Scan `/proc/self/task/*/comm` for `gmain`, `gdbus`, `frida-*`
- Windows: detect named pipes `\\.\pipe\frida-*`

**Frida bypass:** hook detection functions (e.g. `strstr` to hide "frida" string); use early-load gadget.

#### Pin / DynamoRIO Detection

Check `/proc/self/maps` for `pin-`, `dynamorio`, etc., or instruction count timing.

---

### Code Integrity / Self-Hashing

- CRC32/MD5/SHA256 over `.text` section or function bodies – exit if modified
- Continuous integrity thread (watchdog) that re-hashes in loop

**Bypasses:**
- Hardware breakpoints (no code modification)
- Patch the comparison to always succeed
- Hook the hash function
- Emulate with Unicorn/Qiling
- Snapshot & restore memory
- Kill watchdog thread or patch its sleep

---

### Anti-Disassembly

| Technique | How It Works | Bypass |
|---|---|---|
| Jump with same target | `jz label; jnz label` – IDA linear sweep fails | Use recursive descent (Ghidra default) |
| Illegal bytes in instruction stream | `0xE8` (CALL) followed by junk after real target | Follow call target; fix bytes after |
| Opaque predicates | Condition that always evaluates same way but confuses analysis | Z3/angr to determine constant condition |
| Call + pop for anti-lifting | `call $+5; pop reg` – confuses IL lifting | Recognize pattern; skip during lift |

---

### pwntools Binary Patching

```python
from pwn import *

# Patch ptrace to return immediately
elf = ELF('./challenge', checksec=False)
elf.asm(elf.symbols.ptrace, 'ret')
elf.save('patched')

# Other useful patches:
# elf.asm(addr, 'xor eax, eax; ret')   # return 0
# elf.asm(addr, 'mov eax, 1; ret')      # return 1
# elf.asm(addr, 'nop')                  # NOP out a check
```

### LD_PRELOAD Hook

```c
// hook.c — intercept ptrace and return 0
long int ptrace(enum __ptrace_request req, ...) {
    long int (*orig)(enum __ptrace_request, pid_t, void *, void *);
    orig = dlsym(RTLD_NEXT, "ptrace");
    return 0;  // always succeed
}
```

```bash
gcc -shared -fPIC -ldl hook.c -o hook.so
LD_PRELOAD=./hook.so ./binary
```

---

### Anti-Debug Bypass Decision Tree (Binary)

```
遇到反调试 → 按类型分类：
├── ptrace 检测
│   ├── LD_PRELOAD hook ptrace → return 0
│   ├── pwntools patch → ret / xor eax,eax; ret
│   └── GDB catch syscall → set $rax=0
│
├── /proc 检测 (TracerPid)
│   ├── LD_PRELOAD hook fopen → fake status file
│   ├── mount --bind /dev/null /proc/self/status
│   └── GDB 断点在 fopen，改文件名参数
│
├── 时间检测 (rdtsc / clock_gettime)
│   ├── Frida hook clock_gettime → return fixed {0,0}
│   ├── GDB NOP rdtsc 指令
│   └── LD_PRELOAD faketime
│
├── 信号检测 (SIGTRAP/SIGSEGV handler)
│   └── GDB handle SIGTRAP nostop pass
│
├── 代码完整性 (self-hash / CRC)
│   ├── 硬件断点（不修改代码）
│   ├── 修改比较条件
│   ├── Hook hash 函数
│   └── Kill watchdog 线程
│
├── Frida 检测
│   ├── Hook strstr 过滤 "frida"
│   ├── 使用早加载 gadget
│   └── r2frida 替代
│
└── Windows 专用
    ├── PEB BeingDebugged → ScyllaHide / 手动清零
    ├── TLS Callback → x64dbg 事件中断
    ├── 硬件断点检测 → 只用软件断点
    └── INT3 扫描 → 用硬件断点
```

（从 0xsdeo/Hook_JS 吸收）

### 三合一 bypass 核心代码（推荐方式）

同时 Hook eval、new Function、constructor 三种 debugger 注入方式，并修复 toString 防止检测：

```javascript
(function() {
    'use strict';

    let temp_eval = eval;
    let temp_toString = Function.prototype.toString;

    // 修复 toString 防止检测
    Function.prototype.toString = function () {
        if (this === eval) return 'function eval() { [native code] }';
        if (this === Function) return 'function Function() { [native code] }';
        if (this === Function.prototype.toString) return 'function toString() { [native code] }';
        if (this === Function.prototype.constructor) return 'function Function() { [native code] }';
        return temp_toString.apply(this, arguments);
    }

    // 1. Bypass eval → debugger
    window.eval = function () {
        if (typeof arguments[0] == "string") {
            arguments[0] = arguments[0].replaceAll(/debugger/g, '');
        }
        return temp_eval(...arguments);
    }

    // 2. Bypass new Function → debugger
    let Bypass_debugger = Function;
    Function = function () {
        for (let i = 0; i < arguments.length; i++) {
            if (typeof arguments[i] == "string") {
                arguments[i] = arguments[i].replaceAll(/debugger/g, '');
            }
        }
        return Bypass_debugger(...arguments);
    }
    Function.prototype = Bypass_debugger.prototype;

    // 3. Bypass constructor → debugger
    Function.prototype.constructor = function () {
        for (let i = 0; i < arguments.length; i++) {
            if (typeof arguments[i] == "string") {
                arguments[i] = arguments[i].replaceAll(/debugger/g, '');
            }
        }
        return Bypass_debugger(...arguments);
    }
    Function.prototype.constructor.prototype = Function.prototype;
})();
```

**注意事项：**
- 必须 `document-start` 运行时期注入
- 如仍触发 debugger → 检查其他插件是否重写 Function
- 无法 bypass 的情况：`setInterval` 直接调函数引用而非字符串注入（此时需要 Hook setInterval）

### 永不断点模式深层分析

jsjiami 文章展示的高级 debugger 注入模式——**多层 Function 嵌套**，专门绕过单层 Hook：

```javascript
// 多层嵌套 —— 绕过单层 Function Hook
(function (a) {
    return (function (a) {
        return (Function('Function(arguments[0] + "' + a + '")()'))(a);
    })(a);
})('bugger')('de', 0, 0, (0, 0));
```

执行过程解析：
1. 外层自执行函数接收 `'bugger'`
2. 内层拼接 `'de' + 'bugger'` = `'debugger'`
3. 通过 `Function()` 构造字符串 `'Function("debugger")()'`
4. 再次通过 `Function()` 执行 `'debugger'`

**关键洞察**：JS 的 `Function` 构造器是最底层的反调试载体。任何层级的 `Function('debugger')` 都能执行，**除非 Function 本身被 Hook**。

**这就是为什么三合一方案（Hook Function + eval + constructor）是必须的——只 Hook eval 不够，因为多层嵌套可以绕过 eval 直接走 Function。**

### Bypass 决策树

```
遇到 debugger → 判断注入方式：
├── eval('debugger')         → Hook eval（三合一方䅂自动覆盖）
├── new Function('debugger') → Hook Function
├── constructor('debugger')  → Hook constructor
├── setInterval(fn, 3000)    → Hook setInterval 或 CDP 层跳过
├── Object.defineProperty    → Entity 层预 Hook getter/setter
├── iframe debugger          → 拦截 iframe 创建
├── Worker debugger          → 拦截 Worker
├── try-catch 异常触发        → Hook 异常处理
└── Date/performance 差值检测 → 覆盖 Date.now / performance.now
```

### 脱机脚本路径

所有 bypass 脚本已 clone 到 `/opt/hook-js/hook_debugger/`：
- `Bypass_Debugger/Bypass_Debugger.js` — 三合一方案（推荐）
- `Bypass_Debugger/Bypass_Debugger(备用).js` — 备用版本
- `Hook_eval/Hook_eval.js` — 仅 eval bypass
- `Hook_Function/Hook_Function.js` — 仅 Function bypass

---

## Anti-Tamper（抗格式化自毁）绕过

jsjiami.com V6/V7 的防格式化机制：代码格式化后通过 `toString` 校验代码完整性，不匹配则触发自毁（`while(1){debugger}` 卡死）。

### 检测原理

```javascript
// 简化示例：检测函数体是否被格式化
function check() {
    // 原始代码格式特定
    var a=1;
    var b=2;
}
// 格式化后变成：
function check() {
    var a = 1;
    var b = 2;
}
// toString 结果不同，触发自毁
```

### 绕过策略

**策略1：运行时保留原始函数引用**
```javascript
// 在代码执行前，先保存所有原始函数的 toString
var originalToString = Function.prototype.toString;
// 注入前保存函数体的原始文本快照
```

**策略2：Hook toString 返回原始值**
```javascript
// 如果知道检测了哪些函数的 toString，直接 Hook 返回格式化前的字符串
var originalFunc = targetFunction;
targetFunction.toString = function() {
    return 'function targetFunction() {\n  var a=1;\n  var b=2;\n}';
};
```

**策略3：源码级 Patch**（推荐）
直接在 AST 层面识别并删除 tamper 检测代码。检测模式的 AST 特征：
- `if` 条件中包含 `.toString()` 调用
- 条件比较结果是字符串长度或正则匹配
- `if` 的 true 分支是无限循环 + debugger

---

## Anti-Selenium 绕过

jsjiami 可通过 VIP 配置禁止 Selenium 模拟。检测点包括：

| 检测点 | 绕过方法 |
|--------|---------|
| `navigator.webdriver` | 设为 false/undefined（Playwright 默认修复） |
| `navigator.plugins` 长度 | 确保有正常数量的插件 |
| `navigator.languages` | 设为正常值如 `['zh-CN', 'zh']` |
| `chrome.runtime` | Selenium 无此对象 |
| `window.outerHeight` 偏差 | 确保与实际窗口一致 |
| 行为检测（鼠标轨迹/滚动） | Playwright 的 stealth 模式 |

使用 Puppeteer Extra + Stealth 插件可绕过大部分检测：

```javascript
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
```

---

## 实战提炼：逆向过程中的反调试对抗通用模式

### 从 chatgpt2api 和 ONE App 中提炼

### 对抗类型矩阵

| 对抗类型 | 常见实现 | 绕过方法 | 实战案例 |
|---------|---------|---------|---------|
| WAF/CDN 拦截 | SudunWAF / Cloudflare / Xcdn | 换节点/用代理/模拟浏览器指纹 | chatgpt2api 的 Xcdn / ONE App 的 SudunWAF |
| 签名验证 | 服务端校验请求 sign | 逆向签名算法后复现 | ONE App 的 MD5+MD5+salt 签名 |
| Token 绑定 | JWT 绑定 IP/device | 同一 IP 调用 / 模拟设备指纹 | ONE App 的 JWT IP 绑定 (±600s) |
| 请求频率限制 | Rate limiting + 429 | Token 池轮询 + 延时 | chatgpt2api 的账号轮询 |
| 返回加密 | 全部 API 响应 AES 加密 | 逆向 AES Key/IV | ONE App 的 AES-128-CBC 响应加密 |
| 图片加密 | CDN 返回加密的 JPEG | 逆向图片加解密 Key | ONE App 的 CDN AES 加密图片 |
| 代码混淆 | Flutter obfuscation / JS 混淆 | 搜字符串常量跳过混淆层 | ONE App 的 main.dart.js 混淆 |
| 反自动化工 | PoW / Turnstile / CAPTCHA | 第三方 solver / 浏览器自动化 | chatgpt2api 的 sentinel PoW |

### 实战绕过模式

```
遇到反调试 → 按类型分类：
├── WAF/CDN 拦截
│   └── 用 curl_cffi / Playwright 伪造完整浏览器指纹
│
├── 签名验证
│   └── 反编译找 Key/IV/Salt → Python 复现签名算法
│
├── Token 验证
│   ├── 有 bootstrap 无 Token 端点？→ 直接拿 JWT
│   ├── 无？→ HAR 抓取已有的 Token
│   └── 都没有？→ 账号密码登录自动获取
│
├── 加密响应
│   ├── 反编译找 Key/IV → 解密每一步 API 响应
│   └── 如果响应是 Salted__ 开头 → OpenSSL salted 格式 → 试密码
│
├── 加密图片
│   ├── 图片熵值 ~8.0 → 加密 → 找独立 CDN 域名
│   └── Flutter Web 版 JS 中可找到图片解密 Key
│
├── 请求限制
│   ├── 单账号超限 → 多账号轮询（token 池）
│   └── IP 限制 → 代理池 / 更换节点
│
└── 反自动化
    └── 如果太复杂 → 用 Chromium CDP 手工模拟
```
