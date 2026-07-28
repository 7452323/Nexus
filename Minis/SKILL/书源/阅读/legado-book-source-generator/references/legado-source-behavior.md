# 阅读源码行为记录

本文件只记录已从阅读源码或明确实现行为确认的边界。官方教程可确认的规则放在 `official-rule-pack.json`，validator 限制放在 `validator-integration.md` / `validation-policy.md`。

## Jsoup 选择器边界

阅读 HTML 规则使用 Jsoup 解析 CSS selector，不支持 jQuery 扩展选择器，例如 `:contains()`、`:has()`、`:eq()`、`:visible`。

处理方式：用标准 CSS 定位节点，再用 `@text`、`@href`、`<js>` 或后处理规则过滤。

## `@css:` 多 action 链限制

`@css:` 模式下多 action 链容易把前面的 `@href` / `@text` 当成 selector 的一部分。需要链式处理时，优先使用普通规则 action + `##$##<js>` 或明确的 JS 后处理。

## User-Agent 完整性

书源 header 里的 User-Agent 必须是完整浏览器 UA。截断的 UA（如只有 `Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36`）缺少引擎名和版本号，会被反爬系统识别为非标准客户端。

完整 UA 模板：`Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36`

反爬系统检查 UA 完整性是常见行为。书源 header 不应截断浏览器 UA，必须保留 `(KHTML, like Gecko) Chrome/... Safari/...` 后半截。

## `@js:` 内联 JavaScript

规则中可以使用 `@js:` 前缀执行 JavaScript 代码，只能放在其他规则的最后：

```json
{
  "coverUrl": "a@href@js:cover(result)"
}
```

`result` 变量是 `@js:` 前规则的结果。`cover()` 是在 `jsLib` 中定义的函数。

`<js></js>` 标签可以放在规则任意位置，适用于需要更复杂逻辑的场景。

## `jsLib` 函数库

书源顶层可选字段 `jsLib`，写入 JavaScript 函数定义，供规则中的 `@js:` 调用。

常见用途：
- **封面 URL 拼接**：从书籍 URL 提取 ID，按站点规律拼接封面图 URL
- **URL 解析**：处理相对路径、特殊编码等

示例：
```json
{
  "jsLib": "function cover(href){var m=String(href).match(/\\/(\\d+)\\/?$/);if(!m)return '';var id=m[1];var p=id.length<=3?'0':id.slice(0,-3);return 'http://img.example.com/'+p+'/'+id+'/'+id+'s.jpg';}"
}
```

## 正文内容清理

正文 HTML 常含广告、提示文字等噪声，用 `##` 替换规则清理：

```json
{
  "content": "#nr1@html##本章未完，请点击下一页继续阅读##"
}
```

`##要替换的内容##` 表示将匹配文本替换为空字符串。支持正则：`##正则##替换文本##`。

## 章节名清理

章节名可能含分页后缀（如 `第一章（1）`、`第一章（2）`），用正则替换清理：

```json
{
  "chapterName": "@text##（\\d+）####\\(\\d+\\)##"
}
```

先后去掉中文括号 `（数字）` 和英文括号 `(数字)`。

## TLS 指纹

部分站点（如刺猬猫）通过 TLS 握手特征（JA3）区分真实客户端和自动化工具。PC JVM 的 JSSE TLS 指纹与 Android BoringSSL 不同，会被识别为爬虫。validator 改用 curl（OpenSSL）发 HTTP 请求绕过此检测。书源规则不涉及 TLS——这是 validator 的运行环境问题，不是书源配置问题。

## 记录原则

- 没有源码或实现证据的经验不写入本文件。
- validator 兼容建议不写入本文件。
- 站点历史样例不写入本文件。
