# OpenClaw 验收提示词模板（codex-console 版）

```text
请你直接对当前部署好的 openClaw 做一次真实验收：

1. 和 openClaw 进行一次真实对话，不要模拟。
2. 验证 openClaw 当前是否成功使用 CLIProxyAPI 作为模型上游。
3. 验证 Telegram Bot 是否在线。
4. 验证当前 CLIProxyAPI 库存是否由 codex-console 链路持续供给。
5. 如果发现库存为空、模型不可用、RPC probe 异常、Telegram 未连接，请直接修复。
6. 最后告诉我：
   - openClaw 的实际回复内容
   - 当前可用模型
   - 当前 CLIProxyAPI 库存
   - 当前是否可投入使用
```
