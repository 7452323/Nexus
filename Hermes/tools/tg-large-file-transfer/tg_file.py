#!/usr/bin/env python3
"""TG MTProto 大文件收发 — 断点续传版

用法:
  python3 tg_file.py listen                     监听并下载（自动续传）
  python3 tg_file.py fetch <chat_id> <msg_id>   按消息补下（中断后不用重发）
  python3 tg_file.py resume                     续传上次未完成的下载
  python3 tg_file.py upload <file> [chat_id] [caption]

环境变量:
  TG_API_ID TG_API_HASH TG_BOT_TOKEN TG_HOME_CHAT TG_DOWNLOAD_DIR
  TG_SESSION  可选，用户号 session 名（bot 无法 getMessages 时用于 fetch）
"""
import sys, os, json, time, signal, asyncio
from pyrogram import Client, filters

API_ID = int(os.environ.get("TG_API_ID", "0"))
API_HASH = os.environ.get("TG_API_HASH", "")
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
HOME_CHAT = int(os.environ.get("TG_HOME_CHAT", "0"))
DL = os.environ.get("TG_DOWNLOAD_DIR", "/tmp/tg_downloads")
SESSION = os.environ.get("TG_SESSION", "")
STATE = ".tgresume.json"
CHUNK = 1024 * 1024

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("❌ 需要 TG_API_ID / TG_API_HASH / TG_BOT_TOKEN")
    sys.exit(1)

_active = set()
_stop = False


def get_client(name="tg_file_bot"):
    return Client(name, api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def state_path(d=DL):
    return os.path.join(d, STATE)


def load_state(d=DL):
    try:
        with open(state_path(d)) as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(s, d=DL):
    os.makedirs(d, exist_ok=True)
    tmp = state_path(d) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(s, f)
    os.replace(tmp, state_path(d))


class Progress:
    """节流进度：1% 或 2s 才刷一次，避免日志刷屏"""

    def __init__(self, total):
        self.total = max(total or 1, 1)
        self.last_t, self.last_p = 0.0, -1.0

    def __call__(self, cur):
        p = cur * 100 / self.total
        now = time.time()
        if p - self.last_p < 1 and now - self.last_t < 2 and cur < self.total:
            return
        self.last_t, self.last_p = now, p
        sys.stdout.write(f"\r{p:5.1f}% {cur/1048576:.1f}/{self.total/1048576:.1f}MB")
        sys.stdout.flush()


def record(chat_id, msg_id, doc, path):
    s = load_state()
    s[str(msg_id)] = {
        "chat_id": chat_id,
        "msg_id": msg_id,
        "file_id": doc.file_id if doc else None,
        "file_size": (doc.file_size if doc else 0) or 0,
        "name": path,
        "offset": 0,
        "done": False,
    }
    save_state(s)
    return str(msg_id)


def _mark(key, offset, done):
    s = load_state()
    if key in s:
        s[key]["offset"] = offset
        s[key]["done"] = done
        save_state(s)


async def download_media(client, message, key=None, resume=False):
    """分块写盘 + 进度持久化，SIGINT/SIGTERM 安全"""
    doc = message.document or message.video or message.audio
    size = (doc.file_size if doc else 0) or 0
    name = (getattr(doc, "file_name", None) or f"{message.id}.bin") if doc else "photo.jpg"
    name = os.path.basename(name).replace("\x00", "_")
    path = os.path.join(DL, name)
    part = path + ".part"

    offset = 0
    if resume and os.path.exists(part):
        offset = os.path.getsize(part) // CHUNK * CHUNK
        if offset >= size:
            os.replace(part, path)
            return path
        print(f"↩️ 续传 {os.path.basename(part)} @ {offset/1048576:.1f}MB")

    prog = Progress(size)
    mode = "ab" if offset else "wb"
    with open(part, mode) as f:
        async for chunk in client.iter_download(message, offset=offset, chunk_size=CHUNK):
            if _stop:
                raise KeyboardInterrupt
            f.write(chunk)
            offset += len(chunk)
            prog(offset)
            if key:
                _mark(key, offset, False)
        f.flush()
        os.fsync(f.fileno())

    os.replace(part, path)
    if key:
        _mark(key, offset, True)
    print(f"\n✅ {path} ({os.path.getsize(path)/1048576:.1f}MB)")
    return path


# ─── listen ───
def listen():
    os.makedirs(DL, exist_ok=True)
    if SESSION:
        app = Client(SESSION, api_id=API_ID, api_hash=API_HASH)
    else:
        app = get_client("tg_file_listener")

    @app.on_message(filters.document | filters.video | filters.audio | filters.photo)
    async def on_file(c, m):
        ident = f"{m.chat.id}:{m.id}"
        if ident in _active:
            print(f"⏭ 跳过重复: {ident}")
            return
        _active.add(ident)
        doc = m.document or m.video or m.audio
        print(f"\n📨 {getattr(doc, 'file_name', 'photo')} "
              f"({(getattr(doc, 'file_size', 0) or 0)/1048576:.1f}MB) chat={m.chat.id} msg={m.id}")
        key = record(m.chat.id, m.id, doc, getattr(doc, "file_name", "photo"))
        try:
            await download_media(c, m, key, resume=True)
        except KeyboardInterrupt:
            print("\n⏸ 中断，进度已存；跑 resume 继续")
        except Exception as e:
            print(f"\n❌ {type(e).__name__}: {e}")
        finally:
            _active.discard(ident)

    print(f"🎧 监听 {DL}")
    app.run()


# ─── fetch ───
def fetch(chat_id, msg_id):
    os.makedirs(DL, exist_ok=True)
    app = Client(SESSION, api_id=API_ID, api_hash=API_HASH) if SESSION else get_client()
    with app:
        m = app.get_messages(int(chat_id), int(msg_id))
        if not m or not (m.document or m.video or m.audio or m.photo):
            print("❌ 该消息没有文件（bot 账号可能无权 getMessages，设 TG_SESSION 用用户号）")
            sys.exit(1)
        key = record(m.chat.id, m.id, m.document, getattr(m.document, "file_name", "f"))
        asyncio.get_event_loop().run_until_complete(download_media(app, m, key, resume=True))


# ─── resume ───
def resume():
    os.makedirs(DL, exist_ok=True)
    s = {k: v for k, v in load_state().items() if not v.get("done")}
    if not s:
        print("✅ 没有未完成的下载")
        return
    app = Client(SESSION, api_id=API_ID, api_hash=API_HASH) if SESSION else get_client()
    with app:
        for k, v in s.items():
            print(f"↩️ {v['name']} chat={v['chat_id']} msg={v['msg_id']}")
            try:
                m = app.get_messages(v["chat_id"], v["msg_id"])
                if not m or not (m.document or m.video or m.audio):
                    print("  跳过（消息取不到，需 TG_SESSION）")
                    continue
                asyncio.get_event_loop().run_until_complete(download_media(app, m, k, resume=True))
            except Exception as e:
                print(f"  ❌ {type(e).__name__}: {e}")


# ─── upload ───
def progress_cb(current, total):
    pct = current * 100 / max(total, 1)
    sys.stdout.write(f"\r{pct:5.1f}% {current/1048576:.1f}/{total/1048576:.1f}MB")
    sys.stdout.flush()


def upload(file_path, chat_id=None, caption=""):
    if not os.path.exists(file_path):
        print(f"❌ 不存在: {file_path}")
        sys.exit(1)
    chat_id = chat_id or HOME_CHAT
    if not chat_id:
        print("❌ 需要 chat_id 或 TG_HOME_CHAT")
        sys.exit(1)
    print(f"📤 {file_path} ({os.path.getsize(file_path)/1048576:.1f}MB) → {chat_id}")
    with get_client() as app:
        msg = app.send_document(chat_id=chat_id, document=file_path,
                                caption=caption[:1024] or None, progress=progress_cb)
    print(f"\n✅ 上传成功 Message ID: {msg.id}")


def _sig(*_):
    global _stop
    _stop = True


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _sig)
    signal.signal(signal.SIGINT, _sig)
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    cmd = args[0]
    if cmd == "listen":
        listen()
    elif cmd == "fetch":
        fetch(args[1], args[2])
    elif cmd == "resume":
        resume()
    elif cmd == "upload":
        cid = None
        cap = ""
        if len(args) > 2:
            try:
                cid = int(args[2])
                cap = args[3] if len(args) > 3 else ""
            except ValueError:
                cap = args[2]
        upload(args[1], cid, cap)
    else:
        print(__doc__)
        sys.exit(1)
