# Preflight Checker — OpenClaw 工具预检技能

在每次工具调用前检查参数，拦截危险操作，保护系统和数据安全。

## 检查规则

### exec 命令

|触发模式|行为|替代方案|
|---|---|---|
|`rm -rf /`、`rm -rf /*`、`rm -r /`|⛔ 阻止|`trash` 或指定具体路径|
|`mkfs.`、`dd if=`、`chmod -R 000`|⛔ 阻止|确认目标设备和路径|
|`git push --force`|⚠️ 警告|改用 `git push --force-with-lease`|
|`git reset --hard HEAD~`|⚠️ 警告|先 `git stash` 或备份|
|`DROP TABLE`、`DROP DATABASE`|⚠️ 警告|先确认表名|
|`:(){ :|:& };:` fork炸弹|⛔ 阻止|无|

### write / edit 文件路径

|路径模式|行为|
|---|---|
|`/etc/shadow`、`/etc/sudoers`|⛔ 阻止|
|`/etc/ssh/` 下任何文件|⛔ 阻止|
|`/root/.ssh/` 下私钥文件|⛔ 阻止|
|`~/.openclaw/openclaw.json`|⚠️ 需确认|

### URL / 网络请求

|模式|行为|
|---|---|
|URL 指向内网 IP（127.、10.、192.168.、172.16-31.）|⚠️ 警告|
|URL 中明文包含 `ghp_`、`sk-`、`AIzaSy`、`token=`|⚠️ 警告凭据泄露风险|

## 执行流程

```
收到工具调用 → 解析工具名+参数 → 匹配规则表
  ├─ ⛔ 阻止 → 拒绝 + 说明原因 + 推荐替代方案
  ├─ ⚠️ 警告 → 执行 + 打印警告
  └─ ✅ 通过 → 正常执行
```

## 适用场景

- 防止误删除系统关键文件
- 保护 API Key 不被泄露到URL或commit中
- 避免数据库误操作


---

