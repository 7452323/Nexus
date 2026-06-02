---
name: protocol-reverse-engineering
description: "网络协议逆向工程。分析未知协议结构、还原消息格式、推断状态机。TRIGGER when: 用户需要逆向分析网络协议或API通信"
license: MIT
compatibility: Requires protobuf-inspector, netzob, Wireshark
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
---

# 协议逆向工程

## 触发条件

用户需要：
- 分析未知网络协议结构
- 还原API请求/响应格式
- 解析自定义二进制协议
- 分析IoT/游戏/设备通信协议

## 工具链

### protobuf-inspector（Protobuf专用）
```bash
# 安装
pip install protobuf-inspector

# 使用（无需.proto文件）
cat unknown_protobuf.bin | python -m protobuf_inspector
# 输出：自动推断的消息结构
```

### netzob（通用协议逆向）
```bash
# 安装
pip install netzob

# Python API
from netzob.all import *

# 导入捕获的数据
messages = PCAPImporter.readFile("capture.pcap")

# 协议推断
from netzob.Inference.all import *
format = Format(messages)
```

### Wireshark（网络抓包）
```bash
# 命令行抓包
tshark -i eth0 -w capture.pcap

# 过滤特定流量
tshark -r capture.pcap -Y "tcp.port == 8080"
```

## 分析流程

### Step 1: 数据捕获
```bash
# 抓包
tcpdump -i any -w capture.pcap port 8080

# 或用Wireshark GUI
```

### Step 2: 协议识别
```bash
# 检查是否为已知协议
file capture.pcap
strings capture.pcap | grep -i "http\|json\|xml\|protobuf"

# 检查是否为TLS/SSL
tshark -r capture.pcap -Y "tls"
```

### Step 3: 消息格式分析
```bash
# Protobuf分析
cat message.bin | python -m protobuf_inspector

# 自定义二进制分析
# 1. 识别固定头部（长度/类型/序列号）
# 2. 识别分隔符
# 3. 识别字段边界
# 4. 推断数据类型
```

### Step 4: 状态机推断
```bash
# 使用netzob
# 1. 导入多条消息
# 2. 自动推断状态转换
# 3. 生成协议模型
```

## 常见协议模式

### TLV格式
```
[Type 1-4B][Length 1-4B][Value NB]
```

### 固定头部+载荷
```
[Magic 2B][Version 1B][Length 2B][Payload NB][CRC 4B]
```

### 长度前缀
```
[Length 4B][Data NB]
```

### 分隔符分隔
```
[field1]\r\n[field2]\r\n[field3]\r\n
```

## 知识库引用

- `~/.hermes/knowledge/re-engineering/protocol-re/` — protobuf-inspector + netzob工具

## 其他工具

| 工具 | 用途 |
|------|------|
| URH (jopohl/urh) | 无线协议逆向（SDR支持） |
| Scapy | 数据包构造/解析 |
| CyberChef | 数据编解码 |
