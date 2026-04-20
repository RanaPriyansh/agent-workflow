# Agent Workflow

[![GitHub](https://img.shields.io/badge/GitHub-000000?logo=github)](https://github.com/RanaPriyansh/agent-workflow)
[![License](https://img.shields.io/github/license/RanaPriyansh/agent-workflow)](https://github.com/RanaPriyansh/agent-workflow/blob/main/LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/RanaPriyansh/agent-workflow)](https://github.com/RanaPriyansh/agent-workflow/commits/main)

Meta harness for building, maintaining, and scaling project portfolios.

This is not just a DAG toy anymore. It is a lightweight operating harness that can continuously run phase-specific commands across multiple projects, persist state, and keep the project empire warm.

## What it does

- Runs project phases like `build`, `maintain`, and `scale`
- Persists last-run state in JSON
- Executes shell commands inside each project repo
- Skips phases that are not due yet
- Can run once or continuously as a daemon

## Core idea

A project portfolio usually dies from entropy, not lack of ideas.

The meta harness solves that by giving each project a recurring operating loop:

- `build` → prove something still works
- `maintain` → inspect health / drift / dirty state
- `scale` → run compounding actions like collection, research, exports, or growth machinery

## Quick start

```bash
cd /root/git-repos/agent-workflow
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 agent_workflow.py run-once --config meta.example.json --state data/meta_state.json
python3 agent_workflow.py daemon --config meta.example.json --state data/meta_state.json --interval 300
```

## Config format

Use a JSON file like `meta.example.json`:

```json
{
  "projects": [
    {
      "name": "demo-project",
      "path": "/abs/path/to/project",
      "phases": {
        "build": {
          "every_minutes": 60,
          "command": "pytest -q"
        },
        "maintain": {
          "every_minutes": 30,
          "command": "git status --short"
        },
        "scale": {
          "every_minutes": 240,
          "command": "python3 collector.py"
        }
      }
    }
  ]
}
```

## CLI

Run once:

```bash
python3 agent_workflow.py run-once --config meta.example.json --state data/meta_state.json
```

Run continuously:

```bash
python3 agent_workflow.py daemon --config meta.example.json --state data/meta_state.json --interval 300
```

Or after install:

```bash
pip install -e .
agent-workflow run-once --config meta.example.json --state data/meta_state.json
```

## Why this matters

Single repos are not the problem. Portfolio coordination is the problem.

This harness is the thin control layer for:
- build systems
- maintenance loops
- compounding project actions
- future agent delegation and approval points
- eventually, a real project empire OS

## Current MVP limits

- JSON config only
- local shell command execution only
- sequential execution
- no human approval pauses yet
- no distributed queue yet

That is fine. MVP first. Control surface first. Reliability first.

## Validation

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## License

MIT

---

Built with ❤️ by Thielon
