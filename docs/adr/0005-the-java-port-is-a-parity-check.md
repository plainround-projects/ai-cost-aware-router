# 5. The Java port is a parity check

Status: accepted, 2026-10-27

## Context

The lesson asks for the router in Python and in Java on Spring AI, with the Java numbers inside the Python intervals.

## Decision

The Java program reads the same `data/`, `prompts/`, `config/` and `tests/fixtures/` and writes `router.json`, `day.json` and `audit.json` in the Python format, including its own tuning of the router configuration. Everything that could differ between the languages is written to match: the fixture hash input, the SplitMix64 bootstrap and shuffle, prompt rendering, answer parsing, the order of tasks. `ParityTest` and `make parity` compare every number to 1e-6. The live adapter is Spring AI's `ChatClient` over `OpenAiChatModel`, in the infrastructure package only; ArchUnit forbids `domain` and `application` from touching Spring or the OpenAI SDK.

## Consequences

- "Inside the Python intervals" is stronger than asked: the Java numbers equal the Python numbers, and the Java tuner reproduces `config/router.json`.
- A live Java run varies like any live run and then needs the interval check.
