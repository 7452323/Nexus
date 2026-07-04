#!/usr/bin/env python3
"""百度输入法皮肤生成器 v4 — 同时支持 Android(.bds) 和 iOS(.bdi)
用法:
  make_skin.py <name> <author> <out> [--platform a|i]
  --platform a → .bds (Android)  [默认]
  --platform i → .bdi (iOS)
"""
import zipfile, sys, struct, zlib

PNG_1PX = bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000007f1d4b830000000c49444154789c6360f8cf00000002000168651a1a0000000049454e44ae426082')

def mkpng(w=16,h=16,r=200,g=200,b=200,a=255):
    sig=b'\x89PNG\r\n\x1a\n'
    ihdr=b'IHDR'+struct.pack('>IIBBBBB',w,h,8,6,0,0,0)
    ihdr_chunk=struct.pack('>I',13)+ihdr+struct.pack('>I',zlib.crc32(ihdr))
    raw=b''
    for _ in range(h):
        raw+=b'\x00'+bytes([r,g,b,a])*w
    idat=zlib.compress(raw)
    idat_chunk=struct.pack('>I',len(idat))+b'IDAT'+idat+struct.pack('>I',zlib.crc32(b'IDAT'+idat))
    iend_chunk=struct.pack('>I',0)+b'IEND'+struct.pack('>I',zlib.crc32(b'IEND'))
    return sig+ihdr_chunk+idat_chunk+iend_chunk

def create(name, author, output, platform='a'):
    is_ios = platform.lower() == 'i'
    ext = '.bdi' if is_ios else '.bds'
    if not output.endswith(ext):
        output = output.rsplit('.',1)[0] + ext
    
    platform_code = 'I' if is_ios else 'A'
    
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        # === Info.txt ===
        z.writestr("Info.txt", f"Name={name}\nStyle=Default\nSupportPlatform={platform_code}\nAuthor={author}\n")
        
        # === res/default.css ===
        css_parts = []
        css_parts.append(f"""[GLOBAL]
STYLE_NUM=614
FOR=720

[STYLE101]背景
NM_COLOR=1a1a2eff
[STYLE102]字体
NM_COLOR=e6e6e6ff
FONT_CLEARTYPE=1
FONT_SIZE=40
[STYLE103]面板背
NM_COLOR=1a1a2eff
[STYLE104]面板
SIZE=800,245
[STYLE105]更多字体
NM_COLOR=e6e6e6ff
FONT_SIZE=37
[STYLE106]更细胞
NM_IMG=back,5
[STYLE111]候背
NM_COLOR=1a1a2ebb
[STYLE113]候字体
NM_COLOR=e6e6e6ff
FONT_SIZE=42
[STYLE114]首字
NM_COLOR=ff3333ff
FONT_SIZE=42
[STYLE121]列背
NM_IMG=back,7
[STYLE123]列字体
NM_COLOR=e6e6e6ff
FONT_SIZE=38
[STYLE133]分隔
NM_COLOR=454545ff
[STYLE151]气泡
NM_COLOR=aa999999
[STYLE153]泡字体
NM_COLOR=e6e6e6ff
FONT_SIZE=60
[STYLE155]泡细胞
NM_IMG=back,11
""")
        
        # STYLE161-183: graph icons
        for i in range(161,184):
            css_parts.append(f"[STYLE{i}]\nNM_IMG=graph,{i-160}\nHL_IMG=graph,{i-160}\n")
        
        # STYLE201-210: numbers
        for i in range(201,211):
            css_parts.append(f"[STYLE{i}]\nNM_IMG=plus,{i-200}\nHL_IMG=plus,{i-200}\n")
        
        # STYLE211-236: en lowercase
        idx = 1
        for c in 'qwertyuiopasdfghjklzxcvbnm':
            css_parts.append(f"[STYLE{210+idx}]={c}\nNM_IMG=en,{idx}\nHL_IMG=en,{idx}\n")
            idx+=1
        
        # STYLE241-266: en uppercase
        idx = 27
        for c in 'QWERTYUIOPASDFGHJKLZXCVBNM':
            css_parts.append(f"[STYLE{240+idx-26}]={c}\nNM_IMG=en,{idx}\nHL_IMG=en,{idx}\n")
            idx+=1
        
        # STYLE291-296: bh6
        for i in range(291,297):
            css_parts.append(f"[STYLE{i}]\nNM_IMG=bh6,{i-290}\nHL_IMG=bh6,{i-290}\n")
        
        # STYLE301-310: nums small
        for i in range(301,311):
            css_parts.append(f"[STYLE{i}]\nNM_IMG=pluss,{i-300}\nHL_IMG=pluss,{i-300}\n")
        
        # STYLE401-412: symbols
        idx = 11
        for s in ['+','-','*','/','=','%','.',',','?','@','`','~']:
            css_parts.append(f"[STYLE{400+idx-10}]={s}\nNM_IMG=plus,{idx}\nHL_IMG=plus,{idx}\n")
            idx+=1
        
        # STYLE501-510: text indicators
        for i in range(501,511):
            css_parts.append(f"[STYLE{i}]\nNM_IMG=texts,{i-500}\nHL_IMG=texts,{i-500}\n")
        
        # STYLE611-614: spplus (双拼)
        idx = 1
        for s in ['zh','ch','sh','~']:
            css_parts.append(f"[STYLE{610+idx}]={s}\nNM_IMG=add_sp,{idx}\nHL_IMG=add_sp,{idx}\n")
            idx+=1
        
        z.writestr("res/default.css", "\n".join(css_parts))
        
        # === INI files ===
        gen = f"""[INPUT]
BACK_STYLE=101
FORE_STYLE=102

[CAND]
VIEW_RECT=0,0,800,60
LAYOUT_NAME=cand1
TYPE=4

[PANEL]
BACK_STYLE=103
FORE_STYLE=102
SIZE=800,245

[MORE]
GRID=4,5
SYM_LAYOUT=symbol
LAYOUT_NAME=sel_ch
FORE_STYLE=105
CELL_STYLE=106
CELL_SIZE=50,50

[HINT]
LAYOUT_NAME=hint1
TYPE=0

[LIST]
BACK_STYLE=121
CELL_STYLE=123
FORE_STYLE=123
CELL_SIZE=57,60
POS=33,43
VIEW_RECT=0,0,800,118

[KEY60]
CELL_STYLE=133
FORE_STYLE=133
PADDING=10,10,10,10

[KEY61]
STYLE=106
VIEW_RECT=10,452,96,70
HOLD=F50

[KEY63]
VIEW_RECT=10,452,96,70
HOLD=F50

[KEY64]
STYLE=106
VIEW_RECT=700,452,96,70

[KEY65]
STYLE=106
VIEW_RECT=700,108,100,60
"""
        
        cand_ini = """[INPUT]
BACK_STYLE=101
FORE_STYLE=102

[CAND]
VIEW_RECT=0,0,800,60
LAYOUT_NAME=cand1
TYPE=4

[PANEL]
BACK_STYLE=103
FORE_STYLE=102
SIZE=800,245

[MORE]
GRID=4,5
SYM_LAYOUT=symbol
LAYOUT_NAME=sel_ch
FORE_STYLE=105
CELL_STYLE=106
CELL_SIZE=50,50

[HINT]
LAYOUT_NAME=hint1
TYPE=0

[LIST]
BACK_STYLE=121
CELL_STYLE=123
FORE_STYLE=123
CELL_SIZE=57,60
POS=33,43
VIEW_RECT=0,0,800,118

[KEY60]
CELL_STYLE=133
FORE_STYLE=133
PADDING=10,10,10,10

[KEY61]
STYLE=106
VIEW_RECT=10,452,96,70
HOLD=F50

[KEY63]
VIEW_RECT=10,452,96,70
HOLD=F50

[KEY64]
STYLE=106
VIEW_RECT=700,452,96,70

[KEY65]
STYLE=106
VIEW_RECT=700,108,100,60
"""
        
        cand_cnd = """[TAB]
BACK_STYLE=113
FORE_STYLE=113
PADDING=0,0,50,0
CELL_STYLE=113
CELL_W=40

[CAND]
BACK_STYLE=113
FORE_STYLE=113
CELL_STYLE=113
PADDING=0,0,50,0
FIRST_GAP=12
CELL_W=40
"""
        
        hint = """[TIP0]
STYLE=151
PADDING=20,48,0,0
VIEW_RECT=0,200,800,48
POSITION=0,-50,80,
"""
        
        mini_ini = """[INPUT]
BACK_STYLE=101
FORE_STYLE=102

[CAND]
VIEW_RECT=0,0,800,60
LAYOUT_NAME=cand1
TYPE=4

[PANEL]
BACK_STYLE=103
FORE_STYLE=102
SIZE=800,245

[MORE]
GRID=4,5
SYM_LAYOUT=symbol
LAYOUT_NAME=sel_ch
FORE_STYLE=105
CELL_STYLE=106
CELL_SIZE=50,50

[HINT]
LAYOUT_NAME=hint1
TYPE=0

[LIST]
BACK_STYLE=121
CELL_STYLE=123
FORE_STYLE=123
CELL_SIZE=57,60
POS=33,43
"""
        
        modes = ['en_26','en_26s','en_9','en_9s','py_26','py_9','num_26','num_9','symbol','sel_ch','sel_en','bh','hw_full','hw_grid','symbol_hw','def_26_list']
        
        for mode_dir in ['land','port']:
            z.writestr(f"{mode_dir}/gen.ini", gen)
            z.writestr(f"{mode_dir}/def_26.ini", cand_ini)
            z.writestr(f"{mode_dir}/cand0.cnd", cand_cnd)
            z.writestr(f"{mode_dir}/hint1.pop", hint)
            for m in modes:
                z.writestr(f"{mode_dir}/{m}.ini", mini_ini)
        
        # === PNG placeholders ===
        for img in ['back','graph','en','plus','pluss','bh6','texts','add_sp']:
            z.writestr(f"res/{img}.png", mkpng(16,16,26,26,46))
        
        # === .til files (九宫格切片配置) ===
        til = """[GLOBAL]
USE_ALPHA=2
TILE_NUM=1

[IMG1]
SOURCE_RECT=0,0,80,312
INNER_RECT=34,21,18,270
SCALE=1,1,1,1,1
"""
        z.writestr("res/back.til", til)
    
    import os
    print(f"OK {output} ({os.path.getsize(output)} bytes, platform={platform_code})")

if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv)>1 else 'MySkin'
    auth = sys.argv[2] if len(sys.argv)>2 else 'Akino'
    out = sys.argv[3] if len(sys.argv)>3 else 'skin.bds'
    plat = 'a'
    if '--platform' in sys.argv:
        idx = sys.argv.index('--platform')
        if idx+1 < len(sys.argv):
            plat = sys.argv[idx+1]
    create(name, auth, out, plat)
