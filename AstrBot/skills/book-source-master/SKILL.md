# Book Source Master

## Description
A comprehensive guide for writing and debugging book sources for the Legado Reader 3.0 app (also known as "阅读3.0"). Covers API-based and HTML-based sources, field mapping, troubleshooting, and key rotation strategies. Agent uses this to create book sources for any novel website.

## Instructions

### Step 1: Determine Data Source Type

**A. API-based (Preferred, Most Stable)** — Website returns data via JSON API.

Identify by: F12 Developer Tools → Network → XHR/Fetch tab → look for JSON responses.

Write using: `@js:JSON.parse(result)` to parse JSON.

**B. HTML-based (Universal)** — Website returns HTML pages.

Identify by: View page source → look for book list HTML tags.

Write using: `@css:` selectors.

### Step 2: Field Mapping Table

#### searchUrl
```
API-type:  "https://api.example.com/search?q={{key}}&page=0"
HTML-type: "https://site.com/search?q={{key}}"
```

`{{key}}` is automatically replaced by the app with the user's search keyword. Note: it's `{{key}}`, not `{key}`.

#### ruleSearch — Parse Search Results

| Field | API-type | HTML-type |
|-------|----------|-----------|
| `bookList` | `data.books` or `@js:` iterate | `@css:.book-item` |
| `name` | field name (e.g. `title`) | `@css:.title@text` |
| `author` | field name | `@css:.author@text` |
| `bookUrl` | `@js:` construct URL | `@css:a@href` |
| `coverUrl` | field name | `@css:img@src` |
| `intro` | field name (optional) | optional |

**bookUrl must be a complete URL.** Search results typically only have IDs:

```json
"bookList": "@js:var r=JSON.parse(result);var list=r.data.books;if(list){for(var i=0;i<list.length;i++){list[i].bookUrl='https://example.com/detail?id='+list[i].id}}JSON.stringify(list);",
"bookUrl": "bookUrl"
```

**bookUrlPattern** — fill with the characteristic string in bookUrl for matching:
```
Example: "type=2", "book_id=", "/detail/"
```

#### ruleBookInfo — Book Details

API-type:
```json
"ruleBookInfo": {
  "name": "@js:JSON.parse(result).data.book.title",
  "author": "@js:JSON.parse(result).data.book.author",
  "coverUrl": "@js:JSON.parse(result).data.book.cover",
  "intro": "@js:JSON.parse(result).data.book.intro",
  "tocUrl": "@js:'https://example.com/toc?id='+JSON.parse(result).data.book.id"
}
```

HTML-type:
```json
"ruleBookInfo": {
  "name": "@css:.book-title@text",
  "author": "@css:.book-author@text",
  "tocUrl": ""
}
```

#### ruleToc — Parse Table of Contents

Each chapter must have a complete content URL:

```json
"ruleToc": {
  "chapterList": "@js:var r=JSON.parse(result);var list=r.data.chapter_lists;for(var i=0;i<list.length;i++){list[i].cUrl='https://example.com/content?id='+r.data.id+'&cid='+list[i].id}JSON.stringify(list);",
  "chapterName": "title",
  "chapterUrl": "cUrl"
}
```

**Note:** Do not use `chapterUrl` as a field name (it's a Legado reserved word). Use `cUrl` instead.

#### ruleContent — Parse Content

API-type:
```json
"ruleContent": {
  "content": "@js:JSON.parse(result).data.content"
}
```

HTML-type:
```json
"ruleContent": {
  "content": "@css:#content@textNodes"
}
```

Ad filtering (optional):
```json
"ruleContent": {
  "content": "data.content",
  "replaceRegex": "advertisement|promotion|sponsored"
}
```

#### exploreUrl — Category Discovery

Pass search keywords in each category URL:

```json
"exploreUrl": "<js>\nvar list=[\n{\"title\":\"🔥 Recommended\",\"url\":\"https://example.com/search?key=Recommended\"},\n{\"title\":\"📖 Fantasy\",\"url\":\"https://example.com/search?key=Fantasy\"}\n];JSON.stringify(list);\n</js>"
```

Add `"enabledExplore": true` to enable.

### Step 3: Key Rotation (For Rate-Limited APIs)

```json
"searchUrl": "<js>var _keys=[\"KEY1\",\"KEY2\",\"KEY3\"];var _idx=java.getGlobal(\"key_idx\");if(_idx===null)_idx=0;else _idx=(_idx+1)%_keys.length;java.putGlobal(\"key_idx\",_idx);var ak=_keys[_idx];java.put('key',key);result='https://example.com/search?key='+ak+'&wd='+encodeURIComponent(key)+'&page=0'</js>"
```

Add key rotation code to bookList, tocUrl, chapterList, content as well.

### Step 4: Troubleshooting

| Symptom | Possible Cause | Solution |
|---------|---------------|----------|
| No search results | `{{key}}` typo | Check it's `{{key}}` not `{key}` |
| Results found but blank detail | `bookUrl` incomplete | Construct full https:// URL in JS |
| Blank detail page | `bookUrlPattern` mismatch | Check if char string appears in URL |
| No table of contents | `tocUrl` incorrect | Check tocUrl in ruleBookInfo |
| Chapters won't open | `cUrl` incomplete | Each chapter must be full URL |
| Discovery page not showing | `enabledExplore` not set | Add `"enabledExplore": true` |
| Key rate limit hit | Daily limit used up | Rotate key or wait until next day |

### Step 5: Debugging

```bash
# Test API with curl
curl "https://api.example.com/search?q=test"

# Validate JSON syntax
python3 -c "import json; json.load(open('source.json')); print('Valid')"
```

Browser F12 → Network → Search → Inspect request/response structure.

### Step 6: Complete Checklist

- [ ] Determine data source (API or HTML)
- [ ] Test all 4 endpoints with curl (search/detail/toc/content)
- [ ] Write `searchUrl`
- [ ] Write `ruleSearch` + JS to construct `bookUrl`
- [ ] Write `bookUrlPattern`
- [ ] Write `ruleBookInfo` + JS to construct `tocUrl`
- [ ] Write `ruleToc` + JS to construct each `cUrl`
- [ ] Write `ruleContent`
- [ ] Optionally write `exploreUrl`
- [ ] Validate JSON syntax with python3
- [ ] Full chain test in Legado Reader 3.0

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| api_url | string | Yes | Base URL of the novel website API |
| search_query | string | Depends | Search keyword for testing |
| source_type | string | Yes | "api" or "html" |
| use_key_rotation | boolean | No | Enable key rotation (default: false) |
| api_keys | string[] | If rotation enabled | List of API keys |

## Examples

### API-based source for a novel website
```
User: "Create a book source for example.com"
Agent: Follow Steps 1-6, testing each endpoint and generating the JSON source.
```

### Debugging an existing source
```
User: "My book source shows 'no results' when I search"
Agent: Check `{{key}}` syntax → verify `bookUrlPattern` → test with curl → fix accordingly.
```

## Notes
- Always use `cUrl` instead of `chapterUrl` (Legado reserved word conflict)
- The `@js:` prefix uses the Legado JS engine, not browser/Node.js
- For HTML sources, use `@css:` selectors; for API, use `@js:JSON.parse()`
- Validate JSON syntax before importing into the app
- Key rotation must be added to every `@js:` block that makes API calls
- This guide is for the Legado Reader 3.0 app ecosystem only
