# 1. Record and replay model calls

Status: accepted, 2026-10-27

## Context

The study makes about 1,200 distinct model calls across three models. It must be reviewable and runnable without a key, a network or a GPU, and the Java port must be able to check itself against the Python results.

## Decision

All model calls go through the `ChatModel` port. The default adapter replays `tests/fixtures/*.jsonl`, whose lines hold a SHA-256 key over the model id, decoding settings (temperature, max tokens, seed) and every message, plus the response with its billed token counts and measured latency. A recording wrapper appends new exchanges while a real adapter runs and answers from the file when it already holds the key, so a recording run can be interrupted and resumed. A request with no recorded response is a named error (`FixtureMissError`). The Java port computes the same key.

## Alternatives considered

- **Mock objects with canned strings:** then the numbers in the report would be invented.
- **An HTTP recorder:** ties fixtures to one provider's wire format.

## Consequences

- Every number in the reports is reproducible offline, and `make test-e2e` proves it.
- A prompt change needs `make record`. Fixtures keep a readable summary of each request (messages cut at 160 characters); the key identifies the full request.
- Everything the router can ask for must have been recorded: `make checks` also records the second label samples for the test set, because the "no bar" variant of the router needs them.
