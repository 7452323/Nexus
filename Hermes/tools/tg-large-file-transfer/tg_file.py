#!/usr/bin/env python3
"""
TG MTProto 大文件收发工具 — 突破Bot API 20MB限制，上限2GB

用法:
  python3 tg_file.py listen                                    # 监听模式：自动下载发给Bot的大文件
  python3 tg_file.py upload <file> [caption]                   # 上传文件到Home chat
  python3 tg_file.py upload <file> <chat_id> [caption]         # 上传到指定chat

环境变量:
  TG_API_ID        — Telegram API ID
  TG_API_HASH      — Telegram API Hash
  TG_BOT_TOKEN     — Bot Token
  TG_HOME_CHAT     — 默认上传目标 chat_id (可选)
  TG_DOWNLOAD_DIR  — 下载目录 (默认 /tmp/tg_downloads)

依赖:
  pip install pyrogram tgcrypto
"""
import sys, os
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ.get("TG_API_ID", "0"))
API_HASH = os.environ.get("TG_API_HASH", "")
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
HOME_CHAT = int(os.environ.get("TG_HOME_CHAT", "0"))
DOWNLOAD_DIR = os.environ.get("TG_DOWNLOAD_DIR", "/tmp/tg_downloads")

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("❌ 请设置环境变量 TG_API_ID, TG_API_HASH, TG_BOT_TOKEN")
    sys.exit(1)

def get_client(session_name="tg_file_bot"):
    return Client(session_name, api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def progress_cb(current, total):
    pct = current * 100 / total
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    sys.stdout.write(f"\r{bar} {pct:.1f}% ({current/1024/1024:.1f}/{total/1024/1024:.1f}MB)")
    sys.stdout.flush()

# ─── 监听模式 ───
def listen():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    app = get_client("tg_file_listener")
    
    @app.on_message(filters.document | filters.video | filters.audio | filters.photo)
    async def on_file(client: Client, message: Message):
        fname, size = "?", 0
        if message.document:
            fname = message.document.file_name or "unnamed"
            size = message.document.file_size or 0
        elif message.video:
            fname = message.video.file_name or "video.mp4"
            size = message.video.file_size or 0
        elif message.audio:
            fname = message.audio.file_name or "audio.mp3"
            size = message.audio.file_size or 0
        elif message.photo:
            fname = "photo.jpg"
        
        size_str = f"{size/1024/1024:.1f}MB" if size else "?"
        print(f"\n📨 收到: {fname} ({size_str})")
        path = await client.download_media(message, file_name=DOWNLOAD_DIR + "/", progress=progress_cb)
        print(f"\n✅ 保存到: {path}")
        print(f"🎧 继续监听... (Ctrl+C退出)")
    
    print(f"🎧 监听中... 文件保存到 {DOWNLOAD_DIR}")
    app.run()

# ─── 上传模式 ───
def upload(file_path, chat_id=None, caption=""):
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    chat_id = chat_id or HOME_CHAT
    if not chat_id:
        print("❌ 请指定 chat_id 或设置 TG_HOME_CHAT 环境变量")
        sys.exit(1)
    size_mb = os.path.getsize(file_path) / 1024 / 1024
    print(f"📤 上传: {file_path} ({size_mb:.1f}MB) → chat {chat_id}")
    
    app = get_client()
    with app:
        msg = app.send_document(
            chat_id=chat_id,
            document=file_path,
            caption=caption[:1024] if caption else None,
            progress=progress_cb
        )
    print(f"\n✅ 上传成功! Message ID: {msg.id}")

# ─── main ───
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "listen":
        listen()
    elif cmd == "upload":
        if len(sys.argv) < 3:
            print("用法: tg_file.py upload <file> [chat_id] [caption]")
            sys.exit(1)
        file_path = sys.argv[2]
        chat_id = None
        caption = ""
        if len(sys.argv) > 3:
            try:
                chat_id = int(sys.argv[3])
                if len(sys.argv) > 4:
                    caption = sys.argv[4]
            except ValueError:
                caption = sys.argv[3]
        upload(file_path, chat_id, caption)
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)
