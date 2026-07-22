---
name: web-api-reverse
description: Web API 协议逆向技能。破解 ChatGPT/OpenAI 等官网私有协议，还原 API 请求链、认证流、PoW/Turnstile 抗爬虫机制。对接 OpenAI 兼容接口适配层。包含 CF 绕过整合方案、号池管理、ONE App 实战案例。
category: reverse-engineering
tags: [web-api, protocol-reverse, chatgpt, openai, turnstile, pow]
---

# Web API 协议逆向 (统一技能)

## 适用场景

- 目标使用**私有/未公开 API 协议**（非标准 REST/GraphQL）
- 目标前端 SPA 与后端之间有**抗爬虫机制**（PoW、Turnstile、签名）
- 需要将私有 API 包装为**标准 OpenAI 兼容接口**
- 目标有**access_token + refresh_token** 认证体系

## 逆向方法论

### 阶段一：协议侦察

```bash
# 1. 捕获关键请求
# - 认证：login / oauth / token refresh
# - 核心业务：conversation / completion / generation
# - 辅助：chat-requirements / sentinel / captcha

# 2. 识别协议模式
# - backend-api/  vs  backend-anon/  （登录/匿名双链路）
# - SSE/Streaming 协议
# - 心跳/轮询协议
```

### 阶段二：指纹伪造（以 ChatGPT 为例）

```python
fingerprint = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Edge/143.0.0.0",
    "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", ...',
    "sec-ch-ua-platform": '"Windows"',
    "oai-device-id": uuid4(),  # 每次会话随机
    "oai-session-id": uuid4(),  # 每次会话随机
    "oai-client-version": "prod-a194cd...",  # 从官网提取
}
headers["X-OpenAI-Target-Path"] = path
headers["X-OpenAI-Target-Route"] = path
```

### 阶段三：抗爬虫绕过

#### PoW (Proof-of-Work)

```python
# chat-requirements 返回 PoW challenge
# 需要解析 sentinel/sdk.js 并计算 proof_token
def build_proof_token(challenge: dict, seed: str) -> str:
    # 1. 下载并解析 sdk.js
    # 2. 提取 proof-of-work 算法
    # 3. 根据 seed + difficulty 计算 proof_token
    # 4. 将 token 注入后续请求头
    pass
```

#### Turnstile (Cloudflare)

```python
# 偶发 captcha 挑战
# 需要对接 Turnstile solver
def solve_turnstile_token(site_key: str, page_url: str) -> str:
    # 方案1: SeleniumBase sb.solve_captcha()（推荐）
    # 方案2: Pydoll expect_and_bypass_cloudflare_captcha()
    # 方案3: Scrapling StealthyFetcher(solve_cloudflare=True)
    # 方案4: 第三方 solver (capsolver/2captcha)
    pass
```

### 阶段四：核心协议分析

#### 文本对话流
```
1. POST /backend-api/conversation/init  → 获取 conversation_id
2. POST /backend-api/conversation       → 流式 SSE 响应
   请求体包含：messages, model, conversation_id, ...
   响应体：SSE data: [DONE] 格式
```

#### 图片生成协议
```
1. 获取 account quota → GET /backend-api/accounts/check/v4-2023-04-27
2. POST /backend-api/conversation/image_gen → 发起生成任务
3. 轮询 GET /backend-api/conversation/{id}/image_gen/{img_id} → 等待完成
4. 从 image_storage_service 下载结果
```

### 阶段五：认证管理

```python
class AccessTokenManager:
    def __init__(self):
        self.accounts = []  # (access_token, email, quota)
    
    def refresh_quota(self, token):
        # GET /backend-api/me + /backend-api/accounts/check
        pass
    
    def rotate_token(self, invalid_token):
        # 剔除失效 token
        pass
    
    def get_available(self):
        # 返回有额度的可用 token
        pass
```

## 号池管理

| 功能 | 实现 |
|------|------|
| 多账号轮询 | access_token 池，按 round-robin 分配 |
| Token 失效检测 | 401 自动剔除，记录失效原因 |
| 额度监控 | 定时检查 image_gen quota、rate limit |
| 账号导入 | CPA 文件 / sub2api 服务 / OAuth login |

## 适配层：转换为 OpenAI 兼容接口

```python
# 路由映射
/v1/chat/completions   →  backend-api/conversation (streaming SSE)
/v1/images/generations →  backend-api/conversation/image_gen (polling)
/v1/models             →  硬编码模型列表
/v1/responses          →  Codex Responses API

# 关键转换
# 1. OpenAI 请求体 → ChatGPT 请求体（role/message 格式转换）
# 2. ChatGPT SSE 流 → OpenAI SSE 流（chunk 格式转换）
# 3. 错误码映射（OpenAI 格式 vs ChatGPT 格式）
```

## chatgpt2api 项目深度技术拆解

### 架构图

```
┌─ Client ──────────────────────────────┐
│  OpenAI API 兼容请求                     │
│  /v1/chat/completions                    │
│  /v1/images/generations                  │
│  /v1/responses                           │
└──────────────┬──────────────────────────┘
               ▼
┌─ API Layer (ai.py) ───────────────────┐
│  FastAPI Router                         │
│  Pydantic 请求校验                       │
│  LoggedCall 日志链路                     │
└──────────────┬──────────────────────────┘
               ▼
┌─ Protocol Layer (services/protocol/) ─┐
│  openai_v1_chat_complete                │
│  openai_v1_image_generations            │
│  openai_v1_response (Codex)             │
│  → 转换为 ChatGPT 内部格式               │
└──────────────┬──────────────────────────┘
               ▼
┌─ Backend Layer (openai_backend_api.py) ┐
│  OpenAIBackendAPI 类                    │
│  ● Fingerprint 伪造                     │
│  ● PoW/Turnstile 绕过                   │
│  ● 流式/轮询协议实现                     │
│  ● 多账号轮询                           │
└──────────────┬──────────────────────────┘
               ▼
┌─ ChatGPT 官网 ────────────────────────┐
│  chatgpt.com 后端 API                   │
└────────────────────────────────────────┘
```

### 关键协议端点

```
# 聊天流
POST /backend-api/sentinel/chat-requirements
  → 返回 requirements token (含 PoW challenge)
POST /backend-api/conversation
  → 流式 SSE 响应

# 图片生成
POST /backend-api/conversation/image_gen
GET  /backend-api/conversation/{id}/image_gen/{img_id}

# 账号管理
GET  /backend-api/me
POST /backend-api/conversation/init
GET  /backend-api/accounts/check/v4-2023-04-27
```

## ONE App 私有协议逆向实战案例

### 协议全景

```
┌─────────────────────────────────────────────────┐
│              ONE App API Protocol               │
├─────────────────────────────────────────────────┤
│  1. Bootstrap (POST, no token needed)            │
│     → /v2.5/bootstrap                           │
│     → Returns: user info + fresh JWT             │
│                                                  │
│  2. Article/Day (POST, needs JWT)               │
│     → /v2.5/article/day                         │
│     → Body: encrypted "published_at=YYYY-MM-DD" │
│     → Returns: article list with thumb URLs      │
│                                                  │
│  3. CDN Image (GET)                             │
│     → enimg.k8b3rsp.com/storage/thumb/...jpg    │
│     → Returns AES-ENCRYPTED JPEG data            │
│     → Decrypt with AES-128-CBC(img_key, img_iv)  │
│                                                  │
│  Headers (all requests):                         │
│  - uuid, user-key, timestamp, platform,          │
│    app-version, ip, sign, token                  │
│                                                  │
│  Sign: MD5(MD5(ip.platform.ts.uk.uuid) + salt)   │
│  AES: AES-128-CBC + PKCS7                        │
│  CDN AES: key="saIZXc4yMvq0Iz56",               │
│           iv="kbJYtBJUECT0oyjo"                  │
└─────────────────────────────────────────────────┘
```

### 逆向思路（七步走）

| Step | 问题 | 解法 | 关键发现 |
|------|------|------|----------|
| 1 | 入口在哪？ | Blutter 反编译 libapp.so | AES Key/IV/Salt 在构造函数里 |
| 2 | 请求格式？ | 分析 net_manager.dart | 明文→AES→Base64→form-encoded |
| 3 | Sign 算法？ | 反编译+抓包验证 | MD5(MD5(拼接) + salt) |
| 4 | 无 Token 入口？ | 搜索 bootstrap | POST /v2.5/bootstrap 不需要 JWT |
| 5 | 时间窗口？ | 分析 JWT iat 验证 | bootstrap → 立即调 API 有 10min 窗口 |
| 6 | CDN 在哪？ | Playwright 抓 Flutter Web | enimg.k8b3rsp.com 独立 CDN |
| 7 | 图片加密？ | 拦截 main.dart.js | CDN 图片是 AES 加密的 JPEG |

## 工具链

| 工具 | 用途 |
|------|------|
| Minis browser_use | 页面取证、抓包 |
| curl_cffi | TLS 指纹伪装 |
| SeleniumBase | CF 绕过 (UC+CDP) |
| Pydoll | 异步 CF 绕过 |
| Scrapling | 大规模爬取 + MCP |
| Python3 | 协议复现、加解密 |
| Burp Suite | 抓包分析 |
| JSRPC | 不补环境方案 |

## 任务完成自检

- [ ] 是否完整还原了认证流程？
- [ ] 是否记录了所有 API 端点？
- [ ] 是否验证了签名算法？
- [ ] 是否处理了 CF/PoW/Turnstile？
- [ ] 是否构建了号池管理？

