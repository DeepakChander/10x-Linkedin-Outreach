# 10X LinkedIn Outreach — Skill Definition

## Purpose
Automated LinkedIn outreach: discover profiles, send connections/InMails, and message accepted connections.

## Architecture
```
Claude Code → node .claude/scripts/extension_client.js <command> <json>
→ HTTP localhost:3456 → Chrome extension polls → content.js executes on LinkedIn
```

## Commands

### /discover — Find Profiles (Step 1)
Ask user for search filters, then run:
```bash
node .claude/scripts/extension_client.js searchProfiles '{"filters":{"keywords":"...","industry":"...","location":"..."},"maxPages":10}'
```
Save results to `output/profiles.json` with status `"discovered"` and `batch_id`.
Deduplicate by `profileUrl` against existing profiles.

### /connect — Send Connections (Step 2)
Read `output/profiles.json`, filter `status === "discovered"`.
Show list, get single approval, then for each profile:
1. Check if Connect button exists
2. If yes → render connection note → `sendConnection` → status: `"connection_sent"`
3. If no Connect → `deepScan` → render InMail → `sendInMail` → status: `"inmail_sent"`
4. Wait 2-5 min (randomized) between each
5. Save after EACH action (resume-safe)
6. Stop at daily limit (20 connections, 10 InMails)

Handle: WEEKLY_LIMIT (stop + report), CAPTCHA (pause + alert), ALREADY_CONNECTED (skip to Step 3), PENDING (skip).

### /message — Message Accepted (Step 3)
Read `output/profiles.json`, filter `status === "connection_sent"`.
For each: `checkAcceptance`
- `accepted` → deepScan → select template → fill variables → queue message
- `pending` → update `last_checked`, skip
- `declined/not_connected` → update status

Show first 3 messages for preview, approve once, send rest with 30-60s delays.

## profiles.json Schema
```json
[
  {
    "id": "uuid",
    "name": "Jane Doe",
    "headline": "CTO at Acme",
    "company": "Acme Corp",
    "location": "San Francisco",
    "profileUrl": "https://www.linkedin.com/in/janedoe",
    "degree": "2nd",
    "status": "discovered|connection_sent|inmail_sent|accepted|message_sent|pending|declined|cold|archived|profile_not_found|already_connected",
    "batch_id": "2026-01-31-saas-cto",
    "template_used": "option_1",
    "connection_note": "...",
    "message_sent": "...",
    "deep_scan": { "about": "...", "experience": [], "posts": [], "followers": "..." },
    "created_at": "2026-01-31T10:00:00Z",
    "connected_at": null,
    "messaged_at": null,
    "last_checked": null
  }
]
```

## Template Selection Rules
| Priority | Condition | Template |
|----------|-----------|----------|
| 1 | CXO/Director + company >200 employees | option_3_formal |
| 2 | Founder + headline has "building/scaling/growing" + company <200 | option_5_future_facing |
| 3 | Founder/CEO/CTO (general) | option_1_brand_invite |
| 4 | Followers 5000+ OR headline has "creator/speaker/advisor/mentor" | option_4_collaboration |
| 5 | VP/Director + posts about AI/marketing/growth | option_2_featured_voice |
| 6 | 2nd degree + active poster | base_draft |
| 7 | Fallback | option_1_brand_invite |

## Rate Limits
- Connections: 20/day
- InMails: 10/day, 50/month
- Messages: 40/day
- Profile scrapes: 100/day
- Between connections: 2-5 min
- Between messages: 30-60s

## Edge Cases
- LinkedIn not logged in → tell user to log in
- CAPTCHA → pause, alert user
- Weekly invitation limit → stop, report partial progress
- Profile 404 → mark "profile_not_found"
- Already connected → mark "already_connected", skip to /message
- Browser closed mid-batch → resume from last saved profile
- Connection note >300 chars → truncate to 295 + "..."
- InMail monthly quota → warn at 80%, block at 100%
- No response 7+ days → mark "cold", 14+ days → mark "archived"

## Setup
1. Load Chrome extension from `extension/` folder
2. Log into LinkedIn in Chrome
3. Run: `node .claude/scripts/extension_client.js --server`
4. Extension badge turns green → ready
