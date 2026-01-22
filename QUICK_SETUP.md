# Quick Setup Reference

## Installation (Choose One)

### 🪟 Windows
```powershell
irm https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.ps1 | iex
```

### 🍎 Mac / 🐧 Linux
```bash
curl -fsSL https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.sh | bash
```

### 📦 Manual
```bash
git clone https://github.com/Anit-1to10x/10x-outreach-skill.git
cd 10x-outreach-skill
cd canvas && npm install && cd ..
pip install -r requirements.txt
node setup.js
```

---

## Setup Wizard

The installer runs an interactive wizard that collects:

### ✅ Required
- **Exa AI API Key** - Get at https://exa.ai
- **Google Client ID** - Get at https://console.cloud.google.com/
- **Google Client Secret** - Same as above
- **Sender Email** - Your Gmail address

### ⚙️ Optional
- **Gemini AI Key** - https://aistudio.google.com/apikey
- **Canva Credentials** - https://www.canva.com/developers/
- **Anthropic API Key** - https://console.anthropic.com/

### 🔧 Settings
- **Workspace Path** - Default: `~/10x-skill-workspace`
- **Canvas Port** - Default: `3000`
- **Debug Mode** - Default: `false`

---

## Post-Install Steps

### 1. Load Browser Extension
```
chrome://extensions/
→ Enable "Developer mode"
→ "Load unpacked"
→ Select: .claude/skills/browser-extension/
```

### 2. Start Canvas Server
```bash
cd canvas
npm run dev -- --port 3000
```

### 3. Open Canvas
```
http://localhost:3000
```

### 4. Use with Claude Code
```
"start my app"  or  /start
```

---

## Reconfigure

Need to change settings?
```bash
node setup.js
```

Or edit `.env` manually.

---

## Features Enabled by API Keys

| API Key | Features |
|---------|----------|
| **Exa AI** (Required) | Prospect discovery, company lookup, enrichment |
| **Google OAuth** (Required) | Gmail sending, email campaigns |
| **Gemini AI** (Optional) | Image analysis, video processing, PDF extraction |
| **Canva** (Optional) | Design automation, template generation |
| **Anthropic** (Optional) | Advanced AI features (uses Claude Code key if missing) |

---

## Common Commands

```bash
# Run setup wizard
node setup.js

# Start canvas server
npm start
# or
cd canvas && npm run dev

# Start WebSocket server only
cd canvas && npm run server

# Check Node.js version
node --version

# Check Python version
python --version
```

---

## File Locations

```
~/.claude-skills/10x-outreach/     # Install directory
~/10x-skill-workspace/             # Default workspace
.env                               # Your configuration
.claude/skills/browser-extension/  # Browser extension
canvas/                            # Visual canvas app
```

---

## Troubleshooting

### Setup won't run
- Check Node.js is installed: `node --version`
- Check Python is installed: `python --version`
- Verify you're in the correct directory

### Canvas won't start
- Port 3000 in use? Try: `npm run dev -- --port 3001`
- Dependencies missing? Run: `cd canvas && npm install`

### Extension won't connect
- Canvas server running? Check http://localhost:3000
- WebSocket URL correct? Should be: `ws://localhost:3000/ws`
- Try reloading extension

### Gmail auth fails
- Gmail API enabled in Google Cloud Console?
- OAuth credentials correct?
- Redirect URI matches configuration?

---

## Get Help

- 📖 Full guide: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- 🐛 Issues: https://github.com/Anit-1to10x/10x-outreach-skill/issues
- 💬 Discussions: https://github.com/Anit-1to10x/10x-outreach-skill/discussions

---

## What's Next?

1. Design workflows in the visual canvas
2. Use `/discover` to find prospects with Exa AI
3. Create email campaigns with `/outreach`
4. Automate LinkedIn with `/linkedin`
5. Multi-platform sequences with `/workflow`

**Happy outreaching!** 🚀
