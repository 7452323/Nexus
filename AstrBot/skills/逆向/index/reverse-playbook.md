---
name: reverse-playbook
description: 通用逆向实战框架。从实战案例（ONE App/chatgpt2api/HttpCall/tools.miku.ac）中提炼的7大通用逆向模式，遇到同类问题直接套方案。
author: 7452323 (从实战提炼)
category: reverse-engineering
tags:
  - playbook
  - pattern
  - reverse-engineering
  - methodology
  - case-study
---

# Reverse Playbook — 通用逆向实战框架

> 从实战中提炼，为实战服务。
> 以下所有模式均来自**真实逆向案例**，不是纸上谈兵。

---

## 📋 7 大通用逆向模式

| # | 模式 | 解决的问题 | 实战来源 |
|---|------|-----------|---------|
| 1 | 🏗️ **私有协议逆向** | 目标使用私有API协议、AES加密、自定义签名 | ONE App / chatgpt2api |
| 2 | 🪟 **桌面应用注入** | macOS WKWebView / Wails CDP 逆向 | HttpCall |
| 3 | 🌐 **Web 工具站批量提取** | tools.miku.ac 等工具站所有工具归档 | tools.miku.ac |
| 4 | 🐍 **PyInstaller 拆包** | 打包成单文件的 Python 应用逆向 | PyInstaller 实战 |
| 5 | 📱 **Flutter App 逆向** | Flutter libapp.so 反编译 + Key 提取 | ONE App |
| 6 | 🔐 **CDN 加密图片破解** | 服务端返回加密文件，客户端解密显示 | ONE App |
| 7 | 🔄 **AntI-anti-automation** | WAF/PoW/Turnstile/签名/Token 绕过 | chatgpt2api / ONE |

---

## 模式 1：私有协议逆向（最难也最常见）

### 适用判断
- [ ] 请求/响应不是明文 JSON/XML
- [ ] 有 sign/token/key/iv 等请求头
- [ ] 响应看起来是 Base64 乱码
- [ ] 页面加载后动态计算某些参数

### 解决套路

```
┌── 解构 ──────────────────────────────────────────┐
│  1. 确定技术栈（Flutter？原生？Web？Wails？）       │
│  2. 找到加密常量的存储位置（构造函数/HAR/strings）  │
│  3. 提取 Key/IV/Salt → 试解一个已知响应验证正确性  │
│  4. 找到签名算法 → 用 HAR 中的 sign 值验证         │
│  5. 找到无 Token 的入口点（bootstrap/init/guest）   │
└──────────────────────────────────────────────────┘
    ↓
    如果全部成功 → Python 复现完整协议
    如果某步卡住 → 换技术栈继续探索（Web版辅助分析）
```

### 实战对比：两种不同类型的私有协议

| 维度 | ONE App (Flutter) | ChatGPT (Web SPA) |
|------|-------------------|-------------------|
| 反编译工具 | Blutter | 无需（JS bundle 是文本） |
| 加密强度 | 高（全部AES加密） | 低（明文请求） |
| 认证方式 | uuid+user-key+sign → JWT | access_token Bearer |
| 签名算法 | MD5双层+salt | PoW challenge-response |
| 抗爬虫 | IP绑定+时间窗口 | Turnstile+PoW |
| 图片保护 | AES加密JPEG | 无额外保护 |

---

## 模式 2：桌面应用注入（macOS/Wails）

### 适用判断
- [ ] macOS 原生 App 或 Wails 二进制
- [ ] 应用有付费墙/订阅验证
- [ ] 验证通过 WebView 中的 JS API 调用

### 解决套路

```
发现是 Wails → strings 提取嵌入前端资源 → 找 AI prompt
发现是 macOS WKWebView → 
  ├── DYLD_INSERT_LIBRARIES 注入 dylib
  ├── dylib hook WKWebView → 注入 fetch 劫持 JS
  └── JS 拦截 API 响应 → 伪造 Pro 订阅
```

---

## 模式 3：Web 工具站批量提取

### 适用判断
- [ ] 一个域名下挂载几十个在线工具
- [ ] SPA 架构，单个 JS bundle 包含所有工具逻辑
- [ ] 目标是本地离线化/复用/集成

### 解决套路

```
1. 爬首页 → 发现所有工具入口
2. 下载 JS bundle → 搜索 API 端点
3. 对每个工具：
   └── 提取 API 端点 + 请求格式 + 核心逻辑
4. 归类输出：目录结构 / README / 实现代码
```

---

## 模式 4：PyInstaller 拆包

### 适用判断
- [ ] 可执行文件 5MB+
- [ ] strings 出现 `_MEIPASS` / `PyInstaller`
- [ ] 目标是一个 Python 应用

### 解决套路

```
pyinstxtractor → 解包 → .pyc → pycdc/uncompyle6 → 源码
├── strings 搜索 API Key / URL / 配置
└── 反编译后 grep 敏感关键字
```

---

## 模式 5：Flutter App 逆向

### 适用判断
- [ ] APK 中有 `libapp.so` + `libflutter.so`
- [ ] 难以用 jadx/Frida 追踪

### 解决套路

```
Blutter libapp.so → 搜索 aes/sign/http/token → 提取 Key/IV/Salt
├── 没有 Web 版？→ 全靠反编译和 HAR 抓包
├── 有 Web 版？→ Playwright 辅助分析 → 发现 CDN + 图片 Key
└── 两者都没有？→ 抓包 + 暴力猜测签名算法
```

---

## 模式 6：CDN 加密图片破解

### 适用判断
- [ ] 文章/图片 URL 在数据中返回
- [ ] 用 API 域名下载返回 500 / 404
- [ ] 图片在浏览器能正常显示（客户端解密）

### 解决套路

```
1. 判断图片是否加密：下载 → file 命令 → 熵值计算
2. 如果熵值 ~8.0 + file 说 "data" → 加密 ✓
3. 找解密 Key：
   ├── Flutter：去 main.dart.js 搜已知 Key 附近的字符串
   ├── Web：在 JS bundle 中搜 img_key / img_iv / decrypt
   └── 原生：strings 二进制搜 16 字节可疑字符串
4. 试 AES-128-CBC(Key, IV) 解密 → 前两个字节应为 FF D8 (JPEG)
```

---

## 模式 7：Anti-anti-automation（WAF/签名/Token 绕过三层防御）

### 适用判断
- [ ] 请求被 WAF 拦截（403/503/RST）
- [ ] 请求被签名验证拦截（401 sign invalid）
- [ ] Token 过期快且绑定 IP

### 解决套路

```
┌── 第一层：WAF/CDN ─────────────────────────────────┐
│  方案 A：curl_cffi 完整指纹伪造                       │
│  方案 B：Playwright 无头浏览器代理请求                │
│  方案 C：更换节点/代理                               │
└────────────────────────────────────────────────────┘
    ↓ 通过 WAF 但 401
┌── 第二层：签名验证 ─────────────────────────────────┐
│  方案 A：提取签名算法 → Python 复现                  │
│  方案 B：HAR 中的签名值 → 验证算法正确性             │
│  方案 C：找无签名的 bootstrap 端点                   │
└────────────────────────────────────────────────────┘
    ↓ 签名通过但 Token 过期
┌── 第三层：Token/IP 绑定 ────────────────────────────┐
│  方案 A：Bootstrap → 拿新 JWT → 立即调用 API        │
│  方案 B：Token 池 → 多个 token 轮询                 │
│  方案 C：固定 IP 通过代理调用                        │
└────────────────────────────────────────────────────┘
```

---

## 🧠 实战经验对比索引

对同一个东西从不同技能角度看，获取完整认知。

### ONE App 逆向（完整链路）

| 阶段 | 对应技能 | 关键产出 |
|------|---------|---------|
| 反编译 libapp.so | **android-reverse-engineering** → Flutter专项 | AES Key/IV/Salt |
| 签名破解 | **algorithm-reverse** → 签名通用模式 | MD5(MD5(concat)+salt) |
| 入口定位 | **find-crypto-entry** → 全面场景矩阵 | bootstrap 无Token端点 |
| 反自动化工 | **anti-debug** → 对抗模式 | AES加密响应/图片/JWT绑定 |
| 协议逆向 | **web-api-protocol-reverse** → ONE案例 | 协议全景+7步法 |

### chatgpt2api 逆向（完整链路）

| 阶段 | 对应技能 | 关键产出 |
|------|---------|---------|
| JS bundle 分析 | **camoufox-workflow** | fingerprint 伪造 |
| PoW 绕过 | **web-api-protocol-reverse** → chatgpt2api拆解 | sentinel token 机制 |
| 指纹伪造 | **env-patch** | 完整浏览器指纹栈 |
| 号池管理 | **web-api-protocol-reverse** | access_token 轮询/淘汰 |

---

## 🎯 快速启动模板

```python
# 新逆向任务启动模板
def reverse_task(target: str):
    steps = [
        ("技术栈识别", "file / strings / unzip / 目录结构"),
        ("工具选择", "Blutter / jadx / pyinstxtractor / Playwright / strings"),
        ("常量提取", "strings → grep Key/IV/Salt/URL/Token"),
        ("签名破解", "HAR对比 → 穷举算法 → Python复现"),
        ("入口点发现", "搜索 bootstrap/init/guest → 免Token入口"),
        ("管道打通", "Bootstrap→JWT→API调用→响应解密→数据提取"),
        ("自动化", "Python脚本 + Cron定时"),
    ]
    return steps
```
