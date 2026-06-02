# 微信小程序认证体系逆向

逆向微信小程序的登录认证流程——从 wxapkg 解包到 token 机制分析。

## 适用场景

- 分析小程序的 cookie/token 认证机制
- 寻找不依赖 wx.login code 的登录路径
- 理解 token 续期/刷新机制
- 提取 API 端点和请求格式

## 工作流

### Step 1: wxapkg 解包

小程序包通常从以下路径获取：
- iOS: `/var/mobile/Containers/Data/Application/{UUID}/Library/WechatPrivate/{appid}/`
- Android: `/data/data/com.tencent.mm/MicroMsg/{hash}/appbrand/pkg/`
- PC: `~/Library/Containers/com.tencent.xinWeChat/.../appbrand/pkg/`

解包工具：
```bash
# unveilr (推荐，自动解密+解包)
npx unveilr <input.wxapkg> -o <output_dir>

# wxappUnpacker (Node.js)
node wxWxapkg.js -i <input.wxapkg> -o <output_dir>
```

解包后目录结构：
```
__APP__/
├── app-service.js      # 主包业务代码（所有模块打包在一个文件）
├── app-wxss.js         # 样式
├── app-config.json     # 页面配置
├── pages/              # 页面目录
└── ...
```

子包（subpackage）是独立的 wxapkg 文件，解包后也有对应的 `.appservice.js`。

### Step 2: 定位认证模块

小程序的认证代码通常在以下模块中：

**搜索关键词优先级**：
1. `VIP_TANK` / `saturn` / `token` / `tokenId` — 特定应用的 token 名
2. `isLogin` / `checkLogin` / `loginStatus` — 登录状态判断
3. `wx.login` / `getLoginCode` / `loginToken` — 微信登录
4. `getPhoneNumber` / `phoneLogin` / `sendSms` — 手机号登录
5. `cookie` / `setCookie` / `getCookie` — cookie 管理
6. `auth` / `authorize` / `third_party` — 第三方认证

**搜索命令**：
```bash
# 在解包目录中搜索
grep -rn 'VIP_TANK\|tokenId\|tokenExpire' *.js
grep -rn 'weixinAutoLogin\|phoneLogin\|sendSms' *.js
grep -rn 'getWebviewEntranceTicket\|webTank' *.js
```

### Step 3: 分析登录流程

典型的微信小程序登录流程：

```
wx.login() → code
    ↓
wx.getUserInfo() → encryptedData + iv
    ↓
POST /auth/third_party/trylogin/v1
Body: {code, encryptedData, iv, hash, source, loginType, thirdType}
    ↓
Response: {tokenId, tokenExpire, userId}
    ↓
Storage: set("VIP_TANK", tokenId)
```

**关键点**：
- `code` 是微信登录凭证，有效期 5 分钟，只能用一次
- `encryptedData` 需要用户授权（wx.getUserInfo）
- `tokenId` 就是认证 token，后续请求通过 cookie 传递

### Step 4: 寻找替代登录路径

除了 wx.login code，小程序通常还有其他登录方式：

**手机号短信登录**：
```
POST /mlogin-api/...?act=sendSms     → 发送验证码
POST /mlogin-api/...?act=check       → 验证码登录 → 返回 tokenId
```
- 不需要 wx.login code
- 需要手机号 + 短信验证码

**密码登录**：
```
POST /mlogin-api/...?act=passwordLogin
Body: {account, password}
```

**一键登录（wx.getPhoneNumber）**：
- 通过微信手机号快速验证组件
- 底层仍需要 wx.login code，但用户无感

### Step 5: 分析 Token 续期机制

搜索 token 刷新相关代码：
```bash
grep -rn 'refresh\|renew\|expire\|ticket' *.js | grep -i 'token\|tank\|auth'
```

**常见续期模式**：
1. **主动续期** — 定时器在 token 过期前调用刷新接口
2. **被动续期** — 请求返回 401/过期错误时自动刷新
3. **无续期** — token 过期后重新登录（最常见于小程序）
4. **Ticket 换取** — 用已有 session 获取 ticket，再用 ticket 换新 token

**Webview Token 刷新**（小程序内嵌 H5 场景）：
```
POST /xcx/getWebviewEntranceTicket/V2
Body: {sessionId, refresh: 0|1}
Response: {ticket, webTank, webViewLoginExpiration}
```
- 前提：已有有效的主 token（saturn/VIP_TANK）
- 返回的 `webTank` 是 H5 专用 token

### Step 6: 提取 Cookie/Storage 结构

小程序的 cookie 管理通常在一个专门的模块中：

```javascript
// 典型的 cookie 列表
const cookieKeys = [
  "mars_cid",      // 设备 ID
  "userId",        // 用户 ID
  "saturn",        // 主登录 cookie
  "VIP_TANK",      // API 认证 token
  "wap_consumer",  // 用户类型
  "warehouse",     // 仓库/地区
  "address_id",    // 收货地址
  "H5_VIP_TANK"    // Webview 专用 token
];
```

**请求时自动附加 cookie**：
```javascript
getCookies(headerCookie) {
  // 从 storage 读取所有 cookie key
  // 与传入的 cookie 合并
  // 返回完整 cookie 字符串
}
```

## 案例：唯品会小程序 VIP_TANK 逆向

### 背景
- AppID: wxe9714e742209d35f
- 目标：找到不依赖 wx.login code 获取 VIP_TANK 的方法

### 发现的登录路径

| 路径 | 需要 code | 需要手机号 | API 端点 |
|------|-----------|-----------|---------|
| 微信自动登录 | ✅ | ❌ | `wxapi.appvipshop.com/auth/third_party/trylogin/v1` |
| 手机号短信登录 | ❌ | ✅ | `mlogin-api.vip.com/ajaxapi-weixin.html?act=sendSmsV3` |
| 密码登录 | ❌ | ✅ | `mlogin-api.vip.com/ajaxapi-weixin.html?act=...` |

### Token 结构
- `saturn` — 主登录 cookie
- `VIP_TANK` — API 认证 token（tokenId）
- `H5_VIP_TANK` — Webview 专用 token
- `tokenExpire` — 过期时间戳

### 续期机制
- 主 VIP_TANK：**无续期**，过期后重新登录
- H5_VIP_TANK：通过 `getWebviewEntranceTicket/V2` 刷新

### 关键发现
1. 所有获取 VIP_TANK 的方式都需要某种形式的身份验证
2. 唯一不依赖 wx.login code 的方式是手机号短信登录
3. H5_VIP_TANK 可以通过已有 session 刷新，但不能独立获取

## Pitfalls

1. **小程序 JS 是打包后的** — 所有模块打包在 `app-service.js` 一个文件中，变量名被压缩，需要从字符串常量和上下文推断功能
2. **子包是独立文件** — 登录模块可能在主包或子包（如 `_vipshop_login_.wxapkg`）中，需要都检查
3. **code 有效期 5 分钟** — wx.login 获取的 code 只能用一次，有效期 5 分钟，不能缓存复用
4. **storage API 不是标准 localStorage** — 小程序使用 `wx.setStorageSync`/`wx.getStorageSync`，不是浏览器的 localStorage
5. **cookie 管理是自实现的** — 小程序没有原生 cookie 机制，cookie 管理是应用层自己实现的（通常是一个 storage key 列表 + 请求拦截器拼接）
6. **mlogin-api 可能有风控** — 手机号登录接口通常有频率限制、图形验证码、设备指纹等风控措施
7. **不同小程序的 token 名称不同** — VIP_TANK 是唯品会的命名，其他小程序可能叫 `session_token`、`access_token`、`auth_token` 等
8. **wxapkg 解密密钥** — 某些版本的小程序包需要先解密再解包，密钥从微信客户端内存或配置文件中提取
