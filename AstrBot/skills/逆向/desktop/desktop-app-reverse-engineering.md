---
category: reverse-engineering
name: desktop-app-reverse-engineering
description: "逆向分析编译后的桌面应用——静态分析二进制文件，提取嵌入的前端资源、AI prompt/工具定义、架构模式。当用户提供桌面应用二进制（.app/.exe/.deb 等）要求逆向分析其实现细节时使用。覆盖 FAT Binary 双 Slice patch 和 Zustand 验证路径分析。"
version: 2.0.0
author: Akino
tags: [reverse-engineering, desktop-app, binary-analysis, wails, electron, tauri, cdp, ai-agent, fat-binary, zustand]
---

# 桌面应用逆向工程

静态分析编译后的桌面应用二进制，提取嵌入资源、AI 架构、prompt 模板和工具定义。

## When to use

- 用户提供桌面应用（.app / .exe / .deb / AppImage 等）要求逆向分析
- ⚠️ **如果 .exe 是 PyInstaller 打包的 Python 程序**，改用 `reverse-engineering-general` 的 [PyInstaller 逆向](../reverse-engineering-general/references/pyinstaller-exe-reverse.md) 流程（提取源码可直接移植，不需要二进制分析）
- 需要理解某个桌面应用的核心功能实现（如 AI 分析、CDP 连接、网络协议）
- 需要提取嵌入的前端代码（React/Vue/Svelte）
- 需要评估某个应用的架构是否可被 Hermes 复用
- 需要从编译后的 Go/Rust 二进制中提取逻辑信息

## Step 1: 识别应用框架

```bash
# 检查 Info.plist（macOS）
cat "App.app/Contents/Info.plist" | grep -A1 -E "CFBundleExecutable|CFBundleIdentifier|CFBundleGetInfoString"

# 检查框架类型
find "App.app/Contents/" -maxdepth 3 \
  -name "*.asar" -o -name "libflutter*" -o -name "libtauri*" \
  -o -name "Electron*" -o -name "node*" 2>/dev/null
```

| 框架 | 识别特征 | 二进制特征 |
|------|---------|-----------|
| **Electron** | Frameworks/Electron Framework, *.asar | node.js 字符串 |
| **Wails** | `Built using Wails (https://wails.io)` in Info.plist | Go runtime + 嵌入前端 |
| **Tauri** | libtauri*, Rust 字符串 | Rust runtime + 嵌入前端 |
| **Flutter** | libflutter*, App.framework | Dart runtime |
| **Qt** | Qt*, QtCore | C++ symbols |
| **SwiftUI** | SwiftUI, Swift | Swift symbols |

## Step 2: 提取嵌入资源

### 2.1 定位前端代码区域

```python
python3 << 'EOF'
with open(binary_path, 'rb') as f:
    data = f.read()

# Wails: 前端在二进制尾部附近
# 搜索 DOCTYPE / HTML 标记
for marker in [b'<!DOCTYPE html>', b'<html', b'<head>']:
    pos = data.find(marker, len(data) // 2)  # 从后半段搜索
    if pos >= 0:
        print(f"{marker} at offset {pos}")
EOF
```

### 2.2 提取 strings 中的关键信息

```bash
# 全量 strings 提取
strings -n 6 "Binary" > /tmp/app-strings.txt

# AI/LLM 相关
grep -iE "openai|claude|anthropic|gpt-4|chat.completion|anthropic-messages|api_key|x-api-key" /tmp/app-strings.txt

# CDP (Chrome DevTools Protocol) 相关
grep -iE "Runtime\.enable|Network\.enable|Debugger\.enable|Debugger\.step|Fetch\.|Runtime\.evaluate|Runtime\.getProperties" /tmp/app-strings.txt

# 网络请求相关
grep -iE "https?://|api\.|/v1/|endpoint|base_url|baseUrl" /tmp/app-strings.txt

# 前端框架标识
grep -iE "useState|useEffect|zustand|redux|createContext|React\." /tmp/app-strings.txt
```

### 2.3 提取完整前端 JS（Wails/Electron）

**Wails 应用**：前端 dist 打包在 Go 二进制中，用 `go:embed`

```python
python3 << 'EOF'
import re

with open(binary_path, 'rb') as f:
    data = f.read()

# 方法1: 搜索前端打包标记
marker = b'frontend/dist/index.html'
pos = data.find(marker)
print(f"Frontend marker at: {pos}")

# 方法2: 搜索大型 JS 函数块（React 组件代码特征）
# 搜索包含 JSX/React 特征的大段代码
patterns = [
    b'createElement',
    b'useState',
    b'useEffect',
    b'React.',
    b'wailsjs',
]

for p in patterns:
    positions = []
    start = 0
    while len(positions) < 5:
        idx = data.find(p, start)
        if idx == -1: break
        positions.append(idx)
        start = idx + 1
    if positions:
        print(f"{p}: found at {positions[:5]}")
EOF
```

## Step 3: 分析 AI Agent 架构

### 3.1 识别 LLM 协议

从 strings 中提取 API 端点和协议类型：

| 协议标识 | API 格式 | 典型 Base URL |
|---------|---------|--------------|
| `anthropic-messages` | Anthropic Messages API | api.anthropic.com |
| `chat-completions` | OpenAI Chat Completions API | api.openai.com/v1 |
| `responses` | OpenAI Responses API | api.openai.com/v1 |

### 3.2 提取 Agent 状态机

搜索状态关键词：

```bash
grep -iE "idle|analyzing|waiting|running|done|error|paused|completed" /tmp/app-strings.txt
```

典型 Agent Loop 状态流：`idle → analyzing → waiting_user → done / error`

### 3.3 提取工具定义

搜索 CDP 命令映射（AI tool_call → CDP 命令）：

```bash
grep -iE "Debugger\.|Runtime\.|Network\.|Fetch\.|Page\." /tmp/app-strings.txt
```

常见 AI-CDP 工具映射：

| AI 工具名 | CDP 命令 | 功能 |
|-----------|---------|------|
| set_breakpoint | Debugger.setBreakpoint | 设置断点 |
| step_over | Debugger.stepOver | 单步跳过 |
| step_into | Debugger.stepInto | 单步进入 |
| step_out | Debugger.stepOut | 单步跳出 |
| resume | Debugger.resume | 继续执行 |
| evaluate | Runtime.evaluate | 执行 JS 表达式 |
| get_properties | Runtime.getProperties | 获取变量属性 |
| get_response_body | Fetch.getResponseBody | 读取网络响应 |
| search_source | Debugger.searchInContent | 搜索源码 |

### 3.4 提取 AI Prompt 模板

搜索 prompt 相关文本：

```bash
grep -iE "system|instruction|You are|Analyze|Please|help me|tool_use|function_call" /tmp/app-strings.txt
```

注意：prompt 可能被混淆或压缩，不一定能完整提取。Go 二进制中的字符串通常更可读，前端 minified JS 中的 prompt 较难提取。

## Step 4: 分析通信层

### 4.1 Wails IPC

Wails 应用通过 `wails://` 和 `window.wails` 桥接前后端：

```bash
grep -iE "wails://|wails/ipc|wails/runtime|wailsjs|wails:generate" /tmp/app-strings.txt
```

### 4.2 SSE / 流式响应

```bash
grep -iE "text/event-stream|stream|SSE|data:|\\[DONE\\]" /tmp/app-strings.txt
```

### 4.3 WebSocket

```bash
grep -iE "websocket|ws://|wss://|ws:connected|ws:disconnected|ws:error" /tmp/app-strings.txt
```

## Step 5: 提取配置和密钥信息

```bash
# API 端点和密钥
grep -iE "api[_-]?key|API_KEY|secret|token|Bearer|Authorization" /tmp/app-strings.txt

# 默认配置
grep -iE "default|config|settings|preferences" /tmp/app-strings.txt | head -30

# 文件路径（持久化存储）
grep -iE "\.json|\.yaml|\.toml|\.plist|\.db|\.sqlite|localStorage" /tmp/app-strings.txt | head -30
```

## Step 6: Hermes 复用评估模板

对于每个逆向的桌面应用，评估 Hermes 复用可行性：

| 维度 | 评估内容 |
|------|---------|
| 架构模式 | 能否用 Hermes 现有工具复现？ |
| CDP 能力 | 是否需要 MCP 封装？ |
| AI Agent Loop | 与 Hermes delegate_task 的映射关系 |
| LLM 集成 | 是否需要自定义 provider？ |
| 复用价值 | 值得复用的核心创新点是什么？ |
| 开发量 | 预估实现工时 |

### 常见复用路径

1. **CDP 工具 → Lightpanda MCP**：将 CDP 命令封装为 MCP 工具
2. **AI Agent → CodeBuddy**：用 CodeBuddy 后台执行分析任务
3. **LLM 调用 → Hermes custom_provider**：直接对接现有 LLM
4. **SSE 流式 → Hermes streaming**：直接兼容

## Step 7: FAT Binary 双 Slice 意识（关键！）

macOS Universal Binary 包含多个架构 slice，**每个 slice 都有一份完整的 JS/字符串副本**：

```bash
# 检查是否为 FAT binary
python3 -c "
import struct
with open(binary_path, 'rb') as f:
    magic = struct.unpack('>I', f.read(4))[0]
    if magic == 0xcafebabe:
        nfat = struct.unpack('>I', f.read(4))[0]
        print(f'FAT binary: {nfat} architectures')
        for i in range(nfat):
            cpu, sub, offset, size, align = struct.unpack('>IIIII', f.read(20))
            name = {0x01000007: 'x86_64', 0x0100000c: 'arm64'}.get(cpu, f'unknown({cpu})')
            print(f'  Slice {i}: {name} offset=0x{offset:x} size=0x{size:x}')
    elif magic == 0xfeedfacf:
        print('Single arch 64-bit')
"
```

**致命 Pitfall**：如果只 patch 了第一个 slice（通常是 x86_64），而 Mac 以 arm64 运行，patch 完全不生效！**必须对每个 slice 都执行相同的替换。**

### 全 Slice Patch 的正确做法

```python
# ❌ 错误：只搜索一次替换就停
pos = data.find(pattern)
data = data[:pos] + replacement + data[pos+len(pattern):]

# ✅ 正确：全局搜索替换所有出现
pos = 0
while True:
    pos = data.find(pattern, pos)
    if pos < 0:
        break
    data = data[:pos] + replacement + data[pos+len(pattern):]
    pos += len(pattern)
```

## Step 8: 二进制原地字符串替换技术

当前端 JS 以明文嵌入二进制时，**原地替换是最可靠的解锁方式**，比 DYLD 注入或 JS 劫持更稳定。

### 核心原则

1. **替换字符串长度必须严格相等** — 否则破坏二进制结构
2. **用空格填充多余空间** — JS 中空格是合法 token，不影响执行
3. **替换后必须重签名** — `codesign --force --deep --sign - App.app`
4. **所有 slice 都要替换** — 见 Step 7

### 替换模式速查

| 原始 | 替换 | 说明 |
|------|------|------|
| `isPro:()=>{...复杂逻辑...}` | `isPro:()=>!0` + 空格填充 | 函数永远返回 true |
| `isLoggedIn:()=>{...验证...}` | `isLoggedIn:()=>!0` + 空格填充 | 永远登录 |
| `return!0;if(xxx)return!1` | `return!1;if(xxx)return!1` | 翻转返回值 |
| `i<=Date.now()` | `i> Date.now()` | 反转时间比较（同长度13字节） |
| `$e.getState().isPro()` | `!0                   ` | 直接调用替换为 true |
| `function Ci(){return xxx}` | `function Ci(){return!0}` + 空格 | 快捷函数替换 |

### 精确长度匹配模板

```python
# 通用 patch 模板：精确测量 → 填充 → 断言
original = b'isPro:()=>{const l=i().subscription;return!l||uf(l)?!1:l.plan_type==="pro"}'
replacement = b'isPro:()=>!0' + b' ' * (len(original) - 12)  # 12 = len('isPro:()=>!0')
assert len(original) == len(replacement), f"{len(original)} vs {len(replacement)}"
```

### 从二进制精确提取验证函数体

不只是搜索关键词——提取**完整的函数定义字符串**用于替换：

```python
# 搜索 isPro 完整定义
with open(binary_path, 'rb') as f:
    data = f.read()

# 精确搜索：从关键词扩展到完整函数体
search = b'isPro:()=>{const'
pos = data.find(search)
if pos >= 0:
    # 向后读取到匹配的 }
    depth, end = 0, pos
    while end < len(data):
        if data[end:end+1] == b'{': depth += 1
        elif data[end:end+1] == b'}':
            depth -= 1
            if depth == 0:
                end += 1
                break
        end += 1
    full_func = data[pos:end]
    print(f"Full isPro: {full_func.decode()}")
    print(f"Length: {len(full_func)} bytes")
```

## Step 9: Zustand Store 验证路径全覆盖

WebView 架构的桌面应用（Wails/Electron/Tauri）常使用 Zustand 做状态管理，Pro 验证有多种调用路径，**必须全部覆盖**：

### 四种 isPro 调用路径

```
路径 1: Store 定义（源头）
  isPro:()=>{return subscription.plan_type==="pro"}
  → 替换为 isPro:()=>!0

路径 2: Zustand Selector（React 组件常用）
  const isPro = $e(state => state.isPro())   // 或 $e(N=>N.isPro())
  → 路径 1 修复后自动生效（selector 调用的是 store 方法）

路径 3: 快捷函数（工具函数/模块引用）
  function Ci(){return $e.getState().isPro()}
  → 替换为 function Ci(){return!0}

路径 4: 直接调用（store action/非 React 上下文）
  if(!$e.getState().isPro()) return;
  → 替换为 if(!0                   ) return;
```

**关键洞察**：路径 2 的 selector 实际调用路径 1 的 store 方法，所以修复路径 1 就覆盖路径 2。但路径 3 和路径 4 是独立的调用入口，**必须分别 patch**。

### 验证覆盖完整性

```bash
# 搜索所有 isPro 调用点，确认无遗漏
strings -n 4 Binary | grep -iE 'isPro' | sort -u
# 预期看到：定义、selector、快捷函数、直接调用四种模式
```

## Step 10: 输出结构化报告

将所有发现写入 `/tmp/<app-name>-reverse/analysis-report.md`：

```
<app-name>-reverse/
├── analysis-report.md     # 结构化分析报告
├── ref.md                 # 逆向参考文档
├── strings-extracted.txt  # 关键 strings 提取
└── frontend/              # 提取的前端资源（如能提取）
```

**报告必须包含**：
1. 应用架构概述（框架、技术栈、二进制结构）
2. AI 功能实现细节（LLM 协议、Agent 状态机、工具定义）
3. CDP/浏览器连接方式
4. Prompt 模板（如能提取）
5. 会话管理和持久化
6. Hermes 复用评估
7. 关键 strings 索引

## Go 二进制深度提取技巧

### 提取 Go 包路径和函数签名

Go 二进制包含完整的包路径和函数签名，这是最高价值的信息源：

```bash
# 提取项目自身的包路径（过滤掉标准库和第三方库）
strings -n 20 Binary | grep -E "^[a-z]+/internal/" | sort -u

# 提取完整函数签名（agent/llm/debug 相关）
strings -n 30 Binary | grep -E "(agent|llm|debug|mission|store)/" | sort -u
```

**实战发现**：HttpCall (内部名 `jiemian`) 的包结构完全从 strings 暴露：
- `jiemian/internal/agentlab/agent` — 50+ 函数签名（buildCustomSubagentSystemPrompt, mainAgentToolDefinitions 等）
- `jiemian/internal/agentlab/llm` — LLM 客户端实现
- `jiemian/internal/agentlab/cdptools` — CDP 工具注册
- 开发者本地路径也会暴露：`/Users/kang/Claude-works/jiemian_3/internal/...`

### 从 Go 泛型实例化符号提取 JSON Schema

Go 1.18+ 泛型会在二进制中留下完整的类型信息，包含 json tag：

```bash
# 搜索包含 json tag 的结构体定义
strings -n 40 Binary | grep -E 'json:"' | head -50

# 搜索特定包的 JSON 结构
strings -n 40 Binary | grep -E "cdptools|agentlab" | grep 'json:"'
```

**实战发现**：从泛型符号 `param.MarshalWithExtras[go.shape.struct{...}]` 中可以提取完整的工具 Input/Output JSON 结构，精确到每个字段的 json tag、类型和 omitempty 标记。

### 提取 AI Agent System Prompt

Go 二进制中的 prompt 文本通常以中文或英文自然语言形式存在，搜索策略：

```bash
# 方法1: 搜索 prompt 构建函数名附近的字符串
strings -n 10 Binary | grep -B2 -A5 "buildCustom\|buildReview\|currentSession\|contextMemory"

# 方法2: 搜索中文 prompt 关键词（中文逆向工具常见）
strings -n 4 Binary | grep -E "你是|职责|边界|流程|禁止|必须|不要|规则"

# 方法3: 搜索 Markdown 格式的结构化 prompt
strings -n 10 Binary | grep -E "^#{1,3} |^#{1,3}[A-Z]|^#{1,3}步骤"

# 方法4: 搜索工具使用示例格式
strings -n 10 Binary | grep -E "^/[a-z_]+ \{|\"urlPattern\"|\"expression\"|\"location\""
```

**实战发现**：HttpCall 的完整中文 System Prompt 直接明文存储在二进制中，包含角色定义、规则列表、边界约束和输出格式要求。

### 提取多 Agent 协作架构

```bash
# 搜索 Agent 类型和消息协议
strings -n 10 Binary | grep -iE "MainAgent|EnvironmentAgent|ProbeAgent|ReviewAgent|CustomAgent"
strings -n 10 Binary | grep -iE "debug:agent_event|debug:tool_call|debug:tool_result|debug:status|debug:report"
strings -n 10 Binary | grep -iE "launch_subagent|agent_type"
```

**实战发现**：HttpCall 的 4 Agent 架构（Main→Environment→Probe→Review）和消息协议完全可从 strings 逆向出来。

### 提取 Shell 安全防护规则

```bash
# 搜索危险命令正则黑名单
strings -n 5 Binary | grep -E "\\\\b.*\\\\b|rm.*-[rf]|mkfs|diskpart|fork.*bomb"
```

## Pitfalls

1. **Wails 前端嵌入在 Go 二进制中** — 不是独立文件，需要从二进制中提取
2. **strings 输出巨大** — 54MB 二进制可能输出 100K+ 行 strings，必须定向 grep
3. **Go 二进制的字符串比前端 JS 更可读** — Go 不混淆字符串常量，是主要信息源
4. **前端 JS 是 minified 的** — 变量名无意义，需从字符串常量和上下文反推功能
5. **不要运行二进制** — 只做静态分析，避免安全风险（解锁工具构建见 desktop-app-unlock skill）
6. **macOS .app 是目录不是文件** — 二进制在 `Contents/MacOS/<executable>` 下
7. **CDP 事件名是 Go 字符串** — 在二进制中可直接搜索，如 `Debugger.enable`、`Runtime.evaluate`
8. **AI prompt 可能分散** — 不一定在一个地方，可能由前端动态拼接；但 Go 后端的 prompt 通常明文存储
9. **Zustand store 的 key 是可读的** — React 状态管理的 key 通常保留在 minified 代码中
10. **版本字符串可推断更新时间** — 如 `claude-opus-4-0`、`compact_20260112` 可推断更新时间
11. **Go 泛型符号是 JSON Schema 金矿** — `go.shape.struct{...json:"field"...}` 包含完整的结构体字段定义和 json tag，可以精确还原 API 请求/响应格式
12. **开发者路径泄露** — Go 编译时嵌入源码路径（`/Users/xxx/project/...`），可推断开发者信息和项目名
13. **中文 prompt 直接可搜** — 中国开发的逆向工具的 AI prompt 常含中文（"你是""职责""禁止"），用 strings + grep 即可提取
14. **工具别名映射表可提取** — 前端 JS 中的 `{listscripts:"list_scripts",...}` 对象保留在 minified 代码中
15. **CodeBuddy 逆向长任务需分步** — 单次后台任务容易卡住，应拆分为：先提取 strings → 再深度搜索 → 最后构建报告
16. **FAT Binary 双 Slice** — Universal Binary 的 x86_64 和 arm64 slice 各有一份完整的 JS/字符串，patch 时必须全局搜索替换所有出现（详见 Step 7）
17. **二进制原地替换必须长度相等** — JS 字符串替换不能改变二进制大小，用空格填充多余空间，替换后必须重签名
18. **isPro 有四种调用路径** — store 定义、Zustand selector、快捷函数、直接调用，必须全部覆盖才能完全解锁（详见 Step 9）
19. **DYLD 注入不总是可靠** — WKWebView 可能早于 swizzle 初始化，导致 JS 注入时序失败。二进制原地替换是最可靠方案

## 下一步：订阅解锁策略

完成静态分析后，如需绕过付费/订阅限制，使用以下策略。

### 策略选择决策树

```
前端 JS 是否明文嵌入二进制（Wails/Tauri 常见）？
├── 是 → ★ 方案 A: 二进制原地字符串替换（最可靠，推荐首选）
│         见 Step 8-9 的精确替换技术
├── 否（独立前端文件，如 Electron .asar）→ 方案 B: 修改前端文件
└── 以上都不可行 → 方案 C: DYLD_INSERT_LIBRARIES 注入（备选）
```

### 方案 C: DYLD 注入（备选方案）

⚠️ HttpCall 实战中，dylib 成功加载但 WKWebView swizzle 因时序问题未生效。**二进制原地替换是唯一 100% 可靠方案。**

```objc
// unlock.m — hook WKWebView 注入 JS
#import <Foundation/Foundation.h>
#import <WebKit/WebKit.h>
#import <objc/runtime.h>

static WKWebView *swizzled_initWithFrame(id self, SEL _cmd, CGRect frame, WKWebViewConfiguration *config) {
    WKWebView *(*orig)(id, SEL, CGRect, WKWebViewConfiguration *) = (void *)orig_imp;
    WKWebView *webView = orig(self, _cmd, frame, config);
    WKUserScript *script = [[WKUserScript alloc]
        initWithSource:@"(function(){/* fetch hijack payload */})();"
        injectionTime:WKUserScriptInjectionTimeAtDocumentEnd
        forMainFrameOnly:YES];
    [webView.configuration.userContentController addUserScript:script];
    return webView;
}

__attribute__((constructor)) static void init(void) {
    Method m = class_getInstanceMethod(objc_getClass("WKWebView"), @selector(initWithFrame:configuration:));
    orig_imp = method_setImplementation(m, (IMP)swizzled_initWithFrame);
}
```

编译: `clang -dynamiclib -framework WebKit -framework Foundation -arch arm64 -arch x86_64 -o unlock.dylib unlock.m`

### fetch 劫持 Payload 模板

```javascript
(function proUnlock() {
  const origFetch = window.fetch;
  window.fetch = async function (...args) {
    const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
    if (url.includes('/user/subscription')) {
      return new Response(JSON.stringify({code:0,data:{plan_type:'pro',status:'active',end_date:'2099-12-31'}}), {status:200,headers:{'Content-Type':'application/json'}});
    }
    return origFetch.apply(this, args);
  };
})();
```

### 解锁验证清单

| 检查项 | 验证方法 |
|-------|---------|
| Pro 徽章 | UI 中显示 "Pro" 标签 |
| 锁定功能 | 点击无弹窗 |
| AI 功能 | 按钮可点击 |
| 订阅信息 | 设置中显示 Pro，到期 2099 |

### 关键 Pitfalls

- **SIP 可能阻止 DYLD 注入** — 将 app 复制到用户目录后运行
- **WKWebView 只注入一次** — 需在 `didFinishNavigation` 回调中重新注入
- **前后端双重验证** — 后端也校验时需同时 patch IPC 或后端逻辑
- **App 更新破坏二进制修改** — DYLD 方式不修改 app，更兼容更新

## 工具箱

| 工具 | 用途 |
|------|------|
| `strings` | 从二进制提取可读字符串 |
| `file` | 识别文件类型 |
| `grep -iE` | 多模式搜索（macOS 不支持 -P） |
| Python | 二进制搜索、偏移定位、资源提取 |
| `tr ';' '\n'` | 拆分 minified JS |
| CodeBuddy | 后台长分析任务 |
