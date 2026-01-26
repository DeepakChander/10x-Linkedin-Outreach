#!/bin/bash
#
# 10x-Team Outreach Skill Installer
# Install: curl -fsSL https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.sh | bash
#
# This script installs the 10x-Team Visual Workflow Canvas skill for Claude Code
# with IT Operations Support System capabilities.
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           10x-Team Outreach Skill Installer                   ║"
echo "║   Visual Workflow Canvas + IT Operations Support System       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
REPO_URL="https://github.com/Anit-1to10x/10x-outreach-skill"
INSTALL_DIR="${HOME}/.claude-skills/10x-outreach"
BRANCH="main"

# Check for required tools
check_requirements() {
    echo -e "${CYAN}Checking requirements...${NC}"

    # Check for git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}Error: git is not installed${NC}"
        echo "Please install git: https://git-scm.com/downloads"
        exit 1
    fi

    # Check for Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Error: Node.js is not installed${NC}"
        echo "Please install Node.js: https://nodejs.org/"
        exit 1
    fi

    # Check Node version
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        echo -e "${YELLOW}Warning: Node.js 18+ recommended (you have v${NODE_VERSION})${NC}"
    fi

    # Check for npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}Error: npm is not installed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ All requirements met${NC}"
}

# Clone or update repository
install_skill() {
    echo -e "${CYAN}Installing 10x-Team Skill...${NC}"

    # Create skills directory if it doesn't exist
    mkdir -p "${HOME}/.claude-skills"

    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}Existing installation found. Updating...${NC}"
        cd "$INSTALL_DIR"
        git fetch origin
        git reset --hard origin/$BRANCH
    else
        echo -e "${BLUE}Cloning repository...${NC}"
        git clone --depth 1 -b $BRANCH "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi

    echo -e "${GREEN}✓ Skill files installed${NC}"
}

# Install dependencies
install_dependencies() {
    echo -e "${CYAN}Installing dependencies...${NC}"

    cd "$INSTALL_DIR"

    # Check for Python and create virtual environment
    if command -v python3 &> /dev/null || command -v python &> /dev/null; then
        PYTHON_CMD=$(command -v python3 || command -v python)
        echo -e "${BLUE}Creating Python virtual environment...${NC}"

        # Create venv if it doesn't exist
        if [ ! -d ".venv" ]; then
            $PYTHON_CMD -m venv .venv
            echo -e "${GREEN}✓ Virtual environment created${NC}"
        fi

        # Install Python dependencies
        if [ -f "requirements.txt" ]; then
            echo -e "${BLUE}Installing Python dependencies in virtual environment...${NC}"
            .venv/bin/pip install --upgrade pip setuptools wheel --quiet 2>/dev/null || true
            .venv/bin/pip install -r requirements.txt --quiet 2>/dev/null || true
            echo -e "${GREEN}✓ Python dependencies installed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Python not found - skipping Python dependencies${NC}"
        echo -e "${YELLOW}  Install Python from: https://www.python.org/downloads/${NC}"
    fi

    # Install canvas dependencies
    if [ -d "canvas" ]; then
        echo -e "${BLUE}Installing canvas dependencies...${NC}"
        cd canvas
        npm install --silent 2>/dev/null || npm install
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}⚠ Some npm packages may have warnings (this is usually okay)${NC}"
        fi
        cd ..
        echo -e "${GREEN}✓ Canvas dependencies installed${NC}"
    fi

    echo -e "${GREEN}✓ All dependencies installed${NC}"
}

# Create IT Operations directories
setup_it_operations() {
    echo -e "${CYAN}Setting up IT Operations Support directories...${NC}"

    cd "$INSTALL_DIR"

    # Create IT Operations directories
    mkdir -p tickets/active
    mkdir -p tickets/closed
    mkdir -p audit_logs
    mkdir -p sla
    mkdir -p tenants
    mkdir -p knowledge_base
    mkdir -p webhooks
    mkdir -p metrics
    mkdir -p credentials

    echo -e "${GREEN}✓ IT Operations directories created${NC}"
}

# Setup Claude Code integration
setup_claude_integration() {
    echo -e "${CYAN}Setting up Claude Code integration...${NC}"

    # Create symlink in current directory if user wants
    echo ""
    echo -e "${YELLOW}Would you like to set up the skill in your current directory?${NC}"
    echo "This will create a .claude folder with the skill configuration."
    read -p "Setup here? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Copy .claude folder to current directory
        if [ -d ".claude" ]; then
            echo -e "${YELLOW}Existing .claude folder found. Backing up...${NC}"
            mv .claude .claude.backup.$(date +%s)
        fi

        cp -r "$INSTALL_DIR/.claude" .
        cp "$INSTALL_DIR/CLAUDE.md" . 2>/dev/null || true

        # Copy canvas if not exists
        if [ ! -d "canvas" ]; then
            cp -r "$INSTALL_DIR/canvas" .
        fi

        echo -e "${GREEN}✓ Skill configured in current directory${NC}"
    fi

    echo -e "${GREEN}✓ Claude Code integration ready${NC}"
}

# Create env file template
setup_environment() {
    echo -e "${CYAN}Setting up environment...${NC}"

    cd "$INSTALL_DIR"

    # Check if .env already exists
    if [ -f ".env" ]; then
        echo ""
        echo -e "${YELLOW}Existing .env file found.${NC}"
        read -p "Run interactive setup wizard to reconfigure? (y/n): " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            node setup.js
        else
            echo -e "${GREEN}Keeping existing .env configuration${NC}"
        fi
    else
        echo ""
        echo -e "${CYAN}No .env file found. Running interactive setup wizard...${NC}"
        echo ""

        # Run the interactive setup wizard
        node setup.js

        if [ ! -f ".env" ]; then
            echo -e "${YELLOW}⚠ Setup was cancelled or failed. Creating default .env...${NC}"
            if [ -f ".env.example" ]; then
                cp ".env.example" ".env"
                echo -e "${YELLOW}Created .env from template - please edit with your API keys${NC}"
            fi
        fi
    fi

    echo -e "${GREEN}✓ Environment configuration ready${NC}"
}

# Print success message
print_success() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Installation Complete!                          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Installation directory:${NC} $INSTALL_DIR"
    echo ""
    echo -e "${PURPLE}Next Steps:${NC}"
    echo ""
    echo -e "  1. ${CYAN}Load the Browser Extension:${NC}"
    echo -e "     • Open Chrome/Edge/Brave"
    echo -e "     • Go to chrome://extensions/"
    echo -e "     • Enable 'Developer mode'"
    echo -e "     • Click 'Load unpacked'"
    echo -e "     • Select: .claude/skills/browser-extension/"
    echo ""
    echo -e "  2. ${CYAN}Start the Canvas Server:${NC}"
    echo -e "     cd canvas"
    echo -e "     npm run dev -- --port 3000"
    echo ""
    echo -e "  3. ${CYAN}Open the Visual Canvas:${NC}"
    echo -e "     ${BLUE}http://localhost:3000${NC}"
    echo ""
    echo -e "  4. ${CYAN}Use Claude Code:${NC}"
    echo -e "     Say: ${YELLOW}\"start my app\"${NC} or ${YELLOW}\"/start\"${NC}"
    echo ""
    echo -e "${PURPLE}Outreach Commands:${NC}"
    echo -e "  ${YELLOW}/start${NC}      - Start the visual canvas"
    echo -e "  ${YELLOW}/discover${NC}   - Find people using Exa AI"
    echo -e "  ${YELLOW}/outreach${NC}   - Email campaigns"
    echo -e "  ${YELLOW}/linkedin${NC}   - LinkedIn automation"
    echo -e "  ${YELLOW}/twitter${NC}    - Twitter automation"
    echo -e "  ${YELLOW}/instagram${NC}  - Instagram automation"
    echo -e "  ${YELLOW}/workflow${NC}   - Multi-platform sequences"
    echo ""
    echo -e "${PURPLE}IT Operations Commands:${NC}"
    echo -e "  ${YELLOW}/ticket${NC}     - Create and manage tickets"
    echo -e "  ${YELLOW}/sla${NC}        - Check SLA status"
    echo -e "  ${YELLOW}/kb${NC}         - Search knowledge base"
    echo -e "  ${YELLOW}/analyze${NC}    - Analyze email context"
    echo -e "  ${YELLOW}/audit${NC}      - View audit logs"
    echo ""
    echo -e "${PURPLE}Configuration:${NC}"
    echo -e "  • Environment: .env file configured"
    echo -e "  • Workspace: Check your configured workspace path"
    echo -e "  • To reconfigure: ${YELLOW}node setup.js${NC}"
    echo ""
}

# Main installation flow
main() {
    check_requirements
    install_skill
    install_dependencies
    setup_it_operations
    setup_claude_integration
    setup_environment
    print_success
}

# Run main function
main "$@"
