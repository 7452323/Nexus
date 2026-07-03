---
name: jsrpc-auto-reverse
description: JSRPC + Flask + Burp autoDecoder 全自动 JS 逆向方案。Chrome DevTools MCP 连接真实浏览器 → 运行时 Hook 探针自动发现加密入口 → JSRPC WebSocket 调用 → Flask 代理 → Burp 无缝对接。源自 Fausto-404/js-reverse-automation--skill。
author: 7452323 (吸收自 Fausto-404)
category: reverse-engineering
tags:
  - jsrpc
  - autoDecoder
  - chrome-devtools-mcp
  - flask-proxy
  - burp
  - runtime-hook
  - webpack
---

# JSRPC Auto Reverse — JSRPC 全自动 JS 逆向方案

## 核心哲学
**不补环境、不还原算法、不反混淆**——直接连真实浏览器调加密函数。

## 适用场景
- 登录参数加密（RSA/AES/SM2/SM4/MD5/自定义编码）
- 数据爬取时响应内容加密
- 请求签名（sign/token/enc）
- 需要与 Burp 配合进行抓包、改包

## 体系架构

```
┌── 用户输入 ────────────────────────────────────────┐
│  Target URL: https://xxx.com/login                 │
│  Parameters: password                              │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 0: 输入校验 ──────────────────────────────┐
│  check_inputs.py → phase0_input.json               │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 1: 浏览器连接 + 请求复现 ─────────────────┐
│  Chrome DevTools MCP:                              │
│  ● navigate_page(initScript=运行时Hook探针)         │
│  ● 打开目标页面 → 触发目标动作 → 捕获网络请求       │
│  ● 锁定目标请求 URL/Method/Body/Headers            │
│  ● 运行时健康检测: probe_status                    │
│     ok → 正常 | partial → 标记 | timeout → 降级     │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 2: 加密入口发现 ──────────────────────────┐
│  ● 运行时 Hook 探针捕获 fetch/XHR/crypto 调用      │
│  ● 7 维度评分系统筛选候选函数                       │
│  ● 真实样本验证（评分 > 0.6 的候选）                │
│  ● 输出: encryption_candidates.json                 │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 2.5: Webpack 模块解析（可选） ────────────┐
│  优先级链（不跳级）:                                │
│  1. window.__webpack_require__                     │
│  2. webpackChunk* push hook                        │
│  3. require.c 遍历已加载模块                        │
│  4. 离线解析 chunk factory（标记 low confidence）   │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 3: 依赖提取 ──────────────────────────────┐
│  ● call_signature: args/returns/async              │
│  ● runtime: bind_this/bootstrap/globals            │
│  ● 输出: analysis_result.json                       │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 4: 代码生成 ──────────────────────────────┐
│  ├── jsrpc_inject.js — JSRPC 浏览器端注入代码       │
│  ├── flask_proxy.py — Flask 本地代理服务            │
│  └── burp-autodecoder.md — Burp 配置文档            │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 5: 浏览器注入 ────────────────────────────┐
│  ● 刷新页面清理旧 WebSocket                         │
│  ● 注入 Hlclient (JsEnv_Dev.js)                    │
│  ● inject jsrpc_inject.js → 注册加密函数           │
│  ● 验证: curl /list 确认 group 已注册               │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 6: 启动服务 ──────────────────────────────┐
│  ├── JSRPC 服务: ws://127.0.0.1:12080              │
│  └── Flask 代理: http://127.0.0.1:xxx/encode       │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 7: Burp 配置 ────────────────────────────┐
│  ● autoDecoder URL → Flask 代理                    │
│  ● 配置 encode/decode 方向                         │
│  ● 联调验证                                       │
└─────────────────────┬─────────────────────────────┘
                      ▼
              ✅ 全链路打通，Burp 自动解密/加密
```

## 核心组件

### 1. 运行时 Hook 探针 (emit_runtime_hook_probe.py)

预注入到页面的 JS 探针，在所有 JS 执行前安装 Hook：

```javascript
(function() {
  // 避免重复安装
  if (window.__JSRA_TRACE__) return;
  
  var TRACE = { requests: [], crypto: [], serializers: [] };
  window.__JSRA_TRACE__ = TRACE;
  
  // Hook Fetch
  var origFetch = window.fetch;
  window.fetch = function() { /* 记录请求 + 调用栈 */ };
  
  // Hook XHR
  var origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url) { /* 记录 */ };
  
  // Hook crypto.subtle (digest/sign/encrypt/decrypt)
  crypto.subtle.digest = function(algorithm, data) {
    TRACE.crypto.push({type:'digest', algorithm});
    return origDigest(algorithm, data);
  };
  
  // 捕获 Webpack 模块
  // 搜索 __webpack_require__ / webpackChunk* / require.c
})();
```

### 2. 加密候选评分 (detect_encryption.py)

7 维度评分系统：

| 维度 | 权重 | 判定依据 |
|------|------|---------|
| name_score | 1.0 | 函数名包含 encrypt/sign/rsa/aes/md5/sm2 等 |
| source_keyword_score | 1.0 | 源码包含加密库调用关键字 |
| runtime_stack_score | 1.0 | 调用栈关联到目标请求 |
| request_correlation | 0.8 | 请求 body/header 中出现函数名或返回值 |
| input_output_shape | 0.9 | 输入/输出符合加密特征 |
| module_export_score | 0.7 | 从 Webpack 模块导出 |
| verification_score | 1.0 | 真实样本验证通过 |

**阈值**: 总分 > 0.6 → 进入验证阶段

**验证流程**:
1. 用真实请求中的明文输入调用候选函数
2. 对比输出是否匹配抓包中的密文
3. 匹配 → confidence=high

### 3. Webpack 模块解析

优先级链（不跳级）：

```
Priority 1: window.__webpack_require__ 存在？
  ├── 存在 → 直接使用
  └── 不存在 →
Priority 2: webpackChunk* 存在？
  ├── 存在 → hook push 方法，等待下次 chunk 加载
  └── 不存在 →
Priority 3: require.c 遍历
  └── 从已加载 module cache 搜索 export
Priority 4: 离线解析 chunk factory（实验性）
  └── 只生成 candidate，标记 confidence=low
```

### 4. JSRPC (WebSocket 远程调用)

```javascript
// 浏览器端
var client = new Hlclient("ws://127.0.0.1:12080/ws?group=xxx");
client.regAction("encrypt", function(param, resolve) {
  var result = window.encryptFunc(param);
  resolve(String(result));
});
```

```bash
# 调用
curl "http://127.0.0.1:12080/go?group=xxx&action=encrypt&param=plaintext"
# 返回: "密文字符串"
```

### 5. Flask 代理

```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route("/encode", methods=["POST"])
def encode():
    data = request.form.get("dataBody", "")
    # 调 JSRPC 获取加密结果
    # 返回给 Burp autoDecoder
    return encrypted_data
```

### 6. autoDecoder 集成

```bash
# Burp 配置
# 1. 安装 autoDecoder 插件
# 2. 配置：
#    autoDecoder URL: http://127.0.0.1:5000/encode
#    HTTP Method: POST
#    Form Fields: dataBody, dataHeaders
# 3. 配置 encode 方向（请求加密）和 decode 方向（响应解密）
```

## 反调试处理

| 反调试类型 | 注入方案 | 参考来源 |
|-----------|---------|---------|
| debugger 循环 | 重写 eval/Function/constructor 过滤 debugger | antidebug-patterns.md |
| toString 检测 | 重写 Function.prototype.toString | 同上 |
| 控制台清理 | 重写 console.clear | 同上 |
| 时间检测 | 重写 Date.now/performance.now | 同上 |
| DevTools 检测 | 重写 element.attributes 或 viewport 检测 | 同上 |

## 能力边界

### 支持
- 页面导航、evaluate_script、initScript 预注入
- 网络请求读取、console 读取
- Hook fetch/XHR/crypto.subtle/JSON.stringify
- Webpack module cache 捕获
- 早期 Hook 安装（initScript）

### 不支持
- 真实 JS 断点（paused frame）
- 闭包未导出函数
- WASM 未导出内部函数
- Service Worker 内部闭包
- ES module import 拦截
- VMP 静态还原
- CSP WebSocket 绕过
- VM 保护 JS 的直接 Hook

## 快速启动

```bash
# 1. 安装 MCP
pip install chrome-devtools-mcp 或 npx chrome-devtools-mcp@latest

# 2. 配置到 Hermes
# ~/.hermes/config.yaml 添加 MCP 服务

# 3. 启动浏览器
# 启动 Chrome 带远程调试端口

# 4. 输入目标
# Target URL + Parameters To Analyze → 全自动流程
```

## 引用
- 原始项目: Fausto-404/js-reverse-automation--skill
- JsRpc: https://github.com/jxhczhl/JsRpc
- autoDecoder: https://github.com/f0ng/autoDecoder
- chrome-devtools-mcp: https://github.com/ChromeDevTools/chrome-devtools-mcp/