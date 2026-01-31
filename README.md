# 10X LinkedIn Outreach

A focused LinkedIn outreach automation skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Discover profiles, send personalized connection requests, and message accepted connections — all from your terminal.

**Built by [1to10x.in](https://1to10x.in)**

---

## What Is This?

This is a Claude Code skill that automates LinkedIn outreach in 3 steps:

1. **`/discover`** — Search LinkedIn for target profiles by industry, role, location
2. **`/connect`** — Send personalized connection requests (or InMails for 3rd-degree)
3. **`/message`** — Follow up with accepted connections using smart template selection

It uses a Chrome extension as a bridge between Claude Code and LinkedIn's UI. No LinkedIn API keys needed — it works through browser automation with human-like delays.

### Zero Manual Steps

Every command is fully self-contained. When you type `/discover`, the skill automatically:
1. Starts the HTTP bridge server
2. Waits for the Chrome extension to connect (handshake)
3. Pings the content script to verify LinkedIn is logged in
4. Navigates Chrome to the right pages
5. Re-injects the content script after every page navigation
6. Scrapes data and returns results

**You never need to manually run `node ... --server` or refresh tabs.** Just type the command and provide your filters.

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
You type: /discover
         │
         ▼
Claude Code runs: node extension_client.js searchProfiles '{...}'
         │
         ├── 1. Auto-starts HTTP server on port 3456
         ├── 2. Waits for extension handshake (up to 30s)
         ├── 3. Sends ping → verifies LinkedIn login
         ├── 4. Sends actual command
         │
         ▼
Chrome Extension (background.js polls server every 500ms)
         │
         ├── Finds LinkedIn tab
         ├── Navigates to target URL (search page / profile)
         ├── Waits for page load (complete)
         ├── Re-injects content.js (fresh listener every time)
         │
         ▼
content.js (injected into linkedin.com)
         │
         ├── Scrapes DOM (profiles, buttons, text)
         ├── Clicks buttons (Connect, Message, Send)
         ├── Types personalized notes with human-like delays
         │
         ▼
Results flow back: content.js → background.js → server → Claude Code
```

### Key Design Decisions

- **Navigation from background.js, not content.js** — When the page navigates (e.g., search page 1 → page 2), the content script dies. So `background.js` handles all `chrome.tabs.update()` navigation, waits for load, then re-injects `content.js` with a fresh message listener.
- **Always re-inject** — Content scripts go stale after extension reloads. Every command re-injects `content.js` before sending messages, with duplicate-listener guards.
- **Handshake before command** — The client waits for the extension's first `/poll` request before queuing any command. No more race conditions.
- **Ping verification** — Before any real command, a `ping` is sent to verify the content script is alive and LinkedIn is logged in.

---

## One-Time Setup

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
5. You should see **"10X LinkedIn Outreach"** appear

### Step 3: Log into LinkedIn
1. Open a new Chrome tab
2. Go to `linkedin.com` and log in
3. Keep this tab open

### Step 4: Open Claude Code and run commands
```bash
claude
```
Then type `/discover` — everything else is automatic.

> **That's it.** No server to start manually. No scripts to run. No tabs to refresh.

---

## Commands

### `/discover` — Find LinkedIn Profiles (Step 1)

Searches LinkedIn and saves matching profiles to `output/profiles.json`.

**What happens when you type `/discover`:**
1. Claude asks you for search filters (industry, role, location, company size, keywords)
2. Builds a LinkedIn search URL from your filters
3. Runs `node extension_client.js searchProfiles '{...}'` which:
   - Auto-starts server on port 3456
   - Waits for Chrome extension handshake
   - Verifies LinkedIn login via ping
   - Tells background.js to navigate to search URL
   - background.js navigates Chrome → waits for load → re-injects content.js
   - content.js scrapes profile cards on the page
   - Repeats for up to 3 pages (~30 profiles per page)
4. Deduplicates against existing profiles in your database
5. Saves new profiles with status `"discovered"`

**Example interaction:**
```
You: /discover
Claude: What industry? → SaaS
Claude: What role? → CTO
Claude: What location? → San Francisco
Claude: Found 47 new profiles (3 duplicates skipped). Batch: 2026-01-31-saas-cto
Claude: Run /connect to send connection requests to these profiles.
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

**What happens when you type `/connect`:**
1. Reads `output/profiles.json` and filters `status === "discovered"`
2. Shows you the list and asks for **one-time approval**
3. For each profile (all automated):
   - Server auto-starts + handshake + login verify
   - background.js navigates to profile URL → waits for load → injects content.js
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

**What happens when you type `/message`:**
1. Reads `output/profiles.json` and filters `status === "connection_sent"`
2. Groups profiles by date and recommends timing
3. For each profile (all automated):
   - Server auto-starts + handshake + login verify
   - background.js navigates to profile → injects content.js
   - Checks connection status (accepted / pending / declined)
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
| Connection requests | 20 | 5 seconds |
| InMails | 10 (50/month) | 5 seconds |
| Messages | 40 | 5 seconds |
| Profile scrapes | 100 | Automatic |

Limits are tracked in `output/.limits.json` and reset daily at midnight. Monthly InMail count resets on the 1st.

The extension client checks limits **before** every action and refuses to proceed if limits are reached.

---

## How the Auto-Connection Works

This is the flow when you type any command — no manual steps needed:

```
1. Claude runs: node extension_client.js <command> <args>
          │
2. Client tries to bind port 3456
          ├── Success → starts server
          └── Port in use → sends command via HTTP to existing server
          │
3. Server starts, waits for extension poll
          │  (Extension background.js polls /poll every 500ms)
          │
4. Extension connects (first /poll = handshake)
          │
5. Client sends "ping" command
          │  → background.js injects content.js into LinkedIn tab
          │  → content.js responds with {loggedIn: true}
          │
6. Client sends actual command (e.g., searchProfiles)
          │  → background.js navigates Chrome to search URL
          │  → waits for page load (complete)
          │  → re-injects content.js (old one died with navigation)
          │  → content.js scrapes DOM, returns data
          │
7. Result flows back to Claude → profiles.json updated
```

### Why re-inject content.js?

Chrome extensions have a fundamental limitation: when a page navigates, the content script's `chrome.runtime.onMessage` listener dies. This means:
- After `searchProfiles` navigates to page 2, the old content.js is gone
- After extension reload in `chrome://extensions`, all existing content scripts lose their listeners
- After Chrome restarts, no content scripts are running

Our solution: `background.js` handles ALL navigation via `chrome.tabs.update()`, waits for `tabs.onUpdated` status=complete, then always calls `chrome.scripting.executeScript` to inject a fresh `content.js`. The content script has a duplicate-injection guard that removes the old listener before registering a new one.

---

## Edge Cases

| Scenario | How It's Handled |
|----------|-----------------|
| LinkedIn not logged in | Auto-detected by ping, error reported |
| CAPTCHA appears | Pauses all actions, alerts you to solve it manually |
| Weekly invitation limit | Stops, reports partial progress |
| Profile deactivated or 404 | Marks `"profile_not_found"`, skips |
| Already connected | Marks `"already_connected"`, skips to Step 3 |
| Browser closed mid-batch | Resume-safe — picks up from last saved profile |
| Duplicate profiles across searches | Deduplication by `profileUrl` |
| Connection note exceeds 300 chars | Truncates to 295 + "..." |
| InMail monthly quota near limit | Warns at 80%, blocks at 100% |
| No response after 7 days | Marks `"cold"` |
| No response after 14 days | Marks `"archived"` |
| Extension reloaded while tab open | Auto re-injects content script |
| Server already running on port 3456 | Sends command via HTTP to existing server |
| Page navigation kills content script | background.js re-injects after every navigation |
| Slow internet / LinkedIn SPA delays | 2s extra wait after page load + 20s element timeout |

---

## File Structure

```
10x-Linkedin-Outreach/
├── extension/                      Chrome extension
│   ├── manifest.json               Manifest V3, LinkedIn-only permissions
│   ├── background.js               Polls server, navigates tabs, injects content.js
│   ├── content.js                  LinkedIn DOM automation (scrape, connect, message)
│   ├── popup/
│   │   ├── popup.html              Extension popup UI
│   │   ├── popup.css               Dark theme styles
│   │   └── popup.js                Status display + hint when server not running
│   └── icons/                      Extension icons (16, 48, 128px)
│
├── .claude/
│   ├── commands/
│   │   ├── discover.md             Step 1: Search and save profiles
│   │   ├── connect.md              Step 2: Send connections/InMails
│   │   └── message.md              Step 3: Message accepted connections
│   ├── scripts/
│   │   └── extension_client.js     Node.js HTTP bridge (auto-start, handshake, ping)
│   ├── skills/
│   │   └── linkedin-outreach/
│   │       └── SKILL.md            Unified skill definition
│   ├── templates/
│   │   └── linkedin/
│   │       ├── connection-note.md  Connection request note (300 char max)
│   │       ├── inmail-template.md  InMail template with subject line
│   │       └── messages/
│   │           ├── base_draft.md           Casual (2nd degree active posters)
│   │           ├── option_1_brand_invite.md Brand-forward (Founder/CEO/CTO)
│   │           ├── option_2_featured_voice.md Featured voice (VP/Director + AI)
│   │           ├── option_3_formal.md       Formal enterprise (CXO + large co)
│   │           ├── option_4_collaboration.md Collaboration (high followers)
│   │           └── option_5_future_facing.md Future-facing (scaling founders)
│   └── settings.local.json        Bash permissions for node scripts
│
├── output/
│   ├── profiles.json               Profile database (gitignored)
│   └── .limits.json                Rate limit tracking (gitignored)
│
├── CLAUDE.md                       Claude Code project instructions
├── README.md                       This file
└── package.json                    Project metadata (zero dependencies)
```

---

## Troubleshooting

**"EXTENSION_NOT_CONNECTED" error?**
- Make sure Chrome is open
- Go to `chrome://extensions` and verify "10X LinkedIn Outreach" is enabled
- Open `linkedin.com` in a tab

**"NOT_LOGGED_IN" error?**
- Open `linkedin.com` in Chrome and log in
- The skill auto-detects login status before running any command

**"CONTENT_SCRIPT_NOT_READY" error?**
- Press F5 on the LinkedIn tab to refresh it
- This happens rarely — the skill auto-re-injects content scripts

**CAPTCHA appeared?**
- Solve it manually in the browser
- Run the command again — it picks up where it left off

**Weekly limit reached?**
- LinkedIn caps at ~100 invitations per week
- Wait until next week, the skill stops automatically and saves progress

**Port 3456 already in use?**
- The skill auto-detects this and sends commands to the existing server
- Or kill it: `npx kill-port 3456` / `taskkill /F /PID <pid>` on Windows

---

## License

MIT License - Free to use, modify, and distribute.
