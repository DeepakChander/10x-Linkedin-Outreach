# Universal Browser Automation Extension for Claude Code

## Vision

Transform LinkedIn Lookback into a universal browser automation extension that:
- Works across ALL websites (LinkedIn, Instagram, Google, Twitter, etc.)
- Connects directly to Claude Code via native messaging
- Gives Claude Code full browser control (navigation, clicks, form filling, scraping)
- Tracks user activity across all sites for intelligent automation
- Real-time bidirectional communication

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code (CLI)                         │
│  - Receives commands from user                               │
│  - Sends automation instructions to extension                │
│  - Processes scraped data and makes decisions                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Native Messaging API
                  │ (JSON-RPC over stdio)
                  │
┌─────────────────▼───────────────────────────────────────────┐
│           Chrome Extension (Background Service Worker)       │
│  - Listens for Claude Code commands                          │
│  - Orchestrates content scripts                              │
│  - Manages state and storage                                 │
│  - Sends responses back to Claude Code                       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ Chrome Extension Messaging
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              Content Scripts (Injected into pages)           │
│  - LinkedIn: Profile tracking, connection automation         │
│  - Instagram: Post engagement, DM sending                    │
│  - Google: Search automation, SERP scraping                  │
│  - Twitter: Tweet posting, engagement                        │
│  - Generic: Universal DOM manipulation, data extraction      │
└──────────────────────────────────────────────────────────────┘
```

## Core Features

### 1. Universal Website Support

```javascript
// Config-driven website handlers
const SITE_HANDLERS = {
  'linkedin.com': {
    actions: ['track_profile_view', 'send_connection', 'send_message'],
    selectors: { /* LinkedIn-specific selectors */ }
  },
  'instagram.com': {
    actions: ['like_post', 'comment', 'send_dm', 'follow'],
    selectors: { /* Instagram-specific selectors */ }
  },
  'twitter.com': {
    actions: ['tweet', 'like', 'retweet', 'dm'],
    selectors: { /* Twitter-specific selectors */ }
  },
  'google.com': {
    actions: ['search', 'scrape_results'],
    selectors: { /* Google-specific selectors */ }
  },
  '*': {
    actions: ['click', 'type', 'scrape', 'navigate'],
    selectors: {} // Generic actions
  }
};
```

### 2. Native Messaging with Claude Code

```json
// manifest.json
{
  "name": "ClaudeKit Browser Controller",
  "description": "Universal browser automation extension for Claude Code",
  "manifest_version": 3,
  "permissions": [
    "nativeMessaging",
    "activeTab",
    "tabs",
    "storage",
    "cookies",
    "webNavigation",
    "webRequest"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"],
    "run_at": "document_idle"
  }]
}
```

### 3. Claude Code Integration

**Native Messaging Host (Node.js)**:
```javascript
// claude-browser-host.js
const { spawn } = require('child_process');
const readline = require('readline');

// Listen on stdin for messages from Chrome extension
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function sendMessage(message) {
  const buffer = Buffer.from(JSON.stringify(message));
  const header = Buffer.alloc(4);
  header.writeUInt32LE(buffer.length, 0);
  process.stdout.write(header);
  process.stdout.write(buffer);
}

rl.on('line', (line) => {
  try {
    const message = JSON.parse(line);

    // Handle commands from extension
    handleExtensionMessage(message);
  } catch (e) {
    sendMessage({ error: e.message });
  }
});

async function handleExtensionMessage(message) {
  switch (message.type) {
    case 'ACTIVITY_TRACKED':
      // Forward to Claude Code
      await notifyClaudeCode(message.data);
      break;
    case 'ACTION_COMPLETED':
      // Action completed, send response
      sendMessage({ success: true, result: message.result });
      break;
    case 'REQUEST_COMMAND':
      // Ask Claude Code what to do next
      const command = await getNextCommandFromClaude();
      sendMessage({ command });
      break;
  }
}
```

**Register Native Messaging Host**:
```json
// com.claudekit.browser.json (place in native messaging host directory)
{
  "name": "com.claudekit.browser",
  "description": "ClaudeKit Browser Controller Native Host",
  "path": "/path/to/claude-browser-host.js",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://YOUR_EXTENSION_ID/"
  ]
}
```

### 4. Command API

**From Claude Code → Extension**:
```javascript
// Example commands
{
  type: 'NAVIGATE',
  url: 'https://linkedin.com/in/john-doe'
}

{
  type: 'CLICK',
  selector: 'button.connect-button',
  wait_for: 'div.success-message'
}

{
  type: 'TYPE',
  selector: 'textarea.message-input',
  text: 'Hi John, I wanted to connect...'
}

{
  type: 'SCRAPE',
  selectors: {
    name: 'h1.profile-name',
    title: 'div.profile-title',
    company: 'a.company-link'
  }
}

{
  type: 'EXECUTE_WORKFLOW',
  workflow: 'linkedin_outreach',
  params: {
    profile_url: 'https://linkedin.com/in/jane-smith',
    message_template: 'connection_request_v1'
  }
}
```

**From Extension → Claude Code**:
```javascript
// Activity tracking
{
  type: 'PAGE_VISITED',
  url: 'https://instagram.com/user/johndoe',
  timestamp: '2026-01-22T12:00:00Z',
  data: { /* scraped profile data */ }
}

{
  type: 'ACTION_REQUEST',
  context: 'User viewed LinkedIn profile',
  profile_data: { /* extracted data */ },
  question: 'Should I send a connection request?'
}

{
  type: 'ERROR',
  action: 'CLICK',
  error: 'Element not found: button.connect-button'
}
```

## Implementation Plan

### Phase 1: Core Extension (Week 1)
- [ ] Upgrade manifest to v3
- [ ] Add universal content script
- [ ] Implement generic DOM manipulation
- [ ] Add activity tracking for all sites
- [ ] Create extension popup UI

### Phase 2: Native Messaging (Week 2)
- [ ] Create Node.js native host
- [ ] Implement bidirectional messaging
- [ ] Register native host with Chrome
- [ ] Test message passing

### Phase 3: Claude Code Integration (Week 3)
- [ ] Create Claude Code skill
- [ ] Implement command dispatcher
- [ ] Add workflow automation
- [ ] Build debugging tools

### Phase 4: Website Handlers (Week 4)
- [ ] LinkedIn handler (already exists)
- [ ] Instagram handler
- [ ] Twitter/X handler
- [ ] Google Search handler
- [ ] Generic website handler

## Usage Examples

### Example 1: Automated LinkedIn Outreach

In Claude Code:
```bash
claude> Execute LinkedIn outreach to 10 VPs in SaaS companies

# Claude Code:
1. Uses Exa AI to find target profiles
2. Sends commands to extension:
   - NAVIGATE to each profile
   - SCRAPE profile data
   - CLICK "Connect" button
   - TYPE personalized message
3. Tracks results and adjusts strategy
```

### Example 2: Instagram Content Research

```bash
claude> Research top 20 posts on #productmanagement on Instagram

# Claude Code:
1. Sends NAVIGATE command to Instagram
2. Searches for hashtag
3. SCRAPE top posts (images, captions, engagement)
4. Analyzes content patterns
5. Generates content recommendations
```

### Example 3: Google Search Automation

```bash
claude> Find and scrape 50 competitor websites

# Claude Code:
1. NAVIGATE to Google
2. TYPE search query
3. SCRAPE search results
4. For each result:
   - NAVIGATE to website
   - SCRAPE relevant data
   - Store in database
5. Generate competitive analysis report
```

### Example 4: Twitter Engagement

```bash
claude> Like and comment on 20 tweets about AI automation

# Claude Code:
1. NAVIGATE to Twitter search
2. TYPE search query "AI automation"
3. For each tweet:
   - SCRAPE tweet content
   - Generate relevant comment using LLM
   - CLICK like button
   - TYPE comment
   - Wait random delay
4. Track engagement metrics
```

## Security & Privacy

### User Consent
- Explicit permission for each website category
- Activity tracking can be paused/disabled
- Data never leaves user's machine without consent

### Rate Limiting
- Built-in rate limits for each platform
- Respects robots.txt and platform ToS
- Randomized delays to appear human-like

### Data Storage
- All data stored locally in IndexedDB
- Encrypted sensitive data (cookies, tokens)
- User can export/delete data anytime

## Configuration File

```yaml
# ~/.claude/browser-extension-config.yml

extension:
  enabled: true
  tracking:
    enabled: true
    sites: ['linkedin.com', 'instagram.com', 'twitter.com']

  automation:
    enabled: true
    rate_limits:
      linkedin:
        connection_requests: 15/day
        messages: 40/day
      instagram:
        likes: 100/day
        comments: 30/day
        follows: 50/day
      twitter:
        tweets: 10/day
        likes: 100/day

  security:
    require_confirmation: true # Ask before sensitive actions
    log_all_actions: true
    max_daily_actions: 500
```

## Extension File Structure

```
claude-browser-extension/
├── manifest.json
├── background.js           # Service worker
├── content.js              # Universal content script
├── popup/
│   ├── popup.html          # Extension popup UI
│   ├── popup.js
│   └── popup.css
├── handlers/
│   ├── linkedin.js         # LinkedIn-specific logic
│   ├── instagram.js        # Instagram-specific logic
│   ├── twitter.js          # Twitter-specific logic
│   ├── google.js           # Google-specific logic
│   └── generic.js          # Universal DOM manipulation
├── native-host/
│   ├── claude-browser-host.js    # Node.js native host
│   ├── install.sh                # Installation script
│   └── com.claudekit.browser.json # Native host manifest
├── utils/
│   ├── dom-utils.js        # DOM manipulation utilities
│   ├── scraper.js          # Data extraction utilities
│   └── rate-limiter.js     # Rate limiting logic
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## Next Steps

1. **Create universal extension** (expand from LinkedIn Lookback)
2. **Implement native messaging host** (Node.js)
3. **Build Claude Code skill** (command dispatcher)
4. **Add website handlers** (LinkedIn, Instagram, Twitter, Google)
5. **Create comprehensive docs** (setup, API, examples)
6. **Test thoroughly** (all platforms, edge cases)
7. **Publish** (Chrome Web Store + GitHub)

## Benefits Over Browser-Use

| Feature | Browser-Use | Claude Browser Extension |
|---------|-------------|-------------------------|
| Installation | Requires Docker | One-click Chrome extension |
| Performance | Spawns full browser | Lightweight extension |
| User Experience | Headless (hidden) | Visible, controllable |
| Data Persistence | Temporary | Persistent IndexedDB |
| Multi-tab Support | Limited | Full support |
| Cost | Cloud-based | 100% local |
| Speed | Slower (network) | Instant (local) |
| Debugging | Difficult | Chrome DevTools |

## License

MIT License - Open source for community contribution

---

**Status**: Planning → Implementation Ready
**Timeline**: 4 weeks to MVP
**Next Action**: Create universal extension files
