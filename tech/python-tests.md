# Python tests, file by file

## What it is

These are the test files of the Python half: the unit tests of every layer, the end-to-end test that replays the whole study and compares it with the committed reports, the integration tests that need a local server or a database, and the opt-in live tests that call a real model. `pytest.md` explains the tool; this note reads each test.

## Why this repository uses it

The tests are the proof that the numbers in the README are not accidents. Each test states one fact and fails if the code stops making it true.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `tests/__init__.py` | Quoted and explained in the walkthrough below. |
| `tests/e2e/__init__.py` | Quoted and explained in the walkthrough below. |
| `tests/e2e/test_replay_reproduces_committed_reports.py` | Quoted and explained in the walkthrough below. |
| `tests/live/__init__.py` | Quoted and explained in the walkthrough below. |
| `tests/live/test_live_models.py` | Quoted and explained in the walkthrough below. |
| `tests/unit/__init__.py` | Quoted and explained in the walkthrough below. |
| `tests/unit/application/__init__.py` | Quoted and explained in the walkthrough below. |
| `tests/unit/application/test_router_and_experiments.py` | Quoted and explained in the walkthrough below. |
| `tests/unit/domain/__init__.py` | Quoted and explained in the walkthrough below. |
| `tests/unit/domain/test_domain.py` | Quoted and explained in the walkthrough below. |
| `tests/unit/domain/test_llm_and_stats.py` | Quoted and explained in the walkthrough below. |
| `tests/unit/fakes.py` | Quoted and explained in the walkthrough below. |
| `... 5 more files` | All files are listed in the first table of the walkthrough. |


## How it works underneath

pytest finds the files `test_*.py` and runs every function named `test_*`. A test builds some input (often with a small fake instead of a model), calls the code, and uses `assert` to state what must hold. Helpers shared between tests live in `fakes.py` or `conftest.py`. Markers (`integration`, `e2e`, `live`) select groups of tests (`pytest.md`).

## Walkthrough of this repository's use

### Files in this note

| File | Lines | What it is |
| --- | --- | --- |
| `tests/__init__.py` | 0 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/e2e/__init__.py` | 0 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/e2e/test_replay_reproduces_committed_reports.py` | 26 | Replaying the recorded fixtures regenerates exactly the committed configuration and reports (no model, no network). |
| `tests/live/__init__.py` | 0 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/live/test_live_models.py` | 34 | Opt-in tests against real models. |
| `tests/unit/__init__.py` | 0 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/unit/application/__init__.py` | 0 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/unit/application/test_router_and_experiments.py` | 304 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/unit/domain/__init__.py` | 0 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/unit/domain/test_domain.py` | 158 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/unit/domain/test_llm_and_stats.py` | 90 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/unit/fakes.py` | 72 | Small fakes shared by the unit tests. |
| `tests/unit/infrastructure/__init__.py` | 0 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/unit/infrastructure/test_llm_adapters.py` | 185 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/unit/infrastructure/test_support_modules.py` | 133 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/unit/interfaces/__init__.py` | 0 | (no module docstring; the file is tiny or only re-exports names) |
| `tests/unit/interfaces/test_cli.py` | 86 | (no module docstring; the file is tiny or only re-exports names) |

Each file below is quoted exactly, in order, in pieces of about a dozen lines. Under each piece, a bullet list explains every statement in the order it appears. The first time an idea shows up in this note it is explained in a bullet that begins **New idea**.

#### `tests/__init__.py`

This file is empty. It exists so that Python treats the folder as a package.

#### `tests/e2e/__init__.py`

This file is empty. It exists so that Python treats the folder as a package.

#### `tests/e2e/test_replay_reproduces_committed_reports.py`

<!-- fmt: off -->
```python
"""Replaying the recorded fixtures regenerates exactly the committed configuration and reports (no model, no network)."""

import json
from pathlib import Path

import pytest

from cost_router.interfaces import cli

pytestmark = pytest.mark.e2e

ROOT = Path(__file__).resolve().parents[2]
```
<!-- fmt: on -->

- **New idea.** A **docstring** is a text in triple quotes as the first statement of a module, class or function. Python keeps it as documentation and tools can show it.
- `"""Replaying the recorded fixtures regenerates exactly the committed configuration and ...`: a docstring (documentation text). It says: "Replaying the recorded fixtures regenerates exactly the committed configuration and reports (no model, no network)."
- **New idea.** An **import** makes the code of another module available. `import x` gives the whole module under the name `x`; `from x import y` gives just the name `y`.
- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `import pytest`: imports the module(s) `pytest` so this file can use them. `pytest` is the test framework (`pytest.md`).
- `from cost_router.interfaces import cli`: takes the name(s) `cli` from the module `cost_router.interfaces` (a module of this project).
- **New idea.** An **assignment** `name = value` makes the name point at the value. A name written in capital letters is, by convention, a constant: it is not meant to change.
- `pytestmark = pytest.mark.e2e`: sets `pytestmark` to the value of `pytest.mark.e2e`.
- `ROOT = Path(__file__).resolve().parents[2]`: sets `ROOT` to the value of `Path(__file__).resolve().parents[2]`. `Path(__file__).resolve()` is the absolute form of the path `Path(__file__)`; `Path(__file__)` is the file path `__file__`.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- **New idea.** A **function** is a named block of code. `def name(a, b):` defines it; the indented lines are its body. Calling `name(1, 2)` runs the body with `a = 1` and `b = 2`. `return` hands a value back. A parameter written `b=3` has a **default**: it may be left out when calling.
- **New idea.** A function whose name starts with `test_` is found and run by pytest (`pytest.md`). It passes if it finishes without an error.
- `def test_the_whole_study_replays_to_the_committed_reports(tmp_path: Path, monkeypatch):`: defines the test `test_the_whole_study_replays_to_the_committed_reports` taking tmp_path (Path); monkeypatch.
- `env = {`: sets `env` to a dictionary with 3 entries. `str(tmp_path)` is `tmp_path` converted to text; `str(tmp_path / 'config' / 'router.json')` is `tmp_path / 'config' / 'router.json'` converted to text.
- `monkeypatch.setattr(cli, "process_env", lambda: env)`: runs `monkeypatch.setattr(cli, 'process_env', lambda: env)` for its effect and ignores the result. `lambda: env` is a small unnamed function of no arguments that gives `env`.
- **New idea.** `assert condition, message` checks that the condition is true and raises `AssertionError` with the message if it is not. Tests use it to state what must hold.
- `assert cli.main(["all"]) == 0`: checks that `cli.main(['all']) == 0` is true; if it is not, the test (or program) fails here.
- **New idea.** A **for loop** `for x in items:` runs its block once for each item, with `x` naming the current item. `break` leaves the loop early; `continue` skips to the next item.
- `for name in ("models.json", "checks.json", "router.json", "day.json", "audit.json"):`: repeats the block below once for each `name` in `('models.json', 'checks.json', 'router.json', 'day.json', 'audit.js...`.
- `assert json.loads((tmp_path / name).read_text()) == json.loads((ROOT / "reports" / name...`: checks that `json.loads((tmp_path / name).read_text()) == json.loads((ROOT / 'reports' / n...` is true, with the message `name`; if it is not, the test (or program) fails here. `json.loads((tmp_path / name).read_text())` is the JSON text `(tmp_path / name).read_text()` turned into Python values; `json.loads((ROOT / 'reports' / name).read_text())` is the JSON text `(ROOT / 'reports' / name).read_text()` turned into Python values; `(tmp_path / name).read_text()` is the whole text of the file `tmp_path / name`.
- `assert (tmp_path / "REPORT.md").read_text() == (ROOT / "reports" / "REPORT.md").read_te...`: checks that `(tmp_path / 'REPORT.md').read_text() == (ROOT / 'reports' / 'REPORT.md').read...` is true; if it is not, the test (or program) fails here. `(tmp_path / 'REPORT.md').read_text()` is the whole text of the file `tmp_path / 'REPORT.md'`; `(ROOT / 'reports' / 'REPORT.md').read_text()` is the whole text of the file `ROOT / 'reports' / 'REPORT.md'`.
- `assert (tmp_path / "config" / "router.json").read_text() == (ROOT / "config" / "router....`: checks that `(tmp_path / 'config' / 'router.json').read_text() == (ROOT / 'config' / 'rout...` is true; if it is not, the test (or program) fails here. `(tmp_path / 'config' / 'router.json').read_text()` is the whole text of the file `tmp_path / 'config' / 'router.json'`; `(ROOT / 'config' / 'router.json').read_text()` is the whole text of the file `ROOT / 'config' / 'router.json'`.

#### `tests/live/__init__.py`

This file is empty. It exists so that Python treats the folder as a package.

#### `tests/live/test_live_models.py`

<!-- fmt: off -->
```python
"""Opt-in tests against real models. Skipped unless RUN_LIVE=1 (`make test-live`) and, for a hosted model, its key
is in the environment. They are never part of `make test` or CI."""

import os

import pytest

from cost_router.domain.llm import ChatRequest, Message
from cost_router.infrastructure.llm.anthropic import AnthropicChatModel
from cost_router.infrastructure.llm.openai_compat import OpenAICompatibleChatModel

pytestmark = pytest.mark.live

requires_live = pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="set RUN_LIVE=1 (make test-live)")
```
<!-- fmt: on -->

- `"""Opt-in tests against real models. Skipped unless RUN_LIVE=1 ('make test-live') and, ...`: a docstring (documentation text). It says: "Opt-in tests against real models."
- `import os`: imports the module(s) `os` so this file can use them. `os` is operating-system services such as environment variables and paths.
- `import pytest`: imports the module(s) `pytest` so this file can use them. `pytest` is the test framework (`pytest.md`).
- `from cost_router.domain.llm import ChatRequest, Message`: takes the name(s) `ChatRequest, Message` from the module `cost_router.domain.llm` (a module of this project).
- `from cost_router.infrastructure.llm.anthropic import AnthropicChatModel`: takes the name(s) `AnthropicChatModel` from the module `cost_router.infrastructure.llm.anthropic` (a module of this project).
- `from cost_router.infrastructure.llm.openai_compat import OpenAICompatibleChatModel`: takes the name(s) `OpenAICompatibleChatModel` from the module `cost_router.infrastructure.llm.openai_compat` (a module of this project).
- `pytestmark = pytest.mark.live`: sets `pytestmark` to the value of `pytest.mark.live`.
- `requires_live = pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="set RUN_L...`: sets `requires_live` to the value of `pytest.mark.skipif(os.environ.get('RUN_LIVE') != '1', reason='set RUN_LIVE=1 ...`. `pytest.mark.skipif(os.environ.get('RUN_LIVE') != '1', reason='set R...` skips the test when the condition holds; `os.environ.get('RUN_LIVE')` is the environment variable `'RUN_LIVE'` (default (nothing)).

<!-- fmt: off -->
```python
@requires_live
def test_a_local_openai_compatible_server_answers():
    base = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
    model = os.environ.get("LIVE_LOCAL_MODEL", "qwen2.5:0.5b")
    reply = OpenAICompatibleChatModel(base).complete(
        ChatRequest(model, (Message("user", "Reply with the single word: ready"),), max_tokens=16), timeout_s=120
    )
    assert reply.text.strip() and reply.usage.output_tokens > 0


@requires_live
@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY is not set")
def test_claude_answers():
    model = os.environ.get("LIVE_CLAUDE_MODEL", "claude-haiku-5-5")
```
<!-- fmt: on -->

- **New idea.** A **decorator** is a line `@name` above a function or class. It passes the function to `name` and uses what comes back instead. It is a way to add behaviour without editing the function.
- `def test_a_local_openai_compatible_server_answers():`: defines the test `test_a_local_openai_compatible_server_answers` taking no arguments. Decorators: `requires_live`.
- `base = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")`: sets `base` to the value of `os.environ.get('LLM_BASE_URL', 'http://localhost:11434/v1')`. `os.environ.get('LLM_BASE_URL', 'http://localhost:11434/v1')` is the environment variable `'LLM_BASE_URL'` (default `'http://localhost:11434/v1'`).
- `model = os.environ.get("LIVE_LOCAL_MODEL", "qwen2.5:0.5b")`: sets `model` to the value of `os.environ.get('LIVE_LOCAL_MODEL', 'qwen2.5:0.5b')`. `os.environ.get('LIVE_LOCAL_MODEL', 'qwen2.5:0.5b')` is the environment variable `'LIVE_LOCAL_MODEL'` (default `'qwen2.5:0.5b'`).
- `reply = OpenAICompatibleChatModel(base).complete(`: sets `reply` to the value of `OpenAICompatibleChatModel(base).complete(ChatRequest(model, (Message('user', ...`.
- `assert reply.text.strip() and reply.usage.output_tokens > 0`: checks that `reply.text.strip() and reply.usage.output_tokens > 0` is true; if it is not, the test (or program) fails here. `reply.text.strip()` is `reply.text` without white space at both ends.
- `def test_claude_answers():`: defines the test `test_claude_answers` taking no arguments. Decorators: `requires_live`; `pytest.mark.skipif(not os.environ.get('ANTHROPIC_API_KEY'), reason=...`.
- `model = os.environ.get("LIVE_CLAUDE_MODEL", "claude-haiku-5-5")`: sets `model` to the value of `os.environ.get('LIVE_CLAUDE_MODEL', 'claude-haiku-5-5')`. `os.environ.get('LIVE_CLAUDE_MODEL', 'claude-haiku-5-5')` is the environment variable `'LIVE_CLAUDE_MODEL'` (default `'claude-haiku-5-5'`).

<!-- fmt: off -->
```python
    reply = AnthropicChatModel(os.environ["ANTHROPIC_API_KEY"]).complete(
        ChatRequest(model, (Message("user", "Reply with the single word: ready"),), max_tokens=16)
    )
    assert reply.text.strip() and reply.usage.input_tokens > 0
```
<!-- fmt: on -->

- `reply = AnthropicChatModel(os.environ["ANTHROPIC_API_KEY"]).complete(`: sets `reply` to the value of `AnthropicChatModel(os.environ['ANTHROPIC_API_KEY']).complete(ChatRequest(mode...`.
- `assert reply.text.strip() and reply.usage.input_tokens > 0`: checks that `reply.text.strip() and reply.usage.input_tokens > 0` is true; if it is not, the test (or program) fails here. `reply.text.strip()` is `reply.text` without white space at both ends.

#### `tests/unit/__init__.py`

This file is empty. It exists so that Python treats the folder as a package.

#### `tests/unit/application/__init__.py`

This file is empty. It exists so that Python treats the folder as a package.

#### `tests/unit/application/test_router_and_experiments.py`

<!-- fmt: off -->
```python
import pytest

from cost_router.application.answer_checks import AnswerChecks
from cost_router.application.experiments import (
    cheapest_matching,
    check_results,
    collect_answers,
    compare_to_large,
    false_accepts,
    harden,
    make_checks,
    measure_models,
    route_all,
    run_day,
    single_model_summary,
    summarize,
    tune,
    weakest_kind,
)
```
<!-- fmt: on -->

- `import pytest`: imports the module(s) `pytest` so this file can use them. `pytest` is the test framework (`pytest.md`).
- `from cost_router.application.answer_checks import AnswerChecks`: takes the name(s) `AnswerChecks` from the module `cost_router.application.answer_checks` (a module of this project).
- `from cost_router.application.experiments import (`: takes the name(s) `cheapest_matching, check_results, collect_answers, compare_to_large, false_accepts, harden, make_checks, measure_models, route_all, run_day, single_model_summary, summarize, tune, weakest_kind` from the module `cost_router.application.experiments` (a module of this project).

<!-- fmt: off -->
```python
from cost_router.application.router import ESCALATE, CostRouter
from cost_router.domain.checks import is_correct
from cost_router.domain.llm import ChatRequest
from cost_router.domain.pricing import TIERS
from cost_router.domain.routing import Bar, DayBudget
from cost_router.domain.tasks import POLICY_LINES, Kind, Task
from tests.unit.fakes import config, label_task, policy_task, refund_task, sequential, tiers_for

BAR = Bar(0.10, 0.5, 0.02, 0.01, 0.8, (0.5,))
RIGHT_QUOTE = f'Answer: yes\nQuote: "{POLICY_LINES[0]}"'


def by_tier(table):
    """An answer function: look up the reply by the model id in the request."""
```
<!-- fmt: on -->

- `from cost_router.application.router import ESCALATE, CostRouter`: takes the name(s) `ESCALATE, CostRouter` from the module `cost_router.application.router` (a module of this project).
- `from cost_router.domain.checks import is_correct`: takes the name(s) `is_correct` from the module `cost_router.domain.checks` (a module of this project).
- `from cost_router.domain.llm import ChatRequest`: takes the name(s) `ChatRequest` from the module `cost_router.domain.llm` (a module of this project).
- `from cost_router.domain.pricing import TIERS`: takes the name(s) `TIERS` from the module `cost_router.domain.pricing` (a module of this project).
- `from cost_router.domain.routing import Bar, DayBudget`: takes the name(s) `Bar, DayBudget` from the module `cost_router.domain.routing` (a module of this project).
- `from cost_router.domain.tasks import POLICY_LINES, Kind, Task`: takes the name(s) `POLICY_LINES, Kind, Task` from the module `cost_router.domain.tasks` (a module of this project).
- `from tests.unit.fakes import config, label_task, policy_task, refund_task, sequential, ...`: takes the name(s) `config, label_task, policy_task, refund_task, sequential, tiers_for` from the module `tests.unit.fakes` (a module of this project).
- `BAR = Bar(0.10, 0.5, 0.02, 0.01, 0.8, (0.5,))`: sets `BAR` to the value of `Bar(0.1, 0.5, 0.02, 0.01, 0.8, (0.5,))`.
- `RIGHT_QUOTE = f'Answer: yes\nQuote: "{POLICY_LINES[0]}"'`: sets `RIGHT_QUOTE` to the value of `f'Answer: yes\nQuote: "{POLICY_LINES[0]}"'`. the f-string inserts `POLICY_LINES[0]` into the text.
- `def by_tier(table):`: defines the function `by_tier` taking table. Purpose: An answer function: look up the reply by the model id in the request.
- `"""An answer function: look up the reply by the model id in the request."""`: a docstring (documentation text). It says: "An answer function: look up the reply by the model id in the request."

<!-- fmt: off -->
```python
    def answer(request: ChatRequest) -> str:
        reply = table[request.model]
        return str(reply(request)) if callable(reply) else str(reply)

    return answer


def test_tiers_build_prompts_by_kind_and_cost_calls_from_billed_tokens():
    tiers, model = tiers_for(lambda r: " billing ")
    answered = tiers.call("small", label_task())
    assert answered.text == "billing" and answered.tokens == 110
    assert answered.cost == pytest.approx(110 / 1000 * 0.0002)
    assert "LABEL I was charged twice." in tiers.prompt(label_task())
    assert "REFUND" in tiers.prompt(refund_task()) and "1. Returns are accepted" in tiers.prompt(policy_task())
```
<!-- fmt: on -->

- **New idea.** A function defined inside another function is a **closure**: it can read the variables of the function around it, even after that function has returned.
- `def answer(request: ChatRequest) -> str:`: defines the function `answer` taking request (ChatRequest) and returns `str`.
- `reply = table[request.model]`: sets `reply` to the value of `table[request.model]`.
- **New idea.** `return value` ends the function and hands the value to the caller. A function that reaches its end without `return` gives back `None` (nothing).
- `return str(reply(request)) if callable(reply) else str(reply)`: ends the function and hands back `str(reply(request)) if callable(reply) else str(reply)`. `str(reply(request)) if callable(reply) else str(reply)` gives `str(reply(request))` when `callable(reply)` is true, otherwise `str(reply)`; `callable(reply)` is whether `reply` can be called; `str(reply(request))` is `reply(request)` converted to text.
- `return answer`: ends the function and hands back `answer`.
- `def test_tiers_build_prompts_by_kind_and_cost_calls_from_billed_tokens():`: defines the test `test_tiers_build_prompts_by_kind_and_cost_calls_from_billed_tokens` taking no arguments.
- `tiers, model = tiers_for(lambda r: " billing ")`: sets `(tiers, model)` to the value of `tiers_for(lambda r: ' billing ')`. `lambda r: ' billing '` is a small unnamed function of `r` that gives `' billing '`.
- `answered = tiers.call("small", label_task())`: sets `answered` to the value of `tiers.call('small', label_task())`.
- `assert answered.text == "billing" and answered.tokens == 110`: checks that `answered.text == 'billing' and answered.tokens == 110` is true; if it is not, the test (or program) fails here.
- `assert answered.cost == pytest.approx(110 / 1000 * 0.0002)`: checks that `answered.cost == pytest.approx(110 / 1000 * 0.0002)` is true; if it is not, the test (or program) fails here. `pytest.approx(110 / 1000 * 0.0002)` is `110 / 1000 * 0.0002` compared with a small tolerance.
- `assert "LABEL I was charged twice." in tiers.prompt(label_task())`: checks that `'LABEL I was charged twice.' in tiers.prompt(label_task())` is true; if it is not, the test (or program) fails here.
- `assert "REFUND" in tiers.prompt(refund_task()) and "1. Returns are accepted" in tiers.p...`: checks that `'REFUND' in tiers.prompt(refund_task()) and '1. Returns are accepted' in tier...` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
    tiers.call("small", label_task(), second_sample=True)
    first, second = model.requests
    assert (first.temperature, first.seed) == (0.0, None) and (second.temperature, second.seed) == (0.8, 7)
    assert tiers.estimate("large", label_task(), calls=2) > tiers.estimate("small", label_task())


def test_label_agreement_costs_a_second_sample_and_shape_does_not():
    tiers, model = tiers_for(lambda r: "billing")
    agreement = AnswerChecks(tiers, "agreement").check(label_task(), "small", "billing")
    assert agreement.passed and agreement.extra_cost > 0 and agreement.extra_tokens == 110
    assert len(model.requests) == 1
    shape = AnswerChecks(tiers, "shape").check(label_task(), "small", "billing")
    assert shape.passed and shape.extra_cost == 0 and len(model.requests) == 1
    assert AnswerChecks(tiers, "agreement").estimate_extra(label_task(), "small") > 0
```
<!-- fmt: on -->

- `tiers.call("small", label_task(), second_sample=True)`: runs `tiers.call('small', label_task(), second_sample=True)` for its effect and ignores the result.
- `first, second = model.requests`: sets `(first, second)` to the value of `model.requests`.
- `assert (first.temperature, first.seed) == (0.0, None) and (second.temperature, second.s...`: checks that `(first.temperature, first.seed) == (0.0, None) and (second.temperature, secon...` is true; if it is not, the test (or program) fails here.
- `assert tiers.estimate("large", label_task(), calls=2) > tiers.estimate("small", label_t...`: checks that `tiers.estimate('large', label_task(), calls=2) > tiers.estimate('small', labe...` is true; if it is not, the test (or program) fails here.
- `def test_label_agreement_costs_a_second_sample_and_shape_does_not():`: defines the test `test_label_agreement_costs_a_second_sample_and_shape_does_not` taking no arguments.
- `tiers, model = tiers_for(lambda r: "billing")`: sets `(tiers, model)` to the value of `tiers_for(lambda r: 'billing')`. `lambda r: 'billing'` is a small unnamed function of `r` that gives `'billing'`.
- `agreement = AnswerChecks(tiers, "agreement").check(label_task(), "small", "billing")`: sets `agreement` to the value of `AnswerChecks(tiers, 'agreement').check(label_task(), 'small', 'billing')`.
- `assert agreement.passed and agreement.extra_cost > 0 and agreement.extra_tokens == 110`: checks that `agreement.passed and agreement.extra_cost > 0 and (agreement.extra_tokens == ...` is true; if it is not, the test (or program) fails here.
- `assert len(model.requests) == 1`: checks that `len(model.requests) == 1` is true; if it is not, the test (or program) fails here. `len(model.requests)` is the number of items in `model.requests`.
- `shape = AnswerChecks(tiers, "shape").check(label_task(), "small", "billing")`: sets `shape` to the value of `AnswerChecks(tiers, 'shape').check(label_task(), 'small', 'billing')`.
- `assert shape.passed and shape.extra_cost == 0 and len(model.requests) == 1`: checks that `shape.passed and shape.extra_cost == 0 and (len(model.requests) == 1)` is true; if it is not, the test (or program) fails here. `len(model.requests)` is the number of items in `model.requests`.
- `assert AnswerChecks(tiers, "agreement").estimate_extra(label_task(), "small") > 0`: checks that `AnswerChecks(tiers, 'agreement').estimate_extra(label_task(), 'small') > 0` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
    assert AnswerChecks(tiers, "shape").estimate_extra(label_task(), "small") == 0
    assert AnswerChecks(tiers).estimate_extra(refund_task(), "small") == 0
    assert AnswerChecks(tiers).check(refund_task(days=20, total=5000), "small", "40.00").passed
    assert not AnswerChecks(tiers).check(policy_task(), "small", "Answer: 2.").passed


def make_router(answer, cfg=None, realistic_usage=False):
    tiers, model = tiers_for(answer, realistic_usage)
    cfg = cfg or config()
    return CostRouter(tiers, AnswerChecks(tiers, cfg.label_check), cfg), model


def test_the_router_stops_at_the_first_accepted_answer():
    router, model = make_router(lambda r: "40.00")
```
<!-- fmt: on -->

- `assert AnswerChecks(tiers, "shape").estimate_extra(label_task(), "small") == 0`: checks that `AnswerChecks(tiers, 'shape').estimate_extra(label_task(), 'small') == 0` is true; if it is not, the test (or program) fails here.
- `assert AnswerChecks(tiers).estimate_extra(refund_task(), "small") == 0`: checks that `AnswerChecks(tiers).estimate_extra(refund_task(), 'small') == 0` is true; if it is not, the test (or program) fails here.
- `assert AnswerChecks(tiers).check(refund_task(days=20, total=5000), "small", "40.00").pa...`: checks that `AnswerChecks(tiers).check(refund_task(days=20, total=5000), 'small', '40.00')...` is true; if it is not, the test (or program) fails here.
- `assert not AnswerChecks(tiers).check(policy_task(), "small", "Answer: 2.").passed`: checks that `not AnswerChecks(tiers).check(policy_task(), 'small', 'Answer: 2.').passed` is true; if it is not, the test (or program) fails here.
- `def make_router(answer, cfg=None, realistic_usage=False):`: defines the function `make_router` taking answer; cfg, default None; realistic_usage, default False.
- `tiers, model = tiers_for(answer, realistic_usage)`: sets `(tiers, model)` to the value of `tiers_for(answer, realistic_usage)`.
- `cfg = cfg or config()`: sets `cfg` to the value of `cfg or config()`.
- `return CostRouter(tiers, AnswerChecks(tiers, cfg.label_check), cfg), model`: ends the function and hands back `(CostRouter(tiers, AnswerChecks(tiers, cfg.label_check), cfg), model)`.
- `def test_the_router_stops_at_the_first_accepted_answer():`: defines the test `test_the_router_stops_at_the_first_accepted_answer` taking no arguments.
- `router, model = make_router(lambda r: "40.00")`: sets `(router, model)` to the value of `make_router(lambda r: '40.00')`. `lambda r: '40.00'` is a small unnamed function of `r` that gives `'40.00'`.

<!-- fmt: off -->
```python
    decision = router.route(refund_task(days=20, total=5000))
    assert decision.served_by == "small" and decision.answer == "40.00"
    assert len(decision.attempts) == 1 and len(model.requests) == 1


def test_a_failed_check_escalates_to_the_next_tier():
    router, _ = make_router(by_tier({"m-small": "99.00", "m-medium": "40.00", "m-large": "40.00"}))
    decision = router.route(refund_task(days=20, total=5000))
    assert decision.served_by == "medium"
    assert [(a.tier, a.passed) for a in decision.attempts] == [("small", False), ("medium", True)]
    assert decision.spent == pytest.approx(sum(a.cost for a in decision.attempts))


def test_when_every_check_fails_a_person_gets_the_task():
```
<!-- fmt: on -->

- `decision = router.route(refund_task(days=20, total=5000))`: sets `decision` to the value of `router.route(refund_task(days=20, total=5000))`.
- `assert decision.served_by == "small" and decision.answer == "40.00"`: checks that `decision.served_by == 'small' and decision.answer == '40.00'` is true; if it is not, the test (or program) fails here.
- `assert len(decision.attempts) == 1 and len(model.requests) == 1`: checks that `len(decision.attempts) == 1 and len(model.requests) == 1` is true; if it is not, the test (or program) fails here. `len(decision.attempts)` is the number of items in `decision.attempts`; `len(model.requests)` is the number of items in `model.requests`.
- `def test_a_failed_check_escalates_to_the_next_tier():`: defines the test `test_a_failed_check_escalates_to_the_next_tier` taking no arguments.
- `router, _ = make_router(by_tier({"m-small": "99.00", "m-medium": "40.00", "m-large": "4...`: sets `(router, _)` to the value of `make_router(by_tier({'m-small': '99.00', 'm-medium': '40.00', 'm-large': '40....`.
- `decision = router.route(refund_task(days=20, total=5000))`: sets `decision` to the value of `router.route(refund_task(days=20, total=5000))`.
- `assert decision.served_by == "medium"`: checks that `decision.served_by == 'medium'` is true; if it is not, the test (or program) fails here.
- `assert [(a.tier, a.passed) for a in decision.attempts] == [("small", False), ("medium",...`: checks that `[(a.tier, a.passed) for a in decision.attempts] == [('small', False), ('mediu...` is true; if it is not, the test (or program) fails here. `[(a.tier, a.passed) for a in decision.attempts]` builds a list: for each `a` in `decision.attempts`.
- `assert decision.spent == pytest.approx(sum(a.cost for a in decision.attempts))`: checks that `decision.spent == pytest.approx(sum((a.cost for a in decision.attempts)))` is true; if it is not, the test (or program) fails here. `pytest.approx(sum((a.cost for a in decision.attempts)))` is `sum((a.cost for a in decision.attempts))` compared with a small tolerance; `sum((a.cost for a in decision.attempts))` is the sum of `(a.cost for a in decision.attempts)`; `(a.cost for a in decision.attempts)` builds a generator of values: for each `a` in `decision.attempts`.
- `def test_when_every_check_fails_a_person_gets_the_task():`: defines the test `test_when_every_check_fails_a_person_gets_the_task` taking no arguments.

<!-- fmt: off -->
```python
    router, _ = make_router(lambda r: "99.00")
    decision = router.route(refund_task())
    assert decision.served_by == ESCALATE and decision.answer is None and len(decision.attempts) == 3


def test_the_start_tier_and_the_hard_signal_skip_cheap_tiers():
    cfg = config(start={"label": "medium", "refund": "small", "policy": "small"}, hard={"refund": "large"})
    router, model = make_router(lambda r: "40.00", cfg)
    router.route(refund_task(days=20, total=5000))
    assert model.requests[0].model == "m-small"
    hard = refund_task(days=20, total=5000)
    damaged = type(hard)(
        hard.task_id, hard.kind, hard.difficulty, hard.split, hard.text + " It was damaged.", 0, hard.orders
    )
```
<!-- fmt: on -->

- `router, _ = make_router(lambda r: "99.00")`: sets `(router, _)` to the value of `make_router(lambda r: '99.00')`. `lambda r: '99.00'` is a small unnamed function of `r` that gives `'99.00'`.
- `decision = router.route(refund_task())`: sets `decision` to the value of `router.route(refund_task())`.
- `assert decision.served_by == ESCALATE and decision.answer is None and len(decision.atte...`: checks that `decision.served_by == ESCALATE and decision.answer is None and (len(decision....` is true; if it is not, the test (or program) fails here. `decision.answer is None` tests that there is nothing (`None`) in `decision.answer`; `len(decision.attempts)` is the number of items in `decision.attempts`.
- `def test_the_start_tier_and_the_hard_signal_skip_cheap_tiers():`: defines the test `test_the_start_tier_and_the_hard_signal_skip_cheap_tiers` taking no arguments.
- `cfg = config(start={"label": "medium", "refund": "small", "policy": "small"}, hard={"re...`: sets `cfg` to the value of `config(start={'label': 'medium', 'refund': 'small', 'policy': 'small'}, hard=...`.
- `router, model = make_router(lambda r: "40.00", cfg)`: sets `(router, model)` to the value of `make_router(lambda r: '40.00', cfg)`. `lambda r: '40.00'` is a small unnamed function of `r` that gives `'40.00'`.
- `router.route(refund_task(days=20, total=5000))`: runs `router.route(refund_task(days=20, total=5000))` for its effect and ignores the result.
- `assert model.requests[0].model == "m-small"`: checks that `model.requests[0].model == 'm-small'` is true; if it is not, the test (or program) fails here.
- `hard = refund_task(days=20, total=5000)`: sets `hard` to the value of `refund_task(days=20, total=5000)`.
- `damaged = type(hard)(`: sets `damaged` to the value of `type(hard)(hard.task_id, hard.kind, hard.difficulty, hard.split, hard.text + ...`. `type(hard)` is the type of `hard`.

<!-- fmt: off -->
```python
    router.route(damaged)
    assert model.requests[1].model == "m-large"


def test_the_request_cap_is_checked_before_a_call_and_stops_the_cascade():
    router, model = make_router(lambda r: "99.00", config(cap=0.00001), realistic_usage=True)
    decision = router.route(refund_task())
    assert decision.served_by == ESCALATE and "cap" in decision.tags and model.requests == []
    one_call = tiers_for(lambda r: "x")[0].estimate("small", refund_task())
    tight, called = make_router(lambda r: "99.00", config(cap=one_call * 1.5), realistic_usage=True)
    result = tight.route(refund_task())
    assert len(called.requests) == 1 and "cap" in result.tags and result.spent <= one_call * 1.5
```
<!-- fmt: on -->

- `router.route(damaged)`: runs `router.route(damaged)` for its effect and ignores the result.
- `assert model.requests[1].model == "m-large"`: checks that `model.requests[1].model == 'm-large'` is true; if it is not, the test (or program) fails here.
- `def test_the_request_cap_is_checked_before_a_call_and_stops_the_cascade():`: defines the test `test_the_request_cap_is_checked_before_a_call_and_stops_the_cascade` taking no arguments.
- `router, model = make_router(lambda r: "99.00", config(cap=0.00001), realistic_usage=True)`: sets `(router, model)` to the value of `make_router(lambda r: '99.00', config(cap=1e-05), realistic_usage=True)`. `lambda r: '99.00'` is a small unnamed function of `r` that gives `'99.00'`.
- `decision = router.route(refund_task())`: sets `decision` to the value of `router.route(refund_task())`.
- `assert decision.served_by == ESCALATE and "cap" in decision.tags and model.requests == []`: checks that `decision.served_by == ESCALATE and 'cap' in decision.tags and (model.requests...` is true; if it is not, the test (or program) fails here.
- `one_call = tiers_for(lambda r: "x")[0].estimate("small", refund_task())`: sets `one_call` to the value of `tiers_for(lambda r: 'x')[0].estimate('small', refund_task())`. `lambda r: 'x'` is a small unnamed function of `r` that gives `'x'`.
- `tight, called = make_router(lambda r: "99.00", config(cap=one_call * 1.5), realistic_us...`: sets `(tight, called)` to the value of `make_router(lambda r: '99.00', config(cap=one_call * 1.5), realistic_usage=True)`. `lambda r: '99.00'` is a small unnamed function of `r` that gives `'99.00'`.
- `result = tight.route(refund_task())`: sets `result` to the value of `tight.route(refund_task())`.
- `assert len(called.requests) == 1 and "cap" in result.tags and result.spent <= one_call ...`: checks that `len(called.requests) == 1 and 'cap' in result.tags and (result.spent <= one_c...` is true; if it is not, the test (or program) fails here. `len(called.requests)` is the number of items in `called.requests`.

<!-- fmt: off -->
```python
def test_late_in_the_day_the_largest_tier_is_not_offered_but_the_router_keeps_answering():
    router, model = make_router(by_tier({"m-small": "99.00", "m-medium": "99.00", "m-large": "40.00"}))
    day = DayBudget(1.0)
    day.add(0.85)
    decision = router.route(refund_task(days=20, total=5000), day)
    assert decision.served_by == ESCALATE and {r.model for r in model.requests} == {"m-small", "m-medium"}
    assert day.used > 0.85 and decision.share_before == pytest.approx(0.85)
    early, _ = make_router(by_tier({"m-small": "99.00", "m-medium": "99.00", "m-large": "40.00"}))
    assert early.route(refund_task(days=20, total=5000), DayBudget(1.0)).served_by == "large"
    assert router.config.tighten_at == 0.8


def test_the_day_budget_limits_what_a_request_may_spend_and_hands_the_rest_to_a_person():
    router, _ = make_router(lambda r: "99.00", config(cap=1.0), realistic_usage=True)
```
<!-- fmt: on -->

- `def test_late_in_the_day_the_largest_tier_is_not_offered_but_the_router_keeps_answering():`: defines the test `test_late_in_the_day_the_largest_tier_is_not_offered_but_the_router_keeps_answering` taking no arguments.
- `router, model = make_router(by_tier({"m-small": "99.00", "m-medium": "99.00", "m-large"...`: sets `(router, model)` to the value of `make_router(by_tier({'m-small': '99.00', 'm-medium': '99.00', 'm-large': '40....`.
- `day = DayBudget(1.0)`: sets `day` to the value of `DayBudget(1.0)`.
- `day.add(0.85)`: runs `day.add(0.85)` for its effect and ignores the result. `day.add(0.85)` adds `0.85` to the set `day`.
- `decision = router.route(refund_task(days=20, total=5000), day)`: sets `decision` to the value of `router.route(refund_task(days=20, total=5000), day)`.
- `assert decision.served_by == ESCALATE and {r.model for r in model.requests} == {"m-smal...`: checks that `decision.served_by == ESCALATE and {r.model for r in model.requests} == {'m-s...` is true; if it is not, the test (or program) fails here. `{r.model for r in model.requests}` builds a set: for each `r` in `model.requests`.
- `assert day.used > 0.85 and decision.share_before == pytest.approx(0.85)`: checks that `day.used > 0.85 and decision.share_before == pytest.approx(0.85)` is true; if it is not, the test (or program) fails here. `pytest.approx(0.85)` is `0.85` compared with a small tolerance.
- `early, _ = make_router(by_tier({"m-small": "99.00", "m-medium": "99.00", "m-large": "40...`: sets `(early, _)` to the value of `make_router(by_tier({'m-small': '99.00', 'm-medium': '99.00', 'm-large': '40....`.
- `assert early.route(refund_task(days=20, total=5000), DayBudget(1.0)).served_by == "large"`: checks that `early.route(refund_task(days=20, total=5000), DayBudget(1.0)).served_by == 'l...` is true; if it is not, the test (or program) fails here.
- `assert router.config.tighten_at == 0.8`: checks that `router.config.tighten_at == 0.8` is true; if it is not, the test (or program) fails here.
- `def test_the_day_budget_limits_what_a_request_may_spend_and_hands_the_rest_to_a_person():`: defines the test `test_the_day_budget_limits_what_a_request_may_spend_and_hands_the_rest_to_a_person` taking no arguments.
- `router, _ = make_router(lambda r: "99.00", config(cap=1.0), realistic_usage=True)`: sets `(router, _)` to the value of `make_router(lambda r: '99.00', config(cap=1.0), realistic_usage=True)`. `lambda r: '99.00'` is a small unnamed function of `r` that gives `'99.00'`.

<!-- fmt: off -->
```python
    day = DayBudget(0.00005)
    first = router.route(refund_task(), day)
    assert first.tags == ("budget",) and day.used <= day.budget
    spent_after_first = day.used
    second = router.route(refund_task(), day)
    assert second.served_by == ESCALATE and day.used <= day.budget and day.used >= spent_after_first
    assert "budget" in second.tags


def corpus():
    return [
        label_task("t1", "billing", split="build"),
        refund_task("t2", split="build"),
        policy_task("t3", 0, split="build"),
    ]
```
<!-- fmt: on -->

- `day = DayBudget(0.00005)`: sets `day` to the value of `DayBudget(5e-05)`.
- `first = router.route(refund_task(), day)`: sets `first` to the value of `router.route(refund_task(), day)`.
- `assert first.tags == ("budget",) and day.used <= day.budget`: checks that `first.tags == ('budget',) and day.used <= day.budget` is true; if it is not, the test (or program) fails here.
- `spent_after_first = day.used`: sets `spent_after_first` to the value of `day.used`.
- `second = router.route(refund_task(), day)`: sets `second` to the value of `router.route(refund_task(), day)`.
- `assert second.served_by == ESCALATE and day.used <= day.budget and day.used >= spent_af...`: checks that `second.served_by == ESCALATE and day.used <= day.budget and (day.used >= spen...` is true; if it is not, the test (or program) fails here.
- `assert "budget" in second.tags`: checks that `'budget' in second.tags` is true; if it is not, the test (or program) fails here.
- `def corpus():`: defines the function `corpus` taking no arguments.
- `return [`: ends the function and hands back `[label_task('t1', 'billing', split='build'), refund_task('t2', split='build')...`.

<!-- fmt: off -->
```python
def answer_all(request: ChatRequest) -> str:
    text = request.messages[0].content
    if text.startswith("LABEL"):
        return "billing"
    if text.startswith("REFUND"):
        return "40.00"
    return RIGHT_QUOTE


def test_collect_and_measure_models_report_accuracy_and_cost_per_correct():
    tiers, _ = tiers_for(answer_all)
    tasks = corpus()
    answers = collect_answers(tasks, tiers, sequential)
    assert set(answers) == set(TIERS) and set(answers["small"]) == {"t1", "t2", "t3"}
```
<!-- fmt: on -->

- `def answer_all(request: ChatRequest) -> str:`: defines the function `answer_all` taking request (ChatRequest) and returns `str`.
- `text = request.messages[0].content`: sets `text` to the value of `request.messages[0].content`.
- **New idea.** An **if** statement runs its indented block only when the condition is true. `elif` adds another condition to try; `else` runs when none held.
- `if text.startswith("LABEL"):`: runs the block below only if `text.startswith('LABEL')` is true. `text.startswith('LABEL')` is whether `text` begins with `'LABEL'`.
- `return "billing"`: ends the function and hands back `'billing'`.
- `if text.startswith("REFUND"):`: runs the block below only if `text.startswith('REFUND')` is true. `text.startswith('REFUND')` is whether `text` begins with `'REFUND'`.
- `return "40.00"`: ends the function and hands back `'40.00'`.
- `return RIGHT_QUOTE`: ends the function and hands back `RIGHT_QUOTE`.
- `def test_collect_and_measure_models_report_accuracy_and_cost_per_correct():`: defines the test `test_collect_and_measure_models_report_accuracy_and_cost_per_correct` taking no arguments.
- `tiers, _ = tiers_for(answer_all)`: sets `(tiers, _)` to the value of `tiers_for(answer_all)`.
- `tasks = corpus()`: sets `tasks` to the value of `corpus()`.
- `answers = collect_answers(tasks, tiers, sequential)`: sets `answers` to the value of `collect_answers(tasks, tiers, sequential)`.
- `assert set(answers) == set(TIERS) and set(answers["small"]) == {"t1", "t2", "t3"}`: checks that `set(answers) == set(TIERS) and set(answers['small']) == {'t1', 't2', 't3'}` is true; if it is not, the test (or program) fails here. `set(answers)` is `answers` as a set (each value once); `set(TIERS)` is `TIERS` as a set (each value once); `set(answers['small'])` is `answers['small']` as a set (each value once).

<!-- fmt: off -->
```python
    table = measure_models(tasks, answers)
    assert table["small"]["label"].accuracy.value == 1.0
    assert table["large"]["refund"].cost_per_correct == pytest.approx(answers["large"]["t2"].cost)
    assert cheapest_matching(table, 0.02) == {"label": "small", "refund": "small", "policy": "small"}


def test_cheapest_matching_is_none_when_no_tier_reaches_the_large_one():
    tiers, _ = tiers_for(by_tier({"m-small": "x", "m-medium": "x", "m-large": "billing"}))
    tasks = [label_task("t1", "billing")]
    table = measure_models(tasks, collect_answers(tasks, tiers, sequential))
    assert cheapest_matching(table, 0.0)["label"] == "large"
    broken = measure_models(tasks, collect_answers(tasks, tiers_for(lambda r: "x")[0], sequential))
    assert cheapest_matching(broken, 0.0)["label"] == "small"
```
<!-- fmt: on -->

- `table = measure_models(tasks, answers)`: sets `table` to the value of `measure_models(tasks, answers)`.
- `assert table["small"]["label"].accuracy.value == 1.0`: checks that `table['small']['label'].accuracy.value == 1.0` is true; if it is not, the test (or program) fails here.
- `assert table["large"]["refund"].cost_per_correct == pytest.approx(answers["large"]["t2"...`: checks that `table['large']['refund'].cost_per_correct == pytest.approx(answers['large']['...` is true; if it is not, the test (or program) fails here. `pytest.approx(answers['large']['t2'].cost)` is `answers['large']['t2'].cost` compared with a small tolerance.
- `assert cheapest_matching(table, 0.02) == {"label": "small", "refund": "small", "policy"...`: checks that `cheapest_matching(table, 0.02) == {'label': 'small', 'refund': 'small', 'poli...` is true; if it is not, the test (or program) fails here.
- `def test_cheapest_matching_is_none_when_no_tier_reaches_the_large_one():`: defines the test `test_cheapest_matching_is_none_when_no_tier_reaches_the_large_one` taking no arguments.
- `tiers, _ = tiers_for(by_tier({"m-small": "x", "m-medium": "x", "m-large": "billing"}))`: sets `(tiers, _)` to the value of `tiers_for(by_tier({'m-small': 'x', 'm-medium': 'x', 'm-large': 'billing'}))`.
- `tasks = [label_task("t1", "billing")]`: sets `tasks` to a list of 1 item.
- `table = measure_models(tasks, collect_answers(tasks, tiers, sequential))`: sets `table` to the value of `measure_models(tasks, collect_answers(tasks, tiers, sequential))`.
- `assert cheapest_matching(table, 0.0)["label"] == "large"`: checks that `cheapest_matching(table, 0.0)['label'] == 'large'` is true; if it is not, the test (or program) fails here.
- `broken = measure_models(tasks, collect_answers(tasks, tiers_for(lambda r: "x")[0], sequ...`: sets `broken` to the value of `measure_models(tasks, collect_answers(tasks, tiers_for(lambda r: 'x')[0], seq...`. `lambda r: 'x'` is a small unnamed function of `r` that gives `'x'`.
- `assert cheapest_matching(broken, 0.0)["label"] == "small"`: checks that `cheapest_matching(broken, 0.0)['label'] == 'small'` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
def test_check_results_measure_false_accepts_and_the_tuner_moves_a_kind_up():
    def answer(request: ChatRequest) -> str:
        text = request.messages[0].content
        if text.startswith("LABEL"):
            return "returns" if request.model == "m-small" else "billing"
        if text.startswith("REFUND"):
            return "40.00"
        return f'Answer: x\nQuote: "{POLICY_LINES[1]}"' if request.model != "m-large" else RIGHT_QUOTE

    tiers, _ = tiers_for(answer)
    tasks = corpus()
    answers = collect_answers(tasks, tiers, sequential)
    rates = check_results(tasks, answers, tiers, sequential)
    assert rates["small"]["label"]["label_shape"].false_accept_rate == 1.0
```
<!-- fmt: on -->

- `def test_check_results_measure_false_accepts_and_the_tuner_moves_a_kind_up():`: defines the test `test_check_results_measure_false_accepts_and_the_tuner_moves_a_kind_up` taking no arguments.
- `def answer(request: ChatRequest) -> str:`: defines the function `answer` taking request (ChatRequest) and returns `str`.
- `text = request.messages[0].content`: sets `text` to the value of `request.messages[0].content`.
- `if text.startswith("LABEL"):`: runs the block below only if `text.startswith('LABEL')` is true. `text.startswith('LABEL')` is whether `text` begins with `'LABEL'`.
- `return "returns" if request.model == "m-small" else "billing"`: ends the function and hands back `'returns' if request.model == 'm-small' else 'billing'`. `'returns' if request.model == 'm-small' else 'billing'` gives `'returns'` when `request.model == 'm-small'` is true, otherwise `'billing'`.
- `if text.startswith("REFUND"):`: runs the block below only if `text.startswith('REFUND')` is true. `text.startswith('REFUND')` is whether `text` begins with `'REFUND'`.
- `return "40.00"`: ends the function and hands back `'40.00'`.
- `return f'Answer: x\nQuote: "{POLICY_LINES[1]}"' if request.model != "m-large" else RIGH...`: ends the function and hands back `f'Answer: x\nQuote: "{POLICY_LINES[1]}"' if request.model != 'm-large' else R...`. `f'Answer: x\nQuote: "{POLICY_LINES[1]}"' if request.model != 'm-lar...` gives `f'Answer: x\nQuote: "{POLICY_LINES[1]}"'` when `request.model != 'm-large'` is true, otherwise `RIGHT_QUOTE`; the f-string inserts `POLICY_LINES[1]` into the text.
- `tiers, _ = tiers_for(answer)`: sets `(tiers, _)` to the value of `tiers_for(answer)`.
- `tasks = corpus()`: sets `tasks` to the value of `corpus()`.
- `answers = collect_answers(tasks, tiers, sequential)`: sets `answers` to the value of `collect_answers(tasks, tiers, sequential)`.
- `rates = check_results(tasks, answers, tiers, sequential)`: sets `rates` to the value of `check_results(tasks, answers, tiers, sequential)`.
- `assert rates["small"]["label"]["label_shape"].false_accept_rate == 1.0`: checks that `rates['small']['label']['label_shape'].false_accept_rate == 1.0` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
    assert rates["small"]["label"]["label_agreement"].false_accept_rate == 1.0
    assert rates["small"]["refund"]["refund_recompute"].false_accept_rate == 0.0
    assert rates["medium"]["policy"]["policy_quote"].false_accept_rate == 1.0
    assert rates["large"]["policy"]["policy_quote"].false_accept_rate == 0.0
    cfg = tune(tasks, answers, rates, BAR)
    assert cfg.start == {"label": "medium", "refund": "small", "policy": "large"}
    assert cfg.label_check == "agreement" and cfg.request_cap == BAR.request_cap


def test_hard_tasks_skip_a_tier_that_fails_them_on_the_build_set():
    def answer(request: ChatRequest) -> str:
        return "99.00" if "damaged" in request.messages[0].content else "40.00"

    tiers, _ = tiers_for(answer)
```
<!-- fmt: on -->

- `assert rates["small"]["label"]["label_agreement"].false_accept_rate == 1.0`: checks that `rates['small']['label']['label_agreement'].false_accept_rate == 1.0` is true; if it is not, the test (or program) fails here.
- `assert rates["small"]["refund"]["refund_recompute"].false_accept_rate == 0.0`: checks that `rates['small']['refund']['refund_recompute'].false_accept_rate == 0.0` is true; if it is not, the test (or program) fails here.
- `assert rates["medium"]["policy"]["policy_quote"].false_accept_rate == 1.0`: checks that `rates['medium']['policy']['policy_quote'].false_accept_rate == 1.0` is true; if it is not, the test (or program) fails here.
- `assert rates["large"]["policy"]["policy_quote"].false_accept_rate == 0.0`: checks that `rates['large']['policy']['policy_quote'].false_accept_rate == 0.0` is true; if it is not, the test (or program) fails here.
- `cfg = tune(tasks, answers, rates, BAR)`: sets `cfg` to the value of `tune(tasks, answers, rates, BAR)`.
- `assert cfg.start == {"label": "medium", "refund": "small", "policy": "large"}`: checks that `cfg.start == {'label': 'medium', 'refund': 'small', 'policy': 'large'}` is true; if it is not, the test (or program) fails here.
- `assert cfg.label_check == "agreement" and cfg.request_cap == BAR.request_cap`: checks that `cfg.label_check == 'agreement' and cfg.request_cap == BAR.request_cap` is true; if it is not, the test (or program) fails here.
- `def test_hard_tasks_skip_a_tier_that_fails_them_on_the_build_set():`: defines the test `test_hard_tasks_skip_a_tier_that_fails_them_on_the_build_set` taking no arguments.
- `def answer(request: ChatRequest) -> str:`: defines the function `answer` taking request (ChatRequest) and returns `str`.
- `return "99.00" if "damaged" in request.messages[0].content else "40.00"`: ends the function and hands back `'99.00' if 'damaged' in request.messages[0].content else '40.00'`. `'99.00' if 'damaged' in request.messages[0].content else '40.00'` gives `'99.00'` when `'damaged' in request.messages[0].content` is true, otherwise `'40.00'`.
- `tiers, _ = tiers_for(answer)`: sets `(tiers, _)` to the value of `tiers_for(answer)`.

<!-- fmt: off -->
```python
    tasks = [refund_task(f"t{i}", split="build") for i in range(5)]
    hard = [
        type(t)(f"h{i}", t.kind, "hard", "build", t.text + " The item was damaged.", t.gold, t.orders)
        for i, t in enumerate(tasks)
    ]
    everything = tasks + hard
    answers = collect_answers(everything, tiers, sequential)
    rates = check_results(everything, answers, tiers, sequential)
    cfg = tune(everything, answers, rates, BAR, request_cap=0.5)
    assert cfg.start["refund"] == "small" and cfg.hard_start == {"refund": "medium"} and cfg.request_cap == 0.5


def test_routing_the_test_set_summaries_and_the_verdict_against_the_large_model():
    tiers, _ = tiers_for(answer_all)
```
<!-- fmt: on -->

- `tasks = [refund_task(f"t{i}", split="build") for i in range(5)]`: sets `tasks` to the value of `[refund_task(f't{i}', split='build') for i in range(5)]`. `[refund_task(f't{i}', split='build') for i in range(5)]` builds a list: for each `i` in `range(5)`; the f-string inserts `i` into the text; `range(5)` is the whole numbers from `0` up to, not including, `5`.
- `hard = [`: sets `hard` to the value of `[type(t)(f'h{i}', t.kind, 'hard', 'build', t.text + ' The item was damaged.',...`. `[type(t)(f'h{i}', t.kind, 'hard', 'build', t.text + ' The item was ...` builds a list: for each `(i, t)` in `enumerate(tasks)`; `type(t)` is the type of `t`; the f-string inserts `i` into the text.
- `everything = tasks + hard`: sets `everything` to the value of `tasks + hard`.
- `answers = collect_answers(everything, tiers, sequential)`: sets `answers` to the value of `collect_answers(everything, tiers, sequential)`.
- `rates = check_results(everything, answers, tiers, sequential)`: sets `rates` to the value of `check_results(everything, answers, tiers, sequential)`.
- `cfg = tune(everything, answers, rates, BAR, request_cap=0.5)`: sets `cfg` to the value of `tune(everything, answers, rates, BAR, request_cap=0.5)`.
- `assert cfg.start["refund"] == "small" and cfg.hard_start == {"refund": "medium"} and cf...`: checks that `cfg.start['refund'] == 'small' and cfg.hard_start == {'refund': 'medium'} and...` is true; if it is not, the test (or program) fails here.
- `def test_routing_the_test_set_summaries_and_the_verdict_against_the_large_model():`: defines the test `test_routing_the_test_set_summaries_and_the_verdict_against_the_large_model` taking no arguments.
- `tiers, _ = tiers_for(answer_all)`: sets `(tiers, _)` to the value of `tiers_for(answer_all)`.

<!-- fmt: off -->
```python
    tasks = corpus()
    answers = collect_answers(tasks, tiers, sequential)
    router = CostRouter(tiers, make_checks(tiers, config()), config())
    outcomes = route_all(tasks, router)
    summary = summarize(outcomes)
    assert summary.n == 3 and summary.accuracy.value == 1.0 and summary.escalated == 0
    assert summary.served_by == {"small": 3} and summary.max_request_spend > 0
    large = single_model_summary(tasks, answers, "large")
    assert large.total_cost > summary.total_cost
    verdict = compare_to_large(tasks, answers, outcomes, BAR)
    assert verdict["verdict"] == "matched" and verdict["matched_within_margin"] and verdict["cheaper_per_correct"]
    escalating = route_all(tasks, CostRouter(tiers_for(lambda r: "x")[0], make_checks(tiers, config()), config()))
    assert all(o.escalated for o in escalating)
    assert compare_to_large(tasks, answers, escalating, BAR)["verdict"] == "not cheaper"
```
<!-- fmt: on -->

- `tasks = corpus()`: sets `tasks` to the value of `corpus()`.
- `answers = collect_answers(tasks, tiers, sequential)`: sets `answers` to the value of `collect_answers(tasks, tiers, sequential)`.
- `router = CostRouter(tiers, make_checks(tiers, config()), config())`: sets `router` to the value of `CostRouter(tiers, make_checks(tiers, config()), config())`.
- `outcomes = route_all(tasks, router)`: sets `outcomes` to the value of `route_all(tasks, router)`.
- `summary = summarize(outcomes)`: sets `summary` to the value of `summarize(outcomes)`.
- `assert summary.n == 3 and summary.accuracy.value == 1.0 and summary.escalated == 0`: checks that `summary.n == 3 and summary.accuracy.value == 1.0 and (summary.escalated == 0)` is true; if it is not, the test (or program) fails here.
- `assert summary.served_by == {"small": 3} and summary.max_request_spend > 0`: checks that `summary.served_by == {'small': 3} and summary.max_request_spend > 0` is true; if it is not, the test (or program) fails here.
- `large = single_model_summary(tasks, answers, "large")`: sets `large` to the value of `single_model_summary(tasks, answers, 'large')`.
- `assert large.total_cost > summary.total_cost`: checks that `large.total_cost > summary.total_cost` is true; if it is not, the test (or program) fails here.
- `verdict = compare_to_large(tasks, answers, outcomes, BAR)`: sets `verdict` to the value of `compare_to_large(tasks, answers, outcomes, BAR)`.
- `assert verdict["verdict"] == "matched" and verdict["matched_within_margin"] and verdict...`: checks that `verdict['verdict'] == 'matched' and verdict['matched_within_margin'] and verd...` is true; if it is not, the test (or program) fails here.
- `escalating = route_all(tasks, CostRouter(tiers_for(lambda r: "x")[0], make_checks(tiers...`: sets `escalating` to the value of `route_all(tasks, CostRouter(tiers_for(lambda r: 'x')[0], make_checks(tiers, c...`. `lambda r: 'x'` is a small unnamed function of `r` that gives `'x'`.
- `assert all(o.escalated for o in escalating)`: checks that `all((o.escalated for o in escalating))` is true; if it is not, the test (or program) fails here. `all((o.escalated for o in escalating))` is true if every item of `(o.escalated for o in escalating)` is true; `(o.escalated for o in escalating)` builds a generator of values: for each `o` in `escalating`.
- `assert compare_to_large(tasks, answers, escalating, BAR)["verdict"] == "not cheaper"`: checks that `compare_to_large(tasks, answers, escalating, BAR)['verdict'] == 'not cheaper'` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
def test_the_verdict_can_be_cheaper_but_less_accurate():
    tiers, _ = tiers_for(by_tier({"m-small": "40.00", "m-medium": "x", "m-large": "x"}))
    task = refund_task("t2", days=20, total=5000)
    answers = collect_answers([task], tiers, sequential)
    wrong_router = CostRouter(
        tiers, make_checks(tiers, config()), config(start={"label": "small", "refund": "large", "policy": "small"})
    )
    outcomes = route_all([task], wrong_router)
    large = answers["large"]["t2"]
    assert not is_correct(task, large.text)
    assert compare_to_large([task], answers, outcomes, BAR)["verdict"] in {
        "not cheaper",
        "cheaper but less accurate",
        "matched",
    }
```
<!-- fmt: on -->

- `def test_the_verdict_can_be_cheaper_but_less_accurate():`: defines the test `test_the_verdict_can_be_cheaper_but_less_accurate` taking no arguments.
- `tiers, _ = tiers_for(by_tier({"m-small": "40.00", "m-medium": "x", "m-large": "x"}))`: sets `(tiers, _)` to the value of `tiers_for(by_tier({'m-small': '40.00', 'm-medium': 'x', 'm-large': 'x'}))`.
- `task = refund_task("t2", days=20, total=5000)`: sets `task` to the value of `refund_task('t2', days=20, total=5000)`.
- `answers = collect_answers([task], tiers, sequential)`: sets `answers` to the value of `collect_answers([task], tiers, sequential)`.
- `wrong_router = CostRouter(`: sets `wrong_router` to the value of `CostRouter(tiers, make_checks(tiers, config()), config(start={'label': 'small...`.
- `outcomes = route_all([task], wrong_router)`: sets `outcomes` to the value of `route_all([task], wrong_router)`.
- `large = answers["large"]["t2"]`: sets `large` to the value of `answers['large']['t2']`.
- `assert not is_correct(task, large.text)`: checks that `not is_correct(task, large.text)` is true; if it is not, the test (or program) fails here.
- `assert compare_to_large([task], answers, outcomes, BAR)["verdict"] in {`: checks that `compare_to_large([task], answers, outcomes, BAR)['verdict'] in {'not cheaper'...` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
def test_a_day_under_a_budget_tightens_and_reports_before_and_after():
    tiers, _ = tiers_for(by_tier({"m-small": "99.00", "m-medium": "99.00", "m-large": "40.00"}))
    tasks = [refund_task(f"t{i}", days=20, total=5000) for i in range(12)]
    answers = collect_answers(tasks, tiers, sequential)
    factory = lambda: CostRouter(tiers, make_checks(tiers, config()), config())  # noqa: E731
    result = run_day(tasks, answers, factory, 0.6)
    assert result.crossed_at is not None and result.accuracy_before.trials + result.accuracy_after.trials == 12
    assert result.large_served_after == 0 and result.accuracy_after.value == 0.0
    assert result.requests_over_cap == 0 and result.budget == pytest.approx(
        0.6 * sum(a.cost for a in answers["large"].values())
    )
    roomy = run_day(tasks, answers, factory, 50.0)
    assert roomy.crossed_at is None and roomy.accuracy_after.trials == 0 and roomy.under_budget
```
<!-- fmt: on -->

- `def test_a_day_under_a_budget_tightens_and_reports_before_and_after():`: defines the test `test_a_day_under_a_budget_tightens_and_reports_before_and_after` taking no arguments.
- `tiers, _ = tiers_for(by_tier({"m-small": "99.00", "m-medium": "99.00", "m-large": "40.0...`: sets `(tiers, _)` to the value of `tiers_for(by_tier({'m-small': '99.00', 'm-medium': '99.00', 'm-large': '40.00...`.
- `tasks = [refund_task(f"t{i}", days=20, total=5000) for i in range(12)]`: sets `tasks` to the value of `[refund_task(f't{i}', days=20, total=5000) for i in range(12)]`. `[refund_task(f't{i}', days=20, total=5000) for i in range(12)]` builds a list: for each `i` in `range(12)`; the f-string inserts `i` into the text; `range(12)` is the whole numbers from `0` up to, not including, `12`.
- `answers = collect_answers(tasks, tiers, sequential)`: sets `answers` to the value of `collect_answers(tasks, tiers, sequential)`.
- `factory = lambda: CostRouter(tiers, make_checks(tiers, config()), config())  # noqa: E731`: sets `factory` to the value of `lambda: CostRouter(tiers, make_checks(tiers, config()), config())`. `lambda: CostRouter(tiers, make_checks(tiers, config()), config())` is a small unnamed function of no arguments that gives `CostRouter(tiers, make_checks(tiers, ...`.
- `result = run_day(tasks, answers, factory, 0.6)`: sets `result` to the value of `run_day(tasks, answers, factory, 0.6)`.
- `assert result.crossed_at is not None and result.accuracy_before.trials + result.accurac...`: checks that `result.crossed_at is not None and result.accuracy_before.trials + result.accu...` is true; if it is not, the test (or program) fails here. `result.crossed_at is not None` tests that there is something in `result.crossed_at`.
- `assert result.large_served_after == 0 and result.accuracy_after.value == 0.0`: checks that `result.large_served_after == 0 and result.accuracy_after.value == 0.0` is true; if it is not, the test (or program) fails here.
- `assert result.requests_over_cap == 0 and result.budget == pytest.approx(`: checks that `result.requests_over_cap == 0 and result.budget == pytest.approx(0.6 * sum((a...` is true; if it is not, the test (or program) fails here. `pytest.approx(0.6 * sum((a.cost for a in answers['large'].values())))` is `0.6 * sum((a.cost for a in answers['large'].values()))` compared with a small tolerance; `sum((a.cost for a in answers['large'].values()))` is the sum of `(a.cost for a in answers['large'].values())`; `(a.cost for a in answers['large'].values())` builds a generator of values: for each `a` in `answers['large'].values()`.
- `roomy = run_day(tasks, answers, factory, 50.0)`: sets `roomy` to the value of `run_day(tasks, answers, factory, 50.0)`.
- `assert roomy.crossed_at is None and roomy.accuracy_after.trials == 0 and roomy.under_bu...`: checks that `roomy.crossed_at is None and roomy.accuracy_after.trials == 0 and roomy.under...` is true; if it is not, the test (or program) fails here. `roomy.crossed_at is None` tests that there is nothing (`None`) in `roomy.crossed_at`.

<!-- fmt: off -->
```python
def test_false_accepts_are_grouped_by_tier_and_check_and_the_weakest_kind_changes():
    def answer(request: ChatRequest) -> str:
        text = request.messages[0].content
        return f'Answer: x\nQuote: "{POLICY_LINES[1]}"' if text.startswith("POLICY") else "40.00"

    tiers, _ = tiers_for(answer)
    tasks = [policy_task("t3", 0), refund_task("t2")]
    cfg = config()
    outcomes = route_all(tasks, CostRouter(tiers, make_checks(tiers, cfg), cfg))
    report = false_accepts(outcomes, cfg)
    assert report["false_accepts"] == 1 and report["by_tier"] == {"small": 1}
    assert report["by_tier_and_check"]["small/policy_quote"]["tasks"] == ["t3"]
    assert weakest_kind(outcomes) == "policy"
    only_refund = route_all([refund_task()], CostRouter(tiers, make_checks(tiers, cfg), cfg))
```
<!-- fmt: on -->

- `def test_false_accepts_are_grouped_by_tier_and_check_and_the_weakest_kind_changes():`: defines the test `test_false_accepts_are_grouped_by_tier_and_check_and_the_weakest_kind_changes` taking no arguments.
- `def answer(request: ChatRequest) -> str:`: defines the function `answer` taking request (ChatRequest) and returns `str`.
- `text = request.messages[0].content`: sets `text` to the value of `request.messages[0].content`.
- `return f'Answer: x\nQuote: "{POLICY_LINES[1]}"' if text.startswith("POLICY") else "40.00"`: ends the function and hands back `f'Answer: x\nQuote: "{POLICY_LINES[1]}"' if text.startswith('POLICY') else '4...`. `f'Answer: x\nQuote: "{POLICY_LINES[1]}"' if text.startswith('POLICY...` gives `f'Answer: x\nQuote: "{POLICY_LINES[1]}"'` when `text.startswith('POLICY')` is true, otherwise `'40.00'`; `text.startswith('POLICY')` is whether `text` begins with `'POLICY'`; the f-string inserts `POLICY_LINES[1]` into the text.
- `tiers, _ = tiers_for(answer)`: sets `(tiers, _)` to the value of `tiers_for(answer)`.
- `tasks = [policy_task("t3", 0), refund_task("t2")]`: sets `tasks` to a list of 2 items.
- `cfg = config()`: sets `cfg` to the value of `config()`.
- `outcomes = route_all(tasks, CostRouter(tiers, make_checks(tiers, cfg), cfg))`: sets `outcomes` to the value of `route_all(tasks, CostRouter(tiers, make_checks(tiers, cfg), cfg))`.
- `report = false_accepts(outcomes, cfg)`: sets `report` to the value of `false_accepts(outcomes, cfg)`.
- `assert report["false_accepts"] == 1 and report["by_tier"] == {"small": 1}`: checks that `report['false_accepts'] == 1 and report['by_tier'] == {'small': 1}` is true; if it is not, the test (or program) fails here.
- `assert report["by_tier_and_check"]["small/policy_quote"]["tasks"] == ["t3"]`: checks that `report['by_tier_and_check']['small/policy_quote']['tasks'] == ['t3']` is true; if it is not, the test (or program) fails here.
- `assert weakest_kind(outcomes) == "policy"`: checks that `weakest_kind(outcomes) == 'policy'` is true; if it is not, the test (or program) fails here.
- `only_refund = route_all([refund_task()], CostRouter(tiers, make_checks(tiers, cfg), cfg))`: sets `only_refund` to the value of `route_all([refund_task()], CostRouter(tiers, make_checks(tiers, cfg), cfg))`.

<!-- fmt: off -->
```python
    assert weakest_kind(only_refund) is None


def test_hardening_moves_a_kind_up_a_tier_then_strengthens_the_policy_check_then_gives_up():
    cfg = config(start={"label": "small", "refund": "large", "policy": "medium"}, hard={"policy": "medium"})
    up, text = harden(cfg, "policy")
    assert up.start["policy"] == "large" and up.hard_start == {} and "large instead of medium" in text
    stronger, text = harden(up, "policy")
    assert stronger.policy_check == "overlap" and stronger.start == up.start and "best matches" in text
    same, text = harden(cfg, "refund")
    assert same == cfg and "nothing changed" in text


def test_the_overlap_check_rejects_a_real_but_wrong_line():
```
<!-- fmt: on -->

- `assert weakest_kind(only_refund) is None`: checks that `weakest_kind(only_refund) is None` is true; if it is not, the test (or program) fails here. `weakest_kind(only_refund) is None` tests that there is nothing (`None`) in `weakest_kind(only_refund)`.
- `def test_hardening_moves_a_kind_up_a_tier_then_strengthens_the_policy_check_then_gives_...`: defines the test `test_hardening_moves_a_kind_up_a_tier_then_strengthens_the_policy_check_then_gives_up` taking no arguments.
- `cfg = config(start={"label": "small", "refund": "large", "policy": "medium"}, hard={"po...`: sets `cfg` to the value of `config(start={'label': 'small', 'refund': 'large', 'policy': 'medium'}, hard=...`.
- `up, text = harden(cfg, "policy")`: sets `(up, text)` to the value of `harden(cfg, 'policy')`.
- `assert up.start["policy"] == "large" and up.hard_start == {} and "large instead of medi...`: checks that `up.start['policy'] == 'large' and up.hard_start == {} and ('large instead of ...` is true; if it is not, the test (or program) fails here.
- `stronger, text = harden(up, "policy")`: sets `(stronger, text)` to the value of `harden(up, 'policy')`.
- `assert stronger.policy_check == "overlap" and stronger.start == up.start and "best matc...`: checks that `stronger.policy_check == 'overlap' and stronger.start == up.start and ('best ...` is true; if it is not, the test (or program) fails here.
- `same, text = harden(cfg, "refund")`: sets `(same, text)` to the value of `harden(cfg, 'refund')`.
- `assert same == cfg and "nothing changed" in text`: checks that `same == cfg and 'nothing changed' in text` is true; if it is not, the test (or program) fails here.
- `def test_the_overlap_check_rejects_a_real_but_wrong_line():`: defines the test `test_the_overlap_check_rejects_a_real_but_wrong_line` taking no arguments.

<!-- fmt: off -->
```python
    tiers, _ = tiers_for(lambda r: "x")
    question = Task("t3", Kind.POLICY, "easy", "test", "Who pays return shipping?", 1)
    wrong, right = f'Quote: "{POLICY_LINES[6]}"', f'Quote: "{POLICY_LINES[1]}"'
    quote_only = AnswerChecks(tiers, "agreement", "quote")
    overlap = AnswerChecks(tiers, "agreement", "overlap")
    assert quote_only.check(question, "small", wrong).passed
    assert not overlap.check(question, "small", wrong).passed
    assert overlap.check(question, "small", right).passed
```
<!-- fmt: on -->

- `tiers, _ = tiers_for(lambda r: "x")`: sets `(tiers, _)` to the value of `tiers_for(lambda r: 'x')`. `lambda r: 'x'` is a small unnamed function of `r` that gives `'x'`.
- `question = Task("t3", Kind.POLICY, "easy", "test", "Who pays return shipping?", 1)`: sets `question` to the value of `Task('t3', Kind.POLICY, 'easy', 'test', 'Who pays return shipping?', 1)`.
- `wrong, right = f'Quote: "{POLICY_LINES[6]}"', f'Quote: "{POLICY_LINES[1]}"'`: sets `(wrong, right)` to a tuple of 2 items. the f-string inserts `POLICY_LINES[6]` into the text; the f-string inserts `POLICY_LINES[1]` into the text.
- `quote_only = AnswerChecks(tiers, "agreement", "quote")`: sets `quote_only` to the value of `AnswerChecks(tiers, 'agreement', 'quote')`.
- `overlap = AnswerChecks(tiers, "agreement", "overlap")`: sets `overlap` to the value of `AnswerChecks(tiers, 'agreement', 'overlap')`.
- `assert quote_only.check(question, "small", wrong).passed`: checks that `quote_only.check(question, 'small', wrong).passed` is true; if it is not, the test (or program) fails here.
- `assert not overlap.check(question, "small", wrong).passed`: checks that `not overlap.check(question, 'small', wrong).passed` is true; if it is not, the test (or program) fails here.
- `assert overlap.check(question, "small", right).passed`: checks that `overlap.check(question, 'small', right).passed` is true; if it is not, the test (or program) fails here.

#### `tests/unit/domain/__init__.py`

This file is empty. It exists so that Python treats the folder as a package.

#### `tests/unit/domain/test_domain.py`

<!-- fmt: off -->
```python
import pytest

from cost_router.domain.checks import (
    best_matching_line,
    check_label_agreement,
    check_label_shape,
    check_policy,
    check_policy_overlap,
    check_refund,
    content_words,
    is_correct,
    normalize,
    parse_amount_cents,
    parse_label,
    parse_quote,
    quoted_line_index,
)
```
<!-- fmt: on -->

- `import pytest`: imports the module(s) `pytest` so this file can use them. `pytest` is the test framework (`pytest.md`).
- `from cost_router.domain.checks import (`: takes the name(s) `best_matching_line, check_label_agreement, check_label_shape, check_policy, check_policy_overlap, check_refund, content_words, is_correct, normalize, parse_amount_cents, parse_label, parse_quote, quoted_line_index` from the module `cost_router.domain.checks` (a module of this project).

<!-- fmt: off -->
```python
from cost_router.domain.llm import Usage
from cost_router.domain.metrics import (
    bootstrap_accuracy_difference,
    bootstrap_cost_per_correct,
    check_rates,
    cost_per_correct,
    rate,
)
from cost_router.domain.pricing import PriceTable
from cost_router.domain.routing import DayBudget, RouterConfig
from cost_router.domain.signals import hard_signal
from cost_router.domain.stats import shuffled_indices
from cost_router.domain.tasks import POLICY_LINES, Kind, RefundOrder, Task, expected_refund_cents, money, refund_cents
from tests.unit.fakes import label_task, policy_task, refund_task
```
<!-- fmt: on -->

- `from cost_router.domain.llm import Usage`: takes the name(s) `Usage` from the module `cost_router.domain.llm` (a module of this project).
- `from cost_router.domain.metrics import (`: takes the name(s) `bootstrap_accuracy_difference, bootstrap_cost_per_correct, check_rates, cost_per_correct, rate` from the module `cost_router.domain.metrics` (a module of this project).
- `from cost_router.domain.pricing import PriceTable`: takes the name(s) `PriceTable` from the module `cost_router.domain.pricing` (a module of this project).
- `from cost_router.domain.routing import DayBudget, RouterConfig`: takes the name(s) `DayBudget, RouterConfig` from the module `cost_router.domain.routing` (a module of this project).
- `from cost_router.domain.signals import hard_signal`: takes the name(s) `hard_signal` from the module `cost_router.domain.signals` (a module of this project).
- `from cost_router.domain.stats import shuffled_indices`: takes the name(s) `shuffled_indices` from the module `cost_router.domain.stats` (a module of this project).
- `from cost_router.domain.tasks import POLICY_LINES, Kind, RefundOrder, Task, expected_re...`: takes the name(s) `POLICY_LINES, Kind, RefundOrder, Task, expected_refund_cents, money, refund_cents` from the module `cost_router.domain.tasks` (a module of this project).
- `from tests.unit.fakes import label_task, policy_task, refund_task`: takes the name(s) `label_task, policy_task, refund_task` from the module `tests.unit.fakes` (a module of this project).

<!-- fmt: off -->
```python
def test_refund_rules_follow_the_policy():
    assert refund_cents(RefundOrder("o", 5000, 10, 5000, False)) == 5000
    assert refund_cents(RefundOrder("o", 5000, 20, 5000, False)) == 4000
    assert refund_cents(RefundOrder("o", 5000, 31, 5000, False)) == 0
    assert refund_cents(RefundOrder("o", 5000, 20, 2500, True)) == 2500
    assert refund_cents({"days": 16, "returned_cents": 1250, "damaged": False}) == 1000
    assert refund_cents(RefundOrder("o", 5000, 40, 5000, True)) == 0
    assert money(4000) == "40.00" and money(5) == "0.05"


def test_expected_refund_adds_every_order():
    orders = (RefundOrder("a", 5000, 20, 5000, False), RefundOrder("b", 2500, 4, 1250, False))
    task = Task("t", Kind.REFUND, "hard", "test", "x", 5250, orders)
    assert expected_refund_cents(task) == 5250
```
<!-- fmt: on -->

- `def test_refund_rules_follow_the_policy():`: defines the test `test_refund_rules_follow_the_policy` taking no arguments.
- `assert refund_cents(RefundOrder("o", 5000, 10, 5000, False)) == 5000`: checks that `refund_cents(RefundOrder('o', 5000, 10, 5000, False)) == 5000` is true; if it is not, the test (or program) fails here.
- `assert refund_cents(RefundOrder("o", 5000, 20, 5000, False)) == 4000`: checks that `refund_cents(RefundOrder('o', 5000, 20, 5000, False)) == 4000` is true; if it is not, the test (or program) fails here.
- `assert refund_cents(RefundOrder("o", 5000, 31, 5000, False)) == 0`: checks that `refund_cents(RefundOrder('o', 5000, 31, 5000, False)) == 0` is true; if it is not, the test (or program) fails here.
- `assert refund_cents(RefundOrder("o", 5000, 20, 2500, True)) == 2500`: checks that `refund_cents(RefundOrder('o', 5000, 20, 2500, True)) == 2500` is true; if it is not, the test (or program) fails here.
- `assert refund_cents({"days": 16, "returned_cents": 1250, "damaged": False}) == 1000`: checks that `refund_cents({'days': 16, 'returned_cents': 1250, 'damaged': False}) == 1000` is true; if it is not, the test (or program) fails here.
- `assert refund_cents(RefundOrder("o", 5000, 40, 5000, True)) == 0`: checks that `refund_cents(RefundOrder('o', 5000, 40, 5000, True)) == 0` is true; if it is not, the test (or program) fails here.
- `assert money(4000) == "40.00" and money(5) == "0.05"`: checks that `money(4000) == '40.00' and money(5) == '0.05'` is true; if it is not, the test (or program) fails here.
- `def test_expected_refund_adds_every_order():`: defines the test `test_expected_refund_adds_every_order` taking no arguments.
- `orders = (RefundOrder("a", 5000, 20, 5000, False), RefundOrder("b", 2500, 4, 1250, False))`: sets `orders` to a tuple of 2 items.
- `task = Task("t", Kind.REFUND, "hard", "test", "x", 5250, orders)`: sets `task` to the value of `Task('t', Kind.REFUND, 'hard', 'test', 'x', 5250, orders)`.
- `assert expected_refund_cents(task) == 5250`: checks that `expected_refund_cents(task) == 5250` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
def test_labels_must_be_exactly_an_allowed_word():
    assert parse_label(" Billing. ") == "billing"
    assert parse_label('"shipping"') == "shipping"
    assert parse_label("customer support") is None
    assert parse_label("billing issue") is None
    assert check_label_shape("returns") and not check_label_shape("nonsense")
    assert check_label_agreement("billing", "Billing.") and not check_label_agreement("billing", "returns")
    assert not check_label_agreement("nonsense", "nonsense")


def test_amounts_are_read_to_the_cent():
    assert parse_amount_cents("$40.00") == 4000
    assert parse_amount_cents("12") == 1200
    assert parse_amount_cents("1,234.5") == 123450
```
<!-- fmt: on -->

- `def test_labels_must_be_exactly_an_allowed_word():`: defines the test `test_labels_must_be_exactly_an_allowed_word` taking no arguments.
- `assert parse_label(" Billing. ") == "billing"`: checks that `parse_label(' Billing. ') == 'billing'` is true; if it is not, the test (or program) fails here.
- `assert parse_label('"shipping"') == "shipping"`: checks that `parse_label('"shipping"') == 'shipping'` is true; if it is not, the test (or program) fails here.
- `assert parse_label("customer support") is None`: checks that `parse_label('customer support') is None` is true; if it is not, the test (or program) fails here. `parse_label('customer support') is None` tests that there is nothing (`None`) in `parse_label('customer suppo...`.
- `assert parse_label("billing issue") is None`: checks that `parse_label('billing issue') is None` is true; if it is not, the test (or program) fails here. `parse_label('billing issue') is None` tests that there is nothing (`None`) in `parse_label('billing issue')`.
- `assert check_label_shape("returns") and not check_label_shape("nonsense")`: checks that `check_label_shape('returns') and (not check_label_shape('nonsense'))` is true; if it is not, the test (or program) fails here.
- `assert check_label_agreement("billing", "Billing.") and not check_label_agreement("bill...`: checks that `check_label_agreement('billing', 'Billing.') and (not check_label_agreement('...` is true; if it is not, the test (or program) fails here.
- `assert not check_label_agreement("nonsense", "nonsense")`: checks that `not check_label_agreement('nonsense', 'nonsense')` is true; if it is not, the test (or program) fails here.
- `def test_amounts_are_read_to_the_cent():`: defines the test `test_amounts_are_read_to_the_cent` taking no arguments.
- `assert parse_amount_cents("$40.00") == 4000`: checks that `parse_amount_cents('$40.00') == 4000` is true; if it is not, the test (or program) fails here.
- `assert parse_amount_cents("12") == 1200`: checks that `parse_amount_cents('12') == 1200` is true; if it is not, the test (or program) fails here.
- `assert parse_amount_cents("1,234.5") == 123450`: checks that `parse_amount_cents('1,234.5') == 123450` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
    assert parse_amount_cents("Worked out: 50 - 10 = 40\nRefund: 40.00") == 4000
    assert parse_amount_cents("Refund: $5.00 ... then\nRefund: $7.25") == 725
    assert parse_amount_cents("The refund is 40.00 dollars") is None
    assert parse_amount_cents("no number") is None


def test_quotes_are_matched_against_the_policy_lines():
    reply = f'Answer: Yes.\nQuote: "{POLICY_LINES[0]}"'
    assert parse_quote(reply) == normalize(POLICY_LINES[0])
    assert quoted_line_index(reply) == 0
    assert quoted_line_index('Answer: x\nQuote: "Something else."') is None
    assert quoted_line_index("no quote at all") is None
    assert quoted_line_index(f'Answer: x\nQuote: "{POLICY_LINES[2]}"\n\nQuestion: and then it kept going') == 2
    assert check_policy(reply) and not check_policy("Answer: 2.")
```
<!-- fmt: on -->

- `assert parse_amount_cents("Worked out: 50 - 10 = 40\nRefund: 40.00") == 4000`: checks that `parse_amount_cents('Worked out: 50 - 10 = 40\nRefund: 40.00') == 4000` is true; if it is not, the test (or program) fails here.
- `assert parse_amount_cents("Refund: $5.00 ... then\nRefund: $7.25") == 725`: checks that `parse_amount_cents('Refund: $5.00 ... then\nRefund: $7.25') == 725` is true; if it is not, the test (or program) fails here.
- `assert parse_amount_cents("The refund is 40.00 dollars") is None`: checks that `parse_amount_cents('The refund is 40.00 dollars') is None` is true; if it is not, the test (or program) fails here. `parse_amount_cents('The refund is 40.00 dollars') is None` tests that there is nothing (`None`) in `parse_amount_cents('The ref...`.
- `assert parse_amount_cents("no number") is None`: checks that `parse_amount_cents('no number') is None` is true; if it is not, the test (or program) fails here. `parse_amount_cents('no number') is None` tests that there is nothing (`None`) in `parse_amount_cents('no numb...`.
- `def test_quotes_are_matched_against_the_policy_lines():`: defines the test `test_quotes_are_matched_against_the_policy_lines` taking no arguments.
- `reply = f'Answer: Yes.\nQuote: "{POLICY_LINES[0]}"'`: sets `reply` to the value of `f'Answer: Yes.\nQuote: "{POLICY_LINES[0]}"'`. the f-string inserts `POLICY_LINES[0]` into the text.
- `assert parse_quote(reply) == normalize(POLICY_LINES[0])`: checks that `parse_quote(reply) == normalize(POLICY_LINES[0])` is true; if it is not, the test (or program) fails here.
- `assert quoted_line_index(reply) == 0`: checks that `quoted_line_index(reply) == 0` is true; if it is not, the test (or program) fails here.
- `assert quoted_line_index('Answer: x\nQuote: "Something else."') is None`: checks that `quoted_line_index('Answer: x\nQuote: "Something else."') is None` is true; if it is not, the test (or program) fails here. `quoted_line_index('Answer: x\nQuote: "Something else."') ...` tests that there is nothing (`None`) in `quoted_line_index('Answer: ...`.
- `assert quoted_line_index("no quote at all") is None`: checks that `quoted_line_index('no quote at all') is None` is true; if it is not, the test (or program) fails here. `quoted_line_index('no quote at all') is None` tests that there is nothing (`None`) in `quoted_line_index('no quote...`.
- `assert quoted_line_index(f'Answer: x\nQuote: "{POLICY_LINES[2]}"\n\nQuestion: and then ...`: checks that `quoted_line_index(f'Answer: x\nQuote: "{POLICY_LINES[2]}"\n\nQuestion: and th...` is true; if it is not, the test (or program) fails here. the f-string inserts `POLICY_LINES[2]` into the text.
- `assert check_policy(reply) and not check_policy("Answer: 2.")`: checks that `check_policy(reply) and (not check_policy('Answer: 2.'))` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
def test_grading_is_the_ground_truth_and_checks_see_only_the_answer():
    assert is_correct(label_task(gold="billing"), "billing")
    assert not is_correct(label_task(gold="billing"), "returns")
    task = refund_task(days=20, total=5000)
    assert is_correct(task, "40.00") and check_refund(task, "$40.00")
    assert not is_correct(task, "50.00") and not check_refund(task, "50.00")
    right = f'Answer: ok\nQuote: "{POLICY_LINES[0]}"'
    wrong_line = f'Answer: ok\nQuote: "{POLICY_LINES[1]}"'
    assert is_correct(policy_task(gold=0), right) and not is_correct(policy_task(gold=0), wrong_line)
    assert check_policy(wrong_line)  # the check accepts a real line even when it is the wrong one: a false accept


def test_the_hard_signal_sees_two_orders_or_an_exception_word():
    assert hard_signal(Task("t", Kind.REFUND, "hard", "test", "Order PR-100001 and PR-200002 are returned.", 0))
```
<!-- fmt: on -->

- `def test_grading_is_the_ground_truth_and_checks_see_only_the_answer():`: defines the test `test_grading_is_the_ground_truth_and_checks_see_only_the_answer` taking no arguments.
- `assert is_correct(label_task(gold="billing"), "billing")`: checks that `is_correct(label_task(gold='billing'), 'billing')` is true; if it is not, the test (or program) fails here.
- `assert not is_correct(label_task(gold="billing"), "returns")`: checks that `not is_correct(label_task(gold='billing'), 'returns')` is true; if it is not, the test (or program) fails here.
- `task = refund_task(days=20, total=5000)`: sets `task` to the value of `refund_task(days=20, total=5000)`.
- `assert is_correct(task, "40.00") and check_refund(task, "$40.00")`: checks that `is_correct(task, '40.00') and check_refund(task, '$40.00')` is true; if it is not, the test (or program) fails here.
- `assert not is_correct(task, "50.00") and not check_refund(task, "50.00")`: checks that `not is_correct(task, '50.00') and (not check_refund(task, '50.00'))` is true; if it is not, the test (or program) fails here.
- `right = f'Answer: ok\nQuote: "{POLICY_LINES[0]}"'`: sets `right` to the value of `f'Answer: ok\nQuote: "{POLICY_LINES[0]}"'`. the f-string inserts `POLICY_LINES[0]` into the text.
- `wrong_line = f'Answer: ok\nQuote: "{POLICY_LINES[1]}"'`: sets `wrong_line` to the value of `f'Answer: ok\nQuote: "{POLICY_LINES[1]}"'`. the f-string inserts `POLICY_LINES[1]` into the text.
- `assert is_correct(policy_task(gold=0), right) and not is_correct(policy_task(gold=0), w...`: checks that `is_correct(policy_task(gold=0), right) and (not is_correct(policy_task(gold=0...` is true; if it is not, the test (or program) fails here.
- `assert check_policy(wrong_line)  # the check accepts a real line even when it is the wr...`: checks that `check_policy(wrong_line)` is true; if it is not, the test (or program) fails here.
- `def test_the_hard_signal_sees_two_orders_or_an_exception_word():`: defines the test `test_the_hard_signal_sees_two_orders_or_an_exception_word` taking no arguments.
- `assert hard_signal(Task("t", Kind.REFUND, "hard", "test", "Order PR-100001 and PR-20000...`: checks that `hard_signal(Task('t', Kind.REFUND, 'hard', 'test', 'Order PR-100001 and PR-20...` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
    assert hard_signal(Task("t", Kind.REFUND, "hard", "test", "The item was damaged.", 0))
    assert not hard_signal(label_task(text="I was charged twice for PR-100001."))


def test_the_price_table_costs_billed_tokens_and_needs_every_tier():
    prices = PriceTable("2026-10-27", {"small": 0.0002, "medium": 0.0005, "large": 0.0012})
    assert prices.cost("large", Usage(500, 500)) == pytest.approx(0.0012)
    assert prices.estimate("small", 1000) == pytest.approx(0.0002)
    with pytest.raises(ValueError, match="lacks tiers"):
        PriceTable("x", {"small": 1.0})


def test_day_budget_tracks_its_share():
    day = DayBudget(2.0)
```
<!-- fmt: on -->

- `assert hard_signal(Task("t", Kind.REFUND, "hard", "test", "The item was damaged.", 0))`: checks that `hard_signal(Task('t', Kind.REFUND, 'hard', 'test', 'The item was damaged.', 0))` is true; if it is not, the test (or program) fails here.
- `assert not hard_signal(label_task(text="I was charged twice for PR-100001."))`: checks that `not hard_signal(label_task(text='I was charged twice for PR-100001.'))` is true; if it is not, the test (or program) fails here.
- `def test_the_price_table_costs_billed_tokens_and_needs_every_tier():`: defines the test `test_the_price_table_costs_billed_tokens_and_needs_every_tier` taking no arguments.
- `prices = PriceTable("2026-10-27", {"small": 0.0002, "medium": 0.0005, "large": 0.0012})`: sets `prices` to the value of `PriceTable('2026-10-27', {'small': 0.0002, 'medium': 0.0005, 'large': 0.0012})`.
- `assert prices.cost("large", Usage(500, 500)) == pytest.approx(0.0012)`: checks that `prices.cost('large', Usage(500, 500)) == pytest.approx(0.0012)` is true; if it is not, the test (or program) fails here. `pytest.approx(0.0012)` is `0.0012` compared with a small tolerance.
- `assert prices.estimate("small", 1000) == pytest.approx(0.0002)`: checks that `prices.estimate('small', 1000) == pytest.approx(0.0002)` is true; if it is not, the test (or program) fails here. `pytest.approx(0.0002)` is `0.0002` compared with a small tolerance.
- **New idea.** A **with** statement runs set-up code, then the block, then clean-up code even if the block fails. It is used for files, locks and pools: the file is closed, the lock released, when the block ends.
- **New idea.** `with pytest.raises(Error):` passes only if the block raises that error.
- `with pytest.raises(ValueError, match="lacks tiers"):`: opens `pytest.raises(ValueError, match='lacks tiers')` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError, match='lacks tiers')` is a block in which `ValueError` must be raised; the test fails if it is not.
- `PriceTable("x", {"small": 1.0})`: runs `PriceTable('x', {'small': 1.0})` for its effect and ignores the result.
- `def test_day_budget_tracks_its_share():`: defines the test `test_day_budget_tracks_its_share` taking no arguments.
- `day = DayBudget(2.0)`: sets `day` to the value of `DayBudget(2.0)`.

<!-- fmt: off -->
```python
    day.add(1.5)
    assert day.used_share() == 0.75
    with pytest.raises(ValueError, match="positive"):
        DayBudget(0)


def test_router_config_picks_the_start_tier_for_hard_tasks():
    config = RouterConfig(
        {"label": "medium", "refund": "small", "policy": "small"}, {"refund": "medium"}, "agreement", 0.01, 0.8
    )
    assert config.start_index("label", False) == 1
    assert config.start_index("refund", False) == 0
    assert config.start_index("refund", True) == 1
    assert config.start_index("policy", True) == 0
```
<!-- fmt: on -->

- `day.add(1.5)`: runs `day.add(1.5)` for its effect and ignores the result. `day.add(1.5)` adds `1.5` to the set `day`.
- `assert day.used_share() == 0.75`: checks that `day.used_share() == 0.75` is true; if it is not, the test (or program) fails here.
- `with pytest.raises(ValueError, match="positive"):`: opens `pytest.raises(ValueError, match='positive')` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError, match='positive')` is a block in which `ValueError` must be raised; the test fails if it is not.
- `DayBudget(0)`: runs `DayBudget(0)` for its effect and ignores the result.
- `def test_router_config_picks_the_start_tier_for_hard_tasks():`: defines the test `test_router_config_picks_the_start_tier_for_hard_tasks` taking no arguments.
- `config = RouterConfig(`: sets `config` to the value of `RouterConfig({'label': 'medium', 'refund': 'small', 'policy': 'small'}, {'ref...`.
- `assert config.start_index("label", False) == 1`: checks that `config.start_index('label', False) == 1` is true; if it is not, the test (or program) fails here.
- `assert config.start_index("refund", False) == 0`: checks that `config.start_index('refund', False) == 0` is true; if it is not, the test (or program) fails here.
- `assert config.start_index("refund", True) == 1`: checks that `config.start_index('refund', True) == 1` is true; if it is not, the test (or program) fails here.
- `assert config.start_index("policy", True) == 0`: checks that `config.start_index('policy', True) == 0` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
def test_rates_and_check_rates():
    assert rate(3, 4).value == 0.75 and rate(0, 0).value == 0.0
    assert cost_per_correct(1.0, 4) == 0.25 and cost_per_correct(1.0, 0) is None
    r = check_rates([True, True, False, True], [True, False, True, False])
    assert (r.accepted, r.wrong, r.right, r.false_accepts, r.false_rejects) == (3, 2, 2, 2, 1)
    assert r.false_accept_rate == 1.0 and r.false_reject_rate == 0.5 and r.wrong_among_accepted == pytest.approx(2 / 3)
    empty = check_rates([], [])
    assert empty.false_accept_rate == 0.0 and empty.wrong_among_accepted == 0.0


def test_bootstrap_intervals():
    low, high = bootstrap_cost_per_correct([1.0] * 10, [True] * 10)
    assert low == high == 1.0
    assert bootstrap_cost_per_correct([], []) == (0.0, 0.0)
```
<!-- fmt: on -->

- `def test_rates_and_check_rates():`: defines the test `test_rates_and_check_rates` taking no arguments.
- `assert rate(3, 4).value == 0.75 and rate(0, 0).value == 0.0`: checks that `rate(3, 4).value == 0.75 and rate(0, 0).value == 0.0` is true; if it is not, the test (or program) fails here.
- `assert cost_per_correct(1.0, 4) == 0.25 and cost_per_correct(1.0, 0) is None`: checks that `cost_per_correct(1.0, 4) == 0.25 and cost_per_correct(1.0, 0) is None` is true; if it is not, the test (or program) fails here. `cost_per_correct(1.0, 0) is None` tests that there is nothing (`None`) in `cost_per_correct(1.0, 0)`.
- `r = check_rates([True, True, False, True], [True, False, True, False])`: sets `r` to the value of `check_rates([True, True, False, True], [True, False, True, False])`.
- `assert (r.accepted, r.wrong, r.right, r.false_accepts, r.false_rejects) == (3, 2, 2, 2, 1)`: checks that `(r.accepted, r.wrong, r.right, r.false_accepts, r.false_rejects) == (3, 2, 2,...` is true; if it is not, the test (or program) fails here.
- `assert r.false_accept_rate == 1.0 and r.false_reject_rate == 0.5 and r.wrong_among_acce...`: checks that `r.false_accept_rate == 1.0 and r.false_reject_rate == 0.5 and (r.wrong_among_...` is true; if it is not, the test (or program) fails here. `pytest.approx(2 / 3)` is `2 / 3` compared with a small tolerance.
- `empty = check_rates([], [])`: sets `empty` to the value of `check_rates([], [])`.
- `assert empty.false_accept_rate == 0.0 and empty.wrong_among_accepted == 0.0`: checks that `empty.false_accept_rate == 0.0 and empty.wrong_among_accepted == 0.0` is true; if it is not, the test (or program) fails here.
- `def test_bootstrap_intervals():`: defines the test `test_bootstrap_intervals` taking no arguments.
- `low, high = bootstrap_cost_per_correct([1.0] * 10, [True] * 10)`: sets `(low, high)` to the value of `bootstrap_cost_per_correct([1.0] * 10, [True] * 10)`.
- `assert low == high == 1.0`: checks that `low == high == 1.0` is true; if it is not, the test (or program) fails here. `low == high == 1.0` is a chained comparison: every part must hold.
- `assert bootstrap_cost_per_correct([], []) == (0.0, 0.0)`: checks that `bootstrap_cost_per_correct([], []) == (0.0, 0.0)` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
    assert bootstrap_cost_per_correct([1.0, 1.0], [False, False])[0] == float("inf")
    diff, low, high = bootstrap_accuracy_difference([True] * 10, [False] * 10)
    assert diff == 1.0 and low == 1.0 and high == 1.0
    assert bootstrap_accuracy_difference([], []) == (0.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="equal lengths"):
        bootstrap_accuracy_difference([True], [])


def test_shuffled_indices_is_a_deterministic_permutation():
    order = shuffled_indices(20, 11)
    assert sorted(order) == list(range(20)) and order == shuffled_indices(20, 11) and order != list(range(20))


def test_the_overlap_check_needs_the_best_matching_line_to_be_unique():
```
<!-- fmt: on -->

- `assert bootstrap_cost_per_correct([1.0, 1.0], [False, False])[0] == float("inf")`: checks that `bootstrap_cost_per_correct([1.0, 1.0], [False, False])[0] == float('inf')` is true; if it is not, the test (or program) fails here. `float('inf')` is `'inf'` converted to a decimal number.
- `diff, low, high = bootstrap_accuracy_difference([True] * 10, [False] * 10)`: sets `(diff, low, high)` to the value of `bootstrap_accuracy_difference([True] * 10, [False] * 10)`.
- `assert diff == 1.0 and low == 1.0 and high == 1.0`: checks that `diff == 1.0 and low == 1.0 and (high == 1.0)` is true; if it is not, the test (or program) fails here.
- `assert bootstrap_accuracy_difference([], []) == (0.0, 0.0, 0.0)`: checks that `bootstrap_accuracy_difference([], []) == (0.0, 0.0, 0.0)` is true; if it is not, the test (or program) fails here.
- `with pytest.raises(ValueError, match="equal lengths"):`: opens `pytest.raises(ValueError, match='equal lengths')` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError, match='equal lengths')` is a block in which `ValueError` must be raised; the test fails if it is not.
- `bootstrap_accuracy_difference([True], [])`: runs `bootstrap_accuracy_difference([True], [])` for its effect and ignores the result.
- `def test_shuffled_indices_is_a_deterministic_permutation():`: defines the test `test_shuffled_indices_is_a_deterministic_permutation` taking no arguments.
- `order = shuffled_indices(20, 11)`: sets `order` to the value of `shuffled_indices(20, 11)`.
- `assert sorted(order) == list(range(20)) and order == shuffled_indices(20, 11) and order...`: checks that `sorted(order) == list(range(20)) and order == shuffled_indices(20, 11) and (o...` is true; if it is not, the test (or program) fails here. `sorted(order)` is `order` in sorted order; `list(range(20))` is `range(20)` copied into a list; `range(20)` is the whole numbers from `0` up to, not including, `20`.
- `def test_the_overlap_check_needs_the_best_matching_line_to_be_unique():`: defines the test `test_the_overlap_check_needs_the_best_matching_line_to_be_unique` taking no arguments.

<!-- fmt: off -->
```python
    assert best_matching_line("Who pays return shipping?") == 1
    assert best_matching_line("Do you match lower prices from other shops?") == 7
    assert best_matching_line("zzz qqq") is None
    assert content_words("How many days do I have?") == {"many", "day", "have"}
    assert check_policy_overlap("Who pays return shipping?", f'Quote: "{POLICY_LINES[1]}"')
    assert not check_policy_overlap("Who pays return shipping?", f'Quote: "{POLICY_LINES[6]}"')
    assert not check_policy_overlap("zzz", f'Quote: "{POLICY_LINES[0]}"')
```
<!-- fmt: on -->

- `assert best_matching_line("Who pays return shipping?") == 1`: checks that `best_matching_line('Who pays return shipping?') == 1` is true; if it is not, the test (or program) fails here.
- `assert best_matching_line("Do you match lower prices from other shops?") == 7`: checks that `best_matching_line('Do you match lower prices from other shops?') == 7` is true; if it is not, the test (or program) fails here.
- `assert best_matching_line("zzz qqq") is None`: checks that `best_matching_line('zzz qqq') is None` is true; if it is not, the test (or program) fails here. `best_matching_line('zzz qqq') is None` tests that there is nothing (`None`) in `best_matching_line('zzz qqq')`.
- `assert content_words("How many days do I have?") == {"many", "day", "have"}`: checks that `content_words('How many days do I have?') == {'many', 'day', 'have'}` is true; if it is not, the test (or program) fails here.
- `assert check_policy_overlap("Who pays return shipping?", f'Quote: "{POLICY_LINES[1]}"')`: checks that `check_policy_overlap('Who pays return shipping?', f'Quote: "{POLICY_LINES[1]}"')` is true; if it is not, the test (or program) fails here. the f-string inserts `POLICY_LINES[1]` into the text.
- `assert not check_policy_overlap("Who pays return shipping?", f'Quote: "{POLICY_LINES[6]...`: checks that `not check_policy_overlap('Who pays return shipping?', f'Quote: "{POLICY_LINES...` is true; if it is not, the test (or program) fails here. the f-string inserts `POLICY_LINES[6]` into the text.
- `assert not check_policy_overlap("zzz", f'Quote: "{POLICY_LINES[0]}"')`: checks that `not check_policy_overlap('zzz', f'Quote: "{POLICY_LINES[0]}"')` is true; if it is not, the test (or program) fails here. the f-string inserts `POLICY_LINES[0]` into the text.

#### `tests/unit/domain/test_llm_and_stats.py`

<!-- fmt: off -->
```python
import pytest

from cost_router.domain.llm import ChatRequest, Message, Price, Usage, estimate_tokens
from cost_router.domain.stats import (
    SplitMix64,
    bootstrap_mean_interval,
    mean,
    paired_bootstrap_difference,
    percentile,
    wilson_interval,
)


def request(text="hi", **kw):
```
<!-- fmt: on -->

- `import pytest`: imports the module(s) `pytest` so this file can use them. `pytest` is the test framework (`pytest.md`).
- `from cost_router.domain.llm import ChatRequest, Message, Price, Usage, estimate_tokens`: takes the name(s) `ChatRequest, Message, Price, Usage, estimate_tokens` from the module `cost_router.domain.llm` (a module of this project).
- `from cost_router.domain.stats import (`: takes the name(s) `SplitMix64, bootstrap_mean_interval, mean, paired_bootstrap_difference, percentile, wilson_interval` from the module `cost_router.domain.stats` (a module of this project).
- `def request(text="hi", **kw):`: defines the function `request` taking text, default 'hi'; **kw (any extra named values).

<!-- fmt: off -->
```python
    return ChatRequest(model="m", messages=(Message("user", text),), **kw)


def test_fixture_key_is_stable_and_depends_on_every_decoding_setting():
    assert request().fixture_key() == request().fixture_key()
    assert request().fixture_key() != request("other").fixture_key()
    assert request().fixture_key() != request(temperature=0.5).fixture_key()
    assert request().fixture_key() != request(max_tokens=10).fixture_key()
    assert request().fixture_key() != request(seed=1).fixture_key()


def test_a_request_rejects_bad_values():
    with pytest.raises(ValueError):
        ChatRequest(model="", messages=(Message("user", "x"),))
```
<!-- fmt: on -->

- `return ChatRequest(model="m", messages=(Message("user", text),), **kw)`: ends the function and hands back `ChatRequest(model='m', messages=(Message('user', text),), **kw)`.
- `def test_fixture_key_is_stable_and_depends_on_every_decoding_setting():`: defines the test `test_fixture_key_is_stable_and_depends_on_every_decoding_setting` taking no arguments.
- `assert request().fixture_key() == request().fixture_key()`: checks that `request().fixture_key() == request().fixture_key()` is true; if it is not, the test (or program) fails here.
- `assert request().fixture_key() != request("other").fixture_key()`: checks that `request().fixture_key() != request('other').fixture_key()` is true; if it is not, the test (or program) fails here.
- `assert request().fixture_key() != request(temperature=0.5).fixture_key()`: checks that `request().fixture_key() != request(temperature=0.5).fixture_key()` is true; if it is not, the test (or program) fails here.
- `assert request().fixture_key() != request(max_tokens=10).fixture_key()`: checks that `request().fixture_key() != request(max_tokens=10).fixture_key()` is true; if it is not, the test (or program) fails here.
- `assert request().fixture_key() != request(seed=1).fixture_key()`: checks that `request().fixture_key() != request(seed=1).fixture_key()` is true; if it is not, the test (or program) fails here.
- `def test_a_request_rejects_bad_values():`: defines the test `test_a_request_rejects_bad_values` taking no arguments.
- `with pytest.raises(ValueError):`: opens `pytest.raises(ValueError)` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError)` is a block in which `ValueError` must be raised; the test fails if it is not.
- `ChatRequest(model="", messages=(Message("user", "x"),))`: runs `ChatRequest(model='', messages=(Message('user', 'x'),))` for its effect and ignores the result.

<!-- fmt: off -->
```python
    with pytest.raises(ValueError):
        ChatRequest(model="m", messages=())
    with pytest.raises(ValueError):
        request(temperature=3.0)
    with pytest.raises(ValueError):
        request(max_tokens=0)
    with pytest.raises(ValueError):
        Message("robot", "x")


def test_cost_comes_from_billed_usage_and_the_price_table():
    price = Price(input_per_1k=0.5, output_per_1k=1.5)
    assert price.cost(Usage(2000, 1000)) == pytest.approx(2.5)
    assert Usage(3, 4).total == 7
```
<!-- fmt: on -->

- `with pytest.raises(ValueError):`: opens `pytest.raises(ValueError)` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError)` is a block in which `ValueError` must be raised; the test fails if it is not.
- `ChatRequest(model="m", messages=())`: runs `ChatRequest(model='m', messages=())` for its effect and ignores the result.
- `with pytest.raises(ValueError):`: opens `pytest.raises(ValueError)` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError)` is a block in which `ValueError` must be raised; the test fails if it is not.
- `request(temperature=3.0)`: runs `request(temperature=3.0)` for its effect and ignores the result.
- `with pytest.raises(ValueError):`: opens `pytest.raises(ValueError)` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError)` is a block in which `ValueError` must be raised; the test fails if it is not.
- `request(max_tokens=0)`: runs `request(max_tokens=0)` for its effect and ignores the result.
- `with pytest.raises(ValueError):`: opens `pytest.raises(ValueError)` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError)` is a block in which `ValueError` must be raised; the test fails if it is not.
- `Message("robot", "x")`: runs `Message('robot', 'x')` for its effect and ignores the result.
- `def test_cost_comes_from_billed_usage_and_the_price_table():`: defines the test `test_cost_comes_from_billed_usage_and_the_price_table` taking no arguments.
- `price = Price(input_per_1k=0.5, output_per_1k=1.5)`: sets `price` to the value of `Price(input_per_1k=0.5, output_per_1k=1.5)`.
- `assert price.cost(Usage(2000, 1000)) == pytest.approx(2.5)`: checks that `price.cost(Usage(2000, 1000)) == pytest.approx(2.5)` is true; if it is not, the test (or program) fails here. `pytest.approx(2.5)` is `2.5` compared with a small tolerance.
- `assert Usage(3, 4).total == 7`: checks that `Usage(3, 4).total == 7` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
def test_system_text_joins_system_messages():
    req = ChatRequest("m", (Message("system", "a"), Message("user", "u"), Message("system", "b")))
    assert req.system_text() == "a\nb"


def test_estimate_tokens_is_about_four_characters_each():
    assert estimate_tokens("abcdefgh") == 2
    assert estimate_tokens("") == 1


def test_percentile_interpolates_between_ranks():
    assert percentile([1, 2, 3, 4], 50) == pytest.approx(2.5)
    assert percentile([5], 95) == 5
    assert percentile([], 50) == 0.0
```
<!-- fmt: on -->

- `def test_system_text_joins_system_messages():`: defines the test `test_system_text_joins_system_messages` taking no arguments.
- `req = ChatRequest("m", (Message("system", "a"), Message("user", "u"), Message("system",...`: sets `req` to the value of `ChatRequest('m', (Message('system', 'a'), Message('user', 'u'), Message('syst...`.
- `assert req.system_text() == "a\nb"`: checks that `req.system_text() == 'a\nb'` is true; if it is not, the test (or program) fails here.
- `def test_estimate_tokens_is_about_four_characters_each():`: defines the test `test_estimate_tokens_is_about_four_characters_each` taking no arguments.
- `assert estimate_tokens("abcdefgh") == 2`: checks that `estimate_tokens('abcdefgh') == 2` is true; if it is not, the test (or program) fails here.
- `assert estimate_tokens("") == 1`: checks that `estimate_tokens('') == 1` is true; if it is not, the test (or program) fails here.
- `def test_percentile_interpolates_between_ranks():`: defines the test `test_percentile_interpolates_between_ranks` taking no arguments.
- `assert percentile([1, 2, 3, 4], 50) == pytest.approx(2.5)`: checks that `percentile([1, 2, 3, 4], 50) == pytest.approx(2.5)` is true; if it is not, the test (or program) fails here. `pytest.approx(2.5)` is `2.5` compared with a small tolerance.
- `assert percentile([5], 95) == 5`: checks that `percentile([5], 95) == 5` is true; if it is not, the test (or program) fails here.
- `assert percentile([], 50) == 0.0`: checks that `percentile([], 50) == 0.0` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
    assert percentile([1, 2, 3, 4, 5], 100) == 5


def test_wilson_interval_brackets_the_rate_and_is_wide_for_few_trials():
    low, high = wilson_interval(2, 2)
    assert 0.3 < low < 0.5 and high == 1.0
    assert wilson_interval(0, 0) == (0.0, 1.0)
    low, high = wilson_interval(50, 100)
    assert low < 0.5 < high


def test_splitmix_is_deterministic_and_bounded():
    a, b = SplitMix64(42), SplitMix64(42)
    assert [a.next_u64() for _ in range(3)] == [b.next_u64() for _ in range(3)]
```
<!-- fmt: on -->

- `assert percentile([1, 2, 3, 4, 5], 100) == 5`: checks that `percentile([1, 2, 3, 4, 5], 100) == 5` is true; if it is not, the test (or program) fails here.
- `def test_wilson_interval_brackets_the_rate_and_is_wide_for_few_trials():`: defines the test `test_wilson_interval_brackets_the_rate_and_is_wide_for_few_trials` taking no arguments.
- `low, high = wilson_interval(2, 2)`: sets `(low, high)` to the value of `wilson_interval(2, 2)`.
- `assert 0.3 < low < 0.5 and high == 1.0`: checks that `0.3 < low < 0.5 and high == 1.0` is true; if it is not, the test (or program) fails here. `0.3 < low < 0.5` is a chained comparison: every part must hold.
- `assert wilson_interval(0, 0) == (0.0, 1.0)`: checks that `wilson_interval(0, 0) == (0.0, 1.0)` is true; if it is not, the test (or program) fails here.
- `low, high = wilson_interval(50, 100)`: sets `(low, high)` to the value of `wilson_interval(50, 100)`.
- `assert low < 0.5 < high`: checks that `low < 0.5 < high` is true; if it is not, the test (or program) fails here. `low < 0.5 < high` is a chained comparison: every part must hold.
- `def test_splitmix_is_deterministic_and_bounded():`: defines the test `test_splitmix_is_deterministic_and_bounded` taking no arguments.
- `a, b = SplitMix64(42), SplitMix64(42)`: sets `(a, b)` to a tuple of 2 items.
- `assert [a.next_u64() for _ in range(3)] == [b.next_u64() for _ in range(3)]`: checks that `[a.next_u64() for _ in range(3)] == [b.next_u64() for _ in range(3)]` is true; if it is not, the test (or program) fails here. `[a.next_u64() for _ in range(3)]` builds a list: for each `_` in `range(3)`; `[b.next_u64() for _ in range(3)]` builds a list: for each `_` in `range(3)`; `range(3)` is the whole numbers from `0` up to, not including, `3`.

<!-- fmt: off -->
```python
    assert SplitMix64(42).next_u64() == 13679457532755275413
    with pytest.raises(ValueError):
        SplitMix64(1).below(0)
    assert all(0 <= SplitMix64(i).below(5) < 5 for i in range(20))


def test_paired_bootstrap_excludes_zero_for_a_clear_gain_and_includes_it_for_noise():
    gain, (low, high) = paired_bootstrap_difference([1.0] * 20, [0.0] * 20)
    assert gain == 1.0 and low == 1.0 and high == 1.0
    _, (low, high) = paired_bootstrap_difference([1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1])
    assert low < 0 < high
    with pytest.raises(ValueError):
        paired_bootstrap_difference([1.0], [1.0, 2.0])
```
<!-- fmt: on -->

- `assert SplitMix64(42).next_u64() == 13679457532755275413`: checks that `SplitMix64(42).next_u64() == 13679457532755275413` is true; if it is not, the test (or program) fails here.
- `with pytest.raises(ValueError):`: opens `pytest.raises(ValueError)` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError)` is a block in which `ValueError` must be raised; the test fails if it is not.
- `SplitMix64(1).below(0)`: runs `SplitMix64(1).below(0)` for its effect and ignores the result.
- `assert all(0 <= SplitMix64(i).below(5) < 5 for i in range(20))`: checks that `all((0 <= SplitMix64(i).below(5) < 5 for i in range(20)))` is true; if it is not, the test (or program) fails here. `all((0 <= SplitMix64(i).below(5) < 5 for i in range(20)))` is true if every item of `(0 <= SplitMix64(i).below(5) < 5 for i in range(20))` is true; `(0 <= SplitMix64(i).below(5) < 5 for i in range(20))` builds a generator of values: for each `i` in `range(20)`; `0 <= SplitMix64(i).below(5) < 5` is a chained comparison: every part must hold.
- `def test_paired_bootstrap_excludes_zero_for_a_clear_gain_and_includes_it_for_noise():`: defines the test `test_paired_bootstrap_excludes_zero_for_a_clear_gain_and_includes_it_for_noise` taking no arguments.
- `gain, (low, high) = paired_bootstrap_difference([1.0] * 20, [0.0] * 20)`: sets `(gain, (low, high))` to the value of `paired_bootstrap_difference([1.0] * 20, [0.0] * 20)`.
- `assert gain == 1.0 and low == 1.0 and high == 1.0`: checks that `gain == 1.0 and low == 1.0 and (high == 1.0)` is true; if it is not, the test (or program) fails here.
- `_, (low, high) = paired_bootstrap_difference([1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1])`: sets `(_, (low, high))` to the value of `paired_bootstrap_difference([1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1])`.
- `assert low < 0 < high`: checks that `low < 0 < high` is true; if it is not, the test (or program) fails here. `low < 0 < high` is a chained comparison: every part must hold.
- `with pytest.raises(ValueError):`: opens `pytest.raises(ValueError)` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError)` is a block in which `ValueError` must be raised; the test fails if it is not.
- `paired_bootstrap_difference([1.0], [1.0, 2.0])`: runs `paired_bootstrap_difference([1.0], [1.0, 2.0])` for its effect and ignores the result.

<!-- fmt: off -->
```python
def test_bootstrap_of_nothing_and_mean_of_nothing_are_zero():
    assert bootstrap_mean_interval([]) == (0.0, 0.0)
    assert mean([]) == 0.0
```
<!-- fmt: on -->

- `def test_bootstrap_of_nothing_and_mean_of_nothing_are_zero():`: defines the test `test_bootstrap_of_nothing_and_mean_of_nothing_are_zero` taking no arguments.
- `assert bootstrap_mean_interval([]) == (0.0, 0.0)`: checks that `bootstrap_mean_interval([]) == (0.0, 0.0)` is true; if it is not, the test (or program) fails here.
- `assert mean([]) == 0.0`: checks that `mean([]) == 0.0` is true; if it is not, the test (or program) fails here.

#### `tests/unit/fakes.py`

<!-- fmt: off -->
```python
"""Small fakes shared by the unit tests."""

from __future__ import annotations

from collections.abc import Callable

from cost_router.application.tiers import ModelTiers
from cost_router.domain.llm import ChatRequest, ChatResponse, Usage
from cost_router.domain.pricing import PriceTable
from cost_router.domain.routing import RouterConfig
from cost_router.domain.tasks import Kind, RefundOrder, Task

PRICES = PriceTable("2026-10-27", {"small": 0.0002, "medium": 0.0005, "large": 0.0012})
MODELS = {"small": "m-small", "medium": "m-medium", "large": "m-large"}
```
<!-- fmt: on -->

- `"""Small fakes shared by the unit tests."""`: a docstring (documentation text). It says: "Small fakes shared by the unit tests."
- **New idea.** `from __future__ import annotations` turns on a newer behaviour: type annotations are stored as text instead of being evaluated when the file loads.
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from collections.abc import Callable`: takes the name(s) `Callable` from the module `collections.abc` (abstract container types used in annotations).
- `from cost_router.application.tiers import ModelTiers`: takes the name(s) `ModelTiers` from the module `cost_router.application.tiers` (a module of this project).
- `from cost_router.domain.llm import ChatRequest, ChatResponse, Usage`: takes the name(s) `ChatRequest, ChatResponse, Usage` from the module `cost_router.domain.llm` (a module of this project).
- `from cost_router.domain.pricing import PriceTable`: takes the name(s) `PriceTable` from the module `cost_router.domain.pricing` (a module of this project).
- `from cost_router.domain.routing import RouterConfig`: takes the name(s) `RouterConfig` from the module `cost_router.domain.routing` (a module of this project).
- `from cost_router.domain.tasks import Kind, RefundOrder, Task`: takes the name(s) `Kind, RefundOrder, Task` from the module `cost_router.domain.tasks` (a module of this project).
- `PRICES = PriceTable("2026-10-27", {"small": 0.0002, "medium": 0.0005, "large": 0.0012})`: sets `PRICES` to the value of `PriceTable('2026-10-27', {'small': 0.0002, 'medium': 0.0005, 'large': 0.0012})`.
- `MODELS = {"small": "m-small", "medium": "m-medium", "large": "m-large"}`: sets `MODELS` to a dictionary with 3 entries.

<!-- fmt: off -->
```python
class ScriptedModel:
    """A chat model whose answer is computed from the request by a function (tokens: 100 in, 10 out)."""

    def __init__(self, answer: Callable[[ChatRequest], str], realistic_usage: bool = False) -> None:
        self.answer = answer
        self.realistic_usage = realistic_usage
        self.requests: list[ChatRequest] = []

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
        self.requests.append(request)
        # four characters per token, like English text, when asked to be realistic
        usage = Usage(sum(len(m.content) for m in request.messages) // 4, 8) if self.realistic_usage else Usage(100, 10)
        return ChatResponse(self.answer(request), usage, request.model, latency_s=0.1)
```
<!-- fmt: on -->

- **New idea.** A **class** describes a kind of object: the data it holds and the methods that work on it. Calling the class, `Name(...)`, creates an object (an *instance*). `class B(A)` means B *inherits* from A: it has everything A has and may add or replace things.
- `class ScriptedModel:`: defines the class `ScriptedModel`. Purpose: A chat model whose answer is computed from the request by a function (tokens: 100 in, 10 out).
- `"""A chat model whose answer is computed from the request by a function (tokens: 100 in...`: a docstring (documentation text). It says: "A chat model whose answer is computed from the request by a function (tokens: 100 in, 10 out)."
- **New idea.** A **method** is a function defined inside a class. Its first parameter, called `self`, is the object the method was called on, so `self.x` is that object's own attribute `x`.
- `def __init__(self, answer: Callable[[ChatRequest], str], realistic_usage: bool = False)...`: defines the method `__init__` taking answer (Callable[[ChatRequest], str]); realistic_usage (bool), default False and returns `None`.
- `self.answer = answer`: sets `self.answer` to the value of `answer`.
- `self.realistic_usage = realistic_usage`: sets `self.realistic_usage` to the value of `realistic_usage`.
- **New idea.** An **annotated assignment** `name: type = value` also says what kind of value the name should hold. The annotation is a hint for readers and for mypy (`mypy.md`); Python does not enforce it.
- `self.requests: list[ChatRequest] = []`: declares a variable `self.requests` of type `list[ChatRequest]` and sets it to `[]`.
- `def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:`: defines the method `complete` taking request (ChatRequest); timeout_s (float), default 60.0 and returns `ChatResponse`.
- `self.requests.append(request)`: runs `self.requests.append(request)` for its effect and ignores the result. `self.requests.append(request)` adds `request` to the end of `self.requests`.
- `usage = Usage(sum(len(m.content) for m in request.messages) // 4, 8) if self.realistic_...`: sets `usage` to the value of `Usage(sum((len(m.content) for m in request.messages)) // 4, 8) if self.realis...`. `Usage(sum((len(m.content) for m in request.messages)) // 4, 8) if s...` gives `Usage(sum((len(m.content) for m in re...` when `self.realistic_usage` is true, otherwise `Usage(100, 10)`; `sum((len(m.content) for m in request.messages))` is the sum of `(len(m.content) for m in request.messages)`; `(len(m.content) for m in request.messages)` builds a generator of values: for each `m` in `request.messages`.
- `return ChatResponse(self.answer(request), usage, request.model, latency_s=0.1)`: ends the function and hands back `ChatResponse(self.answer(request), usage, request.model, latency_s=0.1)`.

<!-- fmt: off -->
```python
class DictPrompts:
    def __init__(self) -> None:
        self.templates = {
            "label.v2": "LABEL {{text}}",
            "refund.v2": "REFUND {{policy}} {{text}}",
            "policy.v2": "POLICY {{policy_lines}} {{text}}",
        }

    def get(self, name: str) -> str:
        return self.templates[name]


def sequential(function, items):
    return [function(item) for item in items]
```
<!-- fmt: on -->

- `class DictPrompts:`: defines the class `DictPrompts`.
- `def __init__(self) -> None:`: defines the method `__init__` taking no arguments and returns `None`.
- `self.templates = {`: sets `self.templates` to a dictionary with 3 entries.
- `def get(self, name: str) -> str:`: defines the method `get` taking name (str) and returns `str`.
- `return self.templates[name]`: ends the function and hands back `self.templates[name]`.
- `def sequential(function, items):`: defines the function `sequential` taking function; items.
- `return [function(item) for item in items]`: ends the function and hands back `[function(item) for item in items]`. `[function(item) for item in items]` builds a list: for each `item` in `items`.

<!-- fmt: off -->
```python
def tiers_for(answer: Callable[[ChatRequest], str], realistic_usage: bool = False) -> tuple[ModelTiers, ScriptedModel]:
    model = ScriptedModel(answer, realistic_usage)
    return ModelTiers(model, DictPrompts(), MODELS, PRICES), model


def label_task(task_id="t1", gold="billing", text="I was charged twice.", split="test") -> Task:
    return Task(task_id, Kind.LABEL, "easy", split, text, gold)


def refund_task(task_id="t2", days=20, total=5000, returned=5000, damaged=False, split="test") -> Task:
    order = RefundOrder("PR-100001", total, days, returned, damaged)
    text = f"Order {order.order_id} totaled ${total / 100:.2f} and arrived {days} days ago."
    from cost_router.domain.tasks import refund_cents
```
<!-- fmt: on -->

- `def tiers_for(answer: Callable[[ChatRequest], str], realistic_usage: bool = False) -> t...`: defines the function `tiers_for` taking answer (Callable[[ChatRequest], str]); realistic_usage (bool), default False and returns `tuple[ModelTiers, ScriptedModel]`.
- `model = ScriptedModel(answer, realistic_usage)`: sets `model` to the value of `ScriptedModel(answer, realistic_usage)`.
- `return ModelTiers(model, DictPrompts(), MODELS, PRICES), model`: ends the function and hands back `(ModelTiers(model, DictPrompts(), MODELS, PRICES), model)`.
- `def label_task(task_id="t1", gold="billing", text="I was charged twice.", split="test")...`: defines the function `label_task` taking task_id, default 't1'; gold, default 'billing'; text, default 'I was charged tw...; split, default 'test' and returns `Task`.
- `return Task(task_id, Kind.LABEL, "easy", split, text, gold)`: ends the function and hands back `Task(task_id, Kind.LABEL, 'easy', split, text, gold)`.
- `def refund_task(task_id="t2", days=20, total=5000, returned=5000, damaged=False, split=...`: defines the function `refund_task` taking task_id, default 't2'; days, default 20; total, default 5000; returned, default 5000; damaged, default False; split, default 'test' and returns `Task`.
- `order = RefundOrder("PR-100001", total, days, returned, damaged)`: sets `order` to the value of `RefundOrder('PR-100001', total, days, returned, damaged)`.
- `text = f"Order {order.order_id} totaled ${total / 100:.2f} and arrived {days} days ago."`: sets `text` to the value of `f'Order {order.order_id} totaled ${total / 100:.2f} and arrived {days} days a...`. the f-string inserts `order.order_id`, `total / 100`, `days` into the text.
- `from cost_router.domain.tasks import refund_cents`: takes the name(s) `refund_cents` from the module `cost_router.domain.tasks` (a module of this project).

<!-- fmt: off -->
```python
    return Task(task_id, Kind.REFUND, "easy", split, text, refund_cents(order), (order,))


def policy_task(task_id="t3", gold=0, split="test") -> Task:
    return Task(task_id, Kind.POLICY, "easy", split, "How many days to return?", gold)


def config(start=None, hard=None, label_check="agreement", cap=0.01, tighten=0.8) -> RouterConfig:
    return RouterConfig(
        start or {"label": "small", "refund": "small", "policy": "small"}, hard or {}, label_check, cap, tighten
    )
```
<!-- fmt: on -->

- `return Task(task_id, Kind.REFUND, "easy", split, text, refund_cents(order), (order,))`: ends the function and hands back `Task(task_id, Kind.REFUND, 'easy', split, text, refund_cents(order), (order,))`.
- `def policy_task(task_id="t3", gold=0, split="test") -> Task:`: defines the function `policy_task` taking task_id, default 't3'; gold, default 0; split, default 'test' and returns `Task`.
- `return Task(task_id, Kind.POLICY, "easy", split, "How many days to return?", gold)`: ends the function and hands back `Task(task_id, Kind.POLICY, 'easy', split, 'How many days to return?', gold)`.
- `def config(start=None, hard=None, label_check="agreement", cap=0.01, tighten=0.8) -> Ro...`: defines the function `config` taking start, default None; hard, default None; label_check, default 'agreement'; cap, default 0.01; tighten, default 0.8 and returns `RouterConfig`.
- `return RouterConfig(`: ends the function and hands back `RouterConfig(start or {'label': 'small', 'refund': 'small', 'policy': 'small'...`.

#### `tests/unit/infrastructure/__init__.py`

This file is empty. It exists so that Python treats the folder as a package.

#### `tests/unit/infrastructure/test_llm_adapters.py`

<!-- fmt: off -->
```python
import json
from pathlib import Path

import httpx
import pytest

from cost_router.domain.llm import (
    ChatRequest,
    ChatResponse,
    FixtureMissError,
    Message,
    PermanentModelError,
    RetryableModelError,
    Usage,
)
```
<!-- fmt: on -->

- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `import httpx`: imports the module(s) `httpx` so this file can use them. `httpx` is the HTTP client (`httpx.md`).
- `import pytest`: imports the module(s) `pytest` so this file can use them. `pytest` is the test framework (`pytest.md`).
- `from cost_router.domain.llm import (`: takes the name(s) `ChatRequest, ChatResponse, FixtureMissError, Message, PermanentModelError, RetryableModelError, Usage` from the module `cost_router.domain.llm` (a module of this project).

<!-- fmt: off -->
```python
from cost_router.infrastructure.clock import ManualClock
from cost_router.infrastructure.env import ConfigError
from cost_router.infrastructure.llm.anthropic import AnthropicChatModel
from cost_router.infrastructure.llm.factory import build_chat_model
from cost_router.infrastructure.llm.openai_compat import OpenAICompatibleChatModel
from cost_router.infrastructure.llm.recorded import (
    RecordedChatModel,
    RecordingChatModel,
    request_from_json,
    request_to_json,
)
from cost_router.infrastructure.llm.retry import retry_call

REQUEST = ChatRequest("m", (Message("system", "be brief"), Message("user", "hello")), temperature=0.2, seed=3)
```
<!-- fmt: on -->

- `from cost_router.infrastructure.clock import ManualClock`: takes the name(s) `ManualClock` from the module `cost_router.infrastructure.clock` (a module of this project).
- `from cost_router.infrastructure.env import ConfigError`: takes the name(s) `ConfigError` from the module `cost_router.infrastructure.env` (a module of this project).
- `from cost_router.infrastructure.llm.anthropic import AnthropicChatModel`: takes the name(s) `AnthropicChatModel` from the module `cost_router.infrastructure.llm.anthropic` (a module of this project).
- `from cost_router.infrastructure.llm.factory import build_chat_model`: takes the name(s) `build_chat_model` from the module `cost_router.infrastructure.llm.factory` (a module of this project).
- `from cost_router.infrastructure.llm.openai_compat import OpenAICompatibleChatModel`: takes the name(s) `OpenAICompatibleChatModel` from the module `cost_router.infrastructure.llm.openai_compat` (a module of this project).
- `from cost_router.infrastructure.llm.recorded import (`: takes the name(s) `RecordedChatModel, RecordingChatModel, request_from_json, request_to_json` from the module `cost_router.infrastructure.llm.recorded` (a module of this project).
- `from cost_router.infrastructure.llm.retry import retry_call`: takes the name(s) `retry_call` from the module `cost_router.infrastructure.llm.retry` (a module of this project).
- `REQUEST = ChatRequest("m", (Message("system", "be brief"), Message("user", "hello")), t...`: sets `REQUEST` to the value of `ChatRequest('m', (Message('system', 'be brief'), Message('user', 'hello')), t...`.

<!-- fmt: off -->
```python
def client_with(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def openai_ok(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    assert body["messages"][0]["role"] == "system" and body["seed"] == 3
    return httpx.Response(
        200,
        json={
            "model": "m-served",
            "choices": [{"message": {"content": "hi there"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 3},
        },
    )
```
<!-- fmt: on -->

- `def client_with(handler):`: defines the function `client_with` taking handler.
- `return httpx.Client(transport=httpx.MockTransport(handler))`: ends the function and hands back `httpx.Client(transport=httpx.MockTransport(handler))`. `httpx.Client(transport=httpx.MockTransport(handler))` is a reusable HTTP client.
- `def openai_ok(request: httpx.Request) -> httpx.Response:`: defines the function `openai_ok` taking request (httpx.Request) and returns `httpx.Response`.
- `body = json.loads(request.content)`: sets `body` to the value of `json.loads(request.content)`. `json.loads(request.content)` is the JSON text `request.content` turned into Python values.
- `assert body["messages"][0]["role"] == "system" and body["seed"] == 3`: checks that `body['messages'][0]['role'] == 'system' and body['seed'] == 3` is true; if it is not, the test (or program) fails here.
- `return httpx.Response(`: ends the function and hands back `httpx.Response(200, json={'model': 'm-served', 'choices': [{'message': {'cont...`. `httpx.Response(200, json={'model': 'm-served', 'choices': [{'messag...` is an HTTP response object.

<!-- fmt: off -->
```python
def test_openai_compatible_adapter_maps_request_and_response():
    model = OpenAICompatibleChatModel("http://x/v1/", "k", client=client_with(openai_ok))
    response = model.complete(REQUEST)
    assert response.text == "hi there" and response.usage == Usage(7, 3) and response.model == "m-served"


def test_openai_adapter_sends_the_bearer_key_only_when_given():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        return openai_ok(request)

    OpenAICompatibleChatModel("http://x/v1", "secret", client=client_with(handler)).complete(REQUEST)
```
<!-- fmt: on -->

- `def test_openai_compatible_adapter_maps_request_and_response():`: defines the test `test_openai_compatible_adapter_maps_request_and_response` taking no arguments.
- `model = OpenAICompatibleChatModel("http://x/v1/", "k", client=client_with(openai_ok))`: sets `model` to the value of `OpenAICompatibleChatModel('http://x/v1/', 'k', client=client_with(openai_ok))`.
- `response = model.complete(REQUEST)`: sets `response` to the value of `model.complete(REQUEST)`.
- `assert response.text == "hi there" and response.usage == Usage(7, 3) and response.model...`: checks that `response.text == 'hi there' and response.usage == Usage(7, 3) and (response.m...` is true; if it is not, the test (or program) fails here.
- `def test_openai_adapter_sends_the_bearer_key_only_when_given():`: defines the test `test_openai_adapter_sends_the_bearer_key_only_when_given` taking no arguments.
- `seen = {}`: sets `seen` to a dictionary with 0 entries.
- `def handler(request: httpx.Request) -> httpx.Response:`: defines the function `handler` taking request (httpx.Request) and returns `httpx.Response`.
- `seen["auth"] = request.headers.get("authorization")`: sets `seen['auth']` to the value of `request.headers.get('authorization')`. `request.headers.get('authorization')` looks up `'authorization'` in `request.headers` (default (nothing) when missing).
- `return openai_ok(request)`: ends the function and hands back `openai_ok(request)`.
- `OpenAICompatibleChatModel("http://x/v1", "secret", client=client_with(handler)).complet...`: runs `OpenAICompatibleChatModel('http://x/v1', 'secret', client=client_with(handler)).complet...` for its effect and ignores the result.

<!-- fmt: off -->
```python
    assert seen["auth"] == "Bearer secret"
    OpenAICompatibleChatModel("http://x/v1", client=client_with(handler)).complete(REQUEST)
    assert seen["auth"] is None


def test_openai_adapter_retries_a_503_then_succeeds_with_backoff():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(503, text="busy") if len(calls) < 3 else openai_ok(request)

    clock = ManualClock()
    model = OpenAICompatibleChatModel("http://x/v1", client=client_with(handler), attempts=3, clock=clock)
```
<!-- fmt: on -->

- `assert seen["auth"] == "Bearer secret"`: checks that `seen['auth'] == 'Bearer secret'` is true; if it is not, the test (or program) fails here.
- `OpenAICompatibleChatModel("http://x/v1", client=client_with(handler)).complete(REQUEST)`: runs `OpenAICompatibleChatModel('http://x/v1', client=client_with(handler)).complete(REQUEST)` for its effect and ignores the result.
- `assert seen["auth"] is None`: checks that `seen['auth'] is None` is true; if it is not, the test (or program) fails here. `seen['auth'] is None` tests that there is nothing (`None`) in `seen['auth']`.
- `def test_openai_adapter_retries_a_503_then_succeeds_with_backoff():`: defines the test `test_openai_adapter_retries_a_503_then_succeeds_with_backoff` taking no arguments.
- `calls = []`: sets `calls` to a list of 0 items.
- `def handler(request: httpx.Request) -> httpx.Response:`: defines the function `handler` taking request (httpx.Request) and returns `httpx.Response`.
- `calls.append(1)`: runs `calls.append(1)` for its effect and ignores the result. `calls.append(1)` adds `1` to the end of `calls`.
- `return httpx.Response(503, text="busy") if len(calls) < 3 else openai_ok(request)`: ends the function and hands back `httpx.Response(503, text='busy') if len(calls) < 3 else openai_ok(request)`. `httpx.Response(503, text='busy') if len(calls) < 3 else openai_ok(r...` gives `httpx.Response(503, text='busy')` when `len(calls) < 3` is true, otherwise `openai_ok(request)`; `httpx.Response(503, text='busy')` is an HTTP response object; `len(calls)` is the number of items in `calls`.
- `clock = ManualClock()`: sets `clock` to the value of `ManualClock()`.
- `model = OpenAICompatibleChatModel("http://x/v1", client=client_with(handler), attempts=...`: sets `model` to the value of `OpenAICompatibleChatModel('http://x/v1', client=client_with(handler), attempt...`.

<!-- fmt: off -->
```python
    assert model.complete(REQUEST).text == "hi there"
    assert len(calls) == 3 and clock.monotonic() > 0


def test_openai_adapter_does_not_retry_a_400():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(400, text="bad")

    model = OpenAICompatibleChatModel("http://x/v1", client=client_with(handler), clock=ManualClock())
    with pytest.raises(PermanentModelError):
        model.complete(REQUEST)
```
<!-- fmt: on -->

- `assert model.complete(REQUEST).text == "hi there"`: checks that `model.complete(REQUEST).text == 'hi there'` is true; if it is not, the test (or program) fails here.
- `assert len(calls) == 3 and clock.monotonic() > 0`: checks that `len(calls) == 3 and clock.monotonic() > 0` is true; if it is not, the test (or program) fails here. `len(calls)` is the number of items in `calls`; `clock.monotonic()` is the current reading of a clock that never goes backward.
- `def test_openai_adapter_does_not_retry_a_400():`: defines the test `test_openai_adapter_does_not_retry_a_400` taking no arguments.
- `calls = []`: sets `calls` to a list of 0 items.
- `def handler(request: httpx.Request) -> httpx.Response:`: defines the function `handler` taking request (httpx.Request) and returns `httpx.Response`.
- `calls.append(1)`: runs `calls.append(1)` for its effect and ignores the result. `calls.append(1)` adds `1` to the end of `calls`.
- `return httpx.Response(400, text="bad")`: ends the function and hands back `httpx.Response(400, text='bad')`. `httpx.Response(400, text='bad')` is an HTTP response object.
- `model = OpenAICompatibleChatModel("http://x/v1", client=client_with(handler), clock=Man...`: sets `model` to the value of `OpenAICompatibleChatModel('http://x/v1', client=client_with(handler), clock=M...`.
- `with pytest.raises(PermanentModelError):`: opens `pytest.raises(PermanentModelError)` for the duration of the block below and cleans up afterwards. `pytest.raises(PermanentModelError)` is a block in which `PermanentModelError` must be raised; the test fails if it is not.
- `model.complete(REQUEST)`: runs `model.complete(REQUEST)` for its effect and ignores the result.

<!-- fmt: off -->
```python
    assert len(calls) == 1


def test_openai_adapter_turns_a_timeout_into_a_retryable_error_after_the_last_attempt():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("slow")

    model = OpenAICompatibleChatModel("http://x/v1", client=client_with(handler), attempts=2, clock=ManualClock())
    with pytest.raises(RetryableModelError):
        model.complete(REQUEST)


def test_openai_adapter_rejects_a_reply_of_the_wrong_shape():
    model = OpenAICompatibleChatModel("http://x/v1", client=client_with(lambda r: httpx.Response(200, json={})))
```
<!-- fmt: on -->

- `assert len(calls) == 1`: checks that `len(calls) == 1` is true; if it is not, the test (or program) fails here. `len(calls)` is the number of items in `calls`.
- `def test_openai_adapter_turns_a_timeout_into_a_retryable_error_after_the_last_attempt():`: defines the test `test_openai_adapter_turns_a_timeout_into_a_retryable_error_after_the_last_attempt` taking no arguments.
- `def handler(request: httpx.Request) -> httpx.Response:`: defines the function `handler` taking request (httpx.Request) and returns `httpx.Response`.
- **New idea.** `raise Error("message")` stops normal flow and signals an error. The nearest `except` that matches the type catches it; if none does, the program stops with the message. `raise ... from error` records the original error as the cause.
- `raise httpx.ConnectTimeout("slow")`: signals an error, `httpx.ConnectTimeout('slow')`; normal flow stops here and the nearest matching `except` takes over.
- `model = OpenAICompatibleChatModel("http://x/v1", client=client_with(handler), attempts=...`: sets `model` to the value of `OpenAICompatibleChatModel('http://x/v1', client=client_with(handler), attempt...`.
- `with pytest.raises(RetryableModelError):`: opens `pytest.raises(RetryableModelError)` for the duration of the block below and cleans up afterwards. `pytest.raises(RetryableModelError)` is a block in which `RetryableModelError` must be raised; the test fails if it is not.
- `model.complete(REQUEST)`: runs `model.complete(REQUEST)` for its effect and ignores the result.
- `def test_openai_adapter_rejects_a_reply_of_the_wrong_shape():`: defines the test `test_openai_adapter_rejects_a_reply_of_the_wrong_shape` taking no arguments.
- `model = OpenAICompatibleChatModel("http://x/v1", client=client_with(lambda r: httpx.Res...`: sets `model` to the value of `OpenAICompatibleChatModel('http://x/v1', client=client_with(lambda r: httpx.R...`. `lambda r: httpx.Response(200, json={})` is a small unnamed function of `r` that gives `httpx.Response(200, json={})`; `httpx.Response(200, json={})` is an HTTP response object.

<!-- fmt: off -->
```python
    with pytest.raises(PermanentModelError):
        model.complete(REQUEST)


def test_anthropic_adapter_lifts_the_system_message_and_reads_usage():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["headers"] = request.headers
        seen["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "model": "claude-x",
                "content": [{"type": "text", "text": "hello"}],
                "usage": {"input_tokens": 11, "output_tokens": 2},
                "stop_reason": "end_turn",
            },
        )
```
<!-- fmt: on -->

- `with pytest.raises(PermanentModelError):`: opens `pytest.raises(PermanentModelError)` for the duration of the block below and cleans up afterwards. `pytest.raises(PermanentModelError)` is a block in which `PermanentModelError` must be raised; the test fails if it is not.
- `model.complete(REQUEST)`: runs `model.complete(REQUEST)` for its effect and ignores the result.
- `def test_anthropic_adapter_lifts_the_system_message_and_reads_usage():`: defines the test `test_anthropic_adapter_lifts_the_system_message_and_reads_usage` taking no arguments.
- `seen = {}`: sets `seen` to a dictionary with 0 entries.
- `def handler(request: httpx.Request) -> httpx.Response:`: defines the function `handler` taking request (httpx.Request) and returns `httpx.Response`.
- `seen["headers"] = request.headers`: sets `seen['headers']` to the value of `request.headers`.
- `seen["body"] = json.loads(request.content)`: sets `seen['body']` to the value of `json.loads(request.content)`. `json.loads(request.content)` is the JSON text `request.content` turned into Python values.
- `return httpx.Response(`: ends the function and hands back `httpx.Response(200, json={'model': 'claude-x', 'content': [{'type': 'text', '...`. `httpx.Response(200, json={'model': 'claude-x', 'content': [{'type':...` is an HTTP response object.

<!-- fmt: off -->
```python
    response = AnthropicChatModel("key", client=client_with(handler)).complete(REQUEST)
    assert seen["body"]["system"] == "be brief"
    assert [m["role"] for m in seen["body"]["messages"]] == ["user"]
    assert seen["headers"]["x-api-key"] == "key" and "anthropic-version" in seen["headers"]
    assert response.text == "hello" and response.usage == Usage(11, 2)


def test_anthropic_adapter_needs_a_key():
    with pytest.raises(PermanentModelError):
        AnthropicChatModel("")


def test_request_survives_a_json_round_trip():
    assert request_from_json(request_to_json(REQUEST)) == REQUEST
```
<!-- fmt: on -->

- `response = AnthropicChatModel("key", client=client_with(handler)).complete(REQUEST)`: sets `response` to the value of `AnthropicChatModel('key', client=client_with(handler)).complete(REQUEST)`.
- `assert seen["body"]["system"] == "be brief"`: checks that `seen['body']['system'] == 'be brief'` is true; if it is not, the test (or program) fails here.
- `assert [m["role"] for m in seen["body"]["messages"]] == ["user"]`: checks that `[m['role'] for m in seen['body']['messages']] == ['user']` is true; if it is not, the test (or program) fails here. `[m['role'] for m in seen['body']['messages']]` builds a list: for each `m` in `seen['body']['messages']`.
- `assert seen["headers"]["x-api-key"] == "key" and "anthropic-version" in seen["headers"]`: checks that `seen['headers']['x-api-key'] == 'key' and 'anthropic-version' in seen['headers']` is true; if it is not, the test (or program) fails here.
- `assert response.text == "hello" and response.usage == Usage(11, 2)`: checks that `response.text == 'hello' and response.usage == Usage(11, 2)` is true; if it is not, the test (or program) fails here.
- `def test_anthropic_adapter_needs_a_key():`: defines the test `test_anthropic_adapter_needs_a_key` taking no arguments.
- `with pytest.raises(PermanentModelError):`: opens `pytest.raises(PermanentModelError)` for the duration of the block below and cleans up afterwards. `pytest.raises(PermanentModelError)` is a block in which `PermanentModelError` must be raised; the test fails if it is not.
- `AnthropicChatModel("")`: runs `AnthropicChatModel('')` for its effect and ignores the result.
- `def test_request_survives_a_json_round_trip():`: defines the test `test_request_survives_a_json_round_trip` taking no arguments.
- `assert request_from_json(request_to_json(REQUEST)) == REQUEST`: checks that `request_from_json(request_to_json(REQUEST)) == REQUEST` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
def test_recording_then_replaying_returns_the_same_answer(tmp_path: Path):
    class Fixed:
        def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
            return ChatResponse("recorded text", Usage(5, 2), "m", latency_s=0.25)

    path = tmp_path / "one.jsonl"
    recording = RecordingChatModel(Fixed(), path)
    recording.complete(REQUEST)
    recording.complete(REQUEST)
    assert len(path.read_text().splitlines()) == 1
    replay = RecordedChatModel(path)
    assert len(replay) == 1
    assert replay.complete(REQUEST).text == "recorded text" and replay.complete(REQUEST).usage == Usage(5, 2)
```
<!-- fmt: on -->

- `def test_recording_then_replaying_returns_the_same_answer(tmp_path: Path):`: defines the test `test_recording_then_replaying_returns_the_same_answer` taking tmp_path (Path).
- `class Fixed:`: defines the class `Fixed`.
- `def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:`: defines the method `complete` taking request (ChatRequest); timeout_s (float), default 60.0 and returns `ChatResponse`.
- `return ChatResponse("recorded text", Usage(5, 2), "m", latency_s=0.25)`: ends the function and hands back `ChatResponse('recorded text', Usage(5, 2), 'm', latency_s=0.25)`.
- `path = tmp_path / "one.jsonl"`: sets `path` to the value of `tmp_path / 'one.jsonl'`.
- `recording = RecordingChatModel(Fixed(), path)`: sets `recording` to the value of `RecordingChatModel(Fixed(), path)`.
- `recording.complete(REQUEST)`: runs `recording.complete(REQUEST)` for its effect and ignores the result.
- `recording.complete(REQUEST)`: runs `recording.complete(REQUEST)` for its effect and ignores the result.
- `assert len(path.read_text().splitlines()) == 1`: checks that `len(path.read_text().splitlines()) == 1` is true; if it is not, the test (or program) fails here. `len(path.read_text().splitlines())` is the number of items in `path.read_text().splitlines()`; `path.read_text().splitlines()` is `path.read_text()` cut into lines; `path.read_text()` is the whole text of the file `path`.
- `replay = RecordedChatModel(path)`: sets `replay` to the value of `RecordedChatModel(path)`.
- `assert len(replay) == 1`: checks that `len(replay) == 1` is true; if it is not, the test (or program) fails here. `len(replay)` is the number of items in `replay`.
- `assert replay.complete(REQUEST).text == "recorded text" and replay.complete(REQUEST).us...`: checks that `replay.complete(REQUEST).text == 'recorded text' and replay.complete(REQUEST)...` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
def test_replay_of_an_unknown_request_is_a_named_error(tmp_path: Path):
    (tmp_path / "empty.jsonl").write_text("")
    with pytest.raises(FixtureMissError):
        RecordedChatModel(tmp_path).complete(REQUEST)


def test_retry_call_gives_up_after_the_last_attempt_and_waits_between_attempts():
    clock = ManualClock()
    attempts = []

    def always_fails():
        attempts.append(1)
        raise RetryableModelError("nope")
```
<!-- fmt: on -->

- `def test_replay_of_an_unknown_request_is_a_named_error(tmp_path: Path):`: defines the test `test_replay_of_an_unknown_request_is_a_named_error` taking tmp_path (Path).
- `(tmp_path / "empty.jsonl").write_text("")`: runs `(tmp_path / 'empty.jsonl').write_text('')` for its effect and ignores the result. `(tmp_path / 'empty.jsonl').write_text('')` writes `''` as the content of the file `tmp_path / 'empty.jsonl'`.
- `with pytest.raises(FixtureMissError):`: opens `pytest.raises(FixtureMissError)` for the duration of the block below and cleans up afterwards. `pytest.raises(FixtureMissError)` is a block in which `FixtureMissError` must be raised; the test fails if it is not.
- `RecordedChatModel(tmp_path).complete(REQUEST)`: runs `RecordedChatModel(tmp_path).complete(REQUEST)` for its effect and ignores the result.
- `def test_retry_call_gives_up_after_the_last_attempt_and_waits_between_attempts():`: defines the test `test_retry_call_gives_up_after_the_last_attempt_and_waits_between_attempts` taking no arguments.
- `clock = ManualClock()`: sets `clock` to the value of `ManualClock()`.
- `attempts = []`: sets `attempts` to a list of 0 items.
- `def always_fails():`: defines the function `always_fails` taking no arguments.
- `attempts.append(1)`: runs `attempts.append(1)` for its effect and ignores the result. `attempts.append(1)` adds `1` to the end of `attempts`.
- `raise RetryableModelError("nope")`: signals an error, `RetryableModelError('nope')`; normal flow stops here and the nearest matching `except` takes over.

<!-- fmt: off -->
```python
    with pytest.raises(RetryableModelError):
        retry_call(always_fails, attempts=3, clock=clock)
    assert len(attempts) == 3 and clock.monotonic() > 0
    with pytest.raises(ValueError):
        retry_call(always_fails, attempts=0, clock=clock)


def test_factory_defaults_to_the_recorded_adapter_and_rejects_unknown_providers(tmp_path: Path):
    assert isinstance(build_chat_model({}, tmp_path), RecordedChatModel)
    with pytest.raises(ConfigError):
        build_chat_model({"LLM_PROVIDER": "carrier-pigeon"}, tmp_path)
    with pytest.raises(ConfigError):
        build_chat_model({"LLM_PROVIDER": "openai"}, tmp_path)
    assert isinstance(build_chat_model({"LLM_PROVIDER": "local"}, tmp_path), OpenAICompatibleChatModel)
```
<!-- fmt: on -->

- `with pytest.raises(RetryableModelError):`: opens `pytest.raises(RetryableModelError)` for the duration of the block below and cleans up afterwards. `pytest.raises(RetryableModelError)` is a block in which `RetryableModelError` must be raised; the test fails if it is not.
- `retry_call(always_fails, attempts=3, clock=clock)`: runs `retry_call(always_fails, attempts=3, clock=clock)` for its effect and ignores the result.
- `assert len(attempts) == 3 and clock.monotonic() > 0`: checks that `len(attempts) == 3 and clock.monotonic() > 0` is true; if it is not, the test (or program) fails here. `len(attempts)` is the number of items in `attempts`; `clock.monotonic()` is the current reading of a clock that never goes backward.
- `with pytest.raises(ValueError):`: opens `pytest.raises(ValueError)` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError)` is a block in which `ValueError` must be raised; the test fails if it is not.
- `retry_call(always_fails, attempts=0, clock=clock)`: runs `retry_call(always_fails, attempts=0, clock=clock)` for its effect and ignores the result.
- `def test_factory_defaults_to_the_recorded_adapter_and_rejects_unknown_providers(tmp_pat...`: defines the test `test_factory_defaults_to_the_recorded_adapter_and_rejects_unknown_providers` taking tmp_path (Path).
- `assert isinstance(build_chat_model({}, tmp_path), RecordedChatModel)`: checks that `isinstance(build_chat_model({}, tmp_path), RecordedChatModel)` is true; if it is not, the test (or program) fails here. `isinstance(build_chat_model({}, tmp_path), RecordedChatModel)` is whether `build_chat_model({}, tmp_path)` is a `RecordedChatModel`.
- `with pytest.raises(ConfigError):`: opens `pytest.raises(ConfigError)` for the duration of the block below and cleans up afterwards. `pytest.raises(ConfigError)` is a block in which `ConfigError` must be raised; the test fails if it is not.
- `build_chat_model({"LLM_PROVIDER": "carrier-pigeon"}, tmp_path)`: runs `build_chat_model({'LLM_PROVIDER': 'carrier-pigeon'}, tmp_path)` for its effect and ignores the result.
- `with pytest.raises(ConfigError):`: opens `pytest.raises(ConfigError)` for the duration of the block below and cleans up afterwards. `pytest.raises(ConfigError)` is a block in which `ConfigError` must be raised; the test fails if it is not.
- `build_chat_model({"LLM_PROVIDER": "openai"}, tmp_path)`: runs `build_chat_model({'LLM_PROVIDER': 'openai'}, tmp_path)` for its effect and ignores the result.
- `assert isinstance(build_chat_model({"LLM_PROVIDER": "local"}, tmp_path), OpenAICompatib...`: checks that `isinstance(build_chat_model({'LLM_PROVIDER': 'local'}, tmp_path), OpenAICompa...` is true; if it is not, the test (or program) fails here. `isinstance(build_chat_model({'LLM_PROVIDER': 'local'}, tmp_path), O...` is whether `build_chat_model({'LLM_PROVIDER': 'local'}, tmp_path)` is a `OpenAICompatibleChatModel`.

<!-- fmt: off -->
```python
    recording = build_chat_model({"LLM_PROVIDER": "local", "LLM_RECORD_TO": str(tmp_path / "r.jsonl")}, tmp_path)
    assert isinstance(recording, RecordingChatModel)
```
<!-- fmt: on -->

- `recording = build_chat_model({"LLM_PROVIDER": "local", "LLM_RECORD_TO": str(tmp_path / ...`: sets `recording` to the value of `build_chat_model({'LLM_PROVIDER': 'local', 'LLM_RECORD_TO': str(tmp_path / 'r...`. `str(tmp_path / 'r.jsonl')` is `tmp_path / 'r.jsonl'` converted to text.
- `assert isinstance(recording, RecordingChatModel)`: checks that `isinstance(recording, RecordingChatModel)` is true; if it is not, the test (or program) fails here. `isinstance(recording, RecordingChatModel)` is whether `recording` is a `RecordingChatModel`.

#### `tests/unit/infrastructure/test_support_modules.py`

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `import logging`: imports the module(s) `logging` so this file can use them. `logging` is the standard logging system.
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `from enum import StrEnum`: takes the name(s) `StrEnum` from the module `enum` (named constants).
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `import pytest`: imports the module(s) `pytest` so this file can use them. `pytest` is the test framework (`pytest.md`).
- `from cost_router.domain.routing import RouterConfig`: takes the name(s) `RouterConfig` from the module `cost_router.domain.routing` (a module of this project).
- `from cost_router.domain.tasks import Kind`: takes the name(s) `Kind` from the module `cost_router.domain.tasks` (a module of this project).
- `from cost_router.infrastructure.clock import ManualClock, SystemClock`: takes the name(s) `ManualClock, SystemClock` from the module `cost_router.infrastructure.clock` (a module of this project).
- `from cost_router.infrastructure.data import (`: takes the name(s) `load_bar, load_prices, load_router_config, load_tasks, router_config_to_json` from the module `cost_router.infrastructure.data` (a module of this project).

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `from cost_router.infrastructure.env import ConfigError, read_float, read_int, read_str`: takes the name(s) `ConfigError, read_float, read_int, read_str` from the module `cost_router.infrastructure.env` (a module of this project).
- `from cost_router.infrastructure.logging_setup import JsonFormatter, configure_logging`: takes the name(s) `JsonFormatter, configure_logging` from the module `cost_router.infrastructure.logging_setup` (a module of this project).
- `from cost_router.infrastructure.parallel import thread_mapper`: takes the name(s) `thread_mapper` from the module `cost_router.infrastructure.parallel` (a module of this project).
- `from cost_router.infrastructure.prompts import FilePromptStore`: takes the name(s) `FilePromptStore` from the module `cost_router.infrastructure.prompts` (a module of this project).
- `from cost_router.infrastructure.reports import dump_json, dump_jsonl, load_json, to_jso...`: takes the name(s) `dump_json, dump_jsonl, load_json, to_jsonable` from the module `cost_router.infrastructure.reports` (a module of this project).
- `from cost_router.infrastructure.settings import Settings`: takes the name(s) `Settings` from the module `cost_router.infrastructure.settings` (a module of this project).
- `ROOT = Path(__file__).resolve().parents[3]`: sets `ROOT` to the value of `Path(__file__).resolve().parents[3]`. `Path(__file__).resolve()` is the absolute form of the path `Path(__file__)`; `Path(__file__)` is the file path `__file__`.
- `def test_settings_have_validated_defaults_and_overrides(tmp_path: Path):`: defines the test `test_settings_have_validated_defaults_and_overrides` taking tmp_path (Path).
- `defaults = Settings.from_env({}, tmp_path)`: sets `defaults` to the value of `Settings.from_env({}, tmp_path)`.
- `assert defaults.models == {"small": "qwen2.5:0.5b", "medium": "llama3.2:1b", "large": "...`: checks that `defaults.models == {'small': 'qwen2.5:0.5b', 'medium': 'llama3.2:1b', 'large'...` is true; if it is not, the test (or program) fails here.
- `assert defaults.router_config_path == tmp_path / "config" / "router.json"`: checks that `defaults.router_config_path == tmp_path / 'config' / 'router.json'` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `custom = Settings.from_env({"TIER_LARGE": "big", "ROUTER_CONFIG": "/x.json", "WORKERS":...`: sets `custom` to the value of `Settings.from_env({'TIER_LARGE': 'big', 'ROUTER_CONFIG': '/x.json', 'WORKERS'...`.
- `assert custom.models["large"] == "big" and custom.router_config_path == Path("/x.json")...`: checks that `custom.models['large'] == 'big' and custom.router_config_path == Path('/x.jso...` is true; if it is not, the test (or program) fails here. `Path('/x.json')` is the file path `'/x.json'`.
- `with pytest.raises(ConfigError, match="at least"):`: opens `pytest.raises(ConfigError, match='at least')` for the duration of the block below and cleans up afterwards. `pytest.raises(ConfigError, match='at least')` is a block in which `ConfigError` must be raised; the test fails if it is not.
- `Settings.from_env({"WORKERS": "0"}, tmp_path)`: runs `Settings.from_env({'WORKERS': '0'}, tmp_path)` for its effect and ignores the result.
- `def test_env_readers_validate():`: defines the test `test_env_readers_validate` taking no arguments.
- `assert read_str({"A": " x "}, "A") == "x" and read_str({}, "A", "d") == "d"`: checks that `read_str({'A': ' x '}, 'A') == 'x' and read_str({}, 'A', 'd') == 'd'` is true; if it is not, the test (or program) fails here.
- `with pytest.raises(ConfigError, match="required"):`: opens `pytest.raises(ConfigError, match='required')` for the duration of the block below and cleans up afterwards. `pytest.raises(ConfigError, match='required')` is a block in which `ConfigError` must be raised; the test fails if it is not.
- `read_str({}, "A")`: runs `read_str({}, 'A')` for its effect and ignores the result.
- `assert read_float({"F": "1.5"}, "F", 0.0) == 1.5`: checks that `read_float({'F': '1.5'}, 'F', 0.0) == 1.5` is true; if it is not, the test (or program) fails here.
- `with pytest.raises(ConfigError, match="number"):`: opens `pytest.raises(ConfigError, match='number')` for the duration of the block below and cleans up afterwards. `pytest.raises(ConfigError, match='number')` is a block in which `ConfigError` must be raised; the test fails if it is not.
- `read_float({"F": "x"}, "F", 0.0)`: runs `read_float({'F': 'x'}, 'F', 0.0)` for its effect and ignores the result.
- `with pytest.raises(ConfigError, match="at least"):`: opens `pytest.raises(ConfigError, match='at least')` for the duration of the block below and cleans up afterwards. `pytest.raises(ConfigError, match='at least')` is a block in which `ConfigError` must be raised; the test fails if it is not.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `read_float({"F": "-1"}, "F", 0.0)`: runs `read_float({'F': '-1'}, 'F', 0.0)` for its effect and ignores the result.
- `with pytest.raises(ConfigError, match="integer"):`: opens `pytest.raises(ConfigError, match='integer')` for the duration of the block below and cleans up afterwards. `pytest.raises(ConfigError, match='integer')` is a block in which `ConfigError` must be raised; the test fails if it is not.
- `read_int({"I": "x"}, "I", 3)`: runs `read_int({'I': 'x'}, 'I', 3)` for its effect and ignores the result.
- `def test_the_committed_data_and_configuration_load():`: defines the test `test_the_committed_data_and_configuration_load` taking no arguments.
- `tasks = load_tasks(ROOT / "data")`: sets `tasks` to the value of `load_tasks(ROOT / 'data')`.
- `assert len(tasks) == 300`: checks that `len(tasks) == 300` is true; if it is not, the test (or program) fails here. `len(tasks)` is the number of items in `tasks`.
- `assert {t.kind for t in tasks} == set(Kind)`: checks that `{t.kind for t in tasks} == set(Kind)` is true; if it is not, the test (or program) fails here. `{t.kind for t in tasks}` builds a set: for each `t` in `tasks`; `set(Kind)` is `Kind` as a set (each value once).
- `assert sum(t.split == "build" for t in tasks) == 150`: checks that `sum((t.split == 'build' for t in tasks)) == 150` is true; if it is not, the test (or program) fails here. `sum((t.split == 'build' for t in tasks))` is the sum of `(t.split == 'build' for t in tasks)`; `(t.split == 'build' for t in tasks)` builds a generator of values: for each `t` in `tasks`.
- `assert load_bar(ROOT / "config").false_accept_bar == 0.10`: checks that `load_bar(ROOT / 'config').false_accept_bar == 0.1` is true; if it is not, the test (or program) fails here.
- `assert load_prices(ROOT / "config").per_1k_tokens["large"] == 0.0012`: checks that `load_prices(ROOT / 'config').per_1k_tokens['large'] == 0.0012` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `def test_a_router_configuration_round_trips(tmp_path: Path):`: defines the test `test_a_router_configuration_round_trips` taking tmp_path (Path).
- `config = RouterConfig(`: sets `config` to the value of `RouterConfig({'label': 'medium', 'refund': 'small', 'policy': 'large'}, {'ref...`.
- `path = tmp_path / "router.json"`: sets `path` to the value of `tmp_path / 'router.json'`.
- `path.write_text(json.dumps(router_config_to_json(config)))`: runs `path.write_text(json.dumps(router_config_to_json(config)))` for its effect and ignores the result. `path.write_text(json.dumps(router_config_to_json(config)))` writes `json.dumps(router_config_to_json(config))` as the content of the file `path`; `json.dumps(router_config_to_json(config))` is `router_config_to_json(config)` written as JSON text.
- `assert load_router_config(path) == config`: checks that `load_router_config(path) == config` is true; if it is not, the test (or program) fails here.
- `def test_every_prompt_in_the_changelog_exists_and_each_file_is_listed():`: defines the test `test_every_prompt_in_the_changelog_exists_and_each_file_is_listed` taking no arguments.
- `names = {p.stem for p in (ROOT / "prompts").glob("*.md") if p.stem != "CHANGELOG"}`: sets `names` to the value of `{p.stem for p in (ROOT / 'prompts').glob('*.md') if p.stem != 'CHANGELOG'}`. `{p.stem for p in (ROOT / 'prompts').glob('*.md') if p.stem != 'CHAN...` builds a set: for each `p` in `(ROOT / 'prompts').glob('*.md')`, keeping only those for which `p.stem != 'CHANGELOG'` is true; `(ROOT / 'prompts').glob('*.md')` is the files of `ROOT / 'prompts'` that match `'*.md'`.
- `changelog = (ROOT / "prompts" / "CHANGELOG.md").read_text()`: sets `changelog` to the value of `(ROOT / 'prompts' / 'CHANGELOG.md').read_text()`. `(ROOT / 'prompts' / 'CHANGELOG.md').read_text()` is the whole text of the file `ROOT / 'prompts' / 'CHANGELOG.md'`.
- `for name in names:`: repeats the block below once for each `name` in `names`.
- `prompt, _, version = name.rpartition(".")`: sets `(prompt, _, version)` to the value of `name.rpartition('.')`.

<!-- fmt: off -->
```python
        assert f"| {prompt} | {version} |" in changelog, name


def test_prompt_store_reads_a_file_without_its_trailing_newline(tmp_path: Path):
    (tmp_path / "a.v1.md").write_text("hello {{x}}\n\n")
    assert FilePromptStore(tmp_path).get("a.v1") == "hello {{x}}"
    with pytest.raises(FileNotFoundError, match="nope"):
        FilePromptStore(tmp_path).get("nope")


@pytest.mark.parametrize("workers", [1, 3])
def test_thread_mapper_keeps_input_order(workers):
    assert thread_mapper(workers)(lambda x: x * 2, list(range(20))) == [x * 2 for x in range(20)]
```
<!-- fmt: on -->

- `assert f"| {prompt} | {version} |" in changelog, name`: checks that `f'| {prompt} | {version} |' in changelog` is true, with the message `name`; if it is not, the test (or program) fails here. the f-string inserts `prompt`, `version` into the text.
- `def test_prompt_store_reads_a_file_without_its_trailing_newline(tmp_path: Path):`: defines the test `test_prompt_store_reads_a_file_without_its_trailing_newline` taking tmp_path (Path).
- `(tmp_path / "a.v1.md").write_text("hello {{x}}\n\n")`: runs `(tmp_path / 'a.v1.md').write_text('hello {{x}}\n\n')` for its effect and ignores the result. `(tmp_path / 'a.v1.md').write_text('hello {{x}}\n\n')` writes `'hello {{x}}\n\n'` as the content of the file `tmp_path / 'a.v1.md'`.
- `assert FilePromptStore(tmp_path).get("a.v1") == "hello {{x}}"`: checks that `FilePromptStore(tmp_path).get('a.v1') == 'hello {{x}}'` is true; if it is not, the test (or program) fails here. `FilePromptStore(tmp_path).get('a.v1')` looks up `'a.v1'` in `FilePromptStore(tmp_path)` (default (nothing) when missing).
- `with pytest.raises(FileNotFoundError, match="nope"):`: opens `pytest.raises(FileNotFoundError, match='nope')` for the duration of the block below and cleans up afterwards. `pytest.raises(FileNotFoundError, match='nope')` is a block in which `FileNotFoundError` must be raised; the test fails if it is not.
- `FilePromptStore(tmp_path).get("nope")`: runs `FilePromptStore(tmp_path).get('nope')` for its effect and ignores the result. `FilePromptStore(tmp_path).get('nope')` looks up `'nope'` in `FilePromptStore(tmp_path)` (default (nothing) when missing).
- **New idea.** `@pytest.mark.parametrize("x", [1, 2])` runs the same test once for each value, so one function checks many cases.
- `def test_thread_mapper_keeps_input_order(workers):`: defines the test `test_thread_mapper_keeps_input_order` taking workers. Decorators: `pytest.mark.parametrize('workers', [1, 3])`.
- `assert thread_mapper(workers)(lambda x: x * 2, list(range(20))) == [x * 2 for x in rang...`: checks that `thread_mapper(workers)(lambda x: x * 2, list(range(20))) == [x * 2 for x in r...` is true; if it is not, the test (or program) fails here. `[x * 2 for x in range(20)]` builds a list: for each `x` in `range(20)`; `lambda x: x * 2` is a small unnamed function of `x` that gives `x * 2`; `list(range(20))` is `range(20)` copied into a list.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- **New idea.** An **enum** is a fixed set of named values.
- `class Color(StrEnum):`: defines the class `Color` that inherits from `StrEnum`.
- `RED = "red"`: sets `RED` to the constant `'red'`.
- **New idea.** `@dataclass` is a **decorator** (a function applied to the class below it). It reads the annotated fields and writes `__init__`, `__repr__` and `__eq__` for you. `frozen=True` forbids changing a field after creation.
- `class Thing:`: defines the class `Thing`. Decorators: `dataclass(frozen=True)`.
- `color: Color`: declares a field of the class `color` of type `Color` (no value yet).
- `values: tuple[float, ...]`: declares a field of the class `values` of type `tuple[float, ...]` (no value yet).
- `ratio: float`: declares a field of the class `ratio` of type `float` (no value yet).
- `def test_reports_serialize_dataclasses_enums_and_infinity(tmp_path: Path):`: defines the test `test_reports_serialize_dataclasses_enums_and_infinity` taking tmp_path (Path).
- `value = {"t": Thing(Color.RED, (1.23456789, 2.0), float("inf"))}`: sets `value` to a dictionary with 1 entry. `float('inf')` is `'inf'` converted to a decimal number.
- `assert to_jsonable(value) == {"t": {"color": "red", "values": [1.234568, 2.0], "ratio":...`: checks that `to_jsonable(value) == {'t': {'color': 'red', 'values': [1.234568, 2.0], 'rati...` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `dump_json(tmp_path / "a" / "x.json", value)`: runs `dump_json(tmp_path / 'a' / 'x.json', value)` for its effect and ignores the result.
- `assert load_json(tmp_path / "a" / "x.json")["t"]["color"] == "red"`: checks that `load_json(tmp_path / 'a' / 'x.json')['t']['color'] == 'red'` is true; if it is not, the test (or program) fails here.
- `dump_jsonl(tmp_path / "rows.jsonl", [{"b": 1}, {"a": 2}])`: runs `dump_jsonl(tmp_path / 'rows.jsonl', [{'b': 1}, {'a': 2}])` for its effect and ignores the result.
- `assert [json.loads(line) for line in (tmp_path / "rows.jsonl").read_text().splitlines()...`: checks that `[json.loads(line) for line in (tmp_path / 'rows.jsonl').read_text().splitline...` is true; if it is not, the test (or program) fails here. `[json.loads(line) for line in (tmp_path / 'rows.jsonl').read_text()...` builds a list: for each `line` in `(tmp_path / 'rows.jsonl').read_text()...`; `json.loads(line)` is the JSON text `line` turned into Python values; `(tmp_path / 'rows.jsonl').read_text().splitlines()` is `(tmp_path / 'rows.jsonl').read_text()` cut into lines.
- `def test_json_log_lines_carry_extra_fields(capsys):`: defines the test `test_json_log_lines_carry_extra_fields` taking capsys.
- `configure_logging("INFO")`: runs `configure_logging('INFO')` for its effect and ignores the result.
- `configure_logging("INFO")`: runs `configure_logging('INFO')` for its effect and ignores the result.
- `logging.getLogger("t").info("call finished", extra={"tier": "small", "tokens": 7})`: runs `logging.getLogger('t').info('call finished', extra={'tier': 'small', 'tokens': 7})` for its effect and ignores the result. `logging.getLogger('t').info('call finished', extra={'tier': 'small'...` writes an info log line; `logging.getLogger('t')` is the logger named `'t'`.
- `line = json.loads(capsys.readouterr().err.strip().splitlines()[-1])`: sets `line` to the value of `json.loads(capsys.readouterr().err.strip().splitlines()[-1])`. `json.loads(capsys.readouterr().err.strip().splitlines()[-1])` is the JSON text `capsys.readouterr().err.strip().splitlines()[-1]` turned into Python values; `capsys.readouterr().err.strip().splitlines()` is `capsys.readouterr().err.strip()` cut into lines; `capsys.readouterr().err.strip()` is `capsys.readouterr().err` without white space at both ends.
- `assert line["msg"] == "call finished" and line["tier"] == "small" and line["level"] == ...`: checks that `line['msg'] == 'call finished' and line['tier'] == 'small' and (line['level']...` is true; if it is not, the test (or program) fails here.
- **New idea.** **try/except** handles errors. The code in `try:` runs; if it raises an error of the type named in `except`, Python jumps to that block instead of stopping. `finally:` always runs, error or not. `else:` runs only when no error occurred.
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.
- `raise RuntimeError("boom")`: signals an error, `RuntimeError('boom')`; normal flow stops here and the nearest matching `except` takes over. `RuntimeError('boom')` is a RuntimeError.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `except RuntimeError:`: runs when the error is `RuntimeError`.
- `record = logging.getLogger("t").makeRecord("t", logging.ERROR, "f", 1, "bad", (), loggi...`: sets `record` to the value of `logging.getLogger('t').makeRecord('t', logging.ERROR, 'f', 1, 'bad', (), logg...`. `logging.getLogger('t')` is the logger named `'t'`.
- `assert "RuntimeError" in json.loads(JsonFormatter().format(record))["exc"]`: checks that `'RuntimeError' in json.loads(JsonFormatter().format(record))['exc']` is true; if it is not, the test (or program) fails here. `json.loads(JsonFormatter().format(record))` is the JSON text `JsonFormatter().format(record)` turned into Python values; `JsonFormatter().format(record)` is `JsonFormatter()` with its {{}} fields filled in.
- `def test_clocks():`: defines the test `test_clocks` taking no arguments.
- `clock = ManualClock(5.0)`: sets `clock` to the value of `ManualClock(5.0)`.
- `clock.sleep(2.5)`: runs `clock.sleep(2.5)` for its effect and ignores the result. `clock.sleep(2.5)` waits `2.5` seconds.
- `assert clock.monotonic() == 7.5`: checks that `clock.monotonic() == 7.5` is true; if it is not, the test (or program) fails here. `clock.monotonic()` is the current reading of a clock that never goes backward.
- `with pytest.raises(ValueError, match="backward"):`: opens `pytest.raises(ValueError, match='backward')` for the duration of the block below and cleans up afterwards. `pytest.raises(ValueError, match='backward')` is a block in which `ValueError` must be raised; the test fails if it is not.
- `clock.advance(-1)`: runs `clock.advance(-1)` for its effect and ignores the result.
- `real = SystemClock()`: sets `real` to the value of `SystemClock()`.
- `before = real.monotonic()`: sets `before` to the value of `real.monotonic()`. `real.monotonic()` is the current reading of a clock that never goes backward.
- `real.sleep(0)`: runs `real.sleep(0)` for its effect and ignores the result. `real.sleep(0)` waits `0` seconds.

<!-- fmt: off -->
```python
    real.sleep(0.001)
    assert real.monotonic() >= before
```
<!-- fmt: on -->

- `real.sleep(0.001)`: runs `real.sleep(0.001)` for its effect and ignores the result. `real.sleep(0.001)` waits `0.001` seconds.
- `assert real.monotonic() >= before`: checks that `real.monotonic() >= before` is true; if it is not, the test (or program) fails here. `real.monotonic()` is the current reading of a clock that never goes backward.

#### `tests/unit/interfaces/__init__.py`

This file is empty. It exists so that Python treats the folder as a package.

#### `tests/unit/interfaces/test_cli.py`

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `import pytest`: imports the module(s) `pytest` so this file can use them. `pytest` is the test framework (`pytest.md`).
- `from cost_router.domain.llm import ChatRequest`: takes the name(s) `ChatRequest` from the module `cost_router.domain.llm` (a module of this project).
- `from cost_router.domain.tasks import POLICY_LINES`: takes the name(s) `POLICY_LINES` from the module `cost_router.domain.tasks` (a module of this project).
- `from cost_router.interfaces import cli`: takes the name(s) `cli` from the module `cost_router.interfaces` (a module of this project).
- `from tests.unit.fakes import ScriptedModel`: takes the name(s) `ScriptedModel` from the module `tests.unit.fakes` (a module of this project).
- `def answer(request: ChatRequest) -> str:`: defines the function `answer` taking request (ChatRequest) and returns `str`.
- `text = request.messages[0].content`: sets `text` to the value of `request.messages[0].content`.
- `if text.startswith("Classify"):`: runs the block below only if `text.startswith('Classify')` is true. `text.startswith('Classify')` is whether `text` begins with `'Classify'`.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `return "billing"`: ends the function and hands back `'billing'`.
- `if text.startswith("You compute refunds"):`: runs the block below only if `text.startswith('You compute refunds')` is true. `text.startswith('You compute refunds')` is whether `text` begins with `'You compute refunds'`.
- `return "Refund: 0.00"`: ends the function and hands back `'Refund: 0.00'`.
- `return f'Answer: x\nQuote: "{POLICY_LINES[0]}"'`: ends the function and hands back `f'Answer: x\nQuote: "{POLICY_LINES[0]}"'`. the f-string inserts `POLICY_LINES[0]` into the text.
- **New idea.** A **pytest fixture** is a function marked `@pytest.fixture`. A test that has a parameter with the fixture's name receives what the fixture returns (`pytest.md`).
- `def env(tmp_path: Path, monkeypatch):`: defines the function `env` taking tmp_path (Path); monkeypatch. Decorators: `pytest.fixture`.
- `values = {`: sets `values` to a dictionary with 3 entries. `str(tmp_path / 'reports')` is `tmp_path / 'reports'` converted to text; `str(tmp_path / 'router.json')` is `tmp_path / 'router.json'` converted to text.
- `monkeypatch.setattr(cli, "process_env", lambda: values)`: runs `monkeypatch.setattr(cli, 'process_env', lambda: values)` for its effect and ignores the result. `lambda: values` is a small unnamed function of no arguments that gives `values`.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `monkeypatch.setattr("cost_router.interfaces.wiring.build_chat_model", lambda e, f: Scri...`: runs `monkeypatch.setattr('cost_router.interfaces.wiring.build_chat_model', lambda e, f: Scri...` for its effect and ignores the result. `lambda e, f: ScriptedModel(answer)` is a small unnamed function of `e, f` that gives `ScriptedModel(answer)`.
- `return tmp_path`: ends the function and hands back `tmp_path`.
- `def test_all_runs_every_step_and_writes_the_reports(env: Path, capsys):`: defines the test `test_all_runs_every_step_and_writes_the_reports` taking env (Path); capsys.
- `assert cli.main(["all"]) == 0`: checks that `cli.main(['all']) == 0` is true; if it is not, the test (or program) fails here.
- `out = capsys.readouterr().out`: sets `out` to the value of `capsys.readouterr().out`.
- `assert "router configuration" in out and "verdict:" in out and "false accepts by tier/c...`: checks that `'router configuration' in out and 'verdict:' in out and ('false accepts by ti...` is true; if it is not, the test (or program) fails here.
- `reports = env / "reports"`: sets `reports` to the value of `env / 'reports'`.
- `for name in ("models.json", "checks.json", "router.json", "decisions.jsonl", "day.json"...`: repeats the block below once for each `name` in `('models.json', 'checks.json', 'router.json', 'decisions.jsonl', 'd...`.
- `assert (reports / name).exists(), name`: checks that `(reports / name).exists()` is true, with the message `name`; if it is not, the test (or program) fails here. `(reports / name).exists()` is whether `reports / name` exists.
- `router = json.loads((reports / "router.json").read_text())`: sets `router` to the value of `json.loads((reports / 'router.json').read_text())`. `json.loads((reports / 'router.json').read_text())` is the JSON text `(reports / 'router.json').read_text()` turned into Python values; `(reports / 'router.json').read_text()` is the whole text of the file `reports / 'router.json'`.
- `assert set(router["methods"]) == {"router", "router_no_bar", "small", "medium", "large"}`: checks that `set(router['methods']) == {'router', 'router_no_bar', 'small', 'medium', 'lar...` is true; if it is not, the test (or program) fails here. `set(router['methods'])` is `router['methods']` as a set (each value once).
- `assert router["methods"]["router"]["n"] == 150`: checks that `router['methods']['router']['n'] == 150` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `assert json.loads((env / "router.json").read_text())["label_check"] == "agreement"`: checks that `json.loads((env / 'router.json').read_text())['label_check'] == 'agreement'` is true; if it is not, the test (or program) fails here. `json.loads((env / 'router.json').read_text())` is the JSON text `(env / 'router.json').read_text()` turned into Python values; `(env / 'router.json').read_text()` is the whole text of the file `env / 'router.json'`.
- `assert "Step 6" in (reports / "REPORT.md").read_text()`: checks that `'Step 6' in (reports / 'REPORT.md').read_text()` is true; if it is not, the test (or program) fails here. `(reports / 'REPORT.md').read_text()` is the whole text of the file `reports / 'REPORT.md'`.
- `checks = json.loads((reports / "checks.json").read_text())`: sets `checks` to the value of `json.loads((reports / 'checks.json').read_text())`. `json.loads((reports / 'checks.json').read_text())` is the JSON text `(reports / 'checks.json').read_text()` turned into Python values; `(reports / 'checks.json').read_text()` is the whole text of the file `reports / 'checks.json'`.
- `assert set(checks) == {"bar", "rates", "rates_test"}`: checks that `set(checks) == {'bar', 'rates', 'rates_test'}` is true; if it is not, the test (or program) fails here. `set(checks)` is `checks` as a set (each value once).
- `def test_each_step_can_run_alone_in_order(env: Path):`: defines the test `test_each_step_can_run_alone_in_order` taking env (Path).
- `for step in ("models", "checks", "tune", "router", "day", "audit", "report"):`: repeats the block below once for each `step` in `('models', 'checks', 'tune', 'router', 'day', 'audit', 'report')`.
- `assert cli.main([step]) == 0, step`: checks that `cli.main([step]) == 0` is true, with the message `step`; if it is not, the test (or program) fails here.
- `def test_health_reports_the_data_and_prompts(env: Path, capsys):`: defines the test `test_health_reports_the_data_and_prompts` taking env (Path); capsys.
- `assert cli.main(["health"]) == 0`: checks that `cli.main(['health']) == 0` is true; if it is not, the test (or program) fails here.
- `assert "tasks=300 build=150 test=150" in capsys.readouterr().out`: checks that `'tasks=300 build=150 test=150' in capsys.readouterr().out` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `def test_parity_passes_for_equal_reports_and_fails_for_a_changed_number(env: Path, tmp_...`: defines the test `test_parity_passes_for_equal_reports_and_fails_for_a_changed_number` taking env (Path); tmp_path (Path); capsys.
- `assert cli.main(["all"]) == 0`: checks that `cli.main(['all']) == 0` is true; if it is not, the test (or program) fails here.
- `reports = env / "reports"`: sets `reports` to the value of `env / 'reports'`.
- `other = tmp_path / "java"`: sets `other` to the value of `tmp_path / 'java'`.
- `other.mkdir()`: runs `other.mkdir()` for its effect and ignores the result. `other.mkdir()` creates the folder `other`.
- `for name in ("router.json", "day.json", "audit.json"):`: repeats the block below once for each `name` in `('router.json', 'day.json', 'audit.json')`.
- `(other / name).write_text((reports / name).read_text())`: runs `(other / name).write_text((reports / name).read_text())` for its effect and ignores the result. `(other / name).write_text((reports / name).read_text())` writes `(reports / name).read_text()` as the content of the file `other / name`; `(reports / name).read_text()` is the whole text of the file `reports / name`.
- `assert cli.main(["parity", "--java", str(other), "--python", str(reports)]) == 0`: checks that `cli.main(['parity', '--java', str(other), '--python', str(reports)]) == 0` is true; if it is not, the test (or program) fails here. `str(other)` is `other` converted to text; `str(reports)` is `reports` converted to text.
- `changed = json.loads((other / "router.json").read_text())`: sets `changed` to the value of `json.loads((other / 'router.json').read_text())`. `json.loads((other / 'router.json').read_text())` is the JSON text `(other / 'router.json').read_text()` turned into Python values; `(other / 'router.json').read_text()` is the whole text of the file `other / 'router.json'`.
- **New idea.** An **augmented assignment** such as `x += 1` changes the value in place: it means `x = x + 1`.
- `changed["methods"]["router"]["total_cost"] += 1`: adds `1` to `changed['methods']['router']['total_c...` and stores the result back.
- `changed["extra"] = 1`: sets `changed['extra']` to the constant `1`.
- `(other / "router.json").write_text(json.dumps(changed))`: runs `(other / 'router.json').write_text(json.dumps(changed))` for its effect and ignores the result. `(other / 'router.json').write_text(json.dumps(changed))` writes `json.dumps(changed)` as the content of the file `other / 'router.json'`; `json.dumps(changed)` is `changed` written as JSON text.
- `assert cli.main(["parity", "--java", str(other), "--python", str(reports)]) == 1`: checks that `cli.main(['parity', '--java', str(other), '--python', str(reports)]) == 1` is true; if it is not, the test (or program) fails here. `str(other)` is `other` converted to text; `str(reports)` is `reports` converted to text.
- `assert "total_cost" in capsys.readouterr().out`: checks that `'total_cost' in capsys.readouterr().out` is true; if it is not, the test (or program) fails here.

<!-- fmt: off -->
```python
def test_a_bad_setting_exits_with_code_two(monkeypatch, capsys):
    monkeypatch.setattr(cli, "process_env", lambda: {"WORKERS": "zero"})
    assert cli.main(["health"]) == 2
    assert "configuration error" in capsys.readouterr().err


def test_an_interrupt_exits_with_130(env: Path, monkeypatch):
    def interrupted(_services):
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "cmd_models", interrupted)
    assert cli.main(["models"]) == 130
```
<!-- fmt: on -->

- `def test_a_bad_setting_exits_with_code_two(monkeypatch, capsys):`: defines the test `test_a_bad_setting_exits_with_code_two` taking monkeypatch; capsys.
- `monkeypatch.setattr(cli, "process_env", lambda: {"WORKERS": "zero"})`: runs `monkeypatch.setattr(cli, 'process_env', lambda: {'WORKERS': 'zero'})` for its effect and ignores the result. `lambda: {'WORKERS': 'zero'}` is a small unnamed function of no arguments that gives `{'WORKERS': 'zero'}`.
- `assert cli.main(["health"]) == 2`: checks that `cli.main(['health']) == 2` is true; if it is not, the test (or program) fails here.
- `assert "configuration error" in capsys.readouterr().err`: checks that `'configuration error' in capsys.readouterr().err` is true; if it is not, the test (or program) fails here.
- `def test_an_interrupt_exits_with_130(env: Path, monkeypatch):`: defines the test `test_an_interrupt_exits_with_130` taking env (Path); monkeypatch.
- `def interrupted(_services):`: defines the function `interrupted` taking _services.
- `raise KeyboardInterrupt`: signals an error, `KeyboardInterrupt`; normal flow stops here and the nearest matching `except` takes over.
- `monkeypatch.setattr(cli, "cmd_models", interrupted)`: runs `monkeypatch.setattr(cli, 'cmd_models', interrupted)` for its effect and ignores the result.
- `assert cli.main(["models"]) == 130`: checks that `cli.main(['models']) == 130` is true; if it is not, the test (or program) fails here.

## Try it yourself

1. `.venv/bin/python -m pytest tests/unit -q` ends with `N passed`.
2. `.venv/bin/python -m pytest tests/unit -q --collect-only | tail -3` lists how many tests were collected without running them.
3. `.venv/bin/python -m pytest tests/unit -q -x -k fixture` runs only the tests whose name contains `fixture`.
4. Change one expected number in a test copy and run it to see `assert ... == ...` fail with both values printed.

## Mistakes people make

- Tests that depend on the order of other tests.
- A test with no assertion: it can only fail by crashing.
- Calling a real model in a unit test; use a fake or a recording.
- Asserting on floating-point equality without a tolerance.
- Forgetting that a misspelled marker is an error because of `--strict-markers`.

## Check yourself

1. **How does pytest find a test?**  
   File `test_*.py`, function `test_*`.
2. **What fails a test?**  
   A false `assert` or any uncaught exception.
3. **What is a fake?**  
   A small stand-in object that implements a port with scripted behaviour.
4. **What does the end-to-end test compare?**  
   The reports produced from recorded answers with the committed reports.
5. **What does a marker do?**  
   Labels a test so a group can be selected or skipped.

## Further reading

The Python language reference: https://docs.python.org/3/reference/ and the tutorial https://docs.python.org/3/tutorial/ (both for Python 3.13; the project accepts 3.12 or newer). pytest: https://docs.pytest.org/
