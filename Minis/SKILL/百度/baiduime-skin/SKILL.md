---
name: baiduime-skin
description: "百度输入法皮肤/主题制作技能。从 ini 配置结构、图片素材规范、到一键生成 .bds 皮肤包，全流程覆盖。含 Python 自动生成器 make_skin.py，输入主题名和 RGB 色值即可输出完整皮肤包。"
tags: [百度输入法, 输入法皮肤, baiduime, 主题制作, ini配置, bds格式, 键盘布局]
---

# 百度输入法皮肤制作技能

## 一、文件结构

百度输入法皮肤 `.bds` 本质是 **ZIP 压缩包**：

```
MySkin.bds
├── Info.txt          ← 皮肤元数据（名称/作者）
├── res.ini           ← 样式注册表（ID → 图片映射）
├── demo.png          ← 预览图（可选）
├── land/             ← 横屏布局
│   ├── gen.ini       ← 全局输入区/候选词/面板/更多
│   ├── def_26.ini    ← 26键默认键盘
│   ├── def_9.ini     ← 9键默认键盘
│   ├── en_26.ini     ← 英文26键
│   ├── en_9.ini      ← 英文9键
│   ├── py_26.ini     ← 拼音26键
│   ├── py_9.ini      ← 拼音9键
│   ├── hw_full.ini   ← 手写全屏
│   ├── hw_grid.ini   ← 手写九宫格
│   ├── num_26.ini    ← 数字26键
│   ├── num_9.ini     ← 数字9键
│   ├── symbol.ini    ← 符号面板
│   ├── symbol_hw.ini ← 手写符号
│   ├── sel_ch.ini    ← 中文选择
│   ├── sel_en.ini    ← 英文选择
│   ├── sel_hw.ini    ← 手写选择
│   ├── cand.cnd      ← 候选词样式
│   ├── cand0.cnd     ← 候选词样式1
│   ├── cand1.cnd     ← 候选词样式2
│   ├── cand2.cnd     ← 候选词样式3
│   └── hint1.pop     ← 气泡提示样式
└── port/             ← 竖屏布局（同 land 结构）
    └── ...
```

## 二、核心 ini 格式

### 2.1 Info.txt

```
Name=我的皮肤
Style=Default
SupportPlatform=SWIA
Author=Akino
```

### 2.2 res.ini（样式注册表）

```
[res]
back1=@bg.png;0,0,800,250              ← back1 → 背景图 bg.png，裁剪区域 (0,0,800,250)
back2=@key_bg.png;0,0,70,60           ← 按键背景
back3=@space_bg.png;0,0,200,60        ← 空格键背景
fore1=@enter.png;0,0,80,60            ← 回车键前景（图片）
fore2=@q_n.png;0,0,60,60              ← 字符 q 前景
fore3=@w_n.png;0,0,60,60              ← 字符 w 前景
...
```

格式：`ID=@{图片文件名};{x,y,w,h}` — 裁剪区域从大图中切出该按键图。

### 2.3 gen.ini（全局配置）

```
[INPUT]            ← 输入区整体
BACK_STYLE=1       ← 背景 → res 里的 back1
FORE_STYLE=2       ← 前景 → res 里的 key_bg
CENTER=""          ← 前景居中

[CAND]             ← 候选词区
VIEW_RECT=0,0,800,60
LAYOUT_NAME=cand1  ← 引用 cand1.cnd
TYPE=4

[PANEL]            ← 键盘面板
SIZE=800,260
BACK_STYLE=4
FORE_STYLE=2

[MORE]             ← 更多符号面板
GRID=4,5
SYM_LAYOUT=symbol
CELL_STYLE=7
CELL_SIZE=50,50

[HINT]             ← 气泡提示
LAYOUT_NAME=hint1

[LIST]             ← 列表背景
BACK_STYLE=3
CELL_STYLE=3
```

### 2.4 def_26.ini（26键键盘 — 核心）

```
[KEY1]                  ← 按键 1（q 键位置）
BACK_STYLE=3            ← 背景 → res 里的 key_bg
FORE_STYLE=24           ← 前景 → res 里的字母 q 图
VIEW_RECT=34,95,96,82   ← 按键矩形：x=34, y=95, 宽=96, 高=82
UP=1                    ← 上滑输出 1（数字）
CENTER=q                ← 居中显示 q

[KEY2]
BACK_STYLE=3
FORE_STYLE=23
VIEW_RECT=139,95,96,82
UP=2
CENTER=w

...

[KEY24]                 ← 回车键
BACK_STYLE=5            ← 空格背景
CENTER=F49             ← F49=换行

[KEY25]                 ← 空格键
BACK_STYLE=5
CENTER=F49

[KEY60]                 ← 列表背景
CELL_STYLE=8

[KEY61]                 ← shift/中英切换
CENTER=F45

[KEY63]                 ← 空格
BACK_STYLE=5

[KEY81]                 ← 符号键
CENTER=F48

[KEY82]
CENTER=F1

[KEY83]                 ← 返回
CENTER=F4
```

### 2.5 按键事件代码表

| 代码 | 功能 |
|------|------|
| F1 | 切换到符号 |
| F4 | 返回 |
| F45 | 中英切换 |
| F48 | 符号面板 |
| F49 | 换行 |
| F50 | 长按切换 |
| CENTER="abc" | 居中显示文字 |

### 2.6 candX.cnd（候选词样式）

```
[TAB]
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
```

### 2.7 hint1.pop（气泡提示）

```
[TIP0]
BACK_STYLE=202
FORE_STYLE=203
PADDING=20,48,0,0
VIEW_RECT=0,200,800,48
POSITION=0,-50,80,
```

## 三、图片素材规范

### 3.1 文件格式

| 项目 | 要求 |
|------|------|
| 格式 | PNG 24bit（透明通道） |
| 分辨率 | 一套: 800×250 背景 + 60×60 按键字图 |
| 命名 | `res/{字母}_n.png`（_n = normal 状态） |
| 大小 | 单按键图 50-200KB | 
| 适配 | 提供 land/ 和 port/ 两套布局 |

### 3.2 必备素材清单

- `res/bg.png` — 键盘背景图（含所有层的底色）
- `res/{a-z}_n.png` — 26 个字母按键前景
- `res/enter.png` / `space.png` — 功能键
- `res/key_bg.png` — 按键背景底图
- `res/symbol_n.png` — 符号键图

### 3.3 图片命名约定

```
_res/normal/      正常状态
_res/down/        按下状态  
_res/up/          上滑状态
```

单按键文件名：`i_fore{N}_n_{x}_{y}_{w}_{h}.png`
- N = 序号，n = normal，x/y/w/h = 在大图中的裁剪坐标

## 四、一键生成 Python 脚本

```python
scripts/make_skin.py [皮肤名] [作者] [输出.bds]
```

输入主题名和十六进制色值，自动生成完整 BDS 包 + 占位素材。

```bash
python3 scripts/make_skin.py "Ocean" "Akino" ocean.bds
```

输出：22KB 含 60+ ini 文件 + 30 张占位 PNG。

### 4.1 自定义后替换素材

占位图是 1×1 像素灰色 PNG。要正式打包：
1. 按 `res.ini` 里的命名规范准备 PNG 资源
2. 覆盖 `res/` 对应文件
3. 重新 zip 打包为 .bds

## 五、安装与应用

### 5.1 手动安装

1. 把 `skin.bds` 文件放入手机
2. 百度输入法 → 超级皮肤 → 本地 → 选择文件
3. 应用

### 5.2 通过 ADB（开发调试）

```bash
adb push skin.bds /sdcard/baidu/ime/skins/
adb shell am broadcast -a com.baidu.input.skin.REFRESH
```

### 5.3 常见问题

| 问题 | 解法 |
|------|------|
| 安装失败 | 检查 Info.txt UTF-8 编码、ZIP 无损坏 |
| 按键错位 | VIEW_RECT 检查坐标和宽高 |
| 材质不显示 | res.ini 文件名和 ini 中 BACK_STYLE/FORE_STYLE ID 对应 |
| 候选词不显示 | cand.cnd LAYOUT_NAME 一致 |
| 9键和26键不兼容 | 两套 ini 都要写，不能只给一套 |

## 六、逆向现成皮肤

借壳学习（Gearkey 项目格式）：

```bash
unzip some_skin.bds -d skin_src/
cat skin_src/res.ini
cat skin_src/land/def_26.ini
```

GearKey 解包格式参考：
- `land/def_26.ini` 行数 ≈ 300+ 行
- `land/en_26.ini` 英文布局单独一套
- `port/` 竖屏布局 DPI 不同

## 七、进阶：可视化皮肤编辑器思路

如果要做一个可视化编辑器：

1. **画布层** — 拖拽按键、调整 VIEW_RECT（x,y,w,h）
2. **样式面板** — 设置 FORE_STYLE ID → 选择对应素材
3. **预览层** — 调用系统画图 API 渲染 ini 配置到预览图
4. **打包层** — 调用 `scripts/make_skin.py` 生成最终 bds

## 八、参考项目

| Stars | 项目 | 特点 |
|-------|------|------|
| ⭐17 | Gearkey/baidu_input_skins | 🔥 最近活跃，有 BG C 工具 |
| ⭐3 | vancolate/baidu-input-skin-saved | 纯皮肤包 |
| ⭐3 | bencn/BSkin | 制作工具 |
| ⭐2 | ShenHongFei/baidu-ime-skin-moui-pure | 纯净皮 |
