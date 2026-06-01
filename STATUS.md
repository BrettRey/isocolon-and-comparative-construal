# STATUS

## Project

Isocolon and comparative construal: A corpus test of rhetorical balance.

## Stage

Full manuscript draft built and ready for human review. Public GitHub repo requested at setup.

## Trigger

Brett attended Rhetoricon at the University of Waterloo on 2026-05-29. Gini Fahnestock proposed that isocolon makes comparison more salient, pointed, explicit, or forceful. After the talk, Brett asked whether quantitative work had tested the idea. The answer seemed to be no.

## Working Claim

The project should test a production-side textual-function claim, not a reader-side causal claim:

> Formal balance is preferentially associated with comparable-set construals in production; the analysis must report isocolonic length balance and parison-like syntactic parallelism separately.

## Immediate Next Actions

- Wait for library/LDC access to the RST Signalling Corpus data (`LDC2015T10`); all other high-priority library articles/books have been copied into the shared literature folder.
- Code `outputs/audit/adversative_antithesis_full_classical_coding.tsv` for classical antithesis, semantic opposition, and parallel opposition; then run `scripts/fit_antithesis_decomposition.py` to test whether hand-marked classical antitheses show elevated parison.
- Decide final venue posture: Language and Literature first, Rhetorica first, or keep the paper as a rhetoric/stylistics crossover draft until external feedback.
- Next manuscript pass: decide whether the genre-varying summary needs a table or figure, or whether the prose summary is enough.
- Decide whether to seek a second blind human coder. The manuscript now treats the 80-row audit as single-author, non-blind qualitative validation rather than interrater reliability evidence.
- Add the RST Signalling Corpus data comparison when library/LDC access comes through.

## Design Guardrails

- Unit of analysis: adjacent clause pair or colon pair.
- Target relation: comparison.
- Matched non-target relations: contrast, cause, condition, sequence, elaboration.
- Core controls: text, author or speaker where known, genre, period, clause length, connective type, syntactic frame, and general parallelism.
- Main inference: textual evidence for rhetorical function, not psychological effect.

## Session Notes

### 2026-05-30

- Scaffolded the project from the house-style LaTeX template.
- Added buildable seed manuscript with the corpus-distributional claim separated from the reader-response claim.
- Added notes, data, scripts, and output scaffolding.
- Added verified Fahnestock bibliography anchors.
- Added CC BY 4.0 license.
- Built the initial GUM/eRST analysis pipeline, fake-data simulation, scoring sensitivity checks, and qualitative audit batches.
- Completed primary human validation for the first 80 audit rows and targeted adjudication for batch 3 disagreement rows.
- Added 17 open PDFs to the shared literature folder under `literature/isocolon-rhetoric/`.
- Added verified bibliography entries for rhetorical-figure theory, computational figure detection, RST/eRST, RST-SC, PDTB, and advertising-rhetoric precedents.
- Wrote `notes/literature-acquisition.md`, `notes/library-request-list.md`, and `notes/literature-working-map.md`.
- Ingested Brett's library downloads for Fahnestock 1999, Fahnestock 2011, Fahnestock 2004 "Preserving the Figure," Harris & Di Marco 2017, Harris et al. 2018, and the two Das & Taboada 2018 signalling articles.
- Folded the literature frame and current empirical results into `main.tex`: form-function figure theory, false-positive/ranking problem, GUM/eRST corpus basis, validation, preliminary effects, and restrained interpretation.
- Added compact validation and relation-effect tables to `main.tex`, backed by the derived TSVs.
- Added the exact isocolonicity scoring formula and adjusted-effect model specification to `main.tex`.
- Reframed the manuscript to report formal balance, isocolonic length balance, parison-like syntactic parallelism, and lexical echo separately; updated the title, abstract, methods, results table, interpretation, and conclusion.
- Added document-clustered robustness checks, a no-length-controls length-balance model, joint-only and adversative-only matched comparisons, and a regenerated robustness script.
- Added a qualitative-audit summary table, illustrative audit examples, a data/code availability section, and a verified ACL proceedings citation for Kühn and Mitrović's FigLang challenge paper.
- Revised the length-balance analysis after reviewer feedback: the isocolon component now uses mean-length control without maximum-length control, AUC validation reports approximate intervals, score-weight sensitivity is summarized, and a full 343-row adversative-antithesis decomposition worksheet plus analysis runner have been generated.
- Added data-audit robustness checks: GUM-only, continuous-spans-only, leave-one-genre influence checks, permutation movable-row counts, and explicit English-only language scope. Main patterns remain stable.
- Rebuilt `main.pdf` with `make` using XeLaTeX/Biber. Citations resolve; no overfull boxes remain. The only remaining LaTeX warnings are standing preamble warnings from `fancyhdr` and `microtype`.

### 2026-05-31 (evening easification pass)

Easification pass on `main.tex` for a Language and Literature (stylistics, non-statistical) audience. Constraints from Brett: "easify, not shorten" and "no punchy/aphoristic writing." All statistics unchanged; build clean (XeLaTeX + Biber, 0 undefined refs).

- Split "Corpus and measurement" into four subsections; added a worked balance-formula example (8 vs 10 words = 0.8) and inline glosses for edit similarity, Jaccard, lemma, content words, and flat-sequence-vs-parse-tree.
- Validation: AUC explained via the draw-two-pairs picture; precision/recall/lift walked through one shared top-5% slice with a worked example each.
- Added a plain-language Length-vs-Isocolon paragraph at the relation-effects table (why two columns both say "length").
- Robustness: each check reframed as "one explanation removed"; the permutation test rewritten as a step-by-step walkthrough.
- Whole-paper sweep for pseudo-glossing (jargon defined by jargon, house-style filler verbs). Fixed: empirical-Bayes "borrow strength", the inert between-genre SD, the 0.28-SD anchor, logged/standardized length terms, and `captures`/`reflects` filler verbs. Replaced the circular "4.1 points = about four points higher" with a 19-point repetition-control yardstick.
- Removed the `\clearpage` before Conclusion so it flows after Interpretation; left the appendix and acknowledgements clearpages in place.

The pass left several open judgment calls, most importantly final venue posture and whether the genre-varying summary needs a table/figure. These are now tracked under Immediate Next Actions rather than as shipping blockers.

### 2026-05-31 late-stage editorial pass

- Applied the late-stage editorial/reviewer pass to `main.tex` for a rhetoric/stylistics crossover reader while leaving the final venue choice open against the earlier Language and Literature target.
- Removed the pending RST Signalling Corpus note from the abstract; it remains in the body/data statement as later triangulation.
- Clarified Table 2 unit boundaries with `\(\parallel\)`, moved qualitative-audit illustrations into displayed examples, and cut the extra antithesis humour footnote.
- Verified local eRST `syn-prl` signals in the raw `.rs4` files and revised the validation wording: `syn-prl` is treated as a proxy for relation-level syntactic parallelism, not an exact cross-unit alignment test.
- Added a discontinuous-span length note: length counts assigned unit tokens, not full interval width.
- Reframed the 343-row adversative-antithesis decomposition as targeted follow-up rather than an unreported current result.
- Added clean page breaks/running heads for Conclusion, Acknowledgements, and appendices.
- Added the validation-enrichment figure and updated the figure-generation script so manuscript figures can be regenerated.
- House-style check passes. `make` builds `main.pdf` cleanly at 24 pages; the only remaining log warning is the standing microtype footnote patch warning.

### 2026-05-31 ship tidy

- Tidied `main.tex`: split two overlong paragraphs, smoothed the conclusion robustness paragraph, and made the AI acknowledgement generic to avoid stale model-version names.
- Re-ran the house-style linter and full XeLaTeX/Biber build; no style violations, undefined references, citation warnings, or overfull boxes remain.
