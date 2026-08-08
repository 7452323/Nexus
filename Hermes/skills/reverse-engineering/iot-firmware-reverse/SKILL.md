---
name: iot-firmware-reverse
description: 固件/IoT逆向 — binwalk/unblob 提取、squashfs/JFFS2 解析、QEMU 全系统仿真、UART/JTAG 硬件调试
category: reverse-engineering
triggers:
  - 固件逆向
  - IoT 逆向
  - 路由器逆向
  - binwalk
  - firmware extraction
  - QEMU 仿真
  - UART
  - JTAG
  - 嵌入式逆向
  - 摄像头逆向
  - squashfs
---

# 固件/IoT 逆向

来源：GitHub 搜寻补全（2025-2026 最新）。

## 核心工具链

| 工具 | 用途 | 仓库/安装 |
|------|------|-----------|
| **binwalk** | 固件分析/提取（Rust 重写版） | github.com/ReFirmLabs/binwalk |
| **unblob** | 固件提取（支持 30+ 格式） | github.com/onekey-sec/unblob |
| **firmware-mod-kit (FMK)** | 固件修改/重打包 | github.com/rampageX/firmware-mod-kit |
| **FAT (Firmware Analysis Toolkit)** | QEMU 自动化仿真 | github.com/attify/firmware-analysis-toolkit |
| **Firmadyne** | 大规模固件仿真 | github.com/firmadyne/firmadyne |
| **EMBA** | 固件安全扫描器 | github.com/e-m-b-a/emba |
| **QEMU** | 用户态/全系统仿真 | apt install qemu-user-static qemu-system |
| **flashrom** | SPI Flash 读取/写入 | apt install flashrom |
| **OpenOCD** | JTAG/SWD 调试 | apt install openocd |

## 固件获取

### 方法 A：官网下载
```bash
# 搜索厂商支持页面
# 常见格式：.bin, .img, .zip, .tar.gz, .chk, .trx
```

### 方法 B：硬件提取
```bash
# 1. 识别 Flash 芯片（SPI NOR / NAND）
# 2. 用 SOIC-8 夹子连接 flashrom
flashrom -p linux_spi:dev=/dev/spidev0.0 -r firmware.bin

# 3. 或用 JTAG/SWD 读取
openocd -f interface/jlink.cfg -f target/stm32f1x.cfg
```

### 方法 C：OTA 抓包
```bash
# 路由器 OTA 更新时抓包
mitmproxy --mode transparent
# 提取下载的固件 URL
```

## 固件分析

### 1. 初步分析
```bash
# binwalk 扫描（新版 Rust）
binwalk firmware.bin

# 提取文件系统
binwalk -e firmware.bin

# unblob（更全面的格式支持）
unblob firmware.bin

# 查看文件系统类型
file extracted/*
# squashfs: "Squashfs filesystem"
# JFFS2: "JFFS2 filesystem"
# cpio: "cpio archive"
# cramfs: "Linux Compressed ROM File System"
```

### 2. 文件系统提取

```bash
# squashfs
unsquashfs rootfs.squashfs

# JFFS2
jefferson rootfs.jffs2 -d output/

# cpio
cpio -idmv < rootfs.cpio

# ubifs
ubireader_extract_images ubi.img
```

### 3. 关键文件分析

```bash
# 查找硬编码凭证
grep -r "password\|passwd\|admin\|root" extracted/ 2>/dev/null

# 查找私钥/证书
find extracted/ -name "*.pem" -o -name "*.key" -o -name "*.crt"

# 查找 Web 服务配置
find extracted/ -name "*.conf" -o -name "*.cfg" -o -name "*.ini"

# 查找启动脚本
cat extracted/etc/rc.d/* 2>/dev/null
cat extracted/etc/init.d/* 2>/dev/null

# 查找 shadow 文件
cat extracted/etc/shadow
```

## QEMU 仿真

### 用户态仿真（运行单个二进制）
```bash
# 安装对应架构的 qemu
apt install qemu-user-static

# 运行 ARM 二进制
qemu-arm-static -L extracted/ extracted/usr/sbin/httpd

# 运行 MIPS 二进制
qemu-mipsel-static -L extracted/ extracted/bin/busybox
```

### 全系统仿真（FAT）
```bash
# 用 FAT 自动化
git clone https://github.com/attify/firmware-analysis-toolkit
cd firmware-analysis-toolkit

# 修改 fat.config（设置固件路径和 sudo 密码）
./fat.py firmware.bin

# FAT 自动：
# 1. 提取文件系统
# 2. 识别架构（ARM/MIPS/x86）
# 3. 配置 QEMU 网络
# 4. 启动仿真
# 5. 提供 shell 访问
```

### 手动 QEMU 全系统仿真
```bash
# MIPS 路由器仿真
qemu-system-mips \
  -M malta \
  -kernel vmlinux \
  -hda rootfs.ext2 \
  -nographic \
  -netdev user,id=net0,hostfwd=tcp::8080-:80 \
  -device e1000,netdev=net0

# 访问：http://localhost:8080
```

## 硬件调试

### UART
```
引脚识别：
- VCC (3.3V/5V) — 用万用表测
- GND — 对地导通
- TX — 启动时电压波动
- RX — 同 TX

连接：
USB-TTL → 路由器 UART
  TX   →   RX
  RX   →   TX
  GND  →   GND

波特率常见：115200, 57600, 9600
```

```bash
screen /dev/ttyUSB0 115200
# 或
minicom -b 115200 -D /dev/ttyUSB0
```

### JTAG/SWD
```bash
# 用 OpenOCD 连接
openocd -f interface/jlink.cfg -f target/stm32f1x.cfg

# GDB 连接
arm-none-eabi-gdb -ex "target remote localhost:3333"
# dump 内存
(gdb) dump binary memory flash.bin 0x08000000 0x08080000
```

## 安全测试清单

- [ ] 硬编码凭证（grep password/shadow）
- [ ] 默认 Web 登录（admin/admin, root/root）
- [ ] 未加密的固件更新（HTTP OTA）
- [ ] 开启的调试接口（UART shell 无密码）
- [ ] 弱加密（硬编码 AES key）
- [ ] 命令注入（ping/traceroute 参数）
- [ ] 栈溢出（Web CGI 二进制）
- [ ] 后门账户（厂商隐藏的 telnet/ssh 账户）

## 常见架构速查

| 架构 | QEMU 二进制 | 字节序 | 常见设备 |
|------|------------|--------|----------|
| ARM (32-bit) | qemu-arm-static | LE | 路由器、摄像头 |
| ARM (64-bit) | qemu-aarch64-static | LE | 新路由器、TV |
| MIPS (32-bit) | qemu-mipsel-static | LE | 老路由器 |
| MIPS (32-bit BE) | qemu-mips-static | BE | 部分路由器 |
| MIPS64 | qemu-mips64el-static | LE | 高端路由器 |
| x86 | qemu-i386-static | LE | 工控设备 |
| PowerPC | qemu-ppc-static | BE | 老网络设备 |

## 已知局限

1. QEMU 不支持所有外设（WiFi 芯片、硬件加密引擎等）→ 部分功能无法仿真
2. NAND Flash 需要 OOB 数据 → 比 NOR 提取复杂
3. 加密固件（TP-Link、D-Link 新设备）需要先找到解密密钥
4. Secure Boot 设备可能无法修改固件重刷
