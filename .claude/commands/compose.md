---
name: compose
description: Compose and send individual emails
---

# /compose Command

Write and send individual emails.

## Usage

```
/compose [to] [subject]
```

## Workflow

1. **Gather Details:**
   - Recipient email
   - Subject line
   - Email body/content

2. **Preview:**
   - Show complete email draft
   - Offer edit option

3. **Approve:**
   - Wait for explicit confirmation

4. **Send or Save:**
   - Send immediately, or
   - Save as Gmail draft

**Skill:** Routes to `email-composer`

## Examples

**Start composing:**
```
/compose
```

**Compose to specific person:**
```
/compose john@example.com "Meeting Follow-up"
```

## Options

### Using Templates

You can use templates for consistent formatting:

```
/compose --template outreach/introduction.txt
```

### With Attachments

Mention files to attach:
```
/compose
> Send proposal.pdf to client@example.com
```

### Save as Draft

Instead of sending immediately:
```
> Save this as a draft instead of sending
```

## Draft Preview

Before sending, you'll always see:

```
📧 Email Preview:

To: recipient@example.com
Subject: Your Subject

Body:
[Your email content]

---
Options:
1. Send now
2. Edit
3. Save as draft
4. Cancel
```

## Related Commands

- `/reply` - Reply to existing emails
- `/inbox` - Read inbox first
- `/outreach` - Bulk campaigns
- `/templates` - Manage templates
