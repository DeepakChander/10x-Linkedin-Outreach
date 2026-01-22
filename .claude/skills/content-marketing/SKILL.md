---
name: content-marketing
description: |
  Content marketing and creation skill. Use this skill when the user wants to create
  blog posts, social media content, content calendars, or research trending topics.
  Integrates with Exa AI for content research and trend analysis.
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

# Content Marketing Skill

Create and manage content for marketing purposes with intelligent research capabilities.

## When to Use This Skill

Use this skill when the user:
- Wants to create blog posts or articles
- Needs social media content
- Asks about content calendars or planning
- Wants to research trending topics
- Needs content ideas or inspiration

## When NOT to Use This Skill

Do NOT use this skill for:
- SEO keyword research → use `seo-optimization`
- Sending emails → use `email-composer` or `outreach-manager`
- Finding people → use `discovery-engine`
- Analytics → use `analytics`

## Capabilities

1. **Content Research** - Research topics using Exa AI
2. **Blog Writing** - Draft blog posts with SEO optimization
3. **Social Content** - Create platform-specific social posts
4. **Content Calendar** - Plan and schedule content
5. **Trend Analysis** - Identify trending topics and hashtags

## MCP Integration Guidelines

### Primary MCP: Exa AI
This skill primarily uses Exa AI for content research and trend analysis.

### When to Use MCPs

| Operation | MCP | Tool |
|-----------|-----|------|
| Topic research | Exa | `web_search_exa` |
| Competitor analysis | Exa | `company_research_exa` |
| Trend discovery | Exa | `exa_search` |
| Content inspiration | Exa | `deep_researcher_start` |

### MCP Selection Flow

```
User Request → Context Detector → Content Intent → Exa AI Research
     ↓                                                    ↓
  Content                                           Research Results
  Creation                                                ↓
     ↓                                              Draft Content
  Review & Refine
```

### Integration with Other Skills

| Scenario | Route To | Reason |
|----------|----------|--------|
| SEO optimization | `seo-optimization` | Keyword research |
| Email content | `template-manager` | Email templates |
| Social automation | Platform adapters | Posting content |
| Performance tracking | `analytics` | Content metrics |

## Content Types

### Blog Posts
```markdown
# Article Template

## Title: [Engaging, SEO-Optimized Title]

### Introduction (Hook)
- Grab attention
- State the problem
- Preview the solution

### Body (Value)
- Main points with examples
- Data and research
- Actionable insights

### Conclusion (CTA)
- Summarize key points
- Call to action
- Next steps
```

### Social Media Posts

#### LinkedIn Post Template
```
[Hook - First line grabs attention]

Here's what I learned about [topic]:

→ Point 1
→ Point 2
→ Point 3

The key takeaway?
[Insight]

What's your experience with [topic]?

#hashtag1 #hashtag2 #hashtag3
```

#### Twitter Thread Template
```
1/ 🧵 [Hook - The hook that makes people want to read]

2/ [First point with context]

3/ [Second point with example]

4/ [Third point with data]

5/ [Key insight or takeaway]

6/ [Call to action + relevant hashtags]
```

#### Instagram Caption Template
```
[Opening hook - 125 characters max for preview]

[Main content with line breaks for readability]

[Call to action]

.
.
.
[Hashtags - up to 30, most relevant first]
```

## Commands Reference

### Research Topic

```bash
# Using Exa AI for research
python .claude/scripts/content_research.py --topic "AI in marketing" --depth deep
```

### Generate Content Ideas

```bash
python .claude/scripts/content_ideas.py --niche "B2B SaaS" --count 10
```

### Create Content Calendar

```bash
python .claude/scripts/content_calendar.py --weeks 4 --platforms "linkedin,twitter,blog"
```

### Analyze Competitors

```bash
python .claude/scripts/competitor_content.py --company "CompetitorName" --platforms all
```

## Content Calendar Template

```
═══════════════════════════════════════════════════════════════
                    CONTENT CALENDAR - Week of [Date]
═══════════════════════════════════════════════════════════════

MONDAY
┌─────────────┬────────────────────────────────────────────────┐
│ Platform    │ Content                                        │
├─────────────┼────────────────────────────────────────────────┤
│ LinkedIn    │ Industry insight post (10 AM)                  │
│ Twitter     │ Quote + link to blog (2 PM)                    │
│ Blog        │ Publish: "5 Ways to..." (9 AM)                 │
└─────────────┴────────────────────────────────────────────────┘

TUESDAY
┌─────────────┬────────────────────────────────────────────────┐
│ LinkedIn    │ Personal story/lesson (10 AM)                  │
│ Twitter     │ Poll about [topic] (12 PM)                     │
│ Instagram   │ Behind-the-scenes carousel (6 PM)              │
└─────────────┴────────────────────────────────────────────────┘

[Continue for rest of week...]

═══════════════════════════════════════════════════════════════
```

## Best Practices

### Research Phase
1. **Use Exa AI** for semantic search on topics
2. **Analyze competitors** to find content gaps
3. **Check trending topics** for relevance
4. **Validate ideas** with keyword research

### Creation Phase
1. **Hook first** - Start with attention-grabbing opener
2. **Value-driven** - Focus on helping the reader
3. **Platform-specific** - Adapt format for each platform
4. **SEO-conscious** - Include relevant keywords naturally

### Distribution Phase
1. **Optimal timing** - Post when audience is active
2. **Cross-promote** - Repurpose across platforms
3. **Engage** - Respond to comments and shares
4. **Track performance** - Use analytics to improve

## Example Conversation

**User:** "Create a LinkedIn post about AI in sales"

**Assistant:**

1. Research AI in sales trends using Exa AI
2. Find recent statistics and examples
3. Draft LinkedIn post with hook, value, and CTA
4. Include relevant hashtags
5. Offer variations for A/B testing

## Environment Variables

```env
# Content Marketing Configuration
CONTENT_OUTPUT_DIR=output/content
DEFAULT_CONTENT_TONE=professional
INCLUDE_HASHTAGS=true
MAX_HASHTAGS_INSTAGRAM=30
MAX_HASHTAGS_LINKEDIN=5
MAX_HASHTAGS_TWITTER=3
```

## MCP Best Practices

1. **Research before writing** - Use Exa AI to gather insights first
2. **Cite sources** - Reference research in content when appropriate
3. **Stay current** - Use real-time search for trending topics
4. **Validate claims** - Cross-reference facts with multiple sources
5. **Respect rate limits** - Don't overwhelm Exa API with requests
