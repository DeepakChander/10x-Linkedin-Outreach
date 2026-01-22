# WebSocket Adapters - Quick Start Guide

## Installation

Dependencies already installed:
- `websockets==15.0.1` ✓

## Usage

### LinkedIn

```python
from linkedin_adapter import LinkedInAdapter, create_connect_action

# Create adapter
adapter = LinkedInAdapter()

# Create and execute connection request
action = create_connect_action(
    profile_url='https://linkedin.com/in/johndoe',
    name='John Doe',
    message='Hi John, I would love to connect!'
)

result = adapter.execute_action(action, user_id="user123")

if result['success']:
    print(f"✓ Connection sent: {result['message']}")
else:
    print(f"✗ Failed: {result['error']}")
```

### Instagram

```python
from instagram_adapter import InstagramAdapter, create_dm_action

adapter = InstagramAdapter()

action = create_dm_action(
    handle='@johndoe',
    name='John Doe',
    message='Hey John! Love your content! 🔥'
)

result = adapter.execute_action(action)
```

### Twitter

```python
from twitter_adapter import TwitterAdapter, create_follow_action

adapter = TwitterAdapter()

action = create_follow_action(
    handle='@johndoe',
    name='John Doe'
)

result = adapter.execute_action(action)
```

## Available Actions

### LinkedIn
- `view_profile` - Visit a profile
- `like_post` - Like a post
- `comment` - Comment on a post
- `connect` - Send connection request
- `message` - Send direct message
- `follow` - Follow a person/company

### Instagram
- `follow` - Follow a user
- `like_post` - Like a post
- `comment` - Comment on a post
- `dm` - Send direct message
- `story_reply` - Reply to a story

### Twitter
- `follow` - Follow a user
- `like_tweet` - Like a tweet
- `retweet` - Retweet
- `reply` - Reply to tweet
- `dm` - Send direct message
- `quote_tweet` - Quote tweet

## Configuration

### Custom WebSocket URL

```python
adapter = LinkedInAdapter(ws_url='ws://custom-server:3000/ws')
```

### Custom Timeout

```python
adapter = LinkedInAdapter()
adapter.timeout = 60  # 60 seconds
```

## Testing

```bash
cd .claude/scripts
python test_websocket_adapters.py
```

## Rate Limiting

All adapters respect rate limits:

```python
result = adapter.execute_action(action)

if not result.get('can_proceed'):
    print(f"Rate limited: {result['reason']}")
    print(f"Wait {result['wait_seconds']} seconds")
```

## Error Handling

```python
result = adapter.execute_action(action)

if result['success']:
    print("Action completed successfully!")
    print(f"Data: {result.get('data')}")
else:
    print(f"Action failed: {result['error']}")
```

## Server Requirements

Your WebSocket server must:

1. **Listen**: ws://localhost:3000/ws
2. **Accept**: JSON commands with type and payload
3. **Return**: JSON with success, error, data fields

Example server response:
```json
{
  "success": true,
  "data": "Connection request sent successfully"
}
```

## Troubleshooting

### Connection Refused

**Error**: `[WinError 1225] The remote computer refused the network connection`

**Solution**: Start WebSocket server on port 3000

### Timeout

**Error**: `WebSocket timeout after 30s`

**Solution**: Increase timeout or check server responsiveness

```python
adapter.timeout = 60  # Increase to 60 seconds
```

### Rate Limited

**Error**: `can_proceed: false`

**Solution**: Wait for specified time or adjust rate limits

## Complete Example

```python
from linkedin_adapter import LinkedInAdapter, LinkedInAction

# Initialize adapter
adapter = LinkedInAdapter()

# Create custom action
action = LinkedInAction(
    action_type='connect',
    target_url='https://linkedin.com/in/johndoe',
    target_name='John Doe',
    message='Hi John, saw your post about AI. Would love to connect!',
    max_steps=12
)

# Execute action
result = adapter.execute_action(action, user_id="user123")

# Handle result
if result['success']:
    print(f"✓ Success: {result['data']}")
    print(f"Message sent: {result['message']}")
else:
    print(f"✗ Error: {result['error']}")

# Check remaining limits
limits = adapter.get_remaining_limits("user123")
print(f"Remaining connections today: {limits.get('connections_per_day', 'N/A')}")
```

## Migration from Browser-Use MCP

If you were using `generate_task()`, it still works:

```python
# Old way (still works, but internally uses WebSocket)
task_info = adapter.generate_task(action, user_id="user123")

# New way (recommended)
result = adapter.execute_action(action, user_id="user123")
```

Both methods now use WebSocket internally and return the same response format.

## Support

For detailed documentation, see:
- **WEBSOCKET_MIGRATION.md** - Complete migration guide
- **test_websocket_adapters.py** - Test suite examples
- Individual adapter files for specific implementation details
