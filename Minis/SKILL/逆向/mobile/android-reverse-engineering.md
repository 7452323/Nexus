---
name: android-reverse-engineering
description: "Android应用逆向工程全流程 (2026.07)。APK反编译、smali分析、Frida动态Hook、JNI/SO分析、脱壳、混淆对抗。整合最新 AI 驱动工具和 MCP 技能。"
license: MIT
---

# Android 逆向工程 (2026.07)

## 触发条件
- 逆向分析Android APK
- 提取应用逻辑/算法
- 绕过安全检测/脱壳
- 分析恶意Android应用
- 还原混淆代码

## 工具链 (2026.07)

### 必备工具
| 工具 | 安装 | 用途 | Stars |
|------|------|------|-------|
| jadx | `brew install jadx` | APK-Java反编译（v1.5.6, 2026-07） | 49.7k⭐ |
| apktool | `brew install apktool` | APK解包/重打包/smali | — |
| Frida | `pip install frida-tools` | 动态Hook框架 | — |
| Ghidra | 下载安装 | SO原生库分析 | — |
| dex2jar | GitHub releases | DEX-JAR转换 | — |

### AI 驱动工具 (NEW 2026)
| 工具 | Stars | 用途 | 特点 |
|------|-------|------|------|
| **SimoneAvogadro/android-reverse-engineering-skill** | 6.4k⭐ | Claude Code 技能 | 自动反编译 + API 提取 + Frida 脚本生成 |
| **ReverserID/JURIG** | — | AI-agentic RE 框架 | Go 编写，无 MCP，TUI 界面 |
| **incogbyte/android-reverse-engineering-claude-skill** | 86⭐ | Claude Code 技能 | AAB/APK/XAPK 反编译 + 自适应 Frida 动态分析 |

### jadx v1.5.6 新特性 (2026-07)
- Kotlin 元数据恢复（R8 混淆后还原类名）
- 改进的 deobfuscator
- 支持 APK/AAB/XAPK/APKM 多种格式

## 工作流程

### Phase 0: 指纹识别 (NEW)
```bash
# SimoneAvogadro skill
bash scripts/fingerprint.sh app.apk
# 输出: 框架(Flutter/RN/Cordova/Xamarin/Kotlin)、HTTP 栈、混淆级别、Native 库
```

### Phase 1: 信息收集
```bash
file app.apk
unzip -l app.apk | head -30
apktool d app.apk -o app_decoded/
jadx -d app_java/ app.apk
```

### Phase 2: 静态分析
```bash
grep -r "password\|token\|secret\|api_key" app_java/
grep -rn "https\?://" app_java/ --include="*.java"
grep -rn "AES\|RSA\|DES\|Cipher" app_java/
```

### Phase 3: 动态分析（Frida）
```javascript
Java.perform(function() {
    var Cipher = Java.use("javax.crypto.Cipher");
    Cipher.doFinal.overload('[B').implementation = function(input) {
        console.log("Cipher input: " + Java.use("java.lang.String").$new(input));
        var result = this.doFinal(input);
        console.log("Cipher output: " + bytesToHex(result));
        return result;
    };
});
```

### Phase 4: 脱壳
```bash
# Frida 脱壳
frida -U -f com.example.app -l dump_dex.js --no-pause
# BlackDex（免root）
```

### Phase 5: 重打包
```bash
apktool b app_decoded/ -o app_modified.apk
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my.keystore app_modified.apk alias_name
```

## 常见场景

### 场景1: 提取API接口
```bash
grep -rn "Retrofit\|OkHttp\|Volley" app_java/
grep -rn "@GET\|@POST\|@PUT\|@DELETE" app_java/
```

### 场景2: 绕过root检测
```javascript
Java.perform(function() {
    var RootChecker = Java.use("com.scottyab.rootbeer.RootBeer");
    RootChecker.isRooted.implementation = function() { return false; };
});
```

### 场景3: 分析混淆代码
```bash
jadx --deobf app.apk -o app_deobf/
# Kotlin 元数据恢复（R8 混淆后还原 Repository/ViewModel/UseCase 类名）
```

## 注意事项
1. **法律合规**：仅对有授权的应用进行逆向
2. **环境隔离**：在模拟器或隔离设备中分析
3. **jadx 版本**：v1.5.6 (2026-07) 修复了 Java 21/Win 上的 NPE 问题

