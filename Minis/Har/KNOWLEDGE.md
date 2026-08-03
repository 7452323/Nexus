# HAR 分析 → 去广告/爆破会员 知识库

## 一、VIP/会员爆破模式总结

通过分析 NobyDa、Guding88、Crazy-Z7、Orz-3、ddgksf2013 等 14 个仓库的 150+ 个脚本，归纳出以下模式：

### 模式1: JSON完全替换
- 场景: 响应体简单，直接重写整个 JSON
- 示例: WPS Office, CamScanner, 百度网盘
- 代码: `$done({ body: JSON.stringify({ ... 完整数据 ... }) })`

### 模式2: JSON字段修改
- 场景: 只需改几个字段（最常见）
- 字段: vipExpire, vipFlag, vipStatus, isPro, entitlements, subscriptions
- 代码: 
  ```js
  var obj = JSON.parse($response.body);
  obj.data.vipExpire = "2099-01-01";
  obj.vip_status = 1;
  $done({body: JSON.stringify(obj)});
  ```

### 模式3: 正则替换
- 场景: 响应体不是标准 JSON 或只需快速替换
- 示例: NiChi (preview→free), 追追漫画 (vip_status→1)
- 代码:
  ```js
  var body = $response.body
    .replace(/isfree":\d/g, 'isfree":1')
    .replace(/vip_status":\d/g, 'vip_status":1')
    .replace(/show_ad":\w+/g, 'show_ad":false');
  $done({ body });
  ```

### 模式4: RevenueCat 通用解锁
- 场景: iOS 订阅制 App（最通用）
- 拦截: api.revenuecat.com/v1/subscribers/
- 关键: 同时处理 request header（删除 etag 防304）
- 模板:
  ```js
  // request-header → 删除 x-revenuecat-etag
  // response-body → 
  obj.subscriber.subscriptions[productId] = { expires_date: "2099", ... };
  obj.subscriber.entitlements[entitle] = { ... };
  ```

### 模式5: iTunes Store 收据伪造
- 场景: 拦截 buy.itunes.apple.com/verifyReceipt
- 根据 UA 返回不同 product_id
- 适用传统 iTunes 内购验证

### 模式6: UA 多应用匹配
- 场景: 一个脚本解锁多个同一 SDK 的 App
- 通过 UA 正则匹配不同 App，映射到不同 entitlements

### 模式7: url reject (最简单)
- 场景: 广告/统计域名完全不需要
- QX: `url reject`，Surge: `REJECT`

### 模式8: 混淆对抗 (jsjiami)
- Crazy-Z7 大量使用 (Busuu, Cycles, Dspt, zzmh)
- RC4 + Base64 + 数组移位三重混淆
- 核心逻辑不变，只是加壳

## 二、VIP/会员字段大全

从所有脚本中提取的响应字段关键词（去重后 ~70+ 个）:

```
基础VIP标记:
  is_vip, vip, vip_flag, vip_status, vip_level, vipType, 
  VIP, isPro, isPremium, isSubscribed, premium_status,
  premium, is_member, member, has_ad, ad_free

订阅/权限:
  entitlements, subscriptions, subscription, entitlement,
  product_id, product_identifier, membership, planTier, 
  planType, subscriptionProduct, subscriptionTier

到期时间:
  expire_time, expires_date, expired_at, expiry, end_time,
  vipEndDate, vipExpire, vip_expire_time, expire, expiration,
  vip_expire_time, expire_time_stamp, valid_until

用户角色:
  account_type, user_type, role, level, grade, access_level,
  privilege, vip_info, vipInfo, member_type, memberid

试用:
  is_trial, isTrial, trial_period, is_in_intro_offer,
  trial_end, isNewUser, is_activated

权益:
  wealth, total_buy, enable, enabled, is_unlimited,
  isUnlimited, max_devices, limit, quota

状态码型:
  status, vip_status, vipStatus, code, error_code, result
```

## 三、去广告模式

### 域名级
- QX: `[rewrite_local]` → `url reject`
- Surge: `REJECT`, `REJECT-TINY-GIF`, `REJECT-DROP`

### 响应体级
```js
// 正则去掉广告字段
.replace(/show_ad":true/g, 'show_ad":false')
.replace(/"ad":\[.*?\]/g, '"ad":[]')
.replace(/ad_enabled":\w+/g, 'ad_enabled":false')

// 直接删除广告区域
.replace(/<div class="ad-banner">[\s\S]*?<\/div>/g, '')
```

### 请求头级
```js
// 拦截请求，改 header
// 常用于去广告 SDK 初始化请求
```

## 四、签到脚本模式 (Boxjs分组，初步)

典型签到脚本结构:
```js
// 1. 获取 Cookie（从重写规则注入 Boxjs）
// 2. 定时任务执行签到
// 3. 通知结果
```

## 五、代理工具配置语法速查

### Quantumult X
```
[rewrite_local]
<匹配URL> url script-response-body <脚本URL>     // 改响应
<匹配URL> url script-request-header <脚本URL>   // 改请求头
<匹配URL> url reject                              // 拒绝请求

[mitm]
hostname = <域名>

[filter_local]
hostname = domain.com, reject                    // 域名拒绝
```

### Surge
```
[Script]
http-response <URL> requires-body=1,script-path=<URL>
http-request <URL> script-path=<URL>

[MITM]
hostname = *

[URL Rewrite]
^https?://(www.)?example.com/ad - reject
```

### Loon
```
[Script]
http-response <URL> script-path=<URL>, requires-body=true

[MITM]
hostname = *

[Rule]
DOMAIN, ad.example.com, REJECT
```
