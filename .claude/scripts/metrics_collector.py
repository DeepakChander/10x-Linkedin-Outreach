#!/usr/bin/env python3
"""
Metrics Collector for 10x-Outreach-Skill
Real-time dashboard data for IT Operations Support

Metrics:
- Queue depths (workflows, actions, emails)
- Processing rates (per minute/hour)
- Success/failure rates by platform
- Response time histograms (p50, p95, p99)
- Prometheus export format

Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from collections import defaultdict
from dataclasses import dataclass, field
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[X] Missing dependency: {e}")
    sys.exit(1)

load_dotenv(Path(__file__).parent.parent / '.env')


@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


class Counter:
    """Cumulative counter metric."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._values: Dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()

    def inc(self, value: float = 1, labels: Optional[Dict[str, str]] = None):
        """Increment counter."""
        label_key = self._label_key(labels)
        with self._lock:
            self._values[label_key] += value

    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get counter value."""
        label_key = self._label_key(labels)
        return self._values.get(label_key, 0)

    def _label_key(self, labels: Optional[Dict[str, str]]) -> str:
        if not labels:
            return ''
        return ','.join(f'{k}={v}' for k, v in sorted(labels.items()))


class Gauge:
    """Current value metric."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._values: Dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()

    def set(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Set gauge value."""
        label_key = self._label_key(labels)
        with self._lock:
            self._values[label_key] = value

    def inc(self, value: float = 1, labels: Optional[Dict[str, str]] = None):
        """Increment gauge."""
        label_key = self._label_key(labels)
        with self._lock:
            self._values[label_key] += value

    def dec(self, value: float = 1, labels: Optional[Dict[str, str]] = None):
        """Decrement gauge."""
        label_key = self._label_key(labels)
        with self._lock:
            self._values[label_key] -= value

    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value."""
        label_key = self._label_key(labels)
        return self._values.get(label_key, 0)

    def _label_key(self, labels: Optional[Dict[str, str]]) -> str:
        if not labels:
            return ''
        return ','.join(f'{k}={v}' for k, v in sorted(labels.items()))


class Histogram:
    """Distribution metric with percentile calculation."""

    def __init__(self, name: str, description: str, buckets: Optional[List[float]] = None):
        self.name = name
        self.description = description
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        self._values: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
        # Keep only last hour of values
        self._max_values = 10000

    def observe(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Record observation."""
        label_key = self._label_key(labels)
        with self._lock:
            values = self._values[label_key]
            values.append(value)
            # Trim if too many
            if len(values) > self._max_values:
                self._values[label_key] = values[-self._max_values:]

    def get_percentiles(self, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get percentile values."""
        label_key = self._label_key(labels)
        values = self._values.get(label_key, [])

        if not values:
            return {'p50': 0, 'p90': 0, 'p95': 0, 'p99': 0, 'count': 0, 'sum': 0}

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            'p50': sorted_values[int(count * 0.5)] if count > 0 else 0,
            'p90': sorted_values[int(count * 0.9)] if count > 0 else 0,
            'p95': sorted_values[int(count * 0.95)] if count > 0 else 0,
            'p99': sorted_values[int(count * 0.99)] if count > 0 else 0,
            'count': count,
            'sum': sum(values),
            'avg': statistics.mean(values) if values else 0
        }

    def _label_key(self, labels: Optional[Dict[str, str]]) -> str:
        if not labels:
            return ''
        return ','.join(f'{k}={v}' for k, v in sorted(labels.items()))


class MetricsCollector:
    """
    Metrics collection and export system.

    Provides real-time metrics for:
    - Queue depths
    - Processing rates
    - Success/failure rates
    - Response time distributions
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize metrics collector."""
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.metrics_dir = self.base_dir / 'metrics'
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Initialize metrics
        self._init_metrics()

        # Rate tracking
        self._rate_window_seconds = 60
        self._rate_events: Dict[str, List[float]] = defaultdict(list)
        self._rate_lock = threading.Lock()

        # Snapshot storage
        self._snapshots_path = self.metrics_dir / 'snapshots.jsonl'

    def _init_metrics(self):
        """Initialize metric objects."""
        # Counters
        self.emails_sent = Counter('emails_sent_total', 'Total emails sent')
        self.emails_received = Counter('emails_received_total', 'Total emails received')
        self.workflows_completed = Counter('workflows_completed_total', 'Total workflows completed')
        self.workflows_failed = Counter('workflows_failed_total', 'Total workflows failed')
        self.tickets_created = Counter('tickets_created_total', 'Total tickets created')
        self.tickets_resolved = Counter('tickets_resolved_total', 'Total tickets resolved')
        self.platform_actions = Counter('platform_actions_total', 'Total platform actions')
        self.api_requests = Counter('api_requests_total', 'Total API requests')
        self.errors = Counter('errors_total', 'Total errors')

        # Gauges
        self.queue_depth = Gauge('queue_depth', 'Current queue depth')
        self.active_workflows = Gauge('active_workflows', 'Currently active workflows')
        self.active_tickets = Gauge('active_tickets', 'Currently active tickets')
        self.connected_clients = Gauge('connected_clients', 'Currently connected clients')

        # Histograms
        self.email_send_duration = Histogram('email_send_duration_seconds', 'Email send duration')
        self.workflow_duration = Histogram('workflow_duration_seconds', 'Workflow execution duration')
        self.api_response_time = Histogram('api_response_time_seconds', 'API response time')
        self.ticket_response_time = Histogram('ticket_response_time_hours', 'Ticket first response time')

    def record_event(self, event_type: str, labels: Optional[Dict[str, str]] = None):
        """Record event for rate calculation."""
        with self._rate_lock:
            now = time.time()
            key = f"{event_type}:{self._label_key(labels)}"
            self._rate_events[key].append(now)

            # Clean old events
            cutoff = now - self._rate_window_seconds
            self._rate_events[key] = [t for t in self._rate_events[key] if t > cutoff]

    def get_rate(self, event_type: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get events per minute rate."""
        with self._rate_lock:
            key = f"{event_type}:{self._label_key(labels)}"
            events = self._rate_events.get(key, [])

            now = time.time()
            cutoff = now - self._rate_window_seconds
            recent = [t for t in events if t > cutoff]

            # Events per minute
            if len(recent) == 0:
                return 0

            return len(recent) / (self._rate_window_seconds / 60)

    def _label_key(self, labels: Optional[Dict[str, str]]) -> str:
        if not labels:
            return ''
        return ','.join(f'{k}={v}' for k, v in sorted(labels.items()))

    def record_email_sent(self, platform: str = 'gmail', success: bool = True, duration: float = 0):
        """Record email sent metric."""
        labels = {'platform': platform, 'status': 'success' if success else 'failure'}
        self.emails_sent.inc(labels=labels)
        self.record_event('email_sent', labels)

        if duration > 0:
            self.email_send_duration.observe(duration, {'platform': platform})

    def record_workflow(self, workflow_type: str, success: bool, duration: float = 0):
        """Record workflow completion."""
        labels = {'type': workflow_type}

        if success:
            self.workflows_completed.inc(labels=labels)
        else:
            self.workflows_failed.inc(labels=labels)

        self.record_event('workflow_complete', labels)

        if duration > 0:
            self.workflow_duration.observe(duration, labels)

    def record_ticket(self, action: str, priority: str):
        """Record ticket action."""
        labels = {'priority': priority}

        if action == 'created':
            self.tickets_created.inc(labels=labels)
        elif action == 'resolved':
            self.tickets_resolved.inc(labels=labels)

        self.record_event(f'ticket_{action}', labels)

    def record_platform_action(self, platform: str, action: str, success: bool):
        """Record social platform action."""
        labels = {'platform': platform, 'action': action, 'status': 'success' if success else 'failure'}
        self.platform_actions.inc(labels=labels)
        self.record_event('platform_action', labels)

    def record_api_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record API request."""
        labels = {
            'endpoint': endpoint,
            'method': method,
            'status': str(status_code // 100) + 'xx'
        }
        self.api_requests.inc(labels=labels)
        self.api_response_time.observe(duration, labels)

    def record_error(self, error_type: str, source: str):
        """Record error."""
        labels = {'type': error_type, 'source': source}
        self.errors.inc(labels=labels)
        self.record_event('error', labels)

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary for dashboard."""
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',

            # Counters
            'emails_sent_total': self.emails_sent.get(),
            'emails_received_total': self.emails_received.get(),
            'workflows_completed_total': self.workflows_completed.get(),
            'workflows_failed_total': self.workflows_failed.get(),
            'tickets_created_total': self.tickets_created.get(),
            'tickets_resolved_total': self.tickets_resolved.get(),

            # Gauges
            'queue_depth': {
                'workflow': self.queue_depth.get({'type': 'workflow'}),
                'email': self.queue_depth.get({'type': 'email'}),
                'action': self.queue_depth.get({'type': 'action'})
            },
            'active_workflows': self.active_workflows.get(),
            'active_tickets': self.active_tickets.get(),

            # Rates (per minute)
            'rates': {
                'emails_per_minute': self.get_rate('email_sent'),
                'workflows_per_minute': self.get_rate('workflow_complete'),
                'tickets_per_minute': self.get_rate('ticket_created')
            },

            # Histograms
            'response_times': {
                'email_send': self.email_send_duration.get_percentiles(),
                'workflow': self.workflow_duration.get_percentiles(),
                'api': self.api_response_time.get_percentiles()
            }
        }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        # Helper to format metric
        def fmt_metric(name: str, value: float, labels: str = '', help_text: str = ''):
            if help_text:
                lines.append(f'# HELP {name} {help_text}')
                lines.append(f'# TYPE {name} counter')
            label_str = f'{{{labels}}}' if labels else ''
            lines.append(f'{name}{label_str} {value}')

        # Counters
        fmt_metric('emails_sent_total', self.emails_sent.get(), help_text='Total emails sent')
        fmt_metric('workflows_completed_total', self.workflows_completed.get(), help_text='Total workflows completed')
        fmt_metric('workflows_failed_total', self.workflows_failed.get())
        fmt_metric('tickets_created_total', self.tickets_created.get())
        fmt_metric('tickets_resolved_total', self.tickets_resolved.get())

        # Gauges
        lines.append('# TYPE queue_depth gauge')
        lines.append(f'queue_depth{{type="workflow"}} {self.queue_depth.get({"type": "workflow"})}')
        lines.append(f'queue_depth{{type="email"}} {self.queue_depth.get({"type": "email"})}')
        lines.append(f'queue_depth{{type="action"}} {self.queue_depth.get({"type": "action"})}')

        lines.append('# TYPE active_workflows gauge')
        lines.append(f'active_workflows {self.active_workflows.get()}')

        # Histogram percentiles
        email_stats = self.email_send_duration.get_percentiles()
        lines.append('# TYPE email_send_duration_seconds summary')
        lines.append(f'email_send_duration_seconds{{quantile="0.5"}} {email_stats["p50"]}')
        lines.append(f'email_send_duration_seconds{{quantile="0.9"}} {email_stats["p90"]}')
        lines.append(f'email_send_duration_seconds{{quantile="0.95"}} {email_stats["p95"]}')
        lines.append(f'email_send_duration_seconds{{quantile="0.99"}} {email_stats["p99"]}')
        lines.append(f'email_send_duration_seconds_count {email_stats["count"]}')
        lines.append(f'email_send_duration_seconds_sum {email_stats["sum"]}')

        return '\n'.join(lines)

    def save_snapshot(self):
        """Save metrics snapshot to file."""
        snapshot = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            **self.get_summary()
        }

        with open(self._snapshots_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(snapshot) + '\n')

    def get_history(self, hours: int = 24) -> List[Dict]:
        """Get metrics history."""
        if not self._snapshots_path.exists():
            return []

        cutoff = datetime.utcnow() - timedelta(hours=hours)
        history = []

        with open(self._snapshots_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        snapshot = json.loads(line)
                        snap_time = datetime.fromisoformat(
                            snapshot['timestamp'].replace('Z', '+00:00')
                        )
                        if snap_time >= cutoff.replace(tzinfo=snap_time.tzinfo):
                            history.append(snapshot)
                    except:
                        continue

        return history


# Global instance
_collector: Optional[MetricsCollector] = None


def get_metrics_collector(base_dir: Optional[Path] = None) -> MetricsCollector:
    """Get or create metrics collector instance."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector(base_dir)
    return _collector


# CLI
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Metrics Collector CLI')
    parser.add_argument('--summary', action='store_true', help='Show metrics summary')
    parser.add_argument('--prometheus', action='store_true', help='Export Prometheus format')
    parser.add_argument('--snapshot', action='store_true', help='Save metrics snapshot')
    parser.add_argument('--test', action='store_true', help='Record test metrics')

    args = parser.parse_args()

    collector = MetricsCollector()

    if args.summary:
        summary = collector.get_summary()
        print(json.dumps(summary, indent=2))

    elif args.prometheus:
        print(collector.export_prometheus())

    elif args.snapshot:
        collector.save_snapshot()
        print("Snapshot saved")

    elif args.test:
        print("Recording test metrics...")
        collector.record_email_sent('gmail', True, 0.5)
        collector.record_email_sent('gmail', True, 0.8)
        collector.record_email_sent('gmail', False, 2.0)
        collector.record_workflow('outreach', True, 120)
        collector.record_ticket('created', 'P2')
        collector.record_platform_action('linkedin', 'connect', True)
        collector.active_workflows.set(5)
        collector.queue_depth.set(10, {'type': 'email'})

        print("\nSummary after test:")
        print(json.dumps(collector.get_summary(), indent=2))

    else:
        parser.print_help()
