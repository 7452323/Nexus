---
name: ai-driven-reverse
description: AI 驱动逆向工程。整合 GhidraMCP、LLM 辅助反编译、符号执行 MCP、自动化函数识别与重命名。2026 最新 AI + 逆向工作流。
category: reverse-engineering
tags: [ai, ghidra, mcp, llm, symbolic-execution, decompilation]
---

# AI 驱动逆向工程 (NEW 2026)

> 用 LLM + MCP 自动化传统逆向流程。效率提升 10 倍。

## 工具链

| 工具 | 用途 | Stars | 平台 |
|------|------|-------|------|
| **LaurieWired/GhidraMCP** | Ghidra MCP 服务器，LLM 自动反编译/分析/重命名 | 3.2k | Java/Ghidra |
| **bethington/ghidra-mcp** | 另一个 Ghidra MCP，245 个工具，支持 P-code 模拟 | 245 | Java/Ghidra |
| **semba/llm-reverse** | LLM 辅助反编译，自动识别加密算法 | 1.1k | Python |
| **abstract-state/symbolic-execution-mcp** | 符号执行 MCP，集成 angr/taint analysis | new | Python |
| **trailofbits/blint** | 二进制 LLM 分析工具 | 1.2k | Python |
| **google/project-osearch** | AI 驱动二进制搜索 | 800 | Python |

## GhidraMCP 工作流

### 安装

```bash
# 1. 安装 Ghidra
# 下载从 https://ghidra-sre.org/

# 2. 安装 GhidraMCP
git clone https://github.com/LaurieWired/GhidraMCP.git
cd GhidraMCP && ./gradlew extendPcode  # 构建 P-code 插件

# 3. 配置 MCP
# 在 MCP 客户端添加 GhidraMCP 服务
```

### 核心能力

| MCP 工具 | 功能 |
|---------|------|
| `list_functions` | 列出所有函数（名称+地址） |
| `decompile_function` | 反编译指定函数为伪 C 代码 |
| `rename_function` | 重命名函数 |
| `set_comment` | 添加注释 |
| `get_cross_references` | 获取交叉引用 |
| `analyze_structures` | 分析数据结构 |
| `search_strings` | 搜索字符串常量 |
| `get_call_graph` | 获取调用图 |
| `pcode_simulate` | P-code 模拟执行 |

### LLM 辅助分析流程

```
1. GhidraMCP → list_functions → 获取所有函数
2. LLM 分析函数名/字符串 → 标记可疑函数
3. GhidraMCP → decompile_function → 反编译可疑函数
4. LLM 分析伪代码 → 识别算法/协议/漏洞
5. GhidraMCP → rename_function → 自动重命名
6. 迭代直到所有关键函数被识别
```

## LLM 辅助反编译

### 场景：识别加密算法

```python
# 1. 反编译函数（GhidraMCP）
pseudo_code = ghidra_mcp.decompile_function("0x00401000")

# 2. LLM 分析
prompt = f"""
分析以下伪代码，识别加密算法：

{pseudo_code}

提示：
- 查找常量表（S-box、IV、delta）
- 分析运算模式（XOR、移位、模乘）
- 识别算法类型（AES/DES/RC4/TEA/MD5/SHA/自定义）

输出格式：
- 算法名称：
- 关键常量：
- 输入/输出：
- Python 复现代码：
"""
```

### 场景：自动重命名

```python
# LLM 根据函数行为自动推断有意义的名称
functions = ghidra_mcp.list_functions()
for func in functions:
    pseudo = ghidra_mcp.decompile_function(func.address)
    name = llm_suggest_name(pseudo)
    ghidra_mcp.rename_function(func.address, name)
```

## 符号执行 MCP

### 集成 angr

```python
# symbolic-execution-mcp 提供符号执行能力
import angr

proj = angr.Project('target_binary')
state = proj.factory.entry_state()
simgr = proj.factory.simgr(state)

# 符号执行找到到达目标地址的输入
simgr.explore(find=0x401000, avoid=0x401100)
if simgr.found:
    solution = simgr.found[0].posix.dumps(0)  # stdin
    print(f"Found input: {solution}")
```

## AI + JS 逆向

### LLM 辅助 AST 反混淆

```python
# 1. AST 解析混淆代码
# 2. LLM 识别混淆模式
# 3. 生成反混淆脚本
# 4. Babel AST 自动还原

code = """/* obfuscated code */"""
prompt = f"""
分析以下 JS 混淆代码：

{code}

1. 识别混淆器类型（obfuscator.io/jsjiami/sojson/其他）
2. 生成反混淆 Babel AST 脚本
3. 输出还原后的代码
"""
```

## 实战案例

### 案例1：GhidraMCP 自动分析恶意软件

```
1. 加载恶意软件到 Ghidra
2. GhidraMCP → list_functions → 200 个函数
3. LLM 过滤 → 标记 15 个可疑函数
4. GhidraMCP → decompile_function → 逐个反编译
5. LLM 分析 → 识别 C2 通信、加密、持久化
6. 自动重命名 + 注释 → 输出分析报告
耗时：30 分钟（传统方法需 2-3 天）
```

### 案例2：符号执行破解许可验证

```
1. 加载许可验证二进制
2. 符号执行 MCP → 符号化输入
3. explore(find=success_path, avoid=fail_path)
4. 获取有效许可 key
5. 验证通过
```

## 推荐工作流

```
传统流程：静态分析 → 动态调试 → 手动逆向 → 复现（天级）
AI 流程：GhidraMCP → LLM 分析 → 自动重命名 → 复现（小时级）
```

## 限制

1. **Ghidra 需 GUI 环境** — 服务器需 Xvfb
2. **LLM 可能误判** — 需人工验证关键函数
3. **符号执行路径爆炸** — 复杂程序可能超时
4. **混淆代码** — LLM 需结合 AST 反混淆预处理

