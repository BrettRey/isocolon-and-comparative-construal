# Observed Baseline

## Purpose

After the fake-data recovery check, the next step is a transparent
observed-data baseline. This is not the final model. It is a diagnostic fit
using the same adjustment set as the simulation:

- document fixed effects
- explicit versus implicit relation
- same-sentence status
- colon boundary
- semicolon boundary
- log mean unit length
- log maximum unit length

Command:

```bash
scripts/fit_observed_isocolon.py
```

Outputs:

- `data/derived/observed_isocolon_effects.tsv`
- `outputs/figures/observed_isocolon_effects.png`

## Target Definitions

The baseline uses these target definitions:

- `narrow`: `adversative-antithesis`, `adversative-contrast`
- `broad`: `adversative-antithesis`, `adversative-contrast`,
  `joint-disjunction`, `joint-list`
- individual checks: `joint-list`, `adversative-contrast`,
  `adversative-antithesis`, `adversative-concession`

The broad definition is deliberately generous. It tests whether
comparison-like coordination and adversative comparison form a high-balance
family. The individual checks test whether that family is internally coherent.

## First Results

For all adjacent pairs, the adjusted broad-target effect on the composite
isocolonicity score is 0.0415, with 95% interval 0.0375--0.0455. The adjusted
narrow-target effect is 0.0130, with 95% interval 0.0058--0.0202.

The broad effect is stable across basic sensitivity subsets:

- all adjacent: 0.0415
- GUM only: 0.0401
- excluding dictionary and poetry: 0.0412
- same-sentence pairs only: 0.0381
- written-core genres: 0.0377
- colon or semicolon boundary: 0.0751

The narrow effect is smaller and less stable:

- all adjacent: 0.0130
- GUM only: 0.0145
- excluding dictionary and poetry: 0.0138
- same-sentence pairs only: 0.0101
- written-core genres: 0.0074, with interval crossing zero

## Subscales

For all adjacent pairs, the broad target effect appears on all subscales, but
mostly on syntax:

- length score: 0.0080
- syntax score: 0.0770
- lexical score: 0.0244

For the narrow target, length does not move after controls:

- length score: -0.0014
- syntax score: 0.0243
- lexical score: 0.0175

This matters for interpretation. The current corpus signal is more clearly a
parallel-syntax signal than a pure equal-length-cola signal.

## Internal Coherence Check

The individual-label checks show that the broad effect is not homogeneous:

- `joint-list`: 0.0439
- `adversative-contrast`: 0.0241
- `adversative-antithesis`: 0.0039, interval crossing zero
- `adversative-concession`: -0.0131

This is a useful warning. If the paper claims "comparison" too broadly, it
will blur different rhetorical relations. The safer current claim is that
joint-list and adversative-contrast relations show elevated formal parallelism
after basic controls. Antithesis and concession need separate treatment.

## Next Modeling Implication

The final model should not pool contrast, antithesis, concession, and list as
though they are one clean category. It should either:

1. model individual relation labels with partial pooling, or
2. define the target more narrowly as a theoretically motivated family and
   report individual-label checks as a necessary sensitivity analysis.

The current baseline supports continuing, but it also narrows the claim.
