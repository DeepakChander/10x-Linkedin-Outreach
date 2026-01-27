---
name: integrations
description: Sync data with external services and manage import/export
---

# /integrations Command

Pull data from external services, sync contacts, and import/export across formats — all on-demand when you run Claude Code.

## Usage

```
/integrations [action]
```

### Actions

- `/integrations status` — Show all configured integrations and last sync time
- `/integrations sync <service>` — Pull latest data from a service
- `/integrations import <file> --format csv|json` — Import contacts/data from file
- `/integrations export <type> --format csv|json` — Export data (contacts, campaigns, tickets)
- `/integrations connect <service>` — Configure a new service connection
- `/integrations disconnect <service>` — Remove a service connection
- `/integrations log` — View recent sync/import/export activity

## Supported Services

| Service | What It Syncs | How |
|---------|--------------|-----|
| Google Sheets | Contacts, campaign recipients | Sheets API (pull on demand) |
| CSV/JSON files | Contacts, leads, any data | Local file import/export |
| Gmail | Inbox, sent mail, replies | Gmail API (pull on demand) |
| Exa AI | Discovery results, websets | Exa API (pull on demand) |
| CRM export | HubSpot/Salesforce CSV exports | File import |

## How It Works

Unlike webhooks (which need a server running 24/7), integrations work **pull-based**:

1. You run `/integrations sync gmail` in Claude Code
2. Script pulls new emails since last sync
3. Updates local data (contacts, interactions, replies)
4. Logs the sync event

Everything runs on-demand when you use Claude Code — no background server needed.

## Examples

```
/integrations status
/integrations sync gmail
/integrations import leads.csv --format csv
/integrations export contacts --format json
/integrations connect sheets --spreadsheet-id ABC123
/integrations log
```

## Implementation

```bash
python .claude/scripts/integration_manager.py status
python .claude/scripts/integration_manager.py sync gmail
python .claude/scripts/integration_manager.py import leads.csv --format csv
python .claude/scripts/integration_manager.py export contacts --format json
python .claude/scripts/integration_manager.py log
```

## Audit Trail

All sync and import/export events are logged to `output/integrations/sync_log.json`.

## Skill Reference

This command uses the `integration-manager` skill at `.claude/skills/integration-manager/SKILL.md`.
