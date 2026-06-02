---
name: pyinstaller-reverse
description: PyInstaller 打包 Python 应用逆向技能。特征识别 → pyinstxtractor 解包 → pycdc/uncompyle6 反编译 → 逻辑还原全流程。
author: 7452323 (converted from Private Gist)
category: reverse-engineering
tags:
  - pyinstaller
  - python
  - decompile
  - pyc
---

# PyInstaller Reverse — PyInstaller 打包应用逆向

## 适用场景

- Python 应用被 PyInstaller 打包为单个 exe/Linux 二进制
- 目标文件 5MB+，strings 有 Python 特征
- 需要提取原始 Python 源码或配置

## 识别

```bash
# 检查 PyInstaller 特征
file target.exe
strings target.exe | grep -iE "pyinstaller|PyInstaller|_MEIPASS|bootloader"
strings target.exe | grep -iE "python|\.pyc|__pycache__"

# PyInstaller 特征标记：
# - _MEIPASS 环境变量
# - 打包的 .pyc 文件
# - 特定版本 bootloader 签名
```

## 解包流程

```bash
# 1. 安装 pyinstxtractor
git clone https://github.com/extremecoders-re/pyinstxtractor.git

# 2. 解包
python3 pyinstxtractor/pyinstxtractor.py target.exe

# 输出到: target.exe_extracted/
# 包含: .pyc 文件 + PYZ 档案 + 依赖 DLL
```

## 反编译

```bash
# 方法一：uncompyle6
pip install uncompyle6
uncompyle6 target.exe_extracted/main.pyc > main.py

# 方法二：pycdc
# https://github.com/zrax/pycdc
./pycdc target.exe_extracted/main.pyc > main.py

# 方法三：pycdas（AST 反汇编，当反编译失败时）
./pycdas target.exe_extracted/main.pyc > main.ast
```

## 常见陷阱

| 问题 | 原因 | 解决 |
|------|------|------|
| `ImportError: Unknown magic number` | Python 版本不匹配 | 用对应 Python 版本的 pycdc |
| 反编译后语法错误 | 控制流优化残留 | 手动修复 + AST 分析 |
| 部分 .pyc 损坏 | PyInstaller 压缩 | 先用 `archive_viewer.py` 检查 |
| 找不到入口点 | 入口可能在 PYZ 档案中 | `python3 -m pyinstxtractor.cli --extract-pyz` |

## 关键信号提取

```bash
# 直接搜索 API key / URL / 配置
strings target.exe | grep -iE "api_key|token|secret|http|https://"
strings target.exe | grep -iE "config|\.env|\.json|password"

# 反编译后搜索敏感数据
grep -r "api_key\|token\|secret\|password" target.exe_extracted/
grep -r "requests\|http\|url\|endpoint" target.exe_extracted/
```

## 参考资源

- `pyinstxtractor`: https://github.com/extremecoders-re/pyinstxtractor
- `pycdc`: https://github.com/zrax/pycdc
- `uncompyle6`: https://github.com/rocky/python-uncompyle6/
