---
name: ios-shortcut
category: reverse-engineering
description: >-
  Merged skill combining: ios-shortcut-signing, shortcut-plist-analysis.
version: "1.0"
sources:
  - ios-shortcut-signing
  - shortcut-plist-analysis
tags: [reverse-engineering, merged]
---

# ios-shortcut

> **Merged from**: ios-shortcut-signing, shortcut-plist-analysis
> **Source count**: 2

---

## Table of Contents

1. [ios-shortcut-signing](#ios-shortcut-signing)
2. [shortcut-plist-analysis](#shortcut-plist-analysis)

---

## ios-shortcut-signing

# iOS 快捷指令签名技能

## 原理

iOS 17 导入 `.shortcut` 文件必须有 Apple CMS 数字签名（前4字节 `AEA1`）。Apple 私人 PKI 链无法本地生成，必须通过 RoutineHub 社区运营的 **HubSign** 服务签名。

## HubSign API

```
Endpoint: https://hubsign.routinehub.services/sign
Method:   POST
Content:  application/json
Timeout:  ~10-30s
```

### Headers（必须）

```python
headers = {
    "Content-Type": "application/json",
    "Origin": "https://routinehub.co",
    "Referer": "https://routinehub.co/",
    "User-Agent": "cherri/1.0",  # 必须！Chrome UA 会被 CF 拦截返回 HTML
}
```

> ⚠️ **关键**：`User-Agent: cherri/1.0` 是过 Cloudflare 的关键。用 Chrome UA 会返回 `<!DOCTYPE html>` 挑战页而非 AEA1 二进制。

### Request Body

```json
{
  "shortcutName": "快捷指令名称",
  "shortcut": "<完整 XML plist 字符串>"
}
```

### Response

成功返回 `application/octet-stream` 二进制，前4字节固定 `AEA1`。

## plist 根结构

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowClientVersion</key><string>3107.0.8.2</string>
    <key>WFWorkflowClientRelease</key><string>22.1</string>
    <key>WFWorkflowMinimumClientVersion</key><integer>900</integer>
    <key>WFWorkflowTypes</key><array>
        <string>NCWidget</string><string>WatchKit</string>
    </array>
    <key>WFWorkflowIcon</key><dict>
        <key>WFWorkflowIconStartColor</key><integer>4282601983</integer>
        <key>WFWorkflowIconGlyphNumber</key><integer>61440</integer>
    </dict>
    <key>WFWorkflowImportQuestions</key><array/>
    <key>WFWorkflowInputContentItemClasses</key><array>
        <string>WFAppStoreAppContentItem</string>
    </array>
    <key>WFWorkflowActions</key><array>
        <!-- 操作列表 -->
    </array>
</dict>
</plist>
```

## Action Identifier 速查

| 动作 | Identifier | 参数 |
|------|-----------|------|
| 显示文本 | `is.workflow.actions.gettext` | `{"WFTextActionText": "文字"}` |
| 设置剪贴板 | `is.workflow.actions.setclipboard` | `{"WFText": "文字"}` |
| 读取剪贴板 | `is.workflow.actions.getclipboard` | `{}` |
| 显示通知 | `is.workflow.actions.notification` | `{"WFNotificationActionTitle":"标题","WFNotificationActionBody":"内容"}` |
| 注释 | `is.workflow.actions.comment` | `{"WFCommentActionText": "说明"}` |
| 打开URL | `is.workflow.actions.openurl` | `{"WFInput": "https://..."}` |
| 显示弹窗 | `is.workflow.actions.showresult` | `{"Text": "内容"}` ⚠️ 见下方 |
| 条件判断 | `is.workflow.actions.conditional` | 见 Apple 文档 |
| 选图 | `is.workflow.actions.selectphoto` | `{}` |

## ⚠️ iOS 17 兼容性陷阱（重要）

### showresult 参数格式

**iOS 17 闪退根因**：`showresult` 的 `Text` 参数格式问题。

```python
# ❌ 错误 — HubSign 默认生成的旧格式，iOS 17 解析闪退
"Text": {
    "Value": {
        "attachmentsByRange": {},
        "string": {"string": "弹窗内容"}
    },
    "WFSerializationType": "WFTextTokenString"
}

# ✅ 正确 — 直接字符串，iOS 17 正常导入
"Text": "弹窗内容"
```

**结论**：手动构建 plist 时，`showresult` 的 `Text` 直接用字符串值，不要嵌套 dict。其他 action（gettext、setclipboard、openurl、notification）无此问题。

## Python 签名脚本

```python
import plistlib, json
from urllib.request import Request, urlopen

def sign_shortcut(name: str, plist_dict: dict) -> bytes:
    xml = plistlib.dumps(plist_dict, fmt=plistlib.FMT_XML).decode()
    payload = json.dumps({"shortcutName": name, "shortcut": xml}).encode()
    req = Request(
        "https://hubsign.routinehub.services/sign",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Origin": "https://routinehub.co",
            "Referer": "https://routinehub.co/",
            "User-Agent": "cherri/1.0",
        },
    )
    with urlopen(req, timeout=30) as resp:
        data = resp.read()
    assert data[:4] == b"AEA1", f"签名失败: {data[:4]}"
    return data

# 使用示例
shortcut = {
    "WFWorkflowClientVersion": "3107.0.8.2",
    "WFWorkflowClientRelease": "22.1",
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowTypes": ["NCWidget", "WatchKit"],
    "WFWorkflowIcon": {
        "WFWorkflowIconStartColor": 4282601983,
        "WFWorkflowIconGlyphNumber": 61440,
    },
    "WFWorkflowImportQuestions": [],
    "WFWorkflowInputContentItemClasses": ["WFAppStoreAppContentItem"],
    "WFWorkflowActions": [
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.showresult",
            "WFWorkflowActionParameters": {"Text": "Hello iOS 17!"}
        }
    ],
}

data = sign_shortcut("测试", shortcut)
with open("test.shortcut", "wb") as f:
    f.write(data)
print(f"OK: {len(data)} bytes")
```

## 调试方法论（二分法闪退定位）

遇到导入闪退时，用**二分法**快速定位问题动作：

1. **先测单动作**（如单独 `showresult`）→ 确认是否该 action 本身问题
2. **两两组合测试**（getText+showresult vs getText+openurl）→ 排除其他动作干扰
3. **锁定问题动作后**，对比参数格式（嵌套 dict vs 直接字符串）
4. **验证 AEA1 magic**：`head -c 4 file.shortcut | od -An -c` → 必须输出 `A   E   A   1`

### 实测案例（2026-07-20）

| 包 | 动作组 | showresult Text | 结果 |
|---|---|---|---|
| 极简版 | 单独 gettext | — | ✅ |
| 复杂版 | gettext+setclipboard+showresult+openurl | 嵌套 dict | 💥 |
| T1 | gettext+setclipboard | — | ✅ |
| T2 | gettext+openurl | — | ✅ |
| T3 | gettext+showresult | 嵌套 dict | 💥 |
| T4 | 单独 showresult | 嵌套 dict | 💥 |
| T5 | gettext+notification | — | ✅ |
| T6 | 单独 showresult | **直接字符串** | ✅ |

**结论**：仅 `showresult` 的 `Text` 参数格式有问题，其他 action 无影响。

## 完整签名管道脚本

```python
#!/usr/bin/env python3
"""
iOS 快捷指令签名流水线 v2
Fix: showresult Text 直接用字符串，避免 iOS 17 闪退
"""
import plistlib, json, sys, time
from urllib.request import Request, urlopen

HUB_SIGN_URL = "https://hubsign.routinehub.services/sign"

def sign_shortcut(name: str, plist_dict: dict) -> bytes:
    xml = plistlib.dumps(plist_dict, fmt=plistlib.FMT_XML).decode()
    payload = json.dumps({"shortcutName": name, "shortcut": xml}).encode()
    req = Request(HUB_SIGN_URL, data=payload, headers={
        "Content-Type": "application/json",
        "Origin": "https://routinehub.co",
        "Referer": "https://routinehub.co/",
        "User-Agent": "cherri/1.0",
    })
    with urlopen(req, timeout=30) as resp:
        data = resp.read()
    assert data[:4] == b"AEA1", f"签名失败: {data[:4]}"
    return data

def build_complex_demo() -> dict:
    return {
        "WFWorkflowClientVersion": "3107.0.8.2",
        "WFWorkflowClientRelease": "22.1",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowTypes": ["NCWidget", "WatchKit"],
        "WFWorkflowIcon": {"WFWorkflowIconStartColor": 4282601983, "WFWorkflowIconGlyphNumber": 61440},
        "WFWorkflowImportQuestions": [],
        "WFWorkflowInputContentItemClasses": ["WFAppStoreAppContentItem"],
        "WFWorkflowActions": [
            {"WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
             "WFWorkflowActionParameters": {"WFTextActionText": f"运行: {time.strftime('%Y-%m-%d %H:%M:%S')}"}},
            {"WFWorkflowActionIdentifier": "is.workflow.actions.setclipboard",
             "WFWorkflowActionParameters": {"WFText": f"已复制: {time.strftime('%H:%M:%S')}"}},
            {"WFWorkflowActionIdentifier": "is.workflow.actions.notification",
             "WFWorkflowActionParameters": {"WFNotificationActionTitle": "测试", "WFNotificationActionBody": time.strftime('%H:%M:%S')}},
            {"WFWorkflowActionIdentifier": "is.workflow.actions.showresult",
             "WFWorkflowActionParameters": {"Text": f"✅ 正常!\n{time.strftime('%Y-%m-%d %H:%M')}"}},  # 直接字符串！
            {"WFWorkflowActionIdentifier": "is.workflow.actions.openurl",
             "WFWorkflowActionParameters": {"WFInput": "https://www.apple.com"}},
        ],
    }

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "signed.shortcut"
    data = sign_shortcut("ComplexTest", build_complex_demo())
    with open(out, "wb") as f:
        f.write(data)
    print(f"✅ {len(data)} bytes → {out}")
```

使用方法：

```bash
python3 scripts/sign_pipeline.py my_shortcut.shortcut
```

| 项 | 说明 |
|---|---|
| HubSign 可用性 | RoutineHub 社区公益，挂了就没法签 |
| Cloudflare | 必须 `cherri/1.0` UA |
| 批量 | 别批量发，会被 CF 挡 |
| 动作数量 | 一般 < 50 个动作不超时 |

## 相关服务

| 服务 | 说明 |
|------|------|
| HubSign API | 免费公益，唯一已知可用 |
| ShortcutStudio | App Store 6760745118，商业App，接口未公开 |

## 参考文档

- [HubSign API 完整文档](references/hubsign-api-doc.md)
- [iOS 17 闪退调试记录](references/ios17-crash-debug.md)

---

## shortcut-plist-analysis

# Apple Shortcut (.shortcut) 文件结构分析与修改

## 文件格式

Apple Shortcut 使用 **AEA1** 容器格式，结构如下：

```
AEA1 (4 bytes magic)
+ 00 00 00 00 (4 bytes padding)
+ 4 bytes LE size of certificate chain plist
+ Certificate chain (bplist — contains SigningCertificateChain)
+ CMS/PKCS7 signature (ECDSA)
+ BODY: the actual signed workflow data
```

### 关键字段

- **Magic**: `AEA1` (0x41454131)
- **签名证书链**: 紧跟在 magic 后的 **bplist**，含 `SigningCertificateChain`
- **CMS 签名**: 证书链后的 ECDSA 签名数据 (DER 编码)
- **Workflow plist**: CMS enveloped 数据内的真正快捷指令内容

### 两种下载渠道

| 渠道 | API 字段 | 大小 | 签名 | 用途 |
|------|----------|------|------|------|
| `signedShortcut` | `fields.signedShortcut.value` | ~4.9MB | ✅ 已签名 | iPhone 可直接导入 |
| `shortcut` (raw) | `fields.shortcut.value` | ~7.6MB | ❌ 未签名 | 可解码修改，不可直接导入 |

## 获取快捷指令文件

### 通过 iCloud API

```bash
# 获取快捷指令元数据（含下载链接）
curl -s "https://www.icloud.com/shortcuts/api/records/<UUID>"

# 响应中两个关键字段：
# fields.shortcut.value.downloadURL     — 未签名原始 plist
# fields.signedShortcut.value.downloadURL — 已签名 .shortcut
```

注意: downloadURL 中的 `${f}` 需要替换为文件名（如 `shortcut`）。URL token 有有效期，每次使用前需要重新获取 API 响应。

### iCloud API 返回结构

```json
{
  "fields": {
    "shortcut": {
      "value": {
        "downloadURL": "https://cvws.icloud-content.com/B/.../${f}?...",
        "size": 7622574,
        "fileChecksum": "AQNDtvsK+SpbNHBAlgPaCA31vYRR"
      }
    },
    "signedShortcut": {
      "value": {
        "downloadURL": "https://cvws.icloud-content.com/B/.../${f}?...",
        "size": 4857225,
        "fileChecksum": "AVusq1ClQU6JrV0DWNQ5zI59BvDp"
      }
    },
    "name": { "value": "截图套壳" },
    "signingStatus": { "value": "APPROVED" }
  }
}
```

## 解码未签名 plist (raw)

### 读取 bplist

```python
import plistlib
with open('shortcut_raw.plist', 'rb') as f:
    wf = plistlib.loads(f.read())
```

### 关键字段

```
WFWorkflowActions          — 动作列表（数组，每个动作含 identifier + parameters）
WFWorkflowTypes            — 类型（App 快捷指令等）
WFWorkflowIcon             — 图标
WFWorkflowMinimumClientVersion — 最低版本
WFWorkflowImportQuestions  — 导入问题
```

### 动作结构

```python
action = {
    'WFWorkflowActionIdentifier': 'is.workflow.actions.setitemname',
    'WFWorkflowActionParameters': {
        'WFName': '文件名',  # 可以是字符串或嵌套字典
        'UUID': '7CE67CA4-...'
    }
}
```

## 常见动作类型

| Identifier | 功能 | 关键参数 |
|-----------|------|---------|
| `is.workflow.actions.gettext` | 文本 | WFText |
| `is.workflow.actions.setitemname` | 设置文件名 | WFName |
| `is.workflow.actions.alert` | 弹窗 | WFAlertActionTitle |
| `is.workflow.actions.conditional` | 条件判断 | WFConditionalActionString |
| `is.workflow.actions.base64encode` | Base64 编解码 | WFEncodeMode (Encode/Decode) |
| `is.workflow.actions.list` | 列表 | WFItems |
| `is.workflow.actions.overlayimageonimage` | 图片叠加 | - |
| `is.workflow.actions.overlaytext` | 文字叠加 | WFOverlayText |
| `is.workflow.actions.image.convert` | 图片格式转换 | - |
| `is.workflow.actions.image.resize` | 图片缩放 | - |
| `is.workflow.actions.image.combine` | 图片合并 | - |
| `com.apple.shortcuts.OpenWorkflowAction` | 打开子快捷指令 | target |

## 动作索引（关键动作参考）

常见动作 ID 索引：

| 动作位置 | 动作 | 用途 |
|---------|------|------|
| 23 | list | 存储大 JSON 字典的 Base64 (典型套壳截图类) |
| 25 | base64encode (decode) | 解码水印底图 |
| 59 | base64encode (decode) | 解码灵动岛 |
| 61 | base64encode (decode) | 解码底图 |
| 63 | resize | 截图缩放到固定尺寸 |
| 64 | mask | 圆角蒙版 |
| 67-70 | overlayimageonimage | 图片叠加合成 |
| 153 | overlaytext | 日期文字叠加 |
| 160 | setitemname | 设置输出文件名 |
| 174 | conditional | 水印条件判断 |

## 完整的字典键值映射

参考 `references/shortcut-dictionary-reference.md` 获取原始快捷指令所有内嵌资源的一键提取脚本和键值说明。

## 查找内嵌字典数据

快捷指令常把大型 JSON 字典编码为 **Base64 字符串** 存在 `WFItems`（list 动作）中：

```python
actions = wf['WFWorkflowActions']
a_list = actions[idx]  # identifier = 'is.workflow.actions.list'
items = a_list['WFWorkflowActionParameters']['WFItems']
base64_str = items[0]  # 通常是唯一的字符串项
decoded = base64.b64decode(base64_str)
data = json.loads(decoded)  # 大型 JSON 字典
```

### 典型字典结构（截图套壳类）

```json
{
  "完成公告": "文本内容...",
  "底图": "base64图片数据",
  "𝐁ʏ̆̈：喘息": "base64水印图片数据",
  "背景菜单": "base64图片数据",
  "默认模版": "base64图片数据",
  "背景菜单公告": "文本内容...",
  "使用说明": "base64图片数据（或PDF）",
  "随机美女": "https://...URL",
  "完成菜单": "base64图片数据",
  "背景模糊": "base64图片数据",
  "": "base64图片数据",
  "灵动岛": "base64图片数据"
}
```

注意：部分值可能是 **vCard 格式**（`BEGIN:VCARD`）而不是直接 PNG 文件头。需要在 Base64 外再解析 VCF。

## 去水印操作

### 1. 删除字典中的水印键

```python
if '𝐁ʏ̆̈：喘息' in data:
    del data['𝐁ʏ̆̈：喘息']
```

### 2. 清洗文本中的水印签名

```python
data['完成公告'] = data['完成公告'].replace('\\n𝐁ʏ̆̈：喘息', '')
data['背景菜单公告'] = data['背景菜单公告'].replace('𝐁ʏ̆̈：喘息', '')
```

### 3. 修改文件名

```python
actions[31]['WFWorkflowActionParameters']['WFName'] = '新文件名'
```

### 4. 修改弹窗标题

```python
actions[101]['WFWorkflowActionParameters']['WFAlertActionTitle'] = '✔️'
```

### 5. 修改条件判断

```python
actions[174]['WFWorkflowActionParameters']['WFConditionalActionString'] = '✔️'
```

### 6. 修改输出文件名日期格式

文件名通常在 `setitemname` 动作的 `WFName.Value` 字典中，通过 `attachmentsByRange` → `Aggrandizements` → `WFDateFormatVariableAggrandizement` → `WFDateFormat` 字段控制：

```python
name_val = actions[idx]['WFWorkflowActionParameters']['WFName']['Value']
attachments = name_val.get('attachmentsByRange', {})
for range_key, aggs_group in attachments.items():
    for agg in aggs_group.get('Aggrandizements', []):
        if agg.get('Type') == 'WFDateFormatVariableAggrandizement':
            agg['WFDateFormat'] = 'yyyy年MM月dd日 HH:mm:ss'  # 去掉水印
```

## 修改后保存 bplist

```python
with open('modified.plist', 'wb') as f:
    plistlib.dump(wf, f)
```

## iOS 端运行方案

推荐使用 **Python IDE** (App Store: https://apps.apple.com/cn/app/python-ide/id6753987304)

### Python IDE 操作步骤

1. 解压 ZIP 到 Python IDE 文件目录
2. 安装 opencv-python-headless（点右下角 + Package → 搜索安装）
3. 运行脚本，按提示粘贴截图路径（在 Files 中长按图片 → Copy Path）

### 纯快捷指令方案

如果不需要修改模板，也可以直接使用原版快捷指令（来自 iCloud 链接），但在 iOS 17+ 上：
- 已签名的 `.shortcut` 可以直接导入
- 未签名的 `.plist` **无法导入**，提示"无法导入未签名的快捷指令文件"
- 没有开发者签名就无法重新打包 `.shortcut` 文件

## vCard TITLE 字段 — 模板屏幕坐标

快捷指令模板 vCard 的 `TITLE` 字段常包含屏幕区域的 JSON 配置：

```
TITLE:{"V":"A","Y":"1443","W":"983","I":"-11","X":"357"}
```

各字段含义：
- `X`, `Y` — 屏幕区域左上角在模板图上的坐标
- `W` — 屏幕区域宽度
- `I` — 旋转角度
- `V` — 方案版本（A/B）

### 从 TITLE 生成 CFG

```python
import json, re

# 从 VCF 中提取 TITLE
match = re.search(r'TITLE:(\\{.+?\\})', vcf_text)
title_data = json.loads(match.group(1))

x = title_data['X']
y = title_data['Y']
w = title_data['W']
# 屏幕高度需从快捷指令的 resize 动作推断（通常为 width * 屏幕比例）
# Action 63 通常指定了 resize 到 1321x2850
# 所以 h = w * (2850/1321)
h = int(w * (2850 / 1321))

cfg = f\"\"\"
left_top_x={x}
left_top_y={y}
right_top_x={x + w}
right_top_y={y}
left_bottom_x={x}
left_bottom_y={y + h}
right_bottom_x={x + w}
right_bottom_y={y + h}
template_width={template_w}
template_height={template_h}
\"\"\"
```

## 从 vCard 提取模板图片

### 方法一: 从 `PHOTO;ENCODING=b` 提取

```python
import re, base64

vcf_text = base64.b64decode(outer_b64).decode('utf-8', errors='replace')
match = re.search(r'PHOTO;ENCODING=b:(.+?)(?=\\n\\w)', vcf_text, re.DOTALL)
if match:
    b64_pixels = match.group(1).strip().replace('\\n', '').replace('\\r', '')
    # 补 padding
    padding = 4 - len(b64_pixels) % 4
    if padding != 4:
        b64_pixels += '=' * padding
    img_bytes = base64.b64decode(b64_pixels)
    # img_bytes 开头可能是 PNG 头部 (\\x89PNG) 或 JPEG 头部 (\\xFF\\xD8\\xFF)
```

### 方法二: 图片伪装成联系人

有些字典项（如 `𝐁ʏ̆̈：喘息`）只是联系人名片，不包含 PHOTO 字段。检查是否有 `PHOTO;` 行来区分。

## iCloud URL 下载注意事项

### Token 过期

iCloud downloadURL 中的签名参数会**快速过期**（几分钟到几小时）。正确流程：

```python
# 每次下载前重新获取 API
import urllib.request, json
req = urllib.request.Request(f"https://www.icloud.com/shortcuts/api/records/{UUID}")
with urllib.request.urlopen(req) as resp:
    api = json.loads(resp.read())

# 获取最新的 downloadURL
url = api['fields']['shortcut']['value']['downloadURL'].replace('${f}', 'shortcut')
# 或 signed 版本
signed_url = api['fields']['signedShortcut']['value']['downloadURL'].replace('${f}', 'shortcut')

# 立即下载
req2 = urllib.request.Request(url)
with urllib.request.urlopen(req2) as resp:
    data = resp.read()
```

⚠ 不要复用旧的 downloadURL —— 会返回 400 Bad Request (invalid uri signature)。

## iCloud 网页版下载限制

iCloud Shortcuts 分享页在浏览器中访问时：
- 页面是 HTML 渲染（React spa），通过 JS 加载数据
- 直接 `curl` 链接得到的只是 HTML 页面，不是真正的 .shortcut 文件
- 必须通过 API 获取 downloadURL 才能下载真实文件
- 浏览器端 CORS 限制，无法用 fetch 直接下载

## 模板交付原则

用户明确偏好：**只交付模板原始素材**（.png + .cfg），不要代为执行套壳。他们有自己的工作流来自行合成。

**不要替用户套壳截图** — 用户要求做模板就是做 cfg + png，不要自作主张帮用户合成效果图。用户会把模板拿走自己用工具套。

## 快速签名：HubSign 流水线三步（2026-07-20 再次验证通过）

```
写 Action → POST HubSign API → 拿到 AEA1 签名 .shortcut → iOS 点导入 ✅
```

**不需要 Apple 设备、不需要 iCloud、不需要姚 mac、不需要越狱。** HubSign 是 RoutineHub 社区的签名 RPC 服务。

> ⚠️ **2026-07-20 关键实测**：必须用 `User-Agent: cherri/1.0`！任何其他UA都返回CF挑战页（~210KB HTML），而非AEA1二进制。响应 `Content-Disposition: attachment; filename=xxx.shortcut`，`cf-cache-status: DYNAMIC`。

快速 Python 签名（已部署在 `/tmp/shortcut-signer/sign.py`，新版一键脚本见 `scripts/sign_shortcut.py`）：

```python
import sign
signed = sign.sign(sign.build_shortcut('我的快捷指令', [
    sign.ACTIONS['notification']('🎉', '签名成功！'),
]), '我的快捷指令')
open('out.signed.shortcut', 'wb').write(signed)  # AEA1 magic, ~21KB
```

详细 API 文档见 `references/hubsign-signing.md`。
一键签名脚本见 `scripts/sign_shortcut.py`（直接可运行，含常用 action 构造器）。含 iOS 导入闪退时的二分法调试指南（2026-07-20 实战）。

## 已知局限

### 签名限制（iOS 15+）— 必读

> **TL;DR**: iOS 15+ 要求导入文件的魔数为 `AEA1` 且带有效 CMS 签名。Python `plistlib.dump()` 输出仅 `bplist00`，**无法导入**。生成→导入的正确流水线：
> 
> ```
> 方式 A（文件分发）: Python/bplist → 签名（macOS `shortcuts sign` 或 Cherri）→ Telegram 发送
> 方式 B（iCloud链接）: Python/bplist → 上传 iCloud API → 生成链接 → 用户点"从 iCloud 链接添加"
> ```

自 iOS 15 起，Apple 要求所有导入 Shortcuts App 的文件必须是 **AEA1 容器格式的已签名 .shortcut**。

纯 `bplist`（未签名 plist）会被拒绝，提示"无法导入未签名的快捷指令文件"。这是系统级限制，不是内容问题。

#### 为什么第三方 Studio（如 ShortcutStudio）可以？

根据对 ShortcutStudio 1.1.07 (com.shortcutstudio.app) 的 IPA 逆向分析：

| 特征 | 说明 |
|------|------|
| **架构** | SwiftUI 客户端 + 服务器端签名（API: `api.shortcutstudio.app`） |
| **不客户端签名** | IPA 内无 openssl 链接，无本地签名逻辑 |
| **安装方式** | 通过 App Intents 框架安装已签名文件（`SignedShortcutInstall`, `ShortcutStudioShortcutsProvider`） |
| **关键字符串** | `GetGeneratedShortcutFileIntent`, `GenerateShortcutResponse`, `RawShortcutExportFormat` |

→ **签名是服务器行为**，客户端只接收已签名的 AEA1 容器并调用系统 API 安装。

#### 签名结构

```
AEA1 (4 bytes magic, 0x41454131)
+ 00 00 00 00 (4 bytes padding)
+ 4 bytes LE size of certificate chain plist
+ 证书链 (bplist, 含 SigningCertificateChain)
+ CMS/PKCS7 签名 (ECDSA)
+ Body: 真正的 workflow plist (嵌套在 CMS enveloped 数据中)
```

#### 有效方案（按优先级）

| 方案 | 难度 | 适用 | 说明 |
|------|------|------|------|
| **A. HubSign API** | ⭐ | 任何有网络的环境 | **通用推荐**。无 Apple 设备要求。调用 RoutineHub 社区签名的服务端 API，POST plist 过去，返回 AEA1 签名文件。详细文档见 `references/hubsign-signing.md`。 |
| **B. iCloud 链接** | ⭐ | 通用，需 Apple ID | 上传到 iCloud → 生成链接 → 用户点"从 iCloud 链接添加"。Shortcuts App 原生支持，绕过文件导入验证。完整逆向分析见 `references/ios15-signing-guide.md`。 |
| **C. macOS 签名** | ⭐⭐ | 有 Mac | `shortcuts sign -i unsigned.plist -o signed.shortcut`（Apple 官方 CLI）或 `cherri --sign`（开源，https://cherrilang.org/compiler/signing.html） |
| **D. 服务器签名** | ⭐⭐⭐ | 有服务器并逆转签名算法 | 逆向 Cherri 的签名算法自行实现。成本高，不推荐。 |
| **E. 越狱 tweak** | ⭐⭐⭐⭐ | 已越狱 | Unsigncuts / Importcuts 恢复未签名导入能力。 |

#### 实践建议（服务器端 Python 工具）

```
生成 bplist → 判断签名条件
              ├─ 有 Mac → 调 shortcuts sign 或 cherri --sign → 输出 .shortcut
              ├─ 有越狱设备 → dump Apple ID auth data → shortcut-sign CLI 签名 → 输出 .shortcut
              ├─ 无签名且必须走文件越狱 → 仅能在越狱设备用 Importcuts/Unsigncuts
              └─ 通用方案 → 上传 iCloud → 生成链接 → 用户点"从 iCloud 链接添加"
```

#### shortcut-sign (0xilis) — 前沿但非银弹

[shortcut-sign](https://github.com/0xilis/shortcut-sign) 是 libshortcutsign 的 CLI，支持 Linux + macOS，能签名、验证、提取、重签快捷指令。

**但它不是独立签名方案。** 它需要：
- **Apple ID Auth Data**（从越狱设备或 AMFI 禁用的 Mac dump 的私钥 + 证书链 + validation record）
- 没有 auth data 签出的文件 iOS 仍然拒绝（`faile din creating EVP_PKEY object`）

**结论**：没有 Apple 设备（越狱 iOS 或 Mac）提供的 auth data，**纯 Linux 10 无法生成 iOS 可导入的 .shortcut**。

完整技术文档（含逆向分析、ShortcutStudio 架构拆解、Cherri 签名详解）见 `references/ios15-signing-guide.md`。
Linux 签名可行性实测 + shortcut-sign CLI 实测 + auth data 结构见 `references/linux-signing-legal.md`。
**HubSign API 完整文档（接口、参数、Python/C 代码、Action 速查表）见 `references/hubsign-signing.md`。**

### Telegram 文件发送
- 使用 `send_message` 的 `MEDIA:` 语法发送 .shortcut 文件
- 也可以用 bot token 通过 `sendDocument` multipart 命令直发
- 注意: bot token 经常过期/被撤销，需要备用

## 常用图片处理

### 提取内嵌 Base64 图片
```python
img_data = base64.b64decode(data['key'])
with open('output.png', 'wb') as f:
    f.write(img_data)
```

### 检查文件格式
```python
with open(path, 'rb') as f:
    header = f.read(16)
# PNG:  89 50 4E 47 0D 0A 1A 0A
# VCF:  42 45 47 49 4E 3A 56 43 (BEGIN:VC)
# PDF:  25 50 44 46 2D ( %PDF- )
# JPEG: FF D8 FF E0 / FF D8 FF E1
```

### 从 vCard/VCF 提取嵌入图片

快捷指令常将图片编码在 **vCard (VCF)** 文件的 `PHOTO;ENCODING=b:` 字段中，外层再加 Base64。提取方式：

```python
import re, base64

# 先解外层 Base64 得到 VCF 文本
vcf_text = base64.b64decode(inner_b64).decode('utf-8', errors='replace')

# 提取 PHOTO 字段
match = re.search(r'PHOTO;ENCODING=b:(.+?)(?=\\n\\w)', vcf_text, re.DOTALL)
if match:
    b64_pixels = match.group(1).strip().replace('\\n', '').replace('\\r', '')
    # 补 padding
    padding = 4 - len(b64_pixels) % 4
    if padding != 4:
        b64_pixels += '=' * padding
    img_bytes = base64.b64decode(b64_pixels)
    with open('output.png', 'wb') as f:
        f.write(img_bytes)
```

常见 vCard 样式：
- `PHOTO;ENCODING=b:iVBORw0KGgo...` (PNG in base64)
- `PHOTO;ENCODING=b:/9j/4AAQ...` (JPEG in base64)
- `PHOTO;ENCODING=BASE64:...`

注意：有些字典项是纯联系人名片（无 PHOTO 字段，如 `𝐁ʏ̆̈：喘息` 这个 key 其实是个联系人名片，不是图片）。

## 截图套壳工具（手机壳合成）

核心流程：

```
截图 → 透视变换 → 贴合到模板屏幕区域 → 合成
```

### 模板文件结构

每套模板两个同名文件：
- `模板名.png` — 手机壳模板图（RGBA，带透明度）
- `模板名.cfg` — 屏幕四角坐标配置

### CFG 格式

```
left_top_x=376
left_top_y=986
right_top_x=778
right_top_y=930
left_bottom_x=517
left_bottom_y=1879
right_bottom_x=903
right_bottom_y=1790
template_width=1079
template_height=2035
```

4 个坐标点是手机屏幕的四个角在模板图上的像素位置。

### 透视变换合成

```python
import cv2
import numpy as np
from PIL import Image

# 模板屏幕区域 4 个点
src = np.array([[376,986], [778,930], [903,1790], [517,1879]], dtype=np.float32)
# 截图 4 个角
dst = np.array([[0,0], [w,0], [w,h], [0,h]], dtype=np.float32)

matrix = cv2.getPerspectiveTransform(dst, src)
warped = cv2.warpPerspective(
    np.array(screenshot), matrix,
    (template_w, template_h),
    flags=cv2.INTER_LANCZOS4
)

# 合成（变形截图在上，模板在下）
# 处理 alpha 通道
warped_rgba = cv2.cvtColor(warped, cv2.COLOR_RGB2RGBA)
warped_rgba[:,:,3] = 255
mask = np.any(warped > 0, axis=2)
warped_rgba[~mask, 3] = 0

result_np = template_np.copy()
aw = warped_rgba[:,:,3].astype(float) / 255.0
at = template_np[:,:,3].astype(float) / 255.0
for c in range(3):
    result_np[:,:,c] = (warped_rgba[:,:,c] * aw + template_np[:,:,c] * at * (1 - aw)).astype(np.uint8)
result_np[:,:,3] = np.maximum(warped_rgba[:,:,3], template_np[:,:,3])
```

## 依赖

### OpenCV 方案（服务器端）
```bash
pip3 install opencv-python-headless Pillow numpy
```

### 纯 PIL 方案（iOS Python IDE，零额外安装）
PIL 的 `Image.transform(mode=PERSPECTIVE)` 可以实现透视变换，不需要 opencv：

```python
def calc_perspective(src_pts, dst_pts):
    """计算透视变换的8个系数（无需cv2）"""
    import numpy as np
    A, B = [], []
    for i in range(4):
        sx, sy = src_pts[i]
        dx, dy = dst_pts[i]
        A.append([sx, sy, 1, 0, 0, 0, -dx*sx, -dx*sy])
        A.append([0, 0, 0, sx, sy, 1, -dy*sx, -dy*sy])
        B += [dx, dy]
    coeffs = np.linalg.solve(np.array(A, dtype=np.float64), np.array(B, dtype=np.float64))
    return tuple(coeffs)

def shell_screenshot_pil(screenshot, template, screen_pts):
    """纯PIL实现套壳合成"""
    sw, sh = screenshot.size
    tw, th = template.size
    
    coeffs = calc_perspective(
        [(0,0), (sw,0), (sw,sh), (0,sh)],
        screen_pts
    )
    warped = screenshot.transform(
        (tw, th), Image.PERSPECTIVE, coeffs,
        Image.Resampling.BICUBIC  # PERSPECTIVE不支持LANCZOS
    )
    
    # RGBA合成
    result = template.copy()
    warped = warped.convert('RGBA')
    r, g, b, a = warped.split()
    from PIL import ImageOps
    mask = ImageOps.invert(Image.eval(r, lambda x: 255 if x > 5 else 0))
    warped.putalpha(mask)
    result.alpha_composite(warped)
    return result
```

⚠ PERSPECTIVE transform 不支持 `LANCZOS`，只能用 `BICUBIC`、`BILINEAR` 或 `NEAREST`。

### Python IDE (iOS) 上的推荐依赖
Python IDE App Store 自带 Pillow 和 numpy 作为内置库，因此：
- ✅ Pillow — **自带，无需安装**
- ✅ numpy — **自带，无需安装**
- ❌ opencv-python-headless — **需要额外安装，建议避免使用**

## 模板规格

用户模板：
- **模板2**: 1280×2275, 屏幕区域 LT(147,1007) RT(507,949) RB(631,1752) LB(275,1826)
- **模板3**: 1079×2035, 屏幕区域 LT(376,986) RT(778,930) RB(903,1790) LB(517,1879)

## 用户偏好（重要）

### 模板交付原则
用户只想要**模板素材**（.png + .cfg），不要代执行套壳。他们的工作流：
1. 用户提供手机壳模板图 + 自己算坐标 → 制作 cfg + png
2. 用户自行用工具合成
3. **不要替用户跑套壳效果图** — 用户会拿走模板自己用

### iOS 端工具偏好
- Python IDE (iOS) 是首选运行环境
- 需要**零额外依赖**版本（纯 PIL，不用 opencv）
- 用 `Image.transform(mode=PERSPECTIVE)` 代替 `cv2.warpPerspective`
- numpy 是 Python IDE 内置的，可以放心用

### 随机美女 API 选择
- 首选：`https://api.suyanw.cn/api/ksxjj`（用户提供的）
- 备选：`picsum.photos`

## 应用场景

1. 去快捷指令水印（字典级 + 动作级）
2. 提取内嵌素材（图片/VCF/PDF）
3. 制作新模板替换原有模板
4. 独立截图套壳工具（不依赖快捷指令运行环境）

---
