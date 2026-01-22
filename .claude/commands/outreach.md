---
name: outreach
description: Main command for email outreach and campaign operations
---

# /outreach Command

The primary entry point for email outreach operations.

## Usage

```
/outreach [action] [options]
```

## Actions

### `/outreach campaign`
Start an email campaign from Google Sheets.

**Workflow:**
1. Ask for Sheet ID (or use default from .env)
2. Ask for template
3. Preview recipients and template
4. Get approval
5. Execute with rate limiting

**Skill:** Routes to `outreach-manager`

### `/outreach templates`
List and manage email templates.

**Shows:**
- Available templates by category
- Template content preview
- Variable placeholders

**Skill:** Routes to `template-manager`

### `/outreach status`
Check campaign status and authentication.

**Shows:**
- Auth status
- Recent campaigns
- Daily send count

### `/outreach setup`
Run initial setup and authentication.

**Runs:**
```bash
cd "C:\Users\Anit\Downloads\10x-Outreach-Skill" && .venv\Scripts\python.exe scripts\auth_setup.py
```

## Examples

**Start a campaign:**
```
/outreach campaign
```

**List templates:**
```
/outreach templates
```

**Check status:**
```
/outreach status
```

## Related Commands

- `/inbox` - Read and search emails
- `/compose` - Write single emails
- `/reply` - Reply to emails
- `/summarize` - Summarize emails

## Notes

- All campaigns require explicit approval before sending
- Rate limiting is enforced (minimum 60s between emails)
- Use dry-run mode for testing
