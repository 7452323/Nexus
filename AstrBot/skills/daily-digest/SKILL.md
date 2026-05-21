# Daily Digest

## Description
Generates and delivers a daily operational report. Includes API usage statistics, key inventory, server health metrics, and activity summary. Can be triggered manually or run automatically on a schedule.

## Instructions

### Report Content

```
📊 Daily Report - YYYY-MM-DD
━━━━━━━━━━━━━━━━━━━━━

💰 API Costs
  Primary Model: $0.30
  Secondary Model: $0.05
  Total: $0.35

🔑 Key Inventory
  Provider A: 6 valid (Balance $274.24)
  Provider B: 3 (Free)
  Provider C: 1 (Free)

🖥️ Server Health
  CPU: 45%
  Memory: 2.0/2.4 GB (83%)
  Disk: 20/39 GB (51%)
  Uptime: 15 days

📝 Yesterday's Activity
  Sessions: 12
  Tool Calls: 47
  Memory Updates: 3
━━━━━━━━━━━━━━━━━━━━━
```

### Configuration

| Config Item | Default | Description |
|-------------|---------|-------------|
| push_time | 07:30 | Auto-send time daily |
| include_costs | true | Include API cost statistics |
| include_health | true | Include server status |
| include_activity | true | Include yesterday's activity |

### Implementation Steps

1. **Collect API cost data** — Query API usage logs for yesterday
2. **Check key inventory** — Verify remaining valid API keys and balances
3. **Gather server metrics** — CPU, memory, disk, uptime
4. **Count activity** — Sessions, tool calls, memory update counts
5. **Format report** — Use the template above
6. **Deliver** — Send to configured notification channel

### Trigger Methods

- **Scheduled:** Runs automatically at configured push time
- **Manual:** User says "daily report", "today's report", "digest"

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| date | string | No | Specific date for report (default: today) |
| channel | string | No | Delivery channel (default: current chat) |

## Examples

```
User: "daily report"
Agent: Generates and displays the full daily digest with costs, health, and activity.
```

```
User: "how was yesterday's usage?"
Agent: Shows only the activity and cost sections of the daily report.
```

## Notes
- Manual trigger can be used at any time
- Cost data availability depends on provider API support
- Server health requires system-level access (ssh, /proc, df)
- Reports are generated fresh each time, not cached
- Summarize long reports if delivering to chat platforms
