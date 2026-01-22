---
name: lookback
description: LinkedIn Lookback integration - track LinkedIn activity and automate follow-ups
---

# /lookback Command

Integrates LinkedIn Lookback Chrome extension with 10x-Team for intelligent lead tracking and automated workflows.

## Usage

```
/lookback [action] [options]
```

### Actions

#### `/lookback sync`
Sync activity data from LinkedIn Lookback extension to 10x-Team.

**What it does:**
- Exports data from browser IndexedDB
- Imports into 10x-Team database
- Identifies new leads and prospects
- Triggers automated workflows

**Example:**
```bash
/lookback sync
```

#### `/lookback enrich [profile_url]`
Enrich LinkedIn profiles with additional data using Exa AI.

**Parameters:**
- `profile_url`: LinkedIn profile URL (optional, enriches all recent if omitted)

**What it does:**
- Fetches profile data from Lookback
- Discovers context via Exa AI
- Extracts company info, tech stack, recent posts
- Updates prospect database

**Example:**
```bash
/lookback enrich https://linkedin.com/in/john-doe
/lookback enrich  # Enrich all recent profiles
```

#### `/lookback campaign [activity_type]`
Create automated outreach campaign from Lookback activity.

**Parameters:**
- `activity_type`: `profile_view` | `connection_request` | `message_sent` | `all`

**What it does:**
- Filters activities by type
- Segments leads based on engagement
- Creates personalized outreach sequences
- Sets up follow-up automation

**Example:**
```bash
/lookback campaign profile_view
/lookback campaign connection_request
/lookback campaign all
```

#### `/lookback stats [period]`
View LinkedIn activity statistics and insights.

**Parameters:**
- `period`: `today` | `week` | `month` | `all` (default: week)

**What it does:**
- Shows activity breakdown (views, connections, messages)
- Prospect interaction rate
- Top companies/titles engaged
- Conversion metrics

**Example:**
```bash
/lookback stats week
/lookback stats month
```

#### `/lookback check [profile_url]`
Check if you've previously interacted with a LinkedIn profile.

**Parameters:**
- `profile_url`: LinkedIn profile URL (required)

**What it does:**
- Searches Lookback history
- Shows all previous interactions
- Displays last contact date
- Recommends follow-up actions

**Example:**
```bash
/lookback check https://linkedin.com/in/jane-smith
```

## Installation

### Step 1: Install LinkedIn Lookback Extension

1. Clone the repository:
```bash
git clone https://github.com/kvivek0591/linkedin-lookback.git
```

2. Load in Chrome:
   - Go to `chrome://extensions`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `linkedin-lookback` folder

### Step 2: Activate Integration

```bash
/lookback sync
```

This sets up:
- Data sync infrastructure
- Automation workflows
- Prospect enrichment
- Campaign tracking

## Automation Workflows

### Profile Visit → Connection Request
```
Trigger: Profile visit detected
Wait: 24 hours
Check: Not already connected
Action: Send personalized connection request
Rate Limit: 20 connections/day
```

### Connection Accepted → Intro Message
```
Trigger: Connection request accepted
Wait: 48 hours
Check: No prior messages sent
Action: Send introduction message
Rate Limit: 50 messages/day
```

### No Reply → Email Escalation
```
Trigger: LinkedIn message sent
Wait: 5 days
Check: No reply received
Action: Send email via Gmail
```

### Warm Lead Identification
```
Trigger: Multiple profile visits (3+ times)
Analysis: Engagement pattern recognition
Action: Add to high-priority outreach list
```

## Best Practices

1. **Respect LinkedIn Limits**
   - Max 20 connection requests/day
   - Max 50 messages/day
   - Maintain human-like patterns

2. **Personalization**
   - Use profile data for context
   - Reference shared connections
   - Mention company/industry

3. **Multi-Touch Strategy**
   - Combine LinkedIn + Email + Twitter
   - Space out touchpoints (24-48h)
   - Track response rates

4. **Data Privacy**
   - All data stored locally
   - No external servers
   - User controls tracking
   - GDPR compliant

## Troubleshooting

### Extension Not Tracking
1. Check if extension is enabled: `chrome://extensions`
2. Verify tracking toggle is ON in extension popup
3. Refresh LinkedIn page
4. Check browser console for errors

### Sync Failing
1. Ensure extension is installed and active
2. Check IndexedDB browser permissions
3. Verify Node.js environment setup
4. Review sync script logs

### Automation Not Triggering
1. Confirm workflows are enabled
2. Check rate limits not exceeded
3. Verify integration credentials (Gmail, LinkedIn)
4. Review automation logs

## References

- [LinkedIn Lookback GitHub](https://github.com/kvivek0591/linkedin-lookback)
- [LinkedIn Rate Limits](./../skills/linkedin-lookback/references/linkedin-rate-limits.md)
- [Automation Best Practices](./../skills/linkedin-lookback/references/automation-best-practices.md)
