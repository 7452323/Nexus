# Legado JSON 结构要点

以 Legado 源码中的 `BookSource`、`SearchRule`、`BookInfoRule`、`TocRule`、`ContentRule` 为准。

## 顶层必填字段

- `bookSourceUrl`
- `bookSourceName`
- `searchUrl`
- `ruleSearch`
- `ruleBookInfo`
- `ruleToc`
- `ruleContent`

## 导入文件格式

- 提供给阅读导入的 `book-source.json` 顶层必须是 JSON 数组。
- 即使当前只生成一个书源，也要写成 `[ { ... } ]`，不要直接输出单个对象。
- 辅助脚本可以校验单对象结构，但最终交付给阅读导入时必须是数组包装格式。

## 常见可选字段

- `bookSourceGroup`
- `bookUrlPattern`
- `header` — JSON 字符串形式的请求头；UA 完整性要求见 `legado-source-behavior.md`
- `loginUrl`
- `loginUi`
- `loginCheckJs`
- `enabledCookieJar`
- `enabledExplore`
- `exploreUrl`

## 子规则最低要求

### `ruleSearch`

- `bookList`
- `name`
- `bookUrl`
- `coverUrl` — 可选；搜索结果有封面时填写。两种写法：
  - CSS 直接提取：`img@src`（搜索列表含 `<img>` 时）
  - JS 拼接（详情页封面 URL 有规律时）：`a@href@js:cover(result)`，配合 `jsLib` 定义 `cover()` 函数

### `ruleBookInfo`

- `name` — 必填
- `tocUrl` — 常规建议填写；如果目录嵌在详情页，允许留空，但必须在 `analysis.md` 里说明依据
- `coverUrl` — 详情页封面，通常 `img@src` 直接提取

### `ruleToc`

- `chapterList`
- `chapterName`
- `chapterUrl`
- `nextTocUrl` — 目录分页入口，返回下一页 URL 或 URL 数组；没有真实分页证据时不要编造

### `ruleContent`

- `content`
- `nextContentUrl` — 正文分页入口。**使用 CSS 选择器提取"下一页"链接**，如 `#pt_next@href`、`text.下一页@href`。不要用变量引用（如 `defaultContentUrl`），除非配合 `jsLib` 做复杂 URL 拼接
- 正文含"本章未完"等提示文字时，用 `##本章未完，请点击下一页继续阅读##` 替换为空

## `jsLib` — JavaScript 辅助函数库

当规则需要 JS 处理（如封面 URL 拼接）时，在书源顶层添加 `jsLib` 字段，写入 JS 函数定义。规则中通过 `@js:functionName(result)` 调用。

```json
{
  "jsLib": "function cover(href){var m=String(href).match(/\\/(\\d+)\\/?$/);if(!m)return '';var id=m[1];var p=id.length<=3?'0':id.slice(0,-3);return 'http://img.example.com/'+p+'/'+id+'/'+id+'s.jpg';}"
}
```

调用方式：
```json
{
  "coverUrl": "a@href@js:cover(result)"
}
```

`result` 是 `@js:` 前规则的结果（此处为 `a@href` 提取的书籍 URL）。

## `exploreUrl` — 发现页（探索页）

**格式是 JSON 数组字符串**，每个元素是一个对象，包含 `title`（显示名称）、`url`（含 `{{page}}` 分页占位符）、`style`（布局样式）。

```json
{
  "enabledExplore": true,
  "exploreUrl": "[{\"title\":\"分类名\",\"url\":\"https://example.com/class/{{page}}.html\",\"style\":{\"layout_flexGrow\":1,\"layout_flexBasisPercent\":0.25}},{\"title\":\"排行榜\",\"url\":\"https://example.com/top/{{page}}.html\",\"style\":{\"layout_flexGrow\":1,\"layout_flexBasisPercent\":0.25}}]",
  "ruleExplore": {
    "bookList": ".book-list li",
    "name": "a@text",
    "bookUrl": "a@href",
    "coverUrl": "a@href@js:cover(result)"
  }
}
```

`style` 常用值：
- `layout_flexGrow: 1` — 弹性布局
- `layout_flexBasisPercent: 0.25` — 基础宽度占比 25%

`ruleExplore` 结构与 `ruleSearch` 相同，支持 `coverUrl`。

## 生成建议

- 登录站点优先补 `loginUrl`，必要时补 `header`。
- 默认不启用发现：除非用户明确要求发现页，否则设定 `enabledExplore=false`，并且不生成 `exploreUrl` / `ruleExplore`。
- 搜索、详情、目录、正文的规则字段命名必须和 Legado 源码保持一致。
- 能用静态规则表达时，不要加 JS。
- XPath、CSS、JSONPath、Regex 都要以 validator 实测命中为准；选择器语法不确定时先做局部验证，不要把浏览器控制台可用语法直接当成阅读规则语法。
- 默认不要在 `bookSourceComment` 中写调试说明。
- 只有用户明确要求保留限制说明，或进入故障回修阶段时，才考虑在 `bookSourceComment` 写入必要备注。
- 章节名含分页后缀（如 `（1）`、`（2）`）时，用 `##（\\d+）####\\(\\d+\\)##` 替换为空。
- 正文含"本章未完，请点击下一页继续阅读"等提示时，用 `##本章未完，请点击下一页继续阅读##` 替换为空。

## 最小示例

```json
[
  {
    "bookSourceUrl": "https://example.com",
    "bookSourceName": "Example",
    "searchUrl": "https://example.com/search?q={{key}}",
    "ruleSearch": {
      "bookList": "$.items[*]",
      "name": "$.title",
      "bookUrl": "$.url"
    },
    "ruleBookInfo": {
      "name": "$.title",
      "tocUrl": "$.tocUrl"
    },
    "ruleToc": {
      "chapterList": "$.chapters[*]",
      "chapterName": "$.title",
      "chapterUrl": "$.url"
    },
    "ruleContent": {
      "content": "$.content"
    }
  }
]
```
