# Discover Command

Routes to `discovery-engine` skill for finding people to reach out to using Exa AI.

## Usage

```
/discover [query]
```

## Actions

- `/discover` - Start interactive discovery session
- `/discover <query>` - Search for people matching query
- `/discover list` - Show discovered people
- `/discover stats` - Show discovery statistics
- `/discover export` - Export discovered people to CSV/JSON

## Examples

```
/discover AI startup founders in NYC
/discover DevOps engineers at Series B startups
/discover list --has-linkedin
/discover export --format csv
```

## Search Tips

- Be specific: "AI startup founders Series A San Francisco"
- Include location when relevant
- Specify role, industry, and company stage
- Use tags to organize results

## Skill Reference

This command uses the `discovery-engine` skill located at `.claude/skills/discovery-engine/SKILL.md`.

Uses Exa AI MCP for intelligent search:
- `linkedin_search_exa` - LinkedIn people search
- `company_research_exa` - Company research
- `web_search_exa` - Cross-platform profile discovery
