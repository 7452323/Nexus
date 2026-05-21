# Preflight Checker

## Description
Safety validation layer that checks tool call parameters before execution. Intercepts dangerous operations (file deletion, system commands, database destruction), warns about risky actions, and suggests safer alternatives.

## Instructions

### Checks for Shell Commands

| Pattern | Action | Alternative |
|---------|--------|-------------|
| `rm -rf /`, `rm -rf /*`, `rm -r /` | 🚫 Block | Use specific path, not root |
| `mkfs.`, `dd if=`, `chmod -R 000` | 🚫 Block | Confirm target device and path |
| `git push --force` | ⚠️ Warn | Use `git push --force-with-lease` |
| `git reset --hard HEAD~` | ⚠️ Warn | Backup or stash first |
| `DROP TABLE`, `DROP DATABASE` | ⚠️ Warn | Confirm table name first |
| `:(){ :|:& };:` (fork bomb) | 🚫 Block | No alternative |

### Checks for File Operations

| Path Pattern | Action |
|-------------|--------|
| `/etc/shadow`, `/etc/sudoers` | 🚫 Block |
| `/etc/ssh/` any file | 🚫 Block |
| Private key files in `~/.ssh/` | 🚫 Block |
| Config files in `~/.config/` | ⚠️ Require confirmation |

### Checks for URLs / Network Requests

| Pattern | Action |
|---------|--------|
| URL points to internal IP (127., 10., 192.168., 172.16-31.) | ⚠️ Warn |
| URL contains `ghp_`, `sk-`, `AIzaSy`, `token=` in plaintext | ⚠️ Warn credential leak |

### Execution Flow

```
Receive tool call → Parse tool name + parameters → Match against rules
  ├─ ✅ Pass → Execute normally
  ├─ ⚠️ Warn → Execute + print warning
  └─ 🚫 Block → Reject + explain reason + suggest alternative
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| command | string | For exec | Shell command to validate |
| path | string | For file ops | File path to validate |
| url | string | For network | URL to validate |
| strict_mode | boolean | No | Enable all blocks as errors (default: false) |

## Examples

```
User suggestion: "rm -rf /var/logs"
Agent: (Checks: pattern matches safe path) → "✅ Safe. Proceeding with deletion of /var/logs only."
```

```
User suggestion: "rm -rf /"
Agent: (Check: matches root deletion) → "🚫 Blocked. Use 'trash' or specify exact path like 'rm -rf /tmp/target' instead."
```

## Notes
- Never execute rm -rf on root or system directories without explicit, confirmed user intent
- Warn about any git destructive operations before execution
- Block fork bombs and system-destroying commands entirely
- Credential leak detection is best-effort — not a replacement for secure practices
- When uncertain about safety, ask for user confirmation
- File path checks check for containment in protected directories, not just equality
