# Project Profile Schema

Project profiles live at:

```text
~/.docs/workstream-implementer/projects/<project>/project.json
```

They are local-machine config. Do not commit them. Use `~` in paths where possible.

## Required Top-Level Fields

```json
{
  "schema_version": 1,
  "name": "sitesentry",
  "display_name": "SiteSentry",
  "root_hints": ["~/work/pfizer"],
  "jira": {},
  "defaults": {},
  "repos": {},
  "playbooks": {}
}
```

## JIRA

```json
{
  "jira": {
    "project_keys": ["CEN", "PFE"],
    "components": {
      "frontend": "frontend",
      "backend": "backend",
      "data-pipelines": "data-pipelines"
    },
    "subtasks": {
      "default": "ask",
      "create_for": [
        "separate_owner",
        "separate_visible_milestone",
        "separate_repo_pr",
        "blocker_or_dependency"
      ]
    }
  }
}
```

`subtasks.default` may be `ask`, `never`, or `auto_for_multi_repo`.

## Repos

Each repo entry describes one local git repo.

```json
{
  "repos": {
    "backend": {
      "path": "~/work/pfizer/sitesentry/sitesentry-backend",
      "status": "active",
      "kind": "backend",
      "default_branch": "dev",
      "branch": {
        "pattern": "{type}/{ticket}/{slug}"
      },
      "pr": {
        "target": "dev",
        "title_pattern": "{ticket}: {summary}",
        "ci_monitoring": true,
        "merge": {
          "strategy": "squash",
          "enforce_repo_setting": true,
          "allowed_when_user_confirms": true,
          "delete_branch": true
        }
      },
      "verify": [
        "./gradlew test"
      ],
      "start": {
        "command": "SPRING_PROFILES_ACTIVE=dev ./gradlew :site-mastering-web:bootRun",
        "long_running": true
      }
    }
  }
}
```

`status` values:

- `active`: default search and implementation target
- `reference`: search only when relevant to migration, parity, legacy behavior, or explicit user request
- `ignored`: known candidate that should not be used

Repo-level settings override `defaults`.

## Playbooks

Use playbooks for repeated operational workflows.

```json
{
  "playbooks": {
    "full_stack_browser_test": {
      "description": "Start backend and frontend, then run browser verification.",
      "steps": [
        {
          "repo": "backend",
          "command": "docker-compose up -d"
        },
        {
          "repo": "backend",
          "command": "SPRING_PROFILES_ACTIVE=dev ./gradlew :site-mastering-web:bootRun",
          "long_running": true,
          "readiness": {
            "url": "http://localhost:8080/actuator/health"
          }
        },
        {
          "repo": "frontend",
          "cwd": "frontend",
          "command": "yarn dev",
          "long_running": true,
          "readiness": {
            "url": "http://localhost:5173"
          }
        },
        {
          "tool": "agent-browser",
          "task": "browser_test"
        }
      ]
    }
  }
}
```

Confirm before saving new playbooks or changing commands that start services, deploy, merge, or modify repository settings.
