# Genre-Varying Shrinkage Model

## Purpose

The genre sensitivity check estimated each genre separately. That is useful,
but the noisiest genres can look too extreme because they have few documents
or few target rows. This step applies a simple empirical-Bayes shrinkage model
to those genre-specific estimates.

Command:

```bash
scripts/fit_genre_varying_effects.py
```

Outputs:

- `data/derived/genre_varying_effects.tsv`
- `data/derived/genre_varying_summary.tsv`
- `outputs/figures/genre_varying_effects.png`

For each target, the model treats the observed genre estimate as a noisy
measurement of a genre-specific effect. Genre effects are assumed to come from
a normal distribution with corpus-level mean `mu` and between-genre standard
deviation `tau`. The script chooses `mu` and `tau` by marginal likelihood and
then reports the posterior mean for each genre.

This is a transparent approximation to a varying-effects model, not the final
Bayesian model.

## Corpus-Level Estimates

The broad target remains clearly positive after genre-varying shrinkage:

- broad: `mu = 0.0390`, `tau = 0.0111`, 20 genres
- joint-list: `mu = 0.0398`, `tau = 0.0130`, 17 genres
- adversative-contrast: `mu = 0.0291`, `tau = 0.0071`, 4 genres
- narrow: `mu = 0.0118`, `tau = 0.0090`, 15 genres

The main contrast is still broad versus narrow. The broad category has a
substantial genre-level mean. The narrow category has a smaller and less stable
mean, even though shrinkage pulls several noisy negative estimates back toward
the positive corpus-level mean.

## Broad Target

After shrinkage, the broad target is positive in every retained genre. The
largest shrunk estimates are:

- textbook: 0.0532
- interview: 0.0522
- dictionary: 0.0493
- conversation: 0.0485
- speech: 0.0482
- court: 0.0439

The smallest shrunk estimates are:

- reddit: 0.0191
- news: 0.0290
- WikiHow: 0.0295
- vlog: 0.0299
- academic: 0.0323

This makes a pure genre-composition explanation unlikely. The effect varies by
genre, but it is not only an artifact of a few high-parallelism genres.

## Narrow Target

The narrow target is much weaker. The largest shrunk estimates are:

- interview: 0.0197
- conversation: 0.0175
- vlog: 0.0167
- textbook: 0.0166
- fiction: 0.0155

The smallest shrunk estimates are:

- WikiHow: 0.0021
- speech: 0.0048
- academic: 0.0061
- podcast: 0.0081
- voyage: 0.0105

The narrow category should not be the main empirical target unless the paper
has a separate theoretical reason for grouping antithesis with other
comparison-like relations. As a corpus signal, it is much less robust than the
broad list/disjunction/contrast family.

## Interpretation

The current best empirical claim is:

> Across genres, adjacent relation pairs in list, disjunction, and contrast-like
> configurations show more formal parallelism than otherwise similar pairs,
> after document and surface-form controls.

This should be framed as a rhetorical-function test of comparative construal
only if the theory licenses that broader functional grouping. If the claim is
about antithesis narrowly, the present corpus evidence is weak and will need
additional annotation or a different operationalization.
