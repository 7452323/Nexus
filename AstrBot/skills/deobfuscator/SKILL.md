# Deobfuscator

## Description
A comprehensive JavaScript and general code deobfuscation skill. Handles jsjiami, sojson, obfuscator.io, packer, JSFuck, RC4, Base64, ProGuard and other common obfuscation techniques. Uses AST-based analysis, sandbox execution of decryption functions, and code formatting to restore readable code.

## Instructions

### Supported Obfuscation Types

| Type | Feature | Method |
|------|---------|--------|
| **jsjiami v6 / sojson** | `jsjiami.com`/`sojson.com` watermark, `_0x` variables, 3 preamble statements | Sandbox execute decrypt function, AST string replacement |
| **jsjiami v7** | v7, variable table in first line, encrypted function with main variable references | Separate string table, sandbox execution |
| **obfuscator.io** | Heavy `_0x` usage + self-executing array + control flow flattening | Array expansion → constant folding → control flow restore → dead code removal |
| **awsc (Alibaba Cloud)** | Alibaba Cloud CDN default obfuscation, `_0x` characteristic | Same as obfuscator.io |
| **jjencode** | Starts with `$=~[];$={...}` | jjdecode dedicated restore |
| **jsconfuser** | `smEcV` characteristic | Dedicated deobfuscation plugin |
| **Dean Edwards Packer** | `eval(function(p,a,c,k,e,d)` | Auto-unpack |
| **JSFuck** | Only `[]()!+` characters | Interpreter restore |
| **eval/atob nesting** | Multiple layers `eval(atob(...))` | Recursive eval expansion |
| **Python compression** | zlib/bz2/lzma/gzip + base64 nesting | Recursive decompression |
| **Google Closure** | `a.b=c` style renaming | Source map required, partial restore |
| **ProGuard (Android)** | `a.a.a()` style | Mapping file based deobfuscation |

### Workflow

```
1. Detect obfuscation type
   ↓
2. Identify decryption function (sojson: 3 preamble statements, obfuscator: self-executing array, packer: regex pattern)
   ↓
3. Sandbox execute decryption function (isolated-vm for safe execution, get decryption map)
   ↓
4. AST replacement (replace _0x1234('0x1') with actual strings)
   ↓
5. AST purification
   ├─ Constant folding
   ├─ Control flow flattening restore
   ├─ If branch pruning
   ├─ Dead variable removal
   ├─ Sequence expression splitting
   ├─ Object literal merging
   └─ Code formatting
   ↓
6. Output readable code
```

### Tool Chain

| Tool | Purpose | Install |
|------|---------|---------|
| @babel/parser | JS → AST parsing | `npm i @babel/parser` |
| @babel/traverse | AST traversal | `npm i @babel/traverse` |
| @babel/generator | AST → JS | `npm i @babel/generator` |
| isolated-vm | Safe sandbox execution | `npm i isolated-vm` |
| js-beautify | Code formatting | `npm i js-beautify` |

### Basic Deobfuscation Commands

```bash
# Recursive eval expansion (Node.js)
node -e "
function deobf(code) {
  while (code.includes('eval')) {
    try { code = eval(code); } catch(e) { break; }
  }
  console.log(code);
}
deobf(require('fs').readFileSync('input.js','utf8'));
"

# Extract and expand all base64 function strings
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

### Obfuscation Pattern Recognition

| Pattern | Type |
|---------|------|
| `jsjiami.com` / `sojson.com` | jsjiami |
| Heavy `_0x[0-9a-f]{4,6}` variables | obfuscator.io / jsjiami |
| `function(p,a,c,k,e,d)` | Packer |
| Only `[]()!+` | JSFuck |
| `eval(atob(` | Base64 nesting |
| `a=b=c=d` renaming | Closure Compiler |
| `String.fromCharCode` | Unicode encoding |
| Repeated `\\x[0-9a-f]{2}` | Hex encoding |

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| input_file | string | Yes | Path to obfuscated code file |
| output_file | string | No | Output file path (default: input.clean.js) |
| inspect_only | boolean | No | Only detect obfuscation type without deobfuscation |

## Examples

```
User: "Deobfuscate this sojson v6 file"
Agent: Detect type → sandbox execute decryption function → AST replacement → output cleaned code.
```

```
User: "What obfuscation type is this JavaScript?"
Agent: Analyze patterns → print detection result without full deobfuscation.
```

## Notes
- Only process code you own or have rights to reverse-engineer
- Respect open-source licenses and author copyright
- jsjiami has anti-debugging measures — close devtools when unpacking
- Some obfuscation (jsjiami self-defense mode) requires runtime execution, static analysis may be insufficient
- Use isolated-vm sandbox for safe execution of malicious/untrusted code
- For online deobfuscation: de4js (lelinhtinh.github.io/de4js), AST Explorer (astexplorer.net)
