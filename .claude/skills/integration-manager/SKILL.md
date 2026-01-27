---
name: integration-manager
description: |
  Pull-based data sync, import/export, and external service integration.
  Use this skill when the user wants to sync data from external services,
  import/export contacts or campaign data, or check integration status.
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
---

# Integration Manager Skill

Manages on-demand data sync with external services and file import/export. Everything is pull-based — no background server needed.

## When to Use

- User wants to import contacts from CSV, JSON, or Google Sheets
- User wants to export data (contacts, campaigns, tickets) to a file
- User wants to sync latest data from Gmail, Exa, or other services
- User wants to check when data was last synced
- User asks about connecting to external tools

## How It Works

This skill uses **pull-based sync** instead of webhooks:

1. User triggers a sync (e.g., `/integrations sync gmail`)
2. Script connects to the service API and pulls new data since last sync
3. Data is merged into local storage (output/ directory)
4. Sync timestamp and event count are logged

No persistent server. No webhook endpoints. Just on-demand data pulling.

## Core Operations

### Check Status
```bash
python .claude/scripts/integration_manager.py status
```

### Sync from Service
```bash
python .claude/scripts/integration_manager.py sync gmail
python .claude/scripts/integration_manager.py sync sheets --id SPREADSHEET_ID
python .claude/scripts/integration_manager.py sync exa
```

### Import/Export
```bash
python .claude/scripts/integration_manager.py import leads.csv --format csv
python .claude/scripts/integration_manager.py export contacts --format json --output contacts.json
python .claude/scripts/integration_manager.py export campaigns --format csv
python .claude/scripts/integration_manager.py export tickets --format json
```

### View Sync Log
```bash
python .claude/scripts/integration_manager.py log
python .claude/scripts/integration_manager.py log --days 7
```

## Data Flow

```
External Service (Gmail, Sheets, Exa, CSV)
    ↓ (pull on demand)
integration_manager.py
    ↓ (merge into local storage)
output/accounts/contacts.json    ← contacts
output/campaigns/                ← campaign data
output/tickets/                  ← support tickets
output/integrations/sync_log.json ← audit trail
```

## Supported Export Types

| Type | Source | Formats |
|------|--------|---------|
| contacts | account_manager | CSV, JSON |
| campaigns | outreach logs | CSV, JSON |
| tickets | ticket_manager | CSV, JSON |
| discovery | discovery results | CSV, JSON |
| reviews | QA reviews | JSON |

## Audit Trail

All sync and import/export events logged to `output/integrations/sync_log.json` with timestamps.
