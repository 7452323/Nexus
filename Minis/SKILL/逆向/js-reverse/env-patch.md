---
category: reverse-engineering
name: env-patch
version: 1.0.0
description: >-
  JS逆向补环境统一技能。在Node.js中运行依赖浏览器环境的JS代码，提供引擎+策略分离架构、诊断驱动循环、4类问题分类、14模块清单、指纹固定化、替代路线决策。
  TRIGGER when: 用户说"补环境"、"环境模拟"、"Proxy吐环境"、"Node里跑浏览器JS"、"浏览器环境补丁"、"环境patch"、"指纹固定"、"document.all"、"webdriver检测"、"原型链修复"、"native toString保护"、"canvas/WebGL指纹"、"JsRpc替代"。
  DO NOT TRIGGER when: 只在浏览器中调试（用cdp-debug-reverse）、做AST解混淆（用ast-deobfuscation）、纯算法还原（用algorithm-reverse）、写普通Node.js代码。
argument-hint: "[项目名] [可选：场景说明]"
tags: [reverse-engineering, javascript, environment-patching, browser-simulation, proxy, fingerprint, nodejs]
---

# env-patch: JS逆向补环境

对 **$ARGUMENTS** 执行补环境方案。

**前置条件**：已知加密入口（模块ID、函数名、所在脚本）。如未定位，先用 js-reverse-engineering 的 Observe→Capture 阶段定位。

## 技能分工

| 你需要的 | 应该用 |
|---------|--------|
| 补环境协议、环境模拟、诊断驱动补丁、指纹固定 | → **本技能** (env-patch) |
| CDP断点、单步追踪、callFrame求值、脚本替换 | → **cdp-debug-reverse** |
| AST解混淆、控制流扁平化还原、字符串阵列还原 | → **ast-deobfuscation** |
| 纯算法提取、跨语言迁移、算法还原验证 | → **algorithm-reverse** |
| 完整逆向工作流（Observe→Capture→Rebuild→Patch→PureExtraction→Port） | → **js-reverse-engineering** |

**协作模式**：本技能专注 Patch 阶段。Capture 阶段定位入口后交接给本技能；补环境通过后交接给 algorithm-reverse 做纯算法提取；反调试需求先用 **anti-debug** 绕过再补环境；VMP场景补环境后交接给 **jsvmp-reverse** 做VM逆向；瑞数场景中sdenv/JsRpc替代路线由本技能提供，通用VM方法引用 **ruishu-reverse**；深度CDP调试用 cdp-debug-reverse。

## 5条铁律

1. **禁止修改原始JS** — `source/` 下文件只读。`env/` 下的JS副本（main.js/sdk.js/bytecode.js）一旦生成即为定稿，不再修改。所有补丁写在 run.js / sign.js 中。
2. **必须 require env_core.js** — 禁止在 run.js 中重写 setFuncNative / setObjNative / createProxy 等工具函数。所有工具通过 `const env = require('./env_core')` 引入。env_core.js 复制后不再修改。如果需要额外 helper，写在 run.js 顶部，但不得重复实现 env_core 已有功能。
3. **先分析VMP入口参数** — VMP入口的依赖数组决定补环境边界。`typeof chrome !== "undefined" ? chrome : undefined` 检查的是 `globalThis`，不是 `window`。必须用 `Object.defineProperty(global, name, ...)` 同步。
4. **加载顺序是致命的** — VMP在 `require()` 的**瞬间**初始化并读取环境，之后不可更改。run.js 中的代码必须严格按以下顺序：
   1. `const env = require('./env_core')` — 获取工具（第一行）
   2. 构建存根对象（document / navigator / location 等）
   3. `env.init({ window, document, navigator, location })` — 阻断Node泄露 + 挂载全局
   4. 额外环境补齐 — performance、chrome等全局同步
   5. `require('./main.js')` — 加载目标JS
   6. 测试签名
5. **格式验证优先于请求验证** — 签名长度/前缀与浏览器不一致 = 降级，即使HTTP 200也是假阳性。

## 核心概念

### 引擎 + 策略分离架构

| 文件 | 角色 | 修改策略 |
|------|------|---------|
| `env_core.js` | **引擎**：提供 setFuncNative / setObjNative / getNativeProto / wrapFunc / monitor / createProxy 和诊断报告 | 复制后不再修改 |
| `run.js` | **策略**：所有环境存根、补丁、加载逻辑 | 每轮诊断后只改此文件 |
| `browser-stubs` | **存根目录**：按诊断报告按需取用存根代码 | 参考 [references/browser-env-modules.md](references/browser-env-modules.md) |

env_core.js 是工具集 + Proxy引擎 + 诊断报告生成器。它不含任何环境存根——所有站点特定的环境补丁都写在 run.js 中。这种分离确保：

- 引擎代码稳定，一次编写多站复用
- 策略代码每轮迭代，不影响引擎
- 诊断报告由引擎统一生成，格式一致

### 4类问题分类

补环境任务首先判断属于哪一类：

| 类型 | 症状 | 策略 |
|------|------|------|
| **1. 缺对象/缺属性** | 代码直接报 `undefined` / `is not defined` | 逐项补齐，从 browser-stubs 取用规范写法 |
| **2. 原型链/描述符检测** | 对象存在但 `toString` / `instanceof` / `getOwnPropertyDescriptor` 暴露 | 构造器 + prototype + 实例三层补齐，native 保护 |
| **3. 指纹检测** | 基础对象能跑，但 canvas/WebGL/audio/RTC 指纹异常 | 指纹固定化或随机化双模式 |
| **4. 成本过高** | 补环境投入远超收益 | 切换 JsRpc / sdenv / 真浏览器 |

**默认优先走"诊断驱动"的补环境路线**，而不是一次性补全浏览器。

## 诊断循环决策树

每轮运行后读取诊断报告，按以下决策树处理：

```
诊断报告
├── [HANG] 进程卡死/无输出 → 反调试处理
│   ├── setInterval debugger死循环 → hook setInterval过滤
│   ├── eval/Function 动态生成debugger → hook eval + Function剥离
│   └── 同步while(true) → 定位源码，run.js中patch全局
│
├── [ERRORS] → 必须立即修复
│   ├── TypeError: xxx is not a function → 补对应方法
│   ├── xxx is not defined → 补全局变量/构造函数
│   └── Cannot read property of undefined → 补中间对象
│
├── [UNDEFINED] → 逐项处理
│   ├── 先从浏览器获取真实值（CDP evaluate_script）
│   ├── 浏览器也是undefined → 跳过（标记为已确认）
│   └── 浏览器有值 → 补到run.js（从browser-stubs取用规范写法）
│
└── ERRORS = 0 && UNDEFINED全部已确认 → 进入签名格式校验
    ├── 签名长度/前缀与浏览器一致 → 封装sign.js
    └── 签名不一致 → 深度排查
        ├── monitor()包装关键对象，追踪属性访问
        ├── 全局错误拦截：process.on('uncaughtException')
        ├── 对照Node检测绕过清单逐项检查
        ├── 检查cookie/storage是否需要预置真实值
        └── 所有外部hook均无异常 → VMP opcode级检测（见替代路线）
```

**每轮操作**：
1. 读诊断报告
2. 从 browser-stubs 取用对应存根代码，用 env_core 的工具编写
3. 只修改 run.js
4. 重新运行，回到第1步

## 项目结构

```
<project>/
├── source/     # 原始JS（下载，不修改）
├── env/        # 运行环境
│   ├── env_core.js      # 从模板复制，不改
│   ├── main.js          # 目标JS副本（或 sdk.js + bytecode.js）
│   ├── run.js           # 加载器 + 环境存根 + 测试
│   └── sign.js          # 签名接口（最后封装）
├── python/     # 验证脚本
└── docs/progress.md
```

### 场景判断

| 场景 | JS文件 | 参考文档 |
|------|--------|---------|
| 单文件SDK | 复制到 `env/main.js` | — |
| SDK + 字节码分离 | `env/sdk.js` + `env/bytecode.js` | references/multi-file |
| webpack bundle | 提取模块到 `env/main.js` | references/webpack |
| 运行时动态加载 | curl下载到 `source/`，复制到 `env/` | references/dynamic-loading |

## 14模块脚本清单

按依赖顺序列出。每个模块的详细接口参见 [references/browser-env-modules.md](references/browser-env-modules.md)。

| # | 模块 | 职责 |
|---|------|------|
| 1 | **prototype-builder** | 构造器 + prototype + 实例三层构建，建立浏览器对象图骨架 |
| 2 | **descriptor-guard** | 属性描述符对齐（enumerable/configurable/writable/get/set），防止描述符检测 |
| 3 | **native-protector** | Function.prototype.toString 保护 + toString.toString 深层防护 + name/length 修正 |
| 4 | **navigator-module** | Navigator/plugins/mimeTypes/getBattery/userAgentData 完整构建 |
| 5 | **document-module** | Document/HTMLDocument/cookie访问器/DOM查询API/document.all |
| 6 | **storage-module** | Storage/localStorage/sessionStorage 状态预置与cookie联动 |
| 7 | **fingerprint-module** | canvas/WebGL/battery/screen/windowMetrics 指纹固定化 |
| 8 | **performance-module** | performance.now/timeOrigin/timing 时间一致性修正 |
| 9 | **crypto-module** | crypto/getRandomValues/subtle/typed array校验 |
| 10 | **webrtc-module** | RTCPeerConnection/RTCDataChannel/createOffer/ICE候选 |
| 11 | **audio-module** | AudioContext/OfflineAudioContext/AudioBuffer/getChannelData |
| 12 | **worker-module** | Worker/SharedWorker/MessagePort/BroadcastChannel/postMessage |
| 13 | **math-precision-module** | 浏览器/Node Math精度差异对照与修正 |
| 14 | **document-all-module** | document.all 特殊对象三路线处理（native-addon / v8-api / fallback） |

**执行顺序**：1→2→3→4→14（如果站点早期卡死在document.all则前置）→5→6→7→8→9→10→11→12→13。

## 指纹固定化方案

指纹对象补丁必须支持两种模式：

### 固定模式（默认）

从浏览器采集真实指纹种子，固化到补丁中。每次运行返回相同值。

```javascript
// 从浏览器采集的种子数据
const FINGERPRINT_SEED = {
    canvas: 'data:image/png;base64,iVBORw0KGgo...',
    webgl: { vendor: 'Google Inc. (Apple)', renderer: 'ANGLE (Apple, ANGLE Metal Renderer: Apple M3...)' },
    audio: { sampleRate: 44100, channelData: [...] },
    screen: { width: 1920, height: 1080, colorDepth: 24 },
};
```

### 随机化模式

对高安全场景，每次运行生成不同的但内部自洽的指纹值。需确保：
- canvas toDataURL 返回值与 canvas 2d 绘制上下文行为一致
- WebGL vendor/renderer 与 navigator.userAgent/platform 自洽
- screen 尺寸与 window.innerWidth/innerHeight 自洽
- audio 指纹与 audio 上下文参数自洽

**关键原则**：指纹值不是孤立数据，必须与同一设备画像中的其他值保持逻辑一致。

## document.all 特殊处理

`document.all` 不能当普通属性补。它是浏览器历史兼容对象，具有独特的类型系统行为。

### 三路线方案

| 路线 | 方案 | 优劣 |
|------|------|------|
| **native-addon** | sdenv方案：C++ V8 Addon，`ObjectTemplate::MarkAsUndetectable()` | 完美还原，但需编译原生模块 |
| **v8-api** | 直接调用 Node.js 的 V8 C++ API | 需要底层权限，部署复杂 |
| **fallback** | 纯JS降级：Proxy + Symbol.toPrimitive + toString 欺骗 | 无法完全还原 `== undefined` 行为 |

### 验证项

```javascript
// 这四项必须全部通过
document.all == undefined   // true（falsy）
document.all === undefined  // false（不严格等于undefined）
typeof document.all         // "undefined"（唯一typeof返回undefined但不是undefined的对象）
Boolean(document.all)       // false
```

**fallback 路线的 residual risk**：纯 JS 无法让 `typeof` 返回 `"undefined"`（Proxy 的 `apply` trap 无法拦截 `typeof` 操作）。如果目标站点检测 `typeof document.all`，必须走 native-addon 或 sdenv。详见 [references/special-cases.md](references/special-cases.md)。

## Node检测绕过

目标代码常先检测是否在 Node 中运行，检测到则走降级逻辑。详见 [references/node-detection-bypass.md](references/node-detection-bypass.md)。

### 必须处理的检测项

| 检测项 | 对策 | 关键陷阱 |
|--------|------|---------|
| `typeof Buffer !== "undefined"` | `delete globalThis.Buffer`（必须delete，不能用getter） | getter会被GOPD识别为accessor |
| `typeof process !== "undefined"` | `globalThis.process = {env:{BROWSER:true}}`（data property） | 必须是data property不能用getter |
| `Error.prepareStackTrace` | `delete Error.prepareStackTrace` | Node V8特有API |
| `module / exports / require` | 在VMP入口依赖数组中改为void 0 | 或在global上隐藏 |
| `Object.prototype.toString.call(window)` | `Symbol.toStringTag = 'Window'` | 非唯一检测点 |
| Node 21+内置 `navigator` getter | `Object.defineProperty(global, 'navigator', {value:...})` | 简单赋值被内置getter拦截 |

### 统一原则

所有全局变量覆盖都用 `Object.defineProperty`：
```javascript
Object.defineProperty(global, 'navigator', {
    value: proxiedNavigator,
    writable: true, configurable: true, enumerable: true,
});
```

## 替代路线决策

补环境不是唯一路线。当成本明显高于收益时，应切换替代路线。

### 决策矩阵

| 条件 | 推荐路线 |
|------|---------|
| 缺失对象少、依赖链清晰 | **纯补环境**（本技能主路线） |
| DOM/BOM依赖多、想保留原始代码 | **sdenv**（魔改jsdom，支持document.all） |
| 补环境遇到VMP opcode级检测 | **JsRpc**（浏览器内执行，回传结果） |
| 强依赖真实DOM/事件流/渲染 | **真浏览器**（Playwright/Puppeteer） |
| 需要高频采集（毫秒级） | **纯算法还原**（最终目标） |

### JsRpc 架构

```
Node.js/Python ←HTTP→ JsRpc Server ←WebSocket→ 浏览器
                                                  ↓
                                            目标JS自动执行
                                            生成签名/Cookie
                                                  ↓
                                            返回完整结果
```

适用场景：瑞数等VMP保护站点、补环境卡在opcode级检测、需要Cookie+URL后缀全自动。详见 [references/jsrpc-alternative.md](references/jsrpc-alternative.md)。

### sdenv 方案

基于魔改 jsdom + C++ V8 Addon，在 Node.js 中提供接近真实浏览器的环境。

核心优势：
- `document.all` 通过 `MarkAsUndetectable()` 完美还原
- Canvas API 集成 canvas 包，支持2d/webgl
- eval 作用域修复

适用场景：快速验证站点类型、采集参考数据、不需要URL后缀的GET/POST请求。

### 切换信号

遇到以下情况应考虑切换：
- 补环境轮次 > 5 仍无法通过格式校验
- 遇到 VMP opcode 级检测（外部hook全部无效）
- `document.all` 检测无法绕过且无法编译C++ Addon
- Worker/WebRTC/AudioContext 等深层检测成本过高

## 最小因果单元原则

每次补丁只补当前 first divergence 对应的最小因果单元，不机械打地鼠。

| 观测现象 | 缺口类型 | 补法 | 禁止 |
|---------|---------|------|------|
| navigator.userAgent返回undefined | 基础值缺失 | 补最小常量 | 不补整套navigator |
| document.createElement is not a function | 函数壳缺失 | setFuncNative补方法 | 不补完整DOM |
| Cannot read properties of undefined (reading 'style') | 返回对象缺失 | 补最小返回对象 | 不补无关字段 |
| localStorage.getItem is not a function | 宿主方法缺失 | 补storage shim | 不引入私有缓存 |
| Illegal invocation / brand check | 建模方式错误 | 修对象形态/this绑定 | 不乱包Proxy |
| crypto.subtle / TextEncoder缺失 | 平台API缺失 | 补最小API外壳 | 不臆造算法结果 |

## 补丁四步循环

1. **跑** run.js，记录报错和诊断报告
2. **读** 代理诊断日志，定位首个异常访问（first divergence）
3. **补** 只补当前 first divergence 对应的最小因果单元
4. **验** 立即重跑验证，确认该divegence消失后再处理下一个

不要在一轮中补多个不相关的问题——每个补丁应该是原子性的，可独立验证。

## 执行流程

### Step 1: 搭建项目结构 + 首次运行

编写最小 run.js，只包含必要存根：

```javascript
const env = require('./env_core');
const _process = process; // init()会隐藏process，提前保留引用

// 1. 构建最小存根
const fakeDocument = { /* ... */ };
const fakeNavigator = { /* ... */ };
const fakeLocation = { /* ... */ };

// 2. 组装window
const fakeWindow = {
    document: fakeDocument,
    navigator: fakeNavigator,
    location: fakeLocation,
};
fakeWindow.window = fakeWindow;
fakeWindow.self = fakeWindow;
fakeWindow.top = fakeWindow;
fakeWindow.parent = fakeWindow;
fakeWindow.globalThis = fakeWindow;

// 3. 初始化（Node泄露阻断 + 全局挂载）
env.init({
    window: env.createProxy(fakeWindow, 'window', 0),
    document: env.createProxy(fakeDocument, 'document', 0),
    navigator: env.createProxy(fakeNavigator, 'navigator', 0),
    location: env.createProxy(fakeLocation, 'location', 0),
});

// 4. 额外全局同步
// global.chrome = window.chrome;

// 5. 加载目标JS
require('./main.js');

// 6. 测试
console.log('签名函数:', typeof window.签名函数名);
```

运行 `node env/run.js`，读取诊断报告。

### Step 2: 诊断循环

按"诊断循环决策树"逐轮处理，每轮只改 run.js。

### Step 3: 封装验证

**sign.js**：

```javascript
const env = require('./env_core');
// ... 环境构建（与run.js相同）...
require('./main.js');

module.exports = function sign(url, data) {
    return window.签名函数名(url, data);
};
```

**验证顺序**：
1. **格式验证** — 签名长度、前缀与浏览器一致
2. **请求验证** — HTTP 200 + 业务数据返回

## 常见陷阱 (Pitfalls)

| 陷阱 | 表现 | 正确做法 |
|------|------|---------|
| 盲补环境 | 没有代理日志和first divergence就补宿主对象 | 先让环境自吐，再按诊断报告补 |
| 全量模拟 | 一次性补完整浏览器环境 | 逐项回填，最小因果单元 |
| 只补值不补结构 | 属性在实例上应该不在原型上，或反之 | 先补原型链，再补实例值 |
| 忽略描述符 | `enumerable/configurable/writable` 不一致 | 用 Object.defineProperty 显式对齐 |
| 忽略native toString | 手写函数被 `fn.toString()` 检测 | 用 setFuncNative 保护 |
| 忽略toString.toString | 深层检测 `fn.toString.toString()` | 同时保护 toString 本身 |
| 忽略加载顺序 | VMP初始化时环境未就绪 | 严格按铁律第4条顺序 |
| 忽略Node泄露 | process/Buffer/module等暴露 | init()后检查全局变量 |
| 忽略storage状态 | localStorage/sessionStorage有业务依赖值 | 从浏览器预置真实值 |
| 格式校验假阳性 | HTTP 200但签名是降级版 | 格式验证优先于请求验证 |
| 过度代理 | 目标站点检测Proxy | 先诊断再决定代理策略 |
| document.all当普通属性 | `typeof document.all` 返回 "object" | 必须走三路线方案 |

## References

遇到具体场景时按需读取，不要一次性全部装进上下文。

| 文件 | 何时读取 |
|------|---------|
| [browser-env-modules.md](references/browser-env-modules.md) | 需要补具体模块时，查找14个模块的接口契约和规范写法 |
| [special-cases.md](references/special-cases.md) | document.all、native toString深层检测、堆栈异常检测 |
| [node-detection-bypass.md](references/node-detection-bypass.md) | 签名降级，怀疑Node环境被检测 |
| [jsrpc-alternative.md](references/jsrpc-alternative.md) | 补环境成本过高，考虑JsRpc/sdenv替代路线 |
| [validation-methodology.md](references/validation-methodology.md) | 补环境完成后验证，回归测试，判断补丁是否够稳 |
