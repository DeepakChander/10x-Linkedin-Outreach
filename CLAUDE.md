# 10x-Outreach-Skill - Multi-Platform Outreach System

A comprehensive multi-platform outreach automation system for Claude Code with intelligent canvas visualization.

**Developed by 10x.in**

---

## IMPORTANT: Initial Setup Check

**BEFORE doing anything else, you MUST check if initial setup is complete.**

### Setup Detection Protocol

1. **Read the setup status file:**
   ```
   Read file: .claude/SETUP_CHECK.md
   ```

2. **Check if setup is complete:**
   - If file contains "COMPLETE" → Setup is done, proceed normally
   - If file contains "NOT COMPLETE" → Setup required, run auto-setup

3. **If setup is NOT complete:**
   ```python
   python .claude/scripts/auto_setup.py
   ```

4. **After setup completes:**
   - File will be updated to "COMPLETE"
   - User can now use all skills
   - Statusline will appear in terminal

**DO NOT allow user to use skills until setup is complete!**

---

## What is 10x-Outreach-Skill?

A complete agency-in-a-box — every role a 20-person outreach team would fill, automated through Claude Code skills:

- **Discovery & Research** — Exa AI semantic search, websets, LinkedIn search
- **Outreach & Campaigns** — Email, LinkedIn, Twitter, Instagram automation
- **CRM & Pipeline** — Contact database, deal stages, follow-ups
- **Project Management** — Task board, sprints, standups, milestones
- **QA & Compliance** — CAN-SPAM/GDPR checks, spam scoring, brand voice
- **Support & Tickets** — SLA tracking, knowledge base, auto-routing
- **Integrations** — Webhooks, audit logging, external systems
- **Access Control** — RBAC, multi-tenant, credential vault
- **Visual Canvas** — Infinite canvas for workflow design and visualization
- **Analytics** — Campaign metrics, engagement reports

## Installation

### Quick Install (curl)

**macOS/Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.ps1 | iex
```

### Manual Install
```bash
git clone https://github.com/Anit-1to10x/10x-outreach-skill.git
cd 10x-outreach-skill
cd tldraw-canvas && npm install
```

## Quick Start

**Say "start my app" or "/start" in Claude Code** - This automatically:
1. Installs dependencies (if needed)
2. Starts the visual canvas on http://localhost:3000
3. Opens the workflow designer

## All Commands

| Command | Role | Description |
|---------|------|-------------|
| `/start` | — | Start the visual canvas app |
| `/discover` | Discovery Lead | Find people using Exa AI |
| `/exa` | Exa Research | Semantic web search with Exa AI |
| `/websets` | Websets Manager | Curated web collections |
| `/accounts` | Account Manager | CRM contacts, deals, pipeline, follow-ups |
| `/project` | Project Manager | Task board, sprints, standups, milestones |
| `/content` | Content Marketer | Blog posts, social content, content calendars |
| `/seo` | SEO Specialist | Keyword research, competitor analysis, audits |
| `/compose` | Email Planner | Compose individual emails |
| `/outreach` | Campaign Manager | Bulk email campaigns from Google Sheets |
| `/inbox` | Inbox Manager | Read and search Gmail inbox |
| `/reply` | Reply Writer | Generate and send email replies |
| `/summarize` | Email Summarizer | Email digests and summaries |
| `/linkedin` | LinkedIn Specialist | LinkedIn automation via extension |
| `/twitter` | Twitter Specialist | Twitter automation via extension |
| `/instagram` | Instagram Specialist | Instagram automation via extension |
| `/qa` | QA / Compliance | Pre-send review, CAN-SPAM/GDPR, brand voice |
| `/ticket` | Support Manager | Support tickets with SLA tracking |
| `/ops` | Ops Manager | System health, logs, cleanup, backup |
| `/analytics` | Analytics Lead | Campaign metrics and reports |
| `/access` | Access Manager | RBAC, multi-tenant, credential vault |
| `/integrations` | Integration Manager | Data sync, import/export, service connections |
| `/verify` | Email Verifier | Email validation (MX, SPF, DKIM, DMARC) |
| `/canvas` | Canvas Designer | Visual infinite canvas |
| `/team` | Team Manager | Team member credentials |
| `/workflow` | Workflow Engine | Multi-step, multi-platform workflows |
| `/lookback` | Lookback | LinkedIn profile lookback |

## Canvas

The `tldraw-canvas` folder contains a portable infinite canvas for visual workflow design.

**Quick Start:**
```bash
cd tldraw-canvas
npm install
npm run dev
```

Opens at **http://localhost:3000**

### Features
- Infinite canvas — pan and zoom freely
- Drawing tools — pen, highlighter, eraser
- Shapes — rectangle, ellipse, arrow, line, text
- Media — embed images and videos
- Export — PNG, SVG, or JSON
- Auto-save — persistence to localStorage

## Directory Structure

```
10x-Outreach-Skill/
├── .claude/                  # Skill code (portable)
│   ├── skills/               # Skill definitions (22 skills)
│   ├── commands/             # Slash commands (27 commands)
│   ├── agents/               # Autonomous agents (6 agents)
│   ├── scripts/              # Python automation scripts (40+ scripts)
│   ├── templates/            # Message templates
│   ├── workflows/            # Workflow definitions
│   ├── hooks/                # Claude Code hooks
│   ├── mcp.json              # MCP server config + skill registry
│   └── statusline.*          # Custom statusline
│
├── tldraw-canvas/            # Visual canvas
│   ├── src/                  # Canvas implementation
│   ├── package.json          # Dependencies
│   └── README.md             # Canvas docs
│
├── browser-extension/        # Browser extension for social platforms
│
├── output/                   # Runtime output
│   ├── workflows/            # Saved workflows
│   ├── logs/                 # Execution logs
│   ├── discovery/            # Discovered people
│   ├── accounts/             # CRM data
│   ├── projects/             # Project/task data
│   ├── qa/                   # QA reviews
│   └── tickets/              # Support tickets
│
├── install.sh                # Unix installer
├── install.ps1               # Windows installer
└── CLAUDE.md                 # This file
```

## How It Works

1. **Visual Canvas** — Design workflows visually on the infinite canvas
2. **Browser Extension** — Handles social platform automation (LinkedIn, Twitter, Instagram)
3. **Gmail API** — Email sending with OAuth2
4. **Intelligent Rate Limiting** — Prevents spam/detection
5. **Single Approval** — Approve once, execute autonomously

## Professional Outreach Rules

### Touch Limits (Per Person)
| Target Type | Max/Day | Max/Week | Total Max | Cool-Off |
|-------------|---------|----------|-----------|----------|
| Person | 2 | 5 | 8 | 7 days |
| Brand | 1 | 3 | 6 | 14 days |
| Influencer | 1 | 2 | 5 | 14 days |
| Executive | 1 | 2 | 4 | 21 days |

### Platform Delays
| Platform | Between DMs | After Follow |
|----------|-------------|--------------|
| LinkedIn | 24-48 hours | 24 hours |
| Twitter | 24-48 hours | 4-24 hours |
| Instagram | 48-72 hours | 24-48 hours |

### Key Rules
- NEVER message same person more than 2x per day
- NEVER DM without warm-up first (follow, like, engage)
- ALWAYS wait 24+ hours between platforms
- STOP immediately when response received

## Setup Requirements

### Gmail (for email features)
Add to `.env`:
```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
SENDER_EMAIL=your@gmail.com
SENDER_NAME=Your Name
```

### Browser Extension (for social platforms)
The browser extension handles automation for LinkedIn, Twitter, and Instagram.
Install from the `browser-extension/` folder.

## Pre-Built Workflow Templates

| Template | Duration | Platforms |
|----------|----------|-----------|
| B2B Outreach | 14 days | LinkedIn + Email |
| Brand Partnership | 21 days | Instagram + Twitter + Email |
| Influencer Outreach | 21 days | Social + Pitch |
| Multi-Platform | 30 days | All channels |

## License

MIT License - Free to use, modify, and distribute.
