# Team Command

Routes to `team-manager` skill for managing team members and credentials.

## Usage

```
/team [action] [options]
```

## Actions

- `/team` - Show team status overview
- `/team add` - Add a new team member
- `/team list` - List all team members
- `/team setup <name>` - Configure platform credentials for a member
- `/team status` - Show authentication status for all platforms
- `/team remove <name>` - Remove a team member

## Examples

```
/team                      # Show team overview
/team add                  # Add new member (will ask for details)
/team setup John           # Configure John's platform accounts
/team status               # Show who is authenticated where
```

## Skill Reference

This command uses the `team-manager` skill located at `.claude/skills/team-manager/SKILL.md`.
