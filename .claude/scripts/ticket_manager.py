#!/usr/bin/env python3
"""
Ticket Manager for 10x-Outreach-Skill
Full ticket lifecycle management for IT Operations Support

Features:
- Create tickets from emails
- Status workflow: new -> open -> in_progress -> resolved -> closed
- Priority levels: P1 (1hr), P2 (4hr), P3 (8hr), P4 (24hr)
- Assignment and routing
- Comment tracking (internal/external)
- Email-to-ticket linking via email_id index

Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, asdict, field

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


class TicketStatus(str, Enum):
    """Ticket status workflow states."""
    NEW = 'new'              # Just created
    OPEN = 'open'            # Acknowledged, awaiting action
    IN_PROGRESS = 'in_progress'  # Being worked on
    PENDING = 'pending'      # Waiting for external input
    RESOLVED = 'resolved'    # Solution provided
    CLOSED = 'closed'        # Confirmed complete


class TicketPriority(str, Enum):
    """Ticket priority levels with SLA implications."""
    P1 = 'P1'  # Critical - 1hr response, 4hr resolution
    P2 = 'P2'  # High - 4hr response, 8hr resolution
    P3 = 'P3'  # Medium - 8hr response, 2 day resolution
    P4 = 'P4'  # Low - 24hr response, 7 day resolution


class TicketType(str, Enum):
    """Ticket type categories."""
    INCIDENT = 'incident'    # Something is broken
    REQUEST = 'request'      # Service request
    CHANGE = 'change'        # Change request
    PROBLEM = 'problem'      # Recurring issue investigation


@dataclass
class TicketComment:
    """Ticket comment/update."""
    id: str
    ticket_id: str
    author: str
    content: str
    is_internal: bool  # Internal note vs external/customer-visible
    created_at: str

    @classmethod
    def create(cls, ticket_id: str, author: str, content: str, is_internal: bool = False):
        return cls(
            id=str(uuid.uuid4())[:8],
            ticket_id=ticket_id,
            author=author,
            content=content,
            is_internal=is_internal,
            created_at=datetime.utcnow().isoformat() + 'Z'
        )


@dataclass
class TicketSLAInfo:
    """SLA tracking information."""
    response_due: Optional[str] = None     # When first response is due
    resolution_due: Optional[str] = None   # When resolution is due
    responded_at: Optional[str] = None     # When first response was made
    resolved_at: Optional[str] = None      # When marked resolved
    response_breached: bool = False
    resolution_breached: bool = False
    paused_at: Optional[str] = None        # When SLA was paused (pending state)
    pause_duration_minutes: int = 0        # Total pause time


@dataclass
class Ticket:
    """Full ticket data structure."""
    id: str
    title: str
    description: str
    status: str
    priority: str
    ticket_type: str
    requester_email: str
    requester_name: str
    assigned_to: Optional[str]
    created_at: str
    updated_at: str
    email_id: Optional[str]          # Original email message ID
    thread_id: Optional[str]         # Gmail thread ID
    comments: List[Dict] = field(default_factory=list)
    sla: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    @classmethod
    def from_email(
        cls,
        email_data: Dict,
        priority: str = 'P3',
        ticket_type: str = 'incident',
        ai_analysis: Optional[Dict] = None
    ):
        """Create ticket from email data."""
        # Use AI analysis if available
        if ai_analysis:
            priority = ai_analysis.get('priority', priority)
            if ai_analysis.get('intent') in ['incident', 'request', 'change', 'problem']:
                ticket_type = ai_analysis['intent']

        ticket_id = f"TKT-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

        # Extract requester info
        from_field = email_data.get('from', '')
        if '<' in from_field:
            requester_name = from_field.split('<')[0].strip().strip('"')
            requester_email = from_field.split('<')[1].rstrip('>')
        else:
            requester_email = from_field
            requester_name = from_field.split('@')[0] if '@' in from_field else from_field

        now = datetime.utcnow().isoformat() + 'Z'

        return cls(
            id=ticket_id,
            title=email_data.get('subject', 'No Subject'),
            description=email_data.get('body', email_data.get('snippet', '')),
            status=TicketStatus.NEW.value,
            priority=priority,
            ticket_type=ticket_type,
            requester_email=requester_email,
            requester_name=requester_name,
            assigned_to=None,
            created_at=now,
            updated_at=now,
            email_id=email_data.get('id'),
            thread_id=email_data.get('thread_id'),
            comments=[],
            sla={},
            tags=ai_analysis.get('entities', {}).get('systems', []) if ai_analysis else [],
            metadata={
                'ai_analysis': ai_analysis
            } if ai_analysis else {}
        )


class TicketManager:
    """
    Ticket lifecycle manager.

    Handles:
    - Ticket creation from emails
    - Status transitions
    - Assignment
    - Comments and history
    - SLA tracking
    """

    # SLA definitions (in hours)
    SLA_RESPONSE = {
        'P1': 1,
        'P2': 4,
        'P3': 8,
        'P4': 24
    }

    SLA_RESOLUTION = {
        'P1': 4,
        'P2': 8,
        'P3': 48,   # 2 days
        'P4': 168   # 7 days
    }

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize ticket manager."""
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.tickets_dir = self.base_dir / 'tickets'
        self.active_dir = self.tickets_dir / 'active'
        self.closed_dir = self.tickets_dir / 'closed'

        # Create directories
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.closed_dir.mkdir(parents=True, exist_ok=True)

        # Email ID to ticket ID index
        self._email_index_path = self.tickets_dir / 'email_index.json'
        self._email_index = self._load_email_index()

    def _load_email_index(self) -> Dict[str, str]:
        """Load email-to-ticket index."""
        if self._email_index_path.exists():
            try:
                with open(self._email_index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_email_index(self):
        """Save email-to-ticket index."""
        with open(self._email_index_path, 'w', encoding='utf-8') as f:
            json.dump(self._email_index, f, indent=2)

    def _get_ticket_path(self, ticket_id: str) -> Optional[Path]:
        """Get path to ticket file."""
        active_path = self.active_dir / f"{ticket_id}.json"
        if active_path.exists():
            return active_path

        closed_path = self.closed_dir / f"{ticket_id}.json"
        if closed_path.exists():
            return closed_path

        return None

    def _save_ticket(self, ticket: Ticket):
        """Save ticket to file."""
        ticket_dict = asdict(ticket) if hasattr(ticket, '__dataclass_fields__') else ticket.__dict__

        # Determine directory based on status
        if ticket.status == TicketStatus.CLOSED.value:
            file_path = self.closed_dir / f"{ticket.id}.json"
            # Move from active if exists
            active_path = self.active_dir / f"{ticket.id}.json"
            if active_path.exists():
                active_path.unlink()
        else:
            file_path = self.active_dir / f"{ticket.id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(ticket_dict, f, indent=2, default=str)

        # Update email index
        if ticket.email_id:
            self._email_index[ticket.email_id] = ticket.id
            self._save_email_index()

    def _load_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Load ticket from file."""
        path = self._get_ticket_path(ticket_id)
        if not path:
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return Ticket(**data)
        except Exception as e:
            print(f"[!] Error loading ticket {ticket_id}: {e}")
            return None

    def create_ticket(
        self,
        title: str,
        description: str,
        requester_email: str,
        requester_name: str = '',
        priority: str = 'P3',
        ticket_type: str = 'incident',
        email_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        ai_analysis: Optional[Dict] = None
    ) -> Ticket:
        """
        Create a new ticket.

        Args:
            title: Ticket title
            description: Ticket description
            requester_email: Requester's email
            requester_name: Requester's name
            priority: Priority level (P1-P4)
            ticket_type: Type (incident, request, change, problem)
            email_id: Original email ID if from email
            thread_id: Gmail thread ID
            ai_analysis: AI analysis results

        Returns:
            Created Ticket object
        """
        ticket_id = f"TKT-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        now = datetime.utcnow().isoformat() + 'Z'

        # Calculate SLA due dates
        response_hours = self.SLA_RESPONSE.get(priority, 8)
        resolution_hours = self.SLA_RESOLUTION.get(priority, 48)

        response_due = (datetime.utcnow() + timedelta(hours=response_hours)).isoformat() + 'Z'
        resolution_due = (datetime.utcnow() + timedelta(hours=resolution_hours)).isoformat() + 'Z'

        ticket = Ticket(
            id=ticket_id,
            title=title,
            description=description,
            status=TicketStatus.NEW.value,
            priority=priority,
            ticket_type=ticket_type,
            requester_email=requester_email,
            requester_name=requester_name or requester_email.split('@')[0],
            assigned_to=None,
            created_at=now,
            updated_at=now,
            email_id=email_id,
            thread_id=thread_id,
            comments=[],
            sla={
                'response_due': response_due,
                'resolution_due': resolution_due
            },
            tags=ai_analysis.get('entities', {}).get('systems', []) if ai_analysis else [],
            metadata={'ai_analysis': ai_analysis} if ai_analysis else {}
        )

        self._save_ticket(ticket)

        # Audit log
        if AUDIT_AVAILABLE:
            audit_log(
                EventType.WORKFLOW,
                'ticket_created',
                {
                    'ticket_id': ticket_id,
                    'priority': priority,
                    'type': ticket_type,
                    'email_id': email_id
                }
            )

        return ticket

    def create_from_email(
        self,
        email_data: Dict,
        ai_analysis: Optional[Dict] = None
    ) -> Ticket:
        """
        Create ticket from email data.

        Args:
            email_data: Email dict from inbox_reader
            ai_analysis: AI analysis results

        Returns:
            Created Ticket object
        """
        # Check if ticket already exists for this email
        existing_id = self._email_index.get(email_data.get('id'))
        if existing_id:
            existing = self._load_ticket(existing_id)
            if existing:
                return existing

        ticket = Ticket.from_email(email_data, ai_analysis=ai_analysis)

        # Calculate SLA
        response_hours = self.SLA_RESPONSE.get(ticket.priority, 8)
        resolution_hours = self.SLA_RESOLUTION.get(ticket.priority, 48)

        ticket.sla = {
            'response_due': (datetime.utcnow() + timedelta(hours=response_hours)).isoformat() + 'Z',
            'resolution_due': (datetime.utcnow() + timedelta(hours=resolution_hours)).isoformat() + 'Z'
        }

        self._save_ticket(ticket)

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.WORKFLOW,
                'ticket_created_from_email',
                {
                    'ticket_id': ticket.id,
                    'email_id': email_data.get('id'),
                    'priority': ticket.priority
                }
            )

        return ticket

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ID."""
        return self._load_ticket(ticket_id)

    def get_ticket_by_email(self, email_id: str) -> Optional[Ticket]:
        """Get ticket by email ID."""
        ticket_id = self._email_index.get(email_id)
        if ticket_id:
            return self._load_ticket(ticket_id)
        return None

    def update_status(
        self,
        ticket_id: str,
        new_status: str,
        comment: Optional[str] = None,
        user: str = 'system'
    ) -> Optional[Ticket]:
        """
        Update ticket status.

        Args:
            ticket_id: Ticket ID
            new_status: New status value
            comment: Optional comment
            user: User making the change

        Returns:
            Updated Ticket or None
        """
        ticket = self._load_ticket(ticket_id)
        if not ticket:
            return None

        old_status = ticket.status
        ticket.status = new_status
        ticket.updated_at = datetime.utcnow().isoformat() + 'Z'

        # Handle SLA tracking
        now = datetime.utcnow().isoformat() + 'Z'

        if new_status == TicketStatus.OPEN.value and old_status == TicketStatus.NEW.value:
            # First response
            ticket.sla['responded_at'] = now

        elif new_status == TicketStatus.PENDING.value:
            # Pause SLA
            ticket.sla['paused_at'] = now

        elif old_status == TicketStatus.PENDING.value and new_status != TicketStatus.PENDING.value:
            # Resume SLA - calculate pause duration
            if ticket.sla.get('paused_at'):
                paused_at = datetime.fromisoformat(ticket.sla['paused_at'].replace('Z', '+00:00'))
                pause_duration = (datetime.utcnow().replace(tzinfo=paused_at.tzinfo) - paused_at).total_seconds() / 60
                ticket.sla['pause_duration_minutes'] = ticket.sla.get('pause_duration_minutes', 0) + int(pause_duration)
                ticket.sla['paused_at'] = None

        elif new_status == TicketStatus.RESOLVED.value:
            ticket.sla['resolved_at'] = now

        # Add status change comment
        if comment:
            ticket.comments.append(asdict(TicketComment.create(
                ticket_id=ticket_id,
                author=user,
                content=f"Status: {old_status} -> {new_status}\n{comment}",
                is_internal=False
            )))
        else:
            ticket.comments.append(asdict(TicketComment.create(
                ticket_id=ticket_id,
                author=user,
                content=f"Status changed: {old_status} -> {new_status}",
                is_internal=True
            )))

        self._save_ticket(ticket)

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.WORKFLOW,
                'ticket_status_changed',
                {
                    'ticket_id': ticket_id,
                    'old_status': old_status,
                    'new_status': new_status,
                    'user': user
                }
            )

        return ticket

    def assign_ticket(
        self,
        ticket_id: str,
        assignee: str,
        user: str = 'system'
    ) -> Optional[Ticket]:
        """Assign ticket to a user."""
        ticket = self._load_ticket(ticket_id)
        if not ticket:
            return None

        old_assignee = ticket.assigned_to
        ticket.assigned_to = assignee
        ticket.updated_at = datetime.utcnow().isoformat() + 'Z'

        # Auto-transition to open if new
        if ticket.status == TicketStatus.NEW.value:
            ticket.status = TicketStatus.OPEN.value
            ticket.sla['responded_at'] = ticket.updated_at

        ticket.comments.append(asdict(TicketComment.create(
            ticket_id=ticket_id,
            author=user,
            content=f"Assigned to {assignee}" + (f" (from {old_assignee})" if old_assignee else ""),
            is_internal=True
        )))

        self._save_ticket(ticket)

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.WORKFLOW,
                'ticket_assigned',
                {'ticket_id': ticket_id, 'assignee': assignee}
            )

        return ticket

    def add_comment(
        self,
        ticket_id: str,
        content: str,
        author: str,
        is_internal: bool = False
    ) -> Optional[Ticket]:
        """Add comment to ticket."""
        ticket = self._load_ticket(ticket_id)
        if not ticket:
            return None

        ticket.comments.append(asdict(TicketComment.create(
            ticket_id=ticket_id,
            author=author,
            content=content,
            is_internal=is_internal
        )))
        ticket.updated_at = datetime.utcnow().isoformat() + 'Z'

        self._save_ticket(ticket)
        return ticket

    def list_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        include_closed: bool = False
    ) -> List[Dict]:
        """
        List tickets with optional filters.

        Returns:
            List of ticket summary dicts
        """
        tickets = []

        # List active tickets
        for path in self.active_dir.glob('*.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)

                # Apply filters
                if status and ticket.get('status') != status:
                    continue
                if priority and ticket.get('priority') != priority:
                    continue
                if assigned_to and ticket.get('assigned_to') != assigned_to:
                    continue

                tickets.append({
                    'id': ticket['id'],
                    'title': ticket['title'][:50],
                    'status': ticket['status'],
                    'priority': ticket['priority'],
                    'assigned_to': ticket.get('assigned_to'),
                    'created_at': ticket['created_at'],
                    'requester': ticket.get('requester_name', ticket.get('requester_email'))
                })
            except Exception:
                continue

        # Include closed if requested
        if include_closed:
            for path in self.closed_dir.glob('*.json'):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        ticket = json.load(f)

                    if status and ticket.get('status') != status:
                        continue

                    tickets.append({
                        'id': ticket['id'],
                        'title': ticket['title'][:50],
                        'status': ticket['status'],
                        'priority': ticket['priority'],
                        'assigned_to': ticket.get('assigned_to'),
                        'created_at': ticket['created_at'],
                        'requester': ticket.get('requester_name')
                    })
                except Exception:
                    continue

        # Sort by priority then date
        priority_order = {'P1': 0, 'P2': 1, 'P3': 2, 'P4': 3}
        tickets.sort(key=lambda t: (priority_order.get(t['priority'], 9), t['created_at']))

        return tickets

    def get_stats(self) -> Dict[str, Any]:
        """Get ticket statistics."""
        stats = {
            'total_active': 0,
            'total_closed': 0,
            'by_status': {},
            'by_priority': {},
            'sla_at_risk': 0,
            'unassigned': 0
        }

        now = datetime.utcnow()

        for path in self.active_dir.glob('*.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)

                stats['total_active'] += 1

                # Count by status
                status = ticket.get('status', 'unknown')
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

                # Count by priority
                priority = ticket.get('priority', 'unknown')
                stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1

                # Check unassigned
                if not ticket.get('assigned_to'):
                    stats['unassigned'] += 1

                # Check SLA at risk
                sla = ticket.get('sla', {})
                resolution_due = sla.get('resolution_due')
                if resolution_due:
                    due_time = datetime.fromisoformat(resolution_due.replace('Z', '+00:00'))
                    if now.replace(tzinfo=due_time.tzinfo) > due_time - timedelta(hours=2):
                        stats['sla_at_risk'] += 1

            except Exception:
                continue

        stats['total_closed'] = len(list(self.closed_dir.glob('*.json')))

        return stats


# Factory function
def get_ticket_manager(base_dir: Optional[Path] = None) -> TicketManager:
    """Get ticket manager instance."""
    return TicketManager(base_dir)


# CLI
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Ticket Manager CLI')
    parser.add_argument('--list', action='store_true', help='List active tickets')
    parser.add_argument('--stats', action='store_true', help='Show ticket statistics')
    parser.add_argument('--get', metavar='ID', help='Get ticket by ID')
    parser.add_argument('--create', action='store_true', help='Create test ticket')

    args = parser.parse_args()

    manager = TicketManager()

    if args.list:
        tickets = manager.list_tickets()
        print(f"\nActive Tickets ({len(tickets)}):\n")
        for t in tickets:
            print(f"  [{t['priority']}] {t['id']}: {t['title']}")
            print(f"       Status: {t['status']}, Assigned: {t['assigned_to'] or 'Unassigned'}")

    elif args.stats:
        stats = manager.get_stats()
        print(f"\nTicket Statistics:")
        print(f"  Active: {stats['total_active']}")
        print(f"  Closed: {stats['total_closed']}")
        print(f"  Unassigned: {stats['unassigned']}")
        print(f"  SLA at risk: {stats['sla_at_risk']}")
        print(f"\n  By Priority: {stats['by_priority']}")
        print(f"  By Status: {stats['by_status']}")

    elif args.get:
        ticket = manager.get_ticket(args.get)
        if ticket:
            print(json.dumps(asdict(ticket), indent=2, default=str))
        else:
            print(f"Ticket not found: {args.get}")

    elif args.create:
        ticket = manager.create_ticket(
            title="Test Ticket - Printer Issue",
            description="The printer on floor 3 is not working.",
            requester_email="test@example.com",
            requester_name="Test User",
            priority="P3",
            ticket_type="incident"
        )
        print(f"Created ticket: {ticket.id}")

    else:
        parser.print_help()
