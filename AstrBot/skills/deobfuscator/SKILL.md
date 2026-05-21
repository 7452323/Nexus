# 反混淆器 (Deobfuscator)

## 描述
全面的 JavaScript 和通用代码反混淆技能。处理 jsjiami、sojson、obfuscator.io、packer、JSFuck、RC4、Base64、ProGuard 等常见混淆技术。使用基于 AST 的分析、解密函数沙箱执行和代码格式化来恢复可读代码。

## 指令

### 支持的混淆类型

| 类型 | 特征 | 处理方法 |
|------|---------|--------|
| **jsjiami v6 / sojson** | `jsjiami.com`/`sojson.com` 水印，`_0x` 变量，3条前导语句 | 沙箱执行解密函数，AST 字符串替换 |
| **jsjiami v7** | v7，变量表在第一行，加密函数带主变量引用 | 分离字符串表，沙箱执行 |
| **obfuscator.io** | 大量 `_0x` + 自执行数组 + 控制流平坦化 | 数组展开 → 常量折叠 → 控制流恢复 → 死代码清除 |
| **awsc（阿里云）** | 阿里云 CDN 默认混淆，`_0x` 特征 | 同 obfuscator.io |
| **jjencode** | 以 `$=~[];$={...}` 开头 | jjdecode 专用还原 |
| **jsconfuser** | `smEcV` 特征 | 专用反混淆插件 |
| **Dean Edwards Packer** | `eval(function(p,a,c,k,e,d)` | 自动解包 |
| **JSFuck** | 仅含 `[]()!+` 字符 | 解释器还原 |
| **eval/atob 嵌套** | 多层 `eval(atob(...))` | 递归 eval 展开 |
| **Python 压缩** | zlib/bz2/lzma/gzip + base64 嵌套 | 递归解压缩 |
| **Google Closure** | `a.b=c` 风格重命名 | 需要 Source Map，部分还原 |
| **ProGuard (Android)** | `a.a.a()` 风格 | 基于 Mapping 文件的反混淆 |

### 工作流程

```
1. 检测混淆类型
   ↓
2. 识别解密函数（sojson：3条前导语句，obfuscator：自执行数组，packer：正则模式）
   ↓
3. 沙箱执行解密函数（isolated-vm 安全执行，获取解密映射）
   ↓
4. AST 替换（将 _0x1234('0x1') 替换为实际字符串）
   ↓
5. AST 净化
   ├─ 常量折叠
   ├─ 控制流平坦化还原
   ├─ If 分支修剪
   ├─ 死变量清除
   ├─ 序列表达式拆分
   ├─ 对象字面量合并
   └─ 代码格式化
   ↓
6. 输出可读代码
```

### 工具链

| 工具 | 用途 | 安装方式 |
|------|---------|---------|
| @babel/parser | JS → AST 解析 | `npm i @babel/parser` |
| @babel/traverse | AST 遍历 | `npm i @babel/traverse` |
| @babel/generator | AST → JS | `npm i @babel/generator` |
| isolated-vm | 安全沙箱执行 | `npm i isolated-vm` |
| js-beautify | 代码格式化 | `npm i js-beautify` |

### 基本反混淆命令

```bash
# 递归 eval 展开（Node.js）
node -e "
function deobf(code) {
  while (code.includes('eval')) {
    try { code = eval(code); } catch(e) { break; }
  }
  console.log(code);
}
deobf(require('fs').readFileSync('input.js','utf8'));
"

# 提取并展开所有 base64 函数字符串
node -e "
const fs = require('fs');
let code = fs.readFileSync('input.js', 'utf8');
const matches = code.match(/\"[\\w+/=]{20,}\"/g) || [];
for (const m of matches) {
  try {
    const decoded = Buffer.from(m.slice(1,-1), 'base64').toString();
    code = code.replace(m, JSON.stringify(decoded));
  } catch(e) {}
}
console.log(code);
"
```

### 混淆模式识别

| 模式 | 类型 |
|---------|------|
| `jsjiami.com` / `sojson.com` | jsjiami |
| 大量 `_0x[0-9a-f]{4,6}` 变量 | obfuscator.io / jsjiami |
| `function(p,a,c,k,e,d)` | Packer |
| 仅含 `[]()!+` | JSFuck |
| `eval(atob(` | Base64 嵌套 |
| `a=b=c=d` 重命名 | Closure Compiler |
| `String.fromCharCode` | Unicode 编码 |
| 重复的 `\\x[0-9a-f]{2}` | Hex 编码 |

## 参数

| 参数名 | 类型 | 必填 | 描述 |
|-----------|------|----------|-------------|
| input_file | string | 是 | 混淆代码文件路径 |
| output_file | string | 否 | 输出文件路径（默认: input.clean.js） |
| inspect_only | boolean | 否 | 仅检测混淆类型，不执行反混淆 |

## 示例

```
用户："反混淆这个 sojson v6 文件"
智能体：检测类型 → 沙箱执行解密函数 → AST 替换 → 输出清理后的代码。
```

```
用户："这个 JavaScript 是什么混淆类型？"
智能体：分析模式 → 输出检测结果，不执行完整反混淆。
```

## 备注
- 只处理你有所有权或反向工程权限的代码
- 尊重开源许可证和作者版权
- jsjiami 有反调试措施——解包时关闭开发者工具
- 某些混淆（jsjiami 自卫模式）需要运行时执行，静态分析可能不够
- 使用 isolated-vm 沙箱安全执行恶意/不可信代码
- 在线反混淆工具：de4js (lelinhtinh.github.io/de4js), AST Explorer (astexplorer.net)
