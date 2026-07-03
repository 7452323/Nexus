---
category: reverse-engineering
name: algorithm-reverse
version: "1.0"
description: JS逆向算法还原统一技能。面向Web/JS逆向中的签名还原、混合加密拆解、Cookie/Header签名、JSVMP/VMP字节码还原、Wasm协议分析、验证码风控参数还原。统一闭环：请求→writer→builder→entry→source，覆盖6类题型分类、5层检查点、Python复现规范、验证码5线拆分与工程化产出。
tags:
  - js-reverse
  - algorithm-reduction
  - signature-crack
  - captcha
  - jsvmp
  - wasm
  - crypto
  - python-reproduction
---

# Algorithm Reverse — JS逆向算法还原统一技能

## 技能分工

本技能是JS逆向算法还原的**总入口**，与其他技能形成协作链：

| 技能 | 关系 | 协作方式 |
|------|------|----------|
| **find-crypto-entry** | 上游 | 入口定位结果传给本技能，本技能接收后进入算法分析 |
| **ast-deobfuscation** | 前处理 | 解混淆后的可读代码便于本技能分析算法层 |
| **env-patch** | 环境依赖 | 环境准备完成后本技能才能复现签名 |
| **jsvmp-reverse** | 下游转交 | VMP题型识别后转给它处理字节码层面 |
| **web-api-reverse** | 下游转交 | 如果目标是构建API兼容代理，转交它 |

**职责边界**：本技能负责从算法层面还原加密/签名逻辑，定位writer→builder→entry→source链路，产出Python复现代码。入口定位由find-crypto-entry完成，VMP字节码执行逻辑由jsvmp-reverse处理。

## 统一闭环方法论

所有题型统一走这条闭环，不先读混淆大文件：

```text
最终请求 / 最终cookie / 最终verify / 最终WS帧
→ writer（写出点）
→ builder（构造函数）
→ entry（加密入口）
→ source（原始材料）
```

### 核心原则

1. **先找最终写出点**，不先读混淆大文件
2. **先存中间值**，不先猜算法名
3. **先缩小执行范围**，再补环境
4. **先证明输入输出边界**，再决定是否整体迁移
5. **先把结果整理成可复用结构**，再继续做版本适配

### 工作流

1. **锁定最终写出点** — 从 `fetch` / `XMLHttpRequest.send` / `setRequestHeader` / `document.cookie` / `JSON.stringify` / verify提交点 / WS帧发送点切入
2. **记录5层检查点** — writer → builder输入 → 原始串 → 中间态 → 最终输出
3. **先恢复中间态，再恢复最终编码** — 尤其重要于JSVMP和复杂header家族
4. **只在必要时补环境** — 优先补到最小可运行边界
5. **把结果收敛到工程接口** — 分层函数、检查点集合、对照样本

## 实战工具补充

### CryptoJS Hook 法 - 最短路径拿加密参数

当目标使用CryptoJS时，无需静态分析算法，直接油猴Hook:
自动输出algorithm/mode/padding/key/iv。跳过定位writer->builder->entry链路。

**限制**: 仅限CryptoJS调用。

## 6类题型分类与决策树

### 难度分级

| 题型 | 难度 | 核心挑战 |
|------|------|----------|
| 1. 标准签名 | ★★ | 参数排序、编码一致性、原始串恢复 |
| 2. 混合加密 | ★★★ | 对称+非对称组合、密钥动态生成、分层拆解 |
| 3. Cookie/Header签名 | ★★ | 多参数联动、环境采集→builder→写出 |
| 4. JSVMP/VMP | ★★★★ | 字节码解释器、中间数组恢复、环境位串 |
| 5. Wasm协议 | ★★★★★ | 二进制模块反编译、协议边界、导出函数验证 |
| 6. 验证码风控 | ★★★★ | 图像+参数+环境+verify多线并行 |

### 1. 标准签名（★★）

**统一结构**：
```text
request params → normalize/stringify/sort → inject token/timestamp/cookie/ua → hash/encrypt → final sign
```

**识别信号**：输出长度规整、`md5/sha1/hmac`、原始串可恢复、请求字段关系稳定

**典型模式**：
- SHA1→MD5链式签名
- 页面态参数与JS纯算参数分离
- `token&t&appKey&data → MD5`
- 请求签名+响应解密组合

### 2. 混合加密（★★★）

**统一结构**：
```text
明文 → 对称加密(AES) → 再次包装 → 编码 → params
随机key → reverse/transform → RSA/SM2 → encSecKey/signature
```

**识别信号**：对称加密和非对称包装并存、`params + encSecKey`、返回包也可能要解密

**关键要点**：重点不是入口，而是"业务数据"和"密钥包装"分层

### 3. Cookie/Header签名（★★）

**统一结构**：
```text
环境采集 → builder → hash/encrypt/encode → document.cookie / header写入
```

**识别信号**：值写进 `document.cookie`、多个字段共同收口成最终header、中间字段承担不同角色

**最稳入口**：Hook `document.cookie` → 回栈看builder → 追环境采集层

### 4. JSVMP/VMP（★★★★）

**识别信号**：大数组、`for(;;)+switch`、寄存器式状态机、值逐位逐段构造

**共同策略**：
1. 不从文件头正推
2. 先找最终writer和最终返回值
3. 先恢复中间数组/中间对象/payload
4. 再恢复最终编码层

**典型特征**：
- 第一入口是VM入口函数（如 `window._webmsxyw()`），不是最终header串
- 多header需分开看（如 `X-s` 和 `X-S-Common`）
- 核心难点是多段数组、状态推进、时间戳/随机数/UA/环境材料如何进入位数组
- **转交**：字节码执行逻辑的深入分析转交 `jsvmp-reverse`

### 5. Wasm协议（★★★★★）

**识别信号**：`WebAssembly.instantiate`、protobuf/二进制payload、WebSocket分段交互

**优先顺序**：
1. 找加载点
2. 找Wasm URL
3. 看 `instance.exports`
4. 用固定输入验证输出
5. 再决定是否反编译

**关键要点**：先数包或确认message type、先拆协议线和页面线、不要一开始就把二进制题当"某个sign函数"

### 6. 验证码风控（★★★★）

**识别信号**：至少两段请求、图像+参数+环境并存、`collect/w/fs/pow_answer` 等字段

**永远先拆5条线**：初始化线 → 图像识别线 → 参数builder线 → 环境指纹线 → verify线

详见 [验证码5线拆分](#验证码5线拆分) 和 [references/captcha-families.md](./references/captcha-families.md)

### 决策路由

```
目标请求/cookie/verify/WS帧
  ├─ 输出长度规整 + hash算法 → 标准签名
  ├─ 对称+非对称并存 → 混合加密
  ├─ document.cookie / 多header收口 → Cookie/Header签名
  ├─ 大数组 + for(;;)+switch → JSVMP/VMP（转交jsvmp-reverse）
  ├─ WebAssembly.instantiate / 二进制 → Wasm协议
  └─ 图像+参数+环境+verify → 验证码风控
```

完整决策树见 [references/decision-tree.md](./references/decision-tree.md)

## 5层检查点体系

每题至少保存这5层检查点：

| 层 | 内容 | 作用 |
|----|------|------|
| **1. 请求层** | 最终URL / header / body / cookie / WS帧 | 确定参数完整性与编码 |
| **2. 算法层** | 加密算法识别、参与签名的字段和排序规则 | 算法还原的核心依据 |
| **3. 密钥层** | 密钥来源（硬编码/动态获取）、key/iv/salt | 判断密钥动态性与获取方式 |
| **4. 环境层** | window/document/navigator/指纹/collect | 环境依赖程度与补环境范围 |
| **5. 时序层** | 时间戳/序号/Nonce/token/challenge初值 | 可变参数的生成与绑定关系 |

### 检查点记录模板

```json
{
  "writer_checkpoint": "最终写出点与值",
  "builder_input": "喂给builder的完整对象",
  "raw_string": "原始串或原始payload",
  "intermediate": "中间数组/中间对象/编码前字节流",
  "final_output": "最终输出值"
}
```

## Python复现规范

从sign-crack提炼的标准化执行流程：

### 执行流程

```text
提取签名参数 → 定位加密函数 → 分析加密算法 → 生成Python复现代码 → 验证
```

### Step 1：提取签名参数

- 从HAR/抓包/用户描述中提取请求的URL、Headers、Body
- 识别动态签名参数（每次请求不同的：`sign`, `token`, `_signature`, `X-Sign` 等）
- 识别时间戳参数（`timestamp`, `t`, `_t`）
- 识别随机数参数（`nonce`, `random`）

### Step 2：定位加密函数

- 搜索签名参数名 → 回溯调用链 → 定位加密函数
- 常见入口：XHR拦截器(axios interceptors)、fetch wrapper、请求中间件
- 常见加密位置：请求发送前的hook、统一的sign工具函数

### Step 3：分析加密算法

识别加密类型并提取关键参数：

| 类型 | 模式 | 关键参数 |
|------|------|----------|
| MD5 | `sign = MD5(param1 + param2 + secret)` | 参与签名字段、排序规则、secret |
| HMAC-SHA256 | `sign = HMAC(secret, data)` | secret、data构造方式 |
| AES | `encrypted = AES.encrypt(data, key, iv)` | key来源、iv、模式、padding |
| RSA | `encrypted = RSA.encrypt(data, publicKey)` | publicKey来源、填充方式 |
| 自定义 | 分析具体逻辑 | 输入边界、中间态 |

### Step 4：生成Python复现代码

**标准签名模板**：
```python
import hashlib
import hmac
import time

def generate_sign(params: dict, secret: str) -> str:
    """标准签名：参数排序拼接 + MD5"""
    sorted_params = '&'.join(f'{k}={v}' for k, v in sorted(params.items()))
    timestamp = str(int(time.time() * 1000))
    raw = f'{sorted_params}&timestamp={timestamp}&secret={secret}'
    return hashlib.md5(raw.encode()).hexdigest()
```

**混合加密模板**：
```python
import base64
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad

def aes_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    """AES-CBC加密"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data, AES.block_size))

def rsa_encrypt(data: bytes, public_key_pem: str) -> bytes:
    """RSA加密"""
    key = RSA.import_key(public_key_pem)
    cipher = PKCS1_v1_5.new(key)
    return cipher.encrypt(data)

def hybrid_encrypt(plaintext: str, aes_key: bytes, aes_iv: bytes, rsa_pubkey: str) -> dict:
    """混合加密：AES加密数据 + RSA加密密钥"""
    encrypted_data = aes_encrypt(plaintext.encode(), aes_key, aes_iv)
    encrypted_key = rsa_encrypt(aes_key, rsa_pubkey)
    return {
        "params": base64.b64encode(encrypted_data).decode(),
        "encSecKey": encrypted_key.hex()
    }
```

**国密模板**：
```python
from gmssl import sm3, sm4, func

def sm3_hash(data: str) -> str:
    """SM3摘要"""
    return sm3.sm3_hash(func.bytes_to_list(data.encode()))

def sm4_encrypt(data: bytes, key: bytes) -> bytes:
    """SM4-ECB加密"""
    cipher = sm4.CryptSM4()
    cipher.set_key(key, sm4.SM4_ENCRYPT)
    return cipher.crypt_ecb(data)
```

### Step 5：验证

1. 固定时间戳和随机数
2. 用生成的代码计算签名
3. 与浏览器样本逐层对比（原始串→中间态→最终值）
4. 只比最终值通常不够，必须比对中间态

### 关键约束

- key/secret如果是动态获取的，必须说明获取方式
- 如果加密逻辑在混淆代码中，先调用 ast-deobfuscation 还原
- 如果涉及Webpack模块，先提取模块代码
- 如果涉及JSVMP/VMP，转交 jsvmp-reverse 处理字节码逻辑

详见 [references/python-reproduction.md](./references/python-reproduction.md)

## 验证码5线拆分

验证码题永远先拆5条线，每条线单独保存证据，不混写：

### 1. 初始化线

- 加载参数获取（captcha_id / appKey / token）
- SDK初始化
- challenge初值获取
- **产出**：初始化请求参数、challenge/load返回对象

### 2. 图像识别线

- 图片/题面获取
- 识别结果获取（距离/角度/坐标/文字）
- 轨迹生成
- **产出**：图片资源、识别结果、轨迹明文

### 3. 参数builder线

- 加密参数构造
- userAnswer / payload组装
- P1~P9 / w / fs 等字段生成
- **产出**：builder输入对象、builder输出对象

### 4. 环境指纹线

- 设备/浏览器指纹采集
- collect字段构造
- 环境位串生成
- **产出**：指纹对象、collect值

### 5. verify线

- 最终验证请求构造
- 所有线的输出汇合
- 提交验证
- **产出**：verify请求完整参数、响应结果

### 何时先修图像线 vs 参数线

| 先修图像线 | 先修参数线 |
|-----------|-----------|
| 参数层较薄 | `collect/signature/w/fs` 明显更重 |
| verify只校验距离/角度/坐标 | token/challenge/load返回对象没喂进去 |
| — | 环境值明显不一致 |

### 验证码统一检查点

每题至少保存8项：初始化请求参数 → 图片/challenge返回值 → 识别结果 → 轨迹明文 → builder输入对象 → builder输出对象 → 浏览器发送值 → 本地生成值

### Solver落地结构

```text
fetch_challenge → solve_image → build_track_or_answer → build_param_payload → verify
```

不要把图片识别、参数builder、环境模拟写成一个大函数。

详见 [references/captcha-families.md](./references/captcha-families.md)

## 工程化产出规范

### 推荐接口分层

```text
build_context(input)        — 构建上下文
→ build_payload(ctx)        — 构造payload
→ sign_payload(payload, ctx) — 签名/加密
→ validate(browser, local)  — 检查点对齐验证
→ final_output              — 最终输出
```

### 推荐项目层次

```text
context/          — 上下文构建
payload_builder/  — payload构造
crypto_or_vm/     — 算法层/VM层
env_patch/        — 环境补丁
validation/       — 检查点验证
service_or_sdk/   — 服务/SDK封装
```

### 每个案例最少沉淀

1. 最终请求或最终sink
2. 请求链闭环（writer→builder→entry→source）
3. 入口定位路径
4. 中间检查点
5. 本地代码骨架
6. 易错点

### 版本变化时优先排查

1. 输入边界有没有变化
2. 页面态参数或load返回对象有没有变化
3. 中间payload结构有没有变化
4. 只是编码层变了，还是builder逻辑变了
5. 环境字段是变成强校验了，还是仍然可写死

### 标签体系

`header-sign` `cookie-sign` `response-decrypt` `captcha` `vmp` `jsvmp` `wasm` `protobuf` `websocket` `env` `fingerprint` `ast` `solver` `sdk` `service`

详见 [references/engineering-maintenance.md](./references/engineering-maintenance.md)

## 常见陷阱（Pitfalls）

### 方法论陷阱

1. **先补环境，再找入口** — 应该先锁定writer和builder，环境问题等入口确认后再补
2. **只追求不报错** — 不报错不等于结果正确，必须用检查点逐层对齐
3. **只在最终值处打点** — 最终值对了中间可能不对，版本变化时中间态是诊断依据
4. **先读混淆大文件** — 应该从最终请求/sink倒推，不要从文件头正推
5. **先猜算法名** — 应该先存中间值，算法名是确认不是假设

### 算法陷阱

6. **简化JSVMP为"SM3+RC4+Base64"** — 真正难点是多段数组、状态推进、材料注入
7. **把腾讯题误写成"只靠图像和轨迹"** — collect和PoW同样是关键
8. **把网易盾只做图像不做w** — w参数构造才是真正的算法难点
9. **混淆加密类型** — MD5和HMAC-MD5不同，AES-CBC和AES-ECB不同

### 环境陷阱

10. **已经收缩成纯函数还去大补环境** — 如果目标已经是纯函数，不要升级任务
11. **一上来就补所有原型链和native外观** — 先让观察成本下降，保留证据再决定
12. **用Proxy补环境被toString检测** — 反调试检测是常见对抗手段

### 工程化陷阱

13. **把所有逻辑塞进一个大函数** — 应该按 context/payload/crypto/env/validation 分层
14. **没有留下可复用工件** — 每次研究都应沉淀检查点和代码骨架
15. **同站点多文章只保留一个最终答案** — 应记录思路差异（入口定位/AST解混/JSVMP结构/环境位串/算法骨架）

## 资源导航

- [references/algorithm-families.md](./references/algorithm-families.md) — 算法家族分类：标准签名、混合加密、Cookie/Header、JSVMP、Wasm、国密
- [references/captcha-families.md](./references/captcha-families.md) — 验证码家族分类：腾讯、极验、网易盾、百度、阿里、拼多多、V5、hCaptcha
- [references/decision-tree.md](./references/decision-tree.md) — 完整决策树：题型判断、阻塞点判断、请求链定位
- [references/python-reproduction.md](./references/python-reproduction.md) — Python复现规范：代码模板、验证流程、调试策略
- [references/engineering-maintenance.md](./references/engineering-maintenance.md) — 工程化维护：接口设计、版本适配、扩库记录
