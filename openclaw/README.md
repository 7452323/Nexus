<div align="center">
  <img src="https://img.shields.io/badge/OpenClaw-v2026.5.2%2B-8B5CF6?style=for-the-badge&logo=openai&logoColor=white" alt="OpenClaw">
  <img src="https://img.shields.io/badge/Skills-19-10B981?style=for-the-badge&logo=bookstack&logoColor=white" alt="19 Skills">
  <img src="https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge&logo=bookstack&logoColor=white" alt="MIT">
  <img src="https://img.shields.io/badge/Maintained-Yes-EF4444?style=for-the-badge&logo=heart&logoColor=white" alt="Maintained">
</div>

<br>

<h1 align="center">
  🧩 OpenClaw 技能集
</h1>

<p align="center">
  <b>为你的 OpenClaw Agent 注入超能力</b><br>
  记忆增强 · 安全防护 · 运维诊断 · 智能通知 · 一键部署
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="800">
</p>

<br>

## ✨ 特性一览

<table>
<tr>
  <td align="center" width="200">
    <b>🧠 记忆增强</b><br>
    <sub>永不遗忘</sub>
  </td>
  <td align="center" width="200">
    <b>🛡️ 安全防护</b><br>
    <sub>防误操作</sub>
  </td>
  <td align="center" width="200">
    <b>🔧 运维诊断</b><br>
    <sub>一键排查</sub>
  </td>
  <td align="center" width="200">
    <b>📊 智能分析</b><br>
    <sub>数据驱动</sub>
  </td>
</tr>
</table>

<br>

## 🚀 快速开始

### 一键安装全部技能

```bash
bash <(curl -sL https://raw.githubusercontent.com/7452323/Nexus/main/openclaw/install.sh)
```

### 按需安装

```bash
# 只安装你需要的技能
bash install.sh --only=memory-enhancer,preflight-checker,server-doctor

# 或安装全部但跳过某些技能
bash install.sh --skip=daily-digest,usage-analytics

# 查看帮助和可用技能列表
bash install.sh --help
```

> 💡 **提示：** 安装完成后，执行 `openclaw gateway restart` 使技能生效。

<br>

---

<br>

## 📦 全部技能

<details open>
<summary><b>🧠 记忆 & 知识（3项）</b></summary>
<br>

| 技能 | 说明 | 安装 |
|:---:|:---|:---:|
| `memory-enhancer` | 🔋 **记忆增强** — 会话启动时扫描记忆、提问时扩展搜索、回复前召回相关记忆 | `--only=memory-enhancer` |
| `memory-backup-auto` | 💾 **自动备份** — 记忆文件定时打包，保留 7 天快照，支持一键回滚 | `--only=memory-backup-auto` |
| `knowledge-archiver` | 📚 **知识归档** — 自动将关键信息写入 MEMORY.md，重要内容永不遗落 | `--only=knowledge-archiver` |

</details>

<details>
<summary><b>🛡️ 安全 & 稳定性（5项）</b></summary>
<br>

| 技能 | 说明 | 安装 |
|:---:|:---|:---:|
| `preflight-checker` | 🚧 **工具预检** — 拦截 `rm -rf /`、`git push --force` 等危险操作 | `--only=preflight-checker` |
| `session-isolator` | 🔒 **会话隔离** — 微信私聊内容严格隔离，绝不泄露到群聊或其他平台 | `--only=session-isolator` |
| `provider-failover` | 🔁 **故障切换** — API 挂了自动切备用 Key，恢复后无缝切回 | `--only=provider-failover` |
| `context-optimizer` | 📐 **上下文优化** — 长会话自动精简，保留关键信息，节省 Token | `--only=context-optimizer` |
| `rate-limiter` | ⏱️ **频率控制** — 防止 API 限流封号，指数退避智能重试 | `--only=rate-limiter` |

</details>

<details>
<summary><b>🔧 运维 & 工具（3项）</b></summary>
<br>

| 技能 | 说明 | 安装 |
|:---:|:---|:---:|
| `server-doctor` | 🏥 **服务器诊断** — 一键排查 CPU / 内存 / 磁盘 / 网络，自动修复常见问题 | `--only=server-doctor` |
| `skill-scaffold` | 🏗️ **技能脚手架** — 说一句"帮我写个技能"，自动生成 SKILL.md 完整模板 | `--only=skill-scaffold` |
| `config-presets` | ⚙️ **配置预设** — 高性能 / 均衡 / 省电 / 开发模式，一键切换 | `--only=config-presets` |

</details>

<details>
<summary><b>🔔 通知 & 管理（2项）</b></summary>
<br>

| 技能 | 说明 | 安装 |
|:---:|:---|:---:|
| `notification-bridge` | 📡 **通知桥梁** — OpenClaw 结果自动推送到微信 / Telegram / Bark | `--only=notification-bridge` |
| `multi-instance` | 🧬 **多实例管理** — 同一机器跑多个 OpenClaw 配置，端口完全隔离 | `--only=multi-instance` |

</details>

<details>
<summary><b>📈 报告 & 分析（2项）</b></summary>
<br>

| 技能 | 说明 | 安装 |
|:---:|:---|:---:|
| `daily-digest` | 🌅 **每日报告** — 每天 07:30 推送费用 / 健康 / 活动统计到微信 | `--only=daily-digest` |
| `usage-analytics` | 📊 **使用分析** — 查询会话数、工具调用量、费用趋势一览 | `--only=usage-analytics` |

</details>

<details>
<summary><b>📖 书源 & 脚本（2项）</b></summary>
<br>

| 技能 | 说明 | 安装 |
|:---:|:---|:---:|
| `book-source-master` | 📕 **书源大湿** — Legado 阅读3.0 书源编写全指南，CSS/XPath/正则通吃 | `--only=book-source-master` |
| `qx-script-master` | 🦊 **QX 全能脚本** — 解锁·签到·去广告·Cookie·面板，一站式脚本编写技能 | `--only=qx-script-master` |

</details>

<br>

---

<br>

## 🎯 场景推荐

| 使用场景 | 推荐安装组合 |
|:---|:---|
| 🆕 **刚搭好 OpenClaw** | 全部安装 — 每个技能仅一个 Markdown 文件，零负担 |
| 🔐 **注重安全** | `preflight-checker` + `session-isolator` + `rate-limiter` |
| 🛠️ **日常运维** | `server-doctor` + `memory-backup-auto` + `daily-digest` |
| 🔑 **Key 管理** | `provider-failover` + `memory-enhancer` |
| 💡 **开发新技能** | `skill-scaffold` + `book-source-master` |
| 📱 **多端通知** | `notification-bridge` + `multi-instance` |

<br>

---

<br>

## 🗂️ 项目结构

```
openclaw/
├── 📄 README.md          # 本文件
├── 📜 install.sh         # 一键安装脚本
├── 📁 scripts/           # 工具脚本
│   ├── deobfuscate.js    # JS 反混淆工具
│   └── har_parser.py     # HAR 日志解析器
└── 📁 skills/            # 技能文件（19项）
    ├── memory-enhancer.skill.md
    ├── preflight-checker.skill.md
    ├── server-doctor.skill.md
    └── ...
```

<br>

---

<br>

## 📄 许可

<div align="center">
  <strong>MIT License</strong>
  <br><br>
  <sub>
    ✨ 为 <a href="https://github.com/openclaw/openclaw">OpenClaw</a> 社区贡献<br>
    Inspired by <a href="https://github.com/Cyrene963/hermes-patches">hermes-patches</a>
  </sub>
</div>

<br>

<div align="center">
  <img src="https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F%20by-FF69B4?style=for-the-badge" alt="Made with love">
</div>
