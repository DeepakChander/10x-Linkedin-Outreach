# 10X LinkedIn Outreach

Focused LinkedIn outreach automation for Claude Code. Three commands, one workflow.

**Built by [1to10x.in](https://1to10x.in)**

---

## Setup

1. Open Chrome -> `chrome://extensions` -> Enable Developer Mode
2. Click "Load unpacked" -> select the `extension/` folder
3. Log into LinkedIn in Chrome
4. Badge shows "ON" when server is running

## Commands

| Command | What it does |
|---------|-------------|
| `/discover` | Search LinkedIn by filters, save profiles |
| `/connect` | Send connection requests + InMails |
| `/message` | Message accepted connections |

## Workflow

```
/discover -> profiles saved -> /connect -> requests sent -> /message -> conversations started
```

Each command reads/writes `output/profiles.json`. Run them in order.

## How It Works

```
Claude Code -> node extension_client.js <command>
-> HTTP localhost:3456 -> Chrome extension polls
-> content.js automates LinkedIn DOM
-> Result flows back to Claude
```

## Profile Lifecycle

```
discovered -> connection_sent -> accepted -> message_sent
                              -> pending -> cold (7d) -> archived (14d)
           -> inmail_sent
           -> already_connected
           -> declined
           -> profile_not_found
```

## Rate Limits

| Action | Daily Limit |
|--------|------------|
| Connections | 20 |
| InMails | 10 (50/month) |
| Messages | 40 |
| Profile scrapes | 100 |

Delays: 2-5 min between connections, 30-60s between messages.

## Template Selection

| Condition | Template |
|-----------|----------|
| CXO/Director + company >200 | Formal |
| Founder + "building/scaling" + company <200 | Future-facing |
| Founder/CEO/CTO | Brand invite |
| 5000+ followers or creator/speaker | Collaboration |
| VP/Director + AI/growth posts | Featured voice |
| 2nd degree + active poster | Base draft |

## File Structure

```
├── extension/              Chrome extension
│   ├── manifest.json
│   ├── background.js       Polls server, routes commands
│   ├── content.js          LinkedIn DOM automation
│   └── popup/              Extension popup UI
├── .claude/
│   ├── commands/           3 slash commands
│   ├── scripts/            extension_client.js (Node.js bridge)
│   ├── skills/             Skill definition
│   └── templates/          8 message templates
├── output/
│   ├── profiles.json       Profile database
│   └── .limits.json        Rate limit tracking
└── CLAUDE.md               This file
```
