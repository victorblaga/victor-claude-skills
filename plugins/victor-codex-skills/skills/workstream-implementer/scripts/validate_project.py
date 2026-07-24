#!/usr/bin/env python3
"""Validate a workstream-implementer project profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path.home() / ".scratch" / "workstream-implementer" / "projects"
VALID_REPO_STATUS = {"active", "reference", "ignored"}
VALID_MERGE_STRATEGY = {"squash", "merge", "rebase", "ask"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_or_path", help="Project id or path to project.json")
    return parser.parse_args()


def profile_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path.exists() or path.name == "project.json":
        return path
    return ROOT / value / "project.json"


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def validate_repo(name: str, repo: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    status = repo.get("status", "active")
    require(status in VALID_REPO_STATUS, errors, f"repos.{name}.status must be one of {sorted(VALID_REPO_STATUS)}")

    path_value = repo.get("path")
    require(isinstance(path_value, str) and path_value, errors, f"repos.{name}.path is required")
    if isinstance(path_value, str) and path_value:
        path = Path(path_value).expanduser()
        if status != "ignored" and not path.exists():
            warnings.append(f"repos.{name}.path does not exist on this machine: {path_value}")

    if status == "active":
        require(repo.get("default_branch"), errors, f"repos.{name}.default_branch is required for active repos")

    branch = repo.get("branch", {})
    pattern = branch.get("pattern")
    if pattern:
        require("{ticket}" in pattern, errors, f"repos.{name}.branch.pattern should include {{ticket}}")

    pr = repo.get("pr", {})
    merge = pr.get("merge", {})
    strategy = merge.get("strategy")
    if strategy:
        require(
            strategy in VALID_MERGE_STRATEGY,
            errors,
            f"repos.{name}.pr.merge.strategy must be one of {sorted(VALID_MERGE_STRATEGY)}",
        )


def main() -> int:
    args = parse_args()
    path = profile_path(args.project_or_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        raise SystemExit(f"Missing project profile: {path}")

    try:
        profile = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc

    require(profile.get("schema_version") == 1, errors, "schema_version must be 1")
    require(bool(profile.get("name")), errors, "name is required")
    require(isinstance(profile.get("repos"), dict), errors, "repos must be an object")

    repos = profile.get("repos", {})
    if isinstance(repos, dict):
        active_count = sum(1 for repo in repos.values() if repo.get("status", "active") == "active")
        if active_count == 0:
            warnings.append("profile has no active repos")
        for name, repo in repos.items():
            if isinstance(repo, dict):
                validate_repo(name, repo, errors, warnings)
            else:
                errors.append(f"repos.{name} must be an object")

    defaults = profile.get("defaults", {})
    default_merge = defaults.get("pr", {}).get("merge", {}).get("strategy")
    if default_merge:
        require(
            default_merge in VALID_MERGE_STRATEGY,
            errors,
            f"defaults.pr.merge.strategy must be one of {sorted(VALID_MERGE_STRATEGY)}",
        )

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
