# Ruff 0.17.2 (linter and formatter)

## What it is

A **linter** reads source code without running it and reports mistakes and bad habits (an unused import, a variable never read, a missing docstring). A **formatter** rewrites the code into one consistent layout (spaces, line breaks, quote style). **Ruff** does both, is written in Rust, and is fast enough to run on every save.

## Why this repository uses it

Style arguments waste time and unused code hides bugs. With Ruff set up, `make lint` fails on the first violation, so a reviewer reads logic rather than whitespace. The rule sets chosen below also require a docstring on every module, class and function that is part of the public surface, which is how the code explains itself to a beginner.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `pyproject.toml` | `[tool.ruff]` settings. |
| `Makefile` | `make lint` and `make format` call ruff. |
| `.github/workflows/ci.yml` | CI runs `make check`, which includes the lint step. |
| `requirements-dev.lock` | Pins ruff 0.17.2 with hashes. |


## How it works underneath

Ruff reads each `.py` file, turns it into a **syntax tree** (the structure of the program, without the spaces), and runs each switched-on **rule** over that tree. A rule has a code (`F401`) made of a letter prefix naming the family and a number. When a rule finds a violation it prints the file, line, code and message. Some violations have a **safe fix** that ruff can apply automatically with `--fix`.

The **formatter** (`ruff format`) is a separate command. It does not judge, it re-prints the tree in one canonical layout (similar to the Black formatter). `ruff format --check` changes nothing and exits with a failure if any file would change; this is how CI forbids unformatted code.

Settings: `line-length` is the width after which the formatter wraps. `target-version` tells ruff which Python syntax may be assumed (so it can suggest newer forms). `select` lists which rule families are active (everything else is off). `per-file-ignores` switches rules off for some paths, here for tests and scripts.

## Walkthrough of this repository's use

### The settings

`pyproject.toml`

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

### How the Makefile calls it

`Makefile`

```make
lint: $(STAMP) ## ruff check, ruff format check, mypy, import-linter
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy
	$(VENV)/bin/lint-imports
```

`ruff check .` lints every file below the current folder (`.`). `ruff format --check .` verifies the layout without changing files. Then mypy and import-linter run (`mypy.md`, `import-linter.md`). The recipe stops at the first failure.
`Makefile`

```make
format: $(STAMP) ## apply ruff's formatting and safe fixes
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/ruff format .
```

`ruff check --fix .` applies the safe automatic fixes. `ruff format .` rewrites the layout. Run `make format` and then commit if `make lint` complains about layout or import order.

## Try it yourself

1. `.venv/bin/ruff --version` prints the pinned version.
2. `.venv/bin/ruff check .` prints `All checks passed!` on a clean tree.
3. `.venv/bin/ruff format --check .` prints `N files already formatted`.
4. Add `import os` at the top of any source file and run `.venv/bin/ruff check .`: you get `F401 [*] 'os' imported but unused` and a hint that a fix is available. Undo with `git checkout .`.
5. `.venv/bin/ruff rule F401` prints the documentation of one rule.

## Mistakes people make

- **Treating the formatter as optional.** CI runs `--check`, so an unformatted file fails the build even though it works.
- **Silencing a rule instead of fixing it.** `# noqa` comments and `per-file-ignores` should carry a reason; the ones here are for tests and for long explanatory sentences.
- **Assuming ruff checks types.** It does not; that is mypy.
- **Different ruff versions** reformat code differently; the version is pinned in the lock file.

## Check yourself

1. **What is the difference between `ruff check` and `ruff format`?**  
   `check` reports rule violations; `format` rewrites layout.
2. **What does `ruff format --check` do to files?**  
   Nothing; it only exits with a failure if a file would change.
3. **What does `select = [...]` control?**  
   Which rule families are on.
4. **Why are docstring rules (`D100`...) enabled?**  
   So that every module, class and public function explains itself.
5. **What does `--fix` do?**  
   Applies the rules' safe automatic corrections.

## Further reading

Ruff documentation: https://docs.astral.sh/ruff/ (rules, settings, formatter). Pinned version here: 0.17.2.
