# 100X OUTREACH SYSTEM - ARCHITECTURE PLAN

## Executive Summary

Transform the current email-only outreach system into a **comprehensive multi-platform, multi-user outreach automation platform** with intelligent people discovery, workflow orchestration, and enterprise-grade rate limiting.

---

## Current State vs Future State

| Aspect | Current (10x) | Future (100x) |
|--------|---------------|---------------|
| Platforms | Gmail only | LinkedIn, Twitter/X, Instagram, Gmail |
| Users | Single user | Multi-user team support |
| Discovery | Manual (Google Sheets) | AI-powered (Exa AI) |
| Workflow | Simple send | Complex multi-step workflows |
| Rate Limiting | Basic (60s delay) | Intelligent (platform-specific, human-like) |
| Scheduling | None | Daily campaigns, time zones |

---

## NEW ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│                        100X OUTREACH SYSTEM                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   EXA AI     │    │   WORKFLOW   │    │    TEAM      │          │
│  │   DISCOVERY  │───▶│    ENGINE    │◀───│  MANAGEMENT  │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                    │                  │
│         ▼                   ▼                    ▼                  │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │                  PLATFORM ADAPTERS                       │       │
│  ├─────────┬─────────┬─────────┬─────────┬────────────────┤       │
│  │LinkedIn │ Twitter │Instagram│  Gmail  │ Future...      │       │
│  │ Adapter │ Adapter │ Adapter │ Adapter │                │       │
│  └─────────┴─────────┴─────────┴─────────┴────────────────┘       │
│         │         │         │         │                            │
│         ▼         ▼         ▼         ▼                            │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │              BROWSER-USE MCP + NATIVE APIs              │       │
│  │  (Authenticated browser sessions for each platform)      │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │    RATE      │    │   CAMPAIGN   │    │   LOGGING    │          │
│  │   LIMITER    │    │   TRACKER    │    │  & REPORTS   │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## COMPONENT DETAILS

### 1. EXA AI DISCOVERY ENGINE

**Purpose:** Find relevant people to reach out to based on topics/communities

**Integration:**
```json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server", "tools=web_search_exa,linkedin_search_exa,company_research_exa,deep_researcher_start,deep_researcher_check"],
      "env": {
        "EXA_API_KEY": "${EXA_API_KEY}"
      }
    }
  }
}
```

**Capabilities:**
- `linkedin_search_exa` - Find people on LinkedIn by role, company, industry
- `company_research_exa` - Research companies before outreach
- `web_search_exa` - Find Twitter/X profiles, blogs, etc.
- `deep_researcher` - Complex multi-source research

**Workflow:**
```
User: "Find 10 AI startup founders in San Francisco"
         │
         ▼
┌─────────────────────────────────────┐
│ EXA AI Discovery                    │
│ - linkedin_search: "AI startup      │
│   founder San Francisco"            │
│ - company_research: each company    │
│ - web_search: Twitter handles       │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Returns structured data:            │
│ - Name, Title, Company              │
│ - LinkedIn URL                      │
│ - Twitter handle (if found)         │
│ - Email (if public)                 │
│ - Recent posts/interests            │
└─────────────────────────────────────┘
```

---

### 2. TEAM & CREDENTIAL MANAGEMENT

**Structure:**
```
credentials/
├── team.json                    # Team configuration
├── profiles/
│   ├── john/
│   │   ├── profile.json        # User settings
│   │   ├── linkedin.json       # LinkedIn cookies/session
│   │   ├── twitter.json        # Twitter auth
│   │   ├── instagram.json      # Instagram auth
│   │   └── gmail_token.pickle  # Gmail OAuth
│   ├── sarah/
│   │   └── ...
│   └── mike/
│       └── ...
└── browser_profiles/            # Browser-use profile IDs
    ├── john_linkedin.txt
    ├── john_twitter.txt
    └── ...
```

**team.json Schema:**
```json
{
  "team_name": "Acme Outreach Team",
  "members": [
    {
      "id": "john",
      "name": "John Doe",
      "email": "john@acme.com",
      "platforms": {
        "linkedin": {
          "enabled": true,
          "profile_url": "linkedin.com/in/johndoe",
          "browser_profile_id": "uuid-from-browser-use",
          "daily_limit": 50,
          "hourly_limit": 10
        },
        "twitter": {
          "enabled": true,
          "handle": "@johndoe",
          "browser_profile_id": "uuid-from-browser-use",
          "daily_limit": 100,
          "hourly_limit": 20
        },
        "instagram": {
          "enabled": true,
          "handle": "@johndoe",
          "browser_profile_id": "uuid-from-browser-use",
          "daily_limit": 30,
          "hourly_limit": 5
        },
        "gmail": {
          "enabled": true,
          "email": "john@gmail.com",
          "daily_limit": 100
        }
      },
      "timezone": "America/Los_Angeles",
      "active_hours": {"start": "09:00", "end": "18:00"}
    }
  ]
}
```

**New Skill: `team-manager`**
```
/team add <name>           # Add team member
/team setup <name>         # Setup credentials for member
/team list                 # List all team members
/team status               # Show platform auth status
/team limits               # Show/edit rate limits
```

---

### 3. MULTI-PLATFORM ADAPTERS

Each platform has a dedicated adapter using **Browser-Use MCP** for authenticated sessions.

#### LinkedIn Adapter
```python
class LinkedInAdapter:
    """Uses Browser-Use MCP with authenticated profile"""

    async def connect(self, profile_url: str) -> bool
    async def send_connection_request(self, target_url: str, note: str) -> Dict
    async def send_message(self, target_url: str, message: str) -> Dict
    async def view_profile(self, target_url: str) -> Dict
    async def like_post(self, post_url: str) -> Dict
    async def comment_post(self, post_url: str, comment: str) -> Dict
    async def create_post(self, content: str, image_path: str = None) -> Dict
```

#### Twitter/X Adapter
```python
class TwitterAdapter:
    """Uses Browser-Use MCP with authenticated profile"""

    async def send_dm(self, username: str, message: str) -> Dict
    async def follow_user(self, username: str) -> Dict
    async def like_tweet(self, tweet_url: str) -> Dict
    async def reply_tweet(self, tweet_url: str, message: str) -> Dict
    async def create_tweet(self, content: str, media_path: str = None) -> Dict
    async def retweet(self, tweet_url: str) -> Dict
```

#### Instagram Adapter
```python
class InstagramAdapter:
    """Uses Browser-Use MCP with authenticated profile"""

    async def send_dm(self, username: str, message: str) -> Dict
    async def follow_user(self, username: str) -> Dict
    async def like_post(self, post_url: str) -> Dict
    async def comment_post(self, post_url: str, comment: str) -> Dict
    async def create_post(self, content: str, image_path: str) -> Dict
```

---

### 4. WORKFLOW ENGINE

**Core Concept:** Define multi-step, multi-platform outreach sequences with approval gates.

#### Workflow Definition Schema:
```yaml
# workflows/ai_founders_outreach.yaml
name: "AI Founders Outreach Campaign"
description: "Connect with AI startup founders"
version: "1.0"

# Discovery phase
discovery:
  source: "exa"
  query: "AI startup founders Series A San Francisco"
  max_results: 10
  filters:
    - has_linkedin: true
    - company_size: "10-50"

# Execution phases
phases:
  - name: "warm_up"
    platform: "linkedin"
    action: "view_profile"
    delay_after: "2-5 minutes"

  - name: "engage"
    platform: "linkedin"
    action: "like_recent_post"
    delay_after: "1-3 hours"
    condition: "has_recent_posts"

  - name: "connect"
    platform: "linkedin"
    action: "send_connection_request"
    template: "templates/linkedin/connect_ai_founder.txt"
    delay_after: "24-48 hours"

  - name: "follow_twitter"
    platform: "twitter"
    action: "follow"
    condition: "has_twitter"
    delay_after: "2-4 hours"

  - name: "message"
    platform: "linkedin"
    action: "send_message"
    template: "templates/linkedin/intro_message.txt"
    condition: "connection_accepted"
    delay_after: "24-72 hours"

# Rate limiting
rate_limits:
  linkedin:
    connections_per_day: 20
    messages_per_day: 50
    min_delay_seconds: 120
    max_delay_seconds: 300
  twitter:
    follows_per_day: 50
    dms_per_day: 30
    min_delay_seconds: 60
    max_delay_seconds: 180

# Schedule
schedule:
  days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
  hours: {"start": "09:00", "end": "17:00"}
  timezone: "America/Los_Angeles"
```

#### Workflow Engine Features:

1. **Discovery Integration**
   - Pull targets from Exa AI search
   - Enrich with company research
   - Cross-reference platforms (find Twitter from LinkedIn, etc.)

2. **Multi-Phase Execution**
   - Warm-up actions (view profile, like posts)
   - Engagement actions (comment, share)
   - Connection actions (connect, follow)
   - Outreach actions (message, DM)

3. **Smart Delays**
   - Randomized delays (human-like)
   - Platform-specific limits
   - Time-of-day awareness
   - Pause between phases

4. **Conditional Logic**
   - Skip if no Twitter found
   - Wait for connection acceptance
   - Retry on failure

5. **Progress Tracking**
   - Per-target status
   - Phase completion
   - Success/failure rates

---

### 5. RATE LIMITER (Anti-Spam)

**Philosophy:** Act like a human, not a bot

```python
class IntelligentRateLimiter:
    """Human-like rate limiting with platform awareness"""

    PLATFORM_LIMITS = {
        "linkedin": {
            "connections_per_day": 20,      # LinkedIn's soft limit
            "messages_per_day": 50,
            "profile_views_per_day": 100,
            "min_delay_seconds": 120,       # 2 minutes minimum
            "max_delay_seconds": 600,       # 10 minutes maximum
            "hourly_burst_limit": 10,
            "cool_down_after_burst": 1800   # 30 min after burst
        },
        "twitter": {
            "follows_per_day": 50,
            "dms_per_day": 50,
            "tweets_per_day": 20,
            "min_delay_seconds": 60,
            "max_delay_seconds": 300,
            "hourly_burst_limit": 15
        },
        "instagram": {
            "follows_per_day": 30,
            "dms_per_day": 30,
            "likes_per_day": 100,
            "min_delay_seconds": 90,
            "max_delay_seconds": 400,
            "hourly_burst_limit": 8
        },
        "gmail": {
            "emails_per_day": 100,
            "min_delay_seconds": 60,
            "max_delay_seconds": 120
        }
    }

    def calculate_delay(self, platform: str, action_type: str) -> int:
        """Calculate human-like delay with randomization"""
        base = self.PLATFORM_LIMITS[platform]
        min_delay = base["min_delay_seconds"]
        max_delay = base["max_delay_seconds"]

        # Add randomization (gaussian distribution)
        delay = random.gauss((min_delay + max_delay) / 2, (max_delay - min_delay) / 4)
        delay = max(min_delay, min(max_delay, delay))

        # Add extra delay if approaching limits
        if self.is_approaching_limit(platform, action_type):
            delay *= 2

        # Add time-of-day variation
        delay *= self.get_time_factor()

        return int(delay)

    def can_proceed(self, user_id: str, platform: str, action: str) -> Tuple[bool, str]:
        """Check if action is allowed within rate limits"""
        # Check daily limits
        # Check hourly burst limits
        # Check cool-down periods
        # Return (allowed, reason_if_not)
```

**Rate Limiting Features:**
- Per-user, per-platform tracking
- Daily and hourly limits
- Burst detection and cool-down
- Randomized delays (gaussian distribution)
- Time-of-day awareness
- Automatic pause when approaching limits

---

### 6. NEW DIRECTORY STRUCTURE

```
10x-Outreach-Skill/
├── .claude/
│   ├── agents/
│   │   ├── email-planner.md
│   │   ├── email-executor.md
│   │   ├── discovery-agent.md          # NEW: Exa AI discovery
│   │   ├── workflow-planner.md         # NEW: Workflow planning
│   │   └── workflow-executor.md        # NEW: Multi-platform execution
│   │
│   ├── skills/
│   │   ├── outreach-manager/           # Enhanced
│   │   ├── inbox-reader/
│   │   ├── email-composer/
│   │   ├── reply-generator/
│   │   ├── email-summarizer/
│   │   ├── template-manager/
│   │   ├── team-manager/               # NEW: Team/credential management
│   │   ├── discovery-engine/           # NEW: Exa AI people finder
│   │   ├── linkedin-outreach/          # NEW: LinkedIn operations
│   │   ├── twitter-outreach/           # NEW: Twitter operations
│   │   ├── instagram-outreach/         # NEW: Instagram operations
│   │   └── workflow-engine/            # NEW: Multi-step workflows
│   │
│   └── commands/
│       ├── outreach.md                 # Enhanced
│       ├── inbox.md
│       ├── compose.md
│       ├── reply.md
│       ├── summarize.md
│       ├── team.md                     # NEW
│       ├── discover.md                 # NEW
│       ├── workflow.md                 # NEW
│       ├── linkedin.md                 # NEW
│       ├── twitter.md                  # NEW
│       └── instagram.md                # NEW
│
├── scripts/
│   ├── gmail_client.py
│   ├── sheets_reader.py
│   ├── inbox_reader.py
│   ├── email_summarizer.py
│   ├── reply_generator.py
│   ├── send_campaign.py
│   ├── auth_setup.py
│   ├── team_manager.py                 # NEW
│   ├── discovery_engine.py             # NEW
│   ├── linkedin_adapter.py             # NEW
│   ├── twitter_adapter.py              # NEW
│   ├── instagram_adapter.py            # NEW
│   ├── workflow_engine.py              # NEW
│   ├── rate_limiter.py                 # NEW
│   └── campaign_tracker.py             # NEW
│
├── workflows/                           # NEW: Workflow definitions
│   ├── examples/
│   │   ├── ai_founders.yaml
│   │   ├── saas_outreach.yaml
│   │   └── investor_connect.yaml
│   └── custom/
│
├── templates/
│   ├── outreach/
│   ├── promotional/
│   ├── follow-up/
│   ├── newsletter/
│   ├── custom/
│   ├── linkedin/                        # NEW
│   │   ├── connection_request.txt
│   │   ├── intro_message.txt
│   │   └── follow_up.txt
│   ├── twitter/                         # NEW
│   │   ├── dm_intro.txt
│   │   └── reply_template.txt
│   └── instagram/                       # NEW
│       ├── dm_intro.txt
│       └── comment_template.txt
│
├── credentials/                         # NEW: Multi-user credentials
│   ├── team.json
│   └── profiles/
│
├── campaigns/                           # NEW: Campaign tracking
│   ├── active/
│   ├── completed/
│   └── logs/
│
└── output/
    ├── logs/
    ├── sent/
    ├── drafts/
    └── reports/
```

---

### 7. NEW SLASH COMMANDS

| Command | Purpose |
|---------|---------|
| `/team` | Manage team members and credentials |
| `/discover` | Find people using Exa AI |
| `/workflow` | Create, run, monitor workflows |
| `/linkedin` | LinkedIn-specific operations |
| `/twitter` | Twitter-specific operations |
| `/instagram` | Instagram-specific operations |
| `/campaign` | View campaign status and analytics |

---

### 8. WORKFLOW EXAMPLE: DAILY OUTREACH

**User Request:**
> "Every day at 9 AM, find 10 AI developers in NYC and reach out on LinkedIn and Twitter"

**System Creates:**
```yaml
name: "Daily AI Developer Outreach"
schedule:
  frequency: "daily"
  time: "09:00"
  timezone: "America/New_York"

discovery:
  source: "exa"
  query: "AI developer machine learning engineer New York City"
  max_results: 10

phases:
  - platform: "linkedin"
    actions:
      - view_profile (delay: 2-5 min)
      - like_post (delay: 1-2 hours)
      - connect (delay: 4-8 hours)

  - platform: "twitter"
    actions:
      - follow (delay: 2-4 hours after linkedin)
      - like_tweet (delay: 1-2 hours)
```

**Approval Flow:**
```
┌────────────────────────────────────────────────────────────┐
│ WORKFLOW APPROVAL REQUEST                                   │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ Campaign: Daily AI Developer Outreach                       │
│ Schedule: Daily at 9:00 AM EST                             │
│                                                             │
│ Discovery: Exa AI search for AI developers in NYC          │
│ Targets: 10 people per day                                 │
│                                                             │
│ Actions per target:                                        │
│ ├─ LinkedIn: View profile → Like post → Connect            │
│ └─ Twitter: Follow → Like tweet                            │
│                                                             │
│ Rate Limits:                                               │
│ ├─ LinkedIn: 20 connections/day, 2-5 min delays           │
│ └─ Twitter: 50 follows/day, 1-2 hour delays               │
│                                                             │
│ Estimated daily time: ~4 hours of background activity      │
│                                                             │
│ Team Member: John (using his authenticated accounts)       │
│                                                             │
│ ─────────────────────────────────────────────────────────  │
│ Type 'APPROVE' to start this daily campaign                │
│ Type 'EDIT' to modify settings                             │
│ Type 'CANCEL' to discard                                   │
└────────────────────────────────────────────────────────────┘
```

---

### 9. IMPLEMENTATION PHASES

#### Phase 1: Foundation (Week 1-2)
- [ ] Set up Exa AI MCP integration
- [ ] Create team management system
- [ ] Build credential storage structure
- [ ] Create basic rate limiter

#### Phase 2: Platform Adapters (Week 3-4)
- [ ] LinkedIn adapter (using Browser-Use MCP)
- [ ] Twitter adapter (using Browser-Use MCP)
- [ ] Instagram adapter (using Browser-Use MCP)
- [ ] Test authenticated sessions

#### Phase 3: Discovery Engine (Week 5)
- [ ] Exa AI discovery skill
- [ ] People enrichment (cross-platform)
- [ ] Target list management
- [ ] `/discover` command

#### Phase 4: Workflow Engine (Week 6-7)
- [ ] Workflow definition schema
- [ ] Workflow parser and validator
- [ ] Multi-phase executor
- [ ] Progress tracking
- [ ] `/workflow` command

#### Phase 5: Integration & Polish (Week 8)
- [ ] Connect all components
- [ ] Campaign analytics
- [ ] Error handling
- [ ] Documentation
- [ ] Example workflows

---

### 10. SAFETY & COMPLIANCE

1. **Rate Limiting** - Stay well below platform limits
2. **Human-like Behavior** - Randomized delays, natural timing
3. **Single Approval** - User approves entire workflow once
4. **Full Logging** - Audit trail for all actions
5. **Pause/Cancel** - Ability to stop campaigns instantly
6. **No Spam** - Personalized messages, relevant targeting
7. **Respect Opt-outs** - Track and honor "don't contact" requests
8. **Credential Security** - Encrypted storage, no plaintext

---

## SUMMARY

This 100x upgrade transforms your email outreach tool into a **comprehensive multi-platform outreach automation system** with:

- **Intelligent Discovery** via Exa AI
- **Multi-Platform Support** (LinkedIn, Twitter, Instagram, Gmail)
- **Team Collaboration** with per-user credentials
- **Workflow Automation** with multi-step campaigns
- **Human-like Rate Limiting** to avoid detection
- **Single Approval Model** for efficient operation

The system maintains the same philosophy of your current tool:
> **Plan → Approve ONCE → Execute Autonomously**

But now across multiple platforms with intelligent people discovery!
