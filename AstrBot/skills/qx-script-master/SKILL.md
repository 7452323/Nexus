# QX Script Master

## Description
A comprehensive guide for writing proxy tool scripts for Quantumult X, Surge, Loon, and Egern. Covers 5 major script types: Unlock (VIP bypass), Check-in (daily签到), Cookie collection, Ad blocking, and Panel widgets. Includes HAR parsing workflow, multi-platform adaptation layer, Env.js framework integration, and 18 common patterns.

## Instructions

### Script Type Overview

| Type | Purpose | Trigger | Core Logic |
|------|---------|---------|------------|
| 🔓 Unlock | Bypass app VIP/subscription | Response interception (`script-response-body`) | Modify `$response.body` fields → `$done` |
| ✅ Check-in | Daily auto-checkin for points | Scheduled task (`cron`) | HTTP request to checkin API → notify result |
| 🍪 Cookie | Capture login session (prerequisite for checkin) | Request interception (`script-request-header`) | Extract Cookie/Authorization → persist |
| 🚫 Ad Block | Remove in-app ads | Response interception | Set ad fields to empty/false → `$done` |
| 📊 Panel | Display real-time info (Surge) | Scheduled refresh | Request data → render HTML |

### Universal Platform Detection

All scripts should detect the platform first:

```javascript
// ===== Platform Detection =====
const isQX = typeof $task !== 'undefined';
const isSurge = typeof $httpClient !== 'undefined';
const isLoon = typeof $loon !== 'undefined';

// ===== Universal HTTP Request =====
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

// ===== Cross-platform Persistent Storage =====
function kvRead(key) {
    if (isQX && $prefs.valueForKey) return $prefs.valueForKey(key) || '';
    if (isSurge && $persistentStore.read) return $persistentStore.read(key) || '';
    return '';
}

function kvWrite(key, val) {
    if (isQX && $prefs.setValueForKey) $prefs.setValueForKey(val, key);
    if (isSurge && $persistentStore.write) $persistentStore.write(val, key);
}

// ===== Notification =====
function sendNotify(title, subtitle, content) {
    if (typeof $notification !== 'undefined') {
        $notification.post(title, subtitle || '', content || '');
    } else {
        console.log(`${title}: ${subtitle} - ${content}`);
    }
}
```

### Unlock Script — Standard Pattern (70% of cases)

```javascript
var obj = JSON.parse($response.body);

// === Common VIP fields ===
obj.vip = 1;
obj.vip_type = "svip";
obj.isvip = 1;
obj.is_year = true;
obj.expires = "4092599349000";  // 2099 timestamp
obj.expire_time = "4092599349000";

// === Deep nesting ===
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

### URL-Pattern Routing (Multiple APIs in One Script)

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

### Check-in Script Template

```javascript
const $ = new Env('Checkin');

!(async () => {
    const cookie = 'your_cookie_here';
    const resp = await httpRequest('GET', 'https://api.example.com/sign/in', {
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0'
    });
    const data = JSON.parse(resp.body);
    const msg = data.message || data.msg || 'Completed';
    $.msg('Checkin', 'Done', typeof msg === 'string' ? msg : '');
})().catch((e) => $.log(`❌ ${e}`)).finally(() => $.done());
```

### Multi-Account Check-in

```javascript
if (typeof $request !== 'undefined') {
    const value = $request.headers['Cookie'] || $request.headers['Authorization'];
    if (value) {
        let cookies = kvRead('app_cookies').split('#').filter(Boolean);
        cookies = cookies.filter(c => c.slice(0, 15) !== value.slice(0, 15));
        cookies.push(value);
        kvWrite('app_cookies', cookies.join('#'));
        $.msg('Checkin', `Cookie saved (${cookies.length} accounts)`, '');
        $.done();
    }
}

!(async () => {
    const raw = kvRead('app_cookies');
    const accounts = raw.split('#').filter(Boolean);
    for (let i = 0; i < accounts.length; i++) {
        // ... checkin logic per account ...
    }
})().catch(console.log).finally(() => $.done());
```

### Ad Block Script

```javascript
var obj = JSON.parse($response.body);

['data', 'ads', 'adList', 'ad', 'banners', 'items', 'list'].forEach(key => {
    if (Array.isArray(obj[key])) obj[key] = [];
    if (obj.data && Array.isArray(obj.data[key])) obj.data[key] = [];
});

// Ad switch fields
['ad_enabled', 'showAd', 'show_ad', 'hasAd'].forEach(key => {
    if (obj[key] !== undefined) obj[key] = false;
});

$done({ body: JSON.stringify(obj) });
```

### Surge Panel Script

```javascript
const $ = new Env('Info Panel');

!(async () => {
    const resp = await httpRequest('GET', 'https://api.example.com/user/info', {
        'Cookie': kvRead('app_cookie')
    });
    const data = JSON.parse(resp.body);
    const html = `
        <h3>📊 Account Info</h3>
        <p>Username: ${data.nickname || '-'}</p>
        <p>Level: ${data.level || '-'}</p>
        <p>Points: ${data.points || 0}</p>
        <p>VIP: ${data.vip ? '✅' : '❌'}</p>
    `;
    $done(html);
})().catch((e) => $done(`<p>❌ Load failed</p>`)).finally(() => {});
```

### HAR Parsing Workflow

1. Export .har from proxy tool (QX/Surge/Charles)
2. Parse HAR to find checkin/VIP API endpoints
3. Record Cookies, Authorization, User-Agent headers
4. Identify script type (unlock/checkin/cookie)
5. Apply template
6. Test in proxy tool

### Common App VIP Fields Quick Reference

| App | Key URL Pattern | Fields to Modify | Target |
|-----|----------------|------------------|--------|
| CamScanner | `/purchase/cs/query_property` | `vip_type`, `auto_renewal`, `in_trial` | `"svip"`, `true`, `1` |
| PDF Expert | `/api/2.0/subscription` | `isPro`, `isEdu`, `expireDate` | `true`, `true`, `"2099-12-31"` |
| Notability | `/global` (GraphQL) | Full replace | See full replacement pattern |
| Lightroom | `/v1/profile` | `status`, `plan` | `"active"`, `"premium"` |

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| script_type | string | Yes | "unlock", "checkin", "cookie", "adblock", "panel" |
| platform | string | No | "qx", "surge", "loon", "egern" (detected automatically) |
| app_name | string | For unlock | Name of target app |
| har_file | string | For analysis | Path to HAR file for parsing |

## Examples

```
User: "Write an unlock script for CamScanner"
Agent: Use standard unlock pattern → identify VIP fields → generate complete script with Surge/Loon/QX rules.
```

```
User: "Parse this HAR file and write a checkin script"
Agent: Extract API endpoints → find Cookie → generate checkin script template.
```

## Notes
- Platform detection should be automatic — no user configuration needed
- For GraphQL responses, use the "full replacement" pattern (Mode 3)
- Store cookies using cross-platform kvRead/kvWrite functions
- For Egern compatibility, scripts use `export default async function(ctx)` pattern
- Script-Hub (https://script-hub.org) can auto-convert between QX/Surge/Loon formats
- QX supports JQ expressions directly in rewrite rules (no JS needed for simple modifications)
- Respect app developer's terms of service — these techniques are for educational purposes
