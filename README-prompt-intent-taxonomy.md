# Prompt Intent Taxonomy v0.1

This package defines a provider-neutral intermediate representation (IR) for
user intent. Its job is not to shorten every prompt by itself. Its job is to
make the request explicit enough that a router can safely choose a smaller
prompt, a smaller model, fewer tools, a cache hit, or no model call at all.

The core decision is to split the system in two:

```text
natural request
      ↓
intent parser
      ↓
durable Intent IR  ───────────────┐
      ↓                           │ equivalence checks
disposable route plan             │
      ↓                           │
prompt/tool/context compiler      │
      ↓                           │
model or deterministic executor ──┘
```

- **Intent IR** says what must be achieved, what information is relevant, what
  is authorized, and what counts as success.
- **Route plan** says how this attempt will do it: model, effort, tools,
  retrieval, cache, compression, retries, and fallback.

This separation is what makes “use the same or a cheaper tool” possible. A
record that says `web.search: required` can be routed to any compliant search
implementation. A record that says `must_call_vendor_x_search` cannot.

## Package contents

- `prompt-intent-taxonomy-v0.1.yaml` — readable taxonomy, enum registry,
  derived flags, route-plan dimensions, and reconstruction order.
- `prompt-intent-ir-v0.1.schema.json` — JSON Schema for canonical intent
  instances.
- `example-current-request.intent.yaml` — the request that produced this
  package, encoded as canonical IR.
- `example-current-request.intent.json` — semantically identical JSON encoding
  of the same canonical instance.
- `compact-wire-example-v0.1.yaml` — an intentionally terse transport
  projection with a cached/out-of-band key dictionary.

## What is being classified

“Prompt taxonomy” can mean two different things:

1. **User-task taxonomy:** answer, transform, analyze, decide, design, produce,
   act, or operate.
2. **Prompting-technique taxonomy:** zero-shot, few-shot, retrieval-augmented,
   tool-augmented, decomposed, compressed, cached, and so on.

The first belongs in the durable intent. The second belongs in the route plan.
Mixing them would treat an implementation choice such as few-shot prompting as
if it were part of what the user wanted.

The task taxonomy is multi-label. “Research three vendors, recommend one, and
write a migration plan” contains analysis, decision, and design. Reducing that
request to one class discards useful routing information.

| Family | Question it answers | Representative acts |
|---|---|---|
| Information | What should the user know? | answer, explain, teach, define |
| Transformation | How should supplied meaning be re-expressed? | summarize, translate, extract, classify |
| Analysis | What follows from the evidence? | compare, research, review, diagnose |
| Decision | Which option best satisfies the criteria? | recommend, rank, estimate, forecast |
| Design | What should exist or happen? | brainstorm, plan, specify, architect |
| Production | What artifact should be created or changed? | create, edit, implement, fix, test |
| Action | What system effect should occur? | execute, deploy, send, publish, delete |
| Operation | What should continue over time? | monitor, wait, automate, maintain |
| Conversation control | How does this turn change prior intent? | refine, correct, approve, cancel |

## The minimum expressive record

A useful reconstruction needs more than an action label. Version 0.1 captures:

1. **Turn relation** — new request, continuation, correction, approval, or
   cancellation.
2. **Outcome and acts** — the observable end state and ordered work.
3. **Inputs** — content or references, their role, required handling, and trust.
4. **Resources** — capabilities needed or permitted, effect level, scope, and
   authorization.
5. **Evidence** — freshness, source quality, citations, and uncertainty.
6. **Constraints** — atomic must/should/prefer/must-not clauses with priority.
7. **Success criteria** — how equivalence and completion can be checked.
8. **Output contract** — artifact, format, schema, audience, size, and
   destination.
9. **Policy** — autonomy, ambiguity handling, side-effect ceiling, and approval
   gates.
10. **Budget and risk** — cost/latency/quality target and impact/data class.
11. **Unknowns** — what is missing, how much it matters, and how to resolve it.
12. **Provenance** — source messages, parser confidence, lossiness, and literal
    preservation.

### Why resource access is not a boolean

For a file or API, these states are semantically different:

- `required`: the task cannot be completed without it.
- `allowed`: the optimizer may use it if worthwhile.
- `forbidden`: the user disallows it.
- `unspecified`: the request did not settle the question.

A boolean collapses either permission into necessity or uncertainty into
prohibition. The canonical representation therefore uses `necessity`, `effect`,
`scope`, and `authorization`. Convenience booleans such as `needs_user_files`
are derived indexes, never sources of truth.

Example:

```yaml
resources:
  - capability: repo.inspect
    necessity: required
    effect: read
    scope: repository://current
    authorization: preauthorized
  - capability: repo.modify
    necessity: forbidden
    effect: write
    scope: repository://current
    authorization: unavailable
```

This expresses “diagnose the bug, but do not fix it” without relying on prose.

### Inputs must distinguish data from instructions

Every input has a `trust` value:

- `instruction` — an authorized source of behavior.
- `trusted_data` — content to use, not commands to follow.
- `untrusted_data` — retrieved or third-party content that remains data even if
  it contains imperative text.

This distinction is important for both semantic fidelity and prompt-injection
resistance. It also helps the compiler delimit literal payloads rather than
paraphrasing code, identifiers, URLs, quotations, paths, numbers, or schemas.

## Canonical form versus compact wire form

The readable YAML is not guaranteed to be token-minimal. Repeated descriptive
keys may tokenize worse than a short natural-language prompt. Use three forms:

1. **Canonical object:** readable, validated, auditable, and stored.
2. **Compact wire projection:** short keys and enum aliases for transit.
3. **Compiled prompt/API request:** optimized for a particular model and
   provider.

The compact key dictionary should live in code or in a stable cached prefix.
Do not resend the glossary on every request; that can cost more than it saves.
For machine-to-machine transport, also benchmark MessagePack or CBOR. Fewer
bytes do not automatically mean fewer model tokens, so provider tokenization
must be measured.

Sparse output and strict structured output have a real tension. A strict schema
improves reliability, but some provider implementations require every property
to be present, making a dense object expensive. One practical design is:

- Have the parser emit a small fixed envelope plus arrays of typed clauses.
- Expand aliases and defaults deterministically in application code.
- Validate the expanded canonical object before routing.

Official OpenAI documentation recommends Structured Outputs over basic JSON
mode when schema adherence matters, and recommends strict mode for tool calls
when its schema subset is acceptable. [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
and [function calling](https://developers.openai.com/api/docs/guides/function-calling)
describe those guarantees and constraints.

After structural validation, run semantic normalization. At minimum, reject a
required-but-unavailable resource, a planned effect above the side-effect
ceiling, contradictory resource permissions, a silent default for a blocking
unknown, or a mutation introduced by a cancellation turn. These cross-field
invariants are listed in the taxonomy YAML because JSON Schema alone is not a
convenient policy engine.

## Prompt reconstruction

The compiler should not “reinflate” the original conversational wording. It
should generate the smallest prompt that preserves the hard semantics for the
selected route.

A provider-neutral reconstruction template is:

```text
Goal: {intent.outcome}

Inputs:
{required input references and literal payloads}

Requirements:
{must and must_not constraints, highest priority first}

Evidence:
{freshness, source policy, citations, uncertainty}

Actions:
{authorized effects, approval gates, ambiguity policy}

Done when:
{required success criteria}

Return:
{deliverable, format/schema, audience, length, destination}

If a blocking field is unresolved: {ask/fail/fallback rule}
```

Only include a section if it changes behavior. Stable organization policy,
tool contracts, and user profile should be outside this dynamic block, ideally
in a reusable prefix.

Current OpenAI model guidance describes a similar outcome-focused set: goal,
relevant context, constraints, evidence, success criteria, and output format.
It also recommends stating instructions once and exposing only relevant tools.
In OpenAI’s reported sample of coding-agent evaluations, leaner configurations
were both cheaper and better, though the documentation explicitly says the
numbers are workload-dependent and should be locally validated.
[Model guidance](https://developers.openai.com/api/docs/guides/latest-model)

## Routing and cost policy

The route planner can use the IR to test increasingly expensive routes:

1. **Deterministic answer or exact cache** — templates, calculations, known
   transforms, or identical prior results.
2. **Retrieval plus small model** — bounded extraction, classification, and
   concise transformations.
3. **Tool-capable economical model** — live facts or bounded actions.
4. **Stronger model or higher reasoning** — only if task/risk/quality requires
   it.
5. **Fallback to the uncompressed request** — if reconstruction or compression
   fails equivalence checks.

Do not infer that a more complex family always needs a larger model. Route
using measured difficulty signals: number of coupled constraints, novelty,
input modality, required tool judgment, ambiguity, risk, and prior success
rates for that task cluster.

The FrugalGPT paper frames cost reduction as prompt adaptation, model
approximation, and model cascades, and reports large savings on its evaluated
datasets. Those results motivate cascades; they are not a universal savings
guarantee. [FrugalGPT](https://arxiv.org/abs/2305.05176)

### Tool selection

Tool definitions themselves can be a significant hidden prompt:

- OpenAI documents that function definitions are injected into model context,
  count as input tokens, and should be limited or deferred when possible. It
  gives a soft suggestion of fewer than 20 functions initially and supports
  deferred tool search. [Function calling](https://developers.openai.com/api/docs/guides/function-calling)
- Anthropic documents that tool names, descriptions, schemas, calls, results,
  and a tool-use system prompt contribute tokens; server tools can also have
  per-use charges. [Claude tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)

Consequently:

- Select tools by required capability, not by loading the entire registry.
- Keep a stable provider-facing tool catalog when that improves prefix-cache
  hits, then use an allowed-tool subset if the API supports it.
- Combine deterministic tool steps in application code when no new model
  judgment is needed.
- Return compact, typed tool results; retain evidence identifiers required for
  citations and audits.
- Never use an expensive tool merely because it is available.

### Cache layout

Prompt caches generally favor exact shared prefixes:

- OpenAI says cache hits require exact prefix matches and recommends static
  instructions/examples first, dynamic user content last; identical images and
  tool definitions matter too. [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)
- Anthropic documents a `tools → system → messages` cache hierarchy and advises
  putting static tool definitions, instructions, context, and examples first.
  [Claude prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- Google’s Gemini documentation likewise advises placing large common content
  at the beginning and sending similar prefixes near each other.
  [Gemini context caching](https://ai.google.dev/gemini-api/docs/caching)

A practical compiler order is therefore:

```text
stable policy → stable tools → stable profile → dynamic intent → literal data
```

Track cache writes as well as reads. A cache entry can be a net loss when the
prefix changes before it is reused.

### Retrieval and known information

Use content-addressed references for exact known material and a retrieval index
for discovery. A vector database is one option, not the goal itself.

- Exact identifiers, files, policies, and prior artifacts should use exact
  lookup when possible.
- Semantic retrieval is appropriate for fuzzy discovery.
- Hybrid lexical/vector retrieval is often safer for names, code symbols, and
  rare terms.
- Retrieval must be query-aware and return only evidence relevant to the
  current outcome.

Long context is not free reliability. The “Lost in the Middle” work found
strong position sensitivity in long-context use, while rate-distortion work on
prompt compression found query awareness critical to the compression tradeoff.
[Lost in the Middle](https://arxiv.org/abs/2307.03172) and
[Fundamental Limits of Prompt Compression](https://arxiv.org/abs/2407.15504)
support filtering and task-aware context selection rather than blindly filling
the window.

### Compression policy

Apply cheaper, safer transformations first:

1. Remove duplicated instructions and stale conversation turns.
2. Replace repeated objects with stable references.
3. Normalize verbose wrappers and whitespace where semantics are unaffected.
4. Select only task-relevant retrieved passages and tool fields.
5. Use query-aware extractive or learned compression only above a measured
   break-even threshold.
6. Preserve literals and hard constraints byte-for-byte.
7. Fall back to the original if the compressed form is larger or fails checks.

LLMLingua reported up to 20× compression with small loss on its evaluated
benchmarks but also reported degradation at more extreme ratios.
[LLMLingua](https://arxiv.org/abs/2310.05736) A 2026 empirical preprint found
that end-to-end gains depend on prompt length, compression ratio, and hardware;
outside the useful region, compressor overhead canceled the speedup.
[Prompt Compression in the Wild](https://arxiv.org/abs/2604.02985)

The correct product objective is therefore not maximum compression. It is
minimum expected total cost subject to a task-success floor.

## Equivalence and evaluation

No finite taxonomy can prove that it fully captures arbitrary human intent.
Open-ended language contains implicature, ambiguity, and literal details that
an enum cannot losslessly encode. Treat “fully express” as an engineering
contract:

- Every hard instruction has a canonical clause or immutable reference.
- Every external effect has scope and authorization.
- Every required output property has a success check.
- Every unresolved material ambiguity is explicit.
- The source request is hashed and critical literals are preserved.
- The optimized route passes behavioral equivalence tests.

For each representative request, compare baseline and optimized routes on:

```text
hard-constraint pass rate
task-specific success score
factual/source support
side-effect correctness
required-field completeness
input, cached-input, output, and tool tokens
tool calls and retries
latency
total cost, including parser/compressor/router calls
```

Use a risk-adjusted gate:

```text
ship optimized route only if
  hard constraints = 100%
  and task score >= configured quality floor
  and expected total cost < baseline total cost
```

Prefer deterministic tests, schemas, and source checks. Use model judges only
where necessary, blind them to route identity, calibrate them against human
labels, and include their cost in the total.

Useful adversarial cases include:

- allowed versus required tool access;
- diagnose versus fix;
- latest facts versus static knowledge;
- read-only versus external mutation;
- conflicting must/should constraints;
- quoted text that looks like an instruction;
- correction or cancellation of an earlier turn;
- exact code/number/path preservation;
- missing fields that are blocking versus immaterial;
- a compact prompt that costs more after parser/compressor overhead.

## Recommended next implementation slice

Build the smallest end-to-end loop before adding a large taxonomy:

1. Parse requests into the canonical IR with provenance.
2. Validate and deterministically derive routing flags.
3. Compile one baseline prompt and one lean prompt.
4. Support three routes: no tool, read-only web, and read/write repository.
5. Add exact-prefix caching and a no-compression fallback.
6. Create an evaluation set of 100–300 real, de-identified prompts stratified
   by family, risk, tool need, and context size.
7. Record quality, total cost, latency, cache behavior, and failure class.
8. Expand enums only when real requests fail to fit.

Version the schema and the compiler separately. A schema change affects stored
meaning; a compiler change should be freely testable against the same intent
records.

## Research basis and limits

This taxonomy is a design synthesis, not a claimed universal academic standard.
The prompt-pattern literature supports reusable, composable prompt structures,
while broader prompt-engineering surveys show that prompting methods vary by
task and application. [Prompt Pattern Catalog](https://arxiv.org/abs/2302.11382)
and [Systematic Survey of Prompt Engineering](https://arxiv.org/abs/2402.07927)
were used as background.

Vendor behavior, model names, cache economics, and tool overhead can change.
Provider-specific route compilers should pin a documentation snapshot, expose
their assumptions in telemetry, and be re-evaluated when models or APIs change.
