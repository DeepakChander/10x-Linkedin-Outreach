#!/usr/bin/env python3
"""
SLA Tracker for 10x-Outreach-Skill
SLA monitoring and escalation for IT Operations Support

Features:
- Real-time SLA status checking
- Automatic escalation rules
- Breach recording and notifications
- SLA pause/resume for pending states
- Compliance reporting (met/breached/pending)

Default SLAs:
| Priority | Response | Resolution |
|----------|----------|------------|
| P1       | 1 hour   | 4 hours    |
| P2       | 4 hours  | 8 hours    |
| P3       | 8 hours  | 2 days     |
| P4       | 24 hours | 7 days     |

Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[X] Missing dependency: {e}")
    sys.exit(1)

# Import audit logger
try:
    from audit_logger import audit_log, EventType, EventSeverity
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False

load_dotenv(Path(__file__).parent.parent / '.env')


class SLAStatus(str, Enum):
    """SLA status states."""
    ON_TRACK = 'on_track'        # Within SLA
    AT_RISK = 'at_risk'          # <25% time remaining
    BREACHED = 'breached'        # SLA exceeded
    PAUSED = 'paused'            # Waiting on customer
    MET = 'met'                  # Completed within SLA


class EscalationLevel(str, Enum):
    """Escalation levels."""
    NONE = 'none'
    L1 = 'L1'        # Team lead notification
    L2 = 'L2'        # Manager notification
    L3 = 'L3'        # Director/executive notification


@dataclass
class SLADefinition:
    """SLA definition for a priority level."""
    priority: str
    response_hours: float
    resolution_hours: float
    escalation_thresholds: Dict[str, float]  # Percentage of time remaining


# Default SLA definitions
DEFAULT_SLAS = {
    'P1': SLADefinition(
        priority='P1',
        response_hours=1,
        resolution_hours=4,
        escalation_thresholds={'L1': 0.5, 'L2': 0.25, 'L3': 0}  # 50%, 25%, 0%
    ),
    'P2': SLADefinition(
        priority='P2',
        response_hours=4,
        resolution_hours=8,
        escalation_thresholds={'L1': 0.5, 'L2': 0.25, 'L3': 0}
    ),
    'P3': SLADefinition(
        priority='P3',
        response_hours=8,
        resolution_hours=48,  # 2 days
        escalation_thresholds={'L1': 0.25, 'L2': 0.1, 'L3': 0}
    ),
    'P4': SLADefinition(
        priority='P4',
        response_hours=24,
        resolution_hours=168,  # 7 days
        escalation_thresholds={'L1': 0.25, 'L2': 0.1, 'L3': 0}
    )
}


@dataclass
class SLAResult:
    """SLA check result."""
    ticket_id: str
    priority: str
    response_status: str
    resolution_status: str
    response_remaining_minutes: int
    resolution_remaining_minutes: int
    response_percentage_remaining: float
    resolution_percentage_remaining: float
    escalation_level: str
    is_paused: bool
    checked_at: str


class SLATracker:
    """
    SLA tracking and escalation manager.

    Monitors ticket SLAs and triggers escalations based on
    configurable thresholds.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize SLA tracker."""
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.sla_dir = self.base_dir / 'sla'
        self.sla_dir.mkdir(parents=True, exist_ok=True)

        # Load custom SLA definitions if available
        self.sla_defs = self._load_sla_definitions()

        # Escalation history
        self._escalation_log_path = self.sla_dir / 'escalations.jsonl'

        # Breach log
        self._breach_log_path = self.sla_dir / 'breaches.jsonl'

    def _load_sla_definitions(self) -> Dict[str, SLADefinition]:
        """Load SLA definitions from config or use defaults."""
        config_path = self.sla_dir / 'sla_config.json'

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                slas = {}
                for priority, def_dict in config.items():
                    slas[priority] = SLADefinition(**def_dict)
                return slas
            except Exception as e:
                print(f"[!] Error loading SLA config, using defaults: {e}")

        return DEFAULT_SLAS

    def save_sla_definitions(self, slas: Dict[str, SLADefinition]):
        """Save custom SLA definitions."""
        config_path = self.sla_dir / 'sla_config.json'

        config = {p: asdict(d) for p, d in slas.items()}

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        self.sla_defs = slas

    def check_sla(self, ticket: Dict) -> SLAResult:
        """
        Check SLA status for a ticket.

        Args:
            ticket: Ticket dict with sla field

        Returns:
            SLAResult with current status
        """
        now = datetime.now(timezone.utc)
        ticket_id = ticket.get('id', 'unknown')
        priority = ticket.get('priority', 'P3')
        sla_data = ticket.get('sla', {})
        status = ticket.get('status', 'new')

        # Get SLA definition
        sla_def = self.sla_defs.get(priority, DEFAULT_SLAS['P3'])

        # Check if paused (pending status)
        is_paused = status == 'pending'
        pause_minutes = sla_data.get('pause_duration_minutes', 0)

        # Calculate response SLA
        response_status = SLAStatus.ON_TRACK
        response_remaining = 0
        response_percentage = 1.0

        if sla_data.get('responded_at'):
            # Already responded
            response_status = SLAStatus.MET
            response_remaining = 0
            response_percentage = 1.0
        elif sla_data.get('response_due'):
            response_due = datetime.fromisoformat(
                sla_data['response_due'].replace('Z', '+00:00')
            )
            # Adjust for pause time
            response_due = response_due + timedelta(minutes=pause_minutes)

            if is_paused:
                response_status = SLAStatus.PAUSED
            elif now >= response_due:
                response_status = SLAStatus.BREACHED
                response_remaining = -int((now - response_due).total_seconds() / 60)
                response_percentage = 0
            else:
                remaining = (response_due - now).total_seconds() / 60
                total = sla_def.response_hours * 60
                response_remaining = int(remaining)
                response_percentage = remaining / total if total > 0 else 0

                if response_percentage <= 0.25:
                    response_status = SLAStatus.AT_RISK

        # Calculate resolution SLA
        resolution_status = SLAStatus.ON_TRACK
        resolution_remaining = 0
        resolution_percentage = 1.0

        if sla_data.get('resolved_at'):
            resolution_status = SLAStatus.MET
        elif ticket.get('status') == 'closed':
            resolution_status = SLAStatus.MET
        elif sla_data.get('resolution_due'):
            resolution_due = datetime.fromisoformat(
                sla_data['resolution_due'].replace('Z', '+00:00')
            )
            # Adjust for pause time
            resolution_due = resolution_due + timedelta(minutes=pause_minutes)

            if is_paused:
                resolution_status = SLAStatus.PAUSED
            elif now >= resolution_due:
                resolution_status = SLAStatus.BREACHED
                resolution_remaining = -int((now - resolution_due).total_seconds() / 60)
                resolution_percentage = 0
            else:
                remaining = (resolution_due - now).total_seconds() / 60
                total = sla_def.resolution_hours * 60
                resolution_remaining = int(remaining)
                resolution_percentage = remaining / total if total > 0 else 0

                if resolution_percentage <= 0.25:
                    resolution_status = SLAStatus.AT_RISK

        # Determine escalation level
        escalation_level = EscalationLevel.NONE

        # Use worst percentage for escalation
        worst_percentage = min(response_percentage, resolution_percentage)

        if not is_paused:
            thresholds = sla_def.escalation_thresholds
            if worst_percentage <= thresholds.get('L3', 0):
                escalation_level = EscalationLevel.L3
            elif worst_percentage <= thresholds.get('L2', 0.25):
                escalation_level = EscalationLevel.L2
            elif worst_percentage <= thresholds.get('L1', 0.5):
                escalation_level = EscalationLevel.L1

        return SLAResult(
            ticket_id=ticket_id,
            priority=priority,
            response_status=response_status.value,
            resolution_status=resolution_status.value,
            response_remaining_minutes=response_remaining,
            resolution_remaining_minutes=resolution_remaining,
            response_percentage_remaining=round(response_percentage, 2),
            resolution_percentage_remaining=round(resolution_percentage, 2),
            escalation_level=escalation_level.value,
            is_paused=is_paused,
            checked_at=now.isoformat()
        )

    def check_all_tickets(self, tickets_dir: Optional[Path] = None) -> List[SLAResult]:
        """
        Check SLA for all active tickets.

        Args:
            tickets_dir: Path to tickets directory

        Returns:
            List of SLAResult objects
        """
        tickets_dir = tickets_dir or self.base_dir / 'tickets' / 'active'
        results = []

        if not tickets_dir.exists():
            return results

        for path in tickets_dir.glob('*.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)

                result = self.check_sla(ticket)
                results.append(result)

            except Exception as e:
                print(f"[!] Error checking SLA for {path.name}: {e}")

        # Sort by urgency (breached first, then at_risk, then by remaining time)
        def sort_key(r):
            status_order = {'breached': 0, 'at_risk': 1, 'on_track': 2, 'paused': 3, 'met': 4}
            worst_status = min(
                status_order.get(r.response_status, 9),
                status_order.get(r.resolution_status, 9)
            )
            return (worst_status, r.resolution_remaining_minutes)

        results.sort(key=sort_key)

        return results

    def record_breach(
        self,
        ticket_id: str,
        breach_type: str,
        priority: str,
        details: Optional[Dict] = None
    ):
        """Record an SLA breach."""
        breach = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'ticket_id': ticket_id,
            'breach_type': breach_type,  # 'response' or 'resolution'
            'priority': priority,
            'details': details or {}
        }

        with open(self._breach_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(breach) + '\n')

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.WORKFLOW,
                'sla_breach',
                breach,
                EventSeverity.WARNING
            )

    def record_escalation(
        self,
        ticket_id: str,
        escalation_level: str,
        reason: str,
        notified: Optional[List[str]] = None
    ):
        """Record an escalation event."""
        escalation = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'ticket_id': ticket_id,
            'level': escalation_level,
            'reason': reason,
            'notified': notified or []
        }

        with open(self._escalation_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(escalation) + '\n')

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.WORKFLOW,
                'ticket_escalated',
                escalation,
                EventSeverity.WARNING
            )

    def get_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate SLA compliance report.

        Args:
            start_date: Report start date
            end_date: Report end date

        Returns:
            Compliance statistics
        """
        report = {
            'period': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None
            },
            'total_tickets': 0,
            'response_sla': {
                'met': 0,
                'breached': 0,
                'pending': 0,
                'compliance_rate': 0.0
            },
            'resolution_sla': {
                'met': 0,
                'breached': 0,
                'pending': 0,
                'compliance_rate': 0.0
            },
            'by_priority': {},
            'breaches': []
        }

        # Load breach log
        if self._breach_log_path.exists():
            with open(self._breach_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            breach = json.loads(line)
                            breach_time = datetime.fromisoformat(
                                breach['timestamp'].replace('Z', '+00:00')
                            )

                            # Check date filter
                            if start_date and breach_time < start_date.replace(tzinfo=timezone.utc):
                                continue
                            if end_date and breach_time > end_date.replace(tzinfo=timezone.utc):
                                continue

                            report['breaches'].append(breach)
                        except:
                            continue

        # Count breaches
        for breach in report['breaches']:
            priority = breach.get('priority', 'unknown')
            breach_type = breach.get('breach_type', 'unknown')

            if priority not in report['by_priority']:
                report['by_priority'][priority] = {
                    'response_breaches': 0,
                    'resolution_breaches': 0
                }

            if breach_type == 'response':
                report['response_sla']['breached'] += 1
                report['by_priority'][priority]['response_breaches'] += 1
            elif breach_type == 'resolution':
                report['resolution_sla']['breached'] += 1
                report['by_priority'][priority]['resolution_breaches'] += 1

        # Check closed tickets for compliance
        closed_dir = self.base_dir / 'tickets' / 'closed'
        if closed_dir.exists():
            for path in closed_dir.glob('*.json'):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        ticket = json.load(f)

                    created = datetime.fromisoformat(
                        ticket['created_at'].replace('Z', '+00:00')
                    )

                    # Date filter
                    if start_date and created < start_date.replace(tzinfo=timezone.utc):
                        continue
                    if end_date and created > end_date.replace(tzinfo=timezone.utc):
                        continue

                    report['total_tickets'] += 1
                    sla = ticket.get('sla', {})

                    # Response SLA
                    if sla.get('responded_at') and sla.get('response_due'):
                        responded = datetime.fromisoformat(sla['responded_at'].replace('Z', '+00:00'))
                        due = datetime.fromisoformat(sla['response_due'].replace('Z', '+00:00'))
                        if responded <= due:
                            report['response_sla']['met'] += 1
                        else:
                            report['response_sla']['breached'] += 1

                    # Resolution SLA
                    if sla.get('resolved_at') and sla.get('resolution_due'):
                        resolved = datetime.fromisoformat(sla['resolved_at'].replace('Z', '+00:00'))
                        due = datetime.fromisoformat(sla['resolution_due'].replace('Z', '+00:00'))
                        if resolved <= due:
                            report['resolution_sla']['met'] += 1
                        else:
                            report['resolution_sla']['breached'] += 1

                except:
                    continue

        # Calculate compliance rates
        response_total = report['response_sla']['met'] + report['response_sla']['breached']
        if response_total > 0:
            report['response_sla']['compliance_rate'] = round(
                report['response_sla']['met'] / response_total * 100, 1
            )

        resolution_total = report['resolution_sla']['met'] + report['resolution_sla']['breached']
        if resolution_total > 0:
            report['resolution_sla']['compliance_rate'] = round(
                report['resolution_sla']['met'] / resolution_total * 100, 1
            )

        return report

    def get_at_risk_tickets(self) -> List[SLAResult]:
        """Get tickets with breached or at-risk SLAs."""
        all_results = self.check_all_tickets()

        return [
            r for r in all_results
            if r.response_status in ['breached', 'at_risk']
            or r.resolution_status in ['breached', 'at_risk']
        ]


# Factory function
def get_sla_tracker(base_dir: Optional[Path] = None) -> SLATracker:
    """Get SLA tracker instance."""
    return SLATracker(base_dir)


# CLI
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='SLA Tracker CLI')
    parser.add_argument('--check', metavar='TICKET_ID', help='Check SLA for ticket')
    parser.add_argument('--check-all', action='store_true', help='Check all active tickets')
    parser.add_argument('--at-risk', action='store_true', help='Show at-risk tickets')
    parser.add_argument('--report', action='store_true', help='Generate compliance report')

    args = parser.parse_args()

    tracker = SLATracker()

    if args.check:
        tickets_dir = tracker.base_dir / 'tickets' / 'active'
        ticket_path = tickets_dir / f"{args.check}.json"

        if ticket_path.exists():
            with open(ticket_path, 'r', encoding='utf-8') as f:
                ticket = json.load(f)

            result = tracker.check_sla(ticket)
            print(f"\nSLA Status for {args.check}:")
            print(f"  Priority: {result.priority}")
            print(f"  Response: {result.response_status} ({result.response_remaining_minutes} min remaining)")
            print(f"  Resolution: {result.resolution_status} ({result.resolution_remaining_minutes} min remaining)")
            print(f"  Escalation: {result.escalation_level}")
            print(f"  Paused: {result.is_paused}")
        else:
            print(f"Ticket not found: {args.check}")

    elif args.check_all:
        results = tracker.check_all_tickets()
        print(f"\nSLA Status for {len(results)} tickets:\n")

        for r in results:
            status_icon = '🔴' if 'breached' in (r.response_status, r.resolution_status) else \
                          '🟡' if 'at_risk' in (r.response_status, r.resolution_status) else \
                          '⏸️' if r.is_paused else '🟢'

            print(f"  {status_icon} [{r.priority}] {r.ticket_id}")
            print(f"      Response: {r.response_status} | Resolution: {r.resolution_status}")
            print(f"      Remaining: {r.resolution_remaining_minutes} min | Escalation: {r.escalation_level}")

    elif args.at_risk:
        results = tracker.get_at_risk_tickets()
        print(f"\nAt-Risk Tickets ({len(results)}):\n")

        for r in results:
            print(f"  🔴 [{r.priority}] {r.ticket_id}")
            print(f"      Response: {r.response_status}")
            print(f"      Resolution: {r.resolution_status}")
            print(f"      Time remaining: {r.resolution_remaining_minutes} minutes")

    elif args.report:
        report = tracker.get_compliance_report()
        print(f"\nSLA Compliance Report:")
        print(f"\n  Response SLA:")
        print(f"    Met: {report['response_sla']['met']}")
        print(f"    Breached: {report['response_sla']['breached']}")
        print(f"    Compliance: {report['response_sla']['compliance_rate']}%")
        print(f"\n  Resolution SLA:")
        print(f"    Met: {report['resolution_sla']['met']}")
        print(f"    Breached: {report['resolution_sla']['breached']}")
        print(f"    Compliance: {report['resolution_sla']['compliance_rate']}%")

    else:
        parser.print_help()
