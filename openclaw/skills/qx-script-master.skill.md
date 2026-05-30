---
name: qx-script-master
description: "Quantumult X / Surge / Loon 全能脚本编写技能。覆盖 5 大脚本类型：Unlock（响应体/分路径/全替换）、Checkin（单账号/多账户/持久化）、Cookie 采集、去广告、面板工具。含 HAR 解析工作流、多平台适配层、Env.js 框架集成、18 种常见模式。安装此技能即可写出任何 QX/Surge/Loon 脚本。"
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

---

## 一、脚本类型总览

| 类型 | 用途 | 触发方式 | 核心逻辑 |
|------|------|---------|---------|
| 🔓 解锁 | 破解 App 会员/订阅 | 响应拦截（`script-response-body`） | `$response.body` → 改字段 → `$done` |
| ✅ 签到 | 每日自动签到领积分 | 定时任务（`[task_local]`） | HTTP 请求签到接口 → 通知结果 |
| 🍪 Cookie | 获取登录态（签到前置步骤） | 请求拦截（`script-request-header`） | 提取 `Cookie`/`Authorization` → 存本地 |
| 🚫 去广告 | 移除 App 内广告 | 响应拦截 | 广告字段置空 → `$done` |
| 📊 面板 | 显示实时信息（Surge） | 定时刷新 | 请求数据 → 渲染 HTML |

---

## 二、通用架构

### 2.1 多平台检测

所有脚本统一在最前面检测当前平台：

```javascript
// ===== 平台检测 =====
const isQX = typeof $task !== 'undefined';
const isSurge = typeof $httpClient !== 'undefined';
const isLoon = typeof $loon !== 'undefined';

// ===== 平台统一 HTTP 请求 =====
async function httpRequest(method, url, headers = {}, body = null) {
    const options = { url, headers };
    if (body) options.body = typeof body === 'string' ? body : JSON.stringify(body);

    if (isQX) {
        const resp = await $task.fetch({ ...options, method });
        return { status: resp.statusCode, body: resp.body, headers: resp.headers };
    }
    if (isSurge || isLoon) {
        return new Promise((resolve) => {
            const callback = (err, resp, data) => {
                resolve({
                    status: resp.status || resp.statusCode,
                    body: data,
                    headers: resp.headers || {}
                });
            };
            if (method === 'GET') $httpClient.get(options, callback);
            else if (method === 'POST') $httpClient.post(options, callback);
            else if (method === 'PUT') $httpClient.put(options, callback);
        });
    }
}

// ===== 跨平台持久化存储 =====
function kvRead(key) {
    if (isQX && $prefs.valueForKey) return $prefs.valueForKey(key) || '';
    if (isSurge && $persistentStore.read) return $persistentStore.read(key) || '';
    return '';
}

function kvWrite(key, val) {
    if (isQX && $prefs.setValueForKey) $prefs.setValueForKey(val, key);
    if (isSurge && $persistentStore.write) $persistentStore.write(val, key);
}

// ===== 通知 =====
function sendNotify(title, subtitle, content) {
    if (typeof $notification !== 'undefined') {
        $notification.post(title, subtitle || '', content || '');
    } else {
        console.log(`${title}: ${subtitle} - ${content}`);
    }
}

// ===== 日志 =====
function log(msg) {
    console.log(msg);
}
```

### 2.2 Loon 特有 API

Loon 除了支持 Surge 的 `$httpClient/$persistentStore/$notification.post` 外，还有以下特有 API：

#### `$loon` — 设备信息
```javascript
// $loon 自动获取，无需声明
console.log($loon);
// {
//   device: "iPhone",         // 设备名
//   osVersion: "18.3.1",     // 系统版本
//   appVersion: "3.2.3",     // Loon 版本
//   buildVersion: "931"      // 构建版本
// }
```

#### `$script` — 脚本信息
```javascript
$script.name;       // 当前脚本名
$script.startTime;  // 脚本执行时间戳
```

#### `$config` — 配置操作
```javascript
// 获取配置 JSON
const config = JSON.parse($config.getConfig());
console.log(config.running_model);       // 0=直连 1=分流 2=全局
console.log(config.all_policy_groups);   // 所有策略组
console.log(config.policy_select);       // 各策略组的选择

// 设置策略组
$config.getConfig("节点选择", "HK - v1.0");  // 将"节点选择"策略改为HK

// 获取子策略
$config.getSubPolicies("奈飞影视", function(list) {
  console.log(list);  // ["DIRECT", "HK", "JP", ...]
});

// 获取当前选择的策略
const selected = $config.getSelectedPolicy("节点选择");

// 设置运行模式
$config.setRunningModel(1);  // 0=直连 1=分流 2=全局
```

#### `$utils` — 工具函数
```javascript
// GeoIP 查询
const country = $utils.geoip("8.8.8.8");  // "US"

// ASN 查询
const asn = $utils.ipasn("8.8.8.8");       // "15169"

// ASO 查询（AS 组织名）
const aso = $utils.ipaso("8.8.8.8");       // "GOOGLE"

// Gzip 解压（处理压缩响应）
// const decompressed = $utils.ungzip(binaryData);
```

#### `$environment` — 通用脚本环境
仅用于 generic 类型的脚本（运行于节点上时）：
```javascript
// $environment.params.node     — 当前节点名称
// $environment.params.nodeInfo — 节点信息（简化版）
```

#### Rewrite 增强功能

Loon 支持无需 JS 脚本的 JQ 表达式直接修改 JSON 响应体（build 729+）：

```ini
# JQ 修改响应体（完全不需要JS脚本）
^https?://api\.example\.com/vip response-body-json-jq '.vip = 1 | .vip_type = "svip"'

# 添加字段
^https?://api\.example\.com/user response-body-json-add data.vip true

# 删除字段
^https?://api\.example\.com/ad response-body-json-del data.ads

# 直接替换字段
^https?://api\.example\.com/config response-body-json-replace data.ad_enabled false
```

#### $httpClient 增强参数

Loon 的 `$httpClient` 比 Surge 多支持：

```javascript
$httpClient.get({
  url: "https://api.example.com",
  node: "HK - v1.0",       // 指定节点/策略组
  binary-mode: true,        // 返回二进制
  auto-redirect: false,     // 是否自动处理重定向（默认true）
  auto-cookie: false,       // 是否自动存Cookie（默认true）
  alpn: "h2",              // HTTP/2 优先
  timeout: 5000,
  headers: { "Content-Type": "application/json" }
}, function(err, resp, data) {
  if (err) console.log(err);
  console.log(resp.status, data);
});
```

### 2.3 Env.js 框架

Env.js 是 chavyleung 开发的签到脚本通用框架，统一了多平台 API：

```javascript
// 安装 Env.js（首次使用需要）
// 方案 A：在脚本中加载远程 Env.js
const ENV_URL = 'https://raw.githubusercontent.com/chavyleung/scripts/master/Env.js';
// 脚本开头加入（适用于 Surge/Loon）
// #!require $ENV_URL

// 方案 B：使用简化版 Env 封装
const $ = new Env('脚本名称');

// Env 提供的功能：
// $.get(url)           → HTTP GET
// $.post(url, body)    → HTTP POST  
// $.msg(title, sub, content) → 发送通知
// $.read(key)          → 读取持久化数据
// $.write(val, key)    → 写入持久化数据
// $.log(info)          → 输出日志
// $.done()             → 脚本结束

!(async () => {
    await main();
})().catch((e) => $.log(`错误: ${e}`)).finally(() => $.done());

async function main() {
    // 脚本逻辑
}
```

### 2.4 通用脚本结构

所有签到/定时类脚本统一采用以下结构：

```javascript
/*
[Script]
# Surge/Loon
脚本名称 = type=cron, script-path=https://raw.githubusercontent.com/你的仓库/路径/脚本.js, cronexp=10 9 * * *, timeout=60

# 或者 QX
[task_local]
10 9 * * * https://raw.githubusercontent.com/你的仓库/路径/脚本.js, tag=脚本名称, enabled=true

[rewrite_local]
# 如果需要 Cookie 采集
^https?:\/\/api\.example\.com\/login url script-request-header 脚本.js
*/

const $ = new Env('脚本名称');

!(async () => {
    // 1. 判断是 Cookie 采集还是定时任务
    if (typeof $request !== 'undefined') {
        await getCookie();
        return;
    }
    // 2. 执行签到/任务
    await main();
})().catch((e) => $.log(`❌ 错误: ${e}`)).finally(() => $.done());

async function getCookie() {
    // 采集 Cookie/Token
}

async function main() {
    // 签到逻辑
}
```

---

## 三、解锁脚本

### 3.1 模式一：标准响应体修改（70% 的场景用这个）

```javascript
/*
App 名称 - VIP 解锁
https://apps.apple.com/cn/app/id123456789

[rewrite_local]
^https?:\/\/api\.example\.com\/(vip|user|subscription|member) url script-response-body https://raw.githubusercontent.com/7452323/QuantumultX/main/script/AppName.js

[mitm]
hostname = api.example.com
*/

var obj = JSON.parse($response.body);

// === 常规 VIP 字段 ===
obj.vip = 1;                    // 是否 VIP（0/1）
obj.vip_type = "svip";          // VIP 类型（normal/svip）
obj.isvip = 1;
obj.is_year = true;             // 是否年费会员
obj.expires = "4092599349000";  // 过期时间戳（2099年）
obj.expire_time = "4092599349000";

// === 深层嵌套 ===
if (obj.data) {
    obj.data.vip = 1;
    obj.data.is_vip = true;
    obj.data.vip_type = "svip";
    obj.data.isSVIP = true;
}
if (obj.result) {
    obj.result.vip = 1;
}
if (obj.user) {
    obj.user.vip = 1;
    obj.user.viptype = "4";
}

$done({ body: JSON.stringify(obj) });
```

### 3.2 模式二：按 URL 分路径处理

同一个脚本拦截多个接口，不同 URL 不同处理：

```javascript
var obj = JSON.parse($response.body);
var url = $request.url;

// 会员信息
if (url.indexOf('/user/vip') != -1) {
    if (obj.data) obj.data.vip = true;
    if (obj.data) obj.data.expireTime = "4092599349000";
}
// 订阅状态
if (url.indexOf('/subscription/status') != -1) {
    if (obj.data) obj.data.status = "active";
    if (obj.data) obj.data.plan = "premium";
}
// 次数/配额
if (url.indexOf('/usage/remaining') != -1) {
    if (obj.data) obj.data.remaining = 99999;
    if (obj.data) obj.data.pdf_quota = 99999;
}
// 功能开关
if (url.indexOf('/feature/list') != -1) {
    if (obj.data && Array.isArray(obj.data)) {
        obj.data.forEach(item => item.unlocked = true);
    }
}

$done({ body: JSON.stringify(obj) });
```

### 3.3 模式三：完全替换响应体

适用于 GraphQL 或复杂嵌套的 API：

```javascript
// 完全替换为伪造的订阅响应
const fakeResponse = {
    "data": {
        "processAppleReceipt": {
            "__typename": "SubscriptionResult",
            "error": 0,
            "subscription": {
                "__typename": "AppStoreSubscription",
                "status": "active",
                "originalPurchaseDate": "2024-01-01T00:00:00.000Z",
                "originalTransactionId": "570001185968888",
                "expirationDate": "9999-12-31T23:59:59.000Z",
                "productId": "com.example.premium_year",
                "tier": "premium",
                "refundedDate": null,
                "isInBillingRetryPeriod": false,
                "overDeviceLimit": false
            }
        }
    }
};

$done({ body: JSON.stringify(fakeResponse) });
```

### 3.4 模式四：多个脚本模块组合

对于复杂 App，拆成多个文件：

```
AppName/
├── Cookie.js      # Cookie 采集
├── Checkin.js     # 签到脚本
└── Unlock.js      # 解锁脚本
```

### 3.5 常见 App 解锁字段速查

| App | 关键 URL 特征 | 要改的字段 | 目标值 |
|-----|-------------|-----------|-------|
| 扫描全能王 | `/purchase/cs/query_property` | `vip_type`, `auto_renewal`, `in_trial` | `"svip"`, `true`, `1` |
| 全能扫描官 | `/queryProperty` | 同上 | 同上 |
| PDF Expert | `/api/2.0/subscription` | `isPro`, `isEdu`, `expireDate` | `true`, `true`, `"2099-12-31"` |
| Notability | `/global` (GraphQL) | 整个替换 | 见模式三 |
| Foodie | `/v1/user/privilege` | `vip`, `svip`, `isYear` | `1`, `1`, `true` |
| Lightroom | `/v1/profile` | `status`, `plan` | `"active"`, `"premium"` |
| BH Pro | `/user_equity_status_list` | `crowd_portraits_remaining_times` 等 | `88888` |
| Adblock Pro | `/verify` | `p`, `s`, `l`, `t`, `e`, `m`, `f` | `1` |

### 3.6 找解锁字段的方法

```
1. QX 开启抓包 → 打开目标 App
2. 找到返回会员信息的 API（关键词: vip, user, subscription, member, profile）
3. 看返回 JSON 中 0/false 的字段 → 改成 1/true
4. 找到过期时间字段 → 改成未来时间戳
5. 测试 → 调字段 → 上线
```

---

## 四、签到脚本

### 4.1 单账户签到

```javascript
/*
App 名称 - 每日签到
[task_local]
30 8 * * * https://raw.githubusercontent.com/7452323/QuantumultX/main/task/AppName.js, tag=签到, enabled=true

[mitm]
hostname = api.example.com
*/

const $ = new Env('签到');

!(async () => {
    const cookie = 'your_cookie_here'; // 从 HAR 中提取

    const resp = await httpRequest('GET', 'https://api.example.com/sign/in', {
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0'
    });

    const data = JSON.parse(resp.body);
    const msg = data.message || data.msg || data.data || '签到完成';
    $.log(`签到结果: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`);
    $.msg('签到', '完成', typeof msg === 'string' ? msg : '');
})().catch((e) => $.log(`❌ ${e}`)).finally(() => $.done());
```

### 4.2 多账户签到（持久化 + 去重）

```javascript
/*
App 签到 - 多账户版
[rewrite_local]
# Cookie 采集：打开小程序/App 时采集一次
^https?:\/\/api\.example\.com\/(login|user) url script-request-header https://raw.githubusercontent.com/7452323/QuantumultX/main/task/AppName.js

[task_local]
30 8 * * * https://raw.githubusercontent.com/7452323/QuantumultX/main/task/AppName.js, tag=签到, enabled=true
*/

const APP_NAME = '签到';
const STORE_KEY = 'app_cookies';
const $ = new Env(APP_NAME);

// Cookie 采集
if (typeof $request !== 'undefined') {
    const cookie = $request.headers['Cookie'] || $request.headers['cookie'];
    const auth = $request.headers['Authorization'] || $request.headers['authorization'];
    const value = cookie || auth;
    
    if (value && $request.method !== 'OPTIONS') {
        let cookies = kvRead(STORE_KEY).split('#').filter(Boolean);
        
        // 去重：用户ID或标识
        const dedup = value.match(/user_id=([^;]+)/) || value.match(/uid=([^;]+)/);
        const key = dedup ? dedup[1] : value.slice(0, 15);
        
        cookies = cookies.filter(c => {
            const k = c.match(/user_id=([^;]+)/) || c.match(/uid=([^;]+)/);
            return k ? k[1] !== key : c.slice(0, 15) !== key;
        });
        cookies.push(value);
        
        kvWrite(STORE_KEY, cookies.join('#'));
        $.msg(APP_NAME, `Cookie 已保存 (${cookies.length} 个账号)`, '');
        $.done();
    }
}

// 定时签到
!(async () => {
    const raw = kvRead(STORE_KEY);
    if (!raw) {
        $.log('❌ 无 Cookie，请先打开 App 采集');
        $.done();
        return;
    }

    const accounts = raw.split('#').filter(Boolean);
    $.log(`📋 共 ${accounts.length} 个账号`);

    let success = 0, failed = 0;
    for (let i = 0; i < accounts.length; i++) {
        try {
            const resp = await httpRequest('GET', 'https://api.example.com/sign/in', {
                'Cookie': accounts[i],
                'User-Agent': 'Mozilla/5.0'
            });
            const data = JSON.parse(resp.body);
            const msg = data.message || data.msg || '✅';
            $.log(`  账号${i+1}: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`);
            success++;
        } catch (e) {
            $.log(`  ❌ 账号${i+1}: ${e}`);
            failed++;
        }
        if (i < accounts.length - 1) await sleep(2000);
    }
    
    if (failed > 0) $.msg(APP_NAME, `成功 ${success} / 失败 ${failed}`, '');
})().catch(console.log).finally(() => $.done());

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
```

### 4.3 青龙面板适配

```javascript
// 青龙面板下运行（Node.js 环境）
const axios = require('axios');

async function qinglongCheckin(cookie) {
    try {
        const resp = await axios.get('https://api.example.com/sign/in', {
            headers: { 'Cookie': cookie }
        });
        console.log('签到结果:', resp.data.msg || resp.data.message);
    } catch (e) {
        console.log('签到失败:', e.message);
    }
}

// 青龙面板环境变量
// 在青龙面板中配置环境变量: example_cookie=xxx
const cookies = (process.env.example_cookie || '').split('&').filter(Boolean);
for (const cookie of cookies) {
    await qinglongCheckin(cookie);
}
```

---

## 五、Cookie 采集脚本

### 5.1 标准 Cookie 采集

```javascript
/*
[rewrite_local]
# 拦截关键接口，提取 Cookie/Token
^https?:\/\/api\.example\.com\/(login|user|token|profile) url script-request-header https://raw.githubusercontent.com/7452323/QuantumultX/main/task/AppName.js
*/

!(async () => {
    if ($request && $request.method === 'OPTIONS') {
        $.done();
        return;
    }

    const cookie = $request.headers['Cookie'] || $request.headers['cookie'];
    const auth = $request.headers['Authorization'] || $request.headers['authorization'];
    const ua = $request.headers['User-Agent'];

    if (auth) {
        kvWrite('app_token', auth.replace('Bearer ', ''));
        if (ua) kvWrite('app_ua', ua);
        $.msg('Cookie', 'Token 已采集 ✅', '');
        console.log('Token:', auth.slice(0, 20) + '...');
    } else if (cookie) {
        kvWrite('app_cookie', cookie);
        if (ua) kvWrite('app_ua', ua);
        $.msg('Cookie', 'Cookie 已采集 ✅', '');
        console.log('Cookie:', cookie.slice(0, 30) + '...');
    }
})().finally(() => $done());
```

### 5.2 多平台 Cookie 存储

```javascript
// 统一存储接口（跨 QX/Surge/Loon）
function getCookie(key)       { return kvRead(key); }
function setCookie(key, val)  { kvWrite(key, val); }

// Cookie 格式标准化
function parseCookie(cookieStr) {
    const result = {};
    cookieStr.split(';').forEach(pair => {
        const [k, ...v] = pair.trim().split('=');
        if (k) result[k.trim()] = v.join('=');
    });
    return result;
}
```

---

## 六、去广告脚本

### 6.1 广告列表置空

```javascript
var obj = JSON.parse($response.body);

// 常见广告容器字段
['data', 'ads', 'adList', 'ad', 'banners', 'items', 'list', 'recommend'].forEach(key => {
    if (Array.isArray(obj[key])) obj[key] = [];
    if (obj.data && Array.isArray(obj.data[key])) obj.data[key] = [];
});

$done({ body: JSON.stringify(obj) });
```

### 6.2 广告开关修改

```javascript
var obj = JSON.parse($response.body);

// 常见广告开关字段
['ad_enabled', 'showAd', 'show_ad', 'hasAd', 'isAd', 'isAdShow', 'adShow'].forEach(key => {
    if (obj[key] !== undefined) {
        obj[key] = false;
        if (typeof obj[key] === 'number') obj[key] = 0;
    }
});

// 深层
if (obj.data) {
    ['ad_enabled', 'show_ad', 'has_ad'].forEach(key => {
        if (obj.data[key] !== undefined) {
            obj.data[key] = false;
        }
    });
}

$done({ body: JSON.stringify(obj) });
```

---

## 七、面板脚本（Surge）

```javascript
/*
[Panel]
App 信息面板 = script-name=app-panel, update-interval=3600

[Script]
app-panel = type=generic, script-path=https://raw.githubusercontent.com/7452323/QuantumultX/main/task/panel.js, timeout=60
*/

const $ = new Env('信息面板');

!(async () => {
    const resp = await httpRequest('GET', 'https://api.example.com/user/info', {
        'Cookie': kvRead('app_cookie')
    });
    const data = JSON.parse(resp.body);

    // Surge 面板支持 HTML
    const html = `
        <h3>📊 账户信息</h3>
        <p>用户名: ${data.nickname || '-'}</p>
        <p>等级: ${data.level || '-'}</p>
        <p>积分: ${data.points || 0}</p>
        <p>VIP: ${data.vip ? '✅' : '❌'}</p>
    `;
    $done(html);
})().catch((e) => $done(`<p>❌ 加载失败</p>`)).finally(() => {});
```

---

## 八、HAR 抓包→脚本工作流

### 8.1 解析 HAR 提取关键接口

使用仓库附带的 `scripts/har_parser.py` 工具：

```bash
# 解析 .har 文件
python3 scripts/har_parser.py 抓包.har

# 解析 .zip 压缩包（部分抓包工具导出的格式）
python3 scripts/har_parser.py 抓包.zip

# 显示更多细节
python3 scripts/har_parser.py 抓包.har --verbose
```

工具会自动：
- 识别 .har / .zip / .json 三种格式
- 过滤无关请求（图片/字体/CDN/统计）
- 标记 VIP/订阅相关字段
- 显示关键请求头（Cookie/Authorization/Token）

示例输出：

```
📂 文件: example.har (2.3MB)
📊 共 142 条请求

============================================================
🟢 GET 200 | 1.2KB | json
  URL: https://api.example.com/v1/user/info
  Cookie: session=abc123...
  响应字段: code, message, data, vip, vip_type, expire_time
  🔑 可能需要的字段: vip, vip_type, expire_time
     vip = 0
     vip_type = "normal"
     expire_time = 0

============================================================
🟢 POST 200 | 0.5KB | json
  URL: https://api.example.com/user/signin
  响应字段: code, message, data
```

### 8.2 从 HAR 到脚本的完整流程

### 8.2 从 HAR 到脚本的完整流程

```
Step 1: 获取 HAR
  ├─ QX 抓包 → 导出 .har
  ├─ Surge → 导出 .har
  └─ Charles → 导出 .har

Step 2: 解析 HAR
  ├─ 找出签到/API 接口（POST/GET 请求）
  ├─ 记录 Cookie / Authorization / User-Agent
  └─ 记录请求体和响应体结构

Step 3: 确定脚本类型
  ├─ 有 VIP/订阅接口 → 解锁脚本
  ├─ 有签到/积分接口 → 签到脚本
  └─ 需要 Cookie → 再加 Cookie 采集

Step 4: 套用模板
  ├─ 解锁 → 模式一/二/三
  ├─ 签到 → 模板 + Cookie 采集
  └─ 多账户 → 多账户模板

Step 5: 测试
  ├─ QX/Surge 中加载脚本
  ├─ 触发对应接口
  └─ 看日志 → 调字段 → 上线
```

---




## 九、Egern 兼容适配

### 9.1 各平台命名对照

同一概念在不同平台叫法不同：

|概念|QX|Surge|Loon|Egern|
|---|---|---|---|---|
|配置单元|重写|模块|插件 (`.plugin`/`.lpx`)|模块 (`.yaml`)|
|请求拦截|`script-request-header`|`http-request`|`http-request`|`http_request`|
|响应拦截|`script-response-body`|`http-response`|`http-response`|`http_response`|
|定时任务|`[task_local]`|`type=cron`|`cron`|`schedule`|
|面板/小组件|不支持|`type=generic`|不支持|`generic` → Widget DSL|
|脚本触发|URL匹配|URL正则匹配|URL正则匹配|URL正则匹配|
|持久化|`$prefs`|`$persistentStore`|`$persistentStore`|`ctx.storage`|
|HTTPS解密|`[mitm]`|`[MITM]`|`[MITM]`|`mitm`|

> 注: Loon 的 `.lpx` 是最新的插件格式，与 `.plugin` 格式内容相同，仅扩展名不同。

### 9.2 Egern 脚本 API 速览

Egern 的脚本系统与 QX/Surge 有本质区别——它是异步的，用 `export default async function(ctx)` 导出。

|功能|QX/Surge|Egern|
|---|---|---|
|脚本结构|`$done({body})`|`return {body}`|
|响应体|`JSON.parse($response.body)`|`await ctx.response.json()`|
|请求体|`$request.body`|`await ctx.request.text()`|
|HTTP请求|`$task.fetch()` / `$httpClient.get()`|`await ctx.http.get()`|
|存储|`$prefs.valueForKey()`|`ctx.storage.get()`|
|通知|`$notification.post()`|`ctx.notify({title, body})`|
|中断请求|无|`return ctx.abort()`|
|直接返回|无|`return ctx.respond({status, body})`|
|请求头|`$request.headers` (普通对象)|`ctx.request.headers` (Headers对象, `.get()`)|
|响应头|`$response.headers`|`ctx.response.headers`|

### 9.3 环境变量与 jq 重写

#### 环境变量 `ctx.env`

Egern 脚本可以从配置中读取环境变量，同一脚本无需修改即可适配不同 App：

```yaml
# Egern 配置中传递参数给脚本
scriptings:
  - http_response:
      name: 通用解锁
      match: ^https?://api\.example\.com/vip
      script: https://.../unlock.js
      env:
        vip_field: data.vip.status
        vip_value: "true"
```

```javascript
// unlock.js — 通过 ctx.env 读取配置参数
export default async function(ctx) {
  const data = await ctx.response.json();
  // 从环境变量读取要改的字段和值
  const field = ctx.env.vip_field;     // "data.vip.status"
  const value = ctx.env.vip_value;     // "true"
  // 用点分路径设置深层字段
  const keys = field.split('.');
  let obj = data;
  for (let i = 0; i < keys.length - 1; i++) obj = obj[keys[i]];
  obj[keys[keys.length - 1]] = value === "true" ? true : value;
  return { body: data };
}
```

#### jq 过滤器（不写 JS 也能改响应体）

Egern 支持在 body_rewrites 中直接用 jq 表达式修改 JSON，性能更好：

```yaml
body_rewrites:
  # JQ 过滤器 — 完全不需要 JS
  - request_regex:
      match: ^https?://api\.example\.com/vip
      jq:
        - '.vip = 1'
        - '.vip_type = "svip"'
        - '.expires = "4092599349000"'
  # 深层嵌套
  - request_regex:
      match: ^https?://api\.example\.com/user
      jq:
        - '.data.status = "active"'
        - 'del(.data.ads)'
```

### 9.4 跨平台适配层

一个脚本同时兼容 QX/Surge/Loon/Egern：

```javascript
// 多平台适配 —— QX/Surge/Loon/Egern 通杀
(async function() {
  // === 检测平台 ===
  const isEgern = typeof exportDefault !== 'undefined';
  const isQX = typeof $task !== 'undefined';
  const isSurge = typeof $httpClient !== 'undefined' && !isQX;

  // === 统一 HTTP ===
  async function httpGet(url, headers = {}) {
    if (isEgern) {
      const resp = await ctx.http.get(url, { headers });
      return { status: resp.status, body: await resp.text(), headers: resp.headers };
    }
    // QX/Surge/Loon 走原有逻辑
    // ...
  }

  // === 统一存储 ===
  function read(key) {
    if (isEgern) return ctx.storage.get(key) || '';
    if (isQX) return $prefs.valueForKey(key) || '';
    if (isSurge) return $persistentStore.read(key) || '';
    return '';
  }
  function write(key, val) {
    if (isEgern) return ctx.storage.set(key, val);
    if (isQX) return $prefs.setValueForKey(val, key);
    if (isSurge) return $persistentStore.write(val, key);
  }

  // === 执行 ===
  // ... 主逻辑 ...
})();
```

### 9.5 Egern 模块格式

Egern 模块**直接兼容 Surge 的 `.sgmodule` 格式**，不需要转换也无需单独维护：

```ini
# 以下 .sgmodule 文件 Surge 和 Egern 都能用
#!name=示例模块
#!desc=模块描述
#!author=作者

[Script]
解锁 = type=http-response,pattern=^https?://api\.example\.com/vip,script-path=https://...,requires-body=true

[MITM]
hostname = api.example.com
```

**核心结论：** Surge 和 Egern 的模块是通用的。只需维护 `surge/` 目录下的 `.sgmodule` 文件，两个平台都能用。

如果需要在 Egern 主配置中直接嵌入而不是引用模块，使用 YAML 格式：

```yaml
# Egern 主配置中的脚本配置（非模块）
scriptings:
  - http_response:
      name: "解锁"
      match: "^https?://api\.example\.com/vip"
      script_url: "https://.../AppName.js"
      body_required: true

mitm:
  hostnames:
    - "api.example.com"
```

### 9.6 Egern 版解锁模板

```javascript
// Egern 解锁模板 — Response 脚本
export default async function(ctx) {
  const data = await ctx.response.json();

  // === 改 VIP 字段 ===
  data.vip = 1;
  data.is_vip = true;
  if (data.data) data.data.vip = 1;
  if (data.user) data.user.vip = true;
  data.expires = "4092599349000";

  return { body: data };
}
```

### 9.7 Egern 版签到模板

```javascript
// Egern 签到模板 — Schedule 脚本
export default async function(ctx) {
  const cookie = ctx.storage.get('app_cookie');
  if (!cookie) {
    ctx.notify({ title: '签到', body: '❌ 未获取到 Cookie' });
    return;
  }

  const resp = await ctx.http.get('https://api.example.com/sign/in', {
    headers: { 'Cookie': cookie }
  });
  const result = await resp.json();
  const msg = result.message || '签到完成';

  ctx.notify({ title: '签到结果', body: msg });
}
```

### 9.8 存量脚本迁移

现有 QX/Surge 脚本迁移到 Egern 的对照表：

|操作|QX 写法|Egern 写法|
|---|---|---|
|修改变量|`$done({body: JSON.stringify(obj)})`|`return {body: obj}`|
|解析响应|`JSON.parse($response.body)`|`await ctx.response.json()`|
|读请求头|`$request.headers['Cookie']`|`ctx.request.headers.get('Cookie')`|
|返回空|`$done({})` (不修改)|`return` (不修改)|
|拒绝请求|无法|`return ctx.abort()`|
|直接响应|无法|`return ctx.respond({status:200, body:'OK'})`|
|读存储|`$prefs.valueForKey('k')`|`ctx.storage.get('k')`|
|写存储|`$prefs.setValueForKey('v', 'k')`|`ctx.storage.set('k', 'v')`|

### 9.9 自动转换（推荐）

**方案一：Script-Hub（全自动，推荐）**

[Script-Hub](https://github.com/Script-Hub-Org/Script-Hub) 是一个高级脚本转换器，支持 QX → Surge/Loon/Stash/Egern/Shadowrocket 之间的互转：

```yaml
# 使用方法
# 1. 浏览器打开 Script-Hub 网页
# 2. 来源类型: QX 重写/ Surge 模块 / Loon 插件
# 3. 目标类型: Egern
# 4. 输入我们的 QX rewrite 规则链接
# 5. 一键转换 → 得到 Egern 配置
```

转换效果示例：

```
# QX 规则:
^https?://api\.example\.com/vip url script-response-body https://.../App.js

# → Script-Hub 自动转为 Egern:
http-response:
  - match: ^https?://api\.example\.com/vip
    script: https://.../App.js

# QX [task_local]:
30 8 * * * https://.../checkin.js

# → Egern:
schedule:
  - cron: 30 8 * * *
    script: https://.../checkin.js

# QX [mitm]:
hostname = api.example.com

# → Egern:
mitm:
  - hostname: api.example.com
```

**方案二：Egern 模块转换器（仅限 Surge→Egern）**

[gen.egernapp.com](https://gen.egernapp.com/) 可以将 Surge 模块转为 Egern 格式。

**注意：** 脚本内部的 JS 代码（`$done()` vs `return`）Script-Hub 尚不能自动转换。如需在 Egern 原生运行脚本，参考 9.2-9.6 节的迁移指南。


## 十、Surge 独有脚本类型

Surge 除了 `http-request` / `http-response` / `cron` / `generic` 外，还有三种其他平台没有的脚本类型。

### 10.1 `type=event` — 事件脚本

当指定事件发生时触发。目前支持两种事件：

**`network-changed` — 网络变化时触发：**
```ini
[Script]
network-watch = type=event,event-name=network-changed,script-path=network.js
```

```javascript
// network.js — 网络变化时通知
$notification.post('网络切换', $network.wifi.ssid || '蜂窝网络', 
  `DNS: ${$network.dns.join(', ')}`);
$done();
```

**`notification` — 通知事件：**
Surge 弹出通知时触发，脚本可以获取通知内容：
```javascript
// notification = type=event,event-name=notification,script-path=noti.js
console.log($event.data);  // 通知数据
$done();
```

### 10.2 `type=dns` — DNS 脚本

自定义 DNS 响应，可以拦截/修改特定域名的解析结果：

```ini
[Script]
dns-rules = type=dns,script-path=dns.js
```

```javascript
// 拦截指定域名，返回自定义 IP
if ($domain === 'ads.example.com') {
  $done({ matched: true, address: '127.0.0.1', ttl: 600 });
} else if ($domain === 'tracker.example.com') {
  $done({ matched: true, drop: true });  // 直接丢弃
} else {
  $done({});  // 不处理，走正常 DNS
}
```

参数说明：
- `matched: true` — 匹配此规则
- `address: 'IP'` — 返回自定义 IP（IPv4 或 IPv6）
- `drop: true` — 丢弃该 DNS 查询
- `ttl: 秒数` — 缓存时间

### 10.3 `type=rule` — 规则脚本

在 `[Rule]` 段中作为规则使用。可以动态决定是否匹配：

```ini
[Script]
ssid-rule = type=rule,script-path=ssid-rule.js

[Rule]
SCRIPT,ssid-rule,ProxyA
```

```javascript
// ssid-rule.js — 根据 WiFi SSID 决定是否走代理
if ($network.wifi.ssid === 'MyHome') {
  $done({ matched: false });  // 不匹配，继续下一条规则
} else {
  $done({ matched: true });   // 匹配，走 ProxyA
}
```

可用的 `$request` 属性：
```javascript
$request.hostname     // 主机名
$request.destPort     // 目标端口
$request.processPath  // 进程路径
$request.userAgent    // User-Agent
$request.url          // 完整 URL
$request.sourceIP     // 源 IP
$request.dnsResult    // DNS 解析结果
```

### 10.4 `$network` — 网络状态对象

Surge 独有（QX/Loon 均无）：

```javascript
// WiFi 信息
$network.wifi.ssid;      // WiFi 名称
$network.wifi.bssid;     // WiFi BSSID

// 蜂窝网络
$network.cellular.radio; // 蜂窝制式 (LTE/NR/etc)

// DNS
$network.dns;            // DNS 服务器列表 [String]

// 网关
$network.gateway;        // 网关 IP
```

典型用途：根据网络环境切换策略、WiFi SSID 判断、DNS 变更通知。

### 10.5 Surge 模块封装

与 QX 的配置嵌入不同，Surge 用 `.sgmodule` 文件封装模块：

```ini
#!name=示例模块
#!desc=模块描述
#!author=作者
#!homepage=https://github.com/...

[Script]
解锁 = type=http-response,pattern=^https?://api\.example\.com/vip,script-path=https://...,requires-body=true

[Script]
签到 = type=cron,cronexp="30 8 * * *",script-path=https://...,timeout=60

[MITM]
hostname = api.example.com
```

使用 `Script-Hub` 可以在各平台模块间互相转换。


## 十一、高级技巧

### 11.1 JQ 表达式修改（无需JS，更轻量）

QX 最新版本支持 JQ 表达式直接在重写规则中修改 JSON 响应体，无需编写 JavaScript。

**JQ 语法示例：**

```
# 将 ads 数组置空
^https?:\/\/api\.example\.com\/ad url script-response-body jq '.ads = []'

# 将 ad_enabled 设为 false
^https?:\/\/api\.example\.com\/config url script-response-body jq '.ad_enabled = false'

# 同时修改多个字段
^https?:\/\/api\.example\.com\/vip\/info url script-response-body jq '.vip = 1 | .vip_type = "svip" | .expires = "4092599349000"'

# 深层嵌套操作
^https?:\/\/api\.example\.com\/user url script-response-body jq '.data.vip = true | .data.expireTime = "4092599349000"'

# 删除字段
^https?:\/\/api\.example\.com\/response url script-response-body jq 'del(.ads) | del(.tracker)'
```

**JQ vs JS 的选择：**

|场景|推荐方式|原因|
|---|---|---|
|简单字段修改（改1-3个值）|JQ|一行搞定，性能好|
|复杂逻辑（条件判断、循环）|JS|JQ 不支持复杂逻辑|
|去广告（置空数组/改开关）|JQ|最常用场景，JQ 最合适|
|替换整个响应体|JS|需要完整构造新 JSON|
|按 URL 分路径处理|JS|JQ 无法做 URL 判断|

### 11.2 Reject 系列（无需脚本，零开销去广告）

QX 内置的 reject 类型是去广告最高效的方式：

```
# 直接拒绝请求（返回 404）
^https?:\/\/ad\.example\.com\/track url reject

# 返回空 JSON 对象（适用于广告API）
^https?:\/\/api\.example\.com\/ad url reject-dict

# 返回空 JSON 数组
^https?:\/\/api\.example\.com\/ad\/items url reject-array

# 返回 1px 图片
^https?:\/\/ad\.example\.com\/banner url reject-img

# 返回空 200
^https?:\/\/ad\.example\.com\/ping url reject-200
```

### 11.3 Conf 文件管理规则

```
# AD_Block.conf
[rewrite_local]
^https?:\/\/ad\.example\.com url reject
^https?:\/\/api\.example\.com\/ad url reject-dict

[mitm]
hostname = ad.example.com, api.example.com
```

### 11.4 模块化设计

复杂脚本建议拆分为 Cookie/签到/解锁 三个独立文件。

## 十二、仓库结构说明

### 文件分布

|目录|平台|格式|说明|
|---|---|---|---|
|`script/`|通用|`.js`|核心脚本源码|
|`surge/`|Surge / Egern|`.sgmodule`|Surge 模块，Egern 通用|
|`loon/`|Loon|`.plugin` / `.lpx`|Loon 插件（新旧双格式）|
|`python/`|通用|`.py`|Python 辅助脚本|

### 核心原则

1. **只维护一份 JS** — 所有平台共用 `script/` 下的 JS 文件
2. **Surge 和 Egern 模块通用** — `.sgmodule` 两个平台都能用
3. **Loon 新旧兼容** — 同时保留 `.plugin`（旧）和 `.lpx`（新）格式
4. **解锁脚本** — Apple 收据统一走 `UniversalReceipt.js`，各 App 自有 API 走各自 JS

### 后续工作

- [ ] App 识别库：常见 App 的 URL 规则和字段映射
- [ ] 自动 HAR 解析脚本：输入 HAR 自动输出脚本框架
- [ ] Cookie 失效检测：自动判断 Cookie 是否过期
- [ ] 多语言支持：支持更多平台（Stash、LanceList 等）


---

## 十、RevenueCat 4.x 订阅解锁（重要更新）

### 10.1 RevenueCat SDK 特征识别

RevenueCat 是 iOS App 最常用的第三方订阅管理 SDK。抓包时通过以下特征识别：

```json
// 请求头特征
X-Platform: iOS
X-Version: 4.x              // SDK 版本
X-StoreKit2-Enabled: false  // StoreKit1 模式
X-Client-Bundle-ID: com.example
Authorization: Bearer appl_...  // RevenueCat 公钥

// 响应头特征
x-signature: ...  // SDK 4.x 新增响应签名验证
x-revenuecat-etag: ...
```

常见 RevenueCat 域名：
- `api.revenuecat.com`（主域名）
- `api.rc-backup.com`（备用域名）

### 10.2 RevenueCat 4.x 关键变化

SDK 4.x 相比旧版增加了 `x-signature` 响应签名验证机制。**只改响应体不够**——SDK 会校验签名，body 改了但签名不对，SDK 直接拒绝并用缓存数据覆盖。

**解决方案：双规则（body + header 两条规则指向同一个脚本）**

```ini
[MITM]
hostname = api.revenuecat.com, api.rc-backup.com

[rewrite_local]
# 规则1: 改响应体 - 注入PRO权益
^https?://api.(revenuecat|rc-backup).com/v1/.* url script-response-body https://raw.githubusercontent.com/7452323/QuantumultX/main/script/AppName.js

# 规则2: 去签名头 - 否则SDK拒绝修改后的body
^https?://api.(revenuecat|rc-backup).com/v1/.* url script-response-header https://raw.githubusercontent.com/7452323/QuantumultX/main/script/AppName.js
```

### 10.3 JavaScript 脚本模板

```javascript
// ==Header模式（script-response-header）==
if (!$response.body) {
  var h = $response.headers;
  delete h['x-signature'];        // 去签名验证
  delete h['etag'];               // 去缓存标签
  delete h['x-revenuecat-etag'];
  h['Cache-Control'] = 'no-cache'; // 强制重新拉取
  $done({headers: h});
  return;
}

// ==Body模式（script-response-body）==
try {
  var obj = JSON.parse($response.body);
  var now = new Date().toISOString();

  // 永久买断: expires_date = null
  // 订阅制: expires_date = 未来日期
  var pro = {
    expires_date: null,
    product_identifier: "product_id",
    purchase_date: now
  };

  // 任何含 subscriber 的响应都注入
  if (obj.subscriber) {
    obj.subscriber.entitlements = { pro: pro };
    obj.subscriber.subscriptions = { product_id: {
      expires_date: null, period_type: "normal",
      purchase_date: now, store: "app_store"
    }};
  }
  // offerings 也注入保底（部分SDK版从offerings读权益）
  if (obj.offerings) {
    obj.subscriber = { entitlements: { pro: pro }, subscriptions: {} };
  }

  $done({body: JSON.stringify(obj)});
} catch(e) { $done({}); }
```

### 10.4 RevenueCat 抓包关键字段解读

| HAR字段 | 含义 | 用途 |
|---------|------|------|
| `X-Platform: iOS` | iOS平台 | 确认是Apple端订阅 |
| `X-StoreKit2-Enabled: false` | 使用StoreKit1 | 依赖服务端验证，可MITM |
| `X-Version: 4.x` | SDK版本号 | ≥4.x需要处理x-signature |
| `Authorization: Bearer appl_...` | RevenueCat公钥 | 区分是RevenueCat请求 |
| `x-signature` | 响应签名 | 必须删除否则body修改无效 |
| `x-revenuecat-etag` | 响应缓存标签 | 删除强制走新数据 |
| `$RCAnonymousID:xxx` | 匿名用户ID | 每个安装唯一 |
| `X-Client-Bundle-ID` | App的Bundle ID | 确认目标App |
| `product_entitlement_mapping` | 产品→权益映射 | 知道哪个product对应哪个entitlement |
| `/v1/subscribers/{id}` | 订阅状态（核心） | 改这里返回PRO |
| `/v1/subscribers/{id}/offerings` | 付费墙 | 注入subscriber保底 |
| `/v1/receipts` | 收据验证 | "恢复购买"触发，注入PRO |

### 10.5 永久买断 vs 订阅制

| 类型 | expires_date | 特点 |
|------|-------------|------|
| 永久买断 | `null` | 一次付费永久使用，不续期 |
| 订阅制 | `2099-12-31T23:59:59Z` | 定期扣费，有过期时间 |
| 免费试用 | 同上（但 `period_type: "trial"`） | 限时免费体验 |

### 10.6 常见问题

**Q: 恢复购买成功，但下次启动又没了？**
A: SDK启动时后台刷新订阅状态。如果MITM没拦截订阅刷新请求，返回的"无PRO"状态会覆盖缓存。方案：全API路径匹配 + 清掉etag/signature头。

**Q: 抓包里没有 `/v1/subscribers/{id}` 请求？**
A：SDK缓存了上次结果。杀掉app重开，或者卸载重装（首次启动必定请求）。

**Q: Surge/Loon怎么配？**
A：Surge用 `type=http-response`，Loon用 `http-response` 单条规则即可（两者都同时拦截body+header）。
