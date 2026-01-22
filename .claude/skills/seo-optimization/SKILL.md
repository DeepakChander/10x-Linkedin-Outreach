---
name: seo-optimization
description: |
  SEO optimization and keyword research skill. Use this skill when the user wants to
  research keywords, analyze competitors, optimize content for search, or track rankings.
  Integrates with Exa AI for comprehensive SEO research capabilities.
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - AskUserQuestion
---

# SEO Optimization Skill

Comprehensive SEO research and optimization capabilities powered by Exa AI.

## When to Use This Skill

Use this skill when the user:
- Wants keyword research or suggestions
- Needs competitor SEO analysis
- Asks about content optimization for search
- Wants to analyze backlinks
- Needs help with on-page SEO

## When NOT to Use This Skill

Do NOT use this skill for:
- Content creation → use `content-marketing`
- Email campaigns → use `outreach-manager`
- Finding people → use `discovery-engine`
- Analytics dashboards → use `analytics`

## Capabilities

1. **Keyword Research** - Find relevant keywords with Exa AI
2. **Competitor Analysis** - Analyze competitor SEO strategies
3. **Content Optimization** - Suggest improvements for SEO
4. **Backlink Analysis** - Research backlink opportunities
5. **SERP Analysis** - Understand search result landscape

## MCP Integration Guidelines

### Primary MCP: Exa AI
This skill primarily uses Exa AI for SEO research and analysis.

### When to Use MCPs

| Operation | MCP | Tool |
|-----------|-----|------|
| Keyword research | Exa | `web_search_exa` |
| Competitor analysis | Exa | `company_research_exa` |
| Content analysis | Exa | `exa_search` |
| Deep research | Exa | `deep_researcher_start` |
| Webset creation | Exa | `create_webset` |

### MCP Selection Flow

```
User Request → Context Detector → SEO Intent → Exa AI Research
     ↓                                               ↓
  Analysis                                    Keyword Data
     ↓                                               ↓
  Optimization                              Recommendations
  Suggestions
```

### Integration with Other Skills

| Scenario | Route To | Reason |
|----------|----------|--------|
| Create content | `content-marketing` | Content creation |
| Find link prospects | `discovery-engine` | Outreach for backlinks |
| Track performance | `analytics` | SEO metrics |
| Email outreach | `outreach-manager` | Link building outreach |

## Keyword Research

### Research Process

1. **Seed Keywords** - Start with main topic keywords
2. **Related Keywords** - Find semantically related terms
3. **Long-tail Keywords** - Discover specific phrases
4. **Competitor Keywords** - Analyze what competitors rank for
5. **Gap Analysis** - Find keyword opportunities

### Keyword Report Template

```
═══════════════════════════════════════════════════════════════
                    KEYWORD RESEARCH REPORT
═══════════════════════════════════════════════════════════════

🎯 SEED KEYWORD: [Main Keyword]

PRIMARY KEYWORDS (High Volume, Medium Competition):
┌─────────────────────────────┬──────────┬────────────┐
│ Keyword                     │ Intent   │ Difficulty │
├─────────────────────────────┼──────────┼────────────┤
│ [keyword 1]                 │ Info     │ Medium     │
│ [keyword 2]                 │ Trans    │ High       │
│ [keyword 3]                 │ Nav      │ Low        │
└─────────────────────────────┴──────────┴────────────┘

LONG-TAIL KEYWORDS (Lower Volume, Easier to Rank):
┌─────────────────────────────────────────┬────────────┐
│ Keyword                                 │ Difficulty │
├─────────────────────────────────────────┼────────────┤
│ [long-tail keyword 1]                   │ Low        │
│ [long-tail keyword 2]                   │ Low        │
│ [long-tail keyword 3]                   │ Medium     │
└─────────────────────────────────────────┴────────────┘

RELATED TOPICS TO COVER:
• [Related topic 1]
• [Related topic 2]
• [Related topic 3]

CONTENT RECOMMENDATIONS:
1. Create pillar content around "[main keyword]"
2. Target "[long-tail]" for quick wins
3. Build topical authority with related content

═══════════════════════════════════════════════════════════════
```

## Competitor Analysis

### Analysis Process

1. **Identify Competitors** - Find top-ranking sites
2. **Content Analysis** - Analyze their content strategy
3. **Backlink Profile** - Research their link sources
4. **Keyword Gaps** - Find keywords they rank for that you don't
5. **Opportunities** - Identify weaknesses to exploit

### Competitor Report Template

```
═══════════════════════════════════════════════════════════════
                  COMPETITOR SEO ANALYSIS
═══════════════════════════════════════════════════════════════

🎯 COMPETITOR: [Competitor Domain]

OVERVIEW:
• Domain Authority: [Score]
• Estimated Organic Traffic: [Number]
• Top Keywords: [Count]
• Backlinks: [Count]

TOP RANKING CONTENT:
┌─────────────────────────────────────────┬───────────┐
│ Page Title                              │ Keywords  │
├─────────────────────────────────────────┼───────────┤
│ [Title 1]                               │ 45        │
│ [Title 2]                               │ 32        │
│ [Title 3]                               │ 28        │
└─────────────────────────────────────────┴───────────┘

CONTENT GAP OPPORTUNITIES:
These keywords your competitor ranks for but you don't:
• [keyword 1] - Est. traffic: X
• [keyword 2] - Est. traffic: Y
• [keyword 3] - Est. traffic: Z

BACKLINK OPPORTUNITIES:
Sites linking to competitor that might link to you:
• [site1.com] - [reason]
• [site2.com] - [reason]

═══════════════════════════════════════════════════════════════
```

## On-Page SEO Checklist

### Content Optimization

```
ON-PAGE SEO CHECKLIST
═══════════════════════════════════════════════════════════════

URL: [Page URL]

TITLE TAG:
☐ Contains primary keyword
☐ Under 60 characters
☐ Compelling and clickable
Current: "[Current Title]"
Suggested: "[Optimized Title]"

META DESCRIPTION:
☐ Contains primary keyword
☐ Under 160 characters
☐ Includes call to action
Current: "[Current Description]"
Suggested: "[Optimized Description]"

HEADINGS:
☐ H1 contains primary keyword (only one H1)
☐ H2s cover subtopics
☐ Logical heading hierarchy

CONTENT:
☐ Primary keyword in first 100 words
☐ Related keywords naturally included
☐ Minimum 1000 words for pillar content
☐ Internal links to related content
☐ External links to authoritative sources

IMAGES:
☐ Descriptive file names
☐ Alt text with keywords
☐ Compressed for speed

TECHNICAL:
☐ Mobile responsive
☐ Fast page load (<3s)
☐ SSL certificate
☐ Schema markup where applicable

═══════════════════════════════════════════════════════════════
```

## Commands Reference

### Keyword Research

```bash
python .claude/scripts/seo_research.py keywords --topic "AI marketing" --depth deep
```

### Competitor Analysis

```bash
python .claude/scripts/seo_research.py competitor --domain "competitor.com"
```

### Content Audit

```bash
python .claude/scripts/seo_research.py audit --url "yoursite.com/page"
```

### Backlink Research

```bash
python .claude/scripts/seo_research.py backlinks --domain "target.com"
```

## Best Practices

### Research Phase
1. **Start broad** - Begin with main topic, then drill down
2. **Consider intent** - Match keywords to user intent
3. **Analyze SERPs** - Understand what's ranking and why
4. **Find gaps** - Look for underserved topics

### Optimization Phase
1. **Prioritize impact** - Focus on high-opportunity pages first
2. **Natural integration** - Don't force keywords unnaturally
3. **User experience** - SEO should improve, not hurt, UX
4. **Technical foundation** - Ensure site is crawlable

### Monitoring Phase
1. **Track rankings** - Monitor keyword positions
2. **Measure traffic** - Watch organic traffic trends
3. **Analyze behavior** - Check engagement metrics
4. **Iterate** - Continuously improve based on data

## Example Conversation

**User:** "Research keywords for AI sales tools"

**Assistant:**

1. Use Exa AI to research "AI sales tools" landscape
2. Identify primary, secondary, and long-tail keywords
3. Analyze competitor keyword strategies
4. Present keyword report with recommendations
5. Suggest content opportunities

## Environment Variables

```env
# SEO Configuration
SEO_OUTPUT_DIR=output/seo
DEFAULT_KEYWORD_COUNT=50
COMPETITOR_ANALYSIS_DEPTH=deep
INCLUDE_BACKLINK_RESEARCH=true
```

## MCP Best Practices

1. **Use semantic search** - Exa AI excels at finding related content
2. **Research competitors** - Company research tool for SEO insights
3. **Create websets** - Organize research into collections
4. **Deep research mode** - Use for comprehensive analysis
5. **Respect rate limits** - Don't overwhelm the API
