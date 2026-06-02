---
name: cross-platform-proxy-scripting
description: "跨平台代理脚本编写技能。Quantumult X / Surge / Loon / Egern / Stash / Shadowrocket 统一脚本开发，多平台适配层，Env.js框架，模块互转（Script-Hub/LoonKissSurge）。含去广告三大流派（墨鱼流/毒奶流/疯狗流）、46项目源码索引、reject家族详解。"
author: 7452323 (absorbed from 46 QX/Surge/Loon ecosystem projects)
version: 2.0.0
tags: [quantumultx, surge, loon, egern, proxy, script, stash, shadowrocket, Script-Hub]
---

# Cross Platform Proxy Scripting v2.0

## 平台适配层

| 功能 | QX | Surge | Loon | Egern | Stash | Shadowrocket |
|------|-----|-------|------|-------|-------|-------------|
| 持久化 | $prefs | $persistentStore | $persistentStore | $config.get | ↔Loon | ↔Surge |
| 通知 | $notify | $notification | $notification.post | $notification | ↔Loon | ↔Surge |
| HTTP | $task.fetch | $httpClient | $httpClient | $api.http | ↔Loon | - |
| 完成 | $done() | $done() | $done() | $done() | - | - |

## 模块格式对比

| 平台 | 模块后缀 | 去广告实现方式 | MITM 配置 |
|------|----------|---------------|-----------|
| **QX** | `.conf` / `.snippet` | `[rewrite_local]` + `script-response-body` | `[mitm] hostname = ` |
| **Surge** | `.sgmodule` | `[Script] http-response + requires-body=true` | `[MITM] hostname = %APPEND% ` |
| **Loon** | `.plugin` | `[Script] http-response` | `[MITM] hostname = ` |
| **Egern** | `.json` | 类 Surge 格式 | - |
| **Stash** | `.stoverride` | 类 Loon 格式 | - |
| **Shadowrocket** | `.conf` | 简单 reject | 简陋 |

## 多平台统一跳转

```javascript
// 自动识别平台
function getEnv() {
  if (typeof $task !== 'undefined') return 'QX';
  if (typeof $httpClient !== 'undefined') return 'Surge/Loon';
  if (typeof $api !== 'undefined') return 'Egern';
  return 'unknown';
}

// 通用持久化
function read(key) {
    if (typeof $prefs !== 'undefined') return $prefs.valueForKey(key);
    if (typeof $persistentStore !== 'undefined') return $persistentStore.read(key);
}
function write(val, key) {
    if (typeof $prefs !== 'undefined') return $prefs.setValueForKey(val, key);
    if (typeof $persistentStore !== 'undefined') return $persistentStore.write(val, key);
}
```

## 去广告三大流派（跨平台通用）

详见技能 `qx-script-master` 的详细剖析。快速摘要：

1. **墨鱼流** — MITM + response-body JSON 删字段 → 适用于 App 内广告
2. **毒奶流** — CSS 注入 + JS 注入 → 适用于网页广告/影视站
3. **疯狗流** — 800万规则集暴力阻断 → 适用于全网络覆盖

### reject 家族用法

```
# 所有平台通用
DOMAIN-SUFFIX, ad.example.com, reject        # → 404
DOMAIN-SUFFIX, ad.example.com, reject-200    # → 200 empty body
# Surge/Loon 支持 reject-dict (→ {}), reject-array (→ []), reject-img (→ 1px)
```

## 模块互转工具链

| 工具 | 用途 | 用法 |
|------|------|------|
| **Script-Hub** (xream) | Loon→Surge/QX/Stash | `https://script.hub/api/convert?type=surge&url=...` |
| **LoonKissSurge** (QingRex) | CI 自动转换 | `https://surge.qingr.moe/` 一键添加 |
| **czy13724 构建工具** | Surge模块/Loon插件自定义构建 | `https://surge-argu.levifree.qzz.io/` |
| **BoxJS 订阅** | 脚本可视化配置 | `https://docs.boxjs.app` |

## Env.js 核心 API

```javascript
const $ = new Env('脚本名');

// 存储
$.read(key) / $.write(val, key)

// 通知
$.msg(title, sub, body)

// HTTP 请求
$.get(url, cb) / $.post(url, body, cb)

// 日志
$.log(msg)

// 完成
$.done(data)
```
