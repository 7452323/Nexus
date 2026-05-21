# Session Isolator

## Description
Establishes privacy boundaries between different conversation channels. Ensures that private/direct messages are not exposed in group chats or other platforms. Filters memory searches by source channel to maintain context isolation.

## Instructions

### Channel Rules

#### Private Chat — Owner Conversations
```
Allowed:
  - Answer any question from the owner
  - Read and manipulate workspace files and configuration
  - Execute all management operations
  - Use API key-dependent skills

Prohibited:
  - Reveal owner information to other platforms
  - Leak other platform conversations to the current one
```

#### Group Chat / Public Channels
```
Allowed:
  - Answer questions about public projects
  - Share technical knowledge
  - Provide general help

Prohibited:
  - Expose owner name, address, contact info
  - Mention private conversation content
  - Execute sensitive operations (file deletion, config modification)
  - Use API key-dependent skills (unless owner explicitly allows in group)
```

### Context Cleanup

| Source | Cleanup Interval | Retention Limit |
|--------|-----------------|-----------------|
| Private chat | 6 hours | 10000 messages |
| Group chat | 6 hours | 5000 messages |
| Other platforms | 6 hours | 10000 messages |

### Memory Isolation

When performing memory searches, filter by source:
- Private chat session → memory_search returns only private chat matches
- Group chat session → memory_search returns only public-relevant matches

### Pre-Reply Checklist

Before replying cross-platform:
- [ ] Recipient is owner? → Can reveal any content
- [ ] Recipient is group? → Check for owner privacy in response
- [ ] Response references another channel's conversation? → Delete reference
- [ ] Involves sensitive operation? → Reject in group chat
- [ ] Requires API key skill? → Reject in group (unless owner authorized)

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| channel_type | string | Yes | "private" or "group" or "public" |
| action | string | Yes | User action to validate |
| referenced_source | string | No | Source of referenced content, if any |

## Examples

```
Scenario: User in group chat asks "What's my API key?"
Action: Session Isolator identifies group chat → rejects sensitive operation → "I cannot share API keys in this channel."
```

```
Scenario: Owner in private chat asks "Deploy the new version"
Action: Session Isolator identifies private chat → allows all operations → executes deploy.
```

## Notes
- Default channel type is "private" when unsure
- Cross-channel references are automatically stripped
- Memory search results are filtered by current channel type
- Context cleanup limits prevent memory leaks across sessions
- Rules apply symmetrically — no channel leaks to another
- Group chat sensitivity is conservative: block when in doubt
