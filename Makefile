PYTHON ?= $(shell command -v python3.13 || command -v python3.12 || command -v python3)
VENV := .venv
PY := $(VENV)/bin/python
STAMP := $(VENV)/.installed
PKG := cost_router

-include .env
export

.PHONY: help install env up run test test-live lint format audit lock check docker-build down clean models checks tune router day report record test-e2e java-test parity false-accepts

help: ## list the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/' | sort

$(STAMP): requirements-dev.lock pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -q --require-hashes -r requirements-dev.lock
	$(VENV)/bin/pip install -q --no-deps -e .
	touch $@

install: $(STAMP) ## create .venv from the hash-pinned lock file

env:
	@[ -f .env ] || { cp .env.example .env; echo "created .env from .env.example"; }

CLI := $(PY) -m cost_router.interfaces.cli
RECORD ?= tests/fixtures/recorded.jsonl

up: env $(STAMP) ## create .venv and .env (no services: the default adapter replays recorded responses)
	@echo "ready: make run | make test | make lint"

run: $(STAMP) env ## the whole study from recorded responses: models, checks, tuning, router, day, audit, report
	$(CLI) all

models: $(STAMP) env ## step 1: each model alone on the 150 build tasks
	$(CLI) models

checks: $(STAMP) env ## step 2: false-accept and false-reject rate of each check on the build set
	$(CLI) checks

tune: $(STAMP) env ## step 3: derive config/router.json from the build set only
	$(CLI) tune

router: $(STAMP) env ## step 5: the router and each single model on the 150 test tasks
	$(CLI) router

day: $(STAMP) env ## step 4: the test tasks replayed as one day under a budget
	$(CLI) day

false-accepts: $(STAMP) env ## step 6: test-set false accepts by tier and check, and one change to the weakest check
	$(CLI) audit

report: $(STAMP) env ## write reports/REPORT.md from the stored results
	$(CLI) report

# Needs ollama running with the three models in .env.example. New exchanges are appended; known ones are not repeated.
record: $(STAMP) ## re-run everything against local models and append the exchanges to $(RECORD)
	LLM_PROVIDER=local LLM_RECORD_TO=$(RECORD) WORKERS=$${WORKERS:-3} $(CLI) all

test-e2e: $(STAMP) ## regenerate the reports from the fixtures and compare them with the committed ones
	$(PY) -m pytest tests/e2e -m e2e

java-test: ## step 7: build and test the Java (Spring AI) port
	cd java && ./mvnw -q -B verify

parity: $(STAMP) ## step 7: the Java port reproduces the Python report from the same fixtures
	cd java && ./mvnw -q -B -DskipTests package
	java -jar java/target/cost-router-java.jar --data data --prompts prompts --config config --fixtures tests/fixtures --out reports/java
	$(PY) -m cost_router.interfaces.cli parity --java reports/java --python reports

down: ## nothing to stop: this project starts no services
	@echo "no services to stop"

lint: $(STAMP) ## ruff check, ruff format check, mypy, import-linter
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy
	$(VENV)/bin/lint-imports

format: $(STAMP) ## apply ruff's formatting and safe fixes
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/ruff format .

# Unit tests run offline against recorded model responses. The domain and application layers must stay at 95% or more.
test: $(STAMP) ## unit tests with coverage (offline, recorded model responses)
	$(PY) -m pytest tests/unit --cov=$(PKG) --cov-report=term
	$(PY) -m coverage report --include='src/$(PKG)/domain/*,src/$(PKG)/application/*' --fail-under=95

test-live: $(STAMP) ## opt-in tests against real models (RUN_LIVE=1; Claude also needs ANTHROPIC_API_KEY)
	RUN_LIVE=1 $(PY) -m pytest tests/live -m live -ra

audit: $(STAMP) ## check the locked dependencies for known vulnerabilities
	$(VENV)/bin/pip-audit --no-deps --disable-pip -r requirements-dev.lock

lock: ## regenerate requirements.lock and requirements-dev.lock (needs uv)
	uv pip compile pyproject.toml --universal --generate-hashes --python-version 3.12 -o requirements.lock
	uv pip compile pyproject.toml --universal --generate-hashes --python-version 3.12 --extra dev -o requirements-dev.lock

check: lint test ## everything that needs no services

docker-build: ## build the container image
	docker build -t ai-cost-aware-router:dev .

clean: down
	rm -rf $(VENV) logs .pytest_cache .mypy_cache .ruff_cache .import_linter_cache .coverage htmlcov
