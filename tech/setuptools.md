# setuptools (the build backend)

## What it is

A Python **package** is a folder of code plus a description that tells installers how to build and install it. A **build backend** is the program that turns the project folder into an installable *wheel* (`pip-and-venv.md`). **setuptools** is the oldest and most common backend. Modern projects declare the backend in `pyproject.toml` and `pip` calls it; nobody runs `setup.py` by hand any more.

## Why this repository uses it

`pip install -e .` must find the code under `src/`, include the data files that the program reads at run time, and create the command-line launcher. setuptools does these three things from a few lines of `pyproject.toml`.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `pyproject.toml` | `[build-system]`, `[tool.setuptools.*]`, `[project.scripts]`. |
| `src/cost_router/py.typed` | An empty marker file that tells type checkers the package carries type annotations (PEP 561). |
| `Makefile` | `pip install -e .`. |


## How it works underneath

`pip` reads `[build-system]`, installs the `requires` list into a temporary environment, then calls the backend named in `build-backend` with a standard function (`build_wheel` or, for an editable install, `build_editable`). setuptools finds the packages (`packages.find` with `where = ["src"]` looks for folders with code under `src/`), collects the data files named in `package-data`, writes the metadata from `[project]`, and creates the launcher scripts from `[project.scripts]`. A **wheel** is a zip with a fixed layout that pip can unpack. In an **editable** install the environment gets a small link file that points at `src/`, so changes are visible without reinstalling.

## Walkthrough of this repository's use

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

The table `[project.scripts]` (explained line by line in `toml.md`) is also handled by setuptools: it creates the launcher program in `.venv/bin`.

## Try it yourself

1. `.venv/bin/pip show -f ai-cost-aware-router | head -20` shows the installed metadata and, in editable mode, a small `.pth`/finder file instead of copied code.
2. `.venv/bin/python -c "import cost_router, sys; print(cost_router.__file__)"` prints a path under `src/`: the code is used in place.
3. `ls .venv/bin | grep -i "cost-router"` lists the launcher created from `[project.scripts]`.
4. `.venv/bin/pip wheel --no-deps -w /tmp/wheelcheck .` builds a wheel into a temporary folder (needs internet for the build requirement the first time); `unzip -l /tmp/wheelcheck/*.whl | head` lists what a user would receive.

## Mistakes people make

- **Data files that are not declared** in `package-data`: the code works from the source folder (editable install) and fails after a normal install.
- **Putting code outside `src/`** so `packages.find` does not see it.
- **Editing `pyproject.toml` and not reinstalling** when a new launcher or data file is added.
- **Mixing old `setup.py` instructions** with the declarative file.

## Check yourself

1. **What is a build backend?**  
   The program that turns the project folder into an installable wheel.
2. **What does an editable install do?**  
   Links the environment to the source folder, so edits take effect at once.
3. **What is `py.typed` for?**  
   It tells type checkers the package's annotations may be used.
4. **Why declare `package-data`?**  
   So data files are included in the installed package.
5. **Where is the launcher command defined?**  
   Under `[project.scripts]` in `pyproject.toml`.

## Further reading

setuptools documentation: https://setuptools.pypa.io/ . Packaging guide: https://packaging.python.org/en/latest/ . Pinned requirement: `setuptools>=75` in `[build-system]`.
