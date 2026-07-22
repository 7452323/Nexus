---
name: js-reverse
description: JS逆向工程统一技能 (2026.07)。签名定位、加密参数分析、运行时采样、Node补环境复现、AST反混淆、JSVMP还原。整合反调试对抗、算法还原、JSRPC全自动方案、MCP Server 生态。适配 iSH/Alpine 环境。
category: reverse-engineering
tags: [js-reverse, signature, ast, jsvmp, anti-debug, env-patch, mcp]
---

# JS 逆向工程 (统一技能 2026.07)

> 前端 JS 签名定位、加密参数分析、运行时采样、Node 补环境复现。
> 适配 iSH/Alpine 环境：优先用 Minis 浏览器取证 + Python/Node 本地复现。

## 核心原则
- **Observe-first**：先观察，不猜环境
- **Hook-preferred**：优先 Hook，不打断点
- **Breakpoint-last**：最后才打断点
- **Rebuild-oriented**：目标是本地可复现
- **Evidence-first**：每一步都有证据支撑

## MCP Server 生态 (2026.07)

| MCP Server | Stars | 用途 | 特点 |
|------------|-------|------|------|
| **NoOne-hub/JSReverser-MCP** | 899⭐ | JS 逆向全流程 | 110 工具，3 模式 (kernel/compact/full) |
| **lwjjike/JSReverser-Strong-MCP** | 61⭐ | JSReverser 增强版 | 功能增强 |
| **zhizhuodemao/js-reverse-mcp** | — | AI Agent 设计 | 内置反检测，基于 chrome-devtools-mcp |
| **a0yark/js-reverse-mcp** | — | Pro fork | Patchright stealth + JSReverser 能力选择性移植 |
| **715494637/reverse-skill** | 283⭐ | Web JS 逆向 | 请求链证据化 + JSVMP/worker/WASM/webpack 壳层恢复 |
| **ChromeDevTools/chrome-devtools-mcp** | — | 官方 CDP | Google 官方 |

### JSReverser-MCP 工作流 (899⭐)
```
1. Page Observation → 确认请求、脚本、函数
2. Runtime Sampling → 最小化 Hook 采样
3. Evidence Capture → 结果写入 task artifact
4. Local Rebuild → 导出可复现工程
5. Environment Patching → Node 逐项补环境
6. Pure Extraction → env-pass 后纯算法提纯
```

暴露 35+ 工具：`start_reverse_task`, `orchestrate_reverse_task`, `run_reverse_agent`, `create_hook`, `inject_hook`, `get_hook_data`, `hook_function`, `trace_function`, `set_breakpoint_on_text`, `break_on_xhr`, `collect_code`, `understand_code`, `deobfuscate_code`, `risk_panel`, `export_rebuild_bundle` 等

### reverse-skill 工作流 (283⭐)
```
请求链证据化 → 写边界证明 → 壳层恢复(JSVMP/AST/worker/WASM) → 运行时对齐 → 检查点验证
```

## 四阶段工作流

### 1. Observe（页面观察）
工具：Minis 浏览器 navigate → get_readable → find_elements + execute_js 提取关键变量和函数

### 2. Capture（运行时采样）
工具：Minis 浏览器 execute_js 拦截 fetch/XHR + JSRPC WebSocket 远程调用

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
})();
```

### 3. Rebuild（本地复现）
补环境模板：
```javascript
const { JSDOM } = require('jsdom');
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'https://target.com', pretendToBeVisual: true,
});
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.location = dom.window.location;
const crypto = require('crypto').webcrypto;
global.crypto = crypto;
```

### 4. DeepDive（深度分析）
目标：去混淆、控制流还原、业务逻辑提纯

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
const ast = parser.parse(code);
traverse(ast, {
  VariableDeclarator(path) { /* 字符串数组旋转还原 */ },
  BinaryExpression(path) {
    if (t.isLiteral(path.node.left) && t.isLiteral(path.node.right)) path.evaluate();
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

### 路径A: 四板斧（轻量）
1. 数组解混淆 2. 常量折叠 3. 死代码删除 4. 控制流平坦化

### 路径B: 环境仿真（重量）
- jsdom 环境伪装 / Firefox + playwright / sdenv 纯 Node.js

## 瑞数绕过 (NEW 2026)

**工具链**：
- **warterbili/ruishu-re** — 瑞数反爬纯算逆向
- **pysunday/sdenv** — 补环境框架，瑞数 VMP 理论通杀

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
| request_correlation | 0.8 | 请求 body/header 出现函数名 |
| input_output_shape | 0.9 | 输入/输出符合加密特征 |
| module_export_score | 0.7 | 从 Webpack 模块导出 |
| verification_score | 1.0 | 真实样本验证通过 |

### Webpack 模块解析优先级
```
Priority 1: window.__webpack_require__
Priority 2: webpackChunk* hook push
Priority 3: require.c 遍历已加载 module cache
Priority 4: 离线解析 chunk factory (low confidence)
```

## 算法还原
| 算法类型 | 识别特征 | 还原方法 |
|---------|---------|---------|
| MD5 | 初始 IV 0x67452301 | Python hashlib |
| SHA-1 | 初始 IV 0xEFCDAB89 | Python hashlib |
| AES | S-box 常量表 | PyCryptodome |
| RSA | 大整数运算 + 0x10001 | 提取公钥/私钥 |
| TEA/XTEA | 0x9E3779B9 delta | Python struct |
| MT19937 | 0x6C078965 种子 | Python random |
| 自定义 | 混合以上 | 逐步还原 |

## 工具链
| 工具 | 用途 | iSH 可用 |
|------|------|---------|
| Minis browser_use | 页面取证、JS 执行 | ✅ |
| Node.js | 本地补环境复现 | ✅ |
| Python3 | 辅助脚本、加解密验证 | ✅ |
| Babel AST | JS 反混淆 | ✅ |
| js-beautify | 代码格式化 | ✅ |
| JSReverser-MCP | 逆向全流程 MCP | ✅ (需配置) |
| Chrome DevTools MCP | CDP 连接 | ✅ (需配置) |
| JSRPC (jxhczhl) | WebSocket 远程调用 | ✅ |

