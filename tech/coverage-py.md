# coverage.py 7.17.0 and pytest-cov

## What it is

**Code coverage** answers: which lines of my code did the tests execute? **coverage.py** watches the program while the tests run and records every line (and, with branch coverage, every `if` decision) that was reached. A line the tests never reached is a line nobody has checked. **pytest-cov** is the plug-in that starts coverage inside a pytest run.

## Why this repository uses it

The domain and application layers hold the logic whose results the lesson reports. The Makefile requires at least 95 percent of them to be covered, so a change that adds logic without a test fails `make test`. Infrastructure and interfaces (files, HTTP, command line) are exercised by end-to-end and integration tests instead, so they are excluded from the 95 percent gate.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `pyproject.toml` | `[tool.coverage.run]` and `[tool.coverage.report]`. |
| `Makefile` | `make test` measures and then enforces the 95 percent gate. |
| `requirements-dev.lock` | Pins coverage 7.17.0 and pytest-cov. |


## How it works underneath

Python can call a hook every time it is about to run a line. coverage.py installs such a hook (a C extension makes it cheap), notes the file and line number, and at the end of the run writes the result to a file named `.coverage` (a small SQLite database). `coverage report` reads that file, compares with the list of executable lines it finds in the source (using the syntax tree), and prints per-file percentages. With `branch = true` it also notes which way each `if`, loop or `try` went, so a line that is always taken one way shows up as a partial branch. `--fail-under=95` makes `coverage report` exit with a failure when the total is below 95; `--include` restricts the report to named paths.

## Walkthrough of this repository's use

### The settings

`pyproject.toml`

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

### How the Makefile runs and enforces it

`Makefile`

```make
test: $(STAMP) ## unit tests with coverage (offline, recorded model responses)
	$(PY) -m pytest tests/unit --cov=$(PKG) --cov-report=term
	$(PY) -m coverage report --include='src/$(PKG)/domain/*,src/$(PKG)/application/*' --fail-under=95
```

First line: pytest runs the unit tests with `--cov=<package>` (measure that package) and `--cov-report=term` (print the table to the terminal). Second line: `coverage report` reads the data from the first run, restricts to the domain and application folders with `--include`, and fails if the percentage is under 95.

## Try it yourself

1. `make test` ends with a table of `Name Stmts Miss Branch BrPart Cover Missing` rows and a final line `TOTAL ...`; the second command prints a table with only the inner layers and exits with 0 if the total is at least 95 percent.
2. `.venv/bin/coverage report --show-missing | head` lists the line numbers that were never executed.
3. `.venv/bin/coverage html && open htmlcov/index.html` opens a page where unexecuted lines are highlighted (`htmlcov/` is git-ignored).
4. Temporarily delete a test file under `tests/unit/domain` and run `make test`: the gate fails when the percentage drops below 95. Restore with `git checkout .`.

## Mistakes people make

- **Reading 100 percent as "no bugs".** Coverage shows what ran, not whether the assertions were good.
- **Chasing the number** with tests that assert nothing.
- **Mixing data from runs of different code**: delete `.coverage` (`make clean`) if numbers look odd.
- **Forgetting `source`**, so the report includes the tests themselves or third-party code.

## Check yourself

1. **What does coverage measure?**  
   Which lines (and branches) were executed during the tests.
2. **Where is the raw result stored?**  
   In the `.coverage` file.
3. **What does `branch = true` add?**  
   Whether each decision was taken both ways.
4. **Why is the 95 percent gate limited to the domain and application folders?**  
   They hold the logic; the other layers are covered by end-to-end and integration tests.
5. **What does `--fail-under=95` do?**  
   Makes the command exit with an error when the total is below 95 percent.

## Further reading

coverage.py: https://coverage.readthedocs.io/ . pytest-cov: https://pytest-cov.readthedocs.io/ . Pinned coverage version: 7.17.0.
