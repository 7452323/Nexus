---
name: js-reverse
description: JS逆向工程统一技能。签名定位、加密参数分析、运行时采样、Node补环境复现、AST反混淆、JSVMP还原。整合反调试对抗、算法还原、JSRPC全自动方案。适配 iSH/Alpine 环境。
category: reverse-engineering
tags: [js-reverse, signature, ast, jsvmp, anti-debug, env-patch]
---

# JS 逆向工程 (统一技能)

> 前端 JS 签名定位、加密参数分析、运行时采样、Node 补环境复现。
> 适配 iSH/Alpine 环境：优先用 Minis 浏览器取证 + Python/Node 本地复现。

## 核心原则

- **Observe-first**：先观察，不猜环境
- **Hook-preferred**：优先 Hook，不打断点
- **Breakpoint-last**：最后才打断点
- **Rebuild-oriented**：目标是本地可复现
- **Evidence-first**：每一步都有证据支撑

## 四阶段工作流

### 1. Observe（页面观察）

目标：确认目标请求、相关脚本、候选函数。

工具：
- Minis 浏览器：navigate → get_readable → find_elements
- 用 execute_js 提取关键变量和函数
- 用 get_cookies 提取 Cookie

产出：
- 目标请求 URL 或特征
- initiator 线索
- 可疑脚本 URL
- 初始任务记录

### 2. Capture（运行时采样）

目标：对目标请求做最小侵入采样，拿到参数样例。

工具：
- Minis 浏览器 execute_js：拦截 fetch/XHR
- JSRPC WebSocket 远程调用（不补环境方案）

拦截模板：
```javascript
(function() {
  if (window.__JSRA_TRACE__) return;
  var TRACE = { requests: [], crypto: [] };
  window.__JSRA_TRACE__ = TRACE;
  
  var origFetch = window.fetch;
  window.fetch = function() {
    TRACE.requests.push({url: arguments[0], options: arguments[1]});
    return origFetch.apply(this, arguments);
  };
  
  var origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url) {
    TRACE.requests.push({method, url});
    return origOpen.apply(this, arguments);
  };
  
  crypto.subtle.digest = function(algorithm, data) {
    TRACE.crypto.push({type:'digest', algorithm: algorithm.toString()});
    return origDigest.apply(this, arguments);
  };
})();
```

### 3. Rebuild（本地复现）

目标：把页面证据整理成本地可迭代的 Node 复现材料。

规则：
- 本地补环境必须以页面观测证据为依据
- 不允许空想式补 `window/document/navigator/crypto`
- 每次只记录一个最小因果补丁决策

补环境模板：
```javascript
// Node.js 补环境模板
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'https://target.com',
  pretendToBeVisual: true,
});

// 按需补环境——只补页面实际用到的
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.location = dom.window.location;

// 补 crypto（如果页面用了）
const crypto = require('crypto').webcrypto;
global.crypto = crypto;
global.crypto.subtle = crypto.subtle;
```

### 4. DeepDive（深度分析）

目标：本地跑通后，做去混淆、控制流还原、业务逻辑提纯。

## AST 反混淆

### 反混淆四板斧（Babel AST）

1. **数组解混淆** — 旋转字符串数组还原
2. **常量折叠** — 计算常量表达式
3. **死代码删除** — 移除不可达分支
4. **控制流平坦化还原** — 还原 switch-case 嵌套

```javascript
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const t = require('@babel/types');

const code = `/* 混淆代码 */`;
const ast = parser.parse(code);

traverse(ast, {
  // 字符串数组旋转还原
  VariableDeclarator(path) {
    if (path.node.init && path.node.init.type === 'ArrayExpression') {
      // 识别字符串数组 + 旋转函数
    }
  },
  // 常量折叠
  BinaryExpression(path) {
    if (t.isLiteral(path.node.left) && t.isLiteral(path.node.right)) {
      path.evaluate();
    }
  },
});

const output = generate(ast).code;
```

### 混淆类型识别

| 混淆器 | 特征 | 识别方法 |
|--------|------|---------|
| obfuscator.io | 字符串数组+控制流平坦化 | 大数组 + switch-case 嵌套 |
| jsjiami.com V6 | toString 抗格式化 | 函数体正则校验 |
| jsjiami.com V7 | 增强保护 | 多层嵌套 + 反调试 |
| sojson | 简单字符串替换 | eval + 编码字符串 |
| JSFuck | `[]()!+` 编码 | 纯符号代码 |

## JSVMP 双路径分析

### 路径A: 四板斧（轻量，优先）
1. 数组解混淆
2. 常量折叠
3. 死代码删除
4. 控制流平坦化还原

### 路径B: 环境仿真（重量，路径A无效时）
- jsdom 环境伪装（喂入-截出）
- Firefox + playwright 真实浏览器
- sdenv 纯 Node.js

## JSRPC 全自动方案

不补环境、不还原算法、不反混淆——直接连真实浏览器调加密函数。

### 架构

```
Chrome DevTools MCP → 运行时 Hook 探针 → JSRPC WebSocket → Flask 代理 → Burp
```

### 7 维度评分系统

| 维度 | 权重 | 判定依据 |
|------|------|---------|
| name_score | 1.0 | 函数名包含 encrypt/sign/rsa/aes/md5 |
| source_keyword_score | 1.0 | 源码包含加密库调用 |
| runtime_stack_score | 1.0 | 调用栈关联到目标请求 |
| request_correlation | 0.8 | 请求 body/header 中出现函数名 |
| input_output_shape | 0.9 | 输入/输出符合加密特征 |
| module_export_score | 0.7 | 从 Webpack 模块导出 |
| verification_score | 1.0 | 真实样本验证通过 |

**阈值**: 总分 > 0.6 → 进入验证阶段

### Webpack 模块解析优先级

```
Priority 1: window.__webpack_require__ → 直接使用
Priority 2: webpackChunk* → hook push 等待 chunk 加载
Priority 3: require.c → 遍历已加载 module cache
Priority 4: 离线解析 chunk factory（实验性，标记 low confidence）
```

## 算法还原

| 算法类型 | 识别特征 | 还原方法 |
|---------|---------|---------|
| MD5 | 初始 IV 0x67452301 | Python hashlib 复现 |
| SHA-1 | 初始 IV 0xEFCDAB89 | Python hashlib 复现 |
| SHA-256 | 特定常量表 | Python hashlib 复现 |
| AES | S-box 常量表 | PyCryptodome 复现 |
| DES | 置换表 + S-box | PyCryptodome 复现 |
| RSA | 大整数运算 + 0x10001 | 提取公钥/私钥 |
| TEA/XTEA | 0x9E3779B9 delta | Python struct 复现 |
| MT19937 | 0x6C078965 种子 | Python random 复现 |
| 自定义 | 混合以上算法 | 逐步还原 |

## 工具链

| 工具 | 用途 | iSH 可用 |
|------|------|---------|
| Minis browser_use | 页面取证、JS 执行 | ✅ |
| Node.js | 本地补环境复现 | ✅ |
| Python3 | 辅助脚本、加解密验证 | ✅ |
| curl | HTTP 请求验证 | ✅ |
| Babel AST | JS 反混淆 | ✅ |
| js-beautify | 代码格式化 | ✅ |
| Chrome DevTools MCP | JSRPC 连接 | ✅ (需配置) |
| JSRPC (jxhczhl) | WebSocket 远程调用 | ✅ |

## 路由上下文

**上游入口**: `skills/SKILL.md`（总控）、`routing.md`
**下游出口**:
- 需抓包 → `web-api-reverse/`
- 需 CF 绕过 → `cf-bypass/`
- 需代理脚本 → `proxy-script/`

## 任务完成自检

- [ ] 是否产出了可复现证据（命令/脚本/截图）？
- [ ] 是否基于 tool-index 使用了真实工具路径？
- [ ] 是否回写经验到 field-journal/？
- [ ] 是否记录了 siteKey/加密常量到本文件？

