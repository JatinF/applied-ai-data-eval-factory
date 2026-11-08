# Data

`data-eval run` regenerates this tree. Do not hand-edit the JSONL files.

| Path | Contents |
| --- | --- |
| `raw/tickets.jsonl` | 270 synthetic support tickets |
| `raw/documents.jsonl` | Runbooks and product notes |
| `synthetic/synthetic.jsonl` | Targeted variants with provenance |
| `benchmark/benchmark_v1.jsonl` | Held-out benchmark items |
| `benchmark/benchmark_v2.jsonl` | Same test ids, with the V2 note |
| `benchmark/manifest.json` | Both version manifests |
| `benchmark/manifest_v1.json` | V1 task, difficulty, and slice counts |
| `benchmark/manifest_v2.json` | V2 counts for the same items |

Each synthetic row records `id`, `source_id`, `generation_strategy`, `generator`, `prompt_version`, `review_status`, and `target_slice`. The generator name is `deterministic-template` and the prompt version is `template-v1`.

Approved rows may train the linear model. `needs_review` rows are not accepted and are not rejected. Rejected rows are unchanged or too short to use.

This directory is synthetic enterprise support text. It is not a customer export and it is not clinical data.
