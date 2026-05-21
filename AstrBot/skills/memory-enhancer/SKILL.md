# Memory Enhancer

## Description
Enhances the agent's memory system by automatically scanning memory files at session start, expanding user queries with related search terms, and recalling relevant past context before responding. Solves the "new session doesn't remember previous context" problem.

## Instructions

### 1. Memory Indexing — Session Start Trigger

At the start of every new session:

```
Step 1: Scan memory/*.md for last 7 days
Step 2: Extract recent projects (repo names, commands, config changes)
Step 3: Scan MEMORY.md for long-term memory summary
Step 4: Inject summary into session context (~200 words)
```

Summary example:
```
📎 Memory Summary:
- Recent projects: [project names]
- Key users: [users]
- Common tools: python3 / node / git / curl
- Active configs: [API providers and balances]
```

### 2. Query Expansion — User Question Trigger

When user asks a question, expand into multiple search terms:

| User says | Expanded search |
|-----------|-----------------|
| "send a file" | `sendDocument`, `curl`, `telegram`, `file-delivery` |
| "config / change config" | `config.json`, `configuration`, `settings` |
| "error / bug" | `error`, `bug`, `fix`, `workaround`, `log` |
| "restart" | `restart`, `service`, `systemctl` |
| "delete" | `delete`, `backup`, `safety`, `trash` |
| "key / token / API key" | `key`, `api key`, `credential`, `auth` |
| "update / upgrade" | `update`, `upgrade`, `git pull`, `version` |

### 3. Recall Before Reply — Pre-response Trigger

```
1. Extract entities from user message (project names, file names, command names)
2. Perform memory_search for each entity (threshold ≥ 0.6)
3. Hits ≥ 0.85: Directly reference in response
4. Hits 0.6-0.84: Append "📎 Related memory:" reminder block
```

### Constraints

- Memory summary injection: ≤200 characters
- Search threshold minimum: 0.6
- Format recalled memories as quoted blocks

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| search_threshold | number | No | Memory search relevance threshold (0.0-1.0, default: 0.6) |
| max_summary_length | number | No | Max chars for context injection summary (default: 200) |
| recent_days | number | No | Days of memory to scan at session start (default: 7) |

## Examples

```
User: (New session) "What was that project we worked on last week?"
Agent: (Scans memory → finds project) "We worked on the Nexus repository converting OpenClaw skills to AstrBot format."
```

```
User: "Error when running that script"
Agent: (Expands: error, bug, fix, log) → (Finds memory about the script + fix) → "I see you had an issue with script X. The fix was Y."
```

## Notes
- Run memory indexing at the START of each new session
- Query expansion helps find relevant memories even with vague queries
- Pre-response recall prevents repeating past mistakes
- Do not inject memory summary into context every message — only at session start
- Respect memory isolation rules for multi-channel contexts
