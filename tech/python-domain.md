# Python code: the domain layer, file by file

## What it is

The **domain layer**: the plain data types and rules of this lesson, written with nothing but the Python standard library. No file, no network, no vendor library is touched here, so every function can be tested by calling it.

## Why this repository uses it

Keeping the rules apart from the plumbing means a reader can learn the idea of the lesson (what is measured, what counts as a pass) without meeting HTTP, databases or model servers, and the tests of this layer need no set-up. `import-linter` enforces the separation (`import-linter.md`).

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/cost_router/__init__.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/domain/__init__.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/domain/checks.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/domain/llm.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/domain/metrics.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/domain/pricing.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/domain/routing.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/domain/signals.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/domain/stats.py` | Quoted and explained in the walkthrough below. |
| `src/cost_router/domain/tasks.py` | Quoted and explained in the walkthrough below. |


## How it works underneath

Pure functions and frozen data classes. Given the same input they give the same output and change nothing outside themselves. That makes them easy to reason about and to test with a handful of values. Frozen dataclasses (`python.md`) cannot be changed after creation, so a value that was checked stays valid. The package root file `__init__.py` is also listed here.

## Walkthrough of this repository's use

### Files in this note

| File | Lines | What it is |
| --- | --- | --- |
| `src/cost_router/__init__.py` | 1 | ai cost aware router package. |
| `src/cost_router/domain/__init__.py` | 1 | The domain layer. |
| `src/cost_router/domain/checks.py` | 118 | Parsing a model's answer, grading it against the gold answer (what is true), and the checks the router can run without the gold answer (what it can see). |
| `src/cost_router/domain/llm.py` | 117 | Value types for talking to a chat model. |
| `src/cost_router/domain/metrics.py` | 100 | Accuracy, cost per correct answer, and false-accept and false-reject rates. |
| `src/cost_router/domain/pricing.py` | 30 | The dated price table. |
| `src/cost_router/domain/routing.py` | 78 | Router configuration, the daily budget and the records a routing decision leaves. |
| `src/cost_router/domain/signals.py` | 11 | The difficulty signal the router can see before it calls any model: two order ids, or an exception word. |
| `src/cost_router/domain/stats.py` | 97 | Small, dependency-free statistics: percentiles, Wilson intervals and a seeded paired bootstrap. |
| `src/cost_router/domain/tasks.py` | 87 | The tasks the router serves, the policy text they refer to, and the arithmetic that fixes the refund answers. |

Each file below is quoted exactly, in order, in pieces of about a dozen lines. Under each piece, a bullet list explains every statement in the order it appears. The first time an idea shows up in this note it is explained in a bullet that begins **New idea**.

#### `src/cost_router/__init__.py`

<!-- fmt: off -->
```python
"""ai cost aware router package."""
```
<!-- fmt: on -->

- **New idea.** A **docstring** is a text in triple quotes as the first statement of a module, class or function. Python keeps it as documentation and tools can show it.
- `"""ai cost aware router package."""`: a docstring (documentation text). It says: "ai cost aware router package."

#### `src/cost_router/domain/__init__.py`

<!-- fmt: off -->
```python
"""The domain layer."""
```
<!-- fmt: on -->

- `"""The domain layer."""`: a docstring (documentation text). It says: "The domain layer."

#### `src/cost_router/domain/checks.py`

<!-- fmt: off -->
```python
"""Parsing a model's answer, grading it against the gold answer (what is true), and the checks the router can run
without the gold answer (what it can see).

A grader answers "was it right?" and is used only to measure. A check answers "may the router accept this?" and is
what the router uses; the lesson's point is that the two can disagree.
"""

from __future__ import annotations

import re

from cost_router.domain.tasks import LABELS, POLICY_LINES, Kind, Task, expected_refund_cents

NUMBER = r"\$?\s*(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{1,2}))?"
```
<!-- fmt: on -->

- `"""Parsing a model's answer, grading it against the gold answer (what is true), and the...`: a docstring (documentation text). It says: "Parsing a model's answer, grading it against the gold answer (what is true), and the checks the router can run without the gold answer (what it can see)."
- **New idea.** `from __future__ import annotations` turns on a newer behaviour: type annotations are stored as text instead of being evaluated when the file loads.
- **New idea.** An **import** makes the code of another module available. `import x` gives the whole module under the name `x`; `from x import y` gives just the name `y`.
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import re`: imports the module(s) `re` so this file can use them. `re` is regular expressions.
- `from cost_router.domain.tasks import LABELS, POLICY_LINES, Kind, Task, expected_refund_...`: takes the name(s) `LABELS, POLICY_LINES, Kind, Task, expected_refund_cents` from the module `cost_router.domain.tasks` (a module of this project).
- **New idea.** An **assignment** `name = value` makes the name point at the value. A name written in capital letters is, by convention, a constant: it is not meant to change.
- `NUMBER = r"\$?\s*(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{1,2}))?"`: sets `NUMBER` to the constant `'\\$?\\s*(\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.(\\d{1,2`.

<!-- fmt: off -->
```python
REFUND_LINE = re.compile(r"refund\s*:\s*" + NUMBER, re.IGNORECASE)
BARE_AMOUNT = re.compile(NUMBER)
QUOTE = re.compile(r"quote\s*:\s*[\"“']?(.+?)[\"”']?\s*$", re.IGNORECASE | re.MULTILINE)


def normalize(text: str) -> str:
    """Lower case, collapsed spaces, no trailing full stop."""
    return " ".join(text.lower().split()).rstrip(".").strip()


def parse_label(text: str) -> str | None:
    """The answer as one of the allowed labels, or None (anything else, however close, is not a label)."""
    word = normalize(text).strip("\"'`*")
    return word if word in LABELS else None
```
<!-- fmt: on -->

- `REFUND_LINE = re.compile(r"refund\s*:\s*" + NUMBER, re.IGNORECASE)`: sets `REFUND_LINE` to the value of `re.compile('refund\\s*:\\s*' + NUMBER, re.IGNORECASE)`. `re.compile('refund\\s*:\\s*' + NUMBER, re.IGNORECASE)` is the pattern `'refund\\s*:\\s*' + NUMBER` prepared for repeated use.
- `BARE_AMOUNT = re.compile(NUMBER)`: sets `BARE_AMOUNT` to the value of `re.compile(NUMBER)`. `re.compile(NUMBER)` is the pattern `NUMBER` prepared for repeated use.
- `QUOTE = re.compile(r"quote\s*:\s*[\"“']?(.+?)[\"”']?\s*$", re.IGNORECASE | re.MULTILINE)`: sets `QUOTE` to a prepared regular expression (every pattern is explained piece by piece in `regular-expressions.md`). `re.compile('quote\\s*:\\s*[\\"“\']?(.+?)[\\"”\']?\\s*$', re.IGNOREC...` is the pattern `'quote\\s*:\\s*[\\"“\']?(.+?)[\\"”\']?\\s*$'` prepared for repeated use.
- **New idea.** A **function** is a named block of code. `def name(a, b):` defines it; the indented lines are its body. Calling `name(1, 2)` runs the body with `a = 1` and `b = 2`. `return` hands a value back. A parameter written `b=3` has a **default**: it may be left out when calling.
- `def normalize(text: str) -> str:`: defines the function `normalize` taking text (str) and returns `str`. Purpose: Lower case, collapsed spaces, no trailing full stop.
- `"""Lower case, collapsed spaces, no trailing full stop."""`: a docstring (documentation text). It says: "Lower case, collapsed spaces, no trailing full stop."
- **New idea.** `return value` ends the function and hands the value to the caller. A function that reaches its end without `return` gives back `None` (nothing).
- `return " ".join(text.lower().split()).rstrip(".").strip()`: ends the function and hands back `' '.join(text.lower().split()).rstrip('.').strip()`. `' '.join(text.lower().split()).rstrip('.').strip()` is `' '.join(text.lower().split()).rstrip...` without white space at both ends; `' '.join(text.lower().split()).rstrip('.')` is `' '.join(text.lower().split())` without the given characters at the end; `' '.join(text.lower().split())` is the items of `text.lower().split()` joined into one text with `' '` between them.
- `def parse_label(text: str) -> str | None:`: defines the function `parse_label` taking text (str) and returns `str | None`. Purpose: The answer as one of the allowed labels, or None (anything else, however close, is not a label).
- `"""The answer as one of the allowed labels, or None (anything else, however close, is n...`: a docstring (documentation text). It says: "The answer as one of the allowed labels, or None (anything else, however close, is not a label)."
- `word = normalize(text).strip("\"''*")`: sets `word` to the value of `normalize(text).strip('"\''*')`. `normalize(text).strip('"\''*')` is `normalize(text)` without white space at both ends.
- `return word if word in LABELS else None`: ends the function and hands back `word if word in LABELS else None`. `word if word in LABELS else None` gives `word` when `word in LABELS` is true, otherwise `None`.

<!-- fmt: off -->
```python
def _cents(match: re.Match[str]) -> int:
    dollars = int(match.group(1).replace(",", ""))
    return dollars * 100 + int(((match.group(2) or "") + "00")[:2])


def parse_amount_cents(text: str) -> int | None:
    """The amount of the answer's last `Refund:` line, or the whole answer when it is just an amount; else None."""
    matches = list(REFUND_LINE.finditer(text))
    if matches:
        return _cents(matches[-1])
    bare = BARE_AMOUNT.fullmatch(text.strip())
    return _cents(bare) if bare else None
```
<!-- fmt: on -->

- `def _cents(match: re.Match[str]) -> int:`: defines the function `_cents` taking match (re.Match[str]) and returns `int`.
- `dollars = int(match.group(1).replace(",", ""))`: sets `dollars` to the value of `int(match.group(1).replace(',', ''))`. `int(match.group(1).replace(',', ''))` is `match.group(1).replace(',', '')` converted to a whole number; `match.group(1).replace(',', '')` is `match.group(1)` with `','` replaced by `''`; `match.group(1)` is the part of the match that matched group `1`.
- `return dollars * 100 + int(((match.group(2) or "") + "00")[:2])`: ends the function and hands back `dollars * 100 + int(((match.group(2) or '') + '00')[:2])`. `int(((match.group(2) or '') + '00')[:2])` is `((match.group(2) or '') + '00')[:2]` converted to a whole number; `((match.group(2) or '') + '00')[:2]` is a slice (a part) of `(match.group(2) or '') + '00'`; `match.group(2)` is the part of the match that matched group `2`.
- `def parse_amount_cents(text: str) -> int | None:`: defines the function `parse_amount_cents` taking text (str) and returns `int | None`. Purpose: The amount of the answer's last `Refund:` line, or the whole answer when it is just an amount; else None.
- `"""The amount of the answer's last 'Refund:' line, or the whole answer when it is just ...`: a docstring (documentation text). It says: "The amount of the answer's last `Refund:` line, or the whole answer when it is just an amount; else None."
- `matches = list(REFUND_LINE.finditer(text))`: sets `matches` to the value of `list(REFUND_LINE.finditer(text))`. `list(REFUND_LINE.finditer(text))` is `REFUND_LINE.finditer(text)` copied into a list; `REFUND_LINE.finditer(text)` is an iterator over all matches.
- **New idea.** An **if** statement runs its indented block only when the condition is true. `elif` adds another condition to try; `else` runs when none held.
- `if matches:`: runs the block below only if `matches` is true.
- `return _cents(matches[-1])`: ends the function and hands back `_cents(matches[-1])`.
- `bare = BARE_AMOUNT.fullmatch(text.strip())`: sets `bare` to the value of `BARE_AMOUNT.fullmatch(text.strip())`. `BARE_AMOUNT.fullmatch(text.strip())` is a match of the whole text; `text.strip()` is `text` without white space at both ends.
- `return _cents(bare) if bare else None`: ends the function and hands back `_cents(bare) if bare else None`. `_cents(bare) if bare else None` gives `_cents(bare)` when `bare` is true, otherwise `None`.

<!-- fmt: off -->
```python
def parse_quote(text: str) -> str | None:
    """The line the answer quotes (the first `Quote:` line), or None."""
    match = QUOTE.search(text)
    return normalize(match.group(1)) if match else None


def quoted_line_index(text: str) -> int | None:
    """Which policy line the quote is, or None when the quote is not an exact policy line."""
    quote = parse_quote(text)
    if quote is None:
        return None
    for index, line in enumerate(POLICY_LINES):
        if normalize(line) == quote:
            return index
```
<!-- fmt: on -->

- `def parse_quote(text: str) -> str | None:`: defines the function `parse_quote` taking text (str) and returns `str | None`. Purpose: The line the answer quotes (the first `Quote:` line), or None.
- `"""The line the answer quotes (the first 'Quote:' line), or None."""`: a docstring (documentation text). It says: "The line the answer quotes (the first `Quote:` line), or None."
- `match = QUOTE.search(text)`: sets `match` to the value of `QUOTE.search(text)`. `QUOTE.search(text)` is the first place where `text` matches in the text.
- `return normalize(match.group(1)) if match else None`: ends the function and hands back `normalize(match.group(1)) if match else None`. `normalize(match.group(1)) if match else None` gives `normalize(match.group(1))` when `match` is true, otherwise `None`; `match.group(1)` is the part of the match that matched group `1`.
- `def quoted_line_index(text: str) -> int | None:`: defines the function `quoted_line_index` taking text (str) and returns `int | None`. Purpose: Which policy line the quote is, or None when the quote is not an exact policy line.
- `"""Which policy line the quote is, or None when the quote is not an exact policy line."""`: a docstring (documentation text). It says: "Which policy line the quote is, or None when the quote is not an exact policy line."
- `quote = parse_quote(text)`: sets `quote` to the value of `parse_quote(text)`.
- `if quote is None:`: runs the block below only if `quote is None` is true. `quote is None` tests that there is nothing (`None`) in `quote`.
- `return None`: ends the function and hands back `None`.
- **New idea.** A **for loop** `for x in items:` runs its block once for each item, with `x` naming the current item. `break` leaves the loop early; `continue` skips to the next item.
- `for index, line in enumerate(POLICY_LINES):`: repeats the block below once for each `(index, line)` in `enumerate(POLICY_LINES)`. `enumerate(POLICY_LINES)` is pairs (position, item) for the items of `POLICY_LINES`.
- `if normalize(line) == quote:`: runs the block below only if `normalize(line) == quote` is true.
- `return index`: ends the function and hands back `index`.

<!-- fmt: off -->
```python
    return None


def is_correct(task: Task, text: str) -> bool:
    """The ground truth: did the model get this task right?"""
    if task.kind is Kind.LABEL:
        return parse_label(text) == task.gold
    if task.kind is Kind.REFUND:
        return parse_amount_cents(text) == expected_refund_cents(task)
    return quoted_line_index(text) == task.gold


def check_label_shape(text: str) -> bool:
    """Shape only: the answer is one of the allowed labels."""
```
<!-- fmt: on -->

- `return None`: ends the function and hands back `None`.
- `def is_correct(task: Task, text: str) -> bool:`: defines the function `is_correct` taking task (Task); text (str) and returns `bool`. Purpose: The ground truth: did the model get this task right?
- `"""The ground truth: did the model get this task right?"""`: a docstring (documentation text). It says: "The ground truth: did the model get this task right?"
- `if task.kind is Kind.LABEL:`: runs the block below only if `task.kind is Kind.LABEL` is true.
- `return parse_label(text) == task.gold`: ends the function and hands back `parse_label(text) == task.gold`.
- `if task.kind is Kind.REFUND:`: runs the block below only if `task.kind is Kind.REFUND` is true.
- `return parse_amount_cents(text) == expected_refund_cents(task)`: ends the function and hands back `parse_amount_cents(text) == expected_refund_cents(task)`.
- `return quoted_line_index(text) == task.gold`: ends the function and hands back `quoted_line_index(text) == task.gold`.
- `def check_label_shape(text: str) -> bool:`: defines the function `check_label_shape` taking text (str) and returns `bool`. Purpose: Shape only: the answer is one of the allowed labels.
- `"""Shape only: the answer is one of the allowed labels."""`: a docstring (documentation text). It says: "Shape only: the answer is one of the allowed labels."

<!-- fmt: off -->
```python
    return parse_label(text) is not None


def check_label_agreement(text: str, second: str) -> bool:
    """Shape, and a second sample (another temperature and seed) gave the same label."""
    first_label = parse_label(text)
    return first_label is not None and first_label == parse_label(second)


def check_refund(task: Task, text: str) -> bool:
    """The amount equals the one recomputed by code from the order and the policy."""
    return parse_amount_cents(text) == expected_refund_cents(task)
```
<!-- fmt: on -->

- `return parse_label(text) is not None`: ends the function and hands back `parse_label(text) is not None`. `parse_label(text) is not None` tests that there is something in `parse_label(text)`.
- `def check_label_agreement(text: str, second: str) -> bool:`: defines the function `check_label_agreement` taking text (str); second (str) and returns `bool`. Purpose: Shape, and a second sample (another temperature and seed) gave the same label.
- `"""Shape, and a second sample (another temperature and seed) gave the same label."""`: a docstring (documentation text). It says: "Shape, and a second sample (another temperature and seed) gave the same label."
- `first_label = parse_label(text)`: sets `first_label` to the value of `parse_label(text)`.
- `return first_label is not None and first_label == parse_label(second)`: ends the function and hands back `first_label is not None and first_label == parse_label(second)`. `first_label is not None` tests that there is something in `first_label`.
- `def check_refund(task: Task, text: str) -> bool:`: defines the function `check_refund` taking task (Task); text (str) and returns `bool`. Purpose: The amount equals the one recomputed by code from the order and the policy.
- `"""The amount equals the one recomputed by code from the order and the policy."""`: a docstring (documentation text). It says: "The amount equals the one recomputed by code from the order and the policy."
- `return parse_amount_cents(text) == expected_refund_cents(task)`: ends the function and hands back `parse_amount_cents(text) == expected_refund_cents(task)`.

<!-- fmt: off -->
```python
STOPWORDS = frozenset(
    {
        *("a", "an", "the", "of", "to", "in", "on", "for", "is", "are", "be", "do", "does", "can", "i", "my", "me"),
        *("you", "your", "we", "our", "it", "its", "if", "or", "and", "at", "by", "from", "with", "as", "how", "what"),
        *("when", "who", "which", "that", "this", "there", "than", "then"),
    }
)


def content_words(text: str) -> set[str]:
    """Lower-case words of a text without the common function words, with a plural `s` removed."""
    words = (w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS)
    return {w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words}
```
<!-- fmt: on -->

- `STOPWORDS = frozenset(`: sets `STOPWORDS` to the value of `frozenset({*('a', 'an', 'the', 'of', 'to', 'in', 'on', 'for', 'is', 'are', 'b...`. `frozenset({*('a', 'an', 'the', 'of', 'to', 'in', 'on', 'for', 'is',...` is `{*('a', 'an', 'the', 'of', 'to', 'in', 'on', 'for', 'is',...` as an unchangeable set; `*('a', 'an', 'the', 'of', 'to', 'in', 'on', 'fo...` spreads the items of `('a', 'an', 'the', 'of', 't...` into separate values; `*('you', 'your', 'we', 'our', 'it', 'its', 'if'...` spreads the items of `('you', 'your', 'we', 'our'...` into separate values.
- `def content_words(text: str) -> set[str]:`: defines the function `content_words` taking text (str) and returns `set[str]`. Purpose: Lower-case words of a text without the common function words, with a plural `s` removed.
- `"""Lower-case words of a text without the common function words, with a plural 's' remo...`: a docstring (documentation text). It says: "Lower-case words of a text without the common function words, with a plural `s` removed."
- `words = (w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS)`: sets `words` to the value of `(w for w in re.findall('[a-z0-9]+', text.lower()) if w not in STOPWORDS)`. `(w for w in re.findall('[a-z0-9]+', text.lower()) if w not in STOPW...` builds a generator of values: for each `w` in `re.findall('[a-z0-9]+', text.lower())`, keeping only those for which `w not in STOPWORDS` is true; `re.findall('[a-z0-9]+', text.lower())` is all matches of `'[a-z0-9]+'` in `text.lower()`; `text.lower()` is `text` in lower case.
- `return {w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words}`: ends the function and hands back `{w[:-1] if len(w) > 3 and w.endswith('s') else w for w in words}`. `{w[:-1] if len(w) > 3 and w.endswith('s') else w for w in words}` builds a set: for each `w` in `words`; `w[:-1] if len(w) > 3 and w.endswith('s') else w` gives `w[:-1]` when `len(w) > 3 and w.endswith('s')` is true, otherwise `w`; `w[:-1]` is a slice (a part) of `w`.

<!-- fmt: off -->
```python
def best_matching_line(question: str) -> int | None:
    """The policy line sharing the most content words with the question, or None when two lines tie for most."""
    words = content_words(question)
    scores = [len(words & content_words(line)) for line in POLICY_LINES]
    top = max(scores)
    return scores.index(top) if top > 0 and scores.count(top) == 1 else None


def check_policy_overlap(question: str, text: str) -> bool:
    """Stronger than `check_policy`: the quoted line must also be the line that best matches the question's words."""
    index = quoted_line_index(text)
    return index is not None and index == best_matching_line(question)
```
<!-- fmt: on -->

- `def best_matching_line(question: str) -> int | None:`: defines the function `best_matching_line` taking question (str) and returns `int | None`. Purpose: The policy line sharing the most content words with the question, or None when two lines tie for most.
- `"""The policy line sharing the most content words with the question, or None when two l...`: a docstring (documentation text). It says: "The policy line sharing the most content words with the question, or None when two lines tie for most."
- `words = content_words(question)`: sets `words` to the value of `content_words(question)`.
- `scores = [len(words & content_words(line)) for line in POLICY_LINES]`: sets `scores` to the value of `[len(words & content_words(line)) for line in POLICY_LINES]`. `[len(words & content_words(line)) for line in POLICY_LINES]` builds a list: for each `line` in `POLICY_LINES`; `len(words & content_words(line))` is the number of items in `words & content_words(line)`.
- `top = max(scores)`: sets `top` to the value of `max(scores)`. `max(scores)` is the largest of `scores`.
- `return scores.index(top) if top > 0 and scores.count(top) == 1 else None`: ends the function and hands back `scores.index(top) if top > 0 and scores.count(top) == 1 else None`. `scores.index(top) if top > 0 and scores.count(top) == 1 else None` gives `scores.index(top)` when `top > 0 and scores.count(top) == 1` is true, otherwise `None`; `scores.index(top)` is the position of `top` in `scores`; `scores.count(top)` is how many times `top` occurs in `scores`.
- `def check_policy_overlap(question: str, text: str) -> bool:`: defines the function `check_policy_overlap` taking question (str); text (str) and returns `bool`. Purpose: Stronger than `check_policy`: the quoted line must also be the line that best matches the question's words.
- `"""Stronger than 'check_policy': the quoted line must also be the line that best matche...`: a docstring (documentation text). It says: "Stronger than `check_policy`: the quoted line must also be the line that best matches the question's words."
- `index = quoted_line_index(text)`: sets `index` to the value of `quoted_line_index(text)`.
- `return index is not None and index == best_matching_line(question)`: ends the function and hands back `index is not None and index == best_matching_line(question)`. `index is not None` tests that there is something in `index`.

<!-- fmt: off -->
```python
def check_policy(text: str) -> bool:
    """The answer quotes a policy line that exists (it does not say the line is the right one)."""
    return quoted_line_index(text) is not None
```
<!-- fmt: on -->

- `def check_policy(text: str) -> bool:`: defines the function `check_policy` taking text (str) and returns `bool`. Purpose: The answer quotes a policy line that exists (it does not say the line is the right one).
- `"""The answer quotes a policy line that exists (it does not say the line is the right o...`: a docstring (documentation text). It says: "The answer quotes a policy line that exists (it does not say the line is the right one)."
- `return quoted_line_index(text) is not None`: ends the function and hands back `quoted_line_index(text) is not None`. `quoted_line_index(text) is not None` tests that there is something in `quoted_line_index(text)`.

#### `src/cost_router/domain/llm.py`

<!-- fmt: off -->
```python
"""Value types for talking to a chat model.

Nothing here knows about a vendor, an SDK or HTTP: adapters in the infrastructure layer translate these
types to and from a provider's wire format.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

ROLES = frozenset({"system", "user", "assistant"})
```
<!-- fmt: on -->

- `"""Value types for talking to a chat model.`: a docstring (documentation text). It says: "Value types for talking to a chat model."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import hashlib`: imports the module(s) `hashlib` so this file can use them. `hashlib` is hash functions such as SHA-256.
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `ROLES = frozenset({"system", "user", "assistant"})`: sets `ROLES` to the value of `frozenset({'system', 'user', 'assistant'})`. `frozenset({'system', 'user', 'assistant'})` is `{'system', 'user', 'assistant'}` as an unchangeable set.

<!-- fmt: off -->
```python
class ModelError(Exception):
    """Base class for every failure of a model call."""


class RetryableModelError(ModelError):
    """A failure that a second attempt may fix: a timeout, a 5xx, a rate limit, a dropped connection."""


class PermanentModelError(ModelError):
    """A failure that a retry cannot fix: a malformed request, a bad key, an unknown model."""


class FixtureMissError(PermanentModelError):
    """The recorded adapter has no response for this exact request (re-record with `make record`)."""
```
<!-- fmt: on -->

- **New idea.** A **class** describes a kind of object: the data it holds and the methods that work on it. Calling the class, `Name(...)`, creates an object (an *instance*). `class B(A)` means B *inherits* from A: it has everything A has and may add or replace things.
- `class ModelError(Exception):`: defines the class `ModelError` that inherits from `Exception`. Purpose: Base class for every failure of a model call.
- `"""Base class for every failure of a model call."""`: a docstring (documentation text). It says: "Base class for every failure of a model call."
- `class RetryableModelError(ModelError):`: defines the class `RetryableModelError` that inherits from `ModelError`. Purpose: A failure that a second attempt may fix: a timeout, a 5xx, a rate limit, a dropped connection.
- `"""A failure that a second attempt may fix: a timeout, a 5xx, a rate limit, a dropped c...`: a docstring (documentation text). It says: "A failure that a second attempt may fix: a timeout, a 5xx, a rate limit, a dropped connection."
- `class PermanentModelError(ModelError):`: defines the class `PermanentModelError` that inherits from `ModelError`. Purpose: A failure that a retry cannot fix: a malformed request, a bad key, an unknown model.
- `"""A failure that a retry cannot fix: a malformed request, a bad key, an unknown model."""`: a docstring (documentation text). It says: "A failure that a retry cannot fix: a malformed request, a bad key, an unknown model."
- `class FixtureMissError(PermanentModelError):`: defines the class `FixtureMissError` that inherits from `PermanentModelError`. Purpose: The recorded adapter has no response for this exact request (re-record with `make record`).
- `"""The recorded adapter has no response for this exact request (re-record with 'make re...`: a docstring (documentation text). It says: "The recorded adapter has no response for this exact request (re-record with `make record`)."

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


@dataclass(frozen=True)
class ChatRequest:
```
<!-- fmt: on -->

- **New idea.** `@dataclass` is a **decorator** (a function applied to the class below it). It reads the annotated fields and writes `__init__`, `__repr__` and `__eq__` for you. `frozen=True` forbids changing a field after creation.
- `class Message:`: defines the class `Message`. Decorators: `dataclass(frozen=True)`. Purpose: One chat message.
- `"""One chat message."""`: a docstring (documentation text). It says: "One chat message."
- **New idea.** An **annotated assignment** `name: type = value` also says what kind of value the name should hold. The annotation is a hint for readers and for mypy (`mypy.md`); Python does not enforce it.
- `role: str`: declares a field of the class `role` of type `str` (no value yet).
- `content: str`: declares a field of the class `content` of type `str` (no value yet).
- **New idea.** A **method** is a function defined inside a class. Its first parameter, called `self`, is the object the method was called on, so `self.x` is that object's own attribute `x`.
- `def __post_init__(self) -> None:`: defines the method `__post_init__` taking no arguments and returns `None`.
- `if self.role not in ROLES:`: runs the block below only if `self.role not in ROLES` is true.
- **New idea.** `raise Error("message")` stops normal flow and signals an error. The nearest `except` that matches the type catches it; if none does, the program stops with the message. `raise ... from error` records the original error as the cause.
- `raise ValueError(f"unknown role {self.role!r}; expected one of {sorted(ROLES)}")`: signals an error, `ValueError(f'unknown role {self.role!r}; expected one of {sorted(ROLES)}')`; normal flow stops here and the nearest matching `except` takes over. `ValueError(f'unknown role {self.role!r}; expected one of {sorted(RO...` is a ValueError; the f-string inserts `self.role`, `sorted(ROLES)` into the text; `sorted(ROLES)` is `ROLES` in sorted order.
- `class ChatRequest:`: defines the class `ChatRequest`. Decorators: `dataclass(frozen=True)`. Purpose: Everything that decides a model's answer: the model, the messages and the decoding settings.

<!-- fmt: off -->
```python
    """Everything that decides a model's answer: the model, the messages and the decoding settings."""

    model: str
    messages: tuple[Message, ...]
    temperature: float = 0.0
    max_tokens: int = 256
    seed: int | None = None

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("model must not be empty")
        if not self.messages:
            raise ValueError("a request needs at least one message")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
```
<!-- fmt: on -->

- `"""Everything that decides a model's answer: the model, the messages and the decoding s...`: a docstring (documentation text). It says: "Everything that decides a model's answer: the model, the messages and the decoding settings."
- `model: str`: declares a field of the class `model` of type `str` (no value yet).
- `messages: tuple[Message, ...]`: declares a field of the class `messages` of type `tuple[Message, ...]` (no value yet).
- `temperature: float = 0.0`: declares a field of the class `temperature` of type `float` and sets it to `0.0`.
- `max_tokens: int = 256`: declares a field of the class `max_tokens` of type `int` and sets it to `256`.
- `seed: int | None = None`: declares a field of the class `seed` of type `int | None` and sets it to `None`.
- `def __post_init__(self) -> None:`: defines the method `__post_init__` taking no arguments and returns `None`.
- `if not self.model:`: runs the block below only if `not self.model` is true.
- `raise ValueError("model must not be empty")`: signals an error, `ValueError('model must not be empty')`; normal flow stops here and the nearest matching `except` takes over. `ValueError('model must not be empty')` is a ValueError.
- `if not self.messages:`: runs the block below only if `not self.messages` is true.
- `raise ValueError("a request needs at least one message")`: signals an error, `ValueError('a request needs at least one message')`; normal flow stops here and the nearest matching `except` takes over. `ValueError('a request needs at least one message')` is a ValueError.
- `if not 0.0 <= self.temperature <= 2.0:`: runs the block below only if `not 0.0 <= self.temperature <= 2.0` is true. `0.0 <= self.temperature <= 2.0` is a chained comparison: every part must hold.
- `raise ValueError("temperature must be between 0 and 2")`: signals an error, `ValueError('temperature must be between 0 and 2')`; normal flow stops here and the nearest matching `except` takes over. `ValueError('temperature must be between 0 and 2')` is a ValueError.

<!-- fmt: off -->
```python
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

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

- `if self.max_tokens <= 0:`: runs the block below only if `self.max_tokens <= 0` is true.
- `raise ValueError("max_tokens must be positive")`: signals an error, `ValueError('max_tokens must be positive')`; normal flow stops here and the nearest matching `except` takes over. `ValueError('max_tokens must be positive')` is a ValueError.
- `def fixture_key(self) -> str:`: defines the method `fixture_key` taking no arguments and returns `str`. Purpose: A stable hash of the request; the Java port computes the same string, so both read one fixture file.
- `"""A stable hash of the request; the Java port computes the same string, so both read o...`: a docstring (documentation text). It says: "A stable hash of the request; the Java port computes the same string, so both read one fixture file."
- `parts = [`: sets `parts` to a list of 5 items. the f-string inserts `self.temperature` into the text; `str(self.max_tokens)` is `self.max_tokens` converted to text; `'-' if self.seed is None else str(self.seed)` gives `'-'` when `self.seed is None` is true, otherwise `str(self.seed)`.
- `return hashlib.sha256("\x1e".join(parts).encode("utf-8")).hexdigest()`: ends the function and hands back `hashlib.sha256('\x1e'.join(parts).encode('utf-8')).hexdigest()`. `hashlib.sha256('\x1e'.join(parts).encode('utf-8')).hexdigest()` is the hash as hexadecimal text; `hashlib.sha256('\x1e'.join(parts).encode('utf-8'))` is a SHA-256 hash object of `'\x1e'.join(parts).encode('utf-8')`; `'\x1e'.join(parts).encode('utf-8')` is `'\x1e'.join(parts)` turned from text into bytes.

<!-- fmt: off -->
```python
    def system_text(self) -> str:
        """The system messages joined, or an empty string."""
        return "\n".join(m.content for m in self.messages if m.role == "system")


@dataclass(frozen=True)
class Usage:
    """Billed token counts as the provider reported them."""

    input_tokens: int
    output_tokens: int

    @property
    def total(self) -> int:
```
<!-- fmt: on -->

- `def system_text(self) -> str:`: defines the method `system_text` taking no arguments and returns `str`. Purpose: The system messages joined, or an empty string.
- `"""The system messages joined, or an empty string."""`: a docstring (documentation text). It says: "The system messages joined, or an empty string."
- `return "\n".join(m.content for m in self.messages if m.role == "system")`: ends the function and hands back `'\n'.join((m.content for m in self.messages if m.role == 'system'))`. `'\n'.join((m.content for m in self.messages if m.role == 'system'))` is the items of `(m.content for m in self.messages if m.role == 'system')` joined into one text with `'\n'` between them; `(m.content for m in self.messages if m.role == 'system')` builds a generator of values: for each `m` in `self.messages`, keeping only those for which `m.role == 'system'` is true.
- `class Usage:`: defines the class `Usage`. Decorators: `dataclass(frozen=True)`. Purpose: Billed token counts as the provider reported them.
- `"""Billed token counts as the provider reported them."""`: a docstring (documentation text). It says: "Billed token counts as the provider reported them."
- `input_tokens: int`: declares a field of the class `input_tokens` of type `int` (no value yet).
- `output_tokens: int`: declares a field of the class `output_tokens` of type `int` (no value yet).
- **New idea.** A **decorator** is a line `@name` above a function or class. It passes the function to `name` and uses what comes back instead. It is a way to add behaviour without editing the function.
- **New idea.** `@property` lets a method be read like an attribute, without brackets.
- `def total(self) -> int:`: defines the method `total` taking no arguments and returns `int`. Decorators: `property`. Purpose: Input plus output tokens.

<!-- fmt: off -->
```python
        """Input plus output tokens."""
        return self.input_tokens + self.output_tokens


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

- `"""Input plus output tokens."""`: a docstring (documentation text). It says: "Input plus output tokens."
- `return self.input_tokens + self.output_tokens`: ends the function and hands back `self.input_tokens + self.output_tokens`.
- `class ChatResponse:`: defines the class `ChatResponse`. Decorators: `dataclass(frozen=True)`. Purpose: A completed model call.
- `"""A completed model call."""`: a docstring (documentation text). It says: "A completed model call."
- `text: str`: declares a field of the class `text` of type `str` (no value yet).
- `usage: Usage`: declares a field of the class `usage` of type `Usage` (no value yet).
- `model: str`: declares a field of the class `model` of type `str` (no value yet).
- `finish_reason: str = "stop"`: declares a field of the class `finish_reason` of type `str` and sets it to `'stop'`.
- `latency_s: float = 0.0`: declares a field of the class `latency_s` of type `float` and sets it to `0.0`.

<!-- fmt: off -->
```python
@dataclass(frozen=True)
class Price:
    """Dollars per 1,000 tokens, from a dated price table."""

    input_per_1k: float
    output_per_1k: float

    def cost(self, usage: Usage) -> float:
        """The cost of one call from its billed usage."""
        return usage.input_tokens / 1000 * self.input_per_1k + usage.output_tokens / 1000 * self.output_per_1k


def estimate_tokens(text: str) -> int:
    """A rough token count (about four characters per token) for estimates made before a call."""
```
<!-- fmt: on -->

- `class Price:`: defines the class `Price`. Decorators: `dataclass(frozen=True)`. Purpose: Dollars per 1,000 tokens, from a dated price table.
- `"""Dollars per 1,000 tokens, from a dated price table."""`: a docstring (documentation text). It says: "Dollars per 1,000 tokens, from a dated price table."
- `input_per_1k: float`: declares a field of the class `input_per_1k` of type `float` (no value yet).
- `output_per_1k: float`: declares a field of the class `output_per_1k` of type `float` (no value yet).
- `def cost(self, usage: Usage) -> float:`: defines the method `cost` taking usage (Usage) and returns `float`. Purpose: The cost of one call from its billed usage.
- `"""The cost of one call from its billed usage."""`: a docstring (documentation text). It says: "The cost of one call from its billed usage."
- `return usage.input_tokens / 1000 * self.input_per_1k + usage.output_tokens / 1000 * sel...`: ends the function and hands back `usage.input_tokens / 1000 * self.input_per_1k + usage.output_tokens / 1000 * ...`.
- `def estimate_tokens(text: str) -> int:`: defines the function `estimate_tokens` taking text (str) and returns `int`. Purpose: A rough token count (about four characters per token) for estimates made before a call.
- `"""A rough token count (about four characters per token) for estimates made before a ca...`: a docstring (documentation text). It says: "A rough token count (about four characters per token) for estimates made before a call."

<!-- fmt: off -->
```python
    return max(1, (len(text) + 3) // 4)
```
<!-- fmt: on -->

- `return max(1, (len(text) + 3) // 4)`: ends the function and hands back `max(1, (len(text) + 3) // 4)`. `max(1, (len(text) + 3) // 4)` is the largest of `1`, `(len(text) + 3) // 4`; `len(text)` is the number of items in `text`.

#### `src/cost_router/domain/metrics.py`

<!-- fmt: off -->
```python
"""Accuracy, cost per correct answer, and false-accept and false-reject rates."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from cost_router.domain.stats import SplitMix64, wilson_interval


@dataclass(frozen=True)
class Rate:
    """A proportion with its Wilson interval."""
```
<!-- fmt: on -->

- `"""Accuracy, cost per correct answer, and false-accept and false-reject rates."""`: a docstring (documentation text). It says: "Accuracy, cost per correct answer, and false-accept and false-reject rates."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from collections.abc import Sequence`: takes the name(s) `Sequence` from the module `collections.abc` (abstract container types used in annotations).
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `from cost_router.domain.stats import SplitMix64, wilson_interval`: takes the name(s) `SplitMix64, wilson_interval` from the module `cost_router.domain.stats` (a module of this project).
- `class Rate:`: defines the class `Rate`. Decorators: `dataclass(frozen=True)`. Purpose: A proportion with its Wilson interval.
- `"""A proportion with its Wilson interval."""`: a docstring (documentation text). It says: "A proportion with its Wilson interval."

<!-- fmt: off -->
```python
    successes: int
    trials: int
    value: float
    low: float
    high: float


def rate(successes: int, trials: int) -> Rate:
    """A rate and its 95% Wilson interval; zero trials gives value 0 and the whole range."""
    low, high = wilson_interval(successes, trials)
    return Rate(successes, trials, successes / trials if trials else 0.0, low, high)


def cost_per_correct(total_cost: float, correct: int) -> float | None:
```
<!-- fmt: on -->

- `successes: int`: declares a field of the class `successes` of type `int` (no value yet).
- `trials: int`: declares a field of the class `trials` of type `int` (no value yet).
- `value: float`: declares a field of the class `value` of type `float` (no value yet).
- `low: float`: declares a field of the class `low` of type `float` (no value yet).
- `high: float`: declares a field of the class `high` of type `float` (no value yet).
- `def rate(successes: int, trials: int) -> Rate:`: defines the function `rate` taking successes (int); trials (int) and returns `Rate`. Purpose: A rate and its 95% Wilson interval; zero trials gives value 0 and the whole range.
- `"""A rate and its 95% Wilson interval; zero trials gives value 0 and the whole range."""`: a docstring (documentation text). It says: "A rate and its 95% Wilson interval; zero trials gives value 0 and the whole range."
- `low, high = wilson_interval(successes, trials)`: sets `(low, high)` to the value of `wilson_interval(successes, trials)`.
- `return Rate(successes, trials, successes / trials if trials else 0.0, low, high)`: ends the function and hands back `Rate(successes, trials, successes / trials if trials else 0.0, low, high)`. `successes / trials if trials else 0.0` gives `successes / trials` when `trials` is true, otherwise `0.0`.
- `def cost_per_correct(total_cost: float, correct: int) -> float | None:`: defines the function `cost_per_correct` taking total_cost (float); correct (int) and returns `float | None`. Purpose: Money spent divided by right answers; None when nothing was right.

<!-- fmt: off -->
```python
    """Money spent divided by right answers; None when nothing was right."""
    return total_cost / correct if correct else None


def bootstrap_cost_per_correct(
    costs: Sequence[float], corrects: Sequence[bool], resamples: int = 2000, seed: int = 7
) -> tuple[float, float]:
    """A 95% bootstrap interval for total cost over right answers, resampling whole tasks."""
    n = len(costs)
    if n == 0:
        return 0.0, 0.0
    rng = SplitMix64(seed)
    values: list[float] = []
    for _ in range(resamples):
```
<!-- fmt: on -->

- `"""Money spent divided by right answers; None when nothing was right."""`: a docstring (documentation text). It says: "Money spent divided by right answers; None when nothing was right."
- `return total_cost / correct if correct else None`: ends the function and hands back `total_cost / correct if correct else None`. `total_cost / correct if correct else None` gives `total_cost / correct` when `correct` is true, otherwise `None`.
- `def bootstrap_cost_per_correct(`: defines the function `bootstrap_cost_per_correct` taking costs (Sequence[float]); corrects (Sequence[bool]); resamples (int), default 2000; seed (int), default 7 and returns `tuple[float, float]`. Purpose: A 95% bootstrap interval for total cost over right answers, resampling whole tasks.
- `"""A 95% bootstrap interval for total cost over right answers, resampling whole tasks."""`: a docstring (documentation text). It says: "A 95% bootstrap interval for total cost over right answers, resampling whole tasks."
- `n = len(costs)`: sets `n` to the value of `len(costs)`. `len(costs)` is the number of items in `costs`.
- `if n == 0:`: runs the block below only if `n == 0` is true.
- `return 0.0, 0.0`: ends the function and hands back `(0.0, 0.0)`.
- `rng = SplitMix64(seed)`: sets `rng` to the value of `SplitMix64(seed)`.
- `values: list[float] = []`: declares a variable `values` of type `list[float]` and sets it to `[]`.
- `for _ in range(resamples):`: repeats the block below once for each `_` in `range(resamples)`. `range(resamples)` is the whole numbers from `0` up to, not including, `resamples`.

<!-- fmt: off -->
```python
        total = 0.0
        right = 0
        for _ in range(n):
            i = rng.below(n)
            total += costs[i]
            right += corrects[i]
        values.append(total / right if right else float("inf"))
    values.sort()
    return values[int(0.025 * resamples)], values[min(resamples - 1, int(0.975 * resamples))]


def bootstrap_accuracy_difference(
    a: Sequence[bool], b: Sequence[bool], resamples: int = 2000, seed: int = 7
) -> tuple[float, float, float]:
```
<!-- fmt: on -->

- `total = 0.0`: sets `total` to the constant `0.0`.
- `right = 0`: sets `right` to the constant `0`.
- `for _ in range(n):`: repeats the block below once for each `_` in `range(n)`. `range(n)` is the whole numbers from `0` up to, not including, `n`.
- `i = rng.below(n)`: sets `i` to the value of `rng.below(n)`.
- **New idea.** An **augmented assignment** such as `x += 1` changes the value in place: it means `x = x + 1`.
- `total += costs[i]`: adds `costs[i]` to `total` and stores the result back.
- `right += corrects[i]`: adds `corrects[i]` to `right` and stores the result back.
- `values.append(total / right if right else float("inf"))`: runs `values.append(total / right if right else float('inf'))` for its effect and ignores the result. `values.append(total / right if right else float('inf'))` adds `total / right if right else float('inf')` to the end of `values`; `total / right if right else float('inf')` gives `total / right` when `right` is true, otherwise `float('inf')`; `float('inf')` is `'inf'` converted to a decimal number.
- `values.sort()`: runs `values.sort()` for its effect and ignores the result. `values.sort()` is sorts `values` in place.
- `return values[int(0.025 * resamples)], values[min(resamples - 1, int(0.975 * resamples))]`: ends the function and hands back `(values[int(0.025 * resamples)], values[min(resamples - 1, int(0.975 * resamp...`. `int(0.025 * resamples)` is `0.025 * resamples` converted to a whole number; `min(resamples - 1, int(0.975 * resamples))` is the smallest of `resamples - 1`, `int(0.975 * resamples)`; `int(0.975 * resamples)` is `0.975 * resamples` converted to a whole number.
- `def bootstrap_accuracy_difference(`: defines the function `bootstrap_accuracy_difference` taking a (Sequence[bool]); b (Sequence[bool]); resamples (int), default 2000; seed (int), default 7 and returns `tuple[float, float, float]`. Purpose: Mean of (a - b) over paired tasks and its 95% bootstrap interval.

<!-- fmt: off -->
```python
    """Mean of (a - b) over paired tasks and its 95% bootstrap interval."""
    if len(a) != len(b):
        raise ValueError("paired comparison needs equal lengths")
    n = len(a)
    if n == 0:
        return 0.0, 0.0, 0.0
    diffs = [float(x) - float(y) for x, y in zip(a, b, strict=True)]
    rng = SplitMix64(seed)
    means = sorted(sum(diffs[rng.below(n)] for _ in range(n)) / n for _ in range(resamples))
    return sum(diffs) / n, means[int(0.025 * resamples)], means[min(resamples - 1, int(0.975 * resamples))]


@dataclass(frozen=True)
class CheckRates:
```
<!-- fmt: on -->

- `"""Mean of (a - b) over paired tasks and its 95% bootstrap interval."""`: a docstring (documentation text). It says: "Mean of (a - b) over paired tasks and its 95% bootstrap interval."
- `if len(a) != len(b):`: runs the block below only if `len(a) != len(b)` is true. `len(a)` is the number of items in `a`; `len(b)` is the number of items in `b`.
- `raise ValueError("paired comparison needs equal lengths")`: signals an error, `ValueError('paired comparison needs equal lengths')`; normal flow stops here and the nearest matching `except` takes over. `ValueError('paired comparison needs equal lengths')` is a ValueError.
- `n = len(a)`: sets `n` to the value of `len(a)`. `len(a)` is the number of items in `a`.
- `if n == 0:`: runs the block below only if `n == 0` is true.
- `return 0.0, 0.0, 0.0`: ends the function and hands back `(0.0, 0.0, 0.0)`.
- `diffs = [float(x) - float(y) for x, y in zip(a, b, strict=True)]`: sets `diffs` to the value of `[float(x) - float(y) for x, y in zip(a, b, strict=True)]`. `[float(x) - float(y) for x, y in zip(a, b, strict=True)]` builds a list: for each `(x, y)` in `zip(a, b, strict=True)`; `float(x)` is `x` converted to a decimal number; `float(y)` is `y` converted to a decimal number.
- `rng = SplitMix64(seed)`: sets `rng` to the value of `SplitMix64(seed)`.
- `means = sorted(sum(diffs[rng.below(n)] for _ in range(n)) / n for _ in range(resamples))`: sets `means` to the value of `sorted((sum((diffs[rng.below(n)] for _ in range(n))) / n for _ in range(resam...`. `sorted((sum((diffs[rng.below(n)] for _ in range(n))) / n for _ in r...` is `(sum((diffs[rng.below(n)] for _ in range(n))) / n for _ i...` in sorted order; `(sum((diffs[rng.below(n)] for _ in range(n))) / n for _ in range(re...` builds a generator of values: for each `_` in `range(resamples)`; `sum((diffs[rng.below(n)] for _ in range(n)))` is the sum of `(diffs[rng.below(n)] for _ in range(n))`.
- `return sum(diffs) / n, means[int(0.025 * resamples)], means[min(resamples - 1, int(0.97...`: ends the function and hands back `(sum(diffs) / n, means[int(0.025 * resamples)], means[min(resamples - 1, int(...`. `sum(diffs)` is the sum of `diffs`; `int(0.025 * resamples)` is `0.025 * resamples` converted to a whole number; `min(resamples - 1, int(0.975 * resamples))` is the smallest of `resamples - 1`, `int(0.975 * resamples)`.
- `class CheckRates:`: defines the class `CheckRates`. Decorators: `dataclass(frozen=True)`. Purpose: How a check behaves against the ground truth.

<!-- fmt: off -->
```python
    """How a check behaves against the ground truth."""

    accepted: int
    wrong: int
    right: int
    false_accepts: int
    false_rejects: int
    false_accept_rate: float
    false_reject_rate: float
    wrong_among_accepted: float


def check_rates(passed: Sequence[bool], correct: Sequence[bool]) -> CheckRates:
    """False-accept rate = wrong answers accepted / wrong answers; false-reject rate = right answers rejected / right
    answers; wrong-among-accepted = accepted answers that are wrong / accepted answers."""
```
<!-- fmt: on -->

- `"""How a check behaves against the ground truth."""`: a docstring (documentation text). It says: "How a check behaves against the ground truth."
- `accepted: int`: declares a field of the class `accepted` of type `int` (no value yet).
- `wrong: int`: declares a field of the class `wrong` of type `int` (no value yet).
- `right: int`: declares a field of the class `right` of type `int` (no value yet).
- `false_accepts: int`: declares a field of the class `false_accepts` of type `int` (no value yet).
- `false_rejects: int`: declares a field of the class `false_rejects` of type `int` (no value yet).
- `false_accept_rate: float`: declares a field of the class `false_accept_rate` of type `float` (no value yet).
- `false_reject_rate: float`: declares a field of the class `false_reject_rate` of type `float` (no value yet).
- `wrong_among_accepted: float`: declares a field of the class `wrong_among_accepted` of type `float` (no value yet).
- `def check_rates(passed: Sequence[bool], correct: Sequence[bool]) -> CheckRates:`: defines the function `check_rates` taking passed (Sequence[bool]); correct (Sequence[bool]) and returns `CheckRates`. Purpose: False-accept rate = wrong answers accepted / wrong answers; false-reject rate = right answers rejected / right answers; wrong-among-accepted = accepted answers that are wrong / accepted answers.
- `"""False-accept rate = wrong answers accepted / wrong answers; false-reject rate = righ...`: a docstring (documentation text). It says: "False-accept rate = wrong answers accepted / wrong answers; false-reject rate = right answers rejected / right answers; wrong-among-accepted = accepted answers that are wrong / accepted answers."

<!-- fmt: off -->
```python
    accepted = sum(passed)
    wrong = sum(1 for c in correct if not c)
    right = len(correct) - wrong
    false_accepts = sum(1 for p, c in zip(passed, correct, strict=True) if p and not c)
    false_rejects = sum(1 for p, c in zip(passed, correct, strict=True) if not p and c)
    return CheckRates(
        accepted,
        wrong,
        right,
        false_accepts,
        false_rejects,
        false_accepts / wrong if wrong else 0.0,
        false_rejects / right if right else 0.0,
        false_accepts / accepted if accepted else 0.0,
    )
```
<!-- fmt: on -->

- `accepted = sum(passed)`: sets `accepted` to the value of `sum(passed)`. `sum(passed)` is the sum of `passed`.
- `wrong = sum(1 for c in correct if not c)`: sets `wrong` to the value of `sum((1 for c in correct if not c))`. `sum((1 for c in correct if not c))` is the sum of `(1 for c in correct if not c)`; `(1 for c in correct if not c)` builds a generator of values: for each `c` in `correct`, keeping only those for which `not c` is true.
- `right = len(correct) - wrong`: sets `right` to the value of `len(correct) - wrong`. `len(correct)` is the number of items in `correct`.
- `false_accepts = sum(1 for p, c in zip(passed, correct, strict=True) if p and not c)`: sets `false_accepts` to the value of `sum((1 for p, c in zip(passed, correct, strict=True) if p and (not c)))`. `sum((1 for p, c in zip(passed, correct, strict=True) if p and (not ...` is the sum of `(1 for p, c in zip(passed, correct, strict=True) if p and...`; `(1 for p, c in zip(passed, correct, strict=True) if p and (not c))` builds a generator of values: for each `(p, c)` in `zip(passed, correct, strict=True)`, keeping only those for which `p and (not c)` is true; `zip(passed, correct, strict=True)` is items of `passed`, `correct` taken together, position by position.
- `false_rejects = sum(1 for p, c in zip(passed, correct, strict=True) if not p and c)`: sets `false_rejects` to the value of `sum((1 for p, c in zip(passed, correct, strict=True) if not p and c))`. `sum((1 for p, c in zip(passed, correct, strict=True) if not p and c))` is the sum of `(1 for p, c in zip(passed, correct, strict=True) if not p...`; `(1 for p, c in zip(passed, correct, strict=True) if not p and c)` builds a generator of values: for each `(p, c)` in `zip(passed, correct, strict=True)`, keeping only those for which `not p and c` is true; `zip(passed, correct, strict=True)` is items of `passed`, `correct` taken together, position by position.
- `return CheckRates(`: ends the function and hands back `CheckRates(accepted, wrong, right, false_accepts, false_rejects, false_accept...`. `false_accepts / wrong if wrong else 0.0` gives `false_accepts / wrong` when `wrong` is true, otherwise `0.0`; `false_rejects / right if right else 0.0` gives `false_rejects / right` when `right` is true, otherwise `0.0`; `false_accepts / accepted if accepted else 0.0` gives `false_accepts / accepted` when `accepted` is true, otherwise `0.0`.

#### `src/cost_router/domain/pricing.py`

<!-- fmt: off -->
```python
"""The dated price table. Prices are per 1,000 billed tokens, input and output alike."""

from __future__ import annotations

from dataclasses import dataclass

from cost_router.domain.llm import Usage

TIERS = ("small", "medium", "large")


@dataclass(frozen=True)
class PriceTable:
    """Prices as of a date, so a number in a report can be traced to the table that produced it."""
```
<!-- fmt: on -->

- `"""The dated price table. Prices are per 1,000 billed tokens, input and output alike."""`: a docstring (documentation text). It says: "The dated price table."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `from cost_router.domain.llm import Usage`: takes the name(s) `Usage` from the module `cost_router.domain.llm` (a module of this project).
- `TIERS = ("small", "medium", "large")`: sets `TIERS` to a tuple of 3 items.
- `class PriceTable:`: defines the class `PriceTable`. Decorators: `dataclass(frozen=True)`. Purpose: Prices as of a date, so a number in a report can be traced to the table that produced it.
- `"""Prices as of a date, so a number in a report can be traced to the table that produce...`: a docstring (documentation text). It says: "Prices as of a date, so a number in a report can be traced to the table that produced it."

<!-- fmt: off -->
```python
    as_of: str
    per_1k_tokens: dict[str, float]

    def __post_init__(self) -> None:
        missing = [t for t in TIERS if t not in self.per_1k_tokens]
        if missing:
            raise ValueError(f"price table lacks tiers {missing}")

    def cost(self, tier: str, usage: Usage) -> float:
        """The cost of one call from its billed tokens."""
        return usage.total / 1000 * self.per_1k_tokens[tier]

    def estimate(self, tier: str, tokens: int) -> float:
        """The cost of a call of the given token count (used before the call, from an estimate)."""
```
<!-- fmt: on -->

- `as_of: str`: declares a field of the class `as_of` of type `str` (no value yet).
- `per_1k_tokens: dict[str, float]`: declares a field of the class `per_1k_tokens` of type `dict[str, float]` (no value yet).
- `def __post_init__(self) -> None:`: defines the method `__post_init__` taking no arguments and returns `None`.
- `missing = [t for t in TIERS if t not in self.per_1k_tokens]`: sets `missing` to the value of `[t for t in TIERS if t not in self.per_1k_tokens]`. `[t for t in TIERS if t not in self.per_1k_tokens]` builds a list: for each `t` in `TIERS`, keeping only those for which `t not in self.per_1k_tokens` is true.
- `if missing:`: runs the block below only if `missing` is true.
- `raise ValueError(f"price table lacks tiers {missing}")`: signals an error, `ValueError(f'price table lacks tiers {missing}')`; normal flow stops here and the nearest matching `except` takes over. `ValueError(f'price table lacks tiers {missing}')` is a ValueError; the f-string inserts `missing` into the text.
- `def cost(self, tier: str, usage: Usage) -> float:`: defines the method `cost` taking tier (str); usage (Usage) and returns `float`. Purpose: The cost of one call from its billed tokens.
- `"""The cost of one call from its billed tokens."""`: a docstring (documentation text). It says: "The cost of one call from its billed tokens."
- `return usage.total / 1000 * self.per_1k_tokens[tier]`: ends the function and hands back `usage.total / 1000 * self.per_1k_tokens[tier]`.
- `def estimate(self, tier: str, tokens: int) -> float:`: defines the method `estimate` taking tier (str); tokens (int) and returns `float`. Purpose: The cost of a call of the given token count (used before the call, from an estimate).
- `"""The cost of a call of the given token count (used before the call, from an estimate)...`: a docstring (documentation text). It says: "The cost of a call of the given token count (used before the call, from an estimate)."

<!-- fmt: off -->
```python
        return tokens / 1000 * self.per_1k_tokens[tier]
```
<!-- fmt: on -->

- `return tokens / 1000 * self.per_1k_tokens[tier]`: ends the function and hands back `tokens / 1000 * self.per_1k_tokens[tier]`.

#### `src/cost_router/domain/routing.py`

<!-- fmt: off -->
```python
"""Router configuration, the daily budget and the records a routing decision leaves."""

from __future__ import annotations

from dataclasses import dataclass, field

from cost_router.domain.pricing import TIERS


@dataclass(frozen=True)
class Bar:
    """Numbers agreed before any result was seen (config/bar.json)."""

    false_accept_bar: float
```
<!-- fmt: on -->

- `"""Router configuration, the daily budget and the records a routing decision leaves."""`: a docstring (documentation text). It says: "Router configuration, the daily budget and the records a routing decision leaves."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from dataclasses import dataclass, field`: takes the name(s) `dataclass, field` from the module `dataclasses` (classes that are mostly data).
- `from cost_router.domain.pricing import TIERS`: takes the name(s) `TIERS` from the module `cost_router.domain.pricing` (a module of this project).
- `class Bar:`: defines the class `Bar`. Decorators: `dataclass(frozen=True)`. Purpose: Numbers agreed before any result was seen (config/bar.json).
- `"""Numbers agreed before any result was seen (config/bar.json)."""`: a docstring (documentation text). It says: "Numbers agreed before any result was seen (config/bar.json)."
- `false_accept_bar: float`: declares a field of the class `false_accept_bar` of type `float` (no value yet).

<!-- fmt: off -->
```python
    hard_accuracy_bar: float
    accuracy_margin: float
    request_cap: float
    tighten_at: float
    day_budget_fractions: tuple[float, ...]


@dataclass(frozen=True)
class RouterConfig:
    """What the build set decided (config/router.json) plus the limits."""

    start: dict[str, str]
    hard_start: dict[str, str]
    label_check: str
```
<!-- fmt: on -->

- `hard_accuracy_bar: float`: declares a field of the class `hard_accuracy_bar` of type `float` (no value yet).
- `accuracy_margin: float`: declares a field of the class `accuracy_margin` of type `float` (no value yet).
- `request_cap: float`: declares a field of the class `request_cap` of type `float` (no value yet).
- `tighten_at: float`: declares a field of the class `tighten_at` of type `float` (no value yet).
- `day_budget_fractions: tuple[float, ...]`: declares a field of the class `day_budget_fractions` of type `tuple[float, ...]` (no value yet).
- `class RouterConfig:`: defines the class `RouterConfig`. Decorators: `dataclass(frozen=True)`. Purpose: What the build set decided (config/router.json) plus the limits.
- `"""What the build set decided (config/router.json) plus the limits."""`: a docstring (documentation text). It says: "What the build set decided (config/router.json) plus the limits."
- `start: dict[str, str]`: declares a field of the class `start` of type `dict[str, str]` (no value yet).
- `hard_start: dict[str, str]`: declares a field of the class `hard_start` of type `dict[str, str]` (no value yet).
- `label_check: str`: declares a field of the class `label_check` of type `str` (no value yet).

<!-- fmt: off -->
```python
    request_cap: float
    tighten_at: float
    policy_check: str = "quote"

    def start_index(self, kind: str, hard: bool) -> int:
        """The index in TIERS where this kind of task starts."""
        tier = self.hard_start.get(kind) if hard and self.hard_start.get(kind) else self.start[kind]
        return TIERS.index(tier)


class DayBudget:
    """The money spent so far against a daily budget."""

    def __init__(self, budget: float) -> None:
```
<!-- fmt: on -->

- `request_cap: float`: declares a field of the class `request_cap` of type `float` (no value yet).
- `tighten_at: float`: declares a field of the class `tighten_at` of type `float` (no value yet).
- `policy_check: str = "quote"`: declares a field of the class `policy_check` of type `str` and sets it to `'quote'`.
- `def start_index(self, kind: str, hard: bool) -> int:`: defines the method `start_index` taking kind (str); hard (bool) and returns `int`. Purpose: The index in TIERS where this kind of task starts.
- `"""The index in TIERS where this kind of task starts."""`: a docstring (documentation text). It says: "The index in TIERS where this kind of task starts."
- `tier = self.hard_start.get(kind) if hard and self.hard_start.get(kind) else self.start[...`: sets `tier` to the value of `self.hard_start.get(kind) if hard and self.hard_start.get(kind) else self.sta...`. `self.hard_start.get(kind) if hard and self.hard_start.get(kind) els...` gives `self.hard_start.get(kind)` when `hard and self.hard_start.get(kind)` is true, otherwise `self.start[kind]`; `self.hard_start.get(kind)` looks up `kind` in `self.hard_start` (default (nothing) when missing).
- `return TIERS.index(tier)`: ends the function and hands back `TIERS.index(tier)`. `TIERS.index(tier)` is the position of `tier` in `TIERS`.
- `class DayBudget:`: defines the class `DayBudget`. Purpose: The money spent so far against a daily budget.
- `"""The money spent so far against a daily budget."""`: a docstring (documentation text). It says: "The money spent so far against a daily budget."
- `def __init__(self, budget: float) -> None:`: defines the method `__init__` taking budget (float) and returns `None`.

<!-- fmt: off -->
```python
        if budget <= 0:
            raise ValueError("a budget must be positive")
        self.budget = budget
        self.used = 0.0

    def used_share(self) -> float:
        """Spent divided by budget."""
        return self.used / self.budget

    def add(self, amount: float) -> None:
        """Record spending."""
        self.used += amount
```
<!-- fmt: on -->

- `if budget <= 0:`: runs the block below only if `budget <= 0` is true.
- `raise ValueError("a budget must be positive")`: signals an error, `ValueError('a budget must be positive')`; normal flow stops here and the nearest matching `except` takes over. `ValueError('a budget must be positive')` is a ValueError.
- `self.budget = budget`: sets `self.budget` to the value of `budget`.
- `self.used = 0.0`: sets `self.used` to the constant `0.0`.
- `def used_share(self) -> float:`: defines the method `used_share` taking no arguments and returns `float`. Purpose: Spent divided by budget.
- `"""Spent divided by budget."""`: a docstring (documentation text). It says: "Spent divided by budget."
- `return self.used / self.budget`: ends the function and hands back `self.used / self.budget`.
- `def add(self, amount: float) -> None:`: defines the method `add` taking amount (float) and returns `None`. Purpose: Record spending.
- `"""Record spending."""`: a docstring (documentation text). It says: "Record spending."
- `self.used += amount`: adds `amount` to `self.used` and stores the result back.

<!-- fmt: off -->
```python
@dataclass(frozen=True)
class Attempt:
    """One tier tried for one task."""

    tier: str
    passed: bool
    cost: float
    tokens: int


@dataclass(frozen=True)
class Decision:
    """What the router did with one task. `served_by` is a tier name or `escalate_to_person`."""
```
<!-- fmt: on -->

- `class Attempt:`: defines the class `Attempt`. Decorators: `dataclass(frozen=True)`. Purpose: One tier tried for one task.
- `"""One tier tried for one task."""`: a docstring (documentation text). It says: "One tier tried for one task."
- `tier: str`: declares a field of the class `tier` of type `str` (no value yet).
- `passed: bool`: declares a field of the class `passed` of type `bool` (no value yet).
- `cost: float`: declares a field of the class `cost` of type `float` (no value yet).
- `tokens: int`: declares a field of the class `tokens` of type `int` (no value yet).
- `class Decision:`: defines the class `Decision`. Decorators: `dataclass(frozen=True)`. Purpose: What the router did with one task.
- `"""What the router did with one task. 'served_by' is a tier name or 'escalate_to_person...`: a docstring (documentation text). It says: "What the router did with one task."

<!-- fmt: off -->
```python
    task_id: str
    answer: str | None
    served_by: str
    attempts: tuple[Attempt, ...]
    spent: float
    tokens: int
    share_before: float = 0.0
    tags: tuple[str, ...] = field(default_factory=tuple)
```
<!-- fmt: on -->

- `task_id: str`: declares a field of the class `task_id` of type `str` (no value yet).
- `answer: str | None`: declares a field of the class `answer` of type `str | None` (no value yet).
- `served_by: str`: declares a field of the class `served_by` of type `str` (no value yet).
- `attempts: tuple[Attempt, ...]`: declares a field of the class `attempts` of type `tuple[Attempt, ...]` (no value yet).
- `spent: float`: declares a field of the class `spent` of type `float` (no value yet).
- `tokens: int`: declares a field of the class `tokens` of type `int` (no value yet).
- `share_before: float = 0.0`: declares a field of the class `share_before` of type `float` and sets it to `0.0`.
- `tags: tuple[str, ...] = field(default_factory=tuple)`: declares a field of the class `tags` of type `tuple[str, ...]` and sets it to `field(default_factory=tuple)`. `field(default_factory=tuple)` is options for a dataclass field.

#### `src/cost_router/domain/signals.py`

<!-- fmt: off -->
```python
"""The difficulty signal the router can see before it calls any model: two order ids, or an exception word."""

from __future__ import annotations

from cost_router.domain.tasks import EXCEPTION_WORDS, ORDER_ID, Task


def hard_signal(task: Task) -> bool:
    """True when the text mentions two or more order ids, or a damage or partial-return word."""
    lowered = task.text.lower()
    return len(set(ORDER_ID.findall(task.text))) >= 2 or any(word in lowered for word in EXCEPTION_WORDS)
```
<!-- fmt: on -->

- `"""The difficulty signal the router can see before it calls any model: two order ids, o...`: a docstring (documentation text). It says: "The difficulty signal the router can see before it calls any model: two order ids, or an exception word."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `from cost_router.domain.tasks import EXCEPTION_WORDS, ORDER_ID, Task`: takes the name(s) `EXCEPTION_WORDS, ORDER_ID, Task` from the module `cost_router.domain.tasks` (a module of this project).
- `def hard_signal(task: Task) -> bool:`: defines the function `hard_signal` taking task (Task) and returns `bool`. Purpose: True when the text mentions two or more order ids, or a damage or partial-return word.
- `"""True when the text mentions two or more order ids, or a damage or partial-return wor...`: a docstring (documentation text). It says: "True when the text mentions two or more order ids, or a damage or partial-return word."
- `lowered = task.text.lower()`: sets `lowered` to the value of `task.text.lower()`. `task.text.lower()` is `task.text` in lower case.
- `return len(set(ORDER_ID.findall(task.text))) >= 2 or any(word in lowered for word in EX...`: ends the function and hands back `len(set(ORDER_ID.findall(task.text))) >= 2 or any((word in lowered for word i...`. `any((word in lowered for word in EXCEPTION_WORDS))` is true if any item of `(word in lowered for word in EXCEPTION_WORDS)` is true; `len(set(ORDER_ID.findall(task.text)))` is the number of items in `set(ORDER_ID.findall(task.text))`; `(word in lowered for word in EXCEPTION_WORDS)` builds a generator of values: for each `word` in `EXCEPTION_WORDS`.

#### `src/cost_router/domain/stats.py`

<!-- fmt: off -->
```python
"""Small, dependency-free statistics: percentiles, Wilson intervals and a seeded paired bootstrap.

The random generator is a SplitMix64 written out here so that the Java port produces the same intervals
from the same seed.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

_MASK = (1 << 64) - 1
```
<!-- fmt: on -->

- `"""Small, dependency-free statistics: percentiles, Wilson intervals and a seeded paired...`: a docstring (documentation text). It says: "Small, dependency-free statistics: percentiles, Wilson intervals and a seeded paired bootstrap."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import math`: imports the module(s) `math` so this file can use them. `math` is mathematical functions.
- `from collections.abc import Sequence`: takes the name(s) `Sequence` from the module `collections.abc` (abstract container types used in annotations).
- `_MASK = (1 << 64) - 1`: sets `_MASK` to the value of `(1 << 64) - 1`.

<!-- fmt: off -->
```python
class SplitMix64:
    """A tiny deterministic generator (the same arithmetic in the Python and the Java code)."""

    def __init__(self, seed: int) -> None:
        self._state = seed & _MASK

    def next_u64(self) -> int:
        """The next 64-bit value."""
        self._state = (self._state + 0x9E3779B97F4A7C15) & _MASK
        z = self._state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
        return z ^ (z >> 31)
```
<!-- fmt: on -->

- `class SplitMix64:`: defines the class `SplitMix64`. Purpose: A tiny deterministic generator (the same arithmetic in the Python and the Java code).
- `"""A tiny deterministic generator (the same arithmetic in the Python and the Java code)...`: a docstring (documentation text). It says: "A tiny deterministic generator (the same arithmetic in the Python and the Java code)."
- `def __init__(self, seed: int) -> None:`: defines the method `__init__` taking seed (int) and returns `None`.
- `self._state = seed & _MASK`: sets `self._state` to the value of `seed & _MASK`.
- `def next_u64(self) -> int:`: defines the method `next_u64` taking no arguments and returns `int`. Purpose: The next 64-bit value.
- `"""The next 64-bit value."""`: a docstring (documentation text). It says: "The next 64-bit value."
- `self._state = (self._state + 0x9E3779B97F4A7C15) & _MASK`: sets `self._state` to the value of `self._state + 11400714819323198485 & _MASK`.
- `z = self._state`: sets `z` to the value of `self._state`.
- `z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK`: sets `z` to the value of `(z ^ z >> 30) * 13787848793156543929 & _MASK`.
- `z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK`: sets `z` to the value of `(z ^ z >> 27) * 10723151780598845931 & _MASK`.
- `return z ^ (z >> 31)`: ends the function and hands back `z ^ z >> 31`.

<!-- fmt: off -->
```python
    def below(self, bound: int) -> int:
        """A value in [0, bound). The modulo bias is negligible for the sizes used here."""
        if bound <= 0:
            raise ValueError("bound must be positive")
        return self.next_u64() % bound


def mean(values: Sequence[float]) -> float:
    """The arithmetic mean; zero for an empty sequence."""
    return sum(values) / len(values) if values else 0.0


def percentile(values: Sequence[float], q: float) -> float:
    """The q-th percentile (0 to 100) by linear interpolation between closest ranks; zero when empty."""
```
<!-- fmt: on -->

- `def below(self, bound: int) -> int:`: defines the method `below` taking bound (int) and returns `int`. Purpose: A value in [0, bound).
- `"""A value in [0, bound). The modulo bias is negligible for the sizes used here."""`: a docstring (documentation text). It says: "A value in [0, bound)."
- `if bound <= 0:`: runs the block below only if `bound <= 0` is true.
- `raise ValueError("bound must be positive")`: signals an error, `ValueError('bound must be positive')`; normal flow stops here and the nearest matching `except` takes over. `ValueError('bound must be positive')` is a ValueError.
- `return self.next_u64() % bound`: ends the function and hands back `self.next_u64() % bound`.
- `def mean(values: Sequence[float]) -> float:`: defines the function `mean` taking values (Sequence[float]) and returns `float`. Purpose: The arithmetic mean; zero for an empty sequence.
- `"""The arithmetic mean; zero for an empty sequence."""`: a docstring (documentation text). It says: "The arithmetic mean; zero for an empty sequence."
- `return sum(values) / len(values) if values else 0.0`: ends the function and hands back `sum(values) / len(values) if values else 0.0`. `sum(values) / len(values) if values else 0.0` gives `sum(values) / len(values)` when `values` is true, otherwise `0.0`; `sum(values)` is the sum of `values`; `len(values)` is the number of items in `values`.
- `def percentile(values: Sequence[float], q: float) -> float:`: defines the function `percentile` taking values (Sequence[float]); q (float) and returns `float`. Purpose: The q-th percentile (0 to 100) by linear interpolation between closest ranks; zero when empty.
- `"""The q-th percentile (0 to 100) by linear interpolation between closest ranks; zero w...`: a docstring (documentation text). It says: "The q-th percentile (0 to 100) by linear interpolation between closest ranks; zero when empty."

<!-- fmt: off -->
```python
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q / 100.0
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
```
<!-- fmt: on -->

- `if not values:`: runs the block below only if `not values` is true.
- `return 0.0`: ends the function and hands back `0.0`.
- `ordered = sorted(values)`: sets `ordered` to the value of `sorted(values)`. `sorted(values)` is `values` in sorted order.
- `if len(ordered) == 1:`: runs the block below only if `len(ordered) == 1` is true. `len(ordered)` is the number of items in `ordered`.
- `return ordered[0]`: ends the function and hands back `ordered[0]`.
- `position = (len(ordered) - 1) * q / 100.0`: sets `position` to the value of `(len(ordered) - 1) * q / 100.0`. `len(ordered)` is the number of items in `ordered`.
- `low = math.floor(position)`: sets `low` to the value of `math.floor(position)`. `math.floor(position)` is `position` rounded down.
- `high = math.ceil(position)`: sets `high` to the value of `math.ceil(position)`. `math.ceil(position)` is `position` rounded up.
- `if low == high:`: runs the block below only if `low == high` is true.
- `return ordered[low]`: ends the function and hands back `ordered[low]`.
- `return ordered[low] + (ordered[high] - ordered[low]) * (position - low)`: ends the function and hands back `ordered[low] + (ordered[high] - ordered[low]) * (position - low)`.
- `def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:`: defines the function `wilson_interval` taking successes (int); trials (int); z (float), default 1.96 and returns `tuple[float, float]`. Purpose: The Wilson score interval for a proportion; (0, 1) when there are no trials.

<!-- fmt: off -->
```python
    """The Wilson score interval for a proportion; (0, 1) when there are no trials."""
    if trials <= 0:
        return 0.0, 1.0
    p = successes / trials
    denominator = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denominator
    margin = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator
    return max(0.0, centre - margin), min(1.0, centre + margin)


def bootstrap_mean_interval(
    values: Sequence[float], resamples: int = 2000, seed: int = 7, level: float = 0.95
) -> tuple[float, float]:
    """A percentile bootstrap interval for the mean of per-item values."""
```
<!-- fmt: on -->

- `"""The Wilson score interval for a proportion; (0, 1) when there are no trials."""`: a docstring (documentation text). It says: "The Wilson score interval for a proportion; (0, 1) when there are no trials."
- `if trials <= 0:`: runs the block below only if `trials <= 0` is true.
- `return 0.0, 1.0`: ends the function and hands back `(0.0, 1.0)`.
- `p = successes / trials`: sets `p` to the value of `successes / trials`.
- `denominator = 1 + z * z / trials`: sets `denominator` to the value of `1 + z * z / trials`.
- `centre = (p + z * z / (2 * trials)) / denominator`: sets `centre` to the value of `(p + z * z / (2 * trials)) / denominator`.
- `margin = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator`: sets `margin` to the value of `z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denomin...`. `math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials))` is the square root of `p * (1 - p) / trials + z * z / (4 * trials * trials)`.
- `return max(0.0, centre - margin), min(1.0, centre + margin)`: ends the function and hands back `(max(0.0, centre - margin), min(1.0, centre + margin))`. `max(0.0, centre - margin)` is the largest of `0.0`, `centre - margin`; `min(1.0, centre + margin)` is the smallest of `1.0`, `centre + margin`.
- `def bootstrap_mean_interval(`: defines the function `bootstrap_mean_interval` taking values (Sequence[float]); resamples (int), default 2000; seed (int), default 7; level (float), default 0.95 and returns `tuple[float, float]`. Purpose: A percentile bootstrap interval for the mean of per-item values.
- `"""A percentile bootstrap interval for the mean of per-item values."""`: a docstring (documentation text). It says: "A percentile bootstrap interval for the mean of per-item values."

<!-- fmt: off -->
```python
    if not values:
        return 0.0, 0.0
    rng = SplitMix64(seed)
    n = len(values)
    means = sorted(sum(values[rng.below(n)] for _ in range(n)) / n for _ in range(resamples))
    tail = (1 - level) / 2
    return means[int(tail * resamples)], means[min(resamples - 1, int((1 - tail) * resamples))]


def paired_bootstrap_difference(
    treatment: Sequence[float], control: Sequence[float], resamples: int = 2000, seed: int = 7, level: float = 0.95
) -> tuple[float, tuple[float, float]]:
    """The mean of (treatment - control) over paired items and its percentile bootstrap interval."""
    if len(treatment) != len(control):
```
<!-- fmt: on -->

- `if not values:`: runs the block below only if `not values` is true.
- `return 0.0, 0.0`: ends the function and hands back `(0.0, 0.0)`.
- `rng = SplitMix64(seed)`: sets `rng` to the value of `SplitMix64(seed)`.
- `n = len(values)`: sets `n` to the value of `len(values)`. `len(values)` is the number of items in `values`.
- `means = sorted(sum(values[rng.below(n)] for _ in range(n)) / n for _ in range(resamples))`: sets `means` to the value of `sorted((sum((values[rng.below(n)] for _ in range(n))) / n for _ in range(resa...`. `sorted((sum((values[rng.below(n)] for _ in range(n))) / n for _ in ...` is `(sum((values[rng.below(n)] for _ in range(n))) / n for _ ...` in sorted order; `(sum((values[rng.below(n)] for _ in range(n))) / n for _ in range(r...` builds a generator of values: for each `_` in `range(resamples)`; `sum((values[rng.below(n)] for _ in range(n)))` is the sum of `(values[rng.below(n)] for _ in range(n))`.
- `tail = (1 - level) / 2`: sets `tail` to the value of `(1 - level) / 2`.
- `return means[int(tail * resamples)], means[min(resamples - 1, int((1 - tail) * resample...`: ends the function and hands back `(means[int(tail * resamples)], means[min(resamples - 1, int((1 - tail) * resa...`. `int(tail * resamples)` is `tail * resamples` converted to a whole number; `min(resamples - 1, int((1 - tail) * resamples))` is the smallest of `resamples - 1`, `int((1 - tail) * resamples)`; `int((1 - tail) * resamples)` is `(1 - tail) * resamples` converted to a whole number.
- `def paired_bootstrap_difference(`: defines the function `paired_bootstrap_difference` taking treatment (Sequence[float]); control (Sequence[float]); resamples (int), default 2000; seed (int), default 7; level (float), default 0.95 and returns `tuple[float, tuple[float, float]]`. Purpose: The mean of (treatment - control) over paired items and its percentile bootstrap interval.
- `"""The mean of (treatment - control) over paired items and its percentile bootstrap int...`: a docstring (documentation text). It says: "The mean of (treatment - control) over paired items and its percentile bootstrap interval."
- `if len(treatment) != len(control):`: runs the block below only if `len(treatment) != len(control)` is true. `len(treatment)` is the number of items in `treatment`; `len(control)` is the number of items in `control`.

<!-- fmt: off -->
```python
        raise ValueError("a paired comparison needs the same number of items on both sides")
    differences = [t - c for t, c in zip(treatment, control, strict=True)]
    return mean(differences), bootstrap_mean_interval(differences, resamples, seed, level)


def shuffled_indices(n: int, seed: int) -> list[int]:
    """A seeded Fisher-Yates permutation of range(n), the same in the Python and Java ports."""
    rng = SplitMix64(seed)
    order = list(range(n))
    for i in range(n - 1, 0, -1):
        j = rng.below(i + 1)
        order[i], order[j] = order[j], order[i]
    return order
```
<!-- fmt: on -->

- `raise ValueError("a paired comparison needs the same number of items on both sides")`: signals an error, `ValueError('a paired comparison needs the same number of items on both sides')`; normal flow stops here and the nearest matching `except` takes over. `ValueError('a paired comparison needs the same number of items on b...` is a ValueError.
- `differences = [t - c for t, c in zip(treatment, control, strict=True)]`: sets `differences` to the value of `[t - c for t, c in zip(treatment, control, strict=True)]`. `[t - c for t, c in zip(treatment, control, strict=True)]` builds a list: for each `(t, c)` in `zip(treatment, control, strict=True)`; `zip(treatment, control, strict=True)` is items of `treatment`, `control` taken together, position by position.
- `return mean(differences), bootstrap_mean_interval(differences, resamples, seed, level)`: ends the function and hands back `(mean(differences), bootstrap_mean_interval(differences, resamples, seed, lev...`.
- `def shuffled_indices(n: int, seed: int) -> list[int]:`: defines the function `shuffled_indices` taking n (int); seed (int) and returns `list[int]`. Purpose: A seeded Fisher-Yates permutation of range(n), the same in the Python and Java ports.
- `"""A seeded Fisher-Yates permutation of range(n), the same in the Python and Java ports...`: a docstring (documentation text). It says: "A seeded Fisher-Yates permutation of range(n), the same in the Python and Java ports."
- `rng = SplitMix64(seed)`: sets `rng` to the value of `SplitMix64(seed)`.
- `order = list(range(n))`: sets `order` to the value of `list(range(n))`. `list(range(n))` is `range(n)` copied into a list; `range(n)` is the whole numbers from `0` up to, not including, `n`.
- `for i in range(n - 1, 0, -1):`: repeats the block below once for each `i` in `range(n - 1, 0, -1)`. `range(n - 1, 0, -1)` is the whole numbers from `n - 1` up to, not including, `-1`.
- `j = rng.below(i + 1)`: sets `j` to the value of `rng.below(i + 1)`.
- `order[i], order[j] = order[j], order[i]`: sets `(order[i], order[j])` to a tuple of 2 items.
- `return order`: ends the function and hands back `order`.

#### `src/cost_router/domain/tasks.py`

<!-- fmt: off -->
```python
"""The tasks the router serves, the policy text they refer to, and the arithmetic that fixes the refund answers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

LABELS = ("billing", "shipping", "returns", "account")

REFUND_POLICY = (
    "Refunds are 100% of the returned items' price for returns within 15 days of delivery, 80% from day 16 to "
    "day 30, and nothing after day 30. Damaged items are refunded 100% of their price within 30 days."
)
```
<!-- fmt: on -->

- `"""The tasks the router serves, the policy text they refer to, and the arithmetic that ...`: a docstring (documentation text). It says: "The tasks the router serves, the policy text they refer to, and the arithmetic that fixes the refund answers."
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import re`: imports the module(s) `re` so this file can use them. `re` is regular expressions.
- `from dataclasses import dataclass`: takes the name(s) `dataclass` from the module `dataclasses` (classes that are mostly data).
- `from enum import StrEnum`: takes the name(s) `StrEnum` from the module `enum` (named constants).
- `from typing import Any`: takes the name(s) `Any` from the module `typing` (names used in type annotations).
- `LABELS = ("billing", "shipping", "returns", "account")`: sets `LABELS` to a tuple of 4 items.
- `REFUND_POLICY = (`: sets `REFUND_POLICY` to the constant `"Refunds are 100% of the returned items' price for`.

<!-- fmt: off -->
```python
POLICY_LINES = (
    "Returns are accepted within 30 days of delivery.",
    "The customer pays return shipping unless the item arrived damaged or wrong.",
    "Refunds reach the original payment method within 5 business days after the returned item arrives.",
    "An exchange for another size or color is free within 30 days if the item is unopened.",
    "A damaged item is refunded in full, with a prepaid return label, within 30 days of delivery.",
    "Gift cards pay for items only; they cannot pay for shipping.",
    "Electronics have a warranty of 12 months from delivery.",
    "We match a lower price from another shop within 7 days of purchase.",
    "An order can be cancelled for free until it ships, normally within 2 hours of ordering.",
    "We never sell or share a customer's personal data with other companies.",
)

ORDER_ID = re.compile(r"\bPR-\d{6}\b")
```
<!-- fmt: on -->

- `POLICY_LINES = (`: sets `POLICY_LINES` to a tuple of 10 items.
- `ORDER_ID = re.compile(r"\bPR-\d{6}\b")`: sets `ORDER_ID` to a prepared regular expression (every pattern is explained piece by piece in `regular-expressions.md`). `re.compile('\\bPR-\\d{6}\\b')` is the pattern `'\\bPR-\\d{6}\\b'` prepared for repeated use.

<!-- fmt: off -->
```python
EXCEPTION_WORDS = ("damaged", "broken", "exception", "only part", "partial")


class Kind(StrEnum):
    """The three kinds of task."""

    LABEL = "label"
    REFUND = "refund"
    POLICY = "policy"


@dataclass(frozen=True)
class RefundOrder:
    """One order in a refund task."""
```
<!-- fmt: on -->

- `EXCEPTION_WORDS = ("damaged", "broken", "exception", "only part", "partial")`: sets `EXCEPTION_WORDS` to a tuple of 5 items.
- **New idea.** An **enum** is a fixed set of named values.
- `class Kind(StrEnum):`: defines the class `Kind` that inherits from `StrEnum`. Purpose: The three kinds of task.
- `"""The three kinds of task."""`: a docstring (documentation text). It says: "The three kinds of task."
- `LABEL = "label"`: sets `LABEL` to the constant `'label'`.
- `REFUND = "refund"`: sets `REFUND` to the constant `'refund'`.
- `POLICY = "policy"`: sets `POLICY` to the constant `'policy'`.
- `class RefundOrder:`: defines the class `RefundOrder`. Decorators: `dataclass(frozen=True)`. Purpose: One order in a refund task.
- `"""One order in a refund task."""`: a docstring (documentation text). It says: "One order in a refund task."

<!-- fmt: off -->
```python
    order_id: str
    total_cents: int
    days: int
    returned_cents: int
    damaged: bool


@dataclass(frozen=True)
class Task:
    """A task whose answer code can check. `gold` is a label, an amount in cents, or a policy line index."""

    task_id: str
    kind: Kind
    difficulty: str
```
<!-- fmt: on -->

- `order_id: str`: declares a field of the class `order_id` of type `str` (no value yet).
- `total_cents: int`: declares a field of the class `total_cents` of type `int` (no value yet).
- `days: int`: declares a field of the class `days` of type `int` (no value yet).
- `returned_cents: int`: declares a field of the class `returned_cents` of type `int` (no value yet).
- `damaged: bool`: declares a field of the class `damaged` of type `bool` (no value yet).
- `class Task:`: defines the class `Task`. Decorators: `dataclass(frozen=True)`. Purpose: A task whose answer code can check.
- `"""A task whose answer code can check. 'gold' is a label, an amount in cents, or a poli...`: a docstring (documentation text). It says: "A task whose answer code can check."
- `task_id: str`: declares a field of the class `task_id` of type `str` (no value yet).
- `kind: Kind`: declares a field of the class `kind` of type `Kind` (no value yet).
- `difficulty: str`: declares a field of the class `difficulty` of type `str` (no value yet).

<!-- fmt: off -->
```python
    split: str
    text: str
    gold: str | int
    orders: tuple[RefundOrder, ...] = ()


def refund_cents(order: dict[str, Any] | RefundOrder) -> int:
    """The refund for one order under REFUND_POLICY, in cents (half up)."""
    days, returned, damaged = (
        (order.days, order.returned_cents, order.damaged)
        if isinstance(order, RefundOrder)
        else (order["days"], order["returned_cents"], order["damaged"])
    )
    if days > 30:
```
<!-- fmt: on -->

- `split: str`: declares a field of the class `split` of type `str` (no value yet).
- `text: str`: declares a field of the class `text` of type `str` (no value yet).
- `gold: str | int`: declares a field of the class `gold` of type `str | int` (no value yet).
- `orders: tuple[RefundOrder, ...] = ()`: declares a field of the class `orders` of type `tuple[RefundOrder, ...]` and sets it to `()`.
- `def refund_cents(order: dict[str, Any] | RefundOrder) -> int:`: defines the function `refund_cents` taking order (dict[str, Any] | RefundOrder) and returns `int`. Purpose: The refund for one order under REFUND_POLICY, in cents (half up).
- `"""The refund for one order under REFUND_POLICY, in cents (half up)."""`: a docstring (documentation text). It says: "The refund for one order under REFUND_POLICY, in cents (half up)."
- `days, returned, damaged = (`: sets `(days, returned, damaged)` to the value of `(order.days, order.returned_cents, order.damaged) if isinstance(order, Refund...`. `(order.days, order.returned_cents, order.damaged) if isinstance(ord...` gives `(order.days, order.returned_cents, or...` when `isinstance(order, RefundOrder)` is true, otherwise `(order['days'], order['returned_cents...`; `isinstance(order, RefundOrder)` is whether `order` is a `RefundOrder`.
- `if days > 30:`: runs the block below only if `days > 30` is true.

<!-- fmt: off -->
```python
        return 0
    if damaged or days <= 15:
        return int(returned)
    return (int(returned) * 80 + 50) // 100


def expected_refund_cents(task: Task) -> int:
    """The refund the policy gives for every order of the task."""
    return sum(refund_cents(o) for o in task.orders)


def money(cents: int) -> str:
    """Cents as dollars with two places."""
    return f"{cents // 100}.{cents % 100:02d}"
```
<!-- fmt: on -->

- `return 0`: ends the function and hands back `0`.
- `if damaged or days <= 15:`: runs the block below only if `damaged or days <= 15` is true.
- `return int(returned)`: ends the function and hands back `int(returned)`. `int(returned)` is `returned` converted to a whole number.
- `return (int(returned) * 80 + 50) // 100`: ends the function and hands back `(int(returned) * 80 + 50) // 100`. `int(returned)` is `returned` converted to a whole number.
- `def expected_refund_cents(task: Task) -> int:`: defines the function `expected_refund_cents` taking task (Task) and returns `int`. Purpose: The refund the policy gives for every order of the task.
- `"""The refund the policy gives for every order of the task."""`: a docstring (documentation text). It says: "The refund the policy gives for every order of the task."
- `return sum(refund_cents(o) for o in task.orders)`: ends the function and hands back `sum((refund_cents(o) for o in task.orders))`. `sum((refund_cents(o) for o in task.orders))` is the sum of `(refund_cents(o) for o in task.orders)`; `(refund_cents(o) for o in task.orders)` builds a generator of values: for each `o` in `task.orders`.
- `def money(cents: int) -> str:`: defines the function `money` taking cents (int) and returns `str`. Purpose: Cents as dollars with two places.
- `"""Cents as dollars with two places."""`: a docstring (documentation text). It says: "Cents as dollars with two places."
- `return f"{cents // 100}.{cents % 100:02d}"`: ends the function and hands back `f'{cents // 100}.{cents % 100:02d}'`. the f-string inserts `cents // 100`, `cents % 100` into the text.

## Try it yourself

1. `wc -l src/cost_router/__init__.py src/cost_router/domain/__init__.py src/cost_router/domain/checks.py` prints the line count of the first files; the tables above show the same numbers.
2. `.venv/bin/python -c "import cost_router.domain.checks; print('imports fine')"` prints `imports fine`.
3. `.venv/bin/lint-imports` ends with `Contracts: 2 kept, 0 broken.`
4. `.venv/bin/python -m pytest tests/unit -q -k domain | tail -3` runs the tests that exercise this layer and ends with a line such as `N passed`.
5. `grep -c "^def \|^class \|^    def " src/cost_router/domain/checks.py` counts the functions and classes in the first file.

## Mistakes people make

- Importing a vendor library or doing file or network work here; the second import-linter contract fails the build.
- Changing a value in place instead of building a new one.
- Hiding a rule inside a long function; short named functions are what the tests call.
- Comparing decimal numbers with `==`.
- Reading the clock or a random generator directly; the code takes them as arguments or ports so tests can control them.

## Check yourself

1. **What may a domain module import?**  
   The standard library and other domain modules, nothing from the outer layers and no vendor library.
2. **Why are domain data classes frozen?**  
   So that a value that was validated cannot be changed afterwards.
3. **Which tool checks the layer rule?**  
   `import-linter`, run as `lint-imports`.
4. **How do you test a pure function?**  
   Call it with chosen inputs and assert on the returned value.
5. **Where do the rules of the lesson live?**  
   In this layer.

## Further reading

The Python language reference: https://docs.python.org/3/reference/ and the tutorial https://docs.python.org/3/tutorial/ (both for Python 3.13; the project accepts 3.12 or newer).
