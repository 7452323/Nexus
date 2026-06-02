---
category: reverse-engineering
name: js-reverse-engineering
description: "JS逆向工作流总纲——编排6阶段全流程（Observe→Capture→Rebuild→Patch→PureExtraction→Port），协调子技能完成端到端逆向。本技能定义'做什么'和'引用谁'，具体实现由子技能承担。TRIGGER when: 用户要求完整的JS逆向流程、端到端签名分析、从观察到迁移的全链路任务。DO NOT TRIGGER when: 只需要某个子能力（如补环境→env-patch、解混淆→ast-deobfuscation、定位入口→find-crypto-entry）。"
version: 2.0.0
author: Akino
tags: [reverse-engineering, javascript, orchestration, workflow]
---

# JS逆向工作流总纲

本技能是JS逆向领域的**总纲层**，编排6阶段全流程，协调子技能完成端到端逆向。

**核心原则**：本技能定义"做什么"和"引用谁"，具体实现由子技能承担。每个阶段说清目标、完成判据和引用技能，不说具体操作。

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

### 红线

- 还没确认目标请求就开始补环境
- 还没定位关键脚本就手翻混淆代码
- 没有代理日志和first divergence记录就补宿主
- env rebuild还没通过就开始翻Python
- 把补环境成功误当成纯算法已完成

---

## 阶段详细引用

### Observe → cdp-debug-reverse / Lightpanda

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

### 环境导出 → `export_rebuild_bundle` → `diff_env_requirements`（辅助比对，不替代代理日志）

### 证据记录 → `record_reverse_evidence` → `export_session_report`

### 运行时检查 → `inspect_object` / `get_storage` / `search_in_sources` / `monitor_events`

### 隐身注入 → `inject_stealth` / `list_stealth_presets` / `set_user_agent`

### 完整工具参考 → [references/tool-quick-reference.md](references/tool-quick-reference.md)

---

## 安全边界

- 仓库case只保留抽象模板，不放可执行实现
- 真实cookie/token/storage不进仓库
- entry_url用Base64编码
- task artifact默认本地私有
- 共享前先做脱敏审查

---

## Pitfalls

- 盲补环境：没有代理日志和first divergence就补宿主对象
- 过早提纯：env rebuild未通过就做纯算法提取
- 跳过Node直接Python：直接用execjs做补环境而非先在Node中验证
- 全量模拟：一次性补完整浏览器环境而非逐项回填
- 证据丢失：只把结论留聊天记录，不写入task artifact
- diff_env_requirements滥用：跳过代理日志直接依据diff补丁

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
