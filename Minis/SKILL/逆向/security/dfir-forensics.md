---
name: dfir-forensics
description: 数字取证与事件响应 (DFIR) 技能。内存取证 (Volatility)、磁盘取证、日志分析、威胁狩猎、事件响应流程。
author: 7452323
tags:
  - dfir
  - forensics
  - incident-response
  - volatility
  - threat-hunting
  - memory-forensics
  - disk-forensics
---

# 数字取证与事件响应 (DFIR)

## 内存取证

### Volatility

| 插件 | 用途 | 说明 |
|------|------|------|
| **pslist** | 列出进程 | 基础枚举 |
| **pstree** | 进程树 | 父子关系 |
| **psscan** | 进程扫描 | 隐藏进程 |
| **cmdline** | 命令行参数 | 进程参数 |
| **consoles** | 控制台 | 命令历史 |
| **cmdscan** | 命令扫描 | 提取命令 |
| **getsids** | 获取 SID | 权限信息 |
| **privs** | 特权 | 进程特权 |
| **dlllist** | DLL 列表 | 加载的 DLL |
| **handles** | 句柄 | 对象句柄 |
| **filescan** | 文件扫描 | 内存文件 |
| **mutantscan** | 互斥体扫描 | 互斥体对象 |
| **symlinkscan** | 符号链接 | 符号链接 |
| **netscan** | 网络连接 | 网络信息 |
| **connscan** | 连接扫描 | TCP 连接 |
| **sockets** | Socket 扫描 | 所有 Socket |
| **sockscan** | Socket 扫描 | TCP/UDP |
| **timeliner** | 时间线 | 完整时间线 |
| **malfind** | 恶意代码查找 | 注入代码 |
| **ldrmodules** | 加载模块 | 隐藏 DLL |
| **apihooks** | API Hook | Hook 检测 |
| **idt** | IDT 表 | 中断描述符 |
| **gdt** | GDT 表 | 全局描述符 |
| **ssdt** | SSDT 表 | 系统服务表 |
| **driverirp** | 驱动 IRP | 驱动钩子 |
| **driverscan** | 驱动扫描 | 驱动对象 |
| **devicetree** | 设备树 | 设备对象 |
| **modules** | 内核模块 | 模块列表 |
| **modscan** | 模块扫描 | 隐藏模块 |
| **svcscan** | 服务扫描 | 服务枚举 |
| **printkey** | 注册表键 | 注册表 |
| **hivelist** | 注册表配置单元 | 注册表 |
| **hashdump** | 密码哈希 | SAM 哈希 |
| **lsadump** | LSA 密钥 | LSA 密钥 |
| **cachedump** | 缓存哈希 | 域缓存 |
| **procdump** | 进程转储 | 转储 PE |
| **memdump** | 内存转储 | 转储内存 |
| **vaddump** | VAD 转储 | 转储 VAD |
| **vadinfo** | VAD 信息 | VAD 详情 |
| **vadwalk** | VAD 遍历 | VAD 遍历 |
| **timers** | 定时器 | 内核定时器 |
| **unloadedmodules** | 卸载模块 | 卸载模块 |
| **yarascan** | YARA 扫描 | YARA 规则 |
| **shimcache** | Shimcache | 兼容性缓存 |
| **appcompatcache** | AppCompatCache | 兼容性缓存 |
| **atomscan** | Atom 扫描 | Atom 表 |
| **bigpools** | 大内存池 | 大内存池 |
| **kdbgscan** | KDBG 扫描 | 调试结构 |
| **krbtgt** | Krbtgt 哈希 | Kerberos |
| **envars** | 环境变量 | 进程环境 |
| **joblinks** | 作业链接 | 作业对象 |
| ** mutantscan** | 互斥体 | 互斥体 |

### Volatility 3

| 插件 | 用途 |
|------|------|
| **windows.pslist** | 进程列表 |
| **windows.pstree** | 进程树 |
| **windows.psscan** | 进程扫描 |
| **windows.cmdline** | 命令行 |
| **windows.netscan** | 网络扫描 |
| **windows.dlllist** | DLL 列表 |
| **windows.handles** | 句柄 |
| **windows.filescan** | 文件扫描 |
| **windows.malfind** | 恶意代码 |
| **windows.memmap** | 内存映射 |
| **windows.modules** | 模块 |
| **windows.svcscan** | 服务 |
| **windows.registry.hivelist** | 注册表 |
| **windows.hashdump** | 哈希转储 |
| **windows.cachedump** | 缓存转储 |
| **windows.lsadump** | LSA 转储 |
| **windows.timers** | 定时器 |
| **windows.windowstations** | 窗口站 |

### 内存取证流程

```
内存获取 → 转储 → 分析 → 报告
```

### 内存获取工具

| 工具 | 平台 | 说明 |
|------|------|------|
| **winpmem** | Windows | WinPmem |
| **DumpIt** | Windows | 一键转储 |
| **FTK Imager** | Windows | 取证工具 |
| **Belkasoft RAM Capturer** | Windows | 免费 |
| **Magnet RAM Capture** | Windows | 免费 |
| **LiME** | Linux | Linux Memory Extractor |
| **avml** | Linux | Acquire Volatile Memory Linux |
| **fmem** | Linux | 内核模块 |
| **qemu** | Linux | 虚拟机内存 |
| **Rekall** | 跨平台 | Volatility 替代品 |
| **MemProcFS** | Windows | 内存文件系统 |

## 磁盘取证

### Sleuth Kit + Autopsy

| 工具 | 用途 |
|------|------|
| **fsstat** | 文件系统信息 |
| **fls** | 文件列表 |
| **ils** | inode 链接列表 |
| **blkcat** | 块内容 |
| **blkls** | 块列表 |
| **blkstat** | 块状态 |
| **ffind** | 文件名查找 |
| **fsstat** | 文件系统统计 |
| **icat** | inode 内容 |
| **ifind** | inode 查找 |
| **istat** | inode 统计 |
| **jcat** | 日志内容 |
| **jls** | 日志列表 |
| **mactime** | MAC 时间线 |
| **sorter** | 文件分类 |

### 文件系统分析

| 文件系统 | 工具 | 说明 |
|----------|------|------|
| NTFS | FTK, Autopsy, TSK | Windows |
| FAT32 | FTK, Autopsy, TSK | 移动介质 |
| exFAT | FTK, Autopsy | 闪存 |
| Ext2/3/4 | TSK, Autopsy | Linux |
| HFS+ | TSK, Autopsy | Mac |
| APFS | blackbag, Cellebrite | Mac |
| YAFFS2 | 专用工具 | 嵌入式 |

### 时间线分析

| 工具 | 说明 |
|------|------|
| **Plaso/log2timeline** | 时间线创建 |
| **Timeline Explorer** | 时间线浏览 |
| **mactime** | MAC 时间线 |
| **timesketch** | 协作时间线 |

### Windows 取证重点

| 目标 | 路径/位置 | 说明 |
|------|----------|------|
| 注册表 | C:\Windows\System32\config | 系统配置 |
| 事件日志 | C:\Windows\System32\winevt\Logs | 系统日志 |
| 预取 | C:\Windows\Prefetch | 程序执行 |
| Amcache | C:\Windows\AppCompat\Programs | 程序执行 |
| Shimcache | 注册表 | 兼容性缓存 |
| SRUM | C:\Windows\System32\sru | 系统资源使用 |
| 回收站 | \$Recycle.Bin | 删除文件 |
| Jump Lists | %AppData%\Microsoft\Windows\Recent | 最近文件 |
| LNK 文件 | %AppData%\Microsoft\Windows\Recent | 快捷方式 |
| Thumbnail | %LocalAppData%\Microsoft\Windows\Explorer | 缩略图 |
| UsrClass.dat | %LocalAppData%\Microsoft\Windows | 用户注册表 |
| NTUSER.DAT | %UserProfile% | 用户注册表 |
| MFT | NTFS | 主文件表 |
| USN Journal | NTFS | 更新日志 |
| 页面文件 | pagefile.sys | 虚拟内存 |
| 休眠文件 | hiberfil.sys | 休眠内存 |
| 卷影副本 | System Volume Information | 快照 |

### Linux 取证重点

| 目标 | 路径 | 说明 |
|------|------|------|
| 日志 | /var/log | 系统日志 |
| 命令历史 | ~/.bash_history | 历史命令 |
| 用户 | /etc/passwd | 用户列表 |
| 密码哈希 | /etc/shadow | 密码 |
| SSH | ~/.ssh | SSH 密钥 |
| Cron | /var/spool/cron | 计划任务 |
| Systemd | /etc/systemd | 服务 |
| Auth | /var/log/auth.log | 认证日志 |
| Syslog | /var/log/syslog | 系统日志 |
| Messages | /var/log/messages | 消息日志 |
| Wtmp | /var/log/wtmp | 登录记录 |
| Utmp | /var/run/utmp | 当前登录 |
| Btmp | /var/log/btmp | 失败登录 |
| Lastlog | /var/log/lastlog | 最后登录 |

### macOS 取证重点

| 目标 | 路径 | 说明 |
|------|------|------|
| Unified Log | /var/log | 统一日志 |
| FSEvents | /.fseventsd | 文件系统变更 |
| plist | ~/Library/Preferences | 偏好设置 |
| Keychain | ~/Library/Keychains | 钥匙串 |
| KnowledgeC | CoreDuet | 用户行为 |
| Spotlight | .Spotlight-V100 | 搜索 |
| Time Machine | Backups.backupdb | 备份 |
| Quarantine | 元数据 | 下载来源 |
| Safari | ~/Library/Safari | 浏览历史 |
| Notes | 应用数据 | 备忘录 |
| Bumblebee | 恶意软件指标 | 恶意软件 |

## 事件响应

### NIST SP 800-61 事件响应生命周期

```
1. 准备 → 2. 检测与分析 → 3. 遏制/根除/恢复 → 4. 事后活动
```

### PICERL 模型

| 阶段 | 说明 | 输出 |
|------|------|------|
| **Preparation** | 准备 | 团队、工具、流程 |
| **Identification** | 识别 | 告警、确认、分级 |
| **Containment** | 遏制 | 短期遏制、长期遏制 |
| **Eradication** | 根除 | 清除威胁 |
| **Recovery** | 恢复 | 恢复业务 |
| **Lessons Learned** | 总结 | 改进措施 |

### 遏制策略

| 策略 | 说明 |
|------|------|
| 网络隔离 | 断开网络连接 |
| 账户禁用 | 禁用用户账户 |
| 进程终止 | 终止恶意进程 |
| 文件删除 | 删除恶意文件 |
| 防火墙阻断 | 阻断 C2 通信 |
| DNS 阻断 | 阻断 C2 域名 |
| 账户重置 | 重置密码 |
| 系统重装 | 彻底重装 |

### 事件响应工具

| 工具 | 用途 |
|------|------|
| **TheHive** | 事件管理平台 |
| **Cortex** | 分析引擎 |
| **MISP** | 威胁情报共享 |
| **OpenCTI** | 威胁情报平台 |
| **Velociraptor** | 端点可见性 |
| **GRR Rapid Response** | 事件响应 |
| **osquery** | 端点查询 |
| **Wazuh** | SIEM/XDR |
| **Snort** | IDS/IPS |
| **Suricata** | IDS/IPS |
| **Zeek** | 网络分析 |
| **Moloch** | 网络取证 |
| **NetworkMiner** | 网络取证 |

## 威胁狩猎 (Threat Hunting)

### 假设驱动狩猎

```
假设生成 → 数据收集 → 分析验证 → 结论输出
```

### MITRE ATT&CK 框架

| 战术 | 说明 |
|------|------|
| Reconnaissance | 侦察 |
| Resource Development | 资源开发 |
| Initial Access | 初始访问 |
| Execution | 执行 |
| Persistence | 持久化 |
| Privilege Escalation | 权限提升 |
| Defense Evasion | 防御规避 |
| Credential Access | 凭证访问 |
| Discovery | 发现 |
| Lateral Movement | 横向移动 |
| Collection | 收集 |
| Command and Control | 命令控制 |
| Exfiltration | 渗出 |
| Impact | 影响 |

### 威胁狩猎数据源

| 数据源 | 说明 |
|--------|------|
| 进程事件 | 进程创建/终止 |
| 网络连接 | 连接/监听 |
| 文件事件 | 创建/修改/删除 |
| 注册表 | 修改/删除 |
| DNS 查询 | 域名解析 |
| 认证事件 | 登录/失败 |
| PowerShell | 脚本执行 |
| WMI 事件 | WMI 活动 |
| API 调用 | 系统调用 |
| 驱动加载 | 内核模块 |

### 检测规则

| 规则类型 | 说明 | 工具 |
|---------|------|------|
| YARA | 文件/内存特征 | YARA |
| Sigma | 通用检测规则 | Sigma |
| Snort/Suricata | 网络规则 | Snort |
| KQL | Kusto 查询 | Sentinel |
| SPL | Splunk 查询 | Splunk |
| EQL | Event Query Language | Elastic |

## 日志分析

### 日志来源

| 来源 | 类型 | 说明 |
|------|------|------|
| Windows Event | 系统日志 | 安全/系统/应用 |
| Syslog | 系统日志 | Linux 标准 |
| Nginx/Apache | Web 日志 | 访问/错误 |
| DNS | 域名日志 | 解析查询 |
| Firewall | 防火墙日志 | 允许/拒绝 |
| VPN | VPN 日志 | 连接/断开 |
| Proxy | 代理日志 | Web 访问 |
| EDR | 端点日志 | 行为监控 |
| Cloud | 云日志 | API 调用 |
| Email | 邮件日志 | 发送/接收 |
| Database | 数据库日志 | 查询/修改 |

### ELK 栈

| 组件 | 功能 |
|------|------|
| **Elasticsearch** | 搜索/分析引擎 |
| **Logstash** | 日志收集/处理 |
| **Kibana** | 可视化 |
| **Beats** | 轻量采集 |

### Splunk 查询示例

```spl
# 可疑进程创建
index=windows EventCode=4688 
| where NewProcessName IN ("*powershell.exe", "*cmd.exe", "*wscript.exe")
| stats count by ComputerName, NewProcessName, CreatorProcessName

# 异常网络连接
index=windows EventCode=5156 
| where DestPort IN (4444, 8080, 443)
| stats count by SourceIP, DestIP, DestPort
```

## 常用取证命令

### Windows

```powershell
# 获取系统信息
systeminfo

# 获取网络配置
ipconfig /all

# 获取进程
tasklist /v
Get-Process

# 获取网络连接
netstat -ano

# 获取服务
Get-Service

# 获取计划任务
Get-ScheduledTask

# 获取注册表
Get-ItemProperty -Path "HKLM:\..."

# 获取事件日志
Get-WinEvent -LogName Security -MaxEvents 100
Get-EventLog -LogName Security -Newest 100

# 获取用户
Get-LocalUser
net user

# 获取哈希
Invoke-Mimikatz -Command "sekurlsa::logonpasswords"
```

### Linux

```bash
# 系统信息
uname -a
cat /etc/os-release

# 进程
ps aux
ps -ef

# 网络
netstat -tulpn
ss -tulpn
lsof -i

# 用户
cat /etc/passwd
last
lastlog
who
w

# 日志
journalctl
cat /var/log/auth.log
cat /var/log/syslog

# 文件
find / -name "*.sh" -mtime -7
find / -perm -4000  # SUID
find / -perm -2000  # SGID

# 命令历史
cat ~/.bash_history
cat ~/.zsh_history

# 定时任务
crontab -l
cat /etc/crontab
ls /etc/cron.*
```
