---
name: ai-driven-reverse
description: AI 驱动逆向工程 (2026.07)。整合 GhidraMCP、JSReverser-MCP、LLM 辅助反编译、符号执行 MCP、自动化函数识别与重命名。
category: reverse-engineering
tags: [ai, ghidra, mcp, llm, symbolic-execution, decompilation]
---

# AI 驱动逆向工程 (2026.07)

> 用 LLM + MCP 自动化传统逆向流程。效率提升 10 倍。

## MCP Server 生态 (2026.07)

| MCP Server | Stars | 用途 | 平台 |
|------------|-------|------|------|
| **LaurieWired/GhidraMCP** | 3.2k⭐ | Ghidra MCP，LLM 自动反编译/重命名 | Java/Ghidra |
| **bethington/ghidra-mcp** | 245⭐ | 245 工具，P-code 模拟 | Java/Ghidra |
| **0xflux/ghidra-mcp** | — | Ghidra MCP 变体 | Java/Ghidra |
| **nightwing-us/mcpyghidra** | — | Ghidra MCP | Python |
| **wellingtonlee/ghidra-docker-mcp** | — | Ghidra Docker MCP | Docker |
| **cgtudor/reverse-engineering-assistant** | — | AI 逆向助手 | Python |
| **NoOne-hub/JSReverser-MCP** | 899⭐ | JS 逆向全流程 MCP | TypeScript |
| **715494637/reverse-skill** | 283⭐ | Web JS 逆向 + 壳层恢复 | JavaScript |

## GhidraMCP 工作流

### 安装
```bash
git clone https://github.com/LaurieWired/GhidraMCP.git
cd GhidraMCP && ./gradlew extendPcode
```

### 核心能力
| MCP 工具 | 功能 |
|---------|------|
| `list_functions` | 列出所有函数 |
| `decompile_function` | 反编译为伪 C 代码 |
| `rename_function` | 重命名函数 |
| `set_comment` | 添加注释 |
| `get_cross_references` | 获取交叉引用 |
| `analyze_structures` | 分析数据结构 |
| `search_strings` | 搜索字符串常量 |
| `pcode_simulate` | P-code 模拟执行 |

### LLM 辅助分析流程
```
1. GhidraMCP → list_functions → 获取所有函数
2. LLM 分析函数名/字符串 → 标记可疑函数
3. GhidraMCP → decompile_function → 反编译可疑函数
4. LLM 分析伪代码 → 识别算法/协议/漏洞
5. GhidraMCP → rename_function → 自动重命名
```

## JSReverser-MCP 工作流 (899⭐)

### 标准执行流程
```
1. Page Observation → 确认请求、脚本、函数
2. Runtime Sampling → 最小化 Hook 采样
3. Evidence Capture → 结果写入 task artifact
4. Local Rebuild → 导出可复现工程
5. Environment Patching → Node 逐项补环境
6. First-divergence Analysis → 定位分歧点
7. Pure Extraction → env-pass 后纯算法提纯
```

### 工具暴露模式
- `--toolProfile kernel` (默认) — 35 个自动化优先工具
- `--toolProfile compact` — 63 个高频工具
- `--toolProfile full` — 全部 110 个工具

## 符号执行 MCP

### 集成 angr
```python
import angr
proj = angr.Project('target_binary')
state = proj.factory.entry_state()
simgr = proj.factory.simgr(state)
simgr.explore(find=0x401000, avoid=0x401100)
if simgr.found:
    solution = simgr.found[0].posix.dumps(0)
```

## AI + JS 逆向

### LLM 辅助 AST 反混淆
```python
# 1. AST 解析混淆代码
# 2. LLM 识别混淆模式
# 3. 生成反混淆脚本
# 4. Babel AST 自动还原
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

