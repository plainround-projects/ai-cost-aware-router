# Git

## What it is

Git is a program that records the history of a folder of files. Every time you **commit**, git stores a snapshot of the files together with a message, the author and the date. You can go back to any snapshot, compare two snapshots, and keep separate lines of work (**branches**). The folder plus its history is a **repository**; the hidden folder `.git` inside it holds the history.

## Why this repository uses it

This repository uses git for two things beyond saving work. First, the history is evidence: a number that is meant to be a prediction (a threshold, a memory estimate) is committed **before** the experiment that tests it, so the commit date shows it was not adjusted afterwards. Second, git decides what is *not* in the repository: `.gitignore` keeps the virtual environment, caches, logs, `.env` and large model files out.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `.gitignore` | Names the files git must never track. |
| `CHANGELOG.md` | A human-written list of what changed between releases. |
| `docs/adr/* (5 files)` | Decision records; each one is also a commit you can find in the history. |


## How it works underneath

Git stores three kinds of objects, each named by a hash (see `sha-256.md`; git uses SHA-1 or SHA-256 of the content): a **blob** (a file's bytes), a **tree** (a folder: a list of names pointing to blobs and trees) and a **commit** (a pointer to one tree, to the parent commit(s), plus author, date, message). A branch is only a movable label pointing to a commit. Because a commit's name depends on its content and its parent, you cannot change an old commit without changing every later name, which is why history is trustworthy.

Files have three places: the **working tree** (what you see), the **index** or staging area (what `git add` prepared) and the **repository** (what `git commit` saved). `git status` compares them. `git diff` shows changes not yet staged; `git diff --staged` shows what the next commit will contain. `git log` walks the parents from the current commit backward.

A file listed in `.gitignore` is not shown by `git status` and is not added by `git add .`. Ignoring does not remove a file that is already tracked.

## Walkthrough of this repository's use

### The history of this repository

These are the latest commits (`git log --format='%h %ad %s' --date=short`):

```text
e3d8e9d 2026-10-27 docs: add tech/, one note per technology used here (33 files and an index)
bfbaa90 2026-10-27 build: check in the Maven wrapper and use it from the Makefile
4a66528 2026-10-27 docs: add README, ARCHITECTURE, ADRs and CHANGELOG
b122b48 2026-10-27 docs(reports): commit the results of the first full run
c0900c5 2026-10-27 feat(config): add the router configuration derived from the build set
bfb1746 2026-10-27 test(fixtures): record about 1,200 real exchanges with qwen2.5:0.5b, llama3.2:1b and qwen2.5:1.5b
059d843 2026-10-27 feat(java): add the Spring AI port with ArchUnit and a parity test
cb959f9 2026-10-27 test: add unit, e2e replay and opt-in live tests
45220d1 2026-10-27 feat(data): add the 300 tasks, the policy lines and the generator
90c5ab4 2026-10-27 feat(interfaces): add the command-line program and the composition root
732e599 2026-10-27 feat(infrastructure): add recorded, OpenAI-compatible and Anthropic model adapters, data, settings and logging
e8e7232 2026-10-27 feat(application): add model tiers, answer checks, the cost-aware router and the experiments
```

Each line is: short commit name, date, and the message. The messages follow the *conventional commits* habit: a type (`feat`, `fix`, `docs`, `test`, `chore`) then a colon and a summary.

### Numbers committed before the experiment

- `config/bar.json` was first added in commit `6284d97` (2026-10-27): docs(config): fix the agreed bars and limits before any model answers

You can verify each with `git log --diff-filter=A --format='%h %ad %s' --date=short -- <file>` (`--diff-filter=A` keeps commits that **A**dded the file). Compare its date and position with the commit that added the reports, to see that the number came first.

### `.gitignore`

`.gitignore`

```text
.venv/
__pycache__/
*.pyc
*.egg-info/
build/
dist/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.import_linter_cache/
.coverage
htmlcov/
```

- `.venv/`: the virtual environment (rebuilt by `make install`)
- `__pycache__/`: Python's compiled bytecode folders
- `*.pyc`: compiled bytecode files
- `*.egg-info/`: metadata made when the project is installed in editable mode
- `build/`: build output
- `dist/`: packaging output
- `.pytest_cache/`: pytest's cache
- `.mypy_cache/`: mypy's cache
- `.ruff_cache/`: ruff's cache
- `.import_linter_cache/`: import-linter's cache
- `.coverage`: the raw coverage data file
- `htmlcov/`: coverage's HTML report

```text
.env
.DS_Store
logs/
.omc/
java/target/
reports/java/
```

- `.env`: your local settings (they can hold keys, so never commit them; `.env.example` is committed instead)
- `.DS_Store`: macOS folder metadata
- `logs/`: log files
- `.omc/`: local state of a coding assistant tool
- `java/target/`: Maven's build output
- `reports/java/`: reports written by the Java program (regenerated)

## Try it yourself

1. `git log --oneline | head -5` shows the five latest commits, one per line.
2. `git status --short` prints nothing when the working tree is clean.
3. `git show --stat HEAD` shows the latest commit's message and the files it touched.
4. `git check-ignore -v .env` prints the `.gitignore` line that ignores `.env` (file, line number, pattern).
5. `git ls-files | wc -l` counts the tracked files.

## Mistakes people make

- **Committing a secret or a big file by mistake.** Deleting it in the next commit does not remove it from history.
- **Expecting `.gitignore` to untrack a file** that is already committed. Use `git rm --cached FILE` first.
- **Vague messages** ("fix stuff"). The message is the only explanation a future reader gets.
- **Doing `git add .` without `git status`**: you may stage generated files.
- **Rewriting shared history** (`rebase`, `filter-branch`) after others have pulled it.

## Check yourself

1. **What does a commit contain?**  
   A pointer to a snapshot (tree), the parent commit(s), the author, the date and a message.
2. **Why commit a threshold before the experiment?**  
   The commit date proves the threshold was not adjusted after seeing the result.
3. **What does `git status --short` print for a clean tree?**  
   Nothing.
4. **Does adding a file to `.gitignore` remove it from the repository?**  
   No. It only stops untracked files from being added; a tracked file needs `git rm --cached`.
5. **What is a branch?**  
   A movable label that points to a commit.

## Further reading

Pro Git book: https://git-scm.com/book . Reference: https://git-scm.com/docs . Version used while building: the git that ships with macOS developer tools (`git --version`).
