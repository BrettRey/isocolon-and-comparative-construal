# Gauging Isocolonicity

## Working Definition

For this project, \term{isocolonicity} should be treated as a graded textual
property of a relation pair, not as a binary label. The score should capture
how far two adjacent units resemble balanced cola: similar length, similar
syntactic shape, and some lexical or formulaic parallelism.

The primary score should be computed from text and UD annotations, before
looking at the relation effect. eRST gold signal annotations such as
`syn-prl` are useful as validation or as a separate outcome, but they should
not be folded into the primary score if the aim is to test whether relations
predict isocolonic form.

## Current Operational Score

`scripts/score_gum_isocolon.py` reads
`data/derived/gum_erst_adjacent_relation_pairs.tsv` and writes
`data/derived/gum_erst_adjacent_isocolon_scores.tsv`.

The current score has three subscales.

First, length balance:

- word-token balance, excluding punctuation
- character balance, excluding non-word characters
- approximate syllable balance

Each balance measure is:

```text
1 - abs(n1 - n2) / max(n1, n2)
```

Second, syntactic parallelism:

- UPOS sequence similarity
- XPOS sequence similarity
- dependency-relation sequence similarity

Each sequence similarity is normalized edit-distance similarity:

```text
1 - edit_distance(seq1, seq2) / max(len(seq1), len(seq2))
```

Third, lexical parallelism:

- lemma sequence similarity
- content-lemma Jaccard overlap

The composite score is currently:

```text
0.40 * length_score + 0.45 * syntax_score + 0.15 * lexical_score
```

This gives length and syntax most of the weight, because classical isocolon
is mainly equality of cola and parallel construction. Lexical repetition
matters, but it should not dominate the measure, since many strong isocola
use different lexical material in matched slots.

The script also records `has_gold_syn_prl`, a diagnostic flag for GUM/eRST's
gold `syn-prl` signal. This is not part of the composite score.

## First Sanity Check

On 2026-05-30, the scorer produced 17,456 adjacent-pair rows. The mean
isocolonicity score was 0.3276, the median was 0.3276, and the 90th
percentile was 0.4967. There were no zero-word-side rows after including
tokens tagged `X` as words.

Coarse relation means are directionally plausible for a first pass:

- reformulation: 0.4750
- alternation: 0.4091
- conjunction: 0.4044
- contrast: 0.3823
- causal: 0.3577
- concession: 0.3423
- condition: 0.3396
- elaboration: 0.3269
- explanation: 0.2911
- organization: 0.2526
- attribution: 0.2513

Original-label means relevant to the project:

- `joint-list`: 0.4073
- `adversative-contrast`: 0.4080
- `adversative-antithesis`: 0.3626
- `adversative-concession`: 0.3423
- `joint-sequence`: 0.3747
- `joint-disjunction`: 0.4091
- `joint-other`: 0.3738
- `causal-cause`: 0.3558
- `causal-result`: 0.3606
- `contingency-condition`: 0.3396
- `elaboration-additional`: 0.3302

These are descriptive checks only. They are not evidence for the paper's
claim until the model controls for genre, text, relation type, length,
connective status, and syntactic opportunity.

## Cautions

The present syllable measure is heuristic. It is useful for ranking and
diagnostics, but not enough for a prosodic claim.

The sequence measures are order-sensitive, which is appropriate for
parallelism but can penalize legitimate reordering. This is a feature for
isocolon, not a general syntactic-similarity claim.

The composite weights are defensible but arbitrary. The model should also
report subscale results separately. A latent-variable model can come later if
the pilot justifies it.
