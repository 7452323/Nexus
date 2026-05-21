# Memory Backup Auto

## Description
Automatically creates timestamped backups of memory files, configuration, and critical workspace data. Retains multiple version snapshots with configurable retention policies. Supports rollback to restore from any saved snapshot.

## Instructions

### Backup Strategy

| Snapshot Type | Retention Count | Trigger |
|---------------|-----------------|---------|
| Daily snapshot | Last 7 days | First conversation of each day |
| Weekly snapshot | Last 4 weeks | Every Monday first session |

### Backup Content

| File/Directory | Description |
|---------------|-------------|
| `memory/*.md` | Daily memory files |
| `MEMORY.md` | Long-term memory |
| `USER.md`, `SOUL.md` | Configuration files |
| other critical workspace files | As configured |

### Rollback Process

When user says "rollback memory" or "restore backup":

1. List available snapshots (sorted by date descending, show date and size)
2. User selects rollback point (e.g., "rollback to May 18")
3. Backup current state first (in case rollback needs to be undone)
4. Extract selected snapshot to workspace
5. Report rollback results

### Implementation Steps for Backup

1. Check that `memory/` directory exists and is readable
2. Verify output directory has sufficient space (≥100MB)
3. Create timestamped archive using tar/gzip
4. Verify archive integrity (test with `tar -tzf`)
5. Check file count matches expectations
6. Clean up old snapshots beyond retention period

### Implementation Steps for Rollback

1. List available snapshots
2. Ask user to specify which version
3. Create a pre-rollback backup for safety
4. Extract selected snapshot
5. Confirm completion

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | string | Yes | "backup" or "restore" or "list" |
| snapshot_tag | string | For restore | Date tag to restore (e.g., "2026-05-18") |
| retention_days | number | No | Override daily retention (default: 7) |
| retention_weeks | number | No | Override weekly retention (default: 4) |

## Examples

```
User: "backup my memory"
Agent: Creates timestamped backup → verifies integrity → reports result.
```

```
User: "rollback memory to yesterday"
Agent: Lists snapshots → confirms selection → creates pre-rollback safety backup → extracts snapshot.
```

## Notes
- Always create a pre-rollback backup before restoring
- Snapshots are stored in a dedicated backup directory (e.g., `backups/`)
- Verify archive integrity after creation
- Clean up old snapshots automatically after each backup
- Works with tar/gzip for cross-platform compatibility
