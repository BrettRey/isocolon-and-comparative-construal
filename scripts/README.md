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
- `validate_isocolon_score.py`: checks the computed score against gold eRST `syn-prl` signals, writes AUC/threshold summaries with approximate AUC intervals, and exports high/low example rows for qualitative inspection.
- `genre_sensitivity.py`: estimates target effects separately by genre, using the same document-adjusted controls where each genre has enough target and comparison rows.
- `fit_genre_varying_effects.py`: applies an empirical-Bayes shrinkage model to the genre-specific target effects, giving stabilized genre estimates and corpus-level means for broad, narrow, joint-list, and adversative-contrast targets.
- `score_weight_sensitivity.py`: tests whether observed target effects depend on the current length/syntax/lexical component weights by fitting named alternatives and a simplex grid of nonnegative score weights.
- `fit_robustness_checks.py`: runs document-clustered uncertainty checks, mean-only and no-length-control length-balance models, joint-only matched comparisons, and adversative-only matched comparisons.
- `extraction_diagnostics.py`: summarizes interval-level extraction diagnostics, including valid rows, adjacent rows, non-adjacent exclusions, discontinuous spans, and duplicate adjacent span-pair keys.
- `fit_stratified_nulls.py`: runs document/length/punctuation-stratified permutation nulls for broad, list/disjunction, and adversative-contrast target labels.
- `fit_influence_checks.py`: runs leave-one-genre influence checks for broad, within-joint, and within-adversative target effects.
- `make_paper_figures.py`: generates the manuscript coefficient plots from `robustness_checks.tsv` and `stratified_nulls.tsv`.
- `prepare_antithesis_decomposition_audit.py`: extracts audited and full `adversative-antithesis` rows into worksheets for hand-coding classical antithesis, semantic opposition, and parallel opposition.
- `fit_antithesis_decomposition.py`: after those fields are coded, compares hand-marked antithesis subsets on formal balance, isocolon, parison, and lexical echo.
- `sample_qualitative_audit.py`: creates the reproducible 40-row qualitative audit sample, including high broad-target cases, typical broad-target cases, narrow cases, high-scoring non-targets, restatement controls, and baseline non-targets.
- `summarize_qualitative_audit.py`: validates four agent-review TSVs, combines ratings, and writes reviewer, consensus, and stratum-level summaries for the qualitative audit.
- `inspect_rst_signalling.py`: reads the protected local RST Signalling Corpus (`RST_SC_ROOT`, `LDC_ROOT`, or ignored `.ldc-root`) and writes aggregate-only inventories to `data/derived/`; it does not export raw text, examples, prompts, or row-level records.
- `summarize_rst_signalling.py`: reads only the aggregate RST Signalling inventory TSVs and writes aggregate split, signal-family, signal-subtype, project-bridge, and Markdown summaries; it does not read the protected corpus or export row-level records.
- `build_rst_signal_judgment_app.py`: builds the offline `rater_app/rst_signal_crosswalk.html` interface and aggregate item manifest for human/Rency label-crosswalk judgments; it reads only aggregate RST-SC TSVs and exports no raw corpus text.
- `ingest_rst_signal_judgments.py`: merges downloaded signal-crosswalk response JSON files from `rater_app/responses/` into local derived judgment and summary TSVs; it does not read the protected corpus.
