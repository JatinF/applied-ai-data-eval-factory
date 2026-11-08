# ADR-001: Local probabilistic label model

## Status

Accepted.

## Decision

Labeling functions vote or abstain. A local model estimates each function's accuracy from leave-one-out agreement with the other functions, clamps that estimate to the range 0.51–0.97, and combines the votes with a class-conditional log score. The backend name is `local-probabilistic-v1`.

The official `snorkel` package is not a dependency. It pulls in torch, and this repository does not train or serve a torch model. The fit does not take gold labels. `used_gold_to_fit` stays false. Gold accuracy is computed afterward for the report.

## Consequences

A noisy function that disagrees with the others, such as the rule that maps every timeout to `NETWORK`, is down-weighted. Functions are not averaged as equal votes. The implementation is not a claim that Snorkel's LabelModel was executed.
