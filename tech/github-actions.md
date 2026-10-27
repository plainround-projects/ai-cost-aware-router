# GitHub Actions (continuous integration)

## What it is

**Continuous integration** (CI) means: every time someone pushes code, a machine builds it and runs all the checks, and tells everyone the result. **GitHub Actions** is GitHub's CI service. A **workflow** is a YAML file in `.github/workflows/`. It contains **jobs**; each job runs on a fresh virtual machine and executes **steps** in order: either a shell command (`run:`) or a ready-made **action** (`uses:`) such as "check out the code".

## Why this repository uses it

Checks you must remember to run are checks you will forget. The workflow runs the same `make` targets you run locally, on a clean machine with nothing left over from your computer, so "works on my machine" is not an answer. It also proves that the repository's instructions (README, Makefile) are complete.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `.github/workflows/ci.yml` | The one workflow of this repository. |


## How it works underneath

When GitHub sees a push or pull request (the `on:` events), it looks for workflow files, starts one virtual machine per job (`runs-on: ubuntu-latest` is a Linux machine), and runs the steps in order. If a step's command exits non-zero, the job stops and is marked failed (unless the step says otherwise). Jobs run in parallel unless one declares that it needs another. The machine is thrown away afterwards, so nothing persists between runs.

`uses: actions/checkout@v4` downloads your repository into the machine; `@v4` selects a major version of that action. `actions/setup-python` and `actions/setup-java` install the language versions you ask for. `with:` passes the action its inputs. `if: always()` makes a step run even when an earlier step failed; it is used for clean-up. Docker is preinstalled on the Linux machines, which is why the integration job here can start a database container.

## Walkthrough of this repository's use

`.github/workflows/ci.yml`

```yaml
name: ci
```

- `name: ci`: The workflow's name, shown in the Actions tab.

```yaml
on: [push, pull_request]
```

- `on: [push, pull_request]`: When it runs: on every push to any branch and on every pull request.

```yaml
jobs:
  check:
    name: Format, lint, types, import rules, offline tests with coverage, dependency audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: make check
      - run: make audit
      - run: make test-e2e
```

- `jobs:`: A workflow is a set of jobs. Jobs run in parallel unless one declares that it needs another.
- `check:`: A job with the id `check`.
- `name: Format, lint, types, import rules, offline tests with coverage, dependency audit`: The job's display name.
- `runs-on: ubuntu-latest`: The job runs on a fresh virtual machine with a recent Ubuntu Linux.
- `steps:`: The list of steps; they run one after the other in the same machine.
- `- uses: actions/checkout@v4`: Downloads this repository's files onto the machine. `uses` runs a prepared action published by GitHub; `@v4` is its version.
- `- uses: actions/setup-python@v5`: Installs Python.
- `with:`: The inputs of the action above.
- `python-version: "3.13"`: Use Python 3.13 (a string, so `3.13` is not read as the number 3.13).
- `- run: make check`: Runs `make check` on the runner, the same command you run on your machine. That is why CI and your terminal cannot disagree about what a check is.
- `- run: make audit`: Runs `make audit` on the runner, the same command you run on your machine. That is why CI and your terminal cannot disagree about what a check is.
- `- run: make test-e2e`: Runs `make test-e` on the runner, the same command you run on your machine. That is why CI and your terminal cannot disagree about what a check is.

```yaml
  java:
    name: Java port (Spring AI): unit tests, ArchUnit, parity with the Python reports
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "21"
          cache: maven
          cache-dependency-path: java/pom.xml
      - run: make java-test
```

- `java:`: A job with the id `java`.
- `name: Java port (Spring AI): unit tests, ArchUnit, parity with the Python reports`: The job's display name.
- `runs-on: ubuntu-latest`: The job runs on a fresh virtual machine with a recent Ubuntu Linux.
- `steps:`: The list of steps; they run one after the other in the same machine.
- `- uses: actions/checkout@v4`: Downloads this repository's files onto the machine. `uses` runs a prepared action published by GitHub; `@v4` is its version.
- `- uses: actions/setup-java@v4`: Installs a Java Development Kit.
- `with:`: The inputs of the action above.
- `distribution: temurin`: The Eclipse Temurin build of OpenJDK.
- `java-version: "21"`: Java 21 (the oldest version the project supports).
- `cache: maven`: Keeps downloaded Maven libraries between runs to save time.
- `cache-dependency-path: java/pom.xml`: The file whose content decides when the Maven cache is renewed.
- `- run: make java-test`: Runs `make java-test` on the runner, the same command you run on your machine. That is why CI and your terminal cannot disagree about what a check is.

## Try it yourself

1. `grep -E '^  [a-z-]+:$' .github/workflows/ci.yml` lists the job names.
2. Run the same commands a job runs: `make check && make audit` should end with exit status 0 (`echo $?` prints 0).
3. On GitHub, open the **Actions** tab after a push: each job is a row with a green tick or a red cross, and clicking a step shows its log. (This repository has no remote configured; the workflow is ready for one.)
4. `ruby -ryaml -e 'p YAML.load_file(".github/workflows/ci.yml")["on"]'` shows the events (Ruby may print `true` as the key, because YAML 1.1 reads `on` as a boolean; GitHub handles it).

## Mistakes people make

- **A workflow that works only because of your machine's state** (installed tools, files ignored by git). CI starts clean; if it fails there, something was undocumented.
- **Unpinned actions.** `@v4` follows a moving major version; pinning to a commit hash is stricter.
- **Putting secrets into the file.** Use GitHub's encrypted secrets; this repository needs none, because tests replay recorded answers.
- **Expecting jobs to share files.** Each job has its own machine.

## Check yourself

1. **What is a job?**  
   A group of steps that runs on one fresh virtual machine.
2. **What does `uses:` do compared with `run:`?**  
   `uses:` runs a packaged action; `run:` runs a shell command.
3. **What does `if: always()` do?**  
   Runs the step even when an earlier step failed.
4. **Why does CI call `make` targets?**  
   So CI and your terminal run exactly the same commands.
5. **Do jobs share a file system?**  
   No, each job starts on a new machine.

## Further reading

GitHub Actions documentation: https://docs.github.com/actions . Workflow syntax: https://docs.github.com/actions/reference/workflow-syntax-for-github-actions
