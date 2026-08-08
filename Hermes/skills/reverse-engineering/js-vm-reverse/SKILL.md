---
name: js-vm-reverse
category: reverse-engineering
description: >-
  Merged skill combining: jsvmp-reverse, vm-and-bytecode-reverse.
version: "1.0"
sources:
  - jsvmp-reverse
  - vm-and-bytecode-reverse
tags: [reverse-engineering, merged]
---

# js-vm-reverse

> **Merged from**: jsvmp-reverse, vm-and-bytecode-reverse
> **Source count**: 2

---

## Table of Contents

1. [jsvmp-reverse](#jsvmp-reverse)
2. [vm-and-bytecode-reverse](#vm-and-bytecode-reverse)

---

## jsvmp-reverse

# JSVMP/VMP 虚拟机逆向 Skill

> 目标: 任何实例读完本文档，都能独立选择路线、应用技术、避坑，完成 JSVMP/VMP 保护代码的逆向还原。

---

## 技能分工

| 技能 | 职责 | 与本技能关系 |
|------|------|-------------|
| **jsvmp-reverse** (本技能) | VM 整体逆向方法论：路线选择、VM Hook 注入、数据驱动还原、AST 反编译 | 通用底层 |
| cdp-debug-reverse | Chrome DevTools Protocol 调试：VM 断点、内存观察、调用栈追踪 | 提供 VM 运行时调试能力 |
| ast-deobfuscation | AST 反混淆：VM dispatcher 外层控制流平坦化还原 | 为 AST 反编译路线提供干净输入 |
| find-crypto-entry | 加密入口定位：找到 VM 入口函数、加密调用链起点 | 定位 VM 内部关键执行节点 |
| algorithm-reverse | 算法还原：VM 层算法的纯算实现 | 还原 VM 内部的具体加密/签名算法 |
| ruishu-reverse | 瑞数纯算：本技能的垂直领域实例 | 本技能方法论的最佳实战验证 |

**协作模式**: find-crypto-entry 定位入口 → jsvmp-reverse 选择路线 → cdp-debug-reverse 运行时调试 → ast-deobfuscation 清洗代码 → algorithm-reverse 还原算法。

---

## 双路线方法论

### 路线一：数据驱动（推荐首选）

**适用条件**（满足任一即可）:
- VM 指令集不公开或过于复杂（如 740 个 state 的三层嵌套 VM）
- 有可重复执行环境（sdenv / 浏览器 / 补环境可跑）
- 输出格式相对固定（Cookie / Header / 固定长度字节流）
- 只需还原最终输出，不需要理解全部逻辑

**核心思想**: 不理解 VM 内部，只对比输出差异，从差异反推来源。

**步骤**:

```
1. 样本采集 (3-5 组)
   ├── 用可执行环境 (sdenv/浏览器) 跑目标 VM，采集完整输出
   ├── 同时采集所有可获取的中间数据 (keys, 时间戳, 输入参数)
   └── 确保每组样本在同一个 session 内配套 (变量名/密钥对应)

2. 逐字节对比
   ├── 固定位: 所有 session 相同 → 硬编码常量
   ├── keys 派生位: 匹配 keys[N] → 动态提取
   ├── 时间相关位: 有规律变化 → 找公式 (r2mkaTime + delta 等)
   ├── 随机位: 无规律 → Math.random / 随机字节
   └── 未知位: 需更多数据或更深分析

3. 来源追溯
   ├── 对每个变化字节，建立 "输入 → 输出" 的映射关系
   ├── 用 TLV 格式拆分输出，逐 type 分析 (见 data-driven-methodology.md)
   └── 多采集几组数据，验证假设

4. Python/JS 复现
   ├── 逐 type 实现 build 函数
   ├── 每实现一个 type，与参考数据逐字节对比验证
   └── 组装完整管线，端到端验证
```

**优势**: 不需要理解 VM 内部；可快速产出（1 天 vs 2 周手动分析）。

**真实案例**: 瑞数 basearr (154-166B TLV 结构) — 花 2 天读 VM 代码完全浪费，转向数据驱动后 1 天内解决所有问题。

### 路线二：AST 反编译

**适用条件**（满足任一即可）:
- 数据驱动无法覆盖（输出不可重复、字段无法对比）
- 需要理解完整逻辑（如后缀签名、协议解析）
- VM 结构相对标准（dispatcher switch-case、rt[] 函数注册表）
- 产出需要可维护（算法变更时可快速适配）

**核心思想**: eval 代码是合法 JS，用标准 AST 解析器完整解析，精确提取每个语义单元。

**步骤**:

```
1. acorn 解析 → AST
   ├── eval 代码虽高度混淆 (变量名洗牌、二叉搜索 if-else、多层嵌套)
   └── 但语法结构完整，AST 可精确提取每一个语义单元

2. rt[N] 映射表 (识别 dispatcher switch-case)
   ├── 找到 VM 解释器函数 (通常包含大量 if(varName === N) 分支)
   ├── 遍历 AST 中所有 BinaryExpression(===) 条件分支
   ├── 每个分支对应一个 opcode → 提取 opcode 表
   └── 建立 rt[] 函数注册映射 (Array.prototype.push.apply 位置)

3. 调用链追踪
   ├── 从入口函数追踪到最终输出的完整调用链
   ├── 通过常量搜索定位特定算法 (SHA-1: 0x67452301, CRC32: 0xEDB88320)
   └── 追踪数据流: 输入 → 处理 → 输出

4. 自动反汇编
   ├── 字节码 → 汇编指令 (opcode → 助记符)
   ├── 栈模拟 → 伪 JS 代码 (模拟 VM 栈操作)
   └── 手动语义标注 (常量表/字符串表反查 + 数据驱动验证)
```

**优势**: 完整理解，可处理复杂协议，产出可维护代码。AST 效率约为运行时追踪的 **80 倍**。

**详见**: [ast-decompiler-methodology.md](references/ast-decompiler-methodology.md)

### 路线选择决策树

```
VM 逆向需求
  → 输出是否可重复执行？
    → 是 → 数据驱动路线 (优先)
      → 数据驱动是否覆盖全部字段？
        → 是 → 完成
        → 否 → 局部补充 AST 反编译
    → 否 → AST 反编译路线
      → VM 结构是否标准？(dispatcher switch-case)
        → 是 → 自动反汇编 (四步管线)
        → 否 → 手动分析 + VM Hook 注入
```

---

## VM Hook 7 种注入技术

| # | 技术 | 注入点 | 用途 | 适用场景 |
|---|------|--------|------|---------|
| 1 | **Dispatcher Hook** | VM dispatcher 函数 | 拦截每个操作码执行 | 追踪 VM 执行流、记录 opcode 序列 |
| 2 | **Memory Hook** | 内存读写函数 | 追踪数据流 | 追踪 VM 内存操作、定位数据来源 |
| 3 | **Register Hook** | 寄存器操作 | 追踪计算过程 | 分析 VM 寄存器式指令集 |
| 4 | **Call Hook** | 函数调用指令 | 追踪外部调用 | 拦截 VM 调用外部函数 |
| 5 | **Return Hook** | 返回值 | 捕获加密结果 | 定位 VM 输出点 |
| 6 | **Exception Hook** | 异常处理 | 调试 VM 错误 | 捕获 VM 执行异常 |
| 7 | **Custom Opcode** | 注入自定义操作码 | 扩展 VM 能力 | 数据导出、Phase 标记 |

**完整技术细节**: [vm-hook-cookbook.md](references/vm-hook-cookbook.md)

---

## 通用 VM 结构识别

### JSVMP 典型特征

```javascript
// 1. 大数组 + 解释器 + for(;;)+switch
var bigArray = [/* 数千个数值 */];
function vmInterpreter() {
    while (true) {
        switch (bigArray[pc++]) {
            case 0: /* push */ break;
            case 1: /* pop */ break;
            // ... 上百个 case
        }
    }
}

// 2. rt[] 函数注册表
Array.prototype.push.apply(rtArray, [func1, func2, ...]);

// 3. 状态机模式
while (1) {
    var state = getNextState();
    switch (state) {
        case 324: /* ... */ break;
        // ... 上百个 state
    }
}
```

### VMP 变体特征

- **寄存器式**: 显式寄存器操作 (eax/ebx/ecx...)
- **栈式**: 所有操作通过栈进行 (push/pop)
- **混合式**: 栈 + 寄存器混合

### 关键定位方法

| 定位目标 | 方法 | 特征 |
|---------|------|------|
| VM 解释器 | 搜索 `while(true)` 或 `for(;;)` + 大量 `case` | 函数体最长，含上百个分支 |
| 字节码数组 | 解释器引用的大数组 | 数千个数值元素 |
| rt[] 注册点 | 搜索 `Array.prototype.push.apply` | 一次注册几百个函数 |
| 入口函数 | 追踪 `eval.call` 或 `vm.runInContext` | 触发 VM 执行的调用点 |
| 加密函数 | 搜索算法常量 (见下表) | 特征 magic number |

### 算法常量速查

```javascript
// SHA-1
0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0

// MD5
0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476

// CRC32
0xEDB88320

// XTEA / Tea
0x9E3779B9 (2654435769) — delta 常量

// AES (无特征常量，通过 S-Box 或密钥长度定位)

// Base64
'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
// 或自定义字母表
```

---

## 常见陷阱 (Pitfalls)

### 路线选择陷阱

| 陷阱 | 代价 | 正确做法 |
|------|------|---------|
| 反编译 VM 理解输出 | **数天浪费** | 数据驱动: 3-5 组样本对比，10 分钟定位 |
| 照搬其他项目的硬编码公式 | **1 天白费** | 数据驱动: 公式是版本特定的，不通用 |
| 跳过混合验证直接做输出 | 不知道哪步错 | 先用参考中间数据 + 纯算后段 → 验证正确，再逐步替换 |
| 运行时栈追踪反推 opcode 语义 | ~80B/天效率 | AST 静态提取: ~400B/小时 (效率 80 倍) |

### 数据驱动陷阱

| 陷阱 | 正确做法 |
|------|---------|
| 硬编码动态值 (如 type=2) | 多 session 采集，建立索引→值映射 |
| 不配套采集 (nsd/keys/basearr 分开拿) | 必须同一 session 内采集全套 |
| 用变量名定位 (下次加载就变) | 用结构特征: 参数个数、函数体常量、代码长度 |
| 假设字段顺序跨版本固定 | 每次用 basearrParse 验证 TLV 结构 |

### AST 反编译陷阱

| 陷阱 | 正确做法 |
|------|---------|
| AST 替代数据驱动 | AST 告诉你 "怎么算"，但具体值仍需数据驱动 |
| 假设 AST 脚本跨版本通用 | 变量名每次洗牌不同，脚本需适配 |
| 解析字符串内括号时截断 | 括号深度追踪必须处理字符串状态 |

### 编码/数据陷阱

| 陷阱 | 正确做法 |
|------|---------|
| HTTP 下载 JS 用 string 拼接 | Buffer 拼接 + toString('utf-8')，多字节字符会损坏 |
| 长度编码只考虑 1 字节 | 变长编码: <128 用 1B，>=128 用 `[0x80\|hi, lo]` |
| Cookie 名硬编码 | 从 keys 动态提取 (如 `keys[7].split(';')[5] + 'T'`) |

---

## 工具依赖

| 工具 | 用途 | 路线 |
|------|------|------|
| acorn + acorn-walk | AST 解析 + 遍历 | AST 反编译 |
| sdenv | VM 运行时环境模拟 | 数据驱动 |
| Node.js crypto | AES/HMAC/Hash 实现 | 两条路线 |
| js-beautify | 格式化混淆代码 (可选) | 预处理 |

## 真实案例补充

### TikTok 栈式虚拟机 (Stack-Based VM)

来自 [notemrovsky/tiktok-reverse-engineering](https://github.com/notemrovsky/tiktok-reverse-engineering)：

| 特征 | 说明 |
|------|------|
| **架构** | 栈式 VM，77 个 opcode，自定义字节码解释器 |
| **入口模式** | `decode("base64编码字节码")` → 解码成 bytecode → 传入 VM 执行 |
| **opcode 示例** | push/pop/dup/swap/call/jmp/jnz/add/sub/mul/div/and/or/xor/not/eq/lt/gt 等 |
| **string 混淆** | 层叠函数调用链，运行时逐步解码 |
| **加密函数识别** | 通过 magic number 定位 SHA-1 (0x67452301)、CRC32 (0xEDB88320) 等 |
| **复现思路** | 反汇编字节码 → 映射 opcode → 模拟执行 → 复现输出 |

**与瑞数对比**:
- 瑞数: 寄存器式 + 740 个 state + TLV 结构化输出，适合数据驱动路线
- TikTok: 栈式 + 77 个 opcode + 字节码编码为字符串，适合 AST 反编译路线
- 共同点: 都有 dispatcher 循环，运行时解码字符串

**对本技能的验证**: 路线选择准确 — TikTok VM 输出不可预测量化（每次不同），无法用数据驱动，**必须走 AST 反编译路线**。这与技能决策树一致。

### 通用 VM 结构扩展识别

除 JSVMP 和 VMP 外，近期(2025-2026)实际遇到的 VM 类型：

| 类型 | 特征 | 典型 opcode 数 | 代表 |
|------|------|---------------|------|
| 栈式 VM | push/pop + 操作指令 | 40-100 | TikTok (77) |
| 寄存器式 VM | eax/ebx 等显式寄存器 | 100-300 | 瑞数 (740+ state) |
| 字节码 + eval | eval("base64解码后的字节码") | 可变 | TikTok, 部分 WAF |
| 状态机 + 数组 | for(;;)+switch(大数组[pc++]) | 50-200 | JSVMP 标准 |
| rt[] 函数表 | Array.prototype.push.apply 注册 | 100-500 | 常见 JSVM |

---

## 资源导航

| 文件 | 内容 |
|------|------|
| [references/vm-hook-cookbook.md](references/vm-hook-cookbook.md) | 7 种 VM 注入技术详解 + 代码示例 |
| [references/data-driven-methodology.md](references/data-driven-methodology.md) | 数据驱动路线详细步骤 + TLV 分析模式 |
| [references/ast-decompiler-methodology.md](references/ast-decompiler-methodology.md) | AST 反编译路线四步管线 + rt[] 映射 |
| **notemrovsky/tiktok-reverse-engineering** | TikTok 栈式 VM (77 opcode) 完整逆向案例 — 栈式 VM 实战参考 |

---

## vm-and-bytecode-reverse

# SKILL: VM & Bytecode Reverse Engineering — Expert Analysis Playbook

> **AI LOAD INSTRUCTION**: Expert techniques for reversing custom virtual machines and bytecode interpreters. Covers dispatcher identification, opcode mapping, custom ISA reconstruction, disassembler/decompiler writing, maze challenges, and real-world VM protector analysis. Base models often fail to recognize the fetch-decode-execute pattern or attempt to analyze VM bytecode as native code.

## 0. RELATED ROUTING

- [code-obfuscation-deobfuscation](related-skill: code-obfuscation-deobfuscation) when the VM is a commercial protector (VMProtect/Themida)
- [symbolic-execution-tools](related-skill: symbolic-execution-tools) when using angr to solve VM-based challenges
- [anti-debugging-techniques](related-skill: anti-debugging-techniques) when the VM includes anti-debug checks

### Quick identification

| Binary Pattern | Likely VM Type | Start With |
|---|---|---|
| `while(1) { switch(bytecode[pc]) }` | Switch-based dispatcher | Map each case to an operation |
| Indirect jump via table `jmp [table + opcode*8]` | Table-based dispatcher | Dump jump table, analyze handlers |
| Nested if-else chain on byte value | If-chain dispatcher | Same as switch, just different syntax |
| Stack push/pop dominant operations | Stack-based VM | Identify push, pop, arithmetic ops |
| `reg[X] = ...` array operations | Register-based VM | Map register indices to operations |
| 2D grid + direction input | Maze challenge | Extract grid, apply BFS/DFS |

---

## 1. CUSTOM VM IDENTIFICATION

### 1.1 Structural Indicators

```
VM Architecture Components:
┌─────────────────────────────────┐
│  Bytecode Program (data section)│
├─────────────────────────────────┤
│  Program Counter (pc/ip)        │
│  Register File / Stack          │
│  Memory / Data Area             │
├─────────────────────────────────┤
│  Dispatcher Loop                │
│  ├─ Fetch: opcode = code[pc]    │
│  ├─ Decode: lookup handler      │
│  └─ Execute: run handler        │
└─────────────────────────────────┘
```

### 1.2 IDA/Ghidra Signatures

**Switch dispatcher** (most common in CTF):
```c
while (running) {
    unsigned char op = bytecode[pc++];
    switch (op) {
        case 0x00: /* nop */       break;
        case 0x01: /* push imm */  stack[sp++] = bytecode[pc++]; break;
        case 0x02: /* add */       stack[sp-2] += stack[sp-1]; sp--; break;
        // ...
        case 0xFF: /* halt */      running = 0; break;
    }
}
```

**Table dispatcher** (more optimized):
```c
typedef void (*handler_t)(vm_ctx_t*);
handler_t handlers[256] = { handle_nop, handle_push, handle_add, ... };

while (running) {
    handlers[bytecode[pc++]](&ctx);
}
```

---

## 2. ANALYSIS METHODOLOGY

### Step 1: Find the Dispatcher

Look for:
- Large switch statement (many cases) in a loop
- Array of function pointers indexed by a byte from a data buffer
- Single function with high cyclomatic complexity
- Cross-references to a data buffer read byte-by-byte

### Step 2: Map Opcodes to Operations

For each case/handler, determine:

| Property | How to Identify |
|---|---|
| Opcode value | Case number or table index |
| Operation type | Register/stack modifications |
| Operand count | How many bytes consumed after opcode |
| Operand type | Immediate value, register index, or memory address |
| Side effects | Output, memory write, flag modification |

### Step 3: Extract Bytecode Program

```python
# Typical extraction from binary
import struct

with open('challenge', 'rb') as f:
    f.seek(bytecode_offset)
    bytecode = f.read(bytecode_length)

# Or from IDA:
# bytecode = idc.get_bytes(bytecode_addr, bytecode_len)
```

### Step 4: Write Custom Disassembler

```python
OPCODES = {
    0x00: ("nop",  0),    # (mnemonic, operand_bytes)
    0x01: ("push", 1),    # push immediate byte
    0x02: ("pop",  0),
    0x03: ("add",  0),
    0x04: ("sub",  0),
    0x05: ("xor",  0),
    0x06: ("cmp",  0),
    0x07: ("jmp",  2),    # jump to 16-bit address
    0x08: ("je",   2),
    0x09: ("jne",  2),
    0x0A: ("mov",  2),    # mov reg, imm
    0x0B: ("load", 1),    # load from memory[operand]
    0x0C: ("store",1),    # store to memory[operand]
    0x0D: ("print",0),
    0x0E: ("read", 0),    # read input
    0xFF: ("halt", 0),
}

def disassemble(bytecode):
    pc = 0
    while pc < len(bytecode):
        op = bytecode[pc]
        if op not in OPCODES:
            print(f"  {pc:04x}: UNKNOWN {op:#04x}")
            pc += 1
            continue

        mnemonic, operand_size = OPCODES[op]
        operands = bytecode[pc+1:pc+1+operand_size]
        operand_str = ' '.join(f'{b:#04x}' for b in operands)
        print(f"  {pc:04x}: {mnemonic:8s} {operand_str}")
        pc += 1 + operand_size

disassemble(bytecode)
```

### Step 5: Analyze Disassembled Program

With the custom disassembly, apply standard reverse engineering:
- Identify input reading (read opcode)
- Trace data flow from input to comparison
- Determine success/failure conditions
- Extract the check logic (often XOR/ADD transformations of input compared against constants)

---

## 3. COMMON VM PATTERNS IN CTF

### 3.1 Stack-Based VM

Operations work on a stack (like JVM or Python bytecode).

| Opcode | Operation | Stack Effect |
|---|---|---|
| PUSH imm | Push immediate value | [...] → [..., imm] |
| POP | Discard top | [..., a] → [...] |
| ADD | Add top two | [..., a, b] → [..., a+b] |
| SUB | Subtract | [..., a, b] → [..., a-b] |
| MUL | Multiply | [..., a, b] → [..., a*b] |
| XOR | Bitwise XOR | [..., a, b] → [..., a^b] |
| CMP | Compare | [..., a, b] → [..., (a==b)] |
| JMP addr | Unconditional jump | no change |
| JZ addr | Jump if top is zero | [..., a] → [...] |
| PRINT | Output top as char | [..., a] → [...] |
| READ | Read char to stack | [...] → [..., input] |
| HALT | Stop execution | - |

### 3.2 Register-Based VM

Operations use register indices (like x86, ARM).

| Opcode | Format | Operation |
|---|---|---|
| MOV r, imm | `0x01 RR II II` | reg[R] = imm16 |
| MOV r1, r2 | `0x02 R1 R2` | reg[R1] = reg[R2] |
| ADD r1, r2 | `0x03 R1 R2` | reg[R1] += reg[R2] |
| SUB r1, r2 | `0x04 R1 R2` | reg[R1] -= reg[R2] |
| XOR r1, r2 | `0x05 R1 R2` | reg[R1] ^= reg[R2] |
| CMP r1, r2 | `0x06 R1 R2` | flags = compare(r1, r2) |
| JMP addr | `0x07 AA AA` | pc = addr |
| JE addr | `0x08 AA AA` | if equal: pc = addr |
| LOAD r, [addr] | `0x09 RR AA` | reg[R] = mem[addr] |
| STORE [addr], r | `0x0A AA RR` | mem[addr] = reg[R] |
| SYSCALL | `0x0B` | I/O operation based on reg[0] |
| HALT | `0xFF` | stop |

### 3.3 Brainfuck-like / Esoteric VMs

| BF Command | VM Equivalent | Description |
|---|---|---|
| `>` | INC ptr | Move data pointer right |
| `<` | DEC ptr | Move data pointer left |
| `+` | INC [ptr] | Increment byte at pointer |
| `-` | DEC [ptr] | Decrement byte at pointer |
| `.` | OUTPUT [ptr] | Output byte at pointer |
| `,` | INPUT [ptr] | Input byte to pointer |
| `[` | JZ forward | Jump past `]` if byte is zero |
| `]` | JNZ back | Jump back to `[` if byte is nonzero |

---

## 4. MAZE CHALLENGES

### 4.1 Identification

- Binary reads directional input (WASD, arrow keys, UDLR)
- 2D array in data section (walls, paths, start, end)
- Position tracking with x,y coordinates
- Win condition at specific coordinates

### 4.2 Map Extraction

```python
# Extract maze grid from binary data section
MAZE_ADDR = 0x601060
WIDTH = 20
HEIGHT = 15

# From binary dump:
maze = []
for row in range(HEIGHT):
    line = ""
    for col in range(WIDTH):
        cell = bytecode[MAZE_ADDR + row * WIDTH + col - base_addr]
        if cell == 0: line += "."    # path
        elif cell == 1: line += "#"  # wall
        elif cell == 2: line += "S"  # start
        elif cell == 3: line += "E"  # end
        else: line += "?"
    maze.append(line)
    print(line)
```

### 4.3 Automated Solving

```python
from collections import deque

def solve_maze(maze, start, end):
    """BFS solver returns direction string."""
    rows, cols = len(maze), len(maze[0])
    directions = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    queue = deque([(start, "")])
    visited = {start}

    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == end:
            return path

        for name, (dr, dc) in directions.items():
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols and
                maze[nr][nc] != '#' and (nr, nc) not in visited):
                visited.add((nr, nc))
                queue.append(((nr, nc), path + name))

    return None

# Find start and end positions
for r, row in enumerate(maze):
    for c, cell in enumerate(row):
        if cell == 'S': start = (r, c)
        if cell == 'E': end = (r, c)

solution = solve_maze(maze, start, end)
print(f"Path: {solution}")
```

### 4.4 Direction Encoding

Different challenges encode directions differently:

| Encoding | Up | Down | Left | Right |
|---|---|---|---|---|
| WASD | W | S | A | D |
| UDLR | U | D | L | R |
| Arrow keys | ↑ (0x48) | ↓ (0x50) | ← (0x4B) | → (0x4D) |
| Numbers | 1 | 2 | 3 | 4 |
| Hex opcodes | 0x01 | 0x02 | 0x03 | 0x04 |

---

## 5. REAL-WORLD VM VARIANTS

### 5.1 Black-Box VM Fuzzing

When opcodes and handler structure aren't obvious from static analysis, infer the ISA by fuzzing:

**Methodology:**
1. **Determine instruction alignment** — feed bytecode with varying bit widths (6-11 bits), observe register/memory changes
2. **Fuzz with random bytes** — track which byte positions affect which VM state
3. **Build instruction set** — from observed side effects:
   ```
   000 xxxxxxxx  jmpz    001 xxxxxxxx  jmp
   010 xxxxxxxx  call     011 xxxxxxxx  label
   1000 xxxxxxx  loadram  1001 xxxxxxx  saveram
   110 xxxxxxxx  loadi    11100 xxxxxx  shl
   11101 xxxxxx  shr      111100 not    111101 and
   111110 or    111111 setif
   ```
4. **Build assembler/disassembler** — then convert raw bytecode to readable assembly
5. **Fill missing primitives** — XOR from AND/OR/NOT, ADD from full-adder chains

### 5.2 RVA-Based Opcode Dispatching

Opcodes are not fixed numbers — they're RVAs to handler functions:

```c
// Dispatcher pattern:
while (running) {
    uint16_t rva = *(uint16_t*)(bytecode + pc);
    pc += 2;
    handler_t handler = (handler_t)(base + rva);
    handler(&ctx);
}
```

**Analysis approach:**
1. Dump all RVAs from bytecode
2. Map each RVA to its handler function in the binary
3. Reverse each handler to determine its operation
4. Build the opcode mapping from observed behavior

### 5.3 State Machine VMs (90K+ States)

Extremely large state transition tables where each state encodes the program logic:

```java
// BFS to find valid path through 90K+ states
var agenda = new ArrayDeque<State>();
agenda.add(new State(0, ""));
while (!agenda.isEmpty()) {
    var current = agenda.remove();
    if (current.path.length() == TARGET_LENGTH) {
        println(current.path);
        continue;
    }
    for (var transition : machine.get(current.state).entrySet()) {
        agenda.add(new State(transition.getValue(),
                             current.path + (char) transition.getKey()));
    }
}
```

### 5.4 Mixed-Mode (x86-64 / x86) Stagers

64-bit ELF that jumps into 32-bit code via `retf`/`retfq` (bytes `0xCB`):

```asm
; 64-bit code pushes 32-bit far pointer, then retf to switch mode
push    0x23           ; 32-bit code segment selector
push    rbx            ; 32-bit target address
retfq                  ; far return — switches to 32-bit mode
```

**Analysis approach:** Identify `retf`/`retfq` in the binary, locate the pushed target address, disassemble target as 32-bit code.

### 5.5 Known-Plaintext XOR with Position Index

```python
# cipher[i] = plain[i] ^ key[i % k] ^ i  (or ^ (i & 0xff))
def solve(enc, known_prefix):
    for klen in range(2, 33):
        key = bytearray(klen)
        ok = True
        for i, b in enumerate(known_prefix):
            if i >= len(enc): break
            ki = i % klen
            v = enc[i] ^ b  # remove index first
            # If position index XOR: v = (enc[i] ^ i) ^ b to get key
            if key[ki] != 0 and key[ki] != v:
                ok = False; break
            key[ki] = v
        if not ok: continue
        # Validate: decrypted result should be printable ASCII
        pt = bytes(enc[i] ^ key[i % klen] for i in range(len(enc)))
        if all(32 <= c < 127 for c in pt):
            print(klen, key, pt)
```

## 6. REAL-WORLD VM PROTECTORS

### 6.1 VMProtect Analysis Approach

```
1. Find VM entry: search for pushad/pushfd sequence
2. Identify VM context structure (registers, flags, bytecode pointer)
3. Locate handler table (often obfuscated with opaque predicates)
4. For each handler:
   a. Remove junk code / opaque predicates
   b. Identify the core operation
   c. Document handler semantics
5. Trace bytecode execution (instruction-level trace)
6. Reconstruct original code from trace
```

### 6.2 Tigress Obfuscator

Academic VM obfuscator with configurable protection layers.

| Feature | Approach |
|---|---|
| Single-dispatch VM | Standard handler extraction |
| Split handlers | Handlers spread across multiple functions |
| Nested VMs | Outer VM handler invokes inner VM |
| Encrypted bytecode | Dynamic decryption before each fetch |
| Polymorphic handlers | Different code for same operation on each build |

### 6.3 Common VM Protector Patterns

| Protector | Dispatcher Style | Difficulty |
|---|---|---|
| VMProtect | Table + opaque predicates | High |
| Themida (Code Virtualizer) | CISC-like, large handler set | High |
| Tigress | Configurable, academic | Medium-High |
| Custom CTF VM | Simple switch | Low-Medium |
| Movfuscator | All-mov computation | Medium |

---

## 7. TOOLS

| Tool | Purpose | Usage |
|---|---|---|
| IDA Pro | Identify dispatcher, reverse handlers | F5 decompile, xref analysis |
| Ghidra | Free alternative with Sleigh processor modules | Write custom processor for VM ISA |
| angr | Symbolic execution through VM | Treat entire VM as constraint system |
| Pin / DynamoRIO | Dynamic instrumentation for tracing | Record opcode handler execution sequence |
| REVEN | Full-system trace recording | Replay and analyze VM execution |
| Unicorn | Emulate VM execution | Fast handler emulation |
| Miasm | IR-based analysis | Lift VM handlers to IR for analysis |
| Custom Python | Write disassembler/decompiler | Per-challenge custom tooling |

### Ghidra Sleigh Processor Module

For recurring VM architectures, write a Sleigh processor specification:

```
define space ram      type=ram_space      size=2  default;
define space register type=register_space  size=1;

define register offset=0 size=1 [ R0 R1 R2 R3 FLAGS PC SP ];

define token opcode(8)
    op = (0,7)
;

:NOP    is op=0x00 { }
:PUSH   imm is op=0x01; imm { SP = SP - 1; *[ram]:1 SP = imm; }
:POP    is op=0x02 { SP = SP + 1; }
:ADD    is op=0x03 { local a = *[ram]:1 (SP+1); *[ram]:1 (SP+1) = a + *[ram]:1 SP; SP = SP + 1; }
```

---

## 8. DECISION TREE

```
Binary contains custom bytecode interpreter?
│
├─ Can you identify the dispatcher?
│  ├─ Yes (switch/table/if-chain)
│  │  ├─ Few opcodes (< 20) → Simple CTF VM
│  │  │  ├─ Stack-based → map push/pop/arithmetic ops
│  │  │  ├─ Register-based → map mov/add/cmp ops
│  │  │  └─ Write disassembler → analyze program → solve
│  │  │
│  │  └─ Many opcodes (50+) → Commercial protector
│  │     ├─ Known protector → use specific deprotection tools
│  │     └─ Custom → trace execution, pattern-match handlers
│  │
│  └─ No clear dispatcher
│     ├─ All-mov instructions → movfuscator
│     ├─ Encrypted bytecode → find decryption, dump after decode
│     └─ Split/distributed handlers → trace execution to find them
│
├─ Is it a maze challenge?
│  ├─ Extract grid from data section
│  ├─ Identify direction encoding
│  ├─ BFS/DFS to find shortest path
│  └─ Convert path to expected input format
│
├─ Is there input validation in VM?
│  ├─ Small input space → brute-force via Unicorn emulation
│  ├─ Known format → constrained angr solve
│  └─ Complex check → write disassembler, analyze check logic
│
└─ Multiple VM layers (VM in VM)?
   ├─ Analyze outer VM first
   ├─ Extract inner bytecode
   ├─ Repeat analysis for inner VM
   └─ Consider: symbolic execution may handle nested VMs directly
```

---

## 9. CTF SOLVING WORKFLOW

```
1. Run the binary — understand I/O behavior
   └─ What input does it expect? What output on success/failure?

2. Open in IDA/Ghidra — find the main loop
   └─ Look for while/for loop with switch or indirect jump

3. Identify VM components:
   ├─ Bytecode location (where is the program data?)
   ├─ PC/IP variable (how is current position tracked?)
   ├─ Registers/stack (where is VM state stored?)
   └─ I/O handlers (which opcodes read input / write output?)

4. Map all opcodes (create the ISA specification)
   └─ For each case/handler: opcode number, operation, operands

5. Write disassembler in Python
   └─ Output readable assembly for the bytecode

6. Analyze the disassembled program:
   ├─ Find input reading
   ├─ Trace transformations applied to input
   ├─ Find comparison against expected values
   └─ Reverse the transformation to find valid input

7. Solve:
   ├─ If simple transforms (XOR, ADD) → reverse manually
   ├─ If complex → feed to Z3 as constraints
   └─ If maze → extract grid, run pathfinding
```

---
