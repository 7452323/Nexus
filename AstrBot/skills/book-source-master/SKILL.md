# 书源大师 (Book Source Master)

## 描述
编写和调试 Legado 阅读3.0 App（"阅读3.0"）书源的全面指南。涵盖基于 API 和基于 HTML 的书源类型、字段映射、故障排除和密钥轮换策略。智能体使用此指南为任何小说网站创建书源。

## 指令

### 第一步：确定数据源类型

**A. API 型（推荐，最稳定）** — 网站通过 JSON API 返回数据。

识别方法：F12 开发者工具 → 网络 → XHR/Fetch 标签 → 查找 JSON 响应。

编写方法：使用 `@js:JSON.parse(result)` 解析 JSON。

**B. HTML 型（通用）** — 网站返回 HTML 页面。

识别方法：查看页面源代码 → 查找书籍列表的 HTML 标签。

编写方法：使用 `@css:` 选择器。

### 第二步：字段映射表

#### searchUrl
```
API 型： "https://api.example.com/search?q={{key}}&page=0"
HTML 型："https://site.com/search?q={{key}}"
```

`{{key}}` 由 App 自动替换为用户搜索的关键词。注意：是 `{{key}}`，不是 `{key}`。

#### ruleSearch — 解析搜索结果

| 字段 | API 型 | HTML 型 |
|-------|----------|-----------|
| `bookList` | `data.books` 或 `@js:` 迭代 | `@css:.book-item` |
| `name` | 字段名（如 `title`） | `@css:.title@text` |
| `author` | 字段名 | `@css:.author@text` |
| `bookUrl` | `@js:` 构造 URL | `@css:a@href` |
| `coverUrl` | 字段名 | `@css:img@src` |
| `intro` | 字段名（可选） | 可选 |

**bookUrl 必须是完整 URL。** 搜索结果通常只有 ID：

```json
"bookList": "@js:var r=JSON.parse(result);var list=r.data.books;if(list){for(var i=0;i<list.length;i++){list[i].bookUrl='https://example.com/detail?id='+list[i].id}}JSON.stringify(list);",
"bookUrl": "bookUrl"
```

**bookUrlPattern** — 填写 bookUrl 中的特征字符串用于匹配：
```
示例："type=2", "book_id=", "/detail/"
```

#### ruleBookInfo — 书籍详情

API 型：
```json
"ruleBookInfo": {
  "name": "@js:JSON.parse(result).data.book.title",
  "author": "@js:JSON.parse(result).data.book.author",
  "coverUrl": "@js:JSON.parse(result).data.book.cover",
  "intro": "@js:JSON.parse(result).data.book.intro",
  "tocUrl": "@js:'https://example.com/toc?id='+JSON.parse(result).data.book.id"
}
```

HTML 型：
```json
"ruleBookInfo": {
  "name": "@css:.book-title@text",
  "author": "@css:.book-author@text",
  "tocUrl": ""
}
```

#### ruleToc — 解析目录

每个章节必须有完整的内容 URL：

```json
"ruleToc": {
  "chapterList": "@js:var r=JSON.parse(result);var list=r.data.chapter_lists;for(var i=0;i<list.length;i++){list[i].cUrl='https://example.com/content?id='+r.data.id+'&cid='+list[i].id}JSON.stringify(list);",
  "chapterName": "title",
  "chapterUrl": "cUrl"
}
```

**注意：** 不要用 `chapterUrl` 作为字段名（这是 Legado 保留字）。请使用 `cUrl`。

#### ruleContent — 解析正文

API 型：
```json
"ruleContent": {
  "content": "@js:JSON.parse(result).data.content"
}
```

HTML 型：
```json
"ruleContent": {
  "content": "@css:#content@textNodes"
}
```

广告过滤（可选）：
```json
"ruleContent": {
  "content": "data.content",
  "replaceRegex": "广告|推广|赞助"
}
```

#### exploreUrl — 分类发现

在每个分类 URL 中传递搜索关键词：

```json
"exploreUrl": "<js>\nvar list=[\n{\"title\":\"🔥 推荐\",\"url\":\"https://example.com/search?key=推荐\"},\n{\"title\":\"📖 奇幻\",\"url\":\"https://example.com/search?key=奇幻\"}\n];JSON.stringify(list);\n</js>"
```

添加 `"enabledExplore": true` 启用。

### 第三步：密钥轮换（针对被限流的 API）

```json
"searchUrl": "<js>var _keys=[\"KEY1\",\"KEY2\",\"KEY3\"];var _idx=java.getGlobal(\"key_idx\");if(_idx===null)_idx=0;else _idx=(_idx+1)%_keys.length;java.putGlobal(\"key_idx\",_idx);var ak=_keys[_idx];java.put('key',key);result='https://example.com/search?key='+ak+'&wd='+encodeURIComponent(key)+'&page=0'</js>"
```

同样在 bookList、tocUrl、chapterList、content 中加入密钥轮换代码。

### 第四步：故障排除

| 症状 | 可能原因 | 解决方案 |
|---------|---------------|----------|
| 搜索无结果 | `{{key}}` 拼写错误 | 检查是 `{{key}}` 不是 `{key}` |
| 搜到结果但详情空白 | `bookUrl` 不完整 | 在 JS 中构造完整的 https:// 地址 |
| 详情页空白 | `bookUrlPattern` 不匹配 | 检查特征字符串是否出现在 URL 中 |
| 没有目录 | `tocUrl` 不正确 | 检查 ruleBookInfo 中的 tocUrl |
| 章节打不开 | `cUrl` 不完整 | 每个章节必须是完整 URL |
| 发现页不显示 | `enabledExplore` 未设置 | 添加 `"enabledExplore": true` |
| 密钥被限流 | 日用量已用完 | 轮换密钥或等待次日 |

### 第五步：调试

```bash
# 用 curl 测试 API
curl "https://api.example.com/search?q=test"

# 验证 JSON 语法
python3 -c "import json; json.load(open('source.json')); print('有效')"
```

浏览器 F12 → 网络 → 搜索 → 检查请求/响应结构。

### 第六步：完整检查清单

- [ ] 确定数据源（API 或 HTML）
- [ ] 用 curl 测试全部4个端点（搜索/详情/目录/正文）
- [ ] 编写 `searchUrl`
- [ ] 编写 `ruleSearch` + JS 构造 `bookUrl`
- [ ] 编写 `bookUrlPattern`
- [ ] 编写 `ruleBookInfo` + JS 构造 `tocUrl`
- [ ] 编写 `ruleToc` + JS 构造每个 `cUrl`
- [ ] 编写 `ruleContent`
- [ ] 可选编写 `exploreUrl`
- [ ] 用 python3 验证 JSON 语法
- [ ] 在 Legado 阅读3.0 中完整链测试

## 参数

| 参数名 | 类型 | 必填 | 描述 |
|-----------|------|----------|-------------|
| api_url | string | 是 | 小说网站 API 的基础 URL |
| search_query | string | 视情况 | 测试用的搜索关键词 |
| source_type | string | 是 | "api" 或 "html" |
| use_key_rotation | boolean | 否 | 启用密钥轮换（默认: false） |
| api_keys | string[] | 启用轮换时 | API 密钥列表 |

## 示例

### 为小说网站创建 API 型书源
```
用户："为 example.com 创建一个书源"
智能体：按照步骤1-6，测试每个端点并生成 JSON 源。
```

### 调试现有书源
```
用户："我的书源搜索时显示'无结果'"
智能体：检查 `{{key}}` 语法 → 验证 `bookUrlPattern` → 用 curl 测试 → 相应修复。
```

## 备注
- 始终使用 `cUrl` 而不是 `chapterUrl`（Legado 保留字冲突）
- `@js:` 前缀使用 Legado JS 引擎，不是浏览器/Node.js
- HTML 源使用 `@css:` 选择器；API 源使用 `@js:JSON.parse()`
- 导入 App 前验证 JSON 语法
- 密钥轮换必须添加到每个发起 API 调用的 `@js:` 块中
- 本指南仅适用于 Legado 阅读3.0 App 生态系统
