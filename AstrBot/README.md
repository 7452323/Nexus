<div align="center">
  <img src="https://img.shields.io/badge/AstrBot-v3.0%2B-8B5CF6?style=for-the-badge&logo=robot&logoColor=white" alt="AstrBot">
  <img src="https://img.shields.io/badge/Resources-10-10B981?style=for-the-badge&logo=bookstack&logoColor=white" alt="Resources">
  <img src="https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge&logo=bookstack&logoColor=white" alt="MIT">
  <img src="https://img.shields.io/badge/Maintained-Yes-EF4444?style=for-the-badge&logo=heart&logoColor=white" alt="Maintained">
</div>

<br>

<h1 align="center">
  🤖 AstrBot 资源集
</h1>

<p align="center">
  <b>Agentic AI 助手 · 全能接入 · 智能体平台</b><br>
  多IM接入 · LLM对话 · 知识库 · 插件生态 · 一键部署
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="800">
</p>

<br>

## ✨ 关于 AstrBot

<table>
<tr>
  <td align="center" width="250">
    <b>💬 多平台接入</b><br>
    <sub>QQ / 企业微信 / 飞书 / 钉钉 / Telegram / Slack</sub>
  </td>
  <td align="center" width="250">
    <b>🧠 智能对话</b><br>
    <sub>LLM / 多模态 / Agent / MCP / 知识库</sub>
  </td>
  <td align="center" width="250">
    <b>🧩 插件生态</b><br>
    <sub>1000+ 社区插件，一键安装</sub>
  </td>
  <td align="center" width="250">
    <b>🛡️ Agent 沙箱</b><br>
    <sub>隔离执行代码/Shell，安全可控</sub>
  </td>
</tr>
</table>

<br>

> AstrBot 是一个开源的全能 Agent 聊天机器人平台，集成主流即时通讯应用。
> 无论是个人 AI 伴侣、智能客服、自动化助手还是企业知识库，AstrBot 都能帮你快速构建生产级 AI 应用。
>
> 🔗 **GitHub**: [github.com/AstrBotDevs/AstrBot](https://github.com/AstrBotDevs/AstrBot)
>
> 🔗 **文档**: [docs.astrbot.app](https://docs.astrbot.app)

<br>

---

<br>

## 🚀 快速开始

### 一键部署

```bash
# Docker 部署（推荐）
docker run -d --name astrbot -p 6185:6185 \
  -v ./data:/app/data \
  ghcr.io/astrbotdevs/astrbot:latest
```

### 手动部署

```bash
# 克隆仓库
git clone https://github.com/AstrBotDevs/AstrBot.git
cd AstrBot

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

> 💡 **提示：** 首次运行会自动生成配置文件 `data/config.json`，按提示填写 LLM API Key 和 IM 平台配置即可。

<br>

---

<br>

## 📦 本站资源

<details open>
<summary><b>📖 文档 & 指南（3项）</b></summary>
<br>

| 资源 | 说明 | 链接 |
|:---:|:---|:---:|
| 📘 **快速开始** | 从零搭建 AstrBot，5 分钟上手 | [查看 →](https://docs.astrbot.app/guide/quickstart) |
| 📗 **配置详解** | 完整配置项说明，LLM/IM/插件全指南 | [查看 →](https://docs.astrbot.app/guide/config) |
| 📙 **API 参考** | AstrBot API 文档，二次开发必备 | [查看 →](https://docs.astrbot.app/api) |

</details>

<details>
<summary><b>🔌 插件开发（2项）</b></summary>
<br>

| 资源 | 说明 | 链接 |
|:---:|:---|:---:|
| 🧩 **插件开发指南** | 从 Hello World 到发布，一步步教你写插件 | [查看 →](https://docs.astrbot.app/dev/plugin) |
| 📦 **插件市场** | 1000+ 社区插件，搜索/安装/管理 | [查看 →](https://docs.astrbot.app/market) |

</details>

<details>
<summary><b>🛠️ 运维 & 部署（3项）</b></summary>
<br>

| 资源 | 说明 | 链接 |
|:---:|:---|:---:|
| 🐳 **Docker 部署** | 使用 Docker Compose 一键部署生产环境 | [查看 →](https://docs.astrbot.app/deploy/docker) |
| ☁️ **云部署** | 部署到阿里云 / 腾讯云 / AWS 等云平台 | [查看 →](https://docs.astrbot.app/deploy/cloud) |
| 🔄 **升级与迁移** | 版本升级、数据迁移、备份恢复 | [查看 →](https://docs.astrbot.app/deploy/migrate) |

</details>

<details>
<summary><b>🎯 高级功能（2项）</b></summary>
<br>

| 资源 | 说明 | 链接 |
|:---:|:---|:---:|
| 🤖 **Agent 沙箱** | 隔离执行 Python 代码和 Shell 命令，安全可靠 | [查看 →](https://docs.astrbot.app/use/astrbot-agent-sandbox.html) |
| 🧠 **知识库** | 构建专属知识库，RAG 增强问答能力 | [查看 →](https://docs.astrbot.app/use/knowledge-base) |

</details>

<br>

---

<br>

## 🎯 场景推荐

| 使用场景 | 推荐配置 |
|:---|:---|
| 💬 **个人 AI 助手** | WeChat + GPT-4o + 基础插件包 |
| 🏢 **企业智能客服** | 钉钉/飞书 + 知识库 + RAG + Agent 沙箱 |
| 🤖 **自动化运维** | Telegram + Shell Agent + MCP 工具链 |
| 📚 **知识管理** | QQ 群 + 知识库 + 自动摘要插件 |
| 💻 **开发助手** | Slack + Code Agent + GitHub 插件 |
| 🎮 **群聊娱乐** | QQ 群 + 角色扮演 + 游戏插件 |

<br>

---

<br>

## 🗂️ 项目结构

```
AstrBot/
└── 📄 README.md          # 本文件 — AstrBot 资源导航
```

> 📌 **更多内容陆续更新中...**
> 
> 计划添加：
> - AstrBot 配置模板 / 最佳实践
> - 常用插件推荐列表
> - Docker Compose 模板
> - 常见问题排查指南

<br>

---

<br>

## 🔗 相关链接

<div align="center">

| 资源 | 链接 |
|:---|:---:|
| 🏠 **官网** | [astrbot.app](https://astrbot.app) |
| 📖 **文档** | [docs.astrbot.app](https://docs.astrbot.app) |
| 💻 **GitHub** | [github.com/AstrBotDevs/AstrBot](https://github.com/AstrBotDevs/AstrBot) |
| 🐳 **Docker** | [ghcr.io/astrbotdevs/astrbot](https://ghcr.io/astrbotdevs/astrbot) |
| 💬 **社区** | [QQ 群 / Discord / Telegram](https://docs.astrbot.app/community) |

</div>

<br>

---

<br>

## 📄 许可

<div align="center">
  <strong>MIT License</strong>
  <br><br>
  <sub>
    ✨ 由 <a href="https://github.com/AstrBotDevs">AstrBotDevs</a> 社区驱动<br>
    汇集于 <a href="https://github.com/7452323/Nexus">7452323/Nexus</a>
  </sub>
</div>

<br>

<div align="center">
  <img src="https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F%20by-FF69B4?style=for-the-badge" alt="Made with love">
</div>
