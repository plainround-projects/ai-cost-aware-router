# pip-audit 2.10.1

## What it is

Security researchers publish lists of **known vulnerabilities** in libraries, each with an identifier (for example `PYSEC-2024-1` or a CVE number) and the versions that are affected. **pip-audit** takes your list of libraries with exact versions and asks a vulnerability database whether any of them is on such a list.

## Why this repository uses it

The lock files fix the exact versions, which makes the check meaningful: the audit covers what the repository would really install. `make audit` is part of CI, so a newly published vulnerability in a locked library turns the build red until the pin is updated.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `Makefile` | `make audit` runs `pip-audit`. |
| `.github/workflows/ci.yml` | CI runs `make audit`. |
| `requirements-dev.lock` | The list that is audited. |


## How it works underneath

pip-audit reads a requirements file, takes each `name==version` pair, and sends the pairs to the Python Packaging Advisory Database (through the PyPI JSON API). The answer lists any advisory whose affected range includes your version, with the fixed version if one exists. Because it contacts the internet, `make audit` needs network access, and its result can change from day to day even if your files do not. With `--no-deps` pip-audit does not try to resolve dependencies (the lock file already lists them all) and `--disable-pip` stops it from creating a temporary environment; both are only valid because every version is pinned.

## Walkthrough of this repository's use

### The command

`Makefile`

```make
audit: $(STAMP) ## check the locked dependencies for known vulnerabilities
	$(VENV)/bin/pip-audit --no-deps --disable-pip -r requirements-dev.lock
```

`$(VENV)/bin/pip-audit` is the program. `--no-deps` and `--disable-pip` say: trust the list as it stands. `-r requirements-dev.lock` reads the pinned list (the development lock contains the runtime libraries as well). Output is a table of vulnerable libraries, or `No known vulnerabilities found`, and a non-zero exit status in the first case.

### In CI

`.github/workflows/ci.yml`

```yaml
      - run: make audit
```

The step runs the same command in a fresh machine.

## Try it yourself

1. `make audit` (needs internet) prints `No known vulnerabilities found` when the pins are clean.
2. `.venv/bin/pip-audit --version` prints the pinned version.
3. `echo 'requests==2.19.0' > /tmp/old.txt && .venv/bin/pip-audit --no-deps --disable-pip -r /tmp/old.txt` reports advisories for that old version: this shows what a failure looks like (the file is outside the repository).

## Mistakes people make

- **Auditing without pins.** A loose list gives no reliable answer.
- **Treating a green audit as proof of safety.** It only reports vulnerabilities that are known and published.
- **Ignoring a red audit** because the vulnerable code path is not used: decide consciously and record it, do not silence the check.
- **Running offline** and reading the error as a vulnerability.

## Check yourself

1. **What two things does pip-audit compare?**  
   Exact library versions from your list and published advisories.
2. **Why does `make audit` need the internet?**  
   It asks a remote vulnerability database.
3. **Why are `--no-deps` and `--disable-pip` allowed?**  
   Because the lock file already pins every library.
4. **Can the audit result change without any file changing?**  
   Yes: new advisories are published over time.
5. **Where does CI run it?**  
   In the `check` job, after `make check`.

## Further reading

pip-audit: https://pypi.org/project/pip-audit/ . Advisory database: https://github.com/pypa/advisory-database . Pinned version: 2.10.1.
