#!/usr/bin/env python3
"""
Tamper-Proof Audit Logger for 10x-Outreach-Skill
Hash-chained logging with HMAC-SHA256 entry signing

Features:
- HMAC-SHA256 entry signing
- Hash chain linking (blockchain-like integrity)
- JSONL format for easy querying
- Auto-rotation (10k entries per file)
- Event types: auth, data, workflow, security, platform
"""

import os
import sys
import json
import hmac
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[X] Missing dependency: {e}")
    sys.exit(1)

load_dotenv(Path(__file__).parent.parent / '.env')


class EventType(str, Enum):
    """Audit event types."""
    AUTH = 'auth'                # Authentication events
    DATA = 'data'                # Data access/modification
    WORKFLOW = 'workflow'        # Workflow execution
    SECURITY = 'security'        # Security events
    PLATFORM = 'platform'        # Platform actions (email, social)
    SYSTEM = 'system'            # System events
    CREDENTIAL = 'credential'    # Credential access


class EventSeverity(str, Enum):
    """Event severity levels."""
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


class TamperProofAuditLogger:
    """
    Tamper-proof audit logger with hash chain integrity.

    Security features:
    - HMAC-SHA256 signed entries
    - Hash chain linking each entry to previous
    - Auto-rotation to prevent single file corruption
    - Integrity verification on demand

    Usage:
        logger = TamperProofAuditLogger()
        logger.log(EventType.AUTH, 'user_login', {'user': 'john@example.com'})
    """

    # Maximum entries per log file before rotation
    MAX_ENTRIES_PER_FILE = 10000

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize audit logger.

        Args:
            base_dir: Base directory for log storage
        """
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.logs_dir = self.base_dir / 'audit_logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Get signing key
        self._signing_key = self._get_or_create_signing_key()

        # Current log file
        self._current_file: Optional[Path] = None
        self._entry_count = 0
        self._last_hash: Optional[str] = None

        # Initialize current log file
        self._init_current_file()

    def _get_or_create_signing_key(self) -> bytes:
        """Get HMAC signing key from environment or create new one."""
        key_env = os.getenv('AUDIT_SIGNING_KEY')

        if key_env:
            return key_env.encode('utf-8')

        # Check for key file
        key_file = self.logs_dir / '.signing_key'
        if key_file.exists():
            return key_file.read_bytes()

        # Generate new key
        import secrets
        new_key = secrets.token_bytes(32)
        key_file.write_bytes(new_key)

        # Set restrictive permissions
        try:
            os.chmod(key_file, 0o600)
        except Exception:
            pass

        print(f"[!] Generated new audit signing key. Set AUDIT_SIGNING_KEY in .env for persistence.")

        return new_key

    def _get_current_filename(self) -> str:
        """Generate filename for current log file."""
        today = datetime.utcnow().strftime('%Y%m%d')
        return f'audit_{today}.jsonl'

    def _init_current_file(self):
        """Initialize or recover current log file."""
        filename = self._get_current_filename()
        self._current_file = self.logs_dir / filename

        if self._current_file.exists():
            # Count existing entries and get last hash
            self._entry_count = 0
            self._last_hash = '0' * 64  # Genesis hash

            with open(self._current_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            self._entry_count += 1
                            self._last_hash = entry.get('hash', self._last_hash)
                        except json.JSONDecodeError:
                            pass
        else:
            self._entry_count = 0
            self._last_hash = '0' * 64  # Genesis hash

    def _compute_entry_hash(self, entry: Dict) -> str:
        """Compute SHA-256 hash of entry content."""
        # Create canonical JSON string (sorted keys)
        content = json.dumps({
            'timestamp': entry['timestamp'],
            'type': entry['type'],
            'action': entry['action'],
            'data': entry.get('data', {}),
            'prev_hash': entry['prev_hash']
        }, sort_keys=True)

        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _compute_hmac(self, data: str) -> str:
        """Compute HMAC-SHA256 signature."""
        return hmac.new(
            self._signing_key,
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _rotate_if_needed(self):
        """Rotate log file if max entries reached."""
        if self._entry_count >= self.MAX_ENTRIES_PER_FILE:
            # Finalize current file
            self._finalize_file()

            # Start new file
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            self._current_file = self.logs_dir / f'audit_{timestamp}.jsonl'
            self._entry_count = 0
            # Keep last hash for chain continuity

    def _finalize_file(self):
        """Finalize current log file with summary."""
        if not self._current_file or not self._current_file.exists():
            return

        # Write finalization entry
        final_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': 'system',
            'action': 'log_finalized',
            'data': {
                'entry_count': self._entry_count,
                'final_hash': self._last_hash
            },
            'prev_hash': self._last_hash
        }

        final_entry['hash'] = self._compute_entry_hash(final_entry)
        final_entry['signature'] = self._compute_hmac(final_entry['hash'])

        with open(self._current_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(final_entry) + '\n')

    def log(
        self,
        event_type: EventType,
        action: str,
        data: Optional[Dict[str, Any]] = None,
        severity: EventSeverity = EventSeverity.INFO,
        user: Optional[str] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Log an audit event.

        Args:
            event_type: Type of event (auth, data, workflow, etc.)
            action: Action being performed
            data: Additional event data
            severity: Event severity level
            user: User performing action (if applicable)
            source: Source of the event (module/function)

        Returns:
            Entry hash for verification
        """
        self._rotate_if_needed()

        # Ensure we're using today's file
        expected_filename = self._get_current_filename()
        if self._current_file.name != expected_filename:
            self._finalize_file()
            self._current_file = self.logs_dir / expected_filename
            if not self._current_file.exists():
                self._entry_count = 0
                # Keep chain continuity with last hash

        # Build entry
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': event_type.value if isinstance(event_type, EventType) else event_type,
            'action': action,
            'severity': severity.value if isinstance(severity, EventSeverity) else severity,
            'data': data or {},
            'prev_hash': self._last_hash
        }

        if user:
            entry['user'] = user
        if source:
            entry['source'] = source

        # Compute hash
        entry['hash'] = self._compute_entry_hash(entry)

        # Compute HMAC signature
        entry['signature'] = self._compute_hmac(entry['hash'])

        # Write to file
        with open(self._current_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

        # Update state
        self._last_hash = entry['hash']
        self._entry_count += 1

        return entry['hash']

    def verify_integrity(self, log_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Verify integrity of a log file.

        Args:
            log_file: Path to log file (default: current file)

        Returns:
            Dict with verification results
        """
        log_file = log_file or self._current_file

        if not log_file or not log_file.exists():
            return {
                'valid': False,
                'error': 'Log file not found',
                'file': str(log_file)
            }

        results = {
            'valid': True,
            'file': str(log_file),
            'entries_checked': 0,
            'chain_valid': True,
            'signatures_valid': True,
            'errors': []
        }

        prev_hash = '0' * 64  # Genesis hash

        with open(log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                try:
                    entry = json.loads(line)
                    results['entries_checked'] += 1

                    # Verify chain
                    if entry.get('prev_hash') != prev_hash:
                        results['chain_valid'] = False
                        results['errors'].append(f"Line {line_num}: Chain broken")

                    # Verify hash
                    computed_hash = self._compute_entry_hash(entry)
                    if computed_hash != entry.get('hash'):
                        results['valid'] = False
                        results['errors'].append(f"Line {line_num}: Hash mismatch")

                    # Verify signature
                    expected_sig = self._compute_hmac(entry.get('hash', ''))
                    if expected_sig != entry.get('signature'):
                        results['signatures_valid'] = False
                        results['errors'].append(f"Line {line_num}: Invalid signature")

                    prev_hash = entry.get('hash', prev_hash)

                except json.JSONDecodeError:
                    results['errors'].append(f"Line {line_num}: Invalid JSON")

        results['valid'] = (
            results['chain_valid'] and
            results['signatures_valid'] and
            len(results['errors']) == 0
        )

        return results

    def query(
        self,
        event_type: Optional[EventType] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query audit log entries.

        Args:
            event_type: Filter by event type
            action: Filter by action (substring match)
            start_time: Filter entries after this time
            end_time: Filter entries before this time
            user: Filter by user
            limit: Maximum entries to return

        Returns:
            List of matching entries
        """
        results = []

        # Get all log files sorted by date
        log_files = sorted(self.logs_dir.glob('audit_*.jsonl'), reverse=True)

        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(results) >= limit:
                        break

                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line)

                        # Apply filters
                        if event_type and entry.get('type') != event_type.value:
                            continue
                        if action and action.lower() not in entry.get('action', '').lower():
                            continue
                        if user and entry.get('user') != user:
                            continue

                        if start_time or end_time:
                            try:
                                entry_time = datetime.fromisoformat(
                                    entry['timestamp'].replace('Z', '+00:00')
                                )
                                if start_time and entry_time < start_time:
                                    continue
                                if end_time and entry_time > end_time:
                                    continue
                            except:
                                continue

                        results.append(entry)

                    except json.JSONDecodeError:
                        continue

            if len(results) >= limit:
                break

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get audit log statistics."""
        stats = {
            'total_entries': 0,
            'total_files': 0,
            'by_type': {},
            'by_severity': {},
            'oldest_entry': None,
            'newest_entry': None
        }

        log_files = list(self.logs_dir.glob('audit_*.jsonl'))
        stats['total_files'] = len(log_files)

        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line)
                        stats['total_entries'] += 1

                        # Count by type
                        entry_type = entry.get('type', 'unknown')
                        stats['by_type'][entry_type] = stats['by_type'].get(entry_type, 0) + 1

                        # Count by severity
                        severity = entry.get('severity', 'info')
                        stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1

                        # Track time range
                        timestamp = entry.get('timestamp')
                        if timestamp:
                            if not stats['oldest_entry'] or timestamp < stats['oldest_entry']:
                                stats['oldest_entry'] = timestamp
                            if not stats['newest_entry'] or timestamp > stats['newest_entry']:
                                stats['newest_entry'] = timestamp

                    except json.JSONDecodeError:
                        continue

        return stats


# Convenience function for global logger instance
_global_logger: Optional[TamperProofAuditLogger] = None


def get_audit_logger(base_dir: Optional[Path] = None) -> TamperProofAuditLogger:
    """Get or create global audit logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = TamperProofAuditLogger(base_dir)
    return _global_logger


def audit_log(
    event_type: EventType,
    action: str,
    data: Optional[Dict] = None,
    severity: EventSeverity = EventSeverity.INFO,
    user: Optional[str] = None,
    source: Optional[str] = None
) -> str:
    """
    Convenience function to log audit event.

    Usage:
        from audit_logger import audit_log, EventType
        audit_log(EventType.AUTH, 'user_login', {'email': 'user@example.com'})
    """
    logger = get_audit_logger()
    return logger.log(event_type, action, data, severity, user, source)


# CLI for testing
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Audit Logger CLI')
    parser.add_argument('--test', action='store_true', help='Write test entries')
    parser.add_argument('--verify', action='store_true', help='Verify current log integrity')
    parser.add_argument('--stats', action='store_true', help='Show log statistics')
    parser.add_argument('--query', metavar='TYPE', help='Query by event type')

    args = parser.parse_args()

    logger = TamperProofAuditLogger()

    if args.test:
        print("Writing test audit entries...")

        logger.log(EventType.AUTH, 'user_login', {'email': 'test@example.com'})
        logger.log(EventType.WORKFLOW, 'workflow_started', {'workflow_id': 'test-123'})
        logger.log(EventType.PLATFORM, 'email_sent', {'to': 'recipient@example.com'})
        logger.log(EventType.SECURITY, 'permission_denied', {'resource': '/admin'}, EventSeverity.WARNING)

        print("[OK] Test entries written")

    elif args.verify:
        print("Verifying log integrity...")
        result = logger.verify_integrity()

        if result['valid']:
            print(f"[OK] Log verified: {result['entries_checked']} entries")
        else:
            print(f"[X] Verification failed!")
            for error in result['errors'][:10]:
                print(f"    {error}")

    elif args.stats:
        stats = logger.get_stats()
        print(f"\nAudit Log Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Total files: {stats['total_files']}")
        print(f"\n  By type:")
        for t, count in stats['by_type'].items():
            print(f"    {t}: {count}")
        print(f"\n  By severity:")
        for s, count in stats['by_severity'].items():
            print(f"    {s}: {count}")

    elif args.query:
        try:
            event_type = EventType(args.query)
            entries = logger.query(event_type=event_type, limit=10)
            print(f"\nRecent {args.query} events ({len(entries)}):")
            for entry in entries[:10]:
                print(f"  [{entry['timestamp'][:19]}] {entry['action']}")
        except ValueError:
            print(f"[X] Invalid event type: {args.query}")
            print(f"    Valid types: {[e.value for e in EventType]}")

    else:
        parser.print_help()
