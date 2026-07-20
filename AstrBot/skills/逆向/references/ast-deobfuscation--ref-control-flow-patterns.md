# 控制流平坦化模式

这份文档用于处理控制流平坦化、opcode `if` 链、虚拟机解释器主分发器，以及测试位噪声分支。

---

## 适用场景

- `for (...; ![];) { switch (...) { ... } }`
- `while (true) { switch (...) { ... } }`
- `"3|1|2".split('|')` 一类数组或顺序表驱动的平坦化
- 大量 `if (0x31 === opcode) ... else if ...`
- 虚拟机解释器里围绕同一个 opcode 变量做长链分发

---

## 控制流展平原则

- **优先写定向 visitor**，不要一开始追求通用大而全
- 先验证 `init`、`test`、`update`、`body` 结构是否稳定
- 只要结构不匹配，就直接跳过，不要强行展平
- 拼接 case 时同步清理仅用于跳转的赋值、无意义 `break` 和明显噪声语句

### 常见 while-switch 模式

```js
// 模式 1: 数组驱动的顺序表
var _0xarr = "3|1|2|0".split('|');
var _0xi = 0;
while (true) {
  switch (_0xarr[_0xi++]) {
    case '0': /* ... */ break;
    case '1': /* ... */ break;
    case '2': /* ... */ break;
    case '3': /* ... */ break;
  }
  if (_0xi >= _0xarr.length) break;
}

// 模式 2: 状态变量驱动
var _0xstate = 0;
while (true) {
  switch (_0xstate) {
    case 0: _0xstate = 3; continue;
    case 1: _0xstate = 2; continue;
    case 2: /* ... */ _0xstate = 0; continue;
    case 3: /* ... */ _0xstate = 1; continue;
  }
  break;
}
```

### 还原策略

1. **确定代码块的执行顺序** — 静态跟踪状态变量或顺序数组
2. **按顺序提取各 case 的代码块** — 移除跳转赋值和 continue/break
3. **替换整个结构** — 用 `path.replaceWithMultiple()` 替换

```
while/switch 结构 → 提取 case body → 按执行顺序排列 → replaceWithMultiple
```

---

## `if` 链改写为 `switch`

仅在以下条件**同时满足**时改写：

- 整条链都在判断同一个判别表达式
- 每个分支都拿这个表达式与字面量比较
- 分支数量足够长，改写后可读性明显提升

```js
// 改写前
if (0x1a === opcode) { /* ... */ }
else if (0x2b === opcode) { /* ... */ }
else if (0x3c === opcode) { /* ... */ }
// ... 20+ 分支

// 改写后
switch (opcode) {
  case 0x1a: /* ... */ break;
  case 0x2b: /* ... */ break;
  case 0x3c: /* ... */ break;
}
```

---

## 测试位噪声与哨兵比较

某些样本会在测试条件里塞入噪声：

```js
cond && fn(...) !== {}   // 噪声：空对象比较始终为 true
cond && fn(...) === {}   // 噪声：空对象比较始终为 false
```

只在以下前提下清理：

- 它位于 `if`、`for.test` 或 `while.test` 位置
- 右侧确实只是混淆器注入的空对象比较噪声
- 删除后不会影响左侧真实条件的副作用顺序

---

## 虚拟机解释器建议

VM 类混淆通常有三层结构：

1. **主分发器** — `while/switch` 或 `if` 链，根据 opcode 分发到各 handler
2. **栈变量** — 用数组模拟的操作栈
3. **opcode 读取器** — 从字节流中读取下一个 opcode

建议分两轮处理：

**第一轮**:
- 看清主分发器、栈变量、opcode 读取器
- 清掉虚假分支
- 把 `if` 链改成 `switch`

**第二轮**:
- 简化 case 内的局部结构
- 如果 case 内逻辑仍然复杂，保留给人工分析

---

## 停止条件

- 主 opcode 分发器已可读
- 关键 case 已经可以逐个分析
- 继续静态展开开始明显增加误改写风险

满足停止条件后，转入人工分析或结合运行时证据继续逆向。

---

## 与其他步骤的依赖

- **依赖 Step 2（表达式简化）**: 控制流还原前必须先做常量折叠，否则状态变量的值无法确定
- **依赖 Step 1（字符串解密）**: 顺序数组的字符串必须先解密才能确定执行顺序
- **产出供 Step 5（死代码移除）**: 控制流还原后会产生大量不可达代码和无用变量
