#!/usr/bin/env python3
"""百度输入法皮肤配色方案生成器
基于色彩理论（互补/类似/三角/分裂互补/单色系）自动调色
输出 Baidu IME 可直接使用的 STYLE 配置片段
"""
import sys, colorsys, math

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def rgb_to_hsv(r, g, b):
    return colorsys.rgb_to_hsv(r/255, g/255, b/255)

def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r*255), int(g*255), int(b*255)

def baidu_rgba_hex(r, g, b, a=255):
    """百度格式: AARRGGBB"""
    return f"{a:02x}{r:02x}{g:02x}{b:02x}"

# ============================================================
# 配色生成算法
# ============================================================

def analogous(base_hsv, count=5, spread=0.08):
    """类似色"""
    h, s, v = base_hsv
    palette = []
    for i in range(count):
        offset = (i - count//2) * spread
        nh = (h + offset) % 1.0
        palette.append((nh, max(0.3, s), max(0.4, v)))
    return palette

def complementary(base_hsv):
    """互补色"""
    h, s, v = base_hsv
    return [(h, s, v), ((h + 0.5) % 1.0, s, v)]

def split_complementary(base_hsv, spread=0.08):
    """分裂互补"""
    h, s, v = base_hsv
    return [(h, s, v), ((h + 0.5 - spread) % 1.0, s, v), ((h + 0.5 + spread) % 1.0, s, v)]

def triadic(base_hsv):
    """三角色调"""
    h, s, v = base_hsv
    return [(h, s, v), ((h + 1/3) % 1.0, s, v), ((h + 2/3) % 1.0, s, v)]

def tetradic(base_hsv):
    """四角色调"""
    h, s, v = base_hsv
    return [(h, s, v), ((h + 0.25) % 1.0, s, v), ((h + 0.5) % 1.0, s, v), ((h + 0.75) % 1.0, s, v)]

def monochromatic(base_hsv, count=5):
    """单色系（明度变化）"""
    h, s, v = base_hsv
    palette = []
    for i in range(count):
        nv = max(0.15, min(0.95, v + (i - count//2) * 0.18))
        ns = max(0.1, min(1.0, s + (i - count//2) * 0.1))
        palette.append((h, ns, nv))
    return palette

def neutral_warm(base_hsv):
    """暖中性色"""
    return [
        (0.08, 0.6, 0.9),   # 暖白
        (0.07, 0.5, 0.75),  # 暖灰
        (0.06, 0.4, 0.55),  # 中灰
        (0.05, 0.5, 0.3),   # 深灰
        (0.08, 0.8, 0.85),  # 强调
    ]

def cyberpunk_theme():
    """赛博朋克预设"""
    return [
        (0.0, 0.0, 0.05),   # 深黑
        (0.0, 0.0, 0.1),    # 背景
        (0.83, 1.0, 1.0),   # 青色 #00e5ff
        (0.92, 1.0, 1.0),   # 品红 #ff00ff
        (0.12, 0.8, 0.9),   # 金黄
        (0.55, 0.8, 0.7),   # 青绿
    ]

def forest_theme():
    """森林预设"""
    return [
        (0.33, 0.6, 0.2),   # 深绿
        (0.33, 0.5, 0.35),  # 中绿
        (0.35, 0.4, 0.55),  # 浅绿
        (0.25, 0.3, 0.8),   # 米白
        (0.0, 0.0, 0.1),    # 黑底
        (0.08, 0.6, 0.7),   # 橘色强调
    ]

def ocean_theme():
    """海洋预设"""
    return [
        (0.55, 0.6, 0.15),  # 深海蓝
        (0.55, 0.5, 0.3),   # 中蓝
        (0.55, 0.4, 0.5),   # 浅蓝
        (0.58, 0.3, 0.7),   # 天蓝
        (0.5, 0.2, 0.95),   # 白
        (0.0, 0.7, 0.9),    # 红色强调
    ]

PRESETS = {
    'cyber': cyberpunk_theme,
    'forest': forest_theme,
    'ocean': ocean_theme,
}

def generate_baidu_css(style_id_name, palette, style_start=101):
    """把调色板转成百度 default.css 格式"""
    lines = []
    for i, (h, s, v) in enumerate(palette):
        sid = style_start + i
        r, g, b = hsv_to_rgb(h, s, v)
        lines.append(f"[STYLE{sid}]")
        lines.append(f"NM_COLOR={baidu_rgba_hex(r,g,b,0xff)}")
        lines.append(f"")
    return "\n".join(lines)

def generate_full_scheme(base_hex, scheme_name, font_hex=None):
    """生成完整配色方案 — 包含背景/字体/面板/候选"""
    h, s, v = rgb_to_hsv(*hex_to_rgb(base_hex))
    
    generators = {
        'analogous': lambda: analogous((h, s, v), 6),
        'complementary': lambda: complementary((h, s, v)),
        'split': lambda: split_complementary((h, s, v)),
        'triadic': lambda: triadic((h, s, v)),
        'mono': lambda: monochromatic((h, s, v), 6),
        'neutral': lambda: neutral_warm((h, s, v)),
    }
    
    if scheme_name in PRESETS:
        palette = PRESETS[scheme_name]()
    elif scheme_name in generators:
        palette = generators[scheme_name]()
    else:
        palette = analogous((h, s, v), 6)
    
    # 自动选字体色（深底浅字，浅底深字）
    brightness = v
    if brightness < 0.4:
        font_r, font_g, font_b = 230, 230, 230
        first_r, first_g, first_b = 255, 80, 80
    else:
        font_r, font_g, font_b = 30, 30, 30
        first_r, first_g, first_b = 200, 50, 50
    
    if font_hex:
        font_r, font_g, font_b = hex_to_rgb(font_hex)
    
    colors = {
        'bg': hsv_to_rgb(*palette[0]) if palette else (26, 26, 46),
        'font': (font_r, font_g, font_b),
        'font_first': (first_r, first_g, first_b),
        'panel': hsv_to_rgb(*palette[2]) if len(palette) > 2 else (30, 30, 50),
        'key': hsv_to_rgb(*palette[1]) if len(palette) > 1 else (40, 40, 60),
        'candidate': hsv_to_rgb(*palette[3]) if len(palette) > 3 else (35, 35, 55),
        'accent': hsv_to_rgb(*palette[4]) if len(palette) > 4 else (255, 80, 80),
        'separator': (69, 69, 69),
    }
    
    return colors

def format_css_block(colors, style_start=101):
    """格式化为百度 default.css 片段"""
    sid = style_start
    out = []
    for name, (r, g, b) in colors.items():
        out.append(f"[STYLE{sid}] {name}")
        out.append(f"NM_COLOR={baidu_rgba_hex(r,g,b)}")
        out.append(f"HL_COLOR={baidu_rgba_hex(r,g,b)}")
        sid += 1
        out.append("")
    return "\n".join(out)

# ============================================================
# 预设皮肤包（现成配色）
# ============================================================

def preset_skin(name):
    presets = {
        'cyber_night': {
            'bg': (10, 10, 26), 'font': (230, 230, 230), 'accent': (0, 229, 255),
            'panel': (15, 15, 40), 'key': (20, 20, 50), 'candidate': (20, 20, 50),
            'sep': (50, 50, 70), 'name': '赛博之夜',
        },
        'dark_ice': {
            'bg': (20, 25, 40), 'font': (220, 220, 230), 'accent': (80, 180, 255),
            'panel': (25, 30, 50), 'key': (30, 40, 60), 'candidate': (28, 35, 55),
            'sep': (60, 70, 90), 'name': '寒霜之蓝',
        },
        'cream_light': {
            'bg': (250, 245, 235), 'font': (50, 45, 40), 'accent': (230, 120, 80),
            'panel': (245, 240, 225), 'key': (240, 235, 220), 'candidate': (242, 238, 228),
            'sep': (220, 215, 200), 'name': '奶白暖阳',
        },
        'purple_haze': {
            'bg': (30, 20, 50), 'font': (230, 220, 240), 'accent': (200, 100, 255),
            'panel': (35, 25, 60), 'key': (45, 30, 70), 'candidate': (40, 30, 65),
            'sep': (80, 60, 100), 'name': '紫烟迷梦',
        },
        'red_phoenix': {
            'bg': (40, 15, 15), 'font': (240, 230, 220), 'accent': (255, 80, 60),
            'panel': (50, 20, 20), 'key': (60, 25, 25), 'candidate': (55, 22, 22),
            'sep': (100, 50, 50), 'name': '火凤燎原',
        },
        'midnight': {
            'bg': (15, 15, 20), 'font': (200, 200, 210), 'accent': (100, 100, 255),
            'panel': (20, 20, 28), 'key': (25, 25, 35), 'candidate': (22, 22, 32),
            'sep': (50, 50, 60), 'name': '午夜星辰',
        },
        'champagne': {
            'bg': (45, 35, 30), 'font': (240, 230, 220), 'accent': (255, 180, 100),
            'panel': (55, 42, 35), 'key': (60, 48, 40), 'candidate': (58, 45, 38),
            'sep': (100, 80, 70), 'name': '香槟之夜',
        },
    }
    
    if name in presets:
        return presets[name]
    return presets['cyber_night']

def palette_visual(palette):
    """生成 ASCII 调色板可视化"""
    out = []
    for name, (r, g, b) in palette.items():
        block = "██"
        out.append(f"  {block} {name:12} ({r:3},{g:3},{b:3}) {rgb_to_hex(r,g,b)}")
    return "\n".join(out)

if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv)>1 else 'preset'
    
    if action == 'preset':
        name = sys.argv[2] if len(sys.argv)>2 else 'cyber_night'
        s = preset_skin(name)
        print(f"=== Preset: {s['name']} ({name}) ===")
        filtered={k:v for k,v in s.items() if k!='name'}; print(palette_visual(filtered))
        print(f"\n=== CSS (STYLE 101-110) ===")
        colors = [
            ('background', s['bg']),
            ('font', s['font']),
            ('panel', s['panel']),
            ('key_bg', s['key']),
            ('candidate_bg', s['candidate']),
            ('accent', s['accent']),
            ('separator', s['sep']),
        ]
        for i, (n, (r, g, b)) in enumerate(colors):
            print(f"[STYLE{101+i}]\nNM_COLOR={baidu_rgba_hex(r,g,b)}\n")
    
    elif action == 'generate' or action == 'gen':
        base = sys.argv[2] if len(sys.argv)>2 else '#1a1a2e'
        scheme = sys.argv[3] if len(sys.argv)>3 else 'analogous'
        col = generate_full_scheme(base, scheme)
        print(f"=== Base: {base} · Scheme: {scheme} ===")
        print(palette_visual(col))
        print(f"\n=== CSS (STYLE 101-110) ===")
        print(format_css_block(col))
    
    elif action == 'list':
        print("=== Presets ===")
        for k, v in {k: preset_skin(k)['name'] for k in ['cyber_night','dark_ice','cream_light','purple_haze','red_phoenix','midnight','champagne']}.items():
            print(f"  {k:16} {v}")
        print("\n=== Schemes ===")
        for s in ['analogous','complementary','split','triadic','mono','neutral']:
            print(f"  {s}")
