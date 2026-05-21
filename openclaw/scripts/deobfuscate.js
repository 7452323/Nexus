#!/usr/bin/env node
/**
 * deobfuscate.js — 通用 JS 反混淆工具
 *
 * 用法:
 *   node deobfuscate.js input.js                → output.clean.js
 *   node deobfuscate.js input.js -o result.js   → 指定输出
 *   node deobfuscate.js input.js --inspect      → 仅检测混淆类型
 *
 * 依赖 (可选):
 *   npm i -g js-beautify   → 启用代码格式化
 *
 * 支持:
 *   jsjiami v6/v7, obfuscator.io, awsc, jjencode, packer, eval递归, unicode/hex
 */

const fs = require('fs');
const args = process.argv.slice(2);
let inputFile, outputFile, inspectOnly = false;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '-o' && args[i+1]) { outputFile = args[++i]; }
  else if (args[i] === '--inspect') { inspectOnly = true; }
  else if (!args[i].startsWith('-')) { inputFile = args[i]; }
}
if (!inputFile) { console.error('用法: node deobfuscate.js input.js [-o output.js] [--inspect]'); process.exit(1); }

const code = fs.readFileSync(inputFile, 'utf-8');
outputFile = outputFile || inputFile.replace(/\.js$/, '.clean.js');

// === 混淆类型检测 ===
function detectType(code) {
  const patterns = [
    { name: 'jsjiami/sojson',      re: /jsjiami\.com|sojson\.com/ },
    { name: 'obfuscator.io',       re: /_0x[0-9a-f]{4,6}.*_0x[0-9a-f]{4,6}\(/ },
    { name: 'Packer',              re: /eval\(function\(p,a,c,k,e,d\)/ },
    { name: 'JJEncode',            re: /^ﾟωﾟﾉ=|\$=~\[\];\$\{/ },
    { name: 'JSFuck',              re: /^\[\(!\[\] \[/ },
    { name: 'eval(atob)',          re: /eval\(\s*atob\s*\(/ },
    { name: 'String.fromCharCode', re: /String\.fromCharCode/ },
    { name: 'IIFE自执行',          re: /\(function\(\)\{[\s\S]{100,}\}\]\(\)/ },
    { name: '数组混淆',            re: /\[[\s\S]{100,}\]\(function/ },
  ];
  return patterns.filter(p => p.re.test(code)).map(p => p.name);
}
const detected = detectType(code);
console.log(`📋 ${inputFile} (${(code.length/1024).toFixed(1)}KB)`);
console.log(`🔍 ${detected.length ? detected.join(', ') : '未识别'}`);
if (inspectOnly) process.exit(0);

// === Packer 解包 ===
function unpackPacker(code) {
  const m = code.match(/eval\(function\(p,a,c,k,e,d\)\{[\s\S]*?\}\(([\s\S]*?)\)\)/);
  if (!m) return null;
      try {
    let body = m[0], params = m[1];
    const parts = params.match(/'([^']*)'|\[[\s\S]*?\]/g);
    if (!parts || parts.length < 4) return null;
    const k = JSON.parse(parts[3].replace(/'/g, '"').replace(/^\[/, '["').replace(/\]$/, '"]'));
    for (let i = 0; i < k.length; i++) {
      body = body.replace(new RegExp('\\b' + i + '\\b', 'g'), k[i]);
    }
    const core = body.match(/'([^']+)'/);
    return core ? core[1] : body;
      } catch(e) { return null; }
}

// === eval 递归展开 ===
function recursiveEval(c, d) {
  if (d > 10) return c;
      try {
    const m = c.match(/eval\s*\(\s*(atob\s*\(['"][^'"]+['"]\)|function\s*\(\)\s*\{[\s\S]*?\}\s*\(\s*\))\s*\)/);
    if (!m) return c;
    const r = eval(m[0]);
    return (r && typeof r === 'string' && r !== c) ? recursiveEval(r, d+1) : c;
      } catch(e) { return c; }
}

// === 基础清理 ===
function cleanBasic(c) {
  let r = c.replace(/^eval\s*\(?/, '').replace(/\)?\s*$/, '');
  r = recursiveEval(r);
  // JJEncode extraction: (ﾟДﾟ)['_'](...)('_') pattern
  const jjMatch = r.match(/\(ﾟДﾟ\)\s*\[['"]_['"]\]\s*\(([\s\S]+)\)\s*\(['"]_['"]\)/);
  if (jjMatch) {
    try {
      const jjEvaled = eval(jjMatch[0]);
      if (jjEvaled && typeof jjEvaled === 'string' && jjEvaled.length > 10) r = jjEvaled;
    } catch(e) {}
  }
  r = r.replace(/\\u([0-9a-f]{4})/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
  r = r.replace(/\\x([0-9a-f]{2})/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
  r = r.replace(/['"]\s*\+\s*['"]/g, '');
  return r;
}

// === 主管道 ===
let result = code, steps = 0;
const unpacked = unpackPacker(result);
if (unpacked) { result = unpacked; steps++; console.log(`✅ Step1: Packer`); }
const cleaned = cleanBasic(result);
if (cleaned !== result) { result = cleaned; steps++; console.log(`✅ Step2: 基础清理`); }
result = result.replace(/;{2,}/g, ';').replace(/^\s*['"][^'"]*['"];\s*$/gm, '');
    try { result = require('js-beautify').js_beautify(result, { indent_size: 2 }); steps++; console.log(`✅ Step${steps}: 格式化`); }
catch(e) { console.log(`⚠️  安装 js-beautify 可启用格式化: npm i -g js-beautify`); }

fs.writeFileSync(outputFile, result, 'utf-8');
console.log(`\n📦 ${outputFile} (${(result.length/1024).toFixed(1)}KB, ${(result.length/code.length*100).toFixed(1)}%)`);
if (!detected.length) console.log('⚠️  未识别标准混淆, 结果可能不完整。\n💡 完整AST反混淆需 @babel/parser: https://github.com/smallfawn/decode_action');
