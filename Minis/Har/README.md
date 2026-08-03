# Har — 抓包分析 + 去广告/爆破会员工具集

> 一站式 HAR 分析 → 定位 API → 生成破解脚本  
> 基于对 58 个 QuantumX / Surge / Loon / Boxjs 仓库的深度学习

## 快速开始

```bash
# 一键摘要
python3 har_analyzer.py capture.har -s

# 找 VIP 接口（自动检测 70+ 字段模式）
python3 har_analyzer.py capture.har --find-vip

# 找广告请求
python3 har_analyzer.py capture.har --find-ads

# 搜索关键词
python3 har_analyzer.py capture.har --find-vip --gen-script --app-name "某App"

# 对比免费/vip 两个 HAR 差异
python3 har_analyzer.py free.har --diff vip.har

# 建议 Loon json-del 去广告字段
python3 har_analyzer.py capture.har --suggest-loon-ad-del

# 解码混淆 JS 脚本
python3 js_decode.py obfuscated.js
```

## 工具清单

| 文件 | 功能 |
|------|------|
| `har_analyzer.py` | 主分析器 — 解析 / 过滤 / VIP检测 / 脚本生成 / HAR对比 |
| `js_decode.py` | JS 混淆解码 — hex / URL / atob / eval-packer / jsjiami |
| `KNOWLEDGE.md` | 知识库 — 19 种爆破去广告模式 + 70+ VIP 字段大全 |

## har_analyzer 完整能力

### 分析模式

| 命令 | 功能 |
|------|------|
| `-s` / `--summary` | 总览：请求数、方法、状态码、域名 Top N |
| `--find-vip` | 自动检测 VIP 字段（递归 JSON，匹配 70+ 关键词） |
| `--find-ads` | 匹配 37 个广告域名模式 |
| `--find-auth` | 登录 / 认证接口 |
| `--find-config` | 配置 / A/B 测试 / 特性开关接口 |
| `--find-cookies` | Cookie / Token 捕获目标 |
| `--suggest-loon-ad-del` | 检测 JSON 中广告字段，输出 Loon `response-body-json-del` 规则 |
| `--gen-loon-plugin` | 生成完整 Loon 插件（Rule + Rewrite + MitM） |
| `--gen-script` | 根据 HAR 自动生成 QX / Surge 破解脚本模板 |
| `--diff other.har` | 对比两个 HAR（免费 vs VIP），找跳过付费的关键字段 |

### 过滤

| 选项 | 示例 |
|------|------|
| `--domain` | `--domain api.example.com` |
| `--method` | `--method POST` |
| `--url-contains` | `--url-contains /v1/user` |
| `--resource-type` | `--resource-type json` |

### 导出

| 选项 | 示例 |
|------|------|
| `--export-json` | `--export-json result.json` |
| `--export-csv` | `--export-csv report.csv` |

### 在代码中使用

```python
from har_analyzer import HARAnalyzer, VIPFieldDetector, ScriptGenerator

a = HARAnalyzer('capture.har')

# 自动检测 VIP 接口
for e in a.find_vip_related():
    print(f"{e.method} {e.url}")
    for f in VIPFieldDetector.detect_json_fields(e.resp_json):
        print(f"  {f['field']} = {f['value']} [{f['category']}]")

# 生成破解脚本
print(ScriptGenerator.generate_crack_script(a.find_vip_related(), "MyApp"))

# 对比两个 HAR
diff = a.diff(HARAnalyzer('vip_user.har'))
for d in diff['common_with_diff']:
    print(f"Difference: {d['url']}")
```

## js_decode 解码器

支持 7 种 JS 混淆类型自动检测与解码：

| 类型 | 识别特征 | 解码方法 |
|------|----------|----------|
| hex decode | `\x48\x45\x4c...` | 静态 hex→utf-8 |
| URL encode | `%48%45%4c...` | 静态 urldecode |
| atob/base64 | `atob("...")` | 静态 base64 解码 |
| eval packer | `eval(function(p,a,c,k,e,d)` | 字典替换提取 |
| jsjiami | `encode_version =` | 静态提取 + Node RC4 (需 node) |
| RC4 table | `__0xead2d = [...]` | 密钥提取 + 字符串表还原 |

```bash
python3 js_decode.py milk.js
# === milk.js ===
# Size: 4886 → 2939 (40%)
# Obfuscation: \xHH 十六进制编码, jsjiami 商业混淆
# Steps: hex_decode
# Crack Logic (1 lines):
```

## 知识库概览

`KNOWLEDGE.md` 记录了从 58 个仓库中萃取的：

- **19 种爆破去广告模式** — JSON替换 / 字段修改 / 正则 / RevenueCat / iTunes / 请求体修改 / 响应头 / Loon json-del / 307 重定向 / Mock ...
- **70+ VIP 字段关键词** — 按 bool_flags / status_values / expire_time / subscription / member_info 分类
- **三平台语法速查** — QX `[rewrite_local]` / Surge `[Script]` / Loon `[Script]` + `response-body-json-del`
- **签到脚本模板** — Env.js 框架 / Cookie 捕获 / MD5 签名 / 多账号遍历
- **去广告大全** — 域名 reject / JSON 字段删除 / 正则替换 / Mock noop / Content Farm

## 研究溯源

### HAR 解析参考（4 个）

| 项目 | Stars | 更新 | 借鉴 |
|------|-------|------|------|
| [JustusW/harparser](https://github.com/JustusW/harparser) | 17 | 2026-07-20 | HAR 1.2 规范解析模型 |
| [PureWaterSun/har-analyzer](https://github.com/PureWaterSun/har-analyzer) | 6 | 2026-05-24 | 多维度过滤 + 搜索逻辑 |
| [kevinfarrugia/hara](https://github.com/kevinfarrugia/hara) | 9 | 2026-02-04 | 资源分类统计 + CSV 导出 |
| [mfoulks3200/har-analyzer](https://github.com/mfoulks3200/har-analyzer) | 13 | 2026-02-27 | VS Code 扩展 + 大文件策略 |

### 逆向模式参考（58 个，精选高星）

**QX/Surge/Loon — 去广告+爆破**
NobyDa/Script (8.4k⭐), ddgksf2013 (13.4k⭐), blackmatrix7/ios_rule_script (27.4k⭐), Orz-3/QuantumultX (4.5k⭐), Guding88/Script, Crazy-Z7/Script, Hackl0us/SS-Rule-Snippet (11.3k⭐), limbopro/Adblock4limbo (4.5k⭐), Rabbit-Spec/Surge (3.6k⭐), SukkaW/Surge (4.3k⭐), LOWERTOP/Shadowrocket-First (4.8k⭐), fmz200/wool_scripts, sve1r/Rules-For-Quantumult-X …

**广告✌ — 域名规则**
AWAvenue-Ads-Rule, app2smile/rules, fmz200/wool_scripts, BlueSodaYY/quantummult, Barre/privaxy, lingeringsound/10007_auto …

**Boxjs — 签到脚本**
chavyleung/scripts, VirgilClyne/GetSomeFries, DualSubs/YouTube, DualSubs/Universal, xzxxn777/Surge, sudojia/AutoTaskScript, Sliverkiss/QuantumultX, Yuheng0101/X, gxggxl/Scripts …

完整代码保留在本地 `reference_repos/`（~152MB），可通过 `git clone` 各仓库获取。

## 工作流

```
┌─────────────────┐
│ 1. 代理抓包 HAR  │  Thor / Charles / mitmproxy
└────────┬────────┘
         ↓
┌─────────────────┐
│ 2. HAR 分析     │  har_analyzer.py --find-vip --gen-script
└────────┬────────┘
         ↓
┌─────────────────┐
│ 3. 定位关键字段  │  VIPFieldDetector: is_vip / expire_time / entitlements …
└────────┬────────┘
         ↓
┌─────────────────┐
│ 4. 生成脚本      │  ScriptGenerator → QX rewrite + Surge script + Loon plugin
└────────┬────────┘
         ↓
┌─────────────────┐
│ 5. 部署验证      │  导入代理工具 → 开启 MITM → 验证效果
└─────────────────┘
```
