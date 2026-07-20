---
name: ast-deobfuscation
description: 使用 Babel AST 对 JavaScript 做分层、可回退的定向反混淆。7步流程 + 三层自动架构（通用→检测→适配）+ 8站点适配器。支持 sojson、obfuscator.io、reese84、顶象、极验4、同花顺、网易易盾、小红书等。
author: 7452323 (converted from Private Gist)
version: "1.0.0"
tags:
  - ast
  - babel
  - deobfuscation
  - javascript
  - reverse-engineering
  - control-flow-flattening
  - string-decryption
---

# AST 反混淆技能

工具链: `@babel/parser` + `@babel/traverse` + `@babel/generator` + `@babel/types`

## 技能协作链

| 技能 | 职责 |
|------|------|
| ast-deobfuscation（本技能） | AST 静态反混淆：字符串解密、常量折叠、控制流还原、死代码删除 |
| env-patch | 运行时环境补丁，沙箱执行 |
| find-crypto-entry | 定位加密算法入口 |
| algorithm-reverse | 逆向加密算法实现 |
| webpack-unpack | Webpack bundle 拆包 | | | |
| webcrack (外部) | 全自动 obfuscator.io 反混淆 + unminify + transpile reverse + bundle unpack | [对比参考](references/webcrack-comparison.md) | 管道替代: webcrack 做粗加工，本技能做精加工 |

典型协作链: `ast-deobfuscation → find-crypto-entry → algorithm-reverse`

## 三层自动架构

### 第1层：通用变换层（所有输入必经）
- 结构标准化（逗号表达式拆分、方括号转点号）
- 常量折叠与布尔值还原
- Proxy 函数与对象字典内联
- 虚假分支清理
- 死代码移除
- **字符串 RC4/Base64 解码**（jsjiami v6/v7 会用 RC4 和 Base64 编码字符串数组，需要在 Step 1 字符串解密前先试解码）

### 第2层：混淆检测层
自动检测混淆家族并加载对应适配器：
- sojson v6/v7（jsjiami v6/v7）
- obfuscator.io
- awsc（阿里云混淆/fireyejs 225）
- jjencode
- jsconfuser（npm js-confuser）
- 通用 eval/packer
- **aaencode**（颜文字编码，检测特征: `ﾟωﾟﾉ` / `ﾟΘﾟ` / `o^_^o`）
- **jsfuck**（仅 `[]()!+` 6字符编码，检测特征: 代码全是 `[]+()!` 组成）
- **JS/HTML 混合加密**（检测特征: 输出中混有 HTML 标签字符串）

### 第3层：站点适配层
针对特定站点的定制化适配器：
- reese84
- 顶象
- 极验4
- 同花顺
- 网易易盾
- 小红书

## 7步流程

```
Step 0: 混淆检测 + 评估
Step 1: 字符串解密（沙箱执行解密函数）
Step 2: 常量折叠
Step 3: 控制流平坦化还原
Step 4: 死代码删除
Step 5: 变量重命名（可选）
Step 6: 代码格式化输出
Step 7: 语义反压缩（可选，还原 Babel 编译和 minify 痕迹）
```

每步结果自动验证，出错时回退到上一步输出，保证至少返回格式化代码。

### Step 7 扩展：语义反压缩（Semantic Unminify）

脱混淆后的代码可能仍是压缩过的（一行代码、Babel 编译残留）。使用 webcrack 的 22 种语义 transform 进一步提升可读性：

| 变换 | 作用 | 示例 |
|------|------|------|
| **blockStatements** | 单行 if/else 补括号 | `if(x) foo()` → `if(x) { foo() }` |
| **computedProperties** | 方括号转点号 | `obj['key']` → `obj.key` |
| **forToWhile** | for 转 while | `for(;i<0;){}` → `while(i<0){}` |
| **invertBooleanLogic** | 德摩根定律展开 | `!(a&&b)` → `!a\|\|!b` |
| **mergeStrings** | 相邻字符串合并 | `"a"+"b"` → `"ab"` |
| **numberExpressions** | 数字表达式求值 | `0x1f` → `31` |
| **rawLiterals** | 常量模板字面量转字符串 | `` `hello` `` → `"hello"` |
| **removeDoubleNot** | 去双重否定 | `!!x` → `x` |
| **unminifyBooleans** | 解压缩布尔值 | `!0` → `true`, `!1` → `false` |
| **yoda** | Yoda 条件反转 | `(0 === x)` → `(x === 0)` |
| **typeofUndefined** | typeof undefined 展开 | — |
| **voidToUndefined** | void 0 还原 | `void 0` → `undefined` |
| **transpileReversal** | Babel 编译逆转（7种） | `a.b` → `a?.b` / `a\|` → `a\|\|=b` / 模板字面量 |

**实现方式**：作为 post-processor 调用 webcrack CLI（跳过 deobfuscate/unpack stage）：
```bash
npx webcrack deobfuscated.js --no-deobfuscate --no-unpack 2>/dev/null
```

---

## jsjiami.com 专项破解指南

jsjiami.com（原 sojson）是国内最主流的 JS 加密服务，版本从 V5 到 V7。以下是对各版本的破解策略。

### 版本识别

| 特征 | 版本 |
|------|------|
| 代码硬编码 `jsjiami.com.v5` | V5（旧版，易解） |
| 代码硬编码 `jsjiami.com.v6` + 无多态性 | V6 |
| 代码硬编码 `jsjiami.com.v7` + 每次加密结果不同 | V7（多态性） |
| 无版本标识，仅含 eval+变量名缩短 | 混淆加密（L1-L2） |
| 含域名检测 + 反调试注入 | V6/V7 高级配置 |

### V6 破解要点

1. **字符串解密**：V6 使用 RC4 或 Base64 编码字符串数组。第一步：定位 `stringArray` 和 `stringArrayDecoder`，沙箱执行解码函数获取所有明文字符串
2. **控制流平坦化**：`switch-case` 结构，通过 `ast-deobfuscation` Step 3 还原
3. **花指令**：提取的伪代码片段，通过 Step 4 死代码删除
4. **反调试**：debugger 注入 + console.log 阻断，通过 `anti-debug` 绕过
5. **域名锁定**：检测 `window.location.hostname`，匹配失败则卡死。绕过方法：
   - `env-patch` 中 mock `window.location.hostname`
   - 或者在运行时提前注入合法域名

### V7 多态性破解要点

V7 每次加密产生不同的输出结构，不能依赖固定签名匹配。策略：

1. **运行时特征检测**（而非文本签名）：
   - 检测自执行函数包装模式
   - 检测字符串数组 + 解码函数模式
   - 检测 switch-case 控制流
   - 检测 `Function.prototype.apply/bind` 调用链

2. **多态字符串解码**：
   - 定位 `stringArray` 定义（可能是数组字面量或动态拼接）
   - 定位 `stringArrayDecoder`（可能是 `Function` 或 `eval` 构造）
   - 沙箱执行解码函数，捕获返回值

3. **多态花指令**：
   - 每次注入的伪代码不同，但共享相同的外部函数调用模式
   - 通过 Babel AST 的 `isSideEffectFree` 判断删除

4. **反调试+域名锁定**：与 V6 相同，但随机分布在不同的 switch-case 分支中

### jsjiami 加密全过程还原管线

```
1. 检测 → 识别为 jsjiami v6/v7
2. 域名锁绕过 → 运行时 mock location.hostname
3. 反调试绕过 → Hook Function/eval/constructor（anti-debug 三合一方案）
4. Step 1: 字符串解码（RC4 或 Base64）
5. Step 2: 常量折叠
6. Step 3: 控制流平坦化还原
7. Step 4: 死代码删除
8. Step 5: 变量重命名
9. Step 6: 格式化输出
10. 验证 → 对比还原前后功能一致性
```

### AAEncode / JSFuck 专项解码

遇到 aaencode（颜文字风格）或 jsfuck（仅 `[]()!+`）时：

```python
# aaencode 解码：eval 或 console.log 即可出原文
decoded = eval("aaencode_string")  # 浏览器中执行

# 或使用已有库
# npm install aadecode
# npm install jsfuck

# jsfuck 解码
decoded = eval(jsfuck_string)
# 或使用 jsfuck 库的反向操作
```

### 域名锁定绕过

jsjiami 的域名锁定逻辑通常如下：

```javascript
// 典型模式
var _0x... = function() {
    var host = window.location.hostname;
    if (host !== 'allowed.domain.com') {
        while(1) { debugger; }  // 浏览器卡死
    }
};
```

绕过方法（按优先级）：
1. **env-patch mock**：在 Node.js 补环境中设置 `global.window = { location: { hostname: 'allowed.domain.com' } }`
2. **CDP 注入**：在浏览器加载前注入脚本覆盖 `window.location.hostname`
3. **源码 Patch**：直接替换硬编码的域名检测条件为 `true`

### V7 IIFE 字符串表重排 — vm.createContext 沙箱提取

**关键坑**：jsjiami V7 的 IIFE（自执行函数）会在运行时**重排字符串表**（`shift()`/`push()` 操作）。直接从源码提取的字符串表元素顺序是**错误**的——索引不指向你想要的字符串。必须先让 IIFE 在沙箱中跑完，再用解码器获取正确的字符串。

**正确的 vm 沙箱方案**（Node.js `vm.createContext`）：

```javascript
const vm = require('vm');
const code = fs.readFileSync('diy.js', 'utf8');

// 在源码末尾追加调试代码（必须和源码在同一个 try 块内，否则 const 丢失作用域）
const codeWithDebug = code + `
try {
  var __r = [];
  __r.push(['fetch', _0x4ae2fe(0x13b, 'ZEC#')]);
  __r.push(['reveal', _0x4ae2fe(0xeb, '[(@B')]);
  console.log(JSON.stringify(__r));
} catch(e) { console.log('ERR:' + e.message); }
`;

// 全量浏览器 mock (Swal/fetch/layui/ClipboardJS 等 — 缺少可能导致 throw 阻止 IIFE)
const mock = {
  document: {
    addEventListener: () => {},
    getElementById: () => null,
    querySelectorAll: () => [],
    createElement: () => ({
      style: {}, className: '', innerHTML: '',
      appendChild: () => {}, addEventListener: () => {},
      getAttribute: () => null, querySelector: () => null
    }),
    documentElement: { style: {} },
    body: { appendChild: () => {} }
  },
  window: {},
  navigator: { clipboard: null, userAgent: 'Mozilla/5.0' },
  Swal: { fire: () => ({ then: (cb) => { try{cb({isConfirmed:true})}catch(e){}; return {catch:()=>{}}; }}) },
  fetch: () => Promise.resolve({ json: () => Promise.resolve([]) }),
  console: console,
  setTimeout: (fn) => { try{fn()}catch(e){} },
  clearTimeout: () => {},
  ClipboardJS: function() {},
  layui: { use: (deps, cb) => { try{cb({layer: {msg:()=>{}}})}catch(e){} } }
};
mock.window = mock;

const ctx = vm.createContext(mock);
try { vm.runInContext(codeWithDebug, ctx); }
catch(e) { /* expected — main code throws on DOM, but decode succeeded */ }
```

**核心要点**：
1. **单 try 块**：`const _0x4ae2fe = _0x5671;` 是块级作用域。如果把原代码和调试代码分开两个 try，调试代码拿不到 `_0x4ae2fe`
2. **IIFE 必须在 decode 前运行**：否则字符串表没被重排，解码出来是乱码
3. **mock 一切**：`document`, `navigator`, `Swal`, `fetch`, `setTimeout`, `ClipboardJS`, `layui` — 缺任何一个都可能让主代码 throw 阻止 IIFE 执行
4. **`_0x4ae2fe` 就是 `_0x5671`**：在源码顶部有 `const _0x4ae2fe = _0x5671;`，这是最主要的下层引用名
5. **`_0x5671(index, key)` 的 index 需减 0x98**：实际函数内部会做 `index = arguments[0] - 0x98`，所以 decode 时的 index 和源码中看到的 hex 值一致即可（函数内部会自动减偏移）

### 参考资源

- jsjiami 官网: https://www.jsjiami.com/
- 博客文章: https://www.jsjiami.com/article/
- Fuzz Crypto 工具（jsjiami 推荐）: https://github.com/0xsdeo/Fuzz_Crypto_Algorithms
- vm.createContext 沙箱示例: [references/jsjiami-v7-vm-decoder.md](references/jsjiami-v7-vm-decoder.md)
- webcrack 对比参考: [references/webcrack-comparison.md](references/webcrack-comparison.md) — webcrack 与本技能的架构差异、字符串解码对比、控制流还原方式对比、集成建议
- 沙箱执行 hook 技术: [references/sandbox-execution-hooking.md](references/sandbox-execution-hooking.md) — Function/eval hook 反混淆技术、多 pass 架构、`(0, origEval)` 坑与修复、检测优先级链
