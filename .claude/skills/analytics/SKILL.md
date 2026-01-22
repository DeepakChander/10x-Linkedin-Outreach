---
name: analytics
description: |
  Campaign and outreach analytics skill. Use this skill when the user wants to view
  performance metrics, campaign statistics, or analyze outreach effectiveness.
  Provides insights on email open rates, response rates, and platform engagement.
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---

# Analytics Skill

Provides comprehensive analytics and reporting for the 10x Outreach System.

## When to Use This Skill

Use this skill when the user:
- Wants to see campaign performance metrics
- Asks about email open/click/response rates
- Needs outreach effectiveness analysis
- Wants to compare campaign performance
- Requests statistics or reports

## When NOT to Use This Skill

Do NOT use this skill for:
- Sending emails → use `outreach-manager`
- Creating campaigns → use `workflow-engine`
- Finding people → use `discovery-engine`

## Capabilities

1. **Campaign Metrics** - Track emails sent, opened, clicked, replied
2. **Platform Analytics** - LinkedIn, Twitter, Instagram engagement stats
3. **Response Analysis** - Reply rates, sentiment, conversion tracking
4. **Trend Reports** - Daily, weekly, monthly performance trends
5. **Comparative Analysis** - Compare campaigns, templates, approaches

## MCP Integration Guidelines

### Primary MCP: None (Internal Analytics)
This skill primarily uses internal log analysis and metrics collection.

### When to Use MCPs

| Operation | MCP | Tool |
|-----------|-----|------|
| Email tracking | Gmail | Check replies via `inbox-reader` |
| Web research | Exa | Competitor analysis |
| Browser metrics | Browser-Use | Social platform stats |

### Analytics Data Sources

| Source | Location | Data Type |
|--------|----------|-----------|
| Campaign logs | `output/logs/campaigns/` | Email sends, results |
| Tool usage | `output/logs/tool-usage/` | MCP/tool call metrics |
| Workflows | `campaigns/completed/` | Workflow execution data |
| Rate limits | In-memory | Current rate status |

## Commands Reference

### View Campaign Statistics

```bash
python .claude/scripts/analytics.py campaign --id CAMPAIGN_ID
```

### View Daily Summary

```bash
python .claude/scripts/analytics.py daily --date 2024-01-15
```

### View Weekly Report

```bash
python .claude/scripts/analytics.py weekly
```

### Export Report

```bash
python .claude/scripts/analytics.py export --format csv --output report.csv
```

## Metrics Tracked

### Email Metrics
- **Sent** - Total emails sent
- **Delivered** - Successfully delivered
- **Bounced** - Delivery failures
- **Opened** - Opened by recipient (if tracking enabled)
- **Clicked** - Link clicks (if tracking enabled)
- **Replied** - Responses received

### Platform Metrics
- **LinkedIn** - Connections sent/accepted, messages sent/replied, profile views
- **Twitter** - Follows, DMs sent/replied, likes, retweets
- **Instagram** - Follows, DMs sent/replied, likes, comments

### Workflow Metrics
- **Started** - Workflows initiated
- **Completed** - Successfully finished
- **Failed** - Errors encountered
- **Duration** - Time to completion

## Report Templates

### Campaign Summary
```
═══════════════════════════════════════════════════════════════
                    CAMPAIGN ANALYTICS
═══════════════════════════════════════════════════════════════

📊 CAMPAIGN: [Campaign Name]
📅 PERIOD: [Start Date] - [End Date]

EMAIL PERFORMANCE:
┌─────────────┬──────────┬─────────┐
│ Metric      │ Count    │ Rate    │
├─────────────┼──────────┼─────────┤
│ Sent        │ 100      │ 100%    │
│ Delivered   │ 98       │ 98%     │
│ Opened      │ 45       │ 45%     │
│ Clicked     │ 12       │ 12%     │
│ Replied     │ 8        │ 8%      │
└─────────────┴──────────┴─────────┘

BEST PERFORMING:
- Template: "partnership_intro" (52% open rate)
- Subject: "Quick question about..." (48% open rate)
- Day: Tuesday (highest engagement)
- Time: 10:00 AM PST (best response rate)

═══════════════════════════════════════════════════════════════
```

### Platform Comparison
```
═══════════════════════════════════════════════════════════════
                  PLATFORM COMPARISON
═══════════════════════════════════════════════════════════════

ENGAGEMENT BY PLATFORM:
┌─────────────┬──────────┬───────────┬─────────────┐
│ Platform    │ Actions  │ Responses │ Conv. Rate  │
├─────────────┼──────────┼───────────┼─────────────┤
│ LinkedIn    │ 50       │ 15        │ 30%         │
│ Twitter     │ 30       │ 8         │ 27%         │
│ Instagram   │ 20       │ 4         │ 20%         │
│ Email       │ 100      │ 12        │ 12%         │
└─────────────┴──────────┴───────────┴─────────────┘

RECOMMENDATION: LinkedIn showing highest conversion rate.
Consider increasing LinkedIn outreach volume.

═══════════════════════════════════════════════════════════════
```

## Implementation

### Step 1: Gather Data

Read campaign logs and compile metrics:

```bash
# List recent campaigns
ls -la output/logs/campaigns/

# Parse campaign data
python .claude/scripts/analytics.py parse --dir output/logs/campaigns/
```

### Step 2: Calculate Metrics

```python
# Example metrics calculation
metrics = {
    'sent': len(campaign_logs),
    'delivered': len([l for l in logs if l['status'] == 'delivered']),
    'replied': len([l for l in logs if l['replied']]),
    'open_rate': delivered / sent * 100,
    'response_rate': replied / sent * 100
}
```

### Step 3: Present Report

Format and display the report using the templates above.

## Example Conversation

**User:** "Show me analytics for my last campaign"

**Assistant:**

1. Check for recent campaigns in `output/logs/campaigns/`
2. Parse the campaign data
3. Calculate key metrics
4. Present formatted report
5. Offer insights and recommendations

## Environment Variables

```env
# Analytics Configuration
ANALYTICS_RETENTION_DAYS=90
TRACK_OPENS=true
TRACK_CLICKS=true
REPORT_TIMEZONE=America/Los_Angeles
```

## Best Practices

1. **Regular Reviews** - Check analytics weekly to optimize campaigns
2. **A/B Testing** - Compare different templates and approaches
3. **Trend Analysis** - Look for patterns over time
4. **Actionable Insights** - Use data to improve future campaigns
5. **Privacy Compliance** - Respect tracking consent preferences
