# Literature working map

Updated: 2026-05-30

This is a working map, not a finished literature review. Claims below are grounded in the locally acquired PDFs or verified metadata where noted.

## Core thesis emerging from the literature

The project has a defensible gap: rhetorical theory treats figures as form-function pairings, and computational work shows that purely formal repetition/parallelism creates many false positives. What seems missing is a corpus-distributional test of whether one formal figure, isocolon, is preferentially associated with a rhetorical/discourse function: comparative construal.

That framing fits the current study better than a reader-response causal claim. The empirical question is production-side: where do writers/speakers actually use balanced cola, controlling for general parallel syntax and discourse relation type?

## Landscape map

| Source | Core claim or contribution | Method/material | Role in this project | Confidence |
|---|---|---|---|---|
| Fahnestock 2004, "Figures of Argument" | Parallel phrasing can express lines of reasoning iconically; antithesis is treated as both phrasing and reasoning in scientific argument. | Rhetorical analysis of historical scientific arguments. | Theoretical anchor for figures as argumentative/function-bearing forms. | From paper abstract/introduction |
| Fahnestock 1999/2011 | Figures are central to scientific/rhetorical persuasion, not merely decorative. | Books; now available locally as Oxford chapter/part PDFs. | Main theoretical frame for the paper. | Local PDFs acquired; still needs close reading |
| Harris & Di Marco 2017 | Rhetorical figures, argument, and computation can be connected as a research program. | Argument & Computation article. | Contemporary computational-rhetoric frame. | Local PDF acquired; still needs close reading |
| Harris et al. 2018 | Provides an annotation scheme for rhetorical figures. | Annotation-focused paper. | Directly relevant to our codebook and inter-rater disagreement. | Local PDF acquired; still needs close reading |
| Lawrence, Visser & Reed 2017 | Some automatically identifiable figures correspond to argument-dense passages; rhetorical figure mining can test rhetorical claims empirically. | Pilot study on 39,694 words of BBC Moral Maze transcripts annotated for argument structure. | Supports our empirical strategy: detect candidate figures, then evaluate rhetorical/discourse function. | From paper abstract/introduction |
| Mitrovic et al. 2017 | Figures have argumentative roles; ontological/knowledge-based models may help argument mining. | Survey/modeling paper on rhetorical-figure ontologies, RST, and argument mining. | Useful bridge between rhetorical figures, RST relations, and computational annotation. | From paper abstract/introduction |
| Dubremetz & Nivre 2018 | Detecting repetition is easy; detecting repetitions that have rhetorical effect is hard because accidental/irrelevant repetitions are common. | Log-linear classifiers for chiasmus, epanaphora, and epiphora in political debate, then cross-genre application. | Closest methodological precedent for our false-positive controls and qualitative audit. | From paper abstract/introduction |
| Kuehn, Mitrovic & Granitzer 2024 | Computational figure detection faces dataset scarcity, language limitations, inconsistent definitions, and heavy reliance on rule-based methods. | Systematic survey of lesser-known rhetorical-figure detection. | Positions our work as contributing a corpus/test design for a relatively under-tested figure. | From paper abstract/introduction |
| Taboada & Das 2013 | Many rhetorical/coherence relations have signals beyond discourse markers; adding signalling annotations to existing RST relations is useful for discourse parsing. | RST Discourse Treebank re-annotation with signal information. | Supports relation signals as observables and motivates using eRST/RST-SC. | From paper abstract/introduction |
| Das & Taboada 2018/2019 | Coherence relations can be signalled by multiple cue types, not just discourse markers; signals can co-occur. | Corpus studies using RST Signalling Corpus. | Supports treating isocolon as one possible signal among others, not a standalone relation label. | Local PDFs acquired; 2019 skimmed, 2018 needs close reading |
| Zeldes et al. 2025 | eRST extends RST with non-tree structures, multiple/concurrent relations, and explicit/implicit relation signals; releases 200K+ tokens across 12 English genres. | Corpus/framework paper and tools. | Main corpus justification: current, open, multi-genre, signal-rich. | From paper abstract/introduction |
| Carlson, Marcu & Okurowski 2001 / LDC2002T07 | Builds the RST Discourse Treebank as a discourse-annotated resource. | RST annotation of Wall Street Journal text. | Historical corpus background and possible comparison if RST-SC arrives. | From paper/introduction and LDC record |
| McQuarrie & Mick 1996; Leigh 1994 | Empirical work on rhetorical figures in advertising. | Advertising language/headline studies; PDFs not local. | Useful if we want precedent for corpus-like counts of rhetorical figures in persuasive text. | Verified metadata; needs PDFs |

## Clusters by shared assumption

### Figure-as-function

Fahnestock, Harris/Di Marco, Lawrence/Visser/Reed, and Mitrovic et al. share the assumption that figures can be analyzed as couplings of formal arrangement and rhetorical/argumentative function. This is the natural home for the paper's claim.

### Formal-detection-is-not-enough

Dubremetz & Nivre and Kuehn et al. share the assumption that candidate extraction is cheap relative to rhetorical validation. This cluster backs our codebook distinction between formal parallelism and isocolonic rhetorical function.

### Relation-signalling

Taboada/Das and Zeldes/eRST share the assumption that discourse relations are often locally signalled, but by a wider set of cues than discourse markers alone. This lets us frame isocolon as a candidate signal or correlate of comparative construal.

### Corpus infrastructure

GUM/eRST, RST-DT/RST-SC, and PDTB provide relation-annotated corpora with different theoretical commitments. eRST is the current best base for us because it is open, multi-genre, and signal-aware.

### Applied empirical figure studies

McQuarrie/Mick and Leigh seem to provide prior empirical work on rhetorical figures in advertising. Their main value will probably be precedent, not direct methodology.

## Productive tensions

### Formal pattern vs rhetorical figure

Computational detection papers show that a formal pattern can be common while the figure is rare. This is not a contradiction of Fahnestock; it is the methodological burden implied by her view. If figures are form-function pairings, then form alone will overgenerate.

Paper use: justify the qualitative audit, false-positive flags, and agent/human disagreement analysis.

### Discourse marker vs broader signal

Older discourse parsing work often privileges discourse markers/connectives. Taboada/Das and eRST broaden the signal inventory. Our study can sit in that broader space by testing whether balanced cola behave like a discourse-functional cue in comparison contexts.

Paper use: avoid claiming isocolon "marks" comparison categorically. Say it may be preferentially associated with comparative construal or may serve as one cue among several.

### RST-SC vs eRST/GUM

RST-SC is valuable because it is explicitly about signals, but it is based on older WSJ RST-DT data and licensed through LDC. eRST/GUM is broader and available now, but not identical to RST-SC.

Paper use: eRST is sufficient for the main test; RST-SC is a robustness/comparison resource if acquired.

## Likely paper paragraph skeleton

First, rhetorical figures have long been treated as more than ornamental form. Fahnestock's work is the anchor: in scientific argument, parallel and antithetical forms can make lines of reasoning perceptible as form. Harris and colleagues extend this view into computational rhetoric and annotation.

Second, computational work on rhetorical figures shows why formal detection must be handled carefully. Dubremetz and Nivre's work on repetitive figures makes the key point: repetition is easy to find, but rhetorically consequential repetition is not. This justifies separating general parallelism, exact repetition, and isocolon in our coding.

Third, discourse-relation work gives the corpus basis. Taboada and Das show that coherence relations are signalled by more than discourse markers, and eRST gives an open, multi-genre corpus in which relation structure and signals are represented. That makes it possible to test whether isocolon is preferentially distributed with comparison-like construals.

## Manuscript integration status

This frame has now been folded into `main.tex` as a first paper-facing draft. The current manuscript uses four linked moves: figures as form-function pairings; formal figure detection as an overgenerating ranking problem; GUM/eRST as the corpus basis; and the current empirical result as evidence for a restricted textual-function claim. The draft deliberately treats RST-SC as a robustness/comparison resource rather than as a prerequisite for the main eRST/GUM test.

Compact tables for score validation and selected relation effects are now in the manuscript, along with the exact scoring formula and adjusted-effect model specification. The results now separate composite formal balance, isocolonic length balance, parison-like syntactic parallelism, and lexical echo. Review-response passes added audit examples, an audit summary, document-clustered uncertainty, mean-only length-balance estimates, score-weight sensitivity, and matched joint-only/adversative-only comparisons. The next empirical pass should code the adversative-antithesis decomposition worksheet, then decide whether the genre-varying summary needs a table or can stay in prose.

## What not to claim yet

- Don't claim that isocolon causes readers to perceive comparison. We have not tested readers.
- Don't claim isocolon is a discourse marker. Better: candidate signal, cue, correlate, or form-function construction.
- Don't claim RST-SC is necessary for publishability. It is useful, but eRST/GUM plus qualitative validation is already a plausible basis.
- Don't claim all formal parallelism is rhetorical. The qualitative audit exists because it isn't.
- Don't overstate the advertising literature until McQuarrie/Mick and Leigh are read.

## Next reading tasks

1. Read Fahnestock 2004 "Figures of Argument" closely; extract the paragraphs on parallel phrasing, antithesis, and pattern completion.
2. Read Dubremetz & Nivre 2018 methods and error analysis; extract how they operationalize false positives and borderline cases.
3. Read Zeldes et al. 2025 sections on signals and corpus coverage; extract the exact corpus description for the methods section.
4. Read Taboada & Das 2013 and Das & Taboada 2019 for signal categories that might overlap with balanced cola.
5. Read Harris & Di Marco 2017 and Harris et al. 2018 for the computational-rhetoric frame and annotation scheme.
6. When RST-SC data arrives, inspect the data layout and decide whether to run a WSJ comparison or use it only as a methodological reference.
