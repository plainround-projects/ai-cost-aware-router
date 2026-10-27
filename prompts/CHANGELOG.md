# Prompt changelog

Prompts are versioned by file name (`name.vN.md`). The fixture key hashes the rendered prompt, so any edit needs
`make record` to add the new exchanges.

| Prompt | Version | Date | Change |
| --- | --- | --- | --- |
| label | v2 | 2026-10-27 | Category definitions and four examples, answer with one word. Replaces v1, whose first line ("You classify customer support emails") made `llama3.2:1b` answer "support" for 86 of 120 emails; v1 was run once while building and is not in the committed fixtures. |
| refund | v2 | 2026-10-27 | Policy and order text; at most two short lines of working, then a final `Refund: 12.50` line. Replaces v1 (amount only), which the three models mostly got wrong without working (4% to 12%). |
| policy | v2 | 2026-10-27 | The ten policy lines, the exact format with one worked example, "copied word for word". Replaces v1 (no example), where the two smaller models often did not quote. |
