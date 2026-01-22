# LinkedIn Lookback Integration - Quick Start

## Installation

### 1. Install LinkedIn Lookback Extension

```bash
# Clone the extension
cd ~
git clone https://github.com/kvivek0591/linkedin-lookback.git

# Load in Chrome
# 1. Go to chrome://extensions
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select the linkedin-lookback folder
```

### 2. Use LinkedIn Normally
- Visit profiles you're interested in
- Send connection requests
- Send messages
- Extension tracks everything automatically

### 3. Sync Data to 10x-Team

```bash
# In Claude Code
/linkedin-lookback:sync

# Or manually run
node .claude/skills/linkedin-lookback/scripts/sync-lookback-data.js
```

## Quick Commands

```bash
# Sync activity data
/lookback:sync

# Enrich prospects with Exa AI
/lookback:enrich --recent 7d

# Create outreach campaign
/lookback:campaign profile_view

# Check interaction history
/lookback:check https://linkedin.com/in/john-doe

# View statistics
/lookback:stats week
```

## Integration Benefits

1. **Lead Intelligence**: Track profile visits → Identify warm leads → Auto-qualify
2. **Smart Follow-up**: Automated sequences based on activity
3. **Prospect Enrichment**: Combine LinkedIn data + Exa AI for deeper insights
4. **Campaign Attribution**: Connect LinkedIn activity → Conversions
5. **Anti-Spam**: Check history before outreach

## File Structure

```
.claude/skills/linkedin-lookback/
├── SKILL.md                     # Full documentation
├── README.md                     # This file (quick start)
├── scripts/
│   ├── sync-lookback-data.js    # Export from extension → Import to database
│   ├── enrich-prospects.js      # Enrich with Exa AI
│   ├── campaign-generator.js    # Create automated campaigns
│   └── interaction-checker.js   # Check interaction history
└── references/
    ├── linkedin-rate-limits.md          # LinkedIn limits & best practices
    ├── automation-best-practices.md     # Comprehensive automation guide
    └── message-templates.md             # Outreach templates
```

## Data Flow

```
LinkedIn Activity (Manual)
    ↓
Lookback Extension (Browser Storage)
    ↓
sync-lookback-data.js (Export)
    ↓
10x-Team Database (Local JSON)
    ↓
enrich-prospects.js (Exa AI)
    ↓
campaign-generator.js (Automation)
    ↓
LinkedIn/Email Outreach (via 10x-Team)
```

## Environment Variables

Add to `~/10x-skill-workspace/.env`:

```env
# Required for prospect enrichment
EXA_API_KEY=your_exa_api_key

# Required for Gmail follow-up
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_secret
SENDER_EMAIL=your@gmail.com
```

## Support

- Full Documentation: [SKILL.md](./SKILL.md)
- Rate Limits: [references/linkedin-rate-limits.md](./references/linkedin-rate-limits.md)
- Best Practices: [references/automation-best-practices.md](./references/automation-best-practices.md)
- LinkedIn Lookback GitHub: https://github.com/kvivek0591/linkedin-lookback

## License

MIT License
