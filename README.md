# Prompt Intent Taxonomy

This repository contains version 0.1 of a provider-neutral taxonomy for
representing what a user wants from an AI system.

The goal is to preserve the important parts of a request—its outcome, inputs,
constraints, permissions, evidence needs, and definition of success—without
locking execution to a specific model or tool. A router can then choose a
cheaper or simpler way to complete the work while keeping the same intent.

## What's included

- `prompt-intent-taxonomy-v0.1.yaml` defines the taxonomy and routing concepts.
- `prompt-intent-ir-v0.1.schema.json` validates canonical intent records.
- `example-current-request.intent.yaml` and
  `example-current-request.intent.json` show the same request in both formats.
- `compact-wire-example-v0.1.yaml` demonstrates a smaller transport format.
- `README-prompt-intent-taxonomy.md` contains the full design notes, research,
  tradeoffs, and recommended next steps.

## Basic flow

1. Parse a natural-language request into the canonical intent format.
2. Validate it with the JSON Schema.
3. Choose a model, tools, context, and compression strategy separately.
4. Confirm that the result still satisfies the original success criteria.

Version 0.1 is a draft intended as a practical starting point for testing and
iteration.
