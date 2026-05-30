# Relation-Effect Atlas

## Purpose

The observed baseline still depended on hand-selected target definitions. The
relation-effect atlas asks a broader diagnostic question: after the same basic
controls, which eRST original relation labels have the largest adjusted
association with isocolonicity?

Command:

```bash
scripts/relation_effect_atlas.py
```

Outputs:

- `data/derived/observed_relation_effect_atlas.tsv`
- `outputs/figures/observed_relation_effect_atlas.png`

The script estimates one-vs-rest adjusted effects for every original relation
label with at least 75 adjacent-pair rows. Outcomes include the composite
score and the length, syntax, and lexical subscales.

## Main Pattern

The largest positive composite effect is `restatement-repetition`, not a
comparison label:

- `restatement-repetition`: 0.1902

This is useful. It shows that the score is sensitive to overt formal
repetition and not merely to the labels we care about. It also means that
restatement/repetition needs separate handling in the model, because it can
otherwise set the upper benchmark for isocolonicity.

The next positive effects are closer to the current project:

- `joint-disjunction`: 0.0482
- `joint-list`: 0.0439
- `adversative-contrast`: 0.0241
- `joint-sequence`: 0.0205

Weak or null project-relevant labels:

- `joint-other`: 0.0049, interval crossing zero
- `adversative-antithesis`: 0.0039, interval crossing zero

Negative project-relevant label:

- `adversative-concession`: -0.0131

## Interpretation

The atlas reinforces the narrower interpretation from the observed baseline.
The current signal is not "adversativity" or "contrast" in general. It is
strongest for list/disjunction structures and present for
`adversative-contrast`, but not for `adversative-antithesis` or
`adversative-concession`.

That pushes the theoretical question toward comparative construal as matched
coordination or explicit contrast, not toward every adversative relation.

## Modeling Implication

The next model should include relation labels separately or with partial
pooling. A single broad target category is useful for screening, but the
paper's defensible claim should report relation-specific estimates. It should
also either control for or exclude `restatement-repetition`, depending on
whether repetition is treated as a comparison-free positive control or as a
competing rhetorical figure.
