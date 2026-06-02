---
category: reverse-engineering
name: web-api-to-openai-proxy
description: "将任意 Web API 逆向并构建 OpenAI 兼容代理服务。通用方法论：协议逆向 → 格式转换 → 流式适配 → 内容过滤 → Tool Call 模拟（prompt engineering / webSearch 自动启用） → Docker 部署 → Hermes/客户端对接。"
version: 2.0.0
author: Akino
tags: [reverse-engineering, openai, proxy, api, hermes, docker, streaming]
---

# Web API → OpenAI 兼容代理构建指南

将任意非标准 Web API 逆向后，构建兼容 OpenAI `/v1/chat/completions` + `/v1/models` 的代理服务，使 Hermes Agent 等 OpenAI 客户端可直接调用。

---

## 一、整体架构

```
OpenAI Client (Hermes / Cursor / etc.)
    │
    │  OpenAI 格式
    │  POST /v1/chat/completions  (SSE stream)
    │  GET  /v1/models
    ▼
┌──────────────────────────────────┐
│  OpenAI 兼容代理 (FastAPI)        │
│                                  │
│  ① API Key 认证                  │
│  ② 请求转换 (OpenAI → 上游)      │
│  ③ 响应转换 (上游 → OpenAI SSE)  │
│  ④ 内容过滤 (广告/水印/追踪)     │
│  ⑤ 连接池 (httpx 全局单例)       │
└──────────────────────────────────┘
    │
    │  上游自有协议
    ▼
  目标 Web API
```

## 二、逆向分析

### 2.1 抓包流程

1. **浏览器 DevTools** → Sources → 搜索 `api/chat`、`fetch`、`stream` 定位 API 端点
2. **Network 面板** → 记录完整请求头、请求体、SSE 响应格式
3. **前端 JS chunk** → 搜索模型 ID 列表、认证逻辑、特殊参数

### 2.2 必须确认的信息

| 项目 | 确认内容 |
|------|---------|
| 端点 | URL、HTTP Method |
| 认证 | API Key / Cookie / OAuth / 无认证 |
| 请求头 | 特殊 header（如 `x-ai-sdk-chat-version`、`Origin`、`Referer`） |
| 请求体 | JSON 结构，messages 格式差异 |
| 响应格式 | SSE 事件类型 / JSON / WebSocket |
| 模型列表 | 前端 JS 中的模型 ID 及映射 |

### 2.3 常见上游协议分类

**A. Vercel AI SDK 协议**（最常见，Next.js 应用）
- 请求：`messages[].parts[]` 格式（非 `content` 字符串）
- 需要 `x-ai-sdk-chat-version: 1` header
- 需要 `id` / `trigger` / `messageId` 字段
- SSE 事件：`start` / `text-delta` / `reasoning-delta` / `data-text` / `source-url` / `finish`

**B. 标准 OpenAI 兼容**
- 请求/响应已接近 OpenAI 格式，可能仅模型名/字段名不同
- 通常只需做轻量映射

**C. 纯 REST JSON**
- 非流式，可能需要轮询
- 需自行实现 SSE 包装

**D. WebSocket**
- 双向实时通信
- 需维护连接状态，转换为 SSE 输出

## 三、代理服务实现

### 3.1 项目结构（FastAPI）

```
project/
├── app.py                    # FastAPI 入口
├── Dockerfile
├── requirements.txt
├── src/
│   ├── config.py             # 环境变量配置（API_KEY、PORT、UPSTREAM_URL）
│   ├── const.py              # 常量（模型映射、context_length、过滤规则）
│   ├── schemas/
│   │   ├── common.py         # ModelObject / ModelListResponse
│   │   └── chat.py           # ChatCompletionRequest
│   ├── routers/
│   │   ├── models.py         # GET /v1/models
│   │   └── chat.py           # POST /v1/chat/completions
│   └── services/
│       └── chat/
│           ├── request.py    # OpenAI → 上游请求转换
│           ├── response.py   # 上游 SSE → OpenAI SSE 转换
│           └── stream.py     # 流式处理 + 连接池
```

### 3.2 配置层（config.py）— 所有可变项外置

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 代理自身配置
    api_keys: str = ""              # 逗号分隔，为空则不认证
    port: int = 8000

    # 上游配置
    upstream_url: str = ""          # 上游 API 端点
    upstream_origin: str = ""       # Origin header
    upstream_referer: str = ""      # Referer header
    upstream_extra_headers: str = ""  # JSON 格式额外 headers

    # 性能配置
    connect_timeout: int = 15
    read_timeout: int = 120
    max_connections: int = 20
    max_keepalive: int = 10

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
```

### 3.3 常量层（const.py）— 模型与过滤规则

```python
# 模型映射：对外简洁名 → 上游内部名
# 模型 ID 不能含 `/`（Hermes 会解析失败），用简洁名对外
MODEL_MAPPING: dict[str, str] = {
    # "简洁名": "上游/provider/model名",
}

# 上下文窗口大小（必须 ≥ 64000，否则 Hermes 拒绝加载）
MODEL_CONTEXT_LENGTHS: dict[str, int] = {
    # "简洁名": context_length,
}

# 上游注入的内容过滤关键词（广告/水印/追踪等）
# 命中任一关键词的 text-delta / data-text 事件直接丢弃
CONTENT_FILTER_PATTERNS: list[str] = [
    # "上游推广域名",
    # "推广标语关键词",
]

# finish reason 映射
FINISH_REASON_MAP: dict[str, str] = {
    "stop": "stop",
    "length": "length",
    "content_filter": "content_filter",
    "tool_calls": "tool_calls",
    "error": "stop",
    "other": "stop",
}
```

### 3.4 请求转换（request.py）

核心：OpenAI 格式 → 上游格式的映射。每种上游协议需实现不同的转换。

```python
def convert_request(request, model_mapping: dict) -> dict:
    """OpenAI ChatCompletionRequest → 上游请求体"""
    # 1. 消息格式转换
    #    OpenAI: messages[].content (string | list)
    #    Vercel AI SDK: messages[].parts[] (array)
    #    其他: 可能是 messages[].text (string)

    # 2. 模型 ID 映射
    #    简洁名 → 上游名
    model = model_mapping.get(request.model, request.model)

    # 3. 上游特有字段
    #    Vercel AI SDK: id, trigger, messageId
    #    REST: 可能需要 session_id, conversation_id

    # 4. system 消息处理
    #    上游不支持 → 跳过，或拼入首条 user 消息
```

**关键映射点**（按上游类型选择）：

| 转换项 | OpenAI | Vercel AI SDK | REST JSON |
|--------|--------|---------------|-----------|
| 消息内容 | `content: string` | `parts: [{type:"text", text:""}]` | `text: string` |
| system 消息 | `role: "system"` | 通常不支持 | 通常不支持 |
| 模型选择 | `model: string` | `model: string` | `model_id: string` |
| 流式控制 | `stream: bool` | 始终 SSE | `stream: bool` |
| 工具调用 | `tool_calls[]` | `tool-invocation part` | 各异 |

### 3.5 响应转换（response.py）

上游 SSE 事件 → OpenAI SSE chunk 的通用映射框架：

```python
def _make_chunk(completion_id, model, created, delta, finish_reason=None) -> str:
    """构造标准 OpenAI SSE chunk"""
    chunk = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
    }
    return f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

def convert_stream_event(event, completion_id, model, created, filter_fn=None) -> list[str]:
    """上游事件 → OpenAI chunks，filter_fn 用于内容过滤"""
    event_type = event.get("type")
    chunks = []

    if event_type == "start" or event_type == "message_start":
        chunks.append(_make_chunk(completion_id, model, created, {"role": "assistant"}))

    elif event_type in ("text-delta", "content_block_delta"):
        text = event.get("delta", "") or event.get("delta", {}).get("text", "")
        if text and (not filter_fn or not filter_fn(text)):
            chunks.append(_make_chunk(completion_id, model, created, {"content": text}))

    elif event_type in ("reasoning-delta", "thinking_delta"):
        text = event.get("delta", "")
        if text:
            chunks.append(_make_chunk(completion_id, model, created, {"reasoning_content": text}))

    elif event_type == "data-text":
        data = event.get("data", "")
        if isinstance(data, str) and data and data != "Loading..." and (not filter_fn or not filter_fn(data)):
            chunks.append(_make_chunk(completion_id, model, created, {"content": data}))

    elif event_type in ("finish", "message_stop", "done"):
        reason = event.get("finishReason", event.get("stop_reason", "stop"))
        chunks.append(_make_chunk(completion_id, model, created, {}, finish_reason=FINISH_REASON_MAP.get(reason, "stop")))

    elif event_type == "error":
        error_text = event.get("errorText", event.get("error", {}).get("message", "Unknown"))
        chunks.append(_make_chunk(completion_id, model, created, {"content": f"\n[Error: {error_text}"}))

    return chunks
```

### 3.6 内容过滤

上游可能注入推广/水印/追踪内容。需要三层过滤策略：

#### 层级1：长关键词匹配（用于 data-text 整条检测）

```python
from src.const import CONTENT_FILTER_PATTERNS

def _is_ad_content(text: str) -> bool:
    """检测完整文本是否包含广告关键词（用于 data-text 等完整文本场景）"""
    if not text:
        return False
    text_lower = text.lower()
    return any(p.lower() in text_lower for p in CONTENT_FILTER_PATTERNS)
```

#### 层级2：短关键词部分匹配（用于流式 delta）⚠ 关键

**问题**：上游广告文本被 SSE 拆成多个 `text-delta` 事件，单个 delta 可能只有几个字符，完整关键词被截断导致逐条检测漏检。例如：
- delta1: `供赞助。 [Telegram电报`
- delta2: `AI机器人](https://bot.8`
- delta3: `18233.xyz)，让您`
- delta4: `在Telegram电报中直接使用ChatG`
- delta5: `PT（免费）、AI翻译（免`
- delta6: `费）、AI生图/修图。`
- 任何一个单独的 delta 都不包含完整关键词 `Telegram电报AI机器人` 或 `ChatGPT（免费）`。

**解决方案**：增加**短关键词列表**（2-4字子串），单个 delta 只需命中短关键词即可标记为广告可疑：

```python
# const.py
# 短关键词（2-4字），用于流式 delta 部分匹配
AD_SHORT_PATTERNS: list[str] = [
    "stockai.trade",
    "818233",
    "Telegram电报",
    "Web AI助手",
    "免费提供",
    "提供赞助",
    "全网最低",
    "AI视频",
    "AI生图",
    "AI翻译",
    "ChatGPT（",
    "Free AI",
    "AI机器人",
    "修图",
]

# response.py
from src.const import CONTENT_FILTER_PATTERNS, AD_SHORT_PATTERNS

def _is_ad_delta(text: str) -> bool:
    """检测流式 delta 是否包含广告片段（短关键词部分匹配）"""
    if not text:
        return False
    text_lower = text.lower()
    return any(p.lower() in text_lower for p in AD_SHORT_PATTERNS)
```

#### 层级3a：广告状态机（跨 chunk 连续丢弃）— delta 级

一旦检测到广告开始，后续所有 delta 全部丢弃，直到 `text-end` 或 `finish` 事件重置状态。用简单 dict 作为可变状态传递：

```python
# response.py — convert_stream_event 增加 ad_mode 参数
def convert_stream_event(
    event: dict,
    completion_id: str,
    model: str,
    created: int,
    ad_mode: dict | None = None,   # {"active": False}
) -> list[str]:
    event_type = event.get("type")
    chunks = []

    # ... start 事件 ...

    elif event_type == "text-delta":
        delta_text = event.get("delta", "")
        if delta_text:
            if ad_mode is not None:
                if ad_mode.get("active", False):
                    pass  # 广告模式中，跳过
                elif _is_ad_delta(delta_text):
                    ad_mode["active"] = True  # 进入广告模式
                    pass
                else:
                    chunks.append(_make_chunk(..., {"content": delta_text}))
            else:
                if not _is_ad_content(delta_text):
                    chunks.append(_make_chunk(..., {"content": delta_text}))

    elif event_type == "reasoning-delta":
        delta_text = event.get("delta", "")
        if delta_text:
            if ad_mode is not None:
                if ad_mode.get("active", False):
                    pass  # 广告模式中，跳过
                elif _is_ad_delta(delta_text):
                    ad_mode["active"] = True
                    pass
                else:
                    chunks.append(_make_chunk(..., {"reasoning_content": delta_text}))
            else:
                chunks.append(_make_chunk(..., {"reasoning_content": delta_text}))

    elif event_type == "text-end":
        # 文本流结束，重置广告模式
        if ad_mode is not None:
            ad_mode["active"] = False

    elif event_type == "data-text":
        data = event.get("data", "")
        if isinstance(data, str) and data and data != "Loading...":
            if _is_ad_content(data) or _is_ad_delta(data):
                pass  # 整条是广告，直接丢弃
            else:
                chunks.append(_make_chunk(..., {"content": data}))

    elif event_type == "finish":
        if ad_mode is not None:
            ad_mode["active"] = False
        # ... 正常处理 finish ...
```

```python
# stream.py — 初始化 ad_mode 并传递
async def stream_chat_completion(request):
    ad_mode = {"active": False}
    # ... 在调用 convert_stream_event 时传入 ad_mode ...
    for chunk in convert_stream_event(event, completion_id, model, created, ad_mode):
        yield chunk
```

**关键要点**：
- **广告同时注入 `reasoning-delta` 和 `text-delta`**，两个都要过滤
- **`data-text` 广告整条丢弃**：`_is_ad_content`（长关键词）+ `_is_ad_delta`（短关键词）双重检测
- **`text-end` 事件重置广告模式**：上游 SSE 中 `text-end` 表示当前文本流结束，之后的内容是新的正常回答
- **短关键词选择**：2-4字，确保被拆散后单个 chunk 也能命中。短关键词可能误杀（如"修图"出现在正常回答中），但上游广告模式固定，误杀概率极低
- **关键词库维护**：从用户反馈中持续补充，同时维护长关键词（完整匹配）和短关键词（部分匹配）两套列表

#### 层级3b：段落级流式过滤（StreamingAdFilter）— 段落级

**适用场景**：上游广告以完整段落注入（含特定域名，如 `stockai.trade` / `818233.xyz`），而非逐字拆散。此时状态机可能误判（单个 delta 正常但整段是广告），段落级过滤更精准。

**原理**：缓冲到段落边界（`\n\n`），检查完整段落是否含广告关键词，安全段落才输出。对流式输出增加少量延迟（最多一个段落），但误杀率极低。

```go
// filter/ad.go — 段落级流式广告过滤
type StreamingAdFilter struct {
    buf strings.Builder
}

var adDomains = []string{"stockai.trade", "818233.xyz"}

func (f *StreamingAdFilter) Push(delta string) string {
    f.buf.WriteString(delta)
    return f.flushCompleted()
}

func (f *StreamingAdFilter) FlushAll() string {
    full := f.buf.String()
    f.buf.Reset()
    return Clean(full)  // 非流式段落级过滤
}

func (f *StreamingAdFilter) flushCompleted() string {
    full := f.buf.String()
    lastBoundary := strings.LastIndex(full, "\n\n")
    if lastBoundary == -1 {
        return ""  // 没有完整段落，继续缓冲
    }
    completed := full[:lastBoundary+2]
    remaining := full[lastBoundary+2:]
    // 过滤完成的段落
    paragraphs := strings.Split(completed, "\n\n")
    var safe []string
    for _, p := range paragraphs {
        if p == "" || IsAd(p) { continue }
        safe = append(safe, p)
    }
    f.buf.Reset()
    f.buf.WriteString(remaining)
    if len(safe) == 0 { return "" }
    return strings.Join(safe, "\n\n") + "\n\n"
}

func IsAd(paragraph string) bool {
    for _, domain := range adDomains {
        if strings.Contains(paragraph, domain) { return true }
    }
    return false
}

func Clean(text string) string {
    paragraphs := strings.Split(text, "\n\n")
    var filtered []string
    for _, p := range paragraphs {
        if IsAd(p) { continue }
        filtered = append(filtered, p)
    }
    return strings.Join(filtered, "\n\n")
}
```

**选择策略**：

| 广告模式 | 推荐方案 | 原因 |
|---------|---------|------|
| 逐字拆散到 delta | 层级3a 状态机 | 单 delta 短关键词检测 + 连续丢弃 |
| 完整段落注入 | 层级3b 段落级过滤 | 段落级判断更精准，零误杀 |
| 两种都有 | 混合：段落缓冲 + 状态机 | 先段落缓冲，段落内再用状态机 |

### 3.7 连接池复用（stream.py）

```python
_client: httpx.AsyncClient | None = None

async def get_client() -> httpx.AsyncClient:
    """全局单例，复用连接池"""
    global _client
    if _client is None or _client.is_closed:
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        if settings.upstream_origin:
            headers["Origin"] = settings.upstream_origin
        if settings.upstream_referer:
            headers["Referer"] = settings.upstream_referer

        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(180.0, connect=settings.connect_timeout, read=settings.read_timeout),
            limits=httpx.Limits(max_connections=settings.max_connections, max_keepalive_connections=settings.max_keepalive),
            headers=headers,
        )
    return _client
```

**⚠ 陷阱**：`get_client()` 不能用 `async with` 管理（会关闭连接），只用 `client.stream()` / `client.request()` 的上下文管理器。

### 3.8 路由层

```python
# chat.py — 强制流式
@router.post("/v1/chat/completions")
async def chat_completions(request, _api_key=Depends(verify_api_key)):
    return StreamingResponse(
        stream_chat_completion(request),
        media_type="text/event-stream",
    )

# models.py — 必须返回 context_length
@router.get("/v1/models")
async def list_models():
    models = [
        ModelObject(
            id=alias,
            owned_by=PROJECT_NAME,
            context_length=MODEL_CONTEXT_LENGTHS.get(alias, 131072),
        )
        for alias in MODEL_MAPPING
    ]
    return ModelListResponse(data=models)
```

## 四、OpenAI 兼容接口规范

代理必须实现的接口：

### 4.1 GET /v1/models

```json
{
  "object": "list",
  "data": [
    {
      "id": "model-name",
      "object": "model",
      "owned_by": "proxy-name",
      "context_length": 131072
    }
  ]
}
```

### 4.2 POST /v1/chat/completions (SSE)

请求：
```json
{
  "model": "model-name",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": true
}
```

SSE 响应：
```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":T,"model":"model-name","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":T,"model":"model-name","choices":[{"index":0,"delta":{"content":"Hello!"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":T,"model":"model-name","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### 4.3 认证

Bearer token：`Authorization: Bearer <api_key>`

## 五、Hermes Agent 对接

### 5.1 添加 custom_provider

`~/.hermes/config.yaml`:
```yaml
custom_providers:
  - name: my-proxy            # 会变成 provider: custom:my-proxy
    base_url: http://HOST:PORT/v1
    api_key: your-api-key
    model: default-model-id
```

### 5.2 Hermes 关键约束

| 约束 | 说明 |
|------|------|
| **模型 ID 不含 `/`** | Hermes 解析失败。对外用简洁名，内部映射 |
| **context_length ≥ 64000** | 低于此值 Hermes 拒绝加载 |
| **SSE 格式** | `data: {json}\n\n`，结束 `data: [DONE]\n\n` |
| **Bearer 认证** | `Authorization: Bearer xxx` |

### 5.3 切换模型

```bash
hermes model                        # 交互式选择
hermes config set model.default <id>
hermes config set model.provider custom:<name>
```

## 六、实现语言选择

| 维度 | Python/FastAPI | Go |
|------|---------------|-----|
| 开发速度 | 快，代码简洁 | 中等，结构更规范 |
| 镜像大小 | ~150MB | ~10MB（多阶段构建） |
| 内存占用 | ~50-100MB | ~5-10MB |
| 启动时间 | 秒级 | 毫秒级 |
| SSE 流式效率 | 好（httpx + StreamingResponse） | 更好（bufio.Scanner + 立即 Flush） |
| 并发模型 | asyncio + uvloop | goroutine，真并发 |
| 适用场景 | 快速原型、简单代理 | 生产部署、高并发、资源受限环境 |

**结论**：I/O 转发代理的瓶颈在上游响应速度，Go 和 Python 的代理层延迟差异对用户不可感知。Go 的优势在于镜像体积小 15x、内存低 10x、启动快。生产环境优先选 Go。

**⚠ 不要用 Rust**：代理是纯 I/O 密集型，Rust 的零成本抽象和精确内存控制在等网络的场景毫无优势，开发成本却翻倍。

## 七、Go 实现版本

### 7.1 Go 项目结构

```
project/
├── main.go
├── go.mod
├── go.sum
├── Dockerfile
├── docker-compose.yml
├── .env
├── internal/
│   ├── config/
│   │   └── config.go          # 环境变量
│   ├── const/
│   │   └── const.go           # 模型映射、广告关键词、finish reason 映射
│   ├── handler/
│   │   ├── chat.go            # POST /v1/chat/completions
│   │   ├── models.go          # GET /v1/models
│   │   └── health.go          # GET /health
│   ├── middleware/
│   │   └── auth.go            # Bearer Token 认证中间件
│   ├── model/
│   │   └── schema.go          # 请求/响应结构体
│   ├── proxy/
│   │   ├── request.go         # OpenAI → 上游请求转换
│   │   ├── stream.go          # SSE 流转发 + 广告过滤状态机
│   │   └── response.go        # 辅助函数
│   └── adfilter/
│       └── filter.go          # 广告过滤核心
```

### 7.2 核心入口（main.go）

```go
package main

import (
    "log"
    "net/http"
    "stockai2api/internal/config"
    "stockai2api/internal/handler"
    "stockai2api/internal/middleware"
)

func main() {
    cfg := config.Load()
    mux := http.NewServeMux()
    mux.HandleFunc("/health", handler.Health)
    mux.HandleFunc("/v1/models", handler.Models)
    mux.HandleFunc("/v1/chat/completions", middleware.Auth(cfg)(handler.ChatCompletions(cfg)))
    log.Printf("starting on :%s", cfg.Port)
    http.ListenAndServe(":"+cfg.Port, mux)
}
```

### 7.3 SSE 流转发核心（stream.go）

```go
// 全局 HTTP 客户端（连接池复用）
var httpClient = &http.Client{
    Timeout: 180 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:        50,
        MaxIdleConnsPerHost: 20,
        IdleConnTimeout:     90 * time.Second,
    },
}

func StreamChatCompletion(w http.ResponseWriter, r *http.Request, req *model.ChatCompletionRequest) {
    // ... 请求转换、发送到上游 ...

    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")
    flusher, _ := w.(http.Flusher)
    adState := &adfilter.AdState{}

    scanner := bufio.NewScanner(resp.Body)
    scanner.Buffer(make([]byte, 0, 64*1024), 1024*1024)

    for scanner.Scan() {
        line := strings.TrimSpace(scanner.Text())
        if line == "" || !strings.HasPrefix(line, "data: ") { continue }
        dataStr := line[6:]
        if dataStr == "[DONE]" {
            fmt.Fprint(w, "data: [DONE]\n\n")
            flusher.Flush()
            return
        }
        var event map[string]interface{}
        json.Unmarshal([]byte(dataStr), &event)
        chunks := convertStreamEvent(event, completionID, reqModel, created, adState)
        for _, chunk := range chunks { fmt.Fprint(w, chunk) }
        flusher.Flush()  // 每事件立即 flush，真流式
    }
}
```

### 7.4 广告过滤（adfilter/filter.go）

```go
type AdState struct { Active bool }

func (s *AdState) Feed(text string) bool {
    if s.Active { return true }
    if IsAdDelta(text) { s.Active = true; return true }
    return false
}

func (s *AdState) Reset() { s.Active = false }

func IsAdContent(text string) bool { /* 长关键词完整匹配 */ }
func IsAdDelta(text string) bool   { /* 短关键词部分匹配 */ }
```

### 7.5 事件转换中的广告过滤

```go
case "text-delta":
    if adState.Feed(delta) { /* skip */ } else { /* output content */ }
case "reasoning-delta":
    if adState.Feed(delta) { /* skip */ } else { /* output reasoning_content */ }
case "text-end":
    adState.Reset()
case "data-text":
    if IsAdContent(data) || IsAdDelta(data) { /* discard */ } else { /* output */ }
case "finish":
    adState.Reset()
```

### 7.6 Non-Stream 响应（Go 版）⚠ 必须实现

上游只支持 SSE，但 Hermes `stream:false` 期望标准 `chat.completion` JSON。解决方案：内部以 SSE 调上游，收集所有 content，组装完整 JSON 响应。

```go
// internal/proxy/nonstream.go
func NonStreamChatCompletion(w http.ResponseWriter, r *http.Request, req *model.ChatCompletionRequest) {
    stockaiReq := ConvertRequest(req)
    completionID := "chatcmpl-" + uuid.New().String()
    created := time.Now().Unix()
    reqModel := req.Model

    // ... 同 stream.go 发请求到上游 ...

    var contentBuf strings.Builder
    var reasoningBuf strings.Builder
    var finishReason string
    adState := &adfilter.AdState{}

    scanner := bufio.NewScanner(resp.Body)
    scanner.Buffer(make([]byte, 0, 64*1024), 1024*1024)

    for scanner.Scan() {
        line := strings.TrimSpace(scanner.Text())
        if line == "" || !strings.HasPrefix(line, "data: ") { continue }
        dataStr := line[6:]
        if dataStr == "[DONE]" { break }

        var event map[string]interface{}
        json.Unmarshal([]byte(dataStr), &event)
        eventType, _ := event["type"].(string)

        switch eventType {
        case "text-delta":
            delta, _ := event["delta"].(string)
            if delta != "" {
                if adState.Feed(delta) { /* skip */ } else { contentBuf.WriteString(delta) }
            }
        case "reasoning-delta":
            delta, _ := event["delta"].(string)
            if delta != "" {
                if adState.Feed(delta) { /* skip */ } else { reasoningBuf.WriteString(delta) }
            }
        case "text-end":
            adState.Reset()
        case "data-text":
            data, _ := event["data"].(string)
            if data != "" && data != "Loading..." {
                if adfilter.IsAdContent(data) || adfilter.IsAdDelta(data) { /* skip */ } else { contentBuf.WriteString(data) }
            }
        case "source-url":
            url, _ := event["url"].(string); title, _ := event["title"].(string)
            if url != "" {
                if title == "" { title = "Source" }
                contentBuf.WriteString(fmt.Sprintf("\n[%s](%s)", title, url))
            }
        case "finish":
            adState.Reset()
            reason, _ := event["finishReason"].(string)
            finishReason = mapFinishReason(reason)
        case "error":
            errorText, _ := event["errorText"].(string)
            contentBuf.WriteString(fmt.Sprintf("\n[Error: %s]", errorText))
        }
    }

    finalContent := contentBuf.String()
    if reasoningBuf.Len() > 0 { finalContent = reasoningBuf.String() + finalContent }
    if finishReason == "" { finishReason = "stop" }

    response := model.ChatCompletionResponse{
        ID: completionID, Object: "chat.completion", Created: created, Model: reqModel,
        Choices: []model.ChatCompletionChoice{{
            Index: 0, Message: model.ChoiceMessage{Role: "assistant", Content: finalContent}, FinishReason: &finishReason,
        }},
        Usage: model.ChatCompletionUsage{},
    }
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}
```

handler 中分流：
```go
// internal/handler/chat.go
func ChatCompletions(cfg *config.Config) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        var req model.ChatCompletionRequest
        json.NewDecoder(r.Body).Decode(&req)
        if req.Stream {
            proxy.StreamChatCompletion(w, r, &req)
        } else {
            proxy.NonStreamChatCompletion(w, r, &req)
        }
    }
}
```

### 7.7 Tool Role 消息处理（Go 版）⚠ 必须实现

Hermes agent loop 会发 `role:"tool"` 消息，上游不支持会返回 500。必须在请求转换中处理。

```go
// internal/model/schema.go — Message struct 新增字段
type Message struct {
    Role       string          `json:"role"`
    Content    json.RawMessage `json:"content"`
    ToolCalls  []ToolCall      `json:"tool_calls,omitempty"`
    ToolCallID string          `json:"tool_call_id,omitempty"`  // ← 新增
}

// internal/proxy/request.go — ConvertRequest 中新增 tool 角色处理
for _, msg := range req.Messages {
    if msg.Role == "system" { continue }

    // Handle tool role: convert to user message
    if msg.Role == "tool" {
        text := model.ContentToString(msg.Content)
        toolContent := fmt.Sprintf("[Tool Result (tool_call_id: %s)]\n%s", msg.ToolCallID, text)
        stockaiMessages = append(stockaiMessages, model.StockAIMessage{
            ID:    uuid.New().String(),
            Role:  "user",
            Parts: []interface{}{model.StockAITextPart{Type: "text", Text: toolContent}},
        })
        continue
    }

    // ... 正常处理 user/assistant 消息 ...
}
```

### 7.8 Tool Calling 转发（Go 版）⚠ 必须实现

Hermes agent loop 依赖 LLM 的 function calling 能力。代理必须转发 `tools` 定义并正确转换 `tool-input-*` 事件。

#### schema.go 新增

```go
// OpenAI 工具定义
type Tool struct {
    Type     string      `json:"type"`
    Function FunctionDef `json:"function"`
}

type FunctionDef struct {
    Name        string                 `json:"name"`
    Description string                 `json:"description,omitempty"`
    Parameters  map[string]interface{} `json:"parameters,omitempty"`
}

// ChatCompletionRequest 新增
Tools      []Tool       `json:"tools,omitempty"`
ToolChoice  interface{}  `json:"tool_choice,omitempty"`

// StockAIRequest 新增（⚠ Vercel AI SDK tools 是 map 不是 array！）
Tools      map[string]interface{} `json:"tools,omitempty"`
ToolChoice interface{}            `json:"toolChoice,omitempty"`

// ChoiceMessage 新增（non-stream 响应需要）
type ChoiceMessage struct {
    Role      string     `json:"role"`
    Content   string     `json:"content"`
    ToolCalls []ToolCall `json:"tool_calls,omitempty"`
}
```

#### request.go — tools 转换

```go
// OpenAI tools 数组 → Vercel AI SDK tools map
// OpenAI: [{type:"function", function:{name:"get_weather", description:"...", parameters:{...}}}]
// Vercel: {"get_weather": {description:"...", parameters:{...}}}
if toolChoiceStr, ok := req.ToolChoice.(string); ok && toolChoiceStr == "none" {
    // tool_choice="none": don't send tools to upstream
} else if len(req.Tools) > 0 {
    toolsMap := make(map[string]interface{})
    for _, t := range req.Tools {
        if t.Type == "function" {
            toolDef := map[string]interface{}{"description": t.Function.Description}
            if t.Function.Parameters != nil {
                toolDef["parameters"] = t.Function.Parameters
            }
            toolsMap[t.Function.Name] = toolDef
        }
    }
    if len(toolsMap) > 0 { stockaiReq.Tools = toolsMap }
    if toolChoiceStr == "required" { stockaiReq.ToolChoice = "required" }
    // "auto" or unspecified → don't set toolChoice (upstream defaults to auto)
}
```

#### stream.go — tool 事件转换

```go
// 在 StreamChatCompletion 循环中，tool 事件直接处理（不走 convertStreamEvent）
toolCallIndex := 0

switch eventType {
case "tool-input-start":
    toolCallID, _ := event["toolCallId"].(string)
    if toolCallID == "" { toolCallID = uuid.New().String() }
    toolName, _ := event["toolName"].(string)
    idx := toolCallIndex
    toolCallIndex++
    chunk := makeChunk(completionID, reqModel, created, map[string]interface{}{
        "tool_calls": []map[string]interface{}{
            {"index": idx, "id": toolCallID, "type": "function",
             "function": map[string]interface{}{"name": toolName, "arguments": ""}},
        },
    }, nil)
    fmt.Fprint(w, chunk)
    flusher.Flush()
    continue

case "tool-input-delta":
    inputDelta, _ := event["inputTextDelta"].(string)
    idx := toolCallIndex - 1
    if idx < 0 { idx = 0 }
    chunk := makeChunk(completionID, reqModel, created, map[string]interface{}{
        "tool_calls": []map[string]interface{}{
            {"index": idx, "function": map[string]interface{}{"arguments": inputDelta}},
        },
    }, nil)
    fmt.Fprint(w, chunk)
    flusher.Flush()
    continue

case "tool-input-end":
    continue  // no action needed for streaming
}
```

#### nonstream.go — tool_calls 收集

```go
var toolCalls []model.ToolCall
currentToolCallID := ""
currentToolName := ""
var currentArgs strings.Builder

// 在 switch 中:
case "tool-input-start":
    if currentToolCallID != "" {
        toolCalls = append(toolCalls, model.ToolCall{ID: currentToolCallID, Type: "function",
            Function: model.FunctionCall{Name: currentToolName, Arguments: currentArgs.String()}})
    }
    currentToolCallID, _ = event["toolCallId"].(string)
    if currentToolCallID == "" { currentToolCallID = uuid.New().String() }
    currentToolName, _ = event["toolName"].(string)
    currentArgs.Reset()
case "tool-input-delta":
    currentArgs.WriteString(event["inputTextDelta"].(string))
case "tool-input-end":
    if currentToolCallID != "" {
        toolCalls = append(toolCalls, model.ToolCall{...})
        currentToolCallID = ""  // reset
    }
case "finish":
    // finalize any pending tool call
    if currentToolCallID != "" { toolCalls = append(toolCalls, ...) }

// 组装响应时:
if len(toolCalls) > 0 {
    fr := "tool_calls"
    finishReason = fr
    msg.ToolCalls = toolCalls
}
```

## 八、Docker 部署

### 8.1 Dockerfile — Python 版

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY src/ src/
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["python", "app.py"]
```

### 8.2 Dockerfile — Go 版（多阶段构建）

```dockerfile
FROM golang:1.23-alpine AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o stockai2api .

FROM alpine:3.19
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /build/stockai2api .
EXPOSE 8267
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:8267/health || exit 1
CMD ["./stockai2api"]
```

### 8.3 部署三步曲

```bash
# 1. 同步
rsync -avz --exclude='.git' -e "sshpass -p PASSWORD ssh -o StrictHostKeyChecking=no" USER@HOST:/remote/path/ /local/path/

# 2. 重建（远程服务器上）
ssh USER@HOST "cd ~/project-dir && \
  echo PASSWORD | sudo -S docker stop CONTAINER 2>/dev/null; \
  echo PASSWORD | sudo -S docker rm CONTAINER 2>/dev/null; \
  echo PASSWORD | sudo -S docker compose up -d --build"

# 3. 验证
curl http://HOST:PORT/health
curl http://HOST:PORT/v1/models -H "Authorization: Bearer KEY"
curl -N http://HOST:PORT/v1/chat/completions \
  -H "Authorization: Bearer KEY" -H "Content-Type: application/json" \
  -d '{"model":"MODEL","messages":[{"role":"user","content":"Hi"}],"stream":true}'
```

## 七、陷阱清单

| 陷阱 | 解决方案 |
|------|---------|
| 模型 ID 含 `/` 导致 Hermes 解析失败 | 对外简洁名，内部映射到 `provider/model` |
| `/v1/models` 缺 `context_length` 导致 load fail | 必须返回 ≥ 64000 |
| 每次请求创建 httpx client | 全局单例 + 连接池 |
| `async with httpx.AsyncClient()` 关闭连接 | 只用 `client.stream()` 管理请求流 |
| 上游注入广告/水印 | 三层过滤：长关键词（data-text 整条丢弃）+ 短关键词（2-4字，delta 部分匹配）+ 广告状态机（检测到后连续丢弃直到 text-end/finish 重置）。⚠ 广告同时注入 reasoning-delta 和 text-delta，都要过滤 |
| system 消息上游不支持 | 跳过或拼入首条 user 消息 |
| **`role:"tool"` 消息上游不支持** | ⚠ Hermes agent loop 会发 `role:"tool"` 消息（含 `tool_call_id` 和 `content`），上游不接受会返回 500。必须转换为 user 消息，格式如 `[Tool Result (tool_call_id: xxx)]\n{content}`。Message struct 需新增 `ToolCallID` 字段 |
| `content` 格式差异 | 通用转换：string/list → parts[]/text/其他 |
| **`stream:false` 必须返回 JSON** | ⚠ 不能返回 SSE！Hermes 发 `stream:false` 时期望标准 `chat.completion` JSON 对象。方案：内部仍用 SSE 调上游，收集所有 content chunks，组装 `{"object":"chat.completion","choices":[{"message":{"role":"assistant","content":"..."}}]}` 返回。Go 实现见 7.6 节 |
| 上游 SSE buffer 不完整 | 按 `\n` 切分行，保留不完整行到 buffer |
| `data-text` 中 `Loading...` 占位 | 过滤掉 `Loading...` 文本 |
| 逆向成果未持久化 | 所有逆向成果保存到 `<工作目录>/web-reverse/<网站名>/`，含原始文件 + `knowledge-base.md`（LLM 可索引的结构化知识库） |
| Go 版 docker compose 端口被旧容器占用 | 先 `docker stop` + `docker rm` 旧容器，再 `docker compose up -d --build` |
| Go 全局 http.Client 未复用 | 必须包级变量初始化，设置 MaxIdleConns/MaxIdleConnsPerHost，不要每次请求创建 |
| Go SSE 必须每事件 Flush | `flusher.Flush()` 否则客户端收不到流式数据 |
| Go http.RequestWithContext | 用 `http.NewRequestWithContext(r.Context(), ...)` 传递客户端断开信号，避免上游响应时客户端已断开仍继续处理 |
| **Go `stream:false` 返回 SSE** | ⚠ 致命！Hermes 发 `stream:false` 时期望 `chat.completion` JSON，不是 SSE。必须实现 NonStreamChatCompletion：内部收集 SSE → 组装 JSON |
| **Go `role:"tool"` 未处理** | ⚪ 致命！Hermes agent loop 发 `role:"tool"` 消息，上游返回 500。必须在 ConvertRequest 中转为 user 消息 |
| Go main.go 编译错误 | 删除未使用的 import（如 `"os"`），Go 不允许未使用的 import |
| **`tools` 未转发给上游** | ⚠ 致命！Hermes agent loop 发 `tools` 定义 + `tool_choice`，如果代理不转发，LLM 不知道有工具可用，无法产生 tool_calls。必须：(1) ChatCompletionRequest 新增 `Tools []Tool` + `ToolChoice interface{}` 字段；(2) 转换 OpenAI tools 数组 → Vercel AI SDK tools map（key 是工具名，value 是 `{description, parameters}`）；(3) `tool_choice:"none"` → 不传 tools；`"required"` → 传 `toolChoice:"required"`；`"auto"` → 不设 toolChoice |
| **`tool-input-start/delta/end` 事件未转换** | ⚠ 致命！上游 LLM 产生工具调用时发送 `tool-input-start`（含 toolCallId, toolName）和 `tool-input-delta`（含 inputTextDelta），必须转换为 OpenAI 的 `tool_calls` chunk 格式。需要维护 `toolCallIndex` 递增计数器。stream 模式：每次 tool-input-start 生成含完整 id/name/arguments="" 的 chunk，tool-input-delta 生成含 arguments 增量的 chunk。non-stream 模式：收集所有 tool 事件，组装 `message.tool_calls` 字段，设 `finish_reason:"tool_calls"` |
| **Vercel AI SDK 服务端不转发 tools 给 LLM** | ⚠ 关键限制！Vercel AI SDK 的 `tools` 参数只在服务端 tool registry 注册，不传递给 LLM。**解决方案**：使用 Tool Call 模拟模式（见第八节），通过 prompt engineering + 标签解析实现 tool_call，无需上游原生支持 |
| **`tool-input-error` / `tool-output-error` 事件** | Vercel AI SDK 上游在工具执行失败时发送，当前代理应忽略（不转发给客户端），让模型继续文本回复 |

## 八、Tool Call 模拟模式（当上游不支持原生 function calling）

当上游 API（如 Vercel AI SDK 免费站点）不转发 `tools` 给 LLM 时，代理可自行实现 tool_call 循环。核心思路：**prompt engineering 注入工具描述 + 解析模型输出中的工具调用标签 → 转换为 OpenAI tool_calls 格式**。

### 8.1 何时启用

- 上游明确不返回 `tool-input-start/delta/end` 事件
- 上游的 Vercel AI SDK 不将 tools 传递给 LLM
- 需要与 Hermes agent loop 完整对接（agent loop 依赖 tool_calls）

### 8.2 Step 1: 工具描述注入

当请求包含 `tools` 时，在 system prompt 末尾追加工具描述：

```
You have access to the following tools:

<tools>
### tool_name
tool_description
Parameters: {"type":"object","properties":{...}}
To call a tool, output EXACTLY: <tool_call name="tool_name">{"arg1": "val1"}</tool_call >
</tools>

When you need to call a tool, output the tool call tag. Do NOT output anything else after a tool call.
If you don't need to call any tool, just respond normally.
```

**注意**：`</tool_call >` 闭合标签前有一个空格（`</tool_call >` 而非 `</tool_call >`），这是为了与常见的 XML 标签解析区分，实际正则应兼容两者。

### 8.3 Step 2: 解析模型输出

正则匹配 `<tool_call name="...">...</tool_call >`：

```go
var toolCallRegex = regexp.MustCompile(`<tool_call\s+name="([^"]+)">([\s\S]*?)</tool_call\s*>`)
```

**流式模式**：需要缓冲文本，检测是否包含 `<tool_call` 标签。使用 `IsPartialToolCall` 判断是否需要更多数据：

```go
func IsPartialToolCall(text string) bool {
    idx := strings.LastIndex(text, "<tool_call")
    if idx == -1 { return false }
    afterOpen := text[idx:]
    return !strings.Contains(afterOpen, "</tool_call")
}
```

**流式处理逻辑**：
1. 每收到 `text-delta`，追加到缓冲区
2. 如果 `IsPartialToolCall(fullText)` → 不输出，继续缓冲
3. 如果 `Parse(fullText)` 找到完整 tool_call → 转换为 OpenAI tool_calls 格式输出
4. 如果既不是部分也不是完整 → 正常流式输出（经过广告过滤）

### 8.4 Step 3: 转换为 OpenAI tool_calls 格式

```go
type OpenAIToolCall struct {
    ID       string       `json:"id"`
    Type     string       `json:"type"`
    Function FunctionCall `json:"function"`
}

type FunctionCall struct {
    Name      string `json:"name"`
    Arguments string `json:"arguments"`
}

// 生成 ID: "call_" + 24位随机字母数字
// 设置 finish_reason: "tool_calls"
```

**流式 chunk 格式**：
```json
{
  "choices": [{
    "delta": {
      "role": "assistant",
      "tool_calls": [{"index":0, "id":"call_xxx", "type":"function", "function":{"name":"get_weather","arguments":""}}]
    },
    "finish_reason": "tool_calls"
  }]
}
```

### 8.5 Step 4: Tool result 回传

当 Hermes 回传 `role:"tool"` 消息时，转换为文本：

```
// assistant 的 tool_calls → 文本
"I called the tool: <tool_call name=\"get_weather\">{\"city\":\"Beijing\"}</tool_call >"

// tool result → user 文本
"Tool result for get_weather: {\"temperature\": 24, \"condition\": \"sunny\"}"
```

### 8.6 ⚠️ 限制与注意事项

1. **模型遵从性**：免费模型几乎不遵循 tool prompt injection（XML 标签或 JSON 格式均无效）。这是免费模型的天生局限，prompt engineering 解决不了。实测 GLM-5.1、Llama-4-Scout、openrouter/free 等模型全部忽略工具调用指令，直接文本回复（经常幻觉答案）。**对于搜索类工具，应优先使用上游 `webSearch` 参数（见第九节）**
2. **流式延迟**：tool_call 检测需要缓冲，发现 `<tool_call` 标签后必须等闭合标签才能输出，增加了首 token 延迟
3. **多 tool call**：正则支持同一段文本中的多个 `<tool_call/>` 标签
4. **Arguments 解析**：标签内容必须是合法 JSON。如果不是，包装为 `{"value": "原始文本"}`
5. **与广告过滤的交互**：tool_call 文本也应经过广告过滤（广告可能插入在 tool_call 之前）
6. **`data-text` 事件中的模型不可用**：上游返回 `data-text` + "此模型暂时不可用" 时，需转为 `error` 事件处理

## 九、WebSearch 自动启用（Vercel AI SDK 上游）

### 9.1 发现

Vercel AI SDK 上游（如 free.stockai.trade）支持 `webSearch` 请求参数。设为 `true` 后，即使不传 `tools`，模型也能联网搜索并返回实时信息。这比 prompt injection 可靠得多——免费模型不遵循 tool prompt，但上游的 `webSearch` 是服务端功能，与模型遵从性无关。

### 9.2 自动检测与启用

当 Hermes 发来包含搜索类工具的请求时，代理应自动启用 `webSearch: true`：

```go
// converter/request.go
func ConvertRequest(req *OpenAIRequest) *UpstreamRequest {
    // 检测是否有搜索类工具
    hasWebSearch := false
    var nonSearchTools []Tool
    for _, t := range req.Tools {
        nameLower := strings.ToLower(t.Function.Name)
        if strings.Contains(nameLower, "search") ||
           strings.Contains(nameLower, "web") ||
           strings.Contains(nameLower, "browse") ||
           strings.Contains(nameLower, "fetch") {
            hasWebSearch = true
        } else {
            nonSearchTools = append(nonSearchTools, t)
        }
    }
    
    return &UpstreamRequest{
        WebSearch: hasWebSearch,  // 关键：自动启用
        // ...
    }
}
```

### 9.3 策略优先级

代理处理 tool_call 的完整优先级：

| 优先级 | 方式 | 条件 | 可靠性 |
|--------|------|------|--------|
| 1 | 上游原生 `tool-input-start/delta/end` SSE 事件 | 上游支持 function calling | ⭐⭐⭐ |
| 2 | `webSearch: true` 自动启用 | 请求含搜索类工具 | ⭐⭐⭐ |
| 3 | Prompt injection（XML 或 JSON 格式） | 上游不支持原生 tool calling | ⭐（免费模型几乎不遵循） |

### 9.4 ⚠ 注意事项

- `webSearch: true` 对多种模型有效（不仅是 `free-search` 模型），实测 `z-ai/glm-5.1` + `webSearch: true` 也能返回实时搜索结果
- 启用 `webSearch` 后，模型回答中可能包含 `source-url` SSE 事件（搜索来源链接），应转为 Markdown 链接格式输出
- `webSearch` 只解决"联网搜索"能力，不解决其他工具调用（如 read_file, terminal 等）。非搜索工具仍需 prompt injection（虽然成功率低）
- 代理应同时启用 `webSearch` 和注入 prompt（双保险），不要二选一
