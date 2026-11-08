# Failure analysis

V1 shares use baseline_ml predictions on the test split.
V2 shares use linear_finetune predictions on the same test ids.

## v1

Failed tickets: 9.

- retrieval_miss: 0 (0.0000)
- classification_error: 1 (0.1111)
- insufficient_context: 7 (0.7778)
- reasoning_error: 0 (0.0000)
- tool_selection: 1 (0.1111)
- other: 0 (0.0000)

| Slice | Support | Accuracy |
| --- | ---: | ---: |
| database-incidents | 9 | 0.7778 |
| authentication | 11 | 0.9091 |
| payments | 8 | 0.7500 |
| ambiguous-tickets | 3 | 1.0000 |
| missing-context | 8 | 0.1250 |
| cross-domain | 8 | 1.0000 |

## v2

Failed tickets: 8.

- retrieval_miss: 0 (0.0000)
- classification_error: 0 (0.0000)
- insufficient_context: 7 (0.8750)
- reasoning_error: 0 (0.0000)
- tool_selection: 1 (0.1250)
- other: 0 (0.0000)

| Slice | Support | Accuracy |
| --- | ---: | ---: |
| database-incidents | 9 | 0.8889 |
| authentication | 11 | 0.9091 |
| payments | 8 | 0.7500 |
| ambiguous-tickets | 3 | 1.0000 |
| missing-context | 8 | 0.1250 |
| cross-domain | 8 | 1.0000 |
