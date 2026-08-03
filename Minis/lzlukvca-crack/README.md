# 黄豆短剧 (lzlukvca.cc) 金币播放破解

> 基于 main.dart.js (6.7MB) 静态逆向 + AES-256 自定义实现分析  
> 分析日期: 2026-08-04

## 目标

绕过 lzlukvca.cc 的金币扣费机制，免费播放需要金币的短剧。

## 抓包分析成果

| 项 | 值 |
|----|----|
| 主域名 | lzlukvca.cc |
| API 域名池 | hddj05.com / hddj06.com / hddj07.com / hdmgdj.com / fsbd.yskkkkb.me |
| 备用 Cloudflare 边缘 | hvthtcpa.top / psfxhhox.top / qicuknlj.top / sxqirtho.top |
| Flutter 渲染器 | HTML (renderer=html) |
| CanvasKit | 本地化 (useLocalCanvasKit=true) |
| Token 存储 | localStorage `flutter.default:app_token_info` (AES加密) |

## 关键 API 端点

```
POST /api/drama/play     - 播放（核心破解点）
POST /api/drama/detail   - 剧详情
POST /api/drama/list     - 列表
POST /api/drama/search   - 搜索
POST /api/drama/urge     - 催更
POST /api/drama/wish     - 许愿
GET  /api/drama/nav      - 导航
GET  /api/user/info      - 用户信息
GET  /api/user/vip       - VIP状态
POST /api/pay/vip        - VIP购买
POST /api/pay/recharge   - 充值
POST /api/task/list      - 任务列表
POST /api/task/claim     - 任务奖励
```

## 金币相关响应字段（从 main.dart.js 提取）

| 字段 | 含义 | 爆破值 |
|------|------|--------|
| `coin_consume_amount` | 本集消费金币 | 0 |
| `coin_balance_before` | 扣前余额 | 999999 |
| `coin_balance_after` | 扣后余额 | 999999 |
| `coin_quantity` | 当前金币 | 999999 |
| `total_coin` | 总金币 | 999999 |
| `today_coin` | 今日获得 | 999999 |
| `max_reward_coin` | 最大奖励 | 999999 |
| `pending_coin` | 待领取 | 0 |
| `cost_gold` | 金币价格 | 0 |
| `consume_amount` | 消费金额 | 0 |
| `amount` | 数量 | 0 |
| `is_free` | 是否免费 | 1 |
| `is_coin` | 是否金币 | 0 |
| `need_coin` | 需要金币 | 0 |
| `is_locked` | 是否锁定 | 0 |
| `is_pay` | 是否付费 | 1 |
| `is_vip` | 是否VIP | true |

## 破解原理

拦截 `/api/drama/play` 和 `/api/drama/detail` 响应，**递归**修改所有金币相关字段，让客户端认为：

1. 用户有 999999 金币
2. 当前剧集消费 0 金币
3. 扣费前后余额不变
4. 剧集已解锁/免费

## 使用方法

### 1. 上传 JS 到 GitHub

```bash
cd lzlukvca
# 把 lzlukvca.js 推到你自己的 GitHub raw URL
# 把 qx.conf/surge.conf/loon.plugin 中的 your-repo 替换为实际仓库
```

### 2. Quantumult X

```ini
[rewrite_local]
^https?://[a-z0-9-]+\.[a-z]+/api/drama/play url script-response-body https://raw.githubusercontent.com/your-repo/main/lzlukvca.js
^https?://[a-z0-9-]+\.[a-z]+/api/drama/detail url script-response-body https://raw.githubusercontent.com/your-repo/main/lzlukvca.js

[mitm]
hostname = *.hddj05.com, *.hddj06.com, *.hddj07.com, *.hdmgdj.com, *.fsbd.yskkkkb.me
```

### 3. Surge

```ini
[Script]
黄豆短剧 = type=http-response,pattern=^https?://[^/]+/api/drama/(play|detail),requires-body=1,max-size=-1,script-path=https://raw.githubusercontent.com/your-repo/main/lzlukvca.js

[MITM]
hostname = *.hddj05.com, *.hddj06.com, *.hddj07.com, *.hdmgdj.com, *.fsbd.yskkkkb.me
```

### 4. Loon

直接安装 `loon.plugin` 文件。

## 生成脚本

```bash
python3 generate.py
# 输出到 ./lzlukvca/
```

## 局限性

⚠️ **Cloudflare 风控严格**：

1. Cloudflare 在某些 CDN 边缘（如 hddj05.com）会阻断异常 IP
2. Flutter 客户端有"splash 线路检测"，会等客户端完成握手才发 API 请求
3. Token 在 localStorage 加密存储（AES），需要真实登录才能拿到有效 token
4. 视频 URL 大概率也是加密下发（参考 `encryptedConfig` 字段），仅破解扣币可能不够

## 已知未破解部分

| 问题 | 状态 |
|------|------|
| Cloudflare 边缘拦截 | ❌ 需要合法 IP + UA + TLS 指纹 |
| Splash 线路检测 | ❌ Flutter 等待线路 API 成功后才放行 |
| encryptedConfig 视频解密 | ❌ 需进一步逆向 AES-256 实现 |
| 视频 m3u8 URL 拼接规则 | ❌ 需真实抓包样本 |

## 文件

```
lzlukvca/
├── lzlukvca.js       核心破解脚本 (84行)
├── qx.conf           Quantumult X 配置
├── surge.conf        Surge 配置
├── loon.plugin       Loon 插件
└── generate.py       生成器
```