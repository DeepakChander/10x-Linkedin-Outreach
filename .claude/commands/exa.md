---
name: exa
description: Search the web using Exa AI's neural semantic search
---

# Exa Search Command

Search the web with Exa AI's powerful semantic search engine.

**Developed by 10x.in**

## Usage

```
/exa <search query>
```

## Examples

### Find People
```
/exa AI startup founders in San Francisco
/exa CTOs at Series A companies
/exa Machine learning researchers
```

### Company Research
```
/exa company Anthropic
/exa company OpenAI competitors
```

### LinkedIn Search
```
/exa linkedin Product Managers at tech startups
/exa linkedin Software Engineers in AI
```

### Code Search
```
/exa code Python machine learning libraries
/exa code React component patterns
```

### Deep Research
```
/exa research AI safety landscape 2026
/exa research climate tech startups
```

## What Happens

1. **Query Exa AI**: Uses `web_search_exa` MCP tool
2. **Semantic Search**: Neural network powered search (not keyword matching)
3. **Rich Results**: Returns URLs, titles, descriptions, and content
4. **Save Results**: Automatically saves to discovery database

## Search Types

| Type | Command | Example |
|------|---------|---------|
| **General** | `/exa <query>` | `/exa AI founders` |
| **LinkedIn** | `/exa linkedin <query>` | `/exa linkedin CTOs` |
| **Company** | `/exa company <name>` | `/exa company Anthropic` |
| **Code** | `/exa code <query>` | `/exa code React hooks` |
| **Research** | `/exa research <topic>` | `/exa research AI safety` |

## Exa Capabilities

### 🔍 Semantic Search
- Neural network powered (not keyword matching)
- Understands context and intent
- Returns most relevant results

### ⚡ Three Speed Modes
- **Exa Fast**: <350ms (quick results)
- **Exa Deep**: 3.5s (highest quality)
- **Exa Auto**: Balanced (default)

### 🎯 Special Features
- LinkedIn profile search
- GitHub code search
- Company website crawling
- Multi-step deep research
- URL content extraction

## Integration

Results from `/exa` are:
- ✅ Saved to `output/discovery/people.json`
- ✅ Available for workflow creation
- ✅ Ready for outreach campaigns

## Quick Tips

1. **Be specific**: "AI founders in SF" > "founders"
2. **Use filters**: `/exa linkedin` for LinkedIn-only results
3. **Company research**: `/exa company <name>` for deep dive
4. **Code search**: `/exa code` searches GitHub repositories

## Under the Hood

```
/exa AI founders in SF
    ↓
Exa MCP: web_search_exa()
    ↓
Neural semantic search
    ↓
50 enriched results
    ↓
Saved to discovery database
    ↓
Results displayed
```

## Advanced Usage

### Combine with Workflows

```
1. /exa AI startup founders
2. /workflow create for discovered founders
3. Canvas shows workflow with discovered people
4. Execute automated outreach
```

### Chain Searches

```
/exa company Anthropic
(Review results)
/exa linkedin employees at Anthropic
(Creates targeted list)
/workflow create for Anthropic employees
```

## API Key

Uses `EXA_API_KEY` from `.env.local`
- ✅ Already configured: `4bc627c0...5735`
- 🔗 Get key: https://exa.ai

## Resources

- Official Docs: https://docs.exa.ai/reference/search
- MCP Server: https://docs.exa.ai/reference/exa-mcp
- GitHub: https://github.com/exa-labs/exa-mcp-server

---

**Powered by Exa AI MCP**
**Developed by 10x.in** 🔥
