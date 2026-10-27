"""Parsing a model's answer, grading it against the gold answer (what is true), and the checks the router can run
without the gold answer (what it can see).

A grader answers "was it right?" and is used only to measure. A check answers "may the router accept this?" and is
what the router uses; the lesson's point is that the two can disagree.
"""

from __future__ import annotations

import re

from cost_router.domain.tasks import LABELS, POLICY_LINES, Kind, Task, expected_refund_cents

NUMBER = r"\$?\s*(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{1,2}))?"
REFUND_LINE = re.compile(r"refund\s*:\s*" + NUMBER, re.IGNORECASE)
BARE_AMOUNT = re.compile(NUMBER)
QUOTE = re.compile(r"quote\s*:\s*[\"“']?(.+?)[\"”']?\s*$", re.IGNORECASE | re.MULTILINE)


def normalize(text: str) -> str:
    """Lower case, collapsed spaces, no trailing full stop."""
    return " ".join(text.lower().split()).rstrip(".").strip()


def parse_label(text: str) -> str | None:
    """The answer as one of the allowed labels, or None (anything else, however close, is not a label)."""
    word = normalize(text).strip("\"'`*")
    return word if word in LABELS else None


def _cents(match: re.Match[str]) -> int:
    dollars = int(match.group(1).replace(",", ""))
    return dollars * 100 + int(((match.group(2) or "") + "00")[:2])


def parse_amount_cents(text: str) -> int | None:
    """The amount of the answer's last `Refund:` line, or the whole answer when it is just an amount; else None."""
    matches = list(REFUND_LINE.finditer(text))
    if matches:
        return _cents(matches[-1])
    bare = BARE_AMOUNT.fullmatch(text.strip())
    return _cents(bare) if bare else None


def parse_quote(text: str) -> str | None:
    """The line the answer quotes (the first `Quote:` line), or None."""
    match = QUOTE.search(text)
    return normalize(match.group(1)) if match else None


def quoted_line_index(text: str) -> int | None:
    """Which policy line the quote is, or None when the quote is not an exact policy line."""
    quote = parse_quote(text)
    if quote is None:
        return None
    for index, line in enumerate(POLICY_LINES):
        if normalize(line) == quote:
            return index
    return None


def is_correct(task: Task, text: str) -> bool:
    """The ground truth: did the model get this task right?"""
    if task.kind is Kind.LABEL:
        return parse_label(text) == task.gold
    if task.kind is Kind.REFUND:
        return parse_amount_cents(text) == expected_refund_cents(task)
    return quoted_line_index(text) == task.gold


def check_label_shape(text: str) -> bool:
    """Shape only: the answer is one of the allowed labels."""
    return parse_label(text) is not None


def check_label_agreement(text: str, second: str) -> bool:
    """Shape, and a second sample (another temperature and seed) gave the same label."""
    first_label = parse_label(text)
    return first_label is not None and first_label == parse_label(second)


def check_refund(task: Task, text: str) -> bool:
    """The amount equals the one recomputed by code from the order and the policy."""
    return parse_amount_cents(text) == expected_refund_cents(task)


STOPWORDS = frozenset(
    {
        *("a", "an", "the", "of", "to", "in", "on", "for", "is", "are", "be", "do", "does", "can", "i", "my", "me"),
        *("you", "your", "we", "our", "it", "its", "if", "or", "and", "at", "by", "from", "with", "as", "how", "what"),
        *("when", "who", "which", "that", "this", "there", "than", "then"),
    }
)


def content_words(text: str) -> set[str]:
    """Lower-case words of a text without the common function words, with a plural `s` removed."""
    words = (w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS)
    return {w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words}


def best_matching_line(question: str) -> int | None:
    """The policy line sharing the most content words with the question, or None when two lines tie for most."""
    words = content_words(question)
    scores = [len(words & content_words(line)) for line in POLICY_LINES]
    top = max(scores)
    return scores.index(top) if top > 0 and scores.count(top) == 1 else None


def check_policy_overlap(question: str, text: str) -> bool:
    """Stronger than `check_policy`: the quoted line must also be the line that best matches the question's words."""
    index = quoted_line_index(text)
    return index is not None and index == best_matching_line(question)


def check_policy(text: str) -> bool:
    """The answer quotes a policy line that exists (it does not say the line is the right one)."""
    return quoted_line_index(text) is not None
