# 2. Agree the bars before the results

Status: accepted, 2026-10-27

## Context

"This check is too lenient" and "the router matched the large model" are only claims if the thresholds were chosen without looking at the scores.

## Decision

`config/bar.json` was committed alone (`6284d97`) before any model answered a task: a false-accept limit of 10%, a hard-task accuracy floor of 50% for the small tier, an accuracy margin of 2 points against the large model, a per-request cap of $0.0008, the 80% tightening point, and the two day budgets (50% and 30% of the always-large cost). `tune` reads the bar; nothing edits it afterwards.

## Consequences

- The bar turned out strict for kinds where a model is right most of the time but its check cannot tell right from wrong (medium on policy: 95% accuracy, false-accept 100%). The policy kind therefore starts at the large tier. The report shows both the false-accept rate and the share of accepted answers that are wrong, so a reader can see what a looser bar would trade; `router_no_bar` in the report is that trade, measured.
