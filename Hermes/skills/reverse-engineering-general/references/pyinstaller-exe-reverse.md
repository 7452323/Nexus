# PyInstaller EXE Reverse Engineering & Cross-Platform Porting

Extract Python source from PyInstaller-packed Windows `.exe` and port to macOS/Linux.

## When to Use

- User provides a `.exe` that turns out to be PyInstaller-packed Python
- Need to recover source code from a frozen Python application
- Cross-platform conversion: Windows Python app → macOS/Linux

## Step 1: Identify PyInstaller

```bash
file target.exe
# Look for: "PE32+ executable (GUI) x86-64, for MS Windows"

strings target.exe | head -50
# Look for: "!This program cannot be run in DOS mode." + ".pyd" imports

strings target.exe | grep -i "pyi-\|pyinstaller\|python.*\.dll\|PYZ"
# Definitive: "pyi-python-flag", "PYZ.pyz", "python3X.dll"
```

**Other packers to check first:**
- `cx_Freeze`: look for `cx_` prefixes in imports
- `Nuitka`: compiled C, no `.pyc` signatures
- `py2exe`: look for `pythonXX.dll` + `library.zip`
- `Briefcase/BeeWare`: look for `toga` or `rubicon`

## Step 2: Extract with pyinstxtractor

```bash
# Download pyinstxtractor
curl -L -o pyinstxtractor.py \
  https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py

# Extract
python3 pyinstxtractor.py target.exe
# Creates: target.exe_extracted/
```

**Key files in extracted directory:**
```
target.exe_extracted/
├── <module>.pyc          # ← Main entry point (match exe name)
├── PYZ.pyz               # Compressed Python modules
├── PYZ.pyz_extracted/    # Extracted PYZ contents (may be empty)
├── base_library.zip      # Standard library modules
├── *.pyd                 # Windows DLL extensions (C extensions)
├── *.dll                 # Runtime DLLs (python3X.dll, VCRUNTIME, etc.)
└── PyQt*/tkinter/        # GUI framework files if used
```

**Python version detection:**
```bash
# From pyinstxtractor output:
# [+] Python version: 3.12

# Or check DLL name:
ls *.pyd | head
# python312.dll → Python 3.12
```

## Step 3: Decompile .pyc Files

**Critical**: pyinstxtractor warns if you run a different Python version. For Python 3.12 `.pyc` files, ideally use Python 3.12. If unavailable, decompilers may still work with minor issues.

### Tool Selection (by Python version)

| Python Version | Decompiler | Install |
|---------------|-----------|---------|
| 3.7–3.11 | `uncompyle6` | `pip3 install uncompyle6` |
| 3.9–3.12 | `decompyle3` | `pip3 install decompyle3` |
| 3.12+ | `pycdc` (C++) | Build from https://github.com/zrax/pycdc |
| Any | `dis` module | Built-in, gives bytecode only |

### Attempt decompyle3 first

```bash
pip3 install decompyle3
python3 -c "from decompyle3.main import decompile_file; decompile_file('target.exe_extracted/target.pyc')" > target.py
```

### If decompyle3 fails, try uncompyle6

```bash
pip3 install uncompyle6
# uncompyle6 has no __main__, use the API:
python3 -c "
import uncompyle3
import sys
with open('target.py', 'w') as out:
    uncompyle3.decompile_file('target.exe_extracted/target.pyc', out)
"
```

### If both fail (Python 3.12+ bytecode)

```bash
# Option A: Build pycdc from source (REQUIRES cmake)
brew install cmake  # ← must install first
git clone https://github.com/zrax/pycdc.git
cd pycdc && cmake . && make -j4
# Two binaries: pycdc (decompiler) and pycdas (disassembler)
./pycdc ../target.exe_extracted/target.pyc > ../target.py 2>/tmp/errors.txt
# pycdas gives cross-version disassembly (works when pycdc decompilation fails):
./pycdas ../target.exe_extracted/target.pyc > ../target_disasm.txt

# Option B: Install Python 3.12 and retry
brew install python@3.12
python3.12 -m pip install decompyle3
python3.12 -m decompyle3 target.pyc > target.py

# Option C: Extract strings + imports as fallback analysis
strings target.pyc | grep -E "def |class |import |from "
strings target.pyc | grep -E "http|api|url|token|cookie"
```

### Python 3.12 pycdc Limitations (CRITICAL)

**pycdc has incomplete Python 3.12 support.** Async functions, generators, and complex control flow often produce `# WARNING: Decompyle incomplete` with empty function bodies.

Unsupported opcodes that cause failures:
- `RETURN_GENERATOR` (225) — all async functions affected
- `MAKE_CELL` (225) — closure variables
- `LOAD_FAST_AND_CLEAR` (241) — list comprehensions, generators

**Symptoms in pycdc output:**
```python
async def exchange_info1():
    pass
# WARNING: Decompyle incomplete
```

**How to tell if decompilation is complete:**
```bash
grep -c "WARNING: Decompyle incomplete" /tmp/errors.txt
# If > 0, those functions need manual reconstruction
```

### Manual Bytecode Reconstruction (for incomplete async functions)

When pycdc fails on async functions, use code object introspection + pycdas disassembly to reconstruct:

**Step 1: Extract function metadata from code objects**
```python
import marshal, struct

with open('target.pyc', 'rb') as f:
    f.read(4)   # magic
    f.read(4)   # flags
    f.read(8)   # timestamp + size
    code = marshal.load(f)

def get_nested_code(parent, name_chain):
    current = parent
    for name in name_chain:
        for c in current.co_consts:
            if hasattr(c, 'co_name') and c.co_name == name:
                current = c; break
        else:
            return None
    return current

# Get specific function
func = get_nested_code(code, ['ClassName', 'method_name'])
print(f"Args: {func.co_varnames[:func.co_argcount]}")
print(f"All vars: {func.co_varnames}")
print(f"Names (globals/attrs accessed): {func.co_names}")
print(f"Constants: {[c for c in func.co_consts if not hasattr(c, 'co_name')]}")
print(f"Is async: {bool(func.co_flags & 0x80)}")
print(f"Code size: {len(func.co_code)} bytes")
```

**Step 2: Use pycdas disassembly for control flow**
```bash
# pycdas handles Python 3.12 bytecode correctly (cross-version)
./pycdas target.pyc > disasm.txt
# Search for the function:
grep -n "Object Name: function_name" disasm.txt
# Read the disassembly section (shows opcodes, constants, control flow)
```

**Step 3: Reconstruct from bytecode pattern**
Common patterns in async function bytecode:
```
RETURN_GENERATOR  → function is async/generator
GET_AWAITABLE     → await expression
SEND + YIELD_VALUE → await suspension point
BEFORE_ASYNC_WITH → async with statement
CALL + GET_AWAITABLE → calling another async function
STORE_FAST        → local variable assignment
LOAD_GLOBAL       → global/module reference
LOAD_ATTR         → attribute access (obj.attr)
BINARY_SUBSCR     → dict/list subscript (obj[key])
KW_NAMES          → keyword arguments follow
```

**Step 4: Verify reconstruction**
```python
# After manual reconstruction, verify the function can be imported
import importlib.util
spec = importlib.util.spec_from_file_location("target", "reconstructed.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)  # If no errors, syntax is valid
```

### ⚠️ User Preference: Extract Complete Source, Don't Rewrite

When user asks to "extract from exe" or "把exe里的py提取出来", they want the **original source code recovered**, not your own rewritten version. The correct workflow is:

1. Extract with pyinstxtractor
2. Decompile with pycdc/decompyle3
3. **Manually reconstruct incomplete functions** from bytecode
4. Only rewrite/port AFTER the complete source is recovered

"Do not write your own version from scratch" is a hard constraint. If decompilation is incomplete, fix it with bytecode analysis — don't start over.

## Step 4: Analyze Recovered Code

Even partial decompilation reveals critical info:

```bash
# Class/function structure
strings target.pyc | grep -E "class |def |__init__|__main__|async |await "

# Network endpoints
strings target.pyc | grep -E "https?://|api\.|\.com|\.cn|\.io"

# Data patterns
strings target.pyc | grep -E "token|cookie|session|config|setting"

# Dependencies
strings target.pyc | grep -E "import |from .* import"
```

## Step 5: Cross-Platform Porting

### Decision Matrix

| Component | macOS Portability | Action |
|-----------|-------------------|--------|
| Pure Python logic | ✅ Direct reuse | Copy as-is |
| PyQt5/PyQt6 | ✅ Works on macOS | `pip3 install PyQt5` |
| tkinter | ✅ Built-in | Direct reuse |
| Windows APIs (win32gui, ctypes.windll) | ❌ Incompatible | Rewrite with macOS equivalents |
| os.path / pathlib | ✅ Cross-platform | Works, prefer pathlib |
| subprocess (Windows shell) | ⚠️ Partial | Check for `cmd.exe`, `powershell`, `.bat` calls |
| Registry access (winreg) | ❌ No macOS equivalent | Use plist files or config files |
| .pyd extensions | ❌ Windows-only | Need source or macOS .so equivalent |

### Common Rewrites

**Windows paths → Cross-platform:**
```python
# Windows
config_path = os.path.join(os.environ['APPDATA'], 'MyApp', 'config.json')

# Cross-platform
config_path = Path.home() / '.config' / 'myapp' / 'config.json'
```

**GUI → CLI fallback:**
If PyQt5/tkinter dependencies are heavy, create a CLI version that preserves core logic.

**C extensions (.pyd):**
```bash
# Check if source exists in PyPI
pip3 install <package_name>  # May have macOS wheel

# If no macOS wheel, check for pure-Python alternative
# Or compile from source if C source available
```

## Pitfalls

- **Python version mismatch**: `pyinstxtractor` warns but doesn't fail. Decompiled code may have minor bytecode artifacts.
- **PYZ.pyz_extracted may be empty**: If extraction ran with wrong Python version, re-run with matching version.
- **`uncompyle6` / `decompyle3` CLI may not work**: Use the Python API directly (`decompile_file()`), not `python3 -m` invocation.
- **63MB exe ≠ 63MB of Python**: Most bulk is bundled DLLs, PyQt, etc. Actual Python code is usually <1MB.
- **`.pyd` files are Windows-only**: They're compiled C extensions. Check if the package has macOS wheels on PyPI.
- **Don't delete `_extracted/` until analysis is complete**: You may need to re-examine specific `.pyc` files.
- **Signature verification**: Some PyInstaller exes have appended signatures. `pyinstxtractor` handles this, but corrupted archives may need `--offset` flag.
- **pycdc needs cmake**: `brew install cmake` before building. Without it, `cmake .` silently fails.
- **pycdc Python 3.12 async functions are broken**: All `async def` functions produce empty bodies. Use pycdas + manual bytecode reconstruction.
- **Python's `dis` module version-locked**: Python 3.11's `dis` cannot disassemble Python 3.12 bytecode (IndexError: tuple index out of range). Use pycdas instead.
- **PYZ.pyz is NOT a standard zip**: Cannot use `zipfile.ZipFile()` to read it. Use `PyInstaller.archive.readers.ZlibArchiveReader` with `.toc` dict to list/extract modules.
- **Don't rewrite when asked to extract**: If user says "extract from exe", they want the original source recovered, not a new version you wrote. Reconstruct incomplete functions from bytecode analysis.

## Real-World Example: 63MB Caiji.exe → macOS CLI

1. `file` → PE32+ GUI x86-64
2. `strings` → `pyi-python-flag`, `python312.dll`, `PyQt5`
3. `pyinstxtractor.py` → extracted 1529 files, main entry `菜鸡兑换.pyc` (248KB)
4. `uncompyle6`/`decompyle3` failed (Python 3.12 on system Python 3.9)
5. Built `pycdc` from source (`brew install cmake` → `cmake . && make -j4`)
6. `pycdc` partially succeeded: 1221 lines, but 30+ async functions were `# WARNING: Decompyle incomplete`
7. Used `pycdas` (disassembler) + code object introspection to reconstruct:
   - `exchange_info1()` — algorithm server call (http://117.72.195.241:7799/exchange-info)
   - `Caiji.xsign()` — x-sign generation via algorithm server (/get_sign)
   - `Caiji._common_exchange()` — common exchange flow with retry
   - `Caiji.dtxb_exchange()` — dtxb-specific exchange with product listing
   - `ExchangeWorker` — QThread worker with get_token/get_envs from 青龙面板
8. Key discovery: `ZlibArchiveReader.toc` gives 730 module names from PYZ.pyz
9. Product data (RL/RP codes for 100+ items) fully recovered from pycdc constants
10. Algorithm server URL `http://117.72.195.241:7799` + `/get_sign` endpoint recovered from constants
