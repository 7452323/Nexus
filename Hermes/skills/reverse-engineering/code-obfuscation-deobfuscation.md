---
name: code-obfuscation-deobfuscation
description: 代码混淆分析+反混淆playbook。覆盖 JS/Python/Android/通用混淆类型识别、分析工具链和还原策略。
author: 7452323 (converted from Private Gist)
tags:
  - obfuscation
  - deobfuscation
  - code-analysis
  - reverse-engineering
---

# Code Obfuscation & Deobfuscation — 代码混淆分析与反混淆

## 混淆类型通用识别

| 混淆类型 | 特征 | 主要平台 |
|----------|------|----------|
| Renaming | 变量/函数名替换为无意义字符 | JS/Python/Java |
| String Encryption | 字符串编码/加密+运行时解密 | JS/Android |
| Control Flow | 代码结构被打乱（flat/Opaque） | JS/Android |
| Data Encoding | 数据编码（Base64/Hex/自定义） | 全平台 |
| Dead Code | 插入无意义代码 | 全平台 |
| Self-Modifying | 代码运行时修改自身 | JS/Native |
| Anti-Tamper | 完整性校验 | Android/Native |
| Virtualization | 自定义VM执行 | JS/Android |

## 反混淆通用流程

1. 识别混淆类型（特征匹配）
2. 字符串解密（优先执行）
3. 常量折叠
4. 死代码移除
5. 控制流还原
6. 命名还原（reverse renaming）
7. 代码格式化

## 各语言工具

| 语言 | 工具 |
|------|------|
| JavaScript | Babel（parser/traverse/generator）、js-beautify、de4js |
| Python | uncompyle6/decompyle3（pyc）、unpyc37 |
| Android | jadx、apktool、dextractor |
| .NET | dnSpy、de4dot |
| Java | procyon、cfr、fernflower |
