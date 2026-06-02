---
name: ast-deobfuscation
description: 使用 Babel AST 对 JavaScript 做分层、可回退的定向反混淆。7步流程 + 三层自动架构（通用→检测→适配）+ 8站点适配器。支持 sojson、obfuscator.io、reese84、顶象、极验4、同花顺、网易易盾、小红书等。
author: 7452323 (converted from Private Gist)
version: "1.0.0"
tags:
  - ast
  - babel
  - deobfuscation
  - javascript
  - reverse-engineering
  - control-flow-flattening
  - string-decryption
---

# AST 反混淆技能

工具链: `@babel/parser` + `@babel/traverse` + `@babel/generator` + `@babel/types`

## 技能协作链

| 技能 | 职责 |
|------|------|
| ast-deobfuscation（本技能） | AST 静态反混淆：字符串解密、常量折叠、控制流还原、死代码删除 |
| env-patch | 运行时环境补丁，沙箱执行 |
| find-crypto-entry | 定位加密算法入口 |
| algorithm-reverse | 逆向加密算法实现 |
| webpack-unpack | Webpack bundle 拆包 |

典型协作链: `ast-deobfuscation → find-crypto-entry → algorithm-reverse`

## 三层自动架构

### 第1层：通用变换层（所有输入必经）
- 结构标准化（逗号表达式拆分、方括号转点号）
- 常量折叠与布尔值还原
- Proxy 函数与对象字典内联
- 虚假分支清理
- 死代码移除

### 第2层：混淆检测层
自动检测混淆家族并加载对应适配器：
- sojson v6/v7
- obfuscator.io
- awsc（阿里云）
- jjencode
- jsconfuser
- 通用 eval/packer

### 第3层：站点适配层
针对特定站点的定制化适配器：
- reese84
- 顶象
- 极验4
- 同花顺
- 网易易盾
- 小红书

## 7步流程

```
Step 0: 混淆检测 + 评估
Step 1: 字符串解密（沙箱执行解密函数）
Step 2: 常量折叠
Step 3: 控制流平坦化还原
Step 4: 死代码删除
Step 5: 变量重命名（可选）
Step 6: 代码格式化输出
```

每步结果自动验证，出错时回退到上一步输出，保证至少返回格式化代码。
