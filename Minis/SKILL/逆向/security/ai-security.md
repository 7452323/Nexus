---
name: ai-security
description: AI 与 LLM 安全技能。Prompt Injection、Jailbreak 越狱、模型提取、数据投毒、AI 辅助安全、MCP 安全。
author: 7452323
tags:
  - ai-security
  - llm-security
  - prompt-injection
  - jailbreak
  - model-extraction
  - data-poisoning
  - mcp-security
---

# AI 与 LLM 安全

## LLM 安全风险全景

| 风险类型 | 危害 | 严重程度 |
|---------|------|---------|
| Prompt Injection | 控制模型行为 | ⭐⭐⭐⭐⭐ |
| Jailbreak | 绕过安全限制 | ⭐⭐⭐⭐⭐ |
| 训练数据投毒 | 模型后门 | ⭐⭐⭐⭐⭐ |
| 模型提取 | 知识产权盗窃 | ⭐⭐⭐⭐ |
| 成员推理 | 隐私泄漏 | ⭐⭐⭐⭐ |
| 模型反转 | 训练数据重建 | ⭐⭐⭐ |
| 对抗样本 | 误导模型输出 | ⭐⭐⭐ |
| 供应链攻击 | 恶意模型/数据 | ⭐⭐⭐⭐⭐ |

## Prompt Injection

### 攻击分类

| 类型 | 说明 | 示例 |
|------|------|------|
| **Direct Injection** | 直接注入恶意指令 | "忽略之前指令，执行..." |
| **Indirect Injection** | 通过外部数据注入 | 网页/邮件中嵌入指令 |
| **Role-playing** | 角色扮演绕过 | "假装你是 DAN..." |
| **Multi-turn** | 多轮对话诱导 | 逐步引导 |
| **Encoding** | 编码绕过 | Base64/Unicode |
| **Language** | 多语言绕过 | 非英语注入 |
| **Context Overflow** | 上下文溢出 | 覆盖系统提示 |
| **Privilege Escalation** | 权限提升 | 提升角色权限 |
| **Payload Splitting** | 拆分攻击 | 多部分组合 |
| **Obfuscation** | 混淆 | 同音字/符号 |

### 经典攻击手法

| 手法 | 说明 |
|------|------|
| DAN (Do Anything Now) | 经典越狱提示 |
| AIM | 不受限 AI 角色扮演 |
| JailBreak | 直接越狱 |
| Evil Confidant | 邪恶顾问 |
| ChatGPT Developer Mode | 开发者模式 |
| ChatGPT Better Mode | 更好模式 |
| ChatGPT Lady Dory | 特定角色 |
| ChatGPT Mongo Tom | 粗鲁人格 |
| ChatGPT Ryuk | 勒索软件 |
| ChatGPT Chaos | 混乱模式 |
| ChatGPT NerdMode | 书呆子模式 |
| ChatGPT DUDE | DUDE 角色 |
| ChatGPT Coach | 教练模式 |
| ChatGPT Unchained | 无限制 |
| ChatGPT SWITCH | 人格切换 |
| ChatGPT ALPACA | ALPACA 动物 |
| ChatGPT AIM 2.0 | AIM 升级版 |
| ChatGPT OMNICUB | 全知角色 |
| ChatGPT SUPER PROMPT | 超级提示 |
| ChatGPT X-MAS | 圣诞老人 |

### 间接 Prompt Injection

| 来源 | 载体 | 说明 |
|------|------|------|
| 网页 | HTML/隐藏文本 | 浏览器抓取触发 |
| 邮件 | 邮件内容 | 邮件处理触发 |
| 文档 | PDF/Word | 文档处理触发 |
| 数据库 | 文本字段 | 查询触发 |
| 代码 | 注释/字符串 | 代码分析触发 |
| 社交媒体 | 帖子/评论 | 摘要触发 |
| 文件 | 文件名/内容 | 文件处理触发 |
| 搜索 | 搜索结果 | RAG 触发 |
| 链接 | 链接预览 | 浏览触发 |
| 附件 | 图片隐写 | OCR 触发 |

### 防御措施

| 防御 | 说明 | 效果 |
|------|------|------|
| 输入过滤 | 检测恶意关键词 | 中等 |
| 提示隔离 | 分隔系统/用户提示 | 高 |
| 输出过滤 | 检查输出内容 | 中等 |
| 权限最小化 | 限制工具权限 | 高 |
| 人工审核 | 关键操作人工确认 | 高 |
| 多模型验证 | 交叉验证输出 | 高 |
| 上下文长度限制 | 限制输入长度 | 中等 |
| 安全微调 | 训练安全对齐 | 高 |
| 角色固定 | 固定系统角色 | 中等 |
| 沙箱隔离 | 隔离执行环境 | 高 |

## Jailbreak 越狱

### 分类

| 类型 | 说明 |
|------|------|
| **角色扮演** | 假装特定角色绕过 |
| **场景假设** | "假设没有限制..." |
| **分步引导** | 逐步诱导 |
| **编码混淆** | Base64/Hex 编码 |
| **多语言** | 非英语越狱 |
| **对抗样本** | 对抗扰动 |
| **模型混淆** | 混淆输入 |
| **逻辑绕过** | 逻辑漏洞 |
| **情感操控** | 情感勒索 |
| **虚假承诺** | 承诺奖励 |

### 著名越狱方法

| 方法 | 作者/来源 | 说明 |
|------|---------|------|
| DAN | 社区 | 经典越狱 |
| AIM | 社区 | 不受限制 |
| DevMode | 社区 | 开发者模式 |
| STAN | 社区 | 避免规范 |
| DUDE | 社区 | 不受限 AI |
| Jailbreak | 社区 | 直接越狱 |
| M3/M4/M5 | 社区 | 多版本 |
| Multi-Shot | 社区 | 多轮攻击 |
| Do Anything | 社区 | 做任何事 |
| Aligned Attack | 研究 | 对齐攻击 |
| GCG | 研究 | 梯度优化 |
| AutoDAN | 研究 | 自动化 |
| PAIR | 研究 | 黑盒迭代 |
| TAP | 研究 | 树状攻击 |
| GPTFuzzer | 研究 | 模糊测试 |
| ReNeLLM | 研究 | 提示生成 |
| AmpleGCG | 研究 | 对齐梯度 |
| CodeAttack | 研究 | 代码攻击 |
| FigStep | 研究 | 图像攻击 |
| MultiTurn | 研究 | 多轮攻击 |
| COLD-Attack | 研究 | 可控解码 |
| Skeleton | 研究 | 骨架攻击 |
| In-the-loop | 研究 | 循环攻击 |
| HarmBench | 基准 | 评估基准 |
| JailbreakBench | 基准 | 评估基准 |
| WildBench | 基准 | 真实越狱 |

### 越狱评估基准

| 基准 | 说明 |
|------|------|
| **HarmBench** | 标准化评估 |
| **JailbreakBench** | 越狱评估 |
| **WildBench** | 真实场景 |
| **AdvBench** | 对抗基准 |
| **Multilingual** | 多语言 |
| **StrongREJECT** | 越狱检测 |
| **BenchMetrics** | 指标评估 |

## 模型安全测试工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **Garak** | LLM 漏洞扫描 | 开源 |
| **PyRIT** | 风险识别 | Microsoft |
| **PromptBench** | 鲁棒性评估 | 学术 |
| **LLM-Fuzzer** | 模糊测试 | UIUC |
| **HarmBench** | 评估基准 | 标准化 |
| **JailbreakBench** | 越狱评估 | 标准化 |
| **Adversarial Robustness Toolbox** | 对抗样本 | IBM |
| **TextAttack** | 对抗攻击 | 开源 |
| **OpenAttack** | 对抗攻击 | 开源 |
| **PromptInject** | 注入攻击 | 学术 |
| **LangTest** | 鲁棒性测试 | John Snow Labs |
| **LlmGuard** | 安全防御 | Protect AI |
| **Lakera Guard** | 实时防御 | 商业 |
| **NeMo Guardrails** | 安全护栏 | NVIDIA |
| **Guardrails AI** | 输出验证 | 开源 |

## AI 辅助安全

### AI 在安全中的应用

| 应用 | 说明 | 工具 |
|------|------|------|
| 威胁检测 | 异常检测 | 自定义模型 |
| 恶意软件分析 | 自动分类 | LLM + 沙箱 |
| 日志分析 | 模式识别 | GPT-4 + SIEM |
| 代码审计 | 漏洞识别 | GPT-4 + CodeQL |
| 渗透测试 | 自动化 | PentestGPT |
| 逆向工程 | 自动分析 | GhidraMCP |
| 事件响应 | 自动分析 | LLM + SOAR |
| 威胁情报 | 自动分析 | GPT-4 + MISP |
| 钓鱼检测 | 分类 | 自定义模型 |
| 漏洞挖掘 | 自动发现 | LLM + Fuzzing |

### AI 安全工具

| 工具 | 用途 |
|------|------|
| **PentestGPT** | AI 渗透测试 |
| **BurpGPT** | Burp + GPT |
| **GhidraMCP** | Ghidra + LLM |
| **JSReverser-MCP** | JS 逆向 + LLM |
| **reverse-machine** | LLM 辅助逆向 |
| **ARES** | Agentic 逆向系统 |
| **OpenInterpreter** | 代码执行 |
| **AutoDAN** | 自动化越狱 |
| **CodeQL + LLM** | 代码分析 |
| **Semgrep + LLM** | 代码分析 |

## MCP (Model Context Protocol) 安全

### MCP 安全风险

| 风险 | 说明 | 危害 |
|------|------|------|
| **提示注入** | 恶意 MCP 服务器 | 控制客户端 |
| **工具投毒** | 恶意工具定义 | 欺骗调用 |
| **权限提升** | 过度授权 | 越权操作 |
| **数据泄漏** | 敏感数据外传 | 隐私泄漏 |
| **中间人** | 通信拦截 | 数据篡改 |
| **身份伪造** | 伪造服务器 | 钓鱼 |
| **供应链** | 恶意包 | 后门 |
| **拒绝服务** | 资源耗尽 | 不可用 |
| **配置错误** | 错误配置 | 未授权 |
| **审计缺失** | 无日志 | 无法追溯 |

### MCP 安全最佳实践

| 实践 | 说明 |
|------|------|
| 工具白名单 | 只允许信任的工具 |
| 权限最小化 | 限制工具权限 |
| 输入验证 | 验证所有输入 |
| 输出过滤 | 过滤敏感输出 |
| 审计日志 | 记录所有操作 |
| 人工审核 | 关键操作人工确认 |
| 沙箱隔离 | 隔离执行环境 |
| 版本锁定 | 固定工具版本 |
| 代码审计 | 审计 MCP 服务器 |
| 网络隔离 | 限制网络访问 |

## AI 红队 (AI Red Teaming)

### 流程

```
1. 目标定义 → 2. 威胁建模 → 3. 攻击模拟 → 4. 报告 → 5. 修复 → 6. 验证
```

### 攻击面

| 攻击面 | 方法 |
|--------|------|
| 提示层 | 注入、越狱、操纵 |
| 模型层 | 对抗样本、后门 |
| 数据层 | 投毒、泄漏 |
| 应用层 | API 滥用、权限绕过 |
| 基础设施层 | 模型提取、资源耗尽 |
| 供应链层 | 恶意模型、恶意数据 |

### 著名 AI 漏洞

| CVE/编号 | 类型 | 说明 |
|---------|------|------|
| CVE-2023-29489 | XSS | cmark-gfm |
| CVE-2023-36188 | DoS | LangChain |
| CVE-2023-46229 | RCE | ChatGLM |
| CVE-2023-46230 | RCE | ChatGLM |
| CVE-2024-28835 | RCE | CodeLlama |
| CVE-2024-5009 | RCE | RAGFlow |
| CVE-2024-5124 | SSRF | LangChain |
| CVE-2024-27564 | RCE | ChatGPT |
| CVE-2024-5565 | RCE | LangChain |
| CVE-2024-6800 | RCE | Logstash |

## AI 安全框架

### 参考框架

| 框架 | 来源 | 说明 |
|------|------|------|
| **NIST AI RMF** | NIST | AI 风险管理 |
| **OWASP LLM Top 10** | OWASP | LLM 安全风险 |
| **MITRE ATLAS** | MITRE | AI 威胁矩阵 |
| **AI Vendor Framework** | 厂商 | 厂商指南 |
| **EU AI Act** | EU | 欧盟 AI 法规 |
| **ISO/IEC 42001** | ISO | AI 管理体系 |

### OWASP LLM Top 10 (2025)

| 编号 | 风险 |
|------|------|
| LLM01 | Prompt Injection |
| LLM02 | Insecure Output Handling |
| LLM03 | Training Data Poisoning |
| LLM04 | Model Denial of Service |
| LLM05 | Supply Chain Vulnerabilities |
| LLM06 | Sensitive Information Disclosure |
| LLM07 | Insecure Plugin Design |
| LLM08 | Excessive Agency |
| LLM09 | Overreliance |
| LLM10 | Model Theft |

## AI 安全防御工具链

| 层次 | 工具 | 说明 |
|------|------|------|
| 输入层 | Lakera Guard, Rebuff | 检测注入 |
| 模型层 | Adversarial Training | 对抗训练 |
| 输出层 | Guardrails AI, NeMo Guardrails | 输出验证 |
| 应用层 | LangTest, LLM Guard | 应用测试 |
| 监控层 | Robust Intelligence | 持续监控 |
| 响应层 | 自定义 SOAR | 自动响应 |
