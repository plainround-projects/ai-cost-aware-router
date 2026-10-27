"""The human-readable report: plain tables built from the stored results."""

from __future__ import annotations

from typing import Any

from cost_router.domain.pricing import TIERS


def pct(value: float) -> str:
    """A rate as a percentage with one decimal."""
    return f"{value * 100:.1f}%"


def money(value: float | None) -> str:
    """Dollars with six decimals, or n/a."""
    return "n/a" if value is None else f"${value:.6f}"


def interval(low: float, high: float) -> str:
    """A 95% interval in percent."""
    return f"[{pct(low)}, {pct(high)}]"


def render_report(
    models: dict[str, Any], checks: dict[str, Any], router: dict[str, Any], day: dict[str, Any], audit: dict[str, Any]
) -> str:
    """The whole report as Markdown."""
    out = ["# Cost-aware router: results", ""]
    out += ["## Step 1: each model alone, 150 build tasks", ""]
    out += [
        "| Model | Kind | Accuracy (95% interval) | Cost per call | Cost per correct answer |",
        "| --- | --- | --- | --- | --- |",
    ]
    for tier in TIERS:
        for kind, cell in models["table"][tier].items():
            a = cell["accuracy"]
            out.append(
                f"| {tier} | {kind} | {pct(a['value'])} {interval(a['low'], a['high'])} | {money(cell['cost_per_call'])} | {money(cell['cost_per_correct'])} |"
            )
    out += [
        "",
        "Cheapest tier within the agreed margin of the large tier, per kind: "
        + ", ".join(f"{k}: {v or 'none'}" for k, v in models["cheapest_matching"].items())
        + ".",
        "",
    ]
    out += ["## Step 2: the checks, measured against the truth (build set)", ""]
    out += [
        "| Tier | Kind | Check | Accepted | False-accept rate | False-reject rate | Wrong among accepted | Over the bar |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    bar = checks["bar"]
    for tier in TIERS:
        for kind, by_check in checks["rates"][tier].items():
            for name, r in by_check.items():
                over = "YES" if r["false_accept_rate"] > bar else "no"
                out.append(
                    f"| {tier} | {kind} | {name} | {r['accepted']} | {pct(r['false_accept_rate'])} | {pct(r['false_reject_rate'])} | {pct(r['wrong_among_accepted'])} | {over} |"
                )
    out += [
        "",
        f"Bar agreed in advance: a check whose false-accept rate is above {pct(bar)} is not trusted to stop the cascade.",
        "",
    ]
    cfg = router["config"]
    out += ["## Step 3: the configuration the build set produced", "", f"`{cfg}`", ""]
    out += ["## Step 5: the router and each model alone, 150 test tasks", ""]
    out += [
        "| Method | Accuracy (95% interval) | Total cost | Cost per correct (95% interval) | Served by | Escalated to a person |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, s in router["methods"].items():
        a = s["accuracy"]
        low, high = s["cost_per_correct_interval"]
        out.append(
            f"| {name} | {pct(a['value'])} {interval(a['low'], a['high'])} | {money(s['total_cost'])} | {money(s['cost_per_correct'])} [{money(low)}, {money(high)}] | {s['served_by']} | {s['escalated']} |"
        )
    v = router["verdict"]
    out += [
        "",
        f"Router against the large model alone: accuracy difference {v['accuracy_difference_vs_large']:+.3f} (95% interval {v['accuracy_difference_interval'][0]:+.3f} to {v['accuracy_difference_interval'][1]:+.3f}), margin {v['margin']}. Verdict: **{v['verdict']}**.",
        "",
    ]
    out += ["## Step 4: one day under a budget", ""]
    out += [
        "| Budget (share of always-large) | Spent | Under budget | Requests over the cap | Accuracy before 80% | Accuracy after 80% | Large-tier answers after 80% |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for d in day["days"]:
        out.append(
            f"| {pct(d['fraction'])} ({money(d['budget'])}) | {money(d['spent'])} | {d['under_budget']} | {d['requests_over_cap']} | {pct(d['accuracy_before']['value'])} (n={d['accuracy_before']['trials']}) | {pct(d['accuracy_after']['value'])} (n={d['accuracy_after']['trials']}) | {d['large_served_after']} |"
        )
    out += ["", "## Step 6: accepted answers that were wrong (test set)", ""]
    out += [f"`{audit['before']['by_tier_and_check']}`", ""]
    ch = audit["change"]
    if ch:
        out += [
            f"Change ({ch['description']}): accuracy {pct(ch['accuracy_before'])} to {pct(ch['accuracy_after'])}; cost per correct {money(ch['cost_per_correct_before'])} to {money(ch['cost_per_correct_after'])}; false accepts {ch['false_accepts_before']} to {ch['false_accepts_after']}.",
            "",
        ]
    return "\n".join(out) + "\n"
