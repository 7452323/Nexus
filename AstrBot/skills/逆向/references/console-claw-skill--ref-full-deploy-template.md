# 一次性完整部署提示词模板（codex-console 版）

```text
第一步：
拉取这两个仓库并完成基础部署：
- https://github.com/dou-jiang/codex-console
- https://github.com/router-for-me/CLIProxyAPI

第二步：
请你分析这两个项目的联动方式，并直接完成联动，不要只给方案。

联动目标：
- 单机部署，两服务本地直连。
- CLIProxyAPI 作为 CPA 管理端与 API 供给端。
- codex-console 负责账号导入、可用性维护、库存联动与持续供给。
- 管理口令与 API Key 使用强随机值。

关键要求：
1. CLIProxyAPI：
   - 正确生成 config.yaml。
   - 监听本机地址。
   - 启用 management API。
   - 启动后验证：
     - 无 token 访问管理接口返回 401
     - 带 token 访问 `/v0/management/auth-files` 返回 200

2. codex-console：
   - 正常启动其管理界面或服务进程。
   - 完成与本机 CLIProxyAPI 的对接配置。
   - 开启自动维护可用账号与库存供给能力。

3. 联动链路：
   - codex-console 新增或维护的可用账号要能同步进入 CLIProxyAPI。
   - 失效账号要能自动清理或替换。
   - 库存低于阈值时要能自动补充。

第三步：
在与上面两个项目平级的位置新建 `openClaw` 文件夹，并安装官方 openClaw。

第四步：
把 openClaw 接到 CLIProxyAPI：
- openClaw 的模型上游走 CLIProxyAPI 的 `/v1`
- 认证使用 CLIProxyAPI 的业务 API Key
- 要保证 openClaw 消耗的是 codex-console 持续维护并供给到 CLIProxyAPI 的库存

第五步：
把 openClaw 接到 Telegram Bot。

我的 Telegram Bot Token 是：
`<替换为你的 Telegram Bot Token>`

要求：
- 完成 Telegram 对接
- 确认 bot 已成功启动
- 给出 bot 用户名

第六步：
请直接完成部署、配置、必要的代码修复和服务启动，不要停留在分析。

验收要求：
1. openClaw 网关可运行，RPC probe 正常。
2. Telegram Bot 已连接成功。
3. CLIProxyAPI 业务口 `/v1/models` 可用。
4. codex-console 至少成功提供并同步 1 个有效账号到 CLIProxyAPI。
5. 明确列出：
   - codex-console 地址
   - CLIProxyAPI 地址
   - openClaw 配置文件路径
   - 关键 token / password / API Key 存放位置
   - 当前库存数量
6. 如果联动里存在代码缺陷，请直接修复并重启相关服务。
7. 最后给我一份简洁的运行结果总结，以及后续维护建议。
```
