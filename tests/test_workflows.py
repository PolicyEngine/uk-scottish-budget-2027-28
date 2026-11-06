from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _load(name):
    return yaml.safe_load((WORKFLOWS / name).read_text())


def _triggers(workflow):
    # PyYAML reads the key "on" as True.
    return workflow.get("on", workflow.get(True))


def test_deploy_runs_only_on_manual_dispatch():
    triggers = _triggers(_load("deploy.yml"))
    keys = set(triggers) if isinstance(triggers, dict) else {triggers}
    assert keys == {"workflow_dispatch"}


def test_ci_installs_from_the_lock_and_times_out():
    text = (WORKFLOWS / "ci.yml").read_text()
    assert "uv sync --frozen" not in text
    assert "uv sync --locked" in text
    for job in _load("ci.yml")["jobs"].values():
        assert job.get("timeout-minutes"), job.get("name")
