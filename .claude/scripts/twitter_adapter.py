#!/usr/bin/env python3
"""
Twitter/X Adapter for 100X Outreach System

Provides Twitter automation actions using WebSocket connection.
Connects to ws://localhost:3000/ws for platform-specific actions.
"""

import json
import asyncio
import websockets
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

import sys
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rate_limiter import RateLimiter
    from template_loader import TemplateLoader
    from team_manager import TeamManager
except ImportError:
    RateLimiter = None
    TemplateLoader = None
    TeamManager = None


@dataclass
class TwitterAction:
    """A Twitter action to be executed via Browser-Use"""
    action_type: str
    target_handle: str  # @username
    target_name: str
    target_url: str = ""  # Full URL if available
    message: Optional[str] = None
    template_path: Optional[str] = None
    template_vars: Optional[Dict] = None
    tweet_url: Optional[str] = None  # For replies/likes
    max_steps: int = 10


class TwitterAdapter:
    """
    Twitter automation adapter using WebSocket connection.

    Supported Actions:
    - follow: Follow a user
    - like_tweet: Like a specific tweet
    - retweet: Retweet a tweet
    - reply: Reply to a tweet
    - dm: Send a direct message
    - quote_tweet: Quote tweet with comment
    """

    ACTIONS = {
        'follow': {
            'description': 'Follow a Twitter user',
            'rate_limit_key': 'follows_per_day',
            'max_steps': 6
        },
        'like_tweet': {
            'description': 'Like a tweet',
            'rate_limit_key': 'likes_per_day',
            'max_steps': 5
        },
        'retweet': {
            'description': 'Retweet a tweet',
            'rate_limit_key': 'retweets_per_day',
            'max_steps': 5
        },
        'reply': {
            'description': 'Reply to a tweet',
            'rate_limit_key': 'tweets_per_day',
            'max_steps': 8
        },
        'dm': {
            'description': 'Send a direct message',
            'rate_limit_key': 'dms_per_day',
            'max_steps': 10
        },
        'quote_tweet': {
            'description': 'Quote tweet with your comment',
            'rate_limit_key': 'tweets_per_day',
            'max_steps': 8
        }
    }

    def __init__(self, data_dir: str = ".", ws_url: str = 'ws://localhost:3000/ws'):
        self.data_dir = Path(data_dir)
        self.ws_url = ws_url
        self.ws = None
        self.timeout = 30
        self.rate_limiter = RateLimiter() if RateLimiter else None
        self.template_loader = TemplateLoader() if TemplateLoader else None
        self.team_manager = TeamManager() if TeamManager else None
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def _connect(self):
        """Establish WebSocket connection"""
        if self.ws is None or self.ws.closed:
            self.ws = await websockets.connect(self.ws_url)

    async def _send_action(self, action_type: str, payload: Dict) -> Dict:
        """Send action via WebSocket and wait for response"""
        try:
            await self._connect()

            command = {
                "type": "twitter-action",
                "payload": {
                    "type": action_type,
                    **payload
                }
            }

            await self.ws.send(json.dumps(command))

            # Wait for response with timeout
            response = await asyncio.wait_for(
                self.ws.recv(),
                timeout=self.timeout
            )

            return json.loads(response)
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': f'WebSocket timeout after {self.timeout}s'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def execute_action(self, action: TwitterAction, user_id: str = "default") -> Dict:
        """
        Execute Twitter action via WebSocket (synchronous wrapper).

        Returns:
        - success: Whether action succeeded
        - message: Rendered message if applicable
        - error: Error message if failed
        - data: Response data from server
        """
        # Check rate limits
        if self.rate_limiter:
            can_proceed, reason, wait_seconds = self.rate_limiter.can_proceed(
                user_id, 'twitter', action.action_type
            )
            if not can_proceed:
                return {
                    'success': False,
                    'can_proceed': False,
                    'reason': reason,
                    'wait_seconds': wait_seconds
                }

        # Render message template
        message = action.message
        if action.template_path and self.template_loader:
            template_vars = action.template_vars or {}
            template_vars['first_name'] = action.target_name.split()[0] if action.target_name else ''
            template_vars['name'] = action.target_name
            template_vars['handle'] = action.target_handle
            result = self.template_loader.render_by_path(action.template_path, template_vars)
            message = result.get('content', message)

        # Build payload
        handle = action.target_handle.lstrip('@')
        payload = {
            'target_handle': handle,
            'target_name': action.target_name
        }

        if message:
            payload['message'] = message
        if action.tweet_url:
            payload['tweet_url'] = action.tweet_url
        if action.target_url:
            payload['target_url'] = action.target_url

        # Execute via WebSocket
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self._send_action(action.action_type, payload)
            )

            # Record action
            if result.get('success'):
                self.record_action(user_id, action, True, result.get('data'))
            else:
                self.record_action(user_id, action, False, result.get('error'))

            result['message'] = message
            return result
        finally:
            loop.close()

    def generate_task(self, action: TwitterAction, user_id: str = "default") -> Dict:
        """Legacy method for compatibility. Now executes via WebSocket."""
        return self.execute_action(action, user_id)

    async def close(self):
        """Close WebSocket connection"""
        if self.ws and not self.ws.closed:
            await self.ws.close()
        if self._executor:
            self._executor.shutdown(wait=False)

    def __del__(self):
        """Cleanup on object deletion"""
        if self.ws and not self.ws.closed:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.close())
            finally:
                loop.close()

    def record_action(self, user_id: str, action: TwitterAction, success: bool, details: str = None):
        """Record action for rate limiting."""
        if self.rate_limiter:
            self.rate_limiter.record_action(
                user_id, 'twitter', action.action_type,
                action.target_handle, success, details
            )

    def get_remaining_limits(self, user_id: str = "default") -> Dict[str, int]:
        """Get remaining action limits."""
        if self.rate_limiter:
            return self.rate_limiter.get_remaining_limits(user_id, 'twitter')
        return {}

    def calculate_delay(self, action_type: str) -> int:
        """Calculate delay before next action."""
        if self.rate_limiter:
            return self.rate_limiter.calculate_delay('twitter', action_type)
        return 60


# Helper functions for creating actions
def create_follow_action(handle: str, name: str = "") -> TwitterAction:
    return TwitterAction(action_type='follow', target_handle=handle, target_name=name, max_steps=6)

def create_dm_action(handle: str, name: str, template_path: str = None,
                     template_vars: Dict = None, message: str = None) -> TwitterAction:
    return TwitterAction(
        action_type='dm', target_handle=handle, target_name=name,
        message=message, template_path=template_path or 'twitter/dms/cold_dm',
        template_vars=template_vars, max_steps=10
    )

def create_reply_action(handle: str, name: str, tweet_url: str,
                        template_path: str = None, template_vars: Dict = None,
                        message: str = None) -> TwitterAction:
    return TwitterAction(
        action_type='reply', target_handle=handle, target_name=name,
        tweet_url=tweet_url, message=message,
        template_path=template_path or 'twitter/replies/value_add',
        template_vars=template_vars, max_steps=8
    )

def create_like_action(handle: str, name: str = "", tweet_url: str = None) -> TwitterAction:
    return TwitterAction(
        action_type='like_tweet', target_handle=handle, target_name=name,
        tweet_url=tweet_url, max_steps=5
    )


def main():
    """CLI for Twitter adapter."""
    import argparse

    parser = argparse.ArgumentParser(description="Twitter Adapter CLI")
    subparsers = parser.add_subparsers(dest='command')

    # Generate task
    task_parser = subparsers.add_parser('task', help='Generate browser task')
    task_parser.add_argument('--action', required=True,
                             choices=['follow', 'like_tweet', 'retweet', 'reply', 'dm', 'quote_tweet'])
    task_parser.add_argument('--handle', required=True, help='Target @handle')
    task_parser.add_argument('--name', default='', help='Target name')
    task_parser.add_argument('--message', help='Message text')
    task_parser.add_argument('--template', help='Template path')
    task_parser.add_argument('--tweet-url', help='Tweet URL for replies/likes')
    task_parser.add_argument('--user', default='default', help='User ID')

    # Limits
    limits_parser = subparsers.add_parser('limits', help='Check rate limits')
    limits_parser.add_argument('--user', default='default')

    # Actions list
    subparsers.add_parser('actions', help='List available actions')

    args = parser.parse_args()
    adapter = TwitterAdapter()

    if args.command == 'task':
        action = TwitterAction(
            action_type=args.action,
            target_handle=args.handle,
            target_name=args.name,
            message=args.message,
            template_path=args.template,
            tweet_url=args.tweet_url
        )
        result = adapter.generate_task(action, args.user)
        print(json.dumps(result, indent=2))

    elif args.command == 'limits':
        limits = adapter.get_remaining_limits(args.user)
        print("Remaining Twitter limits:")
        for action, remaining in limits.items():
            print(f"  {action}: {remaining}")

    elif args.command == 'actions':
        print("Available Twitter Actions:")
        for action, info in TwitterAdapter.ACTIONS.items():
            print(f"  {action}: {info['description']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
