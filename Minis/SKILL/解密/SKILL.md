---
name: decrypt
description: 解密技能 — 对抗各类加密/编码/混淆的通用工具集。覆盖Base/Hex/URL/Hash、对称加密、JS混淆、图片隐写、流量解密、jsjiami对抗、decode_action 7插件16Visitor全流程
---

# 🔓 解密工具箱

## 快速速查

| 你遇到什么 | 用什么解 |
|-----------|---------|
| `ZmxhZ3t...` | Base64 |
| `1a2b3c4d...` (32位) | MD5 |
| `%7B%22a%22%3A1%7D` | URL Decode |
| `eval(atob(...))` | JS解密 |
| `nZOqk6qUsZaz...` | 可能是AES/RC4 |
| 图片看起来正常但文件很大 | 图片隐写 |
| pcap/流量包加密 | 流量分析 |

## 编码识别

| 特征 | 类型 | 解法 |
|------|------|------|
| `[A-Za-z0-9+/=]{4,}` 末尾=` | Base64 | `base64 -d` |
| `[A-Za-z0-9-_]{4,}` 无填充 | Base64 URL Safe | `base64url -d` |
| `[A-Z2-7=]{4,}` | Base32 | `base32 -d` |
| `[0-9a-v]{4,}` | Base36 | Python int(s, 36) |
| `0x1a2b...` | Hex | `xxd -r -p` |
| `\x1a\x2b...` | Hex Escape | unicode_escape |

## 常用命令

```bash
base64 -d       # Base64
xxd -r -p        # Hex
# 多层Base64
python3 -c "import base64; s='...'
while True:
    try: s=base64.b64decode(s).decode()
    except: break; print(s)"
```

## AES/RC4 解密

```python
from Crypto.Cipher import AES
cipher = AES.new(key, AES.MODE_CBC, iv)
plain = cipher.decrypt(base64.b64decode(data))

def rc4(data, key):
    S = list(range(256)); j = 0
    for i in range(256): j = (j+S[i]+key[i%len(key)])%256; S[i],S[j]=S[j],S[i]
    i=j=0; out=[]
    for c in data:
        i=(i+1)%256; j=(j+S[i])%256; S[i],S[j]=S[j],S[i]
        out.append(c ^ S[(S[i]+S[j])%256])
    return bytes(out)
```


---

## jsjiami.com 加密对抗（10 款产品全览）

| 产品 | 特征 | 难度 |
|------|------|------|
| JS压缩加密 | eval包装+变量名缩短 | ⭐ |
| JS混淆加密 | 字符串hex+变量重命名 | ⭐⭐ |
| JS高级加密(SOJSON) | 自执行函数+花指令 | ⭐⭐⭐ |
| SOJSON.V5 | 64组件+控制流 | ⭐⭐⭐ |
| JS最牛加密V6 | RC4/Base64+控制流+反调试+域名锁 | ⭐⭐⭐⭐ |
| JS最牛加密V7 | 多态+抗格式化+Anti-Selenium+自卫模式 | ⭐⭐⭐⭐⭐ |
| JS方法加密(VIP) | 仅加密方法体 | ⭐⭐ |
| JS/HTML/CSS混合加密 | charCode→eval | ⭐⭐ |
| AAEncode/JSFuck | 仅符号([]()!+) | ⭐ |
| eval压缩 | eval+局部变量缩短 | ⭐ |

### V6 vs V7 区别

| 项 | V6 | V7 |
|----|----|----|
| 加密规则 | RC4/Base64固定 | 多态(每次不同) |
| 控制流 | switch/case平坦化 | 平坦化+不规则跳转 |
| 抗格式化 | 基本 | 强(格式化即失效) |
| 自卫模式 | 无 | 有 |

### V6/V7 通用解密流程（5级）

```
1. 识别版本: jsjiami.v5/.v6/.v7
2. 格式化: js-beautify
3. 字符串解密: V5 hex解码 / V6 RC4提取key / V7多步执行捕获
4. 控制流还原: AST遍历switch/case恢复顺序执行+删除死代码
5. 反调试+域名锁绕过: mock location.hostname / CDP注入 / 删域名校验
```

### jsjiami 配置项影响

| 配置 | 影响 | 反混淆策略 |
|------|------|-----------|
| 压缩成一行 | 单行代码 | js-beautify |
| 防止格式化 | 格式化后失效 | patch检测逻辑 |
| 花指令注入 | 干扰解码 | 死代码识别删除 |
| 自卫模式 | 最高防护 | mock环境变量 |
| 变量规则混淆 | `_0x`格式 | AST重命名 |
| 禁止控制台调试 | 阻塞DevTools | CDP绕过 |
| 安全域名 | 域名锁定 | mock location.hostname |
| 函数全部重命名 | 全局混淆 | 保留配置+AST修复 |


---

## decode_action 反混淆全解析

> smallfawn/decode_action — 7 种加密自动检测 + 16 个 AST Visitor

### 7 种加密类型

| 类型 | 插件 | 识别特征 |
|------|------|---------|
| sojson (jsjiami.v6) | sojson.js | AST对象存储+switch/case |
| sojsonv7 (jsjiami.v7) | sojsonv7.js | 多态+自卫模式 |
| obfuscator | obfuscator.js | 大数组+移位函数+自执行 |
| awsc (阿里云WAF) | awsc.js | 大量void+条件赋值 |
| jsconfuser | jsconfuser.js | 字符串压缩+全局隐藏 |
| jjencode | jjencode.js | 仅`[]()!+$`符号 |
| common | common.js | 代码清理+常量折叠 |

### 16 个 AST Visitor

| Visitor | 功能 |
|---------|------|
| `calculate-constant-exp` | 常量折叠 `1+2→3` |
| `calculate-rstring` | 运行时字符串计算 |
| `parse-control-flow-storage` | 对象存储控制流还原(sojson核心) |
| `merge-object` | 分散对象属性合并(obfuscator) |
| `prune-if-branch` | 修剪恒定if分支(花指令清除) |
| `split-sequence` | 逗号表达式拆分 |
| `delete-unused-var` | 删未使用变量 |
| `delete-unreachable-code` | 删不可达代码 |
| `delete-nested-blocks` | 删多余嵌套块 |
| `delete-illegal-return` | 删非法return |
| `delete-extra` | 删额外无用代码 |
| `split-assignment` | 拆分复合赋值 |
| `split-member-object` | 拆分成员对象 |
| `split-variable-declaration` | 拆分变量声明 |
| `lint-if-statement` | 规范if语句 |
| `check-func` | 函数有效性检查 |

### Python 解密能力

- `try_decompress()`: 自动选gzip/bz2/zlib/lzma解压
- `try_decode_base64()`: Base64解码
- `extract_base64_encoded()`: 从`base64.b64decode('XXX')`提取编码串
- `decrypt_nested()`: 递归解密嵌套层(Base64→解压→exec→...)

### 各插件解码流程

**sojson(V6):** parse→假执行解密→常量折叠→控制流还原→对象合并→if分支修剪→删未用变量
**sojsonv7:** 同V6+删非法return+多次eval
**obfuscator(10步):** 删非法return→对象合并→声明拆分→成员拆分→常量折叠→控制流还原→if处理→if修剪→赋值拆分→逗号拆分→删未用变量
**awsc:** 移除void→条件赋值展开→常量折叠→if修剪→变量删除
**jsconfuser(9步):** Anti-Tooling→Minify→Stack→不透明谓词→控制流→全局隐藏→字符串解压缩→字符串隐藏→重复字面量
**jjencode:** 识别6段→提取全局变量→解析$调用→字符串拼接→eval换console.log
**common:** 删不可达代码→删嵌套块→常量折叠→字符串计算


---

## 代码混淆/反混淆通用

### 混淆类型

| 类型 | 特征 | 平台 |
|------|------|------|
| Renaming | 变量改无意义名 | JS/Python/Java |
| String Encrypt | 字符串加密+运行时解密 | JS/Android |
| Control Flow | 代码结构打乱 | JS/Android |
| Dead Code | 插入无用代码 | 全平台 |
| Virtualization | 自定义VM执行 | JS/Android |

### 反混淆通用流程

1. 识别混淆类型 → 2. 字符串解密 → 3. 常量折叠 → 4. 死代码移除 → 5. 控制流还原 → 6. 命名还原 → 7. 格式化

### 各语言工具

| 语言 | 工具 |
|------|------|
| JS | Babel, js-beautify, de4js, decode_action |
| Python | uncompyle6, decompyle3 |
| Android | jadx, apktool |
| .NET | dnSpy, de4dot |
