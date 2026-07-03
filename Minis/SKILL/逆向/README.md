# 🔧 逆向工程技能树 - Reverse Engineering Skills

> 26 个逆向技能全覆盖，从 Web JS 到 Native SO、从二进制到协议的全栈逆向场景。

## 📂 技能索引 (26个)

| 技能 | 用途 |
|------|------|
| `algorithm-reverse` | JS逆向算法还原——签名/混合加密/Cookie签名 |
| `android-reverse-engineering` | Android应用逆向——APK反编译/smali/Frida Hook/JNI分析/脱壳 |
| `anti-debug` | JS反调试对抗——4类反调试识别+绕过 |
| `anti-debugging-techniques` | 反调试检测+绕过通用playbook |
| `ast-deobfuscation` | Babel AST分层定向反混淆——7步流程 |
| `binary-diffing` | 二进制Diffing——Diaphora/BinDiff对比+补丁分析+1-day漏洞 |
| `camoufox-workflow` | JS逆向工作流——Node.js/Python接口自动化+签名还原 |
| `code-obfuscation-deobfuscation` | 代码混淆分析+反混淆playbook |
| `desktop-app-reverse-engineering` | 桌面应用逆向——静态分析+前端资源提取+AI prompt提取 |
| `env-patch` | JS补环境统一技能——Node.js引擎+策略分离架构 |
| `find-crypto-entry` | 定位加密参数生成入口（函数位置+调用链） |
| `har-to-proxy-script` | HAR抓包→QuantumultX/Surge代理脚本 |
| `ida-reverse-analysis` | IDA Pro逆向分析——IDAPython脚本+加密识别+DLL导出 |
| `ios-app-unlock` | iOS原生Swift应用逆向——Swift5反射+二进制Hook |
| `js-reverse-engineering` | JS逆向总纲——6阶段全流程（Observe→Capture→Rebuild→Patch→PureExt→Auto） |
| `js-reverse-mcp-integration` | JS逆向MCP集成——Patchright反检测引擎+23种工具 |
| `jsvmp-reverse` | JSVMP/VMP虚拟机逆向——数据驱动+AST反编译双路线 |
| `protocol-reverse-engineering` | 协议逆向——protobuf-inspector/netzob/Wireshark+消息格式分析 |
| `pyinstaller-reverse` | PyInstaller打包逆向——解包+反编译+恢复源码 |
| `reverse-engineering-general` | 通用逆向框架——8个子技能（Frida/Unicorn/IDA/DexDump等） |
| `ruishu-reverse` | 瑞数反爬纯算逆向——Cookie T生成+URL后缀 |
| `so-native-analysis` | SO原生库分析——30种工具覆盖基本分析+Flutter专项 |
| `symbolic-execution-tools` | 符号执行+约束求解工具链 |
| `vm-and-bytecode-reverse` | 自定义VM+字节码逆向通用playbook |
| `web-api-reverse-engineering` | Web API协议逆向通用方法论 |
| `web-api-to-openai-proxy` | Web API逆向→OpenAI兼容代理服务构建 |
| `webpack-unpack` | Webpack打包模块提取+还原独立可运行JS |

## ⚡ 典型工作流

### Web JS 逆向全流程
`anti-debug` → `find-crypto-entry` → `env-patch` → `ast-deobfuscation` → `algorithm-reverse` → `web-api-to-openai-proxy`

### 移动端逆向全流程
`android-reverse-engineering` → `so-native-analysis` → `ida-reverse-analysis` → `reverse-engineering-general`

### VMP 逆向全流程
`anti-debug` → `ast-deobfuscation`(预处理) → `jsvmp-reverse`(VMP还原) → `algorithm-reverse`(算法提取)

---

📦 由 [reverse-engineering-skills] 导入 @ 2026-05-26 09:42:36
