# Usage Analytics

## Description
Collects and analyzes agent usage data to understand operational patterns. Tracks session statistics, tool call frequency, API costs, and activity trends. Generates reports on demand.

## Instructions

### Statistics Collected

```
Session Stats:
  Daily session count         → Usage activity level
  Average session duration    → Task complexity indicator
  Peak activity hours         → Optimize scheduled tasks
  Session source distribution → Channel/platform breakdown

Tool Call Stats:
  Daily tool call count       → Workload measurement
  Top 10 most used tools      → High-frequency functions
  Tool call success rate      → Anomaly and error detection
  Average response time       → Performance baseline

Cost Analysis:
  Daily API costs             → Cost control
  Model usage distribution    → Model selection optimization
  Estimated monthly cost      → Budget planning
  7-day cost trend            → Anomaly detection
```

### Query Commands

| User says | Result |
|-----------|--------|
| "usage stats" | Show today's statistics |
| "this month's costs" | Show API cost summary for this month |
| "most used tools" | Show tool call frequency ranking |
| "peak hours" | Show session distribution by hour |
| "7 day trend" | Show last 7 days cost trend |
| "weekly report" | Generate complete weekly analytics |

### Implementation Steps

1. **Session tracking** — Count sessions per day, track source and duration
2. **Tool monitoring** — Log each tool call with name, duration, success/failure
3. **Cost logging** — Record API provider costs per request (when available)
4. **Report generation** — Aggregate data, format for delivery
5. **Storage** — Save analytics to `logs/analytics/` directory, one file per day

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| report_type | string | Yes | "daily", "weekly", "monthly", "cost", "tools", "sessions" |
| date_range | string | No | Date range (e.g., "7d", "30d", "2026-05-01..2026-05-21") |

## Examples

```
User: "usage stats"
Agent: Shows today's stats → "Today: 12 sessions, 47 tool calls (92% success rate), $0.35 API cost"
```

```
User: "7 day cost trend"
Agent: Aggregates last 7 days → "Mon: $0.30, Tue: $0.45, Wed: $0.22, Thu: $0.35, Fri: $0.50, Sat: $0.15, Sun: $0.28"
```

## Notes
- Analytics data is stored locally in `logs/analytics/` directory
- Cost data availability depends on API provider's response
- Session tracking requires minimal overhead per interaction
- Data is not sent to any external analytics service
- Old analytics files should be rotated (keep last 90 days)
- Tool call success rate helps identify frequently failing operations
- Peak hour analysis helps schedule resource-intensive tasks
