# ClaudeKit Universal Browser Extension

This directory contains the ClaudeKit Universal Browser Extension for Claude Code automation.

## 🔗 Standalone Repository

**The browser extension is now available as a standalone repository:**

📦 **GitHub**: https://github.com/Anit-1to10x/claudekit-browser-extension

### Why Standalone?

The extension has been moved to its own repository for:
- ✅ Independent versioning and releases
- ✅ Easier installation (single repo to clone)
- ✅ Chrome Web Store submission
- ✅ Dedicated issue tracking
- ✅ Cleaner dependency management

## 🚀 Quick Install

**Option 1: Use from this directory (current setup)**
```bash
# The extension is already here and works with this skill
# Just load it in Chrome as usual
```

**Option 2: Clone standalone repository (recommended)**
```bash
git clone https://github.com/Anit-1to10x/claudekit-browser-extension.git
cd claudekit-browser-extension
# Follow the README for installation
```

## 📚 Documentation

For complete documentation, visit the standalone repository:
- **README**: https://github.com/Anit-1to10x/claudekit-browser-extension#readme
- **Installation Guide**: https://github.com/Anit-1to10x/claudekit-browser-extension/blob/master/INSTALL.md
- **Getting Started**: https://github.com/Anit-1to10x/claudekit-browser-extension/blob/master/GETTING-STARTED.md
- **API Reference**: https://github.com/Anit-1to10x/claudekit-browser-extension/blob/master/README.md#api-reference

## ⚡ Quick Start (from here)

1. **Load extension in Chrome:**
   - Open `chrome://extensions`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select this directory

2. **Start WebSocket server:**
   ```bash
   cd ../../..  # Go to skill root
   cd canvas && npm start
   ```

3. **Extension connects automatically** to `ws://localhost:3000/ws`

## 🔄 Sync with Standalone

To update this directory with latest changes from standalone:
```bash
cd .claude/skills
rm -rf browser-extension
git clone https://github.com/Anit-1to10x/claudekit-browser-extension.git browser-extension
```

## 📦 What's Included Here

This directory contains a **complete copy** of the extension:
- ✅ manifest.json
- ✅ background.js (WebSocket service worker)
- ✅ content.js (DOM manipulation)
- ✅ handlers/ (LinkedIn, Instagram, Twitter, Google)
- ✅ popup/ (Extension UI)
- ✅ tests/ (35 test suite)

Everything works as-is. The standalone repository just provides:
- Better organization
- Independent versioning
- Easier updates
- Chrome Web Store support

---

**Repository maintained at**: https://github.com/Anit-1to10x/claudekit-browser-extension
