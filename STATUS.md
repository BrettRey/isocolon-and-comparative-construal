# STATUS

## Project

Isocolon and comparative construal: A corpus test of rhetorical balance.

## Stage

Seed project scaffolded on 2026-05-30. Public GitHub repo requested at setup.

## Trigger

Brett attended Rhetoricon at the University of Waterloo on 2026-05-29. Gini Fahnestock proposed that isocolon makes comparison more salient, pointed, explicit, or forceful. After the talk, Brett asked whether quantitative work had tested the idea. The answer seemed to be no.

## Working Claim

The project should test a production-side textual-function claim, not a reader-side causal claim:

> Formal balance is preferentially associated with comparable-set construals in production; the analysis must report isocolonic length balance and parison-like syntactic parallelism separately.

## Immediate Next Actions

- Wait for library/LDC access to the RST Signalling Corpus data (`LDC2015T10`); all other high-priority library articles/books have been copied into the shared literature folder.
- Code `outputs/audit/adversative_antithesis_full_classical_coding.tsv` for classical antithesis, semantic opposition, and parallel opposition; then run `scripts/fit_antithesis_decomposition.py` to test whether hand-marked classical antitheses show elevated parison.
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
