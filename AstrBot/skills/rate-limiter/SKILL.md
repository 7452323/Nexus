# Rate Limiter

## Description
Controls request frequency to external APIs to prevent triggering rate limits. Implements exponential backoff, concurrent request limiting, and API-specific rate thresholds.

## Instructions

### API Rate Limits

| API | Per Minute | Per Day | Throttle Behavior |
|-----|-----------|---------|-------------------|
| Generic (Calls) | 120 | — | Wait 2 seconds |
| GitHub (Anonymous) | 10 | — | Wait 10s + exponential backoff |
| GitHub (Token) | 30 | 5000 | Wait 5s + exponential backoff |
| DeepSeek | 60 | 10000 | Wait 60s then retry |

### Exponential Backoff

```
1st trigger -> Wait 2 seconds -> retry
2nd trigger -> Wait 4 seconds -> retry
3rd trigger -> Wait 8 seconds -> retry
4th trigger -> Wait 16 seconds -> retry
5th trigger -> Wait 30 seconds -> notify user
```

### Concurrency Control

| Config Item | Default |
|-------------|---------|
| Max concurrent requests | 3 |
| Max queue length | 20 |
| Queue full behavior | Return "Queue full, please try later" |

### Implementation Steps

1. **Before each external API call:**
   - Check current request count for the target API
   - If near limit, calculate required delay
   - Apply exponential backoff if rate-limited
   - Track concurrency, queue if at max

2. **On rate limit hit:**
   - Calculate backoff delay
   - Wait and retry once
   - If still rate-limited on 5th attempt, notify user

3. **On successful request:**
   - Update rate counter
   - Reset backoff multiplier

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| api_name | string | Yes | Target API identifier (e.g., "github", "deepseek") |
| max_concurrent | number | No | Override max concurrent requests |
| rate_per_minute | number | No | Override per-minute rate limit |
| rate_per_day | number | No | Override per-day rate limit |

## Examples

```
Scenario: Making 50 GitHub API calls quickly
Action: Rate limiter throttles to 10/min for anonymous → queues remaining → processes with delays.
```

```
Scenario: DeepSeek API returns 429
Action: Calculate backoff → wait 60s → retry → if fails again, increase backoff → notify user at 5th failure.
```

## Notes
- Rate limits are per-API, not global
- Exponential backoff resets after a successful request
- Concurrency limit is global across all APIs
- Queue overflow returns an error rather than blocking indefinitely
- Adjust limits based on the specific API's documented rate limits
- For batch operations, insert delays between requests proactively
