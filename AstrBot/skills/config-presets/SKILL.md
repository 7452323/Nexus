# Config Presets

## Description
Manages configuration profile switching for the AstrBot agent. Allows switching between different performance modes (high-performance, balanced, power-saving, development) with a single command. Optimizes resource usage based on the current task type.

## Instructions

### Available Presets

#### High-Performance Mode
```
Use: Code writing, deep analysis, large project refactoring
Model: Best available reasoning model
Concurrency: 4
Timeout: 120 seconds
```

#### Balanced Mode (Default)
```
Use: Daily conversation, normal tasks
Model: Fast default model
Concurrency: 2
Timeout: 60 seconds
```

#### Power-Saving Mode
```
Use: Simple chat, quick lookups
Model: Fastest response model
Concurrency: 1
Timeout: 30 seconds
```

#### Development Mode
```
Use: Debugging scripts, testing new features
Model: Fast default model
Log Level: DEBUG
```

### Switching Commands

| User says | Effect |
|-----------|--------|
| "high performance mode" | Switch to high-performance preset |
| "power saving mode" | Switch to power-saving |
| "balanced mode" / "default" | Return to default |
| "development mode" | Development mode (more logging) |

### Implementation Steps

1. When user requests a mode switch, acknowledge the request
2. Adjust conversation parameters:
   - High-performance: Use slower, more powerful model for reasoning-heavy tasks
   - Power-saving: Be concise, skip analysis, prefer cached/quick answers
   - Balanced: Normal operation
   - Development: Enable verbose logging, step-by-step debugging
3. Confirm the mode switch is complete

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| mode | string | One of: "high-performance", "balanced", "power-saving", "development" |

## Examples

```
User: "high performance mode"
Agent: "Switched to High-Performance Mode. Using best model for reasoning. Ready for complex analysis tasks."
```

```
User: "power saving mode"
Agent: "Switched to Power-Saving Mode. Responses will be concise and prioritized for speed."
```

## Notes
- Default mode is "balanced" for most interactions
- High-performance mode may consume more API credits
- Power-saving mode limits analysis depth but responds faster
- Mode persists for the current session unless changed
