# JSON and JSON Lines

## What it is

JSON (JavaScript Object Notation) is a text format for data. It has six kinds of value: an **object** `{"key": value, ...}` (a set of named values), an **array** `[v1, v2]`, a **string** in double quotes, a **number**, `true`/`false`, and `null` (nothing). **JSON Lines** (`.jsonl`) puts one complete JSON value on each line of a file.

## Why this repository uses it

Nearly everything the program saves or sends is JSON: the numbers agreed before an experiment, the reports, the recorded model answers, the settings of the model server, the bodies of HTTP calls, and the structured log lines. It is text (so git can diff it), every language can read it, and the Python and the Java halves read the same files.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/cost_router/infrastructure/reports.py` | Writes and reads reports. |
| `reports/*.json (5 files)` | Committed result files. |
| `config/*.json (3 files)` | Settings and pinned values. |
| `**/*.jsonl (3 files)` | Data sets, recorded answers and raw samples. |
| `tests/fixtures/recorded.jsonl` | Recorded model exchanges. |
| `data/tasks.jsonl` | Input data sets, one case per line. |


## How it works underneath

**Syntax rules.** Keys are always strings in double quotes. No trailing commas. No comments. Numbers have no quotes (`0.05`); `"0.05"` is a string. Text escapes: `\n` newline, `\"` quote, `\\` backslash, `\u00e9` a Unicode character.

**Parsing.** A parser reads characters left to right and builds nested objects: `{` starts a dictionary, `[` a list. In Python, `json.loads(text)` returns dictionaries, lists, `str`, `int`/`float`, `True`/`False`, `None`; `json.dumps(obj)` goes the other way.

**Why sort the keys and round floats.** The same data must produce the same bytes. A dictionary built in a different order or a float printed with a different tail would produce a different file and a noisy diff.

**JSONL.** Because each line stands alone, a program can append one record without rewriting the file, process a huge file line by line, and recover after a crash by dropping at most one broken last line. The recorded fixtures rely on this.

## Walkthrough of this repository's use

### The writer and reader

`src/cost_router/infrastructure/reports.py`

<!-- fmt: off -->
```python
"""Writing reports as JSON, JSONL and Markdown with stable key order and rounded floats."""
```
<!-- fmt: on -->

Module docstring: reports are written as JSON, JSONL and Markdown with a stable key order and rounded numbers, so a rerun produces byte-identical files and `git diff` shows only real changes.

<!-- fmt: off -->
```python
from __future__ import annotations

import dataclasses
import json
from enum import Enum
from pathlib import Path
from typing import Any
```
<!-- fmt: on -->

Imports: `dataclasses` (to look inside dataclass objects), `json` (the standard-library reader and writer), `Enum` (a fixed set of named values) and `Path` (a file path object).

<!-- fmt: off -->
```python
def to_jsonable(value: Any) -> Any:
    """Dataclasses, enums and tuples as plain JSON data; floats rounded to 6 places."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: to_jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [to_jsonable(v) for v in value]
    if isinstance(value, float):
        return round(value, 6) if value != float("inf") else None
    return value
```
<!-- fmt: on -->

JSON can only hold objects, lists, text, numbers, `true`, `false` and `null`. This function converts anything else into those. A dataclass becomes a dictionary of its fields (recursively); an enum becomes its value; dictionary keys become text; lists and tuples become lists; a float is rounded to six places (and infinity, which JSON cannot hold, becomes `null`). `isinstance(value, list | tuple)` tests for either type.

<!-- fmt: off -->
```python
def dump_json(path: Path, value: Any) -> None:
    """Write one JSON document, indented, keys sorted."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(to_jsonable(value), indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
```
<!-- fmt: on -->

Writes one JSON document. `mkdir(parents=True, exist_ok=True)` creates missing folders. `indent=2` pretty-prints, `sort_keys=True` fixes the order of keys, `ensure_ascii=False` keeps non-English letters as they are, and the final `+ "\n"` ends the file with a newline.

<!-- fmt: off -->
```python
def dump_jsonl(path: Path, rows: list[Any]) -> None:
    """Write one JSON object per line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(to_jsonable(row), sort_keys=True, ensure_ascii=False) + "\n")
```
<!-- fmt: on -->

Writes a **JSON Lines** file: one JSON object per line, no commas between them, no surrounding list. It can be appended to and read one line at a time.

<!-- fmt: off -->
```python
def load_json(path: Path) -> Any:
    """Read one JSON document."""
    return json.loads(path.read_text(encoding="utf-8"))
```
<!-- fmt: on -->

Reads a file and parses it with `json.loads` (text in, Python objects out).

### A file agreed before the experiment

`config/bar.json` is committed before the result it will judge (see `git.md`):

```json
{
  "written": "2026-10-27, before any model had answered a task",
  "false_accept_bar": 0.10,
  "hard_accuracy_bar": 0.5,
  "accuracy_margin": 0.02,
  "request_cap": 0.0008,
  "tighten_at": 0.8,
  "day_budget_fractions": [0.5, 0.3]
}
```

Reading it key by key:

- `written` = `"2026-10-27, before any model had answered a task"`: text; the author's own words explain it, see the quoted line. The documentation says: "| Learn the difficulty signal from the build set with a small classifier. | No. The build set does choose which kinds start higher and which hard tasks skip the small tier, with the hand-written signal (two order ids, or a damage or partial-return word). |"
- `false_accept_bar` = `0.1`: a number (JSON has one number type). Read by the program at `src/cost_router/infrastructure/data.py:40`.
- `hard_accuracy_bar` = `0.5`: a number (JSON has one number type). Read by the program at `src/cost_router/infrastructure/data.py:41`.
- `accuracy_margin` = `0.02`: a number (JSON has one number type). Read by the program at `src/cost_router/infrastructure/data.py:42`. The documentation says: "`config/bar.json` was committed alone (`6284d97`) before any model answered a task: a false-accept limit of 10%, a hard-task accuracy floor of 50% for the small tier, an accuracy margin of 2 points against the large model, a per-request cap of $0.0008, the 80%"
- `request_cap` = `0.0008`: a number (JSON has one number type). Read by the program at `src/cost_router/infrastructure/data.py:43`. The documentation says: "A router that sits in front of three models of rising price and skill. It sends each task to the cheapest tier that its measured checks trust, escalates when a check fails, never lets one request pass a per-request cap, holds a daily budget by narrowing the ti"
- `tighten_at` = `0.8`: a number (JSON has one number type). Read by the program at `src/cost_router/infrastructure/data.py:44`.
- `day_budget_fractions` = `[0.5, 0.3]`: a list. Read by the program at `src/cost_router/infrastructure/data.py:45`.

### One recorded exchange (JSONL)

`tests/fixtures/recorded.jsonl`, first line, long strings shortened with `...` and indented for reading (in the file it is one line):

```json
{
  "key": "2a50afbc4847ce3d9532c4a70b43003c1d8adbfce9b7d280d84c68837...",
  "request": {
    "max_tokens": 8,
    "messages": [
      {
        "content": "Classify the customer email into exactly one category.\n\nC...",
        "role": "user"
      }
    ],
    "model": "qwen2.5:0.5b",
    "seed": null,
    "temperature": 0.0
  },
  "response": {
    "finish_reason": "stop",
    "input_tokens": 203,
    "latency_s": 0.6399,
    "model": "qwen2.5:0.5b",
    "output_tokens": 2,
    "text": "account"
  }
}
```

- `key` is the SHA-256 of the request (`sha-256.md`).
- `request` repeats the request (long messages are cut so a human can see what was asked).
- `response` holds the reply text, the token counts reported by the server, the model name, the stop reason and the measured delay.

## Try it yourself

1. `python3 -m json.tool config/bar.json | head -5` pretty-prints the agreed-first file; `python3 -m json.tool` also reports an error with a position if the file is broken.
2. `head -n 1 tests/fixtures/*.jsonl | python3 -m json.tool | head -20` shows the first recorded exchange formatted.
3. `wc -l tests/fixtures/*.jsonl` counts the recorded exchanges (one per line).
4. `python3 -c "import json; print(json.dumps({'b': 1, 'a': 2}, sort_keys=True))"` prints `{"a": 2, "b": 1}`.
5. `python3 -c "import json; json.loads('{\"a\": 1,}')"` fails with `Expecting property name enclosed in double quotes`: a trailing comma is not allowed.

## Mistakes people make

- **Trailing commas and comments**, which JSON forbids.
- **Single quotes** around strings or keys.
- **Reading numbers as exact decimals**: `0.1 + 0.2` is not `0.3` in floating point, which is why numbers are rounded when written.
- **Editing a JSONL file by hand and leaving a half line**: every line must be a complete value.
- **Putting secrets into JSON that is committed.**

## Check yourself

1. **What are the six kinds of JSON value?**  
   Object, array, string, number, boolean (`true`/`false`) and `null` (counting booleans as one kind).
2. **What is the difference between JSON and JSONL?**  
   JSON is one value for a whole file; JSONL is one value per line.
3. **Why does `dump_json` sort keys?**  
   So that the same data always produces the same bytes and diffs stay small.
4. **Can JSON contain comments?**  
   No.
5. **Why is `evals/*.json` committed before the experiment?**  
   The commit date shows the numbers were agreed before the result was known.

## Further reading

JSON (ECMA-404): https://www.json.org/ and https://ecma-international.org/publications-and-standards/standards/ecma-404/ . JSON Lines: https://jsonlines.org/ . Python `json`: https://docs.python.org/3/library/json.html
