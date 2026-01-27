#!/usr/bin/env python3
"""
Integration Manager — Pull-based data sync, import/export, service connections.

Usage:
  python integration_manager.py status
  python integration_manager.py sync <service>
  python integration_manager.py import <file> --format csv|json
  python integration_manager.py export <type> --format csv|json [--output <file>]
  python integration_manager.py connect <service> [--config key=value]
  python integration_manager.py disconnect <service>
  python integration_manager.py log [--days 7]

Data: output/integrations/
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path("output/integrations")
SYNC_LOG = DATA_DIR / "sync_log.json"
CONNECTIONS_FILE = DATA_DIR / "connections.json"

# Where other skills store data
CONTACTS_FILE = Path("output/accounts/contacts.json")
CAMPAIGNS_DIR = Path("output/campaigns")
TICKETS_DIR = Path("output/tickets")
DISCOVERY_DIR = Path("output/discovery")
QA_DIR = Path("output/qa")


def _ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load(filepath: Path) -> list:
    if filepath.exists():
        return json.loads(filepath.read_text())
    return []


def _save(filepath: Path, data):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(data, indent=2, default=str))


def _log_event(action: str, service: str, details: Dict):
    _ensure_dirs()
    log = _load(SYNC_LOG)
    log.append({
        "action": action,
        "service": service,
        "details": details,
        "timestamp": datetime.now().isoformat(),
    })
    _save(SYNC_LOG, log)


# ─── Status ──────────────────────────────────────────────────────────────────

def status() -> Dict:
    connections = _load(CONNECTIONS_FILE)
    log = _load(SYNC_LOG)

    last_syncs = {}
    for entry in reversed(log):
        svc = entry.get("service", "")
        if svc and svc not in last_syncs and entry.get("action") == "sync":
            last_syncs[svc] = entry["timestamp"]

    return {
        "connections": [{
            "service": c["service"],
            "status": c.get("status", "active"),
            "connected_at": c.get("connected_at", ""),
            "last_sync": last_syncs.get(c["service"], "never"),
        } for c in connections],
        "total_syncs": sum(1 for e in log if e.get("action") == "sync"),
        "total_imports": sum(1 for e in log if e.get("action") == "import"),
        "total_exports": sum(1 for e in log if e.get("action") == "export"),
    }


# ─── Sync ────────────────────────────────────────────────────────────────────

def sync_service(service: str) -> Dict:
    """Pull latest data from a service. Returns summary of what was synced."""
    connections = _load(CONNECTIONS_FILE)
    conn = next((c for c in connections if c["service"] == service), None)

    if not conn:
        return {"error": f"Service '{service}' not connected. Use 'connect {service}' first.",
                "available": [c["service"] for c in connections]}

    # Each service would have its own sync logic
    # For now, log the sync attempt and return instructions
    result = {
        "service": service,
        "status": "ready",
        "message": f"Sync from {service} triggered",
        "synced_at": datetime.now().isoformat(),
    }

    if service == "gmail":
        result["instructions"] = "Use /inbox to pull latest emails, then /integrations import to process"
    elif service == "sheets":
        result["instructions"] = "Provide spreadsheet ID with --id flag to pull recipients"
    elif service == "exa":
        result["instructions"] = "Use /discover or /exa to pull latest results, then /integrations import"

    _log_event("sync", service, result)
    return result


# ─── Import ──────────────────────────────────────────────────────────────────

def import_data(filepath: str, fmt: str = "csv") -> Dict:
    path = Path(filepath)
    if not path.exists():
        return {"error": f"File not found: {filepath}"}

    imported = 0

    if fmt == "csv":
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            imported = len(rows)

            # Auto-detect: if has 'name' and 'email' columns, import as contacts
            if rows and ("name" in rows[0] or "Name" in rows[0]):
                contacts = _load(CONTACTS_FILE)
                for row in rows:
                    contacts.append({
                        "name": row.get("name", row.get("Name", "")),
                        "email": row.get("email", row.get("Email", "")),
                        "company": row.get("company", row.get("Company", "")),
                        "role": row.get("role", row.get("Role", "")),
                        "source": f"import:{path.name}",
                        "imported_at": datetime.now().isoformat(),
                    })
                _save(CONTACTS_FILE, contacts)

    elif fmt == "json":
        data = json.loads(path.read_text())
        items = data if isinstance(data, list) else [data]
        imported = len(items)

        # Store as-is in imports directory
        import_file = DATA_DIR / f"import_{path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        _save(import_file, items)

    result = {"imported": imported, "file": filepath, "format": fmt}
    _log_event("import", f"file:{path.name}", result)
    return result


# ─── Export ──────────────────────────────────────────────────────────────────

def export_data(data_type: str, fmt: str = "csv", output: str = None) -> Dict:
    # Load data based on type
    if data_type == "contacts":
        data = _load(CONTACTS_FILE)
        keys = ["id", "name", "email", "company", "role", "phone", "deal_stage", "deal_value", "source"]
    elif data_type == "campaigns":
        data = []
        if CAMPAIGNS_DIR.exists():
            for f in CAMPAIGNS_DIR.glob("*.json"):
                data.extend(_load(f) if isinstance(_load(f), list) else [_load(f)])
        keys = None
    elif data_type == "tickets":
        tickets_file = TICKETS_DIR / "tickets.json"
        data = _load(tickets_file)
        keys = ["id", "title", "status", "priority", "assignee", "created_at"]
    elif data_type == "discovery":
        data = []
        if DISCOVERY_DIR.exists():
            for f in DISCOVERY_DIR.glob("*.json"):
                data.extend(_load(f) if isinstance(_load(f), list) else [_load(f)])
        keys = None
    elif data_type == "reviews":
        reviews_file = QA_DIR / "reviews.json"
        data = _load(reviews_file)
        keys = None
    else:
        return {"error": f"Unknown data type: {data_type}. Use: contacts, campaigns, tickets, discovery, reviews"}

    if not data:
        return {"exported": 0, "message": f"No {data_type} data found"}

    if not output:
        output = f"output/exports/{data_type}_export_{datetime.now().strftime('%Y%m%d')}.{fmt}"

    Path(output).parent.mkdir(parents=True, exist_ok=True)

    if fmt == "csv" and keys:
        with open(output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)
    elif fmt == "json":
        Path(output).write_text(json.dumps(data, indent=2, default=str))
    else:
        # CSV without predefined keys — use all keys from first item
        if data and isinstance(data[0], dict):
            keys = list(data[0].keys())
            with open(output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(data)

    result = {"exported": len(data), "file": output, "format": fmt, "type": data_type}
    _log_event("export", data_type, result)
    return result


# ─── Connections ─────────────────────────────────────────────────────────────

def connect_service(service: str, config: Dict = None) -> Dict:
    connections = _load(CONNECTIONS_FILE)
    existing = next((c for c in connections if c["service"] == service), None)

    if existing:
        existing["config"] = {**existing.get("config", {}), **(config or {})}
        existing["updated_at"] = datetime.now().isoformat()
    else:
        connections.append({
            "service": service,
            "status": "active",
            "config": config or {},
            "connected_at": datetime.now().isoformat(),
        })

    _save(CONNECTIONS_FILE, connections)
    _log_event("connect", service, {"config_keys": list((config or {}).keys())})
    return {"service": service, "status": "connected"}


def disconnect_service(service: str) -> Dict:
    connections = _load(CONNECTIONS_FILE)
    connections = [c for c in connections if c["service"] != service]
    _save(CONNECTIONS_FILE, connections)
    _log_event("disconnect", service, {})
    return {"service": service, "status": "disconnected"}


# ─── Log ─────────────────────────────────────────────────────────────────────

def view_log(days: int = 30) -> List[Dict]:
    log = _load(SYNC_LOG)
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    return [e for e in log if e.get("timestamp", "") >= cutoff]


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Integration Manager — Data sync & import/export")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show integration status")

    sp = subparsers.add_parser("sync", help="Sync from a service")
    sp.add_argument("service")

    sp = subparsers.add_parser("import", help="Import data from file")
    sp.add_argument("file")
    sp.add_argument("--format", dest="fmt", default="csv", choices=["csv", "json"])

    sp = subparsers.add_parser("export", help="Export data")
    sp.add_argument("type", choices=["contacts", "campaigns", "tickets", "discovery", "reviews"])
    sp.add_argument("--format", dest="fmt", default="csv", choices=["csv", "json"])
    sp.add_argument("--output")

    sp = subparsers.add_parser("connect", help="Connect a service")
    sp.add_argument("service")
    sp.add_argument("--config", nargs="*", help="key=value pairs")

    sp = subparsers.add_parser("disconnect", help="Disconnect a service")
    sp.add_argument("service")

    sp = subparsers.add_parser("log", help="View sync log")
    sp.add_argument("--days", type=int, default=30)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "status":
        print(json.dumps(status(), indent=2))
    elif args.command == "sync":
        print(json.dumps(sync_service(args.service), indent=2))
    elif args.command == "import":
        print(json.dumps(import_data(args.file, args.fmt), indent=2))
    elif args.command == "export":
        print(json.dumps(export_data(args.type, args.fmt, args.output), indent=2))
    elif args.command == "connect":
        config = {}
        if args.config:
            for item in args.config:
                if "=" in item:
                    k, v = item.split("=", 1)
                    config[k] = v
        print(json.dumps(connect_service(args.service, config), indent=2))
    elif args.command == "disconnect":
        print(json.dumps(disconnect_service(args.service), indent=2))
    elif args.command == "log":
        print(json.dumps(view_log(args.days), indent=2))


if __name__ == "__main__":
    main()
