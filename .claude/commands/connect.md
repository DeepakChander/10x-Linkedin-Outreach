---
allowed-tools: Bash, Read, Write, AskUserQuestion
description: "Send connection requests and InMails to discovered profiles"
---

# /connect — Send Connection Requests

## Prerequisites (auto-handled, no user action needed)
The extension client auto-starts the server, waits for Chrome extension handshake, verifies LinkedIn login, then executes. User just needs Chrome open with LinkedIn logged in.

## Instructions

1. Read `output/profiles.json`.

2. Filter profiles where `status === "discovered"`. If none, tell user to run `/discover` first.

3. Show the list:
   ```
   Ready to connect with N profiles:
   1. Jane Doe — CTO at Acme (2nd degree)
   2. John Smith — VP Eng at StartupCo (3rd degree)
   ...
   ```

4. Ask for **single approval**: "Send connection requests to all N profiles? (approve once)"

5. Check rate limits first:
```bash
node .claude/scripts/extension_client.js getLimits
```

6. For each approved profile:
   a. Deep scan the profile:
   ```bash
   node .claude/scripts/extension_client.js deepScan '{"profileUrl":"<url>"}'
   ```

   b. Save deep_scan data to the profile in profiles.json.

   c. Try sending connection with personalized note:
   - Read `.claude/templates/linkedin/connection-note.md`
   - Fill variables: `{{first_name}}`, `{{specific_insight}}`, `{{company}}` from deep scan
   ```bash
   node .claude/scripts/extension_client.js sendConnection '{"profileUrl":"<url>","note":"<filled note>"}'
   ```

   d. If connection fails with NO_CONNECT_BUTTON or FOLLOW_ONLY (any degree — profile only has Follow button, no Connect):
   - Read `.claude/templates/linkedin/inmail-template.md`
   - Fill variables from deep scan
   ```bash
   node .claude/scripts/extension_client.js sendInMail '{"profileUrl":"<url>","subject":"<subject>","body":"<body>"}'
   ```
   - Update status to `"inmail_sent"`

   e. If connection succeeds: update status to `"connection_sent"`, set `connected_at`

   f. Handle errors:
   - WEEKLY_LIMIT → stop immediately, report progress
   - CAPTCHA → stop, tell user to solve it
   - ALREADY_CONNECTED → set status `"already_connected"`
   - PENDING → set status `"pending"`
   - RATE_LIMITED → stop, report progress

   g. **Save profiles.json after EACH action** (resume-safe)

   h. Wait 5 seconds before next profile

7. Report: "Sent N connections, M InMails. K skipped (already connected/pending). Stopped: <reason if applicable>"

8. Suggest: "Run `/message` tomorrow to follow up with accepted connections."

## Error Handling
- `EXTENSION_NOT_CONNECTED` → Tell user: "Open Chrome, make sure the 10X LinkedIn extension is enabled, and open linkedin.com"
- `NOT_LOGGED_IN` → Tell user: "Log in to LinkedIn in Chrome and try again"
- `CONTENT_SCRIPT_NOT_READY` → Tell user: "Refresh the LinkedIn tab (F5) and try again"
