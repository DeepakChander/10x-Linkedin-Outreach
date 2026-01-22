# Instagram Command

Execute Instagram actions using ClaudeKit Browser Extension via WebSocket.

## Usage

```
/instagram <action> [target] [options]
```

## Actions

### Follow
Follow a user:
```
/instagram follow @username
```

### DM
Send a direct message:
```
/instagram dm @username "Your message here"
/instagram dm @username --template cold_dm
```

### Like
Like a post:
```
/instagram like https://instagram.com/p/ABC123
/instagram like @username  # Likes their latest post
```

### Comment
Comment on a post:
```
/instagram comment https://instagram.com/p/ABC123 "Amazing content!"
/instagram comment @username --template engagement
```

### Story Reply
Reply to a story:
```
/instagram story @username "Love this!"
/instagram story @username --template story_reply
```

## Options

- `--template <name>` - Use a template from templates/instagram/
- `--user <id>` - Team member ID (default: "default")
- `--dry-run` - Preview without executing

## Templates

### DMs
- `cold_dm` - Cold outreach DM
- `influencer_outreach` - Influencer outreach
- `brand_collaboration` - Brand collaboration
- `creator_partnership` - Creator partnership
- `founder_connect` - Founder connection
- `collaboration` - Collaboration request
- `product_feature` - Product feature request

### Comments
- `engagement` - General engagement
- `compliment` - Compliment their content
- `question` - Ask a question
- `support` - Show support
- `value_add` - Add value
- `appreciation` - Show appreciation

### Stories
- `story_reply` - Reply to story
- `story_reaction` - React to story

## Examples

```
/instagram follow @garyvee
/instagram dm @founder --template influencer_outreach
/instagram like https://instagram.com/p/CaBC123xyz
/instagram comment @creator "This is incredible work!"
/instagram story @influencer --template story_reply
```

## Rate Limits

- Follows: 30/day
- DMs: 30/day
- Likes: 60/day
- Comments: 20/day
- Story replies: 30/day

## Notes

- Instagram is very sensitive to automation
- Longer delays are enforced automatically
- DMs may require following first
- Comments under 150 chars look more natural
- Story replies go to their DM inbox

## Invokes Skill

This command uses the `instagram-adapter` skill.
