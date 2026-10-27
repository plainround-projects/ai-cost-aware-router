# Technology notes

These notes explain every technology that appears in `ai-cost-aware-router`, one file per technology, for a reader who has never met any of them. Each file has the same nine parts: what it is, why this repository uses it, where it appears, how it works underneath, a walkthrough of this repository's own files and commands, things to try yourself, common mistakes, five questions to check yourself, and further reading. Code in the walkthroughs is quoted exactly from the repository (or, for `.env.example`, from the text its generator wrote), so you can open the file and follow along.

## Files

| File | Role in this repository |
| --- | --- |
| [archunit.md](archunit.md) | The architecture rules as a Java test. |
| [bash.md](bash.md) | The shell: how the Makefile recipes and scripts run commands. |
| [chat-model-apis.md](chat-model-apis.md) | Chat requests, the two wire formats, and record/replay of model answers. |
| [concurrency.md](concurrency.md) | Threads, locks and processes used by the experiments. |
| [coverage-py.md](coverage-py.md) | Line and branch coverage with the 95 percent gate on the inner layers. |
| [docker.md](docker.md) | The image build: Dockerfile, ignore file and the non-root user. |
| [dotenv.md](dotenv.md) | Environment variables, `.env` files and every setting this repository reads. |
| [editorconfig.md](editorconfig.md) | Editor settings that keep tabs, spaces and line endings consistent. |
| [git.md](git.md) | History as evidence: numbers committed before the experiment, and what `.gitignore` keeps out. |
| [github-actions.md](github-actions.md) | The CI workflow, job by job. |
| [httpx.md](httpx.md) | The HTTP client behind the model adapters. |
| [import-linter.md](import-linter.md) | The layer rules that keep vendor code out of the inner layers. |
| [jackson.md](jackson.md) | Jackson 3, the JSON reader of the Java half. |
| [java.md](java.md) | The Java 21 half of the repository and its value types. |
| [json.md](json.md) | JSON and JSON Lines: reports, agreed-first numbers and recorded exchanges. |
| [junit.md](junit.md) | The Java tests, including the parity test against the Python reports. |
| [make.md](make.md) | The task runner: every `make` target, line by line. |
| [markdown-and-mermaid.md](markdown-and-mermaid.md) | README, decision records, prompts and the architecture diagram. |
| [maven.md](maven.md) | The Java build file and the Maven wrapper. |
| [mypy.md](mypy.md) | The static type checker in strict mode. |
| [ollama.md](ollama.md) | The local model server used to record real answers. |
| [pip-and-venv.md](pip-and-venv.md) | The private environment and the hash-pinned lock files that rebuild it exactly. |
| [pip-audit.md](pip-audit.md) | The check of locked libraries against known vulnerabilities. |
| [pytest.md](pytest.md) | The test runner, its markers and the test files. |
| [python.md](python.md) | The language of all the code, with the shared building blocks read line by line. |
| [regular-expressions.md](regular-expressions.md) | Every pattern in the code, explained piece by piece. |
| [ruff.md](ruff.md) | The linter and formatter, with this repository's rule set. |
| [setuptools.md](setuptools.md) | The build backend that makes the project installable. |
| [sha-256.md](sha-256.md) | The fingerprint function behind recorded answers, lock files and file checks. |
| [spring-ai.md](spring-ai.md) | The Spring AI adapter that is the only class allowed to see the framework. |
| [toml.md](toml.md) | The format of `pyproject.toml`, quoted and explained line by line. |
| [uv.md](uv.md) | The tool that resolves the lock files. |
| [yaml.md](yaml.md) | The syntax of the CI workflow and other YAML files. |

## Reading order

Read the language first, then the build tools, then the pieces that run, then the tests and checks.

1. [python.md](python.md): The language of all the code, with the shared building blocks read line by line.
2. [bash.md](bash.md): The shell: how the Makefile recipes and scripts run commands.
3. [make.md](make.md): The task runner: every `make` target, line by line.
4. [git.md](git.md): History as evidence: numbers committed before the experiment, and what `.gitignore` keeps out.
5. [pip-and-venv.md](pip-and-venv.md): The private environment and the hash-pinned lock files that rebuild it exactly.
6. [uv.md](uv.md): The tool that resolves the lock files.
7. [setuptools.md](setuptools.md): The build backend that makes the project installable.
8. [toml.md](toml.md): The format of `pyproject.toml`, quoted and explained line by line.
9. [dotenv.md](dotenv.md): Environment variables, `.env` files and every setting this repository reads.
10. [editorconfig.md](editorconfig.md): Editor settings that keep tabs, spaces and line endings consistent.
11. [markdown-and-mermaid.md](markdown-and-mermaid.md): README, decision records, prompts and the architecture diagram.
12. [json.md](json.md): JSON and JSON Lines: reports, agreed-first numbers and recorded exchanges.
13. [yaml.md](yaml.md): The syntax of the CI workflow and other YAML files.
14. [regular-expressions.md](regular-expressions.md): Every pattern in the code, explained piece by piece.
15. [sha-256.md](sha-256.md): The fingerprint function behind recorded answers, lock files and file checks.
16. [concurrency.md](concurrency.md): Threads, locks and processes used by the experiments.
17. [httpx.md](httpx.md): The HTTP client behind the model adapters.
18. [chat-model-apis.md](chat-model-apis.md): Chat requests, the two wire formats, and record/replay of model answers.
19. [ollama.md](ollama.md): The local model server used to record real answers.
20. [ruff.md](ruff.md): The linter and formatter, with this repository's rule set.
21. [mypy.md](mypy.md): The static type checker in strict mode.
22. [import-linter.md](import-linter.md): The layer rules that keep vendor code out of the inner layers.
23. [pytest.md](pytest.md): The test runner, its markers and the test files.
24. [coverage-py.md](coverage-py.md): Line and branch coverage with the 95 percent gate on the inner layers.
25. [pip-audit.md](pip-audit.md): The check of locked libraries against known vulnerabilities.
26. [docker.md](docker.md): The image build: Dockerfile, ignore file and the non-root user.
27. [github-actions.md](github-actions.md): The CI workflow, job by job.
28. [java.md](java.md): The Java 21 half of the repository and its value types.
29. [maven.md](maven.md): The Java build file and the Maven wrapper.
30. [jackson.md](jackson.md): Jackson 3, the JSON reader of the Java half.
31. [spring-ai.md](spring-ai.md): The Spring AI adapter that is the only class allowed to see the framework.
32. [junit.md](junit.md): The Java tests, including the parity test against the Python reports.
33. [archunit.md](archunit.md): The architecture rules as a Java test.

## If you have ten minutes

- [python.md](python.md): The language of all the code, with the shared building blocks read line by line.
- [make.md](make.md): The task runner: every `make` target, line by line.
- [chat-model-apis.md](chat-model-apis.md): Chat requests, the two wire formats, and record/replay of model answers.
