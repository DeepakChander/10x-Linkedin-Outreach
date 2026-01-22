#!/usr/bin/env python3
"""
100X Outreach System - Complete Setup Script

This script sets up the 100X Outreach System:
1. Python virtual environment and dependencies
2. Directory structure
3. Environment variables
4. Gmail OAuth2 configuration

NOTE: ClaudeKit Browser Extension is used for platform automation.
      The extension connects via WebSocket at ws://localhost:3000/ws
      Canvas server provides HTTP API at http://localhost:3000/api

Run: python setup_100x.py
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, Optional

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_step(step: int, total: int, text: str):
    print(f"{Colors.CYAN}[{step}/{total}]{Colors.END} {text}")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def run_command(cmd: str, capture: bool = False, shell: bool = True) -> tuple:
    """Run a shell command"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=shell)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def check_prerequisites() -> Dict[str, bool]:
    """Check for required tools"""
    prereqs = {}

    # Check Python version
    prereqs['python'] = sys.version_info >= (3, 9)

    # Check Node.js
    success, stdout, _ = run_command("node --version", capture=True)
    prereqs['node'] = success and stdout.strip().startswith('v')

    # Check npm
    success, _, _ = run_command("npm --version", capture=True)
    prereqs['npm'] = success

    # Check npx
    success, _, _ = run_command("npx --version", capture=True)
    prereqs['npx'] = success

    # Check git (optional)
    success, _, _ = run_command("git --version", capture=True)
    prereqs['git'] = success

    return prereqs

def get_claude_code_config_path() -> Path:
    """Get the Claude Code configuration directory"""
    system = platform.system()

    if system == "Windows":
        # Windows: %APPDATA%\Claude\
        appdata = os.environ.get('APPDATA', '')
        return Path(appdata) / "Claude"
    elif system == "Darwin":
        # macOS: ~/Library/Application Support/Claude/
        return Path.home() / "Library" / "Application Support" / "Claude"
    else:
        # Linux: ~/.config/claude/
        return Path.home() / ".config" / "claude"

def setup_directories(base_dir: Path):
    """Create all necessary directories"""
    directories = [
        "credentials/profiles",
        "campaigns/active",
        "campaigns/completed",
        "campaigns/logs",
        "workflows/custom",
        "output/discovery",
        "output/logs",
        "output/sent",
        "output/drafts",
        "output/reports",
    ]

    for dir_path in directories:
        (base_dir / dir_path).mkdir(parents=True, exist_ok=True)

    # Create .gitkeep files
    for dir_path in directories:
        gitkeep = base_dir / dir_path / ".gitkeep"
        gitkeep.touch(exist_ok=True)

def setup_python_environment(base_dir: Path) -> bool:
    """Set up Python virtual environment and install dependencies"""
    venv_path = base_dir / ".venv"

    # Create virtual environment
    if not venv_path.exists():
        print_info("Creating Python virtual environment...")
        success, _, err = run_command(f'"{sys.executable}" -m venv "{venv_path}"')
        if not success:
            print_error(f"Failed to create virtual environment: {err}")
            return False

    # Determine pip path
    if platform.system() == "Windows":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"

    # Upgrade pip
    print_info("Upgrading pip...")
    run_command(f'"{python_path}" -m pip install --upgrade pip', capture=True)

    # Install requirements
    requirements_file = base_dir / "requirements.txt"
    if requirements_file.exists():
        print_info("Installing Python dependencies...")
        success, _, err = run_command(f'"{pip_path}" install -r "{requirements_file}"')
        if not success:
            print_warning(f"Some dependencies may have failed: {err}")

    # Install additional dependencies for 100X system
    additional_deps = [
        "pyyaml",
        "playwright",
    ]

    print_info("Installing additional dependencies...")
    for dep in additional_deps:
        run_command(f'"{pip_path}" install {dep}', capture=True)

    # Install playwright browsers
    print_info("Installing Playwright browsers (for local browser automation)...")
    run_command(f'"{python_path}" -m playwright install chromium', capture=True)

    return True

# =============================================================================
# CLAUDEKIT BROWSER EXTENSION - NO INSTALLATION NEEDED
# Extension connects via WebSocket to canvas server
# =============================================================================

def setup_extension_info():
    """Display info about ClaudeKit Browser Extension"""
    print_info("ClaudeKit Browser Extension: Local browser automation via WebSocket")
    print_info("Extension connects to canvas server at ws://localhost:3000/ws")
    print_success("Browser automation available via HTTP API at http://localhost:3000/api")

def generate_mcp_config(base_dir: Path, exa_api_key: str = "") -> Dict:
    """Generate MCP configuration for Claude Code"""

    config = {
        "mcpServers": {
            "exa": {
                "command": "npx",
                "args": [
                    "-y",
                    "exa-mcp-server",
                    "tools=web_search_exa,linkedin_search_exa,company_research_exa,deep_researcher_start,deep_researcher_check,crawling_exa"
                ],
                "env": {
                    "EXA_API_KEY": exa_api_key or "${EXA_API_KEY}"
                }
            }
        }
    }

    return config

def save_mcp_config(config: Dict, base_dir: Path):
    """Save MCP configuration to Claude Code settings"""

    # Save local copy
    local_config_path = base_dir / "mcp_config.json"
    with open(local_config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print_success(f"Saved MCP config to: {local_config_path}")

    # Try to save to Claude Code global config
    claude_config_dir = get_claude_code_config_path()

    if claude_config_dir.exists():
        claude_settings = claude_config_dir / "claude_desktop_config.json"

        # Read existing config
        existing_config = {}
        if claude_settings.exists():
            try:
                with open(claude_settings, 'r') as f:
                    existing_config = json.load(f)
            except:
                pass

        # Merge MCP servers
        if 'mcpServers' not in existing_config:
            existing_config['mcpServers'] = {}

        existing_config['mcpServers'].update(config['mcpServers'])

        # Save
        try:
            with open(claude_settings, 'w') as f:
                json.dump(existing_config, f, indent=2)
            print_success(f"Updated Claude Code config: {claude_settings}")
        except Exception as e:
            print_warning(f"Could not update Claude Code config: {e}")
            print_info("You can manually copy mcp_config.json to your Claude settings")

def create_env_file(base_dir: Path, config: Dict):
    """Create or update .env file"""
    env_file = base_dir / ".env"
    env_local = base_dir / ".env.local"

    # Default values
    env_content = f"""# 100X Outreach System Configuration
# Generated by setup_100x.py

# =============================================================================
# Exa AI Configuration (for people discovery)
# =============================================================================
EXA_API_KEY={config.get('exa_api_key', 'your_exa_api_key_here')}

# =============================================================================
# Google OAuth2 Credentials (for Gmail)
# =============================================================================
GOOGLE_CLIENT_ID={config.get('google_client_id', '')}
GOOGLE_CLIENT_SECRET={config.get('google_client_secret', '')}

# =============================================================================
# Sender Configuration
# =============================================================================
SENDER_EMAIL={config.get('sender_email', '')}
SENDER_NAME={config.get('sender_name', '')}

# =============================================================================
# Rate Limits (per user, per day)
# =============================================================================
LINKEDIN_CONNECTIONS_PER_DAY=20
LINKEDIN_MESSAGES_PER_DAY=50
TWITTER_FOLLOWS_PER_DAY=50
TWITTER_DMS_PER_DAY=50
INSTAGRAM_FOLLOWS_PER_DAY=30
INSTAGRAM_DMS_PER_DAY=30

# =============================================================================
# Workflow Settings
# =============================================================================
DEFAULT_MIN_DELAY_SECONDS=120
DEFAULT_MAX_DELAY_SECONDS=600
WORKFLOW_ACTIVE_HOURS_START=09:00
WORKFLOW_ACTIVE_HOURS_END=18:00
WORKFLOW_TIMEZONE=UTC

# =============================================================================
# Campaign Settings
# =============================================================================
EMAIL_DELAY_SECONDS=60
MAX_EMAILS_PER_BATCH=50
DAILY_EMAIL_LIMIT=100
DRY_RUN_MODE=false

# =============================================================================
# Output Configuration
# =============================================================================
OUTPUT_DIR=./output
LOG_DIR=./output/logs
LOG_LEVEL=INFO
"""

    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print_success(f"Created {env_file}")

    # Also update .env.local if API key provided
    if config.get('exa_api_key'):
        with open(env_local, 'w') as f:
            f.write(f"EXA_API_KEY={config['exa_api_key']}\n")
        print_success(f"Saved API key to {env_local}")

def create_quick_start_script(base_dir: Path):
    """Create a quick start script for common operations"""

    if platform.system() == "Windows":
        script_content = '''@echo off
REM 100X Outreach System - Quick Start

if "%1"=="" goto help
if "%1"=="team" goto team
if "%1"=="discover" goto discover
if "%1"=="workflow" goto workflow
if "%1"=="templates" goto templates
if "%1"=="limits" goto limits
goto help

:team
.venv\\Scripts\\python.exe scripts\\team_manager.py %2 %3 %4 %5 %6 %7 %8 %9
goto end

:discover
.venv\\Scripts\\python.exe scripts\\discovery_engine.py %2 %3 %4 %5 %6 %7 %8 %9
goto end

:workflow
.venv\\Scripts\\python.exe scripts\\workflow_engine.py %2 %3 %4 %5 %6 %7 %8 %9
goto end

:templates
.venv\\Scripts\\python.exe scripts\\template_loader.py %2 %3 %4 %5 %6 %7 %8 %9
goto end

:limits
.venv\\Scripts\\python.exe scripts\\rate_limiter.py %2 %3 %4 %5 %6 %7 %8 %9
goto end

:help
echo.
echo 100X Outreach System - Quick Commands
echo =====================================
echo.
echo   100x team [command]      - Manage team members
echo   100x discover [command]  - People discovery
echo   100x workflow [command]  - Manage workflows
echo   100x templates [command] - Manage templates
echo   100x limits [command]    - Check rate limits
echo.
echo Examples:
echo   100x team list
echo   100x templates list --platform linkedin
echo   100x workflow list
echo.

:end
'''
        script_path = base_dir / "100x.bat"
    else:
        script_content = '''#!/bin/bash
# 100X Outreach System - Quick Start

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$SCRIPT_DIR/.venv/bin/python"

case "$1" in
    team)
        shift
        $PYTHON "$SCRIPT_DIR/scripts/team_manager.py" "$@"
        ;;
    discover)
        shift
        $PYTHON "$SCRIPT_DIR/scripts/discovery_engine.py" "$@"
        ;;
    workflow)
        shift
        $PYTHON "$SCRIPT_DIR/scripts/workflow_engine.py" "$@"
        ;;
    templates)
        shift
        $PYTHON "$SCRIPT_DIR/scripts/template_loader.py" "$@"
        ;;
    limits)
        shift
        $PYTHON "$SCRIPT_DIR/scripts/rate_limiter.py" "$@"
        ;;
    *)
        echo ""
        echo "100X Outreach System - Quick Commands"
        echo "====================================="
        echo ""
        echo "  ./100x team [command]      - Manage team members"
        echo "  ./100x discover [command]  - People discovery"
        echo "  ./100x workflow [command]  - Manage workflows"
        echo "  ./100x templates [command] - Manage templates"
        echo "  ./100x limits [command]    - Check rate limits"
        echo ""
        echo "Examples:"
        echo "  ./100x team list"
        echo "  ./100x templates list --platform linkedin"
        echo "  ./100x workflow list"
        echo ""
        ;;
esac
'''
        script_path = base_dir / "100x"

    with open(script_path, 'w') as f:
        f.write(script_content)

    if platform.system() != "Windows":
        os.chmod(script_path, 0o755)

    print_success(f"Created quick start script: {script_path}")

def interactive_setup():
    """Run interactive setup wizard"""
    print_header("100X OUTREACH SYSTEM - SETUP WIZARD")

    base_dir = Path(__file__).parent.resolve()
    total_steps = 8
    config = {}

    # Step 1: Check prerequisites
    print_step(1, total_steps, "Checking prerequisites...")
    prereqs = check_prerequisites()

    if not prereqs['python']:
        print_error(f"Python 3.9+ required. Current: {sys.version}")
        return False
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}")

    if not prereqs['node']:
        print_error("Node.js is required for MCP servers")
        print_info("Install from: https://nodejs.org/")
        return False
    print_success("Node.js installed")

    if not prereqs['npm']:
        print_error("npm is required")
        return False
    print_success("npm installed")

    # Step 2: Create directories
    print_step(2, total_steps, "Creating directory structure...")
    setup_directories(base_dir)
    print_success("Directories created")

    # Step 3: Set up Python environment
    print_step(3, total_steps, "Setting up Python environment...")
    if not setup_python_environment(base_dir):
        print_error("Failed to set up Python environment")
        return False
    print_success("Python environment ready")

    # Step 4: ClaudeKit Browser Extension info
    print_step(4, total_steps, "Configuring ClaudeKit Browser Extension...")
    setup_extension_info()
    print_success("ClaudeKit Browser Extension: Ready (via WebSocket)")

    # Step 5: Get API keys
    print_step(5, total_steps, "Configuring API keys...")
    print()
    print_info("Enter your Exa AI API key (get one at https://exa.ai/)")
    print_info("Press Enter to skip and configure later")
    exa_key = input("Exa API Key: ").strip()
    config['exa_api_key'] = exa_key

    # Step 6: Generate MCP config
    print_step(6, total_steps, "Generating MCP configuration...")
    mcp_config = generate_mcp_config(base_dir, exa_key)
    save_mcp_config(mcp_config, base_dir)

    # Step 7: Create environment file
    print_step(7, total_steps, "Creating environment configuration...")
    create_env_file(base_dir, config)

    # Step 8: Create quick start script
    print_step(8, total_steps, "Creating quick start script...")
    create_quick_start_script(base_dir)

    # Done!
    print_header("SETUP COMPLETE!")

    print(f"""
{Colors.GREEN}Your 100X Outreach System is ready!{Colors.END}

{Colors.BOLD}ClaudeKit Browser Extension:{Colors.END}
   Local browser automation via WebSocket
   Canvas server: http://localhost:3000
   WebSocket: ws://localhost:3000/ws

{Colors.BOLD}Next Steps:{Colors.END}

1. {Colors.CYAN}Start the canvas server:{Colors.END}
   /start (or cd canvas && npm run dev)

2. {Colors.CYAN}Add a team member:{Colors.END}
   /team add

3. {Colors.CYAN}Load the browser extension:{Colors.END}
   - Open Chrome extensions (chrome://extensions/)
   - Enable Developer mode
   - Load unpacked: .claude/skills/browser-extension
   - Extension should connect to WebSocket automatically

4. {Colors.CYAN}Discover people:{Colors.END}
   /discover AI startup founders in San Francisco

5. {Colors.CYAN}Create a workflow:{Colors.END}
   /workflow create

6. {Colors.CYAN}Use platform commands:{Colors.END}
   /linkedin connect https://linkedin.com/in/username
   /twitter dm @username "Hello!"
   /instagram follow @username

{Colors.BOLD}Quick Commands:{Colors.END}
   {"100x.bat" if platform.system() == "Windows" else "./100x"} team list
   {"100x.bat" if platform.system() == "Windows" else "./100x"} templates list
   {"100x.bat" if platform.system() == "Windows" else "./100x"} workflow list

{Colors.BOLD}Available Slash Commands in Claude Code:{Colors.END}
   /team      - Manage team members
   /discover  - Find people with Exa AI
   /workflow  - Create multi-platform campaigns
   /linkedin  - LinkedIn actions (connect, message, like, comment)
   /twitter   - Twitter actions (follow, dm, like, reply, retweet)
   /instagram - Instagram actions (follow, dm, like, comment, story)
   /outreach  - Email campaigns (Gmail)
   /inbox     - Read emails
   /compose   - Write emails
   /reply     - Reply to emails
   /summarize - Email digests

{Colors.BOLD}Gmail Setup (for email campaigns):{Colors.END}
   1. Get Google OAuth2 credentials from Google Cloud Console
   2. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env
   3. Run /outreach to start email campaigns

{Colors.YELLOW}ClaudeKit Browser Extension connects automatically when canvas server is running!{Colors.END}
""")

    return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="100X Outreach System Setup")
    parser.add_argument('--non-interactive', action='store_true',
                        help='Run without prompts (use defaults)')
    parser.add_argument('--exa-key', help='Exa AI API key')
    parser.add_argument('--skip-mcp', action='store_true',
                        help='Skip MCP server installation')

    args = parser.parse_args()

    if args.non_interactive:
        # Non-interactive setup
        base_dir = Path(__file__).parent.resolve()

        print_header("100X OUTREACH SYSTEM - AUTOMATED SETUP")

        prereqs = check_prerequisites()
        if not prereqs['python']:
            print_error("Python 3.9+ required")
            sys.exit(1)

        setup_directories(base_dir)
        setup_python_environment(base_dir)

        # ClaudeKit Browser Extension - no installation needed
        setup_extension_info()

        config = {'exa_api_key': args.exa_key or ''}
        mcp_config = generate_mcp_config(base_dir, config['exa_api_key'])
        save_mcp_config(mcp_config, base_dir)
        create_env_file(base_dir, config)
        create_quick_start_script(base_dir)

        print_success("Setup complete!")
        print_info("ClaudeKit Browser Extension ready - start canvas server with /start")
    else:
        # Interactive setup
        try:
            success = interactive_setup()
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\n\nSetup cancelled.")
            sys.exit(1)


if __name__ == "__main__":
    main()
