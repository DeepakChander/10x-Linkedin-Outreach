---
name: websets
description: Create and manage curated web collections with Exa Websets
---

# Websets Command

Create, manage, and search curated collections of websites.

**Developed by 10x.in**

## Usage

```
/websets <action> [options]
```

## Actions

### Create Webset
```
/websets create <name> <description>
```

**Example:**
```
/websets create "AI Founders" "Collection of AI startup founder profiles"
```

### List Websets
```
/websets list
```

Shows all your websets with IDs, names, and counts.

### Get Webset
```
/websets get <webset_id>
```

**Example:**
```
/websets get abc123
```

### Add to Webset
```
/websets add <webset_id> <url>
```

**Example:**
```
/websets add abc123 https://linkedin.com/in/johndoe
```

### Search Webset
```
/websets search <webset_id> <query>
```

**Example:**
```
/websets search abc123 founders in AI
```

## What Are Websets?

Websets are **curated collections** of web pages that you can:
- 🗂️ Organize discovered people/companies
- 🔍 Search within specific collections
- 📊 Track outreach progress
- 🤝 Share with team members
- 🎯 Create targeted campaigns

## Common Use Cases

### 1. Organize Discovery Results

```bash
# Find people
/exa AI startup founders in SF

# Create webset for them
/websets create "SF AI Founders" "Founders discovered on Jan 22"

# Add each profile
/websets add <id> https://linkedin.com/in/profile1
/websets add <id> https://linkedin.com/in/profile2
```

### 2. Company Research Collections

```bash
# Create webset for competitor research
/websets create "AI Competitors" "Companies in AI space"

# Add companies
/websets add <id> https://anthropic.com
/websets add <id> https://openai.com
/websets add <id> https://deepmind.com
```

### 3. Campaign Tracking

```bash
# Create webset for campaign
/websets create "Q1 Outreach" "LinkedIn outreach campaign"

# Add prospects as you discover them
/exa linkedin Product Managers at startups
/websets add <id> <each_profile_url>

# Search within your campaign
/websets search <id> responded
```

## Workflow Integration

Websets work seamlessly with workflows:

```
1. Create webset: /websets create "Target List" "Q1 prospects"
2. Add discoveries: /exa + /websets add
3. Create workflow: /workflow create for webset <id>
4. Execute: System pulls all URLs from webset
5. Automated outreach to entire webset
```

## Quick Example

```bash
# Step 1: Create collection
/websets create "AI Founders" "Founders in AI space"
> Created webset: abc123

# Step 2: Discover people
/exa AI startup founders
> Found 50 people

# Step 3: Add to webset (automated or manual)
/websets add abc123 https://linkedin.com/in/founder1
/websets add abc123 https://linkedin.com/in/founder2
...

# Step 4: Search within collection
/websets search abc123 Series A
> Returns only Series A founders from your webset

# Step 5: Create targeted workflow
/workflow create for webset abc123
> Creates workflow specifically for this webset
```

## Websets vs Regular Discovery

| Feature | Regular Discovery | Websets |
|---------|------------------|---------|
| **Organization** | Flat list | Organized collections |
| **Search** | Search all | Search within collection |
| **Sharing** | Individual files | Shareable webset ID |
| **Tracking** | Manual | Built-in progress tracking |
| **Workflows** | One-time | Reusable with webset ID |

## API Reference

The `/websets` command uses Exa Websets MCP tools:

- `create_webset` - Create new collection
- `get_webset` - Retrieve webset details
- `list_websets` - List all websets
- `add_to_webset` - Add URL to collection
- `remove_from_webset` - Remove URL
- `search_webset` - Search within collection

## Storage

Websets are stored:
- 🌐 **Cloud**: Exa Websets platform (https://websets.exa.ai/websets)
- 💾 **Local**: `output/websets/` (cached for offline access)

## Best Practices

### 1. Descriptive Names
```
✅ "AI Founders - Series A - Bay Area"
❌ "List1"
```

### 2. Organize by Campaign
```
/websets create "Q1-2026-LinkedIn" "LinkedIn outreach Q1"
/websets create "Q1-2026-Twitter" "Twitter outreach Q1"
```

### 3. Tag with Dates
```
/websets create "Founders-Jan-2026" "Jan 2026 discoveries"
```

### 4. Use for A/B Testing
```
/websets create "Campaign-A" "Template A prospects"
/websets create "Campaign-B" "Template B prospects"
```

## Advanced Features

### Bulk Import from Discovery

```python
# After running /exa search
python .claude/scripts/discovery_engine.py export --format=webset

# Automatically creates webset with all discoveries
```

### Export to CSV

```
/websets get abc123 --export=csv
> Exports all URLs to CSV for team sharing
```

### Merge Websets

```
/websets merge abc123 def456 --name="Combined List"
> Merges two websets into one
```

## API Key

Uses same `EXA_API_KEY` as Exa search:
- ✅ Already configured in `.env.local`
- 🔗 Manage websets: https://websets.exa.ai/websets

## Resources

- Websets Platform: https://websets.exa.ai/websets
- MCP Server: https://github.com/waldzellai/exa-mcp-server-websets
- Exa Docs: https://docs.exa.ai

---

**Powered by Exa Websets MCP**
**Developed by 10x.in** 🔥
