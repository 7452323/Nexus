#!/usr/bin/env python3
"""
Swift5 Reflstr Extractor — Extract type structures from Mach-O Swift binaries.
Usage: python3 swift5_extract.py <binary_path> [keywords...]
"""
import sys
import struct

def find_swift5_sections(data):
    """Find Swift5 metadata sections from Mach-O headers."""
    # Check magic
    magic = struct.unpack('<I', data[:4])[0]
    if magic == 0xfeedfacf:  # 64-bit
        is_64 = True
        header_size = 32
    elif magic == 0xcafebabe:  # FAT
        print("FAT binary detected — analyzing first slice only")
        nfat = struct.unpack('>I', data[4:8])[0]
        # Get first slice offset
        cpu_type, cpu_subtype, offset, size, align = struct.unpack('>IIIII', data[8:28])
        data = data[offset:offset+size]
        magic = struct.unpack('<I', data[:4])[0]
        if magic != 0xfeedfacf:
            print("Unsupported FAT slice format")
            return {}
        is_64 = True
        header_size = 32
    else:
        print(f"Unsupported magic: {hex(magic)}")
        return {}

    ncmds = struct.unpack('<I', data[16:20])[0]
    sizeofcmds = struct.unpack('<I', data[20:24])[0]

    sections = {}
    offset = header_size

    for _ in range(ncmds):
        cmd = struct.unpack('<I', data[offset:offset+4])[0]
        cmdsize = struct.unpack('<I', data[offset+4:offset+8])[0]

        if cmd == 0x19:  # LC_SEGMENT_64
            segname = data[offset+8:offset+24].split(b'\x00')[0].decode()
            nsects = struct.unpack('<I', data[offset+64:offset+68])[0]
            sect_offset = offset + 72

            for _ in range(nsects):
                sectname = data[sect_offset:sect_offset+16].split(b'\x00')[0].decode()
                sect_size = struct.unpack('<Q', data[sect_offset+48:sect_offset+56])[0]
                sect_file_offset = struct.unpack('<I', data[sect_offset+40:sect_offset+44])[0]

                if sectname.startswith('__swift5_'):
                    sections[sectname] = {
                        'offset': sect_file_offset,
                        'size': sect_size,
                        'segment': segname
                    }

                sect_offset += 80  # section_64 size

        offset += cmdsize

    return sections


def extract_reflstr(data, offset, size):
    """Extract and parse __swift5_reflstr strings."""
    reflstr = data[offset:offset+size]
    strings = []
    for s in reflstr.split(b'\x00'):
        try:
            decoded = s.decode('utf-8')
            if decoded:
                strings.append(decoded)
        except:
            pass
    return strings


def search_context(strings, keywords, context_before=3, context_after=10):
    """Search for keywords and show surrounding context."""
    keywords_lower = [k.lower() for k in keywords]
    results = []

    for i, s in enumerate(strings):
        s_lower = s.lower()
        if any(k in s_lower for k in keywords_lower):
            start = max(0, i - context_before)
            end = min(len(strings), i + context_after)
            context = []
            for j in range(start, end):
                context.append({
                    'index': j,
                    'value': strings[j],
                    'is_match': j == i
                })
            results.append(context)

    return results


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <binary_path> [keywords...]")
        print(f"  Default keywords: subscr,paywall,purchase,unlock,premium,trial,curtain,feature,lifetime,iap")
        sys.exit(1)

    binary_path = sys.argv[1]
    keywords = sys.argv[2:] if len(sys.argv) > 2 else [
        'subscr', 'paywall', 'purchase', 'unlock', 'premium',
        'trial', 'curtain', 'feature', 'lifetime', 'iap', 'entitle'
    ]

    print(f"Analyzing: {binary_path}")
    with open(binary_path, 'rb') as f:
        data = f.read()

    # Find Swift5 sections
    sections = find_swift5_sections(data)
    if not sections:
        print("No Swift5 metadata sections found!")
        sys.exit(1)

    print(f"\nSwift5 sections found:")
    for name, info in sections.items():
        print(f"  {name}: offset=0x{info['offset']:x}, size=0x{info['size']:x}")

    # Extract reflstr
    if '__swift5_reflstr' not in sections:
        print("No __swift5_reflstr section!")
        sys.exit(1)

    refl = sections['__swift5_reflstr']
    strings = extract_reflstr(data, refl['offset'], refl['size'])
    print(f"\nTotal reflection strings: {len(strings)}")

    # Search
    print(f"\nSearching for: {', '.join(keywords)}")
    print("=" * 60)

    results = search_context(strings, keywords)
    for context in results:
        for item in context:
            marker = '>>>' if item['is_match'] else '   '
            print(f"  {marker} [{item['index']}] {item['value']}")
        print()

    # Also find string offsets in binary for cross-reference
    print("=" * 60)
    print("String offsets (for radare2/Ghidra cross-reference):")
    for kw in keywords:
        pattern = kw.encode()
        count = data.count(pattern)
        if count > 0:
            idx = data.find(pattern)
            print(f"  {kw}: {count} occurrences, first at 0x{idx:x}")


if __name__ == '__main__':
    main()
