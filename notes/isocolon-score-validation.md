# Isocolon Score Validation

## Purpose

The computed isocolonicity score is a measurement instrument. Before treating
it as an outcome, it needs a check against an independent annotation. GUM/eRST
contains gold `syn-prl` signals for parallel syntactic construction, which
provide a useful but partial validation target.

Command:

```bash
scripts/validate_isocolon_score.py
```

Outputs:

- `data/derived/isocolon_score_validation_summary.tsv`
- `data/derived/isocolon_score_thresholds.tsv`
- `data/derived/isocolon_score_validation_examples.tsv`
- `outputs/figures/isocolon_score_validation.png`

## Quantitative Check

There are 73 adjacent relation pairs flagged with gold `syn-prl`, out of
17,456 adjacent pairs. The base rate is only 0.42%, so threshold precision is
expected to be low even if ranking is useful.

Against the gold `syn-prl` flag:

- composite isocolonicity AUC: 0.731
- length score AUC: 0.646
- syntax score AUC: 0.754
- lexical score AUC: 0.719

The syntax subscale is the strongest single component, which fits the
annotation target: `syn-prl` is a syntactic-parallelism signal, not a general
equal-length-cola label.

At the 95th percentile of the composite score, precision is 3.08%, recall is
36.99%, and lift over the base rate is 7.37. At the 97.5th percentile,
precision is 5.48%, recall is 32.88%, and lift is 13.10. This is useful for
ranking candidates, not for automatic binary classification.

## Qualitative Check

High-scoring gold examples look like genuine isocola:

- "You can use this on twist outs." / "You can use this on braid outs."
- "Somebody can manage to be a teacher." / "Somebody can manage to be a cop."
- "it's all open hardware." / "It's all open source."

High-scoring non-gold examples are often exact repetitions:

- "Two." / "Two."
- "Thank you." / "Thank you."
- "Smart ass." / "Smart ass."

These are not necessarily false positives for formal balance. They are false
positives only relative to the `syn-prl` validation flag. This reinforces the
need to treat `restatement-repetition` separately in the main model.

Some low-scoring gold rows show why the validation flag is partial. Gold
`syn-prl` can attach to local structure inside a larger pair, while the
computed score evaluates the whole relation pair. Example:

- "If an anesthesiologist or a surgeon is distracted by the technology in the
  operating room," / "that can create a problem."

That is not strongly isocolonic as a two-colon pair even if a local syntactic
parallelism signal exists.

## Interpretation

The score is good enough as a continuous ranking and modeling outcome, but it
should not be turned into a binary classifier. It measures broader formal
balance than the gold `syn-prl` signal, and it deliberately includes length
and lexical balance as well as syntax.

For the paper, this validation supports three decisions:

1. Report subscales, especially syntax, alongside the composite.
2. Treat repetition/restatement as a positive-control relation family.
3. Use high-score examples for qualitative sanity checks, not as automatic
   gold labels.
