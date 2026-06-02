# AST 反编译方法论

## 核心思想

JSVMP 的 eval 代码是合法 JS，可以被标准 AST 解析器 (acorn/babel) 完整解析。虽然代码高度混淆 (变量名洗牌、二叉搜索 if-else、多层嵌套)，但语法结构完整，AST 可以精确提取每一个语义单元。

---

## 适用条件

满足以下**任一**即可选择 AST 反编译:

1. 数据驱动无法覆盖 (输出不可重复、字段无法对比)
2. 需要理解完整逻辑 (如后缀签名、协议解析)
3. VM 结构相对标准 (dispatcher switch-case、rt[] 函数注册表)
4. 产出需要可维护 (算法变更时可快速适配)

---

## AST 能做什么 / 不能做什么

### 能做

1. 从 VM 解释器中提取全部 opcode 的 JS 实现
2. 建立完整的 rt[] 函数映射表 (440+ 个函数)
3. 定位特定算法 (SHA-1, Huffman, AES) 的精确函数位置
4. 追踪数据流: 从入口函数到最终输出的完整调用链
5. 自动反汇编字节码 → 可读汇编 → 伪 JS 代码

### 不能做

1. 不能替代数据驱动: AST 告诉你 "怎么算"，但具体值仍需数据驱动对比
2. 不能跨版本通用: 变量名每次洗牌不同，AST 脚本需要适配
3. 不能处理运行时状态: 动态生成的字符串表、运行时决定的分支

### 最佳实践

```
1. 先用运行时追踪 (VM Hook) 建立整体理解: 入口、出口、数据管线
2. 再用 AST 系统性提取: opcode 表、函数映射、算法定位
3. 最后用数据驱动填补 AST 无法覆盖的动态部分: 具体字段值
```

---

## 四步反编译管线

### Step 1: AST 提取 opcode → opcodes.json

**输入**: VM 核心代码 (混淆 JS)
**输出**: opcodes.json (所有 opcode 的 JS 实现)

**核心方法**: 找到 VM 解释器函数 (通常函数体最长，包含大量 `if(varName === N)` 形式的条件分支)，遍历其 AST 中所有 `BinaryExpression(===)` 条件分支，每个分支对应一个 opcode。

```javascript
const acorn = require('acorn');
const walk = require('acorn-walk');
const fs = require('fs');

const code = fs.readFileSync('vm_core.js', 'utf-8');
const ast = acorn.parse(code, { ecmaVersion: 2020 });

// Step 1a: 定位 VM 解释器函数
// 方法: 找函数体最长的函数，或搜索 while(true) + switch 结构
let vmInterpreter = null;
let maxBodySize = 0;

walk.simple(ast, {
    FunctionDeclaration(node) {
        const bodySize = node.end - node.start;
        if (bodySize > maxBodySize) {
            maxBodySize = bodySize;
            vmInterpreter = node;
        }
    },
    FunctionExpression(node) {
        const bodySize = node.end - node.start;
        if (bodySize > maxBodySize) {
            maxBodySize = bodySize;
            vmInterpreter = node;
        }
    }
});

console.log('[INFO] VM interpreter found, body size:', maxBodySize);

// Step 1b: 提取所有 opcode 分支
const opcodes = {};

walk.simple(vmInterpreter, {
    IfStatement(node) {
        if (node.test.type === 'BinaryExpression' &&
            node.test.operator === '===' &&
            node.test.right.type === 'Literal' &&
            typeof node.test.right.value === 'number') {

            const opNum = node.test.right.value;
            const bodySrc = code.substring(node.consequent.start, node.consequent.end);

            if (!opcodes[opNum]) {
                opcodes[opNum] = bodySrc.replace(/\s+/g, ' ').trim();
            }
        }
    }
});

fs.writeFileSync('opcodes.json', JSON.stringify(opcodes, null, 2));
console.log('[INFO] Extracted', Object.keys(opcodes).length, 'opcodes');
```

**输出示例**:

```json
{
    "0": "{ _$eW = _$cR[_$gH._$hn[++_$bh]]; }",
    "1": "{ _$eW = _$gH._$eR[_$gH._$hn[++_$bh]]; }",
    "2": "{ _$eW = !_$eW; }",
    "6": "{ _$eW = _$eW[_$cR[_$gH._$hn[++_$bh]]]; }",
    "8": "{ var _$fc = _$gH._$hn[++_$bh]; _$eW = _$eW(_$fc ? ... }"
}
```

### Step 2: 反汇编字节码 → 汇编指令

**输入**: 字节码数组 + opcodes.json
**输出**: 人类可读的汇编指令

将每个函数的字节码数组转化为助记符指令:

```javascript
function disasm(bc, opcodes) {
    const lines = [];
    let pc = 0;

    while (pc < bc.length) {
        const op = bc[pc];
        const startPc = pc;
        let instr = '';

        switch (op) {
            case 0:  instr = 'ARG(' + bc[++pc] + ')';       pc++; break;
            case 1:  instr = 'LOAD_GLOBAL(' + bc[++pc] + ')'; pc++; break;
            case 2:  instr = 'NOT';                          pc++; break;
            case 3:  instr = 'SET_VAR';                      pc++; break;
            case 5:  instr = 'SET_PROP(' + bc[++pc] + ')';   pc++; break;
            case 6:  instr = 'GET_PROP(' + bc[++pc] + ')';   pc++; break;
            case 7:  instr = 'SUB';                          pc++; break;
            case 8:  instr = 'CALL(' + bc[++pc] + ')';       pc++; break;
            case 9:  instr = 'TRY_ENTER';                    pc++; break;
            case 10: instr = 'CATCH_ENTER';                  pc++; break;
            case 11: instr = 'LOAD_CONST(' + bc[++pc] + ')'; pc++; break;
            case 12: instr = 'LOAD_CALLSTACK';               pc++; break;
            case 13: instr = 'PUSH_CALLSTACK';               pc++; break;
            // ... 根据 opcodes.json 补充所有 opcode
            default: instr = 'OP_' + op + '(???)';           pc++; break;
        }
        lines.push(startPc.toString().padStart(4) + ': ' + instr);
    }
    return lines;
}
```

**输出示例**:

```
   0: ARG(0)
   2: LOAD_GLOBAL(0)
   4: GET_PROP(18)       // .length
   6: LOAD_GLOBAL(0)
   8: LOAD_CONST(67)      // rt[67] 常量表
  10: SET_PROP(0)         // [0] = 131072
  12: BITSHIFT_RIGHT
  14: LOAD_CONST(67)
  16: SET_PROP(7)         // [7] = 127
  18: BITWISE_AND
  20: SET_VAR
```

### Step 3: 栈模拟 → 伪 JS 代码

**输入**: 反汇编输出 + 字符串表/常量表映射
**输出**: 可读的伪 JS 代码

模拟 VM 的栈操作，将汇编指令转化为表达式:

```javascript
function translateBytecode(bc, stringTable, constTable) {
    const stack = [];
    const lines = [];
    let pc = 0;

    function push(expr) { stack.push(expr); }
    function pop() { return stack.length ? stack.pop() : '/*empty*/'; }
    function peek() { return stack[stack.length - 1] || '/*empty*/'; }
    function emit(code) { lines.push('    ' + code); }

    while (pc < bc.length) {
        const op = bc[pc];
        switch (op) {
            case 0: // ARG
                push('arg' + bc[++pc]);
                pc++;
                break;

            case 1: // LOAD_GLOBAL
                push('G[' + bc[++pc] + ']');
                pc++;
                break;

            case 5: { // SET_PROP
                const propIdx = bc[++pc];
                const val = pop();
                const obj = peek();
                emit(obj + '.' + stringTable[propIdx] + ' = ' + val + ';');
                pc++;
                break;
            }

            case 6: // GET_PROP
                push(peek() + '.' + stringTable[bc[++pc]]);
                pc++;
                break;

            case 8: { // CALL
                const argc = bc[++pc];
                const args = [];
                for (let i = 0; i < argc; i++) args.unshift(pop());
                const fn = pop();
                push(fn + '(' + args.join(', ') + ')');
                pc++;
                break;
            }

            case 11: // LOAD_CONST
                push('rt[' + bc[++pc] + ']');
                pc++;
                break;

            // ... 更多 opcode
        }
    }
    return lines;
}
```

**输出示例**:

```javascript
function child40_tlvParser(cookieS_bytes) {
    var len = (cookieS_bytes.length >>> 0) & 127;
    var pos = 0;
    while (pos < len) {
        var type = sliceRead(cookieS_bytes, pos);
        var blockLen = sliceRead(cookieS_bytes, pos);
        var block = cookieS_bytes.slice(pos, pos + blockLen);
    }
}
```

### Step 4: 手动语义标注

**输入**: 伪 JS 代码 + 数据驱动对比结果
**输出**: 完整语义理解 + 算法文档

AST 自动翻译的代码缺乏变量语义。通过以下方式标注:

1. **常量表反查**: `rt[67][28] = 45` → 这是 Huffman 权重中 byte=0 的权重
2. **字符串表反查**: `stringTable[18] = "length"`, `stringTable[16] = "cookie"`
3. **函数签名对比**: `rt[129]` 的函数体包含 `0x67452301` → SHA-1 初始化常量
4. **数据流追踪**: 从输入到输出的完整链路

---

## rt[] 函数注册机制

VM 代码中通常有一个关键的大 push 语句，一次注册所有运行时函数:

```javascript
Array.prototype.push.apply(rtArray, [func1, func2, func3, ...]);
```

### AST 提取方法

```javascript
// 定位 push.apply 调用
const pushPattern = rtArrayName + '.push(';
const pushStart = code.indexOf(pushPattern) + pushPattern.length;

// 按顶层逗号分割参数 (括号深度追踪)
let depth = 0, args = [], current = '';
for (let i = pushStart; i < code.length; i++) {
    const c = code[i];
    if (c === '(' || c === '[' || c === '{') depth++;
    else if (c === ')' || c === ']' || c === '}') {
        if (depth === 0) break;
        depth--;
    }
    else if (c === ',' && depth === 0) {
        args.push(current.trim());
        current = '';
        continue;
    }
    current += c;
}

// 建立 rt 映射
const RT_BASE = 56; // push 之前已填充的函数数量
// args[0] → rt[RT_BASE], args[1] → rt[RT_BASE+1], ...
```

### 常见 rt 函数类型

| rt 类型 | 示例 | 识别方法 |
|---------|------|---------|
| 字符串表 | `rt[64]` = 属性名映射 | 返回字符串数组 |
| 常量表 | `rt[67]` = 数值常量 | 返回数值数组 |
| 算法函数 | `rt[129]` = SHA-1 | 包含算法常量 |
| DOM 操作 | `rt[75]` = Cookie 读取 | 引用 document.cookie |
| 编码函数 | `rt[146]` = Huffman | 特征编码逻辑 |
| 业务函数 | `rt[239]` = 后缀生成器 | 函数体最大 (15KB+) |

---

## 算法定位

### 通过常量搜索定位

```javascript
// SHA-1
const sha1Constants = ["1732584193", "4023233417", "2562383102", "271733878", "3285377520"];
sha1Constants.forEach(c => {
    const pos = code.indexOf(c);
    if (pos !== -1) console.log('[SHA-1] Found at position', pos);
});

// CRC32
const crc32Pos = code.indexOf("3770623696"); // 0xEDB88320
if (crc32Pos !== -1) console.log('[CRC32] Found at position', crc32Pos);

// XTEA
const xteaPos = code.indexOf("2654435769"); // 0x9E3779B9
if (xteaPos !== -1) console.log('[XTEA] Found at position', xteaPos);
```

### 通过 rt 映射 + 调用链追踪

```javascript
// 1. 找到目标函数的 rt 索引
// 2. 在 AST 中搜索所有引用 rt[index] 的位置
// 3. 从引用点回溯调用链

function traceRtCallChain(ast, rtIndex, code) {
    const callSites = [];

    walk.simple(ast, {
        MemberExpression(node) {
            if (node.object.name === rtArrayName &&
                node.property.value === rtIndex) {
                callSites.push({
                    position: node.start,
                    context: code.substring(Math.max(0, node.start - 50), node.end + 50)
                });
            }
        }
    });

    return callSites;
}
```

---

## AST vs 运行时追踪: 效率对比

| 维度 | 运行时追踪 | AST 静态分析 |
|------|-----------|-------------|
| 前置条件 | 需要可执行环境 | 只需代码文本文件 |
| opcode 来源 | Hook while(1) 逐个记录 | AST 一次解析全部提取 |
| 覆盖率 | 只能覆盖当次执行路径 | 覆盖所有分支, 100% opcode |
| 速度 | ~80 字节码/天 (手动追踪) | ~400 字节码/小时 (批量翻译) |
| 可复用性 | 每次运行需重新 hook | 脚本可复用，适配变量名即可 |
| 准确性 | 受运行时状态影响 | 精确到每个 AST 节点 |
| **效率比** | 基准 (1x) | **约 80x** |

**关键结论**: 运行时追踪适合发现入口点和验证假设，AST 适合批量提取和系统性分析。两者结合效果最好。

---

## _ifElse 二叉搜索分发

许多 JSVMP 使用二叉搜索将线性 opcode 列表转化为高效的 if-else 分发:

```javascript
// 原始线性分发 (低效)
if (op === 0) { ... }
else if (op === 1) { ... }
else if (op === 2) { ... }
// ... 114 个分支

// 二叉搜索分发 (高效)
if (op < 57) {
    if (op < 28) {
        if (op < 14) { ... }
        else { ... }
    } else { ... }
} else { ... }
```

**步长表**: `[4, 16, 64, 256, 1024, 4096, 16384, 65536]`

**AST 处理**: 二叉搜索的 if-else 嵌套结构需要递归遍历，而不是简单的线性 IfStatement 处理。

```javascript
function extractOpcodesFromBinarySearch(node, opcodes, code) {
    if (node.type !== 'IfStatement') return;

    // 检查是否是 opcode 比较
    if (node.test.type === 'BinaryExpression' &&
        node.test.operator === '===' &&
        node.test.right.type === 'Literal') {

        const opNum = node.test.right.value;
        opcodes[opNum] = code.substring(node.consequent.start, node.consequent.end);
    }

    // 递归处理 else 分支
    if (node.alternate) {
        extractOpcodesFromBinarySearch(node.alternate, opcodes, code);
    }
}
```

---

## URL 解析追踪技巧

VM 通常不直接使用 `new URL()` 或 `location` 对象，而是用 DOM 标准的 URL 解析技巧:

```javascript
// VM 中常见的 URL 解析方式
var a = document.createElement('a');
a.href = targetUrl;
var pathname = a.pathname;   // 自动解析
var search = a.search;       // 自动解析
var hostname = a.hostname;   // 自动解析
```

**意义**: 在 jsdom/sdenv 环境中，`document.createElement('a')` 必须正确支持 URL 解析，否则 VM 逻辑会失败。

---

## 适用性边界

### 适合 AST 的场景

- 提取 VM 解释器的全部 opcode 实现
- 建立 rt[] 函数映射表
- 定位特定算法 (通过常量搜索)
- 批量反汇编字节码
- 追踪函数调用链 (静态分析)
- 理解代码结构和控制流

### 不适合 AST 的场景

- 输出具体值的确定 → 用数据驱动对比
- 运行时动态生成的数据 → 用 Hook 采集
- 需要实际运行验证的逻辑 → 用 sdenv 运行
- 高度动态的分支选择 → 运行时追踪更直接

---

## 工具脚本模板

### 完整 AST 提取管线

```javascript
const acorn = require('acorn');
const walk = require('acorn-walk');
const fs = require('fs');

async function astPipeline(codePath) {
    const code = fs.readFileSync(codePath, 'utf-8');
    const ast = acorn.parse(code, { ecmaVersion: 2020 });

    // 1. 找到 VM 解释器
    const vmFunc = findLargestFunction(ast, code);

    // 2. 提取 opcodes
    const opcodes = extractOpcodes(vmFunc, code);
    fs.writeFileSync('opcodes.json', JSON.stringify(opcodes, null, 2));

    // 3. 建立 rt[] 映射
    const rtMap = extractRtMap(code);
    fs.writeFileSync('rt_map.json', JSON.stringify(rtMap, null, 2));

    // 4. 定位算法
    const algorithms = locateAlgorithms(code);
    fs.writeFileSync('algorithms.json', JSON.stringify(algorithms, null, 2));

    return { opcodes, rtMap, algorithms };
}

function findLargestFunction(ast, code) {
    let largest = null, maxSize = 0;
    walk.simple(ast, {
        FunctionDeclaration(node) {
            const size = node.end - node.start;
            if (size > maxSize) { maxSize = size; largest = node; }
        }
    });
    return largest;
}

function locateAlgorithms(code) {
    const algorithms = {};
    const signatures = {
        'SHA-1': /0x67452301|1732584193/,
        'CRC32': /0xEDB88320|3770623696/,
        'XTEA': /0x9E3779B9|2654435769/,
        'Huffman': /weight.*45|weight.*6/,
        'Base64': /ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/
    };
    for (const [name, pattern] of Object.entries(signatures)) {
        const match = code.match(pattern);
        if (match) algorithms[name] = match.index;
    }
    return algorithms;
}
```

---

## 常见陷阱

1. **AST 替代数据驱动**: AST 告诉你算法结构，但具体参数值仍需数据驱动验证
2. **假设脚本跨版本通用**: 变量名每次洗牌不同，脚本需适配
3. **括号深度追踪截断**: 字符串内的括号必须跳过，否则函数体提取不完整
4. **二叉搜索 if-else 误判**: 不是所有 if-else 都是 opcode 分发，需检查条件模式
5. **eval 代码格式依赖**: AST 解析前不要做格式化 (可能改变字符串/注释)
6. **大型 AST 内存**: 300KB+ 代码的 AST 可能占用大量内存，考虑流式处理
