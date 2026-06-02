---
name: web-tool-reverse-engineer
description: Web 在线工具逆向技能。对 tools.miku.ac 等在线工具站进行逆向，提取每个工具的 API 实现、前端逻辑、图标资源。按工具分类归档，生成描述 MD + 实现代码 + 复现方案。
author: 7452323
category: reverse-engineering
tags:
  - web-tools
  - reverse-engineering
  - tools-miku
  - api-extraction
---

# Web Tool Reverse Engineer — Web 在线工具逆向

## 适用场景

- 目标是一个在线工具集合（如 tools.miku.ac、在线转换工具站）
- 需要批量提取每个工具的实现逻辑
- 目标是本地复用/离线化/集成到自有系统
- 前端 SPA + 后端 API 的工具站架构

## 总览

```
┌── 任务定义 ──────────────────────────────┐
│  逆向 tools.miku.ac 等在线工具站           │
│  收集所有工具的实现方法                     │
│  按工具创建子文件夹                         │
│  每个子文件夹放:                            │
│    ├── README.md    ← 工具描述 + 图标链接  │
│    └── implement/   ← 实现代码 + 逻辑文档  │
└──────────────────────────────────────────┘
```

## 逆向方法论

### 阶段一：全站侦察

```bash
# 1. 先尝试工具列表 API（Nuxt/Next.js 常用）
# 很多工具站有隐藏的 /api/tools 端点
curl -sL --compressed 'https://target.com/api/tools' \
  -H 'User-Agent: Mozilla/5.0' \
  -H 'Accept: application/json'

# 2. 如果 API 可用，直接拿到完整工具列表（无需爬 HTML）
# tools.miku.ac 的 /api/tools 返回:
# { "success": true, "data": { "tools": [{ "slug": "...", "usage_count": N, "status": "active" }] } }
# 共 145 个工具，含 slug + 使用量，无需解析 HTML

# 3. 如果没 API → 爬首页找 JS bundle
# Nuxt 3 CSR 页面 curl 取到的 HTML 几乎全空（只有骨架 CSS）
# 必须用 --compressed 参数（Nuxt 默认 gzip 压缩响应）
curl -sL --compressed 'https://target.com/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# 4. 分析页面结构，识别工具分类
# 常见工具类型：
# - 图片处理（压缩/裁剪/格式转换/去背景）
# - 编码解码（Base64/URL/Hex）
# - 文本处理（JSON/Markdown/格式化）
# - 加密解密（AES/RSA/哈希）
# - 开发者工具（正则/CSS/格式化）
# - 音视频（压缩/转换/提取）

# 5. 抓取每个工具页面的 HTML/JS
# Nuxt 3 CSR: 页面内容是空的，JS bundle 渲染一切
# 不要浪费时间解析首页 HTML，直接找 JS bundle 或 API

# ⚠️ 实战陷阱：Nuxt 3 CSR 页面
# - curl 拿到的 HTML 除了骨架 <style> 和 <div id="__nuxt"> 外**没有任何工具数据**
# - 所有工具名、描述、分类全靠 JS bundle 初始化
# - 所以「grep 首页 HTML 提取工具列表」在 Nuxt 3 上完全失效
# - 替代方案：找 /api/tools 端点，或者用 browser_navigate 等待 JS 渲染
```

### 阶段一.b：JS Bundle 发现（Nuxt 3 特化）

```bash
# Nuxt 3 的 JS bundle 路径模式：/_nuxt/{hash}.js
# 从首页 HTML 提取 script src:
curl -sL --compressed 'https://target.com/' | grep -oP 'src="[^"]+' | sort -u

# tools.miku.ac 实际结果：assets 托管在二级域名
# JS bundle: https://okmiku.com/_nuxt/wa80Tw6d.js (425KB)
# 注意：CDN 域名可能跟主域名不同（多域名部署）

# 下载 JS bundle
curl -sL --compressed 'https://okmiku.com/_nuxt/wa80Tw6d.js' -o bundle.js

# 但注意：Nuxt 3 将每个工具组件拆分为异步 chunk（懒加载）
# 实际实现代码可能不在主 bundle 中，而分布在多个 /_nuxt/{slug}.hash.js 中
# 如果主 bundle 里搜不到工具实现，需要抓工具页面的 JS
```

### 阶段二：API 协议逆向

```javascript
// 1. 打开浏览器 DevTools → Network 面板
// 2. 触发工具功能，捕获请求
// 3. 分析请求结构：

// 典型工具 API 结构
{
  method: 'POST',  // 或 GET
  url: '/api/tool/encode',
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  body: {
    input: '待处理数据',
    options: { /* 工具特有的选项 */ }
  }
}

// 4. 识别前端 JS 中 API endpoint 的构造逻辑
// 搜索关键字：fetch、axios、ajax、apiUrl、endpoint
```

### 阶段三：前端 JS 逻辑提取

```bash
# 1. 下载所有 JS bundle
curl -sL https://tools.miku.ac/assets/index-*.js > bundle.js

# 2. 格式化并搜索工具实现
# 漂亮的格式化
npx prettier bundle.js > bundle.formatted.js

# 3. 搜索关键模式
grep -oP '(?<=function )\w+' bundle.formatted.js | sort | uniq -c | sort -rn
grep -n "tool\|convert\|encode\|decode\|compress\|resize" bundle.formatted.js | head -50

# 4. 提取每种工具的核心逻辑
# 注意：可能会被混淆（使用 AST 反混淆先处理）
```

### 阶段四：每个工具的输出格式

```
utils/
├── tool-name/                    # 工具名（英文小写+连字符）
│   ├── README.md                 # 工具描述
│   │   ├── 图标链接              # 来自页面的 favicon/icon URL
│   │   ├── 功能介绍              # 中文描述
│   │   ├── API 说明              # 请求/响应格式
│   │   └── 使用示例              # curl/Python 调用示例
│   └── implement/               # 实现代码
│       ├── api.py                # API 调用封装（Python）
│       ├── logic.py              # 核心逻辑复现（纯算法实现）
│       ├── index.js              # 原始 JS 逻辑（提取自 bundle）
│       └── README.md             # 实现逻辑说明
│
├── another-tool/                 # 另一个工具
│   └── ...
│
└── README.md                     # 根目录索引
```

### README.md 模板

```markdown
# {工具名}

## 基础信息
- **类型**: {图片处理/编码解码/文本处理/加密解密/开发者工具/音视频}
- **图标**: ![icon]({icon_url})
- **页面**: {page_url}
- **API**: {api_endpoint}

## 功能介绍
{中文描述}

## API 说明
### 请求
```http
{method} {url}
Content-Type: {content_type}

{request_body_example}
```

### 响应
```json
{response_example}
```

### 选项参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| input | string | 是 | 输入数据 |
| option1 | string | 否 | 选项说明 |

## 使用示例
```bash
curl -s {example_command}
```

```python
# Python 调用示例
import requests

def convert(data, option="default"):
    ...
```

## 实现逻辑
{核心算法/逻辑说明}
```

## 技术要点

### 图标提取
```bash
# 方法一：从页面提取
curl -sL https://tools.miku.ac | grep -oP 'icon|favicon|apple-touch-icon"[^>]*href="([^"]+)"'

# 方法二：从 JS 资源映射
grep -oP 'icon.*?https?://[^"\']+' bundle.js

# 方法三：DevTools 直接查看 elements 面板
```

### API 端点发现
```bash
# 从 JS bundle 搜索 API 路径
grep -oP '/api/[a-z/-]+' bundle.formatted.js | sort -u

# 搜索 fetch 调用中的 URL
grep -oP 'fetch\(["'"'"']([^"'"'"']+)["'"'"']' bundle.formatted.js | sort -u

# 搜索 axios 调用
grep -oP 'axios\.[a-z]+\(["'"'"']([^"'"'"']+)["'"'"']' bundle.formatted.js | sort -u
```

## 自动化工作流

```bash
# 全自动工具站逆向脚本
#!/bin/bash
TARGET_URL="$1"
OUTPUT_DIR="./utils"

# 1. 发现工具列表
curl -sL "$TARGET_URL" | grep -oP 'href="/tool/[^"]+"' | sort -u > tool_list.txt

# 2. 下载 JS bundle
BUNDLE_URL=$(curl -sL "$TARGET_URL" | grep -oP 'src="[^"]*index-[^.]+\.js[^"]*"')
curl -sL "https://tools.miku.ac$BUNDLE_URL" > bundle.js

# 3. 对每个工具提取
while read tool; do
    name=$(echo $tool | grep -oP '(?<=/tool/)[^"]+')
    mkdir -p "$OUTPUT_DIR/$name/implement"
    
    # 提取 API 端点
    grep -A 50 "$name" bundle.js > "$OUTPUT_DIR/$name/api_extract.js"
    
    # 生成 README 模板
    cat > "$OUTPUT_DIR/$name/README.md" << EOF
# $name

## 基础信息
- **类型**: TODO
- **页面**: https://tools.miku.ac/tool/$name
- **API**: TODO

## 功能介绍
TODO

## API 说明
TODO
EOF
done < tool_list.txt
```

## 验证清单
- [ ] 工具发现完整（没有遗漏）
- [ ] 每个工具的 API 端点已确认
- [ ] 前端逻辑已提取（JS bundle 中对应函数）
- [ ] 后端 API 可独立调用（不依赖前端环境）
- [ ] 核心算法可本地复现（Python/Node.js）
- [ ] README 中包含图标链接
- [ ] 所有工具按规范归档
