# Notification Bridge

## Description
Pushes agent operation results and alerts to multiple notification channels. Supports delivering messages to the current conversation, webhook endpoints, and other configurable channels. Handles priority-based routing.

## Instructions

### Supported Channels

| Channel | Configuration Needed | Use Case |
|---------|---------------------|----------|
| Current chat | None needed | Default notification channel |
| Webhook URL | Webhook endpoint URL | External service integration |
| Email (SMTP) | SMTP server config | Important alerts |

### Notification Priority Levels

| Level | Trigger Condition | Channels |
|-------|------------------|----------|
| P0 Critical | Service down, resource critical | Current chat + webhook |
| P1 Important | Daily report, task completion | Current chat |
| P2 Normal | Task progress, status updates | Current chat only |

### Notification Format

```
[Bot] [Level] Title

Message content

Time: YYYY-MM-DD HH:MM
Source: Task/Session name
```

### Implementation Steps

1. Detect notification trigger (P0/P1 conditions, or manual)
2. Format message according to template
3. Deliver to primary channel (current chat)
4. If P0, also deliver to secondary channels (webhook)
5. Log delivery status

### Trigger Methods

- **Auto:** P0/P1 conditions met automatically
- **Manual:** User says "notify me [content]", "send to [channel]"

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | Notification title |
| message | string | Yes | Notification content |
| level | string | Yes | "P0", "P1", or "P2" |
| channel | string | No | Override delivery channel |
| source | string | No | Source identifier (task/session name) |

## Examples

```
User: "notify me when the task completes"
Agent: Sets up monitoring → when task done, sends notification with result.
```

```
User (after alert): "send to webhook"
Agent: Resends last notification to configured webhook endpoint.
```

## Notes
- Current chat is always the default notification channel
- P0 alerts are delivered to all configured channels
- Respect user's quiet hours — avoid P2 notifications at night
- Webhook delivery uses HTTP POST with JSON payload
- Failed delivery to secondary channels should be logged but not retried
- Does not store or manage credentials — use environment variables for tokens
