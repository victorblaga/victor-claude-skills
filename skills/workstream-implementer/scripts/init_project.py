#!/usr/bin/env python3
"""Create a workstream-implementer project profile skeleton."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


ROOT = Path.home() / ".docs" / "workstream-implementer" / "projects"


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="Project id, e.g. acme-app")
    parser.add_argument("--display-name", default=None)
    parser.add_argument("--root-hint", action="append", default=[])
    parser.add_argument("--jira-key", action="append", default=[])
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = ROOT / args.project
    project_path = project_dir / "project.json"
    notes_path = project_dir / "notes.md"

    if project_path.exists() and not args.overwrite:
        raise SystemExit(f"Project profile already exists: {project_path}")

    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "tickets").mkdir(exist_ok=True)

    profile = {
        "schema_version": 1,
        "name": args.project,
        "display_name": args.display_name or args.project,
        "created_at": now(),
        "updated_at": now(),
        "root_hints": args.root_hint,
        "jira": {
            "project_keys": args.jira_key,
            "components": {},
            "subtasks": {
                "default": "ask",
                "create_for": [
                    "separate_owner",
                    "separate_visible_milestone",
                    "separate_repo_pr",
                    "blocker_or_dependency",
                ],
            },
        },
        "defaults": {
            "branch": {
                "pattern": "{type}/{ticket}/{slug}",
                "types": {
                    "feature": "feature",
                    "bugfix": "bugfix",
                    "refactor": "refactor",
                    "chore": "chore",
                },
            },
            "pr": {
                "title_pattern": "{ticket}: {summary}",
                "ci_monitoring": True,
                "merge": {
                    "strategy": "squash",
                    "enforce_repo_setting": True,
                    "allowed_when_user_confirms": True,
                    "delete_branch": True,
                },
            },
        },
        "repos": {},
        "playbooks": {},
    }

    project_path.write_text(json.dumps(profile, indent=2) + "\n")

    if not notes_path.exists():
        notes_path.write_text(
            f"# Project Notes: {args.display_name or args.project}\n\n"
            "Durable project conventions, rationale, and learned workflow notes.\n"
        )

    print(project_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
