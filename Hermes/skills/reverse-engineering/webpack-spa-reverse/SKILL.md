---
name: webpack-spa-reverse
category: reverse-engineering
description: >-
  Merged skill combining: webpack-unpack, spa-early-request-fallback, flutter-web-reverse.
version: "1.0"
sources:
  - webpack-unpack
  - spa-early-request-fallback
  - flutter-web-reverse
tags: [reverse-engineering, merged]
---

# webpack-spa-reverse

> **Merged from**: webpack-unpack, spa-early-request-fallback, flutter-web-reverse
> **Source count**: 3

---

## Table of Contents

1. [webpack-unpack](#webpack-unpack)
2. [spa-early-request-fallback](#spa-early-request-fallback)
3. [flutter-web-reverse](#flutter-web-reverse)

---

## webpack-unpack

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

## Browserify 检测

非 Webpack 的常见 bundle 格式。webcrack 工具（[参考](references/webcrack-comparison.md)）可自动处理。

### 结构特征

```javascript
(function(files, cache, entryIds) {
  function require(id) { ... }
})({
  "./add.js": [
    function(require, module, exports) { ... },
    { "./utils/math.js": 3 }
  ],
})
```

### 识别方法

```bash
# 特征：模块 key 是文件路径字符串
grep -c '".*\.js":\s*\[function' target.js

# 对比 Webpack（模块 key 是数字）
grep -c '"[0-9]\+":\s*function' target.js
```

### 关键区别

| 特征 | Webpack | Browserify |
|------|---------|------------|
| 模块 ID | 数字 | 文件路径字符串 |
| 模块格式 | `id: function(...)` | `path: [factory, deps]` |
| 依赖表示 | 数字 ID | 相对路径映射 |
| 加载函数 | `__webpack_require__` | `require()` |

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

---

## spa-early-request-fallback

# SPA 早期请求 Hook 失败时的回退策略

## 问题

SPA/PWA 页面在 `<script>` 加载后立即发起 API 请求（Vue `mounted()` / React `useEffect()`），浏览器注入的 XHR/Fetch hook 执行时机晚于这些请求。每次 `browser_navigate` 清空之前注入的 hook。

## 回退优先级

### 1. JS Bundle 字符串池提取（首选回退）

混淆器将所有字符串常量集中存储在字符串池中。提取整个池 = 一次性获取全部 API 端点。

```python
import re
with open('app.js') as f:
    js = f.read()

for m in re.finditer(r"function\s+(a0_\w+)\s*\(\s*\)\s*\{", js):
    idx = m.start()
    end = js.find('];', idx)
    chunk = js[idx:end+2]
    strs = re.findall(r"'([^']+)'", chunk)
    apis = [s for s in strs if s.startswith('/') or s.startswith('https://')]
    print(f"Pool: {len(strs)} strings, {len(apis)} API endpoints")
```

**案例**：91Porn PWA app.js 1.7MB → 5093 字符串 → 70+ API 端点、3 个域名、签名公式、DES3 加密。

### 2. 暴力参数测试

从字符串池找到参数名后，curl 测试常见组合：
`{"action":"home","page":"1"}` / `{"c":"index","p":"1"}` / `{"m":"list","limit":"20"}`

### 3. Vue/React 实例遍历

Vue 3 prod 模式 `_instance` 可能是 null，但值得一试。

### 4. CDP Network 域直接抓取

需要比 `browser_console` 更底层的 CDP 协议访问。

## 局限

- 只能提取静态字符串，动态参数名不可见
- 签名密钥动态下发时只有变量名没有值
- 需配合 curl 验证实际请求格式
- 多个 chunk 需全部下载分别提取

## 与其他技能的关系

- **`web-api-reverse-engineering`**：Step 2 前端 JS 分析的补充技术
- **`js-reverse-engineering`**：Observe/Capture 阶段 hook 失败时的回退
- **`saas-backend-api-discovery`**：发现 SaaS API 后转交

## Pitfalls

1. 导航 3 次 hook 仍空 → 立即切换字符串池提取，不要死磕
2. 大型 bundle 可能有多个字符串池函数，全部提取
3. `a0_xxxx` 命名是特定混淆器特征，其他混淆器用不同模式
4. 提取的 API 路径可能是相对路径，需从 `https://` 字符串找 base URL

---

## flutter-web-reverse

# Flutter Web 逆向

dart2js 编译产物（`main.<hash>.js`）体积 6-10MB，但结构规整。

## 1. 文件定位

```bash
# 从 sw.js 或 flutter_bootstrap.js 获取真实 main 文件名
curl -sL "https://target.com/sw.js" | grep -oP 'main\.[a-f0-9]+\.js'

# 首页 HTML 中可能被 SPA fallback 掩盖，优先查 sw.js
```

## 2. API 域名提取

```bash
# Flutter 通常硬编码多个 API 域名（海外/国内）
grep -oP 'https?://[a-z0-9._-]+\.(top|com|me|cc|xyz)' main.dart.js | sort -u
```

## 3. 签名算法提取

dart2js 中加密函数命名规律：
- MD5 实现类通常含 `1732584193` (MD5 IV)
- SHA256 实现含 `1779033703` (SHA256 IV)
- bytes→hex 函数含 `0123456789abcdef`

### 典型签名链

```
sign = hex(SHA256(MD5(input)))
# input = "Dart|requestId|sessionId|urlPath"
```

查找模式：
```bash
grep -oP '.{0,100}(version|deviceType|time|sign).{0,200}' main.dart.js | grep -i dart
grep -oP 'czx\(a\)\{.{0,300}' main.dart.js
```

## 4. AES 密钥

图片/资源加密通常用 AES-ECB：
```bash
grep -oP 'fetchImage|decryptImage|AES|CryptoJS' main.dart.js
grep -oP '(encryptKey|decryptKey|aesKey|resourceKey)' main.dart.js
```

## 5. 中文字符串提取

dart2js **不删除中文**，而是转成 Unicode 转义序列 `\uXXXX`。直接用 Python 解码即可：

```python
import re
code = open('main.dart.js').read()
decoded = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), code)

# 提取所有中文片段
chinese = re.findall(r'[\u4e00-\u9fff]{2,}', decoded)
print(f"Total: {len(chinese)} unique strings")
for s in sorted(set(chinese)):
    print(f"  {s}")
```

常见可提取内容：模块名（短剧/漫画/小说）、UI标签、错误提示、菜单项。

## 6. 菜单/功能枚举

配合 Unicode 解码后的代码，通过以下方式穷举所有功能：

```bash
# 1. API 路由表（最全）
grep -oP '"/([a-z]+/)*[a-z]+"' main.dart.js | sort -u

# 2. SVG/图标 ID 推断模块
grep -oP '[a-zA-Z]+Mod|[a-zA-Z]+Topic|[a-zA-Z]+List|[a-zA-Z]+Wish' main.dart.js | sort -u

# 3. 模块路由路径
grep -oP '/[a-z]+/' main.dart.js | sort -u
```

## 7. 常见 API 端点

```bash
# 提取所有 API 路由（最全方式）
python3 -c "
import re
code = open('main.dart.js').read()
paths = set(re.findall(r'\"(/[a-z]+(?:/[a-z]+)*)\"', code))
for p in sorted(paths):
    print(f'  {p}')
"
```

典型模块结构：
- `/drama/*` — 短剧（navList, list, detail, play, doBuy, doLove, doFavorite, doShare, doHistory, rank, topic, mod, more, search, wish/*, urge/*）
- `/comics/*` — 漫画（同上结构）
- `/novel/*` — 小说（同上结构）
- `/movie/*` — 视频（同上结构）
- `/photo/*` — 图片（同上结构）
- `/post/*` — 社区帖子
- `/user/*` — 用户模块
- `/mine/*` — 个人中心
- `/pay/*` — 支付
- `/ai/*` — AI功能
- `/search/*` — 搜索
- `/chat/*` — 聊天
- `/login/*` — 登录
- `/product/*` — 商城
- `/dating/*` — 交友
- `/up/*` — 创作者
- `/lottery/*` — 抽奖
- `/task/*` — 任务
- `/redeem/*` — 兑换

## 7. 局限性

- **CF 保护**：签名算法可还原，但 VPS IP 可能仍被 CF 拦截
- **中文缺失**：UI 字符串被 tree-shake，无法从 JS 提取
- **AES 密钥动态**：key 从 API 响应获取，无法静态提取
- **WASM 模式**：部分 Flutter Web 使用 WASM 编译，dart2js 模式不适用

## 参考案例

- 黄豆短剧 (lzlukvca.cc)：签名 = hex(SHA256(MD5("Dart|reqId|sessId|path")))，API 域名池 hvthtcpa.top/psfxhhox.top 等，图片 AES-ECB。详见 `references/lzlukvca-case.md`

---
