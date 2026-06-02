1|---
2|name: algorithm-reverse
3|description: JS逆向算法还原统一技能。签名还原、混合加密拆解、Cookie/Header签名、JSVMP/VMP字节码还原、Wasm协议分析。统一闭环：请求→writer→builder→entry→source，Python复现。
4|author: 7452323 (converted from Private Gist)
5|version: "1.0"
6|tags:
7|  - js-reverse
8|  - algorithm-reduction
9|  - signature-crack
10|  - captcha
11|  - jsvmp
12|  - wasm
13|  - crypto
14|---
15|
16|# Algorithm Reverse — JS逆向算法还原统一技能
17|
18|## 技能协作链
19|
20|| 技能 | 关系 | 协作方式 |
21||------|------|----------|
22|| find-crypto-entry | 上游 | 入口定位结果传给本技能 |
23|| ast-deobfuscation | 前处理 | 解混淆后的可读代码便于分析算法层 |
24|| env-patch | 环境依赖 | 环境准备完成后才能复现签名 |
25|| jsvmp-reverse | 下游转交 | VMP题型识别后转交字节码层面 |
26|
27|## 统一闭环方法论
28|
29|所有题型统一走这条闭环，不先读混淆大文件：
30|
31|```text
32|最终请求 / 最终cookie / 最终verify / 最终WS帧
33|→ writer（写出点）
34|→ builder（构造函数）
35|→ entry（加密入口）
36|→ source（原始材料）
37|```
38|
39|### 核心原则
40|1. 先找最终写出点，不先读混淆大文件
41|2. 先存中间值，不先猜算法名
42|3. 先缩小执行范围，再补环境
43|4. 先证明输入输出边界，再决定是否整体迁移
44|
45|## 题型分类（6类）
46|
47|| 分类 | 难度 | 特征 | 产出 |
48||------|------|------|------|
49|| 纯时间戳/随机数签名 | ⭐ | 只有时间戳/随机数 | Python 30行 |
50|| 固定算法+固定 Key | ⭐⭐ | 单步确定，可迁移 | Python 50行 |
51|| 固定算法+动态 Key | ⭐⭐⭐ | 需从 JS 提取 Key | Python 50行+提取脚本 |
52|| 固定算法+混合加密 | ⭐⭐⭐⭐ | RSA/AES 多段组合 | Python 80行 |
53|| VMP 执行+参数自校验 | ⭐⭐⭐⭐⭐ | 依赖 VMP 引擎 | Node迁移，不Python |
54|| 风控/验证码参数组合 | ⭐⭐⭐⭐⭐ | 多参数+Wasm+Cookie | 多段式工程 |
55|
56|## 5层检查点
57|
58|| 检查点 | 通过条件 | 违反后果 |
59||--------|----------|----------|
60|| L1 写出点定位 | 找到修改 Document.cookie / localStorage / XMLHttpRequest.setRequestHeader 的代码位置 | 后续全错 |
61|| L2 输入输出确认 | 在 Node.js 中复现写出点的输入输出 | 环境错误 |
62|| L3 边界测试 | 使用伪造参数测试写出 | 功能验证 |
63|| L4 迁移正确性 | 将输出与真实请求比对 | 无法上线 |
64|| L5 异常处理 | 参数异常时能否提供有效输出 | 工程不可用 |
65|

## 实战提炼：签名算法逆向通用模式

### 从 ONE App 和 chatgpt2api 中提炼

| 实战来源 | 签名算法 | 特征 | 通用模式 |
|---------|---------|------|---------|
| ONE App (Flutter) | `MD5(MD5(ip.platform.ts.uk.uuid) + salt)` | 双层MD5 + 拼接 + salt | **拼接→哈希→加盐→再哈希** |
| chatgpt2api (ChatGPT) | PoW sentinel token | 服务端下发 challenge + 客户端计算 | **Challenge-Response 签名** |
| HttpCall (Wails) | Bearer token from config | 静态 token 认证 | **静态 Token + 前端注入** |

### 通用签名逆向框架

```python
# 当你遇到新 App 的签名算法时，按这个模板系统排查
SIGN_PATTERNS = {
    # 单层哈希
    "md5_single":     lambda params: md5(concat(params)),
    "sha1_single":    lambda params: sha1(concat(params)),
    "sha256_single":  lambda params: sha256(concat(params)),
    
    # 双层哈希（ONE App 模式）
    "md5_md5_salted": lambda params: md5(md5(concat(params)) + salt),
    "md5_sha1":       lambda params: sha1(md5(concat(params))),
    
    # 加盐变种
    "hmac":           lambda key, params: hmac.new(key, concat(params), hashlib.sha256).hexdigest(),
    "salted_concat":  lambda params: md5(concat(params) + salt),
    "salted_prefix":  lambda params: md5(salt + concat(params)),
    
    # Time-based
    "ts_md5":         lambda params, ts: md5(concat(params) + ts),
    "ts_hmac":        lambda key, params, ts: hmac.new(key, concat(params) + ts).hexdigest(),
}

def crack_sign(known_params: dict, known_sign: str):
    """穷举可能的签名算法，匹配已知 sign 值"""
    for algo_name, algo_fn in SIGN_PATTERNS.items():
        try:
            computed = algo_fn(**known_params)
            if computed == known_sign:
                return algo_name
        except:
            continue
    return None
```

### 通用 5 步法

```
1. 找拼接材料：从反编译/HAR/抓包中收集所有请求头参数
2. 找签名值：HAR 文件中的 sign/token/signature 字段
3. 猜算法：md5/sha1/hmac 三种最常见，优先试双层
4. 猜拼接顺序：按字母序、按参数定义顺序、按出现顺序
5. 验证：用已知数据跑一遍，匹配就确认
```
