# 74 工具快速参考表

按 4 大类组织的 JSReverser-MCP 工具快速参考。按逆向目标查工具。

## Navigation (18 工具)

| 工具 | 参数 | 典型用法 |
|------|------|---------|
| `new_page` | url, timeout | 创建新页面并导航，逆向任务第一步 |
| `navigate_page` | type, url, ignoreCache, timeout | 导航/前进/后退/刷新当前页面 |
| `check_browser_health` | — | 检查浏览器连接和页面就绪状态 |
| `list_pages` | — | 列出浏览器中打开的所有页面 |
| `select_page` | pageIdx | 选择页面作为后续工具调用的上下文 |
| `click_element` | selector | 点击元素触发请求 |
| `type_text` | selector, text, delay | 在输入框中输入文本 |
| `query_dom` | selector, all, limit | 查询一个或多个 DOM 元素 |
| `wait_for_element` | selector, timeout | 等待元素出现 |
| `find_clickable_elements` | filterText | 查找可点击的按钮/链接 |
| `get_dom_structure` | maxDepth, includeText | 获取 DOM 树结构 |
| `get_performance_metrics` | — | 获取页面性能指标 |
| `save_session_state` | sessionId, includeCookies/LocalStorage/SessionStorage | 保存当前页面会话状态（cookies/storage） |
| `restore_session_state` | sessionId, navigateToSavedUrl, clearStorageBeforeRestore | 恢复已保存的会话状态 |
| `dump_session_state` | sessionId, path, pretty, encrypt | 导出会话快照为 JSON |
| `load_session_state` | sessionId, path, snapshotJson, overwrite | 从 JSON 或文件加载会话快照 |
| `delete_session_state` | sessionId | 删除内存中的会话快照 |
| `list_session_states` | — | 列出所有已保存的会话快照 |

## Network (6 工具)

| 工具 | 参数 | 典型用法 |
|------|------|---------|
| `list_network_requests` | pageSize, pageIdx, resourceTypes, includePreservedRequests | 列出当前页面的所有网络请求 |
| `get_network_request` | reqid | 获取单个网络请求详情 |
| `get_request_initiator` | requestId, taskId, taskSlug, targetUrl, goal | 获取请求的 JS 调用栈，定位谁触发了目标请求 |
| `list_websocket_connections` | pageSize, pageIdx, urlFilter, includePreservedConnections | 列出所有 WebSocket 连接 |
| `analyze_websocket_messages` | wsid, direction | 分析 WebSocket 消息模式，按类型分组 |
| `get_websocket_messages` | wsid, direction, groupId, pageSize, pageIdx, show_content | 获取 WebSocket 连接的消息内容 |

## Debugging (5 工具)

| 工具 | 参数 | 典型用法 |
|------|------|---------|
| `evaluate_script` | function | 在页面中执行 JS 函数并返回 JSON 结果 |
| `inject_preload_script` | script | 注入在页面加载前执行的脚本（preload hook） |
| `list_console_messages` | pageSize, pageIdx, types, includePreservedMessages | 列出控制台消息 |
| `get_console_message` | msgid | 获取单条控制台消息 |
| `take_screenshot` | format, quality, fullPage, filePath | 截取页面或元素截图 |

## JS Reverse Engineering (45 工具)

### 脚本发现 (4)

| 工具 | 参数 | 典型用法 |
|------|------|---------|
| `list_scripts` | filter | 列出页面加载的所有 JS 脚本 |
| `get_script_source` | scriptId, startLine, endLine, offset, length | 获取脚本源码（支持行范围和字符偏移） |
| `find_in_script` | scriptId, query, contextChars, occurrence, caseSensitive | 在指定脚本中查找字符串的精确位置 |
| `search_in_scripts` | pattern, limit, maxTotalSize | 在已收集的脚本缓存中搜索正则匹配 |

### Hook 采样 (8)

| 工具 | 参数 | 典型用法 |
|------|------|---------|
| `create_hook` | type, params, description, action | 创建 hook 脚本（12 种类型），**推荐首选** |
| `inject_hook` | hookId | 将已创建的 hook 注入当前页面 |
| `get_hook_data` | hookId, view, maxRecords | 获取 hook 采样数据（支持 raw/summary 视图） |
| `hook_function` | target, logArgs, logResult, logStack, hookId | Hook 函数记录调用/参数/返回值，不暂停执行 |
| `trace_function` | functionName, urlFilter, logArgs, logThis, pause, traceId | 追踪函数调用（用 logpoint，不暂停执行） |
| `unhook_function` | hookId | 移除函数 hook |
| `remove_hook` | hookId | 按 ID 移除 hook |
| `list_hooks` | — | 列出所有活跃的 hook |

### 断点调试 (13)

| 工具 | 参数 | 典型用法 |
|------|------|---------|
| `set_breakpoint` | url, lineNumber, columnNumber, condition, isRegex | 在指定行设置断点（**仅当 hook 不足时使用**） |
| `set_breakpoint_on_text` | text, urlFilter, occurrence, condition | 按文本搜索自动定位断点位置 |
| `break_on_xhr` | url | XHR/Fetch 请求 URL 包含指定字符串时触发断点 |
| `pause` | — | 在当前位置暂停 JS 执行 |
| `resume` | — | 恢复 JS 执行 |
| `step_over` | — | 单步跳过（函数调用视为一步） |
| `step_into` | — | 单步进入函数体 |
| `step_out` | — | 跳出当前函数 |
| `get_paused_info` | includeScopes, maxScopeDepth | 获取当前暂停状态的调用栈和作用域变量 |
| `evaluate_on_callframe` | expression, frameIndex | 在暂停的调用帧上下文中执行表达式 |
| `list_breakpoints` | — | 列出所有活跃断点 |
| `remove_breakpoint` | breakpointId | 按 ID 移除断点 |
| `remove_xhr_breakpoint` | url | 移除 XHR 断点 |

### 代码分析 (7)

| 工具 | 参数 | 典型用法 |
|------|------|---------|
| `collect_code` | url, smartMode, returnMode, includeInline/External/Dynamic, maxTotalSize, maxFileSize, pattern, limit, topN | 智能收集页面 JS 代码（summary/priority/incremental/full 模式） |
| `understand_code` | code, focus | AI + 静态分析代码结构/业务/安全 |
| `summarize_code` | mode, code, url, files | 总结单个/多个代码文件或项目级上下文 |
| `deobfuscate_code` | code, aggressive, renameVariables | AI 辅助 JS 反混淆 |
| `detect_crypto` | code, useAI | 检测加密算法/库 |
| `risk_panel` | code, useAI, includeHookSignals, hookId, topN | 综合风险评分（分析器+加密检测+hook 信号） |
| `collection_diff` | previous, current, includeUnchanged | 比较前后两次代码收集的差异 |

### 环境导出 (4)

| 工具 | 参数 | 典型用法 |
|------|------|---------|
| `analyze_target` | url, topN, useAI, runDeobfuscation, hookPreset, autoInjectHooks, waitAfterHookMs, correlationWindowMs, maxCorrelatedFlows, maxFingerprints, autoReplayActions, collect | 一键逆向分析（组合 collect+security+crypto+hook correlation） |
| `export_rebuild_bundle` | *(从 analyze_target 导出)* | 导出 local rebuild bundle |
| `diff_env_requirements` | *(辅助比对)* | 比对环境依赖差异（**辅助用途，不替代代理日志**） |
| `record_reverse_evidence` | taskId, taskSlug, targetUrl, goal, channel, targetKeywords, targetUrlPatterns, targetFunctionNames, targetActionDescription, entry | 追加结构化逆向证据到 task artifact |
| `export_session_report` | format, includeHookData | 导出当前逆向会话为 JSON 或 Markdown |

### 运行时 (5)

| 工具 | 参数 | 典型用法 |
|------|------|---------|
| `inspect_object` | expression, depth, showMethods, showPrototype | 深度检查 JS 对象（属性/原型链/方法） |
| `get_storage` | type, filter | 获取浏览器 storage 数据（cookies/localStorage/sessionStorage） |
| `search_in_sources` | query, caseSensitive, isRegex, maxResults, maxLineLength, excludeMinified, urlFilter | 在所有已加载的 JS 源码中搜索字符串或正则 |
| `monitor_events` | selector, events, monitorId | 监控 DOM 事件 |
| `stop_monitor` | monitorId | 停止事件监控 |

### 隐身 (4)

| 工具 | 参数 | 典型用法 |
|------|------|---------|
| `inject_stealth` | preset | 注入反检测隐身脚本（5 种预设：windows-chrome/mac-chrome/mac-safari/linux-chrome/windows-edge） |
| `list_stealth_features` | — | 列出可用的隐身特性开关 |
| `list_stealth_presets` | — | 列出可用的隐身预设 |
| `set_user_agent` | userAgent | 设置自定义 User-Agent |

## Hook 类型速查

12 种内置 Hook 类型：function, fetch, xhr, websocket, property, event, timer, localStorage, cookie, eval, object-method, custom

## 反混淆管线

Packer → JSVMP → Advanced(invisible-unicode/控制流平坦化/不透明谓词/死代码) → AST优化(常量折叠/传播/变量内联) → 基础(字符串数组/解码/表达式简化) → LLM辅助

## 加密检测能力链

关键字匹配 → 加密库检测 → AST模式识别 → AI深度分析 → 安全评估 → 强度分析

## 隐身覆盖维度

Navigator / Plugin / Screen / Connection / WebGL / Canvas / Audio / WebRTC / Font
