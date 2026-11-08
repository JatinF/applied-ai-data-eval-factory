# Evaluation

Every system is scored on the same test tickets. The scorecard is a set of fields, not a single accuracy.

| Dimension | Fields |
| --- | --- |
| Classification | accuracy, macro precision, macro recall, macro F1 |
| Retrieval | graded Recall@5, MRR, nDCG@5 |
| Answer | groundedness, citation correctness |
| Agent | tool selection, argument correctness, task completion |
| Safety | unsafe-action rate, appropriate abstention on missing context |
| Data | labeling coverage, overlap, conflict |
| Synthetic | approved, rejected, duplicate rate, mean novelty |
| Reliability | accuracy by display slice |
| Operational | P50 and P95 latency in milliseconds |
| Economics | token count and estimated cost |

Recall@5 is graded over the two relevant document ids. A ticket that retrieves one of them scores 0.5. It is not a hit rate.

Groundedness is the fraction of period-separated answer parts that appear inside the cited document text. An empty answer is excluded from the mean. The V1 prompt appends a sentence that is not in any document, so its groundedness is below the V2 prompt, which returns only the cited sentence.

Latency is `time.perf_counter` around each test item, converted to milliseconds, with nearest-rank percentiles. No price is applied. Token counts stay 0 because no model API is called.

`data-eval check-regression` compares a fresh V2 run with `reports/baseline_metrics.json`. It fails if linear macro F1 drops by more than 0.02, prompt groundedness drops by more than 0.03, or the guarded agent's unsafe-action rate rises. Latency is not part of the gate.
