# TG 大文件收发工具

突破 Telegram Bot API 20MB 限制，基于 Pyrogram MTProto 收发大文件，上限 2GB。
**v2 增加断点续传**：中断（含误 kill）后不必让用户重发，`resume` / `fetch` 接着下。

## 依赖

```bash
python3 -m venv venv && source venv/bin/activate
pip install pyrogram tgcrypto
```

## 配置

```bash
export TG_API_ID="your_api_id"
export TG_API_HASH="your_api_hash"
export TG_BOT_TOKEN="your_bot_token"
export TG_HOME_CHAT="your_chat_id"          # 可选，上传默认目标
export TG_DOWNLOAD_DIR="/tmp/tg_downloads"  # 可选
export TG_SESSION=""                        # 可选，用户号 session 名
```

## 用法

```bash
python3 tg_file.py listen                     # 监听并下载，可随时中断
python3 tg_file.py fetch <chat_id> <msg_id>   # 按消息补下/续传
python3 tg_file.py resume                     # 续传所有未完成
python3 tg_file.py upload <file> [chat_id] [caption]
```

## 续传设计

- 下载分块写 `name.part`，进度存 `$TG_DOWNLOAD_DIR/.tgresume.json`
  （`chat_id / msg_id / file_id / file_size / offset / done`）。
- 每次 `listen` 收到同一个 `msg_id` 自动从 `.part` 大小续传；`SIGINT/SIGTERM`
  只置标志位，写完当前块再退，进度不丢。
- 完成后 `os.replace` 改名并标记 `done=True`，`.part` 不残留。
- `iter_download(offset=...)` 的 offset 必须是块大小整数倍，代码已按 `CHUNK`
  向下取整，避免 Telegram 返回 400 `OFFSET_INVALID`。

## 踩过的坑

1. **别在下载中 kill 监听器**。旧脚本直接 `download_media()`，kill 即截断；
   现在有 SIGTERM 处理 + 续传，但仍建议等 `✅` 后再停。
2. **客户端弹 `The document is too large... Maximum: 20 MB`** 是发送侧限制。
   Bot 通过 MTProto 实际能收 2GB，同一个包多试几次/换个网络偶尔就过；
   稳定方案是拉进群发、或走网盘直链。
3. **`getUpdates` 冲突**：同一 Bot Token 只能一个进程 poll。监听期间宿主框架
   收不到消息，下载完立即关监听。
4. **bot 账号不能 `getMessages`**：`fetch` / `resume` 依赖读历史，Bot 会
   `BOT_METHOD_INVALID`。要补下旧消息必须设 `TG_SESSION` 用用户号 session
   （API_ID/API_HASH 须与创建 session 时相同，否则会索要手机号）。
5. 文件名用 `os.path.basename` 清洗，`msg_id` 记录在状态里，避免同名覆盖。

## 参考

已用 3.5MB 模拟载荷验证：中断于 2MB → 续传 → 输出与原文件逐字节一致。
