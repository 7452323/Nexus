# HAR 分析 → 去广告/爆破会员 知识库 v3

> 基于对 55+ 仓库的深度学习，涵盖 QuantumX/Surge/Loon/Boxjs/广告分组

## 一、VIP/会员爆破模式大全

### 模式1: JSON完全替换 (WPS/MIX/CamScanner/百度网盘)
```js
$done({ body: JSON.stringify({ ... 完整硬编码的VIP数据 ... }) })
```
**适用**: 响应结构简单、完全可控。**不**适用于需要保留用户信息的场景。

### 模式2: JSON字段修改 (酷我/网易蜗牛/指尖时光)
```js
var obj = JSON.parse($response.body);
obj.data.vipExpire = "2099-01-01";
obj.data.isVip = true;
obj.vipFlag = 1;
$done({body: JSON.stringify(obj)});
```
**适用**: 最常见，80%的爆破用这个。

### 模式3: 正则替换 (NiChi/追追漫画/Busuu)
```js
var body = $response.body
  .replace(/isfree":\d/g, 'isfree":1')
  .replace(/vip_status":\d/g, 'vip_status":1')
  .replace(/show_ad":\w+/g, 'show_ad":false')
  .replace(/preview/g, "free")
  .replace(/true/g, "false");  // NiChi的巧妙反转
$done({body});
```
**新发现**: NiChi 四连 replace——把 preview→free, view→unlimited, true→false。

### 模式4: RevenueCat通用解锁 (最重要)
```js
// 拦截 api.revenuecat.com/v1/subscribers/
// request-header: 删除 x-revenuecat-etag 防304
// response-body: 
obj.subscriber.subscriptions[productId] = { expires_date: "2099", ownership_type: "PURCHASED" };
obj.subscriber.entitlements[name] = { product_identifier: productId, ... };
```
**一个脚本撬30+ App** (Guding88 APPheji_Revenuecat.js)。核心: 删etag + UA匹配App → 对应productId/entitlement。

### 模式5: UA多应用匹配
```js
var UA = $request.headers['user-agent'];
const UAMappings = {
  'APTV': { name: 'pro', id: 'com.kimen.aptvpro.lifetime' },
  'PhotoRoom': { name: 'business', id: 'com.background.business.yearly' },
  // ... 30+ apps
};
```
**同样的代码结构，切换productId = 解锁不同App**。

### 模式6: iTunes收据伪造
```
拦截: buy.itunes.apple.com/verifyReceipt
伪造: purchase_date, product_id, expires_date
```

### 模式7: url reject (去广告最简单)
```
QX: ^https?://ad\.domain\.com url reject
Surge: DOMAIN, ad.domain.com, REJECT
Loon: DOMAIN, ad.domain.com, REJECT
```

### 模式8: jsjiami混淆对抗 (Crazy-Z7)
三重混淆: Base64 → RC4解密 → 数组移位。核心逻辑不变，只是加壳。

### 模式9: **Loon插件格式** (新发现)
```
# QX style:
^url$ url script-response-body script.js

# Loon Rewrite (更多能力):
^url$ response-body-json-del data.adField   # 删除JSON字段
^url$ response-body-json-jq '.data.modules |= map(select(...))'  # jq表达式
^url$ response-body-json-replace data {}    # 替换JSON子树
^url$ reject-dict                           # 拒绝特定请求
^url$ 307 NEW_URL                           # 307重定向
```

### 模式10: Mock/Noop模式 (SukkaW Surge)
```js
// 替换追踪/广告库为空函数
window.OBR = { extern: { ...noopfn... } };
window.google_tag_manager = { ... };
```
**不是拦截请求，而是替换页面中的JS库为空壳**。

### 模式11: 域名重定向绕过地区限制 (fmz200 TikTok)
```
(?<=_region=)CN(?=&) url 307 MO           # 正则替换地区码
^(https?://tnc...)(.+)(\?)(.+) url 302 $1$3  # 剥掉查询参数
```

### 模式12: 快速系列爆破 (gxggxl 迅捷6款)
一个脚本 `vip = [{id:1, auth_type:1, auth_value:巨长数字}]` 解锁迅捷6款App。

## 二、VIP字段大全 (70+关键词，从55+仓库提取)

### 布尔/标记型
`is_vip`, `vip`, `vipFlag`, `vip_flag`, `vipStatus`, `vip_status`, `isVip`,
`isPro`, `isPremium`, `is_premium`, `isSubscribed`, `is_subscribed`,
`is_member`, `has_ad`, `ad_free`, `is_unlimited`, `isUnlimited`,
`is_super`, `isYearUser`, `isVIPMAutoPay`, `isVIPLuxAutoPay`,
`isTrial`, `is_trial`, `is_in_intro_offer_period`, `isNewUser`,
`is_activated`, `is_xy_vip`, `is_xy_auto_renewal`

### 状态/类型值
`vip_status`, `vipStatus`, `vipType`, `vip_level`, `vipLevel`,
`premium_status`, `premiumStatus`, `status`, `account_type`,
`user_type`, `role`, `grade`, `level`, `access_level`,
`subscription_status`, `vip_info`, `vipInfo`, `member_type`,
`memberid`, `product_id`, `product_identifier`

### 到期时间
`expire_time`, `expires_date`, `expired_at`, `expiry`, `end_time`,
`vipEndDate`, `vipExpire`, `vip_expire_time`, `expiration`,
`valid_until`, `expire_date`, `expire_time_stamp`,
`membership_expiry_date`, `membership_expire`,
`vipLuxuryExpire`, `vipOverSeasExpire`, `vipmExpire`, `vip3Expire`,
`vipendtime`, `vipstartTime`, `xy_vip_expire`, `tradeEndTime`

### 订阅/权益
`entitlements`, `subscriptions`, `subscription`, `entitlement`,
`planTier`, `planType`, `subscriptionProduct`, `subscriptionTier`,
`planId`, `isYearUser`, `ownership_type`, `store`,
`active_subscriptions_ids`, `active_bundle_subscriptions`,
`non_consumables_ids`, `subscription_purchases_state`,
`subscription_purchases`, `has_valid_purchases`

### 特权/权限
`privilege`, `privileges`, `enabled`, `enable`, `features`,
`auth_type`, `auth_value`, `unlock`, `data_recover`, `ocr`,
`pdf2doc`, `pdf_merge`, `pdf_sign`, `pdf_split`,
`wealth`, `total_buy`, `total_cost`, `limit`, `quota`, `max_devices`

### 破解通用值
```js
expire_time: 1846256142        // 2028年
expires_date: "2099-01-01T00:00:00Z"
ownership_type: "PURCHASED"
store: "app_store"
status: 1 / "ACTIVE"
vipFlag: true
level: 99
is_xy_vip: true
```

## 三、去广告模式大全

### A. 域名级拦截
```
QX:    hostname = ad.com, reject
Surge: DOMAIN, ad.com, REJECT
Loon:  DOMAIN, ad.com, REJECT
  AWAvenue: 903条域名规则 (2026-07-27更新)
  app2smile: 贴吧/知乎/B站 专项
  fmz200: 4104个文件的全能规则集
```

### B. 响应体JSON字段删除 (Loon独有)
```
response-body-json-del data.adTimeoutReport data.adSupplementSwitch
response-body-json-jq '.data.bottomBarControl.tabs |= map(select(.tabType | . == "home" or . == "schedule"))'
response-body-json-replace data {}
reject-dict
```

### C. 正则替换去广告
```js
.replace(/show_ad":true/g, 'show_ad":false')
.replace(/"ad":\[.*?\]/g, '"ad":[]')
```

### D. Content Farm屏蔽 (limbopro)
7179个内容农场域名，支持油猴/QX/Surge/AdGuard多平台。

### E. Mock/Noop
替换页面中的追踪/广告JS库为空函数。

## 四、签到脚本模式 (Boxjs分组)

### Env.js 框架 (chavyleung)
多平台适配层: Surge/Loon/Stash/Shadowrocket/QX/Node.js
- `$task.fetch()` / `$httpClient.get()` 自动选择
- `$persistentStore` / `$prefs` 自动选择
- Cookie捕获: `script-request-header` → `$.setdata()`
- 定时任务: `cron "17 7 * * 1"` → `$.getdata()` → HTTP签到 → `$.msg()`

### Sliverkiss通用签到模板
```js
const $ = new Env(moduleName);
// 优先级: 脚本内参数 > 外部传入
$.userCookie = $.getjson(ckName) || [];
for (let item of $.userCookie) {
  let res = await fetch(item);  // 重放原始请求
  $.notifyMsg.push(`[${index}]: ${res}`);
}
```

### 签到脚本关键要素
1. Cookie获取: 通过 `http-request` 拦截 + `$request.headers`
2. 持久化: `$.setdata(token, "KEY_NAME")`
3. 签到执行: cron定时 + HTTP POST/GET
4. 通知: `$.msg("签到成功", "", "获得10积分")`
5. 多账号: `$.getjson()` 数组遍历

## 五、代理工具配置语法速查

| 功能 | QX | Surge | Loon |
|------|-----|-------|------|
| 改响应体 | `url script-response-body` | `http-response script-path=` | `http-response script-path=` |
| 改请求头 | `url script-request-header` | `http-request script-path=` | `http-request script-path=` |
| 拒绝请求 | `url reject` | `REJECT` | `REJECT` |
| JSON字段删 | `script-response-body ← JS` | `script-response-body ← JS` | `response-body-json-del` |
| jq表达式 | ❌ | ❌ | `response-body-json-jq '...'` |
| 307重定向 | `url 307 NEWURL` | ❌ | `url 307 NEWURL` |
| MITM | `[mitm] hostname = ` | `[MITM] hostname = ` | `[MITM] hostname = ` |
| Cookie持久 | `$prefs.setValueForKey` | `$persistentStore.write` | `$persistentStore.write` |
| 计划任务 | `[task_local]` | `cron` | `cron` |
| 去广告域名 | `hostname, reject` | `DOMAIN, h, REJECT` | `DOMAIN, h, REJECT` |

## 六、已深读仓库清单

### QX/Surge/Loon (30/46)
NobyDa/Script, Guding88/Script, Crazy-Z7/Script, Orz-3/QuantumultX, ddgksf2013, blackmatrix7/ios_rule_script, Hackl0us/SS-Rule-Snippet, Hackl0us/GeoIP2-CN, I-am-R-E/Functional-Store-Hub, chxm1023/Advertising, gjwj666/qx, xiaomaoJT/QxScript, shengetui/qx, fyjsy/KOP-XIAO, Orz-3/mini, limbopro/Adblock4limbo, thebestkyle323/Quantumult-x, QingRex/LoonKissSurge, LOWERTOP/Shadowrocket-First, Moli-X/Tool, axcsz/Collect, mist-whisper/Surge, Rabbit-Spec/Surge, SukkaW/Surge, Yarmukhamedov/mitm, deezertidal/deezertidal, fmz200/wool_scripts, sve1r/Rules-For-Quantumult-X, wuai19/rewrite, Yu9191/Yu9191

### 广告✌ (8/8)
AWAvenue-Ads-Rule, app2smile/rules, BlueSodaYY/quantummult, Barre/privaxy, ddgksf2013/AppScheme, lingeringsound/10007_auto, fmz200/wool_scripts

### Boxjs (28/97)
chavyleung/scripts, VirgilClyne/GetSomeFries, DualSubs/YouTube, DualSubs/Universal, BiliUniverse, zqzess, JDWXX/ql_all, Crazy-Z7/Task, srcrs/MagicBox, whyour/qinglong, gxggxl/Scripts, MCdasheng/QuantumultX, LambdaExpression, Yuheng0101/X, mrabit, ChinaUnicom, xzxxn777/Surge, yang7758258, FlechazoPh, zjk2017, sudojia/AutoTaskScript, qd-today/qd, hex-ci/smzdm_script, shidahuilang, yml2213, limoruirui/misaka, Sliverkiss/QuantumultX, JaxsonWang

## 七、破解脚本模板速查

### 最小VIP爆破（JSON字段修改）
```js
var obj = JSON.parse($response.body);
obj.data.vipExpire = "2099-01-01";
obj.data.isVip = true;
$done({body: JSON.stringify(obj)});
```

### RevenueCat通用模板
```js
const obj = JSON.parse($response.body);
if (obj?.subscriber) {
  obj.subscriber.subscriptions["PRODUCT_ID"] = {
    expires_date: "2099-01-01T00:00:00Z",
    ownership_type: "PURCHASED", store: "app_store"
  };
  obj.subscriber.entitlements["ENTITLEMENT"] = {
    product_identifier: "PRODUCT_ID",
    expires_date: "2099-01-01T00:00:00Z"
  };
}
$done({body: JSON.stringify(obj)});
```

### Loon去广告 (json-del + jq)
```
^https://api.app.com/config$ response-body-json-del data.ads data.tracking
^https://api.app.com/feed$ response-body-json-jq '.data.modules |= map(select(.type != "ad"))'
```

### 签到脚本模板
```js
const $ = new Env('App签到');
const cookie = $.getdata('COOKIE_KEY');
if (typeof $request !== 'undefined') {
  // Cookie捕获模式
  $.setdata($request.headers['token'], 'COOKIE_KEY');
  $.done();
} else {
  // 签到执行模式
  $.get({url: 'https://api.app.com/sign', headers: {Cookie: cookie}}, 
    (err, resp, data) => {
      $.msg('签到结果', '', data);
      $.done();
    });
}
```
