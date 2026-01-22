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

1. **TLDraw Canvas** - Official TLDraw SDK providing an infinite canvas for design and collaboration
2. **13 Automation Skills** - LinkedIn, Twitter, Instagram, Gmail automation via ClaudeKit Browser Extension
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

**What the installer does:**
- ✅ Checks for Node.js & Python
- ✅ Installs all dependencies (npm & pip)
- ✅ Runs interactive setup wizard for API keys
- ✅ Creates workspace directories
- ✅ Sets up browser extension

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/Anit-1to10x/10x-outreach-skill.git
cd 10x-outreach-skill

# Install dependencies
cd canvas && npm install && cd ..
pip install -r requirements.txt

# Run interactive setup wizard
node setup.js
```

### Requirements

- **Node.js 18+** - [Download](https://nodejs.org/)
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads)

### Configuration

After installation, you'll be guided through an **interactive setup wizard** that collects:

**Required:**
- 🔑 Exa AI API Key (prospect enrichment)
- 🔑 Google OAuth credentials (Gmail integration)
- 📧 Sender email address

**Optional:**
- 🤖 Gemini AI API Key (multimodal features)
- 🎨 Canva credentials (design automation)
- 🧠 Anthropic API Key (advanced AI features)

**To reconfigure later:**
```bash
node setup.js
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

## 🎨 TLDraw Canvas

An infinite canvas powered by the official **TLDraw SDK** for visual design and collaboration.

### Canvas Features (Official TLDraw SDK)

| Feature | Description |
|---------|-------------|
| **Infinite Canvas** | Pan and zoom freely across unlimited space |
| **Drawing Tools** | Draw, write, add shapes, images, and videos |
| **Selection & Transform** | Click to select, drag to multi-select, transform shapes |
| **Copy/Paste** | Standard clipboard operations with full fidelity |
| **Undo/Redo** | Complete history tracking of all changes |
| **Export** | Export as PNG, SVG, or JSON snapshot |
| **Auto-Save** | Automatic persistence to localStorage |
| **Programmatic Control** | Full API access via Editor instance |

### Basic TLDraw Usage

The canvas runs at **http://localhost:3000** with the standard TLDraw interface:

1. **Draw & Write** - Use toolbar to select drawing tools
2. **Add Shapes** - Rectangle, ellipse, arrow, line, text, etc.
3. **Add Media** - Embed images and videos
4. **Pan & Zoom** - Mouse drag to pan, scroll to zoom
5. **Selection** - Click to select, drag to multi-select
6. **Copy/Paste** - Standard keyboard shortcuts work
7. **Undo/Redo** - Full history support

### Export Options

- **PNG** - Raster image export
- **SVG** - Vector export for scalability
- **JSON** - Full snapshot for persistence and sharing

---

## 📋 Commands

### Core Commands

| Command | Description |
|---------|-------------|
| `/start` | **Start the visual canvas** on localhost:3000 |
| `/canvas` | Open the workflow canvas |
| `/workflow` | Create and run multi-platform workflows |
| `/exa` | **Search the web with Exa AI semantic search** |
| `/websets` | **Create and manage curated web collections** |

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

### Discovery & Management Commands

| Command | Description |
|---------|-------------|
| `/discover` | Find people using Exa AI |
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

- **Node.js 18+** (for the TLDraw canvas)
- **Claude Code**
- **Python 3.9+** (optional, for advanced scripts)
- **10x-Browser Extension** (ClaudeKit Browser Extension at `C:\Users\Anit\Downloads\10x-Browser Extension`)

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
│  │              10x-BROWSER EXTENSION (ClaudeKit)                 │ │
│  │            C:\Users\Anit\Downloads\10x-Browser Extension       │ │
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
├── canvas/                    # TLDraw Canvas (Official SDK)
│   ├── src/
│   │   ├── App.tsx            # Clean TLDraw implementation
│   │   ├── index.css          # Styles
│   │   └── main.tsx           # Entry point
│   └── package.json           # Dependencies (tldraw, react)
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


## 🔧 10x-Browser Extension Integration

The ClaudeKit Browser Extension handles social platform automation for LinkedIn, Twitter, and Instagram.

### Extension Location

`C:\Users\Anit\Downloads\10x-Browser Extension`

### Supported Actions

| Platform | Actions |
|----------|---------|
| **LinkedIn** | Connect, message, view profiles, like posts, comment |
| **Twitter** | Follow, DM, like tweets, reply, retweet |
| **Instagram** | Follow, DM, like posts, comment, story replies |

### How It Works

1. Install the ClaudeKit Browser Extension in your browser
2. The extension receives commands from the 10x-Outreach System
3. Extension performs actions on LinkedIn, Twitter, Instagram
4. Results are sent back to the system for tracking

---

## 🐛 Troubleshooting

### Canvas not starting?

```bash
cd canvas && npm install && npm run dev -- --port 3000
```

### Browser Extension not working?

1. Verify the extension is installed in your browser
2. Check that the extension path is correct: `C:\Users\Anit\Downloads\10x-Browser Extension`
3. Ensure you're logged into LinkedIn/Twitter/Instagram in your browser

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
