# YAML

## What it is

YAML ("YAML Ain't Markup Language") is a text format for structured data: nested lists and key-value pairs, written with indentation instead of brackets. It is meant to be easy for people to read and edit. Configuration files for CI services, Docker Compose and many other tools use it.

## Why this repository uses it

The CI workflow `.github/workflows/ci.yml` is written in YAML because GitHub Actions requires it.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `.github/workflows/ci.yml` | The CI workflow. |


## How it works underneath

YAML has three building blocks.

- **Mapping**: `key: value` lines. A value can be text, a number, `true`/`false`, a list, or another mapping.
- **Sequence** (list): lines that start with `- `, or a bracketed `[a, b]`.
- **Scalar**: a single value. Text is usually written without quotes; quote it when it could be mistaken for something else (`"3.13"`, `"yes"`, a value with a `#` or `: `).

**Indentation is meaning.** Children are indented more than their parent, with spaces only; tabs are not allowed. A `#` starts a comment. Because parsers guess types, the notorious trap is that `3.10` becomes the number 3.1 and `no`/`on` can become booleans in older YAML 1.1 parsers (GitHub's `on:` key is deliberately special-cased). Quote values when in doubt. This repository only uses the plain subset above: no anchors, no multi-document files.

## Walkthrough of this repository's use

The first job of the workflow, line by line (the whole file is explained in `github-actions.md`).

`.github/workflows/ci.yml`

```yaml
name: ci
```

A **key** (`name`), a colon, a space, and a **value** (`ci`). YAML text values need no quotes.

```yaml
on: [push, pull_request]
```

`[push, pull_request]` is a **list** written on one line, items separated by commas: run this workflow on both events.

```yaml
jobs:
```

A key whose value is not on the same line: the indented lines below it are its value, a **mapping** (keys with values).

```yaml
  check:
```

Indentation by two spaces is the structure. `check` is a key inside `jobs`; its value is the indented mapping below.

```yaml
    name: Format, lint, types, import rules, offline tests with coverage, dependency audit
```

A human-readable label for the job (a text value; it contains commas and is still one string).

```yaml
    runs-on: ubuntu-latest
```

The type of machine.

```yaml
    steps:
```

A key whose value is a list; the items follow, each starting with a dash.

```yaml
      - uses: actions/checkout@v4
```

A list item: a dash starts it. It contains a mapping with one key, `uses`.

```yaml
      - uses: actions/setup-python@v5
        with:
```

The next list item. Its mapping continues on the lines below, indented to line up with `uses`.

```yaml
          python-version: "3.13"
```

A text value in double quotes. Quotes are needed here: `3.13` without them would be read as the number 3.13, and `3.10` would become `3.1`.

```yaml
      - run: make check
      - run: make audit
      - run: make test-e2e
```

A list item whose key is `run`: a shell command. Any further `- run:` items below it are more commands, run one after the other.

## Try it yourself

1. `python3 -c "import json,sys; print('no yaml in the standard library')"` reminds you that Python needs a library for YAML; the CI file is only read by GitHub.
2. `ruby -ryaml -e 'puts YAML.load_file(".github/workflows/ci.yml")["jobs"].keys.inspect'` (Ruby ships with macOS) prints the job names as a list, showing how the nesting reads.
3. Break the indentation of one line in a copy (`cp .github/workflows/ci.yml /tmp/ci.yml`, edit `/tmp/ci.yml`) and run the command above on it: Ruby reports a syntax error with a line number.

## Mistakes people make

- **Tabs** for indentation: not allowed.
- **Unquoted version numbers** (`3.10` read as 3.1).
- **Inconsistent indentation**: a line indented one space too much silently becomes a child of the wrong key.
- **A colon followed by a space inside a value** without quotes: it is read as a new mapping.

## Check yourself

1. **How does YAML show that one key belongs inside another?**  
   By indenting it further, with spaces.
2. **What does a leading `- ` mean?**  
   A list item.
3. **Why is `python-version: "3.13"` quoted?**  
   Without quotes it is the number 3.13; `3.10` would lose its zero.
4. **Can YAML use tabs for indentation?**  
   No.
5. **What starts a comment?**  
   A `#`.

## Further reading

YAML 1.2 specification: https://yaml.org/spec/1.2.2/ . GitHub's workflow syntax: https://docs.github.com/actions/reference/workflow-syntax-for-github-actions
