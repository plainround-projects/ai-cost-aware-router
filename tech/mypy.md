# mypy 2.4.0 (static type checker)

## What it is

A **type** says what kind of value something is: a number, a piece of text, a list of numbers. Python does not check types when it runs, but you may write them down as **annotations** (`def area(w: float, h: float) -> float:`). **mypy** reads the annotations and, without running the program, reports places where a value of the wrong type is used, for example passing text where a number is expected, or forgetting that something may be `None`.

## Why this repository uses it

The program passes dictionaries and results between layers; many bugs are "this can be empty" or "this is the wrong field". With `strict = true` mypy refuses unannotated functions in the source, so the shape of every value is written where a beginner can read it.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `pyproject.toml` | `[tool.mypy]` and its override for tests. |
| `Makefile` | `make lint` runs `mypy` with no arguments (the `files` setting names what to check). |
| `src/**/*.py (36 files)` | The annotated code. |
| `requirements-dev.lock` | Pins mypy 2.4.0. |


## How it works underneath

mypy builds a model of every function's input and output types from the annotations (and infers the types of local variables from how they are assigned). It then checks every call and assignment against it. A `str | None` means "text or nothing": using it as text without first checking for `None` is an error. Names from other modules are followed; for libraries without annotations mypy needs stubs or treats them as unknown.

`strict = true` switches on a bundle of options: `disallow_untyped_defs` (every function needs annotations), `disallow_any_generics` (`list` must say `list[int]`), `warn_return_any`, `no_implicit_optional`, `warn_unused_ignores`, and others. mypy never changes the program; annotations are ignored when Python runs the code.

## Walkthrough of this repository's use

### The settings

`pyproject.toml`

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

- `[tool.mypy]`: Settings of mypy (`mypy.md`).
- `python_version = "3.12"`: Check as Python 3.12.
- `strict = true`: Switches on all the strict checks together: every function must be fully annotated, no implicit `Any`, no untyped calls, and more.
- `files = ["src", "tests"]`: What `mypy` with no arguments checks.

```toml
# Test functions are named for the behavior they check; annotating every one adds noise, not safety.
```

- `# Test functions are named for the behavior they check; annotating every one adds noise, not safety.`: a comment written by the author; the tool ignores it. It explains the lines below.

```toml
[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
disallow_incomplete_defs = false
disallow_untyped_calls = false
check_untyped_defs = false
```

- `[[tool.mypy.overrides]]`: Double brackets mean "one more entry of a list of tables": settings for some modules only.
- `module = ["tests.*"]`: The modules these overrides apply to.
- `disallow_untyped_defs = false`: Tests may define functions without annotations.
- `disallow_incomplete_defs = false`: Tests may annotate only some parameters.
- `disallow_untyped_calls = false`: Tests may call functions that have no annotations.
- `check_untyped_defs = false`: Do not check the bodies of unannotated test functions.

### A small illustration (not from this repository)

<!-- fmt: off -->
```python
def double(n: int) -> int:
    return n * 2

double("3")   # mypy: Argument 1 to "double" has incompatible type "str"; expected "int"
```
<!-- fmt: on -->

### How it is run

`Makefile`

```make
lint: $(STAMP) ## ruff check, ruff format check, mypy, import-linter
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy
	$(VENV)/bin/lint-imports
```

The `mypy` line has no file arguments because `files = [...]` in `pyproject.toml` already names the folders to check.

## Try it yourself

1. `.venv/bin/mypy --version` prints the pinned version.
2. `.venv/bin/mypy` prints `Success: no issues found in N source files`.
3. In any source function, change a return annotation from `-> str` to `-> int` and run `.venv/bin/mypy`: it points at the return line. Undo with `git checkout .`.
4. `.venv/bin/mypy --strict --help | head` lists the many switches that `strict` turns on.

## Mistakes people make

- **Believing annotations are checked at run time.** They are not; only mypy checks them.
- **`Any` creeping in.** A value typed `Any` switches checking off for everything it touches.
- **Sprinkling `# type: ignore`** to silence errors. `warn_unused_ignores` (part of strict) at least flags the ones that no longer silence anything.
- **Forgetting `None` cases** (`dict.get` returns `None` for a missing key).

## Check yourself

1. **Does Python check type annotations at run time?**  
   No. mypy checks them without running the code.
2. **What does `str | None` mean?**  
   The value is either text or `None`.
3. **What does `strict = true` do?**  
   Turns on a bundle of strict options such as requiring annotations on every function.
4. **Why are tests configured more loosely?**  
   Test names describe behavior; annotating every test function adds noise, not safety.
5. **Where does mypy find out which files to check?**  
   `files` in `[tool.mypy]`.

## Further reading

mypy documentation: https://mypy.readthedocs.io/ (command line, config file, strict mode). Pinned version: 2.4.0.
