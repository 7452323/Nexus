# Android APK Static Analysis (Python-Only, No Java/JADX)

Pure Python pipeline for static APK analysis when Java/JADX are unavailable.

## Toolchain

| Tool | Purpose | Install |
|------|---------|---------|
| `androguard` | DEX analysis, class listing, method decompilation | `pip3 install androguard` |
| `lief` | SO/ELF binary parsing, symbol extraction | `pip3 install lief` |
| `zipfile` (stdlib) | APK extraction (APK = ZIP) | Built-in |
| `frida` (optional) | Dynamic hooking for runtime validation | `pip3 install frida frida-tools` |

## Phase 1: Quick Reconnaissance

### 1.1 APK Structure Overview

```python
import zipfile
with zipfile.ZipFile('app.apk', 'r') as z:
    names = z.namelist()
    dex_files = [n for n in names if n.endswith('.dex')]
    so_files = [n for n in names if n.endswith('.so')]
    asset_dirs = set(n.split('/')[1] for n in names if n.startswith('assets/') and n.count('/') > 1)
    
    # Tech stack detection
    is_flutter = any('flutter' in n.lower() or 'libflutter' in n.lower() for n in names)
    is_react_native = any('react-native' in n.lower() or 'index.android.bundle' in n.lower() for n in names)
    is_singbox = any('libbox.so' in n or 'nekohasekai' in n.lower() for n in names)
```

### 1.2 Extract Key Files

```python
targets = [n for n in z.namelist() if any(k in n for k in [
    'demo_nodes', 'node_selection', 'config', 'subscribe', 'encrypt', 'api', 'server'
])]
for t in targets:
    z.extract(t, '/tmp/analysis/extracted/')
```

## Phase 2: DEX Analysis with Androguard

### 2.1 Basic APK Info

```python
from androguard.misc import AnalyzeAPK
a, d, dx = AnalyzeAPK("/path/to/app.apk")

print(f"Package: {a.get_package()}")          # e.g. com.ailian.accelerator
print(f"Main Activity: {a.get_main_activity()}")  # entry point
print(f"Version: {a.get_androidversion_code()}")
```

**Note**: Androguard's `AnalyzeAPK` is verbose (DEBUG logging). For clean output, suppress:
```python
import logging
logging.getLogger('androguard').setLevel(logging.WARNING)
```

### 2.2 Class Discovery (Filtered)

```python
# Filter for app-specific classes only (exclude third-party libs)
THIRD_PARTY = ['/google/', '/android/', '/kotlin/', '/okhttp3/', '/java/', '/javax/', 
               '/kotlinx/', '/org/', '/androidx/']

key_patterns = ['subscribe', 'node', 'config', 'encrypt', 'decrypt', 'api', 'network',
                'server', 'proxy', 'profile', 'auth', 'token', 'aes', 'secret']

all_classes = d[0].get_classes()
found = []
for cls in all_classes:
    name = cls.get_name()
    if any(p in name.lower() for p in key_patterns):
        if not any(lib in name for lib in THIRD_PARTY):
            found.append(name)
```

### 2.3 Method Decompilation

```python
# Get a specific class and its methods
from androguard.core.dex import DEX

for cls in d[0].get_classes():
    if 'NodeDataManager' in cls.get_name():
        for method in cls.get_methods():
            print(f"Method: {method.get_name()}")
            # Get bytecode / disassembly
            code = method.get_code()
            if code:
                print(f"  Registers: {code.get_registers_size()}")
                print(f"  Insns: {code.get_insns_size()}")
```

**Limitation**: Androguard provides disassembly, not full decompilation like JADX. For human-readable source, use JADX (requires Java). For analysis, disassembly + string constants + xrefs are often sufficient.

## Phase 3: SO/Native Library Analysis with LIEF

### 3.1 Basic SO Info

```python
import lief
binary = lief.parse('/path/to/libbox.so')
print(f"Arch: {binary.header.machine_type}")
print(f"Exports: {len(list(binary.exported_functions))}")
print(f"Imports: {len(list(binary.imported_functions))}")
```

### 3.2 Symbol Search (Key for Go binaries)

```python
# Go binaries (like sing-box's libbox.so) have JNI bridge symbols
# Pattern: Java_<package>_<class>_<method>
jni_symbols = [s.name for s in binary.exported_functions 
               if s.name.startswith('Java_')]

# Search for specific functionality
key_patterns = ['encrypt', 'decrypt', 'subscribe', 'config', 'profile',
                'node', 'outbound', 'ssl', 'cert']
matched = [s.name for s in binary.exported_functions
           if any(p in s.name.lower() for p in key_patterns)]
```

### 3.3 Go Binary Specifics

Go-compiled SO files (gomobile) have characteristic patterns:
- JNI bridge: `Java_io_nekohasekai_libbox_*` (sing-box)
- cgo bridge: `_cgo_*` and `_cgoexp_*` prefixes
- 1000+ exported functions (Go exports all symbols by default)
- 43MB+ size typical for full Go runtime + app logic

## Phase 4: Identifying Common App Frameworks

| Framework | Detection Signals | Key Classes |
|-----------|------------------|-------------|
| **sing-box (SFA)** | `libbox.so`, `io.nekohasekai.libbox.*`, `io.nekohasekai.sfa.*` | `BoxService`, `CommandClient`, `ProfileDecoder`, `ImportRemoteProfile` |
| **Clash/CMFA** | `libclash.so`, `com.github.kr328.clash.*` | `ClashService`, `ProfileProvider` |
| **V2rayNG** | `libv2ray.so`, `com.v2ray.ang.*` | `V2RayServiceManager` |
| **Flutter** | `libflutter.so`, `assets/flutter_assets/` | Flutter-specific SO analysis needed |
| **React Native** | `index.android.bundle`, `libreactnativejni.so` | JS bundle analysis |

## Phase 5: Node/Subscription Extraction Pattern

For proxy VPN apps (sing-box, Clash, V2rayNG), node data typically flows:

```
API Endpoint (ApiEndpointManager)
    → Authentication (AuthService: login/autoRegister/token)
    → Subscription Fetch (fetchNodesFromApi/getSubscribeInfo)
    → Config Parse (ProfileDecoder/ImportRemoteProfile)
    → Node Store (NodeDataManager/VpnNode DB)
    → UI Display (WebView AndroidBridge interface)
```

### Key Analysis Targets

1. **ApiEndpointManager** — Find hardcoded or dynamically resolved API base URLs
2. **AuthService** — Token generation, request signing, auth headers
3. **fetchNodesFromApi** — HTTP request construction, response parsing
4. **ProfileDecoder** — Config decryption if subscription content is encrypted
5. **NodeDataManager** — Local caching, TrustManager override (cert bypass)

### H5 WebView Bridge Extraction

Proxy apps often use WebView for node selection. Extract the JS interface:

```python
# From assets/h5/node_selection.js
# Look for AndroidBridge calls:
# AndroidBridge.onNodeSelected(tag)
# AndroidBridge.startSpeedTest(tagsJson)
# AndroidBridge.onModeChanged(mode)
```

The Java side implements `@JavascriptInterface` methods — find these in the WebAppInterface inner class.

## Session-Learned Patterns

### AES-CBC Subscription Encryption (sing-box apps)

Many sing-box-based proxy apps encrypt the `subscribe_url` field in the API response. Pattern:

1. API returns `{"data": {"subscribe_url": "v1.<base64>"}}`
2. Format: `"v1." + Base64(IV[16B] + AES-CBC ciphertext)`
3. Key derivation: `SHA256(hardcoded_key_string)` → 32-byte AES-256 key
4. Decryption: strip `"v1."` prefix → Base64 decode → split IV/ciphertext → AES-CBC decrypt → PKCS5 unpad → UTF-8 plaintext

The hardcoded key string is typically found in `NodeDataManager` or similar class. Search string constants for patterns like `*Key*`, `*Secret*`, `*Subscribe*`.

**Tracing the decryption**: look for methods named `decryptSubscribeUrl`, `decryptConfig`, or methods that check for a `"v1."` prefix string.

### Androguard Decompilation Output Size

When using androguard to decompile Go/gomobile-backed classes (like `libbox.ProfileContent`, `libbox.ProfileDecoder`), the output can be **extremely large** (5-50MB per class). These are Go runtime types flattened into Java by gomobile — not useful for analysis. Focus on the app-specific Kotlin/Java classes instead (smaller, more meaningful).

**Practical filter**: Skip decompiling any class under `io.nekohasekai.libbox.*` (these are Go bridge stubs). Target `io.nekohasekai.sfa.*` (app logic) instead.

### fetchNodesFromApi Trace Pattern (sing-box SFA)

Standard call chain for node retrieval in SFA apps:

```
WebAppInterface.fetchNodesFromApi(callback)
  → NodeDataManager.fetchNodes()
    → fetchConfigFromSubscribeDirectly()  // preferred path
      → getUserToken()
      → GET /api/v1/user/getSubscribe (header or param: usertoken)
      → parse response.data.subscribe_url
      → decryptSubscribeUrl()  // AES-CBC if "v1." prefix
      → return sing-box JSON config
    → fetchConfigFromApiOld()  // fallback path
      → same API call, different processing
  → NodeDataManager.parseNodes(configJson)
    → filter outbounds by type (trojan/vless/vmess/ss/hysteria/tuic/anytls)
    → filter "剩余"/"过期" tags
    → build VpnNode list
```

### API Base URL Discovery via DNS TXT

Some apps resolve their API base URL through DNS TXT records rather than hardcoding:

1. Query DNS TXT for a discovery domain (e.g. `a.yrappdns.com`)
2. TXT value format: `urls=https://host1,https://host2,https://host3`
3. Probe each URL (HEAD request, short timeout)
4. Cache first responsive URL as base URL
5. Fallback chain if cached URL fails

Look for classes like `ApiEndpointManager` with methods `awaitBaseUrl`, `forceRefresh`, `refresh`.

## Pitfalls

- **Androguard is slow** — AnalyzeAPK with cross-reference creation takes 10+ seconds. Suppress DEBUG logging to reduce noise.
- **No full Java decompilation without JADX** — Androguard gives disassembly, not decompiled source. Install JADX + Java for human-readable output: `brew install jadx`
- **Go SO symbols are overwhelming** — libbox.so has 1400+ exports. Filter by `Java_` prefix for JNI bridges, then trace into Go internals.
- **Go bridge class decompilation is huge** — `io.nekohasekai.libbox.*` classes decompile to 5-50MB. Skip them, focus on app-specific `io.nekohasekai.sfa.*` classes.
- **APK resources are compressed** — AndroidManifest.xml is binary AXML, not text. Use androguard's `a.get_activities()` instead of raw parse.
- **Python 3.9 compatibility** — macOS system Python is 3.9.6. Don't use `X | None`, use `Optional[X]`. Don't use `dict[str,str]`, use `Dict[str,str]`.
- **Encrypted subscribe_url won't be in strings** — The encryption key string is in DEX constants, but the actual node data is only available at runtime via API. Static analysis can only recover the decryption algorithm + key, not the nodes themselves.

## Delegation Pattern

For long analysis tasks, write a ref.md plan and delegate to local CodeBuddy:

```bash
codebuddy -p -y "Read /tmp/analysis/ref.md and execute all tasks." 
```

The ref.md should include: identified key classes, tool installation status, output paths, and Python version constraints.
