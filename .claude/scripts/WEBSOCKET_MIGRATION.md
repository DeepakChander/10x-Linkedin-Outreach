# WebSocket Adapter Migration

This document describes the migration from Browser-Use MCP to WebSocket-based adapters.

## Overview

The LinkedIn, Instagram, and Twitter adapters have been updated to use WebSocket connections instead of Browser-Use MCP for executing platform-specific actions.

## Changes

### Connection Method

**Before (Browser-Use MCP):**
- Generated browser task descriptions
- Relied on Claude to execute via `mcp__browser-use__browser_task`
- Asynchronous execution through MCP tool calls

**After (WebSocket):**
- Direct WebSocket connection to `ws://localhost:3000/ws`
- Send JSON commands with platform-specific actions
- Receive command results directly

### Adapter Architecture

Each adapter now includes:

1. **WebSocket Connection Management**
   - `_connect()`: Establishes WebSocket connection
   - `close()`: Properly closes connection
   - Connection reuse across multiple actions

2. **Async/Sync Bridge**
   - Async methods for WebSocket communication
   - Synchronous wrapper (`execute_action`) for compatibility
   - Uses `asyncio.new_event_loop()` for sync calls

3. **Backward Compatibility**
   - `generate_task()` still exists but now calls `execute_action()`
   - Maintains same function signatures
   - Helper functions unchanged

## Command Format

### LinkedIn Actions

```python
{
    "type": "linkedin-action",
    "payload": {
        "type": "connect|message|like_post|comment|view_profile|follow",
        "profile_url": "https://linkedin.com/in/user",
        "target_name": "User Name",
        "message": "Optional message text"
    }
}
```

### Instagram Actions

```python
{
    "type": "instagram-action",
    "payload": {
        "type": "follow|dm|like_post|comment|story_reply",
        "target_handle": "username",
        "target_name": "User Name",
        "message": "Optional message text",
        "post_url": "Optional post URL"
    }
}
```

### Twitter Actions

```python
{
    "type": "twitter-action",
    "payload": {
        "type": "follow|dm|like_tweet|retweet|reply|quote_tweet",
        "target_handle": "username",
        "target_name": "User Name",
        "message": "Optional message text",
        "tweet_url": "Optional tweet URL"
    }
}
```

## Response Format

All adapters receive responses in this format:

```python
{
    "success": true|false,
    "error": "Error message if failed",
    "data": "Response data from server",
    "message": "Rendered message text"
}
```

## Usage Examples

### LinkedIn Adapter

```python
from linkedin_adapter import LinkedInAdapter, LinkedInAction

adapter = LinkedInAdapter()

action = LinkedInAction(
    action_type='connect',
    target_url='https://linkedin.com/in/user',
    target_name='John Doe',
    message='Hi John, I would love to connect!'
)

result = adapter.execute_action(action, user_id="user123")

if result['success']:
    print("Connection request sent!")
else:
    print(f"Failed: {result['error']}")
```

### Instagram Adapter

```python
from instagram_adapter import InstagramAdapter, create_dm_action

adapter = InstagramAdapter()

action = create_dm_action(
    handle='@johndoe',
    name='John Doe',
    message='Hey John! Love your content!'
)

result = adapter.execute_action(action)
```

### Twitter Adapter

```python
from twitter_adapter import TwitterAdapter, create_follow_action

adapter = TwitterAdapter()

action = create_follow_action(
    handle='@johndoe',
    name='John Doe'
)

result = adapter.execute_action(action)
```

## Configuration

### WebSocket URL

Default: `ws://localhost:3000/ws`

To use a custom WebSocket server:

```python
adapter = LinkedInAdapter(ws_url='ws://custom-server:3000/ws')
```

### Timeout

Default: 30 seconds

Each adapter has a configurable timeout for WebSocket responses:

```python
adapter = LinkedInAdapter()
adapter.timeout = 60  # 60 seconds
```

## Error Handling

The adapters handle these error scenarios:

1. **Connection Refused**: WebSocket server not running
2. **Timeout**: Response not received within timeout period
3. **Rate Limiting**: Action blocked by rate limiter
4. **Invalid Response**: Malformed JSON from server

All errors are returned in the `error` field of the result dict.

## Rate Limiting

Rate limiting is preserved from the original implementation:

- Checks limits before sending action
- Records successful/failed actions
- Returns rate limit info if blocked

```python
result = adapter.execute_action(action)

if not result.get('can_proceed'):
    print(f"Rate limited: {result['reason']}")
    print(f"Wait {result['wait_seconds']} seconds")
```

## Testing

Run the test suite to verify adapters:

```bash
cd .claude/scripts
python test_websocket_adapters.py
```

**Note**: WebSocket server must be running at `ws://localhost:3000/ws` for tests to pass.

Expected output with server running:
```
LinkedIn Adapter: [PASS]
Instagram Adapter: [PASS]
Twitter Adapter: [PASS]
Helper Functions: [PASS]
```

Expected output without server:
```
LinkedIn Adapter: [FAIL] (expected if server not running)
Instagram Adapter: [FAIL] (expected if server not running)
Twitter Adapter: [FAIL] (expected if server not running)
Helper Functions: [PASS]
```

## Migration Checklist

- [x] Update LinkedIn adapter to WebSocket
- [x] Update Instagram adapter to WebSocket
- [x] Update Twitter adapter to WebSocket
- [x] Maintain backward compatibility
- [x] Preserve rate limiting functionality
- [x] Add error handling for WebSocket errors
- [x] Create test suite
- [x] Document command formats
- [x] Document usage examples

## Dependencies

New dependency added:

```bash
pip install websockets
```

Or add to requirements.txt:
```
websockets>=12.0
```

## Server Requirements

The WebSocket server must:

1. Listen on `ws://localhost:3000/ws`
2. Accept JSON commands with `type` and `payload` fields
3. Return JSON responses with `success`, `error`, and `data` fields
4. Handle platform-specific action types:
   - `linkedin-action`
   - `instagram-action`
   - `twitter-action`

## Troubleshooting

### Connection Errors

**Issue**: `[WinError 1225] The remote computer refused the network connection`

**Solution**: Ensure WebSocket server is running on port 3000

```bash
# Start your WebSocket server
node server.js  # or equivalent
```

### Timeout Errors

**Issue**: `WebSocket timeout after 30s`

**Solutions**:
1. Increase timeout: `adapter.timeout = 60`
2. Check server is processing commands
3. Verify server is sending responses

### Rate Limit Errors

**Issue**: Action blocked by rate limiter

**Solution**: Wait for the specified time or adjust rate limits in configuration

## Future Enhancements

Potential improvements:

1. Connection pooling for multiple concurrent actions
2. Automatic reconnection on connection loss
3. Batch action support
4. Progress callbacks for long-running actions
5. WebSocket authentication/authorization
