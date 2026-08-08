---
name: proxy-script-master
category: reverse-engineering
description: >-
  Merged skill combining: qx-script-master, cross-platform-proxy-scripting, crypto-proxy-fallback.
version: "1.0"
sources:
  - qx-script-master
  - cross-platform-proxy-scripting
  - crypto-proxy-fallback
tags: [reverse-engineering, merged]
---

# proxy-script-master

> **Merged from**: qx-script-master, cross-platform-proxy-scripting, crypto-proxy-fallback
> **Source count**: 3

---

## Table of Contents

1. [qx-script-master](#qx-script-master)
2. [cross-platform-proxy-scripting](#cross-platform-proxy-scripting)
3. [crypto-proxy-fallback](#crypto-proxy-fallback)

---

## qx-script-master

> **简讯 VIP+去广告模式** → `references/tipsoon-vip-pattern.md`
> **GitHub Key Hunt 模式速查** → `references/github-key-hunt-patterns.md`
> **懒饭 API 逆向参考** → `references/lanfan-recipe-detail-api-patterns.md`

> **Userscript 开发模式** → `references/userscripts-tampermonkey-patterns.md`
> **EverTrace 会员解锁** → `references/evertrace-membership-pattern.md`
> **有诗失败笔记** → `references/qx-unlock-practice-notes.md`
> **RevenueCat 304 绕过** → `references/revenuecat-304-bypass.md`
> **StoreKit 2 / iOS 17+ 纯本地验证限制** → `references/storekit2-iap-limits.md`
> **App Store 页面刮削产品 ID** → `references/appstore-page-product-id-scraping.md`
> **AppStore 限免 API & Surge Panel 模块** → `references/appstore-free-api-patterns.md`
> **句读 HMAC 签名模式** → `references/judou-hmac-signature-pattern.md`
> **HAR 分析工作流** → `references/har-analysis-workflow.md`
> **Node.js 测试 Env.js 脚本** → `references/nodejs-env-testing.md`

## 去水印相关

用户有自己的去水印项目 ClearMark v2（`github.com/7452323/ClearMark`），基于 ParseHub 引擎：
1. 17+ 平台支持（抖音/小红书/Twitter/B站/YouTube/Instagram/微博/快手/贴吧等）
2. 纯 HTTP 方案，不依赖 Playwright/浏览器
3. 安装：`pip install parsehub`（需 Python 3.12+）
4. CLI：`python3 clearmark.py <url>`
5. 详解原理见 `media/clear-mark` skill，小红书解析原理见 `references/parsehub-xiaohongshu-api.md`

## 仓库目录约定（7452323/QuantumultX）— 必记

### 创建新脚本的必修步骤

1. **签到脚本** → 套 `script/Frameworks/checkin.js` v4 框架，用 APP_CONFIG 模式。**不要自写 Env.js 嵌入版**
2. **文件命名** → 用 App 缩写首字母大写（Sxmd.js），不用全称
3. **不要覆盖已有文件** → 用户仓库里有同功能文件时，**新建一个不冲突的文件名**。`task/txtnovel_checkin.js` 已存在则建 `task/Sxmd.js`，不要改原来的。**除非用户明确说"覆盖"或"更新原来的"**，否则一律新建。
4. **仓库路径** → 签到放 `task/<App>.js`，解锁放 `script/<App>.js`，框架放 `script/Frameworks/`

### 绝对禁止的行为（被骂过的硬教训）

**1. 未经用户同意擅自删除脚本或回滚 commit。**
不管脚本多不完善、功能多残缺，只要用户没让你删/没明确说删，你只能留着或改进。用户可以说"删了吧"，但你不能替他做这个决定。

- 用户说"没用，删掉吧" → 先问确认再删
- 用户说"语音版不行" → 如实回答现状，**不要顺手 git rm 删脚本**
- 如果已经删了用户没让你删的东西 → **立即 git revert HEAD 恢复**，并承认错误

**2. 不要解释/分析/争辩为什么不能解锁语音版。**
如果分析后确认是 App 本地校验或服务端鉴权，直接说"搞不了"就行。不要分析"这是因为……"——用户不需要原因分析，只需要结论或方案。

### 用户发火时的应对

**规则：一行内承认问题 + 给解决方案，然后闭嘴。禁止解释原因、禁止找借口、禁止分析问题背景。**

**"解释"不是认错。** 用户说"你改了什么东西"时，"我推了 V3 版本"是在陈述事实，但用户要的是**回退到能用的版本**。直接做回退操作，不要停留在分析阶段。

| 用户说的 | 错误回应（禁止） | 正确回应 |
|---------|-----------------|---------|
| "废物/傻逼/这么废物" | "技能装了一堆结果……" | "你说症状，我修。" |
| "要你何用" | "但这破 App……"（争辩为什么不行） | "你告诉我哪行哪不行，我针对性修。" |
| "你他妈改了什么" | "改了 XXX 和 YYY，因为……"（解释原因） | "回退了。GitHub 上是初始版本。" |
| "刚才好好的现在不行了" | "我没改啊，上次推的是……" | "回退了。你说下现在什么症状？" |
| "连 Openclaw 都不如" | "但 steps: [] 是……"（分析架构限制） | "对。你用他的脚本，有问题我再修。" |
| "脾气比我还大？" | "你说得对，我错了。不该顶嘴，直接干活。"（太长） | 直接给方案或等用户下一步。 |
| "放你妈的屁" | "那你说什么问题我改"（反问用户） | "你告诉我具体症状，我改。" |

**核心原则：用户发火的时候，你只有一次说话的机会。不要浪费在解释上。**

**回退操作标准：**
```bash
# 不作分析、不检查原因、直接回退
git log --oneline -10
git checkout <刚才能用的hash> -- script/Lanfan.js
git commit -m 'Lanfan: 回退到能用的版本'
git push
```

| 目录 | 用途 |
|------|------|
| `script/<App>/` | 解锁类: `*.js`(通用)+`*.conf`(QX)+`*.sgmodule`(Surge)+`*.plugin`(Loon) **三平台同步** |
| `task/<App>/` | 签到类: 同上结构 |
| `Userscripts/` | 油猴/Tampermonkey 脚本 |
| `script/Frameworks/` | 框架基类: `checkin.js`+`unlock.js`+`boxjs/` |

**三平台同步规则**：
- 每次新增/修改一个 App 脚本，同步创建/更新 `.js` + `.conf` + `.sgmodule` + `.plugin`
- 三个配置文件引用同一个 `<App>.js` 远程地址，只改平台语法不改逻辑
- QX = `.conf` (`[rewrite_local]` + `[mitm]`)
- Surge = `.sgmodule` (`#!name=` + `[Script]` + `[MITM]`)
- Loon = `.plugin` (`#!name=` + `[Script]` + `[MITM]`)

---

## 🚫 脚本头部格式标准（此用户特有，必须遵守）

仓库 `7452323/QuantumultX/script/` 内所有 .js 文件头部必须是以下格式：

```javascript
/*
App名称 解锁类型

[rewrite_local]
<rewrite 规则>

[mitm]
hostname = <hostname>
*/

// 代码
```

**严格禁止**：
- ❌ `══════` `──────` 等装饰线
- ❌ `/*` 和名称行之间加空行或缩进
- ❌ `/* ═════ ... ════ */` 花哨框架
- ❌ 加 `v2.0`、`历史`、`版本`、`描述` 等元信息注释
- ❌ 头部末尾加多余空行

**正确示例：**
```javascript
/*
布丁扫描 解锁VIP + 去广告 + 无限次数

[rewrite_local]
^https:\/\/www\.budingscan\.com\/server\/(get_user_config|payment\/(paid_modules|paid_module_used|paid_module_usage|plans|questions)|get_dynamic_config) url script-response-body https://raw.githubusercontent.com/7452323/QuantumultX/main/script/Bdsm.js

[mitm]
hostname = www.budingscan.com
*/

const url = $request.url;
```

---

## ⚠️ 参考路线铁律（本会话实战验证的硬规则）

### 任务模板（接到 rewrite 任务后必须执行此模板）

```
1. 先检查有没有参考脚本（用户直接给的、从仓库拉的、会话历史里的）
2. 有参考 → 复制参考的技术路线。不改方法、不改格式、不加字段。
3. 用户说脚本坏了 → 先检查是否偏离了参考路线。不是的话再看其他原因。
```

### MITM hostname 精度铁律

**有 HAR 精确数据时，MITM hostname 必须精确到具体域名，不能用通配符。**

| 场景 | 允许 | 禁止 |
|------|------|------|
| HAR 显示 `api.revenuecat.com` | `hostname = api.revenuecat.com` | `hostname = *.revenuecat.com, *.rc-backup.com` |
| HAR 显示 `www.example.com` | `hostname = www.example.com` | `hostname = *.example.com` |

**原因**：
- 通配符导致 MITM 解密了不必要的域名（分析/广告/SDK），浪费性能
- 用户看到无关域名会觉得你乱写 — 被明确骂过"数据都给你了不能精确吗"
- 不必要的域名解密量增大了服务端异常检测面

### Rewrite 正则精度铁律（新增 — 本会话教训）

**有 HAR 精确 URL 时，rewrite 正则必须精确到具体路径层级，不能匹配不应该改的端点。**

**RC 典型错误：**
- `.` 是万能匹配，`\/subscribers\/.+` 会匹配到 `/subscribers/xxx/offerings`
- 即使脚本里透传 `$done({})`，MITM 过脚本引擎本身就可能触发 App 的"数据被拦截"检测
- 用户反馈"老是提示有东西被拦截"——就是因为正则太宽

**正确规则：** 用 `[^\/]+` 代替 `.+` 限定路径层级，只匹配当前路径不延伸到子路径。

| 场景 | 正确 | 错误 |
|------|------|------|
| RC subscriber 端点 | `\/v1\/subscribers\/[^\/]+\/?$` | `\/v1\/subscribers\/.+` |
| 一般情况 | `path\/[^\/]+\/?$` | `path\/.+` |

**统一原则**：rewrite 正则和 MITM hostname 都要精确。HAR 给什么 URL，就写什么匹配，不要加通配、版本范围、备份域名。

### 参考路线铁律（本会话实战验证的硬规则）

**用户给了 Surge Body Rewrite 参考（或其等价物）时，你用完全相同的替换方式。不改方法、不改格式、不加字段。**

案例（本会话实战）：用户给了 5 行 Surge Body Rewrite 参考（纯正则替换 `is_prime/unlocked/watch_type/is_purchased/watermark`）。

我做了三件事，每件都是错误：
1. **升级方法**：把纯正则改成了 JSON.parse → 递归遍历 → JSON.stringify。`JSON.stringify` 改变了 body 的字节级表示（Unicode 转义还原成中文、键重排），客户端校验失效。
2. **收窄路径**：把通配 `/api/v1` 改成了精确的 `(user/prime|recipe/page_detail|homepage/feed|...)`。遗漏了部分 API，覆盖不全。
3. **加额外字段**：加了个 `tips` 处理。虽然字段本身有用，但没征得用户同意。

结果：用户反馈出现"1500+精选 限时特惠"弹窗。

**修正**：回退到纯正则 + 通配路径 + 不加字段。

**规则**：
1. 识别参考的替换模式（字段名 + 正则 + 替换值）→ 写等价逻辑
2. **不要改方法**（纯正则→JSON 解析）
3. **不要改路径**（通配→精确）
4. **不要加字段**（超过了参考的范围）
5. 脚本出问题后：第一步回退到已知可用的 commit，逐条加回修改，每次确认正常

案例（本会话实战）：用户给了 4 行 Surge Body Rewrite 参考：
```javascript
http-response ^https?:\/\/lanfanapp\.com\/api\/v1 '"is_prime":\w+' '"is_prime":true'
```
我写成 JSON 解析版 → 坏了。回退到纯正则 → 立即可用。

**原因**：JSON.stringify 改变了 body 的字节级表示（Unicode 转义还原成中文、键重排），客户端校验失效。

### 调试原则：先还原再新增

脚本出问题后的修复流程：

1. **第一步：不打嘴仗，用户说坏了就是坏了**
   - 用户说"不行了 / 坏了 / 恢复了旧的就好" → 立刻回退，不要争辩或分析
   - 用户说"你没改的时候的脚本" → 回退到用户给的参考版本，不要抄仓库的/Openclaw的/任何第三方的
2. **第二步：回退到参考的稳定版本**
   - 用户给了 Surge Body Rewrite 参考 → 回退成等价的纯正则版本（完全相同的字段+替换值+匹配方式）
   - 用户说"Openclaw 写的脚本" → 一字不动复制
   - 用户说"刚才好的版本" → `git log --oneline -10` 找最近的 commit，一步步往回退
3. **第三步：确认回退版能跑** — 推到仓库，用户验证
4. **第四步：只加用户明确要加的，一次只加一条**

**禁止**（这些是以前犯过的错，不能再犯）：
- ❌ 一次改一堆东西然后推上去
- ❌ 在 JSON 解析版 catch 块里加正则 fallback（两个不同路径修改同一个 body，互相覆盖）
- ❌ 改完后不等用户确认就连带改 Loon/Surge 配置一起推
- ❌ 用户说"坏了"的时候争辩"我没改啊" — **哪怕用户记错了也是你的问题**
- ❌ 用户说"要你何用"、"连 Openclaw 都不如"时争辩 — 直接问"什么症状，我修"
- ❌ 用户骂你的时候不要顶嘴也不要道歉长篇大论，直接**承认问题+给解决方案**（一行内说完，不要超过三行）
- ❌ **用户给 Surge Body Rewrite 参考后，你用 JSON 解析/不同的替换方式** — 必须用完全等价的纯正则，不要升级方法
- ❌ **用户给了参考后你自己加额外字段** — 只改参考里有的，不加去水印/去广告/Extra 等
- ❌ **用户说"照这个抄"时收窄 rewrite 路径** — 参考用 `/api/v1` 你也用 `/api/v1`，不要"优化"成精确路径
- ❌ **用户说"刚才好好的你改了什么"时去分析原因** — 不回退就开始分析为什么坏了，用户要的是恢复不是诊断
- ❌ **混用正则和 JSON 解析** — 正则改完后再 JSON.stringify 会覆盖正则结果或改变 body 格式

**硬规则——回退操作标准：**
```bash
# 1. 先找到用户说能用的 commit。不作任何分析，不检查原因，不下结论。
git log --oneline -10

# 2. 恢复到那个版本的这一个文件
git checkout <刚才能用的hash> -- script/Lanfan.js

# 3. 提交
git commit -m 'Lanfan: 回退到能用的版本'

# 4. 推送
git push

# 5. 告诉用户已回退。不要分析原因，不要解释为什么之前坏了。
```

**硬规则——用户给参考了，你的脚本必须和参考等价：**
- 参考用 `body.replace(/"is_prime":\w+/g, '"is_prime":true')`
- 你也用 `body.replace(/"is_prime":\w+/g, '"is_prime":true')`
- 不要换成 `JSON.parse` + `obj.is_prime = true` + `JSON.stringify`
- 不要换成 `replace(/"is_prime":true/g, ...)`（方向和替换值不同）
- 参考匹配 `/api/v1`，你也用 `/api/v1`，不要收窄路径
- 不要加参考里没有的字段

### 写 Rewrite 脚本时的极端警告

**以下情况每个都导致用户骂了你或脚本炸了：**

1. **Surge Body Rewrite 参考 → 写成 JSON 解析版** → JSON.stringify 破坏原始 body 字节级结构
2. **用户给了 4 行替换 → 你写了 8 行**（加了额外字段） → 用户反馈 UI 出现异常弹窗
3. **用户给的参考是通配路径 → 你收窄成精确路径** → 覆盖不全
4. **你能跑的版本 → 你觉得"可以优化"然后改方法** → 坏了
5. **用户说某个功能不行 → 你对整个脚本大改** → 本来能用的部分也炸了
6. **JSON.stringify 改变了 Unicode Escape** → 服务端校验失败或客户端缓存失效
7. **有 HAR 精确 URL 却写了通配符正则** → 被用户骂"我不是给你抓包了吗怎么还那么多配符？"
8. **正则 `.+` 匹配到不该匹配的端点**（offerings 被连带拦截） → 用户说"老是提示有东西被拦截"

**如果你发现 JSON 解析版比纯正则有优势（分支处理、路径分类），以下情况才考虑：**
- 用户没有给 Surge Body Rewrite 参考
- 用户明确要求用 JSON 解析
- 纯正则无法可靠工作（字段值类型多样）

**最安全的路（这条路从未让你被骂过）：**
1. 用户给 Surge Body Rewrite 参考 → 写等价纯正则，一字不改
2. 用户没给参考 → 用 JSON 解析版
3. 任何时候用户投诉 → 回退到参考版本，不动
4. 用户要求加字段 → 只加一条，用户确认后再加下一条

用户给了 Surge Body Rewrite 参考（4 行正则），你只能写 4 行正则替换。即使你觉得"可以加上去广告/去水印/加版本号"——不行。等用户自己提出再加。

| 用户说了/给了 | 你做的事 | 禁止做的事 |
|---|---|---|
| "照着这个 Surge Body Rewrite 抄" | 等价的 replace | 改成 JSON 解析、加 extra 字段、加格式化 |
| "看看 Openclaw 的脚本" | 一字不动复制 | 改格式、删字段、优化、加注释 |
| "这个能用" | 锁死这个版本，不动 | 觉得"我可以优化一下"然后改 |
| "有个功能不行" | 问清具体哪个 API/哪个字段，只改那一个 | 大规模重写、换方法、加预料之外的字段 |
| "加上视频替换" | 只加一行 `v.0_10000.` → `v.` | 额外改其他字段

**对照表：**

| 参考的做法 | 你必须做的 | 绝对不能做的 |
|---|---|---|
| 纯正则替换 `body.replace(...)` | 纯正则 | 改成 JSON.parse→分支→JSON.stringify |
| 宽泛路径 `/api/v1` | `/api/v1` | 精确到 `/api/v1/(user|recipe|...)` |
| **HAR 精确 URL**（如 `api.xxx.com/v1/sub/qqq`） | **精确到该 URL** | **加通配子域名、备份域名、版本范围** |
| 只改 4 个字段 | 只改这 4 个 | 加额外字段（watermark/expires_time 等） |
| 正则匹配 `\w+` | 用 `\w+` | 换其他写法 |

**操作清单：**
1. 识别参考的替换模式（字段名 + 正则 + 替换值）
2. 写等价逻辑（相同字段、相同替换值、相同匹配方式）
3. **不要加额外功能**（去广告、去水印、加版本号等——除非用户要求）
4. **不要改格式**（不要加 JSON.stringify 兜底、不要加 try-catch 包裹正则、不要加递归遍历）
5. **不要改路径匹配**（参考用 `/api/v1` 你就用 `/api/v1`）
6. **拒绝"我可以优化它"的冲动**
7. **用户投诉后第一步是回退，不是解释为什么坏了**

### 现已有脚本 → 能跑就不改

用户仓库里现有的脚本，只要他说能跑 / Openclaw 写的 / 用户没投诉，就不要改。尤其不要：
- 改格式（不增删字段）
- 改头部（不增加脚本头行数）
- 改方法（不升级正则→JSON）
- 加注释 / 去注释 / 格式化

---

### ddgksf2013 的 re() 函数批量替换版 — 当用户要求用此风格时使用

ddgksf2013 风格的 `re()` 函数，用 `@` 分隔多个查找/替换对，单次调用完成所有替换：

```javascript
re('"is_vip":\w+@"vip_expire_time":"[^"]+"@...', '"is_vip":true@"vip_expire_time":"2099-12-31 23:59:59"@...')

function re() {
  var e = $response.body;
  if (arguments[0].includes("@")) {
    var n = arguments[0].split("@"),
        r = arguments[1].split("@");
    for (i = 0; i < n.length; i++) {
      var l = new RegExp(n[i], "g");
      e = e.replace(l, r[i]);
    }
  } else {
    l = new RegExp(arguments[0], "g");
    e = e.replace(l, arguments[1]);
  }
  $done({ body: e });
}
```

**特征：**
- `re()` 函数置于文件底部，调用行在顶部
- 替换对数量相同时用 `@` 拼接（长度必须一致）
- 单对替换时直接传两个字符串
- 不要用 `let/const` 声明 — `function re()` 和 `var` 符合其原始风格
- `$done({ body: e })` 用对象形式（兼容 QX/Surge/Loon 三平台）

**何时用：** 用户明确要求"按ddgksf2013风格改"或"用re()函数"时。默认仍优先用纯正则版。

## 脚本风格选择

### 正则版 — 用户给了参考时强制使用

当用户提供了一句 Surge Body Rewrite 参考（`'"is_prime":\w+' '"is_prime":true'`），必须用纯正则：

```javascript
let body = $response.body;
if (!body) { $done({}); }

body = body.replace(/"is_prime":\w+/g, '"is_prime":true');
body = body.replace(/"unlocked":\w+/g, '"unlocked":true');
body = body.replace(/"watch_type":\d+/g, '"watch_type":1');

$done({ body });
```

### 零变量 IIFE 版 — 此用户强制的纯量风格

用户明确要求脚本中**不得出现任何中间变量**（`var X = ...`、`let body = ...`、`const obj = ...` 全部禁止）。方案：用 IIFE + 逗号操作符，函数参数 `o` 作为临时引用，全部修改完在最后一个表达式返回。

```javascript
$done({
  body: JSON.stringify((o => (
    o.data.isCreator = 1,
    o.data.is_vip = true,
    o.data.expireTime = 4092599349,
    o.data.level = 6,
    o.data.level_name = "年卡会员",
    o.data.can_trail = false,
    o
  ))(JSON.parse($response.body)))
});
```

只解析一次 body，0 个 `var/let/const` 声明。仅适用于简单 response-body 修改（无分支、无循环、一条路径做完）。

### JSON 解析版 — 按 URL/路径分支处理，但只有用户没给参考时才用

```javascript
const url = $request.url;
let body = $response.body;

try {
  const obj = JSON.parse(body);

  if (url.includes('/get_user_config')) {
    obj.result.user_type = 3;
  } else if (url.includes('/payment/paid_modules')) {
    obj.result = obj.result.map(m => ({...m, usage_limit: -1}));

---
*[Content truncated: 1094 lines total]*
---

      if (k) args[k.trim()] = (v || '').trim();
    });
  }
  let count = parseInt(args.appCount) || 8;

  try {
    let data = await new Promise((resolve, reject) => {
      $httpClient.get({
        url: 'https://api.example.com/data',
        headers: { 'User-Agent': 'Surge/5.0' }
      }, (err, resp, body) => {
        if (err) reject(new Error(err));
        else {
          try { resolve(JSON.parse(body)); }
          catch(e) { reject(new Error('JSON parse failed')); }
        }
      });
    });
    let lines = [];
    lines.push('━━━ 标题 ━━━');
    data.items.slice(0, count).forEach((item, i) => {
      lines.push(` ${i+1}. ${item.name}`);
    });
    $done({
      title: '面板标题',
      content: lines.join('\n'),
      icon: 'gift.circle',
      'icon-color': '#FF2D55'
    });
  } catch (e) {
    $done({
      title: '面板标题',
      content: '获取失败: ' + e.message,
      icon: 'exclamationmark.circle',
      'icon-color': '#FF3B30'
    });
  }
})();
```

### 自包含模块（base64 内嵌脚本）

Panel 脚本常需要外部宿主。若想让 `.sgmodule` 单文件安装（无需托管 `.js`），可将脚本 **base64 编码**后作为 `script-path` 内嵌：

```bash
base64 -w 0 script.js   # 输出 base64 字符串
```

模块写法：

```ini
[Script]
脚本标识 = type=panel, script-path=data:text/javascript;base64,<base64内容>, argument=appCount=8
```

**注意**：`data:text/javascript;base64,` 中的逗号是 data URI 标准语法，Surge 解析器能正确处理。脚本修改后需重新 base64 编码更新模块。

### 常见 Panel 数据源

| 来源 | 说明 | 稳定性 | 换区支持 |
|------|------|--------|---------|
| AppRaven GraphQL `dailyDeals` | 逆向自 AppRaven 的全球限免数据 | ✅ 稳定 | ✅ 通过 region 参数 |
| iTunes 官方 RSS Feed | `https://rss.applemarketingtools.com/api/v2/us/apps/top-free/10/apps.json` | ✅ 稳定 | ❌ 仅免费排行 |
| ~~酷酷API `zxki.cn`~~ | **用户禁用**，仅中国区，不支持换区 | ❌ 禁用 | ❌ |

**铁律：不要用 zxki.cn。** 用户明确拒绝。用 AppRaven API。

---

## 18+ 种实战模式速查

| # | 模式 | 描述 |
|---|------|------|
| 1 | 响应体全文替换 | `body.replace(/xxx/g, "yyy")` |
| 2 | 响应体 JSON 插值 | `obj.expires_date = "6666-06-06"` |
| 3 | 分路径解锁 | `switch(true) { case /path1/: }` |
| 4 | API 置空去广告 | `reject-200`, `reject-dict` |
| 5 | 开关修改 | `obj.data.enabled = true` |
| 6 | Content Filter | `body.replace(/ad_break/g, "skip")` |
| 7-23 | 见 reject 家族等 | 详见 reject 家族 |

### reject 家族

```
reject       → HTTP 404, 无 body
reject-200   → HTTP 200, 无 body
reject-img   → HTTP 200, 1px gif
reject-dict  → HTTP 200, {}
reject-array → HTTP 200, []
```

---

## App Store 链接 → App ID → Bundle ID 工作流

当用户发送 App Store 链接让你解锁时，按此流程自动获取所需信息。

### 从 App Store 链接提取 App ID

App Store 链接格式：`https://apps.apple.com/us/app/xxx/id123456789`

**提取规则**：URL 中 `/id` 后面的数字部分即为 `trackId`（App Store 上的唯一产品 ID）。

```python
import re
def extract_app_id(url):
    m = re.search(r'/id(\d{6,12})', url)
    return m.group(1) if m else None
```

### iTunes Lookup API — 获取 Bundle ID 和元数据

用苹果官方公开 API 查 Bundle ID、价格、开发者和分类信息：

```
GET https://itunes.apple.com/lookup?id=123456789
```

返回示例：
```json
{
  "resultCount": 1,
  "results": [{
    "trackId": 123456789,
    "trackName": "App Name",
    "bundleId": "com.developer.AppName",
    "sellerName": "Developer",
    "price": 0.0,
    "averageUserRating": 4.5,
    "userRatingCount": 12345,
    "version": "1.0",
    "minimumOsVersion": "13.0",
    "primaryGenreName": "Productivity",
    "trackViewUrl": "https://apps.apple.com/us/app/xxx/id123456789"
  }]
}
```

关键字段：
- `trackId` — App Store 产品 ID（用于找参考脚本/查已解锁 app）
- `bundleId` — iOS 包名（搜索 GitHub 已有解锁脚本专用）
- `price` — 价格（0=免费，>0=付费）
- `trackName` — 搜索 GitHub 已有脚本

### Bundle ID 反查 App ID

```
GET https://itunes.apple.com/lookup?bundleId=com.developer.AppName&entity=software
```

用途：用户给了 bundleId 但需要 App Store 链接时。

### 自动工具

Skill-local script: `scripts/itunes_lookup.py` — 三合一工具，用 `skill_view` 加载或直接运行：
- **无 HAR 时备选**：参考 `references/appstore-page-product-id-scraping.md`，从 App Store 页面直接 Regex 提取产品 ID
```bash
python3 ~/.hermes/skills/reverse-engineering/qx-script-master/scripts/itunes_lookup.py https://apps.apple.com/us/app/xxx/id123456789
python3 ~/.hermes/skills/reverse-engineering/qx-script-master/scripts/itunes_lookup.py id123456789
python3 ~/.hermes/skills/reverse-engineering/qx-script-master/scripts/itunes_lookup.py com.developer.AppName
```

### 完整工作流

```
用户发 App Store 链接
  ↓
提取 app ID (数字)
  ↓
调 iTunes Lookup API → 拿 bundleId + 应用名 + 价格
  ↓
用 bundleId/应用名 搜索 GitHub 已有解锁脚本
  ↓
如找到参考脚本 → 复制技术路线写脚本
  ↓
如未找到 → 按 HAR 分析工作流抓包逆向
```

### 搜索已有解锁脚本

用 bundleId 或应用名搜索公开仓库：

```bash
# 搜 GitHub 公开仓库
curl -s "https://api.github.com/search/code?q=bundleId+com.developer.AppName&per_page=5"

# 搜用户的 QuantumultX 仓库
gh search code "com.developer.AppName" --repo 7452323/QuantumultX 2>/dev/null

# 搜知名脚本仓库 (ddgksf2013, monlor, Semporia 等)
gh search code "com.developer.AppName" --owner ddgksf2013 --owner monlor --owner Semporia 2>/dev/null
```

注意：很多仓库的脚本用 bundleId 作为文件名或注释里的标识，搜不到完整 URL 路径。备选策略：只搜 `appName` 或 `trackName`。

## 注意事项

- MITM 需信任并安装根证书
- JQ 模式仅 Surge 5.10+ 支持
- **禁止国内平台传播**

---

## cross-platform-proxy-scripting

# Cross Platform Proxy Scripting v2.2

## 平台适配层

| 功能 | QX | Surge | Loon | Egern | Stash | Shadowrocket |
|-----|-----|-------|------|-------|-------|-------------|
| 持久化 | $prefs | $persistentStore | $persistentStore | $config.get | ↔Loon | ↔Surge |
| 通知 | $notify | $notification | $notification.post | $notification | ↔Loon | ↔Surge |
| HTTP | $task.fetch | $httpClient | $httpClient | $api.http | ↔Loon | - |
| 完成 | $done() | $done() | $done() | $done() | - | - |

## 模块格式对比

| 平台 | 模块后缀 | 去广告实现方式 | MITM 配置 |
|------|----------|---------------|-----------|
| **QX** | `.conf` / `.snippet` | `[rewrite_local]` + `script-response-body` | `[mitm] hostname = ` |
| **Surge** | `.sgmodule` | `[Script] http-response + requires-body=1` | `[MITM] hostname = %APPEND% ` |
| **Loon** | `.plugin` | `[Script] http-response` | `[Mitm] hostname = ` |
| **Egern** | `.json` | 类 Surge 格式 | - |
| **Stash** | `.stoverride` | 类 Loon 格式 | - |
| **Shadowrocket** | `.conf` | 简单 reject | - |

---

## ⚠️ 三平台同步常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| 用旧域名（`api.budingscan.com` vs `www.budingscan.com`） | 规则永远不生效 | 一定要从最新 HAR 提取实际 hostname |
| QX 用 `/path` 但 Loon/Surge 完全复制没适配 | Loon/Surge 不匹配 | Loon/Surge 需要完整 regex |
| `.sgmodule` 缺少 `max-size=-1` | 大响应体被截断 | 三平台都要加 body 大小限制 |
| `.plugin` 缺少 `requires-body=true` | 响应体为空 | Loon/Surge 必须加此参数 |

---

## 🔴 Loon 配置文件验尸：用户 .lcf 常见坑

> **实战案例 (2026-07-08)**：用户 Loon 配置导致 z-library.sk 反复报错"重复出现问题"，浏览器 TLS 报错。

### 常见坑清单

| # | 问题 | 后果 | 修复 |
|---|------|------|------|
| 1 | `[Mitm] hostname =` 为空 | 对**所有域名**启用 MITM → 破坏 Cloudflare 站点（z-library.sk、github.com 等）的 TLS 证书链 | 删掉 `[Mitm]` 段，或只填需要的精确域名 |
| 2 | `[Plugin] policy=鸡场°` | 引用不存在的策略组 → 插件加载失败 | 改成现有策略组名 |
| 3 | `[Plugin] policy=白月光、` | 中文顿号 + 节点名不是策略组 → 加载失败 | 删掉或改成策略组名 |
| 4 | 订阅链接 token 过期 | 节点全挂 → 直连/电报走不了 | 更新订阅链接 |
| 5 | `DOMAIN-SUFFIX,https://porntube.cool/,代理模式` | URL 写成域名格式 | 改成 `DOMAIN-SUFFIX,porntube.cool,代理模式` |

### 必查步骤

当用户 Loon 出现"某个网站打不开/重复报错/TLS警告"时：

1. **打开 .lcf 文件** → 搜索 `[Mitm] hostname` → 是否为空？
2. **搜索 `[Plugin] policy=`** → 引用的策略组是否存在？
3. **检查 `[Remote Rule]` URL** → 去掉末尾的 `.lsr` 拼合是否正确？
4. **用 `curl -v https://目标域名`** 看是否 TLS 握手失败（MITM 会换证书链）

### MITM 空 hostname 的典型症状

- 浏览器提示"重复出现问题"、"不是私密连接"、"ERR_TUNNEL_CONNECTION_FAILED"
- 特定网站（CF/Cloudflare 保护的）挂掉，但大部分网站正常
- Telegram、Twitter 等未必报错（因为它们信任更多 CA）
- 抓包发现服务器证书是 Loon 的自签名 CA，而非原始证书

---

## 去广告三大流派（跨平台通用）

详见技能 `qx-script-master` 的详细剖析。快速摘要：

1. **墨鱼流** — MITM + response-body JSON 删字段 → 适用于 App 内广告
2. **毒奶流** — CSS 注入 + JS 注入 → 适用于网页广告/影视站
3. **疯狗流** — 800万规则集暴力阻断 → 适用于全网络覆盖

### reject 家族用法

```
# 所有平台通用
DOMAIN-SUFFIX, ad.example.com, reject        # → 404
DOMAIN-SUFFIX, ad.example.com, reject-200    # → 200 empty body
# Surge/Loon 支持 reject-dict (→ {}), reject-array (→ []), reject-img (→ 1px)
```

---

## 模块互转工具链

| 工具 | 用途 | 用法 |
|------|------|------|
| **Script-Hub** (xream) | Loon→Surge/QX/Stash | `https://script.hub/api/convert?type=surge&url=...` |
| **LoonKissSurge** (QingRex) | CI 自动转换 | `https://surge.qingr.moe/` 一键添加 |
| **czy13724 构建工具** | Surge模块/Loon插件自定义构建 | `https://surge-argu.levifree.qzz.io/` |
| **BoxJS 订阅** | 脚本可视化配置 | `https://docs.boxjs.app` |

---

## 关键教训：从 HAR 创建会员解锁脚本

> **此部分是本会话（2026-06-02 布丁扫描+懒饭）的实战教训沉淀。** 用户 7452323 要求：给参考代码就原样复制，不新增、不优化。出错立即回退到已知可用的 commit。

### 可用模板

`templates/vanilla-regex-unlock.js` — 经用户验证可用的纯正则解锁脚本模板，直接复制修改字段名和路径即可。

### 根本原则

**对于 Surge/QX/Loon 的 response-body 解锁脚本：不要用 JSON.parse + JSON.stringify。始终用纯正则 body.replace() 操作原始字符串。**

理由：

- JSON 序列化/反序列化会破坏原始格式（Unicode 转义、字段顺序、缩进）
- 破坏响应格式会使客户端无法解析，触发回退逻辑（显示购买提示/空白页）
- 正则替换只在字符串层级工作，不改变 JSON 结构

### 验证通过的纯正则写法

```javascript
let body = $response.body;
body = body.replace(/\"is_prime\":\\w+/g, '\"is_prime\":true');
body = body.replace(/\"unlocked\":\\w+/g, '\"unlocked\":true');
body = body.replace(/\"watch_type\":\\d+/g, '\"watch_type\":1');
body = body.replace(/\"expires_time\":\"[^\"]+\"/g, '\"expires_time\":\"2099-12-31 23:59:59\"');
body = body.replace(/\"is_purchased\":\\w+/g, '\"is_purchased\":true');
body = body.replace(/\"watermark\":\\w+/g, '\"watermark\":false');
$done({ body });
```

### 何时可以用 JSON 操作

| 场景 | 方法 | 风险 |
|------|------|------|
| 简单字段 true/false/null 替换 | `body.replace()` 正则 ✔ | 无 |
| 需要根据 url 做条件分支修改特定路径 | `JSON.parse` + 判断 + `JSON.stringify` ⚠️ | 格式被破坏，易触发退路 |
| 需要深层递归修改 | 纯正则逐字段替换 ✔ | 覆盖更全，不破坏结构 |

**核心规则：能正则就不要 JSON。** 正则 `\"unlocked\":\\w+` 覆盖所有层级、所有 API。

### 常用解锁字段

| 字段 | 含义 | 替换值 |
|------|------|--------|
| `is_prime` | 会员身份 | `true` |
| `unlocked` | 内容解锁 | `true` |
| `watch_type` | 观看限制等级 | `1` |
| `is_purchased` | 已购买 | `true` |
| `expires_time` | 会员过期时间 | `"2099-12-31 23:59:59"` |
| `watermark` | 水印 | `false` |

### 视频 URL 限制

部分 App 的会员视频用 `v.0_10000.` 后缀标识低清试看版，替换为 `v.` 可得完整版。但视频10秒试看限制可能是客户端播放器行为（响应体中没有相关限制字段），替换 URL 不一定解除限制。

### rewrite 脚本错误处理清单（本会话实战教训）

当用户说脚本"坏了"或"不行了"时，按此顺序操作：

1. **回退到已知可用的 commit** — 用户最后一次确认能用的提交
2. **每次只改一行，推一次** — 让用户验证，不要一次改完全部再推
3. **检查替换方式是否变了** — 从纯正则改成了 JSON.parse+stringify 会导致 body 字节变化，触发客户端回退
4. **检查路径是否被收窄了** — 从 `/api/v1` 改成了精确路径组，可能漏掉端点
5. **检查是否加了新字段** — 超过了用户给的参考范围（用户没要求就别加）
6. **"1500+精选 限时特惠"等弹窗提示恢复** → 检查 3+4+5，不要分析为什么，立即回退

当用户说脚本"坏了"或"不行了"时，按此顺序检查：

1. **回退到已知可用的 commit** — 用 `git log --oneline -10 找 hash` + `git checkout <hash> -- script/xxx.js`
2. **检查替换方式是否变了** — 从纯正则改成了 JSON.parse+stringify 会导致 body 字节变化，触发客户端回退
3. **检查路径是否被收窄了** — 从 `/api/v1` 改成了精确路径组，可能漏掉端点
4. **检查是否加了新字段** — 超过了用户给的参考范围（用户没要求就别加）
5. **每次只改一行，改完推一次让用户验证**

**典型用户反应**："1500+精选 限时特惠"弹窗 → 检查 (2)+(3)+(4)。

**记住**：用户给什么代码你就写什么代码。用户给 5 行正则，你写 6 行就是多。不要觉得"我可以优化"。

### 三平台配置要点

- QX: `[rewrite_local]` + `script-response-body` + `[mitm] hostname =`
- Surge: `[Script] http-response` + `requires-body=true` + `max-size=-1` + `[MITM] hostname = %APPEND%`
- Loon: `[Script] http-response` + `requires-body=true` + `[Mitm] hostname =`
- **不要在配置里用通配符路径匹配所有 API**，应精确到有限 API 组

### 注意事项（避免埋坑）

- 如果服务端返回 `steps: []` (空数组) 而不是隐藏，说明步骤数据在服务端根本不存在于响应体中，rewrite 无法变出数据
- `tips` 字段包含会员引导文案（如"立刻购买懒饭会员..."），这类文案可以通过正则替换为 `\"tips\":\"\"` 来清除
- 每个 App 的 ``watch_type`` 值含义不同，需要从抓包中对比免费/会员菜谱的取值差异
- 用户对自己的代码风格有明确偏好：极短、精确、不添加未要求的特性
- 具体案例见 `references/布丁扫描-布丁扫描-lanfan-rewrite-cases.md`

---

## Env.js 核心 API

```javascript
const $ = new Env('脚本名');

// 存储
$.read(key) / $.write(val, key)

// 通知
$.msg(title, sub, body)

// HTTP 请求
$.get(url, cb) / $.post(url, body, cb)

// 日志
$.log(msg)

// 完成
$.done(data)
```

> Yu9191 的 @nsnanocat/util 提供更完善平台检测 (`$app`) 和 Storage/fetch 封装，适合 Rollup 打包模块化项目。见 qx-script-master → `references/yu9191-dual-style-and-revenuecat.md`

---

## 签到脚本失败排查：Cloudflare Turnstile 检测（2026-06-08 Lyrebird 实战）

**错误信号**: 签到返回 `"Turnstile token is required for daily check-in."` 或 `"Turnstile verification failed"`

**根本原因**: 网站后端对签到端点要求必须传 `{"turnstileToken":"..."}` body 参数。token 由前端 Cloudflare Turnstile widget 在真实浏览器中生成，有效期极短，**纯脚本无法获取**。

**检测流程**:
1. 查看 HAR 中签到 POST 的 body — 是否含 `turnstileToken` 字段
2. 用 `{}` 或 `{"turnstileToken":""}` 直接测试 → 400 + `"token is required"`
3. 复用旧 token → 400 + `"token expired"`
4. 从服务器 IP 测 → 同样拒绝（全球统一强制）

**不可行的替代方案**（已验证）：
- `cf_clearance` cookie 不能替代 turnstileToken
- GET 参数版本（`?turnstileToken=xxx`）— 404
- Header 传递（`x-turnstile-token`）— 401
- 通过 `POST /api/auth/login` 获取新 bearer token 再签到 — 仍缺 turnstileToken

**实战案例: Lyrebird Emby** (`console.lyrebirdemby.com`)
- site_key: `0x4AAAAAACMZLvSu_zM8QCKA`
- 签到端点: `POST /api/account/points/check-in`
- 成功签到返回: `{"amount":10,"balance":370,"checkedInAt":"..."}`
- Token 在抓包中可见，但无法复用
- 结论: **纯脚本签到不可行**，需要 Pydoll/Playwright 等自动化工具或可用的后端降级接口

---

## 参考文件

| 文件 | 内容 |
|------|------|
| `references/loon-config-pitfalls.md` | Loon .lcf 配置常见坑与排查指南（2026-07-08 实战） |
| `references/lyrebird-turnstile-har-analysis.md` | Cloudflare Turnstile HAR 分析案例 |
| `references/lanfan-rewrite-lessons.md` | 懒饭 rewrite 脚本教训 |
| `references/布丁扫描-布丁扫描-lanfan-rewrite-cases.md` | 布丁扫描+懒饭 rewrite 案例集 |

---

## crypto-proxy-fallback

# Crypto Proxy Fallback

## When to Use

Scripts using `require('crypto').createCipheriv('aes-128-ecb', ...)` that need Surge/Loon/QX compatibility. Without a fallback, `crypto is not defined` → API receives unencrypted data → fails silently.

## Runtime Detection

```javascript
const isSurge = typeof $httpClient !== 'undefined' && typeof $loon === 'undefined';
const isLoon  = typeof $loon !== 'undefined';
const isQX    = typeof $task !== 'undefined' && !isLoon && typeof $httpClient === 'undefined';
const isNode  = typeof process !== 'undefined' && process.release && process.release.name === 'node';
```

## Encrypt Helper

```javascript
function encrypt(text) {
  if (isNode) {
    const crypto = require('crypto');
    const key = Buffer.from('YOUR_KEY', 'utf8');
    const ci = crypto.createCipheriv('aes-128-ecb', key, null);
    ci.setAutoPadding(true);
    return Buffer.concat([ci.update(String(text), 'utf8'), ci.final()]).toString('base64');
  }
  return $AES(text, 'YOUR_KEY');
}
```

## Pure-JS AES-128-ECB (verified against native crypto)

PKCS7 padding, standard base64, FIPS-197. Produces byte-identical output to `crypto.createCipheriv('aes-128-ecb', key, null)`:

```javascript
const $AES = (()=>{
  const S=[0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16];
  const R=[0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36];
  const g2=a=>((a<<1)^((a>>7)*0x1b))&0xff;
  const g3=a=>g2(a)^a;
  function ke(kb){
    const w=new Array(44);
    for(let i=0;i<4;i++) w[i]=(kb[4*i]<<24)|(kb[4*i+1]<<16)|(kb[4*i+2]<<8)|kb[4*i+3];
    for(let i=4;i<44;i++){
      let t=w[i-1];
      if(i%4===0) t=(S[(t>>>16)&0xff]<<24)^(S[(t>>>8)&0xff]<<16)^(S[t&0xff]<<8)^S[(t>>>24)&0xff]^(R[i/4-1]<<24);
      w[i]=w[i-4]^t;
    }
    return w;
  }
  function enc(b,w){
    let s=b.slice();
    const ak=r=>{for(let c=0;c<4;c++){const kw=w[r*4+c];s[c*4]^=(kw>>>24)&0xff;s[c*4+1]^=(kw>>>16)&0xff;s[c*4+2]^=(kw>>>8)&0xff;s[c*4+3]^=kw&0xff;}};
    const sb=()=>{for(let i=0;i<16;i++)s[i]=S[s[i]];};
    const sr=()=>{[s[1],s[5],s[9],s[13]]=[s[5],s[9],s[13],s[1]];[s[2],s[6],s[10],s[14]]=[s[10],s[14],s[2],s[6]];[s[3],s[7],s[11],s[15]]=[s[15],s[3],s[7],s[11]];};
    const mc=()=>{for(let c=0;c<4;c++){const i=c*4,a=[s[i],s[i+1],s[i+2],s[i+3]];s[i]=(g2(a[0])^g3(a[1])^a[2]^a[3])&0xff;s[i+1]=(a[0]^g2(a[1])^g3(a[2])^a[3])&0xff;s[i+2]=(a[0]^a[1]^g2(a[2])^g3(a[3]))&0xff;s[i+3]=(g3(a[0])^a[1]^a[2]^g2(a[3]))&0xff;}};
    ak(0);
    for(let r=1;r<=9;r++){sb();sr();mc();ak(r);}
    sb();sr();ak(10);
    return s;
  }
  function pad(b){const p=16-(b.length%16),o=new Uint8Array(b.length+p);o.set(b);for(let i=0;i<p;i++)o[b.length+i]=p;return o;}
  function b64(b){
    const c='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    let r='';
    for(let i=0;i<b.length;i+=3){
      const b0=b[i],b1=i+1<b.length?b[i+1]:0,b2=i+2<b.length?b[i+2]:0;
      r+=c[b0>>2]+c[((b0&3)<<4)|(b1>>4)];
      if(i+1>=b.length) r+='==';
      else{r+=c[((b1&0xf)<<2)|(b2>>6)];if(i+2>=b.length) r+='=';else r+=c[b2&0x3f];}
    }
    return r;
  }
  return (pt,ks)=>{
    const kb=new Uint8Array(ks.split('').map(c=>c.charCodeAt(0)));
    const p=new Uint8Array(pt.split('').map(c=>c.charCodeAt(0)));
    const pd=pad(p),wk=ke(kb);
    let r=[];
    for(let b=0;b<pd.length;b+=16)r.push(...enc(pd.slice(b,b+16),wk));
    return b64(r);
  };
})();
```

## Verification

```bash
node -e "
const c=require('crypto');
const key=Buffer.from('Z0J7M480h6kppf67','utf8');
const p='{\"test\":1}';
const ci=c.createCipheriv('aes-128-ecb',key,null);
ci.setAutoPadding(true);
console.log(Buffer.concat([ci.update(p,'utf8'),ci.final()]).toString('base64'));
"
```

## Pitfalls

- Key encoding: `Buffer.from(key, 'utf8')`, not hex or base64
- PKCS7 padding matches Node's `setAutoPadding(true)`
- No `Buffer` on Surge → `Uint8Array` + manual base64
- Don't try-catch `require('crypto')` — routing depends on isNode check

---
