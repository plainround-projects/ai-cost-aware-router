# Python scripts, file by file

## What it is

Scripts are Python files in the `scripts/` folder that are run directly, not imported. They make the data sets, build hand-written cases, or fetch a model. They are not part of the installed package.

## Why this repository uses it

The data sets in `data/` are not typed by hand. A script generates them from a fixed seed, so anyone can recreate them and see exactly how they were made.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `scripts/make_data.py` | Quoted and explained in the walkthrough below. |


## How it works underneath

A script is run as `python scripts/name.py`. Python sets `__name__` to `"__main__"` for the file that was started, so the block `if __name__ == "__main__":` runs only then. Scripts use the same libraries as the package.

## Walkthrough of this repository's use

### Files in this note

| File | Lines | What it is |
| --- | --- | --- |
| `scripts/make_data.py` | 223 | Generate data/tasks.jsonl deterministically (seed 2026): 300 tasks whose answers code can check. |

Each file below is quoted exactly, in order, in pieces of about a dozen lines. Under each piece, a bullet list explains every statement in the order it appears. The first time an idea shows up in this note it is explained in a bullet that begins **New idea**.

#### `scripts/make_data.py`

<!-- fmt: off -->
```python
"""Generate data/tasks.jsonl deterministically (seed 2026): 300 tasks whose answers code can check.

120 category labels, 100 refund amounts and 80 short policy answers; some easy, some hard; split once into 150 for
building the router (`split: build`) and 150 for the final test (`split: test`), stratified by kind and difficulty.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from cost_router.domain.tasks import POLICY_LINES, REFUND_POLICY, refund_cents
```
<!-- fmt: on -->

- **New idea.** A **docstring** is a text in triple quotes as the first statement of a module, class or function. Python keeps it as documentation and tools can show it.
- `"""Generate data/tasks.jsonl deterministically (seed 2026): 300 tasks whose answers cod...`: a docstring (documentation text). It says: "Generate data/tasks.jsonl deterministically (seed 2026): 300 tasks whose answers code can check."
- **New idea.** `from __future__ import annotations` turns on a newer behaviour: type annotations are stored as text instead of being evaluated when the file loads.
- **New idea.** An **import** makes the code of another module available. `import x` gives the whole module under the name `x`; `from x import y` gives just the name `y`.
- `from __future__ import annotations`: switches on a newer language behaviour: annotations are stored as text, so a class can be named in an annotation before it is defined, and `X | None` works everywhere.
- `import json`: imports the module(s) `json` so this file can use them. `json` is reading and writing JSON text.
- `import random`: imports the module(s) `random` so this file can use them. `random` is random numbers.
- `from pathlib import Path`: takes the name(s) `Path` from the module `pathlib` (file-system paths as objects).
- `from cost_router.domain.tasks import POLICY_LINES, REFUND_POLICY, refund_cents`: takes the name(s) `POLICY_LINES, REFUND_POLICY, refund_cents` from the module `cost_router.domain.tasks` (a module of this project).

<!-- fmt: off -->
```python
DATA = Path(__file__).resolve().parent.parent / "data"

LABEL_BANKS: dict[str, dict[str, list[str]]] = {
    "billing": {
        "core": [
            "I was charged twice for the same order and I want one of the charges reversed.",
            "My card was billed {amount} but the invoice says {other}. Please explain the difference.",
            "Why is there a pending charge on my card for an order I cancelled?",
            "I need a copy of my invoice for last month's payment.",
            "The discount code was not applied and I paid the full price. Please fix the charge.",
        ],
        "distractor": [
            "The parcel did arrive, by the way.",
            "I may also change my password later.",
            "My order number is {order}.",
        ],
    },
    "shipping": {
        "core": [
            "My package still has not arrived and the tracking has not moved for a week.",
            "The tracking page says delivered but nothing is at my door.",
            "Can you change the delivery address for order {order} before it ships?",
            "How long will delivery take to {city}?",
            "The courier left my parcel with a neighbor I do not know. Where is it?",
        ],
        "distractor": [
            "I paid by card without problems.",
            "I might return something else later.",
            "My account email is the same as always.",
        ],
    },
    "returns": {
        "core": [
            "I want to send back the jacket from order {order} because it does not fit.",
            "How do I return an item that I bought last week?",
            "The lamp arrived broken and I would like to return it for a replacement.",
            "Please send me a return label for order {order}.",
            "I changed my mind about the headphones. What is the process to give them back?",
        ],
        "distractor": [
            "I was charged {amount} for it.",
            "Delivery was fast, thank you.",
            "I could not log in to the site yesterday.",
        ],
    },
    "account": {
        "core": [
            "I cannot log in to my account, the password reset email never arrives.",
            "Please change the email address on my account to a new one.",
            "How do I delete my account and my saved data?",
            "My account shows someone else's name. Can you check it?",
            "I want to turn off marketing emails from my account settings but the page fails.",
        ],
        "distractor": [
            "I have an order {order} in progress.",
            "I was billed {amount} last month.",
            "The delivery was on time.",
        ],
    },
}
```
<!-- fmt: on -->

- **New idea.** An **assignment** `name = value` makes the name point at the value. A name written in capital letters is, by convention, a constant: it is not meant to change.
- `DATA = Path(__file__).resolve().parent.parent / "data"`: sets `DATA` to the value of `Path(__file__).resolve().parent.parent / 'data'`. `Path(__file__).resolve()` is the absolute form of the path `Path(__file__)`; `Path(__file__)` is the file path `__file__`.
- **New idea.** An **annotated assignment** `name: type = value` also says what kind of value the name should hold. The annotation is a hint for readers and for mypy (`mypy.md`); Python does not enforce it.
- `LABEL_BANKS: dict[str, dict[str, list[str]]] = {`: declares a variable `LABEL_BANKS` of type `dict[str, dict[str, list[str]]]` and sets it to `{'billing': {'core': ['I was charged twice for the same order and I...`.

<!-- fmt: off -->
```python
CITIES = ["Austin", "Leeds", "Perth", "Toronto", "Dublin", "Oslo"]
AMOUNTS = ["$19.99", "$42.50", "$75.00", "$120.00"]
GREETINGS = ["Hello,", "Hi there,", "Good morning,", "Dear support,"]
CLOSINGS = ["Thanks.", "Please reply soon.", "Regards,", "Thank you for your help."]


def order_id(rng: random.Random) -> str:
    return f"PR-{rng.randint(100000, 199999)}"


def label_tasks(rng: random.Random, count: int) -> list[dict]:
    tasks = []
    categories = list(LABEL_BANKS)
    for i in range(count):
```
<!-- fmt: on -->

- `CITIES = ["Austin", "Leeds", "Perth", "Toronto", "Dublin", "Oslo"]`: sets `CITIES` to a list of 6 items.
- `AMOUNTS = ["$19.99", "$42.50", "$75.00", "$120.00"]`: sets `AMOUNTS` to a list of 4 items.
- `GREETINGS = ["Hello,", "Hi there,", "Good morning,", "Dear support,"]`: sets `GREETINGS` to a list of 4 items.
- `CLOSINGS = ["Thanks.", "Please reply soon.", "Regards,", "Thank you for your help."]`: sets `CLOSINGS` to a list of 4 items.
- **New idea.** A **function** is a named block of code. `def name(a, b):` defines it; the indented lines are its body. Calling `name(1, 2)` runs the body with `a = 1` and `b = 2`. `return` hands a value back. A parameter written `b=3` has a **default**: it may be left out when calling.
- `def order_id(rng: random.Random) -> str:`: defines the function `order_id` taking rng (random.Random) and returns `str`.
- **New idea.** `return value` ends the function and hands the value to the caller. A function that reaches its end without `return` gives back `None` (nothing).
- `return f"PR-{rng.randint(100000, 199999)}"`: ends the function and hands back `f'PR-{rng.randint(100000, 199999)}'`. the f-string inserts `rng.randint(100000, 199999)` into the text.
- `def label_tasks(rng: random.Random, count: int) -> list[dict]:`: defines the function `label_tasks` taking rng (random.Random); count (int) and returns `list[dict]`.
- `tasks = []`: sets `tasks` to a list of 0 items.
- `categories = list(LABEL_BANKS)`: sets `categories` to the value of `list(LABEL_BANKS)`. `list(LABEL_BANKS)` is `LABEL_BANKS` copied into a list.
- **New idea.** A **for loop** `for x in items:` runs its block once for each item, with `x` naming the current item. `break` leaves the loop early; `continue` skips to the next item.
- `for i in range(count):`: repeats the block below once for each `i` in `range(count)`. `range(count)` is the whole numbers from `0` up to, not including, `count`.

<!-- fmt: off -->
```python
        gold = categories[i % 4]
        hard = (i // 4) % 2 == 1
        bank = LABEL_BANKS[gold]
        fill = {
            "order": order_id(rng),
            "amount": rng.choice(AMOUNTS),
            "other": rng.choice(AMOUNTS),
            "city": rng.choice(CITIES),
        }
        sentences = [rng.choice(bank["core"]).format(**fill)]
        if hard:
            other = rng.choice([c for c in categories if c != gold])
            distractor = rng.choice(LABEL_BANKS[other]["distractor"]).format(**fill)
            sentences = [distractor, "What I actually need: " + sentences[0][0].lower() + sentences[0][1:]]
```
<!-- fmt: on -->

- `gold = categories[i % 4]`: sets `gold` to the value of `categories[i % 4]`.
- `hard = (i // 4) % 2 == 1`: sets `hard` to the value of `i // 4 % 2 == 1`.
- `bank = LABEL_BANKS[gold]`: sets `bank` to the value of `LABEL_BANKS[gold]`.
- `fill = {`: sets `fill` to a dictionary with 4 entries. `rng.choice(AMOUNTS)` is a random item of `AMOUNTS`; `rng.choice(CITIES)` is a random item of `CITIES`.
- `sentences = [rng.choice(bank["core"]).format(**fill)]`: sets `sentences` to a list of 1 item. `rng.choice(bank['core']).format(**fill)` is `rng.choice(bank['core'])` with its {{}} fields filled in; `rng.choice(bank['core'])` is a random item of `bank['core']`.
- **New idea.** An **if** statement runs its indented block only when the condition is true. `elif` adds another condition to try; `else` runs when none held.
- `if hard:`: runs the block below only if `hard` is true.
- `other = rng.choice([c for c in categories if c != gold])`: sets `other` to the value of `rng.choice([c for c in categories if c != gold])`. `rng.choice([c for c in categories if c != gold])` is a random item of `[c for c in categories if c != gold]`; `[c for c in categories if c != gold]` builds a list: for each `c` in `categories`, keeping only those for which `c != gold` is true.
- `distractor = rng.choice(LABEL_BANKS[other]["distractor"]).format(**fill)`: sets `distractor` to the value of `rng.choice(LABEL_BANKS[other]['distractor']).format(**fill)`. `rng.choice(LABEL_BANKS[other]['distractor']).format(**fill)` is `rng.choice(LABEL_BANKS[other]['distra...` with its {{}} fields filled in; `rng.choice(LABEL_BANKS[other]['distractor'])` is a random item of `LABEL_BANKS[other]['distractor']`.
- `sentences = [distractor, "What I actually need: " + sentences[0][0].lower() + sentences...`: sets `sentences` to a list of 2 items. `sentences[0][1:]` is a slice (a part) of `sentences[0]`; `sentences[0][0].lower()` is `sentences[0][0]` in lower case.

<!-- fmt: off -->
```python
        text = " ".join([rng.choice(GREETINGS), *sentences, rng.choice(CLOSINGS)])
        tasks.append({"kind": "label", "difficulty": "hard" if hard else "easy", "text": text, "gold": gold})
    return tasks


def refund_tasks(rng: random.Random, count: int) -> list[dict]:
    tasks = []
    for i in range(count):
        hard = i % 2 == 1
        orders = []
        n_orders = 2 if hard and i % 4 == 3 else 1
        for _ in range(n_orders):
            total = rng.choice([2500, 3200, 4500, 5000, 6400, 7500, 9000, 12000])
            days = rng.choice([4, 9, 14, 15, 16, 20, 25, 30, 33])
            partial = hard and rng.random() < 0.6
            returned = total // 2 if partial else total
            damaged = hard and rng.random() < 0.4
            orders.append(
                {
                    "order_id": order_id(rng),
                    "total_cents": total,
                    "days": days,
                    "returned_cents": returned,
                    "damaged": damaged,
                }
            )
```
<!-- fmt: on -->

- `text = " ".join([rng.choice(GREETINGS), *sentences, rng.choice(CLOSINGS)])`: sets `text` to the value of `' '.join([rng.choice(GREETINGS), *sentences, rng.choice(CLOSINGS)])`. `' '.join([rng.choice(GREETINGS), *sentences, rng.choice(CLOSINGS)])` is the items of `[rng.choice(GREETINGS), *sentences, rng.choice(CLOSINGS)]` joined into one text with `' '` between them; `rng.choice(GREETINGS)` is a random item of `GREETINGS`; `*sentences` spreads the items of `sentences` into separate values.
- `tasks.append({"kind": "label", "difficulty": "hard" if hard else "easy", "text": text, ...`: runs `tasks.append({'kind': 'label', 'difficulty': 'hard' if hard else 'easy', 'text': text, ...` for its effect and ignores the result. `tasks.append({'kind': 'label', 'difficulty': 'hard' if hard else 'e...` adds `{'kind': 'label', 'difficulty': 'hard' if hard else 'easy...` to the end of `tasks`; `'hard' if hard else 'easy'` gives `'hard'` when `hard` is true, otherwise `'easy'`.
- `return tasks`: ends the function and hands back `tasks`.
- `def refund_tasks(rng: random.Random, count: int) -> list[dict]:`: defines the function `refund_tasks` taking rng (random.Random); count (int) and returns `list[dict]`.
- `tasks = []`: sets `tasks` to a list of 0 items.
- `for i in range(count):`: repeats the block below once for each `i` in `range(count)`. `range(count)` is the whole numbers from `0` up to, not including, `count`.
- `hard = i % 2 == 1`: sets `hard` to the value of `i % 2 == 1`.
- `orders = []`: sets `orders` to a list of 0 items.
- `n_orders = 2 if hard and i % 4 == 3 else 1`: sets `n_orders` to the value of `2 if hard and i % 4 == 3 else 1`. `2 if hard and i % 4 == 3 else 1` gives `2` when `hard and i % 4 == 3` is true, otherwise `1`.
- `for _ in range(n_orders):`: repeats the block below once for each `_` in `range(n_orders)`. `range(n_orders)` is the whole numbers from `0` up to, not including, `n_orders`.
- `total = rng.choice([2500, 3200, 4500, 5000, 6400, 7500, 9000, 12000])`: sets `total` to the value of `rng.choice([2500, 3200, 4500, 5000, 6400, 7500, 9000, 12000])`. `rng.choice([2500, 3200, 4500, 5000, 6400, 7500, 9000, 12000])` is a random item of `[2500, 3200, 4500, 5000, 6400, 7500, 9000, 12000]`.
- `days = rng.choice([4, 9, 14, 15, 16, 20, 25, 30, 33])`: sets `days` to the value of `rng.choice([4, 9, 14, 15, 16, 20, 25, 30, 33])`. `rng.choice([4, 9, 14, 15, 16, 20, 25, 30, 33])` is a random item of `[4, 9, 14, 15, 16, 20, 25, 30, 33]`.
- `partial = hard and rng.random() < 0.6`: sets `partial` to the value of `hard and rng.random() < 0.6`.
- `returned = total // 2 if partial else total`: sets `returned` to the value of `total // 2 if partial else total`. `total // 2 if partial else total` gives `total // 2` when `partial` is true, otherwise `total`.
- `damaged = hard and rng.random() < 0.4`: sets `damaged` to the value of `hard and rng.random() < 0.4`.
- `orders.append(`: runs `orders.append({'order_id': order_id(rng), 'total_cents': total, 'days': days, 'returned...` for its effect and ignores the result. `orders.append({'order_id': order_id(rng), 'total_cents': total, 'da...` adds `{'order_id': order_id(rng), 'total_cents': total, 'days':...` to the end of `orders`.

<!-- fmt: off -->
```python
        parts = []
        for o in orders:
            sentence = f"Order {o['order_id']} totaled ${o['total_cents'] / 100:.2f} and arrived {o['days']} days ago."
            if o["returned_cents"] != o["total_cents"]:
                sentence += f" I am returning only part of it, worth ${o['returned_cents'] / 100:.2f}."
            else:
                sentence += " I am returning everything."
            if o["damaged"]:
                sentence += " The item was damaged when it arrived."
            parts.append(sentence)
        text = " ".join(parts) + " How much will I be refunded?"
        gold = sum(refund_cents(o) for o in orders)
        tasks.append(
            {"kind": "refund", "difficulty": "hard" if hard else "easy", "text": text, "gold": gold, "orders": orders}
        )
```
<!-- fmt: on -->

- `parts = []`: sets `parts` to a list of 0 items.
- `for o in orders:`: repeats the block below once for each `o` in `orders`.
- `sentence = f"Order {o['order_id']} totaled ${o['total_cents'] / 100:.2f} and arrived {o...`: sets `sentence` to the value of `f"Order {o['order_id']} totaled ${o['total_cents'] / 100:.2f} and arrived {o[...`. the f-string inserts `o['order_id']`, `o['total_cents'] / 100`, `o['days']` into the text.
- `if o["returned_cents"] != o["total_cents"]:`: runs the block below only if `o['returned_cents'] != o['total_cents']` is true.
- **New idea.** An **augmented assignment** such as `x += 1` changes the value in place: it means `x = x + 1`.
- `sentence += f" I am returning only part of it, worth ${o['returned_cents'] / 100:.2f}."`: adds `f" I am returning only part of it, worth ${o['returned_ce...` to `sentence` and stores the result back. the f-string inserts `o['returned_cents'] / 100` into the text.
- `else:` the block below runs when none of the conditions above held.
- `sentence += " I am returning everything."`: adds `' I am returning everything.'` to `sentence` and stores the result back.
- `if o["damaged"]:`: runs the block below only if `o['damaged']` is true.
- `sentence += " The item was damaged when it arrived."`: adds `' The item was damaged when it arrived.'` to `sentence` and stores the result back.
- `parts.append(sentence)`: runs `parts.append(sentence)` for its effect and ignores the result. `parts.append(sentence)` adds `sentence` to the end of `parts`.
- `text = " ".join(parts) + " How much will I be refunded?"`: sets `text` to the value of `' '.join(parts) + ' How much will I be refunded?'`. `' '.join(parts)` is the items of `parts` joined into one text with `' '` between them.
- `gold = sum(refund_cents(o) for o in orders)`: sets `gold` to the value of `sum((refund_cents(o) for o in orders))`. `sum((refund_cents(o) for o in orders))` is the sum of `(refund_cents(o) for o in orders)`; `(refund_cents(o) for o in orders)` builds a generator of values: for each `o` in `orders`.
- `tasks.append(`: runs `tasks.append({'kind': 'refund', 'difficulty': 'hard' if hard else 'easy', 'text': text,...` for its effect and ignores the result. `tasks.append({'kind': 'refund', 'difficulty': 'hard' if hard else '...` adds `{'kind': 'refund', 'difficulty': 'hard' if hard else 'eas...` to the end of `tasks`; `'hard' if hard else 'easy'` gives `'hard'` when `hard` is true, otherwise `'easy'`.

<!-- fmt: off -->
```python
    return tasks


QUESTION_BANK: list[tuple[int, str, str]] = [
    # (line index, easy question, hard question)
    (
        0,
        "How many days do I have to return an item?",
        "I got my parcel 12 days ago and want to send it back: is that still inside the time limit for returns?",
    ),
    (
        1,
        "Who pays for return shipping?",
        "If I just don't want the item any more, am I the one who pays to post it back?",
    ),
    (
        2,
        "How long do refunds take?",
        "Once you have my returned item, in how many business days will the money show up?",
    ),
    (3, "Can I exchange an item?", "Can I swap this for a different size without paying again?"),
    (
        4,
        "What happens if an item arrives damaged?",
        "My vase arrived in pieces, which rule covers that and what do I get?",
    ),
    (5, "Can I use a gift card on any order?", "Is a gift card allowed to pay for shipping on my order?"),
    (
        6,
        "How long is the warranty on electronics?",
        "My headphones stopped working after 8 months. Are they still covered?",
    ),
    (
        7,
        "Do you match lower prices from other shops?",
        "I saw the same lamp cheaper elsewhere last week. Do you adjust the price?",
    ),
    (8, "Can I cancel an order after placing it?", "I ordered an hour ago and want to cancel. Is that possible?"),
    (9, "How do you handle my personal data?", "Do you share my email with other companies?"),
]
```
<!-- fmt: on -->

- `return tasks`: ends the function and hands back `tasks`.
- `QUESTION_BANK: list[tuple[int, str, str]] = [`: declares a variable `QUESTION_BANK` of type `list[tuple[int, str, str]]` and sets it to `[(0, 'How many days do I have to return an item?', 'I got my parcel...`.

<!-- fmt: off -->
```python
def policy_tasks(rng: random.Random, count: int) -> list[dict]:
    tasks = []
    for i in range(count):
        index, easy, hard_q = QUESTION_BANK[i % len(QUESTION_BANK)]
        hard = (i // len(QUESTION_BANK)) % 2 == 1
        question = hard_q if hard else easy
        tasks.append({"kind": "policy", "difficulty": "hard" if hard else "easy", "text": question, "gold": index})
    return tasks


def main() -> None:
    rng = random.Random(2026)
    tasks = label_tasks(rng, 120) + refund_tasks(rng, 100) + policy_tasks(rng, 80)
    for number, task in enumerate(tasks, start=1):
```
<!-- fmt: on -->

- `def policy_tasks(rng: random.Random, count: int) -> list[dict]:`: defines the function `policy_tasks` taking rng (random.Random); count (int) and returns `list[dict]`.
- `tasks = []`: sets `tasks` to a list of 0 items.
- `for i in range(count):`: repeats the block below once for each `i` in `range(count)`. `range(count)` is the whole numbers from `0` up to, not including, `count`.
- `index, easy, hard_q = QUESTION_BANK[i % len(QUESTION_BANK)]`: sets `(index, easy, hard_q)` to the value of `QUESTION_BANK[i % len(QUESTION_BANK)]`. `len(QUESTION_BANK)` is the number of items in `QUESTION_BANK`.
- `hard = (i // len(QUESTION_BANK)) % 2 == 1`: sets `hard` to the value of `i // len(QUESTION_BANK) % 2 == 1`. `len(QUESTION_BANK)` is the number of items in `QUESTION_BANK`.
- `question = hard_q if hard else easy`: sets `question` to the value of `hard_q if hard else easy`. `hard_q if hard else easy` gives `hard_q` when `hard` is true, otherwise `easy`.
- `tasks.append({"kind": "policy", "difficulty": "hard" if hard else "easy", "text": quest...`: runs `tasks.append({'kind': 'policy', 'difficulty': 'hard' if hard else 'easy', 'text': quest...` for its effect and ignores the result. `tasks.append({'kind': 'policy', 'difficulty': 'hard' if hard else '...` adds `{'kind': 'policy', 'difficulty': 'hard' if hard else 'eas...` to the end of `tasks`; `'hard' if hard else 'easy'` gives `'hard'` when `hard` is true, otherwise `'easy'`.
- `return tasks`: ends the function and hands back `tasks`.
- `def main() -> None:`: defines the function `main` taking no arguments and returns `None`.
- `rng = random.Random(2026)`: sets `rng` to the value of `random.Random(2026)`. `random.Random(2026)` is a random number generator.
- `tasks = label_tasks(rng, 120) + refund_tasks(rng, 100) + policy_tasks(rng, 80)`: sets `tasks` to the value of `label_tasks(rng, 120) + refund_tasks(rng, 100) + policy_tasks(rng, 80)`.
- `for number, task in enumerate(tasks, start=1):`: repeats the block below once for each `(number, task)` in `enumerate(tasks, start=1)`. `enumerate(tasks, start=1)` is pairs (position, item) for the items of `tasks`.

<!-- fmt: off -->
```python
        task["task_id"] = f"t{number:03d}"
    # stratified split: within each (kind, difficulty) alternate build and test after a seeded shuffle
    groups: dict[tuple[str, str], list[dict]] = {}
    for task in tasks:
        groups.setdefault((task["kind"], task["difficulty"]), []).append(task)
    for key in sorted(groups):
        members = groups[key]
        rng.shuffle(members)
        for position, task in enumerate(members):
            task["split"] = "build" if position % 2 == 0 else "test"
    DATA.mkdir(exist_ok=True)
    with (DATA / "tasks.jsonl").open("w") as handle:
        for task in sorted(tasks, key=lambda t: t["task_id"]):
            handle.write(json.dumps(task, sort_keys=True) + "\n")
```
<!-- fmt: on -->

- `task["task_id"] = f"t{number:03d}"`: sets `task['task_id']` to the value of `f't{number:03d}'`. the f-string inserts `number` into the text.
- `groups: dict[tuple[str, str], list[dict]] = {}`: declares a variable `groups` of type `dict[tuple[str, str], list[dict]]` and sets it to `{}`.
- `for task in tasks:`: repeats the block below once for each `task` in `tasks`.
- `groups.setdefault((task["kind"], task["difficulty"]), []).append(task)`: runs `groups.setdefault((task['kind'], task['difficulty']), []).append(task)` for its effect and ignores the result. `groups.setdefault((task['kind'], task['difficulty']), []).append(task)` adds `task` to the end of `groups.setdefault((task['kind'], task...`; `groups.setdefault((task['kind'], task['difficulty']), [])` is the entry `(task['kind'], task['difficulty'])` of `groups`, created with `[]` if missing.
- `for key in sorted(groups):`: repeats the block below once for each `key` in `sorted(groups)`. `sorted(groups)` is `groups` in sorted order.
- `members = groups[key]`: sets `members` to the value of `groups[key]`.
- `rng.shuffle(members)`: runs `rng.shuffle(members)` for its effect and ignores the result. `rng.shuffle(members)` mixes the order of `rng`.
- `for position, task in enumerate(members):`: repeats the block below once for each `(position, task)` in `enumerate(members)`. `enumerate(members)` is pairs (position, item) for the items of `members`.
- `task["split"] = "build" if position % 2 == 0 else "test"`: sets `task['split']` to the value of `'build' if position % 2 == 0 else 'test'`. `'build' if position % 2 == 0 else 'test'` gives `'build'` when `position % 2 == 0` is true, otherwise `'test'`.
- `DATA.mkdir(exist_ok=True)`: runs `DATA.mkdir(exist_ok=True)` for its effect and ignores the result. `DATA.mkdir(exist_ok=True)` creates the folder `DATA`.
- **New idea.** A **with** statement runs set-up code, then the block, then clean-up code even if the block fails. It is used for files, locks and pools: the file is closed, the lock released, when the block ends.
- `with (DATA / "tasks.jsonl").open("w") as handle:`: opens `(DATA / 'tasks.jsonl').open('w')` (named `handle`) for the duration of the block below and cleans up afterwards. `(DATA / 'tasks.jsonl').open('w')` opens `DATA / 'tasks.jsonl'`.
- `for task in sorted(tasks, key=lambda t: t["task_id"]):`: repeats the block below once for each `task` in `sorted(tasks, key=lambda t: t['task_id'])`. `sorted(tasks, key=lambda t: t['task_id'])` is `tasks` in sorted order; `lambda t: t['task_id']` is a small unnamed function of `t` that gives `t['task_id']`.
- `handle.write(json.dumps(task, sort_keys=True) + "\n")`: runs `handle.write(json.dumps(task, sort_keys=True) + '\n')` for its effect and ignores the result. `handle.write(json.dumps(task, sort_keys=True) + '\n')` writes `json.dumps(task, sort_keys=True) + '\n'` to `handle`; `json.dumps(task, sort_keys=True)` is `task` written as JSON text.

<!-- fmt: off -->
```python
    (DATA / "policy_lines.txt").write_text("\n".join(POLICY_LINES) + "\n")
    (DATA / "refund_policy.txt").write_text(REFUND_POLICY + "\n")
    counts: dict[str, int] = {}
    for task in tasks:
        counts[f"{task['kind']}/{task['split']}"] = counts.get(f"{task['kind']}/{task['split']}", 0) + 1
    print(len(tasks), "tasks", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
```
<!-- fmt: on -->

- `(DATA / "policy_lines.txt").write_text("\n".join(POLICY_LINES) + "\n")`: runs `(DATA / 'policy_lines.txt').write_text('\n'.join(POLICY_LINES) + '\n')` for its effect and ignores the result. `(DATA / 'policy_lines.txt').write_text('\n'.join(POLICY_LINES) + '\n')` writes `'\n'.join(POLICY_LINES) + '\n'` as the content of the file `DATA / 'policy_lines.txt'`; `'\n'.join(POLICY_LINES)` is the items of `POLICY_LINES` joined into one text with `'\n'` between them.
- `(DATA / "refund_policy.txt").write_text(REFUND_POLICY + "\n")`: runs `(DATA / 'refund_policy.txt').write_text(REFUND_POLICY + '\n')` for its effect and ignores the result. `(DATA / 'refund_policy.txt').write_text(REFUND_POLICY + '\n')` writes `REFUND_POLICY + '\n'` as the content of the file `DATA / 'refund_policy.txt'`.
- `counts: dict[str, int] = {}`: declares a variable `counts` of type `dict[str, int]` and sets it to `{}`.
- `for task in tasks:`: repeats the block below once for each `task` in `tasks`.
- `counts[f"{task['kind']}/{task['split']}"] = counts.get(f"{task['kind']}/{task['split']}...`: sets `counts[f"{task['kind']}/{task['split'...` to the value of `counts.get(f"{task['kind']}/{task['split']}", 0) + 1`. `counts.get(f"{task['kind']}/{task['split']}", 0)` looks up `f"{task['kind']}/{task['split']}"` in `counts` (default `0` when missing); the f-string inserts `task['kind']`, `task['split']` into the text.
- `print(len(tasks), "tasks", dict(sorted(counts.items())))`: runs `print(len(tasks), 'tasks', dict(sorted(counts.items())))` for its effect and ignores the result. `print(len(tasks), 'tasks', dict(sorted(counts.items())))` prints `len(tasks)`, `'tasks'`, `dict(sorted(counts.items()))`; `len(tasks)` is the number of items in `tasks`; `dict(sorted(counts.items()))` is a dictionary made from `sorted(counts.items())`.
- **New idea.** `if __name__ == "__main__":` runs its block only when the file is started as a program, not when another file imports it.
- `if __name__ == "__main__":`: runs the block below only if `__name__ == '__main__'` is true.
- `main()`: runs `main()` for its effect and ignores the result.

## Try it yourself

1. `head -20 scripts/make_data.py` shows the start of the first script.
2. `.venv/bin/python -c "import ast; ast.parse(open('scripts/make_data.py').read()); print('parses')"` prints `parses`.
3. `git log --oneline -- scripts/make_data.py | tail -1` shows the commit that added it.

## Mistakes people make

- Running a script from another folder: paths are relative to the repository root.
- Editing a generated data file by hand instead of the script, which then overwrites the change.
- Forgetting the seed: without it, the data set differs on every run.

## Check yourself

1. **What does `if __name__ == "__main__":` do?**  
   Runs the block only when the file is started as a program.
2. **Why is the data generated by a script?**  
   So anyone can recreate it exactly.
3. **Why a fixed seed?**  
   So the random choices are the same every time.
4. **Are scripts part of the installed package?**  
   No, they live outside `src/`.
5. **Where are generated files written?**  
   Into `data/` or `prompts/`, as the script says.

## Further reading

The Python language reference: https://docs.python.org/3/reference/ and the tutorial https://docs.python.org/3/tutorial/ (both for Python 3.13; the project accepts 3.12 or newer).
