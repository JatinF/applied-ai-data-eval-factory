# Dataset

The corpus is a deterministic synthetic enterprise support set. It is not customer data and it is not clinical data.

Six root-cause classes are used: `ACCOUNT_ACCESS`, `AUTHORIZATION`, `DATABASE`, `NETWORK`, `PAYMENTS`, and `INCIDENT`. Each class has a runbook and a product note. A ticket's relevant documents are that runbook and that product note.

`build_tickets` writes 270 tickets:

- 180 easy copies, 30 for each class
- 36 missing-context copies with the same vague sentence and `product=unknown`
- 24 contradictory copies that paste another domain's wording next to the real fault
- 18 mixed ambiguous or multi-symptom copies
- 12 long-context copies that append a glossary of unrelated terms

The split is the first eight hex digits of SHA-256 of the ticket id, modulo 10. Values below 6 are train, below 8 are validation, and the rest are test. Train and test ids do not overlap. Missing-context sentences repeat across splits, so token Jaccard can be 1.0. That overlap is reported rather than treated as a clean natural corpus.

`recorded_type` matches the generator gold type unless a hash bucket flips it to the next class. Similar-case labeling uses `recorded_type` on train tickets only. It does not read gold.

`data-eval run` writes `data/raw`, `data/synthetic/synthetic.jsonl`, and `data/benchmark`. `benchmark_v2.jsonl` scores the same test ids as v1. The training set changes. The scored set does not.
