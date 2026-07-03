---
name: android-reverse-engineering
description: "Android应用逆向工程全流程。APK反编译、smali分析、Frida动态Hook、JNI/SO分析、脱壳、混淆对抗。TRIGGER when: 用户需要逆向分析Android APK"
license: MIT
compatibility: Requires jadx, apktool, Frida, Ghidra
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
---

# Android逆向工程

## 触发条件

用户需要：
- 逆向分析Android APK
- 提取应用逻辑/算法
- 绕过安全检测/脱壳
- 分析恶意Android应用
- 还原混淆代码

## 工具链

### 必备工具
| 工具 | 安装 | 用途 |
|------|------|------|
| jadx | `brew install jadx` | APK-Java反编译（GUI+CLI） |
| apktool | `brew install apktool` | APK解包/重打包/smali |
| Frida | `pip install frida-tools` | 动态Hook框架 |
| Ghidra | 下载安装 | SO原生库分析 |
| dex2jar | GitHub releases | DEX-JAR转换 |

### 辅助工具
| 工具 | 用途 |
|------|------|
| bytecode-viewer | 多引擎反编译对比 |
| APKEditor | APK资源编辑 |
| MobSF | 自动静动态分析 |
| Quark Engine | 恶意行为分析 |

## 工作流程

### Phase 1: 信息收集
```bash
# 基本信息
file app.apk
unzip -l app.apk | head -30

# APK解包
apktool d app.apk -o app_decoded/

# 反编译为Java
jadx -d app_java/ app.apk

# 查看AndroidManifest.xml
cat app_decoded/AndroidManifest.xml
```

### Phase 2: 静态分析
```bash
# 搜索关键字符串
grep -r "password\|token\|secret\|api_key" app_java/

# 搜索硬编码URL
grep -rn "https\?://" app_java/ --include="*.java"

# 搜索加密相关
grep -rn "AES\|RSA\|DES\|Cipher" app_java/

# 分析SO库
# 用Ghidra打开 app_decoded/lib/arm64-v8a/*.so
```

### Phase 3: 动态分析（Frida）
```javascript
// Hook Java方法
Java.perform(function() {
    var MainActivity = Java.use("com.example.MainActivity");
    MainActivity.checkPassword.implementation = function(input) {
        console.log("Password: " + input);
        var result = this.checkPassword(input);
        console.log("Result: " + result);
        return result;
    };
});

// Hook加密函数
Java.perform(function() {
    var Cipher = Java.use("javax.crypto.Cipher");
    Cipher.doFinal.overload('[B').implementation = function(input) {
        console.log("Cipher input: " + Java.use("java.lang.String").$new(input));
        var result = this.doFinal(input);
        console.log("Cipher output: " + bytesToHex(result));
        return result;
    };
});

// 绕过SSL Pinning
Java.perform(function() {
    var TrustManager = Java.use("com.example.CustomTrustManager");
    TrustManager.checkServerTrusted.implementation = function() {
        // 绕过证书验证
    };
});
```

### Phase 4: 脱壳（如果加壳）
```bash
# FART脱壳（需要root设备）
# 在设备上运行app，等待自动dump

# Frida脱壳脚本
frida -U -f com.example.app -l dump_dex.js --no-pause

# BlackDex（免root脱壳）
# 安装BlackDex APK，选择目标app
```

### Phase 5: 重打包（如需修改）
```bash
# 修改smali代码
vim app_decoded/smali/com/example/MainActivity.smali

# 重新打包
apktool b app_decoded/ -o app_modified.apk

# 签名
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my.keystore app_modified.apk alias_name
```

## 常见场景

### 场景1: 提取API接口
```bash
# 反编译后搜索网络请求
grep -rn "Retrofit\|OkHttp\|Volley" app_java/
grep -rn "@GET\|@POST\|@PUT\|@DELETE" app_java/
```

### 场景2: 绕过root检测
```javascript
// Frida绕过root检测
Java.perform(function() {
    var RootChecker = Java.use("com.scottyab.rootbeer.RootBeer");
    RootChecker.isRooted.implementation = function() {
        return false;
    };
});
```

### 场景3: 分析混淆代码
```bash
# 使用jadx的反混淆功能
jadx --deobf app.apk -o app_deobf/

# 对比多个版本还原类名
# 使用Obfu[DE]scate工具
```

## 知识库引用

- `~/.hermes/knowledge/re-engineering/android-re/` — Android逆向资源库
- `~/.hermes/knowledge/re-engineering/ctf-skills/languages-platforms.md` — Android平台特化

## 注意事项

1. **法律合规**：仅对有授权的应用进行逆向分析
2. **环境隔离**：在模拟器或隔离设备中分析恶意应用
3. **版本差异**：不同Android版本API差异大，注意适配
4. **64位优先**：优先分析arm64-v8a架构的SO库
