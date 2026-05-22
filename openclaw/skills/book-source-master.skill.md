# 书源大湿 — Legado 阅读3.0 书源编写技能

有了这个技能，就能写出任何小说网站的书源。覆盖 API 接口型和 HTML 网页型两种写法，从字段对照到问题排查到调试技巧。

## 书源是什么

书源是一个 JSON 文件，告诉「阅读3.0」App 怎么从一个网站提取小说数据。完整链路：

```
搜索 -> 书籍列表 -> 书籍详情 -> 目录 -> 正文
```

对应的 JSON 字段：

|环节|JSON 字段|
|---|---|
|搜索请求|`searchUrl`|
|解析搜索结果|`ruleSearch`|
|解析书籍详情|`ruleBookInfo`|
|解析目录|`ruleToc`|
|解析正文|`ruleContent`|
|分类发现|`exploreUrl`|

---

## 第一步：确定数据来源

### A. API 接口型（首选，最稳定）

网站通过 JSON API 返回数据。

特征：浏览器 F12 -> Network -> XHR/Fetch，能看到返回 JSON 的请求。

写法：用 `@js:JSON.parse(result)` 解析 JSON。

### B. HTML 网页型（通用）

网站返回 HTML 页面。

特征：右键查看网页源代码，能看到书籍列表的 HTML 标签。

写法：用 `@css:` 选择器。

---

## 第二步：字段对照表

### searchUrl

```
API型:  "https://api.example.com/search?q={{key}}&page=0"
HTML型: "https://site.com/search?q={{key}}"
```

`{{key}}` 是 App 自动替换为用户输入的关键词。注意是 `{{key}}` 不是 `{key}`。

### ruleSearch — 解析搜索结果

|字段|API 型写法|HTML 型写法|
|---|---|---|
|`bookList`|`data.books` 或 `@js:` 遍历|`@css:.book-item`|
|`name`|字段名（如 `title`）|`@css:.title@text`|
|`author`|字段名|可直接写死或 `@css:.author@text`|
|`bookUrl`|`@js:` 拼 URL|`@css:a@href`|
|`coverUrl`|字段名|`@css:img@src`|
|`intro`|字段名|可选|

**bookUrl 必须拼完整 URL。** 搜索结果通常只有 ID，需要构造完整地址：

```json
"bookList": "@js:var r=JSON.parse(result);var list=r.data.books;if(list){for(var i=0;i<list.length;i++){list[i].bookUrl='https://example.com/detail?id='+list[i].id}}JSON.stringify(list);",
"bookUrl": "bookUrl"
```

**bookUrlPattern** 填 bookUrl 里固定的特征字符串，用于匹配书源：
```
例: "type=2"、"book_id="、"/detail/"
```

### ruleBookInfo — 书籍详情

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

### ruleToc — 解析目录

每条章节必须拼出完整的正文 URL：

```json
"ruleToc": {
  "chapterList": "@js:var r=JSON.parse(result);var list=r.data.chapter_lists;for(var i=0;i<list.length;i++){list[i].cUrl='https://example.com/content?id='+r.data.id+'&cid='+list[i].id}JSON.stringify(list);",
  "chapterName": "title",
  "chapterUrl": "cUrl"
}
```

**注意：** 字段名不要用 `chapterUrl`（Legado 保留字），用 `cUrl` 代替。

### ruleContent — 解析正文

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

广告过滤（选加）：
```json
"ruleContent": {
  "content": "data.content",
  "replaceRegex": "广告|推广|首发于"
}
```

### exploreUrl — 分类发现

需要在每个分类 URL 里传**真实搜索关键词**，不要用 `***` 占位符：

```json
"exploreUrl": "<js>\nvar h='https://api.example.com';\nvar list=[\n{\"title\":\"🔥 推荐\",\"url\":h+'/api/search?key=推荐&page_size=20'},\n{\"title\":\"📖 玄幻\",\"url\":h+'/api/search?key=玄幻&page_size=20'},\n{\"title\":\"📖 都市\",\"url\":h+'/api/search?key=都市&page_size=20'}\n];JSON.stringify(list);\n</js>"
```

> ⚠️ **不要用 `key=***`**：很多 API 不认识 `***` 这个占位符，会返回空结果。每个分类填真实关键词（如 `key=玄幻`）。

记得加 `"enabledExplore": true`。

---

## 第三步：分页（翻页）写法 ⭐

这是书源体验的关键。很多书源只有第一页，就是因为缺了分页参数。

### 3.1 认识 `{{page}}` 和 `page` 变量

Legado 提供两种分页机制：

|方式|适用场景|示例|
|---|---|---|
|`{{page}}` URL 占位符|纯 URL 字符串（非 JS 表达式）|`?page={{page}}` → `?page=1`|
|`page` JS 变量|`<js>` 或 `@js:` 表达式中|`var p=page!=null?page:1`|

### 3.2 纯 URL 写法（简单 API）

如果 API 直接用 `page` 参数（1-based）：

```
API型:  "https://api.example.com/search?q={{key}}&page={{page}}"
HTML型: "https://site.com/search?q={{key}}&page={{page}}"
```

Legado 自动把 `{{page}}` 替换成 1, 2, 3…

### 3.3 JS 写法（offset 类 API）

如果 API 用 offset 分页（0-based，如 offset=0, 10, 20…），需要用 JS 计算：

```json
"searchUrl": "<js>var p=page!=null?page:1;result='https://api.example.com/search?q='+encodeURIComponent(key)+'&offset='+((p-1)*10)</js>"
```

公式：`offset = (page - 1) × 每页条数`

### 3.4 ⚠️ 关键陷阱：`page` 是 `null` 不是 `undefined`

Legado 源码（`AnalyzeUrl.kt`）中：

```kotlin
bindings["page"] = page  // page 是 Int?（可空类型）
```

首次搜索时 `page = null`（不是 `undefined`！）。所以：

```javascript
// ❌ 错误写法 - page=null 时 [null-1=-1]，请求全炸
typeof page !== 'undefined' ? page : 1   // → null（因为 typeof null ≠ 'undefined'）

// ✅ 正确写法
page != null ? page : 1                   // → 1（null 判空正确）
page || 1                                 // → 1（利用 JS 真值）
```

### 3.5 exploreUrl 发现页分页

发现页的每条分类 URL 也要加 `{{page}}`：

```json
"exploreUrl": "<js>\nvar h='https://api.example.com';\nvar list=[\n{\"title\":\"🔥 推荐\",\"url\":h+'/api/search?key=推荐&offset={{page}}'},\n{\"title\":\"📖 玄幻\",\"url\":h+'/api/search?key=玄幻&offset={{page}}'}\n];JSON.stringify(list);\n</js>"
```

> **注意：** `{{page}}` 从 1 开始。如果你的 API 用 0-based offset，第1页会从 offset=1 开始（少第1条数据），在不追求绝对精确的场景可以接受。

### 3.6 分页工作原理解析

Legado 处理分页的流程（源码 `AnalyzeUrl.kt`）：

1. **执行 `<js>`** → 生成 URL 字符串
2. **替换 `{{page}}`** → 用 `page` 值替换 URL 中的 `{{page}}` 占位符
3. **请求** → 发送生成好的 URL

关键细节：
- `{{page}}` 替换只在 `page != null` 时执行（`page?.let {}`）
- 所以当 `page = null` 时，`{{page}}` 不变，会导致 URL 失效 → 所以有些书源填 `{{page}}` 后发现页全空
- 用 `<js>` 表达式时，`page` 变量始终可用（即使为 null）

---

## 第四步：Key 轮换写法

当 API 有每日限额时，多个 Key 轮换使用：

```json
"searchUrl": "<js>var _keys=[\"KEY1\",\"KEY2\",\"KEY3\"];var _idx=java.getGlobal(\"key_idx\");if(_idx===null)_idx=0;else _idx=(_idx+1)%_keys.length;java.putGlobal(\"key_idx\",_idx);var ak=_keys[_idx];java.put('key',key);result='https://example.com/search?key='+ak+'&wd='+encodeURIComponent(key)+'&page=0'</js>"
```

bookList、tocUrl、chapterList、content 里同样要加这段轮换逻辑：
- 每个 @js: 开头插入 Key 轮换代码
- URL 中的 Key 替换成 `"+ak+"`（@js: 中）或 `'+ak+'`（<js> 中）

> ⚠️ **注意**：Key 轮换和分页一起用时，别忘了分页参数也要带上，否则翻页失效。

---

## 第五步：常见问题排查

|症状|可能原因|解决方法|
|---|---|---|
|搜不到结果|`{{key}}` 拼错|检查是 `{{key}}` 不是 `{key}`|
|搜到但点进去空白|`bookUrl` 不完整|JS 里拼完整 https:// 地址|
|点进去空白|`bookUrlPattern` 不匹配|特征字符串是否在 URL 里出现|
|有详情没目录|`tocUrl` 不对|检查 ruleBookInfo 里的 tocUrl|
|有目录点不开|`cUrl` 没拼全|每条章节必须是完整 URL|
|发现页不显示|`enabledExplore` 没开|加 `"enabledExplore": true`|
|发现页全空|`key=***` 不识别|换成真实关键词（如 `key=玄幻`）|
|搜索只有第一页|`searchUrl` 没分页|加 `{{page}}` 或用 JS 算 offset|
|发现页只显示一页|`exploreUrl` 没分页|每个 URL 加 `&offset={{page}}`|
|加了分页反而全空|`page` 判空错误|用 `page!=null` 不是 `typeof`|
|Key 被限额|当日次数用完|换 Key 或等第二天|

---

## 第六步：调试技巧

```bash
# curl 测试 API
curl "https://api.example.com/search?q=测试"
# 看返回的 JSON 结构，字段名照抄到书源里

# 测试分页
curl "https://api.example.com/search?q=测试&offset=0"
curl "https://api.example.com/search?q=测试&offset=10"

# 验证 JSON 语法
python3 -c "import json; json.load(open('书源.json')); print('合法')"
```

浏览器 F12 -> Network -> 搜一次小说 -> 看请求和返回结构。

**高级调试：** 开启阅读3.0的「记录日志」，看 `[TOC-JS-RESULT]` 和 `[getHttpResponse]` 日志能定位大部分问题。

---

## 第七步：完整流程清单

- [ ] 确定数据来源（API 还是 HTML）
- [ ] curl 测试搜索/详情/目录/正文四个接口
- [ ] curl 测试分页参数（如果 API 支持）
- [ ] 写 `searchUrl` + 分页（`{{page}}` 或 JS offset）
- [ ] 写 `ruleSearch` + JS 拼 `bookUrl`
- [ ] 写 `bookUrlPattern`
- [ ] 写 `ruleBookInfo` + JS 拼 `tocUrl`
- [ ] 写 `ruleToc` + JS 拼每条 `cUrl`
- [ ] 写 `ruleContent`
- [ ] 要分类发现就写 `exploreUrl`（用真实关键词 + 分页）
- [ ] python3 验证 JSON 语法
- [ ] 导入阅读3.0 全链路测试
- [ ] 测试搜索翻页（搜关键词 → 下拉）
- [ ] 测试发现翻页（点分类 → 下拉）
