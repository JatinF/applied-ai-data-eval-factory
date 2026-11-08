# ADR-003: Programmed reviewers and error-code overrides

## Status

Accepted.

## Decision

There are no external reviewers in this repository. Reviewer A follows labeling-function precedence. Reviewer B follows service metadata, then the domain dictionary and priority. Agreement requires both votes to be present and equal. Cohen's kappa uses rows where both voted.

The adjudicator keeps the agreed label. On disagreement it applies, in order: HTTP 401/403 to `AUTHORIZATION`, `DB-57014` to `DATABASE`, `PAY-1102` to `PAYMENTS`, otherwise the only available vote, otherwise `ABSTAIN`.

The V2 linear model does not train on every adjudicated label. It keeps the weak label unless the adjudication reason says an error code outranks the other vote or identifies the payment fault. It skips rows with `product=unknown`. Approved paraphrases, hard negatives, boundary examples, and rare cases from train gold are added. Adversarial, missing-context, contradictory, and long-context synthetic rows stay `needs_review` and stay out of training.

## Consequences

The published adjudication can differ from the linear training label. That split is intentional: keyword adjudication mislabeled some cross-domain network tickets as database incidents. The README states that reviewers are programmed policies.
