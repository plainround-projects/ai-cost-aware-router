"""Replaying the recorded fixtures regenerates exactly the committed configuration and reports (no model, no network)."""

import json
from pathlib import Path

import pytest

from cost_router.interfaces import cli

pytestmark = pytest.mark.e2e

ROOT = Path(__file__).resolve().parents[2]


def test_the_whole_study_replays_to_the_committed_reports(tmp_path: Path, monkeypatch):
    env = {
        "REPORTS_DIR": str(tmp_path),
        "ROUTER_CONFIG": str(tmp_path / "config" / "router.json"),
        "LLM_PROVIDER": "recorded",
    }
    monkeypatch.setattr(cli, "process_env", lambda: env)
    assert cli.main(["all"]) == 0
    for name in ("models.json", "checks.json", "router.json", "day.json", "audit.json"):
        assert json.loads((tmp_path / name).read_text()) == json.loads((ROOT / "reports" / name).read_text()), name
    assert (tmp_path / "REPORT.md").read_text() == (ROOT / "reports" / "REPORT.md").read_text()
    assert (tmp_path / "config" / "router.json").read_text() == (ROOT / "config" / "router.json").read_text()
