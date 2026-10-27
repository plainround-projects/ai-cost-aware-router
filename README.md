# ai-cost-aware-router

A router that sits in front of three models of rising price and skill. It sends each task to the cheapest tier that its measured checks trust, escalates when a check fails, never lets one request pass a per-request cap, holds a daily budget by narrowing the tiers instead of refusing work, and logs the cost of every decision. The study around it reports accuracy and cost per correct answer against each model alone, with intervals, and audits the answers its checks wrongly let through.

| | |
| --- | --- |
| **Lesson** | `/prep/ai/project-cost-aware-router`, "Cost-aware router" (`data-structure-explainer/src/content/tracks/ai/104-project-cost-aware-router.md` in the Plainround app) |
| **Planned hours** | 10 |
| **Level** | Intermediate |
| **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md), decisions: [docs/adr](docs/adr), prompts: [prompts](prompts) with a [changelog](prompts/CHANGELOG.md) |

## Prerequisites

| Tool | Version | Used for |
| --- | --- | --- |
| Python | 3.12 or 3.13 (tested with 3.13) | the router, the study, the tests |
| GNU Make | 3.81 or newer | every command below |
| JDK | JDK 21 or newer (tested with 25); Maven 3.9.9 comes with the checked-in wrapper `java/mvnw` | the Java (Spring AI) port, step 7 |
| Spring AI | 2.0.1 (with the Spring Boot 4.0.5 dependency BOM) | the Java port's live adapter |
| ollama | 0.40 or newer, only for `make record` | the three tiers: `qwen2.5:0.5b` (small), `llama3.2:1b` (medium), `qwen2.5:1.5b` (large) |
| Python packages | `httpx`; pytest, pytest-cov, ruff, mypy, import-linter, pip-audit for development, hash-pinned in `requirements.lock` and `requirements-dev.lock` | everything |

No cloud account and no API key. `make up`, `make run`, `make test` and `make lint` run offline: every model call is answered from [tests/fixtures/recorded.jsonl](tests/fixtures), which holds the real outputs of the three local models. A hosted model is an opt-in: see "Live runs".

## Setup, run, test, stop

```bash
make up            # create .venv from the hash-pinned lock file and .env from .env.example (no services)
make run           # the whole study from the recorded fixtures: models, checks, tune, router, day, audit, report
make models        # step 1 alone (also: make checks, make tune, make router, make day, make false-accepts, make report)
make test          # unit tests, offline, with coverage (domain and application at 95% or more)
make test-e2e      # replay the study and compare it with the committed configuration and reports
make lint          # ruff check, ruff format check, mypy --strict, import-linter
make audit         # known-vulnerability check of the locked dependencies
make java-test     # the Java port: unit tests, ArchUnit, and the parity test against the Python reports
make parity        # run the Java jar and compare its reports with the Python ones
make test-live     # opt-in: a local server answers, and Claude answers when ANTHROPIC_API_KEY is set
make record        # re-run everything against local ollama and append new exchanges to the fixtures
make down          # nothing to stop: this project starts no services
```

`make help` lists every target. Results land in [reports/](reports): `REPORT.md` (read this first), `models.json`, `checks.json`, `router.json`, `day.json`, `audit.json` and `decisions.jsonl` (one line per routed test task: tiers tried, each check result, cost). The configuration that step 3 derives from the build set is [config/router.json](config/router.json). Logs are JSON on standard error and never contain prompt or answer text.

## The sample data

Generated deterministically by [scripts/make_data.py](scripts/make_data.py) (seed 2026), committed in [data/](data):

- 300 tasks whose answers code can check: **120 category labels** (billing, shipping, returns, account), **100 refund amounts** computed from an order and the refund policy by `domain/tasks.py::refund_cents`, **80 short policy answers** graded by which of ten policy lines the answer quotes.
- Half easy (one order, plain wording, one main request) and half hard (two orders, a partial return, a damaged-item exception; for labels, a second request from another category in the same email).
- Split once, stratified by kind and difficulty, into 150 `build` tasks (used for steps 1 to 3) and 150 `test` tasks (used for steps 4 to 6).
- `config/prices.json`: the dated price table (as of 2026-10-27): small $0.0002, medium $0.0005, large $0.0012 per 1,000 billed tokens. These are illustrative; the three tiers run locally and cost nothing, so the table stands in for the price list of three hosted models. `config/bar.json`: the numbers agreed before any model answered (committed first, `6284d97`).

## Done when: the lesson's checklist and the proof for each line

All numbers come from `make run` on the committed fixtures; `reports/REPORT.md` has the full tables.

| # | Done when (from the lesson) | Command | What proves it |
| --- | --- | --- | --- |
| 1 | A table gives accuracy and cost per correct answer for each model and task kind, and names the cheapest model that reaches the large model's accuracy on each kind, if any does. | `make models` | Step 1 table in the report. Build-set accuracy small / medium / large: label 26.7% / 18.3% / **88.3%**, policy 60.0% / **95.0%** / 87.5%, refund 20.0% / **36.0%** / 14.0%. Cheapest tier within 2 points of the large tier: label **large** (no cheaper tier comes close), policy **medium**, refund **small** (every model is weak at refunds; the large one is the worst). As in the lesson, a bigger model is not better on every kind. |
| 2 | The false-accept and false-reject rate of each check is reported, and any check above the level set in advance is replaced or dropped. | `make checks` | Bar: false-accept rate at most 10% (`config/bar.json`). The label check is over it at small (100%, shape and two-sample agreement alike) and at medium (51%); the policy "quoted line exists" check is over it at every tier (100%, 100%, 60%); the refund check (recomputed by code) is at 0% at every tier. Dropped: label never starts below large. Replaced: the policy check is replaced by a stronger one in step 6. Agreement of two samples barely helps for the same reason as in the lesson: the small model repeats its own bias (100% to 100%). |
| 3 | Every decision is logged with the tiers tried, each check result and the cost, and no logged request spent more than its cap. | `make router` | [reports/decisions.jsonl](reports/decisions.jsonl) has 150 lines with `attempts` (tier, passed, cost). The cap is $0.0008 per request; the largest request spend in the test run is **$0.000547**, no request is tagged `cap`. The cap is checked before each call from a conservative estimate (three characters per token plus the output cap) and verified afterwards from the billed tokens. |
| 4 | The day ends under budget, no request passed its cap, and the report shows accuracy before and after the 80% point. | `make day` | Budget 50% of the always-large cost: spent $0.021643 of $0.021698, **under**; 0 requests over the cap; accuracy before the 80% point 69.8% (43 tasks), after 15.0% (107 tasks), and **no large-tier answer after the 80% point**. Budget 30%: spent $0.012989 of $0.013019, under; accuracy 66.7% (27 tasks) before and 5.7% (123 tasks) after. After the 80% point the router keeps answering with the two cheaper tiers until the money left cannot pay for the next call, then hands the task to a person. |
| 5 | The router's accuracy and cost per correct answer are reported next to each single model's, with intervals, with the share of tasks per tier, and it is stated whether the router matched the large model's accuracy within an agreed margin at a lower cost per correct answer. | `make router` | Test set (150 tasks): router **71.3%** [63.6%, 78.0%] at $0.000556 per correct [$0.000498, $0.000628]; large 59.3% [51.3%, 66.9%] at $0.000488 [$0.000435, $0.000564]; medium 42.0%; small 30.7%. Served by: large 92, medium 19, small 1, a person 38. Paired accuracy difference against large: **+12.0 points** [+7.3, +18.0], above the 2-point margin. **Verdict: not cheaper** (cost per correct is 14% higher): the router is much more accurate than the large model alone, because its checks reject wrong answers and the refund tasks go to the model that is best at them, but it does not match the lesson's saving. `router_no_bar` (every kind starts at small, the bar ignored) costs $0.000354 per correct, 27% less than large, at 40.7% accuracy. Escalations to a person: 38 of 150, reported, not folded into accuracy. |
| 6 | The false-accept count per tier and check is reported, with one change to the weakest check and its effect on accuracy and cost. | `make false-accepts` | Accepted-but-wrong answers on the test set: 5, all at the large tier through the policy quote check (`large/policy_quote`: t235, t250, t255, t290, t295). The change: policy answers must quote the line that best matches the question's words (a code check, no model call). Effect: accuracy 71.3% to 66.7%, cost per correct $0.000556 to $0.000595, false accepts 5 to 3. The change did not pay: it shed some wrong answers and many right ones; a crude word-overlap check is a weak substitute for retrieval. |
| 7 | The Java router's accuracy, tier shares and cost per correct fall inside the Python intervals, and no request passes its cap. | `make java-test`, `make parity` | The Java port reads the same data, prompts, price table, bars and fixtures and writes the same `router.json`, `day.json` and `audit.json`; the parity test compares every number to 1e-6 and passes, so accuracy, tier shares, cost per correct, the day replays and the audit are identical, and so is the maximum request spend (below the cap). |

No Done-when line needs a hosted key.

## Stretch goals

| Stretch (from the lesson) | Built? |
| --- | --- |
| A reasoning model as a fourth tier with a thinking budget, for refund tasks that fail twice. | No. |
| Cache answers to repeated policy questions in front of the router. | No. |
| Learn the difficulty signal from the build set with a small classifier. | No. The build set does choose which kinds start higher and which hard tasks skip the small tier, with the hand-written signal (two order ids, or a damage or partial-return word). |

## Live runs

```bash
# Local models (ollama running, the three models pulled): add real exchanges to the fixtures.
LLM_PROVIDER=local make record

# Claude as the three tiers (the key stays in your environment, never in a file):
export ANTHROPIC_API_KEY=...        # not in .env
LLM_PROVIDER=anthropic TIER_SMALL=claude-haiku-5-5 TIER_MEDIUM=claude-sonnet-5-5 TIER_LARGE=claude-opus-5-5 \
  LLM_RECORD_TO=tests/fixtures/claude.jsonl make run
make test-live      # RUN_LIVE=1: one call to the local server, one to Claude if the key is set
```

Edit `config/prices.json` to the real price list when you run hosted models. The fixture key hashes the model id, the decoding settings and the prompt, so fixtures for different models and prompts coexist in one folder.

## What is simplified for teaching

- Three small local models stand in for three hosted ones, and the prices are illustrative. The models are weak (best overall accuracy 59%), so the numbers show the mechanics of the router, not what production models would do.
- The refund check recomputes the amount from the structured order, which is also how the task is graded, so it cannot accept a wrong answer by construction. A production check would recompute from the orders service, which can itself disagree with what the customer wrote.
- The tuning bar applies to the share of wrong answers a check accepts. With few wrong answers (medium on policy: 2 of 40) that rate is noisy; the report also prints the share of accepted answers that are wrong (5.0% there).
- Latency is not part of this study.

## Project structure

```text
src/cost_router/
  domain/            tasks and refund arithmetic, answer parsing, grading and checks, price table, router
                     configuration and day budget, the difficulty signal, metrics (rates, bootstrap), statistics.
                     Depends on the standard library only.
  application/       ModelTiers (prompt, call, cost), AnswerChecks, CostRouter, the experiments of each step,
                     the report text; ports (ChatModel, PromptStore, Mapper, Clock). Depends on domain.
  infrastructure/    adapters: recorded, OpenAI-compatible and Anthropic models, prompt files, data and
                     configuration files, settings, JSON logging, thread mapper, report writers.
  interfaces/        the command-line program and the composition root (wiring). Nothing depends on it.
data/                300 tasks, the policy lines, the refund policy.
config/              bar.json (agreed first), prices.json (dated), router.json (derived from the build set).
prompts/             versioned prompt templates and CHANGELOG.md.
reports/             the committed results of `make run`.
tests/
  unit/              domain, application (scripted fakes), infrastructure, CLI. No network.
  e2e/               the study replayed from fixtures equals the committed configuration and reports.
  live/              opt-in tests against a real server (skipped unless RUN_LIVE=1).
  fixtures/          recorded.jsonl: real model outputs, keyed by request hash.
java/                Maven project (wrapper `mvnw` checked in): the same study on Spring AI, ArchUnit, parity test.
scripts/             make_data.py (deterministic data generator).
tech/                one note per technology used here, for a reader who has met none of them (tech/README.md is the index).
```

The dependency rule is enforced by `make lint` through import-linter (layers contract, plus a contract that forbids `domain` and `application` from importing `httpx`, `anthropic` or `openai`) and, in Java, by ArchUnit.

## Author and license

Written by Sumit Srivastava. Released under the MIT License, see [LICENSE](LICENSE). Changes are in [CHANGELOG.md](CHANGELOG.md).
