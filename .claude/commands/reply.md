---
name: reply
description: Reply to emails with draft preview and approval
---

# /reply Command

Generate and send email replies with mandatory preview and approval.

## Usage

```
/reply [message_id or search]
```

## Workflow

1. **Find Email:**
   - Search for the email to reply to
   - Or provide message ID directly

2. **Analyze:**
   - Read original email
   - Understand context/intent
   - Suggest reply type

3. **Draft:**
   - Generate appropriate reply
   - Show complete draft

4. **Preview & Approve:**
   - User reviews draft
   - User can edit or approve
   - **NEVER sends without approval**

5. **Send:**
   - Only after explicit "yes"

**Skill:** Routes to `reply-generator`

## Examples

**Reply to recent email:**
```
/reply
> Reply to the email from John about the meeting
```

**Reply by message ID:**
```
/reply 18abc123def
```

**Reply with specific type:**
```
/reply
> Reply to confirm the meeting with Sarah
```

## Reply Types

| Type | Use Case |
|------|----------|
| `acknowledge` | Quick receipt confirmation |
| `confirm` | Confirming requests/meetings |
| `decline` | Politely declining |
| `followup` | Following up on previous |
| `custom` | Your own message |

## Draft Preview

You'll always see the draft before sending:

```
📧 Draft Reply:

To: sender@example.com
Subject: Re: Original Subject

Body:
Hi [Name],

[Draft reply content]

Best regards,
[Your Name]

---
Original email:
[snippet of original]

---
Options:
1. Send as-is
2. Edit reply
3. Change reply type
4. Save as draft
5. Cancel
```

## Safety

- **Always previews** before sending
- **Always asks** for approval
- **Never auto-sends**
- **Can save as draft** instead

## Related Commands

- `/inbox` - Find emails to reply to
- `/compose` - New emails (not replies)
- `/summarize` - Understand email first
