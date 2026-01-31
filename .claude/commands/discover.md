---
allowed-tools: Bash, Read, Write, AskUserQuestion
description: "Find LinkedIn profiles by search filters"
---

# /discover — Find LinkedIn Profiles

## Prerequisites (auto-handled, no user action needed)
The extension client auto-starts the server, waits for Chrome extension handshake, verifies LinkedIn login, then executes. User just needs Chrome open with LinkedIn logged in.

## Instructions

1. Ask the user for search filters:
   - **Industry** (e.g., SaaS, FinTech, HealthTech)
   - **Role/Title** (e.g., CTO, VP Engineering, Founder)
   - **Location** (e.g., USA, San Francisco, Europe)
   - **Company size** (e.g., 50-200, startup, enterprise)
   - **Keywords** (optional, extra search terms)

2. Build the filters JSON from their response.

3. Run the search (server auto-starts, waits for extension, verifies login):
```bash
node .claude/scripts/extension_client.js searchProfiles '{"filters":{"keywords":"<keywords>","industry":"<industry>","location":"<location>","title":"<role>"},"maxPages":3}'
```
The command will:
- Auto-start HTTP server on port 3456
- Wait up to 30s for Chrome extension to connect
- Ping content script to verify LinkedIn is logged in
- If login check fails, it reports the error — tell user to open Chrome with LinkedIn

4. Read existing `output/profiles.json` (create if missing, start with `[]`).

5. Deduplicate: skip any profile whose `profileUrl` already exists in profiles.json.

6. For each new profile, add to profiles.json:
```json
{
  "id": "<generate-uuid>",
  "name": "<name>",
  "headline": "<headline>",
  "location": "<location>",
  "profileUrl": "<url>",
  "degree": "<degree>",
  "status": "discovered",
  "batch_id": "<YYYY-MM-DD>-<industry>-<role>",
  "created_at": "<ISO timestamp>"
}
```

7. Write updated profiles.json.

8. Report: "Found **N** new profiles (M duplicates skipped). Batch: `<batch_id>`"

9. Suggest: "Run `/connect` to send connection requests to these profiles."

## Error Handling
- `EXTENSION_NOT_CONNECTED` → Tell user: "Open Chrome, make sure the 10X LinkedIn extension is enabled, and open linkedin.com"
- `NOT_LOGGED_IN` → Tell user: "Log in to LinkedIn in Chrome and try again"
- `CONTENT_SCRIPT_NOT_READY` → Tell user: "Refresh the LinkedIn tab (F5) and try again"
- `CAPTCHA` → Tell user: "Solve the CAPTCHA in Chrome and run /discover again"
- `RATE_LIMITED` → Tell user the daily limit reached, try tomorrow
- `TIMEOUT` → The extension took too long. Try again.
