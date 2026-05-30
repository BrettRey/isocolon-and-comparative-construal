# Fake-Data Simulation

## Purpose

The first fake-data simulation asks whether the current GUM/eRST adjacent-pair
design can recover a known isocolonicity effect before we treat the observed
relation effects as evidence.

The simulation uses the real row structure from
`data/derived/gum_erst_adjacent_isocolon_scores.tsv`, but replaces the outcome
with generated data. It therefore preserves document, genre, target
prevalence, explicitness, punctuation, same-sentence status, and unit-length
structure.

## Target Definitions

Two target definitions are currently used:

- `narrow`: `adversative-antithesis`, `adversative-contrast`
- `broad`: `adversative-antithesis`, `adversative-contrast`,
  `joint-disjunction`, `joint-list`

These are not final theoretical categories. They are stress-test definitions.
The narrow definition asks whether the design can recover effects with a small
target cell. The broad definition asks whether a comparison-like family has
enough support for a corpus-only test.

## Analysis Model

The recovery model estimates the target effect after adjusting for:

- document fixed effects
- explicit versus implicit relation
- same-sentence status
- colon boundary
- semicolon boundary
- log mean unit length
- log maximum unit length

The estimator uses residualized least squares via the Frisch-Waugh-Lovell
theorem. This is fast and transparent, but it is not the final model for the
paper. It is a screening approximation.

## Simulation Grid

Command:

```bash
scripts/fake_data_simulation.py
```

Default settings:

- 200 simulations per scenario
- true target effects: 0, 0.02, 0.04, 0.06, 0.08
- label-error rates: 0, 0.1, 0.2
- row-level noise SD: 0.12
- document random-effect SD: 0.045
- genre random-effect SD: 0.025

Outputs:

- `data/derived/fake_data_simulation_design.tsv`
- `data/derived/fake_data_simulation_draws.tsv`
- `data/derived/fake_data_simulation_summary.tsv`
- `outputs/figures/fake_data_recovery_power.png`

## Results From First Run

The design has 17,456 adjacent-pair rows across 299 documents and 24 genres.
The broad target definition includes 2,462 rows (14.10%). The narrow target
definition includes 605 rows (3.47%).

With clean labels, both target definitions recover effects on the 0--1
isocolonicity scale with little bias. False-positive rates at true effect 0
are close to the nominal 5% level: 4.5% for broad and 3.5% for narrow.

The main stress-test result is label-noise attenuation. With 20% label error,
a true effect of 0.04 is recovered as about 0.024 under both target
definitions. With 10% label error, a true effect of 0.04 is recovered as about
0.032. This means that label uncertainty is likely a larger threat than raw
sample size.

The simulation is optimistic in one respect: it assumes the scoring outcome is
well represented by a linear Gaussian model after document adjustment. The next
simulation should add noisier measurement channels or a latent isocolonicity
score so that the score itself is treated as fallible.
