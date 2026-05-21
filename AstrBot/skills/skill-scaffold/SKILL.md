# Skill Scaffold

## Description
A skill scaffold generator that creates properly formatted SKILL.md files based on user requirements. Automatically structures the skill with description, instructions, parameters, examples, and notes sections.

## Instructions

### Template Structure

```markdown
# {Skill Name}

## Description
{Short description of what this skill does}

## Instructions
{Detailed step-by-step instructions for the agent to execute this skill}

## Parameters
{Optional parameter definitions}

## Examples
{Usage examples}

## Notes
{Safety notes, constraints, tips}
```

### Generation Process

When user says "write me a skill for X":

1. Ask user: "What does this skill do?" — Understand the core functionality
2. Ask user: "Trigger method — manual (keyword) or automatic (condition)?"
3. Ask user: "Input and output — what does it take, what does it produce?"
4. Generate SKILL.md using the template
5. Save to `skills/{skill-name}/SKILL.md`
6. Inform user of file location

### Quality Checklist

- [ ] Description clearly states purpose in 1-2 sentences
- [ ] Instructions are actionable steps the agent can follow
- [ ] Required parameters are documented with types
- [ ] Examples show realistic usage scenarios
- [ ] Notes cover safety, constraints, and edge cases
- [ ] No OpenClaw-specific API references (use standard shell/Python)
- [ ] SKILL.md uses the correct Anthropic Skills format

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| skill_name | string | Yes | Name of the skill to scaffold |
| skill_description | string | Yes | What the skill does |
| trigger_type | string | Yes | "manual" or "automatic" |
| input_description | string | No | What inputs the skill needs |
| output_description | string | No | What the skill produces |

## Examples

```
User: "Write me a skill for checking weather"
Agent: Asks about functionality, trigger, input/output → Generates SKILL.md → "Saved to skills/weather-checker/SKILL.md"
```

```
User: "I need a skill that monitors my server CPU"
Agent: Walks through scaffolding questions → "Let me generate this for you..."
```

## Notes
- Always ask clarifying questions before generating — a good scaffold depends on clear requirements
- Follow the standard Anthropic Skills format (SKILL.md)
- Avoid platform-specific APIs (like OpenClaw's kvStore, Env, etc.)
- Use standard shell commands and Python for executable parts
- Include a pre-generation checklist to ensure completeness
- Generated skills should be immediately usable without modification
