#!/usr/bin/env python3
"""
Exa Websets REST API Client
Official API wrapper for Exa Websets — curated web entity collections.

Base URL: https://api.exa.ai/websets/v0

Endpoints covered:
  POST   /websets/                        — Create a webset (with search + enrichments)
  GET    /websets/{id}                     — Get webset details
  GET    /websets/                         — List all websets
  DELETE /websets/{id}                     — Delete a webset
  PATCH  /websets/{id}                     — Update webset metadata
  GET    /websets/{id}/items              — List items in a webset
  GET    /websets/{id}/items/{item_id}    — Get a single item
  DELETE /websets/{id}/items/{item_id}    — Delete an item
  POST   /websets/{id}/searches           — Add a new search to existing webset
  GET    /websets/{id}/searches           — List searches in a webset
  POST   /websets/{id}/enrichments        — Add enrichment agent to webset
  GET    /websets/{id}/enrichments        — List enrichments
  POST   /monitors                        — Create a monitor (scheduled re-runs)
  GET    /monitors                        — List monitors
  GET    /monitors/{id}                   — Get monitor details
  DELETE /monitors/{id}                   — Delete a monitor

Docs: https://docs.exa.ai/websets/api/overview
Dashboard: https://websets.exa.ai/websets

Usage:
  python exa_websets_client.py create "AI Founders" "Find AI startup founders" --count 50
  python exa_websets_client.py list
  python exa_websets_client.py get WEBSET_ID
  python exa_websets_client.py items WEBSET_ID
  python exa_websets_client.py add-search WEBSET_ID "ML engineers at Series B startups" --count 20
  python exa_websets_client.py add-enrichment WEBSET_ID "Find their email address" --format text
  python exa_websets_client.py create-monitor WEBSET_ID --cron "0 9 * * 1"
  python exa_websets_client.py delete WEBSET_ID

Requires EXA_API_KEY in environment or .env file.
"""

import json
import os
import sys
import argparse
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
from pathlib import Path

BASE_URL = "https://api.exa.ai/websets/v0"


def get_api_key() -> str:
    """Get Exa API key from environment or .env file."""
    key = os.environ.get("EXA_API_KEY")
    if key:
        return key

    for env_file in [".env", ".env.local"]:
        env_path = Path(env_file)
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("EXA_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    print("ERROR: EXA_API_KEY not found. Set it in environment or .env file.", file=sys.stderr)
    sys.exit(1)


def _request(
    method: str,
    path: str,
    api_key: str,
    body: Optional[Dict] = None,
    params: Optional[Dict] = None,
) -> Dict:
    """Make an HTTP request to the Websets API."""
    url = f"{BASE_URL}{path}"

    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}"

    data = json.dumps(body).encode("utf-8") if body else None

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


# ─── Websets CRUD ────────────────────────────────────────────────────────────

def create_webset(
    search_query: str,
    *,
    count: int = 25,
    entity: Optional[str] = None,
    enrichments: Optional[List[Dict[str, str]]] = None,
    metadata: Optional[Dict[str, str]] = None,
    api_key: Optional[str] = None,
) -> Dict:
    """
    POST /websets/ — Create a new webset with an initial search.

    Args:
        search_query: Natural language description of what to find.
        count: Number of items to find (default 25).
        entity: Type of entity — "person", "company", etc.
        enrichments: List of enrichment configs, each with:
            - description: What data to extract (e.g., "Find their email")
            - format: "text" | "number" | "date" | "boolean" | "url" | "email"
        metadata: Key-value metadata tags for the webset.
    """
    key = api_key or get_api_key()

    body: Dict[str, Any] = {
        "search": {
            "query": search_query,
            "count": count,
        },
    }

    if entity:
        body["search"]["entity"] = entity

    if enrichments:
        body["enrichments"] = [
            {"description": e["description"], "format": e.get("format", "text")}
            for e in enrichments
        ]

    if metadata:
        body["metadata"] = metadata

    return _request("POST", "/websets/", key, body=body)


def get_webset(webset_id: str, *, expand_items: bool = False, api_key: Optional[str] = None) -> Dict:
    """GET /websets/{id} — Get webset details."""
    key = api_key or get_api_key()
    params = {"expand": "items"} if expand_items else None
    return _request("GET", f"/websets/{webset_id}", key, params=params)


def list_websets(*, api_key: Optional[str] = None) -> Dict:
    """GET /websets/ — List all websets."""
    key = api_key or get_api_key()
    return _request("GET", "/websets/", key)


def update_webset(
    webset_id: str,
    *,
    metadata: Optional[Dict[str, str]] = None,
    api_key: Optional[str] = None,
) -> Dict:
    """PATCH /websets/{id} — Update webset metadata."""
    key = api_key or get_api_key()
    body: Dict[str, Any] = {}
    if metadata:
        body["metadata"] = metadata
    return _request("PATCH", f"/websets/{webset_id}", key, body=body)


def delete_webset(webset_id: str, *, api_key: Optional[str] = None) -> Dict:
    """DELETE /websets/{id} — Delete a webset."""
    key = api_key or get_api_key()
    return _request("DELETE", f"/websets/{webset_id}", key)


# ─── Items ───────────────────────────────────────────────────────────────────

def list_items(
    webset_id: str,
    *,
    cursor: Optional[str] = None,
    limit: int = 100,
    api_key: Optional[str] = None,
) -> Dict:
    """GET /websets/{id}/items — List items in a webset."""
    key = api_key or get_api_key()
    params: Dict[str, Any] = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    return _request("GET", f"/websets/{webset_id}/items", key, params=params)


def get_item(webset_id: str, item_id: str, *, api_key: Optional[str] = None) -> Dict:
    """GET /websets/{id}/items/{item_id} — Get a single item."""
    key = api_key or get_api_key()
    return _request("GET", f"/websets/{webset_id}/items/{item_id}", key)


def delete_item(webset_id: str, item_id: str, *, api_key: Optional[str] = None) -> Dict:
    """DELETE /websets/{id}/items/{item_id} — Delete an item."""
    key = api_key or get_api_key()
    return _request("DELETE", f"/websets/{webset_id}/items/{item_id}", key)


# ─── Searches ────────────────────────────────────────────────────────────────

def add_search(
    webset_id: str,
    query: str,
    *,
    count: int = 25,
    entity: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict:
    """POST /websets/{id}/searches — Add a new search to an existing webset."""
    key = api_key or get_api_key()
    body: Dict[str, Any] = {"query": query, "count": count}
    if entity:
        body["entity"] = entity
    return _request("POST", f"/websets/{webset_id}/searches", key, body=body)


def list_searches(webset_id: str, *, api_key: Optional[str] = None) -> Dict:
    """GET /websets/{id}/searches — List searches in a webset."""
    key = api_key or get_api_key()
    return _request("GET", f"/websets/{webset_id}/searches", key)


# ─── Enrichments ─────────────────────────────────────────────────────────────

def add_enrichment(
    webset_id: str,
    description: str,
    *,
    fmt: str = "text",
    api_key: Optional[str] = None,
) -> Dict:
    """
    POST /websets/{id}/enrichments — Add an enrichment agent.

    Enrichments extract additional structured data from each item.

    Args:
        webset_id: Webset to enrich.
        description: What data to extract (e.g., "Find their email address").
        fmt: Output format — "text" | "number" | "date" | "boolean" | "url" | "email".
    """
    key = api_key or get_api_key()
    body = {"description": description, "format": fmt}
    return _request("POST", f"/websets/{webset_id}/enrichments", key, body=body)


def list_enrichments(webset_id: str, *, api_key: Optional[str] = None) -> Dict:
    """GET /websets/{id}/enrichments — List enrichments on a webset."""
    key = api_key or get_api_key()
    return _request("GET", f"/websets/{webset_id}/enrichments", key)


# ─── Monitors ────────────────────────────────────────────────────────────────

def create_monitor(
    webset_id: str,
    *,
    cron: str = "0 9 * * 1",
    api_key: Optional[str] = None,
) -> Dict:
    """
    POST /monitors — Create a scheduled monitor for a webset.

    Monitors automatically re-run searches on a schedule to keep websets current.

    Args:
        webset_id: Webset to monitor.
        cron: Cron expression for schedule (default: every Monday 9am).
    """
    key = api_key or get_api_key()
    body = {"websetId": webset_id, "schedule": {"cron": cron}}
    return _request("POST", "/monitors", key, body=body)


def list_monitors(*, api_key: Optional[str] = None) -> Dict:
    """GET /monitors — List all monitors."""
    key = api_key or get_api_key()
    return _request("GET", "/monitors", key)


def get_monitor(monitor_id: str, *, api_key: Optional[str] = None) -> Dict:
    """GET /monitors/{id} — Get monitor details."""
    key = api_key or get_api_key()
    return _request("GET", f"/monitors/{monitor_id}", key)


def delete_monitor(monitor_id: str, *, api_key: Optional[str] = None) -> Dict:
    """DELETE /monitors/{id} — Delete a monitor."""
    key = api_key or get_api_key()
    return _request("DELETE", f"/monitors/{monitor_id}", key)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Exa Websets REST API Client")
    subparsers = parser.add_subparsers(dest="command", help="API action")

    # create
    sp = subparsers.add_parser("create", help="Create a new webset")
    sp.add_argument("query", help="Search query for the webset")
    sp.add_argument("--count", type=int, default=25, help="Number of items to find")
    sp.add_argument("--entity", help="Entity type: person, company, etc.")
    sp.add_argument("--enrich", nargs="+", help="Enrichment descriptions to add")
    sp.add_argument("--enrich-format", default="text", help="Format for enrichments")

    # list
    subparsers.add_parser("list", help="List all websets")

    # get
    sp = subparsers.add_parser("get", help="Get webset details")
    sp.add_argument("id", help="Webset ID")
    sp.add_argument("--expand-items", action="store_true")

    # delete
    sp = subparsers.add_parser("delete", help="Delete a webset")
    sp.add_argument("id", help="Webset ID")

    # items
    sp = subparsers.add_parser("items", help="List items in a webset")
    sp.add_argument("id", help="Webset ID")
    sp.add_argument("--limit", type=int, default=100)

    # get-item
    sp = subparsers.add_parser("get-item", help="Get a single item")
    sp.add_argument("webset_id", help="Webset ID")
    sp.add_argument("item_id", help="Item ID")

    # add-search
    sp = subparsers.add_parser("add-search", help="Add search to existing webset")
    sp.add_argument("id", help="Webset ID")
    sp.add_argument("query", help="Search query")
    sp.add_argument("--count", type=int, default=25)
    sp.add_argument("--entity", help="Entity type")

    # add-enrichment
    sp = subparsers.add_parser("add-enrichment", help="Add enrichment to webset")
    sp.add_argument("id", help="Webset ID")
    sp.add_argument("description", help="What to extract")
    sp.add_argument("--format", dest="fmt", default="text",
                    choices=["text", "number", "date", "boolean", "url", "email"])

    # list-enrichments
    sp = subparsers.add_parser("list-enrichments", help="List enrichments on a webset")
    sp.add_argument("id", help="Webset ID")

    # create-monitor
    sp = subparsers.add_parser("create-monitor", help="Create a monitor")
    sp.add_argument("id", help="Webset ID")
    sp.add_argument("--cron", default="0 9 * * 1", help="Cron schedule")

    # list-monitors
    subparsers.add_parser("list-monitors", help="List all monitors")

    # delete-monitor
    sp = subparsers.add_parser("delete-monitor", help="Delete a monitor")
    sp.add_argument("id", help="Monitor ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    result: Dict = {}

    if args.command == "create":
        enrichments = None
        if args.enrich:
            enrichments = [{"description": e, "format": args.enrich_format} for e in args.enrich]
        result = create_webset(args.query, count=args.count, entity=args.entity, enrichments=enrichments)

    elif args.command == "list":
        result = list_websets()

    elif args.command == "get":
        result = get_webset(args.id, expand_items=args.expand_items)

    elif args.command == "delete":
        result = delete_webset(args.id)
        print(f"Deleted webset: {args.id}")
        return

    elif args.command == "items":
        result = list_items(args.id, limit=args.limit)

    elif args.command == "get-item":
        result = get_item(args.webset_id, args.item_id)

    elif args.command == "add-search":
        result = add_search(args.id, args.query, count=args.count, entity=args.entity)

    elif args.command == "add-enrichment":
        result = add_enrichment(args.id, args.description, fmt=args.fmt)

    elif args.command == "list-enrichments":
        result = list_enrichments(args.id)

    elif args.command == "create-monitor":
        result = create_monitor(args.id, cron=args.cron)

    elif args.command == "list-monitors":
        result = list_monitors()

    elif args.command == "delete-monitor":
        result = delete_monitor(args.id)
        print(f"Deleted monitor: {args.id}")
        return

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
