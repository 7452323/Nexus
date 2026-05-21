# Context Optimizer

## Description
Automatically optimizes conversation context in long sessions. Preserves critical information while compressing or removing low-priority content. Prevents context window overflow and maintains quality in extended interactions.

## Instructions

### Content Priority Levels

| Level | Content Type | Strategy |
|-------|-------------|----------|
| P0 Must Keep | Core instructions, current tasks, user configuration | No compression |
| P1 Try to Keep | Completed subtask results, technical decisions, preferences | Summarize to 1-2 sentences |
| P2 Can Compress | Debug logs, intermediate tool results, completed old tasks | Compress or delete |
| P3 Can Delete | Confirmations ("OK", "got it"), repeated prompt text | Delete directly |

### Trigger Conditions

| Condition | Threshold |
|-----------|-----------|
| Context token usage | Exceeds 70% of maximum limit |
| Session duration | Exceeds 30 minutes |
| Manual trigger | User says "compress context" |

### Compression Steps

1. Count tokens for each level (P0-P3)
2. Delete all P3 content
3. Compress P2 content to single sentence summary
4. Merge duplicate P1 content
5. Keep P0 content unchanged
6. Output compression report: "Released X tokens (Y → Z)"

### Compression Report Example

```
Before compression: 45000 tokens
After compression: 28000 tokens (released 37%)
P0 Instructions: kept | P1 Summary: kept | P2 Logs: compressed | P3 Confirmations: deleted
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| max_context_tokens | number | Maximum context window size (default: 100000) |
| compression_threshold | number | Percentage threshold to trigger auto-compression (default: 70) |

## Examples

```
User: "compress context"
Agent: "Compression report:
- Before: 45000 tokens
- After: 28000 tokens (released 37%)
- P0 Instructions: kept | P1 Summary: kept | P2 Logs: compressed | P3 Confirmations: deleted"
```

## Notes
- P0 content is never compressed under any circumstances
- User can manually trigger compression at any time
- When auto-triggered, ask for confirmation before compressing
- Compression preserves the semantic meaning of compressed content
- Useful for long-running coding sessions or extended analysis tasks
