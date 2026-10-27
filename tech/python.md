# Python 3.13

## What it is

Python is a programming language that is read and run by a program called the **interpreter**. You write text files ending in `.py`; the interpreter reads one statement at a time, builds objects in memory and runs functions. Libraries are collections of ready-made code that a program loads with `import`. A **module** is one `.py` file; a **package** is a folder of modules with an `__init__.py`.

## Why this repository uses it

All the experiments, the command-line program, the tests and the web service in this repository are Python. The code is split into four layers (`domain`, `application`, `infrastructure`, `interfaces`) so that the plain rules can be read and tested without any network, file or vendor library; `import-linter.md` shows how that is enforced. Version: 3.13 (the Docker images and CI use 3.13.1 / 3.13; the project accepts 3.12 or newer, see `requires-python`).

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/cost_router/domain/*.py (9 files)` | Plain data and rules; imports only the standard library. |
| `src/cost_router/application/*.py (8 files)` | The steps of the experiments, written against protocols (`ports.py`). |
| `src/cost_router/infrastructure/**/*.py (6 files)` | Adapters: files, HTTP, processes, models. |
| `src/cost_router/interfaces/*.py (3 files)` | The command line (`cli.py`) and the wiring that connects the layers. |
| `tests/**/*.py (16 files)` | Tests (`pytest.md`). |
| `pyproject.toml` | Declares the Python version and the libraries (`toml.md`). |


## How it works underneath

**Running.** `python file.py` makes the interpreter compile the file to *bytecode* (simple instructions for a virtual machine) and execute it. `python -m package.module` runs a module found through the import system. An `import x` finds `x.py` or a folder `x/` on `sys.path`, runs it once, and keeps the resulting module object.

**Objects and names.** Everything is an object (numbers, text, functions, classes). A name such as `request` is a label pointing at an object, not a box holding it. Assigning one name to another makes two labels on the same object. Lists and dictionaries can be changed in place; text, numbers and tuples cannot.

**Types.** Python decides types while the program runs. Annotations (`x: int`) are only hints that tools such as mypy read (`mypy.md`). Common types: `int`, `float`, `str`, `bool`, `list`, `tuple`, `dict`, `set`, `None` (nothing).

**Functions and classes.** `def f(a, b=1):` defines a function with an optional argument. A `class` defines a new kind of object; `self` is the object on which a method was called. A **protocol** is a class that lists methods, and any object with those methods fits it, with no inheritance needed; this repository uses protocols to describe what the application needs (the chat model, the clock).

**Errors.** `raise ValueError("...")` stops normal flow; the nearest `try: ... except ValueError:` above catches it. A `with` statement runs set-up and clean-up around a block (files and thread pools are closed when the block ends).

**Comprehensions and f-strings.** `[f(x) for x in xs if cond]` builds a list. `f"{value:.3f}"` inserts a value with three decimals.

## Walkthrough of this repository's use

### All modules

| File | What it does (first sentence of its docstring) |
| --- | --- |
| `src/cost_router/application/answer_checks.py` | The checks the router runs on an answer (no gold answer is visible to them). |
| `src/cost_router/application/experiments.py` | The lesson's steps as functions over the tier, check and router objects. |
| `src/cost_router/application/ports.py` | Ports: what the application needs from the outside world, written as protocols. |
| `src/cost_router/application/report_md.py` | The human-readable report: plain tables built from the stored results. |
| `src/cost_router/application/router.py` | The cost-aware router: cheapest tier first, a check after every answer, escalation on a failed check. |
| `src/cost_router/application/templates.py` | Prompt templates use `{{name}}` placeholders; rendering fails loudly on a missing value or a leftover. |
| `src/cost_router/application/tiers.py` | The three model tiers: building each task's prompt, calling the tier's model, and costing the call. |
| `src/cost_router/domain/checks.py` | Parsing a model's answer, grading it against the gold answer (what is true), and the checks the router can run without the gold answer (what it can see). |
| `src/cost_router/domain/llm.py` | Value types for talking to a chat model. |
| `src/cost_router/domain/metrics.py` | Accuracy, cost per correct answer, and false-accept and false-reject rates. |
| `src/cost_router/domain/pricing.py` | The dated price table. |
| `src/cost_router/domain/routing.py` | Router configuration, the daily budget and the records a routing decision leaves. |
| `src/cost_router/domain/signals.py` | The difficulty signal the router can see before it calls any model: two order ids, or an exception word. |
| `src/cost_router/domain/stats.py` | Small, dependency-free statistics: percentiles, Wilson intervals and a seeded paired bootstrap. |
| `src/cost_router/domain/tasks.py` | The tasks the router serves, the policy text they refer to, and the arithmetic that fixes the refund answers. |
| `src/cost_router/infrastructure/clock.py` | Clocks: the real one, and a manual one for tests and simulations. |
| `src/cost_router/infrastructure/data.py` | Reading the task set, the bars, the price table and the router configuration. |
| `src/cost_router/infrastructure/env.py` | Validated reads from the process environment (twelve-factor configuration). |
| `src/cost_router/infrastructure/llm/anthropic.py` | An adapter for the Anthropic Messages API, over plain HTTP. |
| `src/cost_router/infrastructure/llm/factory.py` | Choose a chat-model adapter from the environment: recorded (the default, offline), a local OpenAI-compatible server, a hosted OpenAI-compatible provider, or Anthropic. |
| `src/cost_router/infrastructure/llm/openai_compat.py` | An adapter for any server that speaks the OpenAI chat-completions protocol (a local ollama or llama.cpp server, or a hosted provider). |
| `src/cost_router/infrastructure/llm/recorded.py` | The recorded adapter replays real responses from JSONL fixtures; the recording adapter writes them. |
| `src/cost_router/infrastructure/llm/retry.py` | Retry with exponential backoff and jitter, for adapters that call a network. |
| `src/cost_router/infrastructure/logging_setup.py` | Structured logging: one JSON object per line on standard error, never prompt or reply text at info level. |
| `src/cost_router/infrastructure/parallel.py` | Run independent jobs on a few threads, keeping the input order of the results. |
| `src/cost_router/infrastructure/prompts.py` | Prompt templates read from versioned files under prompts/. |
| `src/cost_router/infrastructure/reports.py` | Writing reports as JSON, JSONL and Markdown with stable key order and rounded floats. |
| `src/cost_router/infrastructure/settings.py` | Settings from the environment, validated once at start-up. |
| `src/cost_router/interfaces/cli.py` | Command-line entry point: one program, one sub-command per step of the lesson. |
| `src/cost_router/interfaces/wiring.py` | The composition root: build the adapters and services from settings. |

### The shared building blocks, line by line

The six repositories share a small set of modules. They are the best place to see the language in use. The same text appears in every repository (only the package name differs).

#### Chat value types

`src/cost_router/domain/llm.py`

<!-- fmt: off -->
```python
"""Value types for talking to a chat model.

Nothing here knows about a vendor, an SDK or HTTP: adapters in the infrastructure layer translate these
types to and from a provider's wire format.
"""
```
<!-- fmt: on -->

The first statement of a file, a string in triple quotes, is the **module docstring**: documentation that Python keeps and tools can show. The ruff rule `D100` (`ruff.md`) requires one in every module.

<!-- fmt: off -->
```python
from __future__ import annotations

import hashlib
from dataclasses import dataclass
```
<!-- fmt: on -->

Switches on a behavior of newer Python for this file: type annotations are stored as text and not evaluated while the file loads. This lets annotations mention classes defined later in the file and use the short form `X | None`. Then two imports: `hashlib` (a module of the standard library, see `sha-256.md`) and the name `dataclass` from the `dataclasses` module.

<!-- fmt: off -->
```python
ROLES = frozenset({"system", "user", "assistant"})
```
<!-- fmt: on -->

A module-level constant (upper case by convention). `frozenset({...})` is a set that cannot be changed after creation; testing `x in ROLES` is fast. The three roles are the speakers of a chat: `system` (instructions), `user`, `assistant` (the model).

<!-- fmt: off -->
```python
class ModelError(Exception):
    """Base class for every failure of a model call."""


class RetryableModelError(ModelError):
    """A failure that a second attempt may fix: a timeout, a 5xx, a rate limit, a dropped connection."""


class PermanentModelError(ModelError):
    """A failure that a retry cannot fix: a malformed request, a bad key, an unknown model."""
```
<!-- fmt: on -->

A **class** groups data and functions. `class RetryableModelError(ModelError)` means *inherits from*: it is a kind of `ModelError`. An `except ModelError` handler therefore catches all three. The only statement in each is a docstring, which is enough for a class body. These classes name the two kinds of failure the program cares about: worth retrying, and not worth retrying.

<!-- fmt: off -->
```python
class FixtureMissError(PermanentModelError):
    """The recorded adapter has no response for this exact request (re-record with `make record`)."""
```
<!-- fmt: on -->

A third kind of permanent failure: the recorded adapter (`chat-model-apis.md`) was asked for an answer it never recorded.

<!-- fmt: off -->
```python
@dataclass(frozen=True)
class Message:
    """One chat message."""

    role: str
    content: str

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ValueError(f"unknown role {self.role!r}; expected one of {sorted(ROLES)}")
```
<!-- fmt: on -->

`@dataclass` is a **decorator**: a function applied to the class below it. It reads the annotated fields (`role: str`) and writes `__init__`, `__repr__` and `__eq__` for you. `frozen=True` makes instances read-only: assigning to a field after creation raises an error, so a message cannot change after it was checked. `__post_init__` runs right after the generated `__init__`; it raises `ValueError` for a role outside `ROLES`. In the f-string, `{self.role!r}` inserts the value's `repr` (with quotes) and `sorted(ROLES)` lists the allowed roles.

<!-- fmt: off -->
```python
@dataclass(frozen=True)
class ChatRequest:
    """Everything that decides a model's answer: the model, the messages and the decoding settings."""

    model: str
    messages: tuple[Message, ...]
    temperature: float = 0.0
    max_tokens: int = 256
    seed: int | None = None
```
<!-- fmt: on -->

The request: model name, a **tuple** of messages (`tuple[Message, ...]` means any number of `Message` objects; tuples cannot be changed), and decoding settings with defaults (`temperature: float = 0.0` means the argument may be left out). `int | None` means an integer or `None` (no seed).

<!-- fmt: off -->
```python
    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("model must not be empty")
        if not self.messages:
            raise ValueError("a request needs at least one message")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
```
<!-- fmt: on -->

Validation as soon as the object exists. `not 0.0 <= self.temperature <= 2.0` uses a **chained comparison**: it is true when the value lies between 0 and 2. Every check raises `ValueError` with a message that says what is wrong, so a bad request fails at the place it was created and not later inside an HTTP call.

<!-- fmt: off -->
```python
    def fixture_key(self) -> str:
        """A stable hash of the request; the Java port computes the same string, so both read one fixture file."""
        parts = [
            self.model,
            f"{self.temperature:.3f}",
            str(self.max_tokens),
            "-" if self.seed is None else str(self.seed),
            *(f"{m.role}\x1f{m.content}" for m in self.messages),
        ]
        return hashlib.sha256("\x1e".join(parts).encode("utf-8")).hexdigest()
```
<!-- fmt: on -->

The fingerprint of the request, explained line by line in `sha-256.md`. Its result is the name under which a recorded answer is stored.

<!-- fmt: off -->
```python
    def system_text(self) -> str:
        """The system messages joined, or an empty string."""
        return "\n".join(m.content for m in self.messages if m.role == "system")
```
<!-- fmt: on -->

A **generator expression** (`m.content for m in ... if ...`) produces the content of every system message; `"\n".join(...)` glues the pieces with newlines, or gives an empty string if there is none.

<!-- fmt: off -->
```python
@dataclass(frozen=True)
class Usage:
    """Billed token counts as the provider reported them."""

    input_tokens: int
    output_tokens: int
```
<!-- fmt: on -->

Token counts as the provider billed them.

<!-- fmt: off -->
```python
    @property
    def total(self) -> int:
        """Input plus output tokens."""
        return self.input_tokens + self.output_tokens
```
<!-- fmt: on -->

`@property` lets `usage.total` be read like a field although it is computed.

<!-- fmt: off -->
```python
@dataclass(frozen=True)
class ChatResponse:
    """A completed model call."""

    text: str
    usage: Usage
    model: str
    finish_reason: str = "stop"
    latency_s: float = 0.0
```
<!-- fmt: on -->

A finished model call: the reply text, usage, the model that answered, why it stopped (`stop` = finished normally), and how long it took.

<!-- fmt: off -->
```python
@dataclass(frozen=True)
class Price:
    """Dollars per 1,000 tokens, from a dated price table."""

    input_per_1k: float
    output_per_1k: float
```
<!-- fmt: on -->

A price in dollars per 1,000 tokens, taken from a dated price table.

<!-- fmt: off -->
```python
    def cost(self, usage: Usage) -> float:
        """The cost of one call from its billed usage."""
        return usage.input_tokens / 1000 * self.input_per_1k + usage.output_tokens / 1000 * self.output_per_1k
```
<!-- fmt: on -->

Cost = input tokens divided by 1000 times the input price, plus the same for output. `/` is true division, so the result is a float.

<!-- fmt: off -->
```python
def estimate_tokens(text: str) -> int:
    """A rough token count (about four characters per token) for estimates made before a call."""
    return max(1, (len(text) + 3) // 4)
```
<!-- fmt: on -->

A rough count made before a call: about four characters per token. `(len(text) + 3) // 4` is integer division rounded up (`//` drops the fraction); `max(1, ...)` makes sure an empty text still counts as one.

#### Settings from the environment

`src/cost_router/infrastructure/env.py`

<!-- fmt: off -->
```python
"""Validated reads from the process environment (twelve-factor configuration)."""
```
<!-- fmt: on -->

Module docstring. *Twelve-factor configuration* means: settings come from the environment (`dotenv.md`).

<!-- fmt: off -->
```python
from __future__ import annotations

import os
from collections.abc import Mapping
```
<!-- fmt: on -->

As before; then `os` (operating-system services) and `Mapping`, the type of anything that behaves like a read-only dictionary.

<!-- fmt: off -->
```python
class ConfigError(ValueError):
    """An environment variable is missing or has an invalid value."""
```
<!-- fmt: on -->

One error type for every bad setting; it inherits from `ValueError`.

<!-- fmt: off -->
```python
def read_str(env: Mapping[str, str], name: str, default: str | None = None) -> str:
    """A non-empty string variable, or the default when it is unset."""
    value = env.get(name, "").strip()
    if value:
        return value
    if default is None:
        raise ConfigError(f"{name} is required")
    return default
```
<!-- fmt: on -->

Reads text. `env.get(name, "")` returns the value or an empty string; `.strip()` removes spaces at both ends. If there is a value, return it. If there is none and no default was given (`None`), raise: the setting is required. Otherwise return the default. The parameter `env` is a mapping passed in, so tests can supply a plain dictionary.

<!-- fmt: off -->
```python
def read_int(env: Mapping[str, str], name: str, default: int, minimum: int = 0) -> int:
    """An integer variable at or above a minimum."""
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as error:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from error
    if value < minimum:
        raise ConfigError(f"{name} must be at least {minimum}, got {value}")
    return value
```
<!-- fmt: on -->

Reads a whole number that must be at least `minimum`. An empty value gives the default. `int(raw)` raises `ValueError` for text such as `abc`; the `try`/`except` turns it into a `ConfigError` with a readable message, and `from error` keeps the original error attached as the cause.

<!-- fmt: off -->
```python
def read_float(env: Mapping[str, str], name: str, default: float, minimum: float = 0.0) -> float:
    """A float variable at or above a minimum."""
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError as error:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from error
    if value < minimum:
        raise ConfigError(f"{name} must be at least {minimum}, got {value}")
    return value
```
<!-- fmt: on -->

The same for decimal numbers.

<!-- fmt: off -->
```python
def process_env() -> Mapping[str, str]:
    """The real environment (a function so that tests can pass a dict instead)."""
    return os.environ
```
<!-- fmt: on -->

Returns the real environment (`os.environ`, a mapping of text to text). It is a function so that code can ask for it, and tests can pass a dictionary instead.

#### Mapping over items on threads

`src/cost_router/infrastructure/parallel.py`

<!-- fmt: off -->
```python
"""Run independent jobs on a few threads, keeping the input order of the results."""
```
<!-- fmt: on -->

Module docstring.

<!-- fmt: off -->
```python
from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar
```
<!-- fmt: on -->

Imports: `Callable` and `Sequence` are type names for functions and ordered collections; `ThreadPoolExecutor` runs functions on several threads (`concurrency.md`); `TypeVar` creates placeholder types.

<!-- fmt: off -->
```python
T = TypeVar("T")
R = TypeVar("R")
```
<!-- fmt: on -->

`T` and `R` are **type variables**: placeholders meaning "whatever the item type is" and "whatever the result type is". They let the type checker know that mapping a `str` function over a list of `int`s is an error.

<!-- fmt: off -->
```python
def thread_mapper(workers: int) -> Callable[[Callable[[T], R], Sequence[T]], list[R]]:
    """A mapper that uses `workers` threads (one means no threads at all)."""
```
<!-- fmt: on -->

A function that **returns a function**. `thread_mapper(4)` builds and returns `run`, which remembers `workers=4` (a *closure*). The long annotation says: takes a function and a sequence, gives a list.

<!-- fmt: off -->
```python
    def run(function: Callable[[T], R], items: Sequence[T]) -> list[R]:
        if workers <= 1:
            return [function(item) for item in items]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(function, items))
```
<!-- fmt: on -->

`run` applies `function` to every item. With one worker it is a plain list comprehension: no threads, simpler and deterministic. Otherwise a `ThreadPoolExecutor` is opened with a `with` block (it is closed, and all threads finished, when the block ends) and `pool.map` runs the function on the items in parallel but returns the results **in input order**.

<!-- fmt: off -->
```python
    return run
```
<!-- fmt: on -->

Hands back the inner function.

#### Clocks

`src/cost_router/infrastructure/clock.py`

<!-- fmt: off -->
```python
"""Clocks: the real one, and a manual one for tests and simulations."""
```
<!-- fmt: on -->

Module docstring: the real clock, and one for tests.

<!-- fmt: off -->
```python
from __future__ import annotations

import time
```
<!-- fmt: on -->

`time` is the standard-library module for clocks and sleeping.

<!-- fmt: off -->
```python
class SystemClock:
    """Wall time and real sleeping."""

    def monotonic(self) -> float:
        """Seconds from the monotonic clock."""
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        """Block for the given seconds."""
        if seconds > 0:
            time.sleep(seconds)
```
<!-- fmt: on -->

`time.monotonic()` returns seconds from a clock that never goes backward (unlike the wall clock, which can be reset); it is the right clock for measuring durations. `sleep` waits, and ignores zero or negative waits.

<!-- fmt: off -->
```python
class ManualClock:
    """A clock that only moves when told to; `sleep` advances it instead of waiting."""

    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def monotonic(self) -> float:
        """The current manual time."""
        return self._now
```
<!-- fmt: on -->

A clock for tests and simulations. `__init__` stores the start value in `self._now` (a leading underscore means *internal*); `monotonic` returns it.

<!-- fmt: off -->
```python
    def sleep(self, seconds: float) -> None:
        """Advance the manual time."""
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        """Move time forward."""
        if seconds < 0:
            raise ValueError("time cannot go backward")
        self._now += seconds
```
<!-- fmt: on -->

`sleep` does not wait: it **advances** the manual time, so a test of a retry with an 8-second delay finishes immediately. `advance` refuses to go backward.

#### Retry with backoff

`src/cost_router/infrastructure/llm/retry.py`

<!-- fmt: off -->
```python
"""Retry with exponential backoff and jitter, for adapters that call a network."""

from __future__ import annotations
```
<!-- fmt: on -->

Module docstring: *exponential backoff* means waiting longer after each failure; *jitter* adds randomness so many clients do not retry at the same moment.

<!-- fmt: off -->
```python
import random
from collections.abc import Callable

from cost_router.application.ports import Clock
from cost_router.domain.llm import RetryableModelError
```
<!-- fmt: on -->

Imports `random` and `Callable`, and two names from this project: the `Clock` protocol and the retryable error.

<!-- fmt: off -->
```python
def retry_call[T](
    operation: Callable[[], T],
    *,
    attempts: int,
    clock: Clock,
    base_delay_s: float = 0.5,
    max_delay_s: float = 8.0,
    rng: random.Random | None = None,
) -> T:
    """Run `operation`, retrying only RetryableModelError with backoff and full-range jitter (50% to 100%)."""
```
<!-- fmt: on -->

`retry_call[T]` is Python 3.12 generic syntax: `T` is the type of whatever `operation` returns, and the function returns the same type. The bare `*` makes everything after it **keyword-only**: callers must write `attempts=3`, which prevents mixing up arguments. `rng` can be supplied by tests to make the jitter predictable.

<!-- fmt: off -->
```python
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
```
<!-- fmt: on -->

Refuses nonsense input first.

<!-- fmt: off -->
```python
    jitter = rng or random.Random()
```
<!-- fmt: on -->

Uses the supplied random generator or makes a new one. `x or y` yields `y` when `x` is `None`.

<!-- fmt: off -->
```python
    for attempt in range(attempts):
        try:
            return operation()
        except RetryableModelError:
            if attempt == attempts - 1:
                raise
            clock.sleep(min(max_delay_s, base_delay_s * 2**attempt) * jitter.uniform(0.5, 1.0))
```
<!-- fmt: on -->

Try up to `attempts` times. A success returns at once. Only `RetryableModelError` is caught; any other error leaves the loop immediately. On the last attempt the error is raised again (`raise` alone re-raises it). Otherwise the clock sleeps for `min(max_delay_s, base_delay_s * 2**attempt)` seconds (0.5, 1, 2, 4, 8 and then 8, since `**` is the power operator) multiplied by a random number between 0.5 and 1.0.

<!-- fmt: off -->
```python
    raise AssertionError("unreachable")  # pragma: no cover
```
<!-- fmt: on -->

Code that cannot be reached; `# pragma: no cover` tells coverage (`coverage-py.md`) not to count it.

#### JSON logging

`src/cost_router/infrastructure/logging_setup.py`

<!-- fmt: off -->
```python
"""Structured logging: one JSON object per line on standard error, never prompt or reply text at info level."""
```
<!-- fmt: on -->

Module docstring: each log record becomes one JSON object (`json.md`), which a program can search, and prompt or reply text is never logged at info level.

<!-- fmt: off -->
```python
from __future__ import annotations

import json
import logging
import sys
from typing import Any
```
<!-- fmt: on -->

Imports: `json`, `logging` (the standard logging library), `sys`, and `Any` (a type that disables checking).

<!-- fmt: off -->
```python
_RESERVED = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message", "asctime"}
```
<!-- fmt: on -->

The names every log record already has (made by building a dummy record), plus two more. Anything else on a record came from the caller's `extra=` argument and should appear in the output.

<!-- fmt: off -->
```python
class JsonFormatter(logging.Formatter):
    """Format a record as a single JSON line with its `extra` fields included."""

    def format(self, record: logging.LogRecord) -> str:
        """Render the record."""
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        payload.update({k: v for k, v in record.__dict__.items() if k not in _RESERVED})
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, sort_keys=True)
```
<!-- fmt: on -->

A formatter turns a record into text. This one builds a dictionary: a timestamp, the level, the logger name, the message. `payload.update({...})` adds the extra fields; `exc_info` adds a formatted exception. `json.dumps(..., default=str, sort_keys=True)` writes it as one line; `default=str` converts values JSON cannot represent, and sorted keys make output stable.

<!-- fmt: off -->
```python
def configure_logging(level: str = "INFO") -> None:
    """Install the JSON formatter on the root logger (idempotent)."""
    root = logging.getLogger()
    root.setLevel(level.upper())
    for handler in list(root.handlers):
        if getattr(handler, "_json_handler", False):
            root.removeHandler(handler)
    handler = logging.StreamHandler(sys.stderr)
    handler._json_handler = True  # type: ignore[attr-defined]
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    logging.getLogger("httpx").setLevel(logging.WARNING)
```
<!-- fmt: on -->

Sets the minimum level on the root logger, removes any handler this function added before (so calling it twice does not print every line twice), adds a stream handler that writes to **standard error** with the JSON formatter, and quiets the `httpx` library (`httpx.md`) to warnings. `# type: ignore[attr-defined]` tells mypy (`mypy.md`) that setting a private marker attribute on the handler is intended.

## Try it yourself

1. `.venv/bin/python --version` prints the version, for example `Python 3.13.x`.
2. `.venv/bin/python -c "from cost_router.domain.llm import Message; print(Message('user', 'hi'))"` prints `Message(role='user', content='hi')`, the `__repr__` that `@dataclass` wrote.
3. `.venv/bin/python -c "from cost_router.domain.llm import Message; Message('robot', 'hi')"` ends with `ValueError: unknown role 'robot'; expected one of ['assistant', 'system', 'user']`.
4. `.venv/bin/python -c "from cost_router.domain.llm import Message; m = Message('user','x'); m.content = 'y'"` ends with `dataclasses.FrozenInstanceError: cannot assign to field 'content'`.
5. `.venv/bin/python -c "from cost_router.infrastructure.env import read_int; print(read_int({'N': '5'}, 'N', 1), read_int({}, 'N', 1))"` prints `5 1`.

## Mistakes people make

- **Changing a list while looping over it.** Build a new list instead.
- **A mutable default argument** (`def f(x=[])`): the same list is shared by every call. Use `None` and create the list inside.
- **Catching `Exception` and doing nothing.** Errors then vanish. This repository catches the specific errors it can handle.
- **Comparing floats with `==`.** Use a tolerance.
- **Confusing `is` and `==`.** `==` compares values, `is` compares identity; use `is` only for `None`.
- **Importing inside the wrong layer.** The inner layers must not import vendor libraries; `lint-imports` checks it.

## Check yourself

1. **What does `@dataclass(frozen=True)` give you?**  
   A class with a generated constructor, `repr` and equality whose instances cannot be changed after creation.
2. **What is the difference between a list and a tuple?**  
   A list can be changed in place; a tuple cannot.
3. **What does `except RetryableModelError:` catch?**  
   That error and every error class that inherits from it, but no other error.
4. **Why does `ManualClock.sleep` not wait?**  
   It advances the manual time instead, so tests of delays run instantly.
5. **What does the bare `*` in a parameter list do?**  
   Everything after it must be passed by keyword, e.g. `attempts=3`.

## Further reading

Python tutorial and library reference: https://docs.python.org/3/ . Language reference for dataclasses: https://docs.python.org/3/library/dataclasses.html . PEP 695 (generic syntax): https://peps.python.org/pep-0695/
