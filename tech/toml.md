# TOML and pyproject.toml

## What it is

TOML ("Tom's Obvious Minimal Language") is a file format for settings. It looks like the old Windows `.ini` files but has real types: strings in quotes, numbers, true/false, lists in square brackets, and groups called **tables**. `pyproject.toml` is the standard file where a Python project describes itself and where tools such as ruff, mypy and pytest keep their settings.

## Why this repository uses it

One file holds the project's name and version, its dependencies, how it is built, the command-line programs it installs, and the configuration of every checking tool. That keeps the rules of the repository in one place that CI and your editor both read.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `pyproject.toml` | Project metadata, dependencies, the build system, and the settings of ruff, mypy, pytest, coverage and import-linter. |


## How it works underneath

A TOML file is read top to bottom into nested dictionaries. A line `[tool.ruff]` starts a **table** named `ruff` inside `tool`; the `key = value` lines after it belong to that table until the next header. `[[tool.mypy.overrides]]` (double brackets) adds one more entry to a **list of tables**. Strings use double quotes. Lists are `[a, b]` and may span lines. Inline tables are `{ key = value }`. A `#` starts a comment. Tools do not read each other's tables: pip reads `[build-system]` and `[project]`, ruff reads `[tool.ruff]`, pytest reads `[tool.pytest.ini_options]`. Python 3.11 and newer can read TOML with the built-in `tomllib`.

## Walkthrough of this repository's use

The whole file, in order. `pip-and-venv.md`, `ruff.md`, `mypy.md`, `pytest.md`, `coverage-py.md` and `import-linter.md` explain what the tools do with these settings.

`pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"
```

- `[build-system]`: The table that says how to build this project into an installable package.
- `requires = ["setuptools>=75"]`: Needs the library `setuptools` (version 75 or newer) at build time.
- `build-backend = "setuptools.build_meta"`: The Python module that does the build; `setuptools.build_meta` is setuptools' entry point for build tools such as pip.

```toml
[project]
name = "ai-cost-aware-router"
version = "0.1.0"
description = "A router that tries the cheapest model first, escalates only when a cheap check fails, and holds a per-request cap and a daily budget."
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [{ name = "Sumit Srivastava" }]
dependencies = ["httpx>=0.27,<1"]
```

- `[project]`: The table with the project's identity, standardised by Python packaging (PEP 621).
- `name = "ai-cost-aware-router"`: The distribution name, as pip would list it.
- `version = "0.1.0"`: The version of this release.
- `description = "A router that tries the cheapest model first, escalates only when a chea...`: A one-sentence summary.
- `readme = "README.md"`: The file shown as the long description.
- `requires-python = ">=3.12"`: The oldest Python this project runs on (3.12). Newer ones are fine.
- `license = { text = "MIT" }`: The licence text identifier (MIT).
- `authors = [{ name = "Sumit Srivastava" }]`: Who wrote it (an inline table, `{ key = value }`).
- `dependencies = ["httpx>=0.27,<1"]`: The list of libraries, each as `name` plus a version rule. `>=0.27,<1` means "0.27 or newer, but older than 1.0"; the comma is a logical AND. These are loose rules (what the code can work with). The exact versions that were used are fixed in the `.lock` files (see `pip-and-venv.md`).
  - `httpx>=0.27,<1`: `httpx` is the library that sends HTTP requests (`httpx.md`).

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8,<10",
    "pytest-cov>=5",
    "ruff>=0.6",
    "mypy>=1.11",
    "import-linter>=2.0",
    "pip-audit>=2.7",
]
```

- `[project.optional-dependencies]`: Groups of extra libraries that are only installed on request, e.g. `pip install -e '.[dev]'`.
- `dev = [`: The list of libraries, each as `name` plus a version rule. `>=0.27,<1` means "0.27 or newer, but older than 1.0"; the comma is a logical AND. These are loose rules (what the code can work with). The exact versions that were used are fixed in the `.lock` files (see `pip-and-venv.md`).
  - `pytest>=8,<10`: `pytest` runs the tests (`pytest.md`).
  - `pytest-cov>=5`: `pytest-cov` connects pytest to the coverage tool (`coverage-py.md`).
  - `ruff>=0.6`: `ruff` is the linter and formatter (`ruff.md`).
  - `mypy>=1.11`: `mypy` is the type checker (`mypy.md`).
  - `import-linter>=2.0`: `import-linter` checks which package may import which (`import-linter.md`).
  - `pip-audit>=2.7`: `pip-audit` looks for known vulnerabilities in the locked libraries (`pip-audit.md`).

```toml
[project.scripts]
cost-router = "cost_router.interfaces.cli:main"
```

- `[project.scripts]`: Command-line programs that installation creates.
- `cost-router = "cost_router.interfaces.cli:main"`: Installs a command called `cost-router`. When you type it, Python imports `cost_router.interfaces.cli` and calls its function `main`.

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

- `[tool.setuptools.packages.find]`: How setuptools finds the Python packages.
- `where = ["src"]`: Look in `src/` (the "src layout": code lives under `src/` so tests cannot import it by accident without installing).

```toml
[tool.setuptools.package-data]
cost_router = ["py.typed"]
```

- `[tool.setuptools.package-data]`: Non-Python files to include in the package.
- `cost_router = ["py.typed"]`: Ships the empty marker file `py.typed`, which tells type checkers that this package has type hints.

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
src = ["src", "tests"]
```

- `[tool.ruff]`: Settings of ruff (`ruff.md`).
- `line-length = 120`: Lines are wrapped at 120 characters.
- `target-version = "py312"`: Write code for Python 3.12 (so new syntax is allowed).
- `src = ["src", "tests"]`: Folders that contain this project's own code, so ruff can tell project imports from library imports when ordering them.

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "N", "C4", "RUF", "PT", "D100", "D101", "D103", "D104"]
```

- `[tool.ruff.lint]`: Lint rule settings.
- `select = ["E", "F", "I", "B", "UP", "SIM", "N", "C4", "RUF", "PT", "D100", "D101", "D10...`: The rule families that are switched on (a code is a letter prefix plus an optional number): `E` pycodestyle errors (layout and style mistakes); `F` pyflakes (unused imports, undefined names); `I` isort (import order); `B` bugbear (patterns that are probably bugs); `UP` pyupgrade (use newer syntax of the target Python); `SIM` simplify (needlessly complicated code); `N` pep8-naming (names in the usual Python style); `C4` comprehensions (use list/dict comprehensions properly); `RUF` ruff's own rules; `PT` pytest style; `D100` a docstring is required in every module; `D101` a docstring is required in every public class; `D103` a docstring is required in every public function; `D104` a docstring is required in every package.

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D", "E501", "PT011", "PT018"]
"scripts/**" = ["D", "E501"]
# Markdown table rows are long f-strings; wrapping them would make the tables harder to read in the source.
"src/cost_router/application/report_md.py" = ["E501"]
```

- `[tool.ruff.lint.per-file-ignores]`: Rules switched off for some paths.
- `"tests/**" = ["D", "E501", "PT011", "PT018"]`: Tests: no docstring rules (`D`), no line-length rule (`E501`), and two pytest-style rules off (`PT011` wants a message in `pytest.raises`, `PT018` wants asserts split).
- `"scripts/**" = ["D", "E501"]`: Helper scripts: no docstring rules, no line-length rule.
- `# Markdown table rows are long f-strings; wrapping them would make the tables harder to read in the `: a comment written by the author; the tool ignores it. It explains the lines below.
- `"src/cost_router/application/report_md.py" = ["E501"]`: A path in the source where the line-length rule (`E501`) is off, for modules that write report sentences or tables.

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
[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
disallow_incomplete_defs = false
disallow_untyped_calls = false
check_untyped_defs = false
```

- `# Test functions are named for the behavior they check; annotating every one adds noise, not safety.`: a comment written by the author; the tool ignores it. It explains the lines below.
- `[[tool.mypy.overrides]]`: Double brackets mean "one more entry of a list of tables": settings for some modules only.
- `module = ["tests.*"]`: The modules these overrides apply to.
- `disallow_untyped_defs = false`: Tests may define functions without annotations.
- `disallow_incomplete_defs = false`: Tests may annotate only some parameters.
- `disallow_untyped_calls = false`: Tests may call functions that have no annotations.
- `check_untyped_defs = false`: Do not check the bodies of unannotated test functions.

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
markers = [
    "live: needs a real model; opt-in",
    "e2e: regenerates the committed reports from the recorded fixtures",
]
```

- `[tool.pytest.ini_options]`: Settings of pytest (`pytest.md`).
- `testpaths = ["tests"]`: Where to look for tests when no path is given.
- `addopts = "-ra --strict-markers"`: Options added to every run: `-ra` prints a summary of why tests were skipped or failed; `--strict-markers` makes an unknown marker an error.
- `markers = [`: Custom test markers (labels you can put on a test with `@pytest.mark.NAME`). Declaring them here lets `--strict-markers` catch a misspelled marker.
  - `live`: needs a real model; opt-in
  - `e2e`: regenerates the committed reports from the recorded fixtures

```toml
[tool.coverage.run]
source = ["cost_router"]
branch = true
```

- `[tool.coverage.run]`: How the coverage tool (`coverage-py.md`) measures.
- `source = ["cost_router"]`: Measure this package only.
- `branch = true`: Also measure branches: for `if` statements, whether both the true and the false path ran.

```toml
[tool.coverage.report]
show_missing = true
skip_covered = false
```

- `[tool.coverage.report]`: How the report looks.
- `show_missing = true`: List the line numbers that no test ran.
- `skip_covered = false`: Also list files that are fully covered.

```toml
[tool.importlinter]
root_package = "cost_router"
include_external_packages = true
```

- `[tool.importlinter]`: Settings of import-linter (`import-linter.md`).
- `root_package = "cost_router"`: The package whose imports are checked.
- `include_external_packages = true`: Also see imports of libraries (needed by the "forbidden" contract).

```toml
[[tool.importlinter.contracts]]
name = "Layers: interfaces -> infrastructure -> application -> domain, never upward"
type = "layers"
layers = [
    "cost_router.interfaces",
    "cost_router.infrastructure",
    "cost_router.application",
    "cost_router.domain",
]
```

- `[[tool.importlinter.contracts]]`: One architecture rule ("contract").
- `name = "Layers: interfaces -> infrastructure -> application -> domain, never upward"`: The distribution name, as pip would list it.
- `type = "layers"`: A layers contract: modules listed first may import modules listed later, never the other way round.
- `layers = [`: The layers from top to bottom: `cost_router.interfaces`, `cost_router.infrastructure`, `cost_router.application`, `cost_router.domain`. The top layer may import everything below it; `domain` may import nothing above it.

```toml
[[tool.importlinter.contracts]]
name = "Domain and application know no vendor SDK or transport library"
type = "forbidden"
source_modules = ["cost_router.domain", "cost_router.application"]
forbidden_modules = ["httpx", "anthropic", "openai"]
```

- `[[tool.importlinter.contracts]]`: One architecture rule ("contract").
- `name = "Domain and application know no vendor SDK or transport library"`: The distribution name, as pip would list it.
- `type = "forbidden"`: A forbidden contract: the listed source modules must not import the forbidden ones, directly or through other modules.
- `source_modules = ["cost_router.domain", "cost_router.application"]`: The modules that are restricted.
- `forbidden_modules = ["httpx", "anthropic", "openai"]`: The libraries they must never import: `httpx`, `anthropic`, `openai`. That keeps vendor and transport code in the infrastructure layer.

## Try it yourself

1. `python3 -c "import tomllib; d = tomllib.load(open('pyproject.toml','rb')); print(d['project']['name'], d['project']['requires-python'])"` prints the project name and `>=3.12`.
2. `python3 -c "import tomllib; d = tomllib.load(open('pyproject.toml','rb')); print(list(d['tool']))"` lists the tools that have a table (ruff, mypy, pytest, coverage, importlinter, setuptools).
3. `.venv/bin/pip show ai-cost-aware-router` after `make install` shows the metadata pip read from this file (version 0.1.0, author, dependencies).
4. Change `line-length` in `[tool.ruff]` to 100 and run `.venv/bin/ruff format --check .`: files now fail. Revert with `git checkout pyproject.toml`.

## Mistakes people make

- Forgetting quotes around a string (`name = foo`) or using single quotes inside an array of double-quoted strings: TOML requires valid strings.
- Mixing `[table]` and `[[list of tables]]`: `[[tool.mypy.overrides]]` can be repeated; `[tool.mypy]` cannot.
- Editing a dependency here and forgetting the lock files: the pinned versions in `requirements*.lock` do not change until `make lock` runs.
- Putting a setting under the wrong tool name: ruff will not complain about a table it does not own.

## Check yourself

1. **What is the difference between `[x]` and `[[x]]`?**  
   `[x]` is one table. `[[x]]` appends one more table to a list named `x`.
2. **Where do the project's dependencies live?**  
   Under `[project]` in `dependencies`, and groups of extras under `[project.optional-dependencies]`.
3. **What does `requires-python = ">=3.12"` do?**  
   It tells pip not to install the project on a Python older than 3.12.
4. **How does the command `cost-router` get created?**  
   From `[project.scripts]`: installation creates a launcher that imports the named module and calls the named function.
5. **Which tool reads `[tool.importlinter]`?**  
   `import-linter`, run as `lint-imports`.

## Further reading

TOML 1.0 specification: https://toml.io/en/v1.0.0 . Python packaging guide for `pyproject.toml`: https://packaging.python.org/en/latest/specifications/pyproject-toml/
