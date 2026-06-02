# Mergeek AI 搜索逆向案例 — 轮询式 AI 搜索

**日期**: 2026-05-05
**URL**: https://mergeek.com/zh/search
**类型**: 产品搜索 AI（查价格、找产品、问功能）
**模式**: 轮询式（非 SSE/WebSocket）

## 技术栈

- 前端：jQuery + Bootstrap + axios（非 SPA 框架，传统 SSR + jQuery 交互）
- CDN：cdn-static.mergeek.com（需 Referer header 才能下载 JS）
- 图片：weaver-images.oss-cn-beijing.aliyuncs.com（阿里云 OSS）
- 时序 API：time.mergeek.com

## 核心搜索流程

```
1. 用户输入 → sendMessage() → startSearch(query, session_key)
2. POST /search/go { session_key, query, scene_data?, scene_type? }
3. setInterval 500ms → searchResult(session_key)
4. GET /search/go/status?session_key=<key>
5. 返回: { search_status, ongoing_data, desc, cards, context, suggested_categories }
6. search_status == "success" → 停止轮询，渲染结果
7. 超时 60s → 显示错误
```

## API 端点完整列表

### 1. 发起搜索
```
POST /search/go
Headers: Time(UUID), Access-Token(可选), X-Requested-With: XMLHttpRequest
Body: { session_key: UUID, query: string, scene_data?: {project_id, project_name}, scene_type?: "inquiry_project" }
Response: { success: true, data: {} }
```

### 2. 轮询搜索状态
```
GET /search/go/status?session_key=<key>
Response: {
  success: true,
  data: {
    search_status: "ongoing" | "success",
    ongoing_data: [{ msg: "正在搜索..." }],  // 进行中提示
    desc: "<p>AI回复HTML</p>",
    cards: [{ project: {...}, pricing: {...}, promo_event: {...} }],
    suggested_categories: ["分类1"],
    context: { scene_data: {project_id, project_name}, scene_type, display: {icon, title} },
    user_intention: "find_project"
  }
}
```

### 3. 停止搜索
```
DELETE /search?session_key=<key>
```

### 4. 热门搜索（无需登录）
```
GET /search/trending
Response: { data: { hot: [...], find_price: [...], find_app: [...], find_features: [...], home_topics: [...], feat_cats: [...], project_count: N } }
```

### 5. 搜索历史
```
GET /go_project_histories
```

### 6. 项目详情
```
GET /search/projects?project_ids=<id>
```

### 7. 反馈
```
POST /go_feedbacks { content, email }
```

## 认证机制

- **Time header**: UUID 格式，首次 `timeGenerator()` 生成，存 localStorage，每请求必带
- **Access-Token**: OAuth2 token，登录后获取，未登录可搜索但有 IP 限制（每日有限次数）
- **自动刷新**: axios 拦截器自动处理 OauthTokenExpiredError → PUT /oauth 刷新

## 对话上下文机制

- `session_chat_context` 存 sessionStorage
- 搜索成功后返回 `context` 字段 → 自动更新
- 后续搜索带上 `scene_data` + `scene_type` → 实现连续对话
- 点击产品卡片触发 `showProjectData(id, name)` → 设置 context 后重搜

## JS 文件清单

| 文件 | CDN 路径模式 | 大小 | 内容 |
|------|-------------|------|------|
| magic_go/app-*.js | cdn-static.mergeek.com/assets/magic_go/ | 39KB | 搜索核心：sendMessage, startSearch, searchResult, stopSearch |
| must/app-*.js | cdn-static.mergeek.com/assets/must/ | 144KB | 通用：axios配置, OauthToken, Storage, auth, jQuery |
| bootstrap/bootstrap-*.js | cdn-static.mergeek.com/assets/bootstrap/ | 78KB | Bootstrap 框架 |
| login/app-*.js | cdn-static.mergeek.com/assets/login/ | — | 登录模块 |
| redux_states/app-*.js | cdn-static.mergeek.com/assets/redux_states/ | — | 状态管理 |

## 逆向方法总结

1. **CDN JS 下载需 Referer** — 直接 curl 返回 403，加 `-H "Referer: https://mergeek.com/"` 后成功
2. **API 路径均为相对路径** — `grep -oE 'https?://...'` 命中 0 个 API 端点；改用 `grep -n 'axios\.'` 才提取到 `/search/go`、`/search/go/status` 等
3. **Lightpanda hook 失效** — fetch/XHR hook 和 performance API 均捕获不到 SPA 动态请求；静态 JS 分析更可靠
4. **轮询模式识别** — 搜索 `setInterval` + `axios.get` 组合，500ms 间隔轮询
5. **curl 直接验证 API** — 无需登录即可调用 trending 和 search API（有 IP 限制）

## search_status 状态流转

```
用户输入 → POST /search/go → 轮询 GET /search/go/status
  │
  ├── "ongoing" → ongoing_data[0].msg 更新进度
  │
  └── "success" → desc(HTML) + cards(产品) + context(上下文) + suggested_categories
```
