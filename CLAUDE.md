# 10x-Team Outreach System

A comprehensive multi-platform outreach automation system for Claude Code with a visual workflow canvas.

**Recent Improvements** (v2.0):
- ✅ Virtual environment support for isolated Python dependencies
- ✅ n8n-style connection deletion (hover to delete, branching support)
- ✅ Intelligent workflow naming with context (platform-nodes-timestamp)
- ✅ Workflow execution tracking and status management
- ✅ 60-second WebSocket polling (reduced from 500ms)
- ✅ API endpoints for workflow management

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for full details.

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
cd canvas && npm install
```

## Quick Start

**Say "start my app" or "/start" in Claude Code** - This automatically:
1. Installs dependencies (if needed)
2. Starts the visual canvas on http://localhost:3000
3. Opens the workflow designer

### Core Commands

| Command | Description |
|---------|-------------|
| `/start` | **Start the visual canvas app** |
| `/workflow create` | **Claude Code creates workflows visually in the canvas!** |
| `/workflow run` | Execute a saved workflow |
| `/discover` | Find people using Exa AI |
| `/outreach` | Email campaigns |
| `/compose` | Individual emails |
| `/inbox` | Check Gmail inbox |
| `/linkedin` | LinkedIn automation |
| `/twitter` | Twitter automation |
| `/instagram` | Instagram automation |
| `/canvas` | Visual workflow builder |
| `/team` | Manage team credentials |

## 10x-Team Visual Canvas

The visual workflow canvas powered by TLDraw for designing outreach workflows.

### Claude Code Creates Workflows Visually!

Say `/workflow create` and watch Claude Code build your workflow in real-time:

```
User: /workflow create for AI founders on LinkedIn and Twitter

Claude Code:
1. Asks about your target audience
2. Builds the workflow structure
3. Sends commands to canvas API
4. Canvas shows nodes appearing one-by-one!
5. Connections draw automatically

Watch at http://localhost:3000 as:
[Discovery] → [LinkedIn View] → [Like] → [Delay] → [Connect] → [Twitter Follow] → [Message]
```

### Canvas Features
- **Claude Code Integration**: Create workflows by talking to Claude!
- **Drag-to-connect**: Drag from green ▶ (output) to blue ◀ (input)
- **Auto-save**: Your work is automatically preserved
- **Export**: PNG, SVG, or save as .10x file
- **Simulate**: Watch your workflow execute step-by-step
- **Preview**: Highlight execution path before running
- **Templates**: Pre-built B2B, Brand, Influencer workflows

### How to Use the Canvas

1. **Add Nodes**: Click skill buttons in toolbar (Discovery, LinkedIn, etc.)
2. **Connect Nodes**: Drag from green output ▶ to blue input ◀
3. **Configure**: Click a node to set its options
4. **Preview**: Click 👁️ to highlight the execution path
5. **Simulate**: Click 🎬 to watch workflow run step-by-step
6. **Run**: Click ▶ Run to save workflow JSON
7. **Execute**: Say "/workflow run" in Claude Code

### Workflow JSON Output

When you click Run, the workflow is saved to:
- `workflow.json` - In project root (quick access)
- `output/workflows/latest.json` - Latest workflow
- `output/workflows/workflow-{timestamp}.json` - Timestamped backup

## Directory Structure

```
10x-Outreach-Skill/
├── .claude/                  # Skill code (portable)
│   ├── skills/               # Skill definitions
│   ├── commands/             # Slash commands
│   ├── scripts/              # Python automation scripts
│   ├── templates/            # Message templates
│   └── workflows/            # Workflow definitions
│
├── canvas/                   # Visual Workflow Canvas
│   ├── src/                  # React + TLDraw source
│   └── dist/                 # Production build
│
├── output/                   # Runtime output
│   ├── workflows/            # Saved workflows
│   ├── logs/                 # Execution logs
│   └── discovery/            # Discovered people
│
├── install.sh                # Unix installer
├── install.ps1               # Windows installer
└── CLAUDE.md                 # This file
```

## How It Works

1. **Visual Canvas** (TLDraw) - Design workflows visually
2. **Browser-Use MCP** - Handles social platform automation
3. **Gmail API** - Email sending with OAuth2
4. **Intelligent Rate Limiting** - Prevents spam/detection
5. **Single Approval** - Approve once, execute autonomously

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

### Browser-Use (for social platforms)
Browser-Use MCP is cloud-hosted via Claude Code - no local installation needed.

## Pre-Built Workflow Templates

| Template | Duration | Platforms |
|----------|----------|-----------|
| 💼 B2B Outreach | 14 days | LinkedIn + Email |
| 🤝 Brand Partnership | 21 days | Instagram + Twitter + Email |
| ⭐ Influencer Outreach | 21 days | Social + Pitch |
| 🌐 Multi-Platform | 30 days | All channels |

## Workflow Management API

### List All Workflows
```bash
curl http://localhost:3000/api/workflows
```
Returns all workflows sorted by creation date with metadata.

### Get Latest Workflow
```bash
curl http://localhost:3000/api/workflow/latest
```
Returns the most recently created workflow.

### Get Workflow by Name
```bash
curl http://localhost:3000/api/workflow/linkedin-twitter-5nodes-2026-01-22
```
Returns specific workflow with full metadata and execution history.

### Update Workflow Status
```bash
curl -X POST http://localhost:3000/api/workflow/workflow-name/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "executed": true,
    "executionResult": {
      "message": "Successfully executed",
      "stats": { "sent": 50, "failed": 0 }
    }
  }'
```

### Workflow Naming Format
Workflows are automatically named with context:
- Format: `{platforms}-{nodeCount}nodes-{timestamp}.json`
- Example: `linkedin-twitter-instagram-8nodes-2026-01-22T14-30-00.json`

This allows Claude Code to:
1. Identify workflow complexity (node count)
2. Understand platforms involved
3. Sort by creation time
4. Run most recent unexecuted workflow

### Workflow Status Values
- `pending` - Created but not executed
- `running` - Currently executing
- `completed` - Successfully finished
- `failed` - Execution failed

## MCP Tools Available

- `mcp__browser-use__browser_task` - Execute browser actions
- `mcp__browser-use__list_browser_profiles` - List authenticated profiles
- `mcp__browser-use__monitor_task` - Monitor task progress
- `mcp__browser-use__list_skills` - List available skills
- `mcp__browser-use__execute_skill` - Execute pre-built skills
- `mcp__browser-use__get_cookies` - Get authentication cookies

## License

MIT License - Free to use, modify, and distribute.
