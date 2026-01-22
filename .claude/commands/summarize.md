---
name: summarize
description: Summarize and digest emails
---

# /summarize Command

Generate summaries and digests of your emails.

## Usage

```
/summarize [action] [options]
```

## Actions

### `/summarize` or `/summarize recent`
Summarize recent emails.

**Default:** Summarizes 10 most recent emails

```bash
cd "C:\Users\Anit\Downloads\10x-Outreach-Skill" && .venv\Scripts\python.exe scripts\email_summarizer.py --summarize 10
```

**Skill:** Routes to `email-summarizer`

### `/summarize unread`
Summarize only unread emails.

```bash
cd "C:\Users\Anit\Downloads\10x-Outreach-Skill" && .venv\Scripts\python.exe scripts\email_summarizer.py --summarize 20 --unread
```

### `/summarize today`
Generate today's email digest.

```bash
cd "C:\Users\Anit\Downloads\10x-Outreach-Skill" && .venv\Scripts\python.exe scripts\email_summarizer.py --digest today
```

### `/summarize week`
Generate weekly digest.

```bash
cd "C:\Users\Anit\Downloads\10x-Outreach-Skill" && .venv\Scripts\python.exe scripts\email_summarizer.py --digest week
```

### `/summarize search [query]`
Summarize emails matching a search.

```bash
cd "C:\Users\Anit\Downloads\10x-Outreach-Skill" && .venv\Scripts\python.exe scripts\email_summarizer.py --search "from:important@company.com"
```

## Digest Periods

| Period | Command |
|--------|---------|
| Today | `/summarize today` |
| Yesterday | `/summarize yesterday` |
| This week | `/summarize week` |
| This month | `/summarize month` |

## Output Format

```markdown
# Email Digest: Today

Total Emails: 15

## 🚨 Urgent
- **Critical Update** from Boss

## ⚠️ May Need Response
- **Question about proposal** from Client

## 💰 Financial (2)
- Invoice from Vendor
- Payment confirmation

## 📧 General (10)
- Newsletter updates
- Notifications
```

## Export Options

Export summaries to file:

```
/summarize today --export markdown
/summarize week --export json
/summarize recent --export text
```

**Exports to:** `output/reports/`

## Email Categories

| Icon | Category | Description |
|------|----------|-------------|
| 🚨 | Urgent | Contains urgent keywords |
| 💰 | Financial | Invoices, payments |
| 📅 | Meeting | Calendar, schedules |
| 📰 | Newsletter | Digests, newsletters |
| 📦 | Order | Shipping, deliveries |
| 📧 | General | Everything else |

## Action Detection

Summaries highlight emails that may need action:
- "Please reply" → May need response
- "Deadline" → Time-sensitive
- "Can you" → Request
- "Meeting" → Calendar item

## Examples

**Quick summary:**
```
/summarize
```

**Today's digest:**
```
/summarize today
```

**Export weekly report:**
```
/summarize week --export markdown
```

## Related Commands

- `/inbox` - Full email reading
- `/reply` - Reply to emails
- `/compose` - Write emails
