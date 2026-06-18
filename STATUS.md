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

- Send Rency Luan a follow-up email with the GitHub link, the `outputs/audit/adversative_antithesis_full_classical_coding.tsv` worksheet, the `outputs/audit/adversative_antithesis_decomposition_codebook.md` codebook, and the RST/signalling papers now in the shared literature folder.
- Treat Rency's first contribution as rhetorical-theory and rubric work, not bulk coding: she wants to read antithesis/isocolon/parison theory first, especially Fahnestock, Harris, and other figure-theory sources, then help revise the coding categories.
- Use `rater_app/rst_signal_crosswalk.html` for the next `LDC2015T10` step: code the 19 aggregate signal labels into paper-facing roles, use levels, confidence, and follow-up flags, then ingest returned JSON with `make rst-signal-judgments`.
- Revise the 343-row `adversative-antithesis` coding rubric before full coding. The current categories are classical antithesis, semantic opposition, and parallel opposition, but the 2026-06-04 Rency call made clear that the rhetorical-theory pass should come first.
- Decide final venue posture with Rency's input: Language and Literature first, Rhetorica first, another rhetoric journal, or keep the paper as a rhetoric/stylistics crossover draft until external feedback.
- Next manuscript pass: decide whether the genre-varying summary needs a table or figure, or whether the prose summary is enough.
- Decide whether to seek additional human coders. Rency may contact Cathal in Ireland, who she described as strong on rhetorical figures, isocolon, and parison, and Zoya, who works on construction grammar and figures. Confirm roles before recording them as collaborators.
- Add any RST Signalling Corpus comparison only after the aggregate signal-label crosswalk has been human-coded. Until then, keep RST-SC as annotation context rather than manuscript evidence.

## Design Guardrails

- Unit of analysis: adjacent clause pair or colon pair.
- Target relation: comparison.
- Matched non-target relations: contrast, cause, condition, sequence, elaboration.
- Core controls: text, author or speaker where known, genre, period, clause length, connective type, syntactic frame, and general parallelism.
- Main inference: textual evidence for rhetorical function, not psychological effect.

## Session Notes

### 2026-06-18

- Added an offline RST-SC signal-crosswalk interface modeled on the diagnostic-validity rater app. `scripts/build_rst_signal_judgment_app.py` reads only aggregate TSVs and writes `rater_app/rst_signal_crosswalk.html` plus `rater_app/rst_signal_crosswalk_items.tsv`; the app asks human coders to map 19 aggregate slot-4 labels to paper-facing roles, use levels, confidence, and follow-up flags. Downloaded JSON responses go in ignored `rater_app/responses/` and can be merged locally with `scripts/ingest_rst_signal_judgments.py`.

### 2026-06-17

- Shipped `5d9fa4a` with the aggregate RST-SC summary and offline signal-crosswalk app, then shipped `df57928` updating the manuscript and rebuilt PDF so RST-SC is described as locally available under restricted license but outside the reported quantitative results until human label-crosswalk judgment is complete.
- Recorded the U of T LDC General License as a project policy: UofT-only access, non-commercial research/education use, citation/acknowledgment required, and no external distribution, web posting, third-party platform ingestion, AI-chatbot ingestion, commercial use, or internship/co-op/professional-context use.
- Created and reviewed `.agent/ldc-enforcement-plan.md` in Roughdraft, then implemented enforcement: `DATA_POLICY.md`, `scripts/check_restricted_data.py`, `.githooks/pre-commit`, `make policy-check`, `make install-hooks`, `.gitignore` quarantine paths, and synchronized restricted-data instructions in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`.
- Installed the local pre-commit hook. Verification passed: `python3 -m py_compile scripts/check_restricted_data.py`, `make policy-check`, staged-file scan, installed hook run, and a synthetic LDC-marker probe that the scanner blocked and then removed.
- Initially confirmed `LDC2015T10` was not visible in the SharePoint folder despite Nick Field's email; Brett then obtained `/Users/brettreynolds/Downloads/RST_Signalling_Corpus_LDC2015T10.tgz`.
- Moved and extracted `RST_Signalling_Corpus_LDC2015T10.tgz` to `/Users/brettreynolds/RestrictedCorpora/LDC/LDC2015T10/` with private permissions. Inspected only the archive path, size, and top-level directory names; no corpus text was printed or sent to an AI tool.
- Inspected only filenames, sizes, and archive top-level names from the earlier downloaded OneDrive folders. Moved the potentially relevant English-side set (`LDC99T42`, `LDC2015T08`, and the WSJ mapping archive) out of Downloads to `/Users/brettreynolds/RestrictedCorpora/LDC/OneDrive_1_2026-06-17` with private permissions. Left the Chinese Treebank downloads in `Downloads/OneDrive_2_2026-06-17` because they are probably not relevant unless the project deliberately adds a Mandarin comparison.
- Added `scripts/inspect_rst_signalling.py`, a schema-tolerant aggregate inventory script for `LDC2015T10`. It resolves `RST_SC_ROOT`, `LDC_ROOT`, or ignored `.ldc-root`, reads local XML annotations, and writes only aggregate counts: manifest, file inventory, XML tag/attribute counts, feature-vector lengths, feature-slot label counts, schema counts, and candidate formal-signal summaries.
- Ran the RST-SC inventory locally. Outputs are ignored under `data/derived/` and include no raw text or row-level records. The full annotation split has 385 text files and 772 XML files; the train/test splits have 347/38 text files and 696/78 XML files. Candidate aggregate labels include syntactic-family signals and `parallel_syntactic_constructions`, but these are only candidates for human/Rency interpretation.
- Decided not to use a local LLM for this stage. A local model would avoid some third-party-ingestion problems only if fully offline and non-logging, but deterministic Python plus human judgment is enough for the current work.
- Added `scripts/summarize_rst_signalling.py`, which reads only aggregate RST-SC inventory TSVs and writes aggregate summary TSVs plus `notes/rst-signalling-aggregate-summary.md`. The full split summary gives 29,300 annotation-feature vectors; candidate bridge memberships are lexical echo 9,588 (34.58% of slot-4 labels), parison-like syntactic parallelism 558 (2.01%), comparison reference 183 (0.66%), and semantic opposition 37 (0.13%). Counts are non-disjoint label memberships, not automatic isocolon judgments.
- Cross-checked the DiD methods-paper guardrails for relevance. Apply them here only as methodological hygiene: name the target quantity, separate linguistic/measurement/aggregation units, assign each textual feature one job, treat composition and measurement as possible artifacts, and pre-specify what would downgrade a claim. Do not import DiD's causal shock/counterfactual machinery.
- Added an ignored local `.ldc-root` pointer to `/Users/brettreynolds/RestrictedCorpora/LDC`; no restricted LDC data or symlink was moved into the project repo.

### 2026-06-04

- Brett met with Rency Luan from 08:59 to 09:18 about the isocolon paper. Rency said the project looks interesting and that there is "lots of room for rhetorical interpretation."
- Rency's proposed first move is to read the rhetorical-theory literature on antithesis, isocolon, and parison, including Harris and Fahnestock, before settling the coding categories. This supports treating the next step as rubric refinement rather than immediate full-batch coding.
- Brett clarified that the planned "coding" means row-level rhetorical judgment rather than programming. Rency is open to LLM use but hasn't previously used LLMs much and isn't a programmer. She has prior corpus experience with AntConc, DocuScope, and COCA.
- Rency is checking with Waterloo administrators about access to the RST Signalling Corpus (`LDC2015T10`); Waterloo apparently doesn't currently have LDC membership set up. Brett is still waiting on the U of T library route.
- Rency may invite two additional people: Cathal in Ireland, described as strong on rhetorical figures, isocolon, and parison, and Zoya, who works on construction grammar and figures. Rency will contact them directly and cc Brett if appropriate.
- Timeline is flexible. Rency's dissertation is her summer priority, with this project as a secondary summer project and potentially more active in the fall. She also offered to scope possible rhetoric venues.
- Added two missing RST/signalling PDFs to the shared literature folder: `das_2019_nuclearity_rst_signals_coherence_relations.pdf` and `zeldes_liu_2020_neural_discourse_relation_signal_detection.pdf`. The folder already contained Das and Taboada 2019, Liu 2019, Taboada and Das 2013, and the two core Das and Taboada 2018 signalling papers.

### 2026-06-01

- Brett sent Rency Luan a follow-up collaboration email after meeting her at Rhetoricon on 2026-05-29. The invitation frames the project as statistically far along but rhetorically open, with a possible collaboration focused on the antithesis distinction, the ~343 `adversative-antithesis` cases, and the figure-theory and interpretation sections.
- Added a durable PM people page for Rency at `Project-Management/people/luan.md`, including contact, open thread, possible collaboration scope, and tone/context notes.
- Rency replied positively the same morning. She said the project sounds intriguing, called `adversative-antithesis` curious, and asked to read a draft before a call.
- Brett sent the draft, noted that self-deprecating footnotes would obviously be removed if she joined as co-author, asked whether she has access to the RST Signalling Corpus (`LDC2015T10`), and said he is free basically all day Thursday 2026-06-04.

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
