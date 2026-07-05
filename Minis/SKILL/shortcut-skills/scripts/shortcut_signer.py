#!/usr/bin/env python3
"""iOS 快捷指令签名生成器 — 通过 HubSign API
用法:
  python3 shortcut_signer.py <name> '<actions_json>' [-o output] [--color 0xFF00A0FF] [--glyph 0xF0C2]
  python3 shortcut_signer.py --example weather
  python3 shortcut_signer.py --example clipboard
  python3 shortcut_signer.py --example http_request
"""
import sys, os, json, argparse
import plistlib
from urllib.request import Request, urlopen

HUBSIGN_URL = "https://hubsign.routinehub.services/sign"
ATTACHMENTS_DIR = "/var/minis/attachments"

def build_plist(name, actions, icon_color=4282601983, icon_glyph=61440):
    return {
        "WFWorkflowClientVersion": "3107.0.8.2",
        "WFWorkflowClientRelease": "22.1",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowTypes": ["NCWidget", "WatchKit"],
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": icon_color,
            "WFWorkflowIconGlyphNumber": icon_glyph,
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowInputContentItemClasses": [
            "WFAppStoreAppContentItem", "WFArticleContentItem", "WFContactContentItem",
            "WFDateContentItem", "WFDictionaryContentItem", "WFEmailAddressContentItem",
            "WFGenericFileContentItem", "WFImageContentItem", "WFiTunesProductContentItem",
            "WFLocationContentItem", "WFAVAssetContentItem", "WFActiveNotebookContentItem",
            "WFContentItem", "WFMPMediaContentItem",
        ],
        "WFWorkflowActions": actions,
    }

def sign(shortcut_plist, name="Untitled"):
    xml = plistlib.dumps(shortcut_plist, fmt=plistlib.FMT_XML).decode()
    payload = json.dumps({"shortcutName": name, "shortcut": xml}).encode()
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "cherri/1.0",
        "Origin": "https://routinehub.co",
        "Referer": "https://routinehub.co/",
    }
    req = Request(HUBSIGN_URL, data=payload, headers=headers, method="POST")
    with urlopen(req, timeout=30) as resp:
        data = resp.read()
    if data[:4] != b"AEA1":
        raise ValueError(f"Invalid signature: {data[:4].hex()}")
    return data

def save(signed_bytes, name):
    os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
    safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
    out = os.path.join(ATTACHMENTS_DIR, f"{safe_name}.signed.shortcut")
    with open(out, "wb") as f:
        f.write(signed_bytes)
    return out

def load_json_input(s):
    if os.path.isfile(s):
        with open(s) as f:
            return json.load(f)
    return json.loads(s)

# ========== 预置模板 ==========
EXAMPLES = {
    "weather": {
        "icon_color": 0xFF00A0FF,
        "icon_glyph": 0xF0C2,
        "actions": [
            {"WFWorkflowActionIdentifier": "is.workflow.actions.comment",
             "WFWorkflowActionParameters": {"WFCommentActionText": "查询当前位置天气"}},
            {"WFWorkflowActionIdentifier": "is.workflow.actions.location",
             "WFWorkflowActionParameters": {}},
            {"WFWorkflowActionIdentifier": "is.workflow.actions.weather.currentconditions",
             "WFWorkflowActionParameters": {}},
        ]
    },
    "clipboard": {
        "icon_color": 0xFF00FF00,
        "icon_glyph": 0xF0E7,
        "actions": [
            {"WFWorkflowActionIdentifier": "is.workflow.actions.getclipboard",
             "WFWorkflowActionParameters": {}},
            {"WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
             "WFWorkflowActionParameters": {"WFTextActionText": {"Value": {"attachmentsByRange": {}, "string": "📋剪贴板内容:\n"}, "WFSerializationType": "WFTextTokenString"}}},
        ]
    },
    "http_request": {
        "icon_color": 0xFFFF00FF,
        "icon_glyph": 0xF09E,
        "actions": [
            {"WFWorkflowActionIdentifier": "is.workflow.actions.comment",
             "WFWorkflowActionParameters": {"WFCommentActionText": "HTTP GET 请求"}},
            {"WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
             "WFWorkflowActionParameters": {"WFURL": "https://httpbin.org/get", "WFHTTPMethod": "GET"}},
            {"WFWorkflowActionIdentifier": "is.workflow.actions.showalert",
             "WFWorkflowActionParameters": {"WFAlertActionTitle": "HTTP 响应", "WFAlertActionMessage": {"Value": {"attachmentsByRange": {}, "string": "$URL结果"}, "WFSerializationType": "WFTextTokenString"}}},
        ]
    },
    "notify": {
        "icon_color": 0xFFFFFF00,
        "icon_glyph": 0xF0A2,
        "actions": [
            {"WFWorkflowActionIdentifier": "is.workflow.actions.notification",
             "WFWorkflowActionParameters": {
                 "WFNotificationActionTitle": "提醒",
                 "WFNotificationActionBody": "这是一条测试通知",
                 "WFNotificationActionSound": True,
             }},
        ]
    },
}

# ========== CLI ==========
def main():
    p = argparse.ArgumentParser(description="iOS Shortcut Signer")
    p.add_argument("name", nargs="?", help="Shortcut name")
    p.add_argument("actions", nargs="?", help="JSON array or @file.json")
    p.add_argument("-o", "--output", help="Output file path")
    p.add_argument("--color", type=lambda x: int(x, 0), default=4282601983)
    p.add_argument("--glyph", type=lambda x: int(x, 0), default=61440)
    p.add_argument("--example", help="Use preset: weather, clipboard, http_request, notify")
    p.add_argument("--list-examples", action="store_true", help="List available examples")
    args = p.parse_args()

    if args.list_examples:
        print("可用模板:")
        for k, v in EXAMPLES.items():
            print(f"  {k}: {len(v['actions'])} 个操作")
        return

    if args.example:
        if args.example not in EXAMPLES:
            print(f"未知模板: {args.example}")
            sys.exit(1)
        tpl = EXAMPLES[args.example]
        sc = build_plist(args.example, tpl["actions"], tpl["icon_color"], tpl["icon_glyph"])
        signed = sign(sc, args.example)
        out = save(signed, args.example)
        print(f"OK: {out} ({len(signed)} bytes) — 模板: {args.example}")
        return

    if not args.name or not args.actions:
        p.print_help()
        print("\n示例: python3 shortcut_signer.py 查询天气 '[]' --example weather")
        sys.exit(1)

    actions = load_json_input(args.actions)
    sc = build_plist(args.name, actions, args.color, args.glyph)
    print("签名中...")
    signed = sign(sc, args.name)
    out = args.output or save(signed, args.name)
    if not args.output:
        out = save(signed, args.name)
    else:
        with open(out, "wb") as f:
            f.write(signed)

    basename = os.path.basename(out)
    print(f"OK: {out} ({len(signed)} bytes)")
    print(f"\n下载链接: [下载 {basename}](minis://attachments/{basename})")

if __name__ == "__main__":
    main()
