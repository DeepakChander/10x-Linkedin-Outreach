---
name: template
description: Manage email and message templates for outreach campaigns
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob"]
---

# Template Manager

Manage email and message templates for outreach and campaigns.

## User Request

$ARGUMENTS

## Instructions

1. List available templates from `.claude/templates/`
2. Templates are organized by platform: `email/`, `linkedin/`, `twitter/`, `instagram/`
3. Each template uses Markdown with YAML frontmatter and `{{variable}}` placeholders
4. Support operations: list, view, create, edit, duplicate, delete

## Template Structure

```
.claude/templates/
├── email/
│   ├── outreach/        # Cold emails, warm intros, referrals
│   ├── follow-up/       # Follow-up sequences
│   ├── promotional/     # Product launches, announcements
│   └── newsletters/     # Weekly/monthly digests
├── linkedin/
│   ├── connection-requests/
│   ├── messages/
│   ├── inmails/
│   └── comments/
├── twitter/
│   ├── tweets/
│   ├── replies/
│   └── dms/
├── instagram/
│   ├── dms/
│   ├── comments/
│   └── stories/
└── custom/              # User-created templates
```

## Variables

Templates support these variables:
- `{{first_name}}`, `{{last_name}}`, `{{company}}`
- `{{role}}`, `{{industry}}`, `{{location}}`
- `{{sender_name}}`, `{{sender_company}}`
- `{{custom_field}}` — any user-defined field
