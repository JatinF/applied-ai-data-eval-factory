# ADR-002: Local retrieval and a linear refinement

## Status

Accepted.

## Decision

Four runnable systems are compared on one test split:

- `baseline_ml`: multinomial naive Bayes on ticket text, trained on V1 weak labels
- `prompt_template`: an ordered keyword template, not a hosted LLM
- `rag_extractive`: BM25 plus a hashed bag-of-words cosine rerank, then a category vote over the top documents
- `linear_finetune`: one-versus-rest logistic SGD on text, service, and error-code features

Embeddings are 256-dimensional hashed bags of words. The rerank mixes 0.8 lexical score and 0.2 cosine. The index is in process.

`configs/models.yaml` records `hosted_llm: not-run` and `lora: not-run`. The linear model is not a LoRA adapter. The prompt row is not an LLM call.

## Consequences

The comparison can be reproduced without an API key or a GPU. It does not measure a hosted model or a parameter-efficient fine-tune. Retrieval documents are the same in V1 and V2, so Recall@5 is not expected to move when only the classifier changes.
