---
name: decrypt
description: Base/Hex/Hash/AES/RC4/jsjiami/decode_action全链路
---

# 🔓 解密工具箱

## jsjiami 10款产品
V6: RC4+Base64+控制流+反调试+域名锁
V7: 多态+抗格式化+Anti-Selenium+自卫模式

### 5级反混淆流程
1.识别版本→2.格式化→3.字符串解密→4.AST控制流还原→5.反调试绕过

## decode_action 7插件+16Visitor
sojson/sojsonv7/obfuscator/awsc/jsconfuser/jjencode/common

### 16个AST Visitor
calculate-constant-exp, calculate-rstring, parse-control-flow-storage, merge-object, prune-if-branch, split-sequence, delete-unused-var, delete-unreachable-code, delete-nested-blocks, delete-illegal-return, delete-extra, split-assignment, split-member-object, split-variable-declaration, lint-if-statement, check-func

## Python解密
try_decompress(gzip/bz2/zlib/lzma), try_decode_base64, decrypt_nested

## 通用反混淆流程
识别→字符串解密→常量折叠→死代码移除→控制流还原→命名还原→格式化
