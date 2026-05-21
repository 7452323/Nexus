# Memory Enhancer — OpenClaw 记忆增强技能

让 OpenClaw 在每次新会话启动时自动扫描记忆文件、用户提问时自动扩展搜索关键词、回复前自动召回相关记忆。解决"新会话不记得之前的事"这个核心痛点。

## 功能拆解

### 1. 记忆索引 — 会话启动时触发

每次新会话开始，自动执行：

```
步骤 1: 扫描 memory/*.md 中最近 7 天的文件
步骤 2: 提取最近项目（仓库名、命令、配置变更）
步骤 3: 扫描 MEMORY.md 提取长期记忆摘要
步骤 4: 将摘要注入会话上下文（约 200 字）
```

摘要内容示例：
```
📎 记忆摘要:
- 最近项目: 书源编写(七猫/xbookcn)、openclaw-patches 仓库
- 主人: 爸爸(微信)，服务器: racknerd (Debian 12)
- 常用: python3 / node / git / curl
- Key: DeepSeek 主力，余额约 ¥300
```

### 2. 查询扩展 — 用户提问时触发

用户说一句自然语言，自动扩展成多个搜索词同时搜索：

|用户说|扩展搜索|
|---|---|
|"发个文件"|`sendDocument`, `curl`, `telegram`, `file-delivery`|
|"配置/改配置"|`openclaw.json`, `config`, `gateway`, `provider`|
|"报错/错误"|`error`, `bug`, `fix`, `workaround`, `log`|
|"重启"|`gateway`, `restart`, `service`, `systemctl`|
|"删除"|`delete`, `backup`, `safety`, `trash`|
|"扫key/Key/token"|`key`, `api key`, `credential`, `auth`, `scan_keys`|
|"更新"|`update`, `upgrade`, `git pull`, `version`|

### 3. 对话召回 — 回复前触发

```
1. 从用户消息中提取实体（项目名、文件名、命令名）
2. 对每个实体执行 memory_search（阈值 ≥ 0.6）
3. 命中 ≥ 0.85 的直接引用
4. 命中 0.6-0.84 的附加"📎 相关记忆"提醒
```

## 检查清单

每步执行前确认：

- [ ] 会话启动时：memory/*.md 非空？MEMORY.md 可读？注入摘要≤200字
- [ ] 用户提问时：有匹配的扩展映射？执行多词搜索
- [ ] 回复前：memory_search 结果 ≥ 0.6？格式化引用块


---

