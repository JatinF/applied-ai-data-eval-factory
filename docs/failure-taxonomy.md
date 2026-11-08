# Failure taxonomy

A test ticket is a failure when the predicted class differs from the generator root cause or the selected tool differs from the gold tool. The primary label uses this order:

1. `insufficient_context` when the class is wrong and the ticket is in `missing-context`
2. `retrieval_miss` when the class is wrong and neither relevant document is in the top five
3. `reasoning_error` when the class is wrong and the ticket is ambiguous or cross-domain
4. `classification_error` for the remaining class errors
5. `tool_selection` when the class is right and the tool is wrong
6. `other` for anything left

Shares use the failure count as the denominator. Slice accuracy is a separate table. Slices overlap, so they are not a partition.

V1 failure shares use `baseline_ml`. V2 shares use `linear_finetune`. Missing-context tickets share one vague sentence across classes. A text classifier cannot recover that root cause. The report keeps that slice low instead of changing the gold labels.

The V2 training change was chosen from those failure modes: skip `product=unknown` rows, keep a weak label unless an error code overrides it, and hold adversarial, missing-context, contradictory, and long-context synthetic rows out of training.
