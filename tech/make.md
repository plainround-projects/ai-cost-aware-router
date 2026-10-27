# Make

## What it is

Make is a command-line tool that runs named tasks. You write the tasks in a file called `Makefile`. Each task is a **rule**: a **target** (the name), its **prerequisites** (what must be done first), and a **recipe** (the shell commands to run). You then type `make target` and make runs the recipe, after first running the prerequisites. Make was designed to rebuild files only when their inputs changed, and it does that by comparing file dates. Many projects use it as a simple task runner.

## Why this repository uses it

The lesson's commands are all `make` targets: `help`, `install`, `up`, `run`, `models`, `checks`, `tune`, `router`, `day`, `false-accepts`, `report`, `record`, `test-e2e`, `java-test`, `parity`, `down`, `lint`, `format`, `test`, `test-live`, `audit`, `lock`, `check`, `docker-build`. A reader needs to remember one tool and a few verbs, not the long command lines behind them. The `Makefile` is also the place where the exact commands live, so the README, the CI workflow and your terminal all run the same thing.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `Makefile` | Every rule of the project: set-up, run, test, lint, audit, clean. |
| `.github/workflows/ci.yml` | CI runs `make ...` so that CI and your terminal agree. |
| `README.md` | Tells you which `make` command proves each lesson line. |


## How it works underneath

When you type `make test`, make reads `Makefile` from the current folder and builds a graph. Each target is a node. The prerequisites after the colon are arrows to other nodes. Make visits the prerequisites first (depth first), then runs the target's recipe.

For a target that is a **file** (like `.venv/.installed`), make looks at the file's modification date. If the file exists and is newer than all its prerequisites, make skips the recipe. If the file is missing or older, make runs it. That is the whole trick behind "install the environment only when the lock file changed".

For a target that is only a **name** (like `test`), there is no file to compare. Such targets are listed under `.PHONY`, which tells make: always run this.

Each line of a recipe starts with a **tab character** (not spaces) and is handed to the shell (`/bin/sh`). Make starts a **new shell for every recipe line**. That is why `cd java && ./mvnw ...` is written on one line: a `cd` on its own line would be forgotten by the next line. If a command exits with a non-zero **exit status** (the number every program returns; 0 means success), make stops and reports an error.

Variables are written `NAME := value` (set once, now), `NAME = value` (set lazily), `NAME ?= value` (set only if not already set). You use them as `$(NAME)`. Inside a recipe, `$@` is the target's name, and `$$` is how you write a single `$` for the shell. A recipe line starting with `@` is not echoed; starting with `-` means "ignore a failure".

## Walkthrough of this repository's use

Below is the whole `Makefile`, in the order it is written. Each block is quoted exactly; the notes after it explain every variable, every rule and every command. Words such as *virtual environment*, *lock file* or *CLI* are explained in `pip-and-venv.md` and `python.md`.

`Makefile`

```make
PYTHON ?= $(shell command -v python3.13 || command -v python3.12 || command -v python3)
```

`?=` assigns only if the variable is not already set (so you can run `make PYTHON=python3.12`). `$(shell ...)` runs a shell command and uses its output. `command -v NAME` prints the path of NAME if the program exists and prints nothing otherwise, so `a || b || c` tries python3.13, then python3.12, then python3: the first one that exists wins. This is the interpreter used to create the virtual environment.

```make
VENV := .venv
```

`:=` assigns once, immediately. `.venv` is the folder of the virtual environment (a private copy of Python and its libraries, explained in `pip-and-venv.md`).

```make
PY := $(VENV)/bin/python
```

The Python inside that environment. `$(VENV)/bin/python` is a make variable reference: make replaces `$(VENV)` by `.venv`, so this is `.venv/bin/python`.

```make
STAMP := $(VENV)/.installed
```

A file that exists once the environment has been installed. Make compares file dates to decide whether to redo work, so an empty marker file is a way to remember that a step is finished.

```make
PKG := cost_router
```

The name of the Python package in `src/` (used below to tell the coverage tool which folder to measure).

```make
-include .env
```

`include FILE` pulls another file into this one; the leading `-` means "no error if it does not exist". Here the file is `.env`, which holds your local settings as `NAME=value` lines. Together with the next line, every variable in it becomes both a make variable and an environment variable of the commands make runs.

```make
export
```

`export` with no names exports every make variable to the commands it runs. That is how the values from `.env` reach the Python program.

```make
.PHONY: help install env up run test test-live lint format audit lock check docker-build down clean models checks tune router day report record test-e2e java-test parity false-accepts
```

`.PHONY` lists targets that are names of actions, not files. Without it, a file called `test` in the folder would make `make test` think there is nothing to do.

```make
help: ## list the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/' | sort
```

Target `help` (no prerequisites). Its help text, shown by `make help`: "list the targets".
- `@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/' | sort`: Prints the help list. `grep -E` searches with an extended pattern: lines that start with a target name made of lowercase letters and hyphens, then a colon, and contain `## `. `$(MAKEFILE_LIST)` is the list of makefiles being read. `sed -E 's/:.*## /\t/'` replaces everything from the colon up to `## ` by a tab so name and description line up. `sort` orders the lines. `|` (a pipe) feeds the output of one command to the next.

```make
$(STAMP): requirements-dev.lock pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -q --require-hashes -r requirements-dev.lock
	$(VENV)/bin/pip install -q --no-deps -e .
	touch $@
```

A rule whose target is the marker file `$(STAMP)`. Make rebuilds the target when it is missing or older than a prerequisite: here `requirements-dev.lock pyproject.toml`. So changing the lock file or `pyproject.toml` makes the next `make` command reinstall everything. Recipe lines (they start with a tab) are shell commands:
- `$(PYTHON) -m venv $(VENV)`: Creates the virtual environment folder `.venv` with the chosen Python.
- `$(VENV)/bin/pip install -q --require-hashes -r requirements-dev.lock`: Installs every library listed in the lock file. `-q` is quiet. `--require-hashes` makes pip refuse any file whose SHA-256 fingerprint is not written in the lock file, so a tampered or swapped package cannot be installed. `-r FILE` means read the list of requirements from FILE.
- `$(VENV)/bin/pip install -q --no-deps -e .`: Installs this project itself into the environment. `-e` (editable) links the folder `src/` instead of copying it, so edits take effect at once. `--no-deps` stops pip from looking for other libraries (they were already installed, with hashes, a line above). `.` means the project in the current folder, described by `pyproject.toml`.
- `touch $@`: `touch` creates the file or updates its date. `$@` is make's name for the target being built, here the marker file. This line is what records "the environment is installed".

```make
install: $(STAMP) ## create .venv from the hash-pinned lock file
```

Target `install` (needs `$(STAMP)` first). Its help text, shown by `make help`: "create .venv from the hash-pinned lock file".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed.

```make
env:
	@[ -f .env ] || { cp .env.example .env; echo "created .env from .env.example"; }
```

Target `env` (no prerequisites).
- `@[ -f .env ] || { cp .env.example .env; echo "created .env from .env.example"; }`: `[ -f .env ]` is a shell test: true if the file `.env` exists. `A || B` runs B only if A failed (exit status not zero). So: if there is no `.env`, copy the example file to `.env` and print a message. `{ ...; }` groups the two commands. The leading `@` tells make not to echo the command line before running it.

```make
CLI := $(PY) -m cost_router.interfaces.cli
```

A shortcut for the command that runs this program's command-line interface: `python -m PACKAGE.interfaces.cli`. `-m` means run a module by its dotted name (explained in `python.md`). Every later recipe writes `$(CLI) something` instead of repeating this.

```make
RECORD ?= tests/fixtures/recorded.jsonl
```

The file where recorded model answers are stored (the default is the committed fixture file).

```make
up: env $(STAMP) ## create .venv and .env (no services: the default adapter replays recorded responses)
	@echo "ready: make run | make test | make lint"
```

Target `up` (needs `env $(STAMP)` first). Its help text, shown by `make help`: "create .venv and .env (no services: the default adapter replays recorded responses)".
Prerequisites run before the recipe: `env` creates `.env` if it is missing; `$(STAMP)` makes sure the virtual environment is installed.
- `@echo "ready: make run | make test | make lint"`: Prints a message. Nothing is started: the default adapter replays recorded answers.

```make
run: $(STAMP) env ## the whole study from recorded responses: models, checks, tuning, router, day, audit, report
	$(CLI) all
```

Target `run` (needs `$(STAMP) env` first). Its help text, shown by `make help`: "the whole study from recorded responses: models, checks, tuning, router, day, audit, report".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed; `env` creates `.env` if it is missing.
- `$(CLI) all`: Runs the program with the sub-command `all`. `all` runs every step of the study in order (each step is a sub-command of its own).

```make
models: $(STAMP) env ## step 1: each model alone on the 150 build tasks
	$(CLI) models
```

Target `models` (needs `$(STAMP) env` first). Its help text, shown by `make help`: "step 1: each model alone on the 150 build tasks".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed; `env` creates `.env` if it is missing.
- `$(CLI) models`: Runs the program with the sub-command `models`. In the code the sub-command is the function `cmd_models` in `src/cost_router/interfaces/cli.py`, which says: "Step 1: each model alone on the build tasks."

```make
checks: $(STAMP) env ## step 2: false-accept and false-reject rate of each check on the build set
	$(CLI) checks
```

Target `checks` (needs `$(STAMP) env` first). Its help text, shown by `make help`: "step 2: false-accept and false-reject rate of each check on the build set".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed; `env` creates `.env` if it is missing.
- `$(CLI) checks`: Runs the program with the sub-command `checks`. In the code the sub-command is the function `cmd_checks` in `src/cost_router/interfaces/cli.py`, which says: "Step 2: false-accept and false-reject rates of each check on the build set (and the test set, for reference)."

```make
tune: $(STAMP) env ## step 3: derive config/router.json from the build set only
	$(CLI) tune
```

Target `tune` (needs `$(STAMP) env` first). Its help text, shown by `make help`: "step 3: derive config/router.json from the build set only".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed; `env` creates `.env` if it is missing.
- `$(CLI) tune`: Runs the program with the sub-command `tune`. In the code the sub-command is the function `cmd_tune` in `src/cost_router/interfaces/cli.py`, which says: "Step 3: derive the start tiers from the build set only and write config/router.json."

```make
router: $(STAMP) env ## step 5: the router and each single model on the 150 test tasks
	$(CLI) router
```

Target `router` (needs `$(STAMP) env` first). Its help text, shown by `make help`: "step 5: the router and each single model on the 150 test tasks".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed; `env` creates `.env` if it is missing.
- `$(CLI) router`: Runs the program with the sub-command `router`. In the code the sub-command is the function `cmd_router` in `src/cost_router/interfaces/cli.py`, which says: "Step 5: the router and each model alone on the test tasks."

```make
day: $(STAMP) env ## step 4: the test tasks replayed as one day under a budget
	$(CLI) day
```

Target `day` (needs `$(STAMP) env` first). Its help text, shown by `make help`: "step 4: the test tasks replayed as one day under a budget".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed; `env` creates `.env` if it is missing.
- `$(CLI) day`: Runs the program with the sub-command `day`. In the code the sub-command is the function `cmd_day` in `src/cost_router/interfaces/cli.py`, which says: "Step 4: the test tasks as one day under a budget."

```make
false-accepts: $(STAMP) env ## step 6: test-set false accepts by tier and check, and one change to the weakest check
	$(CLI) audit
```

Target `false-accepts` (needs `$(STAMP) env` first). Its help text, shown by `make help`: "step 6: test-set false accepts by tier and check, and one change to the weakest check".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed; `env` creates `.env` if it is missing.
- `$(CLI) audit`: Runs the program with the sub-command `audit`. In the code the sub-command is the function `cmd_audit` in `src/cost_router/interfaces/cli.py`, which says: "Step 6: test-set false accepts, and the one change to the weakest check."

```make
report: $(STAMP) env ## write reports/REPORT.md from the stored results
	$(CLI) report
```

Target `report` (needs `$(STAMP) env` first). Its help text, shown by `make help`: "write reports/REPORT.md from the stored results".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed; `env` creates `.env` if it is missing.
- `$(CLI) report`: Runs the program with the sub-command `report`. In the code the sub-command is the function `cmd_report` in `src/cost_router/interfaces/cli.py`, which says: "Write reports/REPORT.md."

```make
# Needs ollama running with the three models in .env.example. New exchanges are appended; known ones are not repeated.
record: $(STAMP) ## re-run everything against local models and append the exchanges to $(RECORD)
	LLM_PROVIDER=local LLM_RECORD_TO=$(RECORD) WORKERS=$${WORKERS:-3} $(CLI) all
```

Target `record` (needs `$(STAMP)` first). Its help text, shown by `make help`: "re-run everything against local models and append the exchanges to $(RECORD)".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed.
- `LLM_PROVIDER=local LLM_RECORD_TO=$(RECORD) WORKERS=$${WORKERS:-3} $(CLI) all`: Three environment variables are set for this one command. `LLM_PROVIDER=local` switches from replaying recordings to calling the local model server. `LLM_RECORD_TO=FILE` appends every new exchange to FILE. `WORKERS=${WORKERS:-N}` means: use the value of `WORKERS` from the environment if set, otherwise N (the `$$` is how a Makefile writes one `$`). Then the program runs its `all` sub-command.

```make
test-e2e: $(STAMP) ## regenerate the reports from the fixtures and compare them with the committed ones
	$(PY) -m pytest tests/e2e -m e2e
```

Target `test-e2e` (needs `$(STAMP)` first). Its help text, shown by `make help`: "regenerate the reports from the fixtures and compare them with the committed ones".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed.
- `$(PY) -m pytest tests/e2e -m e2e`: Runs only the tests under that folder that carry the matching marker (markers are declared in `pyproject.toml`).

```make
java-test: ## step 7: build and test the Java (Spring AI) port
	cd java && ./mvnw -q -B verify
```

Target `java-test` (no prerequisites). Its help text, shown by `make help`: "step 7: build and test the Java (Spring AI) port".
- `cd java && ./mvnw -q -B verify`: The same wrapper, with the goal `verify`: compile, run all the tests (unit tests and the ArchUnit rules) and check the result.

```make
parity: $(STAMP) ## step 7: the Java port reproduces the Python report from the same fixtures
	cd java && ./mvnw -q -B -DskipTests package
	java -jar java/target/cost-router-java.jar --data data --prompts prompts --config config --fixtures tests/fixtures --out reports/java
	$(PY) -m cost_router.interfaces.cli parity --java reports/java --python reports
```

Target `parity` (needs `$(STAMP)` first). Its help text, shown by `make help`: "step 7: the Java port reproduces the Python report from the same fixtures".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed.
- `cd java && ./mvnw -q -B -DskipTests package`: `cd java && ...` changes into the `java` folder and, only if that worked (`&&`), runs the next command. `./mvnw` is the Maven wrapper script. `-q` quiet, `-B` batch mode (no colors or prompts), `-DskipTests` sets a property that skips the tests, `package` compiles and builds the jar file.
- `java -jar java/target/cost-router-java.jar --data data --prompts prompts --config config --fixtures tests/fixtures --out reports/java`: Runs the jar file just built. `java -jar FILE` starts the Java Virtual Machine and runs the program inside the jar; what follows are the program's own arguments.
- `$(PY) -m cost_router.interfaces.cli parity --java reports/java --python reports`: Runs the module `cost_router.interfaces.cli` of the program with the sub-command `parity` and the options `--java reports/java --python reports`. `--java DIR --python DIR` give the folders of the two programs' reports; the sub-command compares them number by number.

```make
down: ## nothing to stop: this project starts no services
	@echo "no services to stop"
```

Target `down` (no prerequisites). Its help text, shown by `make help`: "nothing to stop: this project starts no services".
- `@echo "no services to stop"`: Prints a message. Nothing is started: the default adapter replays recorded answers.

```make
lint: $(STAMP) ## ruff check, ruff format check, mypy, import-linter
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy
	$(VENV)/bin/lint-imports
```

Target `lint` (needs `$(STAMP)` first). Its help text, shown by `make help`: "ruff check, ruff format check, mypy, import-linter".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed.
- `$(VENV)/bin/ruff check .`: Runs the linter over the whole project (rules are in `pyproject.toml`).
- `$(VENV)/bin/ruff format --check .`: Checks that every file is formatted the way the formatter would write it, without changing anything. `--check` makes it return a failure status if a file would change.
- `$(VENV)/bin/mypy`: Runs the type checker with the settings in `pyproject.toml` (strict mode, over `src` and `tests`).
- `$(VENV)/bin/lint-imports`: Runs import-linter, which checks the layering rules (what may import what) written in `pyproject.toml`.

```make
format: $(STAMP) ## apply ruff's formatting and safe fixes
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/ruff format .
```

Target `format` (needs `$(STAMP)` first). Its help text, shown by `make help`: "apply ruff's formatting and safe fixes".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed.
- `$(VENV)/bin/ruff check --fix .`: Runs the linter and lets it fix what it can fix safely.
- `$(VENV)/bin/ruff format .`: Rewrites the files in the formatter's style.

```make
# Unit tests run offline against recorded model responses. The domain and application layers must stay at 95% or more.
test: $(STAMP) ## unit tests with coverage (offline, recorded model responses)
	$(PY) -m pytest tests/unit --cov=$(PKG) --cov-report=term
	$(PY) -m coverage report --include='src/$(PKG)/domain/*,src/$(PKG)/application/*' --fail-under=95
```

Target `test` (needs `$(STAMP)` first). Its help text, shown by `make help`: "unit tests with coverage (offline, recorded model responses)".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed.
- `$(PY) -m pytest tests/unit --cov=$(PKG) --cov-report=term`: Runs the unit tests. `--cov=PACKAGE` measures which lines of the package the tests executed. `--cov-report=term` prints the table in the terminal.
- `$(PY) -m coverage report --include='src/$(PKG)/domain/*,src/$(PKG)/application/*' --fail-under=95`: Reads the coverage data the previous line collected and prints a report for the `domain` and `application` folders only. `--fail-under=95` makes the command fail if the covered share is below 95%. The single quotes stop the shell from expanding the `*`.

```make
test-live: $(STAMP) ## opt-in tests against real models (RUN_LIVE=1; Claude also needs ANTHROPIC_API_KEY)
	RUN_LIVE=1 $(PY) -m pytest tests/live -m live -ra
```

Target `test-live` (needs `$(STAMP)` first). Its help text, shown by `make help`: "opt-in tests against real models (RUN_LIVE=1; Claude also needs ANTHROPIC_API_KEY)".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed.
- `RUN_LIVE=1 $(PY) -m pytest tests/live -m live -ra`: `RUN_LIVE=1` sets an environment variable for this one command only (the live tests skip themselves unless it is `1`). `-m live` selects tests marked `live`. `-ra` prints a short summary of every skipped or failed test.

```make
audit: $(STAMP) ## check the locked dependencies for known vulnerabilities
	$(VENV)/bin/pip-audit --no-deps --disable-pip -r requirements-dev.lock
```

Target `audit` (needs `$(STAMP)` first). Its help text, shown by `make help`: "check the locked dependencies for known vulnerabilities".
Prerequisites run before the recipe: `$(STAMP)` makes sure the virtual environment is installed.
- `$(VENV)/bin/pip-audit --no-deps --disable-pip -r requirements-dev.lock`: Checks every locked library against a public database of known vulnerabilities. `--no-deps` and `--disable-pip` stop it from resolving or installing anything: it only reads the lock file given by `-r`.

```make
lock: ## regenerate requirements.lock and requirements-dev.lock (needs uv)
	uv pip compile pyproject.toml --universal --generate-hashes --python-version 3.12 -o requirements.lock
	uv pip compile pyproject.toml --universal --generate-hashes --python-version 3.12 --extra dev -o requirements-dev.lock
```

Target `lock` (no prerequisites). Its help text, shown by `make help`: "regenerate requirements.lock and requirements-dev.lock (needs uv)".
- `uv pip compile pyproject.toml --universal --generate-hashes --python-version 3.12 -o requirements.lock`: `uv` is a fast Python package tool. `pip compile` turns the loose requirements in `pyproject.toml` into an exact list. `--universal` makes one list valid for every operating system, `--generate-hashes` adds the SHA-256 of each file, `--python-version 3.12` targets that Python, `-o FILE` names the output.
- `uv pip compile pyproject.toml --universal --generate-hashes --python-version 3.12 --extra dev -o requirements-dev.lock`: The same, with `--extra dev`, which also includes the development tools (pytest, ruff, mypy ...).

```make
check: lint test ## everything that needs no services
```

Target `check` (needs `lint test` first). Its help text, shown by `make help`: "everything that needs no services".
Prerequisites run before the recipe: `lint` runs the style and type checks; `test` runs the unit tests.

```make
docker-build: ## build the container image
	docker build -t ai-cost-aware-router:dev .
```

Target `docker-build` (no prerequisites). Its help text, shown by `make help`: "build the container image".
- `docker build -t ai-cost-aware-router:dev .`: Builds a container image from the `Dockerfile` in this folder. `-t NAME:TAG` names the image. The final `.` is the build context, the folder whose files the Dockerfile may copy.

```make
clean: down
	rm -rf $(VENV) logs .pytest_cache .mypy_cache .ruff_cache .import_linter_cache .coverage htmlcov
```

Target `clean` (needs `down` first).
Prerequisites run before the recipe: `down` stops anything started earlier.
- `rm -rf $(VENV) logs .pytest_cache .mypy_cache .ruff_cache .import_linter_cache .coverage htmlcov`: Deletes the listed folders and files. `-r` goes into folders, `-f` ignores missing ones and never asks.

## Try it yourself

Run these from the repository folder.

1. `grep -hE '^[a-z-]+:.*## ' Makefile | sed -E 's/:.*## /	/' | sort` lists every documented target with its help text (the `## ...` comments), one line per target, sorted. `make help` runs the same pipeline on `$(MAKEFILE_LIST)`; once a `.env` file exists, make also lists `.env` there (it was read with `-include`), `grep` then prefixes each line with the file name, and the target names are lost. That is a known flaw of the `help` target, reported as a follow-up.
2. `make -n test` (`-n` means "dry run") prints the commands `make test` would run without running them. Expect lines starting with `.venv/bin/python -m pytest tests/unit --cov=...` and a `coverage report` line.
3. `make -n install` prints the environment commands if the environment is missing, or `make: Nothing to be done` / nothing if `.venv/.installed` is up to date.
4. `touch pyproject.toml && make -n install` pretends the project file changed: the marker is now older than its prerequisite, so the install commands are printed again. This shows the date comparison at work.
5. `make --version` shows the make you are running (macOS ships GNU Make 3.81, which this Makefile works with).

## Mistakes people make

- **Spaces instead of a tab** at the start of a recipe line: make answers `*** missing separator`. The `.editorconfig` in this repository sets tabs for Makefiles (`editorconfig.md`).
- **Forgetting `.PHONY`**: a file named `test` or `run` would silently stop `make test` from running. Here every action target is in `.PHONY`.
- **Writing `$` where `$$` is needed** in a shell snippet, so make eats the variable before the shell sees it (see the `seq` loop or `$${WORKERS:-N}` in this file).
- **Expecting `cd` to carry over** to the next recipe line. It does not; join with `&&`.
- **Putting secrets in a Makefile.** Settings come from `.env` (`dotenv.md`) instead.

## Check yourself

1. **What does `.PHONY` do?**  
   It lists targets that are actions rather than files, so make always runs them even if a file with that name exists.
2. **Why is `cd java && ./mvnw verify` on one line?**  
   Make runs every recipe line in a new shell, so a `cd` on its own line would not apply to the next line.
3. **What does `$(STAMP)` as a prerequisite achieve?**  
   It makes sure the environment marker file exists and is newer than the lock file and `pyproject.toml`; if not, the install recipe runs first.
4. **What is the difference between `:=` and `?=`?**  
   `:=` always assigns (once, immediately). `?=` assigns only if the variable has no value yet, so the caller can override it.
5. **What does a `-` or `@` at the start of a recipe line mean?**  
   `@` hides the command echo; `-` ignores a failure of that command.

## Further reading

GNU Make manual: https://www.gnu.org/software/make/manual/ . This repository's Makefile is written to work with GNU Make 3.81 (the version macOS ships) and newer.
