"""Generate data/tasks.jsonl deterministically (seed 2026): 300 tasks whose answers code can check.

120 category labels, 100 refund amounts and 80 short policy answers; some easy, some hard; split once into 150 for
building the router (`split: build`) and 150 for the final test (`split: test`), stratified by kind and difficulty.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from cost_router.domain.tasks import POLICY_LINES, REFUND_POLICY, refund_cents

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
    (DATA / "policy_lines.txt").write_text("\n".join(POLICY_LINES) + "\n")
    (DATA / "refund_policy.txt").write_text(REFUND_POLICY + "\n")
    counts: dict[str, int] = {}
    for task in tasks:
        counts[f"{task['kind']}/{task['split']}"] = counts.get(f"{task['kind']}/{task['split']}", 0) + 1
    print(len(tasks), "tasks", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
