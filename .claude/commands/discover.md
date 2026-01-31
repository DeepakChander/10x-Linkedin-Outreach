---
allowed-tools: Bash, Read, Write
description: "Find LinkedIn profiles by search filters"
---

# /discover — Find LinkedIn Profiles

## Instructions

1. Ask the user for search filters:
   - **Industry** (e.g., SaaS, FinTech, HealthTech)
   - **Role/Title** (e.g., CTO, VP Engineering, Founder)
   - **Location** (e.g., USA, San Francisco, Europe)
   - **Company size** (e.g., 50-200, startup, enterprise)
   - **Keywords** (optional, extra search terms)

2. Build the filters JSON from their response.

3. Run the search:
```bash
node .claude/scripts/extension_client.js searchProfiles '{"filters":{"keywords":"<keywords>","industry":"<industry>","location":"<location>"},"maxPages":10}'
```

4. Read existing `output/profiles.json` (create if missing, start with `[]`).

5. Deduplicate: skip any profile whose `profileUrl` already exists in profiles.json.

6. For each new profile, add to profiles.json:
```json
{
  "id": "<generate-uuid>",
  "name": "<name>",
  "headline": "<headline>",
  "location": "<location>",
  "profileUrl": "<url>",
  "degree": "<degree>",
  "status": "discovered",
  "batch_id": "<YYYY-MM-DD>-<industry>-<role>",
  "created_at": "<ISO timestamp>"
}
```

7. Write updated profiles.json.

8. Report: "Found **N** new profiles (M duplicates skipped). Batch: `<batch_id>`"

9. Suggest: "Run `/connect` to send connection requests to these profiles."
