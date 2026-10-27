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
    s.settings.router_config_path.parent.mkdir(parents=True, exist_ok=True)
    s.settings.router_config_path.write_text(json.dumps(router_config_to_json(config), indent=2, sort_keys=True) + "\n")
    print(f"router configuration: {router_config_to_json(config)}")


def _router(s: Services, config: RouterConfig) -> CostRouter:
    return CostRouter(s.tiers, make_checks(s.tiers, config), config)


def _config(s: Services) -> RouterConfig:
    return load_router_config(s.settings.router_config_path)


def _summary_json(summary: Any) -> dict[str, Any]:
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
        print(f"configuration error: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        LOG.warning("interrupted; exchanges already recorded are kept, rerun to resume")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
