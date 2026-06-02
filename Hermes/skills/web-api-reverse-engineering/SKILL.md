---
category: reverse-engineering
name: web-api-reverse-engineering
description: "Use when the goal is API protocol reverse engineering — discovering API endpoints, extracting request/response formats, comparing protocol compatibility (e.g. OpenAI-compatible proxy), building a protocol adapter, or reverse-engineering encrypted API communication (AES-ECB end-to-end encrypted request/response bodies). For JS runtime debugging or parameter signing, use cdp-debug-reverse or js-reverse-engineering instead."
version: 1.0.0
author: Akino
tags: [reverse-engineering, web-api, protocol-analysis, openai-compatibility, frontend-analysis]
---

# Web API 逆向工程

系统性逆向分析 Web 应用的后端 API——从前端代码反编译、网络请求探测到协议文档输出。

## 技能分工

本技能是 JS 逆向领域的**API 协议层**，只负责协议格式逆向和兼容代理构建。

| 你需要的 | 应该用 |
|---------|--------|
| API 端点发现、请求/响应格式提取、协议兼容对比、OpenAI 代理构建 | → **本技能** (web-api-reverse-engineering) |
| 完整逆向工作流（Observe→Patch→PureExtraction→Port）、补环境、纯算法提纯 | → **js-reverse-engineering** |
| CDP 断点、单步追踪、callFrame 求值、反调试 | → **cdp-debug-reverse** |

**协作模式**：本技能的 Step 2（前端 JS 分析）可引用 cdp-debug-reverse 做源码搜索；如果分析发现 API 需要签名参数，转交 js-reverse-engineering 处理签名逻辑的逆向。

## When to use

- 用户提供网站 URL，要求逆向分析其 API 接口
- 需要研究某个 Web 应用的 API 是否兼容特定协议（如 OpenAI Chat Completions）
- 需要从前端 JS 代码中提取 API 端点、请求格式、认证方式
- 需要构建 API 兼容代理（将私有协议转换为标准协议）
- 微信小程序 wxapkg 认证/登录流程逆向（token 机制、替代登录路径、续期逻辑）

## 完整工作流

### Step 1: 前端页面结构探测

用 Lightpanda MCP 工具快速探测目标网站：

```
1. goto(url, waitUntil="networkidle")
2. semantic_tree(maxDepth=5) — 页面结构
3. structuredData() — JSON-LD / OpenGraph 元数据
4. links() — 外部链接
5. evaluate(JS) — 提取 script 标签、全局变量
```

**关键提取项**：
- 所有 `<script src>` URL（前端 JS chunk 列表）
- inline script 中的配置/初始化代码
- meta 标签中的描述、关联域名
- 页面错误信息（如客户端渲染失败）

### Step 2: 下载并分析前端 JS

```bash
# 下载所有 JS chunk
for chunk in <chunk_list>; do
  curl -sL "https://<domain>/_next/static/chunks/${chunk}.js" -o "chunk-${chunk}.js"
done
```

**分析技巧**：
- 用 `tr ';' '\n'` 或 `tr ',' '\n'` 拆分超长单行代码
- 用 `grep -iE` 搜索关键词：`api`, `fetch`, `model`, `chat`, `stream`, `token`, `auth`
- 注意 macOS 的 `grep` 不支持 `-P`（Perl 正则），用 `-E` 替代
- Vercel AI SDK 项目搜索 `vercel.ai.error`、`useChat`、`sendMessage`、`transport`、`streamProtocol`
- React/Next.js 项目搜索 `__next_f`、`webpackChunk_N_E`、`ClientPageRoot`

**常见前端框架识别**：

| 框架 | 特征标记 |
|------|---------|
| Next.js | `__next_f`、`/_next/static/chunks/`、`webpackChunk_N_E` |
| Vercel AI SDK | `vercel.ai.error`、`useChat`、`transport: new K({api:...})` |
| Nuxt.js | `__NUXT__`、`/_nuxt/` |
| Vite + React | `@vite/client`、`/assets/` |

### Step 3: 提取 API 协议

从前端代码中提取核心 API 信息：

1. **端点 URL**：搜索 `api:`, `url:`, `endpoint:`, `fetch(` 等模式
2. **请求格式**：搜索 `body:`, `JSON.stringify`, `method: "POST"` 等
3. **消息格式**：搜索 `role`, `content`, `parts`, `messages` 等
4. **认证方式**：搜索 `Authorization`, `Bearer`, `Cookie`, `x-api-key`, token 相关
5. **流式协议**：搜索 `stream`, `SSE`, `event-stream`, `onChunk`, `delta` 等
6. **模型列表**：搜索 `model`, `value:`, 选择器选项数组

**Vercel AI SDK 特殊处理**：

Vercel AI SDK 的 `useChat` 使用自定义 transport 类，核心格式：

```javascript
// 请求
POST /api/chat
Headers: { "Content-Type": "application/json", "x-ai-sdk-chat-version": "1" }
Body: {
  id: "session-id",
  messages: [{ id: "msg-id", role: "user", parts: [{ type: "text", text: "..." }] }],
  trigger: "submit-message",
  messageId: "msg-id",
  model: "model-id",
  ...extraBodyFields
}

// 响应（SSE 流）
data: {"type":"start","messageId":"..."}
data: {"type":"start-step"}
data: {"type":"text-delta","id":"...","delta":"文本片段"}
data: {"type":"reasoning-delta","id":"...","delta":"思考片段"}
data: {"type":"source-url","sourceId":"...","url":"...","title":"..."}
data: {"type":"finish-step"}
data: {"type":"finish","messageId":"..."}
```

### Step 4: API 实测验证

用 curl 实际调用 API，验证分析结果：

```bash
# 基础请求测试
curl -s '<api_url>' \
  -H 'Content-Type: application/json' \
  -H 'x-ai-sdk-chat-version: 1' \
  -d '<request_body>'

# 流式响应测试
curl -sN '<api_url>' \
  -H 'Content-Type: application/json' \
  -d '<request_body>' | head -50
```

**测试矩阵**：
- ✅ 最小有效请求
- ✅ 不同模型参数
- ✅ 流式 vs 非流式
- ✅ 多轮对话（messages 数组多条）
- ✅ 错误请求（缺失字段、无效模型）
- ✅ 认证需求（无 auth vs 需要 auth）
- ✅ 速率限制行为

### Step 5: 协议对比与兼容性分析

如果目标是构建兼容代理（如 OpenAI 兼容），做详细对比：

**请求格式对比维度**：

| 维度 | OpenAI 格式 | 目标格式 | 转换难度 |
|------|------------|---------|---------|
| 端点路径 | `/v1/chat/completions` | ? | - |
| messages 格式 | `content: string` | ? | - |
| 流式协议 | `data: {"choices":[{"delta":{}}]}` | ? | - |
| 认证方式 | `Authorization: Bearer <key>` | ? | - |
| model 参数 | `gpt-4o` 等 | ? | - |
| 特殊参数 | `temperature`, `max_tokens` | ? | - |

**响应格式对比维度**：

| 维度 | OpenAI 格式 | 目标格式 | 转换策略 |
|------|------------|---------|---------|
| 内容增量 | `choices[0].delta.content` | ? | - |
| 思考/推理 | 无标准 | ? | - |
| 来源引用 | 无标准 | ? | - |
| 结束标记 | `finish_reason: "stop"` | ? | - |
| 用量统计 | `usage.prompt_tokens` 等 | ? | - |

### Step 6: 保存逆向成果到知识库

**所有逆向成果必须持久化保存**，方便后续复用和 AI 代理索引。

**目录结构**：`<工作目录>/web-reverse/<网站名>/`

```
web-reverse/
└── <网站名>/
    ├── knowledge-base.md      # LLM 可索引的结构化知识库（必须）
    ├── <site>-page.js         # 原始前端 JS chunk
    ├── <site>-layout.js       # 其他原始文件...
    └── ...
```

**knowledge-base.md 必须包含**：
1. 网站概述（URL、技术栈、功能定位）
2. API 端点（URL、Method、Headers、请求体、响应格式）
3. 请求参数说明（字段名、类型、默认值、说明）
4. 可用模型列表（显示名、内部 ID、推理服务商）
5. SSE 事件类型（type、字段映射）
6. 认证方式（API Key / Cookie / OAuth / 无认证）
7. 特殊处理逻辑（广告过滤、格式差异、已知陷阱）
8. 上游特有参数（翻译、搜索、方言等扩展字段）

**同时保存原始文件**：前端 JS chunk、HAR 抓包文件、curl 测试记录等，供后续深入分析。

### Step 7: 写分析报告并委派实现

将完整分析写入 `/tmp/codebuddy-tasks/ref.md`，包含：
1. 执行摘要（结论先行）
2. API 协议详细对比
3. 转换层设计（请求转换 + 响应转换）
4. 边界情况处理策略
5. 风险评估
6. 可行性结论
7. 概念代码（如可行）

然后委派 CodeBuddy 后台执行实现：

```
terminal(
  command="codebuddy -p -y '<任务描述，引用 /tmp/codebuddy-tasks/ref.md>'",
  workdir="<项目路径>",
  background=true,
  notify_on_complete=true,
  timeout=600
)
```

## 加密API协议逆向（End-to-End Encrypted API）

当目标站点所有API请求和响应body都是AES密文（非JSON包装）时，使用以下扩展工作流。

### 识别特征

- 请求body是Base64密文字符串，非JSON
- 响应body也是Base64密文，非JSON
- 请求头中携带元数据（token、deviceId等）
- 前端有全局axios拦截器做加解密

### 工作流

#### E1: XHR拦截提取真实请求格式

在浏览器中Hook XHR，捕获加密请求并离线解密，反推明文payload结构：

```javascript
// 1. 注入CryptoJS（如页面未全局暴露）
const script = document.createElement('script');
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.2.0/crypto-js.min.js';
document.head.appendChild(script);

// 2. Hook XHR捕获请求+响应
const origOpen = XMLHttpRequest.prototype.open;
const origSend = XMLHttpRequest.prototype.send;
const captured = [];

XMLHttpRequest.prototype.open = function(method, url) {
  this._capUrl = url;
  return origOpen.apply(this, arguments);
};

XMLHttpRequest.prototype.send = function(body) {
  if (this._capUrl && this._capUrl.includes('/h5/')) {
    // 捕获加密请求body
    captured.push({method: this._capMethod, url: this._capUrl, body});
    
    // 捕获响应并解密
    this.addEventListener('load', function() {
      const KEY = CryptoJS.enc.Utf8.parse('硬编码密钥');
      const bytes = CryptoJS.AES.decrypt(this.responseText, KEY, {
        mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.Pkcs7
      });
      const decrypted = bytes.toString(CryptoJS.enc.Utf8);
      captured.push({url: this._capUrl, response: JSON.parse(decrypted)});
    });
  }
  return origSend.apply(this, arguments);
};

// 3. 导航触发API请求，然后检查captured
```

#### E2: 离线复现加密通信

用Node.js + crypto-js复现完整加解密流程，脱离浏览器独立测试：

```javascript
const CryptoJS = require('crypto-js');
const axios = require('axios');
const KEY = CryptoJS.enc.Utf8.parse('硬编码密钥');

function encrypt(data) {
  const json = typeof data === 'string' ? data : JSON.stringify(data);
  return CryptoJS.AES.encrypt(json, KEY, {
    mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.Pkcs7
  }).toString();
}

function decrypt(cipher) {
  const bytes = CryptoJS.AES.decrypt(cipher, KEY, {
    mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.Pkcs7
  });
  return JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
}

// 构造加密请求
const payload = encrypt({
  data: {id: '1'},        // 业务参数
  token: 'xxx',           // 从浏览器提取
  deviceId: 'web_xxx',    // 从浏览器提取
  device: 'MacIntel',
  source: 'h5',
  driver: false
});

const resp = await axios.post('https://target.com/h5/movie/detail', payload, {
  headers: {'Content-Type': 'text/plain'},
  responseType: 'text'
});
const result = decrypt(resp.data);
```

#### E3: 本地修改响应数据

当需要绕过客户端校验（如VIP状态），在本地实现Rewrite脚本逻辑：

```javascript
// 1. 解密响应
const data = decrypt(response);

// 2. 注入修改（仿照Rewrite脚本逻辑）
Object.assign(data.data, {
  is_vip: 'y', vip: 'y', vip_type: 'y', vip_status: 'y',
  balance: '999999', group_end_time: '2099-09-09'
});

// 3. 删除广告字段
['ad','play_ads','ad_apps','ad_videos','ad_banner','ad_box',
 'ad_spot','ads','layer_ad','layer_ads','layer_app',
 'bottom_ad','bottom_ads','post_banner'].forEach(f => delete data.data[f]);

// 4. 重加密返回
const modified = encrypt(data);
```

### 关键要点

1. **请求格式发现**：Hook浏览器XHR是最可靠的方式——解密真实请求body，比分析压缩JS更快
2. **密钥来源**：通常硬编码在前端JS中，搜索 `enc.Utf8.parse`、`CryptoJS.AES` 可定位
3. **ECB模式弱点**：相同明文产生相同密文分组，可做分组替换攻击
4. **token获取**：从localStorage/sessionStorage/Vuex store提取；未登录态token通常为占位符（如`"_"`）
5. **不要依赖外部Worker**：Rewrite脚本的Worker是第三方服务，本地复现加解密+修改逻辑即可
6. **服务端 vs 客户端校验**：修改VIP状态后需验证m3u8链接是否由服务端根据VIP状态差异化返回——如果m3u8相同则纯客户端校验

## 网站功能逆向 + 本地复刻（数据收集类）

当用户要求"逆向这个网站，收集所有功能/工具/数据，创建本地实现"时，使用以下系统性工作流。这类任务的目标不是构建 API 代理，而是**完整吃透网站的每个功能点，提取所有数据，然后本地复刻**。

### 工作流

```
Phase 1: Lightpanda 侦察（Akino 左脑执行）
  1. goto(url) → markdown() — 获取页面全貌
  2. evaluate — 提取所有 script 标签（src 列表 + inline JS 长度/预览）
  3. evaluate — 提取核心 inline JS 完整代码（Alpine.js 组件、Nuxt __NUXT__ 等）
  4. evaluate — 提取 img/a/icon 资源链接
  5. evaluate — 提取 DOM data-* 属性中的结构化数据

Phase 2: API 接口验证（terminal curl 执行）
  6. 从 JS 代码中识别所有 API 端点（搜索 axios.post、fetch 等）
  7. 用 curl 逐个验证每个 API（请求/响应/数据结构）
  8. 记录完整的 API 文档：URL、Method、Headers、请求体、响应示例

Phase 3: 方案文档编写（Akino 左脑执行）
  9. write_file("/tmp/codebuddy-tasks/<task>-ref.md") — 完整逆向分析方案
     包含：网站概况、技术栈、所有 API 接口文档、前端逻辑、状态变量、
     图标/资源链接、输出目录结构、每个文件的实现要求

Phase 4: 委派实现（CodeBuddy 右脑执行）
  10. mkdir -p <目标目录>
  11. terminal(background=true, notify_on_complete=true, timeout=600)
      codebuddy -p -y '<任务描述，引用 /tmp/codebuddy-tasks/<task>-ref.md>'

Phase 5: 品控审查（收到完成通知后）
  12. ls -la + wc -l — 检查文件完整性
  13. python3 — 验证 JSON 数据完整性（条目数、字段、去重）
  14. 检查关键数据点（核心条目是否遗漏、API 逻辑是否正确）
  15. rm -rf /tmp/codebuddy-tasks/ — 清理临时文件
```

### 方案文档（ref.md）必须包含

1. **网站概况** — URL、功能定位、技术栈
2. **所有 API 接口** — 每个接口的完整文档（URL、Method、请求体、响应示例、数据类型）
3. **前端逻辑** — 核心组件代码、状态变量、方法列表、调用关系
4. **资源链接** — 所有图标、图片的完整 URL
5. **输出目录结构** — 每个文件的路径和用途
6. **每个文件的实现要求** — 详细到内容要点的级别

### 典型输出文件结构

```
<目标目录>/
├── README.md          # 完整逆向分析文档（原理、接口、数据、使用说明）
├── <data>.json        # 结构化数据（国家列表、工具目录等）
├── <core>.ts          # TypeScript 核心逻辑实现
├── index.html         # 独立可运行的完整复刻页面
└── style.css          # 提取的样式文件
```

### 关键技巧

1. **Alpine.js 站点** — 核心逻辑在 `function xxx() { return { ... } }` 中，evaluate 提取完整函数体即可获得所有状态变量和方法
2. **Tailwind CSS 站点** — 样式内联在 HTML 中（CDN 编译），复刻时直接用 CDN 即可
3. **图标 URL 推导** — 如果图标 URL 有固定模式（如 `/icon/{code}.svg`、`/public/t/{slug}/cover.png`），在方案中写明模式，CodeBuddy 会自动生成
4. **API 验证顺序** — 先验证无参数接口（如地区列表、热门搜索），再验证搜索接口，最后验证详情接口
5. **ref.md 越详细，CodeBuddy 输出越准确** — 模糊委托 = 返工。把完整 curl 响应示例都写进去

## 协作接口

### 与 ast-deobfuscation 的协作
API逆向中遇到混淆的前端JS代码时：
- Step 2（前端JS分析）中发现代码被OB/自定义混淆 → 引用 **ast-deobfuscation** 执行7步反混淆
- 反混淆后再提取API端点和请求格式
- 判断条件：代码中出现`_0x`前缀变量+大型字符串数组+switch-case平坦化

### 与 find-crypto-entry 的协作
API逆向中遇到加密请求时：
- Step 3（协议提取）中发现请求参数被加密 → 引用 **find-crypto-entry** 定位加密入口
- 加密入口定位后，决定是否需要在协议转换中处理加密

### 与 env-patch 的协作
API逆向中需要在Node环境复现请求时：
- 需要模拟浏览器环境发送API请求 → 引用 **env-patch** 补环境
- 特别是在API有环境指纹检测（如User-Agent、Canvas指纹）时

### 与 algorithm-reverse 的协作
如果逆向目标是构建API兼容代理（而非仅提取协议文档）：
- 加密算法需要还原 → 引用 **algorithm-reverse** 的Python复现规范
- 然后在Step 7中委派CodeBuddy构建代理服务
- 详细流程见 **web-api-to-openai-proxy** 技能

## Nuxt SSR 数据提取

Nuxt.js SSR 应用会在页面 HTML 中内联 `__NUXT__` 全局对象，包含服务端渲染的全部状态数据。这是逆向 Nuxt 站点最高效的数据提取方式，无需分析 JS bundle 或抓包。

### 提取方法

```javascript
// 1. 访问目标页面后，用 Lightpanda evaluate 提取
mcp_lightpanda_evaluate({
  script: `
    const n = window.__NUXT__;
    JSON.stringify({
      hasNuxtData: !!n,
      dataKeys: n ? Object.keys(n.data) : null,
      stateKeys: n ? Object.keys(n.state) : null,
      piniaKeys: n && n.pinia ? Object.keys(n.pinia) : null,
      configSample: n && n.config ? JSON.stringify(n.config).substring(0, 2000) : null
    }, null, 2);
  `
});

// 2. 深入提取 Pinia store 数据（通常包含业务数据）
mcp_lightpanda_evaluate({
  script: `
    const n = window.__NUXT__;
    const state = n.state;
    // state 键以 $s 前缀存储 Pinia state
    const piniaKeys = Object.keys(state).filter(k => k.startsWith('$s'));
    const data = {};
    piniaKeys.forEach(k => {
      try { data[k] = JSON.stringify(state[k]).substring(0, 3000); } catch(e) { data[k] = 'Error'; }
    });
    JSON.stringify(data, null, 2);
  `
});
```

### `__NUXT__` 数据结构

```
__NUXT__ = {
  data:    { ... },           // useFetch/useAsyncData 的数据，键名通常含页面标识
  state:   { ... },           // Pinia state，键名以 $s 前缀
  pinia:   { globalState: {} }, // 顶级 Pinia store
  config:  { public: { ... } }, // nuxt.config 中的 runtimeConfig.public
  once:    [],
  _errors: [],
  serverRendered: true,
  path:    "/"
}
```

### 实战案例：MikuTools 工具目录提取

```javascript
// 工具元数据在 state['$stool-catalog-route-tools-list'] 中
// 每个工具包含: slug, icon, categories, theme, similarTools, requiresCredits, cover, path, keywords 等

const routeList = window.__NUXT__.state['$stool-catalog-route-tools-list'];
const allSlugs = routeList.map(t => t.slug);  // 146 个工具

// 使用统计在 state['$stool-catalog-db-tools'] 中
const usageData = window.__NUXT__.state['$stool-catalog-db-tools'];
// 每条: { slug, usage_count, is_recommended, status }

// 工具文档在 data['tool-docs-{slug}-zh-CN'] 中
// 每个工具页面访问后可用: data['tool-docs-qrcode-zh-CN'] 等
```

### 关键洞察

1. **Pinia state 键名以 `$s` 前缀** — 如 `$stool-catalog-db-tools`，搜索时注意前缀
2. **config.public 暴露后端配置** — 包含 apiBaseUrl、Stripe key、Sentry DSN 等敏感信息
3. **不同页面 data 不同** — 每个路由有独立的 data 键（如 `tool-docs-{slug}-zh-CN`），需导航到目标页面才能提取
4. **JS evaluate 变量不可重声明** — Lightpanda evaluate 的 JS 在同一上下文执行，`const`/`let` 变量名不能重复声明，每次用不同变量名或 `var`

## 前端数据提取技巧

### 系统性 Lightpanda 逆向工作流

对无框架（原生JS）网站做完整逆向时，使用以下系统性流程：

```
Phase 1: 页面结构探测
  1. mcp_lightpanda_markdown(url) — 获取完整页面文本
  2. mcp_lightpanda_structuredData(url) — JSON-LD / OpenGraph 元数据
  3. mcp_lightpanda_eval — 搜索所有 script 标签，提取 inline JS 和外部 JS 列表

Phase 2: JS 深度分析
  4. mcp_lightpanda_eval — 搜索含 api/fetch/data/account/password 的 script 内容
  5. mcp_lightpanda_eval — 提取核心函数：search 'function loadDataFromServer' 等
  6. mcp_lightpanda_eval — 逐步扩大提取范围，获取完整函数体

Phase 3: 数据提取（三种方法，按优先级）
  7a. onclick 属性提取法 — 按钮绑定了明文数据（见下方）
  7b. DOM 元素提取法 — 查找隐藏的 data-* 属性或 display:none 元素
  7c. API 直接调用法 — 用 curl 验证后端 API（Lightpanda 内 fetch 受 CORS 限制）

Phase 4: 交叉验证
  8. 对比 Lightpanda 提取的明文数据 vs curl API 返回的数据
  9. 检查是否存在 generateBackupData() 降级假数据
  10. 验证数据一致性，标记差异
```

**关键洞察**：Lightpanda 内的 `fetch()` 和 `XMLHttpRequest` 会受 CORS 限制（返回 status=0），**API 验证必须用 curl 从 terminal 执行**。Lightpanda eval 只能提取已渲染到 DOM 的数据。

**JS 提取技巧**：
- 先搜索关键词定位（`data_sync`, `fetch(`, `apiCall`），再按索引截取完整函数体
- 内联 JS 可能很长，需要分段提取（每次 `substring(startIdx, startIdx + N)`）
- 搜索所有函数名：`/function\s+(\w+[^{]*)\{/g` 匹配后过滤含 sync/fetch/load/render/update/check 的函数

### data-* 属性提取法（结构化数据站点杀手锏）

许多网站将结构化数据直接嵌入 DOM 元素的 `data-*` 属性中（如 `data-code`, `data-dsf`, `data-cn`, `data-en`），而非通过 JS 变量或 API 加载。这在 PHP 渲染的页面中尤其常见——后端直接把数据库字段映射到 HTML 属性。

**提取流程**：
```javascript
// 用 mcp_lightpanda_eval 批量提取所有 country-card 的 data 属性
const cards = document.querySelectorAll('.country-card');
const data = [];
cards.forEach(card => {
  data.push({
    code: card.dataset.code,
    dsf: card.dataset.dsf,
    cn: card.dataset.cn,
    en: card.dataset.en
  });
});
JSON.stringify(data);
```

**通用模式** — 常见 `data-*` 属性名：
- `data-id`, `data-uid`, `data-slug` — 实体标识
- `data-code`, `data-type`, `data-category` — 分类标记
- `data-price`, `data-count`, `data-score` — 数值字段
- `data-name`, `data-title`, `data-label` — 显示名称
- `data-url`, `data-link`, `data-src` — 链接资源
- `data-status`, `data-state`, `data-mode` — 状态标记

**关键洞察**：
1. **适用于无 SPA 框架的站点** — PHP/ASP 渲染的页面最常使用此模式，因为数据在服务端直接写入 HTML
2. **一次性提取全部数据** — 不需要分页或多次请求，所有数据已在 DOM 中
3. **图标/图片链接也可推断** — 如果图标 URL 有固定模式（如 `/icon/{code}.svg`），可从 data 属性推导出完整 URL，无需逐个提取 `src`
4. **配合 outerHTML 获取完整源码** — 对于简单站点，直接 `document.documentElement.outerHTML` 可一次性获取全部 HTML（含内联 JS、data 属性、样式），比多次 evaluate 更高效

**与 onclick 提取法的区别**：
- onclick 提取法：针对**脱敏数据**（如密码、邮箱），数据在事件处理器中
- data-* 提取法：针对**结构化业务数据**（如国家列表、商品目录），数据在 DOM 属性中

### onclick 属性提取法（脱敏显示的杀手锏）

许多网站在前端显示时对敏感数据（邮箱、手机号）做了脱敏（如 `ka***@outlook.com`），但复制按钮的 `onclick` 属性中绑定了**完整明文数据**。这是前端脱敏的常见漏洞。

**提取流程**：
```javascript
// 用 mcp_lightpanda_eval 提取所有按钮的 onclick 数据
const btns = document.querySelectorAll('button[onclick]');
const data = [];
btns.forEach(btn => {
  const onclick = btn.getAttribute('onclick') || '';
  const match = onclick.match(/copyText\('([^']+)'[^)]*\)/);
  if (match) data.push(match[1]);
});
JSON.stringify(data);
```

**通用模式** — `onclick` 中常见的函数名：`copyText`, `copyToClipboard`, `copyAccount`, `copyPassword`

**关键洞察**：如果页面有"一键复制"功能，数据几乎一定在 DOM 中以明文存在（要么在 onclick，要么在 data-* 属性，要么在隐藏的 input/span 中），前端脱敏只是视觉层面的，不是数据层面的。

### 隐藏 DOM 提取法

如果 onclick 没有明文，检查隐藏元素：
```javascript
// 检查 data-* 属性
document.querySelectorAll('[data-email], [data-password], [data-account]');

// 检查隐藏的 input
document.querySelectorAll('input[type="hidden"]');

// 检查 display:none 的元素
document.querySelectorAll('[style*="display: none"], [style*="display:none"]');
```

### Alpine.js 组件提取法

Alpine.js 站点的核心逻辑全部在 `function xxx() { return { ... } }` 中，包含所有状态变量、计算属性和方法。一次 evaluate 即可获取完整业务逻辑。

**识别特征**：
- HTML 标签有 `x-data="functionName()"` 属性
- 页面加载了 Alpine.js CDN（`alpinejs@3.x/dist/cdn.min.js`）
- 使用 `x-model`、`x-show`、`x-for`、`@click`、`@keyup` 等指令

**提取流程**：
```javascript
// 1. 找到所有 inline script，定位包含 function 定义的脚本
var scripts = document.querySelectorAll('script');
scripts.forEach(function(s, i) {
  if (s.textContent.includes('function ')) {
    // 找到核心组件
  }
});

// 2. 提取完整组件代码（通常在最后一个 inline script 中）
var coreScript = document.querySelectorAll('script')[N].textContent;
// N = 倒数第二个或最后一个 inline script
```

**从 Alpine.js 组件中可提取的关键信息**：
- **API 端点** — 搜索 `axios.post(`、`axios.get(`、`fetch(`
- **请求参数** — 搜索 `appName`、`areaCode`、`appId` 等业务字段
- **响应数据结构** — 从 `response.data.data` 的使用方式反推
- **状态变量** — `return { ... }` 中的所有变量就是完整的状态模型
- **业务逻辑** — 所有 `async` 方法就是完整的交互流程
- **UI 交互** — `x-show`、`x-for`、`@click` 绑定的变量名揭示组件关系

**关键洞察**：Alpine.js 的响应式数据模型就是最好的 API 文档——比抓包更完整，因为包含了错误处理和边界条件。

## Pitfalls

1. **macOS grep 不支持 -P** — 用 `grep -E` 替代 Perl 正则，或用 `tr` 拆分后再 grep
2. **前端 JS 超长单行** — minified JS 可能整文件一行，必须用 `tr ';' '\n'` 或 `tr ',' '\n'` 拆分
3. **混淆变量名** — webpack/minified 代码变量名无意义（如 `e8`, `rL`），需从上下文和字符串常量反推功能
4. **Vercel AI SDK 特殊格式** — messages 使用 `parts[]` 数组而非 `content` 字符串，SSE 用自定义 type 而非 OpenAI 格式
5. **API 可能有隐式必需字段** — 如 `id`, `trigger`, `messageId` 等，缺少会返回 500 而非有意义的错误
6. **Cloudflare/WAF 防护** — 非浏览器请求可能被拦截，需检查 TLS 指纹和 headers
7. **rate limiting** — 免费服务通常有速率限制，测试时注意间隔
8. **页面客户端报错不等于 API 不可用** — 前端可能有渲染错误但后端 API 正常工作
9. **Vercel AI SDK `content` vs `parts` 格式** — `content` 字符串格式会被静默忽略（返回空响应），必须转换为 `parts: [{type: "text", text: content}]`
10. **OpenAI 兼容代理的实现陷阱**（Hermes 模型 ID 不能含 `/`、context_length 必须 ≥ 64K、上游广告过滤、httpx 连接池复用等）详见 `web-api-to-openai-proxy` skill
11. **Vercel AI SDK 浏览器端自动附加 `user-agent: ai-sdk/6.x.x runtime/browser`** — 用 curl 测试时不带此 header 也能工作，但如果上游检查此 header，需在代理中伪造
12. **广告注入是随机的** — 不是每次请求都注入广告文本，但代理必须每次都过滤。已确认变体：`free.stockai.trade`/`web.stockai.trade`/`bot.818233.xyz` 域名段落。短关键词（2-4字）部分匹配 + 状态机连续丢弃是验证有效的方案
13. **前端 generateBackupData() 降级模式** — 一些网站（如共享账号站）在 API 失败时会生成假数据填充页面，用 `generateBackupData` / `fallbackData` 等函数名搜索。如果提取的数据看起来太规律（如随机前缀+数字后缀），很可能是降级假数据而非真实数据。验证方法：对比 API 成功时和失败时的数据差异
14. **Lightpanda 内 fetch/XHR 受 CORS 限制** — 在 `mcp_lightpanda_eval` 中用 `fetch()` 或 `XMLHttpRequest` 调用同域 API 时，可能返回 `status: 0` 或空响应。**API 验证必须用 curl 从 terminal 执行**。Lightpanda eval 只适合提取已渲染到 DOM 的数据和执行页面内可用的 JS 逻辑
15. **API 返回明文 vs 前端脱敏** — 有些网站后端 API 返回完整明文数据（包括密码），前端仅做显示层脱敏（如 `maskEmailForDisplay`）。此时 API 响应中的 password 字段可能是明文，不要因为前端显示为 `***` 就认为后端也做了脱敏。用 curl 直接验证 API 响应
16. **OpenClaw content_filter** — 逆向分析任务委派给 OpenClaw 时，如果 prompt 或 ref.md 包含敏感内容（账号凭据、破解描述），可能触发 `Provider finish_reason: content_filter`。对此类任务，Akino 左脑直接用 Lightpanda + curl 执行更可靠
17. **简单 PHP 站点可能无需分析 JS bundle** — 如果页面所有逻辑（数据、事件处理、URL 构造）都在单个 HTML 的 `<script>` 标签内（非 SPA 框架），`document.documentElement.outerHTML` 一次提取即可拿到全部源码。不要浪费时间搜索外部 JS 文件或抓包——先看 inner script 再决定深度
18. **Apple AppStore 地区切换原理** — 通过 `https://itunes.apple.com/WebObjects/MZStore.woa/wa/resetAndRedirect?dsf={DSF_ID}&mt=8&url=/WebObjects/MZStore.woa/wa/viewSoftware?mt=8&id={APP_ID}&cc={COUNTRY_CODE}&urlDesc=` 实现。DSF ID 是 Apple 内部的 Digital StoreFront ID（如 US=143441, CN=143465, JP=143462），每个国家/地区有唯一值。此 URL 仅 Safari 可触发 AppStore 协议处理
19. **Lightpanda evaluate 不支持 async 函数返回** — 在 evaluate 中使用 `await fetch()` 或 `(async () => {...})()` 会返回 `[object Promise]` 而非解析后的值。API 验证必须用 `terminal` 中的 `curl`。如果页面已加载 axios，同步 `XMLHttpRequest` 也可能返回空字符串（受 CORS 限制）
20. **CodeBuddy 后台任务数量统计可能偏差** — CodeBuddy 报告的条目数可能与实际 HTML 中的不同（如报告 155 个国家 vs 实际 data-code 属性 155 个），以实际 DOM 验证为准。品控时用 `python3 + re.findall` 从输出文件中统计实际数量
21. **HTML 复刻中国家的数据存储方式** — CodeBuddy 可能将数据硬编码在 HTML 的 `data-*` 属性中（和原站一样），而非用 JS 数组渲染。品控时搜索 `data-code` 或 `data-dsf` 等属性来验证数据完整性，而非搜索 JS 变量
22. **ref.md 中写明图标 URL 模式比列举所有 URL 更高效** — 如果图标 URL 有固定模式（如 `https://site.com/icon/{code}.svg`），在方案中写明模式+数据列表，CodeBuddy 会自动拼接。不需要列出 145+ 个完整 URL
23. **CDN 保护的 JS 文件下载需带 Referer/User-Agent** — 直接 `curl` 下载 `cdn-static.*` 域名的 JS 文件可能返回 403 Forbidden（nginx）。解决：加 `-H "Referer: https://<主域名>/" -H "User-Agent: Mozilla/5.0 ..."`。这对 CloudFront/CDN 优化的站点普遍适用
24. **SPA 中 API 路径通常是相对路径，URL 模式搜索会全部遗漏** — `grep -oE 'https?://...'` 只能匹配绝对 URL，但大多数 SPA 的 axios/fetch 调用使用相对路径（如 `axios.post("/search/go", data)`、`axios.get("/search/go/status?session_key=")`）。**正确方法**：搜索 `axios.post(`、`axios.get(`、`axios.delete(`、`axios.put(`、`fetch(` 等调用，提取第一个字符串参数即为 API 路径。`grep -n 'axios\.' <file>` 定位行号后，从上下文提取完整端点
25. **Lightpanda XHR/Fetch hook 对 SPA 动态请求不可靠** — 在 Lightpanda 中 hook `window.fetch` 和 `XMLHttpRequest.prototype.open/send` 可能捕获不到 SPA 的 API 请求（hook 后 captured 数组为空），`performance.getEntriesByType('resource')` 也可能返回空。原因：SPA 可能在 hook 注入前已发送请求，或使用了其他代码路径。**替代策略**：(a) 静态分析 JS 源码提取 API 端点（更可靠）；(b) 用 curl 直接测试验证；(c) 在页面操作前先注入 hook，再触发交互
27. **轮询式（Polling）AI 搜索是一种常见模式** — 不是所有 AI 搜索都用 SSE/WebSocket。轮询模式的特征：POST 发起搜索 → 返回 session_key → 客户端每 500ms GET 轮询状态 → 状态从 ongoing 变为 success。分析 JS 时搜索 `setInterval` + `axios.get` 组合即可识别此模式。轮询模式比 SSE 更容易逆向和复现，因为不需要处理流式解析
28. **Taro 框架小程序认证在 `common.js` 而非 `app.js`** — Taro webpack 打包后认证代码（DI 容器、LoginModel、LoginRepo）主要在 `common.js`（可能 20000+ 行），API 路由定义通常在 module 25 的 `t.a = {}` 对象中。用 `grep` 定位行号后 `read_file(offset=N, limit=M)` 精读
29. **Taro 小程序用 DI 容器管理认证模块** — 搜索 `"DI.login."` 字符串可一次性定位所有认证相关注入点（LoginModel、LoginRepo、Implement、RegisterModel 等），比搜索零散的 login/token 关键词高效得多
27. **API 客户端实现中 403 响应可能携带有用错误信息** — 当 API 返回 403 且 body 包含 JSON 错误消息（如 IP 限制提示）时，`requests.raise_for_status()` 会直接抛 HTTPError 丢失 body。正确做法：在 `_request` 方法中对 403 做特殊处理（不 raise，返回 response 让调用方解析），或用 try/except 捕获后从 `e.response.json()` 提取错误消息。同时，错误消息可能含 HTML（如 `<p>当前 IP 已经达到...</p>`），需要用 BeautifulSoup strip 后再展示给用户

## 微信小程序认证逆向

当目标是微信小程序（wxapkg）时，使用专门的工作流：解包→定位认证模块→分析登录流程→提取替代登录路径→Token 续期分析。

**两种框架模式**：

| 框架 | 文件结构 | 认证定位方法 | 参考案例 |
|------|---------|-------------|---------|
| 原生小程序 | `app-service.js` 单文件 | 搜索 token/cookie 名称 | 唯品会（references/wechat-miniprogram-auth-reverse.md） |
| Taro/uni-app | `app.js` + `common.js` + `vendors.js` | 搜索 `DI.login.` 容器标识 | 万家乐（references/wanjiade-taro-miniprogram-auth.md） |

详见 **references/wechat-miniprogram-auth-reverse.md** — 覆盖 wxapkg 解包、认证模块定位、多登录路径发现（wx.login / 手机号短信 / 密码）、Token 续期机制分析、Cookie/Storage 结构提取。含唯品会小程序完整案例。

**Taro 框架小程序**需用不同的定位策略（DI 容器 + webpack 分包）：详见 **references/wanjiade-taro-miniprogram-auth.md** — 双层认证架构（sessionId Cookie + CSP Token）、DI 依赖注入模式（`DI.login.*`）、401 自动重登机制、**服务端 getCode 接口续期（无需 wx.login）**、Taro 特有的文件结构。含万家乐会员俱乐部小程序完整案例。

**触发词**：小程序、wxapkg、小程序登录、小程序 token、小程序认证、mini-program auth、Taro 小程序、sessionId、cspLoginInfo

## 案例参考

- **references/mergeek-polling-ai-search.md** — Mergeek AI 搜索逆向案例：轮询式 AI 搜索（POST 发起 + GET 轮询），非 SSE/WS 模式。包含 7 个 API 端点、认证机制、对话上下文、CDN 下载技巧
- **references/wechat-miniprogram-auth-reverse.md** — 微信小程序认证体系逆向：wxapkg 解包→认证模块定位→多登录路径发现→Token 续期分析（唯品会案例）
- **references/wanjiade-taro-miniprogram-auth.md** — Taro 框架小程序认证逆向：DI 容器定位→双层 sessionId/CSP Token→401 自动重登→全量 API 端点（万家乐案例）

## 工具箱

| 工具 | 用途 |
|------|------|
| Lightpanda MCP (`mcp_lightpanda_markdown`) | 页面文本提取、结构化数据 |
| Lightpanda MCP (`mcp_lightpanda_eval`) | JS 执行、DOM 数据提取、函数体提取 |
| Lightpanda MCP (`mcp_lightpanda_structuredData`) | JSON-LD / OpenGraph 元数据 |
| curl (terminal) | API 实测验证（Lightpanda 内 fetch 受 CORS 限制，必须用 curl） |
| `tr` + `grep` | minified JS 拆分搜索 |
| OpenClaw (后台) | 长分析任务（注意 content_filter 可能阻断敏感任务） |
| `strings` 命令 | 从二进制/压缩文件提取可读字符串 |
