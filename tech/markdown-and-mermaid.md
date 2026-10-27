# Markdown and Mermaid diagrams

## What it is

**Markdown** is a way to write formatted text in a plain file. A `#` at the start of a line makes a heading, `-` a bullet, backticks around words make `code`, and a row of `|` makes a table. GitHub and most editors show it formatted. **Mermaid** is a text language for diagrams: a fenced block starting with ```` ```mermaid ```` is drawn as a picture by GitHub, so a diagram can live in the repository as text and be changed in a diff.

## Why this repository uses it

This repository carries 13 Markdown files: the README with the lesson's Done-when table, ARCHITECTURE.md with the diagram of the layers and data flow, the architecture decision records, the changelog, and the prompt templates the program sends to models (a prompt is a text file, so it is versioned with the code).

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `README.md` | How to run, the Done-when table, what is simplified. |
| `ARCHITECTURE.md` | The layers and a Mermaid data-flow diagram. |
| `docs/adr/*.md (5 files)` | One architecture decision record per decision. |
| `CHANGELOG.md` | What was added in each version. |
| `prompts/*.md (4 files)` | Prompt templates with `{{name}}` placeholders. |
| `reports/REPORT.md` | Generated, human-readable result reports. |


## How it works underneath

Markdown is processed by a program that turns marks into HTML. The common marks: `# Title`, `## Subtitle` (headings, the number of `#` is the level); `*italic*`, `**bold**`; `` `code` `` for short code and triple backticks for blocks (a word after the opening fence names the language); `- item` or `1. item` for lists; `[text](address)` for links; `|` columns with a `| --- |` line under the header for tables. A blank line separates paragraphs.

Mermaid is a small language that is turned into SVG drawing by JavaScript in the page that shows it. `flowchart LR` starts a flow chart; `a["text"] --> b["text"]` draws two boxes joined by an arrow; `{...}` makes a decision diamond; `[(...)]` a database cylinder; `-->` is a solid arrow and `-.->` a dashed one; `-- "words" -->` puts a label on the arrow; `<br/>` breaks a line inside a box.

## Walkthrough of this repository's use

### The diagram in `ARCHITECTURE.md`

```text
flowchart LR
    task["Task<br/>(label, refund, policy)"] --> signal{"Start tier<br/>from build set,<br/>hard signal"}
    signal --> small["Small model"]
    small --> check{"Cheap check"}
    check -- "accepted" --> done["Answer + cost log"]
    check -- "failed" --> medium["Medium model"]
    medium --> check2{"Check"}
    check2 -- "failed" --> large["Large model"]
    large --> check3{"Check"}
    check3 -- "failed" --> person["A person"]
    check2 -- "accepted" --> done
    check3 -- "accepted" --> done
    budget["Day budget<br/>(80%: no large tier;<br/>money left caps the request)"] -.-> signal
    bar["config/bar.json<br/>(agreed first)"] -.-> tune["Build-set tuning"]
    tune -.-> signal
```

`flowchart LR` means a flow chart drawn left to right. Each line below is one arrow:

| Line | Meaning |
| --- | --- |
| `task["Task<br/>(label, refund, policy)"] --> signal{"Start tier<br/>from build set,<br/>hard signal"}` | box **Task / (label, refund, policy** to decision (diamond) **Start tier / from build set, / hard signal**: solid arrow (the main flow) |
| `signal --> small["Small model"]` | decision (diamond) **Start tier / from build set, / hard signal** to box **Small model**: solid arrow (the main flow) |
| `small --> check{"Cheap check"}` | box **Small model** to decision (diamond) **Cheap check**: solid arrow (the main flow) |
| `check -- "accepted" --> done["Answer + cost log"]` | decision (diamond) **Cheap check** to box **Answer + cost log**: solid arrow (the main flow), labelled "accepted" |
| `check -- "failed" --> medium["Medium model"]` | decision (diamond) **Cheap check** to box **Medium model**: solid arrow (the main flow), labelled "failed" |
| `medium --> check2{"Check"}` | box **Medium model** to decision (diamond) **Check**: solid arrow (the main flow) |
| `check2 -- "failed" --> large["Large model"]` | decision (diamond) **Check** to box **Large model**: solid arrow (the main flow), labelled "failed" |
| `large --> check3{"Check"}` | box **Large model** to decision (diamond) **Check**: solid arrow (the main flow) |
| `check3 -- "failed" --> person["A person"]` | decision (diamond) **Check** to box **A person**: solid arrow (the main flow), labelled "failed" |
| `check2 -- "accepted" --> done` | decision (diamond) **Check** to box **Answer + cost log**: solid arrow (the main flow), labelled "accepted" |
| `check3 -- "accepted" --> done` | decision (diamond) **Check** to box **Answer + cost log**: solid arrow (the main flow), labelled "accepted" |
| `budget["Day budget<br/>(80%: no large tier;<br/>money left caps the request)"] -.-> signal` | box **Day budget / (80%: no large tier; / money left caps the request** to decision (diamond) **Start tier / from build set, / hard signal**: dashed arrow (a side effect or a reference) |
| `bar["config/bar.json<br/>(agreed first)"] -.-> tune["Build-set tuning"]` | box **config/bar.json / (agreed first** to box **Build-set tuning**: dashed arrow (a side effect or a reference) |
| `tune -.-> signal` | box **Build-set tuning** to decision (diamond) **Start tier / from build set, / hard signal**: dashed arrow (a side effect or a reference) |

### The shape of a decision record

`docs/adr/0001-record-and-replay-model-calls.md` has these headings:

```markdown
# 1. Record and replay model calls
## Context
## Decision
## Alternatives considered
## Consequences
```

- The title is the number and the decision in a few words.
- *Context* says what problem made a decision necessary.
- *Decision* says what was chosen.
- *Alternatives considered* lists what was rejected and why.
- *Consequences* says what follows from the choice, good and bad. A reader six months later can understand the code's shape without asking anyone.

### The prompt templates

A prompt file is plain text. `{{name}}` marks a place the program fills in; the pattern that finds it is explained in `regular-expressions.md`. Keeping prompts in files under `prompts/` means a change to a prompt is a visible change in git, with a version in the file name (for example `classify.v2.md`) where the repository uses that habit.

## Try it yourself

1. `grep -n '^#' README.md | head -20` lists the README's headings, i.e. its outline.
2. `grep -c '^|' README.md` counts the table rows.
3. `awk '/^```mermaid/{f=1;next} /^```/{f=0} f' ARCHITECTURE.md` prints only the diagram source.
4. Paste that source into https://mermaid.live to see the drawing and edit it.
5. `ls docs/adr` lists the decision records in numeric order.

## Mistakes people make

- **A missing blank line** before a list or table, which then renders as part of the previous paragraph.
- **A table row with a different number of `|` than the header.**
- **A Mermaid label containing quotes or brackets without double quotes around the whole label.**
- **Editing generated reports by hand**: the next run overwrites them. Change the code or the data instead.
- **Treating the README as a log.** The README says how it is now; the changelog says what changed.

## Check yourself

1. **How do you make a level-2 heading?**  
   Start the line with `##` and a space.
2. **What does a fenced block with the word `mermaid` do on GitHub?**  
   It is drawn as a diagram.
3. **What does `-.->` mean in Mermaid?**  
   A dashed arrow.
4. **What are the four parts of an ADR?**  
   Context, Decision, Alternatives considered, Consequences.
5. **Why are prompts stored as files?**  
   So that a change to a prompt is versioned and reviewed like code.

## Further reading

CommonMark specification: https://spec.commonmark.org/ . GitHub Flavored Markdown: https://github.github.com/gfm/ . Mermaid flowcharts: https://mermaid.js.org/syntax/flowchart.html . ADRs: https://adr.github.io/
