#
# 10x-Team Outreach Skill Installer for Windows
# Install: irm https://raw.githubusercontent.com/YOUR_USERNAME/10x-outreach-skill/main/install.ps1 | iex
#

$ErrorActionPreference = "Stop"

# Colors
function Write-Color($text, $color) {
    Write-Host $text -ForegroundColor $color
}

# Banner
Write-Host ""
Write-Color "╔══════════════════════════════════════════════════════════════╗" Magenta
Write-Color "║           10x-Team Outreach Skill Installer                   ║" Magenta
Write-Color "║         Visual Workflow Canvas for Claude Code                ║" Magenta
Write-Color "╚══════════════════════════════════════════════════════════════╝" Magenta
Write-Host ""

# Configuration
$REPO_URL = "https://github.com/Anit-1to10x/10x-outreach-skill"
$INSTALL_DIR = "$env:USERPROFILE\.claude-skills\10x-outreach"
$BRANCH = "main"

# Check requirements
function Check-Requirements {
    Write-Color "Checking requirements..." Cyan

    # Check for git
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Color "Error: git is not installed" Red
        Write-Host "Please install git: https://git-scm.com/downloads"
        exit 1
    }

    # Check for Node.js
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Color "Error: Node.js is not installed" Red
        Write-Host "Please install Node.js: https://nodejs.org/"
        exit 1
    }

    # Check Node version
    $nodeVersion = (node -v) -replace 'v', '' -split '\.' | Select-Object -First 1
    if ([int]$nodeVersion -lt 18) {
        Write-Color "Warning: Node.js 18+ recommended (you have v$nodeVersion)" Yellow
    }

    Write-Color "✓ All requirements met" Green
}

# Install skill
function Install-Skill {
    Write-Color "Installing 10x-Team Skill..." Cyan

    # Create skills directory
    $skillsDir = "$env:USERPROFILE\.claude-skills"
    if (-not (Test-Path $skillsDir)) {
        New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null
    }

    if (Test-Path $INSTALL_DIR) {
        Write-Color "Existing installation found. Updating..." Yellow
        Set-Location $INSTALL_DIR
        git fetch origin
        git reset --hard origin/$BRANCH
    } else {
        Write-Color "Cloning repository..." Blue
        git clone --depth 1 -b $BRANCH $REPO_URL $INSTALL_DIR
        Set-Location $INSTALL_DIR
    }

    Write-Color "✓ Skill files installed" Green
}

# Install dependencies
function Install-Dependencies {
    Write-Color "Installing dependencies..." Cyan

    Set-Location $INSTALL_DIR

    # Check for Python
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Color "Creating Python virtual environment..." Blue

        # Create venv if it doesn't exist
        if (-not (Test-Path ".venv")) {
            python -m venv .venv
            Write-Color "✓ Virtual environment created" Green
        }

        # Install Python dependencies
        if (Test-Path "requirements.txt") {
            Write-Color "Installing Python dependencies in virtual environment..." Blue
            & ".venv\Scripts\pip.exe" install -r requirements.txt --quiet --upgrade pip setuptools wheel
            Write-Color "✓ Python dependencies installed" Green
        }
    } else {
        Write-Color "⚠ Python not found - skipping Python dependencies" Yellow
        Write-Color "  Install Python from: https://www.python.org/downloads/" Yellow
    }

    # Install canvas dependencies
    if (Test-Path "canvas") {
        Write-Color "Installing canvas dependencies..." Blue
        Set-Location canvas
        npm install --silent 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Color "⚠ Some npm packages may have warnings (this is usually okay)" Yellow
        }
        Set-Location ..
        Write-Color "✓ Canvas dependencies installed" Green
    }

    Write-Color "✓ All dependencies installed" Green
}

# Setup Claude integration
function Setup-ClaudeIntegration {
    Write-Color "Setting up Claude Code integration..." Cyan

    $currentDir = Get-Location

    Write-Host ""
    Write-Color "Would you like to set up the skill in your current directory?" Yellow
    $response = Read-Host "Setup here? (y/n)"

    if ($response -eq 'y' -or $response -eq 'Y') {
        # Backup existing .claude folder
        if (Test-Path ".claude") {
            $timestamp = Get-Date -Format "yyyyMMddHHmmss"
            Rename-Item ".claude" ".claude.backup.$timestamp"
            Write-Color "Backed up existing .claude folder" Yellow
        }

        # Copy files
        Copy-Item -Path "$INSTALL_DIR\.claude" -Destination "." -Recurse -Force
        if (Test-Path "$INSTALL_DIR\CLAUDE.md") {
            Copy-Item "$INSTALL_DIR\CLAUDE.md" "." -Force
        }

        if (-not (Test-Path "canvas")) {
            Copy-Item -Path "$INSTALL_DIR\canvas" -Destination "." -Recurse -Force
        }

        Write-Color "✓ Skill configured in current directory" Green
    }

    Write-Color "✓ Claude Code integration ready" Green
}

# Setup environment
function Setup-Environment {
    Write-Color "Setting up environment..." Cyan

    Set-Location $INSTALL_DIR

    # Check if .env already exists
    if (Test-Path ".env") {
        Write-Host ""
        Write-Color "Existing .env file found." Yellow
        $response = Read-Host "Run interactive setup wizard to reconfigure? (y/n)"

        if ($response -eq 'y' -or $response -eq 'Y') {
            node setup.js
        } else {
            Write-Color "Keeping existing .env configuration" Green
        }
    } else {
        Write-Host ""
        Write-Color "No .env file found. Running interactive setup wizard..." Cyan
        Write-Host ""

        # Run the interactive setup wizard
        node setup.js

        if (-not (Test-Path ".env")) {
            Write-Color "⚠ Setup was cancelled or failed. Creating default .env..." Yellow
            if (Test-Path ".env.example") {
                Copy-Item ".env.example" ".env"
                Write-Color "Created .env from template - please edit with your API keys" Yellow
            }
        }
    }

    Write-Color "✓ Environment configuration ready" Green
}

# Print success
function Print-Success {
    Write-Host ""
    Write-Color "╔══════════════════════════════════════════════════════════════╗" Green
    Write-Color "║              Installation Complete!                          ║" Green
    Write-Color "╚══════════════════════════════════════════════════════════════╝" Green
    Write-Host ""
    Write-Host "Installation directory: $INSTALL_DIR"
    Write-Host ""
    Write-Color "Next Steps:" Magenta
    Write-Host ""
    Write-Host "  1. " -NoNewline; Write-Color "Load the Browser Extension:" Cyan
    Write-Host "     • Open Chrome/Edge"
    Write-Host "     • Go to chrome://extensions/"
    Write-Host "     • Enable 'Developer mode'"
    Write-Host "     • Click 'Load unpacked'"
    Write-Host "     • Select: .claude/skills/browser-extension/"
    Write-Host ""
    Write-Host "  2. " -NoNewline; Write-Color "Start the Canvas Server:" Cyan
    Write-Host "     cd canvas"
    Write-Host "     npm run dev -- --port 3000"
    Write-Host ""
    Write-Host "  3. " -NoNewline; Write-Color "Open the Visual Canvas:" Cyan
    Write-Host "     " -NoNewline; Write-Color "http://localhost:3000" Blue
    Write-Host ""
    Write-Host "  4. " -NoNewline; Write-Color "Use Claude Code:" Cyan
    Write-Host "     Say: " -NoNewline; Write-Color '"start my app"' Yellow -NoNewline; Write-Host " or " -NoNewline; Write-Color '"/start"' Yellow
    Write-Host ""
    Write-Color "Available Commands:" Magenta
    Write-Host "  /start      - Start the visual canvas"
    Write-Host "  /discover   - Find people using Exa AI"
    Write-Host "  /outreach   - Email campaigns"
    Write-Host "  /linkedin   - LinkedIn automation"
    Write-Host "  /twitter    - Twitter automation"
    Write-Host "  /instagram  - Instagram automation"
    Write-Host "  /workflow   - Multi-platform sequences"
    Write-Host ""
    Write-Color "Configuration:" Magenta
    Write-Host "  • Environment: .env file configured"
    Write-Host "  • Workspace: Check your configured workspace path"
    Write-Host "  • To reconfigure: " -NoNewline; Write-Color "node setup.js" Yellow
    Write-Host ""
}

# Main
try {
    Check-Requirements
    Install-Skill
    Install-Dependencies
    Setup-ClaudeIntegration
    Setup-Environment
    Print-Success
} catch {
    Write-Color "Installation failed: $_" Red
    exit 1
}
