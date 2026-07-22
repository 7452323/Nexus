---
name: ios-reverse
description: "iOS应用逆向工程 (2026.07)。Swift/ObjC反编译、Frida Hook、越狱检测绕过、SSL Pinning 多层绕过、IPA 修补。整合最新工具和决策树。"
category: reverse-engineering
tags: [ios, frida, ssl-pinning, swift, jailbreak]
---

# iOS 逆向工程 (2026.07)

## 工具链

| 工具 | 用途 | 安装 |
|------|------|------|
| **objection** (9.2k⭐) | 运行时移动探索 | `pip install objection` |
| **Frida** (17.8.3) | 动态 Hook | `pip install frida-tools` |
| **httptoolkit/frida-interception-and-unpinning** | HTTPS MITM + SSL pinning 绕过 | GitHub |
| **pritessh/iOS-SSL-Pinning-Bypass** | iOS 17.x SSL Pinning 5层绕过 | GitHub |
| **v-y-archive/Jailbreak-detection** | 越狱检测绕过 | GitHub |
| **OWASP MASTG Frida Gadget** | 非越狱 Frida Gadget 注入 | GitHub |

## SSL Pinning 绕过决策树

```
App traffic not appearing in Burp
├─► Step 1: Try Objection
│     objection --gadget com.target.app explore
│     → ios sslpinning disable
│     ├─► Works? → DONE ✓
│     └─► Fails or partial?
│         ▼
├─► Step 2: Frida Universal Script
│     frida -U -f com.target.app -l ios_ssl_bypass.js
│     ├─► Works? → DONE ✓
│     └─► Hooks fire but no traffic?
│         ▼
├─► Step 3: SSL Kill Switch 2 (jailbreak)
│     Settings → SSL Kill Switch 2 → Enable
│     ├─► Works? → DONE ✓
│     └─► App refuses to connect?
│         ▼
├─► Step 4: IPA Patching
│     objection patchipa --source app.ipa --codesign-signature "..."
│     frida -U -n Gadget -l script.js
│     ├─► Works? → DONE ✓
│     └─► Tamper detection?
│         ▼
└─► Step 5: Hook at Data Layer
      Hook NSURLSession completionHandler
      Hook NSJSONSerialization
      Read post-decryption data directly
```

## SSL Pinning 5层绕过 (pritessh/iOS-SSL-Pinning-Bypass)

同时 Hook iOS TLS 栈的所有层：

| 层 | 框架 | Hook 方式 |
|----|------|----------|
| 1. Security.framework | SecTrustEvaluate / SecTrustEvaluateWithError | 替换为 NativeCallback，写 trusted result |
| 2. BoringSSL | SSL_CTX_set_custom_verify / SSL_set_custom_verify | 替换 callback 为 no-op，返回 SSL_VERIFY_OK |
| 3. Network.framework | sec_protocol_options_set_verify_block | ARM64 安全 fallback，尝试 5 种 type signature |
| 4. Alamofire | SessionDelegate challenge | 直接调用 .useCredential disposition |
| 5. Apple Private | AKCertificatePinning / AACertificatePinner | 所有方法返回 ptr(1) |

### 使用方法
```bash
# Attach mode
frida -l ios-ssl-pinning-bypass.js -n <AppName> -H <device-ip> --timeout=60

# Spawn mode (推荐，hook 在 startup code 之前)
frida -l ios-ssl-pinning-bypass.js -f <bundle-id> -H <device-ip>
```

### 前置条件
- 越狱 iOS 设备 (tested on iOS 17.4.1)
- Frida 17.8.3
- frida-server (matching version)
- Burp Suite / mitmproxy

## 越狱检测绕过

```javascript
// Frida 绕过越狱检测
Java.perform(function() {
    // 常见越狱检测绕过
    var File = Java.use("java.io.File");
    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        if (path.includes("/Applications/Cydia.app") || 
            path.includes("/bin/bash")) {
            return false;
        }
        return this.exists.call(this);
    };
});
```

## IPA 修补

```bash
# 使用 objection
objection patchipa --source app.ipa --codesign-signature "iPhone Developer: Name (ID)"

# 手动流程
# 1. 解压 IPA
unzip app.ipa -d app_extracted/
# 2. 注入 Frida Gadget dylib
# 3. 重签名
codesign -f -s "iPhone Developer: Name (ID)" Payload/App.app/Frameworks/FridaGadget.dylib
# 4. 重新打包
cd app_extracted && zip -qr ../app_patched.ipa .
```

## Info.plist ATS 修补

```bash
# 允许任意 HTTP 加载
plutil -convert xml1 Info.plist -o Info.xml
# 编辑添加 NSAllowsArbitraryLoads = true
plutil -convert binary1 Info.xml -o Info.plist
```

## 常用 Frida 脚本

### Hook NSJSONSerialization（数据层绕过）
```javascript
// 读取所有 JSON API 响应（无论哪个网络库）
Interceptor.attach(ObjC.classes.NSJSONSerialization['+ JSONObjectWithData:options:error:'].implementation, {
    onEnter: function(args) {
        var data = new ObjC.Object(args[2]);
        console.log('JSON data:', data.toString());
    }
});
```

### Hook NSURLSession completionHandler
```javascript
Interceptor.attach(ObjC.classes.NRURLSessionTaskDelegate['- URLSession:dataTask:didReceiveData:'].implementation, {
    onEnter: function(args) {
        var data = new ObjC.Object(args[3]);
        console.log('Response data:', data.toString());
    }
});
```

