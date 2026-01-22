#!/usr/bin/env python3
"""
10x-Outreach-Skill Setup Script
Initializes the environment and installs dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_status(msg, status="info"):
    icons = {
        "info": f"{Colors.BLUE}[i]{Colors.RESET}",
        "success": f"{Colors.GREEN}[OK]{Colors.RESET}",
        "warning": f"{Colors.YELLOW}[!]{Colors.RESET}",
        "error": f"{Colors.RED}[X]{Colors.RESET}",
    }
    print(f"{icons.get(status, icons['info'])} {msg}")

def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}    10x-Outreach-Skill Setup{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    # Check Python version
    print_status("Checking Python version...")
    if sys.version_info < (3, 9):
        print_status(f"Python 3.9+ required. Found: {sys.version}", "error")
        return False
    print_status(f"Python {sys.version_info.major}.{sys.version_info.minor} detected", "success")

    # Create virtual environment
    venv_path = script_dir / '.venv'
    if not venv_path.exists():
        print_status("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
        print_status("Virtual environment created", "success")
    else:
        print_status("Virtual environment already exists", "success")

    # Determine pip path
    if sys.platform == 'win32':
        pip_path = venv_path / 'Scripts' / 'pip.exe'
        python_path = venv_path / 'Scripts' / 'python.exe'
    else:
        pip_path = venv_path / 'bin' / 'pip'
        python_path = venv_path / 'bin' / 'python'

    # Upgrade pip
    print_status("Upgrading pip...")
    subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'],
                   capture_output=True, check=True)
    print_status("Pip upgraded", "success")

    # Install requirements
    requirements_file = script_dir / 'requirements.txt'
    if requirements_file.exists():
        print_status("Installing dependencies (this may take a moment)...")
        result = subprocess.run(
            [str(pip_path), 'install', '-r', str(requirements_file)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_status(f"Failed to install dependencies: {result.stderr}", "error")
            return False
        print_status("Dependencies installed", "success")
    else:
        print_status("requirements.txt not found", "warning")

    # Create .env if not exists
    env_file = script_dir / '.env'
    env_example = script_dir / '.env.example'
    if not env_file.exists() and env_example.exists():
        print_status("Creating .env from template...")
        shutil.copy(env_example, env_file)
        print_status(".env file created - please fill in your credentials", "warning")
    elif env_file.exists():
        print_status(".env file already exists", "success")

    # Create necessary directories
    directories = [
        'input/sheets',
        'output/logs',
        'output/sent',
        'output/drafts',
        'output/reports',
        'templates/outreach',
        'templates/promotional',
        'templates/follow-up',
        'templates/newsletter',
        'templates/custom',
        'samples/signatures',
        'samples/attachments',
    ]

    print_status("Creating directory structure...")
    for dir_path in directories:
        (script_dir / dir_path).mkdir(parents=True, exist_ok=True)
    print_status("Directories created", "success")

    # Create credentials directory
    creds_dir = script_dir / 'credentials'
    creds_dir.mkdir(exist_ok=True)

    # Create .gitignore
    gitignore_path = script_dir / '.gitignore'
    if not gitignore_path.exists():
        print_status("Creating .gitignore...")
        gitignore_content = """.env
.venv/
__pycache__/
*.pyc
credentials/
token.json
token.pickle
output/sent/
output/logs/
*.log
.DS_Store
Thumbs.db
"""
        gitignore_path.write_text(gitignore_content)
        print_status(".gitignore created", "success")

    # Create setup complete marker
    (script_dir / '.setup_complete').touch()

    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}    Setup Complete!{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

    print(f"{Colors.YELLOW}Next Steps:{Colors.RESET}")
    print("1. Edit .env file with your Google OAuth2 credentials")
    print("2. Run: python scripts/auth_setup.py (to authenticate)")
    print("3. Prepare your Google Sheet with recipient data")
    print("4. Create email templates in templates/ folder")
    print(f"5. Use /outreach command in Claude Code\n")

    print(f"{Colors.BLUE}Virtual Environment:{Colors.RESET}")
    if sys.platform == 'win32':
        print(f"   Activate: .venv\\Scripts\\activate")
        print(f"   Python:   .venv\\Scripts\\python.exe")
    else:
        print(f"   Activate: source .venv/bin/activate")
        print(f"   Python:   .venv/bin/python")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
