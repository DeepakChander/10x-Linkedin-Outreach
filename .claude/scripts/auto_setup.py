#!/usr/bin/env python3
"""
Auto Setup for 10x-Outreach-Skill

This script runs on first initialization and:
1. Checks if setup is already done
2. If not, installs all dependencies
3. Asks user for environment variables
4. Creates .env file
5. Marks setup as complete

Developed by 10x.in
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")

def print_step(step_num, total, text):
    print(f"\n{BOLD}[{step_num}/{total}] {text}{RESET}")

class SetupManager:
    def __init__(self):
        # Get project root (3 levels up from this script)
        self.script_dir = Path(__file__).parent
        self.claude_dir = self.script_dir.parent
        self.project_root = self.claude_dir.parent

        self.setup_check_file = self.claude_dir / "SETUP_CHECK.md"
        self.env_file = self.project_root / ".env"
        self.env_example = self.claude_dir / ".env.example"

    def is_setup_complete(self):
        """Check if setup is already done"""
        if not self.setup_check_file.exists():
            return False

        content = self.setup_check_file.read_text()
        return "COMPLETE" in content

    def mark_setup_complete(self):
        """Mark setup as complete"""
        content = """# Setup Status: COMPLETE

Initial setup has been successfully completed!

Completed on: {timestamp}

All dependencies installed and environment configured.

**Setup includes:**
- Python dependencies (requirements.txt)
- Node.js dependencies (package.json)
- TLDraw canvas dependencies
- Environment variables configured
- Statusline configured

You can now use all skills!
"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.setup_check_file.write_text(content.format(timestamp=timestamp))
        print_success(f"Setup marked as complete: {self.setup_check_file}")

    def install_python_dependencies(self):
        """Install Python requirements"""
        requirements_file = self.project_root / "requirements.txt"

        if not requirements_file.exists():
            print_info("No requirements.txt found, creating one...")
            requirements = [
                "google-auth-oauthlib>=1.1.0",
                "google-auth-httplib2>=0.2.0",
                "google-api-python-client>=2.108.0",
                "gspread>=5.12.0",
                "python-dotenv>=1.0.0",
                "websockets>=12.0",
                "aiohttp>=3.9.0"
            ]
            requirements_file.write_text("\n".join(requirements))
            print_success("Created requirements.txt")

        print_info(f"Installing Python dependencies from {requirements_file}...")

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True
            )
            print_success("Python dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install Python dependencies: {e}")
            return False

    def install_node_dependencies(self):
        """Install Node.js dependencies"""
        # Canvas directory
        canvas_dir = self.project_root / "canvas"
        if canvas_dir.exists() and (canvas_dir / "package.json").exists():
            print_info(f"Installing canvas dependencies...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=str(canvas_dir),
                    check=True,
                    shell=True
                )
                print_success("Canvas dependencies installed!")
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to install canvas dependencies: {e}")
                return False

        # TLDraw canvas directory
        tldraw_dir = self.project_root / "tldraw-canvas"
        if tldraw_dir.exists() and (tldraw_dir / "package.json").exists():
            print_info(f"Installing TLDraw canvas dependencies...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=str(tldraw_dir),
                    check=True,
                    shell=True
                )
                print_success("TLDraw canvas dependencies installed!")
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to install TLDraw dependencies: {e}")
                return False

        return True

    def configure_environment(self):
        """Ask user for environment variables and create .env file"""
        print_header("Environment Configuration")

        print(f"{BOLD}I need some information to configure your environment.{RESET}")
        print("Press Enter to skip any optional values.\n")

        env_vars = {}

        # Gmail API credentials
        print(f"\n{BOLD}{BLUE}Gmail API Configuration (Optional):{RESET}")
        print("For email sending features. Get from: https://console.cloud.google.com")

        google_client_id = input(f"{YELLOW}GOOGLE_CLIENT_ID:{RESET} ").strip()
        if google_client_id:
            env_vars["GOOGLE_CLIENT_ID"] = google_client_id

        google_client_secret = input(f"{YELLOW}GOOGLE_CLIENT_SECRET:{RESET} ").strip()
        if google_client_secret:
            env_vars["GOOGLE_CLIENT_SECRET"] = google_client_secret

        sender_email = input(f"{YELLOW}SENDER_EMAIL:{RESET} ").strip()
        if sender_email:
            env_vars["SENDER_EMAIL"] = sender_email

        sender_name = input(f"{YELLOW}SENDER_NAME:{RESET} ").strip()
        if sender_name:
            env_vars["SENDER_NAME"] = sender_name

        # Exa API Key
        print(f"\n{BOLD}{BLUE}Exa AI Configuration (Optional):{RESET}")
        print("For web search and discovery. Get from: https://exa.ai")

        exa_api_key = input(f"{YELLOW}EXA_API_KEY:{RESET} ").strip()
        if exa_api_key:
            env_vars["EXA_API_KEY"] = exa_api_key

        # WebSocket configuration
        print(f"\n{BOLD}{BLUE}WebSocket Configuration:{RESET}")
        websocket_port = input(f"{YELLOW}WEBSOCKET_PORT (default: 3001):{RESET} ").strip()
        env_vars["WEBSOCKET_PORT"] = websocket_port or "3001"

        # Canvas configuration
        canvas_port = input(f"{YELLOW}CANVAS_PORT (default: 3000):{RESET} ").strip()
        env_vars["CANVAS_PORT"] = canvas_port or "3000"

        # Create .env file
        print(f"\n{BOLD}Creating .env file...{RESET}")

        env_content = "# 10x-Outreach-Skill Environment Configuration\n"
        env_content += "# Generated by auto_setup.py\n\n"

        for key, value in env_vars.items():
            env_content += f"{key}={value}\n"

        self.env_file.write_text(env_content)
        print_success(f"Environment file created: {self.env_file}")

        return True

    def create_required_directories(self):
        """Create required directories"""
        print_info("Creating required directories...")

        directories = [
            self.project_root / "output",
            self.project_root / "output" / "workflows",
            self.project_root / "output" / "logs",
            self.project_root / "output" / "discovery",
            self.project_root / "output" / "websets",
            self.claude_dir / "secrets"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print_success(f"Created: {directory.relative_to(self.project_root)}")

    def run_setup(self):
        """Run complete setup process"""
        print_header("10x-Outreach-Skill Auto Setup")
        print(f"{BOLD}Welcome! Let's set up your 10x-Outreach-Skill environment.{RESET}\n")

        total_steps = 5

        # Step 1: Install Python dependencies
        print_step(1, total_steps, "Installing Python Dependencies")
        if not self.install_python_dependencies():
            print_error("Setup failed at Python dependencies")
            return False

        # Step 2: Install Node.js dependencies
        print_step(2, total_steps, "Installing Node.js Dependencies")
        if not self.install_node_dependencies():
            print_error("Setup failed at Node.js dependencies")
            return False

        # Step 3: Create directories
        print_step(3, total_steps, "Creating Required Directories")
        self.create_required_directories()

        # Step 4: Configure environment
        print_step(4, total_steps, "Configuring Environment")
        if not self.configure_environment():
            print_error("Setup failed at environment configuration")
            return False

        # Step 5: Mark setup complete
        print_step(5, total_steps, "Finalizing Setup")
        self.mark_setup_complete()

        print_header("Setup Complete!")
        print(f"{BOLD}{GREEN}All done! Your 10x-Outreach-Skill is ready to use.{RESET}\n")

        print(f"{BOLD}Next steps:{RESET}")
        print(f"  1. {GREEN}Start the canvas:{RESET} cd tldraw-canvas && npm run dev")
        print(f"  2. {GREEN}Start WebSocket:{RESET} cd canvas && node server.js")
        print(f"  3. {GREEN}Use skills:{RESET} /exa, /linkedin, /workflow, etc.\n")

        print(f"{BOLD}Documentation:{RESET}")
        print(f"  - Quick Start: QUICK-START-WORKFLOWS.md")
        print(f"  - Architecture: INTELLIGENT-CANVAS-ARCHITECTURE.md")
        print(f"  - Workflows: WORKFLOW-INTEGRATION.md\n")

        print(f"{BLUE}🔥 Developed by 10x.in{RESET}\n")

        return True


def main():
    """Main entry point"""
    setup = SetupManager()

    # Check if setup is already done
    if setup.is_setup_complete():
        print_header("Setup Already Complete")
        print(f"{GREEN}Your 10x-Outreach-Skill is already configured!{RESET}\n")
        print(f"{BOLD}To re-run setup:{RESET}")
        print(f"  1. Delete {setup.setup_check_file}")
        print(f"  2. Run this script again\n")
        return 0

    # Run setup
    try:
        success = setup.run_setup()
        return 0 if success else 1
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Setup cancelled by user.{RESET}")
        return 130
    except Exception as e:
        print_error(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
