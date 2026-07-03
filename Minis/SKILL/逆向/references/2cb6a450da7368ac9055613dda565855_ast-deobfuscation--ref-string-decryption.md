# 字符串数组解密方法

这份文档用于处理字符串表、解码包装、局部别名链和最小引导 `eval`。

---

## 适用场景

- 文件开头几条语句就在初始化解码器
- 顶层 IIFE 里传入数组、对象或字符串表
- 源码里大量出现 `fn(12)`、`arr[123]`、`String.fromCharCode(...)`
- 第一层去壳之后，函数内部还存在二次字符串恢复

---

## 推荐顺序

1. **先定位**数组字面量、解码函数和别名链
2. **优先做静态恢复**：数组下标、纯字面量拼接、纯数字参数调用
3. **静态无法推进时**，才执行最小引导代码
4. **删除**已经消费掉的引导声明或包装层
5. **重新 parse** 一次，再进入控制流还原阶段

---

## 字符串数组结构识别

典型的字符串数组混淆包含三部分：

### 1. 字符串数组函数

```js
function _0x1234() {
  var _0xarr = ['log', 'Hello', 'apply', 'prototype', ...];
  // 可能有旋转操作
  _0xarr.push(_0xarr.shift());  // 旋转
  return _0xarr;
}
```

### 2. 旋转 IIFE

```js
(function(_0xarr, _0xi) {
  // 对数组执行 push/shift 旋转
  while (_0xi--) {
    _0xarr.push(_0xarr.shift());
  }
})(_0x1234(), 0x1a2);  // 旋转次数
```

### 3. 访问器函数

```js
function _0x5678(_0xi) {
  return _0x1234()[_0xi - 0x0];  // 带偏移量的数组访问
}
// 或者更复杂的: 双参数版本
function _0x5678(_0xi, _0xkey) {
  _0x1234();
  return _0xarr[_0xi - _0xkey];  // 使用闭包变量
}
```

**识别方法**: 通过 AST 体检报告中的"最大 ArrayExpression"和"CallExpression callee 频次 Top 5"定位。

---

## 解密方案

### 方案 A（推荐）: Node.js vm 沙箱

#### A1: 最小引导（提取片段执行）

当可以从AST中干净地提取解码器函数、字符串数组和旋转IIFE时使用。

```js
const vm = require('vm');

// 1. 从 AST 中提取字符串数组 + 旋转 IIFE + 访问器函数的源码
const sandbox = vm.createContext({});

// 2. 在沙箱中执行提取的片段
vm.runInContext(decoderSourceCode, sandbox);

// 3. 遍历 AST 中的 CallExpression，用沙箱函数计算返回值
traverse(ast, {
  CallExpression(path) {
    if (!isAccessorCall(path)) return;
    const args = path.node.arguments.map(a => {
      if (t.isNumericLiteral(a)) return a.value;
      if (t.isStringLiteral(a)) return a.value;
      return null;
    });
    if (args.some(a => a === null)) return;  // 非字面量参数，跳过
    try {
      const result = vm.runInContext(
        `accessorFn(${args.join(',')})`, sandbox
      );
      if (typeof result === 'string') {
        path.replaceWith(t.stringLiteral(result));
      } else if (typeof result === 'number') {
        path.replaceWith(t.numericLiteral(result));
      }
    } catch (e) {
      // 沙箱执行失败，跳过此调用点
    }
  },
});

// 4. 删除已无用的数组函数、旋转 IIFE、访问器函数
```

⚠️ **注意**: 当解码器函数包含反调试自检（如 `new k(a0e)['aEwLep']()` 这类toString检测）时，正则提取可能不完整。此时应使用 A2 方案。

#### A2: 全脚本沙箱引导（推荐用于复杂混淆）

当代码结构复杂（反调试、闭包依赖、多层IIFE交织）导致无法干净提取解码器片段时使用。**核心思路：注入无害的宿主环境stub，让整个脚本在沙箱中完整初始化，然后直接从沙箱中收割解码器函数。**

```js
const vm = require('vm');

// 1. 注入脚本依赖的宿主环境stub（根据脚本类型调整）
const sandbox = {
  // Surge/QuantumultX/Loon Rewrite脚本典型stub
  $request: { url: '', headers: {} },
  $response: { statusCode: 200, body: '{}', headers: {} },
  $prefs: { valueForKey: () => '', setValueForKey: () => {} },
  $persistentStore: { read: () => '', write: () => {} },
  $task: { fetch: () => Promise.resolve({statusCode: 200, body: '{}'}) },
  $httpClient: { get: () => {}, post: () => {} },
  // 通用stub
  console: { log: () => {}, warn: () => {}, error: () => {} },
  Math, String, parseInt, decodeURIComponent, Boolean, RegExp,
  Array, Object, JSON, Date, Number,
  setTimeout, setInterval, clearTimeout, clearInterval,
  Promise, Symbol, Map, Set, Error, TypeError, RangeError,
  Uint8Array, ArrayBuffer, DataView, eval: eval, process: { env: {} }
};
vm.createContext(sandbox);

// 2. 执行完整脚本（超时保护！）
vm.runInContext(fullScriptCode, sandbox, { timeout: 15000 });

// 3. 从沙箱中直接获取解码器函数
// sandbox.a0d, sandbox.a0e 等已初始化完毕
console.log('a0d ready:', typeof sandbox.a0d);  // 'function'

// 4. 正常执行AST遍历替换...
```

**关键优势**:
- 无需正则提取函数片段，避免语法不完整问题
- 反调试自检函数在沙箱中正常执行但不产生副作用
- 旋转IIFE自动完成，数组顺序已正确
- 闭包、arguments对象等复杂初始化全部正确完成

**关键注意**:
- 必须注入足够的环境stub，否则脚本执行会报错中断
- 必须设置timeout（推荐10-15秒），防止无限循环
- 需要了解脚本运行环境（如Surge Rewrite脚本需要$request等）
- 如果脚本末尾有立即执行的业务逻辑，需要确保stub使其无害执行

### 方案 B: 纯静态分析

当旋转逻辑简单时使用：

```js
// 1. 解析数组元素
// 2. 静态计算旋转次数（从旋转 IIFE 中提取）
// 3. 手动应用旋转得到最终数组
// 4. 直接用索引查表替换

function applyRotation(arr, times) {
  for (let i = 0; i < times; i++) {
    arr.push(arr.shift());
  }
  return arr;
}
```

---

## 最小引导 eval 原则

当代码包含多层加密，静态分析无法完全解密时，使用最小引导 `eval`：

- **只执行**前几条足以构造解码器的代码
- **不要直接执行**整份源文件
- **不要在未隔离的环境里**执行明显依赖 DOM、`window`、定时器或网络的逻辑
- **求值目标应尽量窄**，例如"只恢复数字参数到字符串的函数调用"

---

## 常见模式

### 顶层 IIFE 带数组参数

```js
(function(_0xarr, _0xrotate) {
  // 旋转 + 访问器定义
})(['log', 'Hello', ...], 0x1a2);
```

处理：
- 从顶层调用提取 `formalParam -> actualArg` 映射
- 只替换明确命中的数组下标访问
- 处理包装函数里直接可展开的语句块

### 前几条语句就是解密引导

```js
var _0xarr = ['log', 'Hello', ...];  // 第1条
(function(a, b) { ... })(_0xarr, 0x1a2);  // 第2条
function _0xaccess(i) { return _0xarr[i - 0x0]; }  // 第3条
```

处理：
- 只截取前 2 到 5 条关键语句
- 建立最小运行时后，恢复只带字面量参数的调用点
- 删除已消费的引导语句

### 去掉第一层后，局部函数还有二次恢复

```js
function inner() {
  var localArr = ['token', 'encrypt', ...];
  var localAccessor = function(i) { return localArr[i]; };
  // ...
}
```

处理：
- 先展开顶层 IIFE
- 重新 parse
- 再识别函数内部那组"构造器 + 成员表达式 + 数字下标"的模式
- 对局部字符串数组做同样的解密处理

---

## 别名映射（必须步骤）

混淆代码中，访问器函数（如 `a0d`/`a0e`）在**每个函数内部**都有局部别名声明：

```js
function someFunc() {
  var aY = a0d;  // 别名: aY → a0d
  var aX = a0e;  // 别名: aX → a0e
  // 后续代码用 aY(0x123, "key") 而非 a0d(0x123, "key")
}
```

**如果只替换 `a0d`/`a0e` 的直接调用，会遗漏90%以上的调用点。**

### 收集别名映射

```js
const aliases = {};
traverse(ast, {
  VariableDeclarator(path) {
    if (t.isIdentifier(path.node.id) && t.isIdentifier(path.node.init)) {
      const target = path.node.init.name;
      if (target === 'a0d' || target === 'a0e') {
        aliases[path.node.id.name] = target;
      }
    }
  }
});
// aliases = { aY: 'a0d', aX: 'a0e', aM: 'a0e', aL: 'a0d', ... }
// 典型样本有 70+ 个别名

const decryptFuncs = new Set(['a0d', 'a0e', ...Object.keys(aliases)]);
```

### 替换时解析真实函数

```js
traverse(ast, {
  CallExpression(path) {
    const callee = path.node.callee;
    if (!t.isIdentifier(callee) || !decryptFuncs.has(callee.name)) return;
    const realFunc = aliases[callee.name] || callee.name;  // 解析别名
    // 用 realFunc 决定参数模式（a0d双参数 / a0e单参数）
    // 用 sandbox[realFunc](...) 执行解密
  }
});
```

---

## 停止条件

- 主要字符串表已经恢复
- 核心解码器入口已经清楚
- 剩余部分不再适合纯静态恢复

满足以上条件后，应切换到控制流或结构标准化阶段。

---

## 转义字符串还原

```js
traverse(ast, {
  StringLiteral(path) {
    if (path.node.extra) {
      delete path.node.extra;
      // \x48\x65\x6c\x6c\x6f → "Hello"
      // \H\e → "He"
    }
  },
  NumericLiteral(path) {
    if (path.node.extra) {
      delete path.node.extra;
      // 0x12 → 18, 0b1010 → 10
    }
  },
});
```

`node.extra` 存储了原始的转义表示。删除后，`generate()` 会输出已解析的值。

---

## 验证

用 MCP `evaluate_script` 或本地沙箱抽样验证：

```js
// 对比原始访问器函数和解密后的字面量
const original = accessorFn(12);  // 原始函数调用
const replaced = "expectedString"; // 替换后的字面量
assert.strictEqual(original, replaced);
```

建议至少验证 5-10 个调用点，确保解密环境正确。
