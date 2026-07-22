---
name: reverse-engineering-index
description: 逆向工程与安全研究技能树索引 (2026.07)。覆盖27大子领域。
metadata:
  display_name: "🔧 逆向工程与安全研究技能树"
  intent_patterns: "逆向,反编译,脱壳,JS逆向,反调试,Frida,Ghidra,IDA,解混淆,二进制,协议逆向,签名还原,补环境,AST,Unicorn,Android逆向,iOS逆向,小程序逆向,Cloudflare绕过,SeleniumBase,Pydoll,Scrapling,playwright-captcha,JSReverser-MCP,pwn,exploit,渗透测试,红队,蓝队,EDR绕过,免杀,固件,IoT,云安全,容器,K8s,AI安全,Prompt Injection,Jailbreak"
---

# 🔧 逆向工程与安全研究技能树 (2026.07)

> 逆向与安全是最关键的。所有安全任务优先投入资源，持续进化。

安全研究 = 从漏洞挖掘到利用到对抗的全栈安全能力。覆盖 Web 到 Native、用户态到内核态、端点到云端的完整攻击面。

## 📂 子领域索引

### 一、逆向工程 (4)
1. **Android 逆向** — `mobile/android-reverse-engineering.md`
2. **iOS 逆向** — `mobile/ios-reverse.md`
3. **二进制分析** — `binary/ida-reverse-analysis.md`, `binary/pwn-exploit.md`
4. **.NET / Java 逆向** — dnSpy/ILSpy, JD-GUI

### 二、漏洞挖掘与利用 (5)
5. **漏洞复现** — `binary/binary-diffing.md` (ghidriff, diaphora)
6. **Pwn / Exploit** — `binary/pwn-exploit.md` (pwntools, GEF, angr)
7. **Web 安全** — `security/web-security.md` (Burp, Nmap, Nuclei)
8. **智能合约** — Slither, Mythril, Echidna
9. **密码学攻击** — 见解密技能

### 三、渗透测试与红队 (5)
10. **渗透测试** — `security/web-security.md`
11. **内网渗透** — Impacket, BloodHound, Mimikatz
12. **红队基础设施** — Cobalt Strike, Sliver, Havoc
13. **EDR / AV 绕过** — `security/edr-av-bypass.md` (syscall, unhook, ETW/AMSI patch)
14. **浏览器自动化** — Playwright, headless, OpenReverse

### 四、蓝队防御 (3)
15. **取证与事件响应 (DFIR)** — `security/dfir-forensics.md` (Volatility, Autopsy)
16. **威胁狩猎** — Sigma, YARA, MISP, MITRE ATT&CK
17. **安全运营** — Splunk, TheHive, Falco

### 五、平台安全 (3)
18. **固件 / IoT** — `extra/firmware-iot.md` (binwalk, QEMU, AFL++)
19. **云安全** — `security/cloud-security.md` (Prowler, Trivy)
20. **操作系统安全** — Windows AD, Linux LSM, macOS ES

### 六、恶意软件分析 (2)
21. **静态分析** — YARA, CAPA, Ghidra
22. **动态分析** — Cuckoo, ANY.RUN, ProcMon

### 七、AI 安全 (2)
23. **LLM 安全** — `security/ai-security.md` (Garak, PyRIT, HarmBench)
24. **AI 辅助安全** — GhidraMCP, JSReverser-MCP, PentestGPT

### 八、业务协作 (3)
25. **SRC / Bug Bounty** — HackerOne, Bugcrowd
26. **社会工程学** — theHarvester, Shodan, Evilginx2
27. **文档与可视化** — Mermaid, PlantUML, Graphviz

## 🔀 典型工作流

### Web JS 逆向
```
anti-debug → find-crypto-entry → env-patch → ast-deobfuscation → algorithm-reverse
```

### 渗透测试
```
情报收集 → 漏洞扫描 → 渗透攻击 → 后渗透 → 报告
```

### 红队评估
```
初始访问 → 权限提升 → 横向移动 → 持久化 → C2 → 目标达成
```

### 事件响应
```
准备 → 检测 → 遏制 → 根除 → 恢复 → 总结
```

### 固件安全
```
固件获取 → binwalk 分析 → 文件系统提取 → 静态分析 → QEMU 仿真 → 漏洞挖掘
```
