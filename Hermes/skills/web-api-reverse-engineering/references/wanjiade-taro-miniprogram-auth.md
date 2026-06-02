# 万家乐会员俱乐部小程序认证逆向

逆向分析 Taro 框架微信小程序的认证体系——双层 sessionId + CSP Token 架构。

## 案例概况

- **AppID**: wx07b7a339bb2cf065
- **应用**: 万家乐会员俱乐部
- **域名**: `https://wakecloud.chinamacro.com`
- **租户**: tenantId=473, appBuId=2065
- **框架**: Taro (webpack 打包), DI 依赖注入架构
- **CSP 系统**: `https://csm.chinamacro.com/sf-cloud-yx/a_api`

## 解包后文件结构（Taro 框架特有）

与标准 wxapkg 不同，Taro 项目解包后文件结构：

```
wx07b7a339bb2cf065/
├── app.js          # 主入口 + 业务模块（webpack 打包，9000+ 行）
├── common.js       # 公共模块（23000+ 行，含认证核心）
├── vendors.js      # 第三方库
├── taro.js         # Taro 框架运行时
├── app.json        # 页面配置 + ext 租户信息
├── wxat-common/    # 主包页面
├── sub-packages/   # 子包（park/guide/mine/order/marketing/services/ugc/protocol）
├── uniSubpackage/  # uni-app 子包（售后/产品/社区）
└── images/
```

**关键差异**：
- 标准小程序用 `app-service.js` 单文件；Taro 拆分为 `app.js` + `common.js` + `vendors.js`
- 认证代码主要在 `common.js`（DI 容器 + LoginModel + LoginRepo）
- API 路由定义在 `common.js` 的 module 25（`t.a = { ... }` 对象）
- app.json 的 `ext` 字段包含租户配置（tenantId, appBuId, maAppName）

## 双层认证架构

### 第一层：sessionId（HTTP Cookie）

登录接口返回 `loginInfo.sessionId`，存储在 `wx.setStorageSync("cspLoginInfo")`。

每次请求通过拦截器注入 Cookie：
```javascript
// common.js:6132-6135
injectSession(request, loginModelInfo) {
  const sessionId = loginModelInfo?.loginInfo?.sessionId;
  const employeeSessionId = loginModelInfo?.employeeInfo?.sessionId;
  if (sessionId != null) {
    request.headers.cookie = "sessionId=" + sessionId;
  }
  if (employeeSessionId) {
    request.headers.cookie += ";appEmployeeSid=" + employeeSessionId;
  }
}
```

### 第二层：CSP Token

登录同时返回 `cspLoginInfo.token`，也存储在 `cspLoginInfo` 中。
用于 CSP 系统 API（如 `https://csm.chinamacro.com/sf-cloud-yx/a_api`）。

### Storage 结构

```javascript
wx.setStorageSync("cspLoginInfo", {
  ...cspLoginInfo,       // 原始 CSP 响应
  openId: loginInfo.openId,
  mobile: loginInfo.phone
});
```

提取各字段的方式（home/index.js 中的模式）：
```javascript
const cspLoginInfo = wx.getStorageSync("cspLoginInfo");
const token = cspLoginInfo.token;
const openId = cspLoginInfo.userInfo?.openId;
const mobile = cspLoginInfo.userInfo?.mobile;
const companyCode = cspLoginInfo.userInfo?.companyCode;
const profileId = cspLoginInfo.userInfo?.profileId;
```

## 登录流程

### 主登录流程（wx.login）

```
wx.login() → code
    ↓
POST /wd-member/member/login
Body: {
  code: "<wx.login code>",
  tenantId: 473,
  appBuId: 2065,
  wxAppId: "wx07b7a339bb2cf065",
  loginType: "<platform>",
  i3rdSystemCode: "CSP2.0"
}
    ↓
Response: {
  loginInfo: { sessionId, openId, unionId, phone },
  cspLoginInfo: { token, userInfo: { companyCode, mobile, openId, profileId } },
  memberInfo: { avatarImgUrl, nickname, ... },
  vip: true/false,
  score: 0
}
```

### 注册流程

```
POST /wd-member/app/register
Body: {
  loginType, authMobileCode, i3rdSystemCode: "CSP2.0",
  ...extraParams
}
```

快速注册使用 `authMobileCode`（微信手机号组件返回的 code）。

## DI 架构（Taro 依赖注入模式）

认证模块通过 DI 容器管理，关键标识：

| DI Token | 类 | 作用 |
|----------|-----|------|
| `DI.login.LoginModel` | LoginModel (y) | 登录状态管理、createSession、relogin |
| `DI.login.LoginRepo` | LoginRepo (b) | API 请求层（createSession、logout、register） |
| `DI.login.Implement` | Implement (x) | 平台实现（getCode、injectSession、recover） |
| `DI.login.RegisterModel` | RegisterModel (E) | 注册模型、验证码 |
| `DI.login.H5LoginCodeRepo` | h | getCode API 请求层（POST /wd-member/member/getCode） |
| `DI.login.H5LoginCodeModel` | w | getLoginCode 调用封装（从 LoginModel.info 提取 openId/unionId/phone） |
| `DI.login.PLATFORM` | Number | 平台标识 |
| `DI.login.UNAUTH_CODE` | 401 | 未授权错误码 |

**定位方法**：搜索 `DI.login.` 前缀可快速找到所有认证相关注入点。

## Token 续期机制

### ✅ 服务端 Code 生成接口（无需 wx.login 的续期路径）

发现关键接口 `/wd-member/member/getCode`，可由服务端生成登录 code，**完全绕过 wx.login()**：

```
H5LoginCodeRepo → POST /wd-member/member/getCode
参数: { openId, unionId, phone }
返回: { code }
```

**完整续期流程**：

```
Step 1: POST /wd-member/member/getCode
  Body: { openId, unionId, phone }
  → 返回 { code }

Step 2: POST /wd-member/member/login
  Body: {
    code: "<上一步的 code>",
    tenantId: 473,
    appBuId: 2065,
    wxAppId: "wx07b7a339bb2cf065",
    loginType: 1,
    i3rdSystemCode: "CSP2.0"
  }
  → 返回 { loginInfo: { sessionId, openId, unionId, phone }, cspLoginInfo: { token }, ... }

Step 3: Cookie: sessionId=xxx
```

**前置条件**：首次登录后保存 `openId`、`unionId`、`phone` 三个字段即可反复续期。

**DI 容器中的相关模块**：

| DI Token | 类 | 作用 |
|----------|-----|------|
| `DI.login.H5LoginCodeRepo` | h | getCode API 请求层 |
| `DI.login.H5LoginCodeModel` | w | getLoginCode 调用封装 |

**调用链**（common.js:6307-6326）：
```javascript
// H5LoginCodeModel.getLoginCode 从当前 LoginModel.info 中提取 openId/unionId/phone
const loginModel = getLoginModel();
const { openId, unionId } = loginModel.info?.loginInfo || {};
const { phone } = loginModel.info?.userInfo || {};
const code = await h5LoginCodeModel.getLoginCode({ openId, unionId, phone });
```

**设计意图**：H5 环境无法调 `wx.login()` 时的降级方案。小程序端也能用。

### 401 自动重登（被动续期）

```javascript
// common.js:6184-6220 — B 函数（请求拦截器中的认证重试）
async function handleAuthError(request, retryFn) {
  const loginModel = getLoginModel();
  const UNAUTH_CODE = getDI("DI.login.UNAUTH_CODE", 401);
  
  injectSession(request, loginModel.info);  // 注入当前 session
  const result = await retryFn();            // 执行请求
  
  if (!result.success && result.errorCode != null && result.errorCode === UNAUTH_CODE) {
    const reloginResult = await loginModel.relogin();  // 全量重登
    if (reloginResult) {
      injectSession(request, loginModel.info);  // 用新 session
      return await retryFn();                    // 重放原请求
    }
  }
  return result;
}
```

### relogin() 方法

```javascript
// common.js:5788-5828
async relogin(force) {
  if (this.relogining || this.loginStatus === Logining) {
    return await this.loginWaitQueue.push();
  }
  this.relogining = true;
  this.clearSession();           // 清除本地缓存
  return await this.createSession();  // 完整 wx.login → /wd-member/member/login
}
```

### 会话恢复（recover）

LoginModel.createSession 流程：
1. 先尝试 `implement.recover()` 恢复已有 session
2. 如果 recover 返回数据 → 直接使用（跳过 wx.login）
3. 如果 recover 返回 null → 走完整 wx.login + POST /wd-member/member/login

`recover` 的具体实现由各平台自行定义（小程序端 vs H5 端不同）。
**注意**：基础 Implement 类没有 recover 方法（optional chaining 调用），小程序端默认返回 undefined 走 wx.login。H5 端通过 `H5LoginCodeModel` + `/wd-member/member/getCode` 实现等效恢复。

## 全部 API 端点

API 域名构造函数：`https://wakecloud.chinamacro.com` + 路径

### 认证类
- `POST /wd-member/member/login` — 主登录（code→sessionId）
- `POST /wd-member/member/getCode` — **服务端生成 code（无需 wx.login，用 openId+unionId+phone 换取）**
- `POST /wd-member/app/register` — 注册
- `GET /wd-member/app/member/applet/logout` — 登出
- `POST /wd-app/app-manager/query` — 应用配置
- `POST /wd-member/app/agreement` — 用户协议
- `POST /wd-member/app/member/auth` — 更新用户信息
- `GET /wd-member/app/member/sendVCode` — 发送验证码
- `POST /wd-member/app/source/create` — 设置用户场景
- `POST /mtool/app/mini/link/record/create` — 访问记录
- `POST /login/login` — 旧版登录
- `POST /login_v2/login_v2` — V2 登录
- `POST /login_v3/login_v3` — V3 登录

### 用户信息
- `GET /auth/mp/userInfo/v1/getLoginUserInfo` — 登录用户信息
- `GET /auth/mp/userInfo/v1/getWxUserInfo` — 微信用户信息
- `GET /auth/mp/userInfo/v1/getSdkSignature` — SDK 签名
- `GET /auth/vip/user/user_detail` — 用户详情
- `POST /auth/vip/user/update_user` — 更新用户

### 会员/积分
- `GET /wd-member/app/member/score/statistic/` — 积分统计
- `GET /wd-member/app/member/page/score` — 积分记录

### 业务类（需 sessionId）
- 商品: `/wd/home/std/app/item/user/spu/page`, `/wd-item/app/item/spu/info/get`
- 订单: `/commerce/app/order/order`, `/commerce/app/order/query/list`
- 购物车: `/auth/vip/shopping_cart/add|queryList|remove|update`
- 优惠券: `/auth/coupon/ticket/plan/collect`, `/coupon/app/coupon/queryAvailableCoupons`
- 门店: `/auth/store/query_list`, `/auth/store/query_nearest`
- 服务信息: `/wd-item/app/user/config/serviceInfo`

### 特殊外部 API
- CSP 服务: `https://csm.chinamacro.com/sf-cloud-yx/a_api`（需 cspLoginInfo.token）
- 商城 API: `https://mall-api.chinamacro.com/openapi/goods/check_goods`（需 accessToken）

## 与唯品会小程序的架构对比

| 维度 | 唯品会 | 万家乐 |
|------|--------|--------|
| 框架 | 原生小程序 | Taro (webpack) |
| Token 名 | VIP_TANK / saturn | sessionId + cspLoginInfo.token |
| Token 传递 | Cookie (应用层管理) | Cookie header (拦截器注入) |
| 续期 | 无续期（重新登录） | getCode 服务端续期 + relogin 全量重登 |
| 备用登录 | 手机号短信 | 微信手机号快速验证 + H5 getCode（无需 wx.login） |
| DI 架构 | 无 | 有（DI.login.* 容器） |
| 租户系统 | 无 | 有（tenantId/appBuId） |

## 定位技巧（Taro 小程序专用）

1. **认证模块定位**：搜索 `DI.login.` 前缀，找到所有注入点
2. **API 端点定位**：搜索 `r("/` 模式（URL 构造函数的调用），通常在 common.js 的 module 25
3. **登录流程定位**：搜索 `createSession`、`waitLoginSuccess`、`relogin`
4. **Cookie 注入定位**：搜索 `headers.cookie` 或 `injectSession`
5. **401 处理定位**：搜索 `UNAUTH_CODE` 或 `errorCode === 401`
6. **CSP Token 定位**：搜索 `cspLoginInfo` 或 `getStorageSync("cspLoginInfo")`
7. **租户配置定位**：读 app.json 的 `ext` 字段
8. **appId 定位**：搜索 `wxAppId` 或读 app.json 的 `ext.maAppId`
9. **getCode 接口定位**：搜索 `getCode`、`H5LoginCodeRepo`、`LOGIN_GETCODE_API` 或 `/wd-member/member/getCode` — 这是无需 wx.login 的续期关键
10. **login_v2/v3 定位**：搜索 `login_v2`、`login_v3`、`loginV2`、`loginV3` — 存在多个版本的登录接口

## Pitfalls

1. **Taro 打包的 JS 是 webpack 格式** — 不是标准小程序 `app-service.js`，文件更大更分散，需要跨文件搜索
2. **common.js 可能 20000+ 行** — 用 `grep` 定位行号后用 `read_file(offset=N, limit=M)` 精读，不要全文读取
3. **DI 标识符是字符串字面量** — 如 `"DI.login.LoginModel"`，直接搜索字符串即可定位
4. **sessionId 过期无明确错误码** — 默认使用 401 作为未授权码，但可能被覆盖（`DI.login.UNAUTH_CODE`）
5. **CSP Token 和 sessionId 可能不同步过期** — 两层认证各自独立，一个过期不影响另一个
6. **recover() 实现可能在子包中** — 小程序端的 recover 实现可能不在 common.js 中，需要搜索其他文件
7. **tenantId/appBuId 是应用级配置** — 不同商家的小程序使用同一套后端框架但租户不同
8. **relogin 有次数限制** — `MAX_RELOGIN_COUNT = 1`，超过后直接报错不重试
9. **`implement.recover` 是 optional chaining 调用** — 基础 Implement 类（x）没有 recover 方法，`recover?.()` 返回 undefined 后走 wx.login 全流程。H5 环境通过 `H5LoginCodeModel` + `/wd-member/member/getCode` 实现等效的"无 code 续期"
10. **getCode 接口需要已有 session 信息** — `/wd-member/member/getCode` 的参数（openId/unionId/phone）来自首次登录结果。如果这三个字段也丢失了，必须重新走 wx.login
