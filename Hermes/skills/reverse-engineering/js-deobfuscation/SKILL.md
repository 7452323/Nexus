---
name: js-deobfuscation
category: reverse-engineering
description: >-
  Merged skill combining: ast-deobfuscation, deobfuscator, code-obfuscation-deobfuscation, jsjiami-xor-filename-reverse.
version: "1.0"
sources:
  - ast-deobfuscation
  - deobfuscator
  - code-obfuscation-deobfuscation
  - jsjiami-xor-filename-reverse
tags: [reverse-engineering, merged]
---

# js-deobfuscation

> **Merged from**: ast-deobfuscation, deobfuscator, code-obfuscation-deobfuscation, jsjiami-xor-filename-reverse
> **Source count**: 4

---

## Table of Contents

1. [ast-deobfuscation](#ast-deobfuscation)
2. [deobfuscator](#deobfuscator)
3. [code-obfuscation-deobfuscation](#code-obfuscation-deobfuscation)
4. [jsjiami-xor-filename-reverse](#jsjiami-xor-filename-reverse)

---

## ast-deobfuscation

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

---

## deobfuscator

# deobfuscator — 代码反混淆解密技能

## ⚠️ JSC 环境注意事项（Scripting App / iOS JavaScriptCore）

Scripting App 运行在 **JavaScriptCore（JSC）** 上，与 Node.js 的 V8 引擎存在**关键差异**，直接影响 jsjiami 等二进制级混淆的解密：

### 问题 1：String.charCodeAt 在 0x80-0xFF 范围行为不同

jsjiami v7 原版使用 `String.charCodeAt()` 读取"字节"。V8 将字符串按 Latin-1 存储，`charCodeAt` 对 0x00-0xFF 直接返回字节值。JSC 对包含 >0x7F 字符的字符串使用 UTF-16 表示，`charCodeAt` 返回 Unicode 码点而非原始字节。

**后果**：jsjiami 的 RC4 解密在 JSC 上输出错误字节。

### 问题 2：NaN 传播路径

jsjiami 的 KSA（密钥调度算法）依赖对空字符 `charCodeAt` 返回 `NaN`，然后参与位运算：
- V8: `(NaN & 0xFF)` → 0
- JSC: `(NaN & 0xFF)` → 某些版本返回 0，某些返回 NaN → 整条 RC4 链偏移

### 问题 3：Function.prototype.toString 差异

jsjiami v7 用 `Function.prototype.toString()` 做环境指纹检测。JSC 输出的格式与 V8 不同：
- V8: `function anonymous() { ... }`
- JSC: `function () { ... }`（无 `anonymous`）

这会导致某些 jsjiami 变体直接在 Scripting 中拒绝执行。

### JSC 兼容的 RC4 实现

**解决方案：全部走 Uint8Array，不碰 String.charCodeAt**

参见 `references/jsc-rc4.md` 中的完整实现——包括 `rc4DecryptJSC()`、`hexToBytes()`、`bytesToUtf8()`（用 `decodeURIComponent + %XX` 绕过编码问题）。

### 环境检测绕过速查

| 检测方式 | JSC 的问题 | 绕过方法 |
|---------|-----------|---------|
| `Function.toString().indexOf('native')` | JSC 输出含 'native' | 替换 toString 返回 |
| `typeof window === 'undefined'` | Scripting 无 window | `globalThis.window = {}` |
| `location.hostname` | 可能为 undefined | Mock 为 localhost |
| `navigator.userAgent` | Scripting 无 navigator | Mock navigator 对象 |
| `document.createElement` | Scripting 无 DOM | 提供空 mock |

⚠️ **每次在 Scripting 中运行反混淆工具时，优先考虑 JSC 兼容性**。非必要不使用 `String.charCodeAt` 操作字节数据。

## 能处理什么

|混淆类型|特征|解密方法|来源|
|---|---|---|---|---|
|**jsjiami v6 / sojson**|`jsjiami.com` `sojson.com` 水印, `_0x`变量, 前3句为签名+预处理+解密函数|隔离沙箱执行解密函数, AST回填字符串|decode_action/echo094|
|**jsjiami v7**|首行 `_0xodg='jsjiami.com.v7'`; 验证 IIFE + 自修改解密函数; `_0x5671(idx, key)` 格式; `idx - 0x98` 偏移; 自定义 Base64(小写优先) + RC4|沙箱执行 `_0x10f3` 获取字符串表, 或 **VM 沙箱执行全代码**（mock 浏览器全局，追加 debug 代码调用 decoder）→ 详见 [jsjiami-v7.md](references/jsjiami-v7.md)|decode_action/echo094|
|**obfuscator.io**|大量`_0x` + 自执行数组 + 控制流扁平化|数组展开 → 常量折叠 → 控制流还原 → 死代码删除|decode_action/v_jstools|
|**awsc (阿里云混淆/fireyejs)**|阿里云CDN默认混淆; 特征`_0x` + fireyejs 225算法 BX-UA 参数; **Conditional→If** 转换、逻辑运算符`&&`→If、**void 0**移除|专用 awsc.js 插件: RemoveVoid → LintConditionalAssign → LintConditionalIf → LintLogicalIf → 配合 obfuscator 方案处理|decode_action|
|**jjencode**|以 `$=~[];$={};$$=$[(!![]+[])[...]]` 开头的6段式自编码; 全局变量名 `$` `$$` `_$`; 特征: 变量来自 `~[]` `!![]` 等类型强制转换|专用 jjencode.js 插件: 检测6段格式 → 提取第5段目标代码 → 构造 `变量.$(...)` 调用链 → eval 还原|decode_action|
|**jsconfuser**|特征`smEcV`; npm `js-confuser` 混淆器; 包含: anti-tooling, control-flow flattening, string compression/concealing, global concealing, opaque predicates, stack, duplicate literals|专用 jsconfuser.js 插件: 按序执行 9 个 sub-visitor 还原 → 详见下方 [jsconfuser 反混淆模块](#jsconfuser-反混淆模块)|decode_action|
|**eval(function包) / eval unpack**|`eval(function(a,b,c,...){...}(code))`; 外层 eval 包裹自执行函数; 特征: `eval(function(`|自动解包: parse → 识别`CallExpression(callee=eval, args=[CallExpression])` → 提取内层 CallExpression → eval 执行获取原文|decode_action|
|**Python 链式解压**|zlib/bz2/lzma/gzip + base64 多层嵌套; Python `exec(compressed)`; 特征: `base64.b64decode(zlib.decompress(`|递归 auto-detect: base64 decode → gzip→bz2→zlib→lzma 逐个尝试 → 直到不可再解或不再包含 `exec(`|decode_action|
|**jsjiami v7**|首行 `_0xodg='jsjiami.com.v7'`; 验证 IIFE + 自修改解密函数; `_0x5671(idx, key)` 格式; `idx - 0x98` 偏移; 自定义 Base64(小写优先) + RC4|沙箱执行 `_0x10f3` 获取字符串表, 或 **Node.js VM 沙箱执行全代码**（mock 浏览器全局，追加 debug 代码调用 decoder）→ [VM沙箱执行法](references/jsjiami-v7.md#vm-沙箱执行法推荐比手动解码可靠)|decode_action, [references/jsjiami-v7.md](references/jsjiami-v7.md)|
|**obfuscator.io**|大量`_0x` + 自执行数组 + 控制流扁平化|数组展开 → 常量折叠 → 控制流还原 → 死代码删除|decode_action/v_jstools|
|**awsc (阿里云混淆)**|阿里云CDN默认混淆, 特征`_0x`|同obfuscator方案处理|decode_action|
|**jjencode**|以 `$=~[];$={...}` 开头的自编码|jjdecode专用恢复|decode_action|
|**jsconfuser**|特征`smEcV`|专用反混淆插件|decode_action|
|**Dean Edwards Packer**|`eval(function(p,a,c,k,e,d)`|自动解包|经典|
||**AAEncode (顔文字混淆)**|颜文字变量 `ﾟωﾟﾉ`, `o^_^o`, `ﾟΘﾟ`; Unicode 码点算术拼字符串; 末尾 `(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] ( <payload> ) (ﾟΘﾟ)) ('_');` — **双层嵌套**, 外层内层都调 Function()|保留定义区 + 提取 payload → 构建 `defs + (ﾟДﾟ)['_'](payload)(ﾟΘﾟ)` 只解码不执行。详见下方 [AAEncode 实战解码](#aaencode-实战解码针对-surgeqx-脚本), 配套脚本 `scripts/decode-aa-file.cjs`|实测拆解, scripts/decode-aa-file.cjs|
|**JSFuck**|仅由 `[]()!+`|解释器还原|经典|
|**eval/atob嵌套**|多层 `eval(atob(...))`|递归eval展开|经典|
|**Python压缩**|zlib/bz2/lzma/gzip + base64多层嵌套|递归解压直到不可再解|decode_action|
|**Google Closure**|`a.b=c`式重命名|需源码映射, 部分还原|经典|
|**ProGuard (Android)**|`a.a.a()`|映射文件反混淆|经典|

## 企业软件密码解密

来自 DecryptTools 项目（wafinfo/DecryptTools），专门针对国产企业软件的配置密码解密：

|软件|加密类型|解密方法|
|---|---|---|
|万户OA|自定义|工具内集成|
|用友NC|AES|工具内集成|
|金蝶EAS|自定义|工具内集成|
|致远OA|AES/GZIP|字符串解密|
|蓝凌OA|SM4/DES|SM4解密|
|帆软报表|自定义|数据库密码解密|
|海康威视|AES|设备配置解密|
|Navicat|AES-128-CBC|密码解密|
|FinalShell|AES|连接配置解密|
|WebLogic|AES|数据库密码解密|
|Druid|AES|数据库密码解密|
|Spring (Jasypt)|PBE/AES|配置解密|
|H3C CAS|自定义|配置文件解密|

## 混淆类型快速识别

从实战（Yu9191/Rewrite + Mike-offers 批量扫描 ~24 个混淆脚本）总结的快速识别表：

| 头 200 字符特征 | 类型 | 可完全解密？ |
|------|------|--------|
| `ﾟωﾟﾉ` / `ﾟДﾟ` | AAEncode | ✅ 完全可恢复 |
| `sojson=~[];/*sojson.com*/` | sojson v4 | ✅ 完全可恢复 |
| `function php() { return 'jsjiami.com.v6'; }` | jsjiami v6 | ❌ 仅行为分析 |
| `function php() { return 'jsjiami.com.v7'; }` | jsjiami v7 | ❌ 仅行为分析 |
| `__webpack_require__` | Webpack | ✅ 可模块提取 |
| `__webpack_require__` + `sojson` 标记 | Webpack + sojson v4 混合 | ✅ 可逐层还原 |

> 在真实仓库中，jsjiami v6/v7 占总混淆脚本约 80%，AAEncode 和 sojson 占约 15%。

## 工作流程

```
1. 检测混淆类型（识别头部 200 字符特征 → 见上表）
   ↓
2. 识别加密函数（sojson:前3句 obfuscator:自执行数组 packer:正则特征）
   ↓
3. 沙箱执行解密函数（用 isolated-vm 安全执行，获取解密映射表）
   ↓
4. AST 回填（将 _0x1234('0x1') 替换为真实字符串）
   ↓
5. AST 净化
   ├─ 常量折叠（calculate-constant-exp）
   ├─ 控制流平坦化还原（parse-control-flow-storage）
   ├─ If分支修剪（prune-if-branch）
   ├─ 死变量删除（delete-unused-var）
   ├─ 序列表达式拆分（split-sequence）
   ├─ 合并对象字面量（merge-object）
   └─ 代码格式化
   ↓
6. 输出可读代码
```

|**kuizuo/js-deobfuscator**|自动化JS反混淆|Babel AST多层变换，Web端+CLI+API|`npm i @kuizuo/js-deobfuscator`|
|**js-beautify**|代码美化|格式化输出|`npm i js-beautify`|

## jsconfuser 反混淆模块

来自 `smallfawn/decode_action` 的 jsconfuser 插件，按固定顺序执行 9 个 sub-visitor 逐一还原 js-confuser 各项保护：

```javascript
1. AntiTooling          — 反调试/反工具检测移除
2. Minify               — 箭头函数反压缩（deMinifyArrow）
3. DuplicateLiterals    — 重复字面量合并
4. Stack                — 栈帧还原（两次: 先精简, 再通用）
5. StringCompression    — 压缩字符串解压
6. StringConcealing     — 隐藏字符串暴露
7. StringSplitting      — 分裂字符串合并（常量折叠）
8. OpaquePredicates     — 不透明谓词折叠 → 常量折叠 → if分支修剪
9. GlobalConcealing     — 全局对象隐藏还原
10. ControlFlowFlatten  — 控制流平坦化还原（无状态版）→ 常量折叠
```

关键工具：`@babel/parser` + `@babel/traverse` + `isolated-vm` 沙箱执行解码函数。

## Python 链式解压代码（自动检测所有压缩格式）

```python
import base64, bz2, zlib, lzma, gzip

def try_decompress(data):
    for fn in [gzip.decompress, bz2.decompress, zlib.decompress, lzma.decompress]:
        try: return fn(data)
        except: pass
    return data

def try_decode_base64(data):
    try: return base64.b64decode(data)
    except: return data

def decrypt_nested(data):
    while True:
        if isinstance(data, str):
            data = try_decode_base64(data.encode())
        data = try_decompress(data)
        if b"exec(" not in data:
            break
        # extract base64.b64decode('...') string
        import re
        m = re.search(r"base64\.b64decode\('([^']+)'\)", data.decode(errors='replace'))
        if m: data = m.group(1)
        else: break
    return data
```

## AAEncode 实战解密流程（针对 Surge/QX 脚本）

Yu9191/Rewrite 等多个仓库存在 AAEncode（颜文字混淆）加密的 Surge/QX 脚本，结构统一：

### 结构识别

```
/* Surge/QX 头部注释（rewrite / MITM 配置...） */
ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ ['_']; o=(ﾟｰﾟ)  =_=3; ...
...
(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] ( 大量颜文字字符 ) (ﾟΘﾟ)) ('_');
```

核心特征：
- 头部有 `/* ... */` 注释块，内含 `[rewrite_local]` / `[task_local]` / `[MITM]` 配置
- 下方以 `ﾟωﾟﾉ=` 开头定义颜文字变量
- 末尾以 `(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] ( <payload> ) (ﾟΘﾟ)) ('_');` 结束  
- **双层嵌套**：外层 `(ﾟДﾟ) ['_'](...)('_')` 是 Function 构造函数调用，内层 `(ﾟДﾟ) ['_'](payload)(0)` 解码并执行

### 解码方法（Node.js CommonJS, 非 strict 模式）

AAEncode 结构：定义区 + 执行区。

- **定义区**: 自 `ﾟωﾟﾉ` 到最后一个 `(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] (` 之前。设置 `ﾟДﾟ`, `ﾟΘﾟ`, `ﾟεﾟ` 等变量到 `globalThis`。
- **执行区**: `(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] ( <payload> ) (ﾟΘﾟ)) ('_');`
  - 等价于 `Function( Function(<payload>)(0) )()`
  - 内层 `Function(<payload>)(0)` = 解码 payload 返回源码字符串
  - 外层 `Function(源码)()` = 执行解码后的代码

**正确解码方法**：保留定义区，只调用内层解码（不执行外层）：

```javascript
// 1. 分离定义区 + payload
const raw = fs.readFileSync('script.js', 'utf8');
const aaStart = raw.indexOf('ﾟωﾟﾉ');            // 跳过头部注释
const body = raw.slice(aaStart).trim();

const outerStart = "(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] (";
const outerEnd   = ") (ﾟΘﾟ)) ('_');";

const lastIdx = body.lastIndexOf(outerStart);
const defs = body.slice(0, lastIdx);                              // 定义区
const payload = body.slice(lastIdx + outerStart.length)
                     .slice(0, body.slice(lastIdx + outerStart.length).lastIndexOf(outerEnd));

// 2. 构建解码脚本（定义区 + 内层解码 + console.log）
const decodeScript = defs + '\n' +
  'const __r = (ﾟДﾟ) [\'_\'](' + payload + ')(ﾟΘﾟ);\n' +
  'console.log(__r);\n';

// 3. 保存到 tmp 文件并运行（必须 CommonJS, 非 strict 模式）
const fs = require('fs');
const tmp = '/tmp/_aa_decode_' + Date.now() + '.js';
fs.writeFileSync(tmp, decodeScript, 'utf8');
const out = require('child_process')
  .execSync('node ' + tmp, { encoding: 'utf8', maxBuffer: 10*1024*1024 });
fs.unlinkSync(tmp);
console.log(out);  // 解码后的源码
```

⚠️ **关键陷阱**：
- 必须用 `.cjs` 或 `require()`（CommonJS），ESM 的 strict 模式不允许未声明的颜文字变量
- 定义区变量通过无 `var/let/const` 赋值成为 `globalThis` 属性，Function() 构造函数内可访问
- `(ﾟΘﾟ)` = `0` — 必须传 0 参数到内部函数，否则解码逻辑不执行
- 解码后代码很小（300-1000 chars），相比 AAEncode payload（20-65KB）缩小几十倍
- 解码结果是标准 Surge/QX body 修改逻辑（`$response.body` / `$request.url` / `$done()` / `$notification.post()`）

**便捷脚本**：`scripts/decode-aa-file.cjs` — 一键解码：`node .hermes/skills/reverse-engineering/deobfuscator/scripts/decode-aa-file.cjs <input.js> [output.js]`

### 解码后代码特点

解码后的 Surge/QX 脚本通常：
- 判断 `$request.url` 匹配不同 API 端点
- 修改 `$response.body` 中的 JSON（替换 `false`→`true`, 日期→`2099-09-09` 等）
- 调用 `$notification.post()` 或 `$notify()` 发通知
- 结尾 `$done({ body })` 或 `$done({ body: JSON.stringify(obj) })`
- **无二次混淆** — 直接可读的业务逻辑

### 已发现的 AAEncode 实例（Yu9191/Rewrite）

| 文件 | AAEncode大小 | 解码后大小 | 功能 |
|------|-------------|-----------|------|
| aimirror.js | ~65KB | ~1KB | AI Mirror VIP解锁，多端点body修改 |
| aymy.js | ~23KB | ~0.6KB | 直接mock VIP对象（含硬编码JWT token） |
| rwmm.js | ~22KB | ~0.3KB | 修改data字段的vip到期时间 |

## sojson v4 实战解码（针对 Surge/QX 脚本）

sojson v4 的代码自包含——不依赖外部库，所有变量在混淆内部定义。解码策略与 AAEncode 相反：**不修改代码，提供 Mock 环境让其完整执行**，然后捕获 `$done()` 的输出。

### 结构

```
/* 头部注释（rewrite / MITM 配置...） */
sojson=~[];/*sojson.com*/
sojson={___:++sojson,/*sojson.com*/$$$$:(![]+"")[sojson],...};
// ... 数百行字符索引运算构建 Function 引用和 payload 字符串 ...
(sojson.___)[sojson.$_][sojson.$_]  →  Function 构造函数
sojson.$(sojson.$(sojson.$$+"\"..."))  →  解码并执行
```

### 解码方法（Node.js Mock 环境执行）

sojson v4 通过自引用变量映射构建出 `Function` 构造函数，然后调用 `sojson.$(decodedPayload)` 解码执行。**关键点：不要在代码层面拦截 `Function`——sojson 内部已经捕获了原始的 Function 引用，替换 `globalThis.Function` 无效。**

正确方法：提供 Surge 全局变量 Mock，让解码后的脚本自然执行：

```javascript
const vm = require('vm');
const fs = require('fs');

function decodeSojson(inputFile) {
  let code = fs.readFileSync(inputFile, 'utf8');
  // 剔除头部注释
  code = code.replace(/^\/\*[\s\S]*?\*\/[\s\n]*/, '');

  let capturedDone = null;

  const sandbox = {
    console: console,
    setTimeout: fn => fn(),  // sojson 可能用它做延时
    $response: { body: '{"is_vip":false}', status: 200, headers: {} },
    $request: { url: 'https://example.com/api/v1/user/profile' },
    $notification: { post: (t, s, b) => {} },
    $done: (args) => { capturedDone = args; },
  };

  const ctx = vm.createContext(sandbox);
  vm.runInContext(code, ctx, { timeout: 10000 });

  return capturedDone;
}

const result = decodeSojson('Jieluoxuan.js');
// result = { body: '{"is_vip":true}' }
```

⚠️ **关键陷阱**：
- sojson 内部用变量 `sojson.$` 指向 `Function`，是自捕获引用，`globalThis.Function` 替换对其无效
- 不解码直接读 `sojson.$$`（payload 字符串）会得到编码版本——必须先执行前 3 句才生成真实 payload
- 某些 sojson 变体使用 `setTimeout` 延时执行——在 sandbox 中提供 `setTimeout: fn => fn()` 解决
- `$done()` 参数就是解码后的执行结果——不需要额外提取中间状态
- 压缩比极大：例如 Jieluoxuan.js 27KB → 仅 31 字节功能代码 `$done({ body: '{"is_vip":true}' })`

### 与 AAEncode 的对比

| 维度 | AAEncode | sojson v4 |
|------|---------|-----------|
| 编码方式 | 颜文字字符拼接 | 字符索引运算 + 自引用变量 |
| 头部特征 | `ﾟωﾟﾉ` | `sojson=~[];/*sojson.com*/` |
| 解码策略 | 剥离外层，仅执行内层 | 提供 Mock 环境完整执行 |
| Function 引用 | 可通过替换 `globalThis.Function` 拦截 | 自捕获原始引用，无法替换 |
| 函数返回值 | 需要调 `(ﾟДﾟ)['_'](...)(0)` 显式解码 | 直接执行，捕获 `$done()` 即可 |

## 推荐工具链

|工具|用途|安装|
|---|---|---|
|@babel/parser|JS→AST解析|`npm i @babel/parser`|
|@babel/traverse|AST遍历|`npm i @babel/traverse`|
|@babel/generator|AST→JS|`npm i @babel/generator`|
|isolated-vm|安全沙箱执行解密函数（比 vm2 更安全，支持 5s 超时隔离）|`npm i isolated-vm`|
|js-beautify|代码格式化|`npm i js-beautify`|

## decode_action 自动化方案（推荐）

利用 GitHub Actions 自动解密：

1. fork `smallfawn/decode_action`
2. 把待解密代码放入 `input.js`（JS）或 `input.py`（Python）
3. 手动触发 Action → 等待 60s
4. 解密结果在 `output.js` / `output.py`

**支持的 Python 压缩格式：** zlib, bz2, lzma, gzip（autodetect 链式解压）
**支持的 JS 混淆（按检测顺序）：**

| # | 插件 | 检测策略 |
|---|------|----------|
| 1 | obfuscator | Babel parse + 特征检测（自执行数组 + 控制流） |
| 2 | sojsonv7 | 前3句分割 → 自修改函数检测 → RC4 + 自定义 Base64 |
| 3 | sojson | 前3句分割 → 沙箱执行解密函数 |
| 4 | jsconfuser | 特征 `smEcV` + 9 步 AST transform |
| 5 | awsc | 阿里云混淆 → Conditional→If 转换 |
| 6 | jjencode | 6段分号分割检测 |
| 7 | common | 通用 AST 净化（死代码 + 常量折叠） |

**项目核心依赖：** `@babel/parser`, `@babel/traverse`, `@babel/generator`, `@babel/types`, `isolated-vm`, `crypto-js`, `base64url`

**eval(unpack) 辅助插件：** 自动检测 `eval(function(){...}())` 格式，提取内层 CallExpression 并 eval 执行获取原文。

## AST 反混淆核心原理

### 沙箱执行解密函数

**方案A：isolated-vm（推荐，decode_action 使用）**
```javascript
const ivm = require('isolated-vm');
const isolate = new ivm.Isolate({ memoryLimit: 128 });
const context = isolate.createContextSync();

function safeEval(code) {
  return context.evalSync(String(code), { timeout: 5000 });
}
```
优势：每个 isolate 有独立堆 + 内存限制 + 超时控制，比 vm2 更安全，适合执行不可信解密代码。

**方案B：vm.createContext（Node.js 内置）**
```javascript
const vm = require('vm');
const ctx = vm.createContext({ console, Buffer, setTimeout, ... });
vm.runInContext(code, ctx, { timeout: 10000 });
```
优势：无需额外依赖，适合简单场景。

## 常见混淆模式识别

|特征|混淆类型|
|---|---|
|`jsjiami.com` / `sojson.com`|jsjiami|
|大量 `_0x[0-9a-f]{4,6}` 变量|obfuscator.io / jsjiami|
|`function(p,a,c,k,e,d)`|Packer|

---
*[Content truncated: 747 lines total]*
---

  const origEval = globalThis.eval

  try {
    // 钩住 Function 构造函数
    globalThis.Function = function(...args) {
      hadFunctionCall = true
      const bodyIdx = args.length - 1
      if (args[bodyIdx] && typeof args[bodyIdx] === 'string'
          && args[bodyIdx].length > capturedCode.length) {
        capturedCode = args[bodyIdx]
      }
      return function() {}
    }

    // 钩住 eval（只记录，不截获外层eval）
    globalThis.eval = function(str) {
      hadEvalCall = true
      if (typeof str === 'string' && str.length > capturedCode.length) {
        capturedCode = str
      }
      return undefined
    }

    // 关键：用 origEval 执行代码，避免钩住的 eval 把自己输入当 payload 捕获
    try {
      const result = (0, origEval)(code)
      if (!capturedCode && typeof result === 'string' && result.length > 5) {
        capturedCode = result
      }
    } catch {}

    // 兜底：用原始 Function 包裹并执行
    if (!capturedCode) {
      try {
        const fn = origFunction(code)
        if (typeof fn === 'function') {
          const fnResult = fn()
          if (typeof fnResult === 'string' && fnResult.length > 0) {
            capturedCode = fnResult
          }
        }
      } catch {}
    }

    return { captured: capturedCode, hadFunctionCall, hadEvalCall }
  } finally {
    globalThis.Function = origFunction
    globalThis.eval = origEval
  }
}
```

**原理：**
1. 用 `(0, origEval)(code)` 执行混淆代码——origEval 在钩子之前保存，不受 `globalThis.eval` 替换影响
2. 代码内部的 `Function("...")` 或 `eval("...")` 调用触发钩子，捕获 payload
3. 捕获后恢复原始 Function/eval，打包返回

**适用场景：** AAEncode、JJEncode、JSFuck、eval-packed、通用 Function 构造解密

### `(0, origEval)` 关键坑

不要写成 `(0, eval)(code)`！当 `globalThis.eval` 被替换后，`(0, eval)` 解析的是**钩子版本**，钩子会把整个输入代码当作 payload 捕获（因为 eval 钩子截获了 "外层" eval 调用），导致 Function 钩子捕获的内层 payload（更短）被钩子捕获的外层代码（更长）覆盖。

正确做法：在替换 `globalThis.eval` 之前保存 `const origEval = globalThis.eval`，然后用 `(0, origEval)(code)` 执行——函数调用表达式 `(0, origEval)` 直接调用保存的函数引用，不走属性查找，完全绕过被 hook 的版本。

### 多轮自动检测管线

将 executeWithHooks 与自动检测器结合，实现 3～5 轮递归解码直到得到可读代码：

```javascript
function detectType(code) {
  const s = code.replace(/\s/g, '')
  if (code.includes('ﾟωﾟﾉ')) return 'aaencode'
  if (/^[\[\]()!+]+$/.test(s) && s.includes('[]') && s.length > 10) return 'jsfuck'
  if (code.includes('$=~[') || (code.includes('$$') && code.includes('~['))) return 'jjencode'
  if (/eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k/.test(code)) return 'packed'
  if (/var\s+_0x/.test(code) || /\[\'_0x/.test(code)) return 'hexstring'
  if (/eval\s*\(/.test(code)) return 'eval'
  if (/atob\s*\(/.test(code)) return 'base64'
  return 'general'
}

function multiPassDeob(code, maxPasses = 10) {
  let current = code
  const layers = []

  for (let pass = 0; pass < maxPasses; pass++) {
    const processed = preprocess(current)
    if (processed !== current) { layers.push('normalize'); current = processed }

    const type = detectType(current)

    if (type === 'general') {
      const hasDynamic = /\b(?:new Function|Function\s*\(|eval\s*\()/i.test(current)
      if ((hasRealCode(current) || current.length < 10) && !hasDynamic) break
    }

    layers.push(type)
    const result = executeWithHooks(current)

    if (result.captured && result.captured.length > 5) {
      current = result.captured
    } else {
      try { const fn = new Function(current); const r = fn()
        if (typeof r === 'string' && r.length > 5) { current = r; continue }
      } catch {}
      break
    }
    if (current === processed) break
  }
  return { detected: layers[0] || 'general', original: current.trim(), passes: layers.length, layers }
}
```

**工作流：** 检测类型 → dispatch 处理器 → 捕获 payload → 重新检测 → 继续解码 → 直到稳定 → 输出

完整 468 行实现见本技能参考文件 `references/deobfuscate-ts-full.md`。

## 字符串编码层 Python 解码器

通用解码管线（不依赖 Node.js，可在任意环境运行）：

```python
import re, base64, urllib.parse

def decode_layers(code):
    # 1. Hex: \\x68\\x65 → "he"
    code = re.sub(r'(?:\\x[0-9a-fA-F]{2})+', lambda m:
        bytes.fromhex(m.group(0).replace('\\x', '')).decode('latin-1'), code)
    # 2. Unicode: \\u0048 → "H"
    code = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), code)
    # 3. CharCode: String.fromCharCode(72,101) → "He"
    code = re.sub(r'String\.fromCharCode\(([0-9,\s]+)\)', lambda m:
        '"' + ''.join(chr(int(c.strip())) for c in m.group(1).split(',')) + '"', code)
    # 4. Base64: atob("SGVsbG8=") → "Hello"
    code = re.sub(r'atob\([\'\"]([A-Za-z0-9+/=]+)[\'\"]\)', lambda m:
        '"' + base64.b64decode(m.group(1)).decode('utf-8', errors='replace') + '"', code)
    # 5. URI: decodeURIComponent / unescape
    code = re.sub(r'(?:decodeURIComponent|unescape)\([\'\"]([^\'\"]+)[\'\"]\)', lambda m:
        '"' + urllib.parse.unquote(m.group(1)) + '"', code)
    return code
```

## jsjiami 网站信息补充

来自 https://www.jsjiami.com/article/ 官方文章：

| 策略 | 说明 |
|------|------|
| **双层加密** | 先用「JS方法加密」(函数体加密/URL隐藏)，再用「JS最牛加密」(全量混淆) — 两次加密使字符串表不同，增加分析难度 |
| **密钥分散** | A页面获取秘钥 → B页面加工 → C页面使用；存储在 cookie/cache/item 中 |
| **闭包隔离** | 仿 jQuery 的 IIFE + 全局变量赋值模式，缩小作用域减少泄露 |

### jsjiami 版本识别更新

| 特征 | 版本 |
|------|------|
| 含 `jsjiami.com.v5` + `encode_version` + RC4 + 数组左旋（`_0x1250cb` 表 + `_0x2470(idx, key)` 调用） | **V5** — 完全可解密，见 `references/jsjiami-v5-rc4.md` |
| 含 `jsjiami.com.v6` + no-op 桩（`var _0x99dd = _0x99dd || function(){...}`） | V6 基础版 |
| 每次加密输出不同（变量名/字符串表顺序/控制流分支 均变化） | **V7 多态版** |
| 同时含 `setInterval(debugger)` + `location.hostname` 检测 | V6/V7 高级配置 |

### AutoJS 加密特性

jsjiami 的 AutoJS 模式专门调整：
- **PX 平坦系数调整** — 更适合 AutoJS 运行引擎（Rhino），不影响速度
- **禁用控制台反调试** — 自动去掉「禁用控制台调试」和「禁止控制台输出」
- **变量声明提升** — `var mq` 在 if 块内 → 加密可能误判为多个独立变量。应统一在函数顶部声明

### V7 字符串解密特征补充

```
_0x5671 = function(idx, key) {
  idx = idx - 0x98;              // 偏移调整
  var arr = stringArray();       // 获取打乱后的字符串表
  // 自定义 Base64（小写优先）→ RC4 解密
  return decode(arr[idx], key);
};
// 下层引用名：const _0x4ae2fe = _0x5671;
// 调用：_0x4ae2fe(0x13b, 'ZEC#')  → 实际调 _0x5671(0x13b - 0x98, 'ZEC#')
```

**关键坑**：V7 IIFE 会在运行时用 `shift()`/`push()` 重排字符串表。直接读取源码中的数组顺序 = 错误。必须在沙箱中跑完 IIFE 后再调用解码函数。

### 混淆级别对照

| 级别 | jsjiami 商品名 | 特征 | 破解难度 |
|------|---------------|------|---------|
| L1 | 压缩加密 | 仅变量名缩短 | ★ |
| L2 | 混淆加密 | 变量名 + 字符串编码 | ★★ |
| L3 | 最牛加密/高级加密 | 全量混淆+控制流+反调试 | ★★★★ |
| L4 | 混合加密 | L3 + 域名锁定+自卫模式 | ★★★★★ |

## 注意事项

- 只处理你自己拥有或有权反编译的代码
- 遵守开源协议，尊重作者版权
- jsjiami 有反调试（anti-debugger），解包时注意关掉开发者工具
- 部分混淆（jsjiami自卫模式）需要运行时提取解密函数，静态分析可能不够
- jsjiami 官方推荐双层加密方案：先用「JS方法加密」预处理，再用「最牛加密」二次混淆

---

## code-obfuscation-deobfuscation

# Code Obfuscation & Deobfuscation — 代码混淆分析与反混淆

## 混淆类型通用识别

| 混淆类型 | 特征 | 主要平台 |
|----------|------|----------|
| Renaming | 变量/函数名替换为无意义字符 | JS/Python/Java |
| String Encryption | 字符串编码/加密+运行时解密 | JS/Android |
| Control Flow | 代码结构被打乱（flat/Opaque） | JS/Android |
| Data Encoding | 数据编码（Base64/Hex/自定义） | 全平台 |
| Dead Code | 插入无意义代码 | 全平台 |
| Self-Modifying | 代码运行时修改自身 | JS/Native |
| Anti-Tamper | 完整性校验 | Android/Native |
| Virtualization | 自定义VM执行 | JS/Android |

## 反混淆通用流程

1. 识别混淆类型（特征匹配）
2. 字符串解密（优先执行）
3. 常量折叠
4. 死代码移除
5. 控制流还原
6. 命名还原（reverse renaming）
7. 代码格式化

## 各语言工具

| 语言 | 工具 |
|------|------|
| JavaScript | Babel（parser/traverse/generator）、js-beautify、de4js |
| Python | uncompyle6/decompyle3（pyc）、unpyc37 |
| Android | jadx、apktool、dextractor |
| .NET | dnSpy、de4dot |
| Java | procyon、cfr、fernflower |

---

## jsjiami.com 加密对抗全景

jsjiami.com 提供 5 级加密强度，从经典编码到 V7 多态性加密。与反混淆技能的关系：

### 加密层级 vs 反混淆策略

| 级别 | 工具 | 使用的混淆技术 | 反混淆策略 |
|------|------|---------------|-----------|
| L0 | AAEncode/JSFuck/JJEncode | 符号编码 | eval/console.log 解码 |
| L1 | JS压缩加密 | eval包装+变量名缩短 | 通用eval适配器 |
| L2 | JS混淆加密 | 字符串16进制+变量重命名 | hex解码+命名还原 |
| L3 | JS高级加密(V6) | 自执行函数+花指令 | 控制流平坦化还原+死代码删除 |
| L4 | 最牛加密V6 | RC4/Base64+控制流+反调试+域名锁 | 字符串解密+anti-debug+域名mock |
| L5 | 最牛加密V7 | 多态性+抗格式化+Anti-Selenium | 运行时特征检测+anti-tamper |

### jsjiami 版本识别速查

- `jsjiami.com.v5` → 旧版，字符串16进制编码 + 简单控制流
- `jsjiami.com.v6` → RC4/Base64 字符串加密 + 控制流平坦化 + 花指令
- `jsjiami.com.v7` → 多态性（每次加密结果不同）+ 抗格式化 + 反Selenium
- 无版本标识 + eval 包装 → JS压缩加密
- 无版本标识 + charCode 编码 → JS混合加密

### 域名锁定绕过

V6/V7 的域名锁定逻辑会检测 `window.location.hostname`，不匹配时进入死循环卡死浏览器。
绕过：
1. 环境 mock：补环境时覆盖 `location.hostname`
2. CDP 注入：在页面加载前执行脚本覆盖
3. 源码 Patch：AST 中直接删除域名校验条件

---

## jsjiami-xor-filename-reverse

# jsjiami v5/v6 + XOR加密文件名 逆向

针对壁纸/CDN类站点的专项逆向：jsjiami混淆JS + XOR加密资源文件名 + EdgeOne/Cloudflare Pages SPA fallback。

## 识别特征

- JS文件含 `jsjiami.com.v5` 或 `jsjiami.com.v6`
- v5: `_0x2939` 解码器，可eval
- v6: 多层嵌套解码器，eval报错
- API JSON中 `filename` 为Base64密文
- 图片URL `/images/{MD5}.{ext}`，CDN无鉴权
- SPA fallback：所有路径返回index.html

## 工作流

### Step 1: 下载JS并识别版本

```bash
curl -sL "https://site.com/js/script.js" -o script.js
head -c 200 script.js | grep -o 'jsjiami\.com\.v[0-9]'
```

### Step 2: v5解码

Hook `_0x2939` 收集字符串。移除反调试后eval。

### Step 3: v6 XOR密钥提取

v6不能eval。正则提取 `_0x4525` 调用后Node收集字符串。
XOR key 在v6字符串表 `1c9` 索引处。

### Step 4: XOR解密验证

```python
import base64
KEY = b"<key>"

def decrypt_filename(encrypted):
    std = encrypted.replace('-', '+').replace('_', '/')
    pad = len(std) % 4
    if pad: std += '=' * (4 - pad)
    cipher = base64.b64decode(std)
    return bytes([cipher[i] ^ KEY[i % len(KEY)] for i in range(len(cipher))]).decode()
```

### Step 5: 发现API端点

SPA fallback → 从JS源码搜JSON路径：
```bash
grep -oP "['\"][/a-z_]+\.json['\"]" script.js | sort -u
```

### Step 6: 批量下载

```python
data = requests.get("https://site.com/path/to/images.json").json()
for item in data:
    fn = decrypt_filename(item['filename'])
    r = requests.get(f"https://site.com/images/{fn}")
    with open(f"output/{fn}", 'wb') as f: f.write(r.content)
```

## Pitfalls

1. **v6 eval报错** — 用正则提取+Node收集替代
2. **SPA fallback** — 所有路径200，从JS源码找API
3. **XOR key在v6字符串表** — 需收集全量解码结果
4. **Base64 URL-safe** — filename用 `-` `_` 需转标准Base64
5. **反调试移除** — eval前必须移除 `setInterval(debugger)`

## 参考案例

- **bizhi.likew.net** (2026-08-03) — 5,531张壁纸，XOR key `2wE4rT6yU8iO0pI%aS3dF5gH7jK`，API `/top/me/yes/cool/images.json`

---
