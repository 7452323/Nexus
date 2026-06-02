---
category: reverse-engineering
name: webpack-unpack
version: "1.0"
description: 提取Webpack打包模块,还原独立可运行的JS代码。触发词: webpack、打包、解包、模块提取、bundle拆分、__webpack_require__、__webpack_modules__、webpackJsonp。当用户需要从Webpack打包后的JS文件中提取特定模块及其依赖、还原可运行代码、或提到bundle/unpack时, 必须使用此技能。
tags: [reverse-engineering, webpack, bundle-unpacking, javascript, module-extraction]
---

# Webpack 解包 Skill

从 Webpack 打包后的 JS 文件中提取特定模块及其依赖, 生成独立可运行的 JS 代码。

---

## WP4/WP5 识别

首先确定目标文件的 Webpack 版本:

### Webpack 4 特征

- 全局变量: `webpackJsonp` 或 `window["webpackJsonp"]`
- bootloader 通常在 IIFE 的第一个参数
- 模块通过 `jsonpArray.push` 注册
- `__webpack_require__` 作为局部变量在 bootloader 闭包内

```javascript
// WP4 典型入口
(window.webpackJsonp = window.webpackJsonp || []).push([[chunkId], {
  moduleId: function(module, exports, __webpack_require__) { ... }
}]);
```

### Webpack 5 特征

- 全局变量: `__webpack_modules__` 或 `self["webpackChunk"]`
- 模块直接存储在 `__webpack_modules__` 对象中
- 异步 chunk 通过 `self["webpackChunkNAME"].push` 注册
- `__webpack_require__` 可能在全局可访问

```javascript
// WP5 典型入口
var __webpack_modules__ = {
  moduleId: (module, exports, __webpack_require__) => { ... }
};
```

### 快速判断方法

```bash
# 搜索特征字符串
grep -c "webpackJsonp" target.js       # WP4
grep -c "__webpack_modules__" target.js # WP5
grep -c "webpackChunk" target.js        # WP5
```

---

## 分析步骤

### Step 1: 识别 Webpack 版本和 bootloader

- 确认 WP4 或 WP5 (见上方识别方法)
- 定位 bootloader 函数 (通常是 IIFE 的第一个参数)
- 提取最小运行时: module 缓存 + `__webpack_require__` 函数

### Step 2: 定位目标模块

根据用户指定的函数名或特征, 在所有 module 中搜索:

```bash
# 搜索目标函数名
grep -n "targetFunction" target.js

# 搜索特征常量
grep -n "specificConstant\|API_URL" target.js
```

记录目标 module ID。

### Step 3: 依赖链递归解析

从目标 module 出发, 递归解析所有 `__webpack_require__(moduleId)` 调用:

```
目标 module → __webpack_require__(dep1) → __webpack_require__(dep2) → ...
```

构建完整依赖树, 记录所有需要的 module ID。

处理特殊情况:
- **动态导入**: `__webpack_require__.e()` 异步 chunk 加载 — 需要找到对应的 chunk
- **循环依赖**: 记录已访问的 module 避免无限递归
- **条件 require**: `if` 分支中的 `__webpack_require__` — 都需要提取

### Step 4: 提取和重组

提取必要的 module, 组装为独立 JS 文件:

1. **loader.js** — Webpack 运行时 (最小化): module 缓存 + require 函数
2. **modules.js** — 所有依赖 module 的代码
3. **index.js** — 入口文件 (导出目标函数)
4. **test.js** — 验证脚本

### Step 5: 验证

```bash
# 在 Node.js 中运行测试
node extracted/test.js

# 对比输出与浏览器环境中的结果
```

---

## 结构化输出

```
extracted/
├── loader.js      # Webpack 运行时 (最小化)
├── modules.js     # 所有依赖 module
├── index.js       # 入口文件 (导出目标函数)
└── test.js        # 验证脚本
```

### loader.js 模板

```javascript
// Webpack 最小运行时
var __webpack_modules__ = {};
var __webpack_module_cache__ = {};
function __webpack_require__(moduleId) {
    if (__webpack_module_cache__[moduleId]) {
        return __webpack_module_cache__[moduleId].exports;
    }
    var module = __webpack_module_cache__[moduleId] = { exports: {} };
    __webpack_modules__[moduleId](module, module.exports, __webpack_require__);
    return module.exports;
}
```

### modules.js 格式

```javascript
// 合并所有依赖 module
Object.assign(__webpack_modules__, {
    123: function(module, exports, __webpack_require__) {
        // module 123 的原始代码
    },
    456: function(module, exports, __webpack_require__) {
        // module 456 的原始代码
    }
});
```

### index.js 格式

```javascript
// 导出目标函数
var targetModule = __webpack_require__(123);
module.exports = targetModule;
```

### test.js 格式

```javascript
// 验证脚本
var result = require('./index.js');
console.log('Result:', result);
// 根据预期输出进行断言
```

---

## 技能分工

本技能专注于 Webpack bundle 的结构拆解和模块提取。与相关技能的协作关系:

| 需求 | 引用技能 | 说明 |
|------|---------|------|
| 拆包后的代码反混淆 (变量名还原、控制流平坦化还原等) | **ast-deobfuscation** | Webpack 拆包是反混淆的前置步骤。ast-deobfuscation 的 Step 0.5 引用本技能的输出作为输入 |

**调用时机**:
- 需要从 Webpack bundle 中提取模块 → 本技能独立处理
- 拆包后需要进一步反混淆 → 先用本技能拆包, 再调用 ast-deobfuscation
- 非 Webpack 打包格式 (Rollup, Vite, esbuild 等) → 本技能不适用

**典型工作流**:
1. webpack-unpack: 提取目标模块 → `extracted/` 目录
2. ast-deobfuscation: 对 `extracted/modules.js` 进行反混淆 → 可读代码

---

## 常见陷阱

| 陷阱 | 说明 | 解决方案 |
|------|------|---------|
| 提取了整个 bundle | 把所有 module 都搬出来, 文件巨大 | 只提取依赖链上的必要 module |
| 循环依赖导致无限递归 | A require B, B require A | 维护 visited 集合, 已访问的 module 不再递归 |
| 忽略浏览器环境依赖 | module 依赖了 `window`, `document` 等 | 在输出中标注需要补环境, 或提供 mock |
| WP4/WP5 混淆判断 | 文件被混淆后特征不明显 | 同时搜索两种特征, 优先按结构判断 |
| 动态 require | `__webpack_require__(variable)` 无法静态分析 | 尝试追踪变量值, 或标注需要运行时确定 |
| moduleId 不一致 | 不同 chunk 中 moduleId 可能重复或偏移 | 检查 chunk 注册逻辑, 确认全局 moduleId 映射 |
| 丢失 webpack runtime | 只提取了 module 代码, 忘了 require 函数 | 必须包含 loader.js 的最小运行时 |
| 异步 chunk 未提取 | `__webpack_require__.e()` 加载的 chunk 被遗漏 | 搜索 `.e(` 调用, 找到对应 chunk 文件一并提取 |
