import json
from pathlib import Path

import pytest

from cost_router.domain.llm import ChatRequest
from cost_router.domain.tasks import POLICY_LINES
from cost_router.interfaces import cli
from tests.unit.fakes import ScriptedModel


def answer(request: ChatRequest) -> str:
    text = request.messages[0].content
    if text.startswith("Classify"):
        return "billing"
    if text.startswith("You compute refunds"):
        return "Refund: 0.00"
    return f'Answer: x\nQuote: "{POLICY_LINES[0]}"'


@pytest.fixture
def env(tmp_path: Path, monkeypatch):
    values = {
        "REPORTS_DIR": str(tmp_path / "reports"),
        "ROUTER_CONFIG": str(tmp_path / "router.json"),
        "WORKERS": "2",
    }
    monkeypatch.setattr(cli, "process_env", lambda: values)
    monkeypatch.setattr("cost_router.interfaces.wiring.build_chat_model", lambda e, f: ScriptedModel(answer))
    return tmp_path


def test_all_runs_every_step_and_writes_the_reports(env: Path, capsys):
    assert cli.main(["all"]) == 0
    out = capsys.readouterr().out
    assert "router configuration" in out and "verdict:" in out and "false accepts by tier/check" in out
    reports = env / "reports"
    for name in ("models.json", "checks.json", "router.json", "decisions.jsonl", "day.json", "audit.json", "REPORT.md"):
        assert (reports / name).exists(), name
    router = json.loads((reports / "router.json").read_text())
    assert set(router["methods"]) == {"router", "router_no_bar", "small", "medium", "large"}
    assert router["methods"]["router"]["n"] == 150
    assert json.loads((env / "router.json").read_text())["label_check"] == "agreement"
    assert "Step 6" in (reports / "REPORT.md").read_text()
    checks = json.loads((reports / "checks.json").read_text())
    assert set(checks) == {"bar", "rates", "rates_test"}


def test_each_step_can_run_alone_in_order(env: Path):
    for step in ("models", "checks", "tune", "router", "day", "audit", "report"):
        assert cli.main([step]) == 0, step


def test_health_reports_the_data_and_prompts(env: Path, capsys):
    assert cli.main(["health"]) == 0
    assert "tasks=300 build=150 test=150" in capsys.readouterr().out


def test_parity_passes_for_equal_reports_and_fails_for_a_changed_number(env: Path, tmp_path: Path, capsys):
    assert cli.main(["all"]) == 0
    reports = env / "reports"
    other = tmp_path / "java"
    other.mkdir()
    for name in ("router.json", "day.json", "audit.json"):
        (other / name).write_text((reports / name).read_text())
    assert cli.main(["parity", "--java", str(other), "--python", str(reports)]) == 0
    changed = json.loads((other / "router.json").read_text())
    changed["methods"]["router"]["total_cost"] += 1
    changed["extra"] = 1
    (other / "router.json").write_text(json.dumps(changed))
    assert cli.main(["parity", "--java", str(other), "--python", str(reports)]) == 1
    assert "total_cost" in capsys.readouterr().out


def test_a_bad_setting_exits_with_code_two(monkeypatch, capsys):
    monkeypatch.setattr(cli, "process_env", lambda: {"WORKERS": "zero"})
    assert cli.main(["health"]) == 2
    assert "configuration error" in capsys.readouterr().err


def test_an_interrupt_exits_with_130(env: Path, monkeypatch):
    def interrupted(_services):
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "cmd_models", interrupted)
    assert cli.main(["models"]) == 130
