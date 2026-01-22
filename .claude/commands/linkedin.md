# LinkedIn Command

Execute LinkedIn actions using Browser-Use automation.

## Usage

```
/linkedin <action> [target] [options]
```

## Actions

### Connect
Send connection request:
```
/linkedin connect https://linkedin.com/in/username
/linkedin connect @johnsmith --template cold_outreach
```

### Message
Send a message:
```
/linkedin message https://linkedin.com/in/username "Your message here"
/linkedin message @johnsmith --template intro_after_connect
```

### View Profile
View someone's profile (warm-up):
```
/linkedin view https://linkedin.com/in/username
```

### Like Post
Like a recent post:
```
/linkedin like https://linkedin.com/in/username
/linkedin like https://linkedin.com/posts/postid
```

### Comment
Comment on a post:
```
/linkedin comment https://linkedin.com/posts/postid "Great insight!"
/linkedin comment https://linkedin.com/in/username --template thoughtful_engagement
```

## Options

- `--template <name>` - Use a template from templates/linkedin/
- `--user <id>` - Team member ID (default: "default")
- `--dry-run` - Preview without executing

## Templates

### Connection Requests
- `cold_outreach` - General cold outreach
- `startup_founder` - Startup founder outreach
- `thought_leader` - Thought leader connection
- `speaker_invitation` - Speaker invitation
- `content_collaboration` - Content collaboration
- `alumni_connect` - Alumni connection
- `potential_client` - Sales outreach

### Messages
- `intro_after_connect` - First message after connecting
- `follow_up_no_response` - Follow up
- `meeting_request` - Request a meeting
- `partnership_proposal` - Partnership proposal
- `sales_intro` - Sales introduction

### Comments
- `thoughtful_engagement` - Thoughtful comment
- `question_comment` - Ask a question
- `congratulations` - Congratulations

## Examples

```
/linkedin connect https://linkedin.com/in/elonmusk --template startup_founder
/linkedin message @satyanadella --template partnership_proposal
/linkedin like https://linkedin.com/in/billgates
/linkedin comment https://linkedin.com/posts/abc123 "Brilliant perspective on AI!"
```

## Rate Limits

- Connections: 20/day
- Messages: 50/day
- Profile views: 100/day
- Likes: 100/day
- Comments: 25/day

## Invokes Skill

This command uses the `linkedin-adapter` skill.
