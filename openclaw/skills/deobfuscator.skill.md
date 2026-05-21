---
name: deobfuscator
description: "JavaScript/通用代码反混淆解密技能 — 针对 jsjiami/sojson/obfuscator.io/packer/jsfuck/RC4/Base64/ProGuard 等常见加密混淆一键还原"
author: 7452323
version: "2.0.0"
tags:
  - deobfuscation
  - javascript
  - decryption
  - reverse-engineering
  - obfuscator
---

# deobfuscator — 代码反混淆解密技能

## 能处理什么

|混淆类型|特征|解密方法|来源|
|---|---|---|---|---|
|**jsjiami v6 / sojson**|`jsjiami.com` `sojson.com` 水印, `_0x`变量, 前3句为签名+预处理+解密函数|隔离沙箱执行解密函数, AST回填字符串|decode_action|
|**jsjiami v7**|v7版, 首行声明变量表, 加密函数含主变量引用|先分离字符串表, 再沙箱执行解密|decode_action|
|**obfuscator.io**|大量`_0x` + 自执行数组 + 控制流扁平化|数组展开 → 常量折叠 → 控制流还原 → 死代码删除|decode_action/v_jstools|
|**awsc (阿里云混淆)**|阿里云CDN默认混淆, 特征`_0x`|同obfuscator方案处理|decode_action|
|**jjencode**|以 `$=~[];$={...}` 开头的自编码|jjdecode专用恢复|decode_action|
|**jsconfuser**|特征`smEcV`|专用反混淆插件|decode_action|
|**Dean Edwards Packer**|`eval(function(p,a,c,k,e,d)`|自动解包|经典|
|**JSFuck**|仅由 `[]()!+`|解释器还原|经典|
|**eval/atob嵌套**|多层 `eval(atob(...))`|递归eval展开|经典|
|**Python压缩**|zlib/bz2/lzma/gzip + base64多层嵌套|递归解压直到不可再解|decode_action|
|**Google Closure**|`a.b=c`式重命名|需源码映射, 部分还原|经典|
|**ProGuard (Android)**|`a.a.a()`|映射文件反混淆|经典|

## 企业软件密码解密

来自 DecryptTools 项目（wafinfo/DecryptTools），专门针对国产企业软件的配置密码解密：

|软件|加密类型|解密方法|
|---|---|---|
|万户OA|自定义|工具内集成|
|用友NC|AES|工具内集成|
|金蝶EAS|自定义|工具内集成|
|致远OA|AES/GZIP|字符串解密|
|蓝凌OA|SM4/DES|SM4解密|
|帆软报表|自定义|数据库密码解密|
|海康威视|AES|设备配置解密|
|Navicat|AES-128-CBC|密码解密|
|FinalShell|AES|连接配置解密|
|WebLogic|AES|数据库密码解密|
|Druid|AES|数据库密码解密|
|Spring (Jasypt)|PBE/AES|配置解密|
|H3C CAS|自定义|配置文件解密|

## 工作流程

```
1. 检测混淆类型
   ↓
2. 识别加密函数（sojson:前3句 obfuscator:自执行数组 packer:正则特征）
   ↓
3. 沙箱执行解密函数（用 isolated-vm 安全执行，获取解密映射表）
   ↓
4. AST 回填（将 _0x1234('0x1') 替换为真实字符串）
   ↓
5. AST 净化
   ├─ 常量折叠（calculate-constant-exp）
   ├─ 控制流平坦化还原（parse-control-flow-storage）
   ├─ If分支修剪（prune-if-branch）
   ├─ 死变量删除（delete-unused-var）
   ├─ 序列表达式拆分（split-sequence）
   ├─ 合并对象字面量（merge-object）
   └─ 代码格式化
   ↓
6. 输出可读代码
```

## 推荐工具链

|工具|用途|安装|
|---|---|---|
|@babel/parser|JS→AST解析|`npm i @babel/parser`|
|@babel/traverse|AST遍历|`npm i @babel/traverse`|
|@babel/generator|AST→JS|`npm i @babel/generator`|
|isolated-vm|安全沙箱执行解密函数|`npm i isolated-vm`|
|js-beautify|代码格式化|`npm i js-beautify`|

## decode_action 自动化方案（推荐）

利用 GitHub Actions 自动解密：

1. fork `smallfawn/decode_action`
2. 把待解密代码放入 `input.js`（JS）或 `input.py`（Python）
3. 手动触发 Action → 等待 60s
4. 解密结果在 `output.js` / `output.py`

**支持的 Python 压缩格式：** zlib, bz2, lzma, gzip
**支持的 JS 混淆：** sojson v6, sojson v7, obfuscator, awsc, jjencode, jsconfuser, common

## AST 反混淆核心原理

### 沙箱执行解密函数

```javascript
// sojson/obfuscator 的核心—加密函数必须实际执行才能获得解密映射
const ivm = require('isolated-vm');
const isolate = new ivm.Isolate();
const context = isolate.createContextSync();

function safeEval(code) {
  return context.evalSync(String(code));
}
```

### 插件链架构（from decode_action）

```
Plugin: sojson / sojsonv7 / obfuscator / awsc / jjencode / jsconfuser / common
                ↓
AVT Visitor: calculate-constant-exp / delete-unused-var / parse-control-flow-storage
             prune-if-branch / split-sequence / merge-object / lint-if-statement
                ↓
         output.js
```

## 常用解密命令

### Node.js 环境解密

```bash
# 基础 eval 递归展开
node -e "
function deobf(code) {
  while (code.includes('eval')) {
    try { code = eval(code); } catch(e) { break; }
  }
  console.log(code);
}
deobf(require('fs').readFileSync('input.js','utf8'));
"

# 提取并展开所有函数字符串
node -e "
const fs = require('fs');
let code = fs.readFileSync('input.js', 'utf8');
const matches = code.match(/"[\w+/=]{20,}"/g) || [];
for (const m of matches) {
  try {
    const decoded = Buffer.from(m.slice(1,-1), 'base64').toString();
    code = code.replace(m, JSON.stringify(decoded));
  } catch(e) {}
}
console.log(code);
"
```

### jsjiami/sojson 专用解密（AST + 字符串回填）

```javascript
// 用 @babel/parser + @babel/generator 做 AST 解密
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generator = require('@babel/generator').default;
const t = require('@babel/types');

function deobfuscate(code) {
  const ast = parser.parse(code);

  // 1. 解密所有字符串调用，如 _0x1234('0x1') → 真实字符串
  traverse(ast, {
    CallExpression(path) {
      // 匹配 _0x...('0x...') 调用模式
      const callee = path.node.callee;
      if (t.isIdentifier(callee) && /^_0x/.test(callee.name)) {
        const arg = path.node.arguments[0];
        if (t.isStringLiteral(arg)) {
          try {
            // 执行解密函数获取真实值
            const decrypted = decryptString(callee.name, arg.value);
            path.replaceWith(t.stringLiteral(decrypted));
          } catch(e) {}
        }
      }
    },
    // 2. 移除死代码/花指令
    ExpressionStatement(path) {
      if (t.isStringLiteral(path.node.expression)) {
        path.remove();  // 单独的字符串语句（花指令）
      }
    }
  });

  const output = generator(ast, { retainLines: false, compact: false });
  return output.code;
}
```

### Packer 解包

```javascript
// Dean Edwards Packer — 特征: eval(function(p,a,c,k,e,d)
function unpackPacker(code) {
  const match = code.match(/eval\(function\(p,a,c,k,e,d\)\{[\s\S]*?\}(?:\([\s\S]*?\))\)/);
  if (!match) return code;

  let packed = match[0];
  // 提取字典表
  const dictMatch = packed.match(/\|([^|]+)\|/);
  if (!dictMatch) return code;

  // 提取主体
  const bodyMatch = packed.match(/while\(c--\)\{[\s\S]*?\}/);
  if (!bodyMatch) return code;

  // 用 p,a,c,k 参数重建
  const dict = dictMatch[1].split('|');
  let result = packed;
  for (let i = 0; i < dict.length; i++) {
    const regex = new RegExp('\\b' + i.toString().replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'g');
    result = result.replace(regex, dict[i]);
  }
  return result;
}
```

## 常见混淆模式识别

|特征|混淆类型|
|---|---|
|`jsjiami.com` / `sojson.com`|jsjiami|
|大量 `_0x[0-9a-f]{4,6}` 变量|obfuscator.io / jsjiami|
|`function(p,a,c,k,e,d)`|Packer|
|只有 `[]()!+`|JSFuck|
|`eval(atob(`|Base64嵌套|
|`a=b=c=d` 重命名|Closure Compiler|
|`String.fromCharCode`|Unicode编码|
|`\\x[0-9a-f]{2}` 连续出现|Hex编码|

## 随附实用工具

本技能附带一个可直接使用的 Node.js 脚本:

```bash
# 在仓库根目录:
node scripts/deobfuscate.js input.js            # 解密 → input.clean.js
node scripts/deobfuscate.js input.js -o out.js   # 指定输出文件
node scripts/deobfuscate.js input.js --inspect   # 仅检测混淆类型
```

功能: 混淆类型检测 + Packer解包 + eval递归展开 + unicode/hex解码 + js-beautify格式化

## 解密工具推荐


|工具|用途|地址|
|---|---|---|
|babel/parser|JS AST解析|npm i @babel/parser|
|js-beautify|代码格式化|npm i js-beautify|
|synchrony|图形化反混淆|GitHub开源|
|de4js|在线反混淆|lelinhtinh.github.io/de4js|
|unpacker|Packer解包|GitHub开源|
|AST Explorer|AST可视化|astexplorer.net|

## 注意事项

- 只处理你自己拥有或有权反编译的代码
- 遵守开源协议，尊重作者版权
- jsjiami 有反调试（anti-debugger），解包时注意关掉开发者工具
- 部分混淆（jsjiami自卫模式）需要运行时提取解密函数，静态分析可能不够
