# Contributing

This repository holds a draft taxonomy, so most contributions are proposals
about how intent should be represented rather than code changes. The notes
below describe how to make one reviewable.

## Before opening a pull request

Run the validator against the examples:

```bash
pip install -r requirements.txt
python validate.py
```

Every example must validate against `prompt-intent-ir-v0.1.schema.json`. CI
runs the same check on each pull request.

## Changing the schema

The schema and the examples are expected to move together.

1. Edit `prompt-intent-ir-v0.1.schema.json`.
2. Update every example so it still validates.
3. Describe the change in `README-prompt-intent-taxonomy.md` under the design
   notes, including what a router would do differently as a result.

Breaking changes are acceptable while the taxonomy is at v0.x, but they should
be called out explicitly in the pull request description so downstream readers
know the wire format moved.

## Adding a taxonomy concept

A new concept is easier to evaluate when the proposal answers three questions:

- What does a request lose today if the concept is missing?
- How would a router use it to choose a cheaper or simpler execution path?
- How is it validated — a schema constraint, an enum, or free text?

Concepts that cannot be validated tend to drift, so prefer an enum or a
constrained shape where one is reasonable.

## Style

- Keep YAML and JSON examples in sync; they represent the same request.
- Prefer provider-neutral wording. The taxonomy should not assume a specific
  model, vendor, or tool.
- Keep lines wrapped at a readable width in Markdown files.
