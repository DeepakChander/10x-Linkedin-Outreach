---
allowed-tools: Bash, Read, Write
description: "Send connection requests and InMails to discovered profiles"
---

# /connect — Send Connection Requests

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
   
   d. If connection fails with NO_CONNECT_BUTTON (3rd degree, no mutual):
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
   
   h. Wait 2-5 minutes (randomized) before next profile

7. Report: "Sent N connections, M InMails. K skipped (already connected/pending). Stopped: <reason if applicable>"

8. Suggest: "Run `/message` tomorrow to follow up with accepted connections."
