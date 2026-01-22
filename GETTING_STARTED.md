# Getting Started with 10x Outreach Skill

Welcome! This guide will help you set up the **10x Outreach Skill** - a visual workflow canvas for multi-platform outreach automation powered by Claude Code.

---

## What You'll Get

- **Visual Workflow Canvas** - Drag-and-drop interface to design outreach workflows
- **Claude Code Integration** - Claude can create workflows visually in real-time!
- **Multi-Platform Automation** - LinkedIn, Twitter, Instagram, Gmail
- **85+ Message Templates** - Professional, customizable templates
- **Intelligent Rate Limiting** - Avoid spam and detection

---

## Quick Start (2 Minutes)

### Step 1: Install with One Command

Open your terminal and run:

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.sh | bash
```

**Windows (PowerShell as Administrator):**
```powershell
irm https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.ps1 | iex
```

This will:
- Clone the repository
- Install dependencies
- Set up Claude Code integration

### Step 2: Open Claude Code

Navigate to your project directory and start Claude Code:

```bash
cd ~/.claude-skills/10x-outreach
claude
```

Or if you set up in your current directory during installation:
```bash
claude
```

### Step 3: Start the Visual Canvas

In Claude Code, simply say:

```
start my app
```

Or use the slash command:
```
/start
```

### Step 4: Open Your Browser

Go to **http://localhost:3000** to see the visual workflow canvas!

---

## Manual Installation (Alternative)

If the one-liner doesn't work, install manually:

```bash
# Clone the repository
git clone https://github.com/Anit-1to10x/10x-outreach-skill.git

# Navigate to the directory
cd 10x-outreach-skill

# Install canvas dependencies
cd canvas && npm install

# Go back to root
cd ..

# Start Claude Code
claude
```

Then say `/start` to launch the canvas.

---

## Using the Visual Canvas

### Adding Nodes

Click the skill buttons in the toolbar:
- **Discovery** (purple) - Find people with Exa AI
- **LinkedIn** (blue) - Connect, message, engage
- **Twitter** (sky blue) - Follow, DM, reply
- **Instagram** (pink) - Follow, DM, comment
- **Email** (green) - Send emails via Gmail
- **Delay** (gray) - Wait between actions

### Connecting Nodes

1. Look for the **green ▶** (output) on the right side of a node
2. Look for the **blue ◀** (input) on the left side of another node
3. **Drag** from green to blue to connect them!

### Let Claude Code Build Your Workflow!

In Claude Code, say:
```
/workflow create for AI founders on LinkedIn
```

Watch the canvas as Claude Code:
1. Asks about your target audience
2. Builds the workflow structure
3. **Nodes appear one-by-one on the canvas!**
4. Connections draw automatically

### Running Your Workflow

1. Click the **▶ Run** button in the canvas toolbar
2. Or say `/workflow run` in Claude Code

---

## Available Commands

| Command | What It Does |
|---------|--------------|
| `/start` | Start the visual canvas on localhost:3000 |
| `/workflow create` | Claude creates a workflow visually |
| `/workflow run` | Execute your saved workflow |
| `/discover` | Find people using Exa AI |
| `/linkedin` | LinkedIn automation |
| `/twitter` | Twitter automation |
| `/instagram` | Instagram automation |
| `/outreach` | Email campaigns |
| `/inbox` | Check Gmail inbox |
| `/team` | Manage team credentials |

---

## Setting Up Email (Optional)

To use Gmail features, create a `.env` file:

```bash
# In the project root
cp .env.example .env
```

Then edit `.env` with your Gmail OAuth2 credentials:

```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
SENDER_EMAIL=your@gmail.com
SENDER_NAME=Your Name
```

### Getting Gmail Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop App)
5. Copy the Client ID and Client Secret to `.env`

---

## Setting Up Exa AI (Optional)

For the discovery feature, add your Exa API key to `.env`:

```env
EXA_API_KEY=your_exa_api_key
```

Get your API key at [exa.ai](https://exa.ai)

---

## Troubleshooting

### Canvas not starting?

```bash
cd canvas && npm install && npm run dev -- --port 3000
```

### Port 3000 already in use?

```bash
# Find what's using port 3000
lsof -i :3000

# Or use a different port
cd canvas && npm run dev -- --port 3001
```

### Node.js not installed?

Install Node.js 18+ from [nodejs.org](https://nodejs.org/)

### Git not installed?

- **macOS:** `brew install git`
- **Windows:** Download from [git-scm.com](https://git-scm.com/)
- **Linux:** `sudo apt install git`

---

## Example Workflow

Here's a sample B2B outreach workflow:

```
[Discovery: Find AI Founders]
        ↓
[LinkedIn: View Profile]
        ↓
[LinkedIn: Like Recent Post]
        ↓
[Delay: Wait 24 Hours]
        ↓
[LinkedIn: Send Connection Request]
        ↓
[Delay: Wait 48 Hours]
        ↓
[LinkedIn: Send Introduction Message]
        ↓
[Email: Follow-up if No Response]
```

Claude Code can build this for you automatically! Just say:
```
/workflow create for B2B outreach to AI founders
```

---

## Need Help?

- **Documentation:** Check `README.md` and `CLAUDE.md` in the project
- **Issues:** [GitHub Issues](https://github.com/Anit-1to10x/10x-outreach-skill/issues)
- **In Claude Code:** Type `/help` or ask Claude any question!

---

## Quick Reference

| What You Want | What To Say/Do |
|---------------|----------------|
| Start the app | `/start` or "start my app" |
| Create a workflow | `/workflow create for [target]` |
| Run a workflow | `/workflow run` |
| Find people | `/discover [search query]` |
| Connect on LinkedIn | `/linkedin connect [url]` |
| Send email campaign | `/outreach` |
| Check inbox | `/inbox` |

---

**Enjoy building your outreach workflows!** 🚀

Made with Claude Code + TLDraw + Browser-Use MCP
