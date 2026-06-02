# WeChat Mini-Program (.wxapkg) Reverse Engineering

## Overview

WeChat mini-programs are distributed as `.wxapkg` files. PC/Mac versions are **encrypted** with V1MMWX format. Mobile Android versions (from `/data/data/com.tencent.mm/`) are typically unencrypted.

## File Structure

```
{小程序AppID}/
├── 1363/                          # Version directory
│   ├── __APP__.wxapkg            # Main package (encrypted)
│   ├── _vipshop_login_.wxapkg    # Sub-package (login module)
│   ├── _vipshop_order_.wxapkg    # Sub-package (order module)
│   └── ...
```

## Decryption (V1MMWX Format)

### Encryption Scheme

1. **Header**: 6 bytes `V1MMWX` marker
2. **First 1024 bytes after header**: AES-CBC encrypted
3. **Remaining bytes**: XOR encrypted

### Key Derivation

```
AES Key = PBKDF2(password=wxid, salt="saltiest", iterations=1000, keylen=32, hash=SHA1)
AES IV  = "the iv: 16 bytes"  (16 bytes literal)
XOR Key = wxid[-2] (second-to-last character's ASCII value, or 0x66 if wxid < 2 chars)
```

Where `wxid` is the mini-program's AppID (e.g., `wxe9714e742209d35f`).

### Decryption Script (Python)

```python
#!/usr/bin/env python3
import os, argparse
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1
from Crypto.Cipher import AES

WXAPKG_FLAG = 'V1MMWX'

def decrypt_wxapkg(wxid, input_file, output_file):
    key = PBKDF2(wxid.encode(), b'saltiest', 32, count=1000, hmac_hash_module=SHA1)
    with open(input_file, 'rb') as f:
        data = f.read()
    
    if data[:6].decode() != WXAPKG_FLAG:
        # Not encrypted, copy as-is
        with open(output_file, 'wb') as f: f.write(data)
        return
    
    # Decrypt AES portion (bytes 6..1030)
    cipher = AES.new(key, AES.MODE_CBC, b'the iv: 16 bytes')
    header = cipher.decrypt(data[6:1030])
    
    # XOR decrypt remainder (bytes 1030..)
    xor_key = ord(wxid[-2]) if len(wxid) >= 2 else 0x66
    body = bytearray(b ^ xor_key for b in data[1030:])
    
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    with open(output_file, 'wb') as f:
        f.write(header[:1023] + body)
    print(f'Decrypted: {input_file} -> {output_file}')
```

Usage:
```bash
python decrypt_wxapkg.py --wxid wxe9714e742209d35f -d ./encrypted_dir -o ./decrypted_dir
```

## Unpacking

After decryption, use `unpack-wxapkg` (npm) to extract files:

```bash
npm install -g unpack-wxapkg
unpack-wxapkg decrypted.wxapkg output_dir
```

This extracts the full source tree: `.js`, `.json`, `.wxml`, `.wxss`, `.html` files.

## Post-Unpack Analysis

### Key File Types

| Extension | Content |
|-----------|---------|
| `app-service.js` | Main app logic (minified, all modules bundled) |
| `appservice.app.js` | Duplicate of app-service.js |
| `*.appservice.js` | Page/component logic chunks |
| `*.webview.js` | Template rendering code |
| `page-frame.js` | WXML compiled templates |
| `app-config.json` | App configuration |
| `app.wxss` / `*.wxss` | Stylesheets |

### Finding Specific Logic

Since code is heavily minified and bundled, use `grep` with multiple patterns:

```bash
# Login/session related
grep -rn "checkLoginStatus\|setCookie\|VIP_TANK\|saturn\|loginToken\|wx\.checkSession\|wx\.login" --include="*.js"

# Cookie management
grep -rn "Cookie\|getCookies\|setCookie" --include="*.js"

# API endpoints
grep -rn "weixin-api.vip.com\|mapi.vip.com\|mlogin" --include="*.js"
```

### Common Patterns in Mini-Program Auth

1. **wx.login()** → returns temporary `code`
2. **code** → sent to backend → returns session_key + custom tokens
3. **Tokens stored in wx.Storage** (not document.cookie)
4. **wx.checkSession()** → checks if WeChat session is still valid
5. **No automatic token refresh** → most mini-programs re-login on session expiry

## Pitfalls

- **V1MMWX header check fails**: File may not be encrypted (Android version) or uses different encryption. Check first 6 bytes.
- **unpack-wxapkg "firstMark" error**: File is still encrypted. Decrypt first.
- **UTF-8 decode errors during unpack**: Wrong decryption key (wxid). Verify AppID from folder name.
- **Huge "fileCount" numbers (billions)**: Decryption produced garbage. Wrong key or IV.
- **Sub-packages reference main package**: Login module (`_vipshop_login_`) imports from `../../modules/login/index` in the main package. Analyze both.
- **Code is heavily minified**: Variable names are meaningless. Focus on string literals, API URLs, and storage key names to understand logic.
- **Two copies of app-service.js**: `app-service.js` and `appservice.app.js` are identical. Analyze one.
