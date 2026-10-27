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
| [data-files.md](data-files.md) | Every JSON Lines data, fixture and result file, with its keys and its full content. |
| [docker.md](docker.md) | The image build: Dockerfile, ignore file and the non-root user. |
| [dotenv.md](dotenv.md) | Environment variables, `.env` files and every setting this repository reads. |
| [editorconfig.md](editorconfig.md) | Editor settings that keep tabs, spaces and line endings consistent. |
| [git.md](git.md) | History as evidence: numbers committed before the experiment, and what `.gitignore` keeps out. |
| [github-actions.md](github-actions.md) | The CI workflow, job by job. |
| [httpx.md](httpx.md) | The HTTP client behind the model adapters. |
| [import-linter.md](import-linter.md) | The layer rules that keep vendor code out of the inner layers. |
| [jackson.md](jackson.md) | Jackson 3, the JSON reader of the Java half. |
| [java.md](java.md) | The Java 21 half of the repository and its value types. |
| [java-main.md](java-main.md) | Every main Java class, quoted and explained statement by statement. |
| [java-tests.md](java-tests.md) | Every Java test class, quoted and explained. |
| [json.md](json.md) | JSON and JSON Lines: reports, agreed-first numbers and recorded exchanges. |
| [junit.md](junit.md) | The Java tests, including the parity test against the Python reports. |
| [make.md](make.md) | The task runner: every `make` target, line by line. |
| [markdown-and-mermaid.md](markdown-and-mermaid.md) | README, decision records, prompts and the architecture diagram. |
| [maven.md](maven.md) | The Java build file and the Maven wrapper. |
| [maven-wrapper-scripts.md](maven-wrapper-scripts.md) | The `mvnw` and `mvnw.cmd` scripts, line by line. |
| [mypy.md](mypy.md) | The static type checker in strict mode. |
| [ollama.md](ollama.md) | The local model server used to record real answers. |
| [pip-and-venv.md](pip-and-venv.md) | The private environment and the hash-pinned lock files that rebuild it exactly. |
| [pip-audit.md](pip-audit.md) | The check of locked libraries against known vulnerabilities. |
| [pytest.md](pytest.md) | The test runner, its markers and the test files. |
| [python.md](python.md) | The language of all the code, with the shared building blocks read line by line. |
| [python-application.md](python-application.md) | Every application-layer Python file, quoted and explained statement by statement. |
| [python-domain.md](python-domain.md) | Every domain-layer Python file, quoted and explained statement by statement. |
| [python-infrastructure.md](python-infrastructure.md) | Every infrastructure-layer Python file (the adapters), quoted and explained. |
| [python-interfaces.md](python-interfaces.md) | The command line and the wiring, quoted and explained. |
| [python-scripts.md](python-scripts.md) | The data-making and setup scripts, quoted and explained. |
| [python-tests.md](python-tests.md) | Every Python test file, quoted and explained. |
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
2. [python-domain.md](python-domain.md): Every domain-layer Python file, quoted and explained statement by statement.
3. [python-application.md](python-application.md): Every application-layer Python file, quoted and explained statement by statement.
4. [python-infrastructure.md](python-infrastructure.md): Every infrastructure-layer Python file (the adapters), quoted and explained.
5. [python-interfaces.md](python-interfaces.md): The command line and the wiring, quoted and explained.
6. [python-scripts.md](python-scripts.md): The data-making and setup scripts, quoted and explained.
7. [python-tests.md](python-tests.md): Every Python test file, quoted and explained.
8. [bash.md](bash.md): The shell: how the Makefile recipes and scripts run commands.
9. [make.md](make.md): The task runner: every `make` target, line by line.
10. [git.md](git.md): History as evidence: numbers committed before the experiment, and what `.gitignore` keeps out.
11. [pip-and-venv.md](pip-and-venv.md): The private environment and the hash-pinned lock files that rebuild it exactly.
12. [uv.md](uv.md): The tool that resolves the lock files.
13. [setuptools.md](setuptools.md): The build backend that makes the project installable.
14. [toml.md](toml.md): The format of `pyproject.toml`, quoted and explained line by line.
15. [dotenv.md](dotenv.md): Environment variables, `.env` files and every setting this repository reads.
16. [editorconfig.md](editorconfig.md): Editor settings that keep tabs, spaces and line endings consistent.
17. [markdown-and-mermaid.md](markdown-and-mermaid.md): README, decision records, prompts and the architecture diagram.
18. [json.md](json.md): JSON and JSON Lines: reports, agreed-first numbers and recorded exchanges.
19. [yaml.md](yaml.md): The syntax of the CI workflow and other YAML files.
20. [regular-expressions.md](regular-expressions.md): Every pattern in the code, explained piece by piece.
21. [sha-256.md](sha-256.md): The fingerprint function behind recorded answers, lock files and file checks.
22. [concurrency.md](concurrency.md): Threads, locks and processes used by the experiments.
23. [httpx.md](httpx.md): The HTTP client behind the model adapters.
24. [chat-model-apis.md](chat-model-apis.md): Chat requests, the two wire formats, and record/replay of model answers.
25. [ollama.md](ollama.md): The local model server used to record real answers.
26. [ruff.md](ruff.md): The linter and formatter, with this repository's rule set.
27. [mypy.md](mypy.md): The static type checker in strict mode.
28. [import-linter.md](import-linter.md): The layer rules that keep vendor code out of the inner layers.
29. [pytest.md](pytest.md): The test runner, its markers and the test files.
30. [coverage-py.md](coverage-py.md): Line and branch coverage with the 95 percent gate on the inner layers.
31. [pip-audit.md](pip-audit.md): The check of locked libraries against known vulnerabilities.
32. [docker.md](docker.md): The image build: Dockerfile, ignore file and the non-root user.
33. [github-actions.md](github-actions.md): The CI workflow, job by job.
34. [java.md](java.md): The Java 21 half of the repository and its value types.
35. [java-main.md](java-main.md): Every main Java class, quoted and explained statement by statement.
36. [maven.md](maven.md): The Java build file and the Maven wrapper.
37. [maven-wrapper-scripts.md](maven-wrapper-scripts.md): The `mvnw` and `mvnw.cmd` scripts, line by line.
38. [jackson.md](jackson.md): Jackson 3, the JSON reader of the Java half.
39. [spring-ai.md](spring-ai.md): The Spring AI adapter that is the only class allowed to see the framework.
40. [junit.md](junit.md): The Java tests, including the parity test against the Python reports.
41. [java-tests.md](java-tests.md): Every Java test class, quoted and explained.
42. [archunit.md](archunit.md): The architecture rules as a Java test.
43. [data-files.md](data-files.md): Every JSON Lines data, fixture and result file, with its keys and its full content.

## If you have ten minutes

- [python.md](python.md): The language of all the code, with the shared building blocks read line by line.
- [make.md](make.md): The task runner: every `make` target, line by line.
- [chat-model-apis.md](chat-model-apis.md): Chat requests, the two wire formats, and record/replay of model answers.
