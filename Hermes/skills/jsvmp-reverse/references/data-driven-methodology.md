# 数据驱动逆向方法论

## 核心思想

**不理解 VM 内部，只对比输出差异，从差异反推来源。**

当 VM 指令集过于复杂 (如 740 个 state 的三层嵌套)、或者只需要还原最终输出时，数据驱动是最快最可靠的路线。

**真实验证**: 花 2 天读 VM 代码完全浪费，转向数据驱动后 1 天内解决所有问题。

---

## 适用条件

满足以下**任一**即可选择数据驱动:

1. VM 指令集不公开或过于复杂
2. 有可重复执行环境 (sdenv / 浏览器 / 补环境可跑)
3. 输出格式相对固定 (Cookie / Header / 固定长度字节流)
4. 只需还原最终输出，不需要理解全部逻辑

---

## 四步流程

### Step 1: 样本采集 (3-5 组)

**关键原则**: 必须在**同一个 session** 中采集全套配套数据。分开采集的话变量名/密钥对不上。

```javascript
// 一次采集流程
const session = {
    // 1. 输入参数
    nsd: extractNsd(html),           // 种子值
    cd: extractCd(html),             // 配置数据
    cookieS: extractCookieS(response), // 服务端 Cookie

    // 2. 中间数据
    keys: extractKeys(cd),           // 密钥数组
    evalCode: captureEvalCode(),     // VM 加载的代码

    // 3. 输出数据
    cookieT: extractCookieT(dom),    // 目标 Cookie
    basearr: decryptToBasearr(cookieT, keys), // 加密前原始数据
    timestamp: Date.now(),
};
```

**采集工具**:

| 环境 | 工具 | 说明 |
|------|------|------|
| sdenv | `npx pnpm add sdenv` | Node.js 环境模拟，支持 VM 内 XHR |
| 浏览器 | Chrome DevTools | 断点 + console 导出 |
| 补环境 | jsdom + 自定义 mock | 轻量级环境模拟 |

**采集文件结构**:

```
captured/
├── session_1.json     nsd + cd + Cookie S/T + basearr + 时间戳
├── session_2.json     ...
├── session_3.json     ...
├── eval_code.js       VM 代码 (变量名与 session 配套)
└── mainjs.js          主脚本 (静态, 可单独下载)
```

### Step 2: 逐字节对比

对 3-5 组样本的输出进行逐字节对比，区分固定位和变化位:

```javascript
function compareSessions(sessions) {
    const maxLen = Math.max(...sessions.map(s => s.basearr.length));
    const analysis = [];

    for (let i = 0; i < maxLen; i++) {
        const vals = new Set(sessions.map(s => s.basearr[i]));
        const type = vals.size === 1 ? 'FIXED' :
                     vals.size <= 3 ? 'SEMI_FIXED' : 'DYNAMIC';

        analysis.push({
            offset: i,
            values: sessions.map(s => s.basearr[i]),
            type: type
        });

        if (vals.size > 1) {
            console.log(`位置 ${i} [${type}]: ${sessions.map(s => s.basearr[i]).join(' ')}`);
        }
    }
    return analysis;
}
```

**字节变化分类**:

| 分类 | 特征 | 来源 | 处理方式 |
|------|------|------|---------|
| **固定** | 所有 session 相同 | 常量/硬编码 | 直接硬编码 |
| **keys 派生** | 匹配 keys[N] | 密钥提取 | 动态提取 keys |
| **时间相关** | 有规律变化 | 时间戳 | 找公式 |
| **随机** | 无规律 | Math.random | 随机生成 |
| **session 相关** | 同 session 内固定 | 服务端数据 | 从 Cookie S 提取 |
| **未知** | 无法解释 | 需更深分析 | 采更多数据或用 AST |

### Step 3: 来源追溯

对每个变化字节，建立 "输入 → 输出" 的映射关系:

```javascript
function traceField(field, sessions) {
    // 1. 检查是否来自 keys
    for (let ki = 0; ki < 45; ki++) {
        for (const s of sessions) {
            if (arraysEqual(field.value(s), s.keys[ki])) {
                return { source: 'keys', index: ki };
            }
        }
    }

    // 2. 检查是否是时间戳的变换
    for (const s of sessions) {
        const ts = Math.floor(s.timestamp / 1000);
        const bytes = numToNumarr4(ts);
        if (arraysEqual(field.value(s), bytes)) {
            return { source: 'timestamp', transform: 'seconds' };
        }
    }

    // 3. 检查是否是 keys + 时间偏移的组合
    // ... 根据具体场景扩展

    return { source: 'unknown' };
}
```

**常见来源模式**:

| 模式 | 示例 | 说明 |
|------|------|------|
| keys 直接使用 | `keys[16]` → 外层 AES 密钥 | 直接从 keys 读取 |
| keys 计算 | `parseInt(ascii2string(keys[21]))` → 时间偏移 | keys 值经简单转换 |
| keys + 常量 | `keys[2][0:15]` XOR 前 16 字节 | keys 的部分字节参与计算 |
| CRC32(环境值) | `CRC32(userAgent)` → 指纹 | 环境值的哈希 |
| 时间戳 + 随机 | `random20 * 2^32 + currentTime` | 混合值 |
| 间接映射 | `cp1.indexOf(varName) → VALUES[idx]` | 通过中间表查值 |

### Step 4: Python/JS 复现

逐 type 实现 build 函数，每实现一个 type 立即验证:

```javascript
// 1. 实现 buildType3
const type3 = buildType3(config);
const refType3 = referenceBasearr.slice(type3Start, type3End);
assertArraysEqual(type3, refType3, 'type3');

// 2. 实现 buildType10
const type10 = buildType10(config, keys);
const refType10 = referenceBasearr.slice(type10Start, type10End);
assertArraysEqual(type10, refType10, 'type10');

// ... 逐 type 验证

// 3. 组装完整 basearr
const basearr = buildBasearr(config, keys);
assertArraysEqual(basearr, referenceBasearr, 'full basearr');

// 4. 端到端验证 (加密 + HTTP 请求)
const cookieT = generateCookie(basearr, keys);
const response = await httpGet(url, cookieS, cookieT);
assert(response.status === 200, 'HTTP ' + response.status);
```

---

## TLV 格式分析

许多 VM 输出是 TLV (Type-Length-Value) 格式的字节数组。

### TLV 结构

```
[type, length, ...payload, type, length, ...payload, ...]
```

### 解析器

```javascript
function parseTLV(data) {
    const fields = [];
    let pos = 0;
    while (pos < data.length) {
        const type = data[pos++];
        const len = data[pos++];
        const payload = data.slice(pos, pos + len);
        fields.push({ type, length: len, payload, offset: pos - 2 });
        pos += len;
    }
    return fields;
}
```

### 多 session TLV 对比

```javascript
function compareTLVAcrossSessions(sessions) {
    const parsed = sessions.map(s => parseTLV(s.basearr));
    const types = [...new Set(parsed.flat().map(f => f.type))];

    for (const t of types) {
        console.log(`\n=== Type ${t} ===`);
        const fields = parsed.map(p => p.find(f => f.type === t));
        fields.forEach((f, i) => {
            if (f) console.log(`  Session ${i}: len=${f.length} payload=[${f.payload.join(',')}]`);
        });

        // 对比 payload 中的变化字节
        const maxLen = Math.max(...fields.filter(Boolean).map(f => f.payload.length));
        for (let j = 0; j < maxLen; j++) {
            const vals = new Set(fields.filter(Boolean).map(f => f.payload[j]));
            if (vals.size > 1) {
                console.log(`  [${j}] VARIES: ${fields.filter(Boolean).map(f => f.payload[j]).join(' ')}`);
            }
        }
    }
}
```

### 真实案例: 瑞数 basearr 结构

```
type=3  (73B)  环境指纹: UA CRC32, platform, 窗口大小, pathname CRC32
type=10 (N B)  时间+网络: r2mkaTime, 时间戳, hostname
type=7  (12B)  标识: flag, codeUid
type=0  (1 B)  占位: 固定 [0]
type=6  (16B)  加密数据: keys[22] AES 解密结果
type=2  (4 B)  会话映射: cp1 索引 → VALUES 映射
type=9  (5 B)  电池+网络: 充电状态, 网络类型
type=13 (1 B)  占位: 固定 [0]
```

---

## 数据驱动的典型模式

### 模式 1: 固定值硬编码

**识别**: 所有 session 中同一位置始终相同。

```javascript
// 分析结果: 所有 session type=0 都是 [0]
function buildType0() { return [0]; }
```

### 模式 2: keys 直接映射

**识别**: 字段值与某个 keys[N] 完全匹配。

```javascript
// 分析结果: type=6 payload 包含 keys[16] 的 AES 解密结果
function buildType6(keys) {
    // ... AES 解密 keys[22]
}
```

### 模式 3: 环境指纹

**识别**: 字段值与浏览器环境参数相关 (UA, platform, 窗口大小)。

```javascript
// 分析结果: type=3 包含 CRC32(userAgent), platform, innerWidth/Height
function buildType3(config) {
    return [
        1, config.maxTouchPoints || 0,
        config.evalToStringLength || 33,
        128,
        ...numToNumarr4(crc32(config.userAgent)),
        config.platform.length, ...string2ascii(config.platform),
        // ... 更多字段
    ];
}
```

### 模式 4: 时间戳变换

**识别**: 字段值与时间戳有明确数学关系。

```javascript
// 分析结果: type=10[2..5] = r2mkaTime + (runTime - startTime)
// 不是纯 r2mkaTime! 有个时间差偏移
function buildType10Timestamp(keys, config) {
    const r2t = parseInt(ascii2string(keys[21]));
    return numToNumarr4(r2t + (config.runTime - config.startTime));
}
```

### 模式 5: 间接映射 (最难)

**识别**: 字段值通过中间映射表派生，映射关系跨 session 固定。

**真实案例: type=2 的 9 步推导**:

1. 首次采集: `type2 = [103, 181, 101, 224]` → 看起来固定
2. 硬编码 → 第二个 session 失败
3. 尝试套用公式 → 公式是版本特定的，不适用
4. 切换数据驱动: 采集 5 个 session
5. 发现: `keys[29..32]` 在 cp1 (918 个变量名) 中的索引始终固定
6. 建立: cp1_index → VALUES 映射表
7. 实现: `cp1.indexOf(ascii2string(keys[ki])) → VALUES[idx]`
8. 验证: 5 个 session 全部通过

```javascript
function buildType2(keys, nsd) {
    const cp1 = grenKeys(918, nsd);
    const VALUES = [103,0,102,203,224,181,108,240,101,126,
                    103,11,102,203,225,181,208,180,100,127];
    const result = [];
    for (const ki of [29, 30, 31, 32]) {
        const varName = ascii2string(keys[ki]);
        const idx = cp1.indexOf(varName);
        result.push(VALUES[idx]);
    }
    return result;
}
```

---

## 混合验证策略

在纯算实现之前，先用参考中间数据 + 纯算后段验证:

```
验证金字塔:
  纯算全链路 → HTTP 200         (最终目标)
    ↑
  纯算 basearr + 纯算加密 → Cookie T   (完整验证)
    ↑
  sdenv basearr + 纯算加密 → HTTP 200   (混合验证，证明加密正确)
    ↑
  纯算 type3 + 参考其余 → basearr 匹配   (单 type 验证)
    ↑
  纯算 keys → 与 sdenv keys 对比        (密钥验证)
```

**关键**: 不要跳过混合验证直接做 basearr。400 了不知道哪步错。

---

## 采集辅助函数

```javascript
// 数字转字节数组
function numToNumarr4(n) {
    return [(n>>24)&255, (n>>16)&255, (n>>8)&255, n&255];
}
function numToNumarr2(n) {
    return [n >> 8, n & 255];
}

// 字符串与 ASCII 互转
function string2ascii(str) { return str.split('').map(c => c.charCodeAt(0)); }
function ascii2string(arr) { return String.fromCharCode(...arr); }

// CRC32
const CRC_T = new Uint32Array(256);
for (let i = 0; i < 256; i++) {
    let c = i;
    for (let j = 0; j < 8; j++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    CRC_T[i] = c;
}
function crc32(d) {
    if (typeof d === 'string') d = unescape(encodeURIComponent(d)).split('').map(c => c.charCodeAt(0));
    let c = ~0;
    for (let i = 0; i < d.length; i++) c = (c >>> 8) ^ CRC_T[(c ^ d[i]) & 0xFF];
    return (~c) >>> 0;
}

// 逐字节对比找第一个差异
function findFirstDiff(generated, reference) {
    for (let i = 0; i < Math.min(generated.length, reference.length); i++) {
        if (generated[i] !== reference[i]) {
            console.log('差异 @' + i + ':', JSON.stringify(generated.slice(i, i+20)));
            console.log('参考:', JSON.stringify(reference.slice(i, i+20)));
            return i;
        }
    }
    if (generated.length !== reference.length) {
        console.log('长度不同: gen=' + generated.length + ' ref=' + reference.length);
    }
    return -1;
}
```

---

## 常见陷阱

1. **不配套采集**: nsd / keys / basearr 必须同一 session 内采集。分开采集 → 变量名对不上
2. **硬编码动态值**: 看起来固定 → 换 session 就错。始终用 3+ session 验证
3. **套用版本特定公式**: `idx*7+6` 之类的公式依赖特定版本，不通用
4. **跳过混合验证**: 直接全链路 → 400 了不知道哪步错
5. **假设字段顺序固定**: 不同版本的 type 顺序可能不同，每次用 TLV 解析器验证
6. **忽略 hostname 截断**: 部分字段有长度限制 (如 hostname 最多 20 字符)
7. **大小写不一致**: CRC32 计算前可能需要 toUpperCase() / toLowerCase()
8. **时间差偏移**: 时间戳字段可能不是纯时间戳，而是 "基准时间 + 运行时间差"
