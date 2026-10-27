# 4. Enforce the cap before the call

Status: accepted, 2026-10-27

## Context

A cap checked after a call is a log line, not a cap. But the cost of a call is only known from billed tokens, after the call.

## Decision

Before each call the router estimates its cost as three characters per token of the prompt plus the output cap, which errs high for English text, adds the label check's second sample when there is one, and refuses the call when the total would pass the smaller of the per-request cap and the money left in the day. After the run, the report compares each request's billed spend with the cap (`requests_over_cap`, `max_request_spend`).

## Consequences

- No request in the test run or the day replays passed its cap, and both days ended under budget; the guarantee holds as far as the estimate stays above the real token count, and the after-the-fact check would show if it did not.
- A conservative estimate escalates a few tasks to a person that a tighter estimate would have served.
