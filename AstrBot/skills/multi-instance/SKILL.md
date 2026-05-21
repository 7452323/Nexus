# Multi Instance

## Description
Manages multiple independent AstrBot configuration instances on the same machine. Enables running separate environments for development, production, and testing with isolated configurations.

## Instructions

### Instance Directory Structure

```
instances/
├── default/    # Default instance (daily use)
├── dev/        # Development instance (test new features)
└── prod/       # Production instance (stable operation)
```

Each instance contains its own complete configuration files.

### Command Reference

| User says | Effect |
|-----------|--------|
| "switch instance dev" | Switch to development instance (restart required) |
| "create instance test" | Create new instance by copying default config |
| "delete instance test" | Delete test instance (requires confirmation) |
| "list instances" | Show all instances and their status |

### Checklist

Before switching:
- [ ] Target instance configuration exists
- [ ] Target port/working directory is not occupied
- [ ] No ongoing tasks that would be disrupted

When creating:
- [ ] Instance name doesn't already exist
- [ ] Port/working directory not used by other instances

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | string | Yes | "list", "switch", "create", "delete" |
| instance_name | string | For switch/create/delete | Name of the instance |
| source_instance | string | For create only | Instance to copy from (default: "default") |

## Examples

```
User: "list instances"
Agent: Shows all instances with their status → "default (running), dev (stopped), prod (running)"
```

```
User: "switch to dev instance"
Agent: Verify dev instance exists → check if port is free → suggest restart → "Ready to switch. Restart to apply."
```

## Notes
- Creating an instance copies the default instance's configuration
- Deleting requires explicit user confirmation with "yes"
- Instance changes typically require a service restart to take effect
- Ports and working directories must be unique per instance
- Each instance maintains its own memory and conversation history
