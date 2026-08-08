---
name: grpc-protobuf-reverse
description: gRPC/Protobuf 协议逆向与渗透 — 解析 .proto schema、解码 wire format、Burp/Mitmproxy 插件、gRPC-Web 流量分析
category: reverse-engineering
triggers:
  - gRPC 逆向
  - protobuf 解码
  - protobuf decoder
  - gRPC MITM
  - gRPC proxy
  - proto 文件提取
  - protobuf wire format
  - application/grpc
  - grpc-web
  - gRPC pentest
---

# gRPC/Protobuf 协议逆向

来源：合并自 `protocol-reverse-engineering` 的 gRPC 部分 + GitHub 搜寻补全。

## 核心工具链

| 工具 | 用途 | 仓库 |
|------|------|------|
| **protorev** | 未知 protobuf 流逆向，自动推断字段类型 | github.com/patrickomatic/protorev |
| **pbtk** | Protobuf 编辑/重放/Fuzz GUI | github.com/marin-m/pbtk |
| **grpc-pentest-suite** | gRPC 渗透测试套件（反射枚举、SQLi、命令注入） | github.com/nxenon/grpc-pentest-suite |
| **PortSwigger/protobuf-decoder** | Burp Suite 扩展，解码/编码 protobuf | github.com/PortSwigger/protobuf-decoder |
| **Microlens.Proto** | 无 schema 直接解析 wire format | github.com/microlens-solutions/proto |
| **grpcurl** | gRPC 反射调用，类似 curl | github.com/fullstorydev/grpcurl |
| **grpcui** | gRPC Web UI，交互式调试 | github.com/fullstorydev/grpcui |
| **mitmproxy + protobuf addon** | 中间人代理自动解码 protobuf | github.com/mitmproxy/mitmproxy |

## 逆向流程

### 1. 识别 gRPC 流量

```
HTTP/2 特征：
- Content-Type: application/grpc
- grpc-status / grpc-message headers
- 请求路径 /package.Service/Method
- 数据为二进制 protobuf wire format
```

Wireshark 过滤器：`http2.content_type contains "grpc"`

### 2. 提取 .proto 定义

**方法 A：服务端反射**
```bash
# 列出所有服务
grpcurl -plaintext target:50051 list

# 查看服务方法
grpcurl -plaintext target:50051 describe package.Service

# 导出 proto 定义
grpcurl -plaintext target:50051 describe > service.proto
```

**方法 B：JS Bundle 提取（gRPC-Web）**
```javascript
// gRPC-Web 客户端通常嵌入在 webpack bundle 中
// 搜索关键字: "proto.", "grpc.", "serializeBinary", "deserializeBinary"
// 用 webpack-unpack 提取模块后从 JS 代码还原 proto 定义
```

**方法 C：逆向 wire format**
```bash
# protorev - 分析未知 protobuf 流
protorev analyze capture.bin

# 输出推断的字段类型、嵌套结构
# 自动生成 draft .proto 文件
```

### 3. MITM 代理解码

**Burp Suite**：
1. 安装 PortSwigger/protobuf-decoder 扩展
2. 拦截 gRPC-Web 请求，自动解码 base64 + protobuf
3. 手动编辑字段后重新编码发送

**mitmproxy**：
```python
# mitmproxy protobuf addon
from mitmproxy import http
from protobuf_decoder import decode_protobuf

def response(flow: http.HTTPFlow):
    if flow.response.content and b'proto' in flow.response.headers.get('content-type', ''):
        decoded = decode_protobuf(flow.response.content)
        print(decoded)
```

### 4. 渗透测试

```bash
# 安装 grpc-pentest-suite
git clone https://github.com/nxenon/grpc-pentest-suite

# 反射枚举
python grpc_pentest.py --host target:50051 --enum

# SQL 注入测试
python grpc_pentest.py --host target:50051 --sqli

# 命令注入测试
python grpc_pentest.py --host target:50051 --cmdi
```

## gRPC-Web 特殊处理

gRPC-Web 使用 `application/grpc-web+proto` 或 `application/grpc-web-text`（base64）。

```bash
# 解码 grpc-web-text
echo "AAAAAAYKBHRlc3Q=" | base64 -d | xxd
# 前5字节是 gRPC 帧头（1压缩+4长度），之后是 protobuf payload

# 用 protoc 解码已知类型
echo "..." | protoc --decode_raw
```

## protobuf wire format 速查

| Wire Type | 含义 | 用于 |
|-----------|------|------|
| 0 | Varint | int32, int64, uint32, bool, enum |
| 1 | 64-bit | fixed64, sfixed64, double |
| 2 | Length-delimited | string, bytes, embedded messages, packed |
| 3 | Start group | deprecated |
| 4 | End group | deprecated |
| 5 | 32-bit | fixed32, sfixed32, float |

```
字段编码：field_number << 3 | wire_type
例如 0x08 = 0000 1000 → field 1, wire type 0 (Varint)
```

## 已知局限

1. gRPC 反射可能被禁用（生产环境常见），需要 fallback 到逆向 JS bundle 或 wire format
2. 双向流（bidirectional streaming）MITM 困难，需要特殊代理
3. TLS 加密的 gRPC 需要证书 pinning 绕过（Android: Frida script, iOS: SSL Kill Switch 2）
