---
name: routing
description: 三轴路由矩阵（目标类型 × 用户意图 × 工具链）。根据用户输入自动路由到对应子技能。
---

# 路由矩阵

## 三轴路由

### 轴1: 目标类型

| 目标类型 | 入口 |
|---------|------|
| Web SPA / 前端 JS | → `js-reverse/` |
| Web API / 接口协议 | → `web-api/` |
| 桌面应用 (.app/.exe) | → `desktop/` |
| Android APK | → `mobile/` |
| iOS IPA | → `SKILL.md#iOS` |
| 二进制文件 (ELF/PE) | → `binary/` |
| Cloudflare 保护 | → `web-api/cf-bypass.md` |
| Web 漏洞 | → `security/web-security.md` |
| 内核/CTF Pwn | → `binary/pwn-exploit.md` |
| 恶意软件 | → `security/` |
| 固件/路由器 | → `extra/firmware-iot.md` |
| 云环境/K8s | → `security/cloud-security.md` |
| LLM/AI 模型 | → `security/ai-security.md` |

### 轴2: 用户意图

| 用户意图 | 路由 |
|---------|------|
| 签名/加密参数 | → `js-reverse/find-crypto-entry.md` |
| 补环境复现 | → `js-reverse/env-patch.md` |
| 反混淆 | → `js-reverse/ast-deobfuscation.md` |
| 绕过 CF | → `web-api/cf-bypass.md` |
| 协议还原 | → `web-api/web-api-protocol-reverse.md` |
| 桌面解锁 | → `desktop/desktop-app-reverse.md` |
| APK 反编译 | → `mobile/android-reverse.md` |
| CTF/Pwn/漏洞利用 | → `binary/pwn-exploit.md` |
| EDR/AV 绕过/免杀 | → `security/edr-av-bypass.md` |
| 渗透测试/内网 | → `security/web-security.md` |
| 威胁狩猎/取证 | → `security/dfir-forensics.md` |
| AI 安全测试 | → `security/ai-security.md` |
| 固件分析 | → `extra/firmware-iot.md` |
| 云安全/容器 | → `security/cloud-security.md` |
| 恶意软件 | → `security/` |
| 代理脚本 | → `proxy-script/` |
| AI 辅助分析 | → `ai-driven-reverse.md` |

### 轴3: 工具链

| 可用工具 | 路由 |
|---------|------|
| 只有 Minis 浏览器 | → `js-reverse/` (浏览器取证) |
| + Python/Node | → `js-reverse/` + 本地复现 |
| + SeleniumBase/Pydoll/Scrapling | → `web-api/cf-bypass.md` |
| + Burp Suite | → `web-api/web-api-protocol-reverse.md` |
| + Frida/Ghidra | → `binary/` |
| + pwntools/GEF/pwndbg | → `binary/pwn-exploit.md` |
| + Volatility/Autopsy | → `security/dfir-forensics.md` |
| + Nmap/Nuclei/Burp | → `security/web-security.md` |

## 自动路由规则

```
IF 用户提到 "Cloudflare/CF/Turnstile/5秒盾":
    → web-api/cf-bypass.md

IF 用户提到 "JS逆向/签名/加密参数/补环境":
    → js-reverse/SKILL.md

IF 用户提到 "API逆向/协议还原/OpenAI/ChatGPT":
    → web-api/web-api-protocol-reverse.md

IF 用户提到 "APK/Android/反编译":
    → mobile/android-reverse.md

IF 用户提到 "桌面应用/Electron/Wails":
    → desktop/desktop-app-reverse.md

IF 用户提到 "反调试/debugger":
    → js-reverse/anti-debug.md

IF 用户提到 "混淆/反混淆/AST":
    → js-reverse/ast-deobfuscation.md

IF 用户提到 "恶意软件/病毒/木马":
    → security/

IF 用户提到 "代理脚本/QX/Surge":
    → proxy-script/

IF 用户提到 "AI逆向/Ghidra/LLM":
    → ai-driven-reverse.md

IF 用户提到 "Pwn/CTF/漏洞利用/栈溢出/堆利用":
    → binary/pwn-exploit.md

IF 用户提到 "EDR/AV绕过/免杀/syscall/unhook":
    → security/edr-av-bypass.md

IF 用户提到 "渗透测试/内网/横向移动/提权":
    → security/web-security.md

IF 用户提到 "取证/事件响应/威胁狩猎/内存分析":
    → security/dfir-forensics.md

IF 用户提到 "固件/IoT/路由器/binwalk/QEMU":
    → extra/firmware-iot.md

IF 用户提到 "云安全/K8s/容器/云原生":
    → security/cloud-security.md

IF 用户提到 "AI安全/Prompt Injection/Jailbreak":
    → security/ai-security.md
```
