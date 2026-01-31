# 10X LinkedIn Outreach

A focused LinkedIn outreach automation skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Discover profiles, send personalized connection requests, and message accepted connections — all from your terminal.

**Built by [1to10x.in](https://1to10x.in)**

---

## What Is This?

This is a Claude Code skill that automates LinkedIn outreach in 3 steps:

1. **Discover** — Search LinkedIn for target profiles by industry, role, location
2. **Connect** — Send personalized connection requests (or InMails for 3rd-degree)
3. **Message** — Follow up with accepted connections using smart template selection

It uses a Chrome extension as a bridge between Claude Code and LinkedIn's UI. No LinkedIn API keys needed — it works through browser automation with human-like delays.

---

## Why Use This?

| Problem | Solution |
|---------|----------|
| Manually searching LinkedIn is slow | `/discover` scrapes up to 100 profiles at once |
| Writing personalized notes for each person | AI fills templates using deep profile scans |
| Tracking who you sent requests to | `profiles.json` tracks every profile's lifecycle |
| Hitting LinkedIn limits and getting flagged | Built-in rate limiting (20 connections/day, 2-5 min delays) |
| Forgetting to follow up | `/message` checks acceptance and sends follow-ups |
| Losing progress mid-batch | Saves after every single action (resume-safe) |

---

## Architecture

```
You (Claude Code)
  │
  ├── /discover, /connect, /message
  │
  ▼
extension_client.js (Node.js HTTP server on localhost:3456)
  │
  ▼
Chrome Extension (polls server every 500ms)
  │
  ▼
content.js (injected into linkedin.com)
  │
  ▼
LinkedIn DOM (clicks buttons, types messages, scrapes profiles)
  │
  ▼
Results flow back: content.js → extension → server → Claude Code
```

Zero external dependencies. Only uses Node.js built-in `http` module.

---

## Setup

### Prerequisites
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Google Chrome
- Node.js 18+
- A LinkedIn account

### Step 1: Clone the repo
```bash
git clone https://github.com/DeepakChander/10x-Linkedin-Outreach.git
cd 10x-Linkedin-Outreach
```

### Step 2: Load the Chrome Extension
1. Open Chrome and go to `chrome://extensions`
2. Toggle **Developer mode** ON (top right)
3. Click **Load unpacked**
4. Select the `extension/` folder from this project
5. You should see **"10X LinkedIn"** appear with a red "OFF" badge

### Step 3: Log into LinkedIn
1. Open a new Chrome tab
2. Go to `linkedin.com` and log in
3. Keep this tab open while using the skill

### Step 4: Test the connection
```bash
# Start the bridge server
node .claude/scripts/extension_client.js --server
```
The extension badge should turn green ("ON").

In another terminal:
```bash
node .claude/scripts/extension_client.js ping
```
Expected output: `{"success": true, "ready": true, "loggedIn": true}`

### Step 5: Open Claude Code
```bash
claude
```
You now have access to `/discover`, `/connect`, and `/message`.

---

## Commands

### `/discover` — Find LinkedIn Profiles (Step 1)

Searches LinkedIn and saves matching profiles to `output/profiles.json`.

**What it does:**
1. Asks you for search filters (industry, role, location, company size, keywords)
2. Builds a LinkedIn search URL from your filters
3. Scrapes profile cards across up to 10 pages (~100 profiles)
4. Deduplicates against existing profiles in your database
5. Saves new profiles with status `"discovered"`

**Example:**
```
You: /discover
Claude: What industry? → SaaS
Claude: What role? → CTO
Claude: What location? → San Francisco
Claude: Found 47 new profiles (3 duplicates skipped). Batch: 2026-01-31-saas-cto
```

**What gets saved per profile:**
```json
{
  "id": "a1b2c3d4",
  "name": "Jane Doe",
  "headline": "CTO at Acme Corp",
  "location": "San Francisco Bay Area",
  "profileUrl": "https://www.linkedin.com/in/janedoe",
  "degree": "2nd",
  "status": "discovered",
  "batch_id": "2026-01-31-saas-cto",
  "created_at": "2026-01-31T10:00:00Z"
}
```

---

### `/connect` — Send Connection Requests (Step 2)

Sends personalized connection requests to all discovered profiles. Falls back to InMail for 3rd-degree connections.

**What it does:**
1. Reads `output/profiles.json` and filters `status === "discovered"`
2. Shows you the list and asks for **one-time approval**
3. For each profile:
   - Deep scans the profile (name, headline, about, experience, posts, followers)
   - If Connect button exists → fills connection note template → sends request
   - If no Connect button (3rd degree) → fills InMail template → sends InMail
   - Waits 2-5 minutes (randomized) before the next one
   - Saves progress after every single action
4. Stops automatically at daily limits or if LinkedIn shows a warning

**Connection note template** (max 300 chars):
```
Hi {{first_name}}, your {{specific_insight}} at {{company}} caught my attention.
I'm exploring how leaders like you are approaching AI in practice. Would love to connect.
```

**Error handling:**
| Error | What happens |
|-------|-------------|
| Weekly invitation limit | Stops immediately, reports partial progress |
| CAPTCHA detected | Pauses, tells you to solve it manually |
| Already connected | Marks profile, skips to `/message` |
| Pending request | Skips |
| Profile not found (404) | Marks as `"profile_not_found"` |

---

### `/message` — Message Accepted Connections (Step 3)

Checks which connection requests were accepted, then sends personalized follow-up messages.

**What it does:**
1. Reads `output/profiles.json` and filters `status === "connection_sent"`
2. Groups profiles by date and recommends timing:
   ```
   Ready to check 52 profiles:
   - 30 from yesterday (good to check now)
   - 17 from today (may be too early)
   - 5 from 3+ days ago (overdue)
   ```
3. Checks each profile's connection status on LinkedIn
4. For accepted connections:
   - Deep scans the profile
   - Auto-selects the best message template (see Template Selection below)
   - Fills template variables from profile data
5. Shows you the first 3 messages for preview
6. After **one-time approval**, sends all messages with 30-60s delays
7. Marks stale profiles: 7+ days with no acceptance → `"cold"`, 14+ days → `"archived"`

---

## Template Selection

The skill automatically picks the right message template based on the profile:

| Priority | Condition | Template | Tone |
|----------|-----------|----------|------|
| 1 | CXO/Director + company >200 employees | `option_3_formal` | Professional, enterprise-focused |
| 2 | Founder + "building/scaling/growing" in headline + company <200 | `option_5_future_facing` | Confident, growth-oriented |
| 3 | Founder/CEO/CTO (general) | `option_1_brand_invite` | Brand-forward, value proposition |
| 4 | 5000+ followers OR "creator/speaker/advisor" in headline | `option_4_collaboration` | Partnership framing |
| 5 | VP/Director + posts about AI/marketing/growth | `option_2_featured_voice` | "Featured voice" positioning |
| 6 | 2nd degree + active poster | `base_draft` | Casual, no brand mention |
| 7 | Fallback (none of the above) | `option_1_brand_invite` | Default |

All templates use these variables filled from deep profile scans:
- `{{first_name}}` — First name
- `{{company}}` — Current company
- `{{headline}}` — Their LinkedIn headline
- `{{specific_insight}}` — Extracted from their about section, recent posts, or experience
- `{{role}}` — Job title
- `{{industry}}` — Industry
- `{{sender_name}}` — Your name

---

## Profile Lifecycle

Every profile goes through a status lifecycle tracked in `output/profiles.json`:

```
discovered ──→ connection_sent ──→ accepted ──→ message_sent
                    │                  │
                    │                  ├──→ pending ──→ cold (7d) ──→ archived (14d)
                    │                  │
                    │                  └──→ declined
                    │
                    └──→ inmail_sent (already got a message)

discovered ──→ already_connected (skip to /message)
discovered ──→ profile_not_found (dead link)
```

---

## Rate Limits

Built-in rate limiting prevents LinkedIn from flagging your account:

| Action | Daily Limit | Delay Between |
|--------|------------|---------------|
| Connection requests | 20 | 2-5 minutes |
| InMails | 10 (50/month) | 2-5 minutes |
| Messages | 40 | 30-60 seconds |
| Profile scrapes | 100 | Automatic |

Limits are tracked in `output/.limits.json` and reset daily at midnight. Monthly InMail count resets on the 1st.

The extension client checks limits **before** every action and refuses to proceed if limits are reached.

---

## Edge Cases

| Scenario | How It's Handled |
|----------|-----------------|
| LinkedIn not logged in | Returns error, tells you to log in |
| CAPTCHA appears | Pauses all actions, alerts you to solve it manually |
| Weekly invitation limit (LinkedIn's ~100/week cap) | Stops Step 2, reports partial progress, resume next week |
| Profile deactivated or 404 | Marks `"profile_not_found"`, skips |
| Already connected | Marks `"already_connected"`, skips to Step 3 |
| Existing conversation thread | Skips auto-message, alerts you |
| Browser closed mid-batch | Resume-safe — picks up from last saved profile |
| Duplicate profiles across searches | Deduplication by `profileUrl` |
| Connection note exceeds 300 chars | Truncates to 295 + "..." |
| InMail monthly quota near limit | Warns at 80%, blocks at 100% |
| No response after 7 days | Marks `"cold"` |
| No response after 14 days | Marks `"archived"` |
| Extension disconnected | Auto-reconnects every 500ms, badge shows red |
| Slow internet | 20-second element wait timeout, 1 retry before fail |

---

## Extension Client CLI

The bridge server can also be used directly from the terminal:

```bash
# Start server (stays alive)
node .claude/scripts/extension_client.js --server

# Test connection
node .claude/scripts/extension_client.js ping

# Search profiles
node .claude/scripts/extension_client.js searchProfiles '{"filters":{"keywords":"AI SaaS","location":"USA"}}'

# Deep scan a profile
node .claude/scripts/extension_client.js deepScan '{"profileUrl":"https://www.linkedin.com/in/janedoe"}'

# Send connection request
node .claude/scripts/extension_client.js sendConnection '{"profileUrl":"...","note":"Hi Jane, would love to connect."}'

# Send InMail (Premium only)
node .claude/scripts/extension_client.js sendInMail '{"profileUrl":"...","subject":"Quick question","body":"Hi..."}'

# Check if connection was accepted
node .claude/scripts/extension_client.js checkAcceptance '{"profileUrl":"..."}'

# Send message to connection
node .claude/scripts/extension_client.js sendMessage '{"profileUrl":"...","message":"Hi Jane, thanks for connecting!"}'

# Check rate limits
node .claude/scripts/extension_client.js getLimits

# Check server status
node .claude/scripts/extension_client.js getStatus
```

---

## File Structure

```
10x-Linkedin-Outreach/
├── extension/                      Chrome extension
│   ├── manifest.json               Manifest V3, LinkedIn-only permissions
│   ├── background.js               Polls server, routes commands to content script
│   ├── content.js                  LinkedIn DOM automation (search, connect, message)
│   ├── popup/
│   │   ├── popup.html              Extension popup UI
│   │   ├── popup.css               Dark theme styles
│   │   └── popup.js                Status display + reconnect
│   └── icons/                      Extension icons
│
├── .claude/
│   ├── commands/
│   │   ├── discover.md             Step 1: Search and save profiles
│   │   ├── connect.md              Step 2: Send connections/InMails
│   │   └── message.md              Step 3: Message accepted connections
│   ├── scripts/
│   │   └── extension_client.js     Node.js HTTP bridge (zero dependencies)
│   ├── skills/
│   │   └── linkedin-outreach/
│   │       └── SKILL.md            Unified skill definition
│   ├── templates/
│   │   └── linkedin/
│   │       ├── connection-note.md  Connection request note (300 char max)
│   │       ├── inmail-template.md  InMail template with subject line
│   │       └── messages/
│   │           ├── base_draft.md           Casual, no brand (2nd degree active)
│   │           ├── option_1_brand_invite.md Brand-forward (Founder/CEO/CTO)
│   │           ├── option_2_featured_voice.md Featured voice (VP/Director + AI posts)
│   │           ├── option_3_formal.md       Formal enterprise (CXO + large company)
│   │           ├── option_4_collaboration.md Collaboration (high followers/creators)
│   │           └── option_5_future_facing.md Future-facing (scaling founders)
│   └── settings.local.json        Bash permissions for node scripts
│
├── output/
│   ├── profiles.json               Profile database (gitignored)
│   └── .limits.json                Rate limit tracking (gitignored)
│
├── CLAUDE.md                       Claude Code project instructions
├── README.md                       This file
├── package.json                    Project metadata (zero dependencies)
├── setup.md                        Visual setup guide for non-technical users
└── .gitignore                      Ignores profiles, limits, logs, node_modules
```

---

## Troubleshooting

**Extension badge stays red (OFF)?**
- Make sure the server is running: `node .claude/scripts/extension_client.js --server`
- Check that port 3456 is not in use: `lsof -i :3456` or `netstat -an | findstr 3456`

**"No LinkedIn tab open" error?**
- Open `linkedin.com` in Chrome and make sure you're logged in
- The extension only works on `*.linkedin.com` pages

**CAPTCHA appeared?**
- Solve it manually in the browser
- Resume your command — it picks up where it left off

**Weekly limit reached?**
- LinkedIn caps at ~100 invitations per week
- Wait until next week, the skill will stop automatically and save progress

**Extension not loading?**
- Make sure you're using Chrome (not Firefox/Safari)
- Check `chrome://extensions` for any error messages
- Try "Reload" on the extension

---

## License

MIT License - Free to use, modify, and distribute.
