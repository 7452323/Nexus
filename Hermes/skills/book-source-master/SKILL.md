---
name: book-source-master
description: "Legado 阅读3.0 书源编写技能 — 从零写出任何小说/漫画/视频网站的书源。覆盖纯API型/纯HTML型/JS动态型/聚合型/视频型6种完整模板，含Key轮换、分页陷阱、反混淆实战。"
author: 7452323 (OpenClaw → Hermes 合并版 v3.0)
version: 3.0.0
tags:
  - legado
  - book-source
  - web-scraping
  - novels
  - reverse-engineering
---

# 书源大湿 v3 — Legado 阅读3.0 书源编写技能

> 基于 OpenClaw 番茄写法 + Yiove 仓库 31132 个现成书源逆向分析，合并为完整技能。

有了这个技能，你能写出**任何**小说网站、漫画站、视频站的书源。

## 书源是什么

书源是一个 JSON 文件，告诉「阅读3.0」App 怎么从一个网站提取数据。完整链路：

```
搜索(searchUrl+ruleSearch) → 详情(ruleBookInfo) → 目录(ruleToc) → 正文(ruleContent) → 发现(exploreUrl)
```

对应的 JSON 字段：

| 环节 | JSON 字段 |
|------|-----------|
| 搜索请求 | `searchUrl` |
| 解析搜索结果 | `ruleSearch` |
| 解析书籍详情 | `ruleBookInfo` |
| 解析目录 | `ruleToc` |
| 解析正文 | `ruleContent` |
| 分类发现 | `exploreUrl` |
| JS 库（通用函数） | `jsLib` |
| 源类型 | `bookSourceType`（0=文本 4=视频） |
| 网站地址 | `bookSourceUrl` |

---

## 第一步：确定书源类型（选对模板）

### 1. 纯 API 型 — 最稳定 ⭐首选

**特征**：F12 → Network → XHR/Fetch，能看到返回 JSON 的请求。

**用法**：`$.字段名` 直接取 JSON 字段。

完整模板：
```json
{
  "bookSourceGroup": "我的书源",
  "bookSourceName": "示例API书源",
  "bookSourceUrl": "https://api.example.com",
  "bookSourceType": 0,
  "enabled": true,
  "enabledExplore": true,
  "searchUrl": "https://api.example.com/search?q={{key}}&page={{page}}",
  "ruleSearch": {
    "bookList": "$.data.list",
    "name": "$.title",
    "author": "$.author",
    "coverUrl": "$.cover",
    "bookUrl": "$.id@js:'https://api.example.com/book/'+result",
    "kind": "$.category",
    "intro": "$.intro",
    "lastChapter": "$.last_chapter",
    "wordCount": "$.words"
  },
  "ruleBookInfo": {
    "name": "$.data.book.title",
    "author": "$.data.book.author",
    "coverUrl": "$.data.book.cover",
    "intro": "$.data.book.intro",
    "kind": "$.data.book.category",
    "lastChapter": "$.data.book.last_chapter",
    "tocUrl": "$.data.book.id@js:'https://api.example.com/catalog?id='+result"
  },
  "ruleToc": {
    "chapterList": "$.data.chapters",
    "chapterName": "title",
    "chapterUrl": "id@js:'https://api.example.com/content?id='+result"
  },
  "ruleContent": {
    "content": "$.data.content"
  },
  "exploreUrl": "推荐::/api/recommend?page={{page}}\n玄幻::/api/search?key=玄幻&page={{page}}\n都市::/api/search?key=都市&page={{page}}"
}
```

### 2. 纯 HTML 型 — 最通用

**特征**：右键查看源代码，能看到书籍列表的 HTML。

**用法**：`@css:css选择器`。

完整模板：
```json
{
  "bookSourceGroup": "我的书源",
  "bookSourceName": "示例HTML书源",
  "bookSourceUrl": "https://site.com",
  "bookSourceType": 0,
  "enabled": true,
  "enabledExplore": true,
  "searchUrl": "/search?q={{key}}&page={{page}}",
  "ruleSearch": {
    "bookList": "@css:div.book-item",
    "name": "@css:div.book-title@text",
    "author": "@css:div.book-author@text",
    "coverUrl": "@css:img.cover@src",
    "bookUrl": "@css:a.book-link@href",
    "kind": "@css:span.category@text",
    "intro": "@css:div.desc@text",
    "lastChapter": "@css:span.last@text"
  },
  "ruleBookInfo": {
    "name": "@css:h1.book-name@text",
    "author": "@css:span.author@text",
    "coverUrl": "@css:img.cover@src",
    "intro": "@css:div.book-desc@html",
    "kind": "@css:span.category@text",
    "lastChapter": "@css:span.last-chapter@text",
    "tocUrl": "@css:a.toc-link@href"
  },
  "ruleToc": {
    "chapterList": "@css:ul.chapter-list li a",
    "chapterName": "text",
    "chapterUrl": "href",
    "nextTocUrl": "@css:a.next-page@href"
  },
  "ruleContent": {
    "content": "@css:div#content@html||@css:div.content@textNodes",
    "nextContentUrl": "@css:a.next-page@href",
    "replaceRegex": "##本站无弹窗广告|(\\d+)?\\s*第.{0,8}章.*|\\(本章完\\)"
  },
  "exploreUrl": "玄幻::/xuanhuan/{{page}}.html\n仙侠::/xianxia/{{page}}.html\n都市::/dushi/{{page}}.html"
}
```

> `||` 表示多个选择器 fallback。`@textNodes` 适合段落式正文。

### 3. CSS 混合型（tag./class. 语法）

**特征**：网站使用 Jsoup 选择器（非 CSS 标准语法）。

**用法**：`tag.标签名@属性` / `class.类名@属性`。

```json
{
  "bookSourceUrl": "https://jable.tv",
  "bookSourceType": 4,
  "searchUrl": "/search/?q={{key}}&page={{page}}",
  "ruleSearch": {
    "bookList": "class.video-img-box",
    "bookUrl": "tag.h6.title@tag.a@href",
    "coverUrl": "<js>\nvar img = result.select('img.lazyload').first();\nresult = img ? img.attr('data-src') : '';\n</js>",
    "name": "tag.h6.title@tag.a@text",
    "lastChapter": "class.label@text"
  },
  "ruleToc": {
    "chapterList": "class.video-img-box",
    "chapterName": "tag.h6.title@tag.a@text",
    "chapterUrl": "tag.h6.title@tag.a@href"
  },
  "ruleContent": {
    "content": "<js>\nvar m = result.match(/var hlsUrl\\s*=\\s*'([^']+)'/);\nresult = m ? m[1] : '';\n</js>"
  },
  "exploreUrl": "新片::/latest-updates/{{page}}/\n熱門::/hot/{{page}}/"
}
```

### 4. JS 动态型（API+init钩子）

**特征**：搜索/详情通过 `<js>` 块动态构建请求，通常从 `bookUrl` 中提取自定义参数。

```json
{
  "bookSourceGroup": "ΑΡΙ",
  "bookSourceName": "示例JS动态书源",
  "bookSourceUrl": "示例中转站",
  "bookSourceType": 0,
  "enabled": true,
  "enabledExplore": true,
  "searchUrl": "@js:buildRequest(backend + '/search?key=' + encodeURIComponent(key) + '&page=' + (page||1))",
  "ruleSearch": {
    "bookList": "$.list",
    "name": "$.articlename@js:t2s(result)",
    "author": "$.author@js:t2s(result)",
    "coverUrl": "$.imgUrl",
    "bookUrl": "$.articleid\n@js:\n`data:;base64,${java.base64Encode(result)},{\"type\":\"mybxs\"}`",
    "kind": "$.keywords\n@js:for (var i = 0; i < result.size(); i++) {\n    result.set(i, t2s(result.get(i)));\n}\nresult;",
    "intro": "$.intro@js:t2s(result)",
    "lastChapter": "$.lastchapter@js:t2s(result)"
  },
  "ruleBookInfo": {
    "init": "<js>\nbid = java.base64Decode(baseUrl.split(\",\")[1])\nresult = java.ajax(buildRequest(backend + '/detail?book_id=' + bid))\n</js>\n$.list[0]",
    "intro": "$.intro@js:t2s(result)",
    "lastChapter": "$.lastchapter@js:t2s(result)"
  },
  "ruleToc": {
    "chapterList": "<js>\nbid = java.base64Decode(baseUrl.split(\",\")[1])\nresult = java.ajax(buildRequest(backend + '/catalog?book_id=' + bid))\nvar list = JSON.parse(result).list;\nvar arr = [];\nfor (var i = 0; i < list.length; i++) {\n    arr.push(JSON.stringify({\n        title: list[i].chaptername,\n        url: list[i].articleid + '/' + list[i].chapterid\n    }));\n}\nresult = JSON.stringify(arr);\n</js>",
    "chapterName": "$.title",
    "chapterUrl": "$.url"
  },
  "ruleContent": {
    "content": "@js:\nvar parts = java.hexDecodeToString(result).split(\"/\");\nvar bid = parts[0], cid = parts[1];\nresult = java.ajax(buildRequest(backend + '/content?book_id=' + bid + '&chapter_id=' + cid));\nresult = JSON.parse(result).data;",
    "replaceRegex": "##本站无弹出广告|loadAdv\\(10,0\\);"
  },
  "exploreUrl": "推荐::@js:buildRequest(backend + '/novels/list/1_1.html')\n玄幻::@js:buildRequest(backend + '/novels/list/2_1.html')",
  "jsLib": "var backend = 'https://api.backend.com';\nfunction buildRequest(url) { return url; }\nfunction t2s(text) {\n  // 简繁转换逻辑\n  return text;\n}"
}
```

### 5. 聚合型（多源合并）

**特征**：一个书源下搜多个后端，用源配置切换。

```json
{
  "bookSourceGroup": "聚合",
  "bookSourceName": "聚合搜索",
  "bookSourceUrl": "聚合搜索VIP",
  "bookSourceType": 0,
  "enabled": true,
  "enabledExplore": true,
  "searchUrl": "<js>\n// 从源配置读取当前选中的源\nvar cfg = JSON.parse(source.getVariable() || '{}');\nvar base = cfg.server || 'https://api.langge.cf';\nresult = base + '/search?key=' + encodeURIComponent(key) + '&page=' + (page||1);\n</js>",
  "ruleSearch": {
    "bookList": "$.data",
    "name": "$.title",
    "author": "$.author",
    "bookUrl": "<js>\nvar obj = { book_id: result.book_id, source: result.source };\nvar b64 = java.base64Encode(JSON.stringify(obj));\nresult = 'data:;base64,' + b64 + ',{\"type\":\"aggregate\"}';\n</js>"
  },
  "jsLib": "var hosts = ['https://api1.com', 'https://api2.com'];\nfunction getArgs(cfg, key) {\n  try { return JSON.parse(cfg)[key] || ''; }\n  catch { return ''; }\n}"
}
```

### 6. 中转型（绕开反爬）

**特征**：用第三方 API 获取大站（起点、番茄等）数据。

```json
{
  "bookSourceGroup": "中转",
  "bookSourceName": "示例中转向",
  "bookSourceUrl": "https://m.qidian.com",
  "bookSourceType": 0,
  "enabled": true,
  "enabledExplore": true,
  "searchUrl": "{{ho}}/soushu/{{key}}.html?pageNum={{page}}",
  "ruleToc": {
    "chapterList": "<js>\nvar bookId = baseUrl.match(/(\\d+)/)[1]\nresult = java.ajax('https://wxapp.qidian.com/api/book/categoryV2?bookId=' + bookId)\n// ... 处理起点 API 数据\n</js>"
  },
  "jsLib": "var ho = 'https://m.qidian.com';"
}
```

---

## 第二步：字段写法详解

### searchUrl — 搜索请求的 5 种写法

| 写法 | 说明 | 示例 |
|------|------|------|
| 纯 URL + `{{key}}` `{{page}}` | 最常用 | `https://site.com/s?q={{key}}&p={{page}}` |
| 相对路径 | 自动拼接 `bookSourceUrl` | `/search?key={{key}}` |
| `@js:` 表达式 | 单行 JS | `@js:'https://api.com/s?q='+key` |
| `<js>` 块 | 多行 JS | `<js>...拼URL...</js>` |
| POST 请求 | JSON 对象带 body | `url,{"method":"POST","body":"key={{key}}"}` |

### ruleSearch — 解析搜索结果

| 字段 | 说明 | API 型写法 | HTML 型写法 |
|------|------|-----------|-------------|
| `bookList` | 列表容器 | `$.data.list` | `@css:div.item` |
| `name` | 书名 | `$.title` | `@css:h3@text` |
| `author` | 作者 | `$.author` | `@css:.author@text` |
| `bookUrl` | 详情页链接 | `$.id@js:拼完整URL` | `@css:a@href` |
| `coverUrl` | 封面 | `$.cover` | `@css:img@src` |
| `kind` | 分类 | `$.category` | `@css:.kind@text` |
| `intro` | 简介 | `$.intro` | `@css:.desc@text` |
| `lastChapter` | 最新章节 | `$.last_chapter` | `@css:.last@text` |
| `wordCount` | 字数 | `$.words` | `@css:.count@text` |
| `checkKeyWord` | 关键词校验 | 可空 | 可空 |

**bookUrl 必须拼完整 URL。**

搜索结果通常只有 ID，需要构造完整地址：

```json
// API 型 - 用 @js: 拼接
"bookList": "@js:var r=JSON.parse(result);var list=r.data.books;if(list){for(var i=0;i<list.length;i++){list[i].bookUrl='https://example.com/detail?id='+list[i].id}}JSON.stringify(list);",
"bookUrl": "bookUrl"

// API 型 - 用 $ + @js 行内拼接（更简洁）
"bookUrl": "$.id@js:'https://example.com/book/'+result"
```

**bookUrlPattern** 填 bookUrl 里固定的特征字符串，用于匹配书源：
```
例: "type=2"、"book_id="、"/detail/"
```

### ruleBookInfo — 书籍详情

```json
// API 型
"ruleBookInfo": {
  "name": "@js:JSON.parse(result).data.book.title",
  "author": "@js:JSON.parse(result).data.book.author",
  "coverUrl": "@js:JSON.parse(result).data.book.cover",
  "intro": "@js:JSON.parse(result).data.book.intro",
  "tocUrl": "@js:'https://example.com/toc?id='+JSON.parse(result).data.book.id"
}

// HTML 型 - tocUrl 留空则复用 bookUrl
"ruleBookInfo": {
  "name": "@css:.book-title@text",
  "author": "@css:.book-author@text",
  "tocUrl": ""
}
```

**init 钩子**（JS动态型的核心）：

```json
"ruleBookInfo": {
  "init": "<js>\n// 从自定义 URL 中提取参数\nvar bid = java.base64Decode(baseUrl.split(\",\")[1]);\n// 发解密请求\nresult = java.ajax('https://api.com/detail?book_id=' + bid);\n// result 被替换，后续规则解析这个 result\n</js>\n$.list[0]",
  ...
}
```

### ruleToc — 解析目录

```json
// API 型
"ruleToc": {
  "chapterList": "@js:var r=JSON.parse(result);var list=r.data.chapter_lists;for(var i=0;i<list.length;i++){list[i].cUrl='https://example.com/content?id='+r.data.id+'&cid='+list[i].id}JSON.stringify(list);",
  "chapterName": "title",
  "chapterUrl": "cUrl"
}

// HTML 型
"ruleToc": {
  "chapterList": "@css:ul.chapter-list li a",
  "chapterName": "text",
  "chapterUrl": "href"
}

// JS 动态型（最灵活——自己发请求）
"ruleToc": {
  "chapterList": "<js>\nvar bookId = baseUrl.match(/(\\d+)/)[1];\nresult = java.ajax('https://api.com/catalog?bookId=' + bookId);\nvar list = JSON.parse(result).data.chapters;\nvar arr = [];\nfor (var i = 0; i < list.length; i++) {\n  arr.push(JSON.stringify({\n    title: list[i].title,\n    url: 'https://api.com/content?cid=' + list[i].id\n  }));\n}\nresult = JSON.stringify(arr);\n</js>",
  "chapterName": "$.title",
  "chapterUrl": "$.url"
}
```

> **注意：** 字段名不要直接用 `chapterUrl`（Legado 保留字），用 `cUrl` 代替更保险。

### ruleContent — 解析正文

```json
// API 型
"ruleContent": {
  "content": "@js:JSON.parse(result).data.content"
}

// HTML 型
"ruleContent": {
  "content": "@css:#content@textNodes"
}

// 广告过滤
"ruleContent": {
  "content": "data.content",
  "replaceRegex": "##本站无弹窗广告|loadAdv\\(10,0\\);|(\\d+)?\\s*第.{0,8}章.*|\\(本章完\\)"
}

// 视频站（从页面 JS 变量提取）
"ruleContent": {
  "content": "<js>\nvar m = result.match(/var hlsUrl\\s*=\\s*'([^']+)'/);\nresult = m ? m[1] : '';\n</js>"
}
```

### exploreUrl — 分类发现

**需要在每个分类 URL 里传真实搜索关键词，不要用 `***` 占位符！**

```json
// 简单格式
"exploreUrl": "玄幻::/xuanhuan/{{page}}.html\n仙侠::/xianxia/{{page}}.html"

// JSON 格式（可自定义样式）
"exploreUrl": "[{\"title\":\"男频\",\"url\":\"{{ho}}/rank?page={{page}}\",\"style\":{\"layout_flexGrow\":1}}]"

// JS 格式
"exploreUrl": "@js:var h='https://api.com';JSON.stringify([{\"title\":\"推荐\",\"url\":h+'/search?key=推荐&page={{page}}'},{\"title\":\"玄幻\",\"url\":h+'/search?key=玄幻&page={{page}}'}])"

// <js> 块格式
"exploreUrl": "<js>var h='https://api.com';var list=[{\"title\":\"推荐\",\"url\":h+'/search?key=推荐'},{\"title\":\"玄幻\",\"url\":h+'/search?key=玄幻'}];JSON.stringify(list);</js>"
```

> ⚠️ **不要用 `key=***`**：很多 API 不认识 `***`。每个分类填真实关键词（如 `key=玄幻`）。

记得加 `"enabledExplore": true`。

发现页的解析规则用 `ruleExplore`，和 `ruleSearch` 结构一致：
```json
"ruleExplore": {
  "bookList": ".book-list li",
  "name": "h2@text",
  "bookUrl": "a.0@href",
  "coverUrl": "img@src",
  "author": ".author@text"
}
```

---

## 第三步：分页翻页写法 ⭐

这是书源体验的关键。很多书源只有第一页，就是因为缺了分页。

### 认识 `{{page}}` 和 `page` 变量

| 方式 | 适用场景 | 示例 |
|------|----------|------|
| `{{page}}` URL 占位符 | 纯 URL 字符串 | `?page={{page}}` → `?page=1` |
| `page` JS 变量 | `<js>` 或 `@js:` 中 | `var p = page != null ? page : 1` |

### 纯 URL 写法

API 直接用 page 参数（1-based）：
```
API型:  "https://api.com/search?q={{key}}&page={{page}}"
HTML型: "https://site.com/search?q={{key}}&page={{page}}"
```

### JS 写法（offset 类 API）

如果 API 用 offset 分页（0-based），需要 JS 计算：
```json
"searchUrl": "<js>var p=page!=null?page:1;result='https://api.com/search?q='+encodeURIComponent(key)+'&offset='+((p-1)*10)</js>"
```
公式：`offset = (page - 1) × 每页条数`

### ⚠️ 关键陷阱：`page` 是 `null` 不是 `undefined`

```javascript
// ❌ 错误 - page=null 时 typeof null ≠ 'undefined'，结果是 null
typeof page !== 'undefined' ? page : 1   // → null（变成 ?page=null）

// ✅ 正确
page != null ? page : 1                   // → 1

// ✅ 也正确
page || 1                                 // → 1
```

### 分页工作原理解析

Legado 处理分页的流程：
1. 执行 `<js>` → 生成 URL 字符串
2. 替换 `{{page}}` → 用 page 值替换 URL 中的 `{{page}}` 占位符
3. 请求 → 发送生成好的 URL

关键：`{{page}}` 替换只在 `page != null` 时执行。`page = null` 时 `{{page}}` 不变 → URL 失效。

---

## 第四步：Key 轮换写法

当 API 有每日限额时，多个 Key 轮换使用：

```json
"searchUrl": "<js>var _keys=[\"KEY1\",\"KEY2\",\"KEY3\"];var _idx=java.getGlobal(\"key_idx\");if(_idx===null)_idx=0;else _idx=(_idx+1)%_keys.length;java.putGlobal(\"key_idx\",_idx);var ak=_keys[_idx];java.put('key',key);result='https://example.com/search?key='+ak+'&wd='+encodeURIComponent(key)+'&page=0'</js>"
```

bookList、tocUrl、chapterList、content 里同样要加轮换逻辑。

> ⚠️ Key 轮换和分页一起用时，别忘了分页参数也要带上。

---

## 第五步：Yiove 书源仓库 — 学习资源

https://shuyuan.yiove.com/ 有 31132 个现成书源，是最好的学习资料。

### 仓库 API

| 接口 | 说明 |
|------|------|
| `GET /shuyuan/book-sources?page={n}&page_size=20` | 分页列表 |
| `GET /shuyuan/book-source/{id}` | 书源详情（含 `origin_json` 完整书源 JSON） |

```bash
# 搜索特定网站的书源
curl -s "https://shuyuan-api.yiove.com/shuyuan/book-sources?page=1&page_size=20" \
  -H 'User-Agent: Mozilla/5.0' | python3 -m json.tool

# 获取书源详情
curl -s "https://shuyuan-api.yiove.com/shuyuan/book-source/{id}" \
  -H 'User-Agent: Mozilla/5.0'
```

### Python 脚本：搜索+提取

```python
import urllib.request, json

API = 'https://shuyuan-api.yiove.com'

def search_sources(keyword, page=1):
    req = urllib.request.Request(
        f'{API}/shuyuan/book-sources?page={page}&page_size=20',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    data = json.loads(urllib.request.urlopen(req).read())
    return [item for item in data['items'] if keyword in item.get('name','')]

def get_source_detail(source_id):
    req = urllib.request.Request(
        f'{API}/shuyuan/book-source/{source_id}',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    data = json.loads(urllib.request.urlopen(req).read())
    if data.get('origin_json'):
        return json.loads(data['origin_json'])
    return None
```

---

## 第六步：关键 JS API（Java 端方法）

Legado 在 `<js>` 块中暴露的 Java 方法：

| 方法 | 说明 | 示例 |
|------|------|------|
| `java.ajax(url)` | 发送 HTTP GET 请求 | `java.ajax('https://api.com/data')` |
| `java.ajax(url, options)` | 带选项的请求 | `java.ajax(url, {"method":"POST","body":"..."})` |
| `java.base64Encode(str)` | Base64 编码 | `java.base64Encode(bid)` |
| `java.base64Decode(str)` | Base64 解码 | `java.base64Decode(b64)` |
| `java.hexDecodeToString(hex)` | Hex 转字符串 | `java.hexDecodeToString(result)` |
| `java.getArray(key)` | 获取数组变量 | |
| `java.getGlobal(key)` | 获取全局变量 | |
| `java.putGlobal(key, val)` | 设置全局变量（Key轮换用） | |
| `java.put(key, value)` | 存值（跨步骤共享） | `java.put('book_id', book_id)` |
| `java.log(msg)` | 打印日志（调试用） | `java.log('debug: ' + result)` |
| `java.startBrowser(url)` | 打开浏览器 | |
| `cache.get(key)` | 读取缓存 | |
| `cache.set(key, value)` | 写入缓存 | |
| `source.getVariable()` | 获取源配置变量 | `JSON.parse(source.getVariable())` |
| `source.setVariable(json)` | 设置源配置变量 | |
| `result.select('css')` | 在 `<js>` 块内 CSS 选择 | `result.select('img.lazyload').first()` |
| `result.match(regex)` | 在 `<js>` 块内正则匹配 | `result.match(/hlsUrl='([^']+)'/)` |

---

## 第七步：反混淆与防爬对抗

### 常见防爬手段

| 手段 | 说明 | 破解 |
|------|------|------|
| 数字数组 XOR 编码 | 关键字符串 → 数字数组，运行时解码 | 用 Python 重现解码逻辑 |
| jsLib 巨型混淆 | 几百 KB 混淆代码，只导出 1-2 个函数 | 只看导出的函数名，直接调用 |
| hex 编码正文 | 正文 hex 编码 | `java.hexDecodeToString(result)` |
| base64 自定义 URL | `data:;base64,...` 传递参数 | `java.base64Decode(baseUrl.split(",")[1])` |
| 正统转换 t2s | 繁体 → 简体 | `@js:t2s(result)` |
| replaceRegex 清洗 | 正则管道移除广告 | `##广告1\|广告2` |
| POST 请求 | 参数在 body 里 | `java.ajax(url, {"method":"POST","body":"data"})` |

### 完整的防爬书源示例（开源API+前端混淆）

```json
{
  "bookSourceName": "对抗示例",
  "bookSourceUrl": "https://site.com",
  "searchUrl": "@js:buildRequest(backend + '/search')",
  "ruleSearch": {
    "bookList": "$.list",
    "name": "$.title@js:t2s(result)",
    "bookUrl": "$.id@js:'data:;base64,' + java.base64Encode(result) + ',{\"type\":\"x\"}'"
  },
  "ruleBookInfo": {
    "init": "<js>\nvar bid = java.base64Decode(baseUrl.split(',')[1]);\nresult = java.ajax(buildRequest(backend + '/detail?id=' + bid));\n</js>\n$.data[0]"
  },
  "ruleToc": {
    "chapterList": "<js>\nvar bid = java.base64Decode(baseUrl.split(',')[1]);\nresult = java.ajax(buildRequest(backend + '/catalog?id=' + bid));\nvar list = JSON.parse(result).list;\nvar arr = [];\nfor (var i = 0; i < list.length; i++) {\n  arr.push(JSON.stringify({title: list[i].name, url: list[i].id}));\n}\nJSON.stringify(arr);\n</js>",
    "chapterName": "$.title",
    "chapterUrl": "$.url"
  },
  "ruleContent": {
    "content": "@js:\nvar parts = java.hexDecodeToString(result).split('/');\nresult = java.ajax(buildRequest(backend + '/content?id=' + parts[0] + '&cid=' + parts[1]));\nJSON.parse(result).data;",
    "replaceRegex": "##广告"
  },
  "exploreUrl": "热门::@js:buildRequest(backend + '/hot')",
  "jsLib": "var backend = 'https://api.backend.com';\nfunction buildRequest(url) { return url; }\nfunction t2s(t) {\n  // 简繁转换\n  return t;\n}"
}
```

---

## 第八步：调试技巧

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

- 浏览器 F12 → Network → 搜一次书 → 看请求和返回结构
- 开启阅读3.0的「记录日志」，看 `[TOC-JS-RESULT]` 和 `[getHttpResponse]` 定位问题

---

## 第九步：完整流程清单

- [ ] 确定书源类型（API / HTML / JS动态 / 聚合 / 中转 / 视频）
- [ ] curl 测试搜索/详情/目录/正文四个接口
- [ ] curl 测试分页参数
- [ ] 写 `searchUrl` + 分页（`{{page}}` 或 JS offset）
- [ ] 写 `ruleSearch` + JS 拼 `bookUrl`
- [ ] 写 `bookUrlPattern`
- [ ] 写 `ruleBookInfo` + 可选 `init` 钩子 + JS 拼 `tocUrl`
- [ ] 写 `ruleToc` + 可选 `<js>` 块构建目录
- [ ] 写 `ruleContent` + `replaceRegex` 清洗
- [ ] 要分类发现写 `exploreUrl`（真实关键词 + 分页）
- [ ] 要通用函数写 `jsLib`
- [ ] python3 验证 JSON 语法
- [ ] 导入阅读3.0 全链路测试
- [ ] 测试搜索翻页（搜关键词 → 下拉）
- [ ] 测试发现翻页（点分类 → 下拉）
- [ ] 搞不定的去 Yiove 仓库搜同类型书源参考
