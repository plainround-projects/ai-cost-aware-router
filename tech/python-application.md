# Python code: the application layer, file by file

## What it is

The **application layer**: the steps of the experiments, written against *ports* (protocols that say what is needed) instead of against concrete tools.

## Why this repository uses it

Each experiment is a sequence of steps: build the requests, call a model, grade the answers, compute the numbers, write the report. Writing the steps against ports lets the same code run on recorded answers in a test and on a live model in `make record`.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/cost_router/application/__init__.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/application/answer_checks.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/application/experiments.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/application/ports.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/application/report_md.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/application/router.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/application/templates.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/application/tiers.py` | Quoted and explained in the walkthrough below. |


## How it works underneath

The application layer imports the domain and the ports, never an adapter. At run time the interfaces layer passes in the real adapters (the wiring). A test passes in a scripted fake instead. The files here are mostly functions that take such collaborators as arguments and return result records.

## Walkthrough of this repository's use

### Files in this note

| File | Lines | What it is |
| --- | --- | --- |
| `src/cost_router/application/__init__.py` | 1 | The application layer. |
| `src/cost_router/application/answer_checks.py` | 54 | The checks the router runs on an answer (no gold answer is visible to them). |
| `src/cost_router/application/experiments.py` | 341 | The lesson's steps as functions over the tier, check and router objects. |
| `src/cost_router/application/ports.py` | 48 | Ports: what the application needs from the outside world, written as protocols. |
| `src/cost_router/application/report_md.py` | 102 | The human-readable report: plain tables built from the stored results. |
| `src/cost_router/application/router.py` | 63 | The cost-aware router: cheapest tier first, a check after every answer, escalation on a failed check. |
| `src/cost_router/application/templates.py` | 22 | Prompt templates use `{{name}}` placeholders; rendering fails loudly on a missing value or a leftover. |
| `src/cost_router/application/tiers.py` | 73 | The three model tiers: building each task's prompt, calling the tier's model, and costing the call. |

Each file below is quoted exactly, in order, in pieces of about a dozen lines. Under each piece, a bullet list explains every statement in the order it appears. The first time an idea shows up in this note it is explained in a bullet that begins **New idea**.

#### `src/cost_router/application/__init__.py`

<!-- fmt: off -->
```python
"""The application layer."""
```
<!-- fmt: on -->

- **New idea.** A **docstring** is a text in triple quotes as the first statement of a module, class or function. Python keeps it as documentation and tools can show it.
- `"""The application layer."""`: a docstring (documentation text). It says: "The application layer."

#### `src/cost_router/application/answer_checks.py`

<!-- fmt: off -->
```python
"""The checks the router runs on an answer (no gold answer is visible to them)."""

from __future__ import annotations

from dataclasses import dataclass

from cost_router.application.tiers import ModelTiers
from cost_router.domain.checks import (
    check_label_agreement,
    check_label_shape,
    check_policy,
    check_policy_overlap,
    check_refund,
)
```
<!-- fmt: on -->

- `"""The checks the router runs on an answer (no gold answer is visible to them)."""`: a docstring (documentation text). It says: "The checks the router runs on an answer (no gold answer is visible to them)."
- **New idea.** `from __future__ import annotations` turns on a newer behaviour: type annotations are stored as text instead of being evaluated when the file loads.
- **New idea.** An **import** makes the code of another module available. `import x` gives the whole module under the name `x`; `from x import y` gives just the name `y`.
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `from cost_router.application.tiers import ModelTiers`: takes the name(s) `ModelTiers` from the module `cost_router.application.tiers` (a module of this project).
- `from cost_router.domain.checks import (`: takes the name(s) `check_label_agreement, check_label_shape, check_policy, check_policy_overlap, check_refund` from the module `cost_router.domain.checks` (a module of this project).

<!-- fmt: off -->
```python
from cost_router.domain.tasks import Kind, Task


@dataclass(frozen=True)
class CheckResult:
    """Whether the answer may be accepted, and what running the check cost."""

    passed: bool
    extra_cost: float = 0.0
    extra_tokens: int = 0


@dataclass(frozen=True)
class AnswerChecks:
```
<!-- fmt: on -->

- `from cost_router.domain.tasks import Kind, Task`: takes the name(s) `Kind, Task` from the module `cost_router.domain.tasks` (a module of this project).
- **New idea.** A **class** describes a kind of object: the data it holds and the methods that work on it. Calling the class, `Name(...)`, creates an object (an *instance*). `class B(A)` means B *inherits* from A: it has everything A has and may add or replace things.
- **New idea.** `@dataclass` is a **decorator** (a function applied to the class below it). It reads the annotated fields and writes `__init__`, `__repr__` and `__eq__` for you. `frozen=True` forbids changing a field after creation.
- `class CheckResult:`: defines the class `CheckResult`. Decorators: `dataclass(frozen=True)`. Purpose: Whether the answer may be accepted, and what running the check cost.
- `"""Whether the answer may be accepted, and what running the check cost."""`: a docstring (documentation text). It says: "Whether the answer may be accepted, and what running the check cost."
- **New idea.** An **annotated assignment** `name: type = value` also says what kind of value the name should hold. The annotation is a hint for readers and for mypy (`mypy.md`); Python does not enforce it.
- `passed: bool`: declares a field of the class `passed` of type `bool` (no value yet).
- `extra_cost: float = 0.0`: declares a field of the class `extra_cost` of type `float` and sets it to `0.0`.
- `extra_tokens: int = 0`: declares a field of the class `extra_tokens` of type `int` and sets it to `0`.
- `class AnswerChecks:`: defines the class `AnswerChecks`. Decorators: `dataclass(frozen=True)`. Purpose: Label: allowed value (`shape`) or allowed value that a second sample repeats (`agreement`).

<!-- fmt: off -->
```python
    """Label: allowed value (`shape`) or allowed value that a second sample repeats (`agreement`). Refund: recomputed
    by code. Policy: the quoted line exists
    (`quote`), or exists and is the line that best matches the question (`overlap`)."""

    tiers: ModelTiers
    label_check: str = "agreement"
    policy_check: str = "quote"

    def check(self, task: Task, tier: str, text: str) -> CheckResult:
        """Run the check for the task's kind."""
        if task.kind is Kind.REFUND:
            return CheckResult(check_refund(task, text))
        if task.kind is Kind.POLICY:
            return CheckResult(
                check_policy_overlap(task.text, text) if self.policy_check == "overlap" else check_policy(text)
            )
```
<!-- fmt: on -->

- `"""Label: allowed value ('shape') or allowed value that a second sample repeats ('agree...`: a docstring (documentation text). It says: "Label: allowed value (`shape`) or allowed value that a second sample repeats (`agreement`)."
- `tiers: ModelTiers`: declares a field of the class `tiers` of type `ModelTiers` (no value yet).
- `label_check: str = "agreement"`: declares a field of the class `label_check` of type `str` and sets it to `'agreement'`.
- `policy_check: str = "quote"`: declares a field of the class `policy_check` of type `str` and sets it to `'quote'`.
- **New idea.** A **function** is a named block of code. `def name(a, b):` defines it; the indented lines are its body. Calling `name(1, 2)` runs the body with `a = 1` and `b = 2`. `return` hands a value back. A parameter written `b=3` has a **default**: it may be left out when calling.
- **New idea.** A **method** is a function defined inside a class. Its first parameter, called `self`, is the object the method was called on, so `self.x` is that object's own attribute `x`.
- `def check(self, task: Task, tier: str, text: str) -> CheckResult:`: defines the method `check` taking task (Task); tier (str); text (str) and returns `CheckResult`. Purpose: Run the check for the task's kind.
- `"""Run the check for the task's kind."""`: a docstring (documentation text). It says: "Run the check for the task's kind."
- **New idea.** An **if** statement runs its indented block only when the condition is true. `elif` adds another condition to try; `else` runs when none held.
- `if task.kind is Kind.REFUND:`: runs the block below only if `task.kind is Kind.REFUND` is true.
- **New idea.** `return value` ends the function and hands the value to the caller. A function that reaches its end without `return` gives back `None` (nothing).
- `return CheckResult(check_refund(task, text))`: ends the function and hands back `CheckResult(check_refund(task, text))`.
- `if task.kind is Kind.POLICY:`: runs the block below only if `task.kind is Kind.POLICY` is true.
- `return CheckResult(`: ends the function and hands back `CheckResult(check_policy_overlap(task.text, text) if self.policy_check == 'ov...`. `check_policy_overlap(task.text, text) if self.policy_check == 'over...` gives `check_policy_overlap(task.text, text)` when `self.policy_check == 'overlap'` is true, otherwise `check_policy(text)`.

<!-- fmt: off -->
```python
        if self.label_check == "shape":
            return CheckResult(check_label_shape(text))
        second = self.tiers.call(tier, task, second_sample=True)
        return CheckResult(check_label_agreement(text, second.text), second.cost, second.tokens)

    def estimate_extra(self, task: Task, tier: str) -> float:
        """The money a check will add (only the label agreement check calls a model)."""
        if task.kind is Kind.LABEL and self.label_check == "agreement":
            return self.tiers.estimate(tier, task)
        return 0.0
```
<!-- fmt: on -->

- `if self.label_check == "shape":`: runs the block below only if `self.label_check == 'shape'` is true.
- `return CheckResult(check_label_shape(text))`: ends the function and hands back `CheckResult(check_label_shape(text))`.
- **New idea.** An **assignment** `name = value` makes the name point at the value. A name written in capital letters is, by convention, a constant: it is not meant to change.
- `second = self.tiers.call(tier, task, second_sample=True)`: sets `second` to the value of `self.tiers.call(tier, task, second_sample=True)`.
- `return CheckResult(check_label_agreement(text, second.text), second.cost, second.tokens)`: ends the function and hands back `CheckResult(check_label_agreement(text, second.text), second.cost, second.tok...`.
- `def estimate_extra(self, task: Task, tier: str) -> float:`: defines the method `estimate_extra` taking task (Task); tier (str) and returns `float`. Purpose: The money a check will add (only the label agreement check calls a model).
- `"""The money a check will add (only the label agreement check calls a model)."""`: a docstring (documentation text). It says: "The money a check will add (only the label agreement check calls a model)."
- `if task.kind is Kind.LABEL and self.label_check == "agreement":`: runs the block below only if `task.kind is Kind.LABEL and self.label_check == 'agreement'` is true.
- `return self.tiers.estimate(tier, task)`: ends the function and hands back `self.tiers.estimate(tier, task)`.
- `return 0.0`: ends the function and hands back `0.0`.

#### `src/cost_router/application/experiments.py`

<!-- fmt: off -->
```python
"""The lesson's steps as functions over the tier, check and router objects."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from cost_router.application.answer_checks import AnswerChecks
from cost_router.application.ports import Mapper
from cost_router.application.router import ESCALATE, CostRouter
from cost_router.application.tiers import Answered, ModelTiers
from cost_router.domain.checks import (
    check_label_agreement,
    check_label_shape,
    check_policy,
    check_refund,
    is_correct,
)
```
<!-- fmt: on -->

- `"""The lesson's steps as functions over the tier, check and router objects."""`: a docstring (documentation text). It says: "The lesson's steps as functions over the tier, check and router objects."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from collections.abc import Sequence`: takes the name(s) `Sequence` from the module `collections.abc` (abstract container types used in annotations).
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).
- `from cost_router.application.answer_checks import AnswerChecks`: takes the name(s) `AnswerChecks` from the module `cost_router.application.answer_checks` (a module of this project).
- `from cost_router.application.ports import Mapper`: takes the name(s) `Mapper` from the module `cost_router.application.ports` (a module of this project).
- `from cost_router.application.router import ESCALATE, CostRouter`: takes the name(s) `ESCALATE, CostRouter` from the module `cost_router.application.router` (a module of this project).
- `from cost_router.application.tiers import Answered, ModelTiers`: takes the name(s) `Answered, ModelTiers` from the module `cost_router.application.tiers` (a module of this project).
- `from cost_router.domain.checks import (`: takes the name(s) `check_label_agreement, check_label_shape, check_policy, check_refund, is_correct` from the module `cost_router.domain.checks` (a module of this project).

<!-- fmt: off -->
```python
from cost_router.domain.metrics import (
    CheckRates,
    Rate,
    bootstrap_accuracy_difference,
    bootstrap_cost_per_correct,
    check_rates,
    cost_per_correct,
    rate,
)
from cost_router.domain.pricing import TIERS
from cost_router.domain.routing import Bar, DayBudget, Decision, RouterConfig
from cost_router.domain.signals import hard_signal
from cost_router.domain.stats import shuffled_indices
from cost_router.domain.tasks import Kind, Task
```
<!-- fmt: on -->

- `from cost_router.domain.metrics import (`: takes the name(s) `CheckRates, Rate, bootstrap_accuracy_difference, bootstrap_cost_per_correct, check_rates, cost_per_correct, rate` from the module `cost_router.domain.metrics` (a module of this project).
- `from cost_router.domain.pricing import TIERS`: takes the name(s) `TIERS` from the module `cost_router.domain.pricing` (a module of this project).
- `from cost_router.domain.routing import Bar, DayBudget, Decision, RouterConfig`: takes the name(s) `Bar, DayBudget, Decision, RouterConfig` from the module `cost_router.domain.routing` (a module of this project).
- `from cost_router.domain.signals import hard_signal`: takes the name(s) `hard_signal` from the module `cost_router.domain.signals` (a module of this project).
- `from cost_router.domain.stats import shuffled_indices`: takes the name(s) `shuffled_indices` from the module `cost_router.domain.stats` (a module of this project).
- `from cost_router.domain.tasks import Kind, Task`: takes the name(s) `Kind, Task` from the module `cost_router.domain.tasks` (a module of this project).

<!-- fmt: off -->
```python
KINDS = tuple(k.value for k in Kind)
CHECK_NAMES = {
    "label": ("label_shape", "label_agreement"),
    "refund": ("refund_recompute",),
    "policy": ("policy_quote",),
}

Answers = dict[str, dict[str, Answered]]


@dataclass(frozen=True)
class TierKind:
    """A tier's accuracy and cost on one kind of task."""
```
<!-- fmt: on -->

- `KINDS = tuple(k.value for k in Kind)`: sets `KINDS` to the value of `tuple((k.value for k in Kind))`. `tuple((k.value for k in Kind))` is `(k.value for k in Kind)` as a tuple; `(k.value for k in Kind)` builds a generator of values: for each `k` in `Kind`.
- `CHECK_NAMES = {`: sets `CHECK_NAMES` to a dictionary with 3 entries.
- `Answers = dict[str, dict[str, Answered]]`: sets `Answers` to the value of `dict[str, dict[str, Answered]]`.
- `class TierKind:`: defines the class `TierKind`. Decorators: `dataclass(frozen=True)`. Purpose: A tier's accuracy and cost on one kind of task.
- `"""A tier's accuracy and cost on one kind of task."""`: a docstring (documentation text). It says: "A tier's accuracy and cost on one kind of task."

<!-- fmt: off -->
```python
    accuracy: Rate
    cost_per_call: float
    cost_per_correct: float | None


def collect_answers(tasks: Sequence[Task], tiers: ModelTiers, mapper: Mapper) -> Answers:
    """Every tier's first answer (temperature 0) to every task."""
    jobs = [(tier, task) for tier in TIERS for task in tasks]
    results = mapper(lambda job: tiers.call(job[0], job[1]), jobs)
    answers: Answers = {tier: {} for tier in TIERS}
    for (tier, task), answered in zip(jobs, results, strict=True):
        answers[tier][task.task_id] = answered
    return answers
```
<!-- fmt: on -->

- `accuracy: Rate`: declares a field of the class `accuracy` of type `Rate` (no value yet).
- `cost_per_call: float`: declares a field of the class `cost_per_call` of type `float` (no value yet).
- `cost_per_correct: float | None`: declares a field of the class `cost_per_correct` of type `float | None` (no value yet).
- `def collect_answers(tasks: Sequence[Task], tiers: ModelTiers, mapper: Mapper) -> Answers:`: defines the function `collect_answers` taking tasks (Sequence[Task]); tiers (ModelTiers); mapper (Mapper) and returns `Answers`. Purpose: Every tier's first answer (temperature 0) to every task.
- `"""Every tier's first answer (temperature 0) to every task."""`: a docstring (documentation text). It says: "Every tier's first answer (temperature 0) to every task."
- `jobs = [(tier, task) for tier in TIERS for task in tasks]`: sets `jobs` to the value of `[(tier, task) for tier in TIERS for task in tasks]`. `[(tier, task) for tier in TIERS for task in tasks]` builds a list: for each `tier` in `TIERS`.
- `results = mapper(lambda job: tiers.call(job[0], job[1]), jobs)`: sets `results` to the value of `mapper(lambda job: tiers.call(job[0], job[1]), jobs)`. `lambda job: tiers.call(job[0], job[1])` is a small unnamed function of `job` that gives `tiers.call(job[0], job[1])`.
- `answers: Answers = {tier: {} for tier in TIERS}`: declares a variable `answers` of type `Answers` and sets it to `{tier: {} for tier in TIERS}`. `{tier: {} for tier in TIERS}` builds a dictionary: for each `tier` in `TIERS`.
- **New idea.** A **for loop** `for x in items:` runs its block once for each item, with `x` naming the current item. `break` leaves the loop early; `continue` skips to the next item.
- `for (tier, task), answered in zip(jobs, results, strict=True):`: repeats the block below once for each `((tier, task), answered)` in `zip(jobs, results, strict=True)`. `zip(jobs, results, strict=True)` is items of `jobs`, `results` taken together, position by position.
- `answers[tier][task.task_id] = answered`: sets `answers[tier][task.task_id]` to the value of `answered`.
- `return answers`: ends the function and hands back `answers`.

<!-- fmt: off -->
```python
def measure_models(tasks: Sequence[Task], answers: Answers) -> dict[str, dict[str, TierKind]]:
    """Step 1: accuracy per task kind, cost per call and cost per correct answer for each model alone."""
    table: dict[str, dict[str, TierKind]] = {}
    for tier in TIERS:
        table[tier] = {}
        for kind in KINDS:
            subset = [t for t in tasks if t.kind.value == kind]
            correct = [is_correct(t, answers[tier][t.task_id].text) for t in subset]
            cost = sum(answers[tier][t.task_id].cost for t in subset)
            table[tier][kind] = TierKind(
                rate(sum(correct), len(correct)),
                cost / len(subset) if subset else 0.0,
                cost_per_correct(cost, sum(correct)),
            )
```
<!-- fmt: on -->

- `def measure_models(tasks: Sequence[Task], answers: Answers) -> dict[str, dict[str, Tier...`: defines the function `measure_models` taking tasks (Sequence[Task]); answers (Answers) and returns `dict[str, dict[str, TierKind]]`. Purpose: Step 1: accuracy per task kind, cost per call and cost per correct answer for each model alone.
- `"""Step 1: accuracy per task kind, cost per call and cost per correct answer for each m...`: a docstring (documentation text). It says: "Step 1: accuracy per task kind, cost per call and cost per correct answer for each model alone."
- `table: dict[str, dict[str, TierKind]] = {}`: declares a variable `table` of type `dict[str, dict[str, TierKind]]` and sets it to `{}`.
- `for tier in TIERS:`: repeats the block below once for each `tier` in `TIERS`.
- `table[tier] = {}`: sets `table[tier]` to a dictionary with 0 entries.
- `for kind in KINDS:`: repeats the block below once for each `kind` in `KINDS`.
- `subset = [t for t in tasks if t.kind.value == kind]`: sets `subset` to the value of `[t for t in tasks if t.kind.value == kind]`. `[t for t in tasks if t.kind.value == kind]` builds a list: for each `t` in `tasks`, keeping only those for which `t.kind.value == kind` is true.
- `correct = [is_correct(t, answers[tier][t.task_id].text) for t in subset]`: sets `correct` to the value of `[is_correct(t, answers[tier][t.task_id].text) for t in subset]`. `[is_correct(t, answers[tier][t.task_id].text) for t in subset]` builds a list: for each `t` in `subset`.
- `cost = sum(answers[tier][t.task_id].cost for t in subset)`: sets `cost` to the value of `sum((answers[tier][t.task_id].cost for t in subset))`. `sum((answers[tier][t.task_id].cost for t in subset))` is the sum of `(answers[tier][t.task_id].cost for t in subset)`; `(answers[tier][t.task_id].cost for t in subset)` builds a generator of values: for each `t` in `subset`.
- `table[tier][kind] = TierKind(`: sets `table[tier][kind]` to the value of `TierKind(rate(sum(correct), len(correct)), cost / len(subset) if subset else ...`. `cost / len(subset) if subset else 0.0` gives `cost / len(subset)` when `subset` is true, otherwise `0.0`; `sum(correct)` is the sum of `correct`; `len(correct)` is the number of items in `correct`.

<!-- fmt: off -->
```python
    return table


def cheapest_matching(table: dict[str, dict[str, TierKind]], margin: float) -> dict[str, str | None]:
    """For each kind, the cheapest tier whose accuracy is within `margin` of the large tier's, or None."""
    chosen: dict[str, str | None] = {}
    for kind in KINDS:
        target = table["large"][kind].accuracy.value - margin
        chosen[kind] = next((t for t in TIERS if table[t][kind].accuracy.value >= target), None)
    return chosen


def check_results(
    tasks: Sequence[Task], answers: Answers, tiers: ModelTiers, mapper: Mapper
) -> dict[str, dict[str, dict[str, CheckRates]]]:
```
<!-- fmt: on -->

- `return table`: ends the function and hands back `table`.
- `def cheapest_matching(table: dict[str, dict[str, TierKind]], margin: float) -> dict[str...`: defines the function `cheapest_matching` taking table (dict[str, dict[str, TierKind]]); margin (float) and returns `dict[str, str | None]`. Purpose: For each kind, the cheapest tier whose accuracy is within `margin` of the large tier's, or None.
- `"""For each kind, the cheapest tier whose accuracy is within 'margin' of the large tier...`: a docstring (documentation text). It says: "For each kind, the cheapest tier whose accuracy is within `margin` of the large tier's, or None."
- `chosen: dict[str, str | None] = {}`: declares a variable `chosen` of type `dict[str, str | None]` and sets it to `{}`.
- `for kind in KINDS:`: repeats the block below once for each `kind` in `KINDS`.
- `target = table["large"][kind].accuracy.value - margin`: sets `target` to the value of `table['large'][kind].accuracy.value - margin`.
- `chosen[kind] = next((t for t in TIERS if table[t][kind].accuracy.value >= target), None)`: sets `chosen[kind]` to the value of `next((t for t in TIERS if table[t][kind].accuracy.value >= target), None)`. `next((t for t in TIERS if table[t][kind].accuracy.value >= target),...` is the next item from `(t for t in TIERS if table[t][kind].accuracy.value >= tar...`; `(t for t in TIERS if table[t][kind].accuracy.value >= target)` builds a generator of values: for each `t` in `TIERS`, keeping only those for which `table[t][kind].accuracy.value >= target` is true.
- `return chosen`: ends the function and hands back `chosen`.
- `def check_results(`: defines the function `check_results` taking tasks (Sequence[Task]); answers (Answers); tiers (ModelTiers); mapper (Mapper) and returns `dict[str, dict[str, dict[str, CheckRates]]]`. Purpose: Step 2: the false-accept and false-reject rate of each check, for each tier, on the given tasks.

<!-- fmt: off -->
```python
    """Step 2: the false-accept and false-reject rate of each check, for each tier, on the given tasks."""
    out: dict[str, dict[str, dict[str, CheckRates]]] = {}
    for tier in TIERS:
        out[tier] = {}
        for kind in KINDS:
            subset = [t for t in tasks if t.kind.value == kind]
            correct = [is_correct(t, answers[tier][t.task_id].text) for t in subset]
            texts = [answers[tier][t.task_id].text for t in subset]
            out[tier][kind] = {}
            if kind == "label":

                def second_text(task: Task, tier: str = tier) -> str:
                    return tiers.call(tier, task, second_sample=True).text

                seconds = mapper(second_text, subset)
                shape = [check_label_shape(x) for x in texts]
                agree = [check_label_agreement(x, y) for x, y in zip(texts, seconds, strict=True)]
                out[tier][kind]["label_shape"] = check_rates(shape, correct)
                out[tier][kind]["label_agreement"] = check_rates(agree, correct)
            elif kind == "refund":
                passed = [check_refund(t, x) for t, x in zip(subset, texts, strict=True)]
                out[tier][kind]["refund_recompute"] = check_rates(passed, correct)
            else:
                passed = [check_policy(x) for x in texts]
                out[tier][kind]["policy_quote"] = check_rates(passed, correct)
```
<!-- fmt: on -->

- `"""Step 2: the false-accept and false-reject rate of each check, for each tier, on the ...`: a docstring (documentation text). It says: "Step 2: the false-accept and false-reject rate of each check, for each tier, on the given tasks."
- `out: dict[str, dict[str, dict[str, CheckRates]]] = {}`: declares a variable `out` of type `dict[str, dict[str, dict[str, CheckRates]]]` and sets it to `{}`.
- `for tier in TIERS:`: repeats the block below once for each `tier` in `TIERS`.
- `out[tier] = {}`: sets `out[tier]` to a dictionary with 0 entries.
- `for kind in KINDS:`: repeats the block below once for each `kind` in `KINDS`.
- `subset = [t for t in tasks if t.kind.value == kind]`: sets `subset` to the value of `[t for t in tasks if t.kind.value == kind]`. `[t for t in tasks if t.kind.value == kind]` builds a list: for each `t` in `tasks`, keeping only those for which `t.kind.value == kind` is true.
- `correct = [is_correct(t, answers[tier][t.task_id].text) for t in subset]`: sets `correct` to the value of `[is_correct(t, answers[tier][t.task_id].text) for t in subset]`. `[is_correct(t, answers[tier][t.task_id].text) for t in subset]` builds a list: for each `t` in `subset`.
- `texts = [answers[tier][t.task_id].text for t in subset]`: sets `texts` to the value of `[answers[tier][t.task_id].text for t in subset]`. `[answers[tier][t.task_id].text for t in subset]` builds a list: for each `t` in `subset`.
- `out[tier][kind] = {}`: sets `out[tier][kind]` to a dictionary with 0 entries.
- `if kind == "label":`: runs the block below only if `kind == 'label'` is true.
- **New idea.** A function defined inside another function is a **closure**: it can read the variables of the function around it, even after that function has returned.
- `def second_text(task: Task, tier: str = tier) -> str:`: defines the function `second_text` taking task (Task); tier (str), default tier and returns `str`.
- `return tiers.call(tier, task, second_sample=True).text`: ends the function and hands back `tiers.call(tier, task, second_sample=True).text`.
- `seconds = mapper(second_text, subset)`: sets `seconds` to the value of `mapper(second_text, subset)`.
- `shape = [check_label_shape(x) for x in texts]`: sets `shape` to the value of `[check_label_shape(x) for x in texts]`. `[check_label_shape(x) for x in texts]` builds a list: for each `x` in `texts`.
- `agree = [check_label_agreement(x, y) for x, y in zip(texts, seconds, strict=True)]`: sets `agree` to the value of `[check_label_agreement(x, y) for x, y in zip(texts, seconds, strict=True)]`. `[check_label_agreement(x, y) for x, y in zip(texts, seconds, strict...` builds a list: for each `(x, y)` in `zip(texts, seconds, strict=True)`; `zip(texts, seconds, strict=True)` is items of `texts`, `seconds` taken together, position by position.
- `out[tier][kind]["label_shape"] = check_rates(shape, correct)`: sets `out[tier][kind]['label_shape']` to the value of `check_rates(shape, correct)`.
- `out[tier][kind]["label_agreement"] = check_rates(agree, correct)`: sets `out[tier][kind]['label_agreement']` to the value of `check_rates(agree, correct)`.
- `elif kind == "refund":`: runs the block below only if `kind == 'refund'` is true.
- `passed = [check_refund(t, x) for t, x in zip(subset, texts, strict=True)]`: sets `passed` to the value of `[check_refund(t, x) for t, x in zip(subset, texts, strict=True)]`. `[check_refund(t, x) for t, x in zip(subset, texts, strict=True)]` builds a list: for each `(t, x)` in `zip(subset, texts, strict=True)`; `zip(subset, texts, strict=True)` is items of `subset`, `texts` taken together, position by position.
- `out[tier][kind]["refund_recompute"] = check_rates(passed, correct)`: sets `out[tier][kind]['refund_recompute']` to the value of `check_rates(passed, correct)`.
- `else:` the block below runs when none of the conditions above held.
- `passed = [check_policy(x) for x in texts]`: sets `passed` to the value of `[check_policy(x) for x in texts]`. `[check_policy(x) for x in texts]` builds a list: for each `x` in `texts`.
- `out[tier][kind]["policy_quote"] = check_rates(passed, correct)`: sets `out[tier][kind]['policy_quote']` to the value of `check_rates(passed, correct)`.

<!-- fmt: off -->
```python
    return out


def tune(
    build_tasks: Sequence[Task],
    answers: Answers,
    rates: dict[str, dict[str, dict[str, CheckRates]]],
    bar: Bar,
    request_cap: float | None = None,
) -> RouterConfig:
    """Step 3, from the build set only: where each kind starts, and which hard tasks skip the small tier."""
    start: dict[str, str] = {}
    hard_start: dict[str, str] = {}
    for kind in KINDS:
```
<!-- fmt: on -->

- `return out`: ends the function and hands back `out`.
- `def tune(`: defines the function `tune` taking build_tasks (Sequence[Task]); answers (Answers); rates (dict[str, dict[str, dict[st...); bar (Bar); request_cap (float | None), default None and returns `RouterConfig`. Purpose: Step 3, from the build set only: where each kind starts, and which hard tasks skip the small tier.
- `"""Step 3, from the build set only: where each kind starts, and which hard tasks skip t...`: a docstring (documentation text). It says: "Step 3, from the build set only: where each kind starts, and which hard tasks skip the small tier."
- `start: dict[str, str] = {}`: declares a variable `start` of type `dict[str, str]` and sets it to `{}`.
- `hard_start: dict[str, str] = {}`: declares a variable `hard_start` of type `dict[str, str]` and sets it to `{}`.
- `for kind in KINDS:`: repeats the block below once for each `kind` in `KINDS`.

<!-- fmt: off -->
```python
        check_name = CHECK_NAMES[kind][-1]
        start[kind] = next(
            (t for t in TIERS if rates[t][kind][check_name].false_accept_rate <= bar.false_accept_bar), TIERS[-1]
        )
        index = TIERS.index(start[kind])
        signalled = [t for t in build_tasks if t.kind.value == kind and hard_signal(t)]
        if index < len(TIERS) - 1 and len(signalled) >= 5:
            accuracy = sum(is_correct(t, answers[start[kind]][t.task_id].text) for t in signalled) / len(signalled)
            if accuracy < bar.hard_accuracy_bar:
                hard_start[kind] = TIERS[index + 1]
    return RouterConfig(start, hard_start, "agreement", request_cap or bar.request_cap, bar.tighten_at)


@dataclass(frozen=True)
class Outcome:
```
<!-- fmt: on -->

- `check_name = CHECK_NAMES[kind][-1]`: sets `check_name` to the value of `CHECK_NAMES[kind][-1]`.
- `start[kind] = next(`: sets `start[kind]` to the value of `next((t for t in TIERS if rates[t][kind][check_name].false_accept_rate <= bar...`. `next((t for t in TIERS if rates[t][kind][check_name].false_accept_r...` is the next item from `(t for t in TIERS if rates[t][kind][check_name].false_acc...`; `(t for t in TIERS if rates[t][kind][check_name].false_accept_rate <...` builds a generator of values: for each `t` in `TIERS`, keeping only those for which `rates[t][kind][check_name].false_accept_rate <=...` is true.
- `index = TIERS.index(start[kind])`: sets `index` to the value of `TIERS.index(start[kind])`. `TIERS.index(start[kind])` is the position of `start[kind]` in `TIERS`.
- `signalled = [t for t in build_tasks if t.kind.value == kind and hard_signal(t)]`: sets `signalled` to the value of `[t for t in build_tasks if t.kind.value == kind and hard_signal(t)]`. `[t for t in build_tasks if t.kind.value == kind and hard_signal(t)]` builds a list: for each `t` in `build_tasks`, keeping only those for which `t.kind.value == kind and hard_signal(t)` is true.
- `if index < len(TIERS) - 1 and len(signalled) >= 5:`: runs the block below only if `index < len(TIERS) - 1 and len(signalled) >= 5` is true. `len(signalled)` is the number of items in `signalled`; `len(TIERS)` is the number of items in `TIERS`.
- `accuracy = sum(is_correct(t, answers[start[kind]][t.task_id].text) for t in signalled) ...`: sets `accuracy` to the value of `sum((is_correct(t, answers[start[kind]][t.task_id].text) for t in signalled))...`. `sum((is_correct(t, answers[start[kind]][t.task_id].text) for t in s...` is the sum of `(is_correct(t, answers[start[kind]][t.task_id].text) for ...`; `len(signalled)` is the number of items in `signalled`; `(is_correct(t, answers[start[kind]][t.task_id].text) for t in signa...` builds a generator of values: for each `t` in `signalled`.
- `if accuracy < bar.hard_accuracy_bar:`: runs the block below only if `accuracy < bar.hard_accuracy_bar` is true.
- `hard_start[kind] = TIERS[index + 1]`: sets `hard_start[kind]` to the value of `TIERS[index + 1]`.
- `return RouterConfig(start, hard_start, "agreement", request_cap or bar.request_cap, bar...`: ends the function and hands back `RouterConfig(start, hard_start, 'agreement', request_cap or bar.request_cap, ...`.
- `class Outcome:`: defines the class `Outcome`. Decorators: `dataclass(frozen=True)`. Purpose: A routing decision with the ground truth next to it.

<!-- fmt: off -->
```python
    """A routing decision with the ground truth next to it."""

    decision: Decision
    kind: str
    difficulty: str
    correct: bool

    @property
    def escalated(self) -> bool:
        """True when no tier's answer was accepted."""
        return self.decision.served_by == ESCALATE


def route_all(tasks: Sequence[Task], router: CostRouter, day: DayBudget | None = None) -> list[Outcome]:
```
<!-- fmt: on -->

- `"""A routing decision with the ground truth next to it."""`: a docstring (documentation text). It says: "A routing decision with the ground truth next to it."
- `decision: Decision`: declares a field of the class `decision` of type `Decision` (no value yet).
- `kind: str`: declares a field of the class `kind` of type `str` (no value yet).
- `difficulty: str`: declares a field of the class `difficulty` of type `str` (no value yet).
- `correct: bool`: declares a field of the class `correct` of type `bool` (no value yet).
- **New idea.** A **decorator** is a line `@name` above a function or class. It passes the function to `name` and uses what comes back instead. It is a way to add behaviour without editing the function.
- **New idea.** `@property` lets a method be read like an attribute, without brackets.
- `def escalated(self) -> bool:`: defines the method `escalated` taking no arguments and returns `bool`. Decorators: `property`. Purpose: True when no tier's answer was accepted.
- `"""True when no tier's answer was accepted."""`: a docstring (documentation text). It says: "True when no tier's answer was accepted."
- `return self.decision.served_by == ESCALATE`: ends the function and hands back `self.decision.served_by == ESCALATE`.
- `def route_all(tasks: Sequence[Task], router: CostRouter, day: DayBudget | None = None) ...`: defines the function `route_all` taking tasks (Sequence[Task]); router (CostRouter); day (DayBudget | None), default None and returns `list[Outcome]`. Purpose: Serve tasks in order (the day's budget makes the order matter, so this is sequential).

<!-- fmt: off -->
```python
    """Serve tasks in order (the day's budget makes the order matter, so this is sequential)."""
    outcomes = []
    for task in tasks:
        decision = router.route(task, day)
        correct = decision.answer is not None and is_correct(task, decision.answer)
        outcomes.append(Outcome(decision, task.kind.value, task.difficulty, correct))
    return outcomes


@dataclass(frozen=True)
class Summary:
    """Accuracy, money and tier shares of a set of outcomes."""

    n: int
```
<!-- fmt: on -->

- `"""Serve tasks in order (the day's budget makes the order matter, so this is sequential...`: a docstring (documentation text). It says: "Serve tasks in order (the day's budget makes the order matter, so this is sequential)."
- `outcomes = []`: sets `outcomes` to a list of 0 items.
- `for task in tasks:`: repeats the block below once for each `task` in `tasks`.
- `decision = router.route(task, day)`: sets `decision` to the value of `router.route(task, day)`.
- `correct = decision.answer is not None and is_correct(task, decision.answer)`: sets `correct` to the value of `decision.answer is not None and is_correct(task, decision.answer)`. `decision.answer is not None` tests that there is something in `decision.answer`.
- `outcomes.append(Outcome(decision, task.kind.value, task.difficulty, correct))`: runs `outcomes.append(Outcome(decision, task.kind.value, task.difficulty, correct))` for its effect and ignores the result. `outcomes.append(Outcome(decision, task.kind.value, task.difficulty,...` adds `Outcome(decision, task.kind.value, task.difficulty, correct)` to the end of `outcomes`.
- `return outcomes`: ends the function and hands back `outcomes`.
- `class Summary:`: defines the class `Summary`. Decorators: `dataclass(frozen=True)`. Purpose: Accuracy, money and tier shares of a set of outcomes.
- `"""Accuracy, money and tier shares of a set of outcomes."""`: a docstring (documentation text). It says: "Accuracy, money and tier shares of a set of outcomes."
- `n: int`: declares a field of the class `n` of type `int` (no value yet).

<!-- fmt: off -->
```python
    accuracy: Rate
    total_cost: float
    cost_per_correct: float | None
    cost_per_correct_interval: tuple[float, float]
    served_by: dict[str, int]
    escalated: int
    max_request_spend: float


def summarize(outcomes: Sequence[Outcome]) -> Summary:
    """Aggregate outcomes (a router's) with bootstrap intervals."""
    correct = [o.correct for o in outcomes]
    costs = [o.decision.spent for o in outcomes]
    shares: dict[str, int] = {}
```
<!-- fmt: on -->

- `accuracy: Rate`: declares a field of the class `accuracy` of type `Rate` (no value yet).
- `total_cost: float`: declares a field of the class `total_cost` of type `float` (no value yet).
- `cost_per_correct: float | None`: declares a field of the class `cost_per_correct` of type `float | None` (no value yet).
- `cost_per_correct_interval: tuple[float, float]`: declares a field of the class `cost_per_correct_interval` of type `tuple[float, float]` (no value yet).
- `served_by: dict[str, int]`: declares a field of the class `served_by` of type `dict[str, int]` (no value yet).
- `escalated: int`: declares a field of the class `escalated` of type `int` (no value yet).
- `max_request_spend: float`: declares a field of the class `max_request_spend` of type `float` (no value yet).
- `def summarize(outcomes: Sequence[Outcome]) -> Summary:`: defines the function `summarize` taking outcomes (Sequence[Outcome]) and returns `Summary`. Purpose: Aggregate outcomes (a router's) with bootstrap intervals.
- `"""Aggregate outcomes (a router's) with bootstrap intervals."""`: a docstring (documentation text). It says: "Aggregate outcomes (a router's) with bootstrap intervals."
- `correct = [o.correct for o in outcomes]`: sets `correct` to the value of `[o.correct for o in outcomes]`. `[o.correct for o in outcomes]` builds a list: for each `o` in `outcomes`.
- `costs = [o.decision.spent for o in outcomes]`: sets `costs` to the value of `[o.decision.spent for o in outcomes]`. `[o.decision.spent for o in outcomes]` builds a list: for each `o` in `outcomes`.
- `shares: dict[str, int] = {}`: declares a variable `shares` of type `dict[str, int]` and sets it to `{}`.

<!-- fmt: off -->
```python
    for o in outcomes:
        shares[o.decision.served_by] = shares.get(o.decision.served_by, 0) + 1
    return Summary(
        len(outcomes),
        rate(sum(correct), len(correct)),
        sum(costs),
        cost_per_correct(sum(costs), sum(correct)),
        bootstrap_cost_per_correct(costs, correct),
        dict(sorted(shares.items())),
        sum(1 for o in outcomes if o.escalated),
        max(costs, default=0.0),
    )
```
<!-- fmt: on -->

- `for o in outcomes:`: repeats the block below once for each `o` in `outcomes`.
- `shares[o.decision.served_by] = shares.get(o.decision.served_by, 0) + 1`: sets `shares[o.decision.served_by]` to the value of `shares.get(o.decision.served_by, 0) + 1`. `shares.get(o.decision.served_by, 0)` looks up `o.decision.served_by` in `shares` (default `0` when missing).
- `return Summary(`: ends the function and hands back `Summary(len(outcomes), rate(sum(correct), len(correct)), sum(costs), cost_per...`. `len(outcomes)` is the number of items in `outcomes`; `sum(costs)` is the sum of `costs`; `dict(sorted(shares.items()))` is a dictionary made from `sorted(shares.items())`.

<!-- fmt: off -->
```python
def single_model_summary(tasks: Sequence[Task], answers: Answers, tier: str) -> Summary:
    """The same summary for one model answering every task alone."""
    correct = [is_correct(t, answers[tier][t.task_id].text) for t in tasks]
    costs = [answers[tier][t.task_id].cost for t in tasks]
    return Summary(
        len(tasks),
        rate(sum(correct), len(correct)),
        sum(costs),
        cost_per_correct(sum(costs), sum(correct)),
        bootstrap_cost_per_correct(costs, correct),
        {tier: len(tasks)},
        0,
        max(costs, default=0.0),
    )
```
<!-- fmt: on -->

- `def single_model_summary(tasks: Sequence[Task], answers: Answers, tier: str) -> Summary:`: defines the function `single_model_summary` taking tasks (Sequence[Task]); answers (Answers); tier (str) and returns `Summary`. Purpose: The same summary for one model answering every task alone.
- `"""The same summary for one model answering every task alone."""`: a docstring (documentation text). It says: "The same summary for one model answering every task alone."
- `correct = [is_correct(t, answers[tier][t.task_id].text) for t in tasks]`: sets `correct` to the value of `[is_correct(t, answers[tier][t.task_id].text) for t in tasks]`. `[is_correct(t, answers[tier][t.task_id].text) for t in tasks]` builds a list: for each `t` in `tasks`.
- `costs = [answers[tier][t.task_id].cost for t in tasks]`: sets `costs` to the value of `[answers[tier][t.task_id].cost for t in tasks]`. `[answers[tier][t.task_id].cost for t in tasks]` builds a list: for each `t` in `tasks`.
- `return Summary(`: ends the function and hands back `Summary(len(tasks), rate(sum(correct), len(correct)), sum(costs), cost_per_co...`. `len(tasks)` is the number of items in `tasks`; `sum(costs)` is the sum of `costs`; `max(costs, default=0.0)` is the largest of `costs`.

<!-- fmt: off -->
```python
def compare_to_large(tasks: Sequence[Task], answers: Answers, outcomes: Sequence[Outcome], bar: Bar) -> dict[str, Any]:
    """Step 5's verdict: matched the large model's accuracy within the margin at a lower cost per correct?"""
    router = summarize(outcomes)
    large = single_model_summary(tasks, answers, "large")
    router_correct = [o.correct for o in outcomes]
    large_correct = [is_correct(t, answers["large"][t.task_id].text) for t in tasks]
    diff, low, high = bootstrap_accuracy_difference(router_correct, large_correct)
    matched = router.accuracy.value >= large.accuracy.value - bar.accuracy_margin
    cheaper = (
        router.cost_per_correct is not None
        and large.cost_per_correct is not None
        and router.cost_per_correct < large.cost_per_correct
    )
    return {
        "accuracy_difference_vs_large": diff,
        "accuracy_difference_interval": [low, high],
        "margin": bar.accuracy_margin,
        "matched_within_margin": matched,
        "cheaper_per_correct": cheaper,
        "verdict": "matched" if matched and cheaper else ("cheaper but less accurate" if cheaper else "not cheaper"),
    }
```
<!-- fmt: on -->

- `def compare_to_large(tasks: Sequence[Task], answers: Answers, outcomes: Sequence[Outcom...`: defines the function `compare_to_large` taking tasks (Sequence[Task]); answers (Answers); outcomes (Sequence[Outcome]); bar (Bar) and returns `dict[str, Any]`. Purpose: Step 5's verdict: matched the large model's accuracy within the margin at a lower cost per correct?
- `"""Step 5's verdict: matched the large model's accuracy within the margin at a lower co...`: a docstring (documentation text). It says: "Step 5's verdict: matched the large model's accuracy within the margin at a lower cost per correct?"
- `router = summarize(outcomes)`: sets `router` to the value of `summarize(outcomes)`.
- `large = single_model_summary(tasks, answers, "large")`: sets `large` to the value of `single_model_summary(tasks, answers, 'large')`.
- `router_correct = [o.correct for o in outcomes]`: sets `router_correct` to the value of `[o.correct for o in outcomes]`. `[o.correct for o in outcomes]` builds a list: for each `o` in `outcomes`.
- `large_correct = [is_correct(t, answers["large"][t.task_id].text) for t in tasks]`: sets `large_correct` to the value of `[is_correct(t, answers['large'][t.task_id].text) for t in tasks]`. `[is_correct(t, answers['large'][t.task_id].text) for t in tasks]` builds a list: for each `t` in `tasks`.
- `diff, low, high = bootstrap_accuracy_difference(router_correct, large_correct)`: sets `(diff, low, high)` to the value of `bootstrap_accuracy_difference(router_correct, large_correct)`.
- `matched = router.accuracy.value >= large.accuracy.value - bar.accuracy_margin`: sets `matched` to the value of `router.accuracy.value >= large.accuracy.value - bar.accuracy_margin`.
- `cheaper = (`: sets `cheaper` to the value of `router.cost_per_correct is not None and large.cost_per_correct is not None an...`. `router.cost_per_correct is not None` tests that there is something in `router.cost_per_correct`; `large.cost_per_correct is not None` tests that there is something in `large.cost_per_correct`.
- `return {`: ends the function and hands back `{'accuracy_difference_vs_large': diff, 'accuracy_difference_interval': [low, ...`. `'matched' if matched and cheaper else 'cheaper but less accurate' i...` gives `'matched'` when `matched and cheaper` is true, otherwise `'cheaper but less accurate' if cheape...`; `'cheaper but less accurate' if cheaper else 'not cheaper'` gives `'cheaper but less accurate'` when `cheaper` is true, otherwise `'not cheaper'`.

<!-- fmt: off -->
```python
@dataclass(frozen=True)
class DayResult:
    """One replay of the test tasks as a single day under a budget."""

    fraction: float
    budget: float
    spent: float
    under_budget: bool
    requests_over_cap: int
    crossed_at: int | None
    accuracy_before: Rate
    accuracy_after: Rate
    large_served_after: int
    outcomes: list[Outcome]
```
<!-- fmt: on -->

- `class DayResult:`: defines the class `DayResult`. Decorators: `dataclass(frozen=True)`. Purpose: One replay of the test tasks as a single day under a budget.
- `"""One replay of the test tasks as a single day under a budget."""`: a docstring (documentation text). It says: "One replay of the test tasks as a single day under a budget."
- `fraction: float`: declares a field of the class `fraction` of type `float` (no value yet).
- `budget: float`: declares a field of the class `budget` of type `float` (no value yet).
- `spent: float`: declares a field of the class `spent` of type `float` (no value yet).
- `under_budget: bool`: declares a field of the class `under_budget` of type `bool` (no value yet).
- `requests_over_cap: int`: declares a field of the class `requests_over_cap` of type `int` (no value yet).
- `crossed_at: int | None`: declares a field of the class `crossed_at` of type `int | None` (no value yet).
- `accuracy_before: Rate`: declares a field of the class `accuracy_before` of type `Rate` (no value yet).
- `accuracy_after: Rate`: declares a field of the class `accuracy_after` of type `Rate` (no value yet).
- `large_served_after: int`: declares a field of the class `large_served_after` of type `int` (no value yet).
- `outcomes: list[Outcome]`: declares a field of the class `outcomes` of type `list[Outcome]` (no value yet).

<!-- fmt: off -->
```python
def run_day(tasks: Sequence[Task], answers: Answers, router_factory: Any, fraction: float, seed: int = 11) -> DayResult:
    """Step 4: the tasks, in a fixed shuffled order, under a budget of `fraction` of the always-large cost."""
    order = [tasks[i] for i in shuffled_indices(len(tasks), seed)]
    large_cost = sum(answers["large"][t.task_id].cost for t in tasks)
    day = DayBudget(large_cost * fraction)
    router: CostRouter = router_factory()
    outcomes = route_all(order, router, day)
    crossed = next((i for i, o in enumerate(outcomes) if o.decision.share_before >= router.config.tighten_at), None)
    before = outcomes[:crossed] if crossed is not None else outcomes
    after = outcomes[crossed:] if crossed is not None else []
    cap = router.config.request_cap
    return DayResult(
        fraction,
        day.budget,
        day.used,
        day.used <= day.budget,
        sum(1 for o in outcomes if o.decision.spent > cap),
        crossed,
        rate(sum(o.correct for o in before), len(before)),
        rate(sum(o.correct for o in after), len(after)),
        sum(1 for o in after if o.decision.served_by == "large"),
        outcomes,
    )
```
<!-- fmt: on -->

- `def run_day(tasks: Sequence[Task], answers: Answers, router_factory: Any, fraction: flo...`: defines the function `run_day` taking tasks (Sequence[Task]); answers (Answers); router_factory (Any); fraction (float); seed (int), default 11 and returns `DayResult`. Purpose: Step 4: the tasks, in a fixed shuffled order, under a budget of `fraction` of the always-large cost.
- `"""Step 4: the tasks, in a fixed shuffled order, under a budget of 'fraction' of the al...`: a docstring (documentation text). It says: "Step 4: the tasks, in a fixed shuffled order, under a budget of `fraction` of the always-large cost."
- `order = [tasks[i] for i in shuffled_indices(len(tasks), seed)]`: sets `order` to the value of `[tasks[i] for i in shuffled_indices(len(tasks), seed)]`. `[tasks[i] for i in shuffled_indices(len(tasks), seed)]` builds a list: for each `i` in `shuffled_indices(len(tasks), seed)`; `len(tasks)` is the number of items in `tasks`.
- `large_cost = sum(answers["large"][t.task_id].cost for t in tasks)`: sets `large_cost` to the value of `sum((answers['large'][t.task_id].cost for t in tasks))`. `sum((answers['large'][t.task_id].cost for t in tasks))` is the sum of `(answers['large'][t.task_id].cost for t in tasks)`; `(answers['large'][t.task_id].cost for t in tasks)` builds a generator of values: for each `t` in `tasks`.
- `day = DayBudget(large_cost * fraction)`: sets `day` to the value of `DayBudget(large_cost * fraction)`.
- `router: CostRouter = router_factory()`: declares a variable `router` of type `CostRouter` and sets it to `router_factory()`.
- `outcomes = route_all(order, router, day)`: sets `outcomes` to the value of `route_all(order, router, day)`.
- `crossed = next((i for i, o in enumerate(outcomes) if o.decision.share_before >= router....`: sets `crossed` to the value of `next((i for i, o in enumerate(outcomes) if o.decision.share_before >= router....`. `next((i for i, o in enumerate(outcomes) if o.decision.share_before ...` is the next item from `(i for i, o in enumerate(outcomes) if o.decision.share_be...`; `(i for i, o in enumerate(outcomes) if o.decision.share_before >= ro...` builds a generator of values: for each `(i, o)` in `enumerate(outcomes)`, keeping only those for which `o.decision.share_before >= router.config.tighte...` is true; `enumerate(outcomes)` is pairs (position, item) for the items of `outcomes`.
- `before = outcomes[:crossed] if crossed is not None else outcomes`: sets `before` to the value of `outcomes[:crossed] if crossed is not None else outcomes`. `outcomes[:crossed] if crossed is not None else outcomes` gives `outcomes[:crossed]` when `crossed is not None` is true, otherwise `outcomes`; `crossed is not None` tests that there is something in `crossed`; `outcomes[:crossed]` is a slice (a part) of `outcomes`.
- `after = outcomes[crossed:] if crossed is not None else []`: sets `after` to the value of `outcomes[crossed:] if crossed is not None else []`. `outcomes[crossed:] if crossed is not None else []` gives `outcomes[crossed:]` when `crossed is not None` is true, otherwise `[]`; `crossed is not None` tests that there is something in `crossed`; `outcomes[crossed:]` is a slice (a part) of `outcomes`.
- `cap = router.config.request_cap`: sets `cap` to the value of `router.config.request_cap`.
- `return DayResult(`: ends the function and hands back `DayResult(fraction, day.budget, day.used, day.used <= day.budget, sum((1 for ...`. `sum((1 for o in outcomes if o.decision.spent > cap))` is the sum of `(1 for o in outcomes if o.decision.spent > cap)`; `sum((1 for o in after if o.decision.served_by == 'large'))` is the sum of `(1 for o in after if o.decision.served_by == 'large')`; `(1 for o in outcomes if o.decision.spent > cap)` builds a generator of values: for each `o` in `outcomes`, keeping only those for which `o.decision.spent > cap` is true.

<!-- fmt: off -->
```python
def check_name(kind: str, config: RouterConfig) -> str:
    """The name of the check a configuration runs for a kind of task."""
    if kind == "label":
        return f"label_{config.label_check}"
    return "refund_recompute" if kind == "refund" else f"policy_{config.policy_check}"


def false_accepts(outcomes: Sequence[Outcome], config: RouterConfig) -> dict[str, Any]:
    """Step 6: answers the router accepted that were wrong, grouped by the tier that served them and the check."""
    grouped: dict[str, list[str]] = {}
    served_wrong = 0
    for o in outcomes:
        if o.decision.answer is None or o.correct:
            continue
```
<!-- fmt: on -->

- `def check_name(kind: str, config: RouterConfig) -> str:`: defines the function `check_name` taking kind (str); config (RouterConfig) and returns `str`. Purpose: The name of the check a configuration runs for a kind of task.
- `"""The name of the check a configuration runs for a kind of task."""`: a docstring (documentation text). It says: "The name of the check a configuration runs for a kind of task."
- `if kind == "label":`: runs the block below only if `kind == 'label'` is true.
- `return f"label_{config.label_check}"`: ends the function and hands back `f'label_{config.label_check}'`. the f-string inserts `config.label_check` into the text.
- `return "refund_recompute" if kind == "refund" else f"policy_{config.policy_check}"`: ends the function and hands back `'refund_recompute' if kind == 'refund' else f'policy_{config.policy_check}'`. `'refund_recompute' if kind == 'refund' else f'policy_{config.policy...` gives `'refund_recompute'` when `kind == 'refund'` is true, otherwise `f'policy_{config.policy_check}'`; the f-string inserts `config.policy_check` into the text.
- `def false_accepts(outcomes: Sequence[Outcome], config: RouterConfig) -> dict[str, Any]:`: defines the function `false_accepts` taking outcomes (Sequence[Outcome]); config (RouterConfig) and returns `dict[str, Any]`. Purpose: Step 6: answers the router accepted that were wrong, grouped by the tier that served them and the check.
- `"""Step 6: answers the router accepted that were wrong, grouped by the tier that served...`: a docstring (documentation text). It says: "Step 6: answers the router accepted that were wrong, grouped by the tier that served them and the check."
- `grouped: dict[str, list[str]] = {}`: declares a variable `grouped` of type `dict[str, list[str]]` and sets it to `{}`.
- `served_wrong = 0`: sets `served_wrong` to the constant `0`.
- `for o in outcomes:`: repeats the block below once for each `o` in `outcomes`.
- `if o.decision.answer is None or o.correct:`: runs the block below only if `o.decision.answer is None or o.correct` is true. `o.decision.answer is None` tests that there is nothing (`None`) in `o.decision.answer`.
- `continue`: skips the rest of this round and goes to the next item.

<!-- fmt: off -->
```python
        served_wrong += 1
        grouped.setdefault(f"{o.decision.served_by}/{check_name(o.kind, config)}", []).append(o.decision.task_id)
    by_tier: dict[str, int] = {}
    for key, ids in grouped.items():
        tier = key.split("/")[0]
        by_tier[tier] = by_tier.get(tier, 0) + len(ids)
    return {
        "false_accepts": served_wrong,
        "by_tier_and_check": {k: {"count": len(v), "tasks": v} for k, v in sorted(grouped.items())},
        "by_tier": dict(sorted(by_tier.items())),
    }


def harden(config: RouterConfig, kind: str) -> tuple[RouterConfig, str]:
```
<!-- fmt: on -->

- **New idea.** An **augmented assignment** such as `x += 1` changes the value in place: it means `x = x + 1`.
- `served_wrong += 1`: adds `1` to `served_wrong` and stores the result back.
- `grouped.setdefault(f"{o.decision.served_by}/{check_name(o.kind, config)}", []).append(o...`: runs `grouped.setdefault(f'{o.decision.served_by}/{check_name(o.kind, config)}', []).append(o...` for its effect and ignores the result. `grouped.setdefault(f'{o.decision.served_by}/{check_name(o.kind, con...` adds `o.decision.task_id` to the end of `grouped.setdefault(f'{o.decision.serv...`; `grouped.setdefault(f'{o.decision.served_by}/{check_name(o.kind, con...` is the entry `f'{o.decision.served_by}/{check_name(o.kind, config)}'` of `grouped`, created with `[]` if missing; the f-string inserts `o.decision.served_by`, `check_name(o.kind, config)` into the text.
- `by_tier: dict[str, int] = {}`: declares a variable `by_tier` of type `dict[str, int]` and sets it to `{}`.
- `for key, ids in grouped.items():`: repeats the block below once for each `(key, ids)` in `grouped.items()`. `grouped.items()` is the (key, value) pairs of `grouped`.
- `tier = key.split("/")[0]`: sets `tier` to the value of `key.split('/')[0]`. `key.split('/')` is `key` cut into pieces at `'/'`.
- `by_tier[tier] = by_tier.get(tier, 0) + len(ids)`: sets `by_tier[tier]` to the value of `by_tier.get(tier, 0) + len(ids)`. `by_tier.get(tier, 0)` looks up `tier` in `by_tier` (default `0` when missing); `len(ids)` is the number of items in `ids`.
- `return {`: ends the function and hands back `{'false_accepts': served_wrong, 'by_tier_and_check': {k: {'count': len(v), 't...`. `{k: {'count': len(v), 'tasks': v} for k, v in sorted(grouped.items())}` builds a dictionary: for each `(k, v)` in `sorted(grouped.items())`; `dict(sorted(by_tier.items()))` is a dictionary made from `sorted(by_tier.items())`; `sorted(by_tier.items())` is `by_tier.items()` in sorted order.
- `def harden(config: RouterConfig, kind: str) -> tuple[RouterConfig, str]:`: defines the function `harden` taking config (RouterConfig); kind (str) and returns `tuple[RouterConfig, str]`. Purpose: The one change step 6 makes to the weakest check's kind: start one tier higher, or, when it already starts at the top tier, run a stronger check (for policy: the quoted line must also be the line that best matches the...

<!-- fmt: off -->
```python
    """The one change step 6 makes to the weakest check's kind: start one tier higher, or, when it already starts at
    the top tier, run a stronger check (for policy: the quoted line must also be the line that best matches the
    question). Returns the new configuration and a sentence describing the change."""
    index = TIERS.index(config.start[kind])
    if index < len(TIERS) - 1:
        start = {**config.start, kind: TIERS[index + 1]}
        hard = {k: v for k, v in config.hard_start.items() if k != kind or TIERS.index(v) > index + 1}
        changed = RouterConfig(
            start, hard, config.label_check, config.request_cap, config.tighten_at, config.policy_check
        )
        return changed, f"{kind} tasks start at {TIERS[index + 1]} instead of {TIERS[index]}"
    if kind == "policy":
        changed = RouterConfig(
            config.start, config.hard_start, config.label_check, config.request_cap, config.tighten_at, "overlap"
        )
```
<!-- fmt: on -->

- `"""The one change step 6 makes to the weakest check's kind: start one tier higher, or, ...`: a docstring (documentation text). It says: "The one change step 6 makes to the weakest check's kind: start one tier higher, or, when it already starts at the top tier, run a stronger check (for policy: the quoted line must also be the line that best matches the..."
- `index = TIERS.index(config.start[kind])`: sets `index` to the value of `TIERS.index(config.start[kind])`. `TIERS.index(config.start[kind])` is the position of `config.start[kind]` in `TIERS`.
- `if index < len(TIERS) - 1:`: runs the block below only if `index < len(TIERS) - 1` is true. `len(TIERS)` is the number of items in `TIERS`.
- `start = {**config.start, kind: TIERS[index + 1]}`: sets `start` to a dictionary with 2 entries.
- `hard = {k: v for k, v in config.hard_start.items() if k != kind or TIERS.index(v) > ind...`: sets `hard` to the value of `{k: v for k, v in config.hard_start.items() if k != kind or TIERS.index(v) > ...`. `{k: v for k, v in config.hard_start.items() if k != kind or TIERS.i...` builds a dictionary: for each `(k, v)` in `config.hard_start.items()`, keeping only those for which `k != kind or TIERS.index(v) > index + 1` is true; `config.hard_start.items()` is the (key, value) pairs of `config.hard_start`; `TIERS.index(v)` is the position of `v` in `TIERS`.
- `changed = RouterConfig(`: sets `changed` to the value of `RouterConfig(start, hard, config.label_check, config.request_cap, config.tigh...`.
- `return changed, f"{kind} tasks start at {TIERS[index + 1]} instead of {TIERS[index]}"`: ends the function and hands back `(changed, f'{kind} tasks start at {TIERS[index + 1]} instead of {TIERS[index]}')`. the f-string inserts `kind`, `TIERS[index + 1]`, `TIERS[index]` into the text.
- `if kind == "policy":`: runs the block below only if `kind == 'policy'` is true.
- `changed = RouterConfig(`: sets `changed` to the value of `RouterConfig(config.start, config.hard_start, config.label_check, config.requ...`.

<!-- fmt: off -->
```python
        return changed, "policy answers must quote the line that best matches the question, not just any line"
    return config, f"{kind} already starts at the top tier and has no stronger check; nothing changed"


def weakest_kind(outcomes: Sequence[Outcome]) -> str | None:
    """The kind with the most accepted-but-wrong answers on the test set (None when there are none)."""
    counts: dict[str, int] = {}
    for o in outcomes:
        if o.decision.answer is not None and not o.correct:
            counts[o.kind] = counts.get(o.kind, 0) + 1
    return max(sorted(counts), key=lambda k: counts[k]) if counts else None


def make_checks(tiers: ModelTiers, config: RouterConfig) -> AnswerChecks:
```
<!-- fmt: on -->

- `return changed, "policy answers must quote the line that best matches the question, not...`: ends the function and hands back `(changed, 'policy answers must quote the line that best matches the question,...`.
- `return config, f"{kind} already starts at the top tier and has no stronger check; nothi...`: ends the function and hands back `(config, f'{kind} already starts at the top tier and has no stronger check; n...`. the f-string inserts `kind` into the text.
- `def weakest_kind(outcomes: Sequence[Outcome]) -> str | None:`: defines the function `weakest_kind` taking outcomes (Sequence[Outcome]) and returns `str | None`. Purpose: The kind with the most accepted-but-wrong answers on the test set (None when there are none).
- `"""The kind with the most accepted-but-wrong answers on the test set (None when there a...`: a docstring (documentation text). It says: "The kind with the most accepted-but-wrong answers on the test set (None when there are none)."
- `counts: dict[str, int] = {}`: declares a variable `counts` of type `dict[str, int]` and sets it to `{}`.
- `for o in outcomes:`: repeats the block below once for each `o` in `outcomes`.
- `if o.decision.answer is not None and not o.correct:`: runs the block below only if `o.decision.answer is not None and (not o.correct)` is true. `o.decision.answer is not None` tests that there is something in `o.decision.answer`.
- `counts[o.kind] = counts.get(o.kind, 0) + 1`: sets `counts[o.kind]` to the value of `counts.get(o.kind, 0) + 1`. `counts.get(o.kind, 0)` looks up `o.kind` in `counts` (default `0` when missing).
- `return max(sorted(counts), key=lambda k: counts[k]) if counts else None`: ends the function and hands back `max(sorted(counts), key=lambda k: counts[k]) if counts else None`. `max(sorted(counts), key=lambda k: counts[k]) if counts else None` gives `max(sorted(counts), key=lambda k: cou...` when `counts` is true, otherwise `None`; `max(sorted(counts), key=lambda k: counts[k])` is the largest of `sorted(counts)`; `sorted(counts)` is `counts` in sorted order.
- `def make_checks(tiers: ModelTiers, config: RouterConfig) -> AnswerChecks:`: defines the function `make_checks` taking tiers (ModelTiers); config (RouterConfig) and returns `AnswerChecks`. Purpose: The answer checks for a router configuration.

<!-- fmt: off -->
```python
    """The answer checks for a router configuration."""
    return AnswerChecks(tiers, config.label_check, config.policy_check)
```
<!-- fmt: on -->

- `"""The answer checks for a router configuration."""`: a docstring (documentation text). It says: "The answer checks for a router configuration."
- `return AnswerChecks(tiers, config.label_check, config.policy_check)`: ends the function and hands back `AnswerChecks(tiers, config.label_check, config.policy_check)`.

#### `src/cost_router/application/ports.py`

<!-- fmt: off -->
```python
"""Ports: what the application needs from the outside world, written as protocols."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol, TypeVar

from cost_router.domain.llm import ChatRequest, ChatResponse


class ChatModel(Protocol):
    """One chat-completion call. Adapters raise RetryableModelError or PermanentModelError on failure."""

    def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:
```
<!-- fmt: on -->

- `"""Ports: what the application needs from the outside world, written as protocols."""`: a docstring (documentation text). It says: "Ports: what the application needs from the outside world, written as protocols."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from collections.abc import Callable, Sequence`: takes the name(s) `Callable, Sequence` from the module `collections.abc` (abstract container types used in annotations).
- `from typing import Protocol, TypeVar`: takes the name(s) `Protocol, TypeVar` from the module `typing` (names used in type annotations).
- `from cost_router.domain.llm import ChatRequest, ChatResponse`: takes the name(s) `ChatRequest, ChatResponse` from the module `cost_router.domain.llm` (a module of this project).
- **New idea.** A **Protocol** is a class that only lists methods. Any object that has those methods fits it, with no inheritance needed; it describes what a caller needs.
- `class ChatModel(Protocol):`: defines the class `ChatModel` that inherits from `Protocol`. Purpose: One chat-completion call.
- `"""One chat-completion call. Adapters raise RetryableModelError or PermanentModelError ...`: a docstring (documentation text). It says: "One chat-completion call."
- `def complete(self, request: ChatRequest, timeout_s: float = 60.0) -> ChatResponse:`: defines the method `complete` taking request (ChatRequest); timeout_s (float), default 60.0 and returns `ChatResponse`. Purpose: Send the request and return the finished response.

<!-- fmt: off -->
```python
        """Send the request and return the finished response."""
        ...


class Clock(Protocol):
    """Time, replaceable so that tests and simulations are deterministic."""

    def monotonic(self) -> float:
        """Seconds from an arbitrary fixed start; never goes backward."""
        ...

    def sleep(self, seconds: float) -> None:
        """Wait (a manual clock just advances)."""
        ...
```
<!-- fmt: on -->

- `"""Send the request and return the finished response."""`: a docstring (documentation text). It says: "Send the request and return the finished response."
- **New idea.** `...` (an ellipsis) is a placeholder meaning "the body is not written here"; in a Protocol it marks a method that implementations must supply.
- `...`: a placeholder; the body is intentionally not written here.
- `class Clock(Protocol):`: defines the class `Clock` that inherits from `Protocol`. Purpose: Time, replaceable so that tests and simulations are deterministic.
- `"""Time, replaceable so that tests and simulations are deterministic."""`: a docstring (documentation text). It says: "Time, replaceable so that tests and simulations are deterministic."
- `def monotonic(self) -> float:`: defines the method `monotonic` taking no arguments and returns `float`. Purpose: Seconds from an arbitrary fixed start; never goes backward.
- `"""Seconds from an arbitrary fixed start; never goes backward."""`: a docstring (documentation text). It says: "Seconds from an arbitrary fixed start; never goes backward."
- `...`: a placeholder; the body is intentionally not written here.
- `def sleep(self, seconds: float) -> None:`: defines the method `sleep` taking seconds (float) and returns `None`. Purpose: Wait (a manual clock just advances).
- `"""Wait (a manual clock just advances)."""`: a docstring (documentation text). It says: "Wait (a manual clock just advances)."
- `...`: a placeholder; the body is intentionally not written here.

<!-- fmt: off -->
```python
class PromptStore(Protocol):
    """Versioned prompt templates, looked up by name such as `label.v1`."""

    def get(self, name: str) -> str:
        """The template text."""
        ...


T = TypeVar("T")
R = TypeVar("R")


class Mapper(Protocol):
    """Apply a function to items, possibly on several threads, returning results in input order."""
```
<!-- fmt: on -->

- `class PromptStore(Protocol):`: defines the class `PromptStore` that inherits from `Protocol`. Purpose: Versioned prompt templates, looked up by name such as `label.v1`.
- `"""Versioned prompt templates, looked up by name such as 'label.v1'."""`: a docstring (documentation text). It says: "Versioned prompt templates, looked up by name such as `label.v1`."
- `def get(self, name: str) -> str:`: defines the method `get` taking name (str) and returns `str`. Purpose: The template text.
- `"""The template text."""`: a docstring (documentation text). It says: "The template text."
- `...`: a placeholder; the body is intentionally not written here.
- `T = TypeVar("T")`: sets `T` to the value of `TypeVar('T')`. `TypeVar('T')` is a placeholder type.
- `R = TypeVar("R")`: sets `R` to the value of `TypeVar('R')`. `TypeVar('R')` is a placeholder type.
- `class Mapper(Protocol):`: defines the class `Mapper` that inherits from `Protocol`. Purpose: Apply a function to items, possibly on several threads, returning results in input order.
- `"""Apply a function to items, possibly on several threads, returning results in input o...`: a docstring (documentation text). It says: "Apply a function to items, possibly on several threads, returning results in input order."

<!-- fmt: off -->
```python
    def __call__(self, function: Callable[[T], R], items: Sequence[T], /) -> list[R]:
        """Map."""
        ...
```
<!-- fmt: on -->

- `def __call__(self, function: Callable[[T], R], items: Sequence[T], /) -> list[R]:`: defines the method `__call__` taking function (Callable[[T], R]); items (Sequence[T]) and returns `list[R]`. Purpose: Map.
- `"""Map."""`: a docstring (documentation text). It says: "Map."
- `...`: a placeholder; the body is intentionally not written here.

#### `src/cost_router/application/report_md.py`

<!-- fmt: off -->
```python
"""The human-readable report: plain tables built from the stored results."""

from __future__ import annotations

from typing import Any

from cost_router.domain.pricing import TIERS


def pct(value: float) -> str:
    """A rate as a percentage with one decimal."""
    return f"{value * 100:.1f}%"
```
<!-- fmt: on -->

- `"""The human-readable report: plain tables built from the stored results."""`: a docstring (documentation text). It says: "The human-readable report: plain tables built from the stored results."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).
- `from cost_router.domain.pricing import TIERS`: takes the name(s) `TIERS` from the module `cost_router.domain.pricing` (a module of this project).
- `def pct(value: float) -> str:`: defines the function `pct` taking value (float) and returns `str`. Purpose: A rate as a percentage with one decimal.
- `"""A rate as a percentage with one decimal."""`: a docstring (documentation text). It says: "A rate as a percentage with one decimal."
- `return f"{value * 100:.1f}%"`: ends the function and hands back `f'{value * 100:.1f}%'`. the f-string inserts `value * 100` into the text.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `def money(value: float | None) -> str:`: defines the function `money` taking value (float | None) and returns `str`. Purpose: Dollars with six decimals, or n/a.
- `"""Dollars with six decimals, or n/a."""`: a docstring (documentation text). It says: "Dollars with six decimals, or n/a."
- `return "n/a" if value is None else f"${value:.6f}"`: ends the function and hands back `'n/a' if value is None else f'${value:.6f}'`. `'n/a' if value is None else f'${value:.6f}'` gives `'n/a'` when `value is None` is true, otherwise `f'${value:.6f}'`; `value is None` tests that there is nothing (`None`) in `value`; the f-string inserts `value` into the text.
- `def interval(low: float, high: float) -> str:`: defines the function `interval` taking low (float); high (float) and returns `str`. Purpose: A 95% interval in percent.
- `"""A 95% interval in percent."""`: a docstring (documentation text). It says: "A 95% interval in percent."
- `return f"[{pct(low)}, {pct(high)}]"`: ends the function and hands back `f'[{pct(low)}, {pct(high)}]'`. the f-string inserts `pct(low)`, `pct(high)` into the text.
- `def render_report(`: defines the function `render_report` taking models (dict[str, Any]); checks (dict[str, Any]); router (dict[str, Any]); day (dict[str, Any]); audit (dict[str, Any]) and returns `str`. Purpose: The whole report as Markdown.
- `"""The whole report as Markdown."""`: a docstring (documentation text). It says: "The whole report as Markdown."

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `out = ["# Cost-aware router: results", ""]`: sets `out` to a list of 2 items.
- `out += ["## Step 1: each model alone, 150 build tasks", ""]`: adds `['## Step 1: each model alone, 150 build tasks', '']` to `out` and stores the result back.
- `out += [`: adds `['| Model | Kind | Accuracy (95% interval) | Cost per cal...` to `out` and stores the result back.
- `for tier in TIERS:`: repeats the block below once for each `tier` in `TIERS`.
- `for kind, cell in models["table"][tier].items():`: repeats the block below once for each `(kind, cell)` in `models['table'][tier].items()`. `models['table'][tier].items()` is the (key, value) pairs of `models['table'][tier]`.
- `a = cell["accuracy"]`: sets `a` to the value of `cell['accuracy']`.
- `out.append(`: runs `out.append(f"| {tier} | {kind} | {pct(a['value'])} {interval(a['low'], a['high'])} | {m...` for its effect and ignores the result. `out.append(f"| {tier} | {kind} | {pct(a['value'])} {interval(a['low...` adds `f"| {tier} | {kind} | {pct(a['value'])} {interval(a['low'...` to the end of `out`; the f-string inserts `tier`, `kind`, `pct(a['value'])`, `interval(a['low'], a['high'])` into the text.
- `out += [`: adds `['', 'Cheapest tier within the agreed margin of the large...` to `out` and stores the result back. `', '.join((f"{k}: {v or 'none'}" for k, v in models['cheapest_match...` is the items of `(f"{k}: {v or 'none'}" for k, v in models['cheapest_match...` joined into one text with `', '` between them; `(f"{k}: {v or 'none'}" for k, v in models['cheapest_matching'].item...` builds a generator of values: for each `(k, v)` in `models['cheapest_matching'].items()`; the f-string inserts `k`, `v or 'none'` into the text.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `out += ["## Step 2: the checks, measured against the truth (build set)", ""]`: adds `['## Step 2: the checks, measured against the truth (buil...` to `out` and stores the result back.
- `out += [`: adds `['| Tier | Kind | Check | Accepted | False-accept rate | ...` to `out` and stores the result back.
- `bar = checks["bar"]`: sets `bar` to the value of `checks['bar']`.
- `for tier in TIERS:`: repeats the block below once for each `tier` in `TIERS`.
- `for kind, by_check in checks["rates"][tier].items():`: repeats the block below once for each `(kind, by_check)` in `checks['rates'][tier].items()`. `checks['rates'][tier].items()` is the (key, value) pairs of `checks['rates'][tier]`.
- `for name, r in by_check.items():`: repeats the block below once for each `(name, r)` in `by_check.items()`. `by_check.items()` is the (key, value) pairs of `by_check`.
- `over = "YES" if r["false_accept_rate"] > bar else "no"`: sets `over` to the value of `'YES' if r['false_accept_rate'] > bar else 'no'`. `'YES' if r['false_accept_rate'] > bar else 'no'` gives `'YES'` when `r['false_accept_rate'] > bar` is true, otherwise `'no'`.
- `out.append(`: runs `out.append(f"| {tier} | {kind} | {name} | {r['accepted']} | {pct(r['false_accept_rate']...` for its effect and ignores the result. `out.append(f"| {tier} | {kind} | {name} | {r['accepted']} | {pct(r[...` adds `f"| {tier} | {kind} | {name} | {r['accepted']} | {pct(r['...` to the end of `out`; the f-string inserts `tier`, `kind`, `name`, `r['accepted']` into the text.
- `out += [`: adds `['', f'Bar agreed in advance: a check whose false-accept ...` to `out` and stores the result back. the f-string inserts `pct(bar)` into the text.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `cfg = router["config"]`: sets `cfg` to the value of `router['config']`.
- `out += ["## Step 3: the configuration the build set produced", "", f"'{cfg}'", ""]`: adds `['## Step 3: the configuration the build set produced', '...` to `out` and stores the result back. the f-string inserts `cfg` into the text.
- `out += ["## Step 5: the router and each model alone, 150 test tasks", ""]`: adds `['## Step 5: the router and each model alone, 150 test ta...` to `out` and stores the result back.
- `out += [`: adds `['| Method | Accuracy (95% interval) | Total cost | Cost ...` to `out` and stores the result back.
- `for name, s in router["methods"].items():`: repeats the block below once for each `(name, s)` in `router['methods'].items()`. `router['methods'].items()` is the (key, value) pairs of `router['methods']`.
- `a = s["accuracy"]`: sets `a` to the value of `s['accuracy']`.
- `low, high = s["cost_per_correct_interval"]`: sets `(low, high)` to the value of `s['cost_per_correct_interval']`.
- `out.append(`: runs `out.append(f"| {name} | {pct(a['value'])} {interval(a['low'], a['high'])} | {money(s['t...` for its effect and ignores the result. `out.append(f"| {name} | {pct(a['value'])} {interval(a['low'], a['hi...` adds `f"| {name} | {pct(a['value'])} {interval(a['low'], a['hig...` to the end of `out`; the f-string inserts `name`, `pct(a['value'])`, `interval(a['low'], a['high'])`, `money(s['total_cost'])` into the text.
- `v = router["verdict"]`: sets `v` to the value of `router['verdict']`.

<!-- fmt: off -->
```python
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
```
<!-- fmt: on -->

- `out += [`: adds `['', f"Router against the large model alone: accuracy dif...` to `out` and stores the result back. the f-string inserts `v['accuracy_difference_vs_l...`, `v['accuracy_difference_inte...`, `v['accuracy_difference_inte...`, `v['margin']` into the text.
- `out += ["## Step 4: one day under a budget", ""]`: adds `['## Step 4: one day under a budget', '']` to `out` and stores the result back.
- `out += [`: adds `['| Budget (share of always-large) | Spent | Under budget...` to `out` and stores the result back.
- `for d in day["days"]:`: repeats the block below once for each `d` in `day['days']`.
- `out.append(`: runs `out.append(f"| {pct(d['fraction'])} ({money(d['budget'])}) | {money(d['spent'])} | {d['...` for its effect and ignores the result. `out.append(f"| {pct(d['fraction'])} ({money(d['budget'])}) | {money...` adds `f"| {pct(d['fraction'])} ({money(d['budget'])}) | {money(...` to the end of `out`; the f-string inserts `pct(d['fraction'])`, `money(d['budget'])`, `money(d['spent'])`, `d['under_budget']` into the text.

<!-- fmt: off -->
```python
    out += ["", "## Step 6: accepted answers that were wrong (test set)", ""]
    out += [f"`{audit['before']['by_tier_and_check']}`", ""]
    ch = audit["change"]
    if ch:
        out += [
            f"Change ({ch['description']}): accuracy {pct(ch['accuracy_before'])} to {pct(ch['accuracy_after'])}; cost per correct {money(ch['cost_per_correct_before'])} to {money(ch['cost_per_correct_after'])}; false accepts {ch['false_accepts_before']} to {ch['false_accepts_after']}.",
            "",
        ]
    return "\n".join(out) + "\n"
```
<!-- fmt: on -->

- `out += ["", "## Step 6: accepted answers that were wrong (test set)", ""]`: adds `['', '## Step 6: accepted answers that were wrong (test s...` to `out` and stores the result back.
- `out += [f"'{audit['before']['by_tier_and_check']}'", ""]`: adds `[f"'{audit['before']['by_tier_and_check']}'", '']` to `out` and stores the result back. the f-string inserts `audit['before']['by_tier_an...` into the text.
- `ch = audit["change"]`: sets `ch` to the value of `audit['change']`.
- `if ch:`: runs the block below only if `ch` is true.
- `out += [`: adds `[f"Change ({ch['description']}): accuracy {pct(ch['accura...` to `out` and stores the result back. the f-string inserts `ch['description']`, `pct(ch['accuracy_before'])`, `pct(ch['accuracy_after'])`, `money(ch['cost_per_correct_...` into the text.
- `return "\n".join(out) + "\n"`: ends the function and hands back `'\n'.join(out) + '\n'`. `'\n'.join(out)` is the items of `out` joined into one text with `'\n'` between them.

#### `src/cost_router/application/router.py`

<!-- fmt: off -->
```python
"""The cost-aware router: cheapest tier first, a check after every answer, escalation on a failed check."""

from __future__ import annotations

from cost_router.application.answer_checks import AnswerChecks
from cost_router.application.tiers import ModelTiers
from cost_router.domain.pricing import TIERS
from cost_router.domain.routing import Attempt, DayBudget, Decision, RouterConfig
from cost_router.domain.signals import hard_signal
from cost_router.domain.tasks import Task

ESCALATE = "escalate_to_person"
```
<!-- fmt: on -->

- `"""The cost-aware router: cheapest tier first, a check after every answer, escalation o...`: a docstring (documentation text). It says: "The cost-aware router: cheapest tier first, a check after every answer, escalation on a failed check."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from cost_router.application.answer_checks import AnswerChecks`: takes the name(s) `AnswerChecks` from the module `cost_router.application.answer_checks` (a module of this project).
- `from cost_router.application.tiers import ModelTiers`: takes the name(s) `ModelTiers` from the module `cost_router.application.tiers` (a module of this project).
- `from cost_router.domain.pricing import TIERS`: takes the name(s) `TIERS` from the module `cost_router.domain.pricing` (a module of this project).
- `from cost_router.domain.routing import Attempt, DayBudget, Decision, RouterConfig`: takes the name(s) `Attempt, DayBudget, Decision, RouterConfig` from the module `cost_router.domain.routing` (a module of this project).
- `from cost_router.domain.signals import hard_signal`: takes the name(s) `hard_signal` from the module `cost_router.domain.signals` (a module of this project).
- `from cost_router.domain.tasks import Task`: takes the name(s) `Task` from the module `cost_router.domain.tasks` (a module of this project).
- `ESCALATE = "escalate_to_person"`: sets `ESCALATE` to the constant `'escalate_to_person'`.

<!-- fmt: off -->
```python
class CostRouter:
    """Tries tiers in order of price and stops at the first answer a check accepts.

    - The start tier comes from the build set (config/router.json) and a hard task may start higher.
    - Before every call the router adds the next call's estimated cost (and its check's) to what the request has
      spent and refuses to go over the per-request cap, or over what is left of the day's budget when there is one.
    - Once the day's budget is 80% used, the largest tier is no longer available; the router keeps answering until
      the money runs out, then hands the task to a person.
    """

    def __init__(self, tiers: ModelTiers, checks: AnswerChecks, config: RouterConfig) -> None:
        self._tiers = tiers
        self._checks = checks
        self._config = config
```
<!-- fmt: on -->

- `class CostRouter:`: defines the class `CostRouter`. Purpose: Tries tiers in order of price and stops at the first answer a check accepts.
- `"""Tries tiers in order of price and stops at the first answer a check accepts.`: a docstring (documentation text). It says: "Tries tiers in order of price and stops at the first answer a check accepts."
- `def __init__(self, tiers: ModelTiers, checks: AnswerChecks, config: RouterConfig) -> None:`: defines the method `__init__` taking tiers (ModelTiers); checks (AnswerChecks); config (RouterConfig) and returns `None`.
- `self._tiers = tiers`: sets `self._tiers` to the value of `tiers`.
- `self._checks = checks`: sets `self._checks` to the value of `checks`.
- `self._config = config`: sets `self._config` to the value of `config`.

<!-- fmt: off -->
```python
    @property
    def config(self) -> RouterConfig:
        """The configuration in force."""
        return self._config

    def route(self, task: Task, day: DayBudget | None = None) -> Decision:
        """Serve one task and record every tier tried."""
        config = self._config
        share = day.used_share() if day else 0.0
        allowed = TIERS[:-1] if day and share >= config.tighten_at else TIERS
        start = config.start_index(task.kind.value, hard_signal(task))
        limit = config.request_cap if day is None else min(config.request_cap, day.budget - day.used)
        spent = 0.0
        tokens = 0
```
<!-- fmt: on -->

- `def config(self) -> RouterConfig:`: defines the method `config` taking no arguments and returns `RouterConfig`. Decorators: `property`. Purpose: The configuration in force.
- `"""The configuration in force."""`: a docstring (documentation text). It says: "The configuration in force."
- `return self._config`: ends the function and hands back `self._config`.
- `def route(self, task: Task, day: DayBudget | None = None) -> Decision:`: defines the method `route` taking task (Task); day (DayBudget | None), default None and returns `Decision`. Purpose: Serve one task and record every tier tried.
- `"""Serve one task and record every tier tried."""`: a docstring (documentation text). It says: "Serve one task and record every tier tried."
- `config = self._config`: sets `config` to the value of `self._config`.
- `share = day.used_share() if day else 0.0`: sets `share` to the value of `day.used_share() if day else 0.0`. `day.used_share() if day else 0.0` gives `day.used_share()` when `day` is true, otherwise `0.0`.
- `allowed = TIERS[:-1] if day and share >= config.tighten_at else TIERS`: sets `allowed` to the value of `TIERS[:-1] if day and share >= config.tighten_at else TIERS`. `TIERS[:-1] if day and share >= config.tighten_at else TIERS` gives `TIERS[:-1]` when `day and share >= config.tighten_at` is true, otherwise `TIERS`; `TIERS[:-1]` is a slice (a part) of `TIERS`.
- `start = config.start_index(task.kind.value, hard_signal(task))`: sets `start` to the value of `config.start_index(task.kind.value, hard_signal(task))`.
- `limit = config.request_cap if day is None else min(config.request_cap, day.budget - day...`: sets `limit` to the value of `config.request_cap if day is None else min(config.request_cap, day.budget - d...`. `config.request_cap if day is None else min(config.request_cap, day....` gives `config.request_cap` when `day is None` is true, otherwise `min(config.request_cap, day.budget - ...`; `day is None` tests that there is nothing (`None`) in `day`; `min(config.request_cap, day.budget - day.used)` is the smallest of `config.request_cap`, `day.budget - day.used`.
- `spent = 0.0`: sets `spent` to the constant `0.0`.
- `tokens = 0`: sets `tokens` to the constant `0`.

<!-- fmt: off -->
```python
        attempts: list[Attempt] = []
        tags: list[str] = []
        for tier in allowed[min(start, len(allowed)) :]:
            projected = spent + self._tiers.estimate(tier, task) + self._checks.estimate_extra(task, tier)
            if projected > limit:
                tags.append("cap" if limit == config.request_cap else "budget")
                break
            answered = self._tiers.call(tier, task)
            result = self._checks.check(task, tier, answered.text)
            call_cost = answered.cost + result.extra_cost
            spent += call_cost
            tokens += answered.tokens + result.extra_tokens
            attempts.append(Attempt(tier, result.passed, call_cost, answered.tokens + result.extra_tokens))
            if result.passed:
                if day:
                    day.add(spent)
                return Decision(task.task_id, answered.text, tier, tuple(attempts), spent, tokens, share, tuple(tags))
```
<!-- fmt: on -->

- `attempts: list[Attempt] = []`: declares a variable `attempts` of type `list[Attempt]` and sets it to `[]`.
- `tags: list[str] = []`: declares a variable `tags` of type `list[str]` and sets it to `[]`.
- `for tier in allowed[min(start, len(allowed)) :]:`: repeats the block below once for each `tier` in `allowed[min(start, len(allowed)):]`. `allowed[min(start, len(allowed)):]` is a slice (a part) of `allowed`; `min(start, len(allowed))` is the smallest of `start`, `len(allowed)`; `len(allowed)` is the number of items in `allowed`.
- `projected = spent + self._tiers.estimate(tier, task) + self._checks.estimate_extra(task...`: sets `projected` to the value of `spent + self._tiers.estimate(tier, task) + self._checks.estimate_extra(task, ...`.
- `if projected > limit:`: runs the block below only if `projected > limit` is true.
- `tags.append("cap" if limit == config.request_cap else "budget")`: runs `tags.append('cap' if limit == config.request_cap else 'budget')` for its effect and ignores the result. `tags.append('cap' if limit == config.request_cap else 'budget')` adds `'cap' if limit == config.request_cap else 'budget'` to the end of `tags`; `'cap' if limit == config.request_cap else 'budget'` gives `'cap'` when `limit == config.request_cap` is true, otherwise `'budget'`.
- `break`: leaves the loop at once.
- `answered = self._tiers.call(tier, task)`: sets `answered` to the value of `self._tiers.call(tier, task)`.
- `result = self._checks.check(task, tier, answered.text)`: sets `result` to the value of `self._checks.check(task, tier, answered.text)`.
- `call_cost = answered.cost + result.extra_cost`: sets `call_cost` to the value of `answered.cost + result.extra_cost`.
- `spent += call_cost`: adds `call_cost` to `spent` and stores the result back.
- `tokens += answered.tokens + result.extra_tokens`: adds `answered.tokens + result.extra_tokens` to `tokens` and stores the result back.
- `attempts.append(Attempt(tier, result.passed, call_cost, answered.tokens + result.extra_...`: runs `attempts.append(Attempt(tier, result.passed, call_cost, answered.tokens + result.extra_...` for its effect and ignores the result. `attempts.append(Attempt(tier, result.passed, call_cost, answered.to...` adds `Attempt(tier, result.passed, call_cost, answered.tokens +...` to the end of `attempts`.
- `if result.passed:`: runs the block below only if `result.passed` is true.
- `if day:`: runs the block below only if `day` is true.
- `day.add(spent)`: runs `day.add(spent)` for its effect and ignores the result. `day.add(spent)` adds `spent` to the set `day`.
- `return Decision(task.task_id, answered.text, tier, tuple(attempts), spent, tokens, shar...`: ends the function and hands back `Decision(task.task_id, answered.text, tier, tuple(attempts), spent, tokens, s...`. `tuple(attempts)` is `attempts` as a tuple; `tuple(tags)` is `tags` as a tuple.

<!-- fmt: off -->
```python
        if day:
            day.add(spent)
        return Decision(task.task_id, None, ESCALATE, tuple(attempts), spent, tokens, share, tuple(tags))
```
<!-- fmt: on -->

- `if day:`: runs the block below only if `day` is true.
- `day.add(spent)`: runs `day.add(spent)` for its effect and ignores the result. `day.add(spent)` adds `spent` to the set `day`.
- `return Decision(task.task_id, None, ESCALATE, tuple(attempts), spent, tokens, share, tu...`: ends the function and hands back `Decision(task.task_id, None, ESCALATE, tuple(attempts), spent, tokens, share,...`. `tuple(attempts)` is `attempts` as a tuple; `tuple(tags)` is `tags` as a tuple.

#### `src/cost_router/application/templates.py`

<!-- fmt: off -->
```python
"""Prompt templates use `{{name}}` placeholders; rendering fails loudly on a missing value or a leftover."""

from __future__ import annotations

import re

PLACEHOLDER = re.compile(r"\{\{([a-z_]+)\}\}")


def render(template: str, **values: str) -> str:
    """Fill the placeholders; an unknown or unfilled one is an error, never a silent blank."""
    unknown = set(values) - set(PLACEHOLDER.findall(template))
    if unknown:
        raise ValueError(f"template has no placeholder for {sorted(unknown)}")
```
<!-- fmt: on -->

- `"""Prompt templates use '{{name}}' placeholders; rendering fails loudly on a missing va...`: a docstring (documentation text). It says: "Prompt templates use `{{name}}` placeholders; rendering fails loudly on a missing value or a leftover."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import re`: imports the module(s) `re` so this file can use them. `re` is regular expressions.
- `PLACEHOLDER = re.compile(r"\{\{([a-z_]+)\}\}")`: sets `PLACEHOLDER` to a prepared regular expression (every pattern is explained piece by piece in `regular-expressions.md`). `re.compile('\\{\\{([a-z_]+)\\}\\}')` is the pattern `'\\{\\{([a-z_]+)\\}\\}'` prepared for repeated use.
- `def render(template: str, **values: str) -> str:`: defines the function `render` taking template (str); **values (any extra named values) and returns `str`. Purpose: Fill the placeholders; an unknown or unfilled one is an error, never a silent blank.
- `"""Fill the placeholders; an unknown or unfilled one is an error, never a silent blank."""`: a docstring (documentation text). It says: "Fill the placeholders; an unknown or unfilled one is an error, never a silent blank."
- `unknown = set(values) - set(PLACEHOLDER.findall(template))`: sets `unknown` to the value of `set(values) - set(PLACEHOLDER.findall(template))`. `set(values)` is `values` as a set (each value once); `set(PLACEHOLDER.findall(template))` is `PLACEHOLDER.findall(template)` as a set (each value once); `PLACEHOLDER.findall(template)` is all matches of the pattern.
- `if unknown:`: runs the block below only if `unknown` is true.
- **New idea.** `raise Error("message")` stops normal flow and signals an error. The nearest `except` that matches the type catches it; if none does, the program stops with the message. `raise ... from error` records the original error as the cause.
- `raise ValueError(f"template has no placeholder for {sorted(unknown)}")`: signals an error, `ValueError(f'template has no placeholder for {sorted(unknown)}')`; normal flow stops here and the nearest matching `except` takes over. `ValueError(f'template has no placeholder for {sorted(unknown)}')` is a ValueError; the f-string inserts `sorted(unknown)` into the text; `sorted(unknown)` is `unknown` in sorted order.

<!-- fmt: off -->
```python
    def fill(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in values:
            raise ValueError(f"no value for placeholder {{{{{name}}}}}")
        return values[name]

    return PLACEHOLDER.sub(fill, template)
```
<!-- fmt: on -->

- `def fill(match: re.Match[str]) -> str:`: defines the function `fill` taking match (re.Match[str]) and returns `str`.
- `name = match.group(1)`: sets `name` to the value of `match.group(1)`. `match.group(1)` is the part of the match that matched group `1`.
- `if name not in values:`: runs the block below only if `name not in values` is true.
- `raise ValueError(f"no value for placeholder {{{{{name}}}}}")`: signals an error, `ValueError(f'no value for placeholder {{{{{name}}}}}')`; normal flow stops here and the nearest matching `except` takes over. `ValueError(f'no value for placeholder {{{{{name}}}}}')` is a ValueError; the f-string inserts `name` into the text.
- `return values[name]`: ends the function and hands back `values[name]`.
- `return PLACEHOLDER.sub(fill, template)`: ends the function and hands back `PLACEHOLDER.sub(fill, template)`. `PLACEHOLDER.sub(fill, template)` is the text with matches of the pattern replaced.

#### `src/cost_router/application/tiers.py`

<!-- fmt: off -->
```python
"""The three model tiers: building each task's prompt, calling the tier's model, and costing the call."""

from __future__ import annotations

from dataclasses import dataclass

from cost_router.application.ports import ChatModel, PromptStore
from cost_router.application.templates import render
from cost_router.domain.llm import ChatRequest, Message, Usage
from cost_router.domain.pricing import PriceTable
from cost_router.domain.tasks import POLICY_LINES, REFUND_POLICY, Kind, Task

MAX_TOKENS = {Kind.LABEL: 8, Kind.REFUND: 80, Kind.POLICY: 80}
SECOND_SAMPLE = {"temperature": 0.8, "seed": 7}
```
<!-- fmt: on -->

- `"""The three model tiers: building each task's prompt, calling the tier's model, and co...`: a docstring (documentation text). It says: "The three model tiers: building each task's prompt, calling the tier's model, and costing the call."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `from cost_router.application.ports import ChatModel, PromptStore`: takes the name(s) `ChatModel, PromptStore` from the module `cost_router.application.ports` (a module of this project).
- `from cost_router.application.templates import render`: takes the name(s) `render` from the module `cost_router.application.templates` (a module of this project).
- `from cost_router.domain.llm import ChatRequest, Message, Usage`: takes the name(s) `ChatRequest, Message, Usage` from the module `cost_router.domain.llm` (a module of this project).
- `from cost_router.domain.pricing import PriceTable`: takes the name(s) `PriceTable` from the module `cost_router.domain.pricing` (a module of this project).
- `from cost_router.domain.tasks import POLICY_LINES, REFUND_POLICY, Kind, Task`: takes the name(s) `POLICY_LINES, REFUND_POLICY, Kind, Task` from the module `cost_router.domain.tasks` (a module of this project).
- `MAX_TOKENS = {Kind.LABEL: 8, Kind.REFUND: 80, Kind.POLICY: 80}`: sets `MAX_TOKENS` to a dictionary with 3 entries.
- `SECOND_SAMPLE = {"temperature": 0.8, "seed": 7}`: sets `SECOND_SAMPLE` to a dictionary with 2 entries.

<!-- fmt: off -->
```python
@dataclass(frozen=True)
class Answered:
    """One model answer with what it cost."""

    text: str
    cost: float
    usage: Usage
    latency_s: float

    @property
    def tokens(self) -> int:
        """Billed tokens."""
        return self.usage.total
```
<!-- fmt: on -->

- `class Answered:`: defines the class `Answered`. Decorators: `dataclass(frozen=True)`. Purpose: One model answer with what it cost.
- `"""One model answer with what it cost."""`: a docstring (documentation text). It says: "One model answer with what it cost."
- `text: str`: declares a field of the class `text` of type `str` (no value yet).
- `cost: float`: declares a field of the class `cost` of type `float` (no value yet).
- `usage: Usage`: declares a field of the class `usage` of type `Usage` (no value yet).
- `latency_s: float`: declares a field of the class `latency_s` of type `float` (no value yet).
- `def tokens(self) -> int:`: defines the method `tokens` taking no arguments and returns `int`. Decorators: `property`. Purpose: Billed tokens.
- `"""Billed tokens."""`: a docstring (documentation text). It says: "Billed tokens."
- `return self.usage.total`: ends the function and hands back `self.usage.total`.

<!-- fmt: off -->
```python
@dataclass(frozen=True)
class ModelTiers:
    """Calls the model behind a tier name; the same code serves recorded, local and hosted models."""

    model: ChatModel
    prompts: PromptStore
    models: dict[str, str]
    prices: PriceTable

    def prompt(self, task: Task) -> str:
        """The rendered prompt of a task."""
        if task.kind is Kind.LABEL:
            return render(self.prompts.get("label.v2"), text=task.text)
        if task.kind is Kind.REFUND:
            return render(self.prompts.get("refund.v2"), policy=REFUND_POLICY, text=task.text)
```
<!-- fmt: on -->

- `class ModelTiers:`: defines the class `ModelTiers`. Decorators: `dataclass(frozen=True)`. Purpose: Calls the model behind a tier name; the same code serves recorded, local and hosted models.
- `"""Calls the model behind a tier name; the same code serves recorded, local and hosted ...`: a docstring (documentation text). It says: "Calls the model behind a tier name; the same code serves recorded, local and hosted models."
- `model: ChatModel`: declares a field of the class `model` of type `ChatModel` (no value yet).
- `prompts: PromptStore`: declares a field of the class `prompts` of type `PromptStore` (no value yet).
- `models: dict[str, str]`: declares a field of the class `models` of type `dict[str, str]` (no value yet).
- `prices: PriceTable`: declares a field of the class `prices` of type `PriceTable` (no value yet).
- `def prompt(self, task: Task) -> str:`: defines the method `prompt` taking task (Task) and returns `str`. Purpose: The rendered prompt of a task.
- `"""The rendered prompt of a task."""`: a docstring (documentation text). It says: "The rendered prompt of a task."
- `if task.kind is Kind.LABEL:`: runs the block below only if `task.kind is Kind.LABEL` is true.
- `return render(self.prompts.get("label.v2"), text=task.text)`: ends the function and hands back `render(self.prompts.get('label.v2'), text=task.text)`. `self.prompts.get('label.v2')` looks up `'label.v2'` in `self.prompts` (default (nothing) when missing).
- `if task.kind is Kind.REFUND:`: runs the block below only if `task.kind is Kind.REFUND` is true.
- `return render(self.prompts.get("refund.v2"), policy=REFUND_POLICY, text=task.text)`: ends the function and hands back `render(self.prompts.get('refund.v2'), policy=REFUND_POLICY, text=task.text)`. `self.prompts.get('refund.v2')` looks up `'refund.v2'` in `self.prompts` (default (nothing) when missing).

<!-- fmt: off -->
```python
        lines = "\n".join(f"{i + 1}. {line}" for i, line in enumerate(POLICY_LINES))
        return render(self.prompts.get("policy.v2"), policy_lines=lines, text=task.text)

    def request(self, tier: str, task: Task, second_sample: bool = False) -> ChatRequest:
        """The chat request for a tier; the second sample differs in temperature and seed."""
        extras = SECOND_SAMPLE if second_sample else {"temperature": 0.0, "seed": None}
        return ChatRequest(
            self.models[tier],
            (Message("user", self.prompt(task)),),
            temperature=float(extras["temperature"] or 0.0),
            max_tokens=MAX_TOKENS[task.kind],
            seed=extras["seed"],  # type: ignore[arg-type]
        )
```
<!-- fmt: on -->

- `lines = "\n".join(f"{i + 1}. {line}" for i, line in enumerate(POLICY_LINES))`: sets `lines` to the value of `'\n'.join((f'{i + 1}. {line}' for i, line in enumerate(POLICY_LINES)))`. `'\n'.join((f'{i + 1}. {line}' for i, line in enumerate(POLICY_LINES)))` is the items of `(f'{i + 1}. {line}' for i, line in enumerate(POLICY_LINES))` joined into one text with `'\n'` between them; `(f'{i + 1}. {line}' for i, line in enumerate(POLICY_LINES))` builds a generator of values: for each `(i, line)` in `enumerate(POLICY_LINES)`; the f-string inserts `i + 1`, `line` into the text.
- `return render(self.prompts.get("policy.v2"), policy_lines=lines, text=task.text)`: ends the function and hands back `render(self.prompts.get('policy.v2'), policy_lines=lines, text=task.text)`. `self.prompts.get('policy.v2')` looks up `'policy.v2'` in `self.prompts` (default (nothing) when missing).
- `def request(self, tier: str, task: Task, second_sample: bool = False) -> ChatRequest:`: defines the method `request` taking tier (str); task (Task); second_sample (bool), default False and returns `ChatRequest`. Purpose: The chat request for a tier; the second sample differs in temperature and seed.
- `"""The chat request for a tier; the second sample differs in temperature and seed."""`: a docstring (documentation text). It says: "The chat request for a tier; the second sample differs in temperature and seed."
- `extras = SECOND_SAMPLE if second_sample else {"temperature": 0.0, "seed": None}`: sets `extras` to the value of `SECOND_SAMPLE if second_sample else {'temperature': 0.0, 'seed': None}`. `SECOND_SAMPLE if second_sample else {'temperature': 0.0, 'seed': None}` gives `SECOND_SAMPLE` when `second_sample` is true, otherwise `{'temperature': 0.0, 'seed': None}`.
- `return ChatRequest(`: ends the function and hands back `ChatRequest(self.models[tier], (Message('user', self.prompt(task)),), tempera...`. `float(extras['temperature'] or 0.0)` is `extras['temperature'] or 0.0` converted to a decimal number.

<!-- fmt: off -->
```python
    def call(self, tier: str, task: Task, second_sample: bool = False) -> Answered:
        """Ask a tier; the cost comes from the billed tokens and the price table."""
        response = self.model.complete(self.request(tier, task, second_sample))
        return Answered(
            response.text.strip(), self.prices.cost(tier, response.usage), response.usage, response.latency_s
        )

    def estimate(self, tier: str, task: Task, calls: int = 1) -> float:
        """What `calls` calls of this task would cost, from a rough token count made before calling."""
        # Three characters per token over-counts English (it is nearer four), so the estimate errs high and the
        # per-request cap holds even when a prompt tokenizes worse than usual. The billed usage is checked afterwards.
        tokens = (len(self.prompt(task)) + 2) // 3 + MAX_TOKENS[task.kind]
        return self.prices.estimate(tier, tokens) * calls
```
<!-- fmt: on -->

- `def call(self, tier: str, task: Task, second_sample: bool = False) -> Answered:`: defines the method `call` taking tier (str); task (Task); second_sample (bool), default False and returns `Answered`. Purpose: Ask a tier; the cost comes from the billed tokens and the price table.
- `"""Ask a tier; the cost comes from the billed tokens and the price table."""`: a docstring (documentation text). It says: "Ask a tier; the cost comes from the billed tokens and the price table."
- `response = self.model.complete(self.request(tier, task, second_sample))`: sets `response` to the value of `self.model.complete(self.request(tier, task, second_sample))`.
- `return Answered(`: ends the function and hands back `Answered(response.text.strip(), self.prices.cost(tier, response.usage), respo...`. `response.text.strip()` is `response.text` without white space at both ends.
- `def estimate(self, tier: str, task: Task, calls: int = 1) -> float:`: defines the method `estimate` taking tier (str); task (Task); calls (int), default 1 and returns `float`. Purpose: What `calls` calls of this task would cost, from a rough token count made before calling.
- `"""What 'calls' calls of this task would cost, from a rough token count made before cal...`: a docstring (documentation text). It says: "What `calls` calls of this task would cost, from a rough token count made before calling."
- `tokens = (len(self.prompt(task)) + 2) // 3 + MAX_TOKENS[task.kind]`: sets `tokens` to the value of `(len(self.prompt(task)) + 2) // 3 + MAX_TOKENS[task.kind]`. `len(self.prompt(task))` is the number of items in `self.prompt(task)`.
- `return self.prices.estimate(tier, tokens) * calls`: ends the function and hands back `self.prices.estimate(tier, tokens) * calls`.

## Try it yourself

1. `wc -l src/cost_router/application/__init__.py src/cost_router/application/answer_checks.py src/cost_router/application/experiments.py` prints the line count of the first files; the tables above show the same numbers.
2. `.venv/bin/python -c "import cost_router.application.answer_checks; print('imports fine')"` prints `imports fine`.
3. `.venv/bin/lint-imports` ends with `Contracts: 2 kept, 0 broken.`
4. `.venv/bin/python -m pytest tests/unit -q -k application | tail -3` runs the tests that exercise this layer and ends with a line such as `N passed`.
5. `grep -c "^def \|^class \|^    def " src/cost_router/application/answer_checks.py` counts the functions and classes in the first file.

## Mistakes people make

- Importing an adapter (HTTP, files) instead of the port.
- Reading the clock or the environment directly; they arrive as arguments.
- Long functions that mix computing and writing files; the writing belongs in the infrastructure layer.
- Forgetting that the same code must also run offline from fixtures.
- Letting one experiment call another experiment's private helpers.

## Check yourself

1. **What is a port?**  
   A protocol that lists the methods the application needs from the outside world.
2. **Why does the application layer not import adapters?**  
   So it can run on fakes and recordings, and stay free of vendor code.
3. **Who connects ports to adapters?**  
   The wiring in the interfaces layer.
4. **What does an experiment function return?**  
   A record of results that the report code turns into files and tables.
5. **How can a test replace a model?**  
   By passing a scripted fake that implements the same port.

## Further reading

The Python language reference: https://docs.python.org/3/reference/ and the tutorial https://docs.python.org/3/tutorial/ (both for Python 3.13; the project accepts 3.12 or newer).
