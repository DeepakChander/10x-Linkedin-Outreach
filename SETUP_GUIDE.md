# 10x-Outreach-Skill Setup Guide

This guide walks you through setting up the 10x-Outreach-Skill system from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Interactive Setup Wizard](#interactive-setup-wizard)
4. [API Keys & Credentials](#api-keys--credentials)
5. [Browser Extension Setup](#browser-extension-setup)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before installing, ensure you have the following installed:

### Required

- **Node.js 18+**
  - Check: `node --version`
  - Download: https://nodejs.org/

- **Python 3.8+**
  - Check: `python --version` or `python3 --version`
  - Download: https://www.python.org/downloads/

- **Git**
  - Check: `git --version`
  - Download: https://git-scm.com/downloads/

### Optional but Recommended

- **Chrome, Edge, or Brave** (for browser automation)
- **Google Account** (for Gmail integration)

---

## Installation

### Option 1: One-Line Install (Recommended)

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.ps1 | iex
```

The installer will:
1. Check system requirements
2. Clone the repository to `~/.claude-skills/10x-outreach`
3. Install Node.js and Python dependencies
4. Run the interactive setup wizard
5. Create workspace directories

### Option 2: Manual Installation

```bash
# 1. Clone the repository
git clone https://github.com/Anit-1to10x/10x-outreach-skill.git
cd 10x-outreach-skill

# 2. Install Node.js dependencies
cd canvas
npm install
cd ..

# 3. Install Python dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 4. Run setup wizard
node setup.js
```

---

## Interactive Setup Wizard

The setup wizard (`node setup.js`) guides you through configuration with a user-friendly interface.

### What to Expect

```
╔══════════════════════════════════════════════════════════════╗
║        10x-Outreach-Skill Interactive Setup Wizard          ║
║                                                              ║
║   This wizard will help you configure your environment       ║
╚══════════════════════════════════════════════════════════════╝
```

### Configuration Steps

#### 1. Required Configuration

The wizard will ask for essential API keys:

- **Exa AI API Key**
  - What: API key for prospect discovery and enrichment
  - Get it: https://exa.ai
  - Enables: Company lookup, profile discovery, enrichment

- **Google OAuth Credentials**
  - What: Client ID and Secret for Gmail integration
  - Get it: https://console.cloud.google.com/
  - Enables: Email sending via Gmail

- **Sender Email**
  - What: Your Gmail address for sending emails
  - Format: `your-email@gmail.com`
  - Validates email format automatically

#### 2. Optional Configuration

You'll be asked if you want to configure optional features:

- **Gemini AI API Key** (Optional)
  - Get it: https://aistudio.google.com/apikey
  - Enables: Image analysis, video processing, PDF extraction

- **Canva Credentials** (Optional)
  - Get it: https://www.canva.com/developers/
  - Enables: Automated design generation, template creation
  - Requires: Client ID, Client Secret, Access Token

- **Anthropic API Key** (Optional)
  - Get it: https://console.anthropic.com/
  - Enables: Advanced AI features (falls back to Claude Code's key if not provided)

#### 3. Workspace Settings

- **Workspace Path**: Default `~/10x-skill-workspace`
- **Canvas Port**: Default `3000`
- **Debug Mode**: Default `false`

### Example Setup Flow

```
═══ REQUIRED CONFIGURATION ═══

Exa AI API Key:
  Required for prospect enrichment and discovery
  Get your key: https://exa.ai
  Features enabled: Prospect enrichment, Company data lookup

Enter Exa AI API Key: exa_xxxxxxxxxxxxxxxxxx
✓ Exa AI API Key configured

Google Client ID:
  Required for Gmail integration
  Get your key: https://console.cloud.google.com/

Enter Google Client ID: 123456789-xxxxxxxx.apps.googleusercontent.com
✓ Google Client ID configured

[... continues with other fields ...]

═══ CONFIGURATION SUMMARY ═══

Required Features:
✓ Prospect enrichment (Exa AI)
✓ Gmail integration
✓ Email campaigns

Optional Features Enabled:
✓ Multimodal features (Gemini AI)

Disabled Features:
⚠ Design automation (no Canva credentials)

Workspace:
  Path: ~/10x-skill-workspace
  Canvas Port: 3000
  Debug Mode: false

Save this configuration to .env? (y/n): y
✓ .env file created successfully!
✓ Workspace created at: /Users/you/10x-skill-workspace

═══ NEXT STEPS ═══

1. Load the Browser Extension:
   • Open Chrome/Edge
   • Go to chrome://extensions/
   • Enable "Developer mode"
   • Click "Load unpacked"
   • Select: .claude/skills/browser-extension/

2. Start the Canvas Server:
   cd canvas
   npm run dev -- --port 3000

3. Open the Visual Canvas:
   http://localhost:3000

4. Use Claude Code:
   Say: "start my app" or "/start"
```

---

## API Keys & Credentials

### Exa AI API Key

**Purpose:** Prospect discovery and enrichment

**How to get it:**
1. Go to https://exa.ai
2. Sign up for an account
3. Navigate to your dashboard
4. Copy your API key

**Free tier:** Available

### Google OAuth Credentials

**Purpose:** Gmail integration for email sending

**How to get it:**

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" or "Web application"
   - Copy Client ID and Client Secret

**Redirect URI:** `http://localhost:3000/oauth/callback` (for web app type)

### Gemini AI API Key (Optional)

**Purpose:** Multimodal AI features (image, video, PDF processing)

**How to get it:**
1. Go to https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

**Free tier:** Available with rate limits

### Canva Credentials (Optional)

**Purpose:** Automated design generation

**How to get it:**
1. Go to https://www.canva.com/developers/
2. Sign up for a developer account
3. Create a new app
4. Copy Client ID, Client Secret
5. Generate an Access Token

**Note:** Requires Canva Pro or Enterprise account for API access

### Anthropic API Key (Optional)

**Purpose:** Advanced AI features

**How to get it:**
1. Go to https://console.anthropic.com/
2. Sign up for an account
3. Navigate to API Keys
4. Create a new key

**Note:** If not provided, the skill will use Claude Code's built-in API key

---

## Browser Extension Setup

The browser extension enables LinkedIn, Twitter, and Instagram automation.

### Installation Steps

1. **Build the extension** (if not using installer):
   ```bash
   cd .claude/skills/browser-extension
   # Extension is already built, no build step needed
   ```

2. **Load in Chrome/Edge/Brave:**
   - Open your browser
   - Navigate to `chrome://extensions/` (or `edge://extensions/`)
   - Enable "Developer mode" (toggle in top-right corner)
   - Click "Load unpacked"
   - Select the directory: `.claude/skills/browser-extension/`

3. **Verify installation:**
   - You should see "10x Outreach Browser Extension" in your extensions list
   - The extension icon should appear in your browser toolbar

4. **Configure extension:**
   - Click the extension icon
   - Enter the WebSocket URL: `ws://localhost:3000/ws`
   - Click "Connect"

### Extension Features

- **LinkedIn Automation**: Connect, message, like posts, comment
- **Twitter Automation**: Tweet, like, follow, DM
- **Instagram Automation**: Like, comment, follow, DM, story replies
- **Rate Limiting**: Built-in limits to avoid platform restrictions
- **Cookie Management**: Secure authentication handling

---

## Troubleshooting

### Setup Wizard Issues

**Problem:** `node: command not found`
```bash
# Check if Node.js is installed
node --version

# If not installed, download from https://nodejs.org/
```

**Problem:** `python: command not found`
```bash
# Try python3
python3 --version

# If not installed, download from https://www.python.org/downloads/
```

**Problem:** Setup wizard exits without saving
- Make sure you answered "y" to save the configuration
- Check file permissions in the installation directory
- Try running with elevated permissions (sudo on Mac/Linux, Administrator on Windows)

### Installation Issues

**Problem:** `npm install` fails in canvas directory
```bash
# Clear npm cache
npm cache clean --force

# Try installing again
cd canvas
npm install
```

**Problem:** `pip install` fails
```bash
# Upgrade pip
pip install --upgrade pip

# Try installing with verbose output
pip install -r requirements.txt -v
```

**Problem:** Python virtual environment not activating
```bash
# On Windows PowerShell, you may need to enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.venv\Scripts\activate
```

### Runtime Issues

**Problem:** Canvas server won't start
```bash
# Check if port 3000 is already in use
# On Windows:
netstat -ano | findstr :3000

# On Mac/Linux:
lsof -i :3000

# Use a different port
npm run dev -- --port 3001
```

**Problem:** Browser extension not connecting
- Verify WebSocket URL is correct: `ws://localhost:3000/ws`
- Make sure canvas server is running
- Check browser console for connection errors
- Try reloading the extension

**Problem:** Gmail authentication fails
- Verify Google OAuth credentials are correct
- Make sure Gmail API is enabled in Google Cloud Console
- Check redirect URI matches your configuration
- Try regenerating OAuth credentials

### Reconfiguration

If you need to change your configuration:

```bash
# Re-run the setup wizard
node setup.js

# Or manually edit the .env file
nano .env  # or use any text editor
```

### Getting Help

- **Issues:** https://github.com/Anit-1to10x/10x-outreach-skill/issues
- **Discussions:** https://github.com/Anit-1to10x/10x-outreach-skill/discussions
- **Email:** support@10x-team.com

---

## Next Steps

Once setup is complete:

1. **Start the canvas server**: `cd canvas && npm run dev`
2. **Open Claude Code** in your project directory
3. **Say**: `"start my app"` or use `/start` command
4. **Open browser**: http://localhost:3000
5. **Design your first workflow** using the visual canvas
6. **Execute**: Use `/workflow run` command

Happy outreaching! 🚀
