# Scripts

Project scripts belong here.

Expected scripts:

- corpus extraction;
- clause-pair candidate generation;
- isocolon scoring;
- fake-data simulation;
- model fitting;
- figure and table generation.

Current scripts:

- `inspect_gum_erst.py`: validates the local `data/raw/gum-erst` symlink and writes relation, signal, and manifest inventories to `data/derived/`.
- `extract_gum_erst_relation_pairs.py`: extracts valid eRST relation pairs with token spans, adjacency status, same-sentence status, colon/semicolon flags, token counts, and token-balance scores.
- `score_gum_isocolon.py`: scores adjacent eRST relation pairs for length balance, syntactic sequence similarity, lexical parallelism, and a first-pass composite isocolonicity score.
- `fake_data_simulation.py`: simulates known relation effects over the real adjacent-pair design matrix and checks whether a document-adjusted analysis recovers them under different target definitions, effect sizes, and label-error rates.
- `fit_observed_isocolon.py`: fits transparent observed-data baselines for broad, narrow, and individual relation targets across the composite score and subscales, with the same document-adjusted control set used in the fake-data simulation.
- `relation_effect_atlas.py`: estimates document-adjusted effects for every sufficiently frequent eRST original relation label and plots the largest positive and negative relation-label effects.
- `fit_relation_shrinkage.py`: fits a single document-adjusted ridge/shrinkage model for all sufficiently frequent eRST original relation labels, approximating partial pooling across relation effects.
- `validate_isocolon_score.py`: checks the computed score against gold eRST `syn-prl` signals, writes AUC/threshold summaries, and exports high/low example rows for qualitative inspection.
- `genre_sensitivity.py`: estimates target effects separately by genre, using the same document-adjusted controls where each genre has enough target and comparison rows.
- `fit_genre_varying_effects.py`: applies an empirical-Bayes shrinkage model to the genre-specific target effects, giving stabilized genre estimates and corpus-level means for broad, narrow, joint-list, and adversative-contrast targets.
- `score_weight_sensitivity.py`: tests whether observed target effects depend on the current length/syntax/lexical component weights by fitting named alternatives and a simplex grid of nonnegative score weights.
- `sample_qualitative_audit.py`: creates the reproducible 40-row qualitative audit sample, including high broad-target cases, typical broad-target cases, narrow cases, high-scoring non-targets, restatement controls, and baseline non-targets.
- `summarize_qualitative_audit.py`: validates four agent-review TSVs, combines ratings, and writes reviewer, consensus, and stratum-level summaries for the qualitative audit.
