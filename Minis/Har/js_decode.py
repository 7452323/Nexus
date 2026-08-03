#!/usr/bin/env python3
r"""
JS Obfuscation Decoder — 自动检测并解密常见 JS 混淆

支持:
- hex (\\xHH) 解码
- URL encoding 解码
- atob/base64 解码
- eval packer 提取
- jsjiami RC4 (需 Node 运行时)
- 集成到 HAR 分析工作流
"""
import re, os, sys, subprocess, json, base64
from urllib.parse import unquote

class JSObfuscationDecoder:
    """JS 混淆自动检测与解码"""
    
    TYPES = {
        'hex': (r'\\x[0-9a-fA-F]{2}', '\\xHH 十六进制编码'),
        'url_encoded': (r'%[0-9A-F]{2}', 'URL 百分号编码'),
        'eval_packer': (r'eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e', 'eval packer 混淆'),
        'jsjiami': (r'jsjiami\.com|encode_version\s*=', 'jsjiami 商业混淆'),
        'rc4_table': (r'__0x[a-f0-9]+\s*=\s*\[', 'RC4+Base64 字符串表'),
        'atob_usage': (r'atob\s*\(', 'Base64 解码调用'),
        'string_array': (r'var\s+_[a-zA-Z]\w*\s*=\s*\[.*?\]\s*;\s*function\s+_\w+', '字符串数组解引用'),
    }
    
    @classmethod
    def detect(cls, content: str) -> list:
        """检测混淆类型"""
        detected = []
        for name, (pattern, desc) in cls.TYPES.items():
            if re.search(pattern, content, re.IGNORECASE):
                detected.append({'type': name, 'description': desc})
        return detected
    
    @classmethod
    def decode_hex(cls, content: str) -> tuple:
        """解码 \\xHH"""
        def repl(m):
            try:
                return bytes.fromhex(m.group(1)).decode('utf-8')
            except:
                return m.group(0)
        decoded = re.sub(r'\\x([0-9a-fA-F]{2})', repl, content)
        return decoded, decoded != content
    
    @classmethod
    def decode_url(cls, content: str) -> tuple:
        """解码 URL encoded"""
        try:
            decoded = unquote(content)
            return decoded, decoded != content
        except:
            return content, False
    
    @classmethod
    def decode_atob(cls, content: str) -> tuple:
        """解码 atob 字符串"""
        found = 0
        def repl(m):
            nonlocal found
            try:
                decoded = base64.b64decode(m.group(1)).decode('utf-8', errors='replace')
                found += 1
                return f'"{decoded}"'
            except:
                return m.group(0)
        decoded = re.sub(r'atob\(["\']([A-Za-z0-9+/=]+)["\']\)', repl, content)
        return decoded, found > 0
    
    @classmethod
    def extract_eval_packer(cls, content: str) -> tuple:
        """提取 eval packer 内容"""
        m = re.search(r"eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*d\s*\)\s*\{[\s\S]*?\}\s*\('([\s\S]*?)'\s*,\s*\d+\s*,\s*\d+\s*,\s*'([\s\S]*?)'\.split\('\|'\)", content)
        if not m:
            return content, False
        
        packed = m.group(1)
        keywords = m.group(2).split('|')
        
        # 替换数字引用
        def unpack_repl(match):
            idx = int(match.group(1))
            if idx < len(keywords):
                return keywords[idx]
            return match.group(0)
        
        # 先处理转义
        decoded = packed.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')
        # 替换数字
        for _ in range(5):
            decoded = re.sub(r'\b(\d+)\b', unpack_repl, decoded)
        
        return decoded, True
    
    @classmethod
    def try_node_deobfuscate(cls, filepath: str) -> str:
        """用 Node 尝试完整解密 jsjiami"""
        node_script = os.path.join(os.path.dirname(__file__), '..', '..', 'tmp', 'js_deob.js')
        if not os.path.exists(node_script):
            node_script = '/tmp/js_deob.js'
        
        try:
            result = subprocess.run(
                ['node', '--no-warnings', node_script, filepath],
                capture_output=True, text=True, timeout=15
            )
            return result.stdout
        except:
            return ""
    
    @classmethod
    def smart_decode(cls, filepath: str) -> dict:
        """完整的智能解码管道"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                original = f.read()
        except:
            return {'error': 'read_failed'}
        
        if not original.strip():
            return {'error': 'empty'}
        
        size_orig = len(original)
        steps = []
        decoded = original
        
        # 检测
        obf_types = cls.detect(original)
        
        # Step 1: URL decode
        decoded, changed = cls.decode_url(decoded)
        if changed: steps.append('url_decode')
        
        # Step 2: Hex decode
        decoded, changed = cls.decode_hex(decoded)
        if changed: steps.append('hex_decode')
        
        # Step 3: atob decode
        decoded, changed = cls.decode_atob(decoded)
        if changed: steps.append('atob_decode')
        
        # Step 4: Eval packer
        decoded, changed = cls.extract_eval_packer(decoded)
        if changed: steps.append('eval_packer')
        
        # Step 5: Node 运行时解密（仅 jsjiami）
        has_jsjiami = any(t['type'] == 'jsjiami' for t in obf_types)
        if has_jsjiami:
            node_result = cls.try_node_deobfuscate(filepath)
            if node_result and len(node_result) > 200:
                steps.append('node_runtime')
                decoded = node_result
        
        # 提取破解逻辑
        crack_logic = []
        for line in decoded.split('\n'):
            for kw in ['$done', 'JSON.parse', 'JSON.stringify', '.replace(', 'obj.', 
                        'vip', 'premium', 'subscription', 'expire']:
                if kw in line:
                    crack_logic.append(line.strip())
                    break
        
        return {
            'file': os.path.basename(filepath),
            'original_size': size_orig,
            'decoded_size': len(decoded),
            'reduction': f"{(1 - len(decoded)/size_orig)*100:.0f}%",
            'obfuscation_types': [t['description'] for t in obf_types],
            'decode_steps': steps,
            'crack_logic': crack_logic[:20],
            'content': decoded[:3000],
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 js_decode.py <file.js>")
        sys.exit(1)
    
    result = JSObfuscationDecoder.smart_decode(sys.argv[1])
    
    if 'error' in result:
        print(f"ERROR: {result['error']}")
        return
    
    print(f"=== {result['file']} ===")
    print(f"  Size: {result['original_size']} → {result['decoded_size']} ({result['reduction']})")
    print(f"  Obfuscation: {', '.join(result['obfuscation_types'])}")
    print(f"  Steps: {', '.join(result['decode_steps'])}")
    print(f"\n  Crack Logic ({len(result['crack_logic'])} lines):")
    for line in result['crack_logic']:
        print(f"    {line[:120]}")
    print(f"\n  Content Preview:")
    print(result['content'][:2000])

if __name__ == '__main__':
    main()
