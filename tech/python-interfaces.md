# Python code: the interfaces layer, file by file

## What it is

The **interfaces layer**: how a person or another program starts the code. The command-line program, the HTTP routes and the *wiring* that builds all the parts and connects them live here.

## Why this repository uses it

Someone has to decide which adapter is used with which experiment. That decision is made in one place, the wiring, so the rest of the code stays independent of it.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/cost_router/interfaces/__init__.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/interfaces/cli.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/interfaces/wiring.py` | Quoted and explained in the walkthrough below. |


## How it works underneath

The command-line file defines one function per command (`cmd_...`), each taking the wired services and returning an exit code (0 means success). `main` reads the arguments, builds the services and calls the right command. Nothing depends on this layer; it depends on everything below.

## Walkthrough of this repository's use

### Files in this note

| File | Lines | What it is |
| --- | --- | --- |
| `src/cost_router/interfaces/__init__.py` | 1 | The interfaces layer. |
| `src/cost_router/interfaces/cli.py` | 295 | Command-line entry point: one program, one sub-command per step of the lesson. |
| `src/cost_router/interfaces/wiring.py` | 54 | The composition root: build the adapters and services from settings. |

Each file below is quoted exactly, in order, in pieces of about a dozen lines. Under each piece, a bullet list explains every statement in the order it appears. The first time an idea shows up in this note it is explained in a bullet that begins **New idea**.

#### `src/cost_router/interfaces/__init__.py`

<!-- fmt: off -->
```python
"""The interfaces layer."""
```
<!-- fmt: on -->

- **New idea.** A **docstring** is a text in triple quotes as the first statement of a module, class or function. Python keeps it as documentation and tools can show it.
- `"""The interfaces layer."""`: a docstring (documentation text). It says: "The interfaces layer."

#### `src/cost_router/interfaces/cli.py`

<!-- fmt: off -->
```python
"""Command-line entry point: one program, one sub-command per step of the lesson."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any
```
<!-- fmt: on -->

- `"""Command-line entry point: one program, one sub-command per step of the lesson."""`: a docstring (documentation text). It says: "Command-line entry point: one program, one sub-command per step of the lesson."
- **New idea.** `from __future__ import annotations` turns on a newer behaviour: type annotations are stored as text instead of being evaluated when the file loads.
- **New idea.** An **import** makes the code of another module available. `import x` gives the whole module under the name `x`; `from x import y` gives just the name `y`.
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import argparse`: imports the module(s) `argparse` so this file can use them. `argparse` is command-line option parsing.
- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `import logging`: imports the module(s) `logging` so this file can use them. `logging` is the standard logging system.
- `import os`: imports the module(s) `os` so this file can use them. `os` is operating-system services such as environment variables and paths.
- `import sys`: imports the module(s) `sys` so this file can use them. `sys` is the running interpreter: arguments, standard streams, exit.
- `from collections.abc import Sequence`: takes the name(s) `Sequence` from the module `collections.abc` (abstract container types used in annotations).
- `from dataclasses import replace`: takes the name(s) `replace` from the module `dataclasses` (classes that are mostly data).
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).

<!-- fmt: off -->
```python
from cost_router.application.experiments import (
    Outcome,
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

- `from cost_router.application.experiments import (`: takes the name(s) `Outcome, cheapest_matching, check_results, collect_answers, compare_to_large, false_accepts, harden, make_checks, measure_models, route_all, run_day, single_model_summary, summarize, tune, weakest_kind` from the module `cost_router.application.experiments` (a module of this project).

<!-- fmt: off -->
```python
from cost_router.application.report_md import render_report
from cost_router.application.router import CostRouter
from cost_router.domain.pricing import TIERS
from cost_router.domain.routing import RouterConfig
from cost_router.infrastructure.data import load_router_config, router_config_to_json
from cost_router.infrastructure.env import ConfigError, process_env
from cost_router.infrastructure.logging_setup import configure_logging
from cost_router.infrastructure.reports import dump_json, dump_jsonl, load_json, to_jsonable
from cost_router.interfaces.wiring import Services, build_services

LOG = logging.getLogger("cost_router")
# The project folder holds data/, prompts/ and the fixtures; an installed copy (the Docker image) sets PROJECT_ROOT.
ROOT = Path(os.environ.get("PROJECT_ROOT") or Path(__file__).resolve().parents[3])
```
<!-- fmt: on -->

- `from cost_router.application.report_md import render_report`: takes the name(s) `render_report` from the module `cost_router.application.report_md` (a module of this project).
- `from cost_router.application.router import CostRouter`: takes the name(s) `CostRouter` from the module `cost_router.application.router` (a module of this project).
- `from cost_router.domain.pricing import TIERS`: takes the name(s) `TIERS` from the module `cost_router.domain.pricing` (a module of this project).
- `from cost_router.domain.routing import RouterConfig`: takes the name(s) `RouterConfig` from the module `cost_router.domain.routing` (a module of this project).
- `from cost_router.infrastructure.data import load_router_config, router_config_to_json`: takes the name(s) `load_router_config, router_config_to_json` from the module `cost_router.infrastructure.data` (a module of this project).
- `from cost_router.infrastructure.env import ConfigError, process_env`: takes the name(s) `ConfigError, process_env` from the module `cost_router.infrastructure.env` (a module of this project).
- `from cost_router.infrastructure.logging_setup import configure_logging`: takes the name(s) `configure_logging` from the module `cost_router.infrastructure.logging_setup` (a module of this project).
- `from cost_router.infrastructure.reports import dump_json, dump_jsonl, load_json, to_jso...`: takes the name(s) `dump_json, dump_jsonl, load_json, to_jsonable` from the module `cost_router.infrastructure.reports` (a module of this project).
- `from cost_router.interfaces.wiring import Services, build_services`: takes the name(s) `Services, build_services` from the module `cost_router.interfaces.wiring` (a module of this project).
- **New idea.** An **assignment** `name = value` makes the name point at the value. A name written in capital letters is, by convention, a constant: it is not meant to change.
- `LOG = logging.getLogger("cost_router")`: sets `LOG` to the value of `logging.getLogger('cost_router')`. `logging.getLogger('cost_router')` is the logger named `'cost_router'`.
- `ROOT = Path(os.environ.get("PROJECT_ROOT") or Path(__file__).resolve().parents[3])`: sets `ROOT` to the value of `Path(os.environ.get('PROJECT_ROOT') or Path(__file__).resolve().parents[3])`. `Path(os.environ.get('PROJECT_ROOT') or Path(__file__).resolve().par...` is the file path `os.environ.get('PROJECT_ROOT') or Path(__file__).resolve(...`; `os.environ.get('PROJECT_ROOT')` is the environment variable `'PROJECT_ROOT'` (default (nothing)); `Path(__file__).resolve()` is the absolute form of the path `Path(__file__)`.

<!-- fmt: off -->
```python
def _answers(s: Services) -> Any:
    return collect_answers(s.tasks, s.tiers, s.mapper)


def cmd_models(s: Services) -> None:
    """Step 1: each model alone on the build tasks."""
    build = s.split("build")
    answers = _answers(s)
    table = measure_models(build, answers)
    matching = cheapest_matching(table, s.bar.accuracy_margin)
    dump_json(
        s.settings.reports_dir / "models.json", {"table": table, "cheapest_matching": matching, "prices": s.prices}
    )
    for tier in TIERS:
```
<!-- fmt: on -->

- **New idea.** A **function** is a named block of code. `def name(a, b):` defines it; the indented lines are its body. Calling `name(1, 2)` runs the body with `a = 1` and `b = 2`. `return` hands a value back. A parameter written `b=3` has a **default**: it may be left out when calling.
- `def _answers(s: Services) -> Any:`: defines the function `_answers` taking s (Services) and returns `Any`.
- **New idea.** `return value` ends the function and hands the value to the caller. A function that reaches its end without `return` gives back `None` (nothing).
- `return collect_answers(s.tasks, s.tiers, s.mapper)`: ends the function and hands back `collect_answers(s.tasks, s.tiers, s.mapper)`.
- `def cmd_models(s: Services) -> None:`: defines the function `cmd_models` taking s (Services) and returns `None`. Purpose: Step 1: each model alone on the build tasks.
- `"""Step 1: each model alone on the build tasks."""`: a docstring (documentation text). It says: "Step 1: each model alone on the build tasks."
- `build = s.split("build")`: sets `build` to the value of `s.split('build')`. `s.split('build')` is `s` cut into pieces at `'build'`.
- `answers = _answers(s)`: sets `answers` to the value of `_answers(s)`.
- `table = measure_models(build, answers)`: sets `table` to the value of `measure_models(build, answers)`.
- `matching = cheapest_matching(table, s.bar.accuracy_margin)`: sets `matching` to the value of `cheapest_matching(table, s.bar.accuracy_margin)`.
- `dump_json(`: runs `dump_json(s.settings.reports_dir / 'models.json', {'table': table, 'cheapest_matching':...` for its effect and ignores the result.
- **New idea.** A **for loop** `for x in items:` runs its block once for each item, with `x` naming the current item. `break` leaves the loop early; `continue` skips to the next item.
- `for tier in TIERS:`: repeats the block below once for each `tier` in `TIERS`.

<!-- fmt: off -->
```python
        cells = "  ".join(f"{k}={c.accuracy.value:.1%}" for k, c in table[tier].items())
        print(f"{tier:6} {cells}")
    print(f"cheapest within the margin of large: {matching}")


def cmd_checks(s: Services) -> None:
    """Step 2: false-accept and false-reject rates of each check on the build set (and the test set, for reference)."""
    answers = _answers(s)
    rates = check_results(s.split("build"), answers, s.tiers, s.mapper)
    test_rates = check_results(s.split("test"), answers, s.tiers, s.mapper)
    dump_json(
        s.settings.reports_dir / "checks.json",
        {"bar": s.bar.false_accept_bar, "rates": rates, "rates_test": test_rates},
    )
```
<!-- fmt: on -->

- `cells = "  ".join(f"{k}={c.accuracy.value:.1%}" for k, c in table[tier].items())`: sets `cells` to the value of `' '.join((f'{k}={c.accuracy.value:.1%}' for k, c in table[tier].items()))`. `' '.join((f'{k}={c.accuracy.value:.1%}' for k, c in table[tier].ite...` is the items of `(f'{k}={c.accuracy.value:.1%}' for k, c in table[tier].it...` joined into one text with `' '` between them; `(f'{k}={c.accuracy.value:.1%}' for k, c in table[tier].items())` builds a generator of values: for each `(k, c)` in `table[tier].items()`; the f-string inserts `k`, `c.accuracy.value` into the text.
- `print(f"{tier:6} {cells}")`: runs `print(f'{tier:6} {cells}')` for its effect and ignores the result. `print(f'{tier:6} {cells}')` prints `f'{tier:6} {cells}'`; the f-string inserts `tier`, `cells` into the text.
- `print(f"cheapest within the margin of large: {matching}")`: runs `print(f'cheapest within the margin of large: {matching}')` for its effect and ignores the result. `print(f'cheapest within the margin of large: {matching}')` prints `f'cheapest within the margin of large: {matching}'`; the f-string inserts `matching` into the text.
- `def cmd_checks(s: Services) -> None:`: defines the function `cmd_checks` taking s (Services) and returns `None`. Purpose: Step 2: false-accept and false-reject rates of each check on the build set (and the test set, for reference).
- `"""Step 2: false-accept and false-reject rates of each check on the build set (and the ...`: a docstring (documentation text). It says: "Step 2: false-accept and false-reject rates of each check on the build set (and the test set, for reference)."
- `answers = _answers(s)`: sets `answers` to the value of `_answers(s)`.
- `rates = check_results(s.split("build"), answers, s.tiers, s.mapper)`: sets `rates` to the value of `check_results(s.split('build'), answers, s.tiers, s.mapper)`. `s.split('build')` is `s` cut into pieces at `'build'`.
- `test_rates = check_results(s.split("test"), answers, s.tiers, s.mapper)`: sets `test_rates` to the value of `check_results(s.split('test'), answers, s.tiers, s.mapper)`. `s.split('test')` is `s` cut into pieces at `'test'`.
- `dump_json(`: runs `dump_json(s.settings.reports_dir / 'checks.json', {'bar': s.bar.false_accept_bar, 'rate...` for its effect and ignores the result.

<!-- fmt: off -->
```python
    for tier in TIERS:
        for by_check in rates[tier].values():
            for name, r in by_check.items():
                flag = "  <- over the bar" if r.false_accept_rate > s.bar.false_accept_bar else ""
                far, frr = r.false_accept_rate, r.false_reject_rate
                print(f"{tier:6} {name:18} false-accept {far:.3f}  false-reject {frr:.3f}{flag}")


def cmd_tune(s: Services) -> None:
    """Step 3: derive the start tiers from the build set only and write config/router.json."""
    build = s.split("build")
    answers = _answers(s)
    rates = check_results(build, answers, s.tiers, s.mapper)
    config = tune(build, answers, rates, s.bar)
```
<!-- fmt: on -->

- `for tier in TIERS:`: repeats the block below once for each `tier` in `TIERS`.
- `for by_check in rates[tier].values():`: repeats the block below once for each `by_check` in `rates[tier].values()`. `rates[tier].values()` is the values of `rates[tier]`.
- `for name, r in by_check.items():`: repeats the block below once for each `(name, r)` in `by_check.items()`. `by_check.items()` is the (key, value) pairs of `by_check`.
- `flag = "  <- over the bar" if r.false_accept_rate > s.bar.false_accept_bar else ""`: sets `flag` to the value of `' <- over the bar' if r.false_accept_rate > s.bar.false_accept_bar else ''`. `' <- over the bar' if r.false_accept_rate > s.bar.false_accept_bar ...` gives `' <- over the bar'` when `r.false_accept_rate > s.bar.false_acc...` is true, otherwise `''`.
- `far, frr = r.false_accept_rate, r.false_reject_rate`: sets `(far, frr)` to a tuple of 2 items.
- `print(f"{tier:6} {name:18} false-accept {far:.3f}  false-reject {frr:.3f}{flag}")`: runs `print(f'{tier:6} {name:18} false-accept {far:.3f} false-reject {frr:.3f}{flag}')` for its effect and ignores the result. `print(f'{tier:6} {name:18} false-accept {far:.3f} false-reject {frr...` prints `f'{tier:6} {name:18} false-accept {far:.3f} false-reject ...`; the f-string inserts `tier`, `name`, `far`, `frr` into the text.
- `def cmd_tune(s: Services) -> None:`: defines the function `cmd_tune` taking s (Services) and returns `None`. Purpose: Step 3: derive the start tiers from the build set only and write config/router.json.
- `"""Step 3: derive the start tiers from the build set only and write config/router.json."""`: a docstring (documentation text). It says: "Step 3: derive the start tiers from the build set only and write config/router.json."
- `build = s.split("build")`: sets `build` to the value of `s.split('build')`. `s.split('build')` is `s` cut into pieces at `'build'`.
- `answers = _answers(s)`: sets `answers` to the value of `_answers(s)`.
- `rates = check_results(build, answers, s.tiers, s.mapper)`: sets `rates` to the value of `check_results(build, answers, s.tiers, s.mapper)`.
- `config = tune(build, answers, rates, s.bar)`: sets `config` to the value of `tune(build, answers, rates, s.bar)`.

<!-- fmt: off -->
```python
    s.settings.router_config_path.parent.mkdir(parents=True, exist_ok=True)
    s.settings.router_config_path.write_text(json.dumps(router_config_to_json(config), indent=2, sort_keys=True) + "\n")
    print(f"router configuration: {router_config_to_json(config)}")


def _router(s: Services, config: RouterConfig) -> CostRouter:
    return CostRouter(s.tiers, make_checks(s.tiers, config), config)


def _config(s: Services) -> RouterConfig:
    return load_router_config(s.settings.router_config_path)


def _summary_json(summary: Any) -> dict[str, Any]:
```
<!-- fmt: on -->

- `s.settings.router_config_path.parent.mkdir(parents=True, exist_ok=True)`: runs `s.settings.router_config_path.parent.mkdir(parents=True, exist_ok=True)` for its effect and ignores the result. `s.settings.router_config_path.parent.mkdir(parents=True, exist_ok=T...` creates the folder `s.settings.router_config_path.parent`.
- `s.settings.router_config_path.write_text(json.dumps(router_config_to_json(config), inde...`: runs `s.settings.router_config_path.write_text(json.dumps(router_config_to_json(config), inde...` for its effect and ignores the result. `s.settings.router_config_path.write_text(json.dumps(router_config_t...` writes `json.dumps(router_config_to_json(config), indent=2, sort_...` as the content of the file `s.settings.router_config_path`; `json.dumps(router_config_to_json(config), indent=2, sort_keys=True)` is `router_config_to_json(config)` written as JSON text.
- `print(f"router configuration: {router_config_to_json(config)}")`: runs `print(f'router configuration: {router_config_to_json(config)}')` for its effect and ignores the result. `print(f'router configuration: {router_config_to_json(config)}')` prints `f'router configuration: {router_config_to_json(config)}'`; the f-string inserts `router_config_to_json(config)` into the text.
- `def _router(s: Services, config: RouterConfig) -> CostRouter:`: defines the function `_router` taking s (Services); config (RouterConfig) and returns `CostRouter`.
- `return CostRouter(s.tiers, make_checks(s.tiers, config), config)`: ends the function and hands back `CostRouter(s.tiers, make_checks(s.tiers, config), config)`.
- `def _config(s: Services) -> RouterConfig:`: defines the function `_config` taking s (Services) and returns `RouterConfig`.
- `return load_router_config(s.settings.router_config_path)`: ends the function and hands back `load_router_config(s.settings.router_config_path)`.
- `def _summary_json(summary: Any) -> dict[str, Any]:`: defines the function `_summary_json` taking summary (Any) and returns `dict[str, Any]`.

<!-- fmt: off -->
```python
    return to_jsonable(summary)  # type: ignore[no-any-return]


def cmd_router(s: Services) -> None:
    """Step 5: the router and each model alone on the test tasks."""
    test = s.split("test")
    config = _config(s)
    answers = _answers(s)
    outcomes = route_all(test, _router(s, config))
    build = s.split("build")
    rates = check_results(build, answers, s.tiers, s.mapper)
    no_bar = tune(build, answers, rates, replace(s.bar, false_accept_bar=1.0))
    methods = {
        "router": summarize(outcomes),
        "router_no_bar": summarize(route_all(test, _router(s, no_bar))),
        **{t: single_model_summary(test, answers, t) for t in TIERS},
    }
```
<!-- fmt: on -->

- `return to_jsonable(summary)  # type: ignore[no-any-return]`: ends the function and hands back `to_jsonable(summary)`.
- `def cmd_router(s: Services) -> None:`: defines the function `cmd_router` taking s (Services) and returns `None`. Purpose: Step 5: the router and each model alone on the test tasks.
- `"""Step 5: the router and each model alone on the test tasks."""`: a docstring (documentation text). It says: "Step 5: the router and each model alone on the test tasks."
- `test = s.split("test")`: sets `test` to the value of `s.split('test')`. `s.split('test')` is `s` cut into pieces at `'test'`.
- `config = _config(s)`: sets `config` to the value of `_config(s)`.
- `answers = _answers(s)`: sets `answers` to the value of `_answers(s)`.
- `outcomes = route_all(test, _router(s, config))`: sets `outcomes` to the value of `route_all(test, _router(s, config))`.
- `build = s.split("build")`: sets `build` to the value of `s.split('build')`. `s.split('build')` is `s` cut into pieces at `'build'`.
- `rates = check_results(build, answers, s.tiers, s.mapper)`: sets `rates` to the value of `check_results(build, answers, s.tiers, s.mapper)`.
- `no_bar = tune(build, answers, rates, replace(s.bar, false_accept_bar=1.0))`: sets `no_bar` to the value of `tune(build, answers, rates, replace(s.bar, false_accept_bar=1.0))`.
- `methods = {`: sets `methods` to a dictionary with 3 entries. `{t: single_model_summary(test, answers, t) for t in TIERS}` builds a dictionary: for each `t` in `TIERS`.

<!-- fmt: off -->
```python
    by_kind: dict[str, Any] = {}
    for kind in ("label", "refund", "policy"):
        subset = [o for o in outcomes if o.kind == kind]
        by_kind[kind] = {
            "n": len(subset),
            "accuracy": sum(o.correct for o in subset) / len(subset),
            "cost": sum(o.decision.spent for o in subset),
        }
    result = {
        "config": router_config_to_json(config),
        "config_no_bar": router_config_to_json(no_bar),
        "methods": {k: _summary_json(v) for k, v in methods.items()},
        "by_kind": by_kind,
        "verdict": compare_to_large(test, answers, outcomes, s.bar),
    }
```
<!-- fmt: on -->

- **New idea.** An **annotated assignment** `name: type = value` also says what kind of value the name should hold. The annotation is a hint for readers and for mypy (`mypy.md`); Python does not enforce it.
- `by_kind: dict[str, Any] = {}`: declares a variable `by_kind` of type `dict[str, Any]` and sets it to `{}`.
- `for kind in ("label", "refund", "policy"):`: repeats the block below once for each `kind` in `('label', 'refund', 'policy')`.
- `subset = [o for o in outcomes if o.kind == kind]`: sets `subset` to the value of `[o for o in outcomes if o.kind == kind]`. `[o for o in outcomes if o.kind == kind]` builds a list: for each `o` in `outcomes`, keeping only those for which `o.kind == kind` is true.
- `by_kind[kind] = {`: sets `by_kind[kind]` to a dictionary with 3 entries. `len(subset)` is the number of items in `subset`; `sum((o.decision.spent for o in subset))` is the sum of `(o.decision.spent for o in subset)`; `sum((o.correct for o in subset))` is the sum of `(o.correct for o in subset)`.
- `result = {`: sets `result` to a dictionary with 5 entries. `{k: _summary_json(v) for k, v in methods.items()}` builds a dictionary: for each `(k, v)` in `methods.items()`; `methods.items()` is the (key, value) pairs of `methods`.

<!-- fmt: off -->
```python
    dump_json(s.settings.reports_dir / "router.json", result)
    dump_jsonl(s.settings.reports_dir / "decisions.jsonl", [_decision_row(o) for o in outcomes])
    for name, m in methods.items():
        per_correct = m.cost_per_correct or 0
        head = f"{name:7} accuracy {m.accuracy.value:.1%}  cost {m.total_cost:.6f}"
        print(f"{head}  per correct {per_correct:.6f}  {m.served_by}")
    print(f"verdict: {result['verdict']['verdict']}")


def _decision_row(outcome: Outcome) -> dict[str, Any]:
    d = outcome.decision
    return {
        "task_id": d.task_id,
        "kind": outcome.kind,
        "difficulty": outcome.difficulty,
        "served_by": d.served_by,
        "correct": outcome.correct,
        "spent": d.spent,
        "attempts": [{"tier": a.tier, "passed": a.passed, "cost": a.cost} for a in d.attempts],
        "tags": list(d.tags),
    }
```
<!-- fmt: on -->

- `dump_json(s.settings.reports_dir / "router.json", result)`: runs `dump_json(s.settings.reports_dir / 'router.json', result)` for its effect and ignores the result.
- `dump_jsonl(s.settings.reports_dir / "decisions.jsonl", [_decision_row(o) for o in outco...`: runs `dump_jsonl(s.settings.reports_dir / 'decisions.jsonl', [_decision_row(o) for o in outco...` for its effect and ignores the result. `[_decision_row(o) for o in outcomes]` builds a list: for each `o` in `outcomes`.
- `for name, m in methods.items():`: repeats the block below once for each `(name, m)` in `methods.items()`. `methods.items()` is the (key, value) pairs of `methods`.
- `per_correct = m.cost_per_correct or 0`: sets `per_correct` to the value of `m.cost_per_correct or 0`.
- `head = f"{name:7} accuracy {m.accuracy.value:.1%}  cost {m.total_cost:.6f}"`: sets `head` to the value of `f'{name:7} accuracy {m.accuracy.value:.1%} cost {m.total_cost:.6f}'`. the f-string inserts `name`, `m.accuracy.value`, `m.total_cost` into the text.
- `print(f"{head}  per correct {per_correct:.6f}  {m.served_by}")`: runs `print(f'{head} per correct {per_correct:.6f} {m.served_by}')` for its effect and ignores the result. `print(f'{head} per correct {per_correct:.6f} {m.served_by}')` prints `f'{head} per correct {per_correct:.6f} {m.served_by}'`; the f-string inserts `head`, `per_correct`, `m.served_by` into the text.
- `print(f"verdict: {result['verdict']['verdict']}")`: runs `print(f"verdict: {result['verdict']['verdict']}")` for its effect and ignores the result. `print(f"verdict: {result['verdict']['verdict']}")` prints `f"verdict: {result['verdict']['verdict']}"`; the f-string inserts `result['verdict']['verdict']` into the text.
- `def _decision_row(outcome: Outcome) -> dict[str, Any]:`: defines the function `_decision_row` taking outcome (Outcome) and returns `dict[str, Any]`.
- `d = outcome.decision`: sets `d` to the value of `outcome.decision`.
- `return {`: ends the function and hands back `{'task_id': d.task_id, 'kind': outcome.kind, 'difficulty': outcome.difficulty...`. `[{'tier': a.tier, 'passed': a.passed, 'cost': a.cost} for a in d.at...` builds a list: for each `a` in `d.attempts`; `list(d.tags)` is `d.tags` copied into a list.

<!-- fmt: off -->
```python
def cmd_day(s: Services) -> None:
    """Step 4: the test tasks as one day under a budget."""
    test = s.split("test")
    config = _config(s)
    answers = _answers(s)
    days = []
    for fraction in s.bar.day_budget_fractions:
        result = run_day(test, answers, lambda: _router(s, config), fraction)
        days.append(replace(result, outcomes=[]))
        print(
            f"budget {fraction:.0%} of always-large: spent {result.spent:.6f} of {result.budget:.6f} "
            f"(under: {result.under_budget}); over-cap requests {result.requests_over_cap}; "
            f"accuracy before 80% {result.accuracy_before.value:.1%} (n={result.accuracy_before.trials}), "
            f"after {result.accuracy_after.value:.1%} (n={result.accuracy_after.trials})"
        )
```
<!-- fmt: on -->

- `def cmd_day(s: Services) -> None:`: defines the function `cmd_day` taking s (Services) and returns `None`. Purpose: Step 4: the test tasks as one day under a budget.
- `"""Step 4: the test tasks as one day under a budget."""`: a docstring (documentation text). It says: "Step 4: the test tasks as one day under a budget."
- `test = s.split("test")`: sets `test` to the value of `s.split('test')`. `s.split('test')` is `s` cut into pieces at `'test'`.
- `config = _config(s)`: sets `config` to the value of `_config(s)`.
- `answers = _answers(s)`: sets `answers` to the value of `_answers(s)`.
- `days = []`: sets `days` to a list of 0 items.
- `for fraction in s.bar.day_budget_fractions:`: repeats the block below once for each `fraction` in `s.bar.day_budget_fractions`.
- `result = run_day(test, answers, lambda: _router(s, config), fraction)`: sets `result` to the value of `run_day(test, answers, lambda: _router(s, config), fraction)`. `lambda: _router(s, config)` is a small unnamed function of no arguments that gives `_router(s, config)`.
- `days.append(replace(result, outcomes=[]))`: runs `days.append(replace(result, outcomes=[]))` for its effect and ignores the result. `days.append(replace(result, outcomes=[]))` adds `replace(result, outcomes=[])` to the end of `days`.
- `print(`: runs `print(f'budget {fraction:.0%} of always-large: spent {result.spent:.6f} of {result.budg...` for its effect and ignores the result. `print(f'budget {fraction:.0%} of always-large: spent {result.spent:...` prints `f'budget {fraction:.0%} of always-large: spent {result.sp...`; the f-string inserts `fraction`, `result.spent`, `result.budget`, `result.under_budget` into the text.

<!-- fmt: off -->
```python
    dump_json(s.settings.reports_dir / "day.json", {"days": days})


def cmd_audit(s: Services) -> None:
    """Step 6: test-set false accepts, and the one change to the weakest check."""
    test = s.split("test")
    config = _config(s)
    outcomes = route_all(test, _router(s, config))
    before = false_accepts(outcomes, config)
    kind = weakest_kind(outcomes)
    change = None
    if kind is not None:
        changed, description = harden(config, kind)
        after_outcomes = route_all(test, _router(s, changed))
```
<!-- fmt: on -->

- `dump_json(s.settings.reports_dir / "day.json", {"days": days})`: runs `dump_json(s.settings.reports_dir / 'day.json', {'days': days})` for its effect and ignores the result.
- `def cmd_audit(s: Services) -> None:`: defines the function `cmd_audit` taking s (Services) and returns `None`. Purpose: Step 6: test-set false accepts, and the one change to the weakest check.
- `"""Step 6: test-set false accepts, and the one change to the weakest check."""`: a docstring (documentation text). It says: "Step 6: test-set false accepts, and the one change to the weakest check."
- `test = s.split("test")`: sets `test` to the value of `s.split('test')`. `s.split('test')` is `s` cut into pieces at `'test'`.
- `config = _config(s)`: sets `config` to the value of `_config(s)`.
- `outcomes = route_all(test, _router(s, config))`: sets `outcomes` to the value of `route_all(test, _router(s, config))`.
- `before = false_accepts(outcomes, config)`: sets `before` to the value of `false_accepts(outcomes, config)`.
- `kind = weakest_kind(outcomes)`: sets `kind` to the value of `weakest_kind(outcomes)`.
- `change = None`: sets `change` to the constant `None`.
- **New idea.** An **if** statement runs its indented block only when the condition is true. `elif` adds another condition to try; `else` runs when none held.
- `if kind is not None:`: runs the block below only if `kind is not None` is true. `kind is not None` tests that there is something in `kind`.
- `changed, description = harden(config, kind)`: sets `(changed, description)` to the value of `harden(config, kind)`.
- `after_outcomes = route_all(test, _router(s, changed))`: sets `after_outcomes` to the value of `route_all(test, _router(s, changed))`.

<!-- fmt: off -->
```python
        a, b = summarize(outcomes), summarize(after_outcomes)
        change = {
            "kind": kind,
            "description": description,
            "config_after": router_config_to_json(changed),
            "accuracy_before": a.accuracy.value,
            "accuracy_after": b.accuracy.value,
            "cost_per_correct_before": a.cost_per_correct,
            "cost_per_correct_after": b.cost_per_correct,
            "false_accepts_before": before["false_accepts"],
            "false_accepts_after": false_accepts(after_outcomes, changed)["false_accepts"],
        }
    dump_json(s.settings.reports_dir / "audit.json", {"before": before, "change": change})
    counts = {k: v["count"] for k, v in before["by_tier_and_check"].items()}
```
<!-- fmt: on -->

- `a, b = summarize(outcomes), summarize(after_outcomes)`: sets `(a, b)` to a tuple of 2 items.
- `change = {`: sets `change` to a dictionary with 9 entries.
- `dump_json(s.settings.reports_dir / "audit.json", {"before": before, "change": change})`: runs `dump_json(s.settings.reports_dir / 'audit.json', {'before': before, 'change': change})` for its effect and ignores the result.
- `counts = {k: v["count"] for k, v in before["by_tier_and_check"].items()}`: sets `counts` to the value of `{k: v['count'] for k, v in before['by_tier_and_check'].items()}`. `{k: v['count'] for k, v in before['by_tier_and_check'].items()}` builds a dictionary: for each `(k, v)` in `before['by_tier_and_check'].items()`; `before['by_tier_and_check'].items()` is the (key, value) pairs of `before['by_tier_and_check']`.

<!-- fmt: off -->
```python
    print(f"false accepts by tier/check: {counts}")
    print(f"change: {change}")


def cmd_report(s: Services) -> None:
    """Write reports/REPORT.md."""
    out = s.settings.reports_dir
    text = render_report(*(load_json(out / f"{n}.json") for n in ("models", "checks", "router", "day", "audit")))
    (out / "REPORT.md").write_text(text, encoding="utf-8")
    print(f"wrote {out / 'REPORT.md'}")


def cmd_health(s: Services) -> int:
    """Exit 0 when the data, prompts and prices are in place."""
```
<!-- fmt: on -->

- `print(f"false accepts by tier/check: {counts}")`: runs `print(f'false accepts by tier/check: {counts}')` for its effect and ignores the result. `print(f'false accepts by tier/check: {counts}')` prints `f'false accepts by tier/check: {counts}'`; the f-string inserts `counts` into the text.
- `print(f"change: {change}")`: runs `print(f'change: {change}')` for its effect and ignores the result. `print(f'change: {change}')` prints `f'change: {change}'`; the f-string inserts `change` into the text.
- `def cmd_report(s: Services) -> None:`: defines the function `cmd_report` taking s (Services) and returns `None`. Purpose: Write reports/REPORT.md.
- `"""Write reports/REPORT.md."""`: a docstring (documentation text). It says: "Write reports/REPORT.md."
- `out = s.settings.reports_dir`: sets `out` to the value of `s.settings.reports_dir`.
- `text = render_report(*(load_json(out / f"{n}.json") for n in ("models", "checks", "rout...`: sets `text` to the value of `render_report(*(load_json(out / f'{n}.json') for n in ('models', 'checks', 'r...`. `*(load_json(out / f'{n}.json') for n in ('model...` spreads the items of `(load_json(out / f'{n}.json...` into separate values; `(load_json(out / f'{n}.json') for n in ('models', 'checks', 'router...` builds a generator of values: for each `n` in `('models', 'checks', 'router', 'day',...`; the f-string inserts `n` into the text.
- `(out / "REPORT.md").write_text(text, encoding="utf-8")`: runs `(out / 'REPORT.md').write_text(text, encoding='utf-8')` for its effect and ignores the result. `(out / 'REPORT.md').write_text(text, encoding='utf-8')` writes `text` as the content of the file `out / 'REPORT.md'`.
- `print(f"wrote {out / 'REPORT.md'}")`: runs `print(f"wrote {out / 'REPORT.md'}")` for its effect and ignores the result. `print(f"wrote {out / 'REPORT.md'}")` prints `f"wrote {out / 'REPORT.md'}"`; the f-string inserts `out / 'REPORT.md'` into the text.
- `def cmd_health(s: Services) -> int:`: defines the function `cmd_health` taking s (Services) and returns `int`. Purpose: Exit 0 when the data, prompts and prices are in place.
- `"""Exit 0 when the data, prompts and prices are in place."""`: a docstring (documentation text). It says: "Exit 0 when the data, prompts and prices are in place."

<!-- fmt: off -->
```python
    ok = len(s.tasks) == 300 and len(s.split("build")) == 150 and len(s.split("test")) == 150
    for name in ("label.v2", "refund.v2", "policy.v2"):
        s.prompts.get(name)
    counts = f"tasks={len(s.tasks)} build={len(s.split('build'))} test={len(s.split('test'))}"
    print(f"{counts} prices={s.prices.as_of} -> {'ok' if ok else 'FAILED'}")
    return 0 if ok else 1


def cmd_parity(java: Path, python: Path) -> int:
    """Step 7: the Java reports must equal the Python reports (numbers to 1e-6)."""
    mismatches: list[str] = []
    for name in ("router.json", "day.json", "audit.json"):
        _diff(load_json(python / name), load_json(java / name), name, mismatches)
    for mismatch in mismatches[:20]:
```
<!-- fmt: on -->

- `ok = len(s.tasks) == 300 and len(s.split("build")) == 150 and len(s.split("test")) == 150`: sets `ok` to the value of `len(s.tasks) == 300 and len(s.split('build')) == 150 and (len(s.split('test')...`. `len(s.tasks)` is the number of items in `s.tasks`; `len(s.split('build'))` is the number of items in `s.split('build')`; `len(s.split('test'))` is the number of items in `s.split('test')`.
- `for name in ("label.v2", "refund.v2", "policy.v2"):`: repeats the block below once for each `name` in `('label.v2', 'refund.v2', 'policy.v2')`.
- `s.prompts.get(name)`: runs `s.prompts.get(name)` for its effect and ignores the result. `s.prompts.get(name)` looks up `name` in `s.prompts` (default (nothing) when missing).
- `counts = f"tasks={len(s.tasks)} build={len(s.split('build'))} test={len(s.split('test'))}"`: sets `counts` to the value of `f"tasks={len(s.tasks)} build={len(s.split('build'))} test={len(s.split('test'...`. the f-string inserts `len(s.tasks)`, `len(s.split('build'))`, `len(s.split('test'))` into the text; `len(s.tasks)` is the number of items in `s.tasks`; `len(s.split('build'))` is the number of items in `s.split('build')`.
- `print(f"{counts} prices={s.prices.as_of} -> {'ok' if ok else 'FAILED'}")`: runs `print(f"{counts} prices={s.prices.as_of} -> {('ok' if ok else 'FAILED')}")` for its effect and ignores the result. `print(f"{counts} prices={s.prices.as_of} -> {('ok' if ok else 'FAIL...` prints `f"{counts} prices={s.prices.as_of} -> {('ok' if ok else '...`; the f-string inserts `counts`, `s.prices.as_of`, `'ok' if ok else 'FAILED'` into the text; `'ok' if ok else 'FAILED'` gives `'ok'` when `ok` is true, otherwise `'FAILED'`.
- `return 0 if ok else 1`: ends the function and hands back `0 if ok else 1`. `0 if ok else 1` gives `0` when `ok` is true, otherwise `1`.
- `def cmd_parity(java: Path, python: Path) -> int:`: defines the function `cmd_parity` taking java (Path); python (Path) and returns `int`. Purpose: Step 7: the Java reports must equal the Python reports (numbers to 1e-6).
- `"""Step 7: the Java reports must equal the Python reports (numbers to 1e-6)."""`: a docstring (documentation text). It says: "Step 7: the Java reports must equal the Python reports (numbers to 1e-6)."
- `mismatches: list[str] = []`: declares a variable `mismatches` of type `list[str]` and sets it to `[]`.
- `for name in ("router.json", "day.json", "audit.json"):`: repeats the block below once for each `name` in `('router.json', 'day.json', 'audit.json')`.
- `_diff(load_json(python / name), load_json(java / name), name, mismatches)`: runs `_diff(load_json(python / name), load_json(java / name), name, mismatches)` for its effect and ignores the result.
- `for mismatch in mismatches[:20]:`: repeats the block below once for each `mismatch` in `mismatches[:20]`. `mismatches[:20]` is a slice (a part) of `mismatches`.

<!-- fmt: off -->
```python
        print("MISMATCH", mismatch)
    print(
        "parity:",
        "OK, the Java reports equal the Python reports" if not mismatches else f"{len(mismatches)} differences",
    )
    return 1 if mismatches else 0


def _diff(a: Any, b: Any, path: str, out: list[str]) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append(f"{path}.{key} is missing on one side")
            else:
                _diff(a[key], b[key], f"{path}.{key}", out)
```
<!-- fmt: on -->

- `print("MISMATCH", mismatch)`: runs `print('MISMATCH', mismatch)` for its effect and ignores the result. `print('MISMATCH', mismatch)` prints `'MISMATCH'`, `mismatch`.
- `print(`: runs `print('parity:', 'OK, the Java reports equal the Python reports' if not mismatches else...` for its effect and ignores the result. `print('parity:', 'OK, the Java reports equal the Python reports' if...` prints `'parity:'`, `'OK, the Java reports equal the Python reports' if not mi...`; `'OK, the Java reports equal the Python reports' if not mismatches e...` gives `'OK, the Java reports equal the Pytho...` when `not mismatches` is true, otherwise `f'{len(mismatches)} differences'`; the f-string inserts `len(mismatches)` into the text.
- `return 1 if mismatches else 0`: ends the function and hands back `1 if mismatches else 0`. `1 if mismatches else 0` gives `1` when `mismatches` is true, otherwise `0`.
- `def _diff(a: Any, b: Any, path: str, out: list[str]) -> None:`: defines the function `_diff` taking a (Any); b (Any); path (str); out (list[str]) and returns `None`.
- `if isinstance(a, dict) and isinstance(b, dict):`: runs the block below only if `isinstance(a, dict) and isinstance(b, dict)` is true. `isinstance(a, dict)` is whether `a` is a `dict`; `isinstance(b, dict)` is whether `b` is a `dict`.
- `for key in sorted(set(a) | set(b)):`: repeats the block below once for each `key` in `sorted(set(a) | set(b))`. `sorted(set(a) | set(b))` is `set(a) | set(b)` in sorted order; `set(a)` is `a` as a set (each value once); `set(b)` is `b` as a set (each value once).
- `if key not in a or key not in b:`: runs the block below only if `key not in a or key not in b` is true.
- `out.append(f"{path}.{key} is missing on one side")`: runs `out.append(f'{path}.{key} is missing on one side')` for its effect and ignores the result. `out.append(f'{path}.{key} is missing on one side')` adds `f'{path}.{key} is missing on one side'` to the end of `out`; the f-string inserts `path`, `key` into the text.
- `else:` the block below runs when none of the conditions above held.
- `_diff(a[key], b[key], f"{path}.{key}", out)`: runs `_diff(a[key], b[key], f'{path}.{key}', out)` for its effect and ignores the result. the f-string inserts `path`, `key` into the text.

<!-- fmt: off -->
```python
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path} has length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b, strict=False)):
            _diff(x, y, f"{path}[{i}]", out)
    elif isinstance(a, int | float) and isinstance(b, int | float) and not isinstance(a, bool):
        if abs(a - b) > 1e-6:
            out.append(f"{path}: {a} vs {b}")
    elif a != b:
        out.append(f"{path}: {a!r} vs {b!r}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run one sub-command; returns the process exit code."""
```
<!-- fmt: on -->

- `elif isinstance(a, list) and isinstance(b, list):`: runs the block below only if `isinstance(a, list) and isinstance(b, list)` is true. `isinstance(a, list)` is whether `a` is a `list`; `isinstance(b, list)` is whether `b` is a `list`.
- `if len(a) != len(b):`: runs the block below only if `len(a) != len(b)` is true. `len(a)` is the number of items in `a`; `len(b)` is the number of items in `b`.
- `out.append(f"{path} has length {len(a)} vs {len(b)}")`: runs `out.append(f'{path} has length {len(a)} vs {len(b)}')` for its effect and ignores the result. `out.append(f'{path} has length {len(a)} vs {len(b)}')` adds `f'{path} has length {len(a)} vs {len(b)}'` to the end of `out`; the f-string inserts `path`, `len(a)`, `len(b)` into the text; `len(a)` is the number of items in `a`.
- `for i, (x, y) in enumerate(zip(a, b, strict=False)):`: repeats the block below once for each `(i, (x, y))` in `enumerate(zip(a, b, strict=False))`. `enumerate(zip(a, b, strict=False))` is pairs (position, item) for the items of `zip(a, b, strict=False)`; `zip(a, b, strict=False)` is items of `a`, `b` taken together, position by position.
- `_diff(x, y, f"{path}[{i}]", out)`: runs `_diff(x, y, f'{path}[{i}]', out)` for its effect and ignores the result. the f-string inserts `path`, `i` into the text.
- `elif isinstance(a, int | float) and isinstance(b, int | float) and not isinstance(a, bo...`: runs the block below only if `isinstance(a, int | float) and isinstance(b, int | float) and (not isinstance...` is true. `isinstance(a, int | float)` is whether `a` is a `int | float`; `isinstance(b, int | float)` is whether `b` is a `int | float`; `isinstance(a, bool)` is whether `a` is a `bool`.
- `if abs(a - b) > 1e-6:`: runs the block below only if `abs(a - b) > 1e-06` is true. `abs(a - b)` is the size of `a - b` without its sign.
- `out.append(f"{path}: {a} vs {b}")`: runs `out.append(f'{path}: {a} vs {b}')` for its effect and ignores the result. `out.append(f'{path}: {a} vs {b}')` adds `f'{path}: {a} vs {b}'` to the end of `out`; the f-string inserts `path`, `a`, `b` into the text.
- `elif a != b:`: runs the block below only if `a != b` is true.
- `out.append(f"{path}: {a!r} vs {b!r}")`: runs `out.append(f'{path}: {a!r} vs {b!r}')` for its effect and ignores the result. `out.append(f'{path}: {a!r} vs {b!r}')` adds `f'{path}: {a!r} vs {b!r}'` to the end of `out`; the f-string inserts `path`, `a`, `b` into the text.
- `def main(argv: Sequence[str] | None = None) -> int:`: defines the function `main` taking argv (Sequence[str] | None), default None and returns `int`. Purpose: Run one sub-command; returns the process exit code.
- `"""Run one sub-command; returns the process exit code."""`: a docstring (documentation text). It says: "Run one sub-command; returns the process exit code."

<!-- fmt: off -->
```python
    parser = argparse.ArgumentParser(prog="cost-router", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("models", "checks", "tune", "router", "day", "audit", "report", "all", "health"):
        sub.add_parser(name)
    parity = sub.add_parser("parity")
    parity.add_argument("--java", type=Path, required=True)
    parity.add_argument("--python", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "parity":
        return cmd_parity(args.java, args.python)
    env = dict(process_env())
    configure_logging(env.get("LOG_LEVEL", "INFO"))
    try:
        services = build_services(env, ROOT)
```
<!-- fmt: on -->

- `parser = argparse.ArgumentParser(prog="cost-router", description=__doc__)`: sets `parser` to the value of `argparse.ArgumentParser(prog='cost-router', description=__doc__)`.
- `sub = parser.add_subparsers(dest="command", required=True)`: sets `sub` to the value of `parser.add_subparsers(dest='command', required=True)`.
- `for name in ("models", "checks", "tune", "router", "day", "audit", "report", "all", "he...`: repeats the block below once for each `name` in `('models', 'checks', 'tune', 'router', 'day', 'audit', 'report', 'a...`.
- `sub.add_parser(name)`: runs `sub.add_parser(name)` for its effect and ignores the result.
- `parity = sub.add_parser("parity")`: sets `parity` to the value of `sub.add_parser('parity')`.
- `parity.add_argument("--java", type=Path, required=True)`: runs `parity.add_argument('--java', type=Path, required=True)` for its effect and ignores the result.
- `parity.add_argument("--python", type=Path, required=True)`: runs `parity.add_argument('--python', type=Path, required=True)` for its effect and ignores the result.
- `args = parser.parse_args(argv)`: sets `args` to the value of `parser.parse_args(argv)`.
- `if args.command == "parity":`: runs the block below only if `args.command == 'parity'` is true.
- `return cmd_parity(args.java, args.python)`: ends the function and hands back `cmd_parity(args.java, args.python)`.
- `env = dict(process_env())`: sets `env` to the value of `dict(process_env())`. `dict(process_env())` is a dictionary made from `process_env()`.
- `configure_logging(env.get("LOG_LEVEL", "INFO"))`: runs `configure_logging(env.get('LOG_LEVEL', 'INFO'))` for its effect and ignores the result. `env.get('LOG_LEVEL', 'INFO')` looks up `'LOG_LEVEL'` in `env` (default `'INFO'` when missing).
- **New idea.** **try/except** handles errors. The code in `try:` runs; if it raises an error of the type named in `except`, Python jumps to that block instead of stopping. `finally:` always runs, error or not. `else:` runs only when no error occurred.
- `try:`: tries the block below; if it raises an error that one of the `except` lines names, that handler runs instead of stopping the program.
- `services = build_services(env, ROOT)`: sets `services` to the value of `build_services(env, ROOT)`.

<!-- fmt: off -->
```python
        if args.command == "health":
            return cmd_health(services)
        steps = {
            "models": cmd_models,
            "checks": cmd_checks,
            "tune": cmd_tune,
            "router": cmd_router,
            "day": cmd_day,
            "audit": cmd_audit,
            "report": cmd_report,
        }
        for step in list(steps) if args.command == "all" else [args.command]:
            steps[step](services)
    except ConfigError as error:
```
<!-- fmt: on -->

- `if args.command == "health":`: runs the block below only if `args.command == 'health'` is true.
- `return cmd_health(services)`: ends the function and hands back `cmd_health(services)`.
- `steps = {`: sets `steps` to a dictionary with 7 entries.
- `for step in list(steps) if args.command == "all" else [args.command]:`: repeats the block below once for each `step` in `list(steps) if args.command == 'all' else [args.command]`. `list(steps) if args.command == 'all' else [args.command]` gives `list(steps)` when `args.command == 'all'` is true, otherwise `[args.command]`; `list(steps)` is `steps` copied into a list.
- `steps[step](services)`: runs `steps[step](services)` for its effect and ignores the result.
- `except ConfigError as error:`: runs when the error is `ConfigError`, calling it `error`.

<!-- fmt: off -->
```python
        print(f"configuration error: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        LOG.warning("interrupted; exchanges already recorded are kept, rerun to resume")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
<!-- fmt: on -->

- `print(f"configuration error: {error}", file=sys.stderr)`: runs `print(f'configuration error: {error}', file=sys.stderr)` for its effect and ignores the result. `print(f'configuration error: {error}', file=sys.stderr)` prints `f'configuration error: {error}'`; the f-string inserts `error` into the text.
- `return 2`: ends the function and hands back `2`.
- `except KeyboardInterrupt:`: runs when the error is `KeyboardInterrupt`.
- `LOG.warning("interrupted; exchanges already recorded are kept, rerun to resume")`: runs `LOG.warning('interrupted; exchanges already recorded are kept, rerun to resume')` for its effect and ignores the result. `LOG.warning('interrupted; exchanges already recorded are kept, reru...` writes a warning log line.
- `return 130`: ends the function and hands back `130`.
- `return 0`: ends the function and hands back `0`.
- **New idea.** `if __name__ == "__main__":` runs its block only when the file is started as a program, not when another file imports it.
- `if __name__ == "__main__":`: runs the block below only if `__name__ == '__main__'` is true.
- `sys.exit(main())`: runs `sys.exit(main())` for its effect and ignores the result. `sys.exit(main())` ends the program with exit code `main()`.

#### `src/cost_router/interfaces/wiring.py`

<!-- fmt: off -->
```python
"""The composition root: build the adapters and services from settings."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from cost_router.application.ports import ChatModel, Mapper, PromptStore
from cost_router.application.tiers import ModelTiers
from cost_router.domain.pricing import PriceTable
from cost_router.domain.routing import Bar
from cost_router.domain.tasks import Task
from cost_router.infrastructure.data import load_bar, load_prices, load_tasks
```
<!-- fmt: on -->

- `"""The composition root: build the adapters and services from settings."""`: a docstring (documentation text). It says: "The composition root: build the adapters and services from settings."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from collections.abc import Mapping`: takes the name(s) `Mapping` from the module `collections.abc` (abstract container types used in annotations).
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `from cost_router.application.ports import ChatModel, Mapper, PromptStore`: takes the name(s) `ChatModel, Mapper, PromptStore` from the module `cost_router.application.ports` (a module of this project).
- `from cost_router.application.tiers import ModelTiers`: takes the name(s) `ModelTiers` from the module `cost_router.application.tiers` (a module of this project).
- `from cost_router.domain.pricing import PriceTable`: takes the name(s) `PriceTable` from the module `cost_router.domain.pricing` (a module of this project).
- `from cost_router.domain.routing import Bar`: takes the name(s) `Bar` from the module `cost_router.domain.routing` (a module of this project).
- `from cost_router.domain.tasks import Task`: takes the name(s) `Task` from the module `cost_router.domain.tasks` (a module of this project).
- `from cost_router.infrastructure.data import load_bar, load_prices, load_tasks`: takes the name(s) `load_bar, load_prices, load_tasks` from the module `cost_router.infrastructure.data` (a module of this project).

<!-- fmt: off -->
```python
from cost_router.infrastructure.llm.factory import build_chat_model
from cost_router.infrastructure.parallel import thread_mapper
from cost_router.infrastructure.prompts import FilePromptStore
from cost_router.infrastructure.settings import Settings


@dataclass(frozen=True)
class Services:
    """Everything a command needs."""

    settings: Settings
    tasks: list[Task]
    bar: Bar
    prices: PriceTable
```
<!-- fmt: on -->

- `from cost_router.infrastructure.llm.factory import build_chat_model`: takes the name(s) `build_chat_model` from the module `cost_router.infrastructure.llm.factory` (a module of this project).
- `from cost_router.infrastructure.parallel import thread_mapper`: takes the name(s) `thread_mapper` from the module `cost_router.infrastructure.parallel` (a module of this project).
- `from cost_router.infrastructure.prompts import FilePromptStore`: takes the name(s) `FilePromptStore` from the module `cost_router.infrastructure.prompts` (a module of this project).
- `from cost_router.infrastructure.settings import Settings`: takes the name(s) `Settings` from the module `cost_router.infrastructure.settings` (a module of this project).
- **New idea.** A **class** describes a kind of object: the data it holds and the methods that work on it. Calling the class, `Name(...)`, creates an object (an *instance*). `class B(A)` means B *inherits* from A: it has everything A has and may add or replace things.
- **New idea.** `@dataclass` is a **decorator** (a function applied to the class below it). It reads the annotated fields and writes `__init__`, `__repr__` and `__eq__` for you. `frozen=True` forbids changing a field after creation.
- `class Services:`: defines the class `Services`. Decorators: `dataclass(frozen=True)`. Purpose: Everything a command needs.
- `"""Everything a command needs."""`: a docstring (documentation text). It says: "Everything a command needs."
- `settings: Settings`: declares a field of the class `settings` of type `Settings` (no value yet).
- `tasks: list[Task]`: declares a field of the class `tasks` of type `list[Task]` (no value yet).
- `bar: Bar`: declares a field of the class `bar` of type `Bar` (no value yet).
- `prices: PriceTable`: declares a field of the class `prices` of type `PriceTable` (no value yet).

<!-- fmt: off -->
```python
    prompts: PromptStore
    model: ChatModel
    mapper: Mapper

    @property
    def tiers(self) -> ModelTiers:
        """The three tiers on the configured models."""
        return ModelTiers(self.model, self.prompts, self.settings.models, self.prices)

    def split(self, name: str) -> list[Task]:
        """The `build` or `test` tasks."""
        return [t for t in self.tasks if t.split == name]
```
<!-- fmt: on -->

- `prompts: PromptStore`: declares a field of the class `prompts` of type `PromptStore` (no value yet).
- `model: ChatModel`: declares a field of the class `model` of type `ChatModel` (no value yet).
- `mapper: Mapper`: declares a field of the class `mapper` of type `Mapper` (no value yet).
- **New idea.** A **decorator** is a line `@name` above a function or class. It passes the function to `name` and uses what comes back instead. It is a way to add behaviour without editing the function.
- **New idea.** `@property` lets a method be read like an attribute, without brackets.
- **New idea.** A **method** is a function defined inside a class. Its first parameter, called `self`, is the object the method was called on, so `self.x` is that object's own attribute `x`.
- `def tiers(self) -> ModelTiers:`: defines the method `tiers` taking no arguments and returns `ModelTiers`. Decorators: `property`. Purpose: The three tiers on the configured models.
- `"""The three tiers on the configured models."""`: a docstring (documentation text). It says: "The three tiers on the configured models."
- `return ModelTiers(self.model, self.prompts, self.settings.models, self.prices)`: ends the function and hands back `ModelTiers(self.model, self.prompts, self.settings.models, self.prices)`.
- `def split(self, name: str) -> list[Task]:`: defines the method `split` taking name (str) and returns `list[Task]`. Purpose: The `build` or `test` tasks.
- `"""The 'build' or 'test' tasks."""`: a docstring (documentation text). It says: "The `build` or `test` tasks."
- `return [t for t in self.tasks if t.split == name]`: ends the function and hands back `[t for t in self.tasks if t.split == name]`. `[t for t in self.tasks if t.split == name]` builds a list: for each `t` in `self.tasks`, keeping only those for which `t.split == name` is true.

<!-- fmt: off -->
```python
def build_services(env: Mapping[str, str], root: Path) -> Services:
    """Read settings and data, and build the model adapter named by LLM_PROVIDER."""
    settings = Settings.from_env(env, root)
    return Services(
        settings=settings,
        tasks=load_tasks(settings.data_dir),
        bar=load_bar(settings.config_dir),
        prices=load_prices(settings.config_dir),
        prompts=FilePromptStore(settings.prompts_dir),
        model=build_chat_model(env, settings.fixtures_dir),
        mapper=thread_mapper(settings.workers),
    )
```
<!-- fmt: on -->

- `def build_services(env: Mapping[str, str], root: Path) -> Services:`: defines the function `build_services` taking env (Mapping[str, str]); root (Path) and returns `Services`. Purpose: Read settings and data, and build the model adapter named by LLM_PROVIDER.
- `"""Read settings and data, and build the model adapter named by LLM_PROVIDER."""`: a docstring (documentation text). It says: "Read settings and data, and build the model adapter named by LLM_PROVIDER."
- `settings = Settings.from_env(env, root)`: sets `settings` to the value of `Settings.from_env(env, root)`.
- `return Services(`: ends the function and hands back `Services(settings=settings, tasks=load_tasks(settings.data_dir), bar=load_bar...`.

## Try it yourself

1. `wc -l src/cost_router/interfaces/__init__.py src/cost_router/interfaces/cli.py src/cost_router/interfaces/wiring.py` prints the line count of the first files; the tables above show the same numbers.
2. `.venv/bin/python -c "import cost_router.interfaces.cli; print('imports fine')"` prints `imports fine`.
3. `.venv/bin/lint-imports` ends with `Contracts: 2 kept, 0 broken.`
4. `.venv/bin/python -m pytest tests/unit -q -k cli | tail -3` runs the tests that exercise this layer and ends with a line such as `N passed`.
5. `grep -c "^def \|^class \|^    def " src/cost_router/interfaces/cli.py` counts the functions and classes in the first file.

## Mistakes people make

- Putting business rules here; they belong in the domain.
- Doing work when the file is imported instead of in `main`.
- Forgetting that the exit code is how scripts and `make` know a command failed.
- Letting the wiring grow into a second application layer.
- Parsing arguments by hand when `argparse` is in the standard library.

## Check yourself

1. **What is the wiring?**  
   The code that builds the adapters and passes them to the application functions.
2. **What does exit code 0 mean?**  
   Success; any other number means failure.
3. **Which layer may import all the others?**  
   The interfaces layer.
4. **Where do business rules belong?**  
   In the domain layer.
5. **What starts a command?**  
   `main` reads the arguments and calls the matching `cmd_` function.

## Further reading

The Python language reference: https://docs.python.org/3/reference/ and the tutorial https://docs.python.org/3/tutorial/ (both for Python 3.13; the project accepts 3.12 or newer).
