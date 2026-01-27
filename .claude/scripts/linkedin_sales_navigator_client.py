#!/usr/bin/env python3
"""
LinkedIn Sales Navigator API Client (SNAP)
Official REST API wrapper for all publicly documented Sales Navigator endpoints.

Base URL: https://api.linkedin.com/v2

Requires SNAP (Sales Navigator Application Platform) partner access.
LinkedIn has paused new SNAP partner onboarding — this client is for
approved partners with existing access.

Endpoints covered:

  Display Services:
    GET  /salesAccessTokens?q=viewerAndDeveloperApp  — Get iframe auth token

  Profile Services:
    GET  /salesNavigatorProfileAssociations/{key}     — Get single profile match
    GET  /salesNavigatorProfileAssociations?ids=...   — Batch get profile matches

  Analytics Services:
    GET  /salesContracts?q=contractsByMember           — List user contracts
    POST /salesAnalyticsExportJobs?action=exportActivityData      — Export activity
    POST /salesAnalyticsExportJobs?action=exportSeatData          — Export seat data
    POST /salesAnalyticsExportJobs?action=exportActivityOutcomeData — Export outcomes
    GET  /salesAnalyticsExportJobs/{jobId}             — Check export job status

  CRM Sync / Data Validation:
    POST /crmDataValidationExportJobs?crmInstanceId=...  — Create validation export
    GET  /crmDataValidationExportJobs/{jobId}?crmInstanceId=... — Check validation job

Docs: https://learn.microsoft.com/en-us/linkedin/sales/
Auth: OAuth 2.0 Bearer token

Usage:
  python linkedin_sales_navigator_client.py access-token
  python linkedin_sales_navigator_client.py profile --instance-id foo --partner bar --record-id baz
  python linkedin_sales_navigator_client.py contracts
  python linkedin_sales_navigator_client.py export-activity --contract URN --start 1700000000000 --end 1700100000000
  python linkedin_sales_navigator_client.py export-seats --contract URN --start 1700000000000 --end 1700100000000
  python linkedin_sales_navigator_client.py export-outcomes --contract URN --start 1700000000000 --end 1700100000000
  python linkedin_sales_navigator_client.py job-status JOB_ID --contract URN
  python linkedin_sales_navigator_client.py crm-validation-create --crm-instance-id URN --start 1700000000000
  python linkedin_sales_navigator_client.py crm-validation-status JOB_ID --crm-instance-id URN

Requires LINKEDIN_ACCESS_TOKEN in environment or .env file.
"""

import json
import os
import sys
import argparse
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
from pathlib import Path

BASE_URL = "https://api.linkedin.com/v2"

HEADERS_BASE = {
    "X-RestLi-Protocol-Version": "2.0.0",
    "Accept": "application/json",
}


def get_access_token() -> str:
    """Get LinkedIn OAuth2 access token from environment or .env file."""
    key = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if key:
        return key

    for env_file in [".env", ".env.local"]:
        env_path = Path(env_file)
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    print("ERROR: LINKEDIN_ACCESS_TOKEN not found. Set it in environment or .env file.", file=sys.stderr)
    sys.exit(1)


def _request(
    method: str,
    path: str,
    token: str,
    body: Optional[Dict] = None,
    params: Optional[Dict] = None,
    extra_headers: Optional[Dict] = None,
) -> Dict:
    """Make an HTTP request to LinkedIn API."""
    url = f"{BASE_URL}{path}"

    if params:
        qs = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}" if "?" not in url else f"&{qs}"

    data = json.dumps(body).encode("utf-8") if body else None

    headers = {
        **HEADERS_BASE,
        "Authorization": f"Bearer {token}",
        **(extra_headers or {}),
    }
    if body:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {"status": resp.status, "headers": dict(resp.headers)}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


import urllib.parse

# ─── Display Services ────────────────────────────────────────────────────────

def get_sales_access_token(*, token: Optional[str] = None) -> Dict:
    """
    GET /salesAccessTokens?q=viewerAndDeveloperApp

    Returns a short-lived OAuth token for embedding Sales Navigator
    display widgets (iframes) in your CRM application.

    Response: { elements: [{ token: string, expiryTime: long }] }
    """
    t = token or get_access_token()
    return _request("GET", "/salesAccessTokens?q=viewerAndDeveloperApp", t)


# ─── Profile Association Services ─────────────────────────────────────────────

def get_profile_association(
    instance_id: str,
    partner: str,
    record_id: str,
    *,
    token: Optional[str] = None,
) -> Dict:
    """
    GET /salesNavigatorProfileAssociations/(instanceId:{},partner:{},recordId:{})

    Returns the LinkedIn profile associated with a CRM record.

    Response: { profilePhoto: url, profile: url, member: urn:li:person:ID }
    """
    t = token or get_access_token()
    key = f"(instanceId:{instance_id},partner:{partner},recordId:{record_id})"
    return _request("GET", f"/salesNavigatorProfileAssociations/{key}", t)


def batch_get_profile_associations(
    keys: List[Dict[str, str]],
    *,
    token: Optional[str] = None,
) -> Dict:
    """
    GET /salesNavigatorProfileAssociations?ids=List(...)

    Batch retrieve profile associations for multiple CRM records.

    Args:
        keys: List of dicts with {instanceId, partner, recordId}

    Response: { results: { key: { profilePhoto, profile, member } }, errors: {} }
    """
    t = token or get_access_token()
    ids_str = ",".join(
        f"(instanceId:{k['instanceId']},partner:{k['partner']},recordId:{k['recordId']})"
        for k in keys
    )
    return _request("GET", f"/salesNavigatorProfileAssociations?ids=List({ids_str})", t)


# ─── Analytics Services ──────────────────────────────────────────────────────

def get_contracts(*, token: Optional[str] = None) -> Dict:
    """
    GET /salesContracts?q=contractsByMember

    List all Sales Navigator contracts where the authenticated user has an active seat.

    Response: { elements: [{ id: urn, hasReportingAccess: bool, ... }] }
    """
    t = token or get_access_token()
    return _request("GET", "/salesContracts?q=contractsByMember", t)


def export_activity_data(
    contract_urn: str,
    start_at: int,
    end_at: int,
    *,
    token: Optional[str] = None,
) -> Dict:
    """
    POST /salesAnalyticsExportJobs?action=exportActivityData

    Export activities performed by Sales Navigator seat holders
    (saving leads, searches, InMails, etc).

    Args:
        contract_urn: e.g. "urn:li:contract:12345"
        start_at: Start timestamp in milliseconds.
        end_at: End timestamp in milliseconds. Max range: 90 days.
    """
    t = token or get_access_token()
    body = {"startAt": start_at, "endAt": end_at, "contract": contract_urn}
    return _request("POST", "/salesAnalyticsExportJobs?action=exportActivityData", t, body=body)


def export_seat_data(
    contract_urn: str,
    start_at: int,
    end_at: int,
    *,
    token: Optional[str] = None,
) -> Dict:
    """
    POST /salesAnalyticsExportJobs?action=exportSeatData

    Export data about seat holders: name, seat status, Social Selling Index (SSI),
    total connections, total leads saved.

    Args:
        contract_urn: e.g. "urn:li:contract:12345"
        start_at/end_at: Timestamps in ms. Max range: 90 days.
    """
    t = token or get_access_token()
    body = {"startAt": start_at, "endAt": end_at, "contract": contract_urn}
    return _request("POST", "/salesAnalyticsExportJobs?action=exportSeatData", t, body=body)


def export_activity_outcome_data(
    contract_urn: str,
    start_at: int,
    end_at: int,
    *,
    token: Optional[str] = None,
) -> Dict:
    """
    POST /salesAnalyticsExportJobs?action=exportActivityOutcomeData

    Export results of performed activities (InMail response rates, etc).

    Args:
        contract_urn: e.g. "urn:li:contract:12345"
        start_at/end_at: Timestamps in ms. Max range: 90 days.
    """
    t = token or get_access_token()
    body = {"startAt": start_at, "endAt": end_at, "contract": contract_urn}
    return _request("POST", "/salesAnalyticsExportJobs?action=exportActivityOutcomeData", t, body=body)


def get_export_job_status(
    job_id: str,
    contract_urn: str,
    *,
    token: Optional[str] = None,
) -> Dict:
    """
    GET /salesAnalyticsExportJobs/{jobId}?contract={contractUrn}

    Check the status of an analytics export job.

    Response includes:
      - status: "PROCESSING" | "COMPLETED" | "FAILED_DUE_TO_INTERNAL_ERROR"
      - downloadURL: Available when COMPLETED (valid for 3 hours)
    """
    t = token or get_access_token()
    contract_encoded = urllib.parse.quote(contract_urn)
    return _request("GET", f"/salesAnalyticsExportJobs/{job_id}?contract={contract_encoded}", t)


# ─── CRM Data Validation Services ────────────────────────────────────────────

def create_crm_validation_export(
    crm_instance_id: str,
    export_start_at: int,
    *,
    token: Optional[str] = None,
) -> Dict:
    """
    POST /crmDataValidationExportJobs?crmInstanceId={urn}

    Create a CRM data validation export job. Validates whether CRM records
    are expired compared to LinkedIn profiles.

    Args:
        crm_instance_id: CRM Instance URN.
            Salesforce: "urn:li:crmInstance:(SFDC,orgId)"
            Dynamics: "urn:li:crmInstance:(DYNAMICS,uuid)"
        export_start_at: Start timestamp in milliseconds.

    Returns 201 with Location header containing job ID.
    """
    t = token or get_access_token()
    crm_encoded = urllib.parse.quote(crm_instance_id)
    body = {"exportStartAt": export_start_at}
    return _request("POST", f"/crmDataValidationExportJobs?crmInstanceId={crm_encoded}", t, body=body)


def get_crm_validation_status(
    job_id: str,
    crm_instance_id: str,
    *,
    token: Optional[str] = None,
) -> Dict:
    """
    GET /crmDataValidationExportJobs/{jobId}?crmInstanceId={urn}

    Check status of a CRM validation export job.

    Response:
      - status: "PROCESSING" | "COMPLETED" | "FAILED_DUE_TO_INTERNAL_ERROR"
      - downloadUrls: List of CSV download URLs (expire 1 hour)
      - nextExportStartAt: Recommended start time for next export
    """
    t = token or get_access_token()
    crm_encoded = urllib.parse.quote(crm_instance_id)
    return _request("GET", f"/crmDataValidationExportJobs/{job_id}?crmInstanceId={crm_encoded}", t)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Sales Navigator API Client (SNAP)")
    subparsers = parser.add_subparsers(dest="command", help="API endpoint")

    # access-token
    subparsers.add_parser("access-token", help="Get Sales Navigator iframe auth token")

    # profile
    sp = subparsers.add_parser("profile", help="Get profile association for CRM record")
    sp.add_argument("--instance-id", required=True)
    sp.add_argument("--partner", required=True)
    sp.add_argument("--record-id", required=True)

    # batch-profiles
    sp = subparsers.add_parser("batch-profiles", help="Batch get profile associations (JSON input)")
    sp.add_argument("keys_json", help='JSON array of {instanceId, partner, recordId}')

    # contracts
    subparsers.add_parser("contracts", help="List Sales Navigator contracts")

    # export-activity
    sp = subparsers.add_parser("export-activity", help="Export seat holder activity data")
    sp.add_argument("--contract", required=True, help="Contract URN")
    sp.add_argument("--start", required=True, type=int, help="Start timestamp (ms)")
    sp.add_argument("--end", required=True, type=int, help="End timestamp (ms)")

    # export-seats
    sp = subparsers.add_parser("export-seats", help="Export seat holder data (SSI, connections)")
    sp.add_argument("--contract", required=True)
    sp.add_argument("--start", required=True, type=int)
    sp.add_argument("--end", required=True, type=int)

    # export-outcomes
    sp = subparsers.add_parser("export-outcomes", help="Export activity outcome data")
    sp.add_argument("--contract", required=True)
    sp.add_argument("--start", required=True, type=int)
    sp.add_argument("--end", required=True, type=int)

    # job-status
    sp = subparsers.add_parser("job-status", help="Check analytics export job status")
    sp.add_argument("job_id", help="Export job ID")
    sp.add_argument("--contract", required=True, help="Contract URN")

    # crm-validation-create
    sp = subparsers.add_parser("crm-validation-create", help="Create CRM data validation export")
    sp.add_argument("--crm-instance-id", required=True, help="CRM Instance URN")
    sp.add_argument("--start", required=True, type=int, help="Export start timestamp (ms)")

    # crm-validation-status
    sp = subparsers.add_parser("crm-validation-status", help="Check CRM validation export status")
    sp.add_argument("job_id", help="Validation job ID")
    sp.add_argument("--crm-instance-id", required=True)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    result: Dict = {}

    if args.command == "access-token":
        result = get_sales_access_token()

    elif args.command == "profile":
        result = get_profile_association(args.instance_id, args.partner, args.record_id)

    elif args.command == "batch-profiles":
        keys = json.loads(args.keys_json)
        result = batch_get_profile_associations(keys)

    elif args.command == "contracts":
        result = get_contracts()

    elif args.command == "export-activity":
        result = export_activity_data(args.contract, args.start, args.end)

    elif args.command == "export-seats":
        result = export_seat_data(args.contract, args.start, args.end)

    elif args.command == "export-outcomes":
        result = export_activity_outcome_data(args.contract, args.start, args.end)

    elif args.command == "job-status":
        result = get_export_job_status(args.job_id, args.contract)

    elif args.command == "crm-validation-create":
        result = create_crm_validation_export(args.crm_instance_id, args.start)

    elif args.command == "crm-validation-status":
        result = get_crm_validation_status(args.job_id, args.crm_instance_id)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
