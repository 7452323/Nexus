---
name: binary-analysis
category: reverse-engineering
description: >-
  Merged skill combining: ida-reverse-analysis, so-native-analysis, binary-diffing, symbolic-execution-tools.
version: "1.0"
sources:
  - ida-reverse-analysis
  - so-native-analysis
  - binary-diffing
  - symbolic-execution-tools
tags: [reverse-engineering, merged]
---

# binary-analysis

> **Merged from**: ida-reverse-analysis, so-native-analysis, binary-diffing, symbolic-execution-tools
> **Source count**: 4

---

## Table of Contents

1. [ida-reverse-analysis](#ida-reverse-analysis)
2. [so-native-analysis](#so-native-analysis)
3. [binary-diffing](#binary-diffing)
4. [symbolic-execution-tools](#symbolic-execution-tools)

---

## ida-reverse-analysis

# IDA Reverse Analysis & GhidraMCP — 二进制逆向分析

## AI 驱动逆向：GhidraMCP（新！）

### GhidraMCP 是什么

[LaurieWired/GhidraMCP](https://github.com/LaurieWired/GhidraMCP) 是一个 MCP 协议服务器，将 Ghidra 的反编译/分析/重命名等核心功能暴露为 MCP 工具，让 LLM 能自主操作 Ghidra 进行逆向分析。

### 架构
```
Hermes Agent → MCP Client → GhidraMCP Server → Ghidra Plugin → Ghidra API → 二进制
```

### 安装与配置

```bash
# 1. 安装 Ghidra（需要 Java 17+）
# 下载: https://ghidra-sre.org/

# 2. 安装 GhidraMCP 插件
# 复制 GhidraMCP.py 到 Ghidra 的 Extensions 目录

# 3. 启动 Ghidra 并加载二进制
# 4. GhidraMCP 监听端口（默认 8192）
# 5. Hermes 配置 MCP server

# 或者用 Alt: bethington/ghidra-mcp（245 个工具）
```

### 可用 MCP 工具

| 工具名 | 功能 |
|--------|------|
| `decompile_function` | 反编译指定函数为伪代码 |
| `rename_function` | 重命名函数，改善可读性 |
| `rename_data` | 重命名数据/变量 |
| `list_functions` | 列出所有函数 |
| `list_classes` | 列出所有类 |
| `analyze_binary` | 全自动分析二进制 |
| `search_strings` | 搜索字符串 |
| `get_function_graph` | 获取函数调用图 |

### 典型 AI 逆向工作流

```
1. 加载二进制到 Ghidra，运行初始分析
2. GhidraMCP: list_functions → 发现可疑函数
3. GhidraMCP: decompile_function → 获取伪代码
4. Hermes/LLM 分析伪代码 → 理解逻辑
5. GhidraMCP: rename_function → 更新命名
6. 重复 3-5 直到完全理解
```

## IDAPython 实用脚本

```python
# 列出所有函数
for ea in Functions():
    name = GetFunctionName(ea)
    print(f"0x{ea:x}: {name}")

# 获取函数伪代码
import ida_hexrays
if ida_hexrays.init_hexrays_plugin():
    cfunc = ida_hexrays.decompile(ea)
    print(str(cfunc))

# 搜索指定字节模式
pattern = "55 8B EC 83 EC ? ?"
results = ida_search.find_binary(ea, BADADDR, pattern, 16, SEARCH_DOWN)
```

## 加密算法识别

| 特征 | 算法 | 确认方法 |
|------|------|----------|
| 64x64常数表 | AES | 找 S-box 常量 |
| 64x64 盒 + 0x9E3779B9 | TEA/XTEA | delta 常量 |
| 0x6C078965 | MT19937 | 种子初始化 |
| 0x67452301+0xEFCDAB89 | MD5/SHA-1 | 初始 IV |
| 大整数运算+0x10001 | RSA | 公钥指数 |

## DLL 分析流程

1. 加载 DLL 到 IDA
2. 识别导出函数（View → Exports）
3. 分析每个导出函数的调用链
4. 标记系统/第三方 API 调用
5. 提取关键字符串和加密常量

## 外部工具仓库（NEW）

| 仓库 | 用途 | 链接 |
|------|------|------|
| **LaurieWired/GhidraMCP** | Ghidra MCP 服务器，LLM 自主逆向 | https://github.com/LaurieWired/GhidraMCP |
| **bethington/ghidra-mcp** | 245 个 MCP 工具，P-code 模拟 | https://github.com/bethington/ghidra-mcp |
| **qilingframework/qiling** | 可插桩二进制仿真框架（跨平台/跨架构） | https://github.com/qilingframework/qiling |
| **unicorn-engine/unicorn** | CPU 模拟器 | https://github.com/unicorn-engine/unicorn |
| **y9nhjy/RE_Tools** | 全网逆向工具全集 | https://github.com/y9nhjy/RE_Tools |
| **tylerha97/awesome-reversing** | 精选逆向资源列表 | https://github.com/tylerha97/awesome-reversing |

---

## so-native-analysis

# SO Analyzer MCP

Native库（SO文件）分析工具，支持Flutter应用抓包。**免费开源的IDA Pro替代品！**

## 🎯 特色功能

- ✅ **反编译** - 支持radare2/Ghidra/轻量级模式
- ✅ **函数识别** - 识别所有函数（包括未导出）
- ✅ **调用图分析** - 生成DOT格式可视化
- ✅ **控制流图** - 基本块分析
- ✅ **Flutter SSL绕过** - 一键完成
- ✅ **字符串加密检测** - 熵值分析+XOR检测

## 📊 工具总览 (30个)

### SO基础分析 (8个)

| 工具 | 说明 |
|------|------|
| `so_check_env` | 检查分析环境 |
| `so_list_libs` | 列出APK中的所有SO库 |
| `so_extract` | 从APK提取SO文件 |
| `so_info` | 获取SO基本信息 |
| `so_exports` | 获取导出函数列表 |
| `so_imports` | 获取导入函数列表 |
| `so_strings` | 提取字符串 |
| `so_search_symbol` | 搜索符号 |

### Flutter专用 (6个)

| 工具 | 说明 |
|------|------|
| `flutter_detect` | 检测是否是Flutter应用 |
| `flutter_get_version` | 获取Flutter版本 |
| `flutter_find_ssl` | 查找SSL验证函数 |
| `flutter_ssl_offset_v2` | ⭐智能定位SSL函数 |
| `flutter_patch_ssl` | Patch SSL验证（绕过证书） |
| `flutter_patch_apk` | **一键patch Flutter APK** |

### 二进制修改 (5个)

| 工具 | 说明 |
|------|------|
| `so_patch_bytes` | 修改指定偏移的字节 |
| `so_search_bytes` | 搜索字节模式 |
| `so_replace_bytes` | 查找并替换字节 |
| `so_disassemble` | 反汇编代码 |
| `so_get_function_bytes` | 获取函数字节码 |

### 交叉引用分析 (4个)

| 工具 | 说明 |
|------|------|
| `so_xref_string` | ⭐查找字符串交叉引用 |
| `so_find_function` | 根据地址查找函数 |
| `so_analyze_function` | 分析函数特征 |
| `so_get_sections` | 获取代码段信息 |

### ⭐ 高级分析 (9个) - NEW!

| 工具 | 说明 |
|------|------|
| `so_list_all_functions` | 识别所有函数（包括未导出） |
| `so_callgraph` | 生成调用关系图 + DOT图 |
| `so_get_cfg` | 生成控制流图 + DOT图 |
| `so_analyze_function_advanced` | 全面函数分析 |
| `so_decompile` | ⭐反编译生成伪代码 |
| `so_detect_encryption` | 字符串加密检测 |
| `so_trace_register` | 数据流/寄存器追踪 |
| `so_check_radare2` | 检查radare2环境 |
| `so_check_ghidra` | 检查Ghidra环境 |

## 安装

```bash
cd so-analyzer-mcp
pip install -r requirements.txt
```

## MCP配置

```json
{
  "mcpServers": {
    "so-analyzer": {
      "command": "python",
      "args": ["K:/path/to/so-analyzer-mcp/run_server.py"]
    }
  }
}
```

## 使用示例

```python
# 1. 列出SO库
so_list_libs(apk_path="app.apk")

# 2. 检测Flutter
flutter_detect(apk_path="app.apk")

# 3. 提取SO文件
so_extract(apk_path="app.apk", lib_name="libflutter.so", arch="arm64-v8a")

# 4. 搜索SSL相关函数
so_search_symbol(so_path="libflutter.so", pattern="ssl")

# 5. 提取字符串
so_strings(so_path="libflutter.so", search="certificate")
```

## 项目结构

```
so-analyzer-mcp/
├── so_analyzer/
│   ├── __init__.py
│   ├── config.py           # 配置
│   ├── server.py           # MCP服务器 (30个工具)
│   ├── so_utils.py         # SO基础分析
│   ├── flutter_utils.py    # Flutter专用工具
│   ├── flutter_utils_v2.py # Flutter SSL智能定位
│   ├── patch_utils.py      # 二进制修改
│   ├── xref_utils.py       # 交叉引用分析
│   ├── advanced_utils.py   # 高级分析 (NEW!)
│   └── decompile_utils.py  # 反编译工具 (NEW!)
├── radare2/               # radare2 (可选)
├── run_server.py          # 启动脚本
├── requirements.txt
└── README.md
```

## 依赖

**必需**:
- **mcp** - MCP协议库
- **lief** - 二进制文件解析库
- **capstone** - 反汇编引擎

**可选**:
- **radare2** - 反编译 (推荐，~50MB)
- **Ghidra** - 高质量反编译 (~400MB)

## 已完成功能 ✅

- [x] Flutter SSL Patch (一键绕过)
- [x] SO文件修改
- [x] 反编译 (radare2/Ghidra/简单模式)
- [x] 函数识别 (包括未导出)
- [x] 调用图分析
- [x] 控制流图
- [x] 字符串加密检测
- [x] 数据流分析

## 与 IDA Pro MCP 对比

| 功能 | IDA Pro MCP | SO Analyzer MCP |
|------|-------------|-----------------|
| 反编译 | ✅ Hex-Rays | ✅ radare2 |
| 函数识别 | ✅ | ✅ |
| 调用图 | ✅ | ✅ |
| 控制流图 | ✅ | ✅ |
| Flutter SSL | ❌ | ✅ 一键完成 |
| APK操作 | ❌ | ✅ |
| 价格 | $1000+ | **免费** |

---

## binary-diffing

# Binary Diffing — 二进制对比分析

## 工具选择

| 工具 | 优点 | 缺点 | 适用 |
|------|------|------|------|
| Diaphora | 免费、支持多架构 | 较慢 | 日常二进制对比 |
| BinDiff | 快速、准确 | 商业 | 安全补丁分析 |
| TurboDiff | IDA 插件 | 商业 | IDA 用户 |

## 分析流程

1. 获取 patched 和 unpatched 版本
2. 在 IDA 中分别分析两个版本
3. 生成数据库对比
4. 识别差异函数
5. 分析修改内容
6. 判定是否为安全补丁

## 补丁分析类型

| 类型 | 特征 | 意义 |
|------|------|------|
| 新增校验 | 添加 if/边界检查 | 安全补丁 |
| 修改算法 | 加密/解密逻辑变更 | 功能性补丁 |
| 删除代码 | 移除功能 | 功能性补丁 |
| 数值修改 | 常量/偏移变更 | 参数调整 |

---

## symbolic-execution-tools

# SKILL: Symbolic Execution Tools — Expert Analysis Playbook

> **AI LOAD INSTRUCTION**: Expert symbolic execution techniques using angr, Z3, and Unicorn Engine. Covers CTF challenge automation, constraint solving patterns, function hooking, SimProcedure replacement, and emulation-based unpacking. Base models often produce broken angr scripts due to incorrect state initialization or missing hooks for libc functions.

## 0. RELATED ROUTING

- [anti-debugging-techniques](related-skill: anti-debugging-techniques) when anti-debug checks need to be symbolically bypassed
- [code-obfuscation-deobfuscation](related-skill: code-obfuscation-deobfuscation) when using symbolic execution for deobfuscation
- [vm-and-bytecode-reverse](related-skill: vm-and-bytecode-reverse) when applying angr to custom VM challenges

### Advanced Reference

Also load [ANGR_COOKBOOK.md](references/ANGR_COOKBOOK.md) when you need:
- 15+ ready-to-use angr script patterns for common CTF challenges
- Hook templates for scanf, printf, malloc, strcmp
- Symbolic file input, stdin, argv patterns
- Optimization tricks for path explosion management

### When to use which tool

| Scenario | Best Tool | Why |
|---|---|---|
| Pure math / equation system | Z3 | Direct constraint solving, no binary needed |
| Binary with control flow | angr | Explores paths, manages constraints automatically |
| Emulate specific code region | Unicorn | Fast, no symbolic overhead, good for unpacking |
| Complex binary + custom VM | angr + Unicorn (combo) | angr for control flow, Unicorn for VM handlers |
| Kernel / firmware code | Qiling | Full system emulation with OS awareness |

---

## 1. ANGR — CORE CONCEPTS

### 1.1 Pipeline

```
Project(binary)
  → Factory.entry_state() / blank_state(addr=)
    → SimulationManager(state)
      → explore(find=target, avoid=bad)
        → found[0].solver.eval(symbolic_var)
```

### 1.2 Essential Setup

```python
import angr
import claripy

proj = angr.Project('./challenge', auto_load_libs=False)

# Entry state: start from program entry point
state = proj.factory.entry_state()

# Blank state: start from arbitrary address
state = proj.factory.blank_state(addr=0x401000)

# Full init state: with command-line args
state = proj.factory.full_init_state(args=['./challenge', arg1_sym])

simgr = proj.factory.simulation_manager(state)
simgr.explore(find=0x401234, avoid=[0x401300])

if simgr.found:
    found = simgr.found[0]
    solution = found.solver.eval(symbolic_input, cast_to=bytes)
    print(f"Solution: {solution}")
```

### 1.3 Symbolic Variables (claripy)

```python
# Bitvector (fixed-size integer)
sym_input = claripy.BVS("input", 64)        # 64-bit symbolic
sym_byte = claripy.BVS("byte", 8)           # 8-bit symbolic
sym_buf = claripy.BVS("buffer", 8 * 32)     # 32-byte buffer

# Concrete bitvector
concrete = claripy.BVV(0x41, 8)             # concrete value 0x41

# Constraints
state.solver.add(sym_input > 0)
state.solver.add(sym_input < 100)
state.solver.add(sym_byte >= 0x20)           # printable ASCII
state.solver.add(sym_byte <= 0x7e)

# Evaluate
value = state.solver.eval(sym_input)
all_values = state.solver.eval_upto(sym_input, 10)  # up to 10 solutions
```

### 1.4 Symbolic stdin

```python
flag_len = 32
sym_stdin = claripy.BVS("stdin", 8 * flag_len)

state = proj.factory.entry_state(stdin=sym_stdin)

# Constrain to printable ASCII
for i in range(flag_len):
    byte = sym_stdin.get_byte(i)
    state.solver.add(byte >= 0x20)
    state.solver.add(byte <= 0x7e)
```

### 1.5 Hooking Functions

```python
# Hook by address (skip N bytes of original code)
@proj.hook(0x401100, length=5)
def skip_check(state):
    state.regs.eax = 1  # force success

# SimProcedure: replace library function
class MyStrcmp(angr.SimProcedure):
    def run(self, s1, s2):
        return claripy.If(
            self.state.memory.load(s1, 32) == self.state.memory.load(s2, 32),
            claripy.BVV(0, 32),
            claripy.BVV(1, 32)
        )

proj.hook_symbol('strcmp', MyStrcmp())

# Hook common problematic functions
proj.hook_symbol('printf', angr.SIM_PROCEDURES['libc']['printf']())
proj.hook_symbol('scanf', angr.SIM_PROCEDURES['libc']['scanf']())
proj.hook_symbol('puts', angr.SIM_PROCEDURES['libc']['puts']())
```

### 1.6 Memory Operations

```python
# Read memory (symbolic-aware)
data = state.memory.load(addr, size)          # returns BV
data_concrete = state.solver.eval(data, cast_to=bytes)

# Write memory
state.memory.store(addr, claripy.BVV(0x41, 8))
state.memory.store(addr, sym_buf)

# Read/write registers
rax = state.regs.rax
state.regs.rdi = claripy.BVV(0x1000, 64)
```

---

## 2. Z3 CONSTRAINT SOLVING

### 2.1 Core API

```python
from z3 import *

# Sorts
x = BitVec('x', 32)    # 32-bit bitvector
y = Int('y')             # arbitrary precision integer
b = Bool('b')            # boolean

# Solver
s = Solver()
s.add(x + y == 42)
s.add(x > 0)
s.add(y > 0)

if s.check() == sat:
    m = s.model()
    print(f"x = {m[x]}, y = {m[y]}")
```

### 2.2 Common CTF Patterns

```python
# Serial key validation: each char satisfies constraints
key = [BitVec(f'k{i}', 8) for i in range(16)]
s = Solver()
for k in key:
    s.add(k >= 0x30, k <= 0x7a)  # alphanumeric-ish

# XOR key recovery
plaintext = b"known_plaintext"
ciphertext = b"\x12\x34..."
key_byte = BitVec('key', 8)
s = Solver()
for p, c in zip(plaintext, ciphertext):
    s.add(p ^ key_byte == c)

# System of linear equations (modular)
a, b, c = BitVecs('a b c', 32)
s = Solver()
s.add(3*a + 5*b + 7*c == 0x12345678)
s.add(2*a + 4*b + 6*c == 0xDEADBEEF)
s.add(a ^ b ^ c == 0xCAFEBABE)
```

### 2.3 Optimization

```python
from z3 import Optimize

opt = Optimize()
x = BitVec('x', 32)
opt.add(x > 0)
opt.add(x < 1000)
opt.minimize(x)  # find smallest satisfying value
opt.check()
print(opt.model())
```

---

## 3. UNICORN ENGINE — CODE EMULATION

### 3.1 Basic Setup

```python
from unicorn import *
from unicorn.x86_const import *
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

mu = Uc(UC_ARCH_X86, UC_MODE_64)

CODE_ADDR = 0x400000
STACK_ADDR = 0x7fff0000
STACK_SIZE = 0x10000

mu.mem_map(CODE_ADDR, 0x10000)
mu.mem_map(STACK_ADDR, STACK_SIZE)

mu.mem_write(CODE_ADDR, code_bytes)
mu.reg_write(UC_X86_REG_RSP, STACK_ADDR + STACK_SIZE - 0x1000)
mu.reg_write(UC_X86_REG_RBP, STACK_ADDR + STACK_SIZE - 0x1000)

mu.emu_start(CODE_ADDR, CODE_ADDR + len(code_bytes))

result = mu.reg_read(UC_X86_REG_RAX)
```

### 3.2 Hooking Memory & Instructions

```python
# Hook memory access
def hook_mem(uc, access, address, size, value, user_data):
    if access == UC_MEM_WRITE:
        print(f"Write {value:#x} to {address:#x}")
    elif access == UC_MEM_READ:
        print(f"Read from {address:#x}")

mu.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, hook_mem)

# Hook specific instruction (for tracing)
def hook_code(uc, address, size, user_data):
    code = uc.mem_read(address, size)
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    for insn in md.disasm(bytes(code), address):
        print(f"  {insn.address:#x}: {insn.mnemonic} {insn.op_str}")

mu.hook_add(UC_HOOK_CODE, hook_code)
```

### 3.3 Use Cases

| Use Case | Approach |
|---|---|
| Unpack shellcode | Map shellcode, emulate, dump decoded payload |
| Decrypt strings | Emulate decryption function with controlled inputs |
| Brute-force short keys | Loop emulation with different key inputs |
| Analyze obfuscated function | Emulate function, observe register/memory state |
| Firmware code emulation | Map firmware memory layout, emulate routines |

---

## 4. ANGR EXPLORATION STRATEGIES

### 4.1 find/avoid

```python
simgr.explore(
    find=lambda s: b"Correct" in s.posix.dumps(1),   # stdout contains "Correct"
    avoid=lambda s: b"Wrong" in s.posix.dumps(1)      # avoid "Wrong" output
)
```

### 4.2 Managing Path Explosion

| Strategy | Implementation |
|---|---|
| Constrain input space | Add constraints (printable, length limits) |
| Avoid dead-end paths | Use `avoid=` for known failure addresses |
| Hook complex functions | Replace with simplified SimProcedure |
| Limit loop iterations | `state.options.add(angr.options.LAZY_SOLVES)` |
| Use veritesting | `simgr.explore(..., technique=angr.exploration_techniques.Veritesting())` |
| DFS instead of BFS | `simgr.use_technique(angr.exploration_techniques.DFS())` |
| Timeout per path | `simgr.explore(..., num_find=1)` + timeout wrapper |

### 4.3 Concrete + Symbolic Hybrid

```python
state = proj.factory.entry_state(
    add_options={angr.options.UNICORN}  # use Unicorn for concrete regions
)
```

This dramatically speeds up execution: concrete code runs natively via Unicorn, switching to symbolic only when symbolic variables are involved.

---

## 5. PRACTICAL WORKFLOW

### 5.1 CTF Binary Solving Workflow

```
1. Static analysis: identify input method, success/fail conditions
   └─ Find "Correct" / "Wrong" strings → get their xref addresses

2. Choose tool:
   ├─ Pure math (no binary needed) → Z3
   ├─ Small binary, clear success/fail → angr explore
   └─ Specific function to emulate → Unicorn

3. Set up symbolic input:
   ├─ stdin → claripy.BVS + entry_state(stdin=)
   ├─ argv → full_init_state(args=[...])
   ├─ file input → SimFile
   └─ specific memory → state.memory.store(addr, sym)

4. Hook problematic functions:
   ├─ printf/puts → SimProcedure or no-op
   ├─ scanf → custom handler
   ├─ time/random → return concrete value
   └─ anti-debug → skip entirely

5. Explore and extract:
   └─ simgr.explore(find=, avoid=) → solver.eval()
```

---

## 6. DECISION TREE

```
Need to solve a reversing challenge?
│
├─ Is the challenge pure math / equations?
│  └─ Yes → Z3
│     ├─ Linear equations → BitVec + Solver
│     ├─ Modular arithmetic → BitVec (natural mod 2^n)
│     ├─ Boolean logic → Bool + Solver
│     └─ Optimization → Optimize + minimize/maximize
│
├─ Is it a compiled binary with clear success/fail?
│  └─ Yes → angr
│     ├─ Input via stdin → symbolic stdin
│     ├─ Input via argv → full_init_state with symbolic args
│     ├─ Input via file → SimFile
│     ├─ Path explosion → add constraints, avoid paths, hook loops
│     └─ Complex library calls → hook with SimProcedure
│
├─ Need to emulate a specific function/region?
│  └─ Yes → Unicorn Engine
│     ├─ Decryption routine → map code + data, emulate, read result
│     ├─ Shellcode analysis → map shellcode, hook syscalls
│     └─ Key schedule → emulate with different inputs
│
├─ Need to analyze firmware / exotic arch?
│  └─ Yes → Qiling (full system emulation with OS support)
│
├─ Binary has VM protection?
│  └─ angr for handler analysis + Z3 for bytecode constraints
│
└─ None of the above working?
   ├─ Combine: Unicorn for concrete regions + Z3 for constraints
   ├─ Manual reverse engineering with debugger
   └─ Side-channel approach (timing, power analysis for hardware)
```

---

## 7. COMMON PITFALLS & FIXES

| Problem | Cause | Fix |
|---|---|---|
| angr hangs forever | Path explosion in loops | Add `avoid=` for loop-back edges, or hook the loop |
| Z3 returns `unknown` | Non-linear constraints too complex | Simplify, split into sub-problems, use `set_param("timeout", 5000)` |
| Unicorn crashes on syscall | Syscall not handled | Hook syscall interrupt, handle or skip |
| angr wrong result | Incorrect state initialization | Verify initial memory layout matches actual binary |
| Symbolic memory too large | Unbounded symbolic reads | Concretize array indices where possible |
| SimProcedure wrong types | Argument type mismatch | Check calling convention (cdecl vs fastcall) |
| angr can't load binary | Missing libraries | Use `auto_load_libs=False` + hook needed symbols |

---

## 8. TOOL VERSIONS & INSTALLATION

```bash
# angr (Python 3.8+)
pip install angr

# Z3
pip install z3-solver

# Unicorn Engine
pip install unicorn

# Capstone (disassembly, pairs with Unicorn)
pip install capstone

# Keystone (assembly)
pip install keystone-engine
```

---
