---
category: reverse-engineering
name: ruishu-reverse
version: "1.0"
description: 瑞数(Ruishu/Rivers Security)反爬防护纯算逆向 — Cookie T 生成 + URL 后缀处理。触发词: 瑞数、ruishu、rivers security、412防护、Cookie T、动态JS反爬、anti-bot bypass。当用户遇到 412 状态码、需要绕过瑞数反爬、或提到 $_ts.cd / $_ts.nsd 时, 必须使用此技能。
tags: [reverse-engineering, anti-bot, ruishu, cookie-generation, encryption]
---

# 瑞数反爬纯算逆向 Skill

> 目标: 读完本文档, 独立完成瑞数保护站点的 Cookie T 纯算生成 + URL 后缀处理。
> 已验证: 9+ 站点 HTTP 200。

---

## 决策树

拿到目标 URL 后, 按此流程选择方案:

```
1. HTTP GET 目标 URL
   ├── 非 412 → 不是瑞数防护, 退出
   └── 412 + $_ts.cd + $_ts.nsd → 确认瑞数
       │
2. 是否只需 GET 请求?
   ├── 是 (80%场景) → 纯算方案 [阶段 0→5]
   └── 需要 POST
       │
3. POST 是否需要 URL 后缀?
   ├── 不需要 (99%站点) → 纯算 Cookie + 普通 POST [阶段 0→5]
   └── 需要后缀
       ├── 稳定方案 → JsRpc (浏览器注入, 通杀)
       └── 轻量方案 → sdenv VM 内 XHR (单次POST后需重建实例)
```

**快速验证是否需要后缀**: 纯算 Cookie T + 普通 POST → 200 则不需要, 400/412 则需要。

---

## 6 阶段总览

| 阶段 | 输入 | 输出 | 验证标准 | 通用? |
|------|------|------|---------|-------|
| **0 侦察** | 目标 URL | 412 HTML + mainjs + Cookie S + sdenv 参考数据 | sdenv Cookie → 200 | 通用 |
| **1 加密链** | sdenv Cookie T + keys | `generateCookie(basearr, keys) → Cookie T` | sdenv basearr + 纯算加密 → 200 | **通用, 一次性** |
| **2 密钥提取** | $_ts.cd | keys[0..44] (45 组) | keys 和 sdenv 提取的一致 | **通用, 一次性** |
| **3 Coder** | mainjs + nsd + cd | eval 代码 + codeUid + functionsNameSort | eval 代码逐字节一致 | **通用, 一次性** |
| **4 basearr** | 参考数据 + keys | `buildBasearr(config, keys) → basearr` | 纯算全链路 → 200 | **每站点 ~1h** |
| **5 端到端** | 全部 | 纯算 HTTP GET → 200 | 连续 3+ 次 200 | 组装即可 |

**执行顺序**: 严格 0 → 1 → 2 → 3 → 4 → 5, 每步验证通过后再进下一步。

---

## 方法论: 数据驱动 vs AST 分析

### 数据驱动 (用于 Cookie T / basearr — 最重要!)

**核心**: 用 sdenv 采集 3-5 组真实数据 → 逐字节对比 → 找到每个字节的来源。**绝对不要去读内层 VM 代码** (740 个 state, 三层嵌套 — 这是陷阱)。

```
采集 5 session → 每个 TLV 字段拆开 → 逐字节标注:
  固定 (所有 session 相同)       → 硬编码
  来自 keys (匹配 keys[N])      → 动态提取
  时间相关 (有规律变化)          → 找公式
  随机 (无规律)                 → Math.random
  未知                         → 需更多数据或更深分析
```

**真实经验**: 花 2 天读 VM 代码完全浪费。转向数据驱动后, 1 天内解决所有问题。

### AST 分析 (用于 URL 后缀 / eval code 函数)

**核心**: eval code 是合法 JS, 用 acorn 解析 AST → 建立 rt[N] 函数映射 → 递归追踪调用链 → 提取核心算法。几小时完成手工需要数周的工作量。

### 方法选择表

| 目标在哪一层? | 用什么方法 |
|--------------|----------|
| eval code JS 函数 | AST (精确高效) |
| basearr 数据结构 | 数据驱动 (快速可靠) |
| r2mKa VM 字节码 | AST 提取 opcode + 自动反汇编 |
| 运行时动态值 (时间戳等) | sdenv 采集 |

---

## 加密管线 (7 步)

```
basearr (154-166B)
  → Huffman 编码 (~118B)
  → 前 16 字节 XOR keys[2][0:15]
  → AES-128-CBC (key=keys[17], IV=全零, PKCS7)  → ~128B
  → 拼 packet: [2, 8, r2mkaTime(4B), now(4B), 48, keys[2](48B), lenEnc, cipher]
  → CRC32 → [crc(4B), packet]  → ~193B
  → AES-128-CBC (key=keys[16], IV=随机16B, PKCS7)  → ~224B
  → 自定义 Base64 → "0" + 299 字符
```

详见 [references/encryption-pipeline.md](references/encryption-pipeline.md)

---

## 弯路警告 (来自真实踩坑经验)

| 弯路 | 代价 | 正确做法 |
|------|------|---------|
| 反编译内层 VM 理解 basearr | **2 天浪费** | 数据驱动: 5 session 采集, 10 分钟解决 |
| 照搬 rs-reverse 公式 (idx*7+6 等) | **1 天白费** | 数据驱动: 公式是版本特定的, 不通用 |
| 补环境跑 eval 代码 | document.all 需 C++ Addon | Coder 重写 mainjs 逻辑 |
| 硬编码 type=2 值 | 换 session 就错 | cp1 索引→值映射 (5 session 反推) |
| 跳过混合验证直接做 basearr | 400 了不知道哪步错 | 先 sdenv basearr + 纯算加密 = 200, 证明加密正确 |
| 运行时栈追踪反推 opcode 语义 | 80B/天效率 | AST 静态提取: 400B/小时 (效率 80 倍) |

---

## 排错指南

### 返回 412 (Cookie 未被接受)

1. Cookie 名是否正确? → `keys[7].split(';')[5] + 'T'`, 不是硬编码
2. Cookie S 是否一起发了? → 必须同时带 S 和 T
3. Cookie T 格式? → 必须以 "0" 开头
4. 时间是否过期? → Cookie 有效期通常 < 5 分钟, 检查 nonce 时间戳
5. cd 和 Cookie S 是否配套? → 必须来自同一个 412 响应

### 返回 400 (Cookie 格式/内容错误)

1. 加密链是否通过混合验证? → 先用 sdenv basearr + 纯算加密验证
2. basearr 长度是否匹配? → 对比 sdenv 参考 (通常 154-166B)
3. basearr TLV 是否有缺失字段? → 逐字段对比参考
4. keys 提取是否正确? → keys[0] 应为 "64", keys[2] 应为 48B
5. POST 是否需要 URL 后缀? → 先用 sdenv POST 测试确认

### Coder 输出不匹配

1. 逐字节对比找第一个差异位置
2. 常见 6 个 bug:
   - opmate 数量: 5 个命名 + 1 个无名 = 6 (不是 7)
   - gren(0) 用**全局** opmate, 不是局部
   - var 声明: 用 mate index 1 (不是 2)
   - while(1): 也用**全局** opmate
   - _ifElse: start 变量在 for 中被修改, else 分支用修改后的 start
   - debugger: 每个 gren 段重建 PRNG(seed=nsd), posis 跨段累积
3. 差 ~180 字符 → 大概率 debugger 对齐问题

### Keys 提取失败

1. keys[0] 是否 = "64" (ASCII [0x36, 0x34])?
2. keys.length < 45 → XOR 偏移计算错误
3. keys[29..32] 不是各 4B → 结构异常, 需实现 r2mka runTask

### type=2 值不匹配

1. **不要硬编码!** type=2 依赖 nsd → cp1 洗牌结果
2. 采集 5 session, 记录 keys[29..32] 变量名 + type=2 值
3. 在 cp1=grenKeys(keynameNum, nsd) 中查变量名索引
4. 建立 cp1_index → value 映射表 (映射对同一 mainjs 版本固定)

---

## 通用常量速查

```javascript
// PRNG (所有版本通用)
seed = 15679 * (seed & 0xFFFF) + 2531011

// Huffman 权重 (所有版本通用)
byte=0 → weight=45, byte=255 → weight=6, 其余 → weight=1

// AES-128-CBC
外层: key=keys[16], IV=随机16B     内层: key=keys[17], IV=全零16B

// CRC32 多项式
0xEDB88320

// 自定义 Base64 字母表 (所有版本通用)
'qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d'

// BASESTR (cd 解码用, 比 Base64 字母表多 24 个字符)
'qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d{}|~ !#$%()*+,-;=?@[]^'

// getLine 乘数 (mainjs op88)
55295

// 变量名字符集
'_$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

// _ifElse 二叉搜索步长表
[4, 16, 64, 256, 1024, 4096, 16384, 65536]

// Cookie 名
keys[7].split(';')[5] + 'T'

// URL 后缀参数名
keys[7].split(';')[1]
```

### 关键 Keys 含义

| key | 长度 | 含义 | 用途 |
|-----|------|------|------|
| keys[2] | 48B | KEYS48 | XOR 前 16B + packet 内嵌全部 48B |
| keys[7] | 变长 | 配置串 (分号分隔) | Cookie 名 `[5]+'T'`, 后缀参数名 `[1]` |
| keys[16] | 16B | KEY2 | 外层 AES 密钥 |
| keys[17] | 16B | KEY1 | 内层 AES 密钥 |
| keys[19] | 变长 | 时间戳串 | type=10[6..9] |
| keys[21] | 变长 | r2mkaTime 串 | nonce 时间 |
| keys[22] | 变长 | 加密数据 | type=6 AES 解密 |
| keys[24-26] | 变长 | 数值串 | type=10 参数 |
| keys[29-32] | 各 4B | 变量名 | type=2 映射 (cp1 索引→值) |
| keys[33-34] | 变长 | 数值串 | codeUid 计算参数 |

---

## 变量名变化警告

**瑞数的变量名不是固定的!** nsd 不同 → grenKeys(918, nsd) 洗牌不同 → eval 代码中所有变量名变化。

hook 定位必须用结构特征, 不用变量名:
```javascript
// ❌ 错误: 用变量名 (下次就变了)
const target = 'function _$hr(){var _$jZ=[324];';

// ✅ 正确: 用结构特征 (永远不变)
const statePattern = /function\s+(_\$\w+)\(\)\{var\s+(_\$\w+)=\[324\]/;
// ✅ 正确: 用代码长度
if (code.length > 250000) { /* 这是 eval 代码 */ }
// ✅ 正确: 用常量特征
if (code.includes('15679') && code.includes('2531011')) { /* 找到 PRNG */ }
```

---

## URL 后缀方案

99% 的瑞数站点 POST 请求不需要 URL suffix, 只需 Cookie S + T。

需要后缀时的两种方案:

### JsRpc 方案 (推荐, 通用)

通过远程调用浏览器中已加载的瑞数 JS 环境, 直接获取生成结果。环境补丁和注入方法详见 **env-patch** 技能。

- 优点: 通用性强, 适用于所有站点
- 缺点: 依赖浏览器实例

### sdenv VM 内 XHR 方案

利用 sdenv 环境执行瑞数 JS, 在 VM 内部发起 XHR 请求。环境问题详见 **env-patch** 技能。

- 优点: 无需浏览器, 可脚本化
- 缺点: 每个 sdenv 实例仅能发一次 POST 请求, 需要频繁初始化新实例

### Suffix 结构 (参考)

88B 变体 (URL 无 query):
```
[0-3]   4B  nonce (随机)
[4]     1B  flag = 1
[5]     1B  0x6a (站点标记)
[6-54]  49B session (Cookie S 解密)
[55]    1B  marker (0x20=无search / 0x40=有search)
[56-87] 32B sig32 (行为统计编码)
```

120B 变体: 88B + 32B searchSig (SHA-1 签名)

编码: `"0" + URLSafeBase64(bytes)`, 替换 `+→.`, `/→_`, 去 padding

参数名: `keys[7].split(';')[1]`

---

## 站点适配 Checklist

- [ ] 修改 HOST / PORT / PATH
- [ ] sdenv 跑通 → 200 (确认是标准瑞数版本)
- [ ] 混合验证通过 (sdenv basearr + 纯算加密 → 200)
- [ ] flag 值: 从参考 basearr type=7 的 [8..9] 读取
- [ ] type=9 格式: payload 是 2B `[8,0]` 还是 5B?
- [ ] type=3 结构: 逐字节对比
- [ ] type=2 映射: 5+ session 采集, 建立 cp1 索引→值映射
- [ ] Cookie 名后缀: 'T' 还是 'P'?
- [ ] hasDebug: 观察 eval 代码是否有 debugger 语句
- [ ] keynameNum: 从 mainjs 正则提取 (通常 918)
- [ ] 端到端验证: 连续 3+ 次 200

---

## 工具依赖

| 工具 | 安装 | 用途 | 阶段 |
|------|------|------|------|
| Node.js crypto/http | 内置 | AES 加解密, HTTP 请求 | 全部 |
| sdenv | `npx pnpm add sdenv` | 参考数据采集, VM 内 XHR | 0, 4 |
| js-beautify | `npm i js-beautify` | 格式化 mainjs (可选) | 3 |
| acorn + acorn-walk | `npm i acorn acorn-walk` | AST 分析 (后缀逆向) | 6 |

**注意**: npm 11.x + Node 24 有依赖解析死循环 bug, 安装 sdenv **必须**用 pnpm。

---

## 技能分工

本技能专注于瑞数 Cookie T 的纯算生成流程。相关技能的协作关系:

| 需求 | 引用技能 | 说明 |
|------|---------|------|
| VM 通用方法 (反编译、opcode 分析、字节码追踪) | **jsvmp-reverse** | 瑞数使用三层嵌套 VM, 通用 VM 逆向方法引用 jsvmp-reverse 技能 |
| 环境补丁 (sdenv 配置、DOM 模拟、document.all 等) | **env-patch** | JsRpc 浏览器注入和 sdenv 环境问题的解决方案引用 env-patch 技能 |

**调用时机**:
- 遇到 r2mKa VM 字节码层面的问题 → 引用 jsvmp-reverse
- 遇到 sdenv 环境报错或 DOM 补全问题 → 引用 env-patch
- Cookie T 生成、加密链、keys 提取、Coder 重写、basearr 适配 → 本技能独立处理

---

## 参考文件

| 文件 | 内容 |
|------|------|
| [references/encryption-pipeline.md](references/encryption-pipeline.md) | 加密管线 7 步详解: Huffman/AES/CRC32/Base64 完整实现 |
| [references/key-extraction.md](references/key-extraction.md) | 密钥提取: cd 解码 + XOR 偏移推导 + 45 组 keys 提取 |
| [references/coder-rewrite.md](references/coder-rewrite.md) | Coder 重写: 外层 VM 重写 + 75+55 opcode + 调试过程 |
| [references/basearr-adaptation.md](references/basearr-adaptation.md) | basearr 适配: TLV 结构 + 每个 type 实现 + 数据驱动案例 |
