#!/usr/bin/env python3
"""
HAR 解析工具 — 从抓包文件提取关键 API 接口

支持:
  .har 文件（HTTP Archive）
  .zip 文件（部分抓包工具导出格式）
  .json 文件（Mitmproxy/Surge 导出）

用法:
  python3 har_parser.py 抓包.har
  python3 har_parser.py 抓包.zip
  python3 har_parser.py 抓包.json
  python3 har_parser.py 抓包.har --verbose   # 显示更多详情
"""

import json, sys, zipfile, os
from io import StringIO

def load_har(path):
    """加载 HAR 文件，支持 .har/.zip/.json"""
    data = None

    # 如果是 .zip，尝试解压后读取 .har
    if path.endswith('.zip'):
        print(f"📦 检测到 ZIP 压缩包，解压中...")
        with zipfile.ZipFile(path) as z:
            # 找里面的 .har/.json 文件
            har_files = [n for n in z.namelist() if n.endswith('.har') or n.endswith('.json')]
            if not har_files:
                print("❌ ZIP 内未找到 .har 或 .json 文件")
                print(f"   文件列表: {z.namelist()}")
                sys.exit(1)
            target = har_files[0]
            print(f"   读取: {target}")
            data = json.loads(z.read(target))
    else:
        # 直接读 .har 或 .json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

    return data

def extract_entries(data):
    """从 HAR 结构中提取 entries 列表"""
    # 标准 HAR 格式
    if 'log' in data and 'entries' in data['log']:
        return data['log']['entries']
    # Mitmproxy 格式
    if 'entries' in data:
        return data['entries']
    # 直接是数组
    if isinstance(data, list):
        return data
    print("⚠️  无法识别的格式，支持: HAR / Mitmproxy / 数组")
    return []

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    path = sys.argv[1]
    verbose = '--verbose' in sys.argv

    if not os.path.exists(path):
        print(f"❌ 文件不存在: {path}")
        sys.exit(1)

    print(f"📂 文件: {path} ({os.path.getsize(path)/1024:.0f}KB)")
    data = load_har(path)
    entries = extract_entries(data)
    print(f"📊 共 {len(entries)} 条请求\n")

    # 过滤并显示关键 API
    count = 0
    for e in entries:
        url = e['request']['url']
        method = e['request']['method']
        status = e['response']['status']
        mime = e['response']['content'].get('mimeType', '')
        size = e['response']['content'].get('size', 0)

        # 过滤无关请求
        skip_exts = ['.js', '.css', '.png', '.jpg', '.gif', '.svg', '.ico', '.woff', '.ttf']
        if any(url.endswith(ext) for ext in skip_exts): continue
        if any(k in url for k in ['analytics', 'log', 'stat', 'google', 'jpush', 'umeng']): continue
        if size < 50: continue

        count += 1
        print(f"\n{'='*60}")
        print(f"{'🟢' if status == 200 else '🟡'} {method} {status} | {size/1024:.1f}KB | {mime.split('/')[-1]}")
        print(f"  URL: {url[:150]}")

        # 显示请求头（关键字段）
        headers = {h['name']: h['value'] for h in e['request'].get('headers', []) if h['name'] in ('Cookie', 'Authorization', 'User-Agent', 'X-Token', 'token')}
        if headers:
            for k, v in headers.items():
                print(f"  {k}: {v[:80]}..." if len(v) > 80 else f"  {k}: {v}")

        # 显示响应体字段
        text = e['response']['content'].get('text', '')
        if text and len(text) < 5000:
            try:
                obj = json.loads(text)
                if isinstance(obj, dict):
                    print(f"  响应字段: {', '.join(obj.keys())[:120]}")
                    # 标记可疑的 VIP/订阅字段
                    vip_keys = [k for k in obj.keys() if any(v in k.lower() for v in ['vip', 'vip_type', 'is_vip', 'svip', 'member', 'subscription', 'expire'])]
                    if vip_keys:
                        print(f"  🔑 可能需要的字段: {', '.join(vip_keys)}")
                        for k in vip_keys[:3]:
                            print(f"     {k} = {json.dumps(obj[k], ensure_ascii=False)[:60]}")
            except:
                pass

        if not verbose and count >= 30:
            print(f"\n⚠️  显示前 30 条，使用 --verbose 查看全部")
            break

    print(f"\n📋 共显示 {count} 条 API 请求")

if __name__ == '__main__':
    main()
