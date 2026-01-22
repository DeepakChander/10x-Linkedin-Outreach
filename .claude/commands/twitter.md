# Twitter Command

Execute Twitter/X actions using Browser-Use automation.

## Usage

```
/twitter <action> [target] [options]
```

## Actions

### Follow
Follow a user:
```
/twitter follow @username
```

### DM
Send a direct message:
```
/twitter dm @username "Your message here"
/twitter dm @username --template cold_dm
```

### Like
Like a tweet:
```
/twitter like https://x.com/user/status/123456
/twitter like @username  # Likes their latest tweet
```

### Reply
Reply to a tweet:
```
/twitter reply https://x.com/user/status/123456 "Great point!"
/twitter reply @username --template value_add
```

### Retweet
Retweet a tweet:
```
/twitter retweet https://x.com/user/status/123456
```

### Quote Tweet
Quote tweet with comment:
```
/twitter quote https://x.com/user/status/123456 "This is so true!"
/twitter quote @username --template quote_tweet
```

## Options

- `--template <name>` - Use a template from templates/twitter/
- `--user <id>` - Team member ID (default: "default")
- `--dry-run` - Preview without executing

## Templates

### DMs
- `cold_dm` - Cold outreach DM
- `founder_outreach` - Founder outreach
- `thought_leader_outreach` - Thought leader outreach
- `influencer_outreach` - Influencer collaboration
- `collaboration` - Collaboration request
- `podcast_guest` - Podcast guest invitation
- `investor_intro` - Investor introduction

### Replies
- `value_add` - Add value to conversation
- `question` - Ask a question
- `agreement` - Agree with insight
- `insight` - Share an insight
- `build_in_public` - Build in public engagement
- `milestone_congrats` - Congratulate milestones

### Tweets
- `engagement_reply` - Engagement reply
- `quote_tweet` - Quote tweet template
- `mention` - Mention someone

## Examples

```
/twitter follow @elonmusk
/twitter dm @paulgraham --template founder_outreach
/twitter like https://x.com/sama/status/123456
/twitter reply @naval "100% agree with this thread!"
/twitter quote https://x.com/levelsio/status/123 "This is the way."
```

## Rate Limits

- Follows: 50/day
- DMs: 50/day
- Likes: 100/day
- Replies: 75/day
- Retweets: 50/day

## Notes

- DMs may require mutual following
- Tweets/replies are limited to 280 characters
- DMs can be up to 10,000 characters

## Invokes Skill

This command uses the `twitter-adapter` skill.
