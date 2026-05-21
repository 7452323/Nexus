# QX 脚本大师 (QX Script Master)

## 描述
为 Quantumult X、Surge、Loon 和 Egern 编写代理工具脚本的全面指南。涵盖 5 大脚本类型：解锁（VIP 绕过）、签到（每日签到）、Cookie 采集、广告拦截和面板小组件。包含 HAR 解析工作流、多平台适配层、Env.js 框架集成和 18 种常见模式。

## 指令

### 脚本类型概览

| 类型 | 用途 | 触发方式 | 核心逻辑 |
|------|---------|---------|------------|
| 🔓 解锁 | 绕过应用 VIP/订阅 | 响应拦截 (`script-response-body`) | 修改 `$response.body` 字段 → `$done` |
| ✅ 签到 | 每日自动签到获取积分 | 定时任务 (`cron`) | HTTP 请求签到 API → 通知结果 |
| 🍪 Cookie | 捕获登录会话（签到的前置条件） | 请求拦截 (`script-request-header`) | 提取 Cookie/Authorization → 持久化 |
| 🚫 去广告 | 移除应用内广告 | 响应拦截 | 将广告字段设为空/false → `$done` |
| 📊 面板 | 显示实时信息（Surge） | 定时刷新 | 请求数据 → 渲染 HTML |

### 通用平台检测

所有脚本应首先检测平台：

```javascript
// ===== 平台检测 =====
const isQX = typeof $task !== 'undefined';
const isSurge = typeof $httpClient !== 'undefined';
const isLoon = typeof $loon !== 'undefined';

// ===== 通用 HTTP 请求 =====
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
```

### 解锁脚本 — 标准模式（70% 的情况）

```javascript
var obj = JSON.parse($response.body);

// === 常见 VIP 字段 ===
obj.vip = 1;
obj.vip_type = "svip";
obj.isvip = 1;
obj.is_year = true;
obj.expires = "4092599349000";  // 2099 时间戳
obj.expire_time = "4092599349000";

// === 深层嵌套 ===
if (obj.data) {
    obj.data.vip = 1;
    obj.data.is_vip = true;
}
if (obj.user) {
    obj.user.vip = 1;
    obj.user.viptype = "4";
}

$done({ body: JSON.stringify(obj) });
```

### URL 模式路由（一个脚本处理多个 API）

```javascript
var obj = JSON.parse($response.body);
var url = $request.url;

if (url.indexOf('/user/vip') != -1) {
    if (obj.data) obj.data.vip = true;
}
if (url.indexOf('/subscription/status') != -1) {
    if (obj.data) obj.data.status = "active";
}

$done({ body: JSON.stringify(obj) });
```

### 签到脚本模板

```javascript
const $ = new Env('签到');

!(async () => {
    const cookie = 'your_cookie_here';
    const resp = await httpRequest('GET', 'https://api.example.com/sign/in', {
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0'
    });
    const data = JSON.parse(resp.body);
    const msg = data.message || data.msg || '已完成';
    $.msg('签到', '完成', typeof msg === 'string' ? msg : '');
})().catch((e) => $.log(`❌ ${e}`)).finally(() => $.done());
```

### 多账户签到

```javascript
if (typeof $request !== 'undefined') {
    const value = $request.headers['Cookie'] || $request.headers['Authorization'];
    if (value) {
        let cookies = kvRead('app_cookies').split('#').filter(Boolean);
        cookies = cookies.filter(c => c.slice(0, 15) !== value.slice(0, 15));
        cookies.push(value);
        kvWrite('app_cookies', cookies.join('#'));
        $.msg('签到', `Cookie 已保存 (${cookies.length} 个账户)`, '');
        $.done();
    }
}

!(async () => {
    const raw = kvRead('app_cookies');
    const accounts = raw.split('#').filter(Boolean);
    for (let i = 0; i < accounts.length; i++) {
        // ... 每个账户的签到逻辑 ...
    }
})().catch(console.log).finally(() => $.done());
```

### 去广告脚本

```javascript
var obj = JSON.parse($response.body);

['data', 'ads', 'adList', 'ad', 'banners', 'items', 'list'].forEach(key => {
    if (Array.isArray(obj[key])) obj[key] = [];
    if (obj.data && Array.isArray(obj.data[key])) obj.data[key] = [];
});

// 广告开关字段
['ad_enabled', 'showAd', 'show_ad', 'hasAd'].forEach(key => {
    if (obj[key] !== undefined) obj[key] = false;
});

$done({ body: JSON.stringify(obj) });
```

### Surge 面板脚本

```javascript
const $ = new Env('信息面板');

!(async () => {
    const resp = await httpRequest('GET', 'https://api.example.com/user/info', {
        'Cookie': kvRead('app_cookie')
    });
    const data = JSON.parse(resp.body);
    const html = `
        <h3>📊 账户信息</h3>
        <p>用户名：${data.nickname || '-'}</p>
        <p>等级：${data.level || '-'}</p>
        <p>积分：${data.points || 0}</p>
        <p>VIP：${data.vip ? '✅' : '❌'}</p>
    `;
    $done(html);
})().catch((e) => $done(`<p>❌ 加载失败</p>`)).finally(() => {});
```

### HAR 解析工作流

1. 从代理工具（QX/Surge/Charles）导出 .har 文件
2. 解析 HAR 找到签到/VIP API 端点
3. 记录 Cookie、Authorization、User-Agent 头
4. 确定脚本类型（解锁/签到/Cookie）
5. 应用模板
6. 在代理工具中测试

### 常见应用 VIP 字段速查

| 应用 | 关键 URL 模式 | 要修改的字段 | 目标值 |
|-----|----------------|------------------|--------|
| 扫描全能王 | `/purchase/cs/query_property` | `vip_type`, `auto_renewal`, `in_trial` | `"svip"`, `true`, `1` |
| PDF Expert | `/api/2.0/subscription` | `isPro`, `isEdu`, `expireDate` | `true`, `true`, `"2099-12-31"` |
| Notability | `/global` (GraphQL) | 全替换 | 见完整替换模式 |
| Lightroom | `/v1/profile` | `status`, `plan` | `"active"`, `"premium"` |

## 参数

| 参数名 | 类型 | 必填 | 描述 |
|-----------|------|----------|-------------|
| script_type | string | 是 | "unlock", "checkin", "cookie", "adblock", "panel" |
| platform | string | 否 | "qx", "surge", "loon", "egern"（自动检测） |
| app_name | string | 解锁时 | 目标应用名称 |
| har_file | string | 分析时 | 用于解析的 HAR 文件路径 |

## 示例

```
用户："为扫描全能王写一个解锁脚本"
智能体：使用标准解锁模式 → 识别 VIP 字段 → 生成包含 Surge/Loon/QX 规则的完整脚本。
```

```
用户："解析这个 HAR 文件并写一个签到脚本"
智能体：提取 API 端点 → 找到 Cookie → 生成签到脚本模板。
```

## 备注
- 平台检测应自动完成——无需用户配置
- 对于 GraphQL 响应，使用"全替换"模式（模式3）
- 使用跨平台的 kvRead/kvWrite 函数存储 Cookie
- 为了 Egern 兼容性，脚本使用 `export default async function(ctx)` 模式
- Script-Hub (https://script-hub.org) 可以自动转换 QX/Surge/Loon 格式
- QX 支持在重写规则中直接使用 JQ 表达式（简单修改无需 JS）
- 尊重应用开发者的服务条款——这些技术仅用于学习目的
