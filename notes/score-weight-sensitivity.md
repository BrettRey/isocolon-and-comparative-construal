# Score-Weight Sensitivity

## Purpose

The current isocolonicity score uses a chosen weighting:

```text
0.40 * length + 0.45 * syntax + 0.15 * lexical
```

That weighting is defensible, but it should not be allowed to carry the main
empirical result. This check asks whether the target effects survive when the
length, syntax, and lexical components are reweighted.

Command:

```bash
scripts/score_weight_sensitivity.py
```

Outputs:

- `data/derived/score_weight_sensitivity.tsv`
- `data/derived/score_weight_sensitivity_summary.tsv`
- `outputs/figures/score_weight_sensitivity.png`

The script fits the same document-adjusted model as the observed baseline. It
tests named alternatives, including component-only scores, and a grid of
nonnegative weights over the three score components.

## Broad Target

The broad target is robust to the score weighting. Across the 66-point weight
grid, every estimate is positive and every interval excludes zero.

Grid summary:

- minimum estimate: 0.0080
- median estimate: 0.0343
- maximum estimate: 0.0770
- share positive: 1.00
- share with positive interval: 1.00

Named specifications:

- current: 0.0415
- equal weights: 0.0364
- length only: 0.0080
- syntax only: 0.0770
- lexical only: 0.0244
- length/syntax: 0.0425
- syntax/lexical: 0.0507
- length/lexical: 0.0162

This means the broad result is not an artifact of the current composite score.
The effect is strongest for syntactic parallelism, but it is also positive for
length balance and lexical similarity.

## Narrow Target

The narrow target is weaker. Across the grid, 65 of 66 estimates are positive,
but the length-only estimate is slightly negative and its interval crosses
zero.

Grid summary:

- minimum estimate: -0.0014
- median estimate: 0.0142
- maximum estimate: 0.0243
- share positive: 0.985
- share with positive interval: 0.848

Named specifications:

- current: 0.0130
- equal weights: 0.0135
- length only: -0.0014
- syntax only: 0.0243
- lexical only: 0.0175
- length/syntax: 0.0115
- syntax/lexical: 0.0209
- length/lexical: 0.0080

The narrow result is mainly a syntax/lexical result, not a length-balance
result. That matters because traditional isocolon is often described as
balanced length plus parallel structure. If the paper wants to claim narrow
antithesis-like isocolon, this operationalization is still too thin.

## Interpretation

This check strengthens the broad empirical claim and weakens the narrow one.
The current best formulation is:

> List, disjunction, and contrast-like relation pairs show more formal
> parallelism across several reasonable measurements of isocolonicity.

The result should not be phrased as a discovery that antithesis is generally
isocolonic in GUM/eRST. The stronger finding is about a broader comparative or
coordinative construal family, with syntactic parallelism doing much of the
measurable work.
