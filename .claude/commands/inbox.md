---
name: inbox
description: Read, search, and manage inbox emails
---

# /inbox Command

Access and manage your Gmail inbox.

## Usage

```
/inbox [action] [options]
```

## Actions

### `/inbox` or `/inbox list`
Show recent emails from inbox.

**Default:** Shows 10 most recent emails

**Skill:** Routes to `inbox-reader`

### `/inbox unread`
Show only unread emails.

```bash
cd "C:\Users\Anit\Downloads\10x-Outreach-Skill" && .venv\Scripts\python.exe scripts\inbox_reader.py --unread
```

### `/inbox search [query]`
Search emails using Gmail query syntax.

**Examples:**
- `/inbox search from:john@example.com`
- `/inbox search subject:important`
- `/inbox search is:unread after:2024/01/01`

### `/inbox read [message_id]`
Read a specific email by ID.

```bash
cd "C:\Users\Anit\Downloads\10x-Outreach-Skill" && .venv\Scripts\python.exe scripts\inbox_reader.py --read MESSAGE_ID
```

### `/inbox stats`
Show inbox statistics.

**Shows:**
- Total messages
- Unread count
- Today's emails

```bash
cd "C:\Users\Anit\Downloads\10x-Outreach-Skill" && .venv\Scripts\python.exe scripts\inbox_reader.py --stats
```

### `/inbox labels`
List all Gmail labels/folders.

```bash
cd "C:\Users\Anit\Downloads\10x-Outreach-Skill" && .venv\Scripts\python.exe scripts\inbox_reader.py --labels
```

## Search Query Syntax

| Query | Description |
|-------|-------------|
| `from:email` | From sender |
| `to:email` | To recipient |
| `subject:text` | Subject contains |
| `is:unread` | Unread only |
| `is:starred` | Starred only |
| `has:attachment` | Has attachments |
| `after:YYYY/MM/DD` | After date |
| `before:YYYY/MM/DD` | Before date |
| `newer_than:7d` | Last N days |
| `label:name` | Specific label |

## Examples

**Show recent emails:**
```
/inbox
```

**Show unread:**
```
/inbox unread
```

**Search from specific person:**
```
/inbox search from:boss@company.com
```

**Get stats:**
```
/inbox stats
```

## Related Commands

- `/summarize` - Summarize emails
- `/reply` - Reply to emails
- `/compose` - Write new emails
- `/outreach` - Bulk campaigns
