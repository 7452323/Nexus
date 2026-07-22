---
name: tool-index
description: 本机工具可用性清单（iSH/Alpine Linux aarch64）。
---

# 工具索引（iSH 环境）

## ✅ 可用工具

### 浏览器取证
| 工具 | 用途 | 调用方式 |
|------|------|---------|
| Minis browser_use | 页面导航、截图、文本提取 | `browser_use navigate` |
| execute_js | 在页面上下文执行 JS | `browser_use execute_js` |
| get_cookies | 提取 Cookie（含 HttpOnly） | `browser_use get_cookies` |
| get_readable | 提取页面可读文本 | `browser_use get_readable` |
| find_elements | 查找交互元素 | `browser_use find_elements` |

### 本地复现
| 工具 | 用途 | 安装 |
|------|------|------|
| Python3 | 脚本、加解密验证 | ✅ 内置 |
| Node.js | 本地补环境复现 | `apk add nodejs` |
| curl | HTTP 请求 | ✅ 内置 |
| wget | 文件下载 | ✅ 内置 |
| openssl | 加解密操作 | ✅ 内置 |

### 加解密
| 工具 | 用途 |
|------|------|
| Python pycryptodome | AES/DES/RSA/SM2/SM4 |
| Python hashlib | MD5/SHA1/SHA256 |
| OpenSSL CLI | 各种对称/非对称加密 |

### CF 绕过
| 工具 | 用途 | 安装 |
|------|------|------|
| Minis 浏览器 | Turnstile 自动验证 | ✅ 内置 |
| SeleniumBase | UC+CDP Mode + solve_captcha | `pip install seleniumbase` |
| Pydoll | 异步零 WebDriver CF 绕过 | `pip install pydoll` |
| Scrapling | 自适应 + StealthyFetcher | `pip install scrapling` |
| curl_cffi | TLS 指纹伪装 | `pip install curl_cffi` |
| cloudscraper | 基础 IUAM 绕过 | `pip install cloudscraper` |
| FlareSolverr | 独立 CF 绕过服务 | Docker |

### JS 逆向
| 工具 | 用途 | 安装 |
|------|------|------|
| Babel AST | JS 反混淆 | `npm install @babel/*` |
| js-beautify | 代码格式化 | `npm install js-beautify` |
| esprima | JS 解析器 | `npm install esprima` |
| JSRPC | WebSocket 远程调用 | `pip install jsrpc` |

### 网络请求
| 工具 | 用途 |
|------|------|
| curl | HTTP/HTTPS 请求 |
| Python requests | HTTP 库 |
| Python httpx | 异步 HTTP |
| mitmproxy | MITM 代理（需 PC 端） |

## ❌ 不可用工具（需 PC/Mac）

| 工具 | 替代方案 |
|------|---------|
| IDA Pro | Ghidra (在线版) |
| Ghidra (本地) | GhidraMCP (远程) |
| jadx | 在线 JADX |
| apktool | 在线 APK 分析 |
| Frida | 浏览器 CDP |
| x64dbg | 远程调试 |
| Burp Suite | mitmproxy + Python |
| Charles | mitmproxy |
| Wireshark | tcpdump |

## 工具安装速查

```bash
# Python 加解密
pip install pycryptodome pycurl requests httpx

# CF 绕过
pip install seleniumbase pydoll scrapling curl_cffi cloudscraper

# JS 逆向
npm install @babel/parser @babel/traverse @babel/generator js-beautify esprima

# Node.js
apk add nodejs npm
```

