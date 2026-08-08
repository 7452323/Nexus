---
name: security-tools
category: reverse-engineering
description: >-
  Merged skill combining: security-toolchain, security-tools-installation.
version: "1.0"
sources:
  - security-toolchain
  - security-tools-installation
tags: [reverse-engineering, merged]
---

# security-tools

> **Merged from**: security-toolchain, security-tools-installation
> **Source count**: 2

---

## Table of Contents

1. [security-toolchain](#security-toolchain)
2. [security-tools-installation](#security-tools-installation)

---

## security-toolchain

# 安全工具链安装 (Security Toolchain Setup)

安全研究环境工具安装方法论。当 `apt`/`pip`/`go install` 失败或系统无包时的替代方案。

## 核心策略

| 优先级 | 方法 | 适用场景 |
|--------|------|----------|
| 1 | `pip install --break-system-packages` | Python 工具（sqlmap, wafw00f, dirsearch） |
| 2 | `go install` | Go 工具（nuclei, ffuf, naabu, gobuster） |
| 3 | GitHub Releases 预编译二进制 | Rust/Go 工具（feroxbuster, httpx） |
| 4 | GitHub Releases RPM + Python rpmfile 提取 | 仅有 RPM 的工具（nmap 静态包） |
| 5 | 源码编译 | C/C++ 工具（nmap, masscan, Ruby） |

## 通用模式

### Go 工具安装

```bash
export PATH="$PATH:/root/go/bin"
go install github.com/xxx/cmd@latest
# 持久化：echo 'export PATH="$PATH:/root/go/bin"' >> ~/.bashrc
```

### RPM 提取（当 rpm2cpio 不可用时）

适用场景：nmap 静态 RPM（nmap.org/dist/nmap-*-1.x86_64.rpm），GitHub releases 上 nmap RPM 不存在。

```python
import rpmfile, os
with rpmfile.open('/tmp/nmap.rpm') as rpm:
    for member in rpm.getmembers():
        if member.name and ('bin/nmap' in member.name or 'bin/ncat' in member.name):
            os.makedirs(os.path.dirname(f'/tmp/out/{member.name}'), exist_ok=True)
            with open(f'/tmp/out/{member.name}', 'wb') as f:
                f.write(member.data)  # 注意：RPMFile 没有 read() 方法
```

**备选：rpm2cpio + cpio（需 apt 安装 rpm2cpio）**

```bash
apt-get install -y rpm2cpio
cd /tmp && rpm2cpio nmap.rpm | cpio -idmv
```

**⚠️ 注意：** nmap RPM 内含 nmap 二进制但**不一定含 ncat**。缺 ncat 时需从源码单独编译 ncat 子目录。

### 源码编译标准流程

```bash
./configure --prefix=/usr/local --disable-install-doc
make -j$(nproc)
make install
```

## 已知陷阱

- **masscan `--version` 返回 exit 1** 但输出正常，非真正失败
- **WhatWeb 必须在自身目录运行** 或用 `require_relative` 修复路径
- **nikto** 需要 `EXECDIR` 和 `PLUGINDIR` 配置才能启动
- **Ruby psych** 需要系统 `libyaml-dev`，无包时从 yaml.org 源码编译
- **curl-impersonate** 用预编译 tar.gz，不含 ncat 的 nmap RPM 需确认内容
- **Go 1.23 不支持部分新工具** 需 1.25+ 时从官方 tarball 升级

## 详见

- [references/tool-install-recipes.md](references/tool-install-recipes.md) — 具体工具安装命令（nmap/ncat, masscan, nikto, feroxbuster, whatweb, wpscan, curl-impersonate）

---

## security-tools-installation

# Security Tools Installation

最小化 Debian 系统（无 snap/flatpak/cargo/gem/fpm）上安装安全研究工具的方法论。

## 适用场景

- 标准包管理器（apt/pip/go）找不到工具
- 需要最新版本但系统仓库只有旧版
- Docker/容器内快速部署

## 安装策略优先级

1. **pip/apt/go install** — 优先（pip 需 `--break-system-packages`）
2. **GitHub Releases 预编译二进制** — 下载即用（feroxbuster、curl-impersonate）
3. **RPM 解包** — 无 apt 包但有 .rpm 时（Python rpmfile）
4. **源码编译** — 兜底方案（nmap、masscan、Ruby）
5. **Git clone + 手动配置** — Perl/Ruby 脚本类工具

## 工具安装速查

### nmap + ncat（源码编译）

```bash
curl -sL "https://nmap.org/dist/nmap-7.95.tar.bz2" -o /tmp/nmap.tar.bz2
cd /tmp && tar -xjf nmap.tar.bz2 && cd nmap-7.95
./configure --without-zenmap && make -j$(nproc)
cp nmap /usr/local/bin/
cd ncat && ./configure --with-libssl && make -j$(nproc)
cp ncat /usr/local/bin/
```

### ncat（单独提取自 RPM）

```bash
curl -sL "https://nmap.org/dist/nmap-7.95-1.x86_64.rpm" -o /tmp/nmap.rpm
pip install rpmfile
python3 -c "
import rpmfile, os
with rpmfile.open('/tmp/nmap.rpm') as rpm:
    for m in rpm.getmembers():
        if m.name and 'bin/ncat' in m.name:
            os.makedirs('/tmp/nmap_ex', exist_ok=True)
            with open(f'/tmp/nmap_ex/{m.name}', 'wb') as f:
                f.write(rpm.member(m.name).read())
"
cp /tmp/nmap_ex/usr/bin/ncat /usr/local/bin/
```

### masscan（源码编译）

```bash
curl -sL "https://github.com/robertdavidgraham/masscan/archive/refs/tags/1.3.2.tar.gz" -o /tmp/masscan.tar.gz
cd /tmp && tar -xzf masscan.tar.gz && cd masscan-1.3.2
make -j$(nproc) && cp bin/masscan /usr/local/bin/
```

### curl-impersonate（预编译二进制）

```bash
curl -sL "https://github.com/lwthiker/curl-impersonate/releases/download/v0.6.0-alpha.1/curl-impersonate-v0.6.0-alpha.1.x86_64-linux-gnu.tar.gz" -o /tmp/curl-imp.tar.gz
tar -xzf /tmp/curl-imp.tar.gz -C /tmp/ && cp /tmp/curl-impersonate-* /usr/local/bin/
```

### feroxbuster（预编译二进制）

```bash
URL=$(curl -sL "https://api.github.com/repos/epi052/feroxbuster/releases" | grep "browser_download_url.*x86_64-linux.*tar.gz" | head -1 | cut -d'"' -f4)
curl -sL "$URL" -o /tmp/ferox.tar.gz && tar -xzf /tmp/ferox.tar.gz -C /tmp/
cp /tmp/feroxbuster /usr/local/bin/
```

### nikto（Git clone + Perl 配置）

```bash
curl -sL "https://github.com/sullo/nikto/archive/refs/heads/master.tar.gz" -o /tmp/nikto.tar.gz
cd /tmp && tar -xzf nikto.tar.gz
cp -r /tmp/nikto-main/program /usr/local/share/nikto
cp /tmp/nikto-main/program/nikto.pl /usr/local/bin/nikto
cpan XML::Writer
sed -i 's|# EXECDIR=/opt/nikto|EXECDIR=/usr/local/share/nikto|' /tmp/nikto-main/program/nikto.conf.default
sed -i 's|# PLUGINDIR=/opt/nikto/plugins|PLUGINDIR=/usr/local/share/nikto/plugins|' /tmp/nikto-main/program/nikto.conf.default
cp /tmp/nikto-main/program/nikto.conf.default /etc/nikto.conf
```

### whatweb（Git clone + 路径修复）

```bash
curl -sL "https://github.com/urbanadventurer/WhatWeb/archive/refs/heads/master.tar.gz" -o /tmp/whatweb.tar.gz
cd /tmp && tar -xzf whatweb.tar.gz
cp -r /tmp/WhatWeb-master /usr/local/share/whatweb
ln -s /usr/local/share/whatweb/whatweb /usr/local/bin/whatweb
```

### wpscan（需 Ruby + gem）

```bash
curl -sL "https://cache.ruby-lang.org/pub/ruby/3.3/ruby-3.3.4.tar.gz" -o /tmp/ruby.tar.gz
cd /tmp && tar -xzf ruby.tar.gz && cd ruby-3.3.4
./configure --prefix=/usr/local --disable-install-doc && make -j$(nproc) && make install
curl -sL "https://pyyaml.org/download/libyaml/yaml-0.2.5.tar.gz" -o /tmp/yaml.tar.gz
cd /tmp && tar -xzf yaml.tar.gz && cd yaml-0.2.5
./configure --prefix=/usr/local && make && make install
cd /tmp/ruby-3.3.4/ext/psych && ruby extconf.rb --with-yaml-dir=/usr/local && make && make install
gem install wpscan
```

## 常见坑

### apt 找不到包
Debian 最小化安装缺少很多包。`apt-cache search` 确认是否存在，不存在则走源码/GitHub。

### pip 需 `--break-system-packages`
PEP 668 限制，必须加此标志。

### RPM 提取
无 `rpm2cpio` 时用 Python `rpmfile`。注意 `RPMFile` 没有 `.read()` 方法，用 `member(name).read()`。

### GitHub Releases URL
GitHub releases 页面可能返回 "Not Found"（tar.gz 不存在）。用 GitHub API 查询实际下载链接：
```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/releases" | grep "browser_download_url"
```

### 路径修复
Git clone 的脚本常硬编码路径（如 nikto 的 `/opt/nikto`）。安装后需 `sed -i` 修正到实际安装路径。

## 参考

- `references/debian-install-guide.md` — 完整工具安装清单和验证命令

---
