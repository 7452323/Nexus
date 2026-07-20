# Babel API 速查

本文档提供 AST 反混淆中常用的 Babel API 参考、使用模式和注意事项。

---

## 核心模块

```js
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const t = require('@babel/types');
```

---

## 解析与生成

### 解析

```js
const ast = parser.parse(code, {
  sourceType: 'module',    // 'script' | 'module' | 'unambiguous'
  allowAwaitOutsideFunction: true,
  allowReturnOutsideFunction: true,
});
```

- `sourceType: 'module'` — 支持 import/export 语法
- `sourceType: 'unambiguous'` — 自动检测，有 import/export 用 module 否则用 script
- 混淆代码通常包含非标准结构，建议用 `unambiguous` 或 `module`

### 生成

```js
const output = generate(ast, {
  compact: false,          // 格式化输出
  concise: false,          // 非简洁模式
  comments: true,          // 保留注释
  retainLines: false,      // 不保留原始行号
}, code);                  // 传入原始 code 可生成 sourceMap

console.log(output.code);
```

---

## 遍历 (traverse)

### 基本 Visitor

```js
traverse(ast, {
  // 进入节点时调用
  BinaryExpression(path) {
    // path.node — 当前节点
    // path.parent — 父节点
    // path.scope — 当前作用域
  },
  // 退出节点时调用
  FunctionDeclaration: {
    exit(path) { /* ... */ }
  },
});
```

### 常用路径 (path) 方法

| 方法 | 说明 |
|------|------|
| `path.node` | 当前 AST 节点 |
| `path.parent` | 父节点 |
| `path.parentPath` | 父路径 |
| `path.scope` | 当前作用域 |
| `path.get(key)` | 获取子路径，如 `path.get("left")`、`path.get("body")` |
| `path.replaceWith(node)` | 替换当前节点 |
| `path.replaceWithMultiple(nodes)` | 替换为多个节点（用于将一个节点展开为多条语句） |
| `path.remove()` | 删除当前节点 |
| `path.insertBefore(node)` | 在当前节点前插入 |
| `path.insertAfter(node)` | 在当前节点后插入 |
| `path.stop()` | 停止遍历当前节点的子树 |
| `path.skip()` | 跳过当前节点的子树 |

---

## 静态求值

### `path.evaluate()`

```js
const { confident, value } = path.evaluate();
if (confident) {
  const newNode = t.valueToNode(value);
  path.replaceWith(newNode);
}
```

- 返回 `{ confident: boolean, value: any }`
- `confident === true` 表示可静态确定值
- **注意**: Infinity、NaN、undefined 通过 `t.valueToNode()` 生成的是 Identifier 而非 Literal，替换前需检查

### `path.get("test").evaluateTruthy()`

```js
const testPath = path.get("test");
const result = testPath.evaluateTruthy();
// result: true | false | undefined（不确定）
if (result === true) {
  // 条件恒真
} else if (result === false) {
  // 条件恒假
}
```

---

## 作用域与绑定

### `path.scope.getBinding(name)`

```js
const binding = path.scope.getBinding('myVar');
if (binding) {
  binding.constant;        // boolean — 是否未被重新赋值
  binding.referenced;      // boolean — 是否被引用
  binding.references;      // number — 引用次数
  binding.referencePaths;  // NodePath[] — 所有引用路径
  binding.path;            // 声明路径
}
```

### `path.scope.rename(oldName, newName)`

```js
// 安全重命名——会更新所有引用
path.scope.rename('_0xabcd', 'moduleName');
```

- 必须通过 `scope.rename()` 重命名，不能直接修改 `node.name`
- 会自动处理所有引用和绑定

### `path.scope.crawl()`

```js
// 删除/替换节点后，作用域信息可能过期
path.scope.crawl();  // 重新扫描作用域
```

- 在 `path.remove()` 或 `path.replaceWith()` 后，如果后续还需遍历，必须调用
- 在循环遍历中尤其重要

### `path.scope.hasBinding(name)`

```js
path.scope.hasBinding('myVar');       // 当前作用域及父作用域
path.scope.hasOwnBinding('myVar');    // 仅当前作用域
```

---

## 节点类型判断与创建

### 判断类型

```js
t.isIdentifier(node)           // node.type === 'Identifier'
t.isStringLiteral(node)        // node.type === 'StringLiteral'
t.isNumericLiteral(node)       // node.type === 'NumericLiteral'
t.isBooleanLiteral(node)       // node.type === 'BooleanLiteral'
t.isCallExpression(node)       // node.type === 'CallExpression'
t.isMemberExpression(node)     // node.type === 'MemberExpression'
t.isFunctionDeclaration(node)  // node.type === 'FunctionDeclaration'
t.isFunctionExpression(node)   // node.type === 'FunctionExpression'
// ... 所有 AST 节点类型都有对应的 is 函数
```

### 创建节点

```js
t.identifier('name')
t.stringLiteral('hello')
t.numericLiteral(42)
t.booleanLiteral(true)
t.nullLiteral()
t.regExpLiteral('pattern', 'flags')
t.callExpression(callee, args)
t.memberExpression(object, property, computed)
t.binaryExpression(operator, left, right)
t.unaryExpression(operator, argument, prefix)
t.logicalExpression(operator, left, right)
t.conditionalExpression(test, consequent, alternate)
t.functionDeclaration(id, params, body)
t.blockStatement(body)
t.returnStatement(argument)
t.variableDeclaration('var', [declarator])
t.variableDeclarator(id, init)
t.ifStatement(test, consequent, alternate)
t.switchStatement(discriminant, cases)
t.switchCase(test, consequent)
t.whileStatement(test, body)
t.forStatement(init, test, update, body)
t.expressionStatement(expression)
```

---

## 常见模式

### 常量折叠

```js
traverse(ast, {
  BinaryExpression(path) {
    const { confident, value } = path.evaluate();
    if (!confident) return;
    const newNode = t.valueToNode(value);
    if (!t.isLiteral(newNode)) return;  // 排除 Infinity/undefined
    path.replaceWith(newNode);
  },
});
```

### 字符串转义还原

```js
traverse(ast, {
  StringLiteral(path) {
    if (path.node.extra) {
      delete path.node.extra;
      // \x48\x65\x6c\x6c\x6f → "Hello"
    }
  },
  NumericLiteral(path) {
    if (path.node.extra) {
      delete path.node.extra;
      // 0x12 → 18
    }
  },
});
```

### 方括号转点号

```js
traverse(ast, {
  MemberExpression(path) {
    if (!path.node.computed) return;
    if (!t.isStringLiteral(path.node.property)) return;
    const key = path.node.property.value;
    if (!/^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(key)) return;
    path.node.computed = false;
    path.node.property = t.identifier(key);
  },
});
```

### Proxy 函数内联

```js
traverse(ast, {
  FunctionDeclaration(path) {
    // 识别: 函数体只有一条 return
    const body = path.node.body.body;
    if (body.length !== 1 || !t.isReturnStatement(body[0])) return;
    // 确认绑定稳定
    const binding = path.scope.getBinding(path.node.id.name);
    if (!binding || !binding.constant) return;
    // 找到所有引用并内联
    const returnArg = body[0].argument;
    const refPaths = binding.referencePaths;
    for (const refPath of refPaths) {
      // 根据函数体类型做替换...
    }
  },
});
```

---

## 注意事项

1. **`t.valueToNode()` 边界值**: Infinity 返回 `Identifier('Infinity')`，undefined 返回 `Identifier('undefined')`，NaN 返回 `Identifier('NaN')`。替换前必须检查 `t.isLiteral(newNode)`
2. **`path.replaceWithMultiple()`** 会将当前节点替换为多个节点，只适用于语句位置。在表达式位置使用会导致语法错误
3. **遍历中删除节点**: 在 `traverse` 中调用 `path.remove()` 是安全的，Babel 内部处理了迭代器
4. **`scope.crawl()` 的开销**: 每次调用都会重新扫描整个作用域树，不要在单个 visitor 内频繁调用。在循环遍历的每轮结束后调用一次即可
5. **`path.get("key")` vs `path.node.key`**: `path.get()` 返回 Path 对象（有 evaluate/replaceWith 等方法），`path.node.key` 返回原始 AST 节点
6. **解构导入**: `@babel/traverse` 和 `@babel/generator` 是 CommonJS 模块，需要 `.default` 访问
