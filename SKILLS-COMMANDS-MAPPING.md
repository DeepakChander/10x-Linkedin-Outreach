# Skills and Commands Mapping for Claude Code

## Overview
This document maps all available slash commands to their corresponding skills, scripts, and execution flows. Claude Code uses this to understand how to execute each command.

---

## Command → Skill → Script Mapping

### 1. `/start` - Start Canvas App
**Command File:** `.claude/commands/start.md`
**Skill:** N/A (Direct execution)
**Script:** N/A (NPM command)
**Execution:**
```bash
cd canvas && npm run dev -- --port 3000
```
**What It Does:**
- Starts the visual workflow canvas on http://localhost:3000
- Enables WebSocket server for real-time updates
- Loads auto-save functionality

---

### 2. `/discover` - Discovery Engine
**Command File:** `.claude/commands/discover.md`
**Skill:** `.claude/skills/discovery-engine/SKILL.md`
**Script:** `.claude/scripts/discovery_engine.py`
**Execution Flow:**
1. Claude Code invokes `/discover` command
2. Loads discovery-engine skill
3. Executes `discovery_engine.py` with Exa AI
4. Returns list of discovered people
5. Saves to `output/discovery/`

**Input:** Search query (topic, role, company, etc.)
**Output:** JSON file with discovered profiles
**Example:**
```bash
/discover "AI startup founders in San Francisco"
```

---

### 3. `/outreach` - Email Outreach Campaign
**Command File:** `.claude/commands/outreach.md`
**Skill:** `.claude/skills/outreach-manager/SKILL.md`
**Script:** `.claude/scripts/send_campaign.py`
**Execution Flow:**
1. User provides Google Sheet URL with recipients
2. Skill loads `gmail_client.py` for OAuth2
3. Loads templates from `templates/`
4. Executes `send_campaign.py` to send emails
5. Tracks sent emails in `output/sent/`
6. Logs to `output/logs/`

**Dependencies:**
- `gmail_client.py` - Gmail API integration
- `sheets_reader.py` - Google Sheets reader
- `rate_limiter.py` - Professional rate limiting
- `template_loader.py` - Template management

**Input:** Google Sheet URL + template name
**Output:** Campaign report with sent/failed counts

---

### 4. `/compose` - Individual Email Composer
**Command File:** `.claude/commands/compose.md`
**Skill:** `.claude/skills/email-composer/SKILL.md`
**Script:** `.claude/scripts/gmail_client.py`
**Execution Flow:**
1. User requests to compose email
2. Claude drafts email based on context
3. Shows draft for approval
4. Sends via Gmail API
5. Logs sent email

**Input:** Recipient, subject, context
**Output:** Sent email confirmation

---

### 5. `/inbox` - Gmail Inbox Reader
**Command File:** `.claude/commands/inbox.md`
**Skill:** `.claude/skills/inbox-reader/SKILL.md`
**Script:** `.claude/scripts/inbox_reader.py`
**Execution Flow:**
1. Authenticates with Gmail API
2. Fetches recent emails (default: 10)
3. Parses sender, subject, date, snippet
4. Returns formatted list

**Input:** Number of emails (optional)
**Output:** List of recent emails with metadata

---

### 6. `/reply` - Email Reply Generator
**Command File:** `.claude/commands/reply.md`
**Skill:** `.claude/skills/reply-generator/SKILL.md`
**Script:** `.claude/scripts/reply_generator.py`
**Execution Flow:**
1. User specifies email to reply to
2. Claude reads original email context
3. Generates contextual reply
4. Shows draft for ONE approval
5. Sends without further confirmation

**Input:** Email ID or thread ID
**Output:** Sent reply confirmation

---

### 7. `/summarize` - Email Summarizer
**Command File:** `.claude/commands/summarize.md`
**Skill:** `.claude/skills/email-summarizer/SKILL.md`
**Script:** `.claude/scripts/email_summarizer.py`
**Execution Flow:**
1. Fetches emails from specified period
2. Categorizes by sender, topic, urgency
3. Generates concise summaries
4. Returns digest with key insights

**Input:** Time period (today, week, month)
**Output:** Categorized email digest

---

### 8. `/team` - Team Member Management
**Command File:** `.claude/commands/team.md`
**Skill:** `.claude/skills/team-manager/SKILL.md`
**Script:** `.claude/scripts/team_manager.py`
**Execution Flow:**
1. Manages team member credentials
2. Stores authenticated accounts per platform
3. Allows multi-user outreach campaigns
4. Tracks which team member sent what

**Operations:**
- Add team member
- Remove team member
- List team members
- Assign platform credentials

**Input:** Team member name + platform credentials
**Output:** Updated team roster

---

### 9. `/linkedin` - LinkedIn Automation
**Command File:** `.claude/commands/linkedin.md`
**Skill:** `.claude/skills/linkedin-adapter/SKILL.md`
**Script:** `.claude/scripts/linkedin_adapter.py`
**MCP Integration:** `mcp__browser-use__execute_skill`
**Execution Flow:**
1. User requests LinkedIn action (connect, message, like, comment)
2. Skill loads Browser-Use MCP
3. Authenticates with saved profile cookies
4. Executes browser automation
5. Applies rate limiting (24-48 hours between actions)
6. Returns execution result

**Available Actions:**
- View profile
- Send connection request
- Send message
- Like post
- Comment on post
- Endorse skills

**Input:** Target profile URL + action
**Output:** Execution confirmation

---

### 10. `/twitter` - Twitter/X Automation
**Command File:** `.claude/commands/twitter.md`
**Skill:** `.claude/skills/twitter-adapter/SKILL.md`
**Script:** `.claude/scripts/twitter_adapter.py`
**MCP Integration:** `mcp__browser-use__execute_skill`
**Execution Flow:**
1. User requests Twitter action (follow, DM, like, retweet)
2. Skill loads Browser-Use MCP
3. Authenticates with saved profile
4. Executes browser automation
5. Applies rate limiting (4-24 hours between DMs)
6. Returns execution result

**Available Actions:**
- Follow user
- Send DM
- Like tweet
- Retweet
- Quote tweet
- Reply to tweet

**Input:** Target profile/tweet URL + action
**Output:** Execution confirmation

---

### 11. `/instagram` - Instagram Automation
**Command File:** `.claude/commands/instagram.md`
**Skill:** `.claude/skills/instagram-adapter/SKILL.md`
**Script:** `.claude/scripts/instagram_adapter.py`
**MCP Integration:** `mcp__browser-use__execute_skill`
**Execution Flow:**
1. User requests Instagram action (follow, DM, like, comment)
2. Skill loads Browser-Use MCP
3. Authenticates with saved profile
4. Executes browser automation
5. Applies rate limiting (48-72 hours between DMs)
6. Returns execution result

**Available Actions:**
- Follow user
- Send DM
- Like post
- Comment on post
- Reply to story

**Input:** Target profile/post URL + action
**Output:** Execution confirmation

---

### 12. `/canvas` - Visual Workflow Builder
**Command File:** `.claude/commands/canvas.md`
**Skill:** `.claude/skills/canvas-workflow/SKILL.md`
**Execution Flow:**
1. Opens visual canvas at http://localhost:3000
2. Allows drag-and-drop workflow building
3. Claude can send commands via WebSocket
4. Workflow saved to `output/workflows/`

**WebSocket API:**
- `POST /api/canvas/command` - Send command
- `POST /api/canvas/commands/batch` - Batch commands
- `ws://localhost:3000/ws` - Real-time connection

**Input:** Workflow description
**Output:** Visual workflow on canvas

---

### 13. `/workflow create` - Create Workflow Visually
**Command File:** `.claude/commands/workflow.md`
**Skill:** `.claude/skills/workflow-engine/SKILL.md`
**Script:** `.claude/scripts/workflow_engine.py`
**Canvas Integration:** WebSocket API
**Execution Flow:**
1. Claude asks about workflow goals
2. Builds workflow structure
3. Sends commands to canvas via WebSocket:
   ```json
   { "type": "add-node", "payload": {...} }
   { "type": "add-connection", "payload": {...} }
   ```
4. Canvas renders workflow visually
5. User clicks "Run" to save
6. Workflow saved with intelligent name

**Example Workflow:**
```
[Discovery] → [LinkedIn View] → [Like Post] → [Connect] → [Follow on Twitter] → [Send Email]
```

**Input:** Workflow description (platforms, target audience, actions)
**Output:** Visual workflow + saved JSON

---

### 14. `/workflow run` - Execute Saved Workflow
**Command File:** `.claude/commands/workflow.md`
**Skill:** `.claude/skills/workflow-engine/SKILL.md`
**Script:** `.claude/scripts/workflow_engine.py`
**Execution Flow:**
1. Lists available workflows via `GET /api/workflows`
2. User selects workflow or defaults to latest
3. Loads workflow JSON
4. Executes each node sequentially:
   - Discovery nodes → `discovery_engine.py`
   - LinkedIn nodes → `linkedin_adapter.py`
   - Twitter nodes → `twitter_adapter.py`
   - Gmail nodes → `gmail_client.py`
5. Applies rate limiting between actions
6. Updates workflow status via `POST /api/workflow/:name/status`
7. Returns execution report

**Input:** Workflow name (or "latest")
**Output:** Execution report with success/failure counts

---

## Script Dependencies

### Core Scripts
All Python scripts located in `.claude/scripts/`:

1. **gmail_client.py** - Gmail API OAuth2 integration
2. **sheets_reader.py** - Google Sheets data reader
3. **inbox_reader.py** - Gmail inbox fetcher
4. **email_summarizer.py** - Email digest generator
5. **reply_generator.py** - Contextual email replies
6. **send_campaign.py** - Bulk email sender
7. **discovery_engine.py** - Exa AI search integration
8. **workflow_engine.py** - Workflow orchestrator
9. **linkedin_adapter.py** - LinkedIn automation
10. **twitter_adapter.py** - Twitter automation
11. **instagram_adapter.py** - Instagram automation
12. **team_manager.py** - Team credentials manager
13. **template_loader.py** - Email template loader
14. **rate_limiter.py** - Professional rate limiting
15. **canvas_client.py** - Canvas WebSocket client
16. **video_processor.py** - Video analysis (future)

### Shared Utilities
All scripts share common utilities:
- **Rate Limiter**: Prevents spam/detection
- **Logger**: Tracks all actions to `output/logs/`
- **Error Handler**: Graceful failure handling
- **Template System**: Consistent message formatting

---

## API Endpoints

### Canvas Server (Port 3000)

#### WebSocket
- `ws://localhost:3000/ws` - Real-time canvas updates

#### Canvas Commands
- `POST /api/canvas/command` - Send single command
- `POST /api/canvas/commands/batch` - Send multiple commands
- `GET /api/canvas/commands` - Poll for commands (legacy)
- `POST /api/canvas/clear` - Clear canvas

#### Workflow Management
- `POST /api/workflow/save` - Save workflow
- `GET /api/workflows` - List all workflows
- `GET /api/workflow/latest` - Get most recent workflow
- `GET /api/workflow/:name` - Get specific workflow
- `POST /api/workflow/:name/status` - Update workflow status

#### System
- `GET /api/status` - Server health
- `GET /health` - Health check

---

## MCP Tools Integration

### Browser-Use MCP Tools
Used by LinkedIn, Twitter, Instagram adapters:

1. **browser_task** - Execute browser actions
   - Opens browser in cloud
   - Navigates to platform
   - Performs action (click, type, etc.)
   - Returns result

2. **list_browser_profiles** - List authenticated profiles
   - Shows available browser profiles
   - Each profile has saved cookies/sessions
   - Used for platform authentication

3. **monitor_task** - Monitor task progress
   - Real-time status updates
   - Step-by-step execution tracking
   - Error reporting

4. **execute_skill** - Execute pre-built skills
   - Fast execution (milliseconds)
   - No browser overhead
   - Uses saved authentication

5. **get_cookies** - Get authentication cookies
   - Retrieves cookies from profile
   - Used for skill execution
   - Domain-specific filtering

---

## Environment Variables

All scripts use `.env` for configuration:

```env
# Gmail API
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
SENDER_EMAIL=your@gmail.com
SENDER_NAME=Your Name

# Exa AI (Discovery)
EXA_API_KEY=your_exa_key

# Rate Limiting
DEFAULT_DELAY_SECONDS=2
MAX_EMAILS_PER_DAY=50

# Logging
LOG_LEVEL=INFO
LOG_FILE=output/logs/outreach.log
```

---

## Workflow Execution Flow

### Example: Multi-Platform Outreach

**User Command:**
```
/workflow run latest
```

**Execution:**
1. Load workflow from `output/workflows/latest.json`
2. Parse nodes and connections
3. Execute in sequence:

```
Node 1: Discovery (Exa AI)
  └─> discovery_engine.py
  └─> Output: 50 profiles

Node 2: LinkedIn View Profile
  └─> linkedin_adapter.py
  └─> For each profile: View profile
  └─> Delay: 24 hours between views

Node 3: LinkedIn Like Recent Post
  └─> linkedin_adapter.py
  └─> For each profile: Like most recent post
  └─> Delay: 24 hours after view

Node 4: LinkedIn Send Connection
  └─> linkedin_adapter.py
  └─> For each profile: Send connection request
  └─> Delay: 24 hours after like

Node 5: Twitter Follow
  └─> twitter_adapter.py
  └─> For each profile: Follow on Twitter
  └─> Delay: 24 hours after LinkedIn connect

Node 6: Send Email
  └─> gmail_client.py
  └─> For each profile: Send personalized email
  └─> Delay: 48 hours after Twitter follow
```

4. Update workflow status to "completed"
5. Generate execution report
6. Save to `output/logs/workflow-execution-{timestamp}.log`

---

## Command Aliases

Claude Code understands these natural language variations:

### Start App
- "start my app"
- "start the app"
- "start canvas"
- "open workflow builder"
- "launch visual canvas"

### Discovery
- "find people"
- "discover profiles"
- "search for {topic}"
- "find {role} in {location}"

### Outreach
- "send email campaign"
- "run outreach"
- "email these people"
- "start campaign"

### Compose
- "write an email"
- "compose email to {person}"
- "draft email about {topic}"

### Inbox
- "check my inbox"
- "show recent emails"
- "what emails do I have?"

### Reply
- "reply to this email"
- "respond to {sender}"
- "answer this message"

### Summarize
- "summarize my emails"
- "email digest"
- "what are my important emails?"

### LinkedIn/Twitter/Instagram
- "connect with {person} on LinkedIn"
- "follow {person} on Twitter"
- "message {person} on Instagram"
- "like this post"
- "comment on this"

### Workflow
- "create a workflow for {goal}"
- "build automation for {task}"
- "run my latest workflow"
- "execute workflow {name}"

---

## Error Handling

All skills implement consistent error handling:

1. **Authentication Errors**
   - Gmail: Prompts for OAuth2 re-authentication
   - Social: Requests browser profile re-login
   - Solution: Run `python .claude/scripts/auth_setup.py`

2. **Rate Limit Errors**
   - Automatically applies exponential backoff
   - Logs warning to `output/logs/`
   - Continues execution with delays

3. **API Errors**
   - Retries up to 3 times
   - Logs error details
   - Skips failed item and continues

4. **Network Errors**
   - Pauses execution
   - Waits for connection restoration
   - Resumes from last successful action

---

## Logging

All actions logged to `output/logs/`:

**Log Format:**
```
[2026-01-22 14:30:00] [INFO] [discovery] Found 50 profiles for query "AI founders"
[2026-01-22 14:31:00] [INFO] [linkedin] Viewed profile: John Doe (https://linkedin.com/in/johndoe)
[2026-01-22 14:31:05] [WARN] [linkedin] Rate limit applied: 24 hour delay before next action
[2026-01-22 14:32:00] [INFO] [gmail] Email sent to john@example.com
[2026-01-22 14:32:05] [ERROR] [twitter] Failed to follow user: Network error
```

**Log Files:**
- `outreach.log` - Main outreach logs
- `workflow-{timestamp}.log` - Workflow execution logs
- `errors.log` - Error-only logs
- `rate-limiter.log` - Rate limiting events

---

## Quick Reference Table

| Command | Skill | Script | MCP | Output |
|---------|-------|--------|-----|--------|
| `/start` | N/A | N/A | No | Canvas server |
| `/discover` | discovery-engine | discovery_engine.py | No | JSON profiles |
| `/outreach` | outreach-manager | send_campaign.py | No | Campaign report |
| `/compose` | email-composer | gmail_client.py | No | Sent email |
| `/inbox` | inbox-reader | inbox_reader.py | No | Email list |
| `/reply` | reply-generator | reply_generator.py | No | Sent reply |
| `/summarize` | email-summarizer | email_summarizer.py | No | Email digest |
| `/team` | team-manager | team_manager.py | No | Team roster |
| `/linkedin` | linkedin-adapter | linkedin_adapter.py | Yes | Action result |
| `/twitter` | twitter-adapter | twitter_adapter.py | Yes | Action result |
| `/instagram` | instagram-adapter | instagram_adapter.py | Yes | Action result |
| `/canvas` | canvas-workflow | N/A | No | Visual canvas |
| `/workflow create` | workflow-engine | workflow_engine.py | No | Saved workflow |
| `/workflow run` | workflow-engine | workflow_engine.py | Yes | Execution report |

---

## Summary

**Total Commands:** 13
**Total Skills:** 14
**Total Scripts:** 16
**MCP Integration:** 3 platforms (LinkedIn, Twitter, Instagram)
**API Endpoints:** 12
**WebSocket Channels:** 1

Every command is fully mapped to its execution path, allowing Claude Code to:
1. Understand user intent from natural language
2. Load appropriate skill
3. Execute correct script
4. Apply rate limiting
5. Return formatted results
6. Log all actions

The system is production-ready with comprehensive error handling, professional rate limiting, and full workflow automation capabilities.
