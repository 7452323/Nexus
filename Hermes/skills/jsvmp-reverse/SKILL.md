---
category: reverse-engineering
name: jsvmp-reverse
version: 1.0.0
description: JSVMP/VMP 虚拟机逆向通用方法论 — 数据驱动 + AST 反编译双路线，7 种 VM Hook 注入技术，适用于所有 JS 虚拟机保护场景
tags:
  - jsvmp
  - vmp
  - vm reverse
  - bytecode decompiler
  - data driven
  - ast
  - vm hook
  - opcode extraction
  - dispatcher
  - switch-case
---

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

---

## 资源导航

| 文件 | 内容 |
|------|------|
| [references/vm-hook-cookbook.md](references/vm-hook-cookbook.md) | 7 种 VM 注入技术详解 + 代码示例 |
| [references/data-driven-methodology.md](references/data-driven-methodology.md) | 数据驱动路线详细步骤 + TLV 分析模式 |
| [references/ast-decompiler-methodology.md](references/ast-decompiler-methodology.md) | AST 反编译路线四步管线 + rt[] 映射 |
