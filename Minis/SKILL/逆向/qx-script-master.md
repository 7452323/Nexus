---
name: qx-script-master
description: "Quantumult X / Surge / Loon 全能脚本编写技能。覆盖 5 大脚本类型：Unlock（响应体/分路径/全替换）、Checkin（单账号/多账户/持久化）、Cookie 采集、去广告、面板工具。含 HAR 解析工作流、多平台适配层、Env.js 框架集成、18 种常见模式。"
author: 7452323 (converted from OpenClaw)
version: 3.0.0
tags: [QuantumultX, Surge, Loon, unlock, checkin, cookie, adblock, panel, Env.js, proxy]
---

# Quantumult X 全能脚本大师

从抓包到脚本到上线全流程，覆盖 5 大脚本类型、3 大平台、18 种实战模式。

---

## 快速导航

| 章节 | 内容 |
|------|------|
| 一、脚本类型总览 | 解锁 / 签到 / Cookie / 去广告 / 面板 |
| 二、通用架构 | 多平台适配 + Env.js 框架 + 持久化 + 通知 |
| 三、解锁脚本 | 4 种模式 + 常见 App 字段速查 + 调试方法 |
| 四、签到脚本 | 单账号 / 多账户持久化 / 带通知 / 青龙 |
| 五、Cookie 采集 | 请求头捕获 / Token 提取 / 去重存储 |
| 六、去广告脚本 | API 置空 / 开关修改 / 内容过滤 |
| 七、面板脚本 | Surge Panel 面板 / 信息展示 |
| 八、HAR 工作流 | 从抓包到脚本的完整转换 |
| 九、Egern 兼容适配 | 模块封装与分发 |
| 十一、高级技巧 | JQ 表达式 / Reject 系列 / Conf 管理 |
| 十、青龙适配 | 在青龙面板运行 QX 脚本 |
| 十一、完整示例 | 5 个可以直接用的模板 |
| 十二、调试与排查 | 日志 / 通知 / 常见问题 |

## 一、脚本类型总览

### 5 大脚本类型

| 类型 | 使用场景 | 触发方式 | 典型例子 |
|------|----------|----------|----------|
| **Unlock** | 解锁会员/去限制 | MITM 响应体修改 | Spotify解锁 / 简悦VIP |
| **Checkin** | 自动签到领积分 | Cron 定时 | 各种论坛签到 |
| **Cookie** | 采集登录凭证 | MITM 请求头捕获 | 获取Cookie用于Checkin |
| **AdBlock** | 去广告 | 响应体替换 | YouTube去广告 |
| **Panel** | UI 信息展示 | Surge Panel | 流量/会员状态面板 |

### 18 种模式速查

| # | 模式 | 描述 | 适用场景 |
|---|------|------|----------|
| 1 | 响应体全文替换 | 正则替换整个响应体 | Spotify开卡、简悦去限制 |
| 2 | 响应体 JSON 插值 | 修改 JSON 特定字段 | 各类 JSON API 解锁 |
| 3 | 分路径/分域名解锁 | 按 URL 不同路径执行不同逻辑 | 多功能脚本 |
| 4 | 通用 Header 注入 | 修改请求/响应 Header | Cookie 采集基本模式 |
| 5 | Cron 定时签到 | 固定时间执行 | 每日签到 |
| 6 | 多账户持久化 | 多个 token 分别管理+独立通知 | 多账号签到 |
| 7 | Cookie 多源去重 | 同域名/同路径多 Cookie 合并 | 长期维护的签到 |
| 8 | Token 有效期管理 | 过期 / 失效自动通知 | 需定期刷新的签到 |
| 9 | API 置空去广告 | GET 请求返回空 JSON | 开屏去广告 |
| 10 | 开关修改 | 修改 JS 中反汇编对象 | 破解开关型限制 |
| 11 | 内容过滤 | 正则替换响应体 | YouTube去广告 |
| 12 | 面板按钮+数据 | 显示 + 可执行按钮 | 多功能管理面板 |
| 13 | 面板注册脚本 | 面板展示+点击注册 | Surge 面板脚本 |
| 14 | 青龙兼容层 | ql 对象反射到 $ 对象 | 青龙迁移 |
| 15 | Egern 打包 | header 注入+函数体 | Egern 分发 |
| 16 | HAR 抓包解析 | 从 HAR 提取参数/Header | 新 App 逆向 |
| 17 | 多版本兼容 | QX / Surge / Loon 三平台 | 通用分发 |
| 18 | 通知开关 | 是否发送通知 | 用户可控通知 |

## 二、通用架构

### Env.js 框架

```javascript
const $ = new Env('脚本名称');

// 持久化存储
$.read('key');           // 读
$.write('value', 'key'); // 写

// 通知
$.msg('title', 'subtitle', 'body');

// 网络请求
$.get(url, callback);
$.post(url, body, callback);

// 完成
$.done(data);
```

### 多平台适配层

| 方法 | QX | Surge | Loon |
|------|----|-------|------|
| 持久化 | $prefs | $persistentStore | $persistentStore |
| 通知 | $notify | $notification | $notification.post |
| 请求 | $task.fetch | $httpClient | $httpClient |
| 完成 | $done() | $done() | $done() |

## 注意事项

- 尊重各平台的使用条款
- 签名与通知请合理使用
- 长期运行的签到需要考虑 token 有效期管理
- HAR 抓包需要信任 MITM 证书
