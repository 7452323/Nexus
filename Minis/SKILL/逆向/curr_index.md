Hermes逆向技能树-INDEX总索引

INDEX.md

# Hermes 逆向技能树 — 完整索引

> 自动更新于 2026-06-02
> 私有 Gist 专属文件夹，归 7452323 所有

---

## 📁 索引结构

| # | 技能名称 | 分类 | 描述 | 文件数 |
|---|---------|------|------|--------|
| 1 | algorithm-reverse | JS逆向 | 签名还原、混合加密拆解、Cookie/Header签名、JSVMP/Wasm | 1 |
| 2 | android-reverse-engineering | 移动端 | APK反编译/smali修改/Frida Hook/JNI分析/脱壳/重打包 | 1 |
| 3 | anti-debug | JS逆向 | 反调试对抗：无限debugger(9种)、DevTools检测、时间/属性检测 | 1 |
| 4 | ast-deobfuscation | 反混淆 | Babel AST分层反混淆，7步流程+8站点适配器 | 1 |
| 5 | binary-diffing | 二进制 | Diaphora/BinDiff二进制对比、补丁分析、1-day漏洞识别 | 1 |
| 6 | book-source-master | 代理脚本 | Legado阅读3.0书源编写，API/HTML双模式 | 1 |
| 7 | camoufox-workflow | JS逆向 | 6阶段工作流，JSVMP双路径分析，camoufox-reverse MCP | 1 |
| 8 | code-obfuscation-deobfuscation | 混淆分析 | JS/Python/Android混淆类型识别/分析/还原 | 1 |
| 9 | context-optimizer | 工具 | 长会话上下文精简，P0-P3优先级分级 | 1 |
| 10 | cross-platform-proxy-scripting | 代理脚本 | QX/Surge/Loon/Egern/Stash/Shadowrocket多平台适配 | 1 |
| 11 | deobfuscator | 反混淆 | jsjiami/sojson/obfuscator.io/packer/jsfuck/RC4一键还原 | 1 |
| 12 | desktop-app-reverse-engineering | 桌面端 | Wails/Electron/Tauri逆向 + WKWebView注入 + HttpCall AI管道提取 | 1 |
| 13 | env-patch | JS逆向 | Node.js补环境，3层策略(L1→L2→L3)，4种注入方式 | 1 |
| 14 | find-crypto-entry | JS逆向 | 加密参数入口定位，5种题型对应策略 | 1 |
| 15 | har-to-proxy-script | 代理脚本 | HAR→QX/Surge/Loon代理脚本转换 | 1 |
| 16 | ida-reverse-analysis | 二进制 | IDAPython/加密算法识别/DLL分析/F5优化/binary patch | 1 |
| 17 | pyinstaller-reverse | Python | PyInstaller打包应用逆向：解包→反编译→逻辑还原全流程 | 1 |
| 18 | qx-script-master | 代理脚本 | QX/Surge/Loon全能脚本编写，5大类型+HAR解析+Env.js | 1 |
| 19 | web-api-protocol-reverse | Web协议 | ChatGPT官网私有协议逆向：PoW/Turnstile/SSE/号池管理 | 1 |
| 20 | web-tool-reverse-engineer | Web工具站 | tools.miku.ac等在线工具站批量逆向方法论 | 1 |

---

## 🧠 9大逆向子领域

### 1. JS逆向
- algorithm-reverse — 签名/加密算法还原
- anti-debug — 反调试对抗
- ast-deobfuscation — AST反混淆
- camoufox-workflow — JS逆向全流程
- env-patch — 补环境
- find-crypto-entry — 加密入口定位

### 2. 反调试/反混淆
- anti-debug — 9种debugger模式+5种检测绕过
- ast-deobfuscation — Babel AST分层反混淆
- code-obfuscation-deobfuscation — 混淆分析
- deobfuscator — 一键反混淆

### 3. 桌面应用逆向
- desktop-app-reverse-engineering — WKWebView注入+fetch劫持+AI管道提取

### 4. 移动端逆向
- android-reverse-engineering — APK/Frida/JNI

### 5. Web API 协议逆向
- web-api-protocol-reverse — ChatGPT式私有协议逆向
- web-tool-reverse-engineer — 在线工具站批量逆向

### 6. 代码混淆/反混淆
- deobfuscator — 一键还原
- code-obfuscation-deobfuscation — 类型识别+分析
- ast-deobfuscation — AST反混淆

### 7. 二进制逆向
- binary-diffing — 二进制对比
- ida-reverse-analysis — IDA分析

### 8. 代理脚本开发
- cross-platform-proxy-scripting — 多平台适配
- qx-script-master — 5大脚本类型
- har-to-proxy-script — HAR转换
- book-source-master — 书源编写

### 9. Python 应用逆向
- pyinstaller-reverse — PyInstaller解包+反编译

---

## 🆕 本次更新内容 (2026-06-02)

### 新增技能 (3个)
1. **web-api-protocol-reverse** — ChatGPT官网私有协议逆向，PoW/Turnstile绕过，号池管理
2. **web-tool-reverse-engineer** — tools.miku.ac等在线工具站的批量逆向方法论
3. **pyinstaller-reverse** — PyInstaller打包应用逆向全流程

### 完善技能 (2个)
1. **desktop-app-reverse-engineering** — 新增 HttpCall AI Pipeline 逆向方法、fetch劫持、CDP注入
2. **web-api-protocol-reverse** — chatgpt2api深度技术拆解 (OpenAIBackendAPI/号池/PoW/SSE)

### 知识来源
- chatgpt2api (basketikun/chatgpt2api) — ChatGPT协议逆向
- HttpCall 应用逆向 (Wails + AI分析) — 桌面AI管道提取
- tools.miku.ac — 在线工具站逆向方法论
- Akino-CodeBuddy 双脑异步工作流 — soul-v2.md

---

## 🔗 Gist 分布

| Batch | Gist ID | 文件数 | 内容 |
|-------|---------|--------|------|
| Batch1 | 11fddac2b2db7d6003ad09e0267c5f1b | 9个文件 | JS逆向核心 (algorithm-reverse, anti-debug, ast-deobfuscation, env-patch, find-crypto-entry, deobfuscator, code-obfuscation, camoufox-workflow) |
| Batch2 | 3b062cd7ba635d81bee8de694483b9d1 | 8个文件 | 代理脚本 (qx-script-master, cross-platform-proxy-scripting, har-to-proxy-script, book-source-master + android-reverse, desktop-app-reverse, binary-diffing, ida-reverse-analysis) |
| Batch3 | 090b722f263684dca00a84ed978c97dd | 1个文件 | 辅助技能 (context-optimizer) |
| **New** | — | 3个文件 | **web-api-protocol-reverse, web-tool-reverse-engineer, pyinstaller-reverse** |
| INDEX | 8d33c9afc872823cc0b1025882c3fea21 | 1个文件 | 总索引 |

---

> **总技能数: 23** (18原技能 + 3新增)
> 覆盖: JS逆向 / 反调试 / 反混淆 / 桌面逆向 / 移动端 / Web协议 / 二进制 / 代理脚本 / Python逆向


### ONE App 逆向实战 (2026-06-02)

| 技能 | 更新内容 | 来源 |
|------|----------|------|
| **android-reverse-engineering** | 新增 Flutter 逆向专项（Blutter反编译、AES/Sign提取、CDN图片解密、5步实战路径） | one-app-api-reverse.md |
| **web-api-protocol-reverse** | 新增 ONE App 私有协议逆向案例（七步法、认证死循环破解、JW时间窗口、CDN加密图片） | one-app-api-reverse.md |

**ONE App 逆向关键参数**
- AES: `l*bv%Ziq000Biaog` / IV: `8597506002939249`
- Sign: `MD5(MD5(ip.platform.ts.uk.uuid) + salt)`
- CDN: `enimg.k8b3rsp.com` (图片AES加密)
- 自动化: `/root/one_daily_bot.py` 每天7点BJ推送TG

### 通用实战框架 (2026-06-02)

| # | 技能名称 | 分类 | 描述 |
|---|---------|------|------|
| 21 | **reverse-playbook** | 通用框架 | 7大通用逆向模式：私有协议/桌面注入/Web工具站/PyInstaller/Flutter/CDN加密/Anti-anti-automation |

### 实战经验全面沉淀

| 原有技能 | 新增实战模式 | 来源 |
|---------|------------|------|
| **algorithm-reverse** | 签名算法逆向通用模式（5种哈希+5种拼接+穷举框架） | ONE App + chatgpt2api + HttpCall |
| **find-crypto-entry** | 加密入口定位通用框架（全场景矩阵+4种入口类型+决策树） | ONE App + chatgpt2api + HttpCall + PyInstaller |
| **anti-debug** | 逆向过程中的反调试对抗通用模式（8种对抗类型+绕过矩阵） | chatgpt2api + ONE App |
| **reverse-playbook ⭐新** | 7大通用逆向模式+实战对比索引+快速启动模板 | 全部实战案例汇总 |

### JSRPC 全自动逆向方案 (2026-06-02)

吸收自 Fausto-404/js-reverse-automation--skill

| # | 技能名称 | 更新/新增 | 内容 |
|---|---------|----------|------|
| 22 | **jsrpc-auto-reverse** ⭐新 | 新增 | JSRPC + Flask + autoDecoder + CDP MCP 全自动 JS 逆向方案 |
| 7 | **camoufox-workflow** | 完善 | 加入 JSRPC 替代补环境的 4 种场景对比 + 完整方案架构 |
| 21 | **web-api-protocol-reverse** | 完善 | 加入 Chrome DevTools MCP 协议逆向辅助 + initScript 预注入 + Webpack 模块发现 + 7维度评分 |

**核心创新点：**
1. JSRPC — 不补环境，直接连真实浏览器 WebSocket 调加密函数
2. Chrome DevTools MCP — initScript 预注入 Hook 探针（绕过所有早期检测）
3. Phase 0-8 契约化流程 — 每阶段有明确定义输入/输出/成功条件/失败降级
4. 7 维度评分系统 — 自动筛选加密函数候选（name/source/runtime/request/IO/module/verification）
5. Webpack 4 级优先级链 — 自动发现模块中的加密函数
6. autoDecoder 集成 — 一键对接 Burp，端到端加解密

**引用工具：** JsRpc / autoDecoder / chrome-devtools-mcp

index_current.md


---

## 📊 QX/Surge/Loon 生态吸收清单（2026-06-02）

本次从 46 个项目中吸收的知识已注入 `qx-script-master v4.0` 和 `cross-platform-proxy-scripting v2.0`：

**核心吸收：**
1. 去广告三大流派：墨鱼流（应用级JSON删字段）、毒奶流（网页CSS+JS注入）、疯狗流（800万规则集）
2. 46 项目全景索引：全能型/去广告/会员解锁/模块转换/流媒体 5 大分类
3. 模块互转工具链：Script-Hub / LoonKissSurge / 自定义构建工具
4. reject家族详解：reject/reject-200/reject-img/reject-dict/reject-array
5. RevenueCat/QX/Surge/Loon 配置语法速查
6. 多平台统一架构：QX/Surge/Loon/Egern/Stash/Shadowrocket 6 平台
7. 800万规则集切片经验
8. QuanMock 响应 Mock 模式
9. 730+ App 去广告规则引用
10. JQ 表达式在 Surge 中的使用

**来源项目清单（46个）：**
ddgksf2013(13k) blackmatrix7(26k) Orz-3(4.5k) NobyDa(8.4k) limbopro(4.4k) Hacklous(11k) Peng-YM xiaomaoJT luestr fmz200 sve1r zqzess QingRex(745) LOWERTOP(3.4k) Rabbit-Spec I-am-R-E(1k) SukkaW mist-whisper Moli-X Keywos 89996462(918) czy13724 SheepFJ(457) TributePaulWalker ByteSheepStudio Maasea Mike-offers deezertidal Yarmukhamedov Koolson Orz-3/mini(2.1k) app2smile Guding88 gjwj666 chxm1023 nzw9314 Tartarus2014 zZPiglet Naveen alexshen223 cysk003 Yu9191

Nexus 仓库对应目录：`Hermes/skills/qx-script-master/` + `Hermes/skills/cross-platform-proxy-scripting/`

SKILL.md

---
name: reverse-engineering-index
description: 逆向工程技能树索引。覆盖JS逆向、反调试对抗、桌面/移动端逆向、Web API逆向、VM/字节码逆向、代码混淆、二进制逆向、协议逆向、恶意软件分析9大子领域。查找对应skill的入口。
author: 7452323 (converted from Private Gist)
category: reverse-engineering
---

# 🔧 逆向工程技能树

逆向工程 = 从编译产物还原逻辑。本技能树覆盖从 Web JS 到 Native SO、从二进制到协议的全栈逆向场景。

## 📂 子领域索引

### 1. JS 逆向核心
| Skill | 用途 |
|-------|------|
| `camoufox-workflow` | JS逆向工作流——6阶段全流程 |
| `find-crypto-entry` | 定位加密参数生成入口 |
| `env-patch` | JS补环境——Node.js引擎+策略分离 |
| `ast-deobfuscation` | Babel AST分层定向反混淆 |
| `algorithm-reverse` | JS逆向算法还原——签名/混合加密 |
| `anti-debug` | JS反调试对抗 |

### 2. 反调试对抗
| Skill | 用途 |
|-------|------|
| `anti-debug` | JS反调试——4类反调试识别+绕过 |
| `anti-debugging-techniques` | 反调试检测+绕过通用playbook |

### 3. 桌面/移动端逆向
| Skill | 用途 |
|-------|------|
| `desktop-app-reverse-engineering` | 桌面应用逆向——Electron/Wails/Tauri |
| `android-reverse-engineering` | Android应用逆向——APK反编译/Frida |
| `ida-reverse-analysis` | IDA Pro逆向分析 |

### 4. Web API 逆向
| Skill | 用途 |
|-------|------|
| `camoufox-workflow` | JS逆向工作流+签名还原 |
| `har-to-proxy-script` | HAR抓包→代理脚本 |
| `cross-platform-proxy-scripting` | 跨平台代理脚本编写 |

### 5. 代码混淆/反混淆
| Skill | 用途 |
|-------|------|
| `code-obfuscation-deobfuscation` | 混淆分析+反混淆playbook |
| `deobfuscator` | JavaScript反混淆解密 |
| `ast-deobfuscation` | Babel AST反混淆 |

### 6. 其他逆向
| Skill | 用途 |
|-------|------|
| `binary-diffing` | 二进制Diffing+补丁分析 |
| `book-source-master` | Legado阅读3.0书源编写 |
| `qx-script-master` | Quantumult X/Surge脚本 |

## 🔀 典型工作流

### Web JS 逆向全流程
```
anti-debug → find-crypto-entry → env-patch → ast-deobfuscation → algorithm-reverse
```

### 移动端逆向全流程
```
android-reverse-engineering → ida-reverse-analysis
```

### 1-day漏洞研究
```
binary-diffing → 定位修改函数 → 分析修改内容
```

## 📊 2026-06-02 增量吸收（13 新技能）

从本地技能包安装的 13 个新技能，不覆盖已有的 23 个技能。

| # | 技能名称 | 分类 | 描述 | 文件数 |
|---|---------|------|------|--------|
| 21 | ios-app-unlock | iOS逆向 | Swift5反射元数据+二进制Patch解锁Pro功能，适用于StoreKit 2已解密IPA | 1 |
| 22 | js-reverse-engineering | JS逆向 | JS逆向6阶段总纲：Observe→Capture→Rebuild→Patch→Pure→Port | 1 |
| 23 | js-reverse-mcp-integration | JS逆向 | 基于Patchright反检测引擎的JS调试MCP服务器，23种工具 | 1 |
| 24 | jsvmp-reverse | JS逆向 | JSVMP虚拟机逆向：数据驱动+AST反编译双路线，7种VM Hook | 1 |
| 25 | protocol-reverse-engineering | 网络协议 | 未知协议逆向：结构分析、消息格式还原、状态机推断 | 1 |
| 26 | reverse-engineering-general | 通用逆向 | 8子技能：Frida/Unicorn/DEX脱壳/Unity IL2CPP/IDAPython等 | 1 |
| 27 | ruishu-reverse | 反爬 | 瑞数Rivers Security反爬纯算逆向：Cookie T生成+URL后缀 | 1 |
| 28 | so-native-analysis | 二进制 | 30种工具覆盖SO分析/Flutter专项/二进制修改 | 1 |
| 29 | symbolic-execution-tools | 二进制 | 符号执行工具集：angr分析实战，覆盖CFG/约束求解 | 1 |
| 30 | vm-and-bytecode-reverse | 反混淆 | 通用VM/字节码逆向：指令集提取→语义还原→模拟器重放 | 1 |
| 31 | web-api-reverse-engineering | Web协议 | API协议逆向：端点发现/AES-ECB加密通信还原/OpenAI适配 | 1 |
| 32 | web-api-to-openai-proxy | Web协议 | 任意Web API→OpenAI兼容代理：协议逆向→Docker部署 | 1 |
| 33 | webpack-unpack | JS逆向 | Webpack打包模块提取：__webpack_require__→独立JS还原 | 1 |

合计：现有 23 + 新增 13 = **33 个技能**（另有书籍/playbook/索引辅助类）
