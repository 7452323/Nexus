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

需要在每个分类 URL 里传对应的搜索关键词：

```json
"exploreUrl": "<js>\nvar list=[\n{\"title\":\"🔥 推荐\",\"url\":\"https://example.com/search?key=推荐\"},\n{\"title\":\"📖 玄幻\",\"url\":\"https://example.com/search?key=玄幻\"}\n];JSON.stringify(list);\n</js>"
```

记得加 `"enabledExplore": true`。

---

## 第三步：Key 轮换写法

当 API 有每日限额时，多个 Key 轮换使用：

```json
"searchUrl": "<js>var _keys=[\"KEY1\",\"KEY2\",\"KEY3\"];var _idx=java.getGlobal(\"key_idx\");if(_idx===null)_idx=0;else _idx=(_idx+1)%_keys.length;java.putGlobal(\"key_idx\",_idx);var ak=_keys[_idx];java.put('key',key);result='https://example.com/search?key='+ak+'&wd='+encodeURIComponent(key)+'&page=0'</js>"
```

bookList、tocUrl、chapterList、content 里同样要加这段轮换逻辑：
- 每个 @js: 开头插入 Key 轮换代码
- URL 中的 Key 替换成 `"+ak+"`（@js: 中）或 `'+ak+'`（<js> 中）

---

## 第四步：常见问题排查

|症状|可能原因|解决方法|
|---|---|---|
|搜不到结果|`{{key}}` 拼错|检查是 `{{key}}` 不是 `{key}`|
|搜到但点进去空白|`bookUrl` 不完整|JS 里拼完整 https:// 地址|
|点进去空白|`bookUrlPattern` 不匹配|特征字符串是否在 URL 里出现|
|有详情没目录|`tocUrl` 不对|检查 ruleBookInfo 里的 tocUrl|
|有目录点不开|`cUrl` 没拼全|每条章节必须是完整 URL|
|发现页不显示|`enabledExplore` 没开|加 `"enabledExplore": true`|
|Key 被限额|当日次数用完|换 Key 或等第二天|

---

## 第五步：调试技巧

```bash
# curl 测试 API
curl "https://api.example.com/search?q=测试"
# 看返回的 JSON 结构，字段名照抄到书源里

# 验证 JSON 语法
python3 -c "import json; json.load(open('书源.json')); print('合法')"
```

浏览器 F12 -> Network -> 搜一次小说 -> 看请求和返回结构。

---

## 第六步：完整流程清单

- [ ] 确定数据来源（API 还是 HTML）
- [ ] curl 测试搜索/详情/目录/正文四个接口
- [ ] 写 `searchUrl`
- [ ] 写 `ruleSearch` + JS 拼 `bookUrl`
- [ ] 写 `bookUrlPattern`
- [ ] 写 `ruleBookInfo` + JS 拼 `tocUrl`
- [ ] 写 `ruleToc` + JS 拼每条 `cUrl`
- [ ] 写 `ruleContent`
- [ ] 要分类发现就写 `exploreUrl`
- [ ] python3 验证 JSON 语法
- [ ] 导入阅读3.0 全链路测试


---

