# Workflow Command

Routes to `workflow-engine` skill for creating and running multi-platform outreach workflows.

## Usage

```
/workflow [action] [options]
```

## Actions

- `/workflow` - Show active workflows
- `/workflow run` - **Run workflow from Visual Canvas** (reads from queue)
- `/workflow create` - Create a new workflow
- `/workflow load <file>` - Load workflow from YAML
- `/workflow list` - List all workflows
- `/workflow status <id>` - Show workflow status
- `/workflow pause <id>` - Pause a running workflow
- `/workflow resume <id>` - Resume a paused workflow
- `/workflow cancel <id>` - Cancel a workflow

## Canvas Integration

When you design a workflow in the Visual Canvas (http://localhost:3006) and click **Run**:
1. The workflow is saved to `output/workflow-queue/latest.json`
2. Come here and say `/workflow run` to execute it
3. The workflow engine reads the nodes and connections
4. Each skill node is executed in order with proper rate limiting

## Examples

```
/workflow                           # List active workflows
/workflow run                       # Run workflow from Visual Canvas
/workflow create                    # Start workflow creation wizard
/workflow load ai_founders.yaml     # Load from YAML definition
/workflow status abc123             # Check workflow progress
/workflow pause abc123              # Pause running workflow
```

## Workflow Phases

Workflows consist of phases that execute in sequence:

1. **Warm-up** - View profiles, establish presence
2. **Engage** - Like posts, comment, show interest
3. **Connect** - Send connection requests, follow
4. **Outreach** - Send messages, DMs, emails

## Skill Reference

This command uses the `workflow-engine` skill located at `.claude/skills/workflow-engine/SKILL.md`.

Integrates with:
- `discovery-engine` - Find targets
- `team-manager` - Get credentials
- `rate_limiter.py` - Intelligent delays
- Browser-Use MCP - Execute platform actions
