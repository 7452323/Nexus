---
name: Quantumultx
description: "Quantumult X 全能脚本编写技能。覆盖 5 大脚本类型、配置文件全字段详解、MITM抓包→脚本流程、rewrite_local/remote、task_local、配置片段、资源解析器、HAR→脚本转换、持久化与BoxJS"
tags: [QuantumultX, proxy, rewrite, task, mitm, filter, policy, boxjs, script, har]
---

# Quantumult X 全能脚本大师

从抓包到脚本到上线全流程。用户提供 HAR/JSON/ZIP 抓包数据时，分析后输出可用的 QX 脚本。

---

## 📋 快速导航

| # | 章节 | 内容 |
|---|------|------|
| 1 | 配置语法详解 | [general] [dns] [policy] [server] [filter] [rewrite] [task] [mitm] |
| 2 | 脚本类型总览 | 解锁 / 签到 / Cookie / 去广告 / 面板 |
| 3 | 脚本 API 参考 | $task.fetch / $notify / $prefs / $persistentStore / $done |
| 4 | HAR→脚本工作流 | 抓包 → 分析 → 生成 rewrite/task 规则 |
| 5 | Rewrite 详解 | 响应体修改 / 请求头修改 / reject / reject-dict / 302 |
| 6 | Task 详解 | cron/event-interaction/event-network + task-gallery |
| 7 | 资源解析器 | 自定义节点/分流/重写转换 |
| 8 | 配置片段 (snippet) | .snippet 文件创建与引用 |
| 9 | 持久化与 BoxJS | $prefs.write/read + BoxJS 订阅管理 |
| 10 | 去广告实战 | 从抓包到 reject / reject-dict / 响应体替换 |
| 11 | 实战模板 | 5 个可直接用的完整脚本模板 |

---

## 一、配置文件详解

### [general] 通用设置

```
server_check_url=http://www.qualcomm.cn/generate_204   ;节点测试地址
server_check_timeout=2000                                 ;测试超时(ms)
resource_parser_url=https://.../resource-parser.js       ;资源解析器
geo_location_checker=http://ip-api.com/json/?lang=zh-CN, https://.../IP_API.js
running_mode_trigger=filter, filter, asus-5g:all_direct  ;按WiFi自动切换模式
ssid_suspended_list=Asus                                  ;暂停列表
dns_exclusion_list=*.qq.com                              ;不走fake-ip域名
udp_whitelist=53, 80-427, 444-65535                      ;UDP白名单
udp_drop_list=1900, 80                                    ;UDP丢弃(不发ICMP)
fallback_udp_policy=direct
excluded_routes=192.168.0.0/16, 172.16.0.0/12, 100.64.0.0/10, 10.0.0.0/8
doh_user_agent=Agent/1.0
;dns_reject_domain_behavior = loopback | no-error-no-answer | nxdomain | none
;icmp_auto_reply = true
```

### [dns] DNS 设置

```
[dns]
server=114.114.114.114                                     ;普通DNS(多个并发)
server=223.5.5.5
doh-server=https://dns.alidns.com/dns-query              ;DoH (并发)
doq-server = quic://dns.adguard.com                       ;DoQ (覆盖DoH)
;prefer-doh3                                               ;启用DoH3
;no-system                                                 ;禁用系统DNS
;no-ipv6
circumvent-ipv4-answer = 127.0.0.1, 0.0.0.0             ;DNS去广告过滤
;server=/*.taobao.com/223.5.5.5                          ;指定域名DNS
;address=/example.com/192.168.1.1                        ;域名→IP映射
;alias=/example.com/another-example.com                  ;域名别名映射
```

### [policy] 策略组

**6 种类型：**
| 类型 | 说明 |
|------|------|
| static | 手动选择节点 |
| available | 自动选第一个可用 |
| round-robin | 轮流使用 |
| url-latency-benchmark | 选延迟最低 |
| dest-hash | 相同域名固定节点 |
| ssid | 按网络自动切换 |

```conf
[policy]
static=🍎 苹果服务, direct, proxy, img-url=https://...
static=🌏 国外网站, proxy, direct, img-url=...
static=🇭🇰 香港节点, server-tag-regex=香港|HK|Hong, img-url=...

;server-tag-regex 按节点名正则筛选
;resource-tag-regex 按订阅标签正则筛选
;img-url 策略组图标(108×108 png)
```

### [server_local] 本地节点

```conf
[server_local]
;Shadowsocks
shadowsocks=example.com:80, method=aes-128-gcm, password=pwd, obfs=http, obfs-host=apple.com, obfs-uri=/resource/file, fast-open=false, udp-relay=false, tag=ss-01

;Shadowsocks + TLS
shadowsocks=example.com:443, method=chacha20, password=pwd, obfs=over-tls, obfs-host=apple.com, tls-verification=true, udp-relay=true, tag=ss-tls-01

;Shadowsocks 2022
shadowsocks=example.com:80, method=2022-blake3-aes-128-gcm, password=BJDBGeLKx/..., udp-relay=true, tag=ss2022-01

;VMess
vmess=example.com:443, method=none, password=uuid, obfs=over-tls, fast-open=false, udp-relay=false, tag=vmess-tls
;disable aead: aead=false ;TLS指纹: tls-pubkey-sha256=xxx

;Trojan
trojan=example.com:443, password=pwd, over-tls=true, tls-verification=true, fast-open=false, udp-relay=false, tag=trojan-01
;Reality
trojan=example.com:443, password=pwd, over-tls=true, reality-base64-pubkey=xxx, reality-hex-shortid=xxx, tag=trojan-reality

;HTTP
http=user:pass@example.com:80, over-tls=false, tag=http-01

;SOCKS5
socks5=user:pass@example.com:1080, over-tls=false, udp-relay=false, tag=socks5-01
```

### [server_remote] 远程节点订阅

```conf
[server_remote]
https://example.com/sub, tag=订阅名称, update-interval=86400, opt-parser=true, img-url=https://..., enabled=true
;本地节点片段
;servers.snippet, tag=本地节点, enabled=false
```

### [filter_local] 本地分流

```conf
[filter_local]
;规则类型: host / host-suffix / host-keyword / user-agent / geoip / ip-cidr / ip-cidr6 / ip-asn / final
;动作: proxy / direct / reject / reject-200 / reject-tinygif
host, example.com, proxy
host-suffix, .apple.com, direct
host-keyword, adservice, reject
geoip, cn, direct
ip-cidr, 10.0.0.0/8, direct
final, proxy
;force-remote-dns 参数: host, example.com, proxy, force-remote-dns
```

### [filter_remote] 远程分流

```conf
[filter_remote]
https://raw.githubusercontent.com/DivineEngine/Profiles/master/Quantumult/Filter/Guard/Advertising.list, tag=🚦去广告, update-interval=86400, opt-parser=true, enabled=true
;force-policy 覆盖远程规则内的策略组名
;opt-parser=true 开启资源解析器
```

### [rewrite_local] 本地重写

```conf
[rewrite_local]
;reject: 拒绝请求(返回200+空body)
https://example.com/api/ads url reject

;reject-dict: 拒绝JSON请求(返回200+{})
https://example.com/api/json url reject-dict

;reject-200: 返回200+空body(不修改内容类型)
https://example.com/api/v1 url reject-200

;reject-img: 拒绝图片请求(返回1px透明GIF)
^https://example\.com/ads/gif url reject-img

;reject-array: 拒绝JSON数组请求(返回[])
^https://example\.com/api/list url reject-array

;请求头修改
^https://example\.com/account url request-header "X-Skip-Ad: true"

;响应体修改(正则替换)
^https://example\.com/api/data url response-body "old" replace "new"

;响应体JSON字段修改
^https://example\.com/api/user url response-json "vip" replace "true"

;302重定向
^https://example\.com/old url 302 https://example.com/new

;脚本处理(远程)
^https://example\.com/api url script-path=https://example.com/script.js
```

### [rewrite_remote] 远程重写

```conf
[rewrite_remote]
https://raw.githubusercontent.com/xxx/xxx/rewrite.snippet, tag=BoxJS, opt-parser=true, enabled=true
```

### [task_local] 计划任务

```conf
[task_local]
;类型1: cron(定时任务)
0 8 * * * https://raw.githubusercontent.com/xxx/script.js, tag=签到, img-url=https://..., enabled=true

;类型2: event-interaction(UI交互，长按策略组唤出)
event-interaction https://raw.githubusercontent.com/xxx/ui-check.js, tag=流媒体检测, img-url=checkmark.seal.system, enabled=true

;类型3: event-network(网络切换触发)
event-network script.js, tag=网络切换, enabled=false

;参数说明:
;url#force-timeout=10000&method=POST — 脚本超时+请求方法
;tag= — 任务名称
;img-url= — 图标(108×108 png)
;enabled=true/false
```

### [mitm] MITM 设置

```conf
[mitm]
;开启MITM需先安装根证书并信任
hostname = *.example.com, *.app.com, api.target.com
;pass-content-type — 仅处理指定Content-Type
;pass-content-type = text/html, application/json
```

---

## 二、脚本 API 参考

### QX 原生 API

```javascript
// HTTP 请求
$task.fetch(request).then(response => {
  // response.statusCode, response.headers, response.body
  $done();
}, reason => {
  // reason.error
  $done();
});

// request 对象格式
const request = {
  url: "https://example.com/api",
  method: "POST",         // GET/POST/PUT/DELETE/PATCH/HEAD
  headers: {"Key": "Value"},
  body: JSON.stringify({data: "test"}),  // POST请求体
  opts: {
    redirection: true,         // 跟随重定向(默认true)
    'skip-cert-verify': false,  // 跳过证书验证
    'auto-cookie': false        // 自动Cookie管理
  }
};

// 通知
$notify("标题", "副标题", "正文");

// 持久化存储(QX)
$prefs.valueForKey("key");    // 读
$prefs.setValueForKey("value", "key"); // 写

// 环境变量(脚本url中#后的参数)
const args = $environment.variables;
// url#force-timeout=10000&method=POST → args["force-timeout"], args["method"]

// 完成信号
$done();                    // 无返回值
$done({});                  // 空对象结束
$done(response);            // 修改响应后返回

// 日志
console.log("debug info");
```

### $task.fetch 参数详解

```javascript
const req = {
  url: "string",                                         // 必填
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH" | "HEAD", // 默认GET
  headers: { "Content-Type": "application/json" },        // 可选
  body: "string | JSON.stringify(obj)",                   // POST时使用
  opts: {
    redirection: true,          // 自动跟随重定向(默认true)
    'skip-cert-verify': false,   // 跳过证书验证
    'auto-cookie': false         // 自动保存Cookie
  }
};
```

### 多平台适配速查

| 功能 | QX | Surge | Loon |
|------|----|-------|------|
| HTTP请求 | $task.fetch | $httpClient.get/post | $httpClient.get/post |
| 持久化存储 | $prefs | $persistentStore | $persistentStore |
| 通知 | $notify | $notification.post | $notification.post |
| 完成 | $done() | $done() | $done() |
| 日志 | console.log | console.log | console.log |

### $task.fetch 响应对象

```json
{
  "statusCode": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "响应体字符串"
}
```

---

## 三、HAR → 脚本工作流

### 从抓包到脚本

```
1. 开启 QX HTTP抓取(长按风车 / 工具&分析→HTTP抓取)
2. 操作目标App → 关闭抓包
3. 查看抓包数据 → 找到目标请求
4. 分析URL、请求头、请求体、响应体
5. 根据需求决定脚本类型:
   - 去广告 → rewrite reject/reject-dict
   - 修改响应 → rewrite response-body/response-json
   - 签到/Cron → task_local + 脚本
   - 采集Cookie → rewrite request-header 捕获
6. 编写脚本 → 测试验证
```

### HAR 文件分析

当用户提供 HAR 文件/JSON/ZIP 时：

```javascript
// 1. 解析HAR entry
{
  "request": {
    "method": "POST",
    "url": "https://api.example.com/login",
    "headers": [{"name":"Cookie","value":"token=xxx"}],
    "postData": {"mimeType":"application/json","text":"{\"user\":\"test\"}"}
  },
  "response": {
    "status": 200,
    "headers": [{"name":"Set-Cookie","value":"session=abc"}],
    "content": {"text":"{\"success\":true}"}
  }
}

// 2. 提取关键信息
const url = entry.request.url;
const method = entry.request.method;
const reqHeaders = entry.request.headers;
const reqBody = entry.request.postData?.text;
const resBody = entry.response.content?.text;

// 3. 生成对应规则
// 去广告 → reject
// 修改响应 → response-body/response-json
// Cookie采集 → request-header
```

### 典型抓包发现→脚本生成

| HAR 发现 | 脚本生成 |
|----------|----------|
| URL 包含 ad/ads/sponsor | `^url url reject` 或 `^url url reject-dict` |
| 响应体 JSON 含 `"vip":0` | `^url url response-json "vip" replace "1"` |
| 响应体 HTML 含广告元素 | `^url url response-body "ad-code" replace ""` |
| 请求头含 Cookie/Token | rewrite request-header 捕获 + task_local 使用 |
| POST 签到接口 | task_local cron + 脚本执行签到 |
| 响应体含 `"ads":[...]` | `^url url response-json "ads" replace "[]"` |

---

## 四、Rewrite 详解

### 4.1 响应体修改

```conf
[rewrite_local]
;全响应体正则替换
^https://example\.com/api/v1/user url response-body "old-text" replace "new-text"

;JSON字段修改
^https://example\.com/api/v1/user url response-json "vip" replace "1"
^https://example\.com/api/v1/user url response-json "vip_expire" replace "4092599349"

;数组字段置空
^https://example\.com/api/v1/ads url response-json "ads" replace "[]"

;多字段修改(多次写)
^https://example\.com/api/v1/user url response-json "vip" replace "1"
^https://example\.com/api/v1/user url response-json "coins" replace "9999"
```

### 4.2 请求头修改

```conf
[rewrite_local]
;注入请求头
^https://example\.com/api/v1/data url request-header "X-API-Key: xxx"

;修改请求头值
^https://example\.com/api/v1/login url request-header "Authorization: Bearer token123"

;捕获Cookie(用于签到脚本)
^https://example\.com/api/v1/login url request-header "Cookie: .*"
```

### 4.3 Reject 系列

```conf
;reject — 拒绝请求(HTTP 200 + 空body)
;适用于: 图片广告、脚本文件
^https?://.*\.example\.com/ads/.* url reject

;reject-dict — 拒绝JSON请求(HTTP 200 + {})
;适用于: JSON API广告
^https?://.*\.example\.com/api/ad url reject-dict

;reject-200 — 返回200+空body(不修改Content-Type)
;适用于: 某些严格检查Content-Type的App
^https?://.*\.example\.com/track url reject-200

;reject-img — 返回1px透明GIF
;适用于: 图片广告
^https?://.*\.example\.com/ad\.gif url reject-img

;reject-array — 返回200 + []
;适用于: 期望数组响应的API
^https?://.*\.example\.com/api/list url reject-array
```

### 4.4 302 重定向

```conf
;URL重定向
^https://example\.com/old-path url 302 https://example.com/new-path

;跳转到空页面
^https://example\.com/ad-landing url 302 https://example.com/blank
```

### 4.5 脚本处理

```conf
;远程脚本
^https://example\.com/api/target url script-path=https://raw.githubusercontent.com/xxx/script.js
;远程脚本 + 自定义参数(url#后加参数)
^https://example\.com/api/target url script-path=https://raw.githubusercontent.com/xxx/script.js#key=value

;本地脚本(QX 脚本目录下的文件)
^https://example\.com/api/target url script-path=script.js
```

### 4.6 响应体脚本处理

```javascript
// 当rewrite脚本拦截到响应时:
const body = $response.body;

// 修改JSON
let obj = JSON.parse(body);
obj.data.vip = true;
obj.data.ads = [];
$done({body: JSON.stringify(obj)});

// 正则替换
const newBody = body.replace(/old/g, 'new');
$done({body: newBody});

// 直接返回新body
$done({body: '{"success":true,"vip":true}'});

// 修改响应头
$done({
  body: newBody,
  headers: {"X-Custom": "value"}
});
```

---

## 五、Task 详解

### 5.1 task_local 格式

```conf
[task_local]
;cron: 定时任务
格式: cron 脚本路径, tag=名称, img-url=图标, enabled=开/关

;event-interaction: UI交互(长按策略组/节点唤出)
event-interaction 脚本路径, tag=名称, img-url=图标, enabled=true

;event-network: 网络切换触发
event-network 脚本路径, tag=名称, enabled=false
```

### 5.2 cron 表达式

```
分钟 小时 日 月 周
*    *    * * *   = 每分钟
0    8    * * *   = 每天8点
*/30 *    * * *   = 每30分钟
0    8,20 * * *   = 每天8点和20点
0    9    * * 1-5 = 工作日9点
```

### 5.3 task-gallery(任务仓库)

```json
// gallery.json 格式
{
  "name": "签到脚本集",
  "description": "日常签到脚本",
  "tasks": [
    {
      "name": "签到",
      "url": "https://example.com/checkin.js",
      "cron": "0 8 * * *",
      "enabled": true,
      "icons": ["https://example.com/icon.png"]
    }
  ]
}
```

### 5.4 签到脚本模板

```javascript
// 签到脚本通用模板
const $ = new Env("签到脚本名称");

(async () => {
  // 1. 读取Cookie/Token
  const cookie = $.read("cookie_key");
  if (!cookie) {
    $.msg("签到失败", "未获取到Cookie", "请先通过重写采集Cookie");
    $.done();
    return;
  }

  // 2. 执行签到请求
  const response = await $.http.post({
    url: "https://api.example.com/checkin",
    headers: {
      "Cookie": cookie,
      "User-Agent": "Mozilla/5.0..."
    }
  });

  // 3. 解析结果
  const result = JSON.parse(response.body);
  if (result.success) {
    $.msg("签到成功", `获得${result.points}积分`, `总积分: ${result.total}`);
  } else {
    $.msg("签到失败", result.message || "未知错误", "");
  }
})();

function Env(name) {
  const isQX = typeof $task !== "undefined";
  const isSurge = typeof $httpClient !== "undefined";
  const isLoon = typeof $loon !== "undefined";

  this.read = (key) => {
    if (isQX) return $prefs.valueForKey(key);
    if (isSurge || isLoon) return $persistentStore.read(key);
  };

  this.write = (value, key) => {
    if (isQX) return $prefs.setValueForKey(value, key);
    if (isSurge || isLoon) return $persistentStore.write(value, key);
  };

  this.msg = (title, sub, body) => {
    if (isQX) $notify(title, sub, body);
    if (isSurge) $notification.post(title, sub, body);
    if (isLoon) $notification.post(title, sub, body);
  };

  this.http = {
    post: (params) => new Promise((resolve, reject) => {
      if (isQX) {
        $task.fetch({...params, method: "POST"}).then(resp => resolve(resp), err => reject(err));
      } else if (isSurge || isLoon) {
        $httpClient.post(params, (err, resp) => err ? reject(err) : resolve(resp));
      }
    }),
    get: (params) => new Promise((resolve, reject) => {
      if (isQX) {
        $task.fetch({...params, method: "GET"}).then(resp => resolve(resp), err => reject(err));
      } else if (isSurge || isLoon) {
        $httpClient.get(params, (err, resp) => err ? reject(err) : resolve(resp));
      }
    })
  };

  this.done = () => { $done(); };

  // 持久化存储管理(多账户)
  this.readAllKeys = () => {
    // QX: $prefs 无法列举所有key，需要自行维护key列表
    // 建议用固定的key命名: `scriptname_cookies`
    const raw = this.read("cookies");
    return raw ? JSON.parse(raw) : {};
  };
  this.saveCookies = (cookies) => {
    this.write(JSON.stringify(cookies), "cookies");
  };

  this.done = () => { $done(); };
}
```

### 5.5 多账户签到模板

```javascript
// 多账户签到
const $ = new Env("多账户签到");
const accounts = JSON.parse($.read("accounts") || "[]");

(async () => {
  if (accounts.length === 0) {
    $.msg("无账户", "请先在BoxJS或持久化中配置账户信息", "");
    $.done();
    return;
  }

  let results = [];
  for (const acc of accounts) {
    try {
      const resp = await $.http.post({
        url: "https://api.example.com/checkin",
        headers: { "Cookie": acc.cookie }
      });
      const data = JSON.parse(resp.body);
      results.push(`${acc.name}: ${data.message}`);
    } catch (e) {
      results.push(`${acc.name}: 失败`);
    }
  }

  $.msg("签到完成", `成功 ${accounts.length} 个账户`, results.join("\n"));
})();
```

### 5.6 Cookie 采集脚本

```conf
[rewrite_local]
;捕获登录时的Cookie
^https://example\.com/api/login url script-path=https://raw.githubusercontent.com/xxx/cookie.js
```

```javascript
// cookie.js — Cookie采集
const cookie = $request.headers["Cookie"] || $request.headers["cookie"];
if (cookie) {
  // 保存到持久化存储
  const existing = JSON.parse($prefs.valueForKey("cookies") || "{}");
  existing["example"] = cookie;
  $prefs.setValueForKey(JSON.stringify(existing), "cookies");
  $notify("Cookie获取成功", "example.com", cookie.substring(0, 50) + "...");
}
$done({});
```

---

## 六、去广告实战

### 6.1 去广告流程

```
1. 开启HTTP抓包 → 操作App → 关闭抓包
2. 在抓包列表中按关键字搜索: ad, ads, sponsor, promotion, tracking
3. 确定广告请求URL
4. 选择去广告方案:

方案A: URL直接拒绝
^https?://.*example\.com/ads/.* url reject

方案B: JSON API 返回空
^https?://.*example\.com/api/v1/ad url reject-dict

方案C: 响应体删除广告字段
^https?://.*example\.com/api/home url response-json "banner_ads" replace "[]"

方案D: 响应体正则过滤
^https?://.*example\.com/api/data url response-body "<ad>.*?</ad>" replace ""

5. 将规则添加到 [rewrite_local]
6. 将域名添加到 [mitm] hostname
7. 测试验证
```

### 6.2 去广告模板

```conf
[rewrite_local]
# 方案A: URL关键词匹配拒绝
^https?://.*\.googlesyndication\.com/.* url reject
^https?://.*\.doubleclick\.net/.* url reject
^https?://.*\.googleadservices\.com/.* url reject
^https?://.*\.applovin\.com/.* url reject

# 方案B: 特定API路径拒绝
^https?://api\.example\.com/v\d+/ad(url)? reject
^https?://api\.example\.com/v\d+/track(url)? reject-200

# 方案C: 响应体JSON字段清除
^https?://api\.example\.com/v\d+/home url response-json "ads" replace "[]"
^https?://api\.example\.com/v\d+/home url response-json "sponsor" replace "null"

[mitm]
hostname = *.googlesyndication.com, *.doubleclick.net, *.applovin.com, api.example.com
```

---

## 七、配置片段(snippet)

### 7.1 snippet 文件格式

```conf
; snippet 文件放在 iCloud/Quantumult X/Profiles/ 或 Scripts/ 目录
; 以 .snippet 后缀保存

[rewrite_local]
^https?://api\.example\.com/ad url reject

[mitm]
hostname = api.example.com
```

### 7.2 引用 snippet

```conf
;在配置文件中引用：
rewrite.snippet, tag=自定义重写, enabled=true
```

---

## 八、资源解析器

### 8.1 作用

将不兼容格式的远程资源(节点/分流/重写)自动转换为 QX 可用格式。

### 8.2 配置

```conf
[general]
resource_parser_url= https://fastly.jsdelivr.net/gh/KOP-XIAO/QuantumultX@master/Scripts/resource-parser.js
```

### 8.3 使用

在 `server_remote` / `filter_remote` / `rewrite_remote` 中添加：
```
opt-parser=true
```
即可启用解析器处理该订阅。

---

## 九、持久化与 BoxJS

### 9.1 QX 持久化

```javascript
// QX
$prefs.valueForKey("key");        // 读
$prefs.setValueForKey("value", "key"); // 写
```

### 9.2 BoxJS 订阅

BoxJS 提供 Web UI 管理持久化数据，通过 rewrite_remote 添加：

```conf
[rewrite_remote]
https://raw.githubusercontent.com/chavyleung/scripts/master/box/rewrite/boxjs.rewrite.quanx.conf, tag=BoxJS, opt-parser=true, enabled=true
```

然后在 BoxJS 里添加订阅(JSON)来管理各脚本的配置。

---

## 十、完整脚本模板

### 模板1: 去重写广告(最简)

```conf
[rewrite_local]
^https?://.*\.example\.com/ad\.json url reject-dict
[mitm]
hostname = *.example.com
```

### 模板2: JSON解锁会员

```conf
[rewrite_local]
^https?://api\.example\.com/v1/user url response-json "vip" replace "1"
^https?://api\.example\.com/v1/user url response-json "vip_expire" replace "4092599349"
[mitm]
hostname = api.example.com
```

### 模板3: 响应体替换

```conf
[rewrite_local]
^https?://api\.example\.com/v1/user url response-body "\"vip\":false" replace "\"vip\":true"
[mitm]
hostname = api.example.com
```

### 模板4: 每日签到(task_local)

```conf
[task_local]
0 8 * * * https://raw.githubusercontent.com/xxx/checkin.js, tag=每日签到, img-url=https://raw.githubusercontent.com/xxx/icon.png, enabled=true
```

### 模板5: 多规则组合

```conf
[rewrite_local]
^https?://api\.example\.com/v1/home url response-json "ads" replace "[]"
^https?://api\.example\.com/v1/home url response-json "banners" replace "[]"
^https?://api\.example\.com/v1/user url response-json "vip" replace "1"
^https?://stats\.example\.com/track url reject-200

[mitm]
hostname = api.example.com, stats.example.com
```

---

## 注意事项

- 添加 rewrite 规则后，对应的域名必须添加到 [mitm] hostname 中
- MITM 需要信任根证书才能生效
- 正则表达式中的 `.` 需要转义为 `\.`
- 多个 rewrite 规则作用于同一 URL 时，按顺序执行
- task_local 需 QX 处于运行状态且 task 开关开启
- 远程资源(server_remote/filter_remote/rewrite_remote)建议开启 `opt-parser=true` 以兼容各种格式
- 配置片段 .snippet 放在 `iCloud/Quantumult X/Profiles/` 或 `Scripts/` 目录
- 策略组的 `server-tag-regex` 支持正则匹配节点名进行筛选
