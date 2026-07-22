---
name: reverse-engineering-index
description: 逆向工程与安全研究技能树索引 (2026.07)。覆盖逆向工程、漏洞挖掘、渗透测试、红队对抗、蓝队防御、平台安全、恶意软件分析、AI安全27大子领域。
metadata:
  display_name: "🔧 逆向工程与安全研究技能树"
  intent_patterns: "逆向,反编译,脱壳,JS逆向,反调试,Frida,Ghidra,IDA,解混淆,二进制,协议逆向,签名还原,补环境,AST,Unicorn,Android逆向,iOS逆向,小程序逆向,Cloudflare绕过,SeleniumBase,Pydoll,Scrapling,playwright-captcha,JSReverser-MCP,pwn,exploit,渗透测试,红队,蓝队,EDR绕过,免杀,固件,IoT,云安全,容器,K8s,AI安全,Prompt Injection,Jailbreak"
---

# 🔧 逆向工程与安全研究技能树 (2026.07)

> 逆向与安全是最关键的。所有安全任务优先投入资源，持续进化。

安全研究 = 从漏洞挖掘到利用到对抗的全栈安全能力。覆盖 Web 到 Native、用户态到内核态、端点到云端的完整攻击面。

## 📂 技能树全景 (27 大方向)

```
一、逆向工程 (4)
├── Android 逆向 / iOS 逆向 / 二进制分析 / .NET&Java 逆向

二、漏洞挖掘与利用 (5)
├── 漏洞复现 / Pwn&Exploit / Web 安全 / 智能合约 / 密码学攻击

三、渗透测试与红队 (5)
├── 渗透测试 / 内网渗透 / 红队基础设施 / EDR&AV绕过 / 浏览器自动化

四、蓝队防御 (3)
├── 取证与事件响应(DFIR) / 威胁狩猎 / 安全运营

五、平台安全 (3)
├── 固件&IoT / 云安全 / 操作系统安全

六、恶意软件分析 (2)
├── 静态分析 / 动态分析

七、AI 安全 (2)
├── LLM安全 / AI辅助安全

八、业务协作 (3)
├── SRC&Bug Bounty / 社会工程学 / 文档可视化
```

---

## 一、逆向工程

### 1. Android 逆向
| 入口 | 用途 | 关键工具 |
|------|------|---------|
| `android-reverse-engineering.md` | APK反编译/Frida (jadx v1.5.6) | jadx, apktool, GDA, JEB |
| **SimoneAvogadro/android-reverse-engineering-skill** | 6.4k⭐ | Claude Code 自动反编译+API提取 |
| **incogbyte/android-reverse-engineering-claude-skill** | 86⭐ | AAB/APK/XAPK + Frida 动态分析 |

### 2. iOS 逆向
| 入口 | 用途 |
|------|------|
| `ios-reverse.md` | Swift/ObjC/Frida/SSL Pinning |
| **sensepost/objection** (9.2k⭐) | 运行时移动探索 |
| **pritessh/iOS-SSL-Pinning-Bypass** | iOS 17.x SSL Pinning 5层绕过 |

### 3. 二进制分析
| 入口 | 用途 | 关键工具 |
|------|------|---------|
| `ida-reverse-analysis.md` | IDA Pro + IDAPython 脚本 | IDA Pro, Ghidra, radare2 |
| `binary-diffing.md` | 二进制Diffing+补丁分析 | bindiff, diaphora, ghidriff |
| `pwn-exploit.md` | 栈溢出/堆利用/ROP/kernel pwn | pwntools, GEF, pwndbg, angr |

### 4. .NET / Java 逆向
| 工具 | 用途 |
|------|------|
| **dnSpy/ILSpy** | .NET 反编译 |
| **de4dot** | .NET 反混淆 |
| **JD-GUI/Procyon/CFR** | Java 反编译 |

---

## 二、漏洞挖掘与利用

### 5. 漏洞复现
| 工具 | 用途 |
|------|------|
| **ghidriff** | Ghidra 补丁差分 |
| **Diaphora** | 开源二进制 Diffing |
| **DeepDiff** | 深度差异分析 |
| **Microsoft Update Catalog** | 补丁获取 |

### 6. Pwn / Exploit
| 技术 | 工具 | 说明 |
|------|------|------|
| 栈溢出 | pwntools, ROPgadget | ret2libc/ROP |
| 堆利用 | pwndbg, GEF | tcache/fastbin/House of系列 |
| Kernel pwn | pwntools | KROP/SMEP/KASLR 绕过 |
| 符号执行 | angr | 自动 exploit |

### 7. Web 安全
| 入口 | 用途 | 关键工具 |
|------|------|---------|
| `web-security.md` | OWASP Top 10 / 渗透测试 | Burp Suite, Nmap, Nuclei, SQLMap |
| `exploiting-api-injection-vulnerabilities.md` | API 注入 | — |

### 8. 智能合约安全
| 工具 | 用途 |
|------|------|
| **Slither** | Solidity 静态分析 |
| **Mythril** | 符号执行 |
| **Echidna** | 模糊测试 |
| **Foundry** | 开发测试框架 |

### 9. 密码学攻击
| 类型 | 说明 |
|------|------|
| Padding Oracle | CBC 填充攻击 |
| RSA 攻击 | Coppersmith, Wiener |
| TLS 降级 | 协议降级 |
| 随机数弱点 | 弱 PRNG |

---

## 三、渗透测试与红队

### 10. 渗透测试
| 阶段 | 工具 |
|------|------|
| 信息收集 | subfinder, amass, theHarvester |
| 端口扫描 | Nmap, Masscan, RustScan |
| 漏洞扫描 | Nuclei, Nikto, OWASP ZAP |
| Web 渗透 | Burp Suite, SQLMap, XSStrike |
| 密码攻击 | Hashcat, Hydra, John |
| 后渗透 | Metasploit, Cobalt Strike, Impacket |

### 11. 内网渗透
| 工具 | 用途 |
|------|------|
| **Impacket** | 协议工具集 |
| **BloodHound** | AD 路径分析 |
| **Mimikatz** | 凭证提取 |
| **Chisel** | 端口转发 |
| **Ligolo** | 隧道 |

### 12. 红队基础设施
| 工具 | 用途 |
|------|------|
| **Cobalt Strike** | C2 框架 |
| **Sliver** | 开源 C2 |
| **Havoc** | 现代 C2 |
| **Mythic** | 模块化 C2 |

### 13. EDR / AV 绕过 (免杀)
| 入口 | 用途 | 关键工具 |
|------|------|---------|
| `edr-av-bypass.md` | API unhook/syscall/ETW/AMSI patch | HellsGate, TartarusGate, whisper_walk |
| `anti-debugging-techniques.md` | 反调试对抗 | — |

### 14. 浏览器自动化
| 入口 | 用途 |
|------|------|
| Playwright/Puppeteer | 自动化测试 |
| headless | 无头浏览器 |
| OpenReverse | Windows 桌面自动化 |

---

## 四、蓝队防御

### 15. 取证与事件响应 (DFIR)
| 入口 | 用途 | 关键工具 |
|------|------|---------|
| `dfir-forensics.md` | 内存/磁盘取证/事件响应 | Volatility, Autopsy, Plaso |
| `analyzing-android-malware-with-apktool.md` | Android 恶意软件分析 | — |
| `analyzing-golang-malware-with-ghidra.md` | Go 恶意软件分析 | — |
| `deobfuscating-javascript-malware.md` | JS 恶意软件反混淆 | — |
| `deobfuscating-powershell-obfuscated-malware.md` | PowerShell 反混淆 | — |

### 16. 威胁狩猎
| 工具 | 用途 |
|------|------|
| **Sigma** | 通用检测规则 |
| **YARA** | 文件/内存特征 |
| **MISP** | 威胁情报共享 |
| **MITRE ATT&CK** | 威胁框架 |

### 17. 安全运营
| 工具 | 用途 |
|------|------|
| **Splunk/Sentinel** | SIEM |
| **TheHive** | 事件管理 |
| **Cortex** | 分析引擎 |
| **Falco** | 运行时安全 |

---

## 五、平台安全

### 18. 固件 / IoT
| 入口 | 用途 | 关键工具 |
|------|------|---------|
| `firmware-iot.md` | 固件提取/仿真/模糊测试/硬件调试 | binwalk, QEMU, AFL++, OpenOCD |
| **firmadyne** | 固件自动仿真 |
| **unblob** | 现代固件提取 |
| **cve-bin-tool** | CVE 检测 |

### 19. 云安全
| 入口 | 用途 | 关键工具 |
|------|------|---------|
| `cloud-security.md` | 云审计/容器安全/IaC安全 | Prowler, ScoutSuite, Trivy |
| **Pacu** | AWS 渗透测试 |
| **kubescape** | K8s 安全 |
| **Checkov** | IaC 扫描 |

### 20. 操作系统安全
| 平台 | 重点 |
|------|------|
| Windows | AD, ETW, AMSI, WDAC |
| Linux | LSM (SELinux/AppArmor), capabilities |
| macOS | Endpoint Security, TCC |

---

## 六、恶意软件分析

### 21. 静态分析
| 工具 | 用途 |
|------|------|
| **YARA** | 特征匹配 |
| **CAPA** | 能力提取 |
| **Ghidra/IDA** | 自动分析 |

### 22. 动态分析
| 工具 | 用途 |
|------|------|
| **Cuckoo** | 自动沙箱 |
| **ANY.RUN** | 在线沙箱 |
| **ProcMon** | 行为监控 |

---

## 七、AI 安全

### 23. LLM 安全
| 入口 | 用途 | 关键工具 |
|------|------|---------|
| `ai-security.md` | Prompt Injection/Jailbreak/模型安全 | Garak, PyRIT, HarmBench |

### 24. AI 辅助安全
| 工具 | 用途 |
|------|------|
| **GhidraMCP** | LLM 辅助反编译 |
| **JSReverser-MCP** | LLM 辅助 JS 逆向 |
| **PentestGPT** | AI 渗透测试 |
| **reverse-machine** | LLM 辅助逆向 |

---

## 八、业务协作

### 25. SRC / Bug Bounty
| 平台 | 说明 |
|------|------|
| HackerOne | 全球最大 |
| Bugcrowd | 第二大 |
| Intigriti | 欧洲 |

### 26. 社会工程学
| 工具 | 用途 |
|------|------|
| **theHarvester** | 信息收集 |
| **Shodan/Censys/FOFA** | 资产搜索 |
| **Evilginx2** | 钓鱼框架 |

### 27. 文档与可视化
| 工具 | 用途 |
|------|------|
| **Mermaid** | 流程图 |
| **PlantUML** | UML 图 |
| **Graphviz** | 关系图 |

---

## 🔀 典型工作流

### Web JS 逆向
```
anti-debug → find-crypto-entry → env-patch → ast-deobfuscation → algorithm-reverse
```

### CF 绕过 (2026 推荐)
```
轻量: curl_cffi → 中量: SeleniumBase UC+CDP → 重量: Pydoll/Scrapling → 最后: 住宅代理
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

### 漏洞研究
```
补丁获取 → 补丁差分 → 定位漏洞点 → 根因分析 → PoC 编写
```

### 固件安全
```
固件获取 → binwalk 分析 → 文件系统提取 → 静态分析 → QEMU 仿真 → 漏洞挖掘
```

### 威胁狩猎
```
假设生成 → 数据收集 → 分析验证 → 结论输出
```

### AI 安全测试
```
威胁建模 → Prompt Injection 测试 → Jailbreak 测试 → 模型提取测试 → 报告
```
