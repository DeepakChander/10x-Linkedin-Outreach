#!/usr/bin/env python3
"""
Workflow Database - Track workflow IDs, status, and execution history

This module provides a simple JSON-based database for tracking workflows
created in the TLDraw canvas and their execution status.

Developed by 10x.in
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid

# Workflow database file
DB_FILE = Path(__file__).parent.parent.parent / "output" / "workflows" / "workflow_db.json"

# Workflow statuses
STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_PAUSED = "paused"

class WorkflowDatabase:
    """Simple JSON-based workflow database"""

    def __init__(self, db_file: Path = DB_FILE):
        self.db_file = db_file
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database file if it doesn't exist"""
        if not self.db_file.exists():
            self._save_db({"workflows": {}, "metadata": {"created": datetime.now().isoformat()}})

    def _load_db(self) -> Dict:
        """Load database from file"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"workflows": {}, "metadata": {"created": datetime.now().isoformat()}}

    def _save_db(self, db: Dict):
        """Save database to file"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)

    def create_workflow(
        self,
        name: str,
        canvas_data: Dict,
        platforms: List[str],
        node_count: int,
        description: str = ""
    ) -> str:
        """
        Create a new workflow entry

        Args:
            name: Workflow name
            canvas_data: JSON data from TLDraw canvas
            platforms: List of platforms (linkedin, twitter, instagram, email)
            node_count: Number of nodes in workflow
            description: Optional workflow description

        Returns:
            Workflow ID (UUID)
        """
        db = self._load_db()

        # Generate unique workflow ID
        workflow_id = str(uuid.uuid4())[:8]  # Short UUID for readability

        # Create workflow entry
        workflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "platforms": platforms,
            "node_count": node_count,
            "canvas_data": canvas_data,
            "status": STATUS_PENDING,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "execution_history": []
        }

        db["workflows"][workflow_id] = workflow
        self._save_db(db)

        return workflow_id

    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow by ID"""
        db = self._load_db()
        return db["workflows"].get(workflow_id)

    def update_status(
        self,
        workflow_id: str,
        status: str,
        message: str = "",
        execution_data: Optional[Dict] = None
    ):
        """
        Update workflow status

        Args:
            workflow_id: Workflow ID
            status: New status (pending, running, completed, failed, paused)
            message: Status message
            execution_data: Optional execution result data
        """
        db = self._load_db()

        if workflow_id not in db["workflows"]:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = db["workflows"][workflow_id]
        old_status = workflow["status"]

        # Update status
        workflow["status"] = status
        workflow["updated_at"] = datetime.now().isoformat()

        # Add to execution history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "status_change": f"{old_status} → {status}",
            "message": message
        }

        if execution_data:
            history_entry["data"] = execution_data

        workflow["execution_history"].append(history_entry)

        self._save_db(db)

    def list_workflows(
        self,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        List workflows with optional filtering

        Args:
            status: Filter by status (pending, running, completed, failed, paused)
            platform: Filter by platform (linkedin, twitter, instagram, email)
            limit: Maximum number of results

        Returns:
            List of workflows (sorted by created_at descending)
        """
        db = self._load_db()
        workflows = list(db["workflows"].values())

        # Filter by status
        if status:
            workflows = [w for w in workflows if w["status"] == status]

        # Filter by platform
        if platform:
            workflows = [w for w in workflows if platform in w["platforms"]]

        # Sort by created_at descending
        workflows.sort(key=lambda w: w["created_at"], reverse=True)

        return workflows[:limit]

    def get_latest_workflow(self, status: Optional[str] = None) -> Optional[Dict]:
        """Get the most recently created workflow"""
        workflows = self.list_workflows(status=status, limit=1)
        return workflows[0] if workflows else None

    def delete_workflow(self, workflow_id: str):
        """Delete a workflow"""
        db = self._load_db()

        if workflow_id in db["workflows"]:
            del db["workflows"][workflow_id]
            self._save_db(db)

    def get_statistics(self) -> Dict:
        """Get workflow statistics"""
        db = self._load_db()
        workflows = db["workflows"].values()

        total = len(workflows)
        by_status = {}
        by_platform = {}

        for workflow in workflows:
            # Count by status
            status = workflow["status"]
            by_status[status] = by_status.get(status, 0) + 1

            # Count by platform
            for platform in workflow["platforms"]:
                by_platform[platform] = by_platform.get(platform, 0) + 1

        return {
            "total": total,
            "by_status": by_status,
            "by_platform": by_platform
        }


def main():
    """CLI interface for workflow database"""
    import sys

    db = WorkflowDatabase()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python workflow_database.py list [--status=pending]")
        print("  python workflow_database.py get <workflow_id>")
        print("  python workflow_database.py stats")
        print("  python workflow_database.py latest [--status=pending]")
        return

    command = sys.argv[1]

    if command == "list":
        # Parse optional status filter
        status = None
        if len(sys.argv) > 2 and sys.argv[2].startswith("--status="):
            status = sys.argv[2].split("=")[1]

        workflows = db.list_workflows(status=status)

        if not workflows:
            print("No workflows found")
            return

        print(f"\n{'ID':<10} {'Name':<30} {'Status':<12} {'Platforms':<20} {'Nodes':<6} {'Created'}")
        print("-" * 100)

        for w in workflows:
            platforms_str = ", ".join(w["platforms"])
            created = w["created_at"][:16].replace("T", " ")  # Format: YYYY-MM-DD HH:MM
            print(f"{w['id']:<10} {w['name'][:28]:<30} {w['status']:<12} {platforms_str:<20} {w['node_count']:<6} {created}")

    elif command == "get":
        if len(sys.argv) < 3:
            print("Error: Missing workflow ID")
            return

        workflow_id = sys.argv[2]
        workflow = db.get_workflow(workflow_id)

        if not workflow:
            print(f"Workflow {workflow_id} not found")
            return

        print(json.dumps(workflow, indent=2))

    elif command == "stats":
        stats = db.get_statistics()
        print(json.dumps(stats, indent=2))

    elif command == "latest":
        # Parse optional status filter
        status = None
        if len(sys.argv) > 2 and sys.argv[2].startswith("--status="):
            status = sys.argv[2].split("=")[1]

        workflow = db.get_latest_workflow(status=status)

        if not workflow:
            print("No workflows found")
            return

        print(json.dumps(workflow, indent=2))

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
