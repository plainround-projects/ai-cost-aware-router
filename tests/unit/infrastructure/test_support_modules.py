import json
import logging
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import pytest

from cost_router.domain.routing import RouterConfig
from cost_router.domain.tasks import Kind
from cost_router.infrastructure.clock import ManualClock, SystemClock
from cost_router.infrastructure.data import (
    load_bar,
    load_prices,
    load_router_config,
    load_tasks,
    router_config_to_json,
)
from cost_router.infrastructure.env import ConfigError, read_float, read_int, read_str
from cost_router.infrastructure.logging_setup import JsonFormatter, configure_logging
from cost_router.infrastructure.parallel import thread_mapper
from cost_router.infrastructure.prompts import FilePromptStore
from cost_router.infrastructure.reports import dump_json, dump_jsonl, load_json, to_jsonable
from cost_router.infrastructure.settings import Settings

ROOT = Path(__file__).resolve().parents[3]


def test_settings_have_validated_defaults_and_overrides(tmp_path: Path):
    defaults = Settings.from_env({}, tmp_path)
    assert defaults.models == {"small": "qwen2.5:0.5b", "medium": "llama3.2:1b", "large": "qwen2.5:1.5b"}
    assert defaults.router_config_path == tmp_path / "config" / "router.json"
    custom = Settings.from_env({"TIER_LARGE": "big", "ROUTER_CONFIG": "/x.json", "WORKERS": "4"}, tmp_path)
    assert custom.models["large"] == "big" and custom.router_config_path == Path("/x.json") and custom.workers == 4
    with pytest.raises(ConfigError, match="at least"):
        Settings.from_env({"WORKERS": "0"}, tmp_path)


def test_env_readers_validate():
    assert read_str({"A": " x "}, "A") == "x" and read_str({}, "A", "d") == "d"
    with pytest.raises(ConfigError, match="required"):
        read_str({}, "A")
    assert read_float({"F": "1.5"}, "F", 0.0) == 1.5
    with pytest.raises(ConfigError, match="number"):
        read_float({"F": "x"}, "F", 0.0)
    with pytest.raises(ConfigError, match="at least"):
        read_float({"F": "-1"}, "F", 0.0)
    with pytest.raises(ConfigError, match="integer"):
        read_int({"I": "x"}, "I", 3)


def test_the_committed_data_and_configuration_load():
    tasks = load_tasks(ROOT / "data")
    assert len(tasks) == 300
    assert {t.kind for t in tasks} == set(Kind)
    assert sum(t.split == "build" for t in tasks) == 150
    assert load_bar(ROOT / "config").false_accept_bar == 0.10
    assert load_prices(ROOT / "config").per_1k_tokens["large"] == 0.0012


def test_a_router_configuration_round_trips(tmp_path: Path):
    config = RouterConfig(
        {"label": "medium", "refund": "small", "policy": "large"}, {"refund": "medium"}, "agreement", 0.001, 0.8
    )
    path = tmp_path / "router.json"
    path.write_text(json.dumps(router_config_to_json(config)))
    assert load_router_config(path) == config


def test_every_prompt_in_the_changelog_exists_and_each_file_is_listed():
    names = {p.stem for p in (ROOT / "prompts").glob("*.md") if p.stem != "CHANGELOG"}
    changelog = (ROOT / "prompts" / "CHANGELOG.md").read_text()
    for name in names:
        prompt, _, version = name.rpartition(".")
        assert f"| {prompt} | {version} |" in changelog, name


def test_prompt_store_reads_a_file_without_its_trailing_newline(tmp_path: Path):
    (tmp_path / "a.v1.md").write_text("hello {{x}}\n\n")
    assert FilePromptStore(tmp_path).get("a.v1") == "hello {{x}}"
    with pytest.raises(FileNotFoundError, match="nope"):
        FilePromptStore(tmp_path).get("nope")


@pytest.mark.parametrize("workers", [1, 3])
def test_thread_mapper_keeps_input_order(workers):
    assert thread_mapper(workers)(lambda x: x * 2, list(range(20))) == [x * 2 for x in range(20)]


class Color(StrEnum):
    RED = "red"


@dataclass(frozen=True)
class Thing:
    color: Color
    values: tuple[float, ...]
    ratio: float


def test_reports_serialize_dataclasses_enums_and_infinity(tmp_path: Path):
    value = {"t": Thing(Color.RED, (1.23456789, 2.0), float("inf"))}
    assert to_jsonable(value) == {"t": {"color": "red", "values": [1.234568, 2.0], "ratio": None}}
    dump_json(tmp_path / "a" / "x.json", value)
    assert load_json(tmp_path / "a" / "x.json")["t"]["color"] == "red"
    dump_jsonl(tmp_path / "rows.jsonl", [{"b": 1}, {"a": 2}])
    assert [json.loads(line) for line in (tmp_path / "rows.jsonl").read_text().splitlines()] == [{"b": 1}, {"a": 2}]


def test_json_log_lines_carry_extra_fields(capsys):
    configure_logging("INFO")
    configure_logging("INFO")
    logging.getLogger("t").info("call finished", extra={"tier": "small", "tokens": 7})
    line = json.loads(capsys.readouterr().err.strip().splitlines()[-1])
    assert line["msg"] == "call finished" and line["tier"] == "small" and line["level"] == "INFO"
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        record = logging.getLogger("t").makeRecord("t", logging.ERROR, "f", 1, "bad", (), logging.sys.exc_info())
    assert "RuntimeError" in json.loads(JsonFormatter().format(record))["exc"]


def test_clocks():
    clock = ManualClock(5.0)
    clock.sleep(2.5)
    assert clock.monotonic() == 7.5
    with pytest.raises(ValueError, match="backward"):
        clock.advance(-1)
    real = SystemClock()
    before = real.monotonic()
    real.sleep(0)
    real.sleep(0.001)
    assert real.monotonic() >= before
