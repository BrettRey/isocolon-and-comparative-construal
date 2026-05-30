# Genre Sensitivity

## Purpose

The earlier sensitivity checks showed that the broad target effect survives
large subset exclusions. The genre sensitivity check asks whether the effect
is visible within individual genres or whether it is mainly a genre-composition
artifact.

Command:

```bash
scripts/genre_sensitivity.py
```

Outputs:

- `data/derived/genre_sensitivity_effects.tsv`
- `outputs/figures/genre_sensitivity_effects.png`

The script estimates document-adjusted target effects separately within each
genre when there are at least 20 target rows, 50 non-target rows, and 3
documents. The adjustment set is the usual one: explicitness, same-sentence
status, colon and semicolon boundary, log mean unit length, log max unit
length, and document fixed effects.

## Broad Target

The broad target is positive in every genre with enough data. It is largest in
dictionary, textbook, interview, conversation, speech, and court, and smallest
in Reddit, news, vlogs, WikiHow, and poetry.

Selected broad-target adjusted effects:

- dictionary: 0.0953
- textbook: 0.0602
- interview: 0.0600
- conversation: 0.0566
- speech: 0.0537
- court: 0.0471
- fiction: 0.0403
- essay: 0.0391
- academic: 0.0282
- news: 0.0232
- reddit: 0.0141
- poetry: 0.0151, interval crossing zero

This supports the claim that the broad effect is not only a genre-composition
artifact, though genre clearly modulates its size.

## Narrow Target

The narrow target is much less stable across genres. Positive estimates appear
in conversation, interview, vlog, and textbook, but several genres have
intervals crossing zero, and some estimates are near zero or negative.

Selected narrow-target adjusted effects:

- conversation: 0.0382
- interview: 0.0370
- vlog: 0.0358
- textbook: 0.0276
- fiction: 0.0233, interval crossing zero
- reddit: 0.0143, interval crossing zero
- academic: -0.0088, interval crossing zero
- whow: -0.0127, interval crossing zero
- speech: -0.0237, interval crossing zero

This again warns against treating antithesis and contrast as one robust
target category.

## Interpretation

The broad target has cross-genre support, but the theory has to explain why
the signal is strongest for list/disjunction/contrast structures rather than
for all adversative relations. The safest empirical claim is now:

> Across genres, adjacent relation pairs in list/disjunction/contrast-like
> configurations show more formal parallelism than otherwise similar pairs,
> after document and surface-form controls.

The next model should let the target effect vary by genre rather than forcing
a single common effect.
