# 3. Measure every check against the truth

Status: accepted, 2026-10-27

## Context

A check that looks reasonable can still accept wrong answers. The label check "is one of the four words" is a perfectly valid test of shape and says nothing about correctness.

## Decision

Grading and checking are separate: `domain/checks.py::is_correct` knows the gold answer and is used only to measure; the `check_*` functions see only the answer (and, for refunds, the structured order, which is the same data the grader uses, so that check is an oracle by construction). `check_results` runs each check on every tier's real answers and reports the false-accept rate (wrong answers accepted over wrong answers), the false-reject rate, and the share of accepted answers that are wrong.

## Consequences

- The tuner can drop a tier for a kind with data instead of by intuition, and the audit can say which check let which answer through.
- The refund check's 0% false-accept rate is not evidence of a good check; the README says so.
