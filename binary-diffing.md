---
name: binary-diffing
description: "二进制Diffing与补丁分析。对比两个二进制文件的差异，定位修改点，用于1-day漏洞研究和恶意软件变体分析。TRIGGER when: 用户需要对比二进制差异或分析补丁"
license: MIT
compatibility: Requires IDA Pro or Ghidra, Diaphora or BinDiff
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
---

# 二进制Diffing

## 触发条件

用户需要：
- 对比patch前后二进制，定位修改
- 分析1-day漏洞（对比旧版本和新版本）
- 对比恶意软件变体差异
- 分析固件更新变化

## 工具链

### Diaphora（推荐，免费开源）
```bash
# IDA插件安装
# 下载 diaphora.py 放入 IDA plugins 目录

# IDA中使用
# 1. 打开旧版本二进制
# 2. Plugins → Diaphora → Export
# 3. 打开新版本二进制
# 4. Plugins → Diaphora → Import & Diff
```

### BinDiff（Google出品）
```bash
# 需要先用BinExport导出
# IDA/Ghidra中导出 .BinExport 文件

# BinDiff对比
bindiff primary.BinExport secondary.BinExport
```

### qbindiff（实验性，边缘case更优）
```bash
pip install qbindiff
# 使用BinExport或Quokka格式
```

## 分析流程

### Step 1: 导出分析结果
```bash
# IDA + Diaphora
# File → Produce File → Diaphora Export

# Ghidra + BinExport
# Tools → BinExport
```

### Step 2: 对比
```bash
# Diaphora: 自动匹配20+启发式
# BinDiff: 函数级匹配
```

### Step 3: 分析差异
- 相似度高的函数：可能是修改点
- 新增函数：可能是新功能或补丁
- 删除函数：可能是移除的漏洞代码

## 使用场景

### 1-day漏洞研究
```bash
# 流程：旧版本(有漏洞) vs 新版本(已修复)
# 1. 导出两个版本
# 2. 对比找到修改的函数
# 3. 分析修改内容，还原漏洞
```

### 恶意软件变体分析
```bash
# 对比不同版本恶意软件
# 找到新增/修改的功能
# 分析C2通信变化
```

## 知识库引用

- `~/.hermes/knowledge/re-engineering/binary-diffing/` — Diaphora + BinExport工具
