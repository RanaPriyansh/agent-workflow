import json
import tempfile
import unittest
from pathlib import Path

from agent_workflow import load_meta_config, run_meta_once


class MetaHarnessTests(unittest.TestCase):
    def test_load_meta_config_reads_projects_and_phases(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "meta.json"
            cfg_path.write_text(json.dumps({
                "projects": [
                    {
                        "name": "demo",
                        "path": ".",
                        "phases": {
                            "build": {"every_minutes": 10, "command": "echo build"},
                            "maintain": {"every_minutes": 20, "command": "echo maintain"}
                        }
                    }
                ]
            }))
            cfg = load_meta_config(cfg_path)
            self.assertEqual(len(cfg.projects), 1)
            self.assertEqual(cfg.projects[0].name, "demo")
            self.assertIn("build", cfg.projects[0].phases)

    def test_run_meta_once_executes_due_phase_and_updates_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_dir = root / "demo"
            project_dir.mkdir()
            marker = project_dir / "ran.txt"
            cfg_path = root / "meta.json"
            state_path = root / "state.json"
            cfg_path.write_text(json.dumps({
                "projects": [
                    {
                        "name": "demo",
                        "path": str(project_dir),
                        "phases": {
                            "build": {
                                "every_minutes": 0,
                                "command": f"python3 -c \"from pathlib import Path; Path('ran.txt').write_text('ok')\""
                            }
                        }
                    }
                ]
            }))
            result = run_meta_once(cfg_path, state_path)
            self.assertEqual(result["runs"][0]["status"], "ok")
            self.assertTrue(marker.exists())
            state = json.loads(state_path.read_text())
            self.assertIn("demo", state["projects"])
            self.assertIn("build", state["projects"]["demo"]["phases"])

    def test_run_meta_once_skips_not_due_phase(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_dir = root / "demo"
            project_dir.mkdir()
            cfg_path = root / "meta.json"
            state_path = root / "state.json"
            cfg_path.write_text(json.dumps({
                "projects": [
                    {
                        "name": "demo",
                        "path": str(project_dir),
                        "phases": {
                            "build": {"every_minutes": 999, "command": "echo build"}
                        }
                    }
                ]
            }))
            state_path.write_text(json.dumps({
                "projects": {
                    "demo": {
                        "phases": {
                            "build": {"last_started_at": "2099-01-01T00:00:00+00:00"}
                        }
                    }
                }
            }))
            result = run_meta_once(cfg_path, state_path)
            self.assertEqual(result["runs"], [])


if __name__ == "__main__":
    unittest.main()
