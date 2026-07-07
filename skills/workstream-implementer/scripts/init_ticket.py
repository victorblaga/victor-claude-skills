#!/usr/bin/env python3
"""Create a workstream-implementer ticket workbook."""

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
    parser.add_argument("ticket", help="JIRA key or draft id")
    parser.add_argument("--summary", default="")
    parser.add_argument("--mode", default="untriaged")
    parser.add_argument("--scope", default="untriaged")
    parser.add_argument("--repo", action="append", default=[])
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def write(path: Path, text: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    path.write_text(text)


def main() -> int:
    args = parse_args()
    project_dir = ROOT / args.project
    project_path = project_dir / "project.json"
    if not project_path.exists():
        raise SystemExit(f"Missing project profile: {project_path}")

    profile = json.loads(project_path.read_text())
    ticket_dir = project_dir / "tickets" / args.ticket
    workstreams_dir = ticket_dir / "workstreams"
    workstreams_dir.mkdir(parents=True, exist_ok=True)

    repos = args.repo
    if not repos:
        repos = [
            name
            for name, repo in profile.get("repos", {}).items()
            if repo.get("status", "active") == "active"
        ]

    status = f"""# Status: {args.ticket}

- Project: {args.project}
- JIRA: {args.ticket}
- Summary: {args.summary}
- Current phase: intake
- Scope: {args.scope}
- Mode: {args.mode}
- Active repos: {", ".join(repos) if repos else "untriaged"}
- Branches: none
- PRs: none
- Last completed: workbook created
- Next action: read JIRA contract and propose repo scope
- Blockers: none
- Last updated: {now()}
"""
    write(ticket_dir / "status.md", status, args.overwrite)

    write(
        ticket_dir / "jira.md",
        f"""# JIRA Contract: {args.ticket}

## Original Request

TBD

## Implementation Contract

TBD

## Stakeholder Updates

TBD
""",
        args.overwrite,
    )
    write(
        ticket_dir / "repos.md",
        f"""# Repo Scope: {args.ticket}

## Proposed Scope

TBD

## Active Repos

{chr(10).join(f'- {repo}' for repo in repos) if repos else 'TBD'}

## Reference Repos

TBD
""",
        args.overwrite,
    )
    write(ticket_dir / "plan.md", f"# Plan: {args.ticket}\n\nTBD\n", args.overwrite)
    write(ticket_dir / "verification.md", f"# Verification: {args.ticket}\n\nTBD\n", args.overwrite)
    write(ticket_dir / "review.md", f"# Review: {args.ticket}\n\nTBD\n", args.overwrite)
    write(ticket_dir / "decisions.md", f"# Decisions: {args.ticket}\n\nTBD\n", args.overwrite)
    write(ticket_dir / "context.md", f"# Context: {args.ticket}\n\nTBD\n", args.overwrite)

    for repo in repos:
        safe_repo = repo.replace("/", "-")
        write(
            workstreams_dir / f"{safe_repo}.md",
            f"""# Workstream: {repo}

- Repo: {repo}
- Status: unstarted
- Branch: TBD
- PR: TBD

## Plan

TBD

## Verification

TBD
""",
            args.overwrite,
        )

    print(ticket_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
