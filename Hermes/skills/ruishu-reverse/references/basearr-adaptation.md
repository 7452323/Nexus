# basearr 适配方法

阶段 4: basearr 站点适配 (数据驱动)

- **输入**: sdenv 参考 basearr + keys (45 组) + codeUid
- **输出**: `buildBasearr(config, keys)` 函数
- **验证**: 纯算 Cookie T → HTTP 200

basearr 是 TLV 格式的字节数组 (154-166B), 是 Cookie T 加密链的源数据。每个站点的 basearr 结构大同小异, 但存在版本差异 (字段长度、flag 值、type 顺序等)。适配的核心是: 拿真实数据逐字节匹配, 不碰内层 VM。

---

## 数据驱动三步法

### 第一步: 采集参考数据

用 sdenv 运行目标站点, 获取真实 Cookie T, 解密还原 basearr:

```javascript
// 1. sdenv 运行 → 获取真实 Cookie T
const dom = await jsdomFromUrl(url, { userAgent: UA });
const cookieT = extractCookieT(dom);

// 2. 解密 Cookie T → basearr
const basearr = decryptCookieT(cookieT, keys);
// 例: [3,73,1,0,33,128,159,173,0,238,8,77,97,99,73,110,116,101,108,...]
```

### 第二步: 多 session 对比

至少采集 3-5 个 session 的 basearr, 逐字节对比, 区分固定值和动态值:

```javascript
for (let i = 0; i < maxLen; i++) {
    const vals = new Set(sessions.map(s => s[i]));
    if (vals.size > 1) {
        console.log(`位置 ${i}: ${sessions.map(s => s[i]).join(' ')}`);
    }
}
```

变化的字节只有四类来源: keys 派生、时间戳、随机数、session 相关。

### 第三步: 逐字段实现

对每个字节找到明确来源, 实现 build 函数。每实现一个 type, 用参考数据验证该段字节一致。

---

## TLV 格式

basearr 整体是 TLV (Type-Length-Value) 结构:

```
[type, length, ...payload, type, length, ...payload, ...]
```

最终结构示例 (len=166):

```
3, 73, [type=3 payload 73B]
10, N, [type=10 payload NB]
7, 12, [type=7 payload 12B]
0, 1, [0]
6, 16, [type=6 payload 16B]
2, 4, [type=2 payload 4B]
9, 5, [type=9 payload 5B]
13, 1, [0]
```

---

## 各 type 完整实现

### type=3 环境指纹

type=3 是最长的段 (65-73B), 包含浏览器环境指纹。大部分字段跨 session 固定。

```javascript
function buildType3(config) {
    return [
        1, config.maxTouchPoints||0, config.evalToStringLength||33, 128,
        ...numToNumarr4(crc32(config.userAgent)),
        config.platform.length, ...string2ascii(config.platform),
        ...numToNumarr4(config.execNumberByTime||1600),
        ...(config.randomAvg||[50,8]), 0, 0,
        ...numToNumarr4(16777216), ...numToNumarr4(0),
        ...numToNumarr2(config.innerHeight||768), ...numToNumarr2(config.innerWidth||1024),
        ...numToNumarr2(config.outerHeight||768), ...numToNumarr2(config.outerWidth||1024),
        ...new Array(8).fill(0), ...numToNumarr4(4), ...numToNumarr4(0),
        ...numToNumarr4(crc32(config.pathname.toUpperCase())),
        ...numToNumarr4(0),
    ];
}
```

字段说明:

| 偏移 | 长度 | 内容 | 来源 |
|------|------|------|------|
| 0 | 1 | 固定 1 | 常量 |
| 1 | 1 | maxTouchPoints | navigator.maxTouchPoints |
| 2 | 1 | eval.toString().length | 通常 33 |
| 3 | 1 | 固定 128 | 常量 |
| 4-7 | 4 | CRC32(UserAgent) | uuid() 函数 |
| 8 | 1 | platform 长度 | 自动 |
| 9+ | N | platform ASCII | "MacIntel" / "Win32" 等 |
| +0-3 | 4 | execNumberByTime | 3ms 循环计数 (~1600) |
| +4-5 | 2 | randomAvg | 98 个随机数均值/方差 |
| +6-7 | 2 | 固定 0,0 | 常量 |
| +8-11 | 4 | 16777216 | 常量 (0x01000000) |
| +12-15 | 4 | 0 | 常量 |
| +16-23 | 8 | innerH/W, outerH/W | 各 2B |
| +24-31 | 8 | 全零 | 常量 |
| +32-35 | 4 | 固定 4 | 检测标志 |
| +36-39 | 4 | 0 | 常量 |
| +40-43 | 4 | CRC32(pathname.toUpperCase()) | URL 路径 |
| +44-47 | 4 | 0 | 常量 |

注意: 部分版本 (len=166) 末尾多 8 个零字节 (`numToNumarr8(0)`)。

---

### type=10 时间+网络

type=10 包含时间戳、随机数和主机名。变化最多的段。

```javascript
function buildType10(config, keys) {
    const r2t = parseInt(ascii2string(keys[21]));
    const k19 = parseInt(ascii2string(keys[19]));
    const hostname = config.hostname.substring(0, 20);
    const random20 = Math.floor(Math.random() * 1048575);
    const currentTime = (config.currentTime || Date.now()) & 0xFFFFFFFF;
    return [
        3, 13,
        ...numToNumarr4(r2t + (config.runTime - config.startTime)),
        ...numToNumarr4(k19),
        ...numToNumarr8(random20 * 4294967296 + (currentTime >>> 0)),
        parseInt(ascii2string(keys[24])) || 4,
        hostname.length, ...string2ascii(hostname),
    ];
}
```

关键发现: `type=10[2..5]` 不是纯 r2mkaTime, 而是 `r2mkaTime + (runTime - startTime)`。

---

### type=7 标识

type=7 包含版本标志和 codeUid。

```javascript
function buildType7(config) {
    return [1, 0, 0, 0, 0, 0, 0, 0,
        ...numToNumarr2(config.flag || 2830),
        ...numToNumarr2(config.codeUid || 0)];
}
```

| 偏移 | 长度 | 内容 | 来源 |
|------|------|------|------|
| 0-7 | 8 | [1,0,0,0,0,0,0,0] | 常量 |
| 8-9 | 2 | flag | 站点特定: 2830, 2833, 3855, 4114 等 |
| 10-11 | 2 | codeUid | CRC32(funcCode) XOR CRC32(mainCodeSlice) & 0xFFFF |

**flag 值是站点适配的关键参数之一**, 必须从参考数据中读取。

---

### type=6 keys[22] AES 解密

type=6 包含 keys[22] 的解密数据。完整实现需要 BASESTR 解码 + AES-CBC 解密 + UTF-8 解码。

实际使用中, type=6 的值跨 session 变化较小。如果已有一次成功的参考数据, 可以直接复用 (短时间内有效)。长期运行需要完整实现 encryptMode2 + decode + decrypt 链路。

---

### type=2 会话映射 (数据驱动)

type=2 是 4 个字节, 看起来简单但陷阱最多。完整案例:

#### 9 步真实案例

1. **发现问题**: 硬编码后第一个 session 成功, 第二个失败
2. **尝试 rs-reverse 公式**: `idx*7+6` 公式依赖特定版本, 不适用
3. **切换到数据驱动**: 采集多个 session 的 (nsd, keys[29..32], type=2) 三元组
4. **采集 5 个 session**: 记录每组的 nsd, keys[29..32] 变量名, type=2 值
5. **发现规律**: 无论 nsd 如何变化, keys[29..32] 在 cp1 中的索引始终固定
6. **构建映射**: 固定值表 + cp1 索引映射
7. **实现**:

```javascript
function buildType2Simple(keys, nsd) {
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

8. **验证**: 5 个 session 全部 HTTP 200

---

### type=0 占位

```javascript
[0]  // 固定 1 字节
```

### type=9 电池+网络

```javascript
function buildType9(config) {
    const { connType } = config.connection || {};
    const { charging, chargingTime, level } = config.battery || {};
    const connIdx = ['bluetooth','cellular','ethernet','wifi','wimax'].indexOf(connType) + 1;
    let oper = 0;
    if (level) oper |= 2;
    if (charging) oper |= 1;
    if (connIdx !== undefined) oper |= 8;
    return [
        oper,
        Math.round((level || 1) * 100),
        ...numToNumarr2(chargingTime || 0),
        connIdx,
    ];
}
```

### type=13 占位

```javascript
[0]  // 固定 1 字节
```

---

## 最终组装 buildBasearr

```javascript
function buildBasearr(config, keys, nsd) {
    const type3 = buildType3(config);
    const type10 = buildType10(config, keys);
    const type7 = buildType7(config);
    const type6 = buildType6(keys, config);
    const type2 = buildType2(keys, nsd);
    const type9 = buildType9(config);

    return [
        3, type3.length, ...type3,
        10, type10.length, ...type10,
        7, type7.length, ...type7,
        0, 1, 0,                          // type=0, len=1, [0]
        6, type6.length, ...type6,
        2, type2.length, ...type2,
        9, type9.length, ...type9,
        13, 1, 0,                         // type=13, len=1, [0]
    ];
}
```

注意: type 顺序可能因版本而异。以参考数据为准。

---

## 站点适配清单

- [ ] 1. 获取 412 响应, 提取 nsd + cd + mainjs URL
- [ ] 2. 提取 keys (纯算或 sdenv)
- [ ] 3. 运行 Coder 计算 codeUid
- [ ] 4. sdenv 采集 3+ 个 session 的参考 basearr
- [ ] 5. 分析 TLV 结构, 确定 type 顺序
- [ ] 6. 多 session 对比, 标记每个字节的变化类型
- [ ] 7. 确定 flag 值 (type=7 的 [8..9])
- [ ] 8. 确定 type=2 的固定索引映射
- [ ] 9. 实现 buildBasearr, 与参考数据逐字节对比
- [ ] 10. 纯算 Cookie T → HTTP 200 验证
- [ ] 11. 连续 5+ 个 session 全部 200

---

## 常见坑

1. **flag 值不通用**: rs-reverse 默认 4114, 实际站点可能是 2830/2833/3855 等, 必须从参考数据读取
2. **type 顺序**: 不同版本的 type 顺序可能不同, 以 basearrParse 解析结果为准
3. **numToNumarr8(0) 尾部**: 部分版本 (len=166) type=3 末尾多 8 个零字节
4. **hostname 截断**: type=10 的 hostname 最多 20 字符
5. **pathname 大写**: CRC32 计算前必须 toUpperCase()
6. **时间差**: type=10[2..5] 是 r2mkaTime + runTime - startTime, 不是纯 r2mkaTime
7. **type=2 非固定**: 每个 session 的 nsd 不同导致 cp1 洗牌不同, 但索引映射关系固定
