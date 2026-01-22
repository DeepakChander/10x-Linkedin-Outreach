# 10x Outreach Skill

<div align="center">

**Visual Workflow Canvas + Multi-Platform Outreach Automation for Claude Code**

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet?style=for-the-badge)](https://claude.ai/code)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platforms](https://img.shields.io/badge/Platforms-LinkedIn%20%7C%20Twitter%20%7C%20Instagram%20%7C%20Gmail-blue?style=for-the-badge)](#)

[Installation](#-one-line-installation) • [Quick Start](#-quick-start) • [Visual Canvas](#-visual-workflow-canvas) • [Commands](#-commands) • [Templates](#-templates)

</div>

---

## What is This?

**10x Outreach Skill** is a Claude Code skill that gives you:

1. **Visual Workflow Canvas** - A drag-and-drop infinite canvas (powered by TLDraw) to design multi-platform outreach workflows
2. **13 Automation Skills** - LinkedIn, Twitter, Instagram, Gmail automation with intelligent rate limiting
3. **85+ Message Templates** - Professional, customizable templates for all platforms
4. **Team Management** - Multiple team members with their own credentials

---

## 🚀 One-Line Installation

### macOS / Linux
```bash
curl -fsSL https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.ps1 | iex
```

### Manual Installation
```bash
git clone https://github.com/Anit-1to10x/10x-outreach-skill.git
cd 10x-outreach-skill
cd canvas && npm install
```

---

## ⚡ Quick Start

### Step 1: Start the Visual Canvas

Open Claude Code in any project directory and say:

```
start my app
```

Or use the slash command:

```
/start
```

This automatically:
- Installs dependencies (if needed)
- Starts the visual canvas on **http://localhost:3000**
- Opens the workflow designer in your browser

### Step 2: Design Your Workflow

1. **Add Nodes** - Click skill buttons in the toolbar (Discovery, LinkedIn, Twitter, etc.)
2. **Connect Nodes** - Drag from green **▶** (output) to blue **◀** (input)
3. **Configure** - Click any node to set its options
4. **Run** - Click the Run button to export your workflow

### Step 3: Execute Your Workflow

```
/workflow run
```

Claude Code reads the workflow JSON and executes each step with intelligent delays.

---

## 🎨 Visual Workflow Canvas

The canvas is an infinite workspace powered by **TLDraw** where you design outreach sequences visually.

### Canvas Features

| Feature | Description |
|---------|-------------|
| **Claude Code Integration** | Claude Code can create workflows visually in real-time! |
| **Drag-to-Connect** | Drag from green ▶ to blue ◀ to connect nodes |
| **Auto-Save** | Your work is automatically saved to localStorage |
| **Export PNG/SVG** | Export your workflow as an image |
| **Save as .10x** | Save/load workflows as portable files |
| **Preview Mode** | Highlight the execution path before running |
| **Simulation** | Watch your workflow execute step-by-step |
| **Workflow Templates** | Pre-built B2B, Brand, Influencer workflows |

### Claude Code Creates Workflows Visually

When you say `/workflow create`, Claude Code will:
1. Ask about your target audience and platforms
2. Build the workflow JSON
3. Send commands to the canvas API
4. **Watch nodes appear one-by-one on the canvas!**
5. Connections draw automatically between nodes

```
User: /workflow create for AI founders on LinkedIn

Claude Code builds visually:
[Discovery] → [View Profile] → [Like Post] → [Delay] → [Connect] → [Message]
```

### Node Types

| Node | Color | Purpose |
|------|-------|---------|
| **Discovery** | Purple | Find people with Exa AI |
| **LinkedIn** | Blue | Connect, message, engage |
| **Twitter** | Sky Blue | Follow, DM, reply, retweet |
| **Instagram** | Pink | Follow, DM, comment, stories |
| **Email** | Green | Send emails via Gmail |
| **Delay** | Gray | Wait between actions |
| **Condition** | Yellow | Branch based on response |

### How Connections Work

```
[Discovery] ──▶ [LinkedIn Connect] ──▶ [Delay 24h] ──▶ [LinkedIn Message]
                                                              │
                                                              ▼
                                              [Email Follow-up] ◀── [Condition: No Response]
```

When you click **Run**, the canvas generates a `workflow.json` file:

```json
{
  "name": "My Outreach Workflow",
  "steps": [
    { "step": 1, "skill": "discovery", "config": { "query": "AI founders" } },
    { "step": 2, "skill": "linkedin", "action": "connect" },
    { "step": 3, "skill": "delay", "hours": 24 },
    { "step": 4, "skill": "linkedin", "action": "message" }
  ],
  "connections": [...]
}
```

---

## 📋 Commands

### Core Commands

| Command | Description |
|---------|-------------|
| `/start` | **Start the visual canvas** on localhost:3000 |
| `/canvas` | Open the workflow canvas |
| `/workflow` | Create and run multi-platform workflows |

### Platform Commands

| Command | Description |
|---------|-------------|
| `/linkedin` | LinkedIn actions (connect, message, like, comment) |
| `/twitter` | Twitter actions (follow, DM, like, reply, retweet) |
| `/instagram` | Instagram actions (follow, DM, like, comment, story) |

### Email Commands

| Command | Description |
|---------|-------------|
| `/outreach` | Email campaigns from Google Sheets |
| `/compose` | Write individual emails |
| `/inbox` | Read and search Gmail |
| `/reply` | Reply to emails |
| `/summarize` | Get email digests |

### Management Commands

| Command | Description |
|---------|-------------|
| `/discover` | Find people with Exa AI |
| `/team` | Manage team members and credentials |

---

## 🛠 Skills

The skill includes **13 automation skills**:

| Skill | File | Description |
|-------|------|-------------|
| `start-app` | Start the visual canvas |
| `canvas-workflow` | Visual workflow designer |
| `discovery-engine` | Find people with Exa AI |
| `linkedin-adapter` | LinkedIn automation |
| `twitter-adapter` | Twitter automation |
| `instagram-adapter` | Instagram automation |
| `gmail-adapter` | Gmail sending |
| `outreach-manager` | Email campaigns |
| `email-composer` | Individual emails |
| `inbox-reader` | Read Gmail |
| `reply-generator` | Generate replies |
| `email-summarizer` | Email digests |
| `team-manager` | Team credentials |
| `workflow-engine` | Multi-platform sequences |

---

## 📝 Templates

**85+ pre-built templates** across 4 platforms:

| Platform | Count | Categories |
|----------|-------|------------|
| **LinkedIn** | 24 | Connection requests, Messages, InMails, Comments |
| **Twitter** | 22 | DMs, Replies, Tweets, Quote tweets |
| **Instagram** | 22 | DMs, Comments, Story replies |
| **Email** | 18 | Outreach, Follow-ups, Newsletters, Promotional |

### Using Templates

Templates use `{{variables}}` for personalization:

```markdown
Hi {{first_name}},

I saw your work on {{topic}} and thought it was impressive.
Would love to connect and learn more about {{company}}.

Best,
{{sender_name}}
```

---

## 🔄 Pre-Built Workflows

Located in `.claude/workflows/examples/`:

| Workflow | Duration | Platforms | Use Case |
|----------|----------|-----------|----------|
| **B2B Professional** | 14 days | LinkedIn + Email | Business outreach |
| **Brand Outreach** | 21 days | Instagram + Twitter + Email | Brand partnerships |
| **Influencer** | 21 days | Twitter + Instagram | Content creators |
| **Investor** | 28 days | Twitter + LinkedIn + Email | Fundraising |
| **Multi-Platform** | 30 days | All | Adaptive routing |

---

## ⚙️ Setup

### Requirements

- **Node.js 18+** (for the visual canvas)
- **Claude Code** (with Browser-Use MCP access)
- **Python 3.9+** (optional, for advanced scripts)

### Environment Variables

Create a `.env` file:

```env
# Gmail OAuth2 (for email features)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_secret
SENDER_EMAIL=your@gmail.com
SENDER_NAME=Your Name

# Exa AI (for discovery)
EXA_API_KEY=your_exa_key

# Rate Limits (optional)
LINKEDIN_CONNECTIONS_PER_DAY=20
TWITTER_FOLLOWS_PER_DAY=50
INSTAGRAM_FOLLOWS_PER_DAY=30
```

### Gmail Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop App)
5. Add credentials to `.env`
6. Run `/outreach` to authenticate

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     10x OUTREACH SKILL                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              VISUAL WORKFLOW CANVAS (TLDraw)                   │ │
│  │         http://localhost:3000 - Drag & Drop Designer           │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│                              ▼                                       │
│                     workflow.json                                    │
│                              │                                       │
│                              ▼                                       │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────────────┐ │
│  │   DISCOVERY   │   │   WORKFLOW    │   │    TEAM MANAGER       │ │
│  │   (Exa AI)    │──▶│    ENGINE     │◀──│  (Multi-user creds)   │ │
│  └───────────────┘   └───────────────┘   └───────────────────────┘ │
│                              │                                       │
│         ┌────────────────────┼────────────────────┐                 │
│         ▼                    ▼                    ▼                  │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │  LINKEDIN   │     │   TWITTER   │     │  INSTAGRAM  │           │
│  │   ADAPTER   │     │   ADAPTER   │     │   ADAPTER   │           │
│  └─────────────┘     └─────────────┘     └─────────────┘           │
│         │                    │                    │                  │
│         └────────────────────┼────────────────────┘                 │
│                              ▼                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │           BROWSER-USE MCP (Cloud-Hosted via Claude)            │ │
│  │              No local browser installation needed               │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────────────┐ │
│  │     RATE      │   │    TEMPLATE   │   │       GMAIL           │ │
│  │    LIMITER    │   │     LOADER    │   │       CLIENT          │ │
│  └───────────────┘   └───────────────┘   └───────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
10x-outreach-skill/
├── canvas/                    # Visual Workflow Canvas
│   ├── src/
│   │   ├── App.tsx            # Main app with auto-save
│   │   ├── nodes/             # Custom TLDraw shapes
│   │   │   └── SkillNodeShapeUtil.tsx
│   │   ├── connection/        # Connection lines
│   │   │   └── ConnectionShapeUtil.tsx
│   │   └── components/
│   │       ├── WorkflowToolbar.tsx
│   │       ├── ExportControls.tsx
│   │       └── ConnectionDragger.tsx
│   └── package.json
│
├── .claude/                   # Claude Code Skill
│   ├── skills/                # 13 skill definitions
│   ├── commands/              # Slash commands
│   ├── scripts/               # Python automation
│   ├── templates/             # 85+ message templates
│   └── workflows/             # Workflow definitions
│
├── output/                    # Runtime output
│   └── workflows/             # Saved workflow JSONs
│
├── install.sh                 # Unix installer
├── install.ps1                # Windows installer
├── CLAUDE.md                  # Claude Code instructions
└── README.md                  # This file
```

---

## 🛡 Safety & Rate Limiting

### Touch Limits (Per Person)

| Target | Max/Day | Max/Week | Total | Cool-Off |
|--------|---------|----------|-------|----------|
| Person | 2 | 5 | 8 | 7 days |
| Brand | 1 | 3 | 6 | 14 days |
| Influencer | 1 | 2 | 5 | 14 days |
| Executive | 1 | 2 | 4 | 21 days |

### Platform Rate Limits

| Platform | Action | Daily Limit | Delay |
|----------|--------|-------------|-------|
| LinkedIn | Connections | 20 | 2-10 min |
| LinkedIn | Messages | 50 | 2-10 min |
| Twitter | Follows | 50 | 1-5 min |
| Twitter | DMs | 50 | 1-5 min |
| Instagram | Follows | 30 | 1.5-7 min |
| Instagram | DMs | 30 | 1.5-7 min |
| Gmail | Emails | 100 | 1-3 min |

### Key Principles

- **Never spam** - Max 2 touches per day per person
- **Warm-up first** - Follow and engage BEFORE sending DMs
- **Platform gaps** - Wait 24+ hours between platforms
- **Stop on response** - Immediately pause when they reply
- **Human-like delays** - Randomized timing to avoid detection

---

## 🔌 Canvas API (For Developers)

The canvas exposes a REST API that Claude Code uses to create workflows visually.

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/canvas/status` | GET | Check if canvas is running |
| `/api/canvas/workflow` | POST | Create a complete workflow with nodes and connections |
| `/api/canvas/command` | POST | Send a single command (add-node, add-connection, clear) |
| `/api/canvas/commands` | GET | Poll for pending commands |

### Example: Create Workflow via API

```bash
curl -X POST http://localhost:3000/api/canvas/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Workflow",
    "nodes": [
      {"id": "n1", "skill": "discovery", "label": "Find People"},
      {"id": "n2", "skill": "linkedin", "label": "Connect"}
    ],
    "connections": [
      {"from": "n1", "to": "n2"}
    ]
  }'
```

### Python Client

```python
from canvas_client import create_workflow, add_node, check_canvas_status

# Check if canvas is running
status = check_canvas_status()

# Create a B2B workflow
create_b2b_workflow()

# Or create custom
create_workflow({
    "nodes": [...],
    "connections": [...]
})
```

---

## 🔧 Browser-Use MCP

Browser-Use MCP is **cloud-hosted via Claude Code** - no local installation needed.

### Available Tools

| Tool | Description |
|------|-------------|
| `mcp__browser-use__browser_task` | Execute browser automation |
| `mcp__browser-use__list_browser_profiles` | List authenticated profiles |
| `mcp__browser-use__monitor_task` | Monitor task progress |
| `mcp__browser-use__list_skills` | List available skills |
| `mcp__browser-use__execute_skill` | Execute pre-built skills |
| `mcp__browser-use__get_cookies` | Get authentication cookies |

### Authentication Flow

1. Run any platform command (e.g., `/linkedin connect`)
2. Browser opens for you to log in manually
3. Session is saved in cloud profile
4. Future actions use saved session

---

## 🐛 Troubleshooting

### Canvas not starting?

```bash
cd canvas && npm install && npm run dev -- --port 3000
```

### Browser not authenticating?

1. Run `mcp__browser-use__list_browser_profiles`
2. If no profiles, run a simple action to trigger login
3. Log in manually when browser opens

### Gmail issues?

1. Check OAuth2 credentials in `.env`
2. Run `/outreach` to re-authenticate
3. Verify token hasn't expired

---

## 📄 License

MIT License - Free to use, modify, and distribute.

---

<div align="center">

**Built with Claude Code**

[Report Bug](https://github.com/Anit-1to10x/10x-outreach-skill/issues) • [Request Feature](https://github.com/Anit-1to10x/10x-outreach-skill/issues)

</div>
