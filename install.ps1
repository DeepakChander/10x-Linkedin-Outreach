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
            & ".venv\Scripts\pip.exe" install -r requirements.txt --quiet
            Write-Color "✓ Python dependencies installed" Green
        }
    } else {
        Write-Color "⚠ Python not found - skipping Python dependencies" Yellow
    }

    # Install canvas dependencies
    if (Test-Path "canvas") {
        Write-Color "Installing canvas dependencies..." Blue
        Set-Location canvas
        npm install --silent 2>$null
        Set-Location ..
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

    if (-not (Test-Path ".env") -and (Test-Path "$INSTALL_DIR\.env.example")) {
        Copy-Item "$INSTALL_DIR\.env.example" ".env"
        Write-Color "Created .env file from template" Yellow
        Write-Color "Please edit .env with your API keys" Yellow
    }
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
    Write-Color "Quick Start:" Magenta
    Write-Host "  1. Open Claude Code in your project directory"
    Write-Host "  2. Say: " -NoNewline; Write-Color '"start my app"' Yellow -NoNewline; Write-Host " or " -NoNewline; Write-Color '"/start"' Yellow
    Write-Host "  3. Open " -NoNewline; Write-Color "http://localhost:3000" Cyan -NoNewline; Write-Host " in your browser"
    Write-Host ""
    Write-Color "Available Commands:" Magenta
    Write-Host "  /start      - Start the visual canvas"
    Write-Host "  /discover   - Find people using Exa AI"
    Write-Host "  /outreach   - Email campaigns"
    Write-Host "  /linkedin   - LinkedIn automation"
    Write-Host "  /twitter    - Twitter automation"
    Write-Host "  /workflow   - Multi-platform sequences"
    Write-Host ""
    Write-Color "Manual Start:" Magenta
    Write-Host "  cd canvas; npm run dev -- --port 3000"
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
