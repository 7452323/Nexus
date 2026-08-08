---
name: desktop-app-reverse
category: reverse-engineering
description: >-
  Merged skill combining: desktop-app-reverse-engineering, pyinstaller-reverse.
version: "1.0"
sources:
  - desktop-app-reverse-engineering
  - pyinstaller-reverse
tags: [reverse-engineering, merged]
---

# desktop-app-reverse

> **Merged from**: desktop-app-reverse-engineering, pyinstaller-reverse
> **Source count**: 2

---

## Table of Contents

1. [desktop-app-reverse-engineering](#desktop-app-reverse-engineering)
2. [pyinstaller-reverse](#pyinstaller-reverse)

---

## desktop-app-reverse-engineering

# Desktop App Reverse Engineering — 桌面应用逆向

## 应用类型识别

| 类型 | 特征文件 | 工具 |
|------|----------|------|
| Electron | asar 文件 | asar extract |
| Wails | .exe + wails.json | 直接分析 |
| Tauri | 前端资源在二进制外 | 定位前端目录 |
| .NET | exe/dll | dnSpy |
| Qt/QML | qml 文件 | 直接读取 |

## 通用流程

1. 识别技术栈（看文件结构）
2. 解包/提取前端资源
3. 搜索关键字符串（API/URL/Key）
4. 分析认证逻辑
5. 定位 AI prompt（如果有）

## macOS 专项：WKWebView 注入

### 识别场景
- macOS 应用使用 WKWebView（常出现在 Mac Catalyst / AppKit + Web 混合应用中）
- 应用无 Hardened Runtime 或签名为 adhoc（`codesign -dv` 检查）
- 前端逻辑执行 API 调用验证权限（如 `/api/user/subscription`）

### 破解路径：DYLD 注入 + WKWebView JS 注入

```
┌── 侦察 ──────────────────────────────────────────┐
│  1. `codesign -dv /Applications/Target.app`       │
│     检查签名类型: adhoc / 无 hardened runtime     │
│  2. `strings Target | grep -i "api\|fetch\|http"`  │
│     定位关键 API endpoints                         │
│  3. 抓包确认认证请求和响应格式                     │
└──────────────────────────────────────────────────┘
    │
    ▼
┌── 构建 dylib ────────────────────────────────────┐
│  创建 ObjC dylib，hook WKWebView 的              │
│  - (id)webView:createWebViewWithConfiguration:   │
│  在 navigationDelegate 中注入 JS payload         │
│  方案：用 `[webView evaluateJavaScript:...]`      │
│  或 hook `-[WKWebView initWithFrame:configuration:]` │
└──────────────────────────────────────────────────┘
    │
    ▼
┌── JS Payload 设计 ───────────────────────────────┐
│  劫持 fetch() / XMLHttpRequest 拦截 API 响应:     │
│                                                    │
│  const origFetch = window.fetch;                   │
│  window.fetch = async (...args) => {                │
│    const res = await origFetch(...args);            │
│    const url = typeof args[0] === 'string' ? args[0] : args[0]?.url; │
│    if (url?.includes('/user/subscription')) {       │
│      return new Response(JSON.stringify({            │
│        plan_type: 'pro',                             │
│        ...                                          │
│      }), { status: 200, headers: res.headers });    │
│    }                                                │
│    return res;                                      │
│  };                                                 │
└──────────────────────────────────────────────────┘
    │
    ▼
┌── 注入执行 ──────────────────────────────────────┐
│  DYLD_INSERT_LIBRARIES=unlock.dylib               │
│  /Applications/Target.app/Contents/MacOS/Target    │
│  (或使用 install_name_tool 直接嵌入 LC_LOAD_DYLIB) │
└──────────────────────────────────────────────────┘
```

### 编译 dylib

```bash
clang -dynamiclib -o unlock.dylib unlock.m \
  -framework WebKit -framework Foundation \
  -fobjc-arc -O2
```

### 关键检查点
- 确认 dylib 被加载：`DYLD_PRINT_LIBRARIES=1` 启动
- 确认 JS 注入成功：在 injected JS 中 `console.log` + 查看系统日志
- 如果 app 有 Hardened Runtime，需要先移除或签署 entitlements：
  `codesign --remove-signature /Applications/Target.app`

## Wails 前端资源提取

```bash
# Go binary → 搜索 wails.json → 提取嵌入的 index.html + JS
strings Target | grep -E '^wails\.json|^index\.html|^[A-Za-z]*\.js' | head -20
strings Target | sed -n '/<html/,/<\/html>/p' | head -100
```

### Wails AI prompt 提取
- 搜索 `system.*prompt`、`messages.*role`、`model` 等关键词
- 定位应用的 AI 分析功能使用的 system prompt
- 提取后直接复用于 Hermes Agent 的 reverse engineering pipeline

## Electron 专项
```bash
npx asar extract app.asar app/
# 前端资源在 app/ 目录
```

## Wails 专项
- 前端资源直接嵌入二进制
- 搜索 `wails.json` 定位版本
- 字符串搜索提取 AI prompt

### Wails + Chrome DevTools Protocol (CDP) 注入

HttpCall 风格的 Wails 逆向：利用 Wails 内置的 WebView 调试能力。

**侦察步骤：**
```bash
# 1. 识别 Wails 应用
strings Target | grep -i "wails"
file Target  # 检查二进制类型
```

**核心技术：CDP 浏览器连接 + AI prompt 提取**
```
┌── 识别 ───────────────────────────────────────────┐
│  1. strings 发现 AI 相关字符串 (Claude/Kimi/API)  │
│  2. 确认是 Wails (Go + Web) 二进制                │
│  3. 前端资源嵌入在二进制中                         │
└──────────────────────────────────────────────────┘
    │
    ▼
┌── AI Pipeline 提取 ───────────────────────────────┐
│  使用 Wails 应用的 Chrome DevTools Protocol 连接：  │
│  1. 启动 app 并连接 CDP                            │
│  2. 注入 JS 拦截/查看 AI API 调用                  │
│  3. 提取：                                        │
│     - 使用的 AI 模型 (Claude/Kimi/DeepSeek/...)    │
│     - 完整的 system prompt + user message 模板     │
│     - 函数调用链（参数生成逻辑）                   │
│     - 使用的代理/路由配置                          │
│  4. 评估哪些逻辑可被 Hermes 复用                   │
└──────────────────────────────────────────────────┘
```

## 实战案例：HttpCall Pro Unlock — Wails 二进制原地 Patch

基于 https://www.httpcall.com/ Wails Pro 版解锁实战。

### 原理层：为什么 Wails 二进制可以原地 patch JS？

**核心事实：** Wails 使用 Go 的 `embed.FS` 在编译时将前端资源（HTML/JS/CSS）直接嵌入到 Go 二进制的 `__TEXT.__rodata` 段。这些数据是**明文存储的字符串字面量**，不是加密也不是编译后的字节码。

```
Go 源码 → go build → 嵌入二进制 __TEXT.__rodata 段
  //go:embed frontend/dist
  var fs embed.FS
  → strings 能直接读到 "isPro:()=>{const l=..."
```

**为什么能原地替换不破坏二进制？**
- Mach-O 二进制的结构布局在编译完成后固定。各个段（`__TEXT`、`__DATA`、`__LINKEDIT`）之间有固定的偏移和大小
- `__TEXT.__rodata` 段存储的是**只读数据引用**，不是代码
- embed 的 JS 字符串在段内以 C 字符串形式存在
- 只要替换后的字节数 **完全等于** 原始字节数，二进制段偏移不变、符号表不变、Mach-O header 不变
- 所以 `len(old) == len(new)` 是硬约束 — 短的用空格填充对齐

```python
# patch 核心逻辑 — 为什么字节长度必须相等
(b'isPro:()=>{const l=i().subscription;return!l||uf(l)?!1:l.plan_type===\"pro\"||l.plan_type===\"enterprise"}',  # 103 bytes
 b'isPro:()=>!0' + b' ' * (103 - 12))  # 12 bytes + 91 spaces = 103 bytes
```

**为什么 adhoc 签名就能跑？**
- macOS 的 Gatekeeper 只检查二进制有没有签名，不检查有效签名
- `codesign --sign -` 生成匿名(adhoc)签名，满足最低要求
- HttpCall 没有启用 Hardened Runtime（通过 `codesign -dv` 确认）
- 如果有 Hardened Runtime，可以 `codesign --remove-signature` 移除，再用 adhoc 重签

**为什么三个函数就够？**
- `isPro()` → 控制 Pro 功能开关
- `isLoggedIn()` → 控制登录状态（Pro 需要登录）
- `uf()` → 控制订阅是否过期
- 这三个函数构成**权限三角**：已登录 + 是 Pro + 未过期 = 全部解锁

**通用原理：** 任何 Wails/Electron/Tauri 应用，只要前端 JS 以明文嵌入且无完整性校验（没签前端资源/没做 checksum），都可以用**相同字节长度原地替换法**篡改认证逻辑。前提确认：没有运行时 integrity check、没有签名校验前端资源。

### HttpCall 风格 AI 分析管道逆向

基于 https://www.httpcall.com/ Wails 应用的逆向实践。

### 目标
- 拆解 Wails 应用中 AI 分析请求功能的实现
- 提取 AI Prompt、模型配置、参数生成逻辑
- 评估 Hermes 可复用性

### 逆向流程

#### 1. 静态侦察
```bash
# 提取二进制中的 AI 字符串
strings HttpCall | grep -iE "claude|kimi|deepseek|openai|gpt|system.*prompt"
strings HttpCall | grep -iE "api\.[a-z]|https?://|model|temperature|max_tokens"
strings HttpCall | sed -n '/system/,/assistant/p'  # 提取 system prompt 片段
```

#### 2. 前端资源提取（Wails 嵌入）
```bash
# Wails 前端资源嵌入在 Go 二进制中
# 方法一：strings 提取 HTML/JS 资源
strings HttpCall | grep -E '\.(html|js|css|json)' | head -50

# 方法二：提取嵌入文件系统
# Wails 使用 embed.FS，资源在 runtime 前可被完整 dump
# 可以找到 go:embed 标记的目录并提取

# 方法三：通过 Wails 内置 DevTools 连接
# Wails 使用 WebView2 (Windows) 或 WKWebView (macOS)
# 可通过 CDP 或 Safari Web Inspector 连接
```

#### 3. AI Prompt 提取模板
```python
# 从 binary strings 中提取 AI Prompt 的通用模式
import re

patterns = [
    r'(?i)"system"\s*:\s*"([^"]{50,})"',  # system role content
    r'(?i)system.*?prompt.*?"([^"]{100,})"',  # system prompt
    r'(?i)messages.*?\[.*?\{.*?role.*?system',  # messages array
    r'(?i)(你是一个|你是|You are|Act as|As an)[^\.]+',  # Chinese/English system prompt
]

with open('dump.txt', 'r') as f:
    text = f.read()
    for p in patterns:
        matches = re.findall(p, text)
        for m in matches:
            print(f"[FOUND] {m[:200]}...")
```

#### 4. 函数调用链追踪
```
1. 从 binary strings 中找到 API endpoint URL
2. 在前端 JS 中搜索该 endpoint 的调用位置
3. 追踪参数构建过程（哪些用户输入？哪些是硬编码？）
4. 提取完整的请求/响应格式
5. 评估管道可复用性
```

#### 5. Hermes 可复用性评估矩阵

| HttpCall 组件 | Hermes 等价能力 | 复用难度 |
|---------------|----------------|----------|
| AI 模型调用 (Claude/Kimi/DeepSeek) | Hermes provider 配置 | 低 — 直接替换 |
| 浏览器连接 (CDP) | Hermes browser tool | 低 — 原生支持 |
| 请求参数生成逻辑 | 需要独立 Adapter | 中 — 提取 prompt + 格式 |
| API 代理/路由 | Hermes gateway | 低 — 配置替代 |
| Chrome DevTools Protocol 调试 | browser_console JS expression | 低 — 原生支持 |
| fetch/XMLHttpRequest 拦截 | Hermes 无原生 fetch 劫持 | 高 — 需自定义 middleware |

### 关键发现记录模板

```markdown
# HttpCall/AI分析管道逆向报告

## 基本信息
- 应用: {app_name}
- 框架: Wails v{version} (Go {go_version} + React {react_version})
- 目标: {analysis_goal}

## AI Pipeline 发现
### 模型配置
- 模型: {model_name}
- API Key 来源: {env/config/embed}
- Endpoint: {api_url}

### System Prompt 全文
```
{full_system_prompt}
```

### 请求格式
```json
{request_template}
```

## Hermes 复用计划
- [ ] 提取 system prompt → Hermes system prompt
- [ ] 适配 browser tool 做 CDP 连接
- [ ] 重写参数生成逻辑为 Python
- [ ] 配置 provider 路由
```

## PyInstaller 专项

### 识别
检查打包特征：
```bash
file target.exe       # PE32 executable (GUI/Linux)
strings target.exe | grep -i "pyinstaller\|PyInstaller\|_MEIPASS"
# PyInstaller 特征：MEIPASS 目录、bootloader 签名
```

### 提取流程
```bash
# 1. 使用 pyinstxtractor 解包
git clone https://github.com/extremecoders-re/pyinstxtractor.git
python3 pyinstxtractor.py target.exe

# 2. 解压后找到 .pyc 文件
ls target.exe_extracted/

# 3. 使用 pycdc/uncompyle6 反编译 .pyc
uncompyle6 target.exe_extracted/main.pyc > main.py
```

### 关键信号
- `config.json` / `.env` 嵌入在打包中 — 直接 strings 搜索
- 网络请求相关的 API key、URL 端点 — strings + 反编译
- 算法逻辑通过加密库调用（cryptodome/hashlib）— 直接反编译可见

---

## pyinstaller-reverse

# PyInstaller Reverse — PyInstaller 打包应用逆向

## 适用场景

- Python 应用被 PyInstaller 打包为单个 exe/Linux 二进制
- 目标文件 5MB+，strings 有 Python 特征
- 需要提取原始 Python 源码或配置

## 识别

```bash
# 检查 PyInstaller 特征
file target.exe
strings target.exe | grep -iE "pyinstaller|PyInstaller|_MEIPASS|bootloader"
strings target.exe | grep -iE "python|\.pyc|__pycache__"

# PyInstaller 特征标记：
# - _MEIPASS 环境变量
# - 打包的 .pyc 文件
# - 特定版本 bootloader 签名
```

## 解包流程

```bash
# 1. 安装 pyinstxtractor
git clone https://github.com/extremecoders-re/pyinstxtractor.git

# 2. 解包
python3 pyinstxtractor/pyinstxtractor.py target.exe

# 输出到: target.exe_extracted/
# 包含: .pyc 文件 + PYZ 档案 + 依赖 DLL
```

## 反编译

```bash
# 方法一：uncompyle6
pip install uncompyle6
uncompyle6 target.exe_extracted/main.pyc > main.py

# 方法二：pycdc
# https://github.com/zrax/pycdc
./pycdc target.exe_extracted/main.pyc > main.py

# 方法三：pycdas（AST 反汇编，当反编译失败时）
./pycdas target.exe_extracted/main.pyc > main.ast
```

## 常见陷阱

| 问题 | 原因 | 解决 |
|------|------|------|
| `ImportError: Unknown magic number` | Python 版本不匹配 | 用对应 Python 版本的 pycdc |
| 反编译后语法错误 | 控制流优化残留 | 手动修复 + AST 分析 |
| 部分 .pyc 损坏 | PyInstaller 压缩 | 先用 `archive_viewer.py` 检查 |
| 找不到入口点 | 入口可能在 PYZ 档案中 | `python3 -m pyinstxtractor.cli --extract-pyz` |

## 关键信号提取

```bash
# 直接搜索 API key / URL / 配置
strings target.exe | grep -iE "api_key|token|secret|http|https://"
strings target.exe | grep -iE "config|\.env|\.json|password"

# 反编译后搜索敏感数据
grep -r "api_key\|token\|secret\|password" target.exe_extracted/
grep -r "requests\|http\|url\|endpoint" target.exe_extracted/
```

## 参考资源

- `pyinstxtractor`: https://github.com/extremecoders-re/pyinstxtractor
- `pycdc`: https://github.com/zrax/pycdc
- `uncompyle6`: https://github.com/rocky/python-uncompyle6/

---
