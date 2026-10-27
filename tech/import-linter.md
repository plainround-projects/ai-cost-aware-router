# import-linter 2.15 (architecture rules as tests)

## What it is

An `import` statement in one Python file makes it depend on another file. If every file may import every other file, the structure decays into tangles. **import-linter** reads the imports of the whole package (it does not run the code), builds the graph of who imports whom, and checks it against rules you write in `pyproject.toml`. It is run with the command `lint-imports`.

## Why this repository uses it

This repository promises a layered design: the domain (plain rules and data) knows nothing about the application (the steps), which knows nothing about infrastructure (files, HTTP, databases), which knows nothing about the interfaces (the command line, the web endpoints). That promise is only true if a machine checks it. The second rule keeps vendor libraries out of the inner layers so the inner code can be tested without them.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `pyproject.toml` | `[tool.importlinter]` and its two contracts. |
| `Makefile` | `make lint` runs `lint-imports`. |
| `.github/workflows/ci.yml` | CI runs it through `make check`. |
| `src/cost_router/* (37 files)` | The four layer folders the contracts name. |


## How it works underneath

import-linter first imports no code. It uses a library called *grimp* to parse the source files and record each `import`. Then each **contract** is evaluated.

A **layers** contract lists packages from highest to lowest. A higher layer may import a lower one; a lower layer must not import a higher one, directly or through a chain of other modules (import-linter follows indirect chains). A **forbidden** contract says that some source packages must not import some named modules, directly or indirectly. With `include_external_packages = true`, third-party libraries such as `httpx` are part of the graph, so they can be named as forbidden.

When a rule is broken, the output shows the shortest import chain that breaks it, so you can see exactly which line to change. The exit code is non-zero, which makes `make lint` fail.

## Walkthrough of this repository's use

### The contracts

`pyproject.toml`

```toml
[tool.importlinter]
root_package = "cost_router"
include_external_packages = true
```

- `[tool.importlinter]`: Settings of import-linter (`import-linter.md`).
- `root_package = "cost_router"`: The package whose imports are checked.
- `include_external_packages = true`: Also see imports of libraries (needed by the "forbidden" contract).

```toml
[[tool.importlinter.contracts]]
name = "Layers: interfaces -> infrastructure -> application -> domain, never upward"
type = "layers"
layers = [
    "cost_router.interfaces",
    "cost_router.infrastructure",
    "cost_router.application",
    "cost_router.domain",
]
```

- `[[tool.importlinter.contracts]]`: One architecture rule ("contract").
- `name = "Layers: interfaces -> infrastructure -> application -> domain, never upward"`: The distribution name, as pip would list it.
- `type = "layers"`: A layers contract: modules listed first may import modules listed later, never the other way round.
- `layers = [`: The layers from top to bottom: `cost_router.interfaces`, `cost_router.infrastructure`, `cost_router.application`, `cost_router.domain`. The top layer may import everything below it; `domain` may import nothing above it.

```toml
[[tool.importlinter.contracts]]
name = "Domain and application know no vendor SDK or transport library"
type = "forbidden"
source_modules = ["cost_router.domain", "cost_router.application"]
forbidden_modules = ["httpx", "anthropic", "openai"]
```

- `[[tool.importlinter.contracts]]`: One architecture rule ("contract").
- `name = "Domain and application know no vendor SDK or transport library"`: The distribution name, as pip would list it.
- `type = "forbidden"`: A forbidden contract: the listed source modules must not import the forbidden ones, directly or through other modules.
- `source_modules = ["cost_router.domain", "cost_router.application"]`: The modules that are restricted.
- `forbidden_modules = ["httpx", "anthropic", "openai"]`: The libraries they must never import: `httpx`, `anthropic`, `openai`. That keeps vendor and transport code in the infrastructure layer.

### How it is run

The `Makefile` rule `lint` ends with `$(VENV)/bin/lint-imports`, quoted in `ruff.md`. Python code that breaks the rules would be, for example, a line `import httpx` in a domain module: the second contract fails and prints the chain from the domain module to `httpx`.

## Try it yourself

1. `.venv/bin/lint-imports` prints the two contract names, each followed by `KEPT`, and ends with `Contracts: 2 kept, 0 broken.`
2. Add `import httpx` to the top of any file under `src/cost_router/domain/`, and run it again: the second contract is `BROKEN` and the chain is printed. Undo with `git checkout .`.
3. `.venv/bin/lint-imports --verbose` also prints how many files and dependencies were analysed.

## Mistakes people make

- **Only checking direct imports.** A forbidden library can sneak in through a helper module; import-linter reports indirect chains, which is why the contract works.
- **Putting the rule only in a document.** A rule in a README is a wish; a contract in CI is a check.
- **Importing inside a function to dodge the check.** The tool still sees function-level imports, which is the point.
- **Forgetting `root_package`.** Without it the tool does not know which package to analyse.

## Check yourself

1. **What does a layers contract forbid?**  
   A lower layer importing a higher layer, directly or indirectly.
2. **Why is `httpx` listed as forbidden for the domain and application?**  
   So that the inner layers can be tested without a network library and are not tied to a vendor.
3. **Does import-linter run your code?**  
   No, it reads the imports from the source files.
4. **What does `include_external_packages = true` allow?**  
   Naming third-party libraries in contracts.
5. **What does the output show when a rule is broken?**  
   The chain of imports that connects the forbidden pair.

## Further reading

import-linter documentation: https://import-linter.readthedocs.io/ (contract types: layers, forbidden). Pinned version: 2.15.
