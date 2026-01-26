#!/usr/bin/env python3
"""
Multi-Tenant Manager for 10x-Outreach-Skill
Isolated configurations per organization

Features:
- Tenant-specific data directories
- Rate limit overrides per tenant
- Feature flags per tenant
- Resource quotas (users, workflows, targets)
- Tenant suspension/reactivation

Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
import uuid

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


@dataclass
class TenantQuotas:
    """Resource quotas for tenant."""
    max_users: int = 10
    max_workflows: int = 50
    max_targets_per_day: int = 100
    max_emails_per_day: int = 500
    max_storage_mb: int = 1000
    max_api_requests_per_hour: int = 1000


@dataclass
class TenantRateLimits:
    """Rate limit overrides for tenant."""
    email_per_hour: int = 50
    linkedin_per_day: int = 100
    twitter_per_day: int = 200
    instagram_per_day: int = 50
    api_per_minute: int = 60


@dataclass
class TenantFeatures:
    """Feature flags for tenant."""
    ai_analysis: bool = True
    semantic_search: bool = True
    webhooks: bool = True
    sla_tracking: bool = True
    multi_platform: bool = True
    custom_templates: bool = True
    api_access: bool = True
    export_data: bool = True


@dataclass
class Tenant:
    """Tenant configuration."""
    id: str
    name: str
    slug: str  # URL-safe identifier
    domain: Optional[str]
    status: str  # active, suspended, trial
    created_at: str
    updated_at: str
    owner_email: str
    plan: str = 'standard'  # trial, standard, premium, enterprise
    quotas: Dict = field(default_factory=dict)
    rate_limits: Dict = field(default_factory=dict)
    features: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    suspended_at: Optional[str] = None
    suspension_reason: Optional[str] = None


# Plan defaults
PLAN_DEFAULTS = {
    'trial': {
        'quotas': TenantQuotas(max_users=3, max_workflows=10, max_targets_per_day=50, max_emails_per_day=100),
        'features': TenantFeatures(webhooks=False, api_access=False)
    },
    'standard': {
        'quotas': TenantQuotas(),
        'features': TenantFeatures()
    },
    'premium': {
        'quotas': TenantQuotas(max_users=50, max_workflows=200, max_targets_per_day=500, max_emails_per_day=2000),
        'features': TenantFeatures()
    },
    'enterprise': {
        'quotas': TenantQuotas(max_users=1000, max_workflows=10000, max_targets_per_day=10000, max_emails_per_day=50000),
        'features': TenantFeatures()
    }
}


class MultiTenantManager:
    """
    Multi-tenant management system.

    Handles:
    - Tenant creation and configuration
    - Data isolation
    - Quota management
    - Feature flags
    - Tenant suspension
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize multi-tenant manager."""
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.tenants_dir = self.base_dir / 'tenants'
        self.tenants_dir.mkdir(parents=True, exist_ok=True)

        self._tenants_index_path = self.tenants_dir / 'index.json'
        self._tenants: Dict[str, Tenant] = self._load_tenants()

    def _load_tenants(self) -> Dict[str, Tenant]:
        """Load tenant index."""
        if self._tenants_index_path.exists():
            try:
                with open(self._tenants_index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                tenants = {}
                for tid, tdata in data.items():
                    tenants[tid] = Tenant(**tdata)
                return tenants
            except Exception as e:
                print(f"[!] Error loading tenants: {e}")

        return {}

    def _save_tenants(self):
        """Save tenant index."""
        data = {tid: asdict(t) for tid, t in self._tenants.items()}

        with open(self._tenants_index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _create_tenant_directories(self, tenant_id: str):
        """Create directory structure for tenant."""
        tenant_dir = self.tenants_dir / tenant_id

        # Create subdirectories
        subdirs = [
            'credentials',
            'workflows',
            'campaigns',
            'campaigns/active',
            'campaigns/completed',
            'campaigns/logs',
            'tickets',
            'tickets/active',
            'tickets/closed',
            'knowledge_base',
            'knowledge_base/articles',
            'templates',
            'output',
            'output/discovery',
            'output/exports',
            'audit_logs',
        ]

        for subdir in subdirs:
            (tenant_dir / subdir).mkdir(parents=True, exist_ok=True)

    def create_tenant(
        self,
        name: str,
        owner_email: str,
        plan: str = 'standard',
        domain: Optional[str] = None
    ) -> Optional[Tenant]:
        """
        Create a new tenant.

        Args:
            name: Tenant name
            owner_email: Owner email address
            plan: Subscription plan
            domain: Optional domain for tenant

        Returns:
            Created Tenant or None if slug exists
        """
        # Generate slug and ID
        slug = self._generate_slug(name)
        tenant_id = f"TNT-{str(uuid.uuid4())[:8].upper()}"

        # Check if slug exists
        for t in self._tenants.values():
            if t.slug == slug:
                print(f"[!] Tenant slug already exists: {slug}")
                return None

        now = datetime.utcnow().isoformat() + 'Z'

        # Get plan defaults
        plan_config = PLAN_DEFAULTS.get(plan, PLAN_DEFAULTS['standard'])

        tenant = Tenant(
            id=tenant_id,
            name=name,
            slug=slug,
            domain=domain,
            status='active',
            created_at=now,
            updated_at=now,
            owner_email=owner_email,
            plan=plan,
            quotas=asdict(plan_config['quotas']),
            rate_limits=asdict(TenantRateLimits()),
            features=asdict(plan_config['features'])
        )

        # Create directories
        self._create_tenant_directories(tenant_id)

        # Save
        self._tenants[tenant_id] = tenant
        self._save_tenants()

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.SYSTEM,
                'tenant_created',
                {'tenant_id': tenant_id, 'name': name, 'plan': plan}
            )

        return tenant

    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name."""
        import re
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self._tenants.get(tenant_id)

    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        for tenant in self._tenants.values():
            if tenant.slug == slug:
                return tenant
        return None

    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain."""
        for tenant in self._tenants.values():
            if tenant.domain and tenant.domain == domain:
                return tenant
        return None

    def update_tenant(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        domain: Optional[str] = None,
        plan: Optional[str] = None,
        quotas: Optional[Dict] = None,
        rate_limits: Optional[Dict] = None,
        features: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Tenant]:
        """Update tenant configuration."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return None

        if name is not None:
            tenant.name = name
        if domain is not None:
            tenant.domain = domain
        if plan is not None:
            tenant.plan = plan
        if quotas is not None:
            tenant.quotas.update(quotas)
        if rate_limits is not None:
            tenant.rate_limits.update(rate_limits)
        if features is not None:
            tenant.features.update(features)
        if metadata is not None:
            tenant.metadata.update(metadata)

        tenant.updated_at = datetime.utcnow().isoformat() + 'Z'
        self._save_tenants()

        return tenant

    def suspend_tenant(self, tenant_id: str, reason: str) -> bool:
        """Suspend tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False

        tenant.status = 'suspended'
        tenant.suspended_at = datetime.utcnow().isoformat() + 'Z'
        tenant.suspension_reason = reason
        tenant.updated_at = tenant.suspended_at

        self._save_tenants()

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.SYSTEM,
                'tenant_suspended',
                {'tenant_id': tenant_id, 'reason': reason},
                EventSeverity.WARNING
            )

        return True

    def reactivate_tenant(self, tenant_id: str) -> bool:
        """Reactivate suspended tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False

        tenant.status = 'active'
        tenant.suspended_at = None
        tenant.suspension_reason = None
        tenant.updated_at = datetime.utcnow().isoformat() + 'Z'

        self._save_tenants()

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.SYSTEM,
                'tenant_reactivated',
                {'tenant_id': tenant_id}
            )

        return True

    def delete_tenant(self, tenant_id: str, delete_data: bool = False) -> bool:
        """
        Delete tenant.

        Args:
            tenant_id: Tenant ID
            delete_data: If True, delete all tenant data

        Returns:
            True if deleted
        """
        if tenant_id not in self._tenants:
            return False

        if delete_data:
            tenant_dir = self.tenants_dir / tenant_id
            if tenant_dir.exists():
                shutil.rmtree(tenant_dir)

        del self._tenants[tenant_id]
        self._save_tenants()

        if AUDIT_AVAILABLE:
            audit_log(
                EventType.SYSTEM,
                'tenant_deleted',
                {'tenant_id': tenant_id, 'data_deleted': delete_data},
                EventSeverity.WARNING
            )

        return True

    def get_tenant_path(self, tenant_id: str, subpath: str = '') -> Optional[Path]:
        """Get path within tenant's data directory."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return None

        path = self.tenants_dir / tenant_id
        if subpath:
            path = path / subpath

        return path

    def is_tenant_active(self, tenant_id: str) -> bool:
        """Check if tenant is active."""
        tenant = self._tenants.get(tenant_id)
        return tenant is not None and tenant.status == 'active'

    def check_quota(self, tenant_id: str, quota_type: str, current_value: int) -> bool:
        """
        Check if tenant is within quota.

        Args:
            tenant_id: Tenant ID
            quota_type: Quota key (e.g., 'max_users')
            current_value: Current usage value

        Returns:
            True if within quota
        """
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False

        quota_limit = tenant.quotas.get(quota_type, 0)
        return current_value < quota_limit

    def has_feature(self, tenant_id: str, feature: str) -> bool:
        """Check if tenant has feature enabled."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False

        return tenant.features.get(feature, False)

    def get_rate_limit(self, tenant_id: str, limit_type: str) -> int:
        """Get rate limit for tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return 0

        return tenant.rate_limits.get(limit_type, 0)

    def list_tenants(self, status: Optional[str] = None) -> List[Dict]:
        """List all tenants."""
        tenants = []

        for tenant in self._tenants.values():
            if status and tenant.status != status:
                continue

            tenants.append({
                'id': tenant.id,
                'name': tenant.name,
                'slug': tenant.slug,
                'status': tenant.status,
                'plan': tenant.plan,
                'owner_email': tenant.owner_email,
                'created_at': tenant.created_at
            })

        return tenants

    def get_usage(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant resource usage."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return {}

        tenant_dir = self.tenants_dir / tenant_id
        if not tenant_dir.exists():
            return {}

        usage = {
            'users': 0,
            'workflows': 0,
            'tickets_active': 0,
            'kb_articles': 0,
            'storage_mb': 0
        }

        # Count workflows
        workflows_dir = tenant_dir / 'workflows'
        if workflows_dir.exists():
            usage['workflows'] = len(list(workflows_dir.glob('*.json')))

        # Count tickets
        tickets_dir = tenant_dir / 'tickets' / 'active'
        if tickets_dir.exists():
            usage['tickets_active'] = len(list(tickets_dir.glob('*.json')))

        # Count KB articles
        kb_dir = tenant_dir / 'knowledge_base' / 'articles'
        if kb_dir.exists():
            usage['kb_articles'] = len(list(kb_dir.glob('*.json')))

        # Calculate storage
        total_size = 0
        for path in tenant_dir.rglob('*'):
            if path.is_file():
                total_size += path.stat().st_size
        usage['storage_mb'] = round(total_size / (1024 * 1024), 2)

        return usage

    def get_stats(self) -> Dict[str, Any]:
        """Get multi-tenant statistics."""
        stats = {
            'total_tenants': len(self._tenants),
            'active_tenants': 0,
            'suspended_tenants': 0,
            'by_plan': {},
            'by_status': {}
        }

        for tenant in self._tenants.values():
            # Count by status
            stats['by_status'][tenant.status] = stats['by_status'].get(tenant.status, 0) + 1
            if tenant.status == 'active':
                stats['active_tenants'] += 1
            elif tenant.status == 'suspended':
                stats['suspended_tenants'] += 1

            # Count by plan
            stats['by_plan'][tenant.plan] = stats['by_plan'].get(tenant.plan, 0) + 1

        return stats


# Global instance
_tenant_manager: Optional[MultiTenantManager] = None


def get_tenant_manager(base_dir: Optional[Path] = None) -> MultiTenantManager:
    """Get or create tenant manager instance."""
    global _tenant_manager
    if _tenant_manager is None:
        _tenant_manager = MultiTenantManager(base_dir)
    return _tenant_manager


# CLI
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Multi-Tenant Manager CLI')
    parser.add_argument('--create', metavar='NAME', help='Create new tenant')
    parser.add_argument('--email', help='Owner email for new tenant')
    parser.add_argument('--plan', default='standard', help='Plan for new tenant')
    parser.add_argument('--list', action='store_true', help='List tenants')
    parser.add_argument('--get', metavar='ID', help='Get tenant details')
    parser.add_argument('--suspend', metavar='ID', help='Suspend tenant')
    parser.add_argument('--reactivate', metavar='ID', help='Reactivate tenant')
    parser.add_argument('--usage', metavar='ID', help='Show tenant usage')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--reason', help='Suspension reason')

    args = parser.parse_args()

    manager = MultiTenantManager()

    if args.create:
        if not args.email:
            print("[X] --email required for tenant creation")
            sys.exit(1)

        tenant = manager.create_tenant(
            name=args.create,
            owner_email=args.email,
            plan=args.plan
        )

        if tenant:
            print(f"\nTenant created:")
            print(f"  ID: {tenant.id}")
            print(f"  Name: {tenant.name}")
            print(f"  Slug: {tenant.slug}")
            print(f"  Plan: {tenant.plan}")

    elif args.list:
        tenants = manager.list_tenants()
        print(f"\nTenants ({len(tenants)}):\n")
        for t in tenants:
            status_icon = '🟢' if t['status'] == 'active' else '🔴'
            print(f"  {status_icon} {t['id']}: {t['name']} ({t['plan']})")
            print(f"        Slug: {t['slug']}, Owner: {t['owner_email']}")

    elif args.get:
        tenant = manager.get_tenant(args.get)
        if tenant:
            print(f"\nTenant: {tenant.name}")
            print(f"  ID: {tenant.id}")
            print(f"  Slug: {tenant.slug}")
            print(f"  Status: {tenant.status}")
            print(f"  Plan: {tenant.plan}")
            print(f"  Owner: {tenant.owner_email}")
            print(f"\n  Quotas: {tenant.quotas}")
            print(f"  Features: {tenant.features}")
        else:
            print(f"Tenant not found: {args.get}")

    elif args.suspend:
        reason = args.reason or "Administrative action"
        if manager.suspend_tenant(args.suspend, reason):
            print(f"Tenant suspended: {args.suspend}")
        else:
            print(f"Tenant not found: {args.suspend}")

    elif args.reactivate:
        if manager.reactivate_tenant(args.reactivate):
            print(f"Tenant reactivated: {args.reactivate}")
        else:
            print(f"Tenant not found: {args.reactivate}")

    elif args.usage:
        usage = manager.get_usage(args.usage)
        if usage:
            print(f"\nTenant Usage:")
            for key, value in usage.items():
                print(f"  {key}: {value}")
        else:
            print(f"Tenant not found: {args.usage}")

    elif args.stats:
        stats = manager.get_stats()
        print(f"\nMulti-Tenant Statistics:")
        print(f"  Total tenants: {stats['total_tenants']}")
        print(f"  Active: {stats['active_tenants']}")
        print(f"  Suspended: {stats['suspended_tenants']}")
        print(f"\n  By plan: {stats['by_plan']}")
        print(f"  By status: {stats['by_status']}")

    else:
        parser.print_help()
