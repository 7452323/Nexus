# Notification Bridge — OpenClaw 通知桥梁技能

将 OpenClaw 运行结果推送到多个通知渠道。

## 支持的渠道

|渠道|所需配置|用途|
|---|---|---|
|微信（当前会话）|无需配置|默认通知渠道|
|Telegram Bot|TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID|重要告警推送|
|Bark（iOS）|BARK_SERVER + BARK_DEVICE_KEY|推送通知到 iPhone|

## 通知优先级

|级别|触发条件|推送渠道|
|---|---|---|
|P0 紧急|Key 余额不足、服务宕机、磁盘快满|微信 + Telegram|
|P1 重要|每日报告、新 Key 发现、定时任务完成|微信|
|P2 普通|任务进展、状态更新|仅微信|

## 通知格式

```
[OpenClaw] [级别] 标题

消息内容

时间: 2026-05-19 12:00
来源: 任务/会话名称
```

## 触发方式

- 自动: 满足 P0/P1 条件时自动推送
- 手动: 说"通知我 [内容]"、"发到 [渠道]"


---

