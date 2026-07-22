---
name: web-security-pentest
description: Web 安全与渗透测试技能。OWASP Top 10、漏洞类型 (SQL/XSS/SSRF/XXE)、渗透流程、工具链 (Burp/Nmap/Nuclei)。
author: 7452323
tags:
  - web-security
  - penetration-testing
  - owasp
  - burp-suite
  - nmap
  - nuclei
  - sql-injection
  - xss
---

# Web 安全与渗透测试

## OWASP Top 10 (2021)

| 编号 | 漏洞类型 | 危害 | 检测工具 |
|------|---------|------|---------|
| A01 | 访问控制失效 (Broken Access Control) | 越权操作 | Burp + 手工 |
| A02 | 密码学失败 (Cryptographic Failures) | 数据泄漏 | testssl.sh |
| A03 | 注入 (Injection) | RCE/数据泄漏 | SQLMap + 手工 |
| A04 | 不安全设计 (Insecure Design) | 架构缺陷 | 代码审计 |
| A05 | 安全配置错误 (Security Misconfiguration) | 未授权访问 | Nuclei |
| A06 | 自带缺陷组件 (Vulnerable Components) | 已知漏洞利用 |
| A07 | 身份验证失败 (Auth Failures) | 账号接管 | Burp |
| A08 | 软件和数据完整性失败 | 供应链攻击 | SCA工具 |
| A09 | 安全日志和监控失败 | 攻击无法检测 | 日志审计 |
| A10 | SSRF | 内网探测/云元数据 | 手工 + interactsh |

## 漏洞类型详解

### 注入类

| 类型 | 测试方法 | 工具 | 危害 |
|------|---------|------|------|
| **SQL 注入** | ' OR 1=1-- , UNION SELECT | SQLMap, 手工 | 数据泄漏/RCE |
| **NoSQL 注入** | {$ne: 1} | 手工 | 认证绕过 |
| **LDAP 注入** | *)(uid=*))(\|(uid=* | 手工 | 认证绕过 |
| **SSTI** | {{7*7}} | tplmap | RCE |
| **OS 命令注入** | ; ls, \| whoami | 手工 | RCE |
| **模板注入** | ${7*7}, {{7*7}} | tplmap | RCE |
| **EL 注入** | ${7*7} | 手工 | RCE |
| **表达式注入** | #{7*7} | 手工 | RCE |

### 前端类

| 类型 | 测试方法 | 危害 |
|------|---------|------|
| **XSS (反射)** | <script>alert(1)</script> | Cookie 窃取 |
| **XSS (存储)** | 同上，持久化 | 蠕虫传播 |
| **XSS (DOM)** | 前端 JS 处理不当 | 无需服务端交互 |
| **CSRF** | 伪造请求 | 非授权操作 |
| **Clickjacking** | iframe 覆盖 | 误点击 |
| **DOM Clobbering** | 覆盖 DOM 对象 | XSS/逻辑绕过 |
| **Prototype Pollution** | __proto__ 注入 | XSS/RCE (Node) |
| **WebSocket Hijacking** | CSWSH | 会话劫持 |

### 服务端类

| 类型 | 测试方法 | 危害 |
|------|---------|------|
| **SSRF** | 内网地址回显 | 内网探测/云元数据 |
| **XXE** | 外部实体注入 | RCE/文件读取 |
| **反序列化** | 构造恶意 payload | RCE |
| **文件上传** | 绕过扩展名/Content-Type | Webshell |
| **文件包含** | php://filter, file:// | 代码执行 |
| **路径遍历** | ../../etc/passwd | 任意文件读取 |
| **IDOR** | 修改 ID 参数 | 水平/垂直越权 |
| **业务逻辑** | 绕过支付/验证 | 经济损失 |

### 高级漏洞

| 类型 | 说明 |
|------|------|
| **HTTP 走私** | CL/TE 头部不一致 |
| **HTTP 请求夹带** | 前端/后端解析差异 |
| **Web Cache Poisoning** | 缓存投毒 |
| **CORS 配置错误** | 跨域数据泄漏 |
| **JWT 攻击** | alg=none, 弱密钥, JWK 注入 |
| **OAuth 漏洞** | redirect_uri 绕过, state 缺失 |
| **GraphQL 漏洞** | 内省查询, 嵌套 DoS |

## 渗透测试流程

### PTES 标准

```
1. 前期交互 → 2. 情报收集 → 3. 威胁建模 → 4. 漏洞分析 → 5. 渗透攻击 → 6. 后渗透 → 7. 报告
```

### 情报收集 (Recon)

| 阶段 | 工具 | 输出 |
|------|------|------|
| 子域名枚举 | subfinder, amass, assetfinder | 子域名列表 |
| 端口扫描 | Nmap, Masscan, RustScan | 开放端口 |
| 服务识别 | Nmap -sC -sV | 服务版本 |
| 目录爆破 | ffuf, feroxbuster, dirsearch | 隐藏路径 |
| 指纹识别 | wappalyzer, whatweb | 技术栈 |
| 截图 | aquatone, eyewitness | 视觉侦察 |
| JS 分析 | LinkFinder, subjs | API 端点 |
| 历史 URL | waybackurls, gau | 历史路径 |
| OSINT | theHarvester, Recon-ng | 员工信息 |

### 漏洞扫描

| 工具 | 特点 |
|------|------|
| **Nuclei** | 模板化扫描，社区模板丰富 |
| **Nikto** | Web 服务器扫描 |
| **OWASP ZAP** | 开源 Web 漏洞扫描 |
| **Burp Scanner** | 商业级扫描 |
| **Wapiti** | 黑盒扫描 |
| **SQLMap** | SQL 注入专用 |
| **XSStrike** | XSS 扫描 |
| **Commix** | 命令注入 |

### 渗透攻击

| 阶段 | 工具 | 目标 |
|------|------|------|
| 初始访问 | Metasploit, 漏洞利用 | 获得 Shell |
| 权限提升 | LinPEAS, WinPEAS, GTFOBins | Root/SYSTEM |
| 凭证提取 | Mimikatz, LaZagne | 密码/Token |
| 横向移动 | Impacket, Evil-WinRM, Chisel | 内网扩展 |
| 持久化 | 计划任务, WMI, 注册表 | 维持访问 |
| 数据渗出 | DNS 隧道, HTTP 隧道 | 数据外传 |

## Burp Suite 核心功能

| 功能 | 用途 |
|------|------|
| Proxy | 拦截/修改 HTTP 请求 |
| Repeater | 手动重放/修改请求 |
| Intruder | 暴力破解/模糊测试 |
| Decoder | 编码/解码 |
| Comparer | 差异对比 |
| Sequencer | 随机性分析 |
| Extender | 插件扩展 |

### 常用 Burp 插件

| 插件 | 功能 |
|------|------|
| Autorize | 越权检测 |
| Param Miner | 隐藏参数发现 |
| Turbo Intruder | 高速并发 |
| JSON Web Tokens | JWT 分析 |
| Retire.js | JS 库漏洞 |
| Backslash Powered Scanner | 注入检测 |
| Upload Scanner | 文件上传检测 |
| Active Scan++ | 增强主动扫描 |

## CTF Web 题型速查

| 题型 | 解题思路 |
|------|---------|
| SQL 注入 | 判断闭合类型 → UNION → 注出数据 |
| 命令注入 | 绕过过滤 (空格/关键词黑名单) |
| 文件上传 | 绕过：Content-Type, 双截屏, .htaccess |
| 反序列化 | 构造 POP 链 |
| SSTI | 识别模板引擎 → 找 payload |
| SSRF | 绕过：302 跳转, DNS 重绑定, 进制转换 |
| XSS | 绕过 CSP, 过滤 |
| XXE | 外部实体 → 文件读取 |
| SSRF + XXE | 组合拳 |
| PHP 特性 | 弱类型, 反序列化, 伪协议 |
