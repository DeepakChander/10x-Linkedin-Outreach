#!/usr/bin/env python3
"""
LinkedIn Adapter for 100X Outreach System

Provides LinkedIn automation actions using WebSocket connection.
All actions are executed through authenticated browser profiles.

This adapter connects to ws://localhost:3001/ws and sends platform-specific actions.
"""

import json
import asyncio
import websockets
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

# Import local modules
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
class LinkedInAction:
    """A LinkedIn action to be executed"""
    action_type: str
    target_url: str
    target_name: str
    message: Optional[str] = None
    template_path: Optional[str] = None
    template_vars: Optional[Dict] = None
    browser_task: Optional[str] = None  # Generated browser task description
    max_steps: int = 10


class LinkedInAdapter:
    """
    LinkedIn automation adapter using WebSocket connection.

    Supported Actions:
    - view_profile: Visit a LinkedIn profile
    - like_post: Like a post on LinkedIn
    - comment: Comment on a post
    - connect: Send a connection request
    - message: Send a direct message
    - follow: Follow a person/company
    """

    ACTIONS = {
        'view_profile': {
            'description': 'View a LinkedIn profile',
            'rate_limit_key': 'profile_views_per_day',
            'max_steps': 5
        },
        'like_post': {
            'description': 'Like a LinkedIn post',
            'rate_limit_key': 'likes_per_day',
            'max_steps': 8
        },
        'comment': {
            'description': 'Comment on a LinkedIn post',
            'rate_limit_key': 'comments_per_day',
            'max_steps': 10
        },
        'connect': {
            'description': 'Send a connection request',
            'rate_limit_key': 'connections_per_day',
            'max_steps': 12
        },
        'message': {
            'description': 'Send a direct message',
            'rate_limit_key': 'messages_per_day',
            'max_steps': 12
        },
        'follow': {
            'description': 'Follow a person or company',
            'rate_limit_key': 'connections_per_day',
            'max_steps': 8
        }
    }

    def __init__(self, data_dir: str = ".", ws_url: str = 'ws://localhost:3001/ws'):
        self.data_dir = Path(data_dir)
        self.ws_url = ws_url
        self.ws = None
        self.timeout = 30  # 30 seconds timeout
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
                "type": "linkedin-action",
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

    def execute_action(self, action: LinkedInAction, user_id: str = "default") -> Dict:
        """
        Execute LinkedIn action via WebSocket (synchronous wrapper).

        Returns a dict with:
        - success: Whether action succeeded
        - message: Rendered message if applicable
        - error: Error message if failed
        - data: Response data from server
        """
        # Check rate limits
        if self.rate_limiter:
            can_proceed, reason, wait_seconds = self.rate_limiter.can_proceed(
                user_id, 'linkedin', action.action_type
            )
            if not can_proceed:
                return {
                    'success': False,
                    'can_proceed': False,
                    'reason': reason,
                    'wait_seconds': wait_seconds
                }

        # Render message template if provided
        message = action.message
        if action.template_path and self.template_loader:
            template_vars = action.template_vars or {}
            template_vars['first_name'] = action.target_name.split()[0] if action.target_name else ''
            template_vars['name'] = action.target_name
            result = self.template_loader.render_by_path(action.template_path, template_vars)
            message = result.get('content', message)

        # Build payload based on action type
        payload = {
            'profile_url': action.target_url,
            'target_name': action.target_name
        }

        if message:
            payload['message'] = message

        # Execute via WebSocket
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self._send_action(action.action_type, payload)
            )

            # Record action for rate limiting
            if result.get('success'):
                self.record_action(user_id, action, True, result.get('data'))
            else:
                self.record_action(user_id, action, False, result.get('error'))

            result['message'] = message
            return result
        finally:
            loop.close()

    def generate_task(self, action: LinkedInAction, user_id: str = "default") -> Dict:
        """
        Legacy method for compatibility.
        Now returns WebSocket execution result instead of browser task.
        """
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

    def record_action(self, user_id: str, action: LinkedInAction, success: bool, details: str = None):
        """Record an action for rate limiting"""
        if self.rate_limiter:
            self.rate_limiter.record_action(
                user_id,
                'linkedin',
                action.action_type,
                action.target_url,
                success,
                details
            )

    def get_remaining_limits(self, user_id: str = "default") -> Dict[str, int]:
        """Get remaining action limits for today"""
        if self.rate_limiter:
            return self.rate_limiter.get_remaining_limits(user_id, 'linkedin')
        return {}

    def calculate_delay(self, action_type: str) -> int:
        """Calculate delay before next action"""
        if self.rate_limiter:
            return self.rate_limiter.calculate_delay('linkedin', action_type)
        return 120  # Default 2 minutes


def create_view_profile_action(profile_url: str, name: str = "") -> LinkedInAction:
    """Helper to create a view profile action"""
    return LinkedInAction(
        action_type='view_profile',
        target_url=profile_url,
        target_name=name,
        max_steps=5
    )


def create_connect_action(profile_url: str, name: str, template_path: str = None,
                          template_vars: Dict = None, message: str = None) -> LinkedInAction:
    """Helper to create a connection request action"""
    return LinkedInAction(
        action_type='connect',
        target_url=profile_url,
        target_name=name,
        message=message,
        template_path=template_path or 'linkedin/connection-requests/cold_outreach',
        template_vars=template_vars,
        max_steps=12
    )


def create_message_action(profile_url: str, name: str, template_path: str = None,
                          template_vars: Dict = None, message: str = None) -> LinkedInAction:
    """Helper to create a message action"""
    return LinkedInAction(
        action_type='message',
        target_url=profile_url,
        target_name=name,
        message=message,
        template_path=template_path or 'linkedin/messages/intro_after_connect',
        template_vars=template_vars,
        max_steps=12
    )


def create_like_action(profile_url: str, name: str = "") -> LinkedInAction:
    """Helper to create a like post action"""
    return LinkedInAction(
        action_type='like_post',
        target_url=profile_url,
        target_name=name,
        max_steps=8
    )


def create_comment_action(profile_url: str, name: str, comment: str = None,
                          template_path: str = None, template_vars: Dict = None) -> LinkedInAction:
    """Helper to create a comment action"""
    return LinkedInAction(
        action_type='comment',
        target_url=profile_url,
        target_name=name,
        message=comment,
        template_path=template_path,
        template_vars=template_vars,
        max_steps=10
    )


def main():
    """CLI interface for LinkedIn adapter"""
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn Adapter CLI")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Generate task
    task_parser = subparsers.add_parser('task', help='Generate browser task')
    task_parser.add_argument('--action', required=True,
                             choices=['view_profile', 'like_post', 'comment', 'connect', 'message', 'follow'])
    task_parser.add_argument('--url', required=True, help='Target LinkedIn URL')
    task_parser.add_argument('--name', default='', help='Target name')
    task_parser.add_argument('--message', help='Message or comment text')
    task_parser.add_argument('--template', help='Template path')
    task_parser.add_argument('--user', default='default', help='User ID')

    # Check limits
    limits_parser = subparsers.add_parser('limits', help='Check rate limits')
    limits_parser.add_argument('--user', default='default', help='User ID')

    # Calculate delay
    delay_parser = subparsers.add_parser('delay', help='Calculate delay')
    delay_parser.add_argument('--action', required=True, help='Action type')

    # List actions
    subparsers.add_parser('actions', help='List available actions')

    args = parser.parse_args()

    adapter = LinkedInAdapter()

    if args.command == 'task':
        action = LinkedInAction(
            action_type=args.action,
            target_url=args.url,
            target_name=args.name,
            message=args.message,
            template_path=args.template
        )
        result = adapter.generate_task(action, args.user)
        print(json.dumps(result, indent=2))

    elif args.command == 'limits':
        limits = adapter.get_remaining_limits(args.user)
        print("Remaining LinkedIn limits for today:")
        for action, remaining in limits.items():
            print(f"  {action}: {remaining}")

    elif args.command == 'delay':
        delay = adapter.calculate_delay(args.action)
        print(f"Recommended delay for {args.action}: {delay} seconds")

    elif args.command == 'actions':
        print("Available LinkedIn Actions:")
        for action, info in LinkedInAdapter.ACTIONS.items():
            print(f"  {action}: {info['description']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
