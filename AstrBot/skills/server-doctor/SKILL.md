# Server Doctor

## Description
One-click server diagnostic tool. Automatically checks system resources, service health, and network connectivity when the server appears to be having issues. Provides actionable repair suggestions and can auto-fix common problems.

## Instructions

### Diagnostic Flow

```
Step 1: Check System Resources
  CPU > 80% -> Inspect top 10 processes
  Memory > 85% -> Inspect top 5 memory-consuming processes
  Disk > 85% -> Find files larger than 1GB

Step 2: Check Agent Service
  Process running? -> If not, attempt to start
  Port listening? -> If not, check logs

Step 3: Check Critical Services
  Docker -> Status + container list
  Web servers -> Reachability
  Other configured services -> Status

Step 4: Check Network
  External -> ping 8.8.8.8
  DNS -> resolve github.com
  Primary API provider -> Test connectivity
```

### Auto-Fix Actions

| Problem | Auto-Fix Method |
|---------|-----------------|
| Process not running | Attempt to start the service |
| Disk low | Clean logs, cache, temp files |
| Docker not running | `systemctl start docker` |

### Diagnostic Report Format

```
CPU: 25% ✅
Memory: 2.0/2.4 GB (83%) ⚠️ Monitor
Disk: 20/39 GB (51%) ✅
Uptime: 15 days
Agent Service: Running ✅
Docker: Running ✅ (3 containers)
Network: Reachable ✅
```

### Implementation Steps

1. Execute commands to gather system metrics (top, free, df)
2. Check if agent service is running (ps aux / systemctl)
3. Check key services (docker ps, curl localhost:port)
4. Test network connectivity (ping, dig, curl)
5. Generate formatted report
6. If any issue found, propose fix
7. For auto-fixable issues, ask user permission then execute fix

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| quick_mode | boolean | No | Skip detailed analysis, only show summary (default: false) |
| auto_fix | boolean | No | Attempt auto-fix without asking (default: false, ask first) |
| services | array | No | Custom list of services to check |

## Examples

```
User: "diagnose the server"
Agent: Runs all 4 diagnostic steps → generates report → "CPU: 25% ✅ | Memory: 83% ⚠️ | Disk: 51% ✅ | Agent: Running ✅ | Docker: 3 containers ✅"
```

```
User: "server is slow"
Agent: Checks CPU/memory → finds memory > 85% → lists top processes → "Memory usage high. Top consumer: node (1.2GB). Suggest restarting."
```

## Notes
- Quick mode only shows summary without detailed process lists
- Auto-fix requires explicit user opt-in or confirmation per action
- Network checks use standard tools (ping, curl) available on most Linux systems
- For non-standard services, user must configure custom service checks
- Report uses ✅ for healthy, ⚠️ for warnings, ❌ for critical
- Always run disk clean suggestions past the user first
