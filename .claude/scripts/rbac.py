#!/usr/bin/env python3
"""
Role-Based Access Control (RBAC) for 10x-Outreach-Skill
User authentication and permission management

Roles:
- Admin: All permissions
- Agent: Create/execute workflows, use platforms, view analytics
- Viewer: Read-only access

Features:
- Password hashing (PBKDF2-SHA256)
- Custom permission grants/revokes
- Tenant-scoped permissions
- Permission checking API

Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import sys
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Set
from dataclasses import dataclass, asdict, field
from enum import Enum

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


class Permission(str, Enum):
    """Available permissions."""
    # Workflow permissions
    WORKFLOW_CREATE = 'workflow.create'
    WORKFLOW_EXECUTE = 'workflow.execute'
    WORKFLOW_DELETE = 'workflow.delete'
    WORKFLOW_VIEW = 'workflow.view'

    # Email permissions
    EMAIL_SEND = 'email.send'
    EMAIL_READ = 'email.read'
    EMAIL_REPLY = 'email.reply'

    # Ticket permissions
    TICKET_CREATE = 'ticket.create'
    TICKET_UPDATE = 'ticket.update'
    TICKET_ASSIGN = 'ticket.assign'
    TICKET_CLOSE = 'ticket.close'
    TICKET_VIEW = 'ticket.view'

    # Platform permissions
    PLATFORM_LINKEDIN = 'platform.linkedin'
    PLATFORM_TWITTER = 'platform.twitter'
    PLATFORM_INSTAGRAM = 'platform.instagram'

    # Analytics permissions
    ANALYTICS_VIEW = 'analytics.view'
    ANALYTICS_EXPORT = 'analytics.export'

    # Admin permissions
    USER_MANAGE = 'user.manage'
    SETTINGS_MANAGE = 'settings.manage'
    TENANT_MANAGE = 'tenant.manage'
    AUDIT_VIEW = 'audit.view'


class Role(str, Enum):
    """Predefined roles."""
    ADMIN = 'admin'
    AGENT = 'agent'
    VIEWER = 'viewer'


# Role permission mappings
ROLE_PERMISSIONS = {
    Role.ADMIN: set(Permission),  # All permissions

    Role.AGENT: {
        Permission.WORKFLOW_CREATE,
        Permission.WORKFLOW_EXECUTE,
        Permission.WORKFLOW_VIEW,
        Permission.EMAIL_SEND,
        Permission.EMAIL_READ,
        Permission.EMAIL_REPLY,
        Permission.TICKET_CREATE,
        Permission.TICKET_UPDATE,
        Permission.TICKET_VIEW,
        Permission.PLATFORM_LINKEDIN,
        Permission.PLATFORM_TWITTER,
        Permission.PLATFORM_INSTAGRAM,
        Permission.ANALYTICS_VIEW,
    },

    Role.VIEWER: {
        Permission.WORKFLOW_VIEW,
        Permission.EMAIL_READ,
        Permission.TICKET_VIEW,
        Permission.ANALYTICS_VIEW,
    }
}


@dataclass
class User:
    """User account."""
    id: str
    username: str
    email: str
    password_hash: str
    salt: str
    role: str
    tenant_id: Optional[str] = None
    created_at: str = ''
    updated_at: str = ''
    last_login: Optional[str] = None
    is_active: bool = True
    custom_permissions: List[str] = field(default_factory=list)  # Additional permissions
    revoked_permissions: List[str] = field(default_factory=list)  # Removed permissions
    metadata: Dict[str, Any] = field(default_factory=dict)


class RBACManager:
    """
    Role-based access control manager.

    Handles:
    - User creation and management
    - Password hashing and verification
    - Permission checking
    - Role assignment
    """

    # Password hashing parameters
    PBKDF2_ITERATIONS = 600000
    SALT_LENGTH = 32
    HASH_LENGTH = 32

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize RBAC manager."""
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.users_dir = self.base_dir / 'credentials'
        self.users_dir.mkdir(parents=True, exist_ok=True)

        self._users_path = self.users_dir / 'users.json'
        self._users: Dict[str, User] = self._load_users()

    def _load_users(self) -> Dict[str, User]:
        """Load users from storage."""
        if self._users_path.exists():
            try:
                with open(self._users_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                users = {}
                for uid, udata in data.items():
                    users[uid] = User(**udata)
                return users
            except Exception as e:
                print(f"[!] Error loading users: {e}")

        return {}

    def _save_users(self):
        """Save users to storage."""
        data = {uid: asdict(u) for uid, u in self._users.items()}

        with open(self._users_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        # Set restrictive permissions
        try:
            os.chmod(self._users_path, 0o600)
        except:
            pass

    def _hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """Hash password using PBKDF2-SHA256."""
        if salt is None:
            salt = secrets.token_bytes(self.SALT_LENGTH)

        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            self.PBKDF2_ITERATIONS,
            dklen=self.HASH_LENGTH
        )

        return password_hash.hex(), salt.hex()

    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash."""
        salt_bytes = bytes.fromhex(salt)
        computed_hash, _ = self._hash_password(password, salt_bytes)
        return secrets.compare_digest(computed_hash, password_hash)

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = 'agent',
        tenant_id: Optional[str] = None
    ) -> Optional[User]:
        """
        Create a new user.

        Args:
            username: Unique username
            email: User email
            password: Plain text password (will be hashed)
            role: User role (admin, agent, viewer)
            tenant_id: Tenant ID for multi-tenant

        Returns:
            Created User or None if username exists
        """
        # Check if username exists
        for user in self._users.values():
            if user.username == username:
                print(f"[!] Username already exists: {username}")
                return None

        # Generate user ID
        user_id = f"USR-{secrets.token_hex(4).upper()}"

        # Hash password
        password_hash, salt = self._hash_password(password)
        now = datetime.utcnow().isoformat() + 'Z'

        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            salt=salt,
            role=role,
            tenant_id=tenant_id,
            created_at=now,
            updated_at=now
        )

        self._users[user_id] = user
        self._save_users()

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.AUTH,
                'user_created',
                {'user_id': user_id, 'username': username, 'role': role}
            )

        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user.

        Args:
            username: Username
            password: Plain text password

        Returns:
            User if authenticated, None otherwise
        """
        # Find user by username
        user = None
        for u in self._users.values():
            if u.username == username:
                user = u
                break

        if not user:
            if AUDIT_AVAILABLE:
                audit_log(
                    EventType.AUTH,
                    'login_failed',
                    {'username': username, 'reason': 'user_not_found'},
                    EventSeverity.WARNING
                )
            return None

        if not user.is_active:
            if AUDIT_AVAILABLE:
                audit_log(
                    EventType.AUTH,
                    'login_failed',
                    {'username': username, 'reason': 'account_disabled'},
                    EventSeverity.WARNING
                )
            return None

        # Verify password
        if not self._verify_password(password, user.password_hash, user.salt):
            if AUDIT_AVAILABLE:
                audit_log(
                    EventType.AUTH,
                    'login_failed',
                    {'username': username, 'reason': 'invalid_password'},
                    EventSeverity.WARNING
                )
            return None

        # Update last login
        user.last_login = datetime.utcnow().isoformat() + 'Z'
        self._save_users()

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.AUTH,
                'login_success',
                {'user_id': user.id, 'username': username}
            )

        return user

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password."""
        user = self._users.get(user_id)
        if not user:
            return False

        # Verify old password
        if not self._verify_password(old_password, user.password_hash, user.salt):
            return False

        # Set new password
        password_hash, salt = self._hash_password(new_password)
        user.password_hash = password_hash
        user.salt = salt
        user.updated_at = datetime.utcnow().isoformat() + 'Z'

        self._save_users()

        if AUDIT_AVAILABLE:
            audit_log(EventType.AUTH, 'password_changed', {'user_id': user_id})

        return True

    def reset_password(self, user_id: str, new_password: str) -> bool:
        """Reset user password (admin action)."""
        user = self._users.get(user_id)
        if not user:
            return False

        password_hash, salt = self._hash_password(new_password)
        user.password_hash = password_hash
        user.salt = salt
        user.updated_at = datetime.utcnow().isoformat() + 'Z'

        self._save_users()

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.AUTH,
                'password_reset',
                {'user_id': user_id},
                EventSeverity.WARNING
            )

        return True

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    def update_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[User]:
        """Update user fields."""
        user = self._users.get(user_id)
        if not user:
            return None

        if email is not None:
            user.email = email
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active
        if metadata is not None:
            user.metadata.update(metadata)

        user.updated_at = datetime.utcnow().isoformat() + 'Z'
        self._save_users()

        return user

    def delete_user(self, user_id: str) -> bool:
        """Delete user."""
        if user_id in self._users:
            del self._users[user_id]
            self._save_users()

            if AUDIT_AVAILABLE:
                audit_log(EventType.AUTH, 'user_deleted', {'user_id': user_id})

            return True
        return False

    def grant_permission(self, user_id: str, permission: str) -> bool:
        """Grant additional permission to user."""
        user = self._users.get(user_id)
        if not user:
            return False

        if permission not in user.custom_permissions:
            user.custom_permissions.append(permission)

        # Remove from revoked if present
        if permission in user.revoked_permissions:
            user.revoked_permissions.remove(permission)

        user.updated_at = datetime.utcnow().isoformat() + 'Z'
        self._save_users()

        return True

    def revoke_permission(self, user_id: str, permission: str) -> bool:
        """Revoke permission from user."""
        user = self._users.get(user_id)
        if not user:
            return False

        if permission not in user.revoked_permissions:
            user.revoked_permissions.append(permission)

        # Remove from custom if present
        if permission in user.custom_permissions:
            user.custom_permissions.remove(permission)

        user.updated_at = datetime.utcnow().isoformat() + 'Z'
        self._save_users()

        return True

    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get effective permissions for user."""
        user = self._users.get(user_id)
        if not user:
            return set()

        # Start with role permissions
        try:
            role = Role(user.role)
            permissions = set(p.value for p in ROLE_PERMISSIONS.get(role, set()))
        except ValueError:
            permissions = set()

        # Add custom permissions
        permissions.update(user.custom_permissions)

        # Remove revoked permissions
        permissions -= set(user.revoked_permissions)

        return permissions

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        permissions = self.get_user_permissions(user_id)
        return permission in permissions

    def check_permission(self, user_id: str, permission: str) -> bool:
        """
        Check permission and log access attempt.

        Args:
            user_id: User ID
            permission: Permission to check

        Returns:
            True if permitted
        """
        has_perm = self.has_permission(user_id, permission)

        if AUDIT_AVAILABLE and not has_perm:
            audit_log(
                EventType.SECURITY,
                'permission_denied',
                {'user_id': user_id, 'permission': permission},
                EventSeverity.WARNING
            )

        return has_perm

    def list_users(self, tenant_id: Optional[str] = None) -> List[Dict]:
        """List all users."""
        users = []

        for user in self._users.values():
            if tenant_id and user.tenant_id != tenant_id:
                continue

            users.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'last_login': user.last_login,
                'created_at': user.created_at
            })

        return users

    def get_stats(self) -> Dict[str, Any]:
        """Get RBAC statistics."""
        stats = {
            'total_users': len(self._users),
            'active_users': sum(1 for u in self._users.values() if u.is_active),
            'by_role': {}
        }

        for user in self._users.values():
            role = user.role
            stats['by_role'][role] = stats['by_role'].get(role, 0) + 1

        return stats


# Global instance
_rbac_manager: Optional[RBACManager] = None


def get_rbac_manager(base_dir: Optional[Path] = None) -> RBACManager:
    """Get or create RBAC manager instance."""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager(base_dir)
    return _rbac_manager


# Decorator for permission checking
def require_permission(permission: str):
    """Decorator to require permission for function."""
    def decorator(func):
        def wrapper(user_id: str, *args, **kwargs):
            manager = get_rbac_manager()
            if not manager.check_permission(user_id, permission):
                raise PermissionError(f"Permission denied: {permission}")
            return func(user_id, *args, **kwargs)
        return wrapper
    return decorator


# CLI
if __name__ == '__main__':
    import argparse
    import getpass

    parser = argparse.ArgumentParser(description='RBAC Manager CLI')
    parser.add_argument('--create-user', metavar='USERNAME', help='Create new user')
    parser.add_argument('--role', default='agent', help='Role for new user')
    parser.add_argument('--email', help='Email for new user')
    parser.add_argument('--list', action='store_true', help='List users')
    parser.add_argument('--delete', metavar='USER_ID', help='Delete user')
    parser.add_argument('--authenticate', metavar='USERNAME', help='Test authentication')
    parser.add_argument('--permissions', metavar='USER_ID', help='Show user permissions')
    parser.add_argument('--stats', action='store_true', help='Show RBAC statistics')

    args = parser.parse_args()

    manager = RBACManager()

    if args.create_user:
        email = args.email or f"{args.create_user}@example.com"
        password = getpass.getpass("Enter password: ")
        confirm = getpass.getpass("Confirm password: ")

        if password != confirm:
            print("[X] Passwords do not match")
            sys.exit(1)

        user = manager.create_user(
            username=args.create_user,
            email=email,
            password=password,
            role=args.role
        )

        if user:
            print(f"\nUser created:")
            print(f"  ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Role: {user.role}")
        else:
            print("[X] Failed to create user")

    elif args.list:
        users = manager.list_users()
        print(f"\nUsers ({len(users)}):\n")
        for u in users:
            status = 'Active' if u['is_active'] else 'Inactive'
            print(f"  {u['id']}: {u['username']} ({u['role']}) - {status}")
            print(f"        Email: {u['email']}, Last login: {u['last_login'] or 'Never'}")

    elif args.delete:
        if manager.delete_user(args.delete):
            print(f"User deleted: {args.delete}")
        else:
            print(f"User not found: {args.delete}")

    elif args.authenticate:
        password = getpass.getpass("Password: ")
        user = manager.authenticate(args.authenticate, password)

        if user:
            print(f"\n[OK] Authentication successful!")
            print(f"  User ID: {user.id}")
            print(f"  Role: {user.role}")
        else:
            print("[X] Authentication failed")

    elif args.permissions:
        permissions = manager.get_user_permissions(args.permissions)
        user = manager.get_user(args.permissions)

        if user:
            print(f"\nPermissions for {user.username} ({user.role}):")
            for p in sorted(permissions):
                print(f"  - {p}")
        else:
            print(f"User not found: {args.permissions}")

    elif args.stats:
        stats = manager.get_stats()
        print(f"\nRBAC Statistics:")
        print(f"  Total users: {stats['total_users']}")
        print(f"  Active users: {stats['active_users']}")
        print(f"\n  By role:")
        for role, count in stats['by_role'].items():
            print(f"    {role}: {count}")

    else:
        parser.print_help()
