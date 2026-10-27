# Changelog

## 0.1.0 - 2026-10-27

- Domain: tasks and refund arithmetic, answer parsing, ground-truth grading, the label, refund and policy checks (and a stronger policy overlap check), the price table, router configuration, day budget, the difficulty signal, rate and bootstrap metrics.
- Application: model tiers, answer checks, the cost-aware router with a per-request cap and a day budget, and the experiments of each lesson step.
- Infrastructure: recorded, OpenAI-compatible and Anthropic chat-model adapters behind one port, versioned prompt files, JSON logging, validated settings.
- Data: 300 tasks (120 label, 100 refund, 80 policy) split 150 build and 150 test; agreed bars committed before any model answered.
- Recorded fixtures: about 1,200 real exchanges with `qwen2.5:0.5b`, `llama3.2:1b` and `qwen2.5:1.5b` served by ollama 0.40.6.
- Java (Spring AI 2.0.1) port with ArchUnit and a parity test against the Python reports.
- CI: format, lint, types, import rules, unit tests with coverage, audit, e2e replay, Java build.
