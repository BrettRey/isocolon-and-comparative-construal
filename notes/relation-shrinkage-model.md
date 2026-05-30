# Relation Shrinkage Model

## Purpose

The relation-effect atlas estimates one label at a time. That is useful for
discovery, but it does not share information across relation labels. The next
step is a single relation-label model with shrinkage, which approximates the
partial-pooling move we would want in a fuller Bayesian model.

Command:

```bash
scripts/fit_relation_shrinkage.py
```

Outputs:

- `data/derived/relation_shrinkage_effects.tsv`
- `data/derived/relation_shrinkage_summary.tsv`
- `outputs/figures/relation_shrinkage_effects.png`

## Model

The script uses the same adjustment set as the observed baseline:

- document fixed effects
- explicit versus implicit relation
- same-sentence status
- colon boundary
- semicolon boundary
- log mean unit length
- log maximum unit length

It residualizes the outcome and relation-label indicators against those
controls, then fits a ridge model over relation labels. The ridge penalty is
chosen by generalized cross-validation. Relation labels with fewer than 75
rows are grouped into `__rare__`.

This is not a full Bayesian multilevel model, but it has the key property we
need at this stage: small and unstable relation effects are pulled toward the
overall relation mean.

## First Results

For the composite isocolonicity score, the selected ridge penalty is 5.0119,
with effective degrees of freedom 29.38 across 31 relation groups.

Largest positive shrunk adjusted effects:

- `restatement-repetition`: 0.1759
- `joint-disjunction`: 0.0550
- `joint-list`: 0.0423
- `adversative-contrast`: 0.0303
- `joint-sequence`: 0.0262

Weak or uncertain project-relevant effects:

- `adversative-antithesis`: 0.0074
- `joint-other`: 0.0052
- `adversative-concession`: -0.0038

The shrinkage model keeps the relation-effect atlas's substantive ordering,
but pulls unstable negative and positive one-vs-rest estimates toward zero.
This is preferable for reporting relation-specific effects.

## Interpretation

The result is now clearer:

1. The measurement positive control works: `restatement-repetition` is much
   higher than any comparison-like relation.
2. The strongest comparison-adjacent effects are in disjunction, list, and
   adversative contrast.
3. Antithesis and concession should not be merged into the main positive
   target without a separate theoretical reason.

For the paper, this suggests a relation-specific claim rather than a single
comparison-vs-noncomparison contrast.
