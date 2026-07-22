---
name: cloud-security
description: 云安全与容器安全技能。云平台配置审计 (AWS/Azure/GCP)、容器安全 (Docker/K8s)、容器逃逸、IaC安全。
author: 7452323
tags:
  - cloud-security
  - aws
  - azure
  - gcp
  - kubernetes
  - docker
  - container-escape
  - iac
---

# 云安全与容器安全

## 云平台安全

### 三大云平台核心服务

| 功能 | AWS | Azure | GCP |
|------|-----|-------|-----|
| 计算 | EC2 | Virtual Machines | Compute Engine |
| 存储 | S3 | Blob Storage | Cloud Storage |
| 数据库 | RDS | SQL Database | Cloud SQL |
| IAM | IAM | Azure AD | Cloud IAM |
| 网络 | VPC | VNet | VPC |
| 容器 | EKS/ECS | AKS/ACI | GKE |
| 无服务器 | Lambda | Functions | Cloud Functions |
| KMS | KMS | Key Vault | Cloud KMS |

### 常见云配置错误

| 错误 | 危害 | 检测工具 |
|------|------|---------|
| S3 Bucket 公开 | 数据泄漏 | Prowler, ScoutSuite |
| IAM 过度授权 | 权限提升 | Prowler, Splunk |
| 安全组配置不当 | 未授权访问 | Prowler, ScoutSuite |
| 存储账户公开 | 数据泄漏 | ScoutSuite |
| 日志未开启 | 无法审计 | Prowler |
| 加密未启用 | 数据泄漏 | Prowler |
| 公开快照/AMI | 数据泄漏 | Prowler |
| VPC 流日志未开 | 无法审计 | Prowler |
| 密码策略弱 | 账号爆破 | Prowler |
| MFA 未启用 | 账号劫持 | Prowler |

### 云安全工具

| 工具 | 用途 | 平台 |
|------|------|------|
| **Prowler** | AWS/Azure/GCP 安全审计 | 全平台 |
| **ScoutSuite** | 多云安全审计 | 全平台 |
| **CloudSploit** | 云配置扫描 | 全平台 |
| **Pacu** | AWS 渗透测试 | AWS |
| **Terraform** | IaC 部署 | 全平台 |
| **Checkov** | IaC 安全扫描 | 全平台 |
| **tfsec** | Terraform 安全 | 全平台 |
| **kubescape** | K8s 安全 | Kubernetes |
| **kube-bench** | K8s CIS 基准 | Kubernetes |
| **Trivy** | 容器镜像扫描 | 全平台 |
| **Grype** | 漏洞扫描 | 全平台 |
| **Falco** | 运行时安全 | Kubernetes |

### 云渗透测试流程

```
信息收集 → 配置审计 → 权限枚举 → 横向移动 → 数据渗出 → 持久化
```

### AWS 渗透测试

| 阶段 | 工具 | 命令示例 |
|------|------|---------|
| 枚举 | enumerate-iam | python3 enumerate_iam.py |
| 权限 | PACU | run pacu |
| 存储 | S3Scanner | pip3 install s3scanner |
| 枚举 | aws_recon | aws_recon |
| 枚举 | cloud_enum | cloud_enum |
| 利用 | Principal Mapper | pmapper graph create |

### Azure 渗透测试

| 工具 | 用途 |
|------|------|
| **MicroBurst** | Azure 渗透测试 |
| **AzureHound** | BloodHound for Azure |
| **ROAD** | Azure AD 攻击 |
| **Stormspotter** | Azure 安全态势 |
| **PowerZure** | Azure 渗透框架 |

### GCP 渗透测试

| 工具 | 用途 |
|------|------|
| **GCPBucketBrute** | GCS 枚举 |
| **GCPwn** | GCP 渗透 |
| **Pentest-Tools-GCP** | GCP 渗透 |

## 容器安全

### Docker 安全

| 风险 | 说明 | 防御 |
|------|------|------|
| 特权容器 | --privileged | 避免使用 |
| Socket 挂载 | -v /var/run/docker.sock | 禁止 |
| 敏感目录挂载 | -v /:/host | 限制 |
| 主机网络 | --net=host | 避免 |
| 过多能力 | --cap-add=ALL | 最小权限 |
| Root 容器 | USER root | 非 root |
| 基础镜像漏洞 | 旧版本/官方 | 定期扫描 |
| 敏感信息泄露 | 硬编码密码 | Secret 管理 |

### Docker 安全命令

```bash
# 安全扫描
docker scan image:tag

# 查看容器能力
docker inspect --format '{{.HostConfig.CapAdd}}' container

# 查看挂载点
docker inspect --format '{{.Mounts}}' container

# 查看特权模式
docker inspect --format '{{.HostConfig.Privileged}}' container

# 查看网络模式
docker inspect --format '{{.HostConfig.NetworkMode}}' container
```

### Kubernetes 安全

| 风险 | 说明 | 防御 |
|------|------|------|
| API Server 暴露 | 未授权访问 | RBAC + 认证 |
| etcd 未授权 | 存储所有数据 | TLS + 认证 |
| Dashboard 暴露 | Web UI 暴露 | 禁止公开 |
| Kubelet 暴露 | 10250 端口 | 认证授权 |
| 特权 Pod | privileged: true | Pod Security |
| hostNetwork | hostNetwork: true | 避免 |
| hostPID | hostPID: true | 避免 |
| hostIPC | hostIPC: true | 避免 |
| 未受限的服务账户 | automountServiceAccountToken | false |
| 容器逃逸 | 内核漏洞 | 更新补丁 |

### K8s 安全工具

| 工具 | 用途 |
|------|------|
| **kubescape** | K8s 安全扫描 |
| **kube-bench** | CIS 基准 |
| **kube-hunter** | K8s 渗透 |
| **kubeaudit** | K8s 审计 |
| **Trivy** | 镜像扫描 |
| **Falco** | 运行时检测 |
| **Kyverno** | 策略引擎 |
| **OPA/Gatekeeper** | 策略引擎 |
| **Starboard** | 安全编排 |
| **kubesploit** | K8s 渗透 |

### RBAC 安全

```yaml
# 危险配置
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: dangerous-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
---
# 安全配置
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: safe-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

## 容器逃逸

### 逃逸技术

| 技术 | 条件 | 难度 |
|------|------|------|
| **特权容器** | --privileged | ⭐ 简单 |
| **Socket 挂载** | docker.sock 挂载 | ⭐ 简单 |
| **内核漏洞** | 旧内核 | ⭐⭐⭐ |
| **Capabilities 滥用** | CAP_SYS_ADMIN 等 | ⭐⭐ |
| **procfs 挂载** | /proc 暴露 | ⭐⭐ |
| **cgroup release_agent** | notify_on_release | ⭐⭐⭐ |
| **Device cgroup** | 设备访问权限 | ⭐⭐⭐ |
| **core_pattern** | 宿主机可写 | ⭐⭐⭐ |
| **RunC 漏洞** | CVE-2019-5736 | ⭐⭐ |
| **Binfmt_misc** | 辅助二进制格式 | ⭐⭐⭐ |
| **eBPF** | CAP_BPF | ⭐⭐⭐⭐ |
| **Kernel module** | CAP_SYS_MODULE | ⭐⭐ |

### 逃逸工具

| 工具 | 用途 |
|------|------|
| **CDK** | 容器安全评估和渗透 |
| **botb** | 容器逃逸 |
| **deepce** | 容器逃逸脚本 |
| **ConMachi** | 容器安全 |
| **Peirates** | K8s 渗透 |

### 检测容器逃逸

| 监控项 | 工具 |
|--------|------|
| 异常进程 | Falco, Sysdig |
| 异常网络 | Falco, Cilium |
| 异常文件 | Falco, Auditd |
| 容器内系统调用 | Falco, Tracee |
| 容器间通信 | Cilium, Calico |
| 镜像漏洞 | Trivy, Grype, Snyk |

## IaC 安全

### 常见风险

| 风险 | 示例 |
|------|------|
| 硬编码密码 | password = "admin" |
| 公开存储 | acl = "public-read" |
| 开放安全组 | 0.0.0.0/0 |
| 未加密 | encrypted = false |
| 过度授权 | Action = "*" |
| 日志未启用 | 删除日志配置 |
| 版本锁定缺失 | 未指定版本 |

### 扫描工具

| 工具 | 支持格式 | 特点 |
|------|---------|------|
| **Checkov** | Terraform, CloudFormation, K8s | 支持最广 |
| **tfsec** | Terraform | 专注 Terraform |
| **Terrascan** | Terraform, K8s, Helm | 多格式 |
| **KICS** | 全格式 | 开源 |
| **Snyk IaC** | 全格式 | 商业 |
| **Semgrep** | 自定义 | 规则灵活 |
| **cfn-nag** | CloudFormation | AWS 专用 |

## 云原生安全架构

### 安全层次

```
┌─────────────────────────────────┐
│   应用安全 (WAF, RASP)          │
├─────────────────────────────────┤
│   运行时安全 (Falco, Tracee)    │
├─────────────────────────────────┤
│   编排安全 (Kyverno, OPA)       │
├─────────────────────────────────┤
│   网络安全 (Cilium, Calico)     │
├─────────────────────────────────┤
│   节点安全 (Seccomp, SELinux)   │
├─────────────────────────────────┤
│   供应链安全 (SBOM, Sigstore)   │
├─────────────────────────────────┤
│   镜像安全 (Trivy, Cosign)      │
└─────────────────────────────────┘
```

### 供应链安全

| 工具 | 用途 |
|------|------|
| **SBOM** | 软件物料清单 |
| **Syft** | SBOM 生成 |
| **Grype** | SBOM 漏洞扫描 |
| **Cosign** | 镜像签名 |
| **Sigstore** | 签名基础设施 |
| **SLSA** | 供应链安全框架 |
| **in-toto** | 供应链完整性 |
