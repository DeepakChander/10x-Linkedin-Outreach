#!/usr/bin/env python3
"""
Test script for WebSocket adapters.
Verifies LinkedIn, Instagram, and Twitter adapters work with WebSocket connection.
"""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from linkedin_adapter import LinkedInAdapter, LinkedInAction, create_connect_action
from instagram_adapter import InstagramAdapter, InstagramAction, create_dm_action
from twitter_adapter import TwitterAdapter, TwitterAction, create_follow_action


def test_linkedin_adapter():
    """Test LinkedIn adapter WebSocket connectivity"""
    print("\n=== Testing LinkedIn Adapter ===")

    adapter = LinkedInAdapter()

    # Test connection action
    action = LinkedInAction(
        action_type='connect',
        target_url='https://linkedin.com/in/test-user',
        target_name='Test User',
        message='Hi Test, I would love to connect!'
    )

    print(f"Action type: {action.action_type}")
    print(f"Target: {action.target_name}")
    print(f"Message: {action.message}")

    # Note: This will fail if WebSocket server is not running
    # That's expected - this is to test the adapter structure
    try:
        result = adapter.execute_action(action, user_id="test_user")
        print(f"Result: {json.dumps(result, indent=2)}")
        return result.get('success', False)
    except Exception as e:
        print(f"Expected error (server not running): {e}")
        return False


def test_instagram_adapter():
    """Test Instagram adapter WebSocket connectivity"""
    print("\n=== Testing Instagram Adapter ===")

    adapter = InstagramAdapter()

    # Test DM action
    action = InstagramAction(
        action_type='dm',
        target_handle='@testuser',
        target_name='Test User',
        message='Hey Test! Love your content!'
    )

    print(f"Action type: {action.action_type}")
    print(f"Target: {action.target_handle}")
    print(f"Message: {action.message}")

    try:
        result = adapter.execute_action(action, user_id="test_user")
        print(f"Result: {json.dumps(result, indent=2)}")
        return result.get('success', False)
    except Exception as e:
        print(f"Expected error (server not running): {e}")
        return False


def test_twitter_adapter():
    """Test Twitter adapter WebSocket connectivity"""
    print("\n=== Testing Twitter Adapter ===")

    adapter = TwitterAdapter()

    # Test follow action
    action = TwitterAction(
        action_type='follow',
        target_handle='@testuser',
        target_name='Test User'
    )

    print(f"Action type: {action.action_type}")
    print(f"Target: {action.target_handle}")

    try:
        result = adapter.execute_action(action, user_id="test_user")
        print(f"Result: {json.dumps(result, indent=2)}")
        return result.get('success', False)
    except Exception as e:
        print(f"Expected error (server not running): {e}")
        return False


def test_helper_functions():
    """Test helper functions for creating actions"""
    print("\n=== Testing Helper Functions ===")

    # LinkedIn
    linkedin_action = create_connect_action(
        profile_url='https://linkedin.com/in/test',
        name='Test User',
        message='Hello!'
    )
    print(f"LinkedIn action created: {linkedin_action.action_type}")

    # Instagram
    instagram_action = create_dm_action(
        handle='@test',
        name='Test User',
        message='Hey there!'
    )
    print(f"Instagram action created: {instagram_action.action_type}")

    # Twitter
    twitter_action = create_follow_action(
        handle='@test',
        name='Test User'
    )
    print(f"Twitter action created: {twitter_action.action_type}")

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("WebSocket Adapters Test Suite")
    print("=" * 60)
    print("\nNote: WebSocket server should be running at ws://localhost:3000/ws")
    print("If not running, connection errors are expected.\n")

    tests = [
        ("LinkedIn Adapter", test_linkedin_adapter),
        ("Instagram Adapter", test_instagram_adapter),
        ("Twitter Adapter", test_twitter_adapter),
        ("Helper Functions", test_helper_functions),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL] (expected if server not running)"
        print(f"{test_name}: {status}")

    print("\n" + "=" * 60)
    print("Test suite completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
