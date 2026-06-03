# 书源 JS 混淆与反防爬模式参考

从 Yiove 仓库现成书源中观察到的防爬混淆手段，以及对应的破解方法。

## 模式1：数字数组 + atob 解码

```javascript
// 编码阶段：将关键字符串转为数字数组
[60036,60028,60050,60030, ...]

// 解码阶段：数字 XOR → charCodeAt → String.fromCharCode
function decode(arr, key) {
  return arr.map(n => String.fromCharCode(n ^ key)).join('');
}
```

常见变体是两层嵌套：数字数组 → 解码出 atob → 再解码出真实代码。

## 模式2：jsLib 巨型混淆块

放在 jsLib 字段里，几百 KB 的混淆代码，实际只导出 1-2 个函数：
- buildRequest(url) — 拼搜索URL
- t2s(text) — 简繁转换
- getLimit(type) — 查询用量

**破解**：只看导出了什么函数名，在规则里直接调用，不需要理解混淆内容。

## 模式3：正统转换 (t2s) 与简繁处理

繁→简转换，用于港台小说站：

```javascript
"name": "$.articlename@js:t2s(result)"
```

## 模式4：replaceRegex 清洗正文

```json
"replaceRegex": "##本站无弹出广告|loadAdv\\(10,0\\);|(\\\\d+)?\\\\s*第.{0,8}章.*|\\(本章完\\)|..."
```

通过正则管道符一次性移除多种广告。

## 模式5：自定义 data: URL 协议

Legado 允许自定义 URL 协议传递上下文：

```
bookUrl = "data:;base64,${base64(bid)},{\"type\":\"mybxs\"}"
```

在 init 中提取：
```javascript
bid = java.base64Decode(baseUrl.split(",")[1])
```

## 模式6：init 钩子预处理

ruleBookInfo 和 ruleContent 的 init 字段在正式请求前执行，结果通过 result 变量传递。

## 模式7：正文 Hex 编码

部分书源的正文通过 hex 编码传递：

```javascript
cinfo = java.hexDecodeToString(result).split("/");
bid = cinfo[0];
cid = cinfo[1];
result = java.ajax(`.../content?book_id=${bid}&chapter_id=${cid}`);
```

## 模式8：动态多源路由

聚合型书源通过 source.getVariable() 读取用户配置：

```javascript
function getArguments(open_argument, key) {
    open_argument = JSON.parse(open_argument);
    return open_argument[key] || '';
}
```

## 破解方法速查

| 混淆手段 | 破解方法 |
|----------|----------|
| 数字数组 XOR 编码 | 用 Python/Node 重现代码逻辑，提取解码后的关键字符串 |
| jsLib 巨型混淆 | 只看它 export 了什么函数名，在规则里直接调用 |
| hex 编码正文 | `java.hexDecodeToString(result)` |
| base64 自定义 URL | `java.base64Decode(baseUrl.split(",")[1])` |
| 正统转换 t2s | `@js:t2s(result)` |
| 繁体字 | `@js:t2s(result)` |
| 聚合多源 | 看 jsLib 里的 host 数组和 getArguments 实现 |
| POST 请求 | `java.ajax(url, {"method":"POST","body":"data"})` |
| 正文广告 | `replaceRegex` 正则管道清洗 |
