<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-v2026.5.12%2B-blue?style=flat-square" alt="OpenClaw">
  <img src="https://img.shields.io/badge/skills-19-green?style=flat-square" alt="16 skills">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="MIT">
</p>

<h1 align="center">🧩 OpenClaw Patches</h1>
<p align="center"><b>OpenClaw Agent 社区增强补丁合集</b><br>
一键安装，为你的 OpenClaw 增加记忆增强、工具预检、会话隔离等 19 项实用技能。</p>

---

## 🚀 快速安装

```bash
bash <(curl -sL https://raw.githubusercontent.com/7452323/Nexus/main/openclaw/install.sh)
```

### 选择性安装

```bash
# 只装你需要的
bash install.sh --only=memory-enhancer,preflight-checker,server-doctor

# 或跳过不需要的
bash install.sh --skip=daily-digest,usage-analytics

# 查看帮助
bash install.sh --help
```

---

## 🧠 全部技能

### 记忆 & 知识
|技能|说明|安装命令|
|---|---|---|
|`memory-enhancer`|记忆增强 — 会话启动时扫描记忆、提问时扩展搜索、回复前召回相关记忆|`--only=memory-enhancer`|
|`memory-backup-auto`|自动备份 — 记忆文件定时打包，保留 7 天快照，支持回滚|`--only=memory-backup-auto`|
|`knowledge-archiver`|知识归档 — 自动将关键信息写入 MEMORY.md，不遗漏|`--only=knowledge-archiver`|

### 安全 & 稳定性
|技能|说明|安装命令|
|---|---|---|
|`preflight-checker`|工具预检 — 拦截 rm -rf /、git push --force 等危险操作|`--only=preflight-checker`|
|`session-isolator`|会话隔离 — 微信私聊内容不泄露到群聊或其他平台|`--only=session-isolator`|
|`provider-failover`|故障切换 — API 挂了自动切备用 Key，恢复后自动切回|`--only=provider-failover`|
|`context-optimizer`|上下文优化 — 长会话自动精简，保住关键信息|`--only=context-optimizer`|
|`rate-limiter`|频率控制 — 防止 API 限流封号，指数退避重试|`--only=rate-limiter`|

### 运维 & 工具
|技能|说明|安装命令|
|---|---|---|
|`server-doctor`|服务器诊断 — 一键排查 CPU/内存/磁盘/网络，自动修复常见问题|`--only=server-doctor`|
|`skill-scaffold`|技能脚手架 — 说"帮我写个技能"，自动生成 SKILL.md 模板|`--only=skill-scaffold`|
|`config-presets`|配置预设 — 高性能/均衡/省电/开发模式一键切换|`--only=config-presets`|

### 通知 & 管理
|技能|说明|安装命令|
|---|---|---|
|`notification-bridge`|通知桥梁 — OpenClaw 结果自动推送到微信/Telegram/Bark|`--only=notification-bridge`|
|`multi-instance`|多实例管理 — 同机器跑多个 OpenClaw 配置，端口隔离|`--only=multi-instance`|

### 报告 & 分析
|技能|说明|安装命令|
|---|---|---|
|`daily-digest`|每日报告 — 每天 07:30 推送费用/健康/活动统计到微信|`--only=daily-digest`|
|`usage-analytics`|使用分析 — 查询会话数、工具调用、费用趋势|`--only=usage-analytics`|

### 书源
|技能|说明|安装命令|
|---|---|---|
|`book-source-master`|书源大湿 — Legado 阅读3.0 书源编写全指南|
|`qx-script-master`|QX 全能脚本 — 解锁·签到·去广告·Cookie·面板一站式脚本编写技能|`--only=book-source-master`|

---

## 💡 使用建议

|使用场景|推荐安装|
|---|---|
|刚搭建 OpenClaw|全部安装（没负担，每个技能仅一个 Markdown 文件）|
|注重安全|`preflight-checker` + `session-isolator` + `rate-limiter`|
|日常运维|`server-doctor` + `memory-backup-auto` + `daily-digest`|
|Key 管理|`provider-failover` + `memory-enhancer`|
|开发新技能|`skill-scaffold` + `book-source-master`|

---

## 📄 许可

MIT License

---

<p align="center">
  <sub> inspired by <a href="https://github.com/Cyrene963/hermes-patches">hermes-patches</a></sub>
</p>
