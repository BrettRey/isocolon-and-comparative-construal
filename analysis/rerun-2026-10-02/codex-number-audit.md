<!-- Saved verbatim by the parent Claude Code session from Codex stdout, 2026-10-02. -->
**No numerical mismatches found among the traceable claims.** The reported values match the TSVs at the stated precision. The calibration examples cannot be linked to individual output rows, and several descriptions need qualification.

Work was read-only. I checked reported model coefficients against the model-output TSVs and recomputed their rescaling and rounding; I did not refit the regressions.

## MISMATCHES

None found.

In particular, all 12 calibration-table gaps match the specified rule: **displayed score minus displayed non-target median, 32.1**.

## UNTRACEABLE

The pair-level TSV contains document names and token intervals, but **no unit text or manuscript-example identifiers**. Consequently, these scores cannot be attributed to the quoted examples from the supplied files:

| `main.tex` line | Manuscript score |
|---:|---:|
| 449, repeated at 461 | 100.0 |
| 464 | 95.2 |
| 467 | 60.0 |
| 470 | 59.9 |
| 473 | 50.0 |
| 476 | 50.0 |
| 479 | 40.0 |
| 482 | 40.0 |
| 485 | 30.0 |
| 488 | 30.0 |
| 491 | 20.0 |
| 494 | 19.6 |

These are **12 example scores, appearing 13 times**. Their target/non-target assignments are likewise untraceable. Finding rows with matching rounded scores would not establish example identity.

The accompanying gaps are verified **conditionally on the displayed scores**. The non-target median itself is independently verified.

I excluded the human-audit numbers, including the eight antithesis cases at line 892, under your requested human-audit exclusion.

## VERIFIED

The following compact counts identify the principal checked numeric cells. Repeated prose statements were also checked against the same sources.

| Section | Checked and matched |
|---|---|
| Abstract and corpus description | All corpus counts, 4.2-point effect, and 0.28-SD approximation |
| Score-scale discussion and calibration | Four quantiles, SD, baseline median, repetition effect, effect-size ratios, and **12 gap cells** |
| Results | **56 relation-effects table cells**, all repeated estimates and intervals, and **10 genre-summary numbers** |
| Robustness discussion and appendix | **33 robustness-table cells**, all repeated estimates and intervals, and **4 weight-sensitivity range endpoints** |
| Validation body and appendix | **20 AUC-table cells**; both threshold slices’ counts, percentages, recovery rates, and enrichment |
| Extraction appendix | **9 count cells**, plus count identities |
| Permutation appendix | **21 table cells** |

That includes **151 matched numeric table cells**, counting calibration gaps but excluding untraceable calibration scores.

### Independently recomputed descriptive quantities

Source: `derived/gum_erst_adjacent_isocolon_scores.tsv`, using all rows unless otherwise specified.

| Claim and manuscript lines | Computed value | Reported value |
|---|---:|---:|
| Pairs, documents, genres: 33–34, 217 | 17,912; 301; 24 | Same |
| Collections: 235–236 | GUM 16,723; GENTLE 1,189 | Same |
| Composite median: 425 | 33.26 points | 33.3 |
| Composite quartiles: 425 | 22.63, 42.22 | 22.6, 42.2 |
| Composite 95th percentile: 425–426 | 56.109 | 56.1 |
| Composite sample SD: 510, 577 | 14.756866 | 14.8 |
| Non-target median: 450, 500 | 32.12 | 32.1 |
| Broad effect / empirical SD: 41, 510, 577 | 0.281810 | About 0.28 |
| Broad effect / repetition effect: 507–508 | 0.219480 | About a fifth |

The broad target distribution’s median is **39.555**, versus **32.12** for non-targets, supporting the described rightward shift.

### Model estimates and intervals

Sources and selection rules:

- `robustness_checks.tsv`, `check=document_clustered`: main estimates and document-clustered intervals; columns `estimate`, `cluster_ci_low`, `cluster_ci_high`.
- Same file, `check=length_with_mean_control`: mean-only isocolon estimates.
- Same file, `check=coordination_matched` and `target=joint_list_or_disjunction_vs_other_joint`: joint-only comparison.
- Same file, `check=adversative_matched` and `target=adversative_contrast_vs_other_adversative`: adversative-only comparison.
- Same file, `check=gum_only` or `continuous_spans_only`: corresponding subsets.
- Every reported effect and interval endpoint was multiplied by 100 and rounded to one decimal.

All eight rows at lines 654–661 match, including independently counted target and comparison sizes.

The clustered broad-family interval is **[3.565614, 4.751645] points**, correctly displayed as **[3.6, 4.8]**. The narrow-family interval is **[0.493356, 2.121400]**, correctly displayed as **[0.5, 2.1]**. Using the ordinary intervals in `observed_isocolon_effects.tsv` instead would give different endpoints.

The qualitative statements also match:

- Antithesis: **0.410148 points**, clustered interval **[−0.645610, 1.465905]** — near zero and crosses zero.
- Concession: **−1.383065 points**, clustered interval **[−2.038519, −0.727610]** — negative.
- Joint-disjunction exceeds joint-list: **4.718322 > 4.424827**.
- Parison supplies the largest broad-family full-control component effect: **7.700976**, versus lexical **2.601492** and length **0.757493**.
- Repetition’s lexical effect exceeds its parison effect: **32.874764 > 27.209897**.

### Genre and sensitivity checks

`genre_varying_summary.tsv`:

| Target | `n_genres` | `100 × eb_mu` | `100 × eb_tau` |
|---|---:|---:|---:|
| Broad | 20 | 3.921968 → 3.9 | 1.003085 → 1.0 |
| Joint-list | 17 | 4.054034 → 4.1 | 1.173722 → 1.2 |
| Narrow | 16 | 1.145488 → 1.1 | 0.903343 → 0.9 |
| Contrast | 4 | 2.902387 → 2.9 | 0.457299 → 0.5 |

The genre counts also match distinct genres in `genre_sensitivity_effects.tsv`.

`score_weight_sensitivity_summary.tsv`, rows `weight_family=grid`:

- Broad: **0.757493–7.700976 points**, displayed **0.8–7.7**; `share_positive=1`.
- Contrast: **0.095616–4.402636 points**, displayed **0.1–4.4**; `share_positive=1`.

The leave-one-genre claim at lines 714–715 is supported by `influence_checks.tsv`. Across the omitted-genre rows:

| Specification | Estimate range, points | Smallest clustered lower endpoint |
|---|---:|---:|
| Broad main | 3.993–4.301 | 3.401 |
| List/disjunction within joint | 1.562–2.112 | 0.516 |
| Contrast within adversative | 2.612–3.067 | 1.018 |
| Contrast parison within adversative | 5.094–5.921 | 2.329 |

All remain positive, with clustered intervals excluding zero.

### Validation

I recomputed AUCs, Hanley–McNeil intervals, and labelled/unlabelled means directly from the pair rows. All 20 cells at lines 1091–1094 match.

Threshold calculations, independently reconstructed using inclusive score cutoffs:

| Slice | Selected | Labelled | Hit rate | Recall | Enrichment |
|---|---:|---:|---:|---:|---:|
| 95th percentile | 896 | 27 | 3.013393% | 34.177215% | 6.832392× |
| 97.5th percentile | 448 | 24 | 5.357143% | 30.379747% | 12.146474× |

The corpus base rate is **79/17,912 = 0.441045%**. Thus **3.0%, about seven times, 0.4%, 34%, 5.4%, and 30%** all match their intended rounding.

### Extraction and permutation arithmetic

All extraction-table counts match `extraction_diagnostics.tsv`, column `value`. Available pair-level checks independently confirm adjacency count, document/genre counts, collection counts, explicit/implicit counts, discontinuity count, and zero duplicate `(doc, unit1_toks, unit2_toks)` keys.

The count identities hold:

```text
17,912 + 18,031 = 35,943
15,817 +  2,214 = 18,031
 5,077 + 12,835 = 17,912
```

All 21 permutation-table cells match `stratified_nulls.tsv`, rows selected by `target`, using:

```text
100 × observed_estimate
100 × null_mean
100 × null_q025, 100 × null_q975
movable_strata, movable_rows, movable_target_rows
```

Each observed effect exceeds its null interval’s upper endpoint.

## OTHER DESCRIPTION ISSUES

1. **AUC is described as strict winning probability.**  
   Lines 745–747 and 1098–1100 should include half credit for ties:

   ```text
   AUC = P(labelled score > unlabelled score)
         + ½ P(equal scores)
   ```

   This matters particularly for lexical echo:

   | Measure | AUC | Strict winning probability | Tie probability |
   |---|---:|---:|---:|
   | Composite | 0.715949 | 0.715872 | 0.000155 |
   | Parison | 0.740059 | 0.734550 | 0.011019 |
   | Lexical echo | 0.740749 | 0.656595 | 0.168307 |

   “Wins about 72 times in 100” remains a sound composite approximation, but the general definition is incomplete.

2. **The genre spread is a model parameter, not the observed spread of pooled estimates.**  
   Lines 640–643 accurately reproduce `eb_tau`. Describe these as **estimated between-genre standard deviations**. They are not the empirical SDs of the individual observed genre effects, which are respectively **1.826, 1.502, 1.862, and 2.048 points** for broad, joint-list, narrow, and contrast.

3. **The claimed bounds do not generally bound adjusted regression coefficients.**  
   Lines 667–668 say the adjusted differences have possible values from −100 to +100. That bound applies to raw differences between bounded scores or group means; an OLS coefficient adjusted for covariates is not necessarily confined to it. The reported coefficients themselves pose no problem.

4. **“Strongest” exceeds the supplied relation scan’s coverage.**  
   Lines 622–623 establish repetition as strongest among the eight targets in `robustness_checks.tsv`. The supplied outputs do not contain a fitted scan of every `orig_label`, so **“strongest among the relations tested”** is supported; an unrestricted corpus-wide ranking is unverified.

The “slightly higher” AUC statement is numerically supported, but should remain descriptive: the supplied outputs do not test differences between those correlated AUCs.

## Calculation code

These are the core non-obvious calculations used, condensed from the executed checks:

```python
import pandas as pd
import numpy as np
from scipy.stats import rankdata

p = pd.read_csv(
    "derived/gum_erst_adjacent_isocolon_scores.tsv", sep="\t"
)
r = pd.read_csv("derived/robustness_checks.tsv", sep="\t")

broad = p.orig_label.isin([
    "adversative-antithesis", "adversative-contrast",
    "joint-disjunction", "joint-list"
])

quantiles = 100 * p.isocolon_score.quantile([.25, .5, .75, .95])
sd_points = 100 * p.isocolon_score.std(ddof=1)
baseline_median = 100 * p.loc[~broad, "isocolon_score"].median()

main = r[
    (r.check == "document_clustered") &
    (r.outcome == "isocolon_score")
].set_index("target")

sd_ratio = main.loc["broad", "estimate"] / p.isocolon_score.std()
repetition_ratio = (
    main.loc["broad", "estimate"] /
    main.loc["restatement_repetition", "estimate"]
)

gold = p.has_gold_syn_prl.astype(bool).to_numpy()
n1, n0 = gold.sum(), (~gold).sum()

for column in [
    "isocolon_score", "length_score", "syntax_score", "lexical_score"
]:
    x = p[column].to_numpy()
    auc = (
        rankdata(x)[gold].sum() - n1 * (n1 + 1) / 2
    ) / (n1 * n0)

    q1 = auc / (2 - auc)
    q2 = 2 * auc**2 / (1 + auc)
    se = np.sqrt(
        (auc * (1 - auc)
         + (n1 - 1) * (q1 - auc**2)
         + (n0 - 1) * (q2 - auc**2)) / (n1 * n0)
    )
    interval = (auc - 1.96 * se, auc + 1.96 * se)

    negatives = np.sort(x[~gold])
    left = np.searchsorted(negatives, x[gold], side="left")
    right = np.searchsorted(negatives, x[gold], side="right")
    strict_win = left.sum() / (n1 * n0)
    ties = (right - left).sum() / (n1 * n0)

for percentile in [95, 97.5]:
    cutoff = p.isocolon_score.quantile(percentile / 100)
    selected = p.isocolon_score.to_numpy() >= cutoff
    hits = (selected & gold).sum()
    precision = hits / selected.sum()
    recall = hits / n1
    lift = precision / (n1 / len(p))
```

Table checks selected the appropriate target, outcome, and control specification, asserted one matching output row, and compared each manuscript cell with `round(100 × output_value, 1)`. Target counts were independently recomputed from `orig_label`; comparison counts were `17,912 − target_count`.
