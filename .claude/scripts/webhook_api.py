#!/usr/bin/env python3
"""
Webhook API for 10x-Outreach-Skill
External system integration via webhooks

Features:
- Webhook endpoint registration
- HMAC-SHA256 payload signing
- Automatic retries (3x with exponential backoff)
- Event types: workflow, email, platform, system
- Delivery tracking and history

Events:
- workflow.trigger / workflow.completed / workflow.failed
- email.received / email.replied
- ticket.created / ticket.updated / ticket.resolved
- system.rate_limit_warning / system.error

Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import sys
import json
import hmac
import hashlib
import uuid
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
import queue

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[X] Missing dependency: {e}")
    sys.exit(1)

# Try to import aiohttp for async webhook delivery
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# Fallback to requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Import audit logger
try:
    from audit_logger import audit_log, EventType, EventSeverity
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False

load_dotenv(Path(__file__).parent.parent / '.env')


class WebhookEventType(str, Enum):
    """Webhook event types."""
    # Workflow events
    WORKFLOW_TRIGGER = 'workflow.trigger'
    WORKFLOW_COMPLETED = 'workflow.completed'
    WORKFLOW_FAILED = 'workflow.failed'
    WORKFLOW_STEP = 'workflow.step'

    # Email events
    EMAIL_RECEIVED = 'email.received'
    EMAIL_REPLIED = 'email.replied'
    EMAIL_SENT = 'email.sent'

    # Ticket events
    TICKET_CREATED = 'ticket.created'
    TICKET_UPDATED = 'ticket.updated'
    TICKET_RESOLVED = 'ticket.resolved'
    TICKET_SLA_WARNING = 'ticket.sla_warning'
    TICKET_SLA_BREACH = 'ticket.sla_breach'

    # Platform events
    PLATFORM_ACTION = 'platform.action'
    PLATFORM_ERROR = 'platform.error'

    # System events
    SYSTEM_RATE_LIMIT = 'system.rate_limit_warning'
    SYSTEM_ERROR = 'system.error'
    SYSTEM_HEALTH = 'system.health'


@dataclass
class WebhookEndpoint:
    """Registered webhook endpoint."""
    id: str
    url: str
    events: List[str]
    secret: str
    active: bool
    created_at: str
    description: Optional[str] = None
    tenant_id: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    retry_count: int = 3
    timeout_seconds: int = 30


@dataclass
class WebhookDelivery:
    """Webhook delivery record."""
    id: str
    endpoint_id: str
    event_type: str
    payload: Dict
    status: str  # pending, success, failed
    attempts: int
    created_at: str
    delivered_at: Optional[str] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None


class WebhookManager:
    """
    Webhook management and delivery system.

    Handles:
    - Endpoint registration and management
    - Event dispatching
    - Secure payload signing
    - Retry logic with exponential backoff
    - Delivery tracking
    """

    # Retry delays in seconds
    RETRY_DELAYS = [5, 30, 300]  # 5s, 30s, 5min

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize webhook manager."""
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.webhooks_dir = self.base_dir / 'webhooks'
        self.webhooks_dir.mkdir(parents=True, exist_ok=True)

        # Endpoint storage
        self._endpoints_path = self.webhooks_dir / 'endpoints.json'
        self._endpoints: Dict[str, WebhookEndpoint] = self._load_endpoints()

        # Delivery history
        self._history_dir = self.webhooks_dir / 'history'
        self._history_dir.mkdir(exist_ok=True)

        # Pending delivery queue
        self._delivery_queue = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def _load_endpoints(self) -> Dict[str, WebhookEndpoint]:
        """Load registered endpoints."""
        if self._endpoints_path.exists():
            try:
                with open(self._endpoints_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                endpoints = {}
                for eid, edata in data.items():
                    endpoints[eid] = WebhookEndpoint(**edata)
                return endpoints
            except Exception as e:
                print(f"[!] Error loading webhook endpoints: {e}")

        return {}

    def _save_endpoints(self):
        """Save endpoints to file."""
        data = {eid: asdict(ep) for eid, ep in self._endpoints.items()}

        with open(self._endpoints_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def register(
        self,
        url: str,
        events: List[str],
        description: Optional[str] = None,
        tenant_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> WebhookEndpoint:
        """
        Register a new webhook endpoint.

        Args:
            url: Webhook URL
            events: List of event types to subscribe to
            description: Optional description
            tenant_id: Tenant ID for multi-tenant isolation
            headers: Custom headers to include
            secret: Custom signing secret (auto-generated if not provided)

        Returns:
            Registered WebhookEndpoint
        """
        endpoint_id = f"WH-{str(uuid.uuid4())[:8].upper()}"

        # Generate signing secret
        if not secret:
            secret = hashlib.sha256(os.urandom(32)).hexdigest()

        endpoint = WebhookEndpoint(
            id=endpoint_id,
            url=url,
            events=events,
            secret=secret,
            active=True,
            created_at=datetime.utcnow().isoformat() + 'Z',
            description=description,
            tenant_id=tenant_id,
            headers=headers or {}
        )

        self._endpoints[endpoint_id] = endpoint
        self._save_endpoints()

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.SYSTEM,
                'webhook_registered',
                {'endpoint_id': endpoint_id, 'url': url, 'events': events}
            )

        return endpoint

    def unregister(self, endpoint_id: str) -> bool:
        """Unregister a webhook endpoint."""
        if endpoint_id in self._endpoints:
            del self._endpoints[endpoint_id]
            self._save_endpoints()
            return True
        return False

    def update(
        self,
        endpoint_id: str,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        active: Optional[bool] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[WebhookEndpoint]:
        """Update endpoint configuration."""
        if endpoint_id not in self._endpoints:
            return None

        endpoint = self._endpoints[endpoint_id]

        if url is not None:
            endpoint.url = url
        if events is not None:
            endpoint.events = events
        if active is not None:
            endpoint.active = active
        if headers is not None:
            endpoint.headers = headers

        self._save_endpoints()
        return endpoint

    def get_endpoint(self, endpoint_id: str) -> Optional[WebhookEndpoint]:
        """Get endpoint by ID."""
        return self._endpoints.get(endpoint_id)

    def list_endpoints(self, tenant_id: Optional[str] = None) -> List[WebhookEndpoint]:
        """List all endpoints, optionally filtered by tenant."""
        endpoints = list(self._endpoints.values())

        if tenant_id:
            endpoints = [e for e in endpoints if e.tenant_id == tenant_id]

        return endpoints

    def _sign_payload(self, payload: str, secret: str) -> str:
        """Compute HMAC-SHA256 signature for payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def dispatch(
        self,
        event_type: str,
        data: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> List[str]:
        """
        Dispatch event to all subscribed webhooks.

        Args:
            event_type: Event type string
            data: Event payload data
            tenant_id: Tenant ID for filtering

        Returns:
            List of delivery IDs
        """
        delivery_ids = []

        # Build payload
        payload = {
            'event': event_type,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'data': data
        }

        # Find matching endpoints
        for endpoint in self._endpoints.values():
            if not endpoint.active:
                continue

            # Tenant filter
            if tenant_id and endpoint.tenant_id and endpoint.tenant_id != tenant_id:
                continue

            # Event filter
            if event_type not in endpoint.events and '*' not in endpoint.events:
                # Check wildcard patterns
                event_prefix = event_type.split('.')[0] + '.*'
                if event_prefix not in endpoint.events:
                    continue

            # Create delivery record
            delivery_id = f"DLV-{str(uuid.uuid4())[:8].upper()}"
            delivery = WebhookDelivery(
                id=delivery_id,
                endpoint_id=endpoint.id,
                event_type=event_type,
                payload=payload,
                status='pending',
                attempts=0,
                created_at=datetime.utcnow().isoformat() + 'Z'
            )

            # Queue for delivery
            self._delivery_queue.put((delivery, endpoint))
            delivery_ids.append(delivery_id)

        # Ensure worker is running
        self._ensure_worker()

        return delivery_ids

    def _ensure_worker(self):
        """Ensure delivery worker thread is running."""
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._stop_event.clear()
            self._worker_thread = threading.Thread(target=self._delivery_worker, daemon=True)
            self._worker_thread.start()

    def _delivery_worker(self):
        """Background worker for webhook delivery."""
        while not self._stop_event.is_set():
            try:
                # Get delivery from queue with timeout
                try:
                    delivery, endpoint = self._delivery_queue.get(timeout=1)
                except queue.Empty:
                    continue

                # Attempt delivery
                self._deliver(delivery, endpoint)

            except Exception as e:
                print(f"[!] Webhook worker error: {e}")

    def _deliver(self, delivery: WebhookDelivery, endpoint: WebhookEndpoint):
        """Deliver webhook with retries."""
        payload_json = json.dumps(delivery.payload)
        signature = self._sign_payload(payload_json, endpoint.secret)

        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': f'sha256={signature}',
            'X-Webhook-Event': delivery.event_type,
            'X-Webhook-Delivery-ID': delivery.id,
            **endpoint.headers
        }

        max_attempts = endpoint.retry_count + 1

        for attempt in range(max_attempts):
            delivery.attempts = attempt + 1

            try:
                if REQUESTS_AVAILABLE:
                    response = requests.post(
                        endpoint.url,
                        data=payload_json,
                        headers=headers,
                        timeout=endpoint.timeout_seconds
                    )

                    delivery.response_code = response.status_code
                    delivery.response_body = response.text[:1000]  # Limit response size

                    if 200 <= response.status_code < 300:
                        delivery.status = 'success'
                        delivery.delivered_at = datetime.utcnow().isoformat() + 'Z'
                        self._save_delivery(delivery)
                        return

                    # Non-2xx response
                    delivery.error = f"HTTP {response.status_code}"

                else:
                    delivery.status = 'failed'
                    delivery.error = 'No HTTP client available'
                    self._save_delivery(delivery)
                    return

            except Exception as e:
                delivery.error = str(e)

            # Retry if not last attempt
            if attempt < max_attempts - 1:
                delay = self.RETRY_DELAYS[min(attempt, len(self.RETRY_DELAYS) - 1)]
                self._stop_event.wait(delay)

        # All retries exhausted
        delivery.status = 'failed'
        self._save_delivery(delivery)

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.SYSTEM,
                'webhook_delivery_failed',
                {
                    'delivery_id': delivery.id,
                    'endpoint_id': endpoint.id,
                    'attempts': delivery.attempts,
                    'error': delivery.error
                },
                EventSeverity.WARNING
            )

    def _save_delivery(self, delivery: WebhookDelivery):
        """Save delivery record to history."""
        # Organize by date
        date_str = datetime.utcnow().strftime('%Y%m%d')
        date_dir = self._history_dir / date_str
        date_dir.mkdir(exist_ok=True)

        delivery_path = date_dir / f"{delivery.id}.json"

        with open(delivery_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(delivery), f, indent=2)

    def get_delivery_history(
        self,
        endpoint_id: Optional[str] = None,
        status: Optional[str] = None,
        days: int = 7
    ) -> List[Dict]:
        """Get delivery history."""
        deliveries = []
        cutoff = datetime.utcnow() - timedelta(days=days)

        for date_dir in self._history_dir.iterdir():
            if not date_dir.is_dir():
                continue

            # Date filter
            try:
                dir_date = datetime.strptime(date_dir.name, '%Y%m%d')
                if dir_date < cutoff:
                    continue
            except ValueError:
                continue

            for delivery_path in date_dir.glob('*.json'):
                try:
                    with open(delivery_path, 'r', encoding='utf-8') as f:
                        delivery = json.load(f)

                    # Filters
                    if endpoint_id and delivery.get('endpoint_id') != endpoint_id:
                        continue
                    if status and delivery.get('status') != status:
                        continue

                    deliveries.append(delivery)

                except:
                    continue

        # Sort by created_at
        deliveries.sort(key=lambda d: d.get('created_at', ''), reverse=True)

        return deliveries

    def get_stats(self) -> Dict[str, Any]:
        """Get webhook statistics."""
        stats = {
            'total_endpoints': len(self._endpoints),
            'active_endpoints': sum(1 for e in self._endpoints.values() if e.active),
            'deliveries_today': 0,
            'success_rate': 0.0,
            'by_status': {'success': 0, 'failed': 0, 'pending': 0}
        }

        # Count today's deliveries
        today_dir = self._history_dir / datetime.utcnow().strftime('%Y%m%d')
        if today_dir.exists():
            for path in today_dir.glob('*.json'):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        delivery = json.load(f)

                    stats['deliveries_today'] += 1
                    status = delivery.get('status', 'unknown')
                    if status in stats['by_status']:
                        stats['by_status'][status] += 1

                except:
                    continue

        total = stats['by_status']['success'] + stats['by_status']['failed']
        if total > 0:
            stats['success_rate'] = round(stats['by_status']['success'] / total * 100, 1)

        return stats

    def stop(self):
        """Stop the webhook manager."""
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=5)


# Global instance
_webhook_manager: Optional[WebhookManager] = None


def get_webhook_manager(base_dir: Optional[Path] = None) -> WebhookManager:
    """Get or create webhook manager instance."""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager(base_dir)
    return _webhook_manager


def dispatch_event(
    event_type: str,
    data: Dict[str, Any],
    tenant_id: Optional[str] = None
) -> List[str]:
    """Convenience function to dispatch webhook event."""
    manager = get_webhook_manager()
    return manager.dispatch(event_type, data, tenant_id)


# CLI
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Webhook Manager CLI')
    parser.add_argument('--register', metavar='URL', help='Register new webhook')
    parser.add_argument('--events', help='Comma-separated events for registration')
    parser.add_argument('--list', action='store_true', help='List registered webhooks')
    parser.add_argument('--unregister', metavar='ID', help='Unregister webhook')
    parser.add_argument('--history', action='store_true', help='Show delivery history')
    parser.add_argument('--stats', action='store_true', help='Show webhook statistics')
    parser.add_argument('--test', metavar='ID', help='Send test event to endpoint')

    args = parser.parse_args()

    manager = WebhookManager()

    if args.register:
        events = args.events.split(',') if args.events else ['*']
        endpoint = manager.register(args.register, events)
        print(f"\nRegistered webhook:")
        print(f"  ID: {endpoint.id}")
        print(f"  URL: {endpoint.url}")
        print(f"  Events: {endpoint.events}")
        print(f"  Secret: {endpoint.secret}")

    elif args.list:
        endpoints = manager.list_endpoints()
        print(f"\nRegistered Webhooks ({len(endpoints)}):\n")
        for ep in endpoints:
            status = 'Active' if ep.active else 'Inactive'
            print(f"  {ep.id}: {ep.url}")
            print(f"        Events: {', '.join(ep.events)}")
            print(f"        Status: {status}")

    elif args.unregister:
        if manager.unregister(args.unregister):
            print(f"Unregistered: {args.unregister}")
        else:
            print(f"Not found: {args.unregister}")

    elif args.history:
        history = manager.get_delivery_history()
        print(f"\nRecent Deliveries ({len(history)}):\n")
        for d in history[:20]:
            status_icon = '✓' if d['status'] == 'success' else '✗'
            print(f"  {status_icon} {d['id']}: {d['event_type']}")
            print(f"        Status: {d['status']}, Attempts: {d['attempts']}")

    elif args.stats:
        stats = manager.get_stats()
        print(f"\nWebhook Statistics:")
        print(f"  Total endpoints: {stats['total_endpoints']}")
        print(f"  Active endpoints: {stats['active_endpoints']}")
        print(f"  Deliveries today: {stats['deliveries_today']}")
        print(f"  Success rate: {stats['success_rate']}%")

    elif args.test:
        endpoint = manager.get_endpoint(args.test)
        if endpoint:
            delivery_ids = manager.dispatch(
                'system.test',
                {'message': 'Test webhook delivery'},
            )
            print(f"Dispatched test event. Delivery ID: {delivery_ids}")
        else:
            print(f"Endpoint not found: {args.test}")

    else:
        parser.print_help()
