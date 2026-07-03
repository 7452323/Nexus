---
name: cross-platform-proxy-scripting
description: "跨平台代理脚本编写指南 (Quantumult X / Surge / Loon / Shadowrocket / Stash / Egern)。覆盖：BoxJS兼容层、cookie捕获、app解锁、广告拦截、重写规则、配置模板"
version: 2.0.0
tags: [quantumultx, surge, loon, shadowrocket, boxjs, rewrite, adblock, unlock]
---

# 跨平台代理脚本开发指南

## 一、BoxJS 跨平台兼容层

BoxJS (chavyleung/scripts) 提供了一个跨平台的 `Env` 类，运行在 QX/Loon/Surge/Stash/Egern/Shadowrocket/Node.js 之上。

### 1.1 环境检测

```javascript
const $ = new Env('任务名称')

// 获取当前环境
$.getEnv()           // -> 'Quantumult X' | 'Surge' | 'Loon' | 'Shadowrocket' | 'Node.js' | 'Egern' | 'Stash'
$.isNode()           // -> true/false
$.isQuanX()          // -> true/false
$.isSurge()          // -> true/false
$.isLoon()           // -> true/false
```

### 1.2 核心API

```javascript
// HTTP 请求（自动适配当前环境）
$.http.get({url, headers, timeout}, callback)
$.http.post({url, headers, body, timeout}, callback)

// 数据存储（持久化cookie/token）
$.getdata(key)       // 读取
$.setdata(val, key)  // 写入

// 通知
$.msg(title, subt, desc, url)

// 日志
$.log(msg)
$.logError(msg)

// 结束
$.done()
```

### 1.3 单脚本模板

```javascript
const $ = new Env('任务名称')

!(async () => {
  await init()
  await doTask()
  $.msg($.name, '完成', '详情')
})().catch(e => $.logError(e)).finally(() => $.done())

async function init() {
  $.cookie1 = $.getdata('cookie_key1')
  $.cookie2 = $.getdata('cookie_key2')
}
```

## 二、QX 重写规则体系

### 2.1 规则类型

| 类型 | 语法 | 用途 |
|------|------|------|
| 响应修改 | `url script-response-body path/to/script.js` | app解锁、去广告 |
| 请求修改 | `url script-request-body path/to/script.js` | cookie捕获 |
| 请求头修改 | `url script-request-header path/to/script.js` | 请求头捕获 |
| 拒绝 | `url reject` | 拦截请求 |
| 拒绝-200 | `url reject-200` | 返回空200 |
| 拒绝-Img | `url reject-img` | 拦截图片 |
| 拒绝-dict | `url reject-dict` | 拦截字典 |

### 2.2 App解锁模式

```
hostname = *.target_domain.com

^https?:\/\/target\.com\/api\/vip\/check url script-response-body https://raw.github.com/user/repo/main/unlock.js
```

### 2.3 广告拦截模式

```
# 拦截广告API
^https?:\/\/api\.app\.com\/ad\/ url reject

# 拦截SDK上报
^https?:\/\/sdk\.analytics\.com\/ url reject

# 拦截广告图片
^https?:\/\/track\.app\.com\/impression url reject-img
```

## 三、Cookie 捕获流程

```
┌──────────┐    ┌──────────────┐    ┌──────────┐
│  用户     │───→│  代理工具     │───→│  目标API  │
└──────────┘    └──────────────┘    └──────────┘
                      │
               script-request-body/header
                      │
                      ▼
                Cookie 持久化
               ($.setdata/cookie.js)
                      │
                      ▼
                BoxJS 本地存储
```

## 四、跨平台配置对照

| 功能 | QX | Surge | Loon |
|------|:--:|:-----:|:----:|
| 响应修改 | `url script-response-body` | `type=http-response` | `http-response` |
| 请求修改 | `url script-request-body` | `type=http-request` | `http-request` |
| 拒绝 | `url reject` | `type=reject` | `reject` |
| hostname | `hostname = xxx` | `[MITM] hostname = xxx` | `[MITM] hostname = xxx` |
| 任务定时 | `[task_local] 0 0 * * *` | `cron "0 0 * * *"` | `cron "0 0 * * *"` |

## 五、277 个常用解锁规则分布

| 来源 | 数量 | 特点 |
|------|:----:|------|
| ddgksf2013 | 最多 | 墨鱼去广告，质量高 |
| NobyDa | 多 | 签到/任务脚本 |
| KOP-XIAO | 多 | 资源解析器 |
| Tartarus2014 | 多 | Loon/QX规则 |
| yqc007 | 中 | 各种app解锁 |
| Marol62926 | 中 | 国际app |
| zqzess | 少 | 优质去广告 |
| Alex0510 | 少 | 工具类 |

## 六、调试技巧

```javascript
// 实时调试脚本
console.log('debug info')     // QX/Loon控制台可见

// 查看响应体
let body = JSON.parse($response.body)
console.log(JSON.stringify(body, null, 2))

// 替换响应
$done({ body: JSON.stringify(fakedResult) })
```


## 七、Protobuf 二进制响应解锁（高级）

部分 App 使用 Protobuf（如 Spotify）传输数据，不能直接改 JSON。需要用 protobuf.js 解码→修改→重新编码。

### 7.1 Protobuf 解锁模式

```javascript
// 1. 加载 protobuf 定义（schema）
const protoDef = {"nested": {
  "BootstrapResponse": {
    "fields": {
      "ucsResponseV0": {"type": "UcsResponseWrapperV0", "id": 2}
    }
  }
}};
const root = protobuf.Root.fromJSON(protoDef);

// 2. 解码二进制body
const binaryBody = new Uint8Array($response.bodyBytes);
const decoded = root.lookupType("ResponseType").decode(binaryBody);

// 3. 修改字段（如Spotify Premium解锁）
decoded.accountAttributes['type'] = {stringValue: 'premium'};
decoded.accountAttributes['ads'] = {boolValue: false};
decoded.accountAttributes['on-demand'] = {boolValue: true};
decoded.accountAttributes['high-bitrate'] = {boolValue: true};

// 4. 重新编码
body = root.lookupType("ResponseType").encode(decoded).finish();

// 5. 返回
$done({bodyBytes: body.buffer});
```

### 7.2 Spotify Premium 解锁（protobuf）

关键属性修改（摘自 app2smile/rules）：
| 属性 | 值 | 效果 |
|------|:---:|------|
| ads | false | 去广告 |
| type | "premium" | 变Premium |
| on-demand | true | 点播 |
| high-bitrate | true | 高音质 |
| unrestricted | true | 无限制 |
| catalogue | "premium" | 目录权限 |
| offline | true | 离线下载 |

## 八、RevenueCat 服务端订阅解锁

伪装成其他已订阅用户的回包：

```ini
# QX
^https:\/\/api\.revenuecat\.com url script-response-body https://raw.github.com/xxx/unlock.js

# Loon plugin
[URL Rewrite]
^https:\/\/(api\.revenuecat\.com|api\.rc-backup\.com)\/.+
\/(receipts$$|subscribers\/[^/]+$$) https://rc-backup.workers.dev header

# 常用代理服务
- rc-backup.lovebabyforever.workers.dev
- reven.lovebabyforever.workers.dev
```

## 九、app2smile 多平台模块架构

每个 App 都有多平台模块文件：
```
AppName/
├── AppName.sgmodule    # Surge
├── AppName.conf        # Quantumult X
├── AppName.stoverride  # Stash
├── AppName.module      # Shadowrocket
└── AppName.js          # 核心脚本（通用）
```

## 十、SukkaW/Surge 自动构建管线

使用 TypeScript 构建 Surge 规则集，自动从数据源生成：
```
Build/
├── index.ts            # 入口
├── build-common.ts     # 通用规则
├── build-reject-ips.ts # 拒绝IP
├── build-apple-cdn.ts  # Apple CDN
├── build-chn-cidr.ts   # 国内IP
└── build-stream.ts     # 流媒体
```

## 十一、AdBlock 综合拦截模式

从 Moli-X/Resources 等提取的模式：

```
hostname = *.ad-server.com, *.analytics.com, *.tracking.com

# 模式1: 直接reject
^https?://api.app.com/v1/ad/ url reject

# 模式2: 返回空200
^https?://api.app.com/v1/ad/ url reject-200

# 模式3: JSON过滤
let obj = JSON.parse($response.body);
obj.data = obj.data.filter(item => item.type !== "ad");
$done({body: JSON.stringify(obj)});

# 模式4: 删除字段
delete obj.data.ad;
delete obj.data.banner;
$done({body: JSON.stringify(obj)});

# 模式5: Protobuf修改
$done({bodyBytes: modifiedBuffer});
```


## 十二、GKD UI自动化去广告（App内弹窗/开屏）

GKD（搞快点）是新一代 UI 自动化去广告工具，通过选择器匹配 App 内的 UI 元素并自动点击跳过。

### 12.1 GKD 规则语法

```json5
{
  id: 'com.example.app',       // 应用包名
  name: '示例App',              // 应用名
  groups: [{
    key: 0,
    name: '开屏广告',              // 规则组名
    desc: '跳过开屏广告',
    order: -10,                   // 优先级
    matchTime: 10000,             // 匹配超时(ms)
    actionMaximum: 1,             // 最大执行次数
    resetMatch: 'app',            // 重置时机
    rules: [{
      matches: '[text*="跳过"]',   // 选择器
      action: 'clickCenter'        // 点击中心
    }]
  }]
}
```

### 12.2 选择器语法

| 表达式 | 含义 | 示例 |
|--------|------|------|
| `[text*="跳过"]` | text包含 | 匹配含"跳过"的文本 |
| `[text^="跳过"]` | text开头 | 匹配"跳过"开头 |
| `[text$="跳过"]` | text结尾 | 匹配"跳过"结尾 |
| `[text="跳过"]` | 精确匹配 | 完全匹配 |
| `[text~=".*skip.*"]` | 正则 | 正则匹配 |
| `@View[clickable=true]` | 锚点`@` | 点击目标 |
| `<n` | 父级选择器 | 第n层父节点 |
| `+n` | 兄弟选择器 | 第n个兄弟节点 |
| `[visibleToUser=true]` | 可见性 | 用户可见 |

### 12.3 经典规则模式

```javascript
// 开屏广告 - text包含"跳过"
[text*="跳过"][text.length<10][visibleToUser=true]

// 字节SDK广告 - 小叉号点击
@View[clickable=true][childCount=0][visibleToUser=true][width<200&&height<200]

// 更新提示
[text*="更新"][text.length<10]
// or
@LinearLayout > [text*="取消"][clickable=true]

// 青少年模式
[text*="青少年模式"] <<n Button[text="我知道了"]

// 弹窗广告关闭
ImageView[clickable=true][childCount=0] <(1,2) FrameLayout[childCount>2]
```

## 十三、自动签到/看广告脚本框架

### 13.1 多平台签到架构

```
签到脚本（Python/JS）
├── 登录模块    → 账号密码 / Cookie / Token
├── 签到模块    → 发送请求 / 点击按钮
├── 通知模块    → 企业微信 / 钉钉 / PushPlus / Telegram
├── 代理模块    → 可选HTTP代理
└── 配置文件    → config.json / .env
```

### 13.2 通用签到脚本模板

```python
#!/usr/bin/env python3
import json, requests, time

class AutoSign:
    def __init__(self, config_path='config.json'):
        with open(config_path) as f:
            self.config = json.load(f)
        self.session = requests.Session()
    
    def login(self):
        # 登录获取token
        resp = self.session.post(self.config['login_url'], json={
            'username': self.config['username'],
            'password': self.config['password']
        })
        self.token = resp.json().get('token')
        self.session.headers['Authorization'] = f'Bearer {self.token}'
    
    def sign_in(self):
        # 执行签到
        resp = self.session.post(self.config['sign_url'])
        return resp.json()
    
    def check_in(self):
        # 查询签到状态
        resp = self.session.get(self.config['check_url'])
        data = resp.json()
        return data.get('signed', False), data.get('days', 0)
    
    def notify(self, msg):
        # 通知推送
        url = f"https://pushplus.plus/send"
        requests.post(url, json={
            'token': self.config['push_token'],
            'title': '签到结果',
            'content': msg
        })

if __name__ == '__main__':
    sign = AutoSign()
    sign.login()
    result = sign.sign_in()
    sign.notify(str(result))
```

## 十四、TG自动签到/社区脚本

```typescript
// linuxdo-scripts 扩展模式 (Vue + TypeScript)
// 浏览器扩展自动签到
export default defineUnlistedScript(() => {
  // 监听页面加载
  document.addEventListener('DOMContentLoaded', async () => {
    // 查找签到按钮
    const signBtn = document.querySelector('.checkin-btn');
    if (signBtn) {
      // 自动点击签到
      signBtn.click();
      // 记录结果
      await chrome.storage.local.set({ 
        lastCheckin: Date.now() 
      });
    }
  });
});
```

## 十五、多平台消息推送

| 平台 | URL | 方式 |
|------|-----|------|
| 企业微信 | `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=KEY` | Webhook |
| 钉钉 | `https://oapi.dingtalk.com/robot/send?access_token=TOKEN` | Webhook |
| PushPlus | `https://www.pushplus.plus/send` | HTTP |
| Telegram | `https://api.telegram.org/botTOKEN/sendMessage` | Bot API |
| Server酱 | `https://sctapi.ftqq.com/SENDKEY.send` | HTTP |
