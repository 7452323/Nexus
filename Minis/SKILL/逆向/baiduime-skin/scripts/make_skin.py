import zipfile, os, struct, zlib, sys

PNG_1PX = bytes.fromhex('89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de0000000c49444154789c633871e2040004b40259162e81400000000049454e44ae426082')

def make_png(w=1,h=1,r=200,g=200,b=200):
    sig=b'\x89PNG\r\n\x1a\n'
    ihdr=b'IHDR'+struct.pack('>IIBBBBB',w,h,8,2,0,0,0)
    ihdr_chunk=struct.pack('>I',13)+ihdr+struct.pack('>I',zlib.crc32(ihdr))
    raw=b'\x00'+bytes([r,g,b])*w*h
    idat=zlib.compress(raw)
    idat_chunk=struct.pack('>I',len(idat))+b'IDAT'+idat+struct.pack('>I',zlib.crc32(b'IDAT'+idat))
    iend_chunk=struct.pack('>I',0)+b'IEND'+struct.pack('>I',zlib.crc32(b'IEND'))
    return sig+ihdr_chunk+idat_chunk+iend_chunk

def create_skin(name, author, output, style='default', desc='Custom Baidu IME skin by Akino'):
    """Generate complete Baidu IME skin (.bds) from parameters."""
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        # === Info.txt ===
        z.writestr("Info.txt", f"Name={name}\nStyle=Default\nSupportPlatform=SWIA\nAuthor={author}\n")
        
        # === res.ini (style registry) ===
        res = """[res]
back1=@bg.png;0,0,800,250
back2=@key_bg.png;0,0,70,60
back3=@space_bg.png;0,0,200,60
fore1=@enter.png;0,0,80,60

"""
        for i,c in enumerate('qwertyuiopasdfghjklzxcvbnm',1):
            res += f"fore{i+1}=@{c}_n.png;0,0,60,60\n"
        
        z.writestr("res.ini", res)
        
        # === ini templates ===
        gen_ini = """[INPUT]
BACK_STYLE=1
FORE_STYLE=2
CENTER=""

[CAND]
VIEW_RECT=0,0,800,60
LAYOUT_NAME=cand1
TYPE=4

[PANEL]
BACK_STYLE=4
FORE_STYLE=2
SIZE=800,260

[MORE]
GRID=4,5
SYM_LAYOUT=symbol
LAYOUT_NAME=sel_ch
FORE_STYLE=6
CELL_STYLE=7
CELL_SIZE=50,50

[HINT]
LAYOUT_NAME=hint1
TYPE=0

[LIST]
BACK_STYLE=3
CELL_STYLE=3
FORE_STYLE=2
"""
        key_ini = """[INPUT]
BACK_STYLE=1
FORE_STYLE=2
VIEW_RECT=0,0,0,0
CENTER=""

[PANEL]
BACK_STYLE=4
FORE_STYLE=2
VIEW_RECT=0,0,0,0

[MORE]
GRID=4,5
SYM_LAYOUT=symbol
LAYOUT_NAME=sel_ch
FORE_STYLE=6
CELL_STYLE=7
CELL_SIZE=50,50

[CAND]
VIEW_RECT=0,0,800,60
LAYOUT_NAME=cand1
TYPE=4

[HINT]
LAYOUT_NAME=hint1
TYPE=0

[KEY1]
BACK_STYLE=3
FORE_STYLE=2
VIEW_RECT={x},{y},{w},{h}
UP={i}
CENTER={c}

"""
        cand_xml = """[TAB]
BACK_STYLE=117
FORE_STYLE=129
PADDING=0,0,50,0
CELL_STYLE=132
CELL_W=40

[CAND]
BACK_STYLE=117
FORE_STYLE=129
CELL_STYLE=132
PADDING=0,0,50,0
FIRST_GAP=12
CELL_W=40
"""
        
        # === Write land and port modes ===
        for mode in ['land','port']:
            z.writestr(f"{mode}/gen.ini", gen_ini)
            z.writestr(f"{mode}/cand0.cnd", cand_xml)
            
            # 24 letter keys (Q W E R T Y U I O P A S D F G H J K L Z X C V B N)
            keys_def = "qwertyuiopasdfghjklzxcvbn"
            for i, c in enumerate(keys_def, 1):
                x = 10 + ((i-1) % 10) * 78
                y = 90 + ((i-1) // 10) * 75
                z.writestr(f"{mode}/key_{i}.ini", key_ini.format(x=x,y=y,w=70,h=60,i=i,c=c))
            
            # Function keys
            z.writestr(f"{mode}/enter.ini","""[INPUT]
BACK_STYLE=1
FORE_STYLE=2

[KEY25]
BACK_STYLE=5
CENTER=F49
VIEW_RECT=0,0,450,65
HOLD=F50
""")
            z.writestr(f"{mode}/symbol.ini","""[INPUT]
BACK_STYLE=1
FORE_STYLE=2

[KEY30]
BACK_STYLE=8
CENTER=F48
VIEW_RECT=10,295,90,65
""")
        
        # === 占位图片 ===
        for img in ['bg.png','key_bg.png','space_bg.png','enter.png']:
            z.writestr(f"res/{img}", PNG_1PX)
        
        for c in 'qwertyuiopasdfghjklzxcvbnm':
            z.writestr(f"res/{c}_n.png", PNG_1PX)
            
    print(f"OK: {output} ({os.path.getsize(output)} bytes)")

if __name__ == '__main__':
    n = sys.argv[1] if len(sys.argv)>1 else 'MySkin'
    a = sys.argv[2] if len(sys.argv)>2 else 'Akino'
    o = sys.argv[3] if len(sys.argv)>3 else 'output.bds'
    create_skin(n,a,o)
