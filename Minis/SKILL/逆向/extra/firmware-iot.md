---
name: firmware-iot
description: 固件与 IoT 安全分析技能。固件提取 (binwalk/unblob)、QEMU 全系统仿真、模糊测试 (AFL++)、硬件调试 (UART/JTAG)。
author: 7452323
tags:
  - firmware
  - iot
  - embedded
  - binwalk
  - qemu
  - fuzzing
  - afl
  - uart
  - jtag
---

# 固件 / IoT 安全

## 固件提取

### 获取固件

| 来源 | 方法 |
|------|------|
| 官网下载 | 厂商网站/支持页 |
| OTA 升级 | 抓包拦截升级请求 |
| 串口 (UART) | 直接读取 Flash |
| SPI 编程器 | 直接读取芯片 |
| JTAG | 边界扫描读取 |
| 第三方 | 固件分享网站 |

### 固件分析工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **binwalk** | 固件分析和提取 | 最常用 |
| **unblob** | 现代固件提取 | NSFW 替代 |
| **firmadyne** | 固件仿真 | 自动启动 |
| **FAT** | 固件分析框架 | Firmadyne 简化版 |
| **EMBA** | 嵌入式漏洞分析 | 企业级 |
| **FACT** | 固件分析比较 | 自动化分析 |
| **cve-bin-tool** | CVE 检测 | 二进制漏洞匹配 |
| ** flashrom** | SPI 读取 | 硬件级 |
| **OpenOCD** | 调试 | JTAG/SWD |
| **JLink** | 调试 | Segger 硬件 |

### Binwalk 核心命令

```bash
# 扫描固件
binwalk firmware.bin

# 提取文件系统
binwalk -e firmware.bin

# 递归提取
binwalk -Me firmware.bin

# 自定义提取
binwalk -D 'gzip compressed' firmware.bin

# 熵分析 (检测加密)
binwalk -E firmware.bin
```

### 文件系统类型

| 文件系统 | 特征 | 用途 |
|----------|------|------|
| **SquashFS** | 只读压缩 | 最常见 |
| **UBI/UBIFS** | 闪存转换层 | NAND Flash |
| **JFFS2** | 日志结构 | NOR Flash |
| **YAFFS2** | NAND 专用 | 早期 Android |
| **CramFS** | 极简只读 | 早期嵌入式 |
| **Ext2/3/4** | Linux 标准 | 可写系统 |
| **FAT32** | Windows 兼容 | 简单系统 |
| **TmpFS** | 内存文件系统 | 临时文件 |
| **ProcFS** | 内核信息 | /proc |
| **SysFS** | 设备信息 | /sys |

## 固件分析流程

### 标准流程

```
固件获取 → binwalk 分析 → 文件系统提取 → 静态分析 → 动态仿真 → 漏洞挖掘
```

### 静态分析目标

| 目标 | 工具 | 说明 |
|------|------|------|
| 固件解包 | binwalk, unblob | 提取文件系统 |
| 文件浏览 | 手动/shell | 查看配置/脚本 |
| 密码破解 | hashcat, john | 提取哈希 |
| 私钥搜索 | grep | RSA/ECC 私钥 |
| 后门搜索 | grep -r "backdoor" | 已知后门 |
| 服务分析 | 检查 init 脚本 | 启动的服务 |
| 网络配置 | 配置文件 | 端口/服务 |
| Web 服务 | 固件内 Web 文件 | 前端漏洞 |

### 动态仿真

#### QEMU 全系统仿真

```bash
# 安装
sudo apt install qemu-system-mips qemu-system-arm qemu-utils

# MIPS 启动
qemu-system-mips -M malta -kernel vmlinux -hda rootfs.ext2 -append "root=/dev/sda" -net nic -net user

# ARM 启动
qemu-system-arm -M vexpress-a9 -kernel zImage -dtb vexpress-v2p-ca9.dtb -sd rootfs.ext2 -append "console=ttyAMA0,115200 root=/dev/mmcblk0p2" -net nic -net user

# 网络配置
-i -net nic -net user,hostfwd=tcp::8080-:80
```

#### Firmadyne

```bash
# 安装
git clone https://github.com/firmadyne/firmadyne
cd firmadyne
./configure

# 提取
./sources/extractor/extractor.py -b Brand -sql 1 -np -nk "firmware.bin" images/

# 创建镜像
./scripts/makeImage.sh 1

# 推断网络
./scripts/inferNetwork.sh 1

# 运行
./scripts/run.sh 1
```

#### FirmAE

```bash
# 比 Firmadyne 更高的成功率
git clone https://github.com/pr0v3rbs/FirmAE
cd FirmAE
./run.sh -r Brand firmware.bin
```

## 硬件调试

### UART (串口)

| 步骤 | 说明 |
|------|------|
| 1. 识别接口 | 万用表测 TX/RX/GND |
| 2. 确定波特率 | 逻辑分析仪/尝试常用值 |
| 3. 连接 | USB-TTL 转换器 |
| 4. 交互 | minicom/picocom/screen |
| 5. 利用 | 中断 bootloader/获取 shell |

### 常用波特率

```
9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600
```

### JTAG

| 引脚 | 说明 |
|------|------|
| TDI | Test Data In |
| TDO | Test Data Out |
| TMS | Test Mode Select |
| TCK | Test Clock |
| TRST | Test Reset (可选) |
| GND | 地 |

### SWD (Serial Wire Debug)

| 引脚 | 说明 |
|------|------|
| SWDIO | 数据线 |
| SWCLK | 时钟线 |
| GND | 地 |

### 调试工具

| 工具 | 用途 |
|------|------|
| **OpenOCD** | 开源调试 |
| **JLink** | Segger 商业调试 |
| **Bus Pirate** | 多功能工具 |
| **FT2232H** | 自制 JTAG |
| **GreatFET** | 硬件黑客工具 |
| **Shikra** | 硬件调试器 |
| **Logic Analyzer** | 逻辑分析 (Saleae) |

### 硬件分析工具

| 工具 | 用途 |
|------|------|
| **Bus Pirate** | SPI/I2C/UART |
| **Shikra** | 多功能 |
| **GreatFET** | 开源硬件 |
| **JTAGulator** | JTAG 引脚识别 |
| **Logic Analyzer** | 协议分析 |
| **Multimeter** | 电压/通断 |
| **Oscilloscope** | 波形分析 |

## IoT 协议

### 常见协议

| 协议 | 用途 | 端口 | 安全分析 |
|------|------|------|---------|
| **MQTT** | 发布订阅 | 1883/8883 | 未授权访问 |
| **CoAP** | 受限应用 | 5683/5684 | 资源暴露 |
| **Zigbee** | 低功耗无线 | — | 密钥嗅探 |
| **BLE** | 蓝牙低功耗 | — | 重放攻击 |
| **LoRaWAN** | 远距离无线 | — | 密钥泄露 |
| **Modbus** | 工业控制 | 502 | 明文传输 |
| **S7** | 西门子 PLC | 102 | 重放/DOS |
| **DNP3** | 电力 SCADA | 20000 | 命令注入 |
| **IEC 104** | 电力远动 | 2404 | 命令注入 |
| **MMS** | 制造报文 | 102 | 命令注入 |

### 工具

| 工具 | 用途 |
|------|------|
| **Wireshark** | 抓包分析 |
| **tcpdump** | 命令行抓包 |
| **mqtt-spy** | MQTT 客户端 |
| **gatttool** | BLE 交互 |
| **bettercap** | 网络攻击 |
| **Ubertooth** | BLE 嗅探 |
| **GNU Radio** | SDR 分析 |
| **HackRF** | SDR 硬件 |
| **RTL-SDR** | 低成本 SDR |

## 模糊测试 (Fuzzing)

### 分类

| 类型 | 说明 | 工具 |
|------|------|------|
| 黑盒 Fuzz | 无源码 | AFL, LibFuzzer |
| 白盒 Fuzz | 有源码 | AFL, LibFuzzer |
| 灰盒 Fuzz | 部分反馈 | AFL, LibFuzzer |
| 协议 Fuzz | 协议测试 | boofuzz, AFLNet |
| 内核 Fuzz | 系统调用 | syzkaller |
| 浏览器 Fuzz | DOM/JS | domato, jsfunfuzz |

### AFL++

```bash
# 编译
afl-gcc -o target target.c
afl-clang-fast -o target target.c

# Fuzzing
afl-fuzz -i input_dir -o output_dir -- ./target @@

# 持久模式
__AFL_INIT();
while (__AFL_LOOP(10000)) {
    // 测试代码
}
```

### LibFuzzer

```cpp
// fuzz_target.cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    // 测试代码
    return 0;
}

// 编译
clang++ -g -fsanitize=fuzzer fuzz_target.cpp -o fuzz_target

# 运行
./fuzz_target corpus/
```

### 协议 Fuzzing

```python
# boofuzz
from boofuzz import *

session = Session(target=Target(connection=TCPSocketConnection("192.168.1.1", 80)))

s_initialize("GET")
s_string("GET")
s_delim(" ")
s_string("/")
s_static("\r\n\r\n")

session.connect(s_get("GET"))
session.fuzz()
```

## 路由器固件漏洞常见类型

| 类型 | 说明 | 检测 |
|------|------|------|
| 命令注入 | 参数未过滤 | 参数 fuzz |
| 缓冲区溢出 | 输入过长 | 边界测试 |
| 认证绕过 | 硬编码密码 | 固件分析 |
| 未授权访问 | 默认配置 | 服务扫描 |
| CSRF | 无 token | 请求分析 |
| 目录穿越 | ../ 过滤不严 | 路径测试 |
| 后门 | 调试接口 | 端口扫描 |
| 信息泄露 | 错误信息 | 错误触发 |
| 更新无签名 | 固件可篡改 | 更新分析 |
| 硬编码密钥 | 私钥/密码 | grep 搜索 |
