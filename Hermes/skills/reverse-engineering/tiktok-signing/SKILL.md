---
name: tiktok-signing
category: reverse-engineering
description: >-
  Merged skill combining: tiktok-mobile-signing.
version: "1.0"
sources:
  - tiktok-mobile-signing
tags: [reverse-engineering, merged]
---

# tiktok-signing

> **Merged from**: tiktok-mobile-signing
> **Source count**: 1

---

## Table of Contents

1. [tiktok-mobile-signing](#tiktok-mobile-signing)

---

## tiktok-mobile-signing

# TikTok/Douyin Mobile Signing Algorithms

## Overview

TikTok/Douyin mobile app uses **five** signature headers for API requests:

| Header | Function | Algorithm |
|--------|----------|-----------|
| **X-Khronos** | Unix timestamp | 8 hex chars (`hex(time.time())[2:]`) |
| **X-SS-STUB** | Body integrity | `md5(body).hexdigest()` (空body则md5空字符串) |
| **X-Gorgon** | Request integrity | XOR with GORGON_TABLE → nibble swap → reverse_bits ^ 0xeb |
| **X-Ladon** | Lightweight token | Custom Feistel-like encode → base64 |
| **X-Argus** | Main mobile signature | Protobuf → SM3 → SIMON-128 → mix → enc_pb → AES-CBC → base64 |

## Key Resources

### Primary reference repo (actively maintained)
- **armxe/tiktok-api** — https://github.com/armxe/tiktok-api
  - Last major update: 2026-03-28
  - Pure Python, no external file dependencies
  - Contains Mobile/ (Metasec), Web/ (X-Bogus), TTEncrypt/

### Alternative implementations
- **ssovit/x-gorogn-khronos-argus-ladon** — Go implementation, older (9 months stale)
- **huaerxiela/douyin-algorithm** — C++ native, TikTok v23.2.0 era, unmaintained
- **AlexYanger/douyin_gorgon** — Python, older reference

## Algorithm Pipeline

### X-Argus (最复杂)
```
protobuf → pad(16) → SIMON-128/128 → mix(2-byte xor) → enc_pb(xor+rev) 
  → add_headers → AES-CBC → base64
```

Key derivation: `SM3(sign_key + random(4) + sign_key)[:32]` → split into two 16-byte halves for SIMON key.

AES-CBC key: `md5(sign_key[:16])`, iv: `md5(sign_key[16:])`.

### X-Gorgon (预览版)
```
buffer = params[:4] + payload[:4] + cookies[:4] + fixed_4bytes + ts[:4]  (20 bytes)
  → XOR GORGON_TABLE (20 bytes: ce7c47e421ff095cc9da81690147cba1ed6cc4b1)
  → nibble swap each byte
  → XOR cascade (byte[i] ^= byte[i+1])
  → reverse_bits(byte) ^ 0xEB
  → last byte: nibble swap → XOR byte[0] → reverse_bits ^ 0xEB
  → prefix = 8404a0ae1000 (arm64) or 0404a0ae1000
  → hex
```

### X-Ladon
```
payload = f"{ts}-{license_id}-{app_id}".encode()
pad to 32 bytes with padding value
derive 34 key rounds from md5(app_id bytes)
apply custom Feistel-like encode in 2 blocks of 4 int32
base64(random_bytes(4) + encoded)
```

## Key Extraction from APK

SIGN_KEY is hardcoded in **libmetasec.so** inside the TikTok APK. Changes per app version.

Extraction method:
1. Download latest TikTok APK (apkmirror)
2. `unzip` → extract `lib/arm64-v8a/libmetasec.so`
3. Search for base64 pattern (44 chars ending with `=`)
4. The default key as of 2026-03: `wC8lD4bMTxmNVwY5jSkqi3QWmrphr/58ugLko7UZgWM=`

GORGON_TABLE (20 bytes): Search SO for hex `ce7c47e421ff095cc9da81690147cba1ed6cc4b1`.

## Dyn Version Support

dyn_encode versions **1–8** are implemented, each using different hash/MD5/XOR combos:
- **v1–v4**: Various MD5 + XOR patterns
- **v5**: SM3 (instead of MD5)
- **v6**: AES-OFB from MD5-derived key
- **v7**: RC4 + SHA256
- **v8**: SHA256 + CRC32 + SHA1

Add new versions as they appear — structure stays constant, only the hash/encode chain changes.

## Pre-built Standalone Implementation

File: `douyin_sign.py` in working directory — single-file, `pip install pycryptodome gmssl`.

Usage:
```python
from douyin_sign import sign_all
headers = sign_all(
    url="https://api16-normal.../?aid=1233&...",
    app_id=1233,
    body="",
    cookies="sessionid=xxx",   # optional
    device_id="7123456789..."
)
# Returns: {x-khronos, x-ss-stub, x-gorgon, x-ladon, x-argus}
```

## Auto-Update Strategy

Algorithm structure rarely changes (SIMON-128/AES/SM3 are fixed standards).
What changes per version: **SIGN_KEY**, **GORGON_TABLE**, **dyn_version logic**.

Best approach: periodic APK → SO → constant extraction CI.
Full Unicorn emulation of libmetasec.so is technically possible but not worth it —
Python rewrite is faster and more maintainable.

## Web Signatures (X-Bogus & A-Bogus)

| Header | Function | Algorithm | Status |
|--------|----------|-----------|--------|
| **X-Bogus** | Web request integrity | 20-char `[0-9A-Za-z]` — MD5×2 + RC4 + shifted base64 |  Deprecated but still works |
| **A-Bogus** | Web request integrity (current) | ~164-char — SM3×2 + RC4 + shifted base64 variant |  **Active** |
| **X-Gnarly** | ChaCha20 PRNG seed | Deterministic RNG from navigator properties, 8 rounds |  Legacy only |

### X-Bogus Pipeline (旧版, 兼容)
```
user-agent + URL params + cookies → nav-params string
  → X-Gnarly (ChaCha20 PRNG) seed generation
  → LZW compression of nav-params (10-bit codes, dynamic dict up to 1024 entries)
  → Shifted base64 encode
  → 20-char [0-9A-Za-z]{20} result
```

### A-Bogus Pipeline (当前版本) — 详见 `references/a-bogus-algorithm.md`
```
1. SM3×2 hash of params+suffix, suffix, and RC4-encoded UA
2. Build 72+ byte structure (timestamps, hash fragments, aid/pageId, env fingerprint)
3. RC4(key=0x79=121) encrypt
4. Prepend 4-byte random noise
5. Variant base64 (no padding, s4 table) → ~164 char output
```

**⚠️ A-Bogus is the current algorithm.** Modern Douyin Web uses A-Bogus, not X-Bogus. A-Bogus uses SM3 (国密) instead of MD5, produces ~164-char output instead of 20-char, and requires an environment fingerprint ("1536|747|...|Win32").

📚 **New reference**: `references/a-bogus-algorithm.md` — 完整的 A-Bogus Python 实现、SM3 实现、shifted base64 变体编码。
📚 **New reference**: `references/2026-07-09-abogus-implementation.md` — 2026-07-09 实现会话记录，含关键常量、踩坑经验、参考仓库。

### X-Gnarly (ChaCha20 variant)
- Modified ChaCha20 with **8 rounds** instead of standard 20
- Quarter-round: a+=b; d^=a; d<<<=16; c+=d; b^=c; b<<<=12; a+=b; d^=a; d<<<=8; c+=d; b^=c; b<<<=7
- Seed from navigator.appVersion + navigator.userAgent + URL params
- Used as deterministic PRNG for X-Bogus intermediate values

## TTEncrypt

TTEncrypt is a **custom AES variant** used for encrypting request payloads (not signature headers). It's a huge (~1700 lines) pure-Python reimplementation with:

- **Decrypt**: standard AES-CBC via pycryptodome
- **Encrypt**: custom AES with 10 hardcoded S-box lookup tables (dword_0 through dword_9, each 256 × 32-bit)
- **Custom hash**: SHA-2-like `calculate()` method, 128-byte block processing, initial vector LIST_6B0 (same as SHA-256 IV)
- **SIMON-like cipher**: `hex_0A2()` — Feistel-like block cipher using key expansion from `hex_27E()` (SHA-like compression)
- **Mixing**: `hex_30A()` — SIMON-like mixing step

Algorithm flow: input bytes → pad to 128-byte blocks → `calculate()` each block (SHA-2-like) → use result as AES-like cipher key → encrypt via `hex_CF8()` (10 rounds, custom S-box)

**Relevant only for: payload encryption, not request signing.** Used by the App for certain encrypted uploads.

## douyin-sign 仓库结构 (Recommended)

The `douyin-sign` package at `/root/douyin-sign/` is the canonical implementation. Structure:

```
douyin-sign/
├── sign/                          # Core algorithms package
│   ├── __init__.py                # sign_all() entry point, sign_web_request(), sign_web_request_abogus()
│   ├── constants.py               # Load constants from constants/current/
│   ├── native.py                  # ARM bit manipulation (LSRS, LSLS, UBFX, ADDS, ADC, etc.)
│   ├── gorgon.py                  # X-Gorgon (XOR table → nibble swap → cascade → rev_bits)
│   ├── argus.py                   # X-Argus (protobuf → SM3 → SIMON → AES-CBC → b64)
│   ├── ladon.py                   # X-Ladon (Feistel-like encode → RC4 → b64)
│   ├── khronos.py                 # X-Khronos (timestamp hex)
│   ├── ssstub.py                  # X-SS-STUB (MD5 body)
│   ├── dyn_encode.py              # Dyn version 1-8 (different hash/encode chains)
│   ├── protobuf.py                # Protobuf wire serializer
│   ├── simon.py                   # SIMON-128/128 cipher
│   ├── aes.py                     # AES-CBC wrapper (pycryptodome)
│   ├── rc4.py                     # RC4 cipher
│   ├── bogus.py                   # X-Bogus (Web, deprecated)
│   ├── abogus.py                  # A-Bogus (Web, current — SM3 + RC4 + variant b64)
│   ├── gnarly.py                  # X-Gnarly (ChaCha20 PRNG)
│   ├── compress.py                # LZW (10-bit)
│   ├── base.py                    # Node.js compatible/shifted base64
│   ├── ressource.py              # Shifted base64 + RC4 web variant
│   └── ttencrypt.py              # TTEncrypt payload encryption (custom AES)
├── constants/
│   └── current/                   # Versioned constants
│       ├── sign_key.b64           # Current base64-encoded 32-byte key
│       ├── gorgon_table.hex       # Current 20-byte GORGON_TABLE
│       └── protobuf_fields.json   # Protobuf field number mapping
├── extractors/                    # (future) Frida/Ghidra/APK extraction scripts
├── .github/workflows/
│   └── sync.yml                   # Nightly CI: extract constants, run tests, PR
├── update.py                      # APK → SO → constant extraction script
├── tests/
│   └── test_sign.py
├── setup.py
├── proxy.py                       # (deployment) FastAPI HTTP proxy for douyin-sign
└── README.md
```

### Repo Creation Workflow (for future sessions)

When creating a new `douyin-sign` repo from scratch:

1. **Source materials**: clone armxe/tiktok-api for Mobile/, Web/, TTEncrypt/ reference implementations
2. **Parallel approach**: use 3 background subagents writing in parallel:
   - Subagent 1: Mobile core (native, gorgon, argus, ladon, khronos, ssstub, protobuf, simon, aes, rc4, dyn_encode, constants, __init__)
   - Subagent 2: Web + TTEncrypt (bogus, gnarly, compress, base, ressource, ttencrypt)
   - Subagent 3: Infrastructure (setup.py, README, CI, tests, update.py, constants files)
3. **Key adaptation**: armxe imports are intra-package (`from cipher import AES`, `from helpers import argus`) — flatten to `sign.aes`, `sign.argus` etc. relative imports
4. **External deps**: pycryptodome (AES-CBC), gmssl (SM3) — no other runtime deps
5. **Constants separation**: all hardcoded values (SIGN_KEY, GORGON_TABLE, protobuf fields) go in `constants/current/`, loaded via `constants.py`, not hardcoded in algorithm code

## High-Level Request Wrappers

The `douyin-sign` package provides two high-level wrappers that combine signing + actual HTTP request:

### `sign_mobile_request()` — Mobile API

```python
from sign import sign_mobile_request

result = sign_mobile_request(
    method="GET",
    path="/aweme/v1/aweme/post/",
    params={"sec_user_id": "MS4wLjAB..."},
)
# Signs with X-Gorgon/X-Khronos/X-SS-STUB/X-Argus, 
# sends to api.douyin.com, returns JSON
```

- Uses **Mobile API** base: `https://api.douyin.com`
- Full X-Gorgon family signatures (Gorgon + Khronos + SS-STUB + Argus)
- Requires `Device` object (or uses seed device as fallback)
- ⚠️ **DNS limitation**: `api.douyin.com` does NOT resolve from overseas servers — test from China/Asia region only
  - Even Chinese public DNS (114.114.114.114) returns **NXDOMAIN** — the domain is intentionally absent from global DNS
  - dnspython + socket.getaddrinfo monkey-patch **won't help** when the authoritative DNS itself returns nothing
  - Only real fix: hardcode a known-working IP from a real App's packet capture + `/etc/hosts` entry
- ⚠️ **register_device() fallback**: if server registration returns `device_id=0` (silent reject), the function now falls back to `make_seed_device()` instead of crashing. Gives a usable `Device` with seed IDs for testing the signing pipeline, but seed IDs won't pass server validation for real API calls.

### `sign_web_request()` — Web API

```python
from sign import sign_web_request

result = sign_web_request(
    path="/aweme/v1/web/hot/search/list/",
    params={"detail_list": "1"},
)
# Signs with X-Bogus, sends to www.douyin.com, returns JSON
```

- Uses **Web API** base: `https://www.douyin.com`
- X-Bogus only (browser-style signing)
- ✅ Works from overseas servers (confirmed working from non-China IP)
- Default UA: Chrome 120 Windows

### `sign_web_request_abogus()` — Web API (current algorithm)

```python
from sign import sign_web_request_abogus

result = sign_web_request_abogus(
    path="/aweme/v1/web/aweme/post/",
    params={"sec_user_id": "MS4wLjAB...", "count": "6"},
    window_env="1536|747|...|Win32",
)
# Signs with A-Bogus, sends to www.douyin.com, returns JSON
```

- Uses **Web API** base: `https://www.douyin.com`
- A-Bogus (current algorithm, SM3 + RC4 + variant base64)
- ✅ Same overseas behavior as `sign_web_request()`
- Optional parameter `window_env` — defaults to standard fingerprint if not overridden
- Default UA: Chrome 120 Windows
- ⚠️ For modern Douyin Web, `sign_web_request_abogus()` is preferred over `sign_web_request()` (X-Bogus) because Douyin has switched to A-Bogus as the current web signature.

### Endpoint Difference

| API | Base URL | Example Path | Signatures |
|-----|----------|-------------|------------|
| Web | `www.douyin.com` | `/aweme/v1/web/aweme/post/` | X-Bogus |
| Mobile | `api.douyin.com` | `/aweme/v1/aweme/post/` | X-Gorgon, X-Khronos, X-SS-STUB, X-Argus, X-Ladon |

The two APIs may return different JSON structures for the same logical endpoint. Migrating from Web to Mobile requires field-level testing.

## Device Registration

### Device Class (`sign/device.py`)

```python
from sign import Device

d = Device(
    "1234567890",           # device_id
    install_id="987654321", # install_id
    iid="",
    device_type="SM-S928B",
    os_version="34",
    app_version="38.5.0",
)

# Generate session headers
d.to_cookie()       # "install_id=...; odin_tt=...; sessionid=..."
d.user_agent        # "com.ss.android.ugc.aweme/38.5.0 (Android 34; SM-S928B)"
d.to_headers()      # dict: User-Agent + Cookie + X-Requested-With

# Persist / restore
d.to_dict()         # → dict
Device.from_dict()  # → Device
```

Every signed Mobile API request needs a `Device` with at minimum `device_id` and `install_id` for X-Argus.

### register_device() — Async Registration

```python
from sign import register_device

d = await register_device()  # Device with server-returned IDs
```

- POSTs to `https://log.snssdk.com/service/2/device_register/`
- Uses preseed parameters (random device_type, openudid, etc.)
- Signs request with X-Gorgon only (no X-Argus needed)

### ⚠️ `api.douyin.com` DNS NXDOMAIN (global)

**`api.douyin.com` does NOT resolve from any DNS server worldwide** — not even 114.114.114.114 (China Telecom). The domain is intentionally absent from global DNS. This is NOT a client-side DNS blocking issue.

- dnspython + socket.getaddrinfo monkey-patch **does NOT help** — the authoritative DNS itself returns NXDOMAIN
- Only fix: capture a real App's network traffic → extract the hardcoded IP → write to `/etc/hosts`
- Alternative: deploy the proxy on a VPS and use Web API (`www.douyin.com`) instead, which works globally

### ⚠️ Known Pitfall: Returns `device_id=0`

Tested 2026-06-30: registration returns `{"server_time":1782817561,"device_id":0,"install_id":0}`.

The server rejects the registration because:
1. **Signature not recognized** — X-Gorgon algorithm may encode params differently for registration endpoint
2. **Missing required fields** — real TikTok App sends additional device fingerprint params
3. **Rate limiting / IP blacklist** — may need device farm or proxy rotation
4. **Endpoint deprecated** — registration flow may have changed

**Fix**: capture real App's registration traffic via Frida/packet capture and compare byte-for-byte. Alternative: use a **pre-registered device_id** from a working App install.

## FastAPI Proxy Deployment

The `proxy.py` template (`templates/proxy.py`) provides a lightweight HTTP proxy that signs requests and proxies them through the VPS.

**📚 New reference**: `references/mobile-api-alternative.md` — how `aweme.snssdk.com` bypasses Janus.
**📚 New reference**: `references/video-download.md` — CDN URL parameters, watermark removal, and download flow.

### Key Design Decision: Proxy, don't return signed_url

| Approach | Issue |
|----------|-------|
| Return `signed_url` → client calls www.douyin.com directly | **HTTP 200, Content-Length: 0** — non-China IPs pass X-Bogus verification but get empty responses (server-side geo-gating) |
| Proxy the request through the VPS | **Works** — the VPS itself gets real data back from www.douyin.com and relays it to the client |

**Always proxy the request through the VPS.** Never return a `signed_url` for the client to call directly — non-China IPs get empty responses even with valid X-Bogus.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/douyin/web/{path}` | Web API — signs + proxies through www.douyin.com. ✅ Works globally |
| GET | `/api/douyin/mobile/{path}` | Mobile API — signs with full X-Gorgon family. ❌ api.douyin.com unreachable from overseas |

### Proxy Workflow

```python
# proxy.py — Deployed on VPS, uses httpx to proxy requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from sign.bogus import sign_full
import httpx

@app.get("/api/douyin/web/{path:path}")
async def web_api(path: str, request: Request):
    params = dict(request.query_params)
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"
    signed_qs = sign_full(qs, ua)
    full_url = f"https://www.douyin.com/{path}?{signed_qs}"
    resp = httpx.get(full_url, headers={
        "User-Agent": ua, "Referer": "https://www.douyin.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }, timeout=20)
    return PlainTextResponse(resp.text, status_code=resp.status_code)
```

## douyin-sign Repository

- **GitHub**: https://github.com/7452323/douyin-sign

- armxe imports are non-standard (`from cipher import AES`) — must be adapted to `from .aes import AES` for the package to work

---
*[Content truncated: 437 lines total]*
---

- ⚠️ **DNS limitation**: `api.douyin.com` does NOT resolve from overseas servers — test from China/Asia region only
  - Even Chinese public DNS (114.114.114.114) returns **NXDOMAIN** — the domain is intentionally absent from global DNS
  - dnspython + socket.getaddrinfo monkey-patch **won't help** when the authoritative DNS itself returns nothing
  - Only real fix: hardcode a known-working IP from a real App's packet capture + `/etc/hosts` entry
- ⚠️ **register_device() fallback**: if server registration returns `device_id=0` (silent reject), the function now falls back to `make_seed_device()` instead of crashing. Gives a usable `Device` with seed IDs for testing the signing pipeline, but seed IDs won't pass server validation for real API calls.

### `sign_web_request()` — Web API

```python
from sign import sign_web_request

result = sign_web_request(
    path="/aweme/v1/web/hot/search/list/",
    params={"detail_list": "1"},
)
# Signs with X-Bogus, sends to www.douyin.com, returns JSON
```

- Uses **Web API** base: `https://www.douyin.com`
- X-Bogus only (browser-style signing)
- ✅ Works from overseas servers (confirmed working from non-China IP)
- Default UA: Chrome 120 Windows

### `sign_web_request_abogus()` — Web API (current algorithm)

```python
from sign import sign_web_request_abogus

result = sign_web_request_abogus(
    path="/aweme/v1/web/aweme/post/",
    params={"sec_user_id": "MS4wLjAB...", "count": "6"},
    window_env="1536|747|...|Win32",
)
# Signs with A-Bogus, sends to www.douyin.com, returns JSON
```

- Uses **Web API** base: `https://www.douyin.com`
- A-Bogus (current algorithm, SM3 + RC4 + variant base64)
- ✅ Same overseas behavior as `sign_web_request()`
- Optional parameter `window_env` — defaults to standard fingerprint if not overridden
- Default UA: Chrome 120 Windows
- ⚠️ For modern Douyin Web, `sign_web_request_abogus()` is preferred over `sign_web_request()` (X-Bogus) because Douyin has switched to A-Bogus as the current web signature.

### Endpoint Difference

| API | Base URL | Example Path | Signatures |
|-----|----------|-------------|------------|
| Web | `www.douyin.com` | `/aweme/v1/web/aweme/post/` | X-Bogus |
| Mobile | `api.douyin.com` | `/aweme/v1/aweme/post/` | X-Gorgon, X-Khronos, X-SS-STUB, X-Argus, X-Ladon |

The two APIs may return different JSON structures for the same logical endpoint. Migrating from Web to Mobile requires field-level testing.

## Device Registration

### Device Class (`sign/device.py`)

```python
from sign import Device

d = Device(
    "1234567890",           # device_id
    install_id="987654321", # install_id
    iid="",
    device_type="SM-S928B",
    os_version="34",
    app_version="38.5.0",
)

# Generate session headers
d.to_cookie()       # "install_id=...; odin_tt=...; sessionid=..."
d.user_agent        # "com.ss.android.ugc.aweme/38.5.0 (Android 34; SM-S928B)"
d.to_headers()      # dict: User-Agent + Cookie + X-Requested-With

# Persist / restore
d.to_dict()         # → dict
Device.from_dict()  # → Device
```

Every signed Mobile API request needs a `Device` with at minimum `device_id` and `install_id` for X-Argus.

### register_device() — Async Registration

```python
from sign import register_device

d = await register_device()  # Device with server-returned IDs
```

- POSTs to `https://log.snssdk.com/service/2/device_register/`
- Uses preseed parameters (random device_type, openudid, etc.)
- Signs request with X-Gorgon only (no X-Argus needed)

### ⚠️ `api.douyin.com` DNS NXDOMAIN (global)

**`api.douyin.com` does NOT resolve from any DNS server worldwide** — not even 114.114.114.114 (China Telecom). The domain is intentionally absent from global DNS. This is NOT a client-side DNS blocking issue.

- dnspython + socket.getaddrinfo monkey-patch **does NOT help** — the authoritative DNS itself returns NXDOMAIN
- Only fix: capture a real App's network traffic → extract the hardcoded IP → write to `/etc/hosts`
- Alternative: deploy the proxy on a VPS and use Web API (`www.douyin.com`) instead, which works globally

### ⚠️ Known Pitfall: Returns `device_id=0`

Tested 2026-06-30: registration returns `{"server_time":1782817561,"device_id":0,"install_id":0}`.

The server rejects the registration because:
1. **Signature not recognized** — X-Gorgon algorithm may encode params differently for registration endpoint
2. **Missing required fields** — real TikTok App sends additional device fingerprint params
3. **Rate limiting / IP blacklist** — may need device farm or proxy rotation
4. **Endpoint deprecated** — registration flow may have changed

**Fix**: capture real App's registration traffic via Frida/packet capture and compare byte-for-byte. Alternative: use a **pre-registered device_id** from a working App install.

## FastAPI Proxy Deployment

The `proxy.py` template (`templates/proxy.py`) provides a lightweight HTTP proxy that signs requests and proxies them through the VPS.

**📚 New reference**: `references/mobile-api-alternative.md` — how `aweme.snssdk.com` bypasses Janus.
**📚 New reference**: `references/video-download.md` — CDN URL parameters, watermark removal, and download flow.

### Key Design Decision: Proxy, don't return signed_url

| Approach | Issue |
|----------|-------|
| Return `signed_url` → client calls www.douyin.com directly | **HTTP 200, Content-Length: 0** — non-China IPs pass X-Bogus verification but get empty responses (server-side geo-gating) |
| Proxy the request through the VPS | **Works** — the VPS itself gets real data back from www.douyin.com and relays it to the client |

**Always proxy the request through the VPS.** Never return a `signed_url` for the client to call directly — non-China IPs get empty responses even with valid X-Bogus.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/douyin/web/{path}` | Web API — signs + proxies through www.douyin.com. ✅ Works globally |
| GET | `/api/douyin/mobile/{path}` | Mobile API — signs with full X-Gorgon family. ❌ api.douyin.com unreachable from overseas |

### Proxy Workflow

```python
# proxy.py — Deployed on VPS, uses httpx to proxy requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from sign.bogus import sign_full
import httpx

@app.get("/api/douyin/web/{path:path}")
async def web_api(path: str, request: Request):
    params = dict(request.query_params)
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"
    signed_qs = sign_full(qs, ua)
    full_url = f"https://www.douyin.com/{path}?{signed_qs}"
    resp = httpx.get(full_url, headers={
        "User-Agent": ua, "Referer": "https://www.douyin.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }, timeout=20)
    return PlainTextResponse(resp.text, status_code=resp.status_code)
```

## douyin-sign Repository

- **GitHub**: https://github.com/7452323/douyin-sign

- armxe imports are non-standard (`from cipher import AES`) — must be adapted to `from .aes import AES` for the package to work
- TTEncrypt is 1707 lines of dense code — always read the source file directly instead of trying to reproduce from memory; the S-box tables (dword_0..dword_9) must be exact copies
- **ttencrypt.py is too large for subagents (1707 lines)** — they routinely drop or truncate it. `cp` it directly from the source repo: `cp /root/tiktok-api/TTEncrypt/ttencrypt.py sign/ttencrypt.py`
- **Test format expectations**: X-Khronos output is 8-char hex (not 13-digit decimal), X-Gorgon output is hex (not 20-char alphanumeric like X-Bogus). Subagent-written tests often hardcode the wrong format — always `pytest` and fix assertions before commit
- **.gitignore needed before first commit**: subagents never add it. Create `__pycache__/`, `*.pyc`, `.venv/`, `.pytest_cache/` then `git rm --cached` any pycache files already staged
- X-Bogus does NOT use the same constants as X-Gorgon — it has its own algorithm independent of GORGON_TABLE/SIGN_KEY
- **method param mismatch**: when writing functions that accept a `method` parameter, the actual HTTP call must use `httpx.request(method=method, ...)` — not a verb-specific shortcut like `httpx.get()`. Triple-check during code review or when debugging 405 errors
### ⚠️ `api.douyin.com` NXDOMAIN (global): the domain is globally absent from public DNS (even 114.114.114.114 returns NXDOMAIN). The dnspython + socket.getaddrinfo monkey-patch technique is NOT a fix for this — it only helps when client DNS is blocked but the domain is still resolvable via an alternative DNS server. For api.douyin.com, only hardcoded IPs from real packet captures work
- **Overseas deployment**: Web API (www.douyin.com) works fine from any VPS. Mobile API (api.douyin.com) is unreachable from overseas — use aweme.snssdk.com instead, or test in China/Asia region
### ⚠️ Non-China IP empty response trap (Janus per-endpoint filtering)

Returning `signed_url` for the client to call www.douyin.com directly → HTTP 200 + Content-Length: 0 (empty body). X-Bogus passes (no 444 error), but the server geo-gates the response.

**BUT: even proxying through the VPS does NOT fix user-specific endpoints.** Janus applies **per-endpoint IP-geo filtering**, not just IP-level blocking:

| Endpoint Class | Example | VPS proxy | Client direct |
|----------------|---------|-----------|---------------|
| Public (no user data) | `hot/search/list/` | ✅ Real data | ✅ Real data |
| User-specific | `aweme/post/`, `user/profile/other/` | ❌ content-length: 0 | ❌ content-length: 0 |
| User-specific (explicit block) | `following/list/` | ❌ 404 `"Unsupported path(Janus)"` | ❌ 404 |

The VPS itself (with valid X-Bogus) gets empty responses for user endpoints. Cookies (real/fake `s_v_web_id`) don't help — block is IP-geo at Janus level, not cookie-based.

**Fix**: use Mobile API through `aweme.snssdk.com` (see `references/mobile-api-alternative.md`). This domain is NOT subject to the same Janus geo-filtering.

## Pitfalls

- **`sign_mobile_request` is sync, not async** — calling it with `await` in a FastAPI route raises `TypeError: object dict can't be used in 'await' expression`. Use `asyncio.to_thread(sign_mobile_request, ...)` in async handlers.
- **`MOBILE_API_BASE` patching** — `from sign import MOBILE_API_BASE; MOBILE_API_BASE = "..."` creates a local copy the function doesn't see. Use `import sign; sign.MOBILE_API_BASE = "..."` instead.
- **VPS kill pattern** — `fuser` is not installed on many minimal Linux VPS images. Use `PID=$(ss -tlnp | grep 8800 | grep -oP 'pid=\K\d+') && [ -n "$PID" ] && kill -9 $PID` to kill the old proxy process.
- **Janus per-endpoint IP-geo blocking**: non-China IPs get content-length: 0 for user-specific endpoints (aweme/post/, profile/other/) even with valid X-Bogus from the VPS proxy itself. following/list/ returns 404 "Unsupported path(Janus)". Public endpoints (hot/search/list/) work fine.
- X-SS-STUB IS JUST MD5 — trivial, don't list it as "missing" (triggers user irritation)
- SIGN_KEY is 32 bytes, base64-encoded = 44 chars ending with `=`
- X-Gorgon arm64 prefix = `8404`, non-arm64 = `0404`
- Empty body still needs MD5 of empty string, not skipped
- Body payload for X-Gorgon is raw bytes or 16 zero-bytes, not the MD5 hash
- X-Argus needs device_type (e.g. SM925), sdk_version (e.g. v04.04.05-ov-android), etc. — not all optional
- dyn_seed + dyn_version are optional — without them, protobuf field 24/25/26 are omitted

---
