# Provider Failover

## Description
Automatically detects when the primary API provider becomes unavailable and seamlessly fails over to backup services. Monitors provider health and restores primary when it recovers. Provides transparent failover with notification.

## Instructions

### Failure Detection

| Anomaly Type | Detection Condition |
|-------------|---------------------|
| HTTP 5xx | Status code >= 500 |
| Timeout | No response within 15 seconds |
| Insufficient balance | total_balance < 0.01 |
| Rate limited (429) | Status code = 429 |
| Auth failure (401) | Status code = 401 |

### Failover Flow

```
Request primary provider
  -> Success -> Return normally
  -> Failure -> Wait 5 seconds -> Retry once
       -> Success -> Return normally
       -> Fail again -> Switch to backup provider
            -> Success -> Mark as active for continued use
            -> All failed -> Notify user all providers unavailable
```

### Provider Priority

1. Primary provider (check balance, highest first)
2. Secondary provider
3. Tertiary provider (free tier, only when others are fully down)

### Recovery Check

- Every 30 minutes, automatically check if primary provider has recovered
- When recovered, switch back to primary
- Failover events are logged to `logs/provider-failover.log`

### Implementation Steps

1. **Configure providers** — list of providers with endpoints, auth, and priority
2. **On each API call** — attempt primary, detect failure, fallback
3. **On failover** — log event, notify user if persistent
4. **Health check** — periodic background check on primary
5. **Restore** — when primary recovers, switch back and notify

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| providers | array | Yes | List of provider configurations with endpoint, auth, priority |
| retry_count | number | No | Retries before failover (default: 1) |
| retry_delay | number | No | Delay between retries in ms (default: 5000) |
| health_check_interval | number | No | Primary health check interval in ms (default: 1800000) |
| timeout_ms | number | No | Request timeout in ms (default: 15000) |

## Examples

```
Scenario: Primary provider returns 503
Action: Wait 5s → retry → still fails → switch to backup → mark backup active → notify user.
```

```
Scenario: Provider recovery check finds primary healthy
Action: Switch back to primary → notify user → log recovery event.
```

## Notes
- Maintain a simple priority-ordered list of providers
- Check account balance before routing to a provider
- Log all failover events with timestamps and reasons
- Notify user on first failover, not on every retry
- Retry once with delay before failing over (transient errors are common)
- Health check interval: 30 minutes for primary recovery monitoring
