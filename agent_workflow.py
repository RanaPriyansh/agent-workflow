from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


@dataclass
class PhaseSpec:
    name: str
    every_minutes: int
    command: str


@dataclass
class ProjectSpec:
    name: str
    path: str
    phases: dict[str, PhaseSpec] = field(default_factory=dict)


@dataclass
class MetaConfig:
    projects: list[ProjectSpec]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def load_meta_config(path: str | Path) -> MetaConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    projects: list[ProjectSpec] = []
    for project_payload in payload.get("projects", []):
        phases_payload = project_payload.get("phases", {})
        phases: dict[str, PhaseSpec] = {}
        for phase_name, phase in phases_payload.items():
            phases[phase_name] = PhaseSpec(
                name=phase_name,
                every_minutes=int(phase.get("every_minutes", 60)),
                command=str(phase.get("command", "")).strip(),
            )
        projects.append(
            ProjectSpec(
                name=str(project_payload["name"]),
                path=str(project_payload["path"]),
                phases=phases,
            )
        )
    return MetaConfig(projects=projects)


def load_state(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"projects": {}}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"projects": {}}


def save_state(path: str | Path, state: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _phase_due(last_started_at: str | None, every_minutes: int, now: datetime) -> bool:
    if every_minutes <= 0:
        return True
    last = _parse_dt(last_started_at)
    if last is None:
        return True
    return now >= last + timedelta(minutes=every_minutes)


def _ensure_project_state(state: dict[str, Any], project_name: str) -> dict[str, Any]:
    projects = state.setdefault("projects", {})
    project_state = projects.setdefault(project_name, {})
    project_state.setdefault("phases", {})
    return project_state


def _run_command(command: str, workdir: str) -> dict[str, Any]:
    started_at = _utcnow()
    proc = subprocess.run(
        command,
        shell=True,
        cwd=workdir,
        capture_output=True,
        text=True,
    )
    finished_at = _utcnow()
    return {
        "status": "ok" if proc.returncode == 0 else "error",
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": round((finished_at - started_at).total_seconds(), 3),
    }


def run_meta_once(config_path: str | Path, state_path: str | Path) -> dict[str, Any]:
    cfg = load_meta_config(config_path)
    state = load_state(state_path)
    now = _utcnow()
    runs: list[dict[str, Any]] = []

    for project in cfg.projects:
        project_state = _ensure_project_state(state, project.name)
        phase_state_map = project_state.setdefault("phases", {})
        for phase_name, phase in project.phases.items():
            phase_state = phase_state_map.setdefault(phase_name, {})
            if not _phase_due(phase_state.get("last_started_at"), phase.every_minutes, now):
                continue
            result = _run_command(phase.command, project.path)
            phase_state.update({
                "last_started_at": result["started_at"],
                "last_finished_at": result["finished_at"],
                "last_status": result["status"],
                "last_returncode": result["returncode"],
                "last_duration_seconds": result["duration_seconds"],
            })
            run_record = {
                "project": project.name,
                "path": project.path,
                "phase": phase_name,
                "command": phase.command,
                **result,
            }
            runs.append(run_record)

    state["last_tick_at"] = now.isoformat()
    state["last_run_count"] = len(runs)
    if runs:
        state["recent_runs"] = (runs + state.get("recent_runs", []))[:50]
    save_state(state_path, state)
    return {"tick_at": now.isoformat(), "runs": runs, "state_path": str(state_path)}


def run_meta_daemon(config_path: str | Path, state_path: str | Path, interval_seconds: int = 300) -> None:
    while True:
        result = run_meta_once(config_path, state_path)
        print(json.dumps({"event": "meta_tick", "tick_at": result["tick_at"], "run_count": len(result["runs"])}), flush=True)
        time.sleep(max(1, int(interval_seconds)))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Meta harness for building, maintaining, and scaling projects")
    sub = parser.add_subparsers(dest="command", required=True)

    run_once = sub.add_parser("run-once", help="Run one meta harness tick")
    run_once.add_argument("--config", default="meta.json")
    run_once.add_argument("--state", default="data/meta_state.json")

    daemon = sub.add_parser("daemon", help="Run the meta harness continuously")
    daemon.add_argument("--config", default="meta.json")
    daemon.add_argument("--state", default="data/meta_state.json")
    daemon.add_argument("--interval", type=int, default=300)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "run-once":
        result = run_meta_once(args.config, args.state)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "daemon":
        run_meta_daemon(args.config, args.state, args.interval)
        return 0
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
