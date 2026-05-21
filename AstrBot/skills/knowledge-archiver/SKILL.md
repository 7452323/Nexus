# Knowledge Archiver

## Description
Automatically extracts valuable information from conversations and archives it to long-term memory (MEMORY.md). Triggered by keywords like "remember", "save", "archive", or upon discovery of important technical decisions, configuration changes, or workflow optimizations.

## Instructions

### Trigger Conditions

Trigger when ANY of these conditions are met:

| Condition | Example |
|-----------|---------|
| User says "remember", "save this", "archive" | "Remember this command" |
| New API key or configuration discovered | "Found another API key" |
| Important technical decision made | "We'll store all sources as JSON from now on" |
| Workflow optimization discovered | "This script is 3x faster than the old one" |
| Server configuration changed | "Changed SearXNG port to 28080" |

### Archive Format

```
## [Date] [Category] [Topic]

- **Source**: xxx
- **Content**: xxx
- **Notes**: xxx
```

### Pre-archive Checklist

- [ ] Is the information already in MEMORY.md? (Search keywords to deduplicate)
- [ ] Does it contain sensitive information (API keys, passwords → do NOT archive)?
- [ ] Is the information accurate and reliable?

### Implementation Steps

1. **Detect trigger** from user input or discovered context
2. **Extract key information** — what, why, source, reliability
3. **Deduplicate** — search MEMORY.md for existing entries
4. **Check sensitivity** — skip if it contains passwords, private keys, personal data
5. **Format** according to the archive template
6. **Append to MEMORY.md** or relevant memory file
7. **Confirm** with a brief acknowledgment

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| content | string | Yes | Information to archive |
| category | string | No | Category tag (e.g., "Config", "Tool", "Decision") |
| source | string | No | Where this info came from |

## Examples

```
User: "Remember that the API endpoint is https://api.example.com/v2"
Agent: (Checks for duplicates, formats, archives) → "Saved: API endpoint configuration."
```

```
User: "Save this debugging approach for future reference"
Agent: (Extracts key technique, archives to MEMORY.md) → "Archived debugging technique."
```

## Notes
- Never archive passwords, API keys, or private credentials
- Deduplicate before archiving — check existing memory entries
- Tag entries by category for easier retrieval
- Keep entries concise but complete enough for future reference
- Archive format uses the same structure as MEMORY.md for consistency
