---
name: js-reverse-master
category: reverse-engineering
description: >-
  Merged skill combining: js-reverse-engineering, camoufox-workflow, find-crypto-entry, js-reverse-mcp-integration, jsrpc-auto-reverse, algorithm-reverse.
version: "1.0"
sources:
  - js-reverse-engineering
  - camoufox-workflow
  - find-crypto-entry
  - js-reverse-mcp-integration
  - jsrpc-auto-reverse
  - algorithm-reverse
tags: [reverse-engineering, merged]
---

# js-reverse-master

> **Merged from**: js-reverse-engineering, camoufox-workflow, find-crypto-entry, js-reverse-mcp-integration, jsrpc-auto-reverse, algorithm-reverse
> **Source count**: 6

---

## Table of Contents

1. [js-reverse-engineering](#js-reverse-engineering)
2. [camoufox-workflow](#camoufox-workflow)
3. [find-crypto-entry](#find-crypto-entry)
4. [js-reverse-mcp-integration](#js-reverse-mcp-integration)
5. [jsrpc-auto-reverse](#jsrpc-auto-reverse)
6. [algorithm-reverse](#algorithm-reverse)

---

## js-reverse-engineering

# JS逆向工作流总纲

本技能是JS逆向领域的**总纲层**，编排6阶段全流程，协调子技能完成端到端逆向。

**核心原则**：本技能定义"做什么"和"引用谁"，具体实现由子技能承担。每个阶段说清目标、完成判据和引用技能，不说具体操作。

**持续进化原则**：本技能树是必装的。每次吸收外部逆向工程的精华（新工具、新方法论、新工作流、新反模式），必须反馈到技能树中：
1. 工具类吸收 → 更新工具选择决策树
2. 方法论吸收 → 更新阶段定义/切换规则/参考文档
3. 反模式吸收 → 更新 Pitfalls 和反模式清单
4. 案例/经验吸收 → 更新反模式清单或引用链接
5. 吸收后，更新 SKILL.md 的 version 字段
6. 类级重写 → 如果某个子技能的触发条件已被总纲覆盖，更新该子技能触发条件

---

## 技能树总览

```
L0 基础层
├── cdp-debug-reverse ──── CDP协议调试原语
├── find-crypto-entry ──── 加密入口定位
└── webpack-unpack ─────── Webpack解包

L1 分析层
├── ast-deobfuscation ──── AST反混淆
├── anti-debug ─────────── 反调试对抗
└── env-patch ──────────── 补环境

L2 还原层
├── algorithm-reverse ──── 算法/协议逆向
├── jsvmp-reverse ──────── JSVMP/VMP逆向
└── ruishu-reverse ─────── 瑞数纯算逆向

L3 领域层
├── web-api-reverse ────── API协议逆向
└── skill-creator ──────── 技能创建元技能
```

---

## 六阶段工作流

任何逆向任务必须明确当前所处阶段；没有阶段结论，不应跳到下一阶段。

| 阶段 | 目标 | 核心原则 | 完成判据 | 引用技能 |
|------|------|---------|---------|---------|
| **Observe** | 确认目标请求、脚本、函数 | Observe-first | 能回答：谁发起、哪段脚本、如何触发 | → **cdp-debug-reverse**（脚本发现、请求拦截） |
| **Capture** | 最小侵入采样 | Hook-preferred | 至少一条可复用真实运行样本 | → **find-crypto-entry**（定位加密入口）+ **cdp-debug-reverse**（Hook采样） |
| **Rebuild** | 导出本地Node复现工程 | Rebuild-oriented | 本地稳定复现入口 | → **ast-deobfuscation**（解混淆后代码可读）+ **env-patch**（导出环境bundle） |
| **Patch** | 按代理日志驱动补环境 | Evidence-first | env rebuild跑通+服务端验收通过 | → **anti-debug**（先过反调试）+ **env-patch**（诊断驱动补环境） |
| **PureExtraction** | 分离环境噪音与算法输入 | Freeze-first | Node pure与runtime fixture对齐 | → **algorithm-reverse**（算法还原）+ **jsvmp-reverse**（VMP场景） |
| **Port** | 迁移到Python/其他宿主 | Node-before-Python | 外部语言版本与Node pure对齐 | → **algorithm-reverse**（Python复现规范） |

### 阶段切换规则

- 只有env rebuild跑通且服务端验收通过后，才允许进入PureExtraction
- 只有Node pure已稳定后，才建议进入Port
- 任一阶段出现不一致，应回退到最早出现分叉的阶段
- **证据门禁**：路由到定位前，必须从真实样本确认目标请求，禁止猜测
- **状态契约**：每个阶段产物必须包含统一状态块（就绪/部分完成/阻塞/失败/不可交付），用于阶段切换判断

### 复杂度分级（L1-L4 路由）

在开始任何逆向任务前，先评估目标复杂度，选择路由路径：

| 级别 | 特征 | 路由路径 | 示例 |
|------|------|---------|------|
| **L1 透明链** | 请求参数可见，无混淆，无壳 | Observe → Capture → Port | 简单form签名 |
| **L2 单层壳** | 有混淆但无环境检测 | → Rebuild → PureExtraction | obfuscator.io混淆 |
| **L3 多层壳+环境** | 有多层混淆+环境检测 | → Patch → PureExtraction | 补环境+AST还原 |
| **L4 对抗级** | 瑞数/极验/WASM/VMP | → anti-debug → 专项技能 | 瑞数5代+ |

### 红线

- 还没确认目标请求就开始补环境
- 还没定位关键脚本就手翻混淆代码
- 没有代理日志和first divergence记录就补宿主
- env rebuild还没通过就开始翻Python
- 把补环境成功误当成纯算法已完成
- **跳过证据门禁**：目标请求未从真实样本确认就跳到定位阶段
### Observe → cdp-debug-reverse / Lightpanda

**第零步（除非你在浏览器里看过页面，否则别跳）：先看渲染页面**

不要假设 API 返回 = 页面显示。SSR/Next.js RSC/diy.js 可能直接把完整数据嵌进 DOM，API 只是辅助功能。先浏览器打开页面看实际渲染了什么，确认数据是从 API 来还是从 SSR 来，再决定后续方向。

如果服务器无浏览器环境，让用户截图/描述页面渲染结果——这比任何代码分析都更快、更准。

**⚠ API-level auth vs TLS fingerprint 陷阱**：某些服务（如 MiMo `api.xiaomimimo.com`）的认证分两步——
1. Bootstrap/JWT token：任意客户端可读（200 OK）
2. 核心接口（chat）：需要 TLS JA3 指纹或设备指纹绑定

当遇到 bootstrap 成功但核心接口被 403，且换 IP 也无效 → **高度怀疑 TLS 指纹校验**，不是单纯 IP 封锁。免费代理隧道不改 JA3 指纹，也无法绕过。

**多域名陷阱**：同一个站点可能有 CN 主站和 EU 备用站指向**不同服务器**（`dig +short` 看 IP）。一个域名限速了试另一个——但不同服务器可能跑了不同版本，行为可能不一致。用户说页面数据和 API 不一致时，先 DNS 确认自己测的是哪个版本。

**IP 限速绕过**：某些服务器对源 IP 限速（403/429）。如果系统有 `tor` 服务（`which tor`），直接用 SOCKS5 代理绕过：
```bash
curl -s --socks5-hostname 127.0.0.1:9050 -m 15 "https://target.com/"
```
Tor 默认在 `127.0.0.1:9050` 暴露 SOCKS5。搭配 Python `httpx` 或 `requests` 使用前先验证 Tor 是否运行（`systemctl status tor` 或 `pgrep -a tor`）。比换 IP 段更轻量，无额外依赖。

1. 用 `list_scripts` 发现页面脚本
2. 用 `list_network_requests` 捕获目标请求
3. 用 `get_request_initiator` 追踪请求发起者
4. 确认：谁发起、哪段脚本、如何触发

**Lightpanda 替代方案**（无需 CDP 时的轻量 Observe）：
- `mcp_lightpanda_goto` → 加载页面
- `mcp_lightpanda_semantic_tree` → 页面结构概览
- `mcp_lightpanda_interactiveElements` → 交互元素发现（按钮、输入框、表单）
- `mcp_lightpanda_evaluate` → 提取 script 标签列表、全局变量、inline JS
- `mcp_lightpanda_structuredData` → JSON-LD / OpenGraph 元数据
- `mcp_lightpanda_links` → 外部链接发现

Lightpanda 优势：无需配置 CDP 连接，直接在 MCP 层操作。适合快速 Observe 阶段。
Lightpanda 限制：XHR/Fetch hook 对 SPA 动态请求不可靠，无法做断点调试。如需深度调试仍需 cdp-debug-reverse。

### Capture → find-crypto-entry + cdp-debug-reverse

1. 用 **find-crypto-entry** 定位加密入口（静态搜索优先，XHR断点辅助）
2. 用 **cdp-debug-reverse** 的Hook工具采样关键函数输入输出
3. 确认：至少一条可复用真实运行样本

### Rebuild → ast-deobfuscation + env-patch

1. 遇到混淆代码 → **ast-deobfuscation** 执行7步反混淆
2. 遇到Webpack打包 → **webpack-unpack** 先解包再反混淆
3. 用 **env-patch** 的 `export_rebuild_bundle` 导出本地复现工程
4. 确认：本地稳定复现入口

### Patch → anti-debug + env-patch

1. 遇到反调试 → **anti-debug** 绕过（CDP层优先，JS层fallback）
2. 用 **env-patch** 执行诊断驱动补环境
   - 最小因果单元原则：每次只补当前first divergence
   - 补丁四步循环：跑→读日志→补最小单元→重跑验证
3. 遇到document.all → **env-patch** 的sdenv方案
4. 补环境成本过高 → 评估JsRpc/sdenv替代路线
5. 确认：env rebuild跑通+服务端验收通过

### PureExtraction → algorithm-reverse + jsvmp-reverse

1. 标准签名/混合加密/验证码 → **algorithm-reverse**
   - 6类题型分类 + 5层检查点体系
   - 验证码场景用5线拆分法
2. JSVMP/VMP → **jsvmp-reverse**
   - 数据驱动路线（推荐首选）
   - AST反编译路线（复杂协议）
3. 瑞数 → **ruishu-reverse**
4. 确认：Node pure与runtime fixture对齐

### Port → algorithm-reverse

1. 用 **algorithm-reverse** 的Python复现规范生成代码
2. 验证：外部语言版本与Node pure对齐
3. 工程化产出（Docker/服务化）按需

---

## 典型场景的技能串联

### 场景A：混淆JS签名
```
find-crypto-entry → ast-deobfuscation → algorithm-reverse
```

### 场景B：VMP加密+环境检测
```
anti-debug → env-patch → find-crypto-entry → jsvmp-reverse → algorithm-reverse
```

### 场景C：瑞数反爬
```
ruishu-reverse（412确认→决策树→纯算/JsRpc/sdenv三选一）
```

### 场景D：API协议逆向
```
web-api-reverse → 遇混淆→ast-deobfuscation → 遇加密→find-crypto-entry + algorithm-reverse
```

---

## 工具选择决策树

按逆向目标快速查工具（共74个工具，4大类）。

### 脚本发现 → `list_scripts` → `get_script_source` / `find_in_script` / `search_in_scripts`

### Hook采样（优先） → `create_hook` → `inject_hook` → `get_hook_data`
- 函数监控：`hook_function` / `trace_function`
- 断点调试（最后手段）：`set_breakpoint` / `set_breakpoint_on_text` / `break_on_xhr`

### 请求定位 → `list_network_requests` → `get_network_request` / `get_request_initiator`

### 代码分析 → `collect_code` → `understand_code` / `summarize_code` → `deobfuscate_code` / `detect_crypto` → `risk_panel`

### 一键分析 → `analyze_target`（组合collect+security+crypto+hook correlation）

### 国密/特殊加密 → `node /opt/jshook-skill/dist/skill.js detect-crypto "<code>"`
（jshook 内置 `sm-crypto`，当 `detect_crypto` 无结果时切换）

### 事件断点（鼠标/键盘/WebSocket）→ `node /opt/jshook-skill/dist/skill.js event-breakpoint set-mouse`
（JSReverser-MCP 仅有 XHR 断点，jshook 补充事件级断点）

### Watch 表达式 → `node /opt/jshook-skill/dist/skill.js watch add <expr> <label>`
（持久化监控表达式值变化，JSReverser-MCP 无此功能）

### 脚本黑盒 → `node /opt/jshook-skill/dist/skill.js blackbox set *vendor*.js`
（跳过第三方库的断点干扰）

### DOM 文本定位 → `node /opt/jshook-skill/dist/skill.js dom clickable "登录"`
（按文本精确查找可点击元素，比 CSS selector 更直观）

### 缓存/统计 → `node /opt/jshook-skill/dist/skill.js stats`
（查看缓存命中率、压缩率，评估数据收集质量）

### 环境导出 → `export_rebuild_bundle` → `diff_env_requirements`（辅助比对，不替代代理日志）

### 证据记录 → `record_reverse_evidence` → `export_session_report`

### 运行时检查 → `inspect_object` / `get_storage` / `search_in_sources` / `monitor_events`

### 隐身注入 → `inject_stealth` / `list_stealth_presets` / `set_user_agent`

### 完整工具参考 → [references/tool-quick-reference.md](references/tool-quick-reference.md)

### 证据驱动工作流 → [references/evidence-driven-workflow.md](references/evidence-driven-workflow.md)
（阶段门禁、复杂度分级L1-L4、请求链状态机、17条反模式清单、纯算迁移检查清单）
### Electron 桌面应用逆向 → [references/electron-desktop-re-pipeline.md](references/electron-desktop-re-pipeline.md)
（ASAR提取 → webcrack → Babel scope rename，来自 SkillsMP re-js-app 46★）

### 瑞数专项增强 → [references/evidence-driven-workflow.md](references/evidence-driven-workflow.md#瑞数专项增强)
（两跳路由、hasDebug分支处理、basearr闭合）

---

## JS Hook 方法论（从 jsjiami.com 文章吸收）

### setTimeout Hook 劫持

jsjiami 文章《setTimeout Hook 劫持》(#12) 提供的浏览器级动态劫持方案。**与 JSReverser-MCP 的 CDP Hook 互补**——当无法使用 CDP（反检测环境）时，在页面上直接注入油猴脚本劫持定时器。

```javascript
// 保存原始引用
var _setTimeout = window.setTimeout;

// 重写 setTimeout 实现劫持
window.setTimeout = function(ref, tm) {
    var code = '' + ref;  // toString 获取函数源码
    
    // 检测目标脚本并替换
    if (code.indexOf('www.target.com/main.js') !== -1) {
        ref = function() {
            var script = document.createElement("script");
            script.setAttribute("src", "https://my-proxy.com/main.js");
            var s = document.getElementsByTagName("script")[0];
            s.parentNode.insertBefore(script, s);
        };
    }
    return _setTimeout(ref, tm);
};
```

**适用场景：**
- 劫持动态加载的 JS 脚本
- 替换广告/统计代码
- 替换加密后的代码为明文版本
- 分析定时器逻辑和调用频率

**扩展：同样的模式可应用于：**
- `setInterval` — 劫持轮询请求
- `requestAnimationFrame` — 劫持动画/Canvas 渲染
- `addEventListener` — 劫持事件绑定

### Sign 签名逆向方法论

从 jsjiami 《丁香公开课 sign 签名分析》(#2) 提炼的通用 sign 逆向流程：

```
1. 定位 → Chrome Network 面板搜索 'sign' / 'signature' / '_sign'
2. 断点 → XHR Breakpoints 或给 sign 相关函数下断点
3. 提取 → 将加密代码复制到本地独立运行
4. 还原 → 分析：参数字典排序 + 拼接 + 哈希算法
```

常见 sign 生成模式：
```javascript
// 模式1：按 key 排序拼接（丁香公开课）
var keys = Object.keys(allParams).filter(k => v !== undefined).sort();
var raw = keys.map(k => k + '=' + allParams[k]).join('&');
var sign = sha1(raw);

// 模式2：固定 salt 拼接
var sign = md5(params + 'fixed_salt');

// 模式3：动态 salt + 时间戳
var sign = sha256(params + timestamp + nonce + secretKey);
```

### 永不断点反调试深层分析

jsjiami 《永不断点 Debugger》(#3) 展示的多层 Function 嵌套 debugger 注入：

```javascript
// jsjiami 的反调试示例 —— 多层嵌套绕过 toString 检测
(function (a) {
    return (function (a) {
        return (Function('Function(arguments[0] + "' + a + '")()'))(a);
    })(a);
})('bugger')('de', 0, 0, (0, 0));
```

**绕过策略：**
1. Chrome DevTools → ⏸️ Deactivate breakpoints (Ctrl+F8)
2. DevTools → Settings → Ignore List → 添加脚本忽略
3. 启动参数：`chrome --disable-debugger`
4. 覆写 Function 构造函数（`anti-debug` 三合一方案）
5. **关键洞察**：JS 的 `Function` 构造器是最底层的反调试载体。只要 Function 没有被 Hook，任何层级的 Function('debugger') 都能执行。所以 Hook Function 是所有反调试方案的基础。

### 防检测跳转技术

jsjiami 《优雅跳转 & 防检测跳转》(#8) 展示的绕过爬虫检测的跳转模式：

```html
<script>
var surl = 'https://target.com/';
// 通过函数拼接字符串，绕过静态检测
var x = function() { return 'top.'; };
var f = function() { return 'loca'; };
var s = function() { return 'tion.'; };
var e = function() { return 'href'; };
var o = function() { return '="'; };

function errorLoad() {
    setTimeout(function() {
        eval(x() + f() + s() + e() + o() + surl + '"');
    }, 500);
}
</script>
<!-- 利用图片加载失败触发跳转，绕过爬虫/爬虫检测 -->
<img src="https://zz.baidu.com/load.gif" onerror="errorLoad();" style="display:none;">
```

**核心技巧：**
- 字符串通过函数拼接（绕过静态分析中的字符串搜索）
- 通过 `onerror` 触发（比 `window.onload` 更难被 Hook）
- `eval` 执行拼接结果（最终执行时才能确定目标 URL）

### 代码质量与加密的关系

从 jsjiami 文章(#5 "is not defined" 排错) 提炼的加密兼容性最佳实践：

**变量必须提前声明：**
```javascript
// ❌ 错误 —— 混淆后变量提升可能导致 is not defined
if (type == 1) { var mq = 'active'; }
else if (type == 2) { var mq = 'selected'; }

// ✅ 正确 —— 提前声明 + 赋默认值
var mq = 'checked';
if (type == 1) { mq = 'active'; }
else if (type == 2) { mq = 'selected'; }
```

**使用闭包模式暴露全局接口：**
```javascript
// ✅ 推荐 —— 闭包 + 单一全局导出
(function(w) {
    var T = {};
    T.test = function() { /* todo */ };
    w.T = T;
})(window);
T.test();  // 安全调用
```

**代码规范与加密兼容性核对表：**
- [ ] 所有变量在使用前已声明
- [ ] 使用 `===` 而非 `==`（避免隐式类型转换导致混淆后异常）
- [ ] 不使用 `arguments.callee`（严格模式下禁用）
- [ ] 使用闭包模式组织代码
- [ ] 字符串引用外部变量时用模板字符串而非拼接
- [ ] 文件编码为 UTF-8 无 BOM

### AST 反混淆补充工具箱

除了 Babel 以外，可以引入以下专用工具：

| 工具 | 用途 | 安装 | 
|------|------|------|
| **webcrack** | ⭐2.7k obfuscator.io反混淆+webpack/browserify解包+unminify，一站式 | `npx webcrack [input.js]` |
| **decode-js** | 基于 Babel 的自动化反混淆工具，支持 sojson/obfuscator.io 等 | `npm install decode-js` |
| **ClarityJS** | 支持 jsjiami v7 的反混淆 | `npm install clarityjs` |
| **de4js** | 在线/CLI 反混淆，支持多种混淆类型 | `npm install de4js` |
| **js-beautify** | 代码格式化 | `npm install js-beautify` |
| **VM2** | 沙箱执行环境，安全执行混淆代码中的解密函数 | `npm install vm2` |
| **deobfuscate.relative.im** | 在线一键JS反混淆（mangled/obfuscated） | `https://deobfuscate.relative.im` |

> 上述方法论和代码示例来自 jsjiami.com/article 共16篇文章的精华提炼。完整文章索引见 [`reverse-engineering-index`](../reverse-engineering-index/SKILL.md) 或 jsjiami.com/article/。

---

## 安全边界

- 仓库case只保留抽象模板，不放可执行实现
- 真实cookie/token/storage不进仓库
- entry_url用Base64编码
- task artifact默认本地私有
- 共享前先做脱敏审查

---

## Pitfalls

- **跳过渲染验证**：API 返回掩码 ≠ 页面也掩码。SSR/diy.js 可能嵌入了完整数据。先看页面再分析代码，不走这一步就开始反混淆是浪费时间。
- 盲补环境：没有代理日志和first divergence就补宿主对象
- 过早提纯：env rebuild未通过就做纯算法提取
- 跳过Node直接Python：直接用execjs做补环境而非先在Node中验证
- 全量模拟：一次性补完整浏览器环境而非逐项回填
- 证据丢失：只把结论留聊天记录，不写入task artifact
- diff_env_requirements滥用：跳过代理日志直接依据diff补丁
- **跳过证据门禁**：未从真实样本确认目标请求就跳到定位
- **关键字全局搜索**（AP-L1）：看到sign/token就全局搜，不溯源initiator栈
- **盲堆patch**（AP-RT1）：不找first divergence就乱加mock
- **全量反编译**（AP-R1）：遇到混淆就解整个文件，不先确认边界
- **风控分支当摩擦删**（AP-RT2）：不分清debugger是纯摩擦还是风控分支

> 完整17条反模式清单见 [references/evidence-driven-workflow.md#反模式清单](references/evidence-driven-workflow.md#反模式清单17条)

---

## 技能分工

本技能是JS逆向领域的**总纲层**，编排6阶段工作流并协调子技能。

| 你需要的 | 应该用 |
|---------|--------|
| 完整逆向工作流（Observe→Capture→Rebuild→Patch→PureExtraction→Port） | → **本技能** (js-reverse-engineering) |
| CDP断点、单步追踪、callFrame求值、脚本替换 | → **cdp-debug-reverse** |
| 加密入口定位（静态搜索+XHR断点） | → **find-crypto-entry** |
| Webpack解包 | → **webpack-unpack** |
| AST反混淆、控制流平坦化还原、字符串数组解密 | → **ast-deobfuscation** |
| 反调试对抗（CDP层+JS层双层架构） | → **anti-debug** |
| 补环境、环境模拟、指纹固定、document.all、JsRpc替代 | → **env-patch** |
| 算法/协议逆向、6类题型、Python复现 | → **algorithm-reverse** |
| JSVMP/VMP逆向（数据驱动+AST反编译） | → **jsvmp-reverse** |
| 瑞数纯算逆向 | → **ruishu-reverse** |
| API协议逆向、端点发现、OpenAI兼容代理 | → **web-api-reverse-engineering** |
| **国密SM2/SM3/SM4检测**（现有工具覆盖不到） | → **jshook** (`node /opt/jshook-skill/dist/skill.js detect-crypto`) |
| **CryptoJS 全参数捕获（油猴注入）** | → **Hook_JS** (`/opt/hook-js/Hook_CryptoJS/Hook_CryptoJS.js`) |
| **国密 SM 运行时 Hook** | → **Hook_JS** (`/opt/hook-js/Hook_CryptoJS/Hook_smcrypto.js`) |
| **React 路由提取** | → **Hook_JS** (`/opt/hook-js/React/Get_React.js`) |
| **Vue 导航守卫清除** | → **Hook_JS** (`/opt/hook-js/vue/Clear_vue_Navigation_Guards.js`) |
| **Bypass Debugger 三合一方案**（eval+Function+constructor） | → **Hook_JS** (`/opt/hook-js/hook_debugger/Bypass_Debugger/Bypass_Debugger.js`) |
| **AntiDebug Breaker Chrome插件**（36脚本，反调试+加密Hook+网络Hook+Vue/React辅助） | → **AntiDebug_Breaker** (`/tmp/AntiDebug_Breaker/scripts/`) — Chrome商店安装或加载未打包 |
| **CryptoJS 全参数自动捕获**（key/iv/mode/padding/密文，apply Hook+特征检测） | → **AntiDebug_Breaker** (`scripts/Hook_CryptoJS.js`) — 无需库名，运行时自动识别 |
| **JSEncrypt RSA Hook**（公钥/私钥/明文/密文，call Hook+方法特征检测） | → **AntiDebug_Breaker** (`scripts/Hook_JSEncrypt.js`) |
| **SM-Crypto 国密Hook**（SM2/SM3/SM4，webpack拦截+测试向量验证） | → **AntiDebug_Breaker** (`scripts/Hook_SMcrypto.js`) |
| **iframe 逃逸防御**（Proxy拦截contentWindow，防iframe获取原生函数） | → **AntiDebug_Breaker** (`scripts/AntiAnti_Hook.js`) |
| **console只读保护**（Proxy冻结console.log/clear/table防覆盖） | → **AntiDebug_Breaker** (`scripts/hook_log.js`) |
| **页面跳转阻断**（onbeforeunload+debugger通杀跳转） | → **AntiDebug_Breaker** (`scripts/location_href.js`) |
| **事件断点（鼠标/键盘/WebSocket）** | → **jshook** (`event-breakpoint set-mouse/set-keyboard/set-timer`) |
| **Watch 表达式持久化监控** | → **jshook** (`watch add/list/evaluate/remove`) |
| **脚本黑盒化（跳过第三方库）** | → **jshook** (`blackbox set *jquery*.js`) |
| **DOM 按文本查找可点击元素** | → **jshook** (`dom clickable 登录`) |
| **缓存统计/数据清理** | → **jshook** (`stats` / `clear`)
| **jsjiami.com 加密产物解混淆** | → **ast-deobfuscation**（jsjiami 专项章节）|
| **jsjiami 域名锁定绕过** | → **anti-debug**（Anti-Tamper 章节）|
| **jsjiami 反调试/反Selenium** | → **anti-debug**（Anti-Selenium 章节）|
| **AAEncode/JSFuck 解码** | → **ast-deobfuscation**（AAEncode/JSFuck 专项解码）|

## 网络安全领域交叉引用

本技能与网络安全领域技能树(~/.hermes/skills/cybersecurity/)存在以下交叉点：

| 网络安全技能 | 交叉点 | 协作说明 |
|-------------|--------|---------|
| web-pentest | Web攻击面→API协议逆向 | web-pentest发现Web端点漏洞时，如需逆向JS加密逻辑转交本技能 |
| crypto-attacks | 密码学攻击→加密定位/算法还原 | crypto-attacks分析加密缺陷时，find-crypto-entry定位入口、algorithm-reverse还原算法 |
| binary-exploitation | 二进制VM利用→VMP保护逆向 | jsvmp-reverse的VMP逆向方法论与binary-exploitation的VM逃逸互通 |
| malware-analysis | 反分析→反调试/反混淆 | malware-analysis的反调试对抗与anti-debug方法论互通；恶意脚本解混淆→ast-deobfuscation |
| forensics-analysis | 取证→CDP协议调试 | cdp-debug-reverse的CDP调试能力可用于网络取证中的协议分析 |
| ctf-competition | CTF Web/Reverse→JS逆向工作流 | CTF中涉及JS逆向的题目直接使用本技能的6阶段工作流 |

---

## camoufox-workflow

# Camoufox Workflow — JS逆向工作流

## 硬约束 Checklist

启动技能后必须完成以下3项检查才能开始分析：

### CHECK-1: 环境自检
确认工具链状态（Node.js、Python、浏览器环境）。

### CHECK-2: 经验库速查
根据目标域名和特征关键词查找已有案例。**同时必须检查用户的 Gist 和仓库——用户有 23+ 私有 Gist 和多个仓库（如 steal 仓库）可能已经包含现成工具。**
- tiktok.com / X-Bogus / X-Gnarly → jsvmp-dual-sign 方案
- douyin.com / a_bogus → jsdom 环境伪装
- nmpa.gov.cn / RS 412 / sdenv → sdenv 纯 Node.js
- obfuscator.io → 通用四板斧
- **PyInstaller 打包的 Python 应用** → `strings` + `pyinstxtractor` + 反编译 `.pyc`
- **ChatGPT Web 协议** → `backend-api/` + `OpenAIBackendAPI` + PoW/Turnstile 绕过

**已吸收的外部仓库索引**（按优先级排序）：
- **715494637/reverse-skill** (242★) → 阶段门禁/证据驱动/L1-L4路由/反模式17条/请求链状态机/瑞数增强/6模板 → evidence-driven-workflow.md
- **0xsdeo/Hook_JS** (538★) → CryptoJS全参数Hook/国密SM/React路由/Vue守卫/三合一BypassDebugger → /opt/hook-js/ + anti-debug 增强
- **wuji66dde/jshook-skill** (210★) → 国密检测/事件断点/Watch表达式/脚本黑盒化/DOM文本定位 → /opt/jshook-skill/ + 工具链引用
- **zhizhuodemao/js-reverse-mcp** → 23工具CDP调试/反检测浏览器/断点/Hook/网络分析 → MCP 服务器配置
- **Fausto-404/js-reverse-automation--skill** (JSRPC) → 浏览器实时调用/7维度评分/Flask代理 → JSRPC 动态剥离法
- **P4nda0s/reverse-skills** → 8个逆向子技能（Frida/Unicorn/DEX/IL2CPP） → reverse-engineering-general
- **Kaliiiiiiiiii-Vinyzu/patchright** (3.4k★) → Playwright反检测分支，C++级patch移除navigator.webdriver，60+ stealth参数 → js-reverse-mcp 内核
- **Kaliiiiiiiiii-Vinyzu/patchright-nodejs** (702★) → patchright Node.js 原生绑定
- **ultrafunkamsterdam/undetected-chromedriver** (12.7k★) → Selenium反检测驱动，自动化绕过CF/DataDome等反爬
- **FlareSolverr/FlareSolverr** (14.1k★) → Docker代理服务，用真实浏览器绕过CF挑战页 + Turnstile验证
- **VeNoMouS/cloudscraper** (6.6k★) → Python模块，基于requests的CF IUAM页面绕过（仅限JS挑战）
- **sarperavci/CloudflareBypassForScraping** (2.4k★) → Cookie生成器 + 任意HTTP方法请求镜像
- **ZFC-Digital/puppeteer-real-browser** (1.6k★) → Puppeteer反检测，绕过CF/PerimeterX等
- **Zendriver/cdpdriver** (1.3k★) → Python CDP驱动，Playwright API风格但无WebDriver特征
- **NoahCardoza/CloudProxy** (571★) → 代理服务器自动处理CF验证
- **unixfox/pupflare** (443★) → Puppeteer CF挑战解决器
- **vvanglro/cf-clearance** (362★) → Python生成CF clearance cookie

**Turnstile/CAPTCHA Solver**:
- **Theyka/Turnstile-Solver** (817★) → Cloudflare Turnstile 自动求解
- **Jobians/cloudflare-turnstile-bypass** → Node.js + patchright Turnstile token获取
- **2captcha/2captcha-python** (757★) → 付费验证码打码服务API封装(reCAPTCHA/Turnstile/funcaptcha)
- **RiskByPass/riskbypass_demo** (213★) → 指纹对抗演示

**反检测浏览器**:
- **seleniumbase/SeleniumBase** (12.8k★) → 增强版Selenium，UC模式内置反检测
- **autoscrape-labs/pydoll** (6.9k★) → 无CDP/无WebDriver特征的浏览器自动化
- **omkarcloud/botasaurus** (4.7k★) → 爬虫框架，内置反检测+代理轮换
- **Virtual-Browser/VirtualBrowser** (2.9k★) → 虚拟浏览器指纹
- **adryfish/fingerprint-chromium** (2.6k★) → 浏览器指纹随机化
- **botswin/BotBrowser** (2.5k★) → 反检测浏览器，C++级patch
- **vibheksoni/stealth-browser-mcp** (673★) → MCP stealth浏览器，绕过CF

**中文生态 CF 绕过工具**:
- **g1879/DrissionPage** (12.1k★) → 无需WebDriver的浏览器自动化，绕过CF检测

吸收流程见 **规则五**。

### CHECK-3: 确认工作流阶段
选择当前所处阶段。任务完成后进入**成果吸收阶段**。

### CHECK-4: 任务完成后必做
完成任务或吸收外部仓库后，执行**规则五**（扫描→分类注入→更新总纲→更新经验库→持久化）。

## 执行范式：双脑异步协作（Akino-CodeBuddy）

> 这是用户的**核心工作流**，适用于所有逆向工程任务，不限于JS逆向。

### 核心原则

| 左脑（规划者） | 右脑（执行者） |
|---------------|---------------|
| 架构师·分析师·品控官 | 工程师·实现者·执行者 |
| **不直接编码实现** | **不跳过方案直接开干** |
| 写方案 → 写盘 → 启动后台 | 读方案 → 编码 → 自动通知 |
| 收到通知 → 品控审查 → 吸收 | 完成后 notify_on_complete |

### 执行规则

**规则一：先分析再动手**
每个 RE 任务到达时，先回答三个问题再写一行代码：
1. 真正要逆向的是什么？（算法/协议/App？）
2. 有没有现成方案？（经验库速查 + 已有技能树）
3. 影响范围多大？（单点破解 vs 通用方案？）

**规则二：异步优先，不阻塞**
编码类任务永远后台启动（`background=true, notify_on_complete=true`），不阻塞分析流程：
```
写方案 write_file("/tmp/ref.md")
  → terminal(command="codebuddy -p -y '实现...参考/tmp/ref.md'", background=true, notify_on_complete=true)
  → [继续分析/处理其他任务]
  → 收到通知 → 品控审查 → 成果吸收
```

**规则三：煮沸湖泊**
当完整实现只比90%版本多花几分钟时，选完整版。
- ✅ 模块100%测试覆盖、所有边界情况、完整错误路径
- ❌ 选方案B说"少写代码，覆盖90%" — 如果方案A只多70行，选方案A

**规则四：先查后建**
每个新任务开始前，先搜索记忆和技能库。如果是常见问题，直接用已有方案。
不搜索的代价是重新发明一个更差的东西。

**规则五：成果自动吸收 — 每次任务/吸收后必做

每次任务完成后（或外部仓库吸收后），必须执行以下步骤：

1. **扫描成果**
   - 新发现的工具/脚本 → 安装到 `/opt/` 并记录路径
   - 新方法论/反模式 → 写入 `js-reverse-engineering/references/`
   - 新工作流模式 → 更新 `camoufox-workflow` 或对应技能
   - 新配置/知识 → 记忆沉淀

2. **分类注入**（3选1）
   - 工具链（CLI/脚本） → `camoufox-workflow` 补充工具链章节
   - 方法论/流程 → `js-reverse-engineering` references/
   - 反调试/加密等具体能力 → 对应子技能（anti-debug/find-crypto-entry 等）

3. **更新总纲** → `js-reverse-engineering` 的技能分工表 + 工具选择表
4. **更新经验库** → `CHECK-2` 的速查表（新增已吸收仓库的摘要索引）
5. **持久化** → 记忆 + 通知用户吸收摘要

**煮沸湖泊原则在此同样适用**：吸收时做完整对比（功能差异表），不只是加一行链接。

### 反向注入：CodeBuddy 搜索 → 爱马仕执行

当逆向任务需要网络搜索收集资料时，反向用 CodeBuddy 做搜索：
```
1. Akino 定义搜索目标（什么知识需要收集）
2. terminal(command="codebuddy -p -y '网络搜索xxx信息，整理为结构化的知识文档写盘到/tmp/xxx.md'", background=true, notify_on_complete=true)
3. [收到通知] → 读取搜索结果 → Akino 分析提炼 → 写入技能
```

## 6阶段工作流

### Phase 0: 任务归一化
- 锁定目标站点、目标对象、成功标准
- 确认至少一个可观察样本
- 输出：任务分析文档写盘到 `/tmp/`

### Phase 1: 证据采集
- 打开浏览器手动触发目标操作
- **先找 Web 版 JS bundle 分析**（如有 Web 版）：
  - 下载 JS bundle 搜索 API 端点、签名密钥、认证参数
  - 与 App 抓包结果交叉验证
- 捕获完整请求链（上下游请求）
- 区分正常态与风控态样本
- 输出：请求链路记录 + 样本包

### Phase 2: 定位
- 断点定位加密点
- 调用栈回溯（writer → builder → entry → source）
- 确认写入边界、触发动作、上游依赖
- Hook 关键函数
- **Sign 签名快速定位**（从 jsjiami 文章吸收）：
  1. Chrome Network 面板搜索 `sign` / `signature` / `_sign`
  2. XHR Breakpoints 断点拦截目标请求
  3. 提取加密代码到本地独立运行
  4. 分析：参数字典排序 → 拼接 → 哈希算法

### Phase 3: 源码分析（恢复）
- 混淆识别
- AST 解混淆
- 算法逻辑提取
- 只恢复与已证边界相连的切片

### Phase 4: 动态验证（运行时）
- 补环境运行
- 参数输出比对
- 逐个检查点对齐，从first divergence修复
- 边界测试

### Phase 5: 算法还原（纯提取）
- Python/Node 复现
- 输入输出一致性验证

### Phase 6: 验证交付
- 多轮测试（中间态+最终态双对比）
- 文档产出
- 成果吸收（自动进化协议）

> ⚠️ **阶段门禁**：每个阶段有明确退出条件才能进入下一阶段。跳到下阶段前必须确认当前阶段的必交付物已完成。详情见 `js-reverse-engineering/references/evidence-driven-workflow.md`
>
> **复杂度分级**：开始任务前先评估 L1-L4，选择最短路由路径。低复杂度任务不必走完所有阶段。

---

## 补充工具链: jshook-skill

jshook-skill 是与 JSReverser-MCP 互补的 Node.js CLI 工具链，提供现有工具未覆盖的独特能力。安装路径: `/opt/jshook-skill/`，调用方式: `node /opt/jshook-skill/dist/skill.js <command>`。

### 什么时候用 jshook 替代 JSReverser-MCP

| 场景 | 推荐工具 | 原因 |
|------|---------|------|
| 标准 Hook/断点/XHR 中断 | JSReverser-MCP | 工具更丰富，MCP 协议集成更好 |
| 国密 SM2/SM3/SM4 检测 | **jshook** | 内置 `sm-crypto` 支持 |
| 抖音 X-Bogus 分析 | **jshook** | 内置 `xbogus` 包 |
| 事件断点（鼠标/键盘/WebSocket） | **jshook** | JSReverser-MCP 仅有 XHR 断点 |
| Watch 表达式持久化监控 | **jshook** | `watch add/list/evaluate/export/import` |
| 脚本黑盒化（忽略库文件） | **jshook** | `blackbox set/remove/list` 跳过第三方库 |
| DOM 按文本找可点击元素 | **jshook** | `dom clickable 登录` 比 MCP 的 `find_clickable_elements` 更强 |
| 缓存/数据管理 & 统计 | **jshook** | `stats` / `clear` 查看缓存命中率 |
| 反检测平台预设 | 都可 | jshook 5种预设，JSReverser-MCP 也有类似 |
| CDP 深度调试 | JSReverser-MCP | 调用帧、作用域变量、条件断点更好 |

### jshook 独有工具速查

```bash
# 国密检测（new!）
node /opt/jshook-skill/dist/skill.js detect-crypto "<code>"

# 事件断点（new!）
# 鼠标事件断点
event-breakpoint set-mouse
# 键盘事件断点
event-breakpoint set-keyboard
# 定时器断点
event-breakpoint set-timer

# Watch 表达式（new!）
watch add "window.location.href" "当前URL"
watch list
watch evaluate
watch remove <id>

# 脚本黑盒化（new!）
blackbox set *jquery*.js
blackbox set-common    # 黑盒化常用库
blackbox list

# DOM 按文本查找可点击元素（增强）
dom clickable 登录     # 按文本定位按钮
dom clickable "提交订单"

# 缓存统计
stats
stats --type=cache
clear                 # 清除所有数据
```

### jshook 标准逆向工作流增强

在 Phase 2-4 中，当遇到 JSReverser-MCP 工具链无法覆盖的场景时，切换到 jshook:

```
Phase 2 增强:
  # 如果 detect_crypto 无结果 → 用 jshook 的 sm-crypto 检测国密
  node /opt/jshook-skill/dist/skill.js detect-crypto "<code>"
  
  # 如果 XHR 断点不够 → 用 event-breakpoint 补事件断点
  node /opt/jshook-skill/dist/skill.js xhr-breakpoint set */api/*
  node /opt/jshook-skill/dist/skill.js event-breakpoint set-mouse

Phase 4 增强:
  # 需要持续监控表达式变化 → 用 watch
  node /opt/jshook-skill/dist/skill.js watch add "signData" "签名结果"
  node /opt/jshook-skill/dist/skill.js watch evaluate

  # 脚本太多干扰调试 → 黑盒化第三方库
  node /opt/jshook-skill/dist/skill.js blackbox set *vendor*.js

  # 反检测 → 使用预设
  node /opt/jshook-skill/dist/skill.js stealth inject-preset windows-chrome
```

---

## 补充油猴 Hook 脚本集: Hook_JS

538 星油猴 Hook 脚本合集，来自 [0xsdeo/Hook_JS](https://github.com/0xsdeo/Hook_JS)。安装路径: `/opt/hook-js/`。

这些是**直接在浏览器中注入**的油猴脚本（Tampermonkey `document-start`），和 JSReverser-MCP 的 MCP 协议 Hook 互补。

### 什么时候用 Hook_JS 脚本

| 场景 | 直接打开油猴装对应脚本 |
|------|----------------------|
| 需要捕获 CryptoJS 全算法参数（key/iv/mode/padding） | `Hook_CryptoJS/Hook_CryptoJS.js` |
| 需要捕获国密 SM2/SM3/SM4 调用参数 | `Hook_CryptoJS/Hook_smcrypto.js` |
| 需要提取 React SPA 路由表 | `React/Get_React.js` |
| Vue 导航守卫阻挡导致页面无法正常操作 | `vue/Clear_vue_Navigation_Guards.js` |
| 需要捕获 Webpack 模块导出并注入执行 | `测试/模块导出提取注入.js` |
| eval/new Function/constructor 无限 debugger | `hook_debugger/Bypass_Debugger/Bypass_Debugger.js` |
| 需要 Hook XHR/Fetch 请求参数+堆栈 | `Hook_xhr/Hook_xhr.js` / `Hook_fetch.js` |
| 需要 Hook cookie 设置 | `Hook_cookie/Hook_cookie v0.2.js` |
| 需要 Hook JSON.parse/stringify 内容+堆栈 | `hook_JSON.js` |
| 需要冻结 window size 防指纹检测 | `实用小脚本/Fixed_window_size.js` |
| 需要绕过格式化检测 | `实用小脚本/过格式化检测.js` |
| 需要 Hook localStorage/sessionStorage | `hook_window/hook_localStorage.js` |

### Hook_JS 脚本与 JSReverser-MCP 的区别

| 维度 | JSReverser-MCP | Hook_JS 油猴脚本 |
|------|---------------|-----------------|
| 注入方式 | CDP 协议注入（AI 控制） | 油猴自动注入（浏览器级） |
| 可见性 | 可能被站点反调试检测到 CDP | 油猴注入对站点不可见（不触发 CDP 检测） |
| 控制权 | AI 通过 MCP 工具可动态启停 | 脚本自动运行，不能远程控制 |
| 堆栈信息 | 通过 CDP callFrame 获得 | 通过 `new Error().stack` 打印 |
| 参数捕获 | 需要在断点或 hook_function 中主动查看 | 自动打印参数和堆栈到控制台 |
| 适用场景 | 深度调试、断点分析 | 快速捕获、避免 CDP 反检测 |

### 关键脚本说明

**Hook_CryptoJS.js**: Hook CryptoJS 所有对称加密（AES/DES/TripleDES/Rabbit/RC4/RC4Drop）+ 哈希（MD5/SHA1/SHA256/SHA512）+ HMAC。自动打印：ciphertext、key、iv、algorithm、mode、padding、blockSize。如果解密时未获取到运算模式/填充方式，配合 Fuzz_Crypto_Algorithms 使用（https://github.com/0xsdeo/Fuzz_Crypto_Algorithms）。

**Hook_smcrypto.js**: Hook 国密 sm-crypto 库的 SM2/SM3/SM4 调用。SM2 捕获：公钥/私钥、加密/解密参数、签名/验签参数。SM3 捕获：输入输出。SM4 捕获：key、加密/解密参数。

**Get_React.js**: 通过 DOM 监控自动提取 React Router 路由表。使用 `window.__REACT_ROUTES__` 获取完整路由列表。支持 React Router v6+。

**Clear_vue_Navigation_Guards.js**: Hook `Array.prototype.push` 拦截 Vue 路由守卫注册，打印设置守卫的堆栈，同时清除全局前置守卫和全局解析守卫。

**模块导出提取注入.js**: 对 Webpack 打包的模块，先提取 export 语句，然后创建 import 模块在页面中执行，打印所有导出内容。用于还原 Webpack 模块的导出函数。

**Bypass_Debugger.js**: 三合一 debugger 绕过方案 —— 同时 Hook eval、new Function、constructor 三种注入方式。用 `replaceAll(/debugger/g, '')` 清除所有 debugger 语句，同时修复 toString 返回值防止检测。

**Fixed_window_size.js**: 固定 `window.innerHeight` 和 `window.innerWidth` 返回值，防指纹检测。默认值可自行调整。

## JSVMP 双路径分析

### 路径A: 四板斧（轻量，优先）
1. 数组解混淆
2. 常量折叠
3. 死代码删除
4. 控制流平坦化还原

### 路径B: 环境仿真（重量，路径A无效时）
- jsdom 环境伪装（喂入-截出）
- Firefox + playwright 真实浏览器
- sdenv 纯 Node.js

## JSRPC 动态剥离法（从 Fausto-404/js-reverse-automation 吸收）

### 核心思想
不补环境、不还原算法、不反混淆——直接连真实浏览器调加密函数。

### 什么时候用 JSRPC 替代补环境

| 传统做法 | JSRPC 做法 | 选择依据 |
|---------|-----------|---------|
| 补环境 (env-patch) | JSRPC WebSocket 调用 | 如果反调试太多/环境检测太复杂 → JSRPC |
| AST 反混淆 (ast-deobfuscation) | 直接调用真实浏览器中的函数 | 如果是 VMP/动态代码 → JSRPC |
| 算法还原 (algorithm-reverse) | 让浏览器算，Python 收结果 | 如果算法链条太长 → JSRPC |
| 定位加密入口 (find-crypto-entry) | Chrome DevTools MCP 自动发现 | 如果入口在闭包/Webpack 中 → CDP |

### JSRPC 方案全景

```
┌── 用户 ──────────────────────────────────────────┐
│  输入: Target URL + Parameters To Analyze          │
└──────────────────┬───────────────────────────────┘
                   ▼
┌── Chrome DevTools MCP ───────────────────────────┐
│  ● navigate_page(initScript) 预注入 Hook 探针     │
│  ● evaluate_script 后注入                        │
│  ● 运行时 Hook: fetch/XHR/crypto/JSON.stringify   │
│  ● Webpack module cache 捕获                     │
│  ● 7 维度候选评分                                 │
│  ● 真实样本验证                                   │
└──────────────────┬───────────────────────────────┘
                   ▼
┌── JSRPC (WsRpc/Hlclient) ───────────────────────┐
│  ● 浏览器中注册加密函数为 WebSocket handler       │
│  ● Python 通过 WebSocket 调用                    │
│  ● 实时返回值                                   │
│  ● 无需补环境、无需理解算法细节                    │
└──────────────────┬───────────────────────────────┘
                   ▼
┌── Python Flask Proxy ────────────────────────────┐
│  ● /encode — 接收请求 → 调 JSRPC → 返回加密结果  │
│  ● /decode — 解密（如果有）                      │
│  ● 对接 Burp autoDecoder                          │
└──────────────────┬───────────────────────────────┘
                   ▼
              Burp Suite ←→ autoDecoder ←→ Flask Proxy
```

### 运行时 Hook 探针（7 维度评分）

| 维度 | 说明 | 分值 |
|------|------|------|
| name_score | 函数名包含 encrypt/sign/rsa/aes 等关键词 | 0-1.0 |
| source_keyword_score | 源码包含加密库调用 | 0-1.0 |
| runtime_stack_score | 运行时调用栈匹配目标请求 | 0-1.0 |
| request_correlation_score | 请求 body 出现函数名或返回值 | 0-0.8 |
| input_output_shape_score | 输入/输出符合加密特征 | 0-0.9 |
| module_export_score | Webpack 模块导出的函数 | 0-0.7 |
| verification_score | 真实样本验证通过 | 0-1.0 |

**候选验证**: 评分 > 0.6 的候选，用真实样本调用验证

### 引用工具
- JsRpc: https://github.com/jxhczhl/JsRpc
- autoDecoder: https://github.com/f0ng/autoDecoder
- chrome-devtools-mcp: https://github.com/ChromeDevTools/chrome-devtools-mcp/

---

## 🔬 逆向原理 — 理解底层机理

用户铁律：「要懂得原理」— 每个方法输出时必须附带原理说明。

### 1. 为什么字符串常量在各种反编译中都是最高效的入口？

| 技术栈 | 编译器行为 | 原因 |
|--------|-----------|------|
| Flutter/Dart AOT | `.rodata` 段保留所有字符串 | Dart 混淆器只重命名符号，不动常量池 |
| Go (Wails embed.FS) | 前端 JS 以明文写入 `.rodata` | `go:embed` 不做压缩或加密 |
| Webpack/Vite | bundle 保留全部字面量 | JS 打包器无内置字符串混淆 |
| PyInstaller | `.pyc` 的 `co_consts` 含所有字面量 | Python 字节码必须保留常量 |

**公理**: 无论什么技术栈，字符串常量永远是攻击者最容易提取的信息。

### 2. 为什么签名算法一定在客户端？

架构约束：若签名在服务端计算，用户密码须先明文传给服务端（HTTPS 终止后处理），存在中间人风险。所以签名只能由客户端算。密钥/盐必然在客户端某处，不存在「密钥在客户端但不可提取」的安全模型。

### 3. 为什么 bootstrap 接口不需要 Token？

客户端首次启动时不可能有 token（登录在初始化之后）。bootstrap 预设无 token 可用。每个 App 都有类似端点（bootstrap/init/guest/preload/setup）。

### 4. 为什么 AES 加密数据熵值 ≈ 8.0？

AES 产物位分布均匀 → 每字节 256 种可能 → 信息熵 8 bits/byte。JPEG/PNG 熵值 4-7（自然图像局部相关性）。**鉴别公式**：熵值 ≈ 8.0 + `file` 说 `data` → 加密。

### 5. 为什么 Wails 二进制原地 patch 不崩溃？

`go:embed` 写入 `.rodata`，该段存的是**只读数据引用**，不是可执行指令。替换同长度字符串不改变段长度 → Mach-O 符号表/重定位不受影响。adhoc 签名重新计算 hash。**边界**：有 checksum 校验的 App 需先 patch 校验函数。

### 6. 为什么 CSR 页面 curl 拿不到内容？

CSR 渲染：服务端只返骨架 HTML。浏览器执行 JS bundle 后 Vue 动态填充 DOM。**结论**：CSR 站点直接找 API endpoint 或走浏览器渲染。

---

## find-crypto-entry

1|---
2|name: find-crypto-entry
3|description: 定位加密参数生成入口技能 — 从最终请求/响应倒推加密函数在代码中的精确位置和调用链。5种题型对应的定位策略，从时间戳到Obfuscator/VMP。
4|author: 7452323 (converted from Private Gist)
5|tags:
6|  - js-reverse
7|  - crypto-entry
8|  - signature
9|  - call-stack
10|---
11|
12|# Find Crypto Entry — 定位加密参数生成入口
13|
14|## 5种题型入口定位策略
15|
16|| 题型 | 特征 | 定位策略 | 定位时间 |
17||------|------|----------|----------|
18|| 时间戳/随机数 | 参数看起来像时间戳 | 搜索时间戳生成代码 | ~5分钟 |
19|| 简单函数调用 | 参数来自某函数返回值 | 打点搜索 | ~15分钟 |
20|| 中等混淆 | 函数名/变量名被混淆 | AST解混淆后搜索 | ~30分钟 |
21|| 控制流平坦化 | switch-case 迷宫 | 控制流还原后定位 | ~1h |
22|| VMP 虚拟机 | 字符串表+虚拟机执行 | 数据流追踪 | ~数小时 |
23|
24|## 定位方法论
25|
26|### 从请求倒推
27|```
28|最终请求的 URL/Header/Body
29|→ 搜索关键字（参数名/路径/特征字符串）
30|→ 从搜索结果回溯调用链
31|→ 找到写出点（setRequestHeader / append / 直接赋值）
32|```
33|
34|### Hook 关键函数
35|```javascript
36|// Hook XMLHttpRequest
37|var originalOpen = XMLHttpRequest.prototype.open;
38|XMLHttpRequest.prototype.open = function() {
39|    console.log('open:', arguments);
40|    return originalOpen.apply(this, arguments);
41|};
42|
43|// Hook Cookie
44|Object.defineProperty(document, 'cookie', {
45|    set: function(val) {
46|        debugger;  // 断点捕获
47|        return val;
48|    }
49|});
50|```
51|
52|## 协作链
53|
54|`find-crypto-entry → algorithm-reverse → Python复现`
55|
56|找到入口后转交 algorithm-reverse 进行算法还原。
57|

## 实战提炼：加密参数入口定位通用框架

### 从 ONE App、chatgpt2api、HttpCall 中提炼

### 全场景入口定位矩阵

| 场景 | 技术栈 | 入口位置 | 定位方法 |
|------|--------|---------|---------|
| Flutter App (ONE) | Dart/Blutter | `libapp.so` 构造函数 | 搜索 `http`/`aes`/`sign` → 找 `app_container.dart` |
| Web SPA (chatgpt2api) | JS + PoW | JS bundle 或 service worker | 搜索 `sign`/`token`/`proof` → 找计算函数 |
| Wails 桌面 (HttpCall) | Go + WebView2/WKWebView | Go binary 中的前端资源 | `strings` → `grep` AI 相关 → 提取嵌入 HTML/JS |
| iOS 原生 | ObjC/Swift + CFNetwork | `__TEXT.__cstring` | `strings` → `grep API_KEY/secret/baseURL` |
| Android 原生 | Java/Kotlin + OkHttp | smali 或 JNI SO | jadx 搜索 `encrypt`/`sign` → 追调用链 |
| PyInstaller | Python → .pyc | 打包的 .pyc 文件 | 反编译后搜 `requests`/`api`/`hashlib` |

### 4 种入口类型和战场策略

| 入口类型 | 特征 | 最佳突破口 | 优先级 |
|---------|------|-----------|--------|
| **构造函数常量** | Key/IV/Salt/URL 在类初始化时赋值 | `strings` 搜索 | ⭐ 最高，最可靠 |
| **网络层拦截器** | OkHttp Interceptor / URLSession delegate | 搜索 `header`/`intercept` | ⭐ 高 |
| **加密工具类** | 独立的 `encrypt`/`decrypt`/`sign` 函数 | 搜索 `aes`/`md5`/`hmac` | ⭐ 高 |
| **运行时动态计算** | 使用 JNI/CDP/Wasm 计算 | 断点/Hook | 中等，需要动态分析 |

### 快速定位决策树

```
遇到加密参数入口问题？
├── 有 APK/二进制？
│   ├── Flutter → Blutter → 搜构造函数
│   ├── Java/Android → jadx → 搜 encrypt/sign
│   └── PyInstaller → pyinstxtractor → 反编译 .pyc
├── 有 Web 端？
│   ├── SPA → 搜 JS bundle → 搜 sign/encrypt
│   ├── Flutter Web → main.dart.js → 搜字符串常量
│   └── Wails → strings 二进制 → 搜嵌入前端资源
├── 有 HAR 抓包？
│   └── 对比 sign 值 → 穷举签名算法
└── 什么都有？
    └── 看响应解密：截获响应→试已知 Key 解密→区分加密类型
```

---

## js-reverse-mcp-integration

# JS Reverse MCP

English | [中文](README_zh.md)

A JavaScript reverse engineering MCP server that enables AI coding assistants (Claude, Cursor, Copilot) to debug and analyze JavaScript code in web pages.

Built on the [Patchright](https://github.com/nicecaesar/patchright) anti-detection engine with multi-layered anti-bot bypass capabilities, allowing it to work on sites with bot detection such as Zhihu and Google.

## Features

- **Anti-detection browser**: Based on Patchright (Playwright anti-detection fork), 60+ stealth launch arguments, bypasses mainstream anti-bot systems
- **Script analysis**: List all loaded JS scripts, search code, get/save source code
- **Breakpoint debugging**: Set/remove breakpoints, conditional breakpoints, precise positioning in minified code
- **Function tracing**: Trace any function (including module-internal functions) via logpoints
- **Execution control**: Pause/resume execution, step debugging (over/into/out) with source context
- **Runtime inspection**: Evaluate expressions at breakpoints, inspect scope variables
- **Network analysis**: View request initiator call stacks, set XHR breakpoints, WebSocket message analysis
- **Script injection**: Inject scripts that run before page load for interception and instrumentation

## Requirements

- [Node.js](https://nodejs.org/) v20.19 or later
- [Chrome](https://www.google.com/chrome/) stable

## Quick Start (npx)

No installation required. Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "js-reverse": {
      "command": "npx",
      "args": ["js-reverse-mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add js-reverse npx js-reverse-mcp
```

### Codex

```bash
codex mcp add js-reverse -- npx js-reverse-mcp
```

### Cursor

Go to `Cursor Settings` -> `MCP` -> `New MCP Server`, and use the configuration above.

### VS Code Copilot

```bash
code --add-mcp '{"name":"js-reverse","command":"npx","args":["js-reverse-mcp"]}'
```

## Local Installation (Alternative)

```bash
git clone https://github.com/zhizhuodemao/js-reverse-mcp.git
cd js-reverse-mcp
npm install
npm run build
```

Then use local path in your MCP configuration:

```json
{
  "mcpServers": {
    "js-reverse": {
      "command": "node",
      "args": ["/path/to/js-reverse-mcp/build/src/index.js"]
    }
  }
}
```

## Anti-Detection

js-reverse-mcp includes multi-layered anti-detection measures to work on sites with bot detection:

### Anti-Detection Architecture

| Layer | Description |
|-------|-------------|
| Patchright Engine | C++ level anti-detection patches, removes `navigator.webdriver`, avoids `Runtime.enable` leaks |
| 60+ Stealth Args | Removes automation signatures, bypasses headless detection, GPU/network/behavior fingerprint spoofing |
| Harmful Args Removal | Excludes `--enable-automation` and 4 other default Playwright arguments |
| Silent CDP Navigation | Navigation tools don't activate CDP domains, captures requests only through Playwright-level listeners, preventing anti-bot scripts from detecting debugging protocol activity |
| Google Referer Spoofing | All navigations automatically include `referer: https://www.google.com/` |
| Persistent Login State | Uses persistent user-data-dir by default, login state preserved across sessions |

## Tools (23)

### Page & Navigation

| Tool              | Description                                                    |
| ----------------- | -------------------------------------------------------------- |
| `select_page`     | List open pages, or select one by index as debugging context   |
| `new_page`        | Create a new page and navigate to URL                          |
| `navigate_page`   | Navigate, go back, forward, or reload                          |
| `select_frame`    | List all frames (iframes), or select one as execution context  |
| `take_screenshot` | Take a page screenshot                                         |

### Script Analysis

| Tool                | Description                                                    |
| ------------------- | -------------------------------------------------------------- |
| `list_scripts`      | List all JavaScript scripts loaded in the page                 |
| `get_script_source` | Get script source snippet by line range or character offset    |
| `save_script_source`| Save full script source to a local file (for large/minified/WASM files) |
| `search_in_sources` | Search for strings or regex patterns across all scripts        |

### Breakpoint & Execution Control

| Tool                     | Description                                                |
| ------------------------ | ---------------------------------------------------------- |
| `set_breakpoint_on_text` | Set breakpoint by searching code text (works with minified code) |
| `break_on_xhr`           | Set XHR/Fetch breakpoint by URL pattern                    |
| `remove_breakpoint`      | Remove breakpoint(s) by ID, URL, or all; auto-resumes     |
| `list_breakpoints`       | List all active breakpoints                                |
| `get_paused_info`        | Get paused state, call stack and scope variables           |
| `pause_or_resume`        | Toggle pause/resume execution                              |
| `step`                   | Step over, into, or out with source context in response    |

### Function Tracing & Injection

| Tool                | Description                                                           |
| ------------------- | --------------------------------------------------------------------- |
| `trace_function`    | Trace any function call (including bundled internals) via logpoints   |
| `inject_before_load`| Inject or remove a script that runs before page load                  |

### Network & WebSocket

| Tool                     | Description                                    |
| ------------------------ | ---------------------------------------------- |
| `list_network_requests`  | List network requests, or get one by reqid     |
| `get_request_initiator`  | Get JavaScript call stack for a network request|
| `get_websocket_messages` | List WebSocket connections, analyze messages, or get message details |

### Inspection

| Tool                    | Description                                    |
| ----------------------- | ---------------------------------------------- |
| `evaluate_script`       | Execute JavaScript in the page (supports paused context, main world, and saving results/binary data to file) |
| `list_console_messages` | List console messages, or get one by msgid     |

## Usage Examples

### Basic JS Reverse Engineering Workflow

1. **Open the target page**

```
Open https://example.com and list all loaded JS scripts
```

2. **Find target functions**

```
Search all scripts for code containing "encrypt"
```

3. **Set breakpoints**

```
Set a breakpoint at the entry of the encryption function
```

4. **Trigger and analyze**

```
Trigger an action on the page, then inspect arguments, call stack and scope variables when the breakpoint hits
```

### Trace Module-Internal Functions

```
Use trace_function to trace the webpack-bundled internal function "encryptData",
view arguments of each call without setting breakpoints
```

### WebSocket Protocol Analysis

```
List WebSocket connections, analyze message patterns, view messages of specific types
```

## Configuration Options

| Option                 | Description                                | Default    |
| ---------------------- | ------------------------------------------ | ---------- |
| `--browserUrl, -u`     | Connect to a running Chrome instance       | -          |
| `--wsEndpoint, -w`     | WebSocket endpoint connection              | -          |
| `--headless`           | Run in headless mode                       | false      |
| `--executablePath, -e` | Custom Chrome executable path              | -          |
| `--isolated`           | Use temporary user data directory (fresh each time) | false |
| `--channel`            | Chrome channel: stable, canary, beta, dev  | stable     |
| `--viewport`           | Initial viewport size, e.g. `1280x720`    | real size  |
| `--hideCanvas`         | Enable Canvas fingerprint noise            | false      |
| `--blockWebrtc`        | Block WebRTC to prevent real IP leaks      | false      |
| `--disableWebgl`       | Disable WebGL to prevent GPU fingerprinting | false     |
| `--noStealth`          | Disable stealth launch arguments (for debugging) | false |
| `--proxyServer`        | Proxy server configuration                 | -          |
| `--logFile`            | Debug log file path                        | -          |

### Example Configurations

**Enhanced anti-detection (Canvas noise + WebRTC blocking):**

```json
{
  "mcpServers": {
    "js-reverse": {
      "command": "npx",
      "args": [
        "js-reverse-mcp",
        "--hideCanvas",
        "--blockWebrtc"
      ]
    }
  }
}
```

**Isolated mode (no persistent login, fresh profile each time):**

```json
{
  "mcpServers": {
    "js-reverse": {
      "command": "npx",
      "args": [
        "js-reverse-mcp",
        "--isolated"
      ]
    }
  }
}
```

### Connect to a Running Chrome Instance

1. Launch Chrome (close all Chrome windows first, then restart):

**macOS**

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

**Windows**

```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\chrome-debug"
```

2. Configure MCP connection:

```json
{
  "mcpServers": {
    "js-reverse": {
      "command": "npx",
      "args": [
        "js-reverse-mcp",
        "--browser-url=http://127.0.0.1:9222"
      ]
    }
  }
}
```

## Troubleshooting

### Blocked by Anti-Bot Systems

If you are blocked when visiting certain sites (e.g. Zhihu returning error 40362):

1. **Clear the contaminated profile**: Delete the `~/.cache/chrome-devtools-mcp/chrome-profile` directory
2. **Use isolated mode**: Add the `--isolated` flag
3. **Enable Canvas noise**: Add the `--hideCanvas` flag

## Security Notice

This tool exposes browser content to MCP clients, allowing inspection, debugging, and modification of any data in the browser. Do not use it on pages containing sensitive information.

## License

Apache-2.0

---

## jsrpc-auto-reverse

# JSRPC Auto Reverse — JSRPC 全自动 JS 逆向方案

## 核心哲学
**不补环境、不还原算法、不反混淆**——直接连真实浏览器调加密函数。

## 适用场景
- 登录参数加密（RSA/AES/SM2/SM4/MD5/自定义编码）
- 数据爬取时响应内容加密
- 请求签名（sign/token/enc）
- 需要与 Burp 配合进行抓包、改包

## 体系架构

```
┌── 用户输入 ────────────────────────────────────────┐
│  Target URL: https://xxx.com/login                 │
│  Parameters: password                              │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 0: 输入校验 ──────────────────────────────┐
│  check_inputs.py → phase0_input.json               │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 1: 浏览器连接 + 请求复现 ─────────────────┐
│  Chrome DevTools MCP:                              │
│  ● navigate_page(initScript=运行时Hook探针)         │
│  ● 打开目标页面 → 触发目标动作 → 捕获网络请求       │
│  ● 锁定目标请求 URL/Method/Body/Headers            │
│  ● 运行时健康检测: probe_status                    │
│     ok → 正常 | partial → 标记 | timeout → 降级     │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 2: 加密入口发现 ──────────────────────────┐
│  ● 运行时 Hook 探针捕获 fetch/XHR/crypto 调用      │
│  ● 7 维度评分系统筛选候选函数                       │
│  ● 真实样本验证（评分 > 0.6 的候选）                │
│  ● 输出: encryption_candidates.json                 │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 2.5: Webpack 模块解析（可选） ────────────┐
│  优先级链（不跳级）:                                │
│  1. window.__webpack_require__                     │
│  2. webpackChunk* push hook                        │
│  3. require.c 遍历已加载模块                        │
│  4. 离线解析 chunk factory（标记 low confidence）   │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 3: 依赖提取 ──────────────────────────────┐
│  ● call_signature: args/returns/async              │
│  ● runtime: bind_this/bootstrap/globals            │
│  ● 输出: analysis_result.json                       │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 4: 代码生成 ──────────────────────────────┐
│  ├── jsrpc_inject.js — JSRPC 浏览器端注入代码       │
│  ├── flask_proxy.py — Flask 本地代理服务            │
│  └── burp-autodecoder.md — Burp 配置文档            │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 5: 浏览器注入 ────────────────────────────┐
│  ● 刷新页面清理旧 WebSocket                         │
│  ● 注入 Hlclient (JsEnv_Dev.js)                    │
│  ● inject jsrpc_inject.js → 注册加密函数           │
│  ● 验证: curl /list 确认 group 已注册               │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 6: 启动服务 ──────────────────────────────┐
│  ├── JSRPC 服务: ws://127.0.0.1:12080              │
│  └── Flask 代理: http://127.0.0.1:xxx/encode       │
└─────────────────────┬─────────────────────────────┘
                      ▼
┌── Phase 7: Burp 配置 ────────────────────────────┐
│  ● autoDecoder URL → Flask 代理                    │
│  ● 配置 encode/decode 方向                         │
│  ● 联调验证                                       │
└─────────────────────┬─────────────────────────────┘
                      ▼
              ✅ 全链路打通，Burp 自动解密/加密
```

## 核心组件

### 1. 运行时 Hook 探针 (emit_runtime_hook_probe.py)

预注入到页面的 JS 探针，在所有 JS 执行前安装 Hook：

```javascript
(function() {
  // 避免重复安装
  if (window.__JSRA_TRACE__) return;
  
  var TRACE = { requests: [], crypto: [], serializers: [] };
  window.__JSRA_TRACE__ = TRACE;
  
  // Hook Fetch
  var origFetch = window.fetch;
  window.fetch = function() { /* 记录请求 + 调用栈 */ };
  
  // Hook XHR
  var origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url) { /* 记录 */ };
  
  // Hook crypto.subtle (digest/sign/encrypt/decrypt)
  crypto.subtle.digest = function(algorithm, data) {
    TRACE.crypto.push({type:'digest', algorithm});
    return origDigest(algorithm, data);
  };
  
  // 捕获 Webpack 模块
  // 搜索 __webpack_require__ / webpackChunk* / require.c
})();
```

### 2. 加密候选评分 (detect_encryption.py)

7 维度评分系统：

| 维度 | 权重 | 判定依据 |
|------|------|---------|
| name_score | 1.0 | 函数名包含 encrypt/sign/rsa/aes/md5/sm2 等 |
| source_keyword_score | 1.0 | 源码包含加密库调用关键字 |
| runtime_stack_score | 1.0 | 调用栈关联到目标请求 |
| request_correlation | 0.8 | 请求 body/header 中出现函数名或返回值 |
| input_output_shape | 0.9 | 输入/输出符合加密特征 |
| module_export_score | 0.7 | 从 Webpack 模块导出 |
| verification_score | 1.0 | 真实样本验证通过 |

**阈值**: 总分 > 0.6 → 进入验证阶段

**验证流程**:
1. 用真实请求中的明文输入调用候选函数
2. 对比输出是否匹配抓包中的密文
3. 匹配 → confidence=high

### 3. Webpack 模块解析

优先级链（不跳级）：

```
Priority 1: window.__webpack_require__ 存在？
  ├── 存在 → 直接使用
  └── 不存在 →
Priority 2: webpackChunk* 存在？
  ├── 存在 → hook push 方法，等待下次 chunk 加载
  └── 不存在 →
Priority 3: require.c 遍历
  └── 从已加载 module cache 搜索 export
Priority 4: 离线解析 chunk factory（实验性）
  └── 只生成 candidate，标记 confidence=low
```

### 4. JSRPC (WebSocket 远程调用)

```javascript
// 浏览器端
var client = new Hlclient("ws://127.0.0.1:12080/ws?group=xxx");
client.regAction("encrypt", function(param, resolve) {
  var result = window.encryptFunc(param);
  resolve(String(result));
});
```

```bash
# 调用
curl "http://127.0.0.1:12080/go?group=xxx&action=encrypt&param=plaintext"
# 返回: "密文字符串"
```

### 5. Flask 代理

```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route("/encode", methods=["POST"])
def encode():
    data = request.form.get("dataBody", "")
    # 调 JSRPC 获取加密结果
    # 返回给 Burp autoDecoder
    return encrypted_data
```

### 6. autoDecoder 集成

```bash
# Burp 配置
# 1. 安装 autoDecoder 插件
# 2. 配置：
#    autoDecoder URL: http://127.0.0.1:5000/encode
#    HTTP Method: POST
#    Form Fields: dataBody, dataHeaders
# 3. 配置 encode 方向（请求加密）和 decode 方向（响应解密）
```

## 反调试处理

| 反调试类型 | 注入方案 | 参考来源 |
|-----------|---------|---------|
| debugger 循环 | 重写 eval/Function/constructor 过滤 debugger | antidebug-patterns.md |
| toString 检测 | 重写 Function.prototype.toString | 同上 |
| 控制台清理 | 重写 console.clear | 同上 |
| 时间检测 | 重写 Date.now/performance.now | 同上 |
| DevTools 检测 | 重写 element.attributes 或 viewport 检测 | 同上 |

## 能力边界

### 支持
- 页面导航、evaluate_script、initScript 预注入
- 网络请求读取、console 读取
- Hook fetch/XHR/crypto.subtle/JSON.stringify
- Webpack module cache 捕获
- 早期 Hook 安装（initScript）

### 不支持
- 真实 JS 断点（paused frame）
- 闭包未导出函数
- WASM 未导出内部函数
- Service Worker 内部闭包
- ES module import 拦截
- VMP 静态还原
- CSP WebSocket 绕过
- VM 保护 JS 的直接 Hook

## 快速启动

```bash
# 1. 安装 MCP
pip install chrome-devtools-mcp 或 npx chrome-devtools-mcp@latest

# 2. 配置到 Hermes
# ~/.hermes/config.yaml 添加 MCP 服务

# 3. 启动浏览器
# 启动 Chrome 带远程调试端口

# 4. 输入目标
# Target URL + Parameters To Analyze → 全自动流程
```

## 引用
- 原始项目: Fausto-404/js-reverse-automation--skill
- JsRpc: https://github.com/jxhczhl/JsRpc
- autoDecoder: https://github.com/f0ng/autoDecoder
- chrome-devtools-mcp: https://github.com/ChromeDevTools/chrome-devtools-mcp/

---

## algorithm-reverse

1|---
2|name: algorithm-reverse
3|description: JS逆向算法还原统一技能。签名还原、混合加密拆解、Cookie/Header签名、JSVMP/VMP字节码还原、Wasm协议分析。统一闭环：请求→writer→builder→entry→source，Python复现。
4|author: 7452323 (converted from Private Gist)
5|version: "1.0"
6|tags:
7|  - js-reverse
8|  - algorithm-reduction
9|  - signature-crack
10|  - captcha
11|  - jsvmp
12|  - wasm
13|  - crypto
14|---
15|
16|# Algorithm Reverse — JS逆向算法还原统一技能
17|
18|## 技能协作链
19|
20|| 技能 | 关系 | 协作方式 |
21||------|------|----------|
22|| find-crypto-entry | 上游 | 入口定位结果传给本技能 |
23|| ast-deobfuscation | 前处理 | 解混淆后的可读代码便于分析算法层 |
24|| env-patch | 环境依赖 | 环境准备完成后才能复现签名 |
25|| jsvmp-reverse | 下游转交 | VMP题型识别后转交字节码层面 |
26|
27|## 统一闭环方法论
28|
29|所有题型统一走这条闭环，不先读混淆大文件：
30|
31|```text
32|最终请求 / 最终cookie / 最终verify / 最终WS帧
33|→ writer（写出点）
34|→ builder（构造函数）
35|→ entry（加密入口）
36|→ source（原始材料）
37|```
38|
39|### 核心原则
40|1. 先找最终写出点，不先读混淆大文件
41|2. 先存中间值，不先猜算法名
42|3. 先缩小执行范围，再补环境
43|4. 先证明输入输出边界，再决定是否整体迁移
44|
45|## 题型分类（6类）
46|
47|| 分类 | 难度 | 特征 | 产出 |
48||------|------|------|------|
49|| 纯时间戳/随机数签名 | ⭐ | 只有时间戳/随机数 | Python 30行 |
50|| 固定算法+固定 Key | ⭐⭐ | 单步确定，可迁移 | Python 50行 |
51|| 固定算法+动态 Key | ⭐⭐⭐ | 需从 JS 提取 Key | Python 50行+提取脚本 |
52|| 固定算法+混合加密 | ⭐⭐⭐⭐ | RSA/AES 多段组合 | Python 80行 |
53|| VMP 执行+参数自校验 | ⭐⭐⭐⭐⭐ | 依赖 VMP 引擎 | Node迁移，不Python |
54|| 风控/验证码参数组合 | ⭐⭐⭐⭐⭐ | 多参数+Wasm+Cookie | 多段式工程 |
55|
56|## 5层检查点
57|
58|| 检查点 | 通过条件 | 违反后果 |
59||--------|----------|----------|
60|| L1 写出点定位 | 找到修改 Document.cookie / localStorage / XMLHttpRequest.setRequestHeader 的代码位置 | 后续全错 |
61|| L2 输入输出确认 | 在 Node.js 中复现写出点的输入输出 | 环境错误 |
62|| L3 边界测试 | 使用伪造参数测试写出 | 功能验证 |
63|| L4 迁移正确性 | 将输出与真实请求比对 | 无法上线 |
64|| L5 异常处理 | 参数异常时能否提供有效输出 | 工程不可用 |
65|

## 实战提炼：签名算法逆向通用模式

### 从 ONE App 和 chatgpt2api 中提炼

| 实战来源 | 签名算法 | 特征 | 通用模式 |
|---------|---------|------|---------|
| ONE App (Flutter) | `MD5(MD5(ip.platform.ts.uk.uuid) + salt)` | 双层MD5 + 拼接 + salt | **拼接→哈希→加盐→再哈希** |
| chatgpt2api (ChatGPT) | PoW sentinel token | 服务端下发 challenge + 客户端计算 | **Challenge-Response 签名** |
| HttpCall (Wails) | Bearer token from config | 静态 token 认证 | **静态 Token + 前端注入** |

### 通用签名逆向框架

```python
# 当你遇到新 App 的签名算法时，按这个模板系统排查
SIGN_PATTERNS = {
    # 单层哈希
    "md5_single":     lambda params: md5(concat(params)),
    "sha1_single":    lambda params: sha1(concat(params)),
    "sha256_single":  lambda params: sha256(concat(params)),
    
    # 双层哈希（ONE App 模式）
    "md5_md5_salted": lambda params: md5(md5(concat(params)) + salt),
    "md5_sha1":       lambda params: sha1(md5(concat(params))),
    
    # 加盐变种
    "hmac":           lambda key, params: hmac.new(key, concat(params), hashlib.sha256).hexdigest(),
    "salted_concat":  lambda params: md5(concat(params) + salt),
    "salted_prefix":  lambda params: md5(salt + concat(params)),
    
    # Time-based
    "ts_md5":         lambda params, ts: md5(concat(params) + ts),
    "ts_hmac":        lambda key, params, ts: hmac.new(key, concat(params) + ts).hexdigest(),
}

def crack_sign(known_params: dict, known_sign: str):
    """穷举可能的签名算法，匹配已知 sign 值"""
    for algo_name, algo_fn in SIGN_PATTERNS.items():
        try:
            computed = algo_fn(**known_params)
            if computed == known_sign:
                return algo_name
        except:
            continue
    return None
```

### 通用 5 步法

```
1. 找拼接材料：从反编译/HAR/抓包中收集所有请求头参数
2. 找签名值：HAR 文件中的 sign/token/signature 字段
3. 猜算法：md5/sha1/hmac 三种最常见，优先试双层
4. 猜拼接顺序：按字母序、按参数定义顺序、按出现顺序
5. 验证：用已知数据跑一遍，匹配就确认
```

---
