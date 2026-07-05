# iOS 快捷指令签名生成器

## 触发条件

用户提到"快捷指令"、"shortcut"、"签名"、"iOS 自动化"、"制作快捷指令"时激活。

## 功能

生成可直接导入 iOS 快捷指令 App 的已签名 .shortcut 文件。

## 使用方法

```bash
# 基本生成
python3 scripts/shortcut_signer.py "快捷指令名" \
  '操作JSON数组' \
  [-o output.signed.shortcut] \
  [--color 0xFF00A0FF] \
  [--glyph 0xF0C2]
```

## 支持的操作

| 操作 | identifier | 参数 |
|------|------------|------|
| 要求输入 | is.workflow.actions.ask | WFAskActionPrompt |
| 打开URL | is.workflow.actions.openurl | WFInput |
| 设置剪贴板 | is.workflow.actions.setclipboard | WFText |
| 获取剪贴板 | is.workflow.actions.getclipboard | - |
| 显示通知 | is.workflow.actions.notification | WFNotificationActionTitle, WFNotificationActionBody |
| 文本 | is.workflow.actions.gettext | WFTextActionText |
| 注释 | is.workflow.actions.comment | WFCommentActionText |
| 获取位置 | is.workflow.actions.location | - |
| 获取当前天气 | is.workflow.actions.weather.currentconditions | - |
| 获取天气预报 | is.workflow.actions.weather.forecast | WFWeatherLocation |
| 条件判断 | is.workflow.actions.conditional | WFCondition, WFControlFlowMode |
| 重复 | is.workflow.actions.repeat.count | WFRepeatCount |
| HTTP请求 | is.workflow.actions.downloadurl | WFURL, WFHTTPMethod, WFHTTPHeaders, WFHTTPBody |
| 从输入获取 | is.workflow.actions.gettext | WFTextActionText |
| 显示提醒 | is.workflow.actions.showalert | WFAlertActionTitle, WFAlertActionMessage |

## 示例

### 天气通知
```json
[
  {"WFWorkflowActionIdentifier": "is.workflow.actions.comment", "WFWorkflowActionParameters": {"WFCommentActionText": "查询天气"}},
  {"WFWorkflowActionIdentifier": "is.workflow.actions.location", "WFWorkflowActionParameters": {}},
  {"WFWorkflowActionIdentifier": "is.workflow.actions.weather.currentconditions", "WFWorkflowActionParameters": {}}
]
```

### HTTP 请求 + 弹窗
```json
[
  {"WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl", "WFWorkflowActionParameters": {"WFURL": "https://api.example.com", "WFHTTPMethod": "GET"}},
  {"WFWorkflowActionIdentifier": "is.workflow.actions.showalert", "WFWorkflowActionParameters": {"WFAlertActionTitle": "结果", "WFAlertActionMessage": "$input"}}
]
```

## 输出

签名后的 .signed.shortcut 文件，存放于 /var/minis/attachments/ 目录下，生成 minis:// 链接供用户下载。

## 技术细节

- 签名服务：RoutineHub HubSign API
- 端点：https://hubsign.routinehub.services/sign
- 签名魔数：AEA1（4字节）
- 需要 Origin/Referer 头
