1|---
2|name: web-api-protocol-reverse
3|description: Web API 协议逆向技能。破解 ChatGPT/OpenAI 等官网私有协议，还原 API 请求链、认证流、PoW/Turnstile 抗爬虫机制。对接 OpenAI 兼容接口适配层。
4|author: 7452323 (converted from Private Gist + chatgpt2api逆向)
5|category: reverse-engineering
6|tags:
7|  - web-api
8|  - protocol-reverse
9|  - chatgpt
10|  - openai
11|  - turnstile
12|  - pow
13|---
14|
15|# Web API Protocol Reverse — Web API 协议逆向
16|
17|## 适用场景
18|
19|- 目标使用**私有/未公开 API 协议**（非标准 REST/GraphQL）
20|- 目标前端 SPA 与后端之间有**抗爬虫机制**（PoW、Turnstile、签名）
21|- 需要将私有 API 包装为**标准 OpenAI 兼容接口**
22|- 目标有**access_token + refresh_token** 认证体系
23|
24|## 逆向方法论
25|
26|### 阶段一：协议侦察
27|
28|```bash
29|# 1. 捕获关键请求
30|# - 认证：login / oauth / token refresh
31|# - 核心业务：conversation / completion / generation
32|# - 辅助：chat-requirements / sentinel / captcha
33|
34|# 2. 识别协议模式
35|# - backend-api/  vs  backend-anon/  （登录/匿名双链路）
36|# - SSE/Streaming 协议
37|# - 心跳/轮询协议
38|```
39|
40|### 阶段二：指纹伪造（以 ChatGPT 为例）
41|
42|```python
43|# 浏览器指纹栈 — 必须与请求头完全一致
44|fingerprint = {
45|    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Edge/143.0.0.0",
46|    "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", ...',
47|    "sec-ch-ua-platform": '"Windows"',
48|    "oai-device-id": uuid4(),  # 每次会话随机
49|    "oai-session-id": uuid4(),  # 每次会话随机
50|    "oai-client-version": "prod-a194cd...",  # 从官网提取
51|}
52|
53|# 必须添加的请求头
54|headers["X-OpenAI-Target-Path"] = path
55|headers["X-OpenAI-Target-Route"] = path
56|```
57|
58|### 阶段三：抗爬虫绕过
59|
60|#### PoW (Proof-of-Work)
61|```python
62|# chat-requirements 返回 PoW challenge
63|# 需要解析 sentinel/sdk.js 并计算 proof_token
64|# 实现见 utils/pow.py
65|def build_proof_token(challenge: dict, seed: str) -> str:
66|    pass
67|```
68|
69|#### Turnstile (Cloudflare)
70|```python
71|# 偶发 captcha 挑战
72|# 需要对接 Turnstile solver
73|# 实现见 utils/turnstile.py
74|def solve_turnstile_token(site_key: str, page_url: str) -> str:
75|    pass
76|```
77|
78|### 阶段四：核心协议分析
79|
80|#### 文本对话流
81|```
82|1. POST /backend-api/conversation/init  → 获取 conversation_id
83|2. POST /backend-api/conversation       → 流式 SSE 响应
84|   请求体包含：messages, model, conversation_id, ...
85|   响应体：SSE data: [DONE] 格式
86|```
87|
88|#### 图片生成协议
89|```
90|1. 获取 account quota → GET /backend-api/accounts/check/v4-2023-04-27
91|2. POST /backend-api/conversation/image_gen → 发起生成任务
92|3. 轮询 GET /backend-api/conversation/{id}/image_gen/{img_id} → 等待完成
93|4. 从 image_storage_service 下载结果
94|```
95|
96|#### 可编辑文件生成 (PPT/PSD)
97|```
98|1. POST /backend-api/conversation → 发起可编辑文件请求
99|2. 拦截 attachment / artifact 中的 sandbox 路径
100|3. 从 file-service:// 下载生成的素材
101|4. 组装为可下载的附件
102|```
103|
104|### 阶段五：认证管理
105|
106|```python
107|# access_token 管理
108|class AccessTokenManager:
109|    def __init__(self):
110|        self.accounts = []  # (access_token, email, quota)
111|    
112|    def refresh_quota(self, token):
113|        # GET /backend-api/me + /backend-api/accounts/check
114|        pass
115|    
116|    def rotate_token(self, invalid_token):
117|        # 剔除失效 token
118|        pass
119|    
120|    def get_available(self):
121|        # 返回有额度的可用 token
122|        pass
123|```
124|
125|## 号池管理
126|
127|| 功能 | 实现 |
128||------|------|
129|| 多账号轮询 | access_token 池，按 round-robin 分配 |
130|| Token 失效检测 | 401 自动剔除，记录失效原因 |
131|| 额度监控 | 定时检查 image_gen quota、rate limit |
132|| 账号导入 | CPA 文件 / sub2api 服务 / OAuth login |
133|
134|## 号池导入方式
135|
136|### CPA 文件导入
137|```json
138|[
139|  {
140|    "access_token": "eyJhbGciOi...",
141|    "email": "user@example.com",
142|    "fp": {"user-agent": "...", "impersonate": "edge101"}
143|  }
144|]
145|```
146|
147|### sub2api 导入
148|从 sub2api 服务器拉取 OpenAI OAuth 账号并批量导入。
149|
150|### OAuth Login
151|通过 Chrome DevTools Protocol 自动化完成 OAuth 登录，提取 access_token。
152|
153|## 适配层：转换为 OpenAI 兼容接口
154|
155|```python
156|# 路由映射
157|/v1/chat/completions   →  backend-api/conversation (streaming SSE)
158|/v1/images/generations →  backend-api/conversation/image_gen (polling)
159|/v1/models             →  硬编码模型列表
160|/v1/responses          →  Codex Responses API
161|
162|# 关键转换
163|# 1. OpenAI 请求体 → ChatGPT 请求体（role/message 格式转换）
164|# 2. ChatGPT SSE 流 → OpenAI SSE 流（chunk 格式转换）
165|# 3. 错误码映射（OpenAI 格式 vs ChatGPT 格式）
166|```
167|
168|## chatgpt2api 项目深度技术拆解
169|
170|### 架构图
171|
172|```
173|┌─ Client ──────────────────────────────┐
174|│  OpenAI API 兼容请求                     │
175|│  /v1/chat/completions                    │
176|│  /v1/images/generations                  │
177|│  /v1/images/edits                        │
178|│  /v1/responses                           │
179|│  /v1/messages (Anthropic)                │
180|│  /v1/search                              │
181|│  /v1/ppt/generations                     │
182|│  /v1/psd/generations                     │
183|└──────────────┬──────────────────────────┘
184|               │
185|               ▼
186|┌─ API Layer (ai.py) ───────────────────┐
187|│  FastAPI Router                         │
188|│  Pydantic 请求校验                       │
189|│  LoggedCall 日志链路                     │
190|│  content_filter 安全检查                 │
191|│  identity 认证验证                       │
192|└──────────────┬──────────────────────────┘
193|               │
194|               ▼
195|┌─ Protocol Layer (services/protocol/) ─┐
196|│  openai_v1_image_generations            │
197|│  openai_v1_image_edit                   │
198|│  openai_v1_chat_complete                │
199|│  openai_v1_response (Codex)             │
200|│  anthropic_v1_messages                  │
201|│  openai_search                          │
202|│                                         │
203|│  → 转换 OpenAI/Anthropic 请求体         │
204|│    为 ChatGPT 内部格式                   │
205|│  → 调用 OpenAIBackendAPI                │
206|└──────────────┬──────────────────────────┘
207|               │
208|               ▼
209|┌─ Backend Layer (openai_backend_api.py) ┐
210|│  OpenAIBackendAPI 类                    │
211|│  ● Fingerprint 伪造                     │
212|│  ● PoW/Turnstile 绕过                   │
213|│  ● 流式/轮询协议实现                     │
214|│  ● 多账号轮询                           │
215|│  ● 缓存 & 去重                          │
216|└──────────────┬──────────────────────────┘
217|               │
218|               ▼
219|┌─ ChatGPT 官网 ────────────────────────┐
220|│  chatgpt.com 后端 API                   │
221|│  backend-api/sentinel/...               │
222|│  backend-api/conversation/...           │
223|│  backend-api/accounts/...               │
224|└────────────────────────────────────────┘
225|```
226|
227|### OpenAIBackendAPI 核心类详解
228|
229|| 方法 | 作用 | 技术要点 |
230||------|------|----------|
231|| `_build_fp()` | 构造浏览器指纹 | 伪 Edge101、随机 OAI-Device-Id/Session-Id |
232|| `_headers()` | 构造完备请求头 | `X-OpenAI-Target-Path`/`X-OpenAI-Target-Route` |
233|| `_get_chat_requirements()` | 获取 sentinel token (PoW+Turnstile) | 解析 sdk.js 返回的 challenge |
234|| `_get_conversation()` | 流式对话请求 | SSE 流，`data: [DONE]` 终止 |
235|| `_get_image_gen()` | 发起图片生成 | 轮询等待机制 |
236|| `get_user_info()` | 查询账号额度/类型 | 并行 3 请求 (me+init+account) |
237|| `stream_conversation()` | 底层统一流式入口 | 登录/未登录双链路 |
238|
239|### 关键协议端点
240|
241|```
242|# 聊天流
243|POST /backend-api/sentinel/chat-requirements
244|  → 返回 requirements token (含 PoW challenge)
245|POST /backend-api/conversation
246|  → 流式 SSE 响应
247|  → 请求体: {messages, model, conversation_id, ...}
248|  → 特殊情况：conversation_id 为 None 时自动创建新对话
249|
250|# 图片生成
251|POST /backend-api/conversation/image_gen
252|  → 返回 image_gen_id
253|GET  /backend-api/conversation/{id}/image_gen/{img_id}
254|  → 轮询直到返回结果
255|
256|# 账号管理
257|GET  /backend-api/me                          → 用户基本信息
258|POST /backend-api/conversation/init           → 获取 limits_progress (额度)
259|GET  /backend-api/accounts/check/v4-2023-04-27 → 完整账号信息
260|```
261|
262|### PoW (Proof-of-Work) 实现详情
263|
264|```python
265|# 从 chat-requirements 响应中提取 PoW seed
266|# 使用 sentinel/sdk.js 中的算法计算 proof_token
267|#
268|# 关键参数：
269|# - seed: 服务端下发的种子字符串
270|# - difficulty: PoW 难度（影响计算时间）
271|# - expires_at: token 过期时间
272|#
273|# 流程：
274|# 1. 下载并解析 sdk.js
275|# 2. 提取 proof-of-work 算法
276|# 3. 根据 seed + difficulty 计算 proof_token
277|# 4. 将 token 注入后续请求头
278|#
279|# 实现文件: utils/pow.py
280|```
281|
282|### Turnstile 绕过
283|
284|```python
285|# Cloudflare Turnstile 验证
286|# 偶发触发，非每次请求都需要
287|# 实现文件: utils/turnstile.py
288|#
289|# 方案：
290|# 1. 使用第三方 solver (capsolver/2captcha)
291|# 2. 维护已解好的 token 缓存
292|# 3. token 过期自动重新求解
293|```
294|
295|### 号池管理深度细节
296|
297|```python
298|# 账号状态管理
299|class AccountPool:
300|    - access_token_pool: list[dict]  # 每个账号含 token + 元数据
301|    - round_robin_index: int         # 轮询指针
302|    - invalid_tokens: set            # 失效 token 黑名单
303|    - quota_cache: dict              # 额度缓存 (有效期 5 分钟)
304|
305|# 自动刷新机制
306|# - 定时任务: 每 30 分钟刷新所有账号额度
307|# - 请求失败触发: 401 时立即剔除并尝试下一个
308|# - 限流恢复: 429 时记录恢复时间，到期后重新可用
309|```
310|
311|### 可编辑文件生成协议 (PPT/PSD)
312|
313|```
314|1. POST /backend-api/conversation 使用 editable_file model (gpt-5-5-thinking)
315|2. 在 SSE 流中拦截 attachment/artifact
316|3. 从 artifact 中提取 sandbox 路径 (sandbox:/mnt/data/...)
317|4. 使用 file-service:// 协议下载生成的素材
318|5. 组装为最终可下载文件 (PPTX/ZIP)
319|
320|关键实现：
321|- EDITABLE_PPT_PROMPT: 让模型生成可编辑 PPT 的 system prompt
322|- EDITABLE_PSD_PROMPT: 让模型生成可编辑 PSD 的系统 prompt
323|- 素材拆分为单独 PNG 再拼接
324|```
325|
326|### 代理/指纹管理
327|
328|```python
329|# 代理支持
330|# - HTTP/HTTPS/SOCKS5/SOCKS5H
331|# - 每账号独立代理配置
332|# - 使用 curl_cffi 库（支持指纹模仿）
333|
334|# Proxy 配置结构
335|{
336|    "protocol": "http",      # http|https|socks5|socks5h
337|    "host": "127.0.0.1",
338|    "port": 7890,
339|    "username": "",         # 可选
340|    "password": "",         # 可选
341|    "mode": "direct"        # direct|global|rule
342|}
343|```
344|
345|### 可复用经验总结
346|
347|| 技术点 | 可复用性 | Hermes 对应 |
348||--------|----------|-------------|
349|| PoW 绕过 | 低 | 协议特定，每目标需重写 |
350|| Turnstile 求解 | 低 | 需第三方 solver |
351|| Fingerprint 伪造 | 高 | Hermes browser tool 已内置 |
352|| 号池轮询 | 高 | Hermes credential pool 已内置 |
353|| OpenAI 协议适配 | 高 | 直接复用为 Hermes provider |
354|| SSE 流式解析 | 中 | 需定制 stream parser |
355|| 多账号 OAuth 获取 | 中 | 用 browser tool 自动化 |
356|
357|## 参考资源
358|
359|- `references/chatgpt2api-protocol-analysis.md` — chatgpt2api 协议逆向深度分析
360|- `references/openai-backend-api-reference.md` — OpenAIBackendAPI 类文档
361|

## ONE App 私有协议逆向实战案例

基于 ONE·一个（成人版）Flutter App 的 API 逆向实战。

### 协议全景

```
┌─────────────────────────────────────────────────┐
│              ONE App API Protocol               │
├─────────────────────────────────────────────────┤
│                                                  │
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

### 与本技能的其他技术对比

| 维度 | ChatGPT 协议 | ONE App 协议 |
|------|-------------|-------------|
| 认证 | access_token (Bearer) | uuid + user-key + sign → JWT |
| 请求加密 | 明文 | AES-128-CBC + Base64 |
| 响应加密 | 明文 | AES-128-CBC + Base64 |
| 抗爬虫 | PoW + Turnstile | IP 绑定 + 签名 + 时间窗口 |
| 静态文件 | 独立 CDN | 独立 CDN（但文件是 AES 加密的） |
| 反编译难度 | 无（Web SPA） | 高（Flutter libapp.so） |
