# Changelog - Setup Wizard Implementation

## [1.1.0] - 2026-01-22

### Added

#### Interactive Setup Wizard (`setup.js`)
- **NEW**: Interactive Node.js setup wizard with color-coded terminal output
- **NEW**: Step-by-step configuration collection for all API keys
- **NEW**: Email validation for SENDER_EMAIL field
- **NEW**: Feature summary showing enabled/disabled features based on configuration
- **NEW**: Automatic `.env` file generation from collected values
- **NEW**: Workspace directory creation (campaigns, templates, outputs, logs)
- **NEW**: Backup of existing `.env` files with timestamp
- **NEW**: Clear next steps instructions after setup completion

#### Configuration Categories
- **Required Configuration**:
  - Exa AI API Key (prospect enrichment)
  - Google Client ID and Secret (Gmail integration)
  - Sender Email address (with validation)

- **Optional Configuration**:
  - Gemini AI API Key (multimodal features)
  - Canva credentials (design automation)
  - Anthropic API Key (advanced AI features)

- **Workspace Settings**:
  - Workspace path (default: ~/10x-skill-workspace)
  - Canvas port (default: 3000)
  - Debug mode (default: false)

#### Documentation
- **NEW**: `SETUP_GUIDE.md` - Comprehensive 11 KB setup documentation including:
  - Prerequisites and system requirements
  - Installation instructions (one-line and manual)
  - Interactive setup wizard walkthrough
  - API keys acquisition guide with links
  - Browser extension setup instructions
  - Troubleshooting section with common issues

- **NEW**: `QUICK_SETUP.md` - 3.7 KB quick reference card with:
  - Installation one-liners for all platforms
  - Required vs optional API keys
  - Post-install steps
  - Common commands
  - File locations
  - Quick troubleshooting tips

- **NEW**: `SETUP_IMPLEMENTATION.md` - Technical implementation details

- **NEW**: `package.json` - Root package.json for ES module support with scripts:
  - `npm run setup` - Run setup wizard
  - `npm start` - Start canvas server
  - `npm run server` - Start WebSocket server only

### Enhanced

#### Windows Installer (`install.ps1`)
- **Enhanced**: Integrated setup wizard execution after dependency installation
- **Enhanced**: Better Python dependency handling with virtual environment
- **Enhanced**: Improved error handling for npm install with warning messages
- **Enhanced**: Checks for existing `.env` before running wizard (offers reconfiguration)
- **Enhanced**: Updated success message with comprehensive next steps including:
  - Browser extension installation instructions
  - Canvas server startup
  - Visual canvas URL
  - Claude Code usage
  - Available commands
  - Reconfiguration command

#### Unix/Mac Installer (`install.sh`)
- **Enhanced**: Same improvements as install.ps1 for Unix systems
- **Enhanced**: Python 3 support with fallback to python command
- **Enhanced**: Virtual environment creation and activation
- **Enhanced**: Interactive wizard integration
- **Enhanced**: Cross-platform path handling

#### README.md
- **Enhanced**: Installation section with:
  - "What the installer does" overview
  - Clear system requirements (Node.js 18+, Python 3.8+, Git)
  - Configuration section explaining required and optional API keys
  - Reconfiguration instructions
  - Better visual formatting with emojis

### Improved

#### User Experience
- **Improved**: Color-coded output for better readability:
  - Green (✓) for success messages
  - Yellow (⚠) for warnings and optional items
  - Red (✗) for errors
  - Cyan (ℹ) for information
  - Magenta for headers

- **Improved**: Input validation:
  - Email format validation
  - Required field checks
  - Boolean value validation (true/false)

- **Improved**: Error handling:
  - Graceful handling of missing tools
  - Clear error messages with solutions
  - Fallback to .env.example if setup cancelled

- **Improved**: Configuration summary:
  - Shows which features are enabled
  - Warns about disabled features
  - Displays workspace settings

#### Installation Process
- **Improved**: Dependency installation:
  - Python virtual environment creation
  - Upgrade pip, setuptools, wheel before installing requirements
  - Better npm install error handling
  - Progress indicators for each step

- **Improved**: Post-installation guidance:
  - Step-by-step browser extension setup
  - Canvas server startup instructions
  - Claude Code integration instructions
  - Available commands reference

### Fixed

#### Installer Issues
- **Fixed**: Python dependency installation now uses virtual environment
- **Fixed**: npm install failures now show appropriate warnings
- **Fixed**: Existing .env files are backed up before overwriting
- **Fixed**: Canvas port configuration properly integrated

#### Documentation Issues
- **Fixed**: Installation instructions now comprehensive and clear
- **Fixed**: API key acquisition instructions with direct links
- **Fixed**: Browser extension setup properly documented

### Technical Details

#### New Files
- `setup.js` (17 KB) - Interactive setup wizard
- `package.json` (501 bytes) - Root package configuration
- `SETUP_GUIDE.md` (11 KB) - Comprehensive setup guide
- `QUICK_SETUP.md` (3.7 KB) - Quick reference
- `SETUP_IMPLEMENTATION.md` - Implementation details
- `CHANGELOG_SETUP.md` - This changelog

#### Modified Files
- `install.ps1` - Enhanced Windows installer
- `install.sh` - Enhanced Unix/Mac installer
- `README.md` - Updated installation section

#### Features
- ES module support via package.json
- Color-coded terminal output
- Input validation and error handling
- Automatic workspace creation
- Configuration backup and recovery
- Cross-platform compatibility

### Breaking Changes

None. All changes are backwards compatible. Existing `.env` files are preserved and backed up before any modifications.

### Migration Guide

If you have an existing installation:

1. **Backup your current `.env` file** (installer does this automatically, but manual backup recommended)
2. **Pull latest changes** from the repository
3. **Run setup wizard** (optional):
   ```bash
   node setup.js
   ```
4. **Or keep existing configuration** - no action needed if you're happy with current setup

### Deprecation Notices

None.

### Security Notes

- API keys are never logged or displayed in console
- `.env` file permissions are preserved
- Backup files include timestamp to prevent overwrites
- Virtual environment isolates Python dependencies

### Known Issues

None identified. Please report issues at: https://github.com/Anit-1to10x/10x-outreach-skill/issues

### Contributors

This release includes contributions from the 10x-Team setup wizard implementation.

### Next Release Preview

Planned for next version:
- API key validation during setup
- Auto-detection of existing configurations
- Configuration profiles (save/load multiple setups)
- Integration testing during setup
- Video tutorial links

---

## Installation

To get the latest version with these improvements:

### One-Line Install

**Windows:**
```powershell
irm https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.ps1 | iex
```

**Mac/Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/Anit-1to10x/10x-outreach-skill/main/install.sh | bash
```

### Manual Update

```bash
cd ~/.claude-skills/10x-outreach
git pull origin main
node setup.js
```

---

## Support

- 📖 Setup Guide: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- 📝 Quick Setup: [QUICK_SETUP.md](QUICK_SETUP.md)
- 🐛 Report Issues: https://github.com/Anit-1to10x/10x-outreach-skill/issues
- 💬 Discussions: https://github.com/Anit-1to10x/10x-outreach-skill/discussions
