1|---
2|name: anti-debug
3|description: JS反调试对抗技能。识别并绕过4类反调试手段：无限debugger（9种模式）、DevTools检测、时间检测、属性检测。统一5步流程。
4|author: 7452323 (converted from Private Gist)
5|tags:
6|  - anti-debug
7|  - anti-devtools
8|  - debugger
9|  - js-reverse
10|---
11|
12|# Anti-Debug — JS反调试对抗技能
13|
14|## 4类反调试
15|
16|### 1. 无限 debugger
17|
18|| 模式 | 特征 | 绕过方式 |
19||------|------|----------|
20|| constructor | `function(){}[\"constructor\"](...)` | 重写 constructor |
21|| setInterval | 定时触发 debugger | 拦截 setInterval |
22|| eval | eval 中注入 debugger | 重写 eval |
23|| Function | new Function('debugger') | 重写 Function |
24|| Object.defineProperty | getter/setter 触发 | 提前 Hook |
25|| iframe | 子页面 debugger | 拦截 iframe 创建 |
26|| worker | Web Worker debugger | 拦截 Worker |
27|| catch 异常触发 | try-catch 触发 | Hook 异常 |
28|| Date 定时 | Date.now 差值检测 | 覆盖 Date.now |
29|
30|### 2. DevTools 检测
31|- 元素检测：`toString.call(element)`
32|- 控制台检测：`console.log` 是否被重写
33|- 窗口大小检测
34|- 颜色格式检测
35|
36|### 3. 时间检测
37|- `Date.now` / `performance.now` 差值
38|- setTimeout 延迟分析
39|
40|### 4. 属性检测
41|- `element[n]` 访问
42|- 原型链遍历
43|- 异常消息解析
44|
45|## 统一5步流程
46|
47|1. 识别反调试类型（断点定位触发点）
48|2. Hook 关键函数（constructor/setInterval/eval/Function）
49|3. 替换实现（返回无操作的 stub）
50|4. 验证绕过（确认代码正常运行）
51|5. 固化补丁（保存到环境补丁中）
52|

## 实战提炼：逆向过程中的反调试对抗通用模式

### 从 chatgpt2api 和 ONE App 中提炼

### 对抗类型矩阵

| 对抗类型 | 常见实现 | 绕过方法 | 实战案例 |
|---------|---------|---------|---------|
| WAF/CDN 拦截 | SudunWAF / Cloudflare / Xcdn | 换节点/用代理/模拟浏览器指纹 | chatgpt2api 的 Xcdn / ONE App 的 SudunWAF |
| 签名验证 | 服务端校验请求 sign | 逆向签名算法后复现 | ONE App 的 MD5+MD5+salt 签名 |
| Token 绑定 | JWT 绑定 IP/device | 同一 IP 调用 / 模拟设备指纹 | ONE App 的 JWT IP 绑定 (±600s) |
| 请求频率限制 | Rate limiting + 429 | Token 池轮询 + 延时 | chatgpt2api 的账号轮询 |
| 返回加密 | 全部 API 响应 AES 加密 | 逆向 AES Key/IV | ONE App 的 AES-128-CBC 响应加密 |
| 图片加密 | CDN 返回加密的 JPEG | 逆向图片加解密 Key | ONE App 的 CDN AES 加密图片 |
| 代码混淆 | Flutter obfuscation / JS 混淆 | 搜字符串常量跳过混淆层 | ONE App 的 main.dart.js 混淆 |
| 反自动化工 | PoW / Turnstile / CAPTCHA | 第三方 solver / 浏览器自动化 | chatgpt2api 的 sentinel PoW |

### 实战绕过模式

```
遇到反调试 → 按类型分类：
├── WAF/CDN 拦截
│   └── 用 curl_cffi / Playwright 伪造完整浏览器指纹
│
├── 签名验证
│   └── 反编译找 Key/IV/Salt → Python 复现签名算法
│
├── Token 验证
│   ├── 有 bootstrap 无 Token 端点？→ 直接拿 JWT
│   ├── 无？→ HAR 抓取已有的 Token
│   └── 都没有？→ 账号密码登录自动获取
│
├── 加密响应
│   ├── 反编译找 Key/IV → 解密每一步 API 响应
│   └── 如果响应是 Salted__ 开头 → OpenSSL salted 格式 → 试密码
│
├── 加密图片
│   ├── 图片熵值 ~8.0 → 加密 → 找独立 CDN 域名
│   └── Flutter Web 版 JS 中可找到图片解密 Key
│
├── 请求限制
│   ├── 单账号超限 → 多账号轮询（token 池）
│   └── IP 限制 → 代理池 / 更换节点
│
└── 反自动化
    └── 如果太复杂 → 用 Chromium CDP 手工模拟
```
