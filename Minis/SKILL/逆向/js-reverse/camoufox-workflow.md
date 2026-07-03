---
name: camoufox-workflow
description: JS逆向工程工作流技能。Node.js/Python接口自动化与签名还原，camoufox-reverse MCP工具索引，6阶段工作流（任务理解→侦察→源码分析→动态验证→算法还原→验证交付），JSVMP双路径分析。
author: 7452323 (converted from Private Gist)
category: reverse-engineering
tags:
  - js-reverse
  - camoufox
  - signature
  - jsvmp
---

# Camoufox Workflow - JS逆向工作流

## 硬约束 Checklist

启动技能后必须完成以下3项检查才能开始分析：

### CHECK-1: MCP 版本检查 + 环境自检
调用 `check_environment()`，确认 esprima、playwright、browser 状态。

### CHECK-2: 经验库速查
根据目标域名和特征关键词查找已有案例：
- tiktok.com / X-Bogus / X-Gnarly → jsvmp-dual-sign 方案
- douyin.com / a_bogus → jsdom 环境伪装
- nmpa.gov.cn / RS 412 / sdenv → sdenv 纯 Node.js
- obfuscator.io → 通用四板斧

### CHECK-3: 确认工作流阶段
选择当前所处阶段

## 6阶段工作流

### Phase 1: 任务理解
- 分析目标行为
- 确认抓包范围
- 输出：任务分析文档

### Phase 2: 侦察
- 断点定位加密点
- 调用栈回溯
- Hook 关键函数

### Phase 3: 源码分析
- 混淆识别
- AST 解混淆
- 算法逻辑提取

### Phase 4: 动态验证
- 补环境运行
- 参数输出比对
- 边界测试

### Phase 5: 算法还原
- Python/Node 复现
- 输入输出一致性验证

### Phase 6: 验证交付
- 多轮测试
- 文档产出

## JSVMP 双路径分析

### 路径A: 四板斧（轻量，优先）
1. 数组解混淆
2. 常量折叠
3. 死代码删除
4. 控制流平坦化还原

### 路径B: 环境仿真（重量，路径A无效时）
- jsdom 环境伪装（喂入-截出）
- Firefox + playwright 真实浏览器
- sdenv 纯 Node.js
