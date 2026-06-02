---
name: qx-script-master
description: "Quantumult X / Surge / Loon 全能脚本编写技能。覆盖 5 大脚本类型、18+ 种实战模式、HAR 工作流、多平台源码库索引（46 个顶级项目实战经验整合）。2026.06 版新增：墨鱼去广告模式、毒奶网页CSS注入、Script-Hub/LoonKissSurge模块转换、RevenueCat/BuyItUnes批量解锁、800万规则集经验、UniFi/QuanMock响应Mock、Cookie串多源聚合"
author: 7452323 (absorbed from ddgksf2013/limbopro/QingRex/luestr/fmz200/SheepFJ/zZPiglet/blackmatrix7/NobyDa/Peng-YM/Orz-3/Hackl0us/I-am-R-E/Rabbit-Spec/SukkaW/89996462/czy13724/Keywos/Moli-X/sve1r/zqzess/xiaomaoJT/mist-whisper/LOWERTOP/TributePaulWalker/chxm1023/Maasea/nzw9314/Mike-offers/Guding88/gjwj666/app2smile/Koolson/deezertidal/ByteSheepStudio/Yarmukhamedov/alexshen223/Naveen)
version: 4.0.0
tags: [QuantumultX, Surge, Loon, unlock, checkin, cookie, adblock, panel, Env.js, proxy, Script-Hub, sgmodule, snippet, JQ, MITM]
---

# Quantumult X 全能脚本大师 v4.0

从抓包到脚本到上线全流程，覆盖 5 大脚本类型、18+ 种实战模式、46 个顶级项目的实操经验整合。

---

## 快速导航

| 章节 | 内容 |
|------|------|
| 一、QX/Surge/Loon 生态全景 | 46 个顶级项目分类索引 |
| 二、脚本类型总览 | 解锁 / 签到 / Cookie / 去广告 / 面板 |
| 三、通用架构 | 多平台适配 + Env.js 框架 + 持久化 |
| 四、去广告三大流派 | 墨鱼流 / 毒奶流 / 疯狗流 |
| 五、模块转换 | Script-Hub / LoonKissSurge / 平台互转 |
| 六、18+ 种实战模式 | 含 JQ 表达式、reject 系、Cookie 串聚合 |
| 七、核心源码库索引 | 46 个仓库用途速查 |
| 八、常见 App 逆向实战 | RevenueCat / B站 / Spotify / 抖音 |
| 九、调试与维护 | 日志 / 通知 / 保活 / 自动化 |

---

## 一、QX/Surge/Loon 生态全景（46 项目分类索引）

### 🌟 全能型（Rule+Rewrite+Script 一站式）

| 项目 | Stars | 亮点 |
|------|-------|------|
| **墨鱼 ddgksf2013** | 13k | QX 去广告天花板：42+ 广告拦截 + 11 会员解锁 + 8 应用增强 + 8 网页优化 + 图标库集合 |
| **blackmatrix7/ios_rule_script** | 26k | 分流规则 + 重写规则 + 脚本 | 维护最勤奋（16h前更新）| 7 大平台格式 |
| **Orz-3/QuantumultX** | 4.5k | 紧凑 QX 配置 | B站/YouTube/TikTok/Netflix 解锁 |
| **NobyDa/Script** | 8.4k | 多平台（QX/Surge/Loon/Stash）+ 京东/爱奇艺/B站签到 + 广告分流 |
| **limbopro/Adblock4limbo** | 4.4k | CSS注入+JS注入去网页广告方案 | 1.8万+通用选择器 → 详见【去广告三大流派】 |
| **Hackl0us/SS-Rule-Snippet** | 11k | 精简化规则鼻祖 | 7 平台同步 | 懒人规则一键导入 |
| **Peng-YM/QuanX** | - | Task 自动签到 + Rewrite 重写框架 | BoxJS 集成 |
| **sve1r/Rules-For-QX** | - | 规则/重写/BackCN 回流/图标 | CDN 加速支持 |
| **zqzess/rule_for_quantumultX** | - | 机器人自动同步上游 | 支持 QX/Loon/Surge/Clash/ADGuardHome |
| **fmz200/wool_scripts** | - | 730+ App 去广告 | QX/Loon/Surge/Egern/Stash 五格式 |
| **89996462/Quantumult-X** | 918 | 快速更新 | 持续维护 |
| **czy13724/Quantumult-X** | - | 多作者共创 | 网页脚本检索 + BoxJS/图标/模块自定义构建 |
| **xiaomaoJT/QxScript** | 457 | 懒人中英文双版 + Mac版 | 微信教程合集 |
| **TributePaulWalker/Profiles** | - | 基于 ConnersHua(RuleGo) | 分流/重写/脚本 |

### 🎯 模块转换/工具链

| 项目 | 说明 |
|------|------|
| **QingRex/LoonKissSurge** | Loon 插件 → Surge 模块自动转换（Script-Hub 深度集成），全自动 CI 推送 |
| **ByteSheepStudio/QuanMock** | 响应 Mock 工具：MITM 截获响应 → 重写 JSON 字段 → 前端调试无需造数据 |
| **I-am-R-E/Functional-Store-Hub** | 网易/知乎/WPS/财新/Nicegram/流利说解锁脚本 |
| **Maasea/sgmodule** | Surge 模块集合 |
| **Yarmukhamedov/mitm** | mitmproxy 集成方案 |

### 💎 去广告专门

| 项目 | 说明 |
|------|------|
| **luestr/CrazyRule** | 800 万条广告拦截规则暴力压测 → 79 个切片文件 |
| **chxm1023/Advertising** | 52 star 的去广告规则 |
| **Rabbit-Spec/Surge** | Surge 自用配置+模块+脚本 | 分流引用 blackmatrix7 |
| **SukkaW/Surge** | Surge 模块/配置 |
| **mist-whisper/Surge** | Surge 脚本集合 |
| **Moli-X/Tool + Resources** | QX/Loon/Surge 去广告脚本 + BoxJS |
| **Keywos/rule + Quantumult-X** | 规则集 |
| **gjwj666/qx** | QX 配置 |

### 📱 会员解锁专门

| 项目 | 说明 |
|------|------|
| **SheepFJ/QuantumultX** | CADmini/车工计算器/蛋啵/滚动截屏/简讯/图片转文字/遥望 等小众 App 会员解锁 |
| **deezertidal/deezertidal + Rewrite** | QX Rewrite 解锁脚本 |
| **Mike-offers/Rewrite** | Rewrite 集合 |
| **Guding88/Script** | 266 star 的通用脚本 |
| **app2smile/rules** | Spotify/贴吧/QD 脚本（被多处引用） |

### 🏝 流媒体/签到/工具

| 项目 | 说明 |
|------|------|
| **zZPiglet/Task** | QX Task 签到（被多项目引用） |
| **Tartarus2014/Loon-Script** | Loon 脚本 |
| **Naveen/dove** | - |
| **alexshen223/surge-script** | Surge 脚本 |
| **cysk003/Marol62926-Quantumultx** | QX 配置 |
| **nzw9314/QuantumultX** | QX Task 集合 |
| **Koolson/Qure** | QX 图标库鼻祖（被所有项目引用） |
| **Orz-3/mini** | QX mini 风格图标库 |
| **LOWERTOP/Shadowrocket-First** | 小火箭使用手册 |
| **Hackl0us/GeoIP2-CN** | GeoIP2 数据库（Go 实现，7.3k star） |
| **Yu9191/Yu9191** | 88 star 的 QX 配置 |

---

## 二、去广告三大流派（实战核心）

根据 46 个项目总结出三大去广告流派：

### 流派 A：墨鱼流（ddgksf2013 代表）— 应用级去广告

**核心思想**：MITM 截获 → 响应体 JSON 解析 → 删除广告字段

```javascript
// 经典模式：开屏广告置空
case /^https?:\/\/.*\.cupid\.iqiyi\.com\/mixer\?/.test($.request.url):
  let obj = JSON.parse($.response.body);
  delete obj["adSlots"];    // 删广告
  response = { body: JSON.stringify(obj) };
  break;

// B 站开屏：把展示时间推到 100 年后
obj["data"]["max_time"] = 0;
obj["data"]["list"]["show"] = [];

// 知乎信息流：删 ad_info 段
obj["data"] = obj["data"].filter(item => !item.ad_info);
```

**典型代码位置**：`blackmatrix7/script/startup/startup.js`、`ddgksf2013/Scripts/*.js`

**使用格式（QX）**：
```
# QX snippet 格式
^https?:\/\/example\.com\/api\/ad url script-response-body https://raw.xxx/script.js
hostname = example.com
```

### 流派 B：毒奶流（limbopro 代表）— 网页级去广告

**核心思想**：CSS 选择器 + 自定义 JS 注入移除网页广告元素

**1.8 万+ 通用去广告 CSS 选择器**，配合导航按钮、工具箱、沉浸式翻译

```javascript
// 核心方案：在所有网页注入去广告脚本
// 1. 加载通用去广告 CSS 选择器
// 2. 根据域名加载独立 CSS 选择器
// 3. 加载导航按钮+工具箱
https://limbopro.com/Adguard/Adblock4limbo.js
```

**使用格式（Surge）**：
```
# hostname 需要 MITM 的域名
hostname = www.bbc.com, www.ted.com

# 匹配 URL 重写
(bbc|ted) script-response-body https://limbopro.com/Adguard/Adblock4limbo.js
```

**特点**：擅长在线影视/Porn 类网站的去广告（低端影视/Jable/MissAV 等）

### 流派 C：疯狗流（luestr 代表）— 暴力规则集去广告

**核心思想**：800 万条规则暴力阻断 → 79 个切片文件（每 10 万条一个）

```
# Loon
https://raw.githubusercontent.com/luestr/CrazyRule/main/Loon/ad-loon_1.list

# QX / Surge
https://raw.githubusercontent.com/luestr/CrazyRule/main/QX/ad-qx_1.list
```

**适用**：极致的全网络去广告，但需要大量内存，建议 Loon 使用

### 综合策略推荐

| 场景 | 推荐方案 |
|------|----------|
| App 开屏广告 | 墨鱼流（get_startup_ad） |
| App 信息流广告 | 墨鱼流（response-body 过滤） |
| 网页 Banner 广告 | 毒奶流（CSS 注入） |
| 影视站广告 | 毒奶流（毒奶去广告计划） |
| 全网络覆盖 | 疯狗流（开源白名单规则） |
| 会员解锁 | 墨鱼流（RevenueCat/BuyItUnes） |

---

## 三、18+ 种实战模式速查

| # | 模式 | 描述 | 适用场景 | 典型代码 |
|---|------|------|----------|----------|
| 1 | 响应体全文替换 | 正则替换整个响应体 | Spotify开卡 | `response.body = body.replace(/xxx/g, "yyy")` |
| 2 | 响应体 JSON 插值 | 修改 JSON 特定字段 | RevenueCat解锁 | `obj.entitlements[product].expires_date = "2099-12-31"` |
| 3 | 分路径/分域名解锁 | 按 URL 路径分支 | 全能脚本 | `switch(true) { case /path1/: ... }` |
| 4 | API 置空去广告 | GET → 空 JSON/空数组 | 开屏去广告 | `reject-200`, `reject-dict`, `reject-array` |
| 5 | 开关修改 | 修改响应体中 type/status | 功能解锁 | `obj.data.enabled = true` |
| 6 | Content Filter（正则流） | 正则替换响应体 | YouTube去广告 | `body.replace(/ad_break/g, "skip")` |
| 7 | CSS 注入 | 插入 CSS 隐藏元素 | 网页去广告 | `#ad-banner { display: none !important }` |
| 8 | JS 注入 | 插入去广告逻辑 | 网页去广告 | `<script>removeAds()</script>` |
| 9 | Cookie 单源采集 | Header 捕获 | 单账号签到 | `$request.headers["Cookie"]` |
| 10 | Cookie 多源聚合 | 多个 Cookie 串合并 | 多账号 | `cookies.push(response.headers["Set-Cookie"])` |
| 11 | 单账号签到 | Cron 定时 GET/POST | 日常签到 | `$task.fetch({url, headers})` |
| 12 | 多账户持久化 | token 数组+独立通知 | 多号 | `JSON.parse($.read("accounts"))` |
| 13 | Token 生命周期 | 过期自动失效通知 | 长效维护 | `Date.parse(expiry) < Date.now()` |
| 14 | 面板信息展示 | Surge Panel | 状态 | `$surge.selectGroupPolicy(...)` |
| 15 | 面板可交互（点击执行） | 点击执行 JS | 交互 | `$surge.setSelectGroupPolicy(...)` |
| 16 | 模块转换 | Loon→Surge、QX→Loon | 跨平台 | Script-Hub / LoonKissSurge |
| 17 | QuanMock（响应 Mock） | MITM 篡改 JSON | 前端调试 | `JSON.parse($response.body).age = 101` |
| 18 | JQ 表达式 | Surge 新版 JQ 过滤 | Surge | `.data.items[] | select(.type == "ad")` |
| 19 | reject 家族 | 4 种 reject 方式 | 广告域名 | `reject / reject-200 / reject-img / reject-dict / reject-array` |
| 20 | UniFi/多平台统一 | 一套代码跑三平台 | 通用 | `typeof $task !== "undefined" ? QX : typeof $httpClient ...` |

### reject 家族详解

```
reject          → HTTP 404, 无 body（开屏广告）
reject-200      → HTTP 200, 无 body（请求 expect 200）
reject-img      → HTTP 200, 1px gif（图片占位）
reject-dict     → HTTP 200, {}（API 期望对象）
reject-array    → HTTP 200, []（API 期望数组）
```

---

## 四、模块转换（跨平台分发）

### Script-Hub（xream 维护）

将 Loon 插件 → Surge/QX/Stash 模块，自动转换格式

```javascript
// 核心转换逻辑
input_loon_plugin → detect_platform → output_module
// 支持自定义参数
https://script.hub/api/convert?type=surge&url=...
```

### LoonKissSurge（QingRex）

CI 自动将 iKelee Loon 仓库 → Surge 模块，每日同步

```bash
# 架构
upstream_loon_repo → GitHub Action Script-Hub Docker → surge.qingr.moe
# 使用：直接访问 https://surge.qingr.moe/ 一键添加
```

### QX → Surge 模块格式差异

| 功能 | QX | Surge |
|------|----|-------|
| 配置格式 | `.conf` | `.sgmodule` |
| 重写 | `[rewrite_remote]` | `[Script]` |
| 分流 | `[filter_remote]` | `[Rule]` |
| MITM | `[mitm] hostname = ` | `[MITM] skip-server-cert-verify = false` |
| 脚本格式 | snippet | Module |

---

## 五、常见 App 逆向实战

### RevenueCat 解锁（最通用的模式）

被 ddgksf2013 广泛使用，支持多家 App 会员解锁：

```javascript
// RevenueCat 响应体格式
{
  "request_date_ms": 1717200000000,
  "subscriber": {
    "subscriptions": {
      "pro": {
        "expires_date": "2099-12-31T00:00:00Z",
        "is_sandbox": false,
        "original_purchase_date": "2025-01-01T00:00:00Z",
        "unsubscribe_detected_at": null
      }
    },
    "entitlements": {
      "pro": {
        "expires_date": "2099-12-31T00:00:00Z",
        "product_identifier": "com.app.pro.yearly"
      }
    }
  }
}

// 修改策略：把 expires_date 全部推到 2099 年
```

### B 站开屏去广告（组合拳）

```javascript
// 1. 置空 splash/list → max_time = 0, show = []
// 2. 修改 v2/splash/list 响应
// 3. 屏蔽活动入口
```

### 字节系 App 开屏

```javascript
// 常见模式：修改配置接口中的 ad_switch
obj.data.ad_switch = 0;
// 或给 duration 设 0
obj.data.splash_duration = 0;
```

---

## 六、QQ/Surge/Loon 配置语法速查

### QX 配置三段式

```
[general]
[policy]
  static=策略名, proxy/direct/reject, server-tag-regex=..., img-url=...
[dns]
[分流]
  [filter_remote]   # 远程规则集
  [filter_local]    # 本地规则
[重写]
  [rewrite_remote]  # 远程重写
  [rewrite_local]   # 本地重写
[任务]
  [task_local]
  [task_remote]
[mitm]
  hostname = ...
```

### Surge 模块结构（sgmodule）

```
#!name=模块名
#!desc=描述
#!system=ios

[Script]
xxx = type=rule, pattern=^https?://..., requires-script=true

[Rule]
DOMAIN-SUFFIX, example.com, REJECT

[MITM]
hostname = %APPEND% example.com
```

### Loon 插件结构

```
#!name=插件名
#!desc=描述

[MITM]
hostname = example.com

[Script]
http-response ^https?://... script-path=..., requires-body=true, tag=xxx

[Rule]
DOMAIN-SUFFIX, example.com, REJECT
```

---

## 七、46 项目源码价值索引

| 需求 | 找谁看 | 对应目录 |
|------|--------|----------|
| 去开屏广告通杀 | blackmatrix7 | `script/startup/startup.js` |
| 单 App 去广告 | ddgksf2013 | `Rewrite/AdBlock/*.conf` |
| 网页去广告 | limbopro | `Adblock4limbo.js + CSS/` |
| RevenueCat 解锁 | ddgksf2013 | `Scripts/revenuecat.vip.js` |
| B 站解锁 | ddgksf2013/NobyDa | `Orz-3/Bili_Auto_Regions.js` |
| iOS 天气解锁 | VirgilClyne/iRingo | `WeatherKit.snippet` |
| WPS 会员 | I-am-R-E | `WPSOffice/` |
| Spotify 解锁 | app2smile | `rules/module/spotify.conf` |
| 800 万规则 | luestr | `CrazyRule/` |
| 小火箭使用 | LOWERTOP | `Shadowrocket-First/` |
| 图标库 | Koolson/Qure | `IconSet/` |
| Task 签到 | zZPiglet | `Task/` |
| 模块转换 | QingRex | LoonKissSurge |
| Mock 数据 | ByteSheepStudio | QuanMock |
| BoxJS 订阅 | NobyDa/Peng-YM | `boxjs.json` |

---

## 注意事项

- MITM 前置条件：必须信任并安装根证书
- App 升级后可能失效：部分 App 会检测 MITM（如银行类、抖音）
- JQ 模式：仅 Surge 5.10+ 支持，QX/Loon 无此功能
- 800 万规则集：仅推荐 Loon 使用，QX/Surge 会爆内存
- Cookie 采集：一般只在首次获取时工作，需要登录态
- **禁止国内平台传播**：多数项目明确禁止公众号/自媒体转载
