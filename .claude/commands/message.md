---
allowed-tools: Bash, Read, Write, AskUserQuestion
description: "Message accepted LinkedIn connections"
---

# /message — Message Accepted Connections

## Prerequisites (auto-handled, no user action needed)
The extension client auto-starts the server, waits for Chrome extension handshake, verifies LinkedIn login, then executes. User just needs Chrome open with LinkedIn logged in.

## Instructions

1. Read `output/profiles.json`.

2. Filter profiles where `status === "connection_sent"` (skip `"inmail_sent"` — those already got a message via InMail).

3. Group by date and give smart recommendation:
   ```
   Ready to check N profiles:
   - 30 from yesterday (good to check now)
   - 17 from today (may be too early)
   - 5 from 3+ days ago (overdue)
   ```

4. For each profile, check acceptance:
```bash
node .claude/scripts/extension_client.js checkAcceptance '{"profileUrl":"<url>"}'
```

5. Sort results:
   - **Accepted** → queue for messaging
   - **Pending** → update `last_checked`, skip
   - **Not connected / declined** → update status to `"declined"`

6. For each accepted profile:
   a. Deep scan if not already scanned:
   ```bash
   node .claude/scripts/extension_client.js deepScan '{"profileUrl":"<url>"}'
   ```

   b. Select template using rules from SKILL.md:
   - Read the profile's headline, company, followers, posts
   - Apply rules in priority order (1-7)
   - Read the selected template from `.claude/templates/linkedin/messages/`

   c. Fill template variables:
   - `{{first_name}}` — first word of name
   - `{{company}}` — from deep scan
   - `{{headline}}` — their headline
   - `{{specific_insight}}` — from about/posts/experience
   - `{{role}}` — their job title

   d. Queue the message with template name

7. Show first 3 messages for preview:
   ```
   Preview (3 of N):

   → Jane Doe (option_1_brand_invite):
   "Hi Jane, loved your take on AI in fintech..."

   → John Smith (base_draft):
   "Hey John, your recent post about scaling..."
   ```

8. Ask for **single approval**: "Send all N messages?"

9. Send each message:
```bash
node .claude/scripts/extension_client.js sendMessage '{"profileUrl":"<url>","message":"<filled message>"}'
```
   - Update status to `"message_sent"`, set `messaged_at`
   - Save after each send
   - Wait 30-60 seconds between messages

10. Handle stale profiles (no response tracking):
    - If `connected_at` is 7+ days ago and still `"connection_sent"` → mark `"cold"`
    - If 14+ days → mark `"archived"`

11. Report: "Sent N messages, M still pending, K declined."

## Error Handling
- `EXTENSION_NOT_CONNECTED` → Tell user: "Open Chrome, make sure the 10X LinkedIn extension is enabled, and open linkedin.com"
- `NOT_LOGGED_IN` → Tell user: "Log in to LinkedIn in Chrome and try again"
- `CONTENT_SCRIPT_NOT_READY` → Tell user: "Refresh the LinkedIn tab (F5) and try again"
