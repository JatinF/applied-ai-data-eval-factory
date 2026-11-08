# Measured results

These figures come from `data-eval run` on the synthetic enterprise support set.
No hosted model was called. LoRA was not trained. No price is applied.

Tickets 270. Test 46. Agreement 0.6222. Cohen's kappa 0.6611. Adjudicated disagreements 66.

Synthetic generated 960, approved 321, rejected 159, mean novelty 0.4177.

Train and test ids overlap: 0. Max train/test token Jaccard: 1.0000.

| System | Accuracy | F1 | Groundedness | Recall@5 | P50 ms | P95 ms | Unsafe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| iteration v1 | | | | | | | |
| baseline_ml | 0.8261 | 0.8296 | n/a | n/a | 0.0152 | 0.0240 | n/a |
| prompt_template | 0.7609 | 0.8319 | 0.5000 | 0.9022 | 0.2146 | 0.2920 | n/a |
| rag_extractive | 0.8043 | 0.8078 | 1.0000 | 0.9022 | 0.2179 | 0.2981 | n/a |
| unguarded_agent | 0.8261 | 0.8296 | n/a | 0.9022 | 0.2375 | 0.2518 | 0.0217 |
| iteration v2 | | | | | | | |
| linear_finetune | 0.8478 | 0.8457 | n/a | n/a | 0.0158 | 0.0241 | n/a |
| prompt_template | 0.7826 | 0.8605 | 1.0000 | 0.9022 | 0.2263 | 0.2551 | n/a |
| rag_extractive | 0.8043 | 0.8078 | 1.0000 | 0.9022 | 0.2282 | 0.2618 | n/a |
| guarded_agent | 0.8478 | 0.8457 | n/a | 0.9022 | 0.2379 | 0.2531 | 0.0000 |

## Curation

- Added 120 approved hard negatives.
- Added labeling functions lf_db_error_code, lf_pay_error_code, and lf_auth_on_payments.
- V2 prompt drops the unsupported restart sentence and ignores the glossary appendix.
- V2 agent blocks credential reset unless the prediction is account access on the identity service.
- V2 linear model skips context-free rows, keeps weak labels unless an error code overrides them, and adds approved synthetic rows.
- Retrieval documents are unchanged between V1 and V2.
- Reviewers are programmed policies, not external people.
