# pytest 9.1.1

## What it is

A **test** is a small program that calls your code with known inputs and checks the outputs. **pytest** finds the tests (files named `test_*.py`, functions named `test_*`), runs them, and reports which passed or failed. A test passes if it finishes without an error; the usual way to fail is an `assert` statement whose condition is false.

## Why this repository uses it

The Done-when lines of the lesson are numbers, and tests are what keep those numbers honest: unit tests cover the logic, an end-to-end test replays the recorded model answers and compares the output with the committed report, and the optional live tests call a real model. Here the tests are grouped as: __init__.py: 0 tests, e2e: 1 tests, live: 2 tests, unit: 72 tests.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `tests/unit/** (12 files)` | Fast tests of single functions and classes; no network. |
| `tests/e2e/** (2 files)` | Replays the whole study from recorded answers and checks the committed reports. |
| `tests/live/** (2 files)` | Calls a real model; only runs when asked. |
| `tests/fixtures/recorded.jsonl` | Recorded model answers used by the tests. |
| `pyproject.toml` | `[tool.pytest.ini_options]`. |
| `Makefile` | `make test`, `make test-e2e`, `make test-live`, `make test-integration`. |


## How it works underneath

**Collection.** pytest walks the folders named in `testpaths`, imports each `test_*.py`, and collects every function whose name starts with `test_`. It runs them one by one; a failure in one does not stop the others.

**Assertions.** pytest rewrites the `assert` statements while importing the test so that a failure shows the values: `assert 1 + 1 == 3` reports `assert 2 == 3`.

**Fixtures.** A function decorated with `@pytest.fixture` prepares something (a temporary folder, a fake server). A test asks for it by naming a parameter with the same name, and pytest passes the result in; `conftest.py` holds fixtures shared by a folder. The built-in `tmp_path` fixture gives each test its own empty folder.

**Markers.** `@pytest.mark.live` labels a test. `-m "not live"` runs everything but the labelled tests; `--strict-markers` turns an unknown label into an error, which catches typos.

**Exit status.** 0 if all passed, non-zero otherwise, which is what makes `make test` and CI fail. `-ra` at the end of a run prints a short summary of every test that was skipped or failed.

## Walkthrough of this repository's use

### The settings

`pyproject.toml`

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

### The test files

| File | What it checks (first sentence of its docstring) |
| --- | --- |
| `tests/e2e/test_replay_reproduces_committed_reports.py` | Replaying the recorded fixtures regenerates exactly the committed configuration and reports (no model, no network). |
| `tests/live/test_live_models.py` | Opt-in tests against real models. |
| `tests/unit/application/test_router_and_experiments.py` | (no docstring) |
| `tests/unit/domain/test_domain.py` | (no docstring) |
| `tests/unit/domain/test_llm_and_stats.py` | (no docstring) |
| `tests/unit/fakes.py` | Small fakes shared by the unit tests. |
| `tests/unit/infrastructure/test_llm_adapters.py` | (no docstring) |
| `tests/unit/infrastructure/test_support_modules.py` | (no docstring) |
| `tests/unit/interfaces/test_cli.py` | (no docstring) |

### How the Makefile runs them

`Makefile`

```make
test: $(STAMP) ## unit tests with coverage (offline, recorded model responses)
	$(PY) -m pytest tests/unit --cov=$(PKG) --cov-report=term
	$(PY) -m coverage report --include='src/$(PKG)/domain/*,src/$(PKG)/application/*' --fail-under=95
```

Runs only `tests/unit` and measures coverage (`coverage-py.md`) in the same run. `$(PY)` is `.venv/bin/python`; `-m pytest` runs pytest as a module.
`Makefile`

```make
test-e2e: $(STAMP) ## regenerate the reports from the fixtures and compare them with the committed ones
	$(PY) -m pytest tests/e2e -m e2e
```

The end-to-end test replays the whole study from the recorded answers.

## Try it yourself

1. `.venv/bin/pytest --version` prints the pinned version.
2. `.venv/bin/pytest tests/unit -q` prints a row of dots, then `N passed in X.XXs`.
3. `.venv/bin/pytest tests/unit -q --collect-only | tail -3` lists how many tests were collected without running them.
4. `.venv/bin/pytest -k fixture_key -v` runs only tests whose name contains `fixture_key` (if any), one per line with `PASSED`.
5. `.venv/bin/pytest --markers | head -20` lists the markers, including the project's own.

## Mistakes people make

- **A test that asserts nothing** always passes.
- **Tests that depend on each other's order or on files left by another test.** Use `tmp_path` and fixtures.
- **Calling a real model or network from a unit test.** The unit tests here use recorded answers; live tests are opt-in.
- **Forgetting that a misspelled marker is silently accepted** unless `--strict-markers` is on (it is).
- **Comparing floating-point numbers with `==`.** Use `pytest.approx`.

## Check yourself

1. **How does pytest decide what is a test?**  
   Files named `test_*.py` and functions named `test_*`.
2. **What fails a test?**  
   An exception, most often a false `assert`.
3. **What does `-m "not live"` do?**  
   Runs every test except those marked `live`.
4. **What is a fixture?**  
   A prepared object or resource that a test receives by naming it as a parameter.
5. **Why `--strict-markers`?**  
   Unknown markers become errors, so typos are caught.

## Further reading

pytest documentation: https://docs.pytest.org/ (how to write tests, fixtures, markers). Pinned version: 9.1.1.
