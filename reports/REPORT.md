# Cost-aware router: results

## Step 1: each model alone, 150 build tasks

| Model | Kind | Accuracy (95% interval) | Cost per call | Cost per correct answer |
| --- | --- | --- | --- | --- |
| small | label | 26.7% [17.1%, 39.0%] | $0.000041 | $0.000155 |
| small | policy | 60.0% [44.6%, 73.7%] | $0.000068 | $0.000113 |
| small | refund | 20.0% [11.2%, 33.0%] | $0.000041 | $0.000204 |
| medium | label | 18.3% [10.6%, 29.9%] | $0.000102 | $0.000555 |
| medium | policy | 95.0% [83.5%, 98.6%] | $0.000172 | $0.000181 |
| medium | refund | 36.0% [24.1%, 49.9%] | $0.000096 | $0.000267 |
| large | label | 88.3% [77.8%, 94.2%] | $0.000248 | $0.000281 |
| large | policy | 87.5% [73.9%, 94.5%] | $0.000408 | $0.000466 |
| large | refund | 14.0% [7.0%, 26.2%] | $0.000248 | $0.001769 |

Cheapest tier within the agreed margin of the large tier, per kind: label: large, policy: medium, refund: small.

## Step 2: the checks, measured against the truth (build set)

| Tier | Kind | Check | Accepted | False-accept rate | False-reject rate | Wrong among accepted | Over the bar |
| --- | --- | --- | --- | --- | --- | --- | --- |
| small | label | label_agreement | 60 | 100.0% | 0.0% | 73.3% | YES |
| small | label | label_shape | 60 | 100.0% | 0.0% | 73.3% | YES |
| small | policy | policy_quote | 40 | 100.0% | 0.0% | 40.0% | YES |
| small | refund | refund_recompute | 10 | 0.0% | 0.0% | 0.0% | no |
| medium | label | label_agreement | 36 | 51.0% | 0.0% | 69.4% | YES |
| medium | label | label_shape | 37 | 53.1% | 0.0% | 70.3% | YES |
| medium | policy | policy_quote | 40 | 100.0% | 0.0% | 5.0% | YES |
| medium | refund | refund_recompute | 18 | 0.0% | 0.0% | 0.0% | no |
| large | label | label_agreement | 53 | 0.0% | 0.0% | 0.0% | no |
| large | label | label_shape | 53 | 0.0% | 0.0% | 0.0% | no |
| large | policy | policy_quote | 38 | 60.0% | 0.0% | 7.9% | YES |
| large | refund | refund_recompute | 7 | 0.0% | 0.0% | 0.0% | no |

Bar agreed in advance: a check whose false-accept rate is above 10.0% is not trusted to stop the cascade.

## Step 3: the configuration the build set produced

`{'hard_start': {'refund': 'medium'}, 'label_check': 'agreement', 'policy_check': 'quote', 'request_cap': 0.0008, 'start': {'label': 'large', 'policy': 'large', 'refund': 'small'}, 'tighten_at': 0.8}`

## Step 5: the router and each model alone, 150 test tasks

| Method | Accuracy (95% interval) | Total cost | Cost per correct (95% interval) | Served by | Escalated to a person |
| --- | --- | --- | --- | --- | --- |
| large | 59.3% [51.3%, 66.9%] | $0.043397 | $0.000488 [$0.000435, $0.000564] | {'large': 150} | 0 |
| medium | 42.0% [34.4%, 50.0%] | $0.017894 | $0.000284 [$0.000243, $0.000343] | {'medium': 150} | 0 |
| router | 71.3% [63.6%, 78.0%] | $0.059499 | $0.000556 [$0.000498, $0.000628] | {'escalate_to_person': 38, 'large': 92, 'medium': 19, 'small': 1} | 38 |
| router_no_bar | 40.7% [33.1%, 48.7%] | $0.021586 | $0.000354 [$0.000273, $0.000476] | {'escalate_to_person': 30, 'large': 1, 'medium': 22, 'small': 97} | 30 |
| small | 30.7% [23.8%, 38.5%] | $0.007230 | $0.000157 [$0.000127, $0.000205] | {'small': 150} | 0 |

Router against the large model alone: accuracy difference +0.120 (95% interval +0.073 to +0.180), margin 0.02. Verdict: **not cheaper**.

## Step 4: one day under a budget

| Budget (share of always-large) | Spent | Under budget | Requests over the cap | Accuracy before 80% | Accuracy after 80% | Large-tier answers after 80% |
| --- | --- | --- | --- | --- | --- | --- |
| 50.0% ($0.021698) | $0.021643 | True | 0 | 69.8% (n=43) | 15.0% (n=107) | 0 |
| 30.0% ($0.013019) | $0.012989 | True | 0 | 66.7% (n=27) | 5.7% (n=123) | 0 |

## Step 6: accepted answers that were wrong (test set)

`{'large/policy_quote': {'count': 5, 'tasks': ['t235', 't250', 't255', 't290', 't295']}}`

Change (policy answers must quote the line that best matches the question, not just any line): accuracy 71.3% to 66.7%; cost per correct $0.000556 to $0.000595; false accepts 5 to 3.

