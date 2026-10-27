# Regular expressions

## What it is

A **regular expression** (regex) is a short text that describes a pattern of characters, such as "two digits, a dash, two digits". A regex engine can test whether a text contains the pattern, find all the places where it occurs, cut out parts of the match, or replace it. Python's engine is the standard-library module `re`; Java's is `java.util.regex`.

## Why this repository uses it

The program reads free text from models and from users and must pick facts out of it: an order id, a refund amount, a label like `A` or `B`, a citation such as `[kb-12]`, an e-mail address to hide, or a phrase such as "ignore previous instructions". Regular expressions do this in one line each, and the same pattern can be written in the Java port.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/cost_router/application/templates.py` | 1 regular expression(s) |
| `src/cost_router/domain/checks.py` | 4 regular expression(s) |
| `src/cost_router/domain/tasks.py` | 1 regular expression(s) |
| `java/src/main/java/dev/plainround/router/application/Templates.java` | Java port of the patterns (`java.util.regex`). |
| `java/src/main/java/dev/plainround/router/domain/Checks.java` | Java port of the patterns (`java.util.regex`). |
| `java/src/main/java/dev/plainround/router/domain/Tasks.java` | Java port of the patterns (`java.util.regex`). |
| `src/cost_router/application/templates.py` | The `{{name}}` placeholder pattern. |


## How it works underneath

A regex is built from a few pieces.

- **Literal characters** match themselves. `refund` matches the text `refund`.
- **Classes**: `[abc]` any one of a, b or c; `[0-9]` a digit; `[^x]` anything except x. Shortcuts: `\d` digit, `\w` letter/digit/underscore, `\s` whitespace; capital letters mean the opposite. `.` is any character except newline.
- **Quantifiers** say how often the previous piece repeats: `*` zero or more, `+` one or more, `?` zero or one, `{2,4}` two to four. They are *greedy* (take as much as possible); a following `?` makes them *lazy*.
- **Anchors** match positions, not characters: `^` start, `$` end, `\b` the boundary between a word character and a non-word character.
- **Groups**: `( ... )` groups and *captures*; `(?: ... )` groups without capturing; `|` means or.
- **Look-around**: `(?<=x)` and `(?<!x)` look backward, `(?=x)` and `(?!x)` look forward; they test the surroundings without consuming them.
- **Flags**: `(?i)` ignore case, `(?m)` make `^`/`$` work per line.

How the engine works: it tries to match the pattern at the first position of the text, then at the next, until it succeeds or the text ends. At each step it follows the pattern; when a choice (an alternative or a quantifier) fails later, it **backtracks** and tries another choice. A badly written pattern can backtrack an enormous number of times on some inputs, which is why patterns here are short and anchored on word boundaries.

In Python: `re.compile(p)` prepares a pattern once; `.search(text)` finds the first match anywhere; `.fullmatch` must match the whole text; `.findall` returns all matches; `.sub(repl, text)` replaces; `.split` cuts. Use **raw strings** (`r"..."`) so that `\d` is not read as an escape by Python itself.

## Walkthrough of this repository's use

### The placeholder pattern

`src/cost_router/application/templates.py`

<!-- fmt: off -->
```python
PLACEHOLDER = re.compile(r"\{\{([a-z_]+)\}\}")
```
<!-- fmt: on -->

`PLACEHOLDER` finds `{{name}}` in a template: `\{\{` and `\}\}` are the literal braces, `(` ... `)` captures the name, `[a-z_]+` is one or more lowercase letters or underscores. The `r` before the quote makes it a **raw string**: backslashes are kept as they are, which regular expressions need.

### Every pattern in the Python source

Each table reads the pattern from left to right, in the order the engine meets the pieces. A piece with a quantifier is shown with it.

#### `src/cost_router/application/templates.py` line 7

<!-- fmt: off -->
```python
PLACEHOLDER = re.compile(r"\{\{([a-z_]+)\}\}")
```
<!-- fmt: on -->

The pattern, as text: `\{\{([a-z_]+)\}\}`

| Part | Meaning |
| --- | --- |
| `\{` | the character `{` itself |
| `\{` | the character `{` itself |
| `(` | start of a capturing group (its match can be read afterwards) |
| `[a-z_]+` | any one of `a` to `z`, `_`, one or more times |
| `)` | end of the group |
| `\}` | the character `}` itself |
| `\}` | the character `}` itself |

#### `src/cost_router/domain/checks.py` line 15

<!-- fmt: off -->
```python
REFUND_LINE = re.compile(r"refund\s*:\s*" + NUMBER, re.IGNORECASE)
```
<!-- fmt: on -->

The pattern, as text: `refund\s*:\s*\$?\s*(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{1,2}))?`

| Part | Meaning |
| --- | --- |
| `refund` | the literal text |
| `\s*` | whitespace (space, tab, newline), zero or more times |
| `:` | the literal text |
| `\s*` | whitespace (space, tab, newline), zero or more times |
| `\$?` | the character `$` itself, optional (zero or one time) |
| `\s*` | whitespace (space, tab, newline), zero or more times |
| `(` | start of a capturing group (its match can be read afterwards) |
| `\d{1,3}` | a digit 0-9, 1 to 3 times |
| `(?:` | start of a group that is not captured |
| `,` | the literal text |
| `\d{3}` | a digit 0-9, exactly 3 times |
| `)+` | end of the group; the whole group is repeated: one or more times |
| `\|` | or: either what is on the left or what is on the right |
| `\d+` | a digit 0-9, one or more times |
| `)` | end of the group |
| `(?:` | start of a group that is not captured |
| `\.` | the character `.` itself |
| `(` | start of a capturing group (its match can be read afterwards) |
| `\d{1,2}` | a digit 0-9, 1 to 2 times |
| `)` | end of the group |
| `)?` | end of the group; the whole group is repeated: optional (zero or one time) |

#### `src/cost_router/domain/checks.py` line 16

<!-- fmt: off -->
```python
BARE_AMOUNT = re.compile(NUMBER)
```
<!-- fmt: on -->

The pattern, as text: `\$?\s*(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{1,2}))?`

| Part | Meaning |
| --- | --- |
| `\$?` | the character `$` itself, optional (zero or one time) |
| `\s*` | whitespace (space, tab, newline), zero or more times |
| `(` | start of a capturing group (its match can be read afterwards) |
| `\d{1,3}` | a digit 0-9, 1 to 3 times |
| `(?:` | start of a group that is not captured |
| `,` | the literal text |
| `\d{3}` | a digit 0-9, exactly 3 times |
| `)+` | end of the group; the whole group is repeated: one or more times |
| `\|` | or: either what is on the left or what is on the right |
| `\d+` | a digit 0-9, one or more times |
| `)` | end of the group |
| `(?:` | start of a group that is not captured |
| `\.` | the character `.` itself |
| `(` | start of a capturing group (its match can be read afterwards) |
| `\d{1,2}` | a digit 0-9, 1 to 2 times |
| `)` | end of the group |
| `)?` | end of the group; the whole group is repeated: optional (zero or one time) |

#### `src/cost_router/domain/checks.py` line 17

<!-- fmt: off -->
```python
QUOTE = re.compile(r"quote\s*:\s*[\"“']?(.+?)[\"”']?\s*$", re.IGNORECASE | re.MULTILINE)
```
<!-- fmt: on -->

The pattern, as text: `quote\s*:\s*[\"“']?(.+?)[\"”']?\s*$`

| Part | Meaning |
| --- | --- |
| `quote` | the literal text |
| `\s*` | whitespace (space, tab, newline), zero or more times |
| `:` | the literal text |
| `\s*` | whitespace (space, tab, newline), zero or more times |
| `[\"“']?` | any one of `"`, `“`, `'`, optional (zero or one time) |
| `(` | start of a capturing group (its match can be read afterwards) |
| `.+?` | any one character except a newline, one or more times, as few as possible (lazy) |
| `)` | end of the group |
| `[\"”']?` | any one of `"`, `”`, `'`, optional (zero or one time) |
| `\s*` | whitespace (space, tab, newline), zero or more times |
| `$` | the end of the text (or of a line with the `m` flag) |

#### `src/cost_router/domain/checks.py` line 98

<!-- fmt: off -->
```python
words = (w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS)
```
<!-- fmt: on -->

The pattern, as text: `[a-z0-9]+`

| Part | Meaning |
| --- | --- |
| `[a-z0-9]+` | any one of `a` to `z`, `0` to `9`, one or more times |

#### `src/cost_router/domain/tasks.py` line 30

<!-- fmt: off -->
```python
ORDER_ID = re.compile(r"\bPR-\d{6}\b")
```
<!-- fmt: on -->

The pattern, as text: `\bPR-\d{6}\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `PR-` | the literal text |
| `\d{6}` | a digit 0-9, exactly 6 times |
| `\b` | a backspace (only inside a class) |

### Java

These Java files use `Pattern` or `String.matches`/`replaceAll`. The syntax is the same for everything above, except that a backslash must be doubled inside a Java string (`"\\d"` is the pattern `\d`), and flags can be written as `Pattern.CASE_INSENSITIVE`.

- `java/src/main/java/dev/plainround/router/application/Templates.java`
- `java/src/main/java/dev/plainround/router/domain/Checks.java`
- `java/src/main/java/dev/plainround/router/domain/Tasks.java`

## Try it yourself

1. `python3 -c "import re; print(re.findall(r'\bPR-\d{6}\b', 'orders PR-123456 and PR-99'))"` prints `['PR-123456']`: the second does not have six digits.
2. `python3 -c "import re; print(re.sub(r'\s+', ' ', 'a   b \n c'))"` prints `a b c`.
3. `python3 -c "import re; m = re.search(r'(\d+)-(\d+)', 'pages 10-20'); print(m.group(0), m.group(1), m.group(2))"` prints `10-20 10 20`.
4. `python3 -c "import re; print(re.findall(r'a.*b', 'a1b2b'), re.findall(r'a.*?b', 'a1b2b'))"` prints `['a1b2b'] ['a1b']`: greedy against lazy.
5. Open https://regex101.com in a browser, choose the Python flavor and paste one of the patterns above; it draws the same explanation.

## Mistakes people make

- **Forgetting the raw-string prefix** so `\b` becomes a backspace character.
- **Unescaped dots**: `PR-12.34` also matches `PR-12x34`. Use `\.`.
- **Greedy matching across too much text** (`.*`); use a class that excludes the end character, or a lazy quantifier.
- **No anchors**: `\d{6}` also matches inside a longer number; `\b` stops that.
- **Parsing nested structure** (HTML, JSON) with a regex. Use a parser.
- **Trusting a regex as security**: the guardrail rules are a first filter, which the red-team suite measures; they are not a guarantee.

## Check yourself

1. **What does `\b` match?**  
   A boundary between a word character and a non-word character; it consumes no text.
2. **What is the difference between `(...)` and `(?:...)`?**  
   The first captures its match for later reading; the second only groups.
3. **What does a trailing `?` after `*` change?**  
   It makes the repetition lazy: as few characters as possible.
4. **Why use raw strings for patterns in Python?**  
   So backslashes reach the regex engine unchanged.
5. **What does `re.search` return when nothing matches?**  
   `None`.

## Further reading

Python `re` module and the regex HOWTO: https://docs.python.org/3/library/re.html , https://docs.python.org/3/howto/regex.html . Java `java.util.regex.Pattern`: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/regex/Pattern.html
