You are auditing the numbers in a corpus-linguistics manuscript against the analysis outputs that produced them. Work read-only and return your full report as your final message.

Files (all in the current directory):
- `main.tex`: the manuscript. Numbers are hard-coded.
- `derived/*.tsv`: analysis outputs. `gum_erst_adjacent_isocolon_scores.tsv` has one row per adjacent discourse-relation pair (17,912 rows) with `isocolon_score` (the composite formal-balance score, 0-1), `length_score` (the paper's "isocolon" subscore), `syntax_score` ("parison"), `lexical_score` ("lexical echo"), `orig_label` (eRST relation label), `genre`, `collection`, `rel_type`. The other files hold model estimates (`robustness_checks.tsv`, `observed_isocolon_effects.tsv`), extraction counts, validation against `syn-prl` signals (AUC and threshold slices), genre-varying (empirical-Bayes) summaries, composite-weight sensitivity, stratified permutation nulls, and leave-one-genre checks. Work out which file and row/column each manuscript number comes from yourself; the manuscript defines its target groups (see the "Defining the target relations" subsection and its table).

The paper reports effects as score points: raw 0-1 differences multiplied by 100, one decimal. In the score-calibration table, "Gap" is the displayed (rounded) score minus the displayed (rounded) non-target median.

Task:
1. Check every number in the abstract, body, tables, captions, and appendices that should derive from these outputs (counts, estimates, intervals, AUCs, percentages, medians, SDs, ratios, genre counts, ranges). Recompute from the TSVs; don't trust the manuscript.
2. Check derived arithmetic and verbal approximations in the text (for example "about 0.28 standard deviations", "about a fifth", "about seven times", "wins about N times in 100", ordering claims such as "slightly higher", "near zero", "crosses zero").
3. Skip numbers that are not data-derived (the scoring weights 0.40/0.45/0.15, the worked 8-versus-10-word example, the 80-pair human audit table, the 500 permutations, the 66 weightings count, percentile cutoffs as labels).

Report format:
- MISMATCHES: line number, manuscript value, value you computed, source file and row/column, and how you computed it.
- UNTRACEABLE: numbers you couldn't tie to any output, with line numbers.
- VERIFIED: a compact count of numbers checked and matched, grouped by section.
- Any other errors you notice in how numbers are described.
Show your commands or code for anything non-obvious. Don't claim a check passed unless you ran it.
