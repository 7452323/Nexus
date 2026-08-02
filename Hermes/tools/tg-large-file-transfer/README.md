# TG 大文件收发工具

突破 Telegram Bot API 20MB 限制，基于 Pyrogram MTProto 收发大文件，上限 2GB。

## 依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install pyrogram tgcrypto
```

## 配置

通过环境变量传入凭据，不硬编码：

```bash
export TG_API_ID="your_api_id"
export TG_API_HASH="your_api_hash"
export TG_BOT_TOKEN="your_bot_token"
export TG_HOME_CHAT="your_chat_id"        # 可选，上传默认目标
export TG_DOWNLOAD_DIR="/tmp/tg_downloads" # 可选，下载目录
```

## 用法

### 收文件（用户 → Bot）

```bash
# 启动监听器（前台）
python3 tg_file.py listen

# Bot会自动下载所有收到的文件到 TG_DOWNLOAD_DIR
# 在另一个终端或后台运行，用户发文件后自动下载
```

### 发文件（Bot → 用户）

```bash
# 上传到默认 Home chat
python3 tg_file.py upload /path/to/file "文件说明"

# 上传到指定 chat
python3 tg_file.py upload /path/to/file 123456789 "文件说明"
```

## 注意事项

1. **getUpdates 冲突**：Bot 同一时刻只能有一个进程 poll getUpdates。如果 Hermes（或其他框架）也在用同一个 Bot Token 收消息，监听器会抢走 updates。处理完大文件后应尽快关闭监听器。
2. **Session 文件**：首次运行会生成 `tg_file_bot.session` / `tg_file_listener.session`，之后复用。
3. **2GB 上限**：Bot 通过 MTProto 上传单文件上限 2GB。
4. **进度条**：上传/下载均显示进度条。
