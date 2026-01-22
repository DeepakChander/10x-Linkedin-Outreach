# 10x-Outreach-Skill - Multi-Platform Outreach System

A comprehensive multi-platform outreach automation system for Claude Code with intelligent canvas visualization.

**Developed by 10x.in**

---

## 🚨 IMPORTANT: Initial Setup Check

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
   # Run auto-setup
   python .claude/scripts/auto_setup.py
   ```

4. **After setup completes:**
   - File will be updated to "COMPLETE"
   - User can now use all skills
   - Statusline will appear in terminal

**DO NOT allow user to use skills until setup is complete!**

---

## 📦 What is 10x-Outreach-Skill?

A comprehensive multi-platform outreach automation system for Claude Code with:

**Recent Features** (v3.0):
- ✅ **Automatic setup on first initialization**
- ✅ **Intelligent canvas visualization** (CSV, research, workflows, LinkedIn profiles)
- ✅ **Multi-format export** (PDF, PPT, PNG, MD, TXT, etc.)
- ✅ **Custom statusline** (shows directory, git, model, session, context usage)
- ✅ **Exa AI integration** (semantic search, websets)
- ✅ **Workflow automation** (visual design → automatic execution)
- ✅ **Browser extension** (LinkedIn, Twitter, Instagram automation)

See [INTELLIGENT-CANVAS-ARCHITECTURE.md](INTELLIGENT-CANVAS-ARCHITECTURE.md) for full details.

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
| `/exa` | **Search the web with Exa AI semantic search** |
| `/websets` | **Create and manage curated web collections** |
| `/discover` | Find people using Exa AI |
| `/outreach` | Email campaigns |
| `/compose` | Individual emails |
| `/inbox` | Check Gmail inbox |
| `/linkedin` | LinkedIn automation |
| `/twitter` | Twitter automation |
| `/instagram` | Instagram automation |
| `/canvas` | Visual workflow builder |
| `/team` | Manage team credentials |

## TLDraw Canvas

A standalone, portable implementation of the official TLDraw SDK.

### Two Canvas Options

| Canvas | Purpose | Location |
|--------|---------|----------|
| **tldraw-canvas** | Clean, standalone TLDraw (recommended) | `./tldraw-canvas/` |
| **canvas** | Legacy API server (deprecated frontend) | `./canvas/` |

### Recommended: tldraw-canvas

The `tldraw-canvas` folder contains a **clean, portable** implementation using the **official TLDraw SDK** with zero custom modifications.

**Quick Start:**
```bash
cd tldraw-canvas
npm install
npm run dev
```

Opens at **http://localhost:3000**

### Features (Official TLDraw SDK)

- ✨ **Infinite Canvas** - Pan and zoom freely across unlimited space
- 🎨 **Drawing Tools** - Pen, highlighter, eraser
- 📐 **Shapes** - Rectangle, ellipse, arrow, line, text, and more
- 🖼️ **Media** - Embed images and videos
- 📋 **Copy/Paste** - Full clipboard support with fidelity
- ↩️ **Undo/Redo** - Complete history tracking
- 💾 **Export** - PNG, SVG, or JSON format
- 🔄 **Auto-Save** - Automatic persistence to localStorage
- 👥 **Multiplayer** - Real-time collaboration (optional)

### Basic Usage

1. **Draw & Write** - Use the toolbar to select tools
2. **Add Shapes** - Click shape buttons (rectangle, ellipse, arrow, etc.)
3. **Add Media** - Drag and drop images or videos
4. **Pan & Zoom** - Mouse drag to pan, scroll wheel to zoom
5. **Select & Transform** - Click to select, drag handles to resize
6. **Copy/Paste** - Ctrl+C / Ctrl+V (Cmd+C / Cmd+V on Mac)
7. **Undo/Redo** - Ctrl+Z / Ctrl+Shift+Z
8. **Export** - Menu → Export as PNG, SVG, or JSON

### Portable Design

The `tldraw-canvas` folder is designed to be **easily copied** to any other skill:

1. Copy the entire `tldraw-canvas` folder
2. Run `npm install` in the new location
3. Update port in `vite.config.ts` if needed
4. Run `npm run dev`

That's it! No configuration needed.

### TLDraw Resources

- Official Docs: https://tldraw.dev
- Quick Start: https://tldraw.dev/quick-start
- API Reference: https://tldraw.dev/api
- Examples: https://tldraw.dev/examples
- GitHub: https://github.com/tldraw/tldraw

## Directory Structure

```
10x-Outreach-Skill/
├── .claude/                  # Skill code (portable)
│   ├── skills/               # Skill definitions
│   ├── commands/             # Slash commands
│   ├── scripts/              # Python automation scripts
│   ├── templates/            # Message templates
│   ├── workflows/            # Workflow definitions
│   ├── hooks/                # Claude Code hooks
│   │   └── lib/              # Hook libraries (context-tracker, etc.)
│   ├── statusline.cjs        # Custom statusline (Node.js)
│   ├── statusline.ps1        # Custom statusline (PowerShell)
│   └── statusline.sh         # Custom statusline (Shell)
│
├── canvas/                   # Canvas API Server
│   ├── server.js             # WebSocket/HTTP API server
│   └── src/                  # Legacy custom canvas (deprecated)
│
├── tldraw-canvas/            # Standalone TLDraw (Official SDK)
│   ├── src/                  # Clean TLDraw implementation
│   │   ├── App.tsx           # Pure TLDraw component
│   │   ├── main.tsx          # React entry
│   │   └── index.css         # Styles
│   ├── package.json          # TLDraw dependencies
│   └── README.md             # Portable TLDraw docs
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

1. **Visual Canvas** (TLDraw) - Design workflows visually using the official TLDraw SDK
2. **10x-Browser Extension** - Handles social platform automation via ClaudeKit Browser Extension
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

### 10x-Browser Extension (for social platforms)
The ClaudeKit Browser Extension handles automation for LinkedIn, Twitter, and Instagram.
Located at: `C:\Users\Anit\Downloads\10x-Browser Extension`

## Pre-Built Workflow Templates

| Template | Duration | Platforms |
|----------|----------|-----------|
| 💼 B2B Outreach | 14 days | LinkedIn + Email |
| 🤝 Brand Partnership | 21 days | Instagram + Twitter + Email |
| ⭐ Influencer Outreach | 21 days | Social + Pitch |
| 🌐 Multi-Platform | 30 days | All channels |


## Browser Extension Integration

The 10x-Outreach System integrates with the ClaudeKit Browser Extension for social platform automation:

- **LinkedIn Actions** - Connect, message, view profiles, like, comment
- **Twitter Actions** - Follow, DM, like, reply, retweet
- **Instagram Actions** - Follow, DM, like, comment, story replies

Extension path: `C:\Users\Anit\Downloads\10x-Browser Extension`

## License

MIT License - Free to use, modify, and distribute.
