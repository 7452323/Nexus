#!/usr/bin/env python3
"""百度输入法皮肤预览器 v3 — 支持 BDS(Android) 和 BDI(iOS)
用法:
  preview_skin.py <in.bds|in.bdi> <out.html>
"""
import sys, os, zipfile

def rgba_color(h):
    h = h.strip().strip('"').strip("'")
    if len(h) == 8:
        return f"#{h[2:8]}"
    return None

def generate_html_preview(bds_path, output_html):
    z = zipfile.ZipFile(bds_path)
    
    # Detect format
    is_ios = bds_path.endswith('.bdi')
    platform_str = "📱 iPhone (iOS)" if is_ios else "🤖 Android"
    file_ext = "bdi" if is_ios else "bds"
    
    try:
        info = z.read('Info.txt').decode('utf-8')
        name = [l for l in info.split('\n') if l.startswith('Name=')]
        name = name[0].split('=',1)[1] if name else 'Skin'
        author = [l for l in info.split('\n') if l.startswith('Author=')]
        author = author[0].split('=',1)[1] if author else ''
    except:
        name, author = 'Unknown', ''
    
    try:
        css = z.read('res/default.css').decode('utf-8')
    except:
        css = ""
    
    # Extract colors from css
    bg_color, font_color, panel_color = '#1a1a2e', '#e6e6e6', '#1a1a2e'
    for line in css.split('\n'):
        if 'STYLE101' in line and 'NM_COLOR' in line:
            bg_color = rgba_color(line.split('=')[-1]) or bg_color
        elif 'STYLE102' in line and 'NM_COLOR' in line:
            font_color = rgba_color(line.split('=')[-1]) or font_color
    
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>{name} — {'BDI' if is_ios else 'BDS'} 预览</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ 
    background: #0a0a1a; display: flex; justify-content: center; align-items: center;
    min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}}
.phone {{
    width: 400px; background: #1a1a2e; border-radius: 20px; padding: 8px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}}
.screen {{ background: {bg_color}; border-radius: 12px; height: 260px; display: flex; flex-direction: column; }}
.cand-bar {{
    height: 50px; background: rgba(0,0,0,0.3); display: flex; align-items: center;
    padding: 0 12px; font-size: 18px; color: {font_color}; gap: 16px;
}}
.keyboard {{ flex: 1; padding: 6px; display: flex; flex-direction: column; justify-content: center; }}
.key-row {{ display: flex; gap: 4px; justify-content: center; margin-bottom: 4px; }}
.key {{
    width: 32px; height: 38px; background: rgba(255,255,255,0.1); border-radius: 5px;
    display: flex; align-items: center; justify-content: center; font-size: 14px;
    color: {font_color}; cursor: pointer; transition: all 0.1s;
}}
.key:hover {{ background: rgba(255,255,255,0.25); transform: scale(1.05); }}
.key.enter {{ width: 70px; background: rgba(0,200,255,0.3); font-size: 10px; }}
.key.space {{ width: 180px; }}
.key.sym {{ width: 50px; font-size: 10px; }}
.info {{ padding: 10px 4px 4px; font-size: 11px; color: #888; text-align: center; }}
.platform {{ color: #0f0; font-weight: bold; }}
</style>
</head>
<body>
<div class="phone">
  <div class="screen">
    <div class="cand-bar">
      <span style="color:#ff5555;font-weight:bold">百度</span>
      <span>输入法</span>
      <span>皮肤预览</span>
    </div>
    <div class="keyboard">
      <div class="key-row">
        <div class="key">q</div><div class="key">w</div><div class="key">e</div><div class="key">r</div>
        <div class="key">t</div><div class="key">y</div><div class="key">u</div><div class="key">i</div>
        <div class="key">o</div><div class="key">p</div>
      </div>
      <div class="key-row">
        <div class="key">a</div><div class="key">s</div><div class="key">d</div><div class="key">f</div>
        <div class="key">g</div><div class="key">h</div><div class="key">j</div><div class="key">k</div>
        <div class="key">l</div>
      </div>
      <div class="key-row">
        <div class="key enter">Enter</div>
        <div class="key">z</div><div class="key">x</div><div class="key">c</div>
        <div class="key">v</div><div class="key">b</div><div class="key">n</div><div class="key">m</div>
        <div class="key enter">⌫</div>
      </div>
      <div class="key-row">
        <div class="key sym">?123</div><div class="key">中英</div>
        <div class="key space">space</div><div class="key sym">.com</div>
        <div class="key enter">↵</div>
      </div>
    </div>
  </div>
  <div class="info">{platform_str} · {name} · by {author}</div>
</div>
</body>
</html>"""
    
    with open(output_html, 'w') as f:
        f.write(html)
    z.close()
    return output_html

if __name__ == '__main__':
    bds = sys.argv[1] if len(sys.argv)>1 else 'skin.bds'
    out = sys.argv[2] if len(sys.argv)>2 else 'preview.html'
    generate_html_preview(bds, out)
    print(f"OK: {out} ({os.path.getsize(out)} bytes)")
