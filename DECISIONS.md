# DECISIONS

2026-05-30 -- Project scaffolded as a short corpus-based rhetoric paper. Reason: the Rhetoricon exchange produced a testable production-side claim that does not require a reader experiment.

2026-05-30 -- Working title: "Isocolon and comparative construal: A corpus test of rhetorical balance." Reason: it names the figure, the target rhetorical relation, and the empirical method without overclaiming reader-side effect.

2026-05-30 -- Use CC BY 4.0 as the repository license. Reason: the primary outputs are scholarly prose, notes, and documentation rather than software.

2026-05-30 -- Do not claim a psychological effect from corpus evidence alone. Reason: corpus evidence can support preferential association and production-side rhetorical selection, but not reader-side causation.

2026-05-30 -- Start with verified Fahnestock bibliography anchors only. Reason: the seed manuscript should cite the talk's theoretical background without pretending the literature review is complete.

2026-05-30 -- Use four agents for each remaining validation/audit batch: two Codex and two Opus. Reason: four is the smallest balanced replicated panel for this design. It gives two draws from each model family, allows within-family and cross-family agreement checks, preserves informative 2--2 ties as item-difficulty signals, and supports measurement-error summaries without treating agent majority vote as ground truth.

2026-05-30 -- Pause full-batch human coding after the first 80 human-coded rows, but allow targeted human adjudication of agent-disagreement rows. Reason: the current 80-row human-coded set is enough for a pilot validation section; additional human effort should focus on boundary cases where the four-agent panel splits or marks uncertainty.

2026-05-30 -- Report composite formal balance, isocolonic length balance, parison-like syntactic parallelism, and lexical echo separately. Reason: the headline effect is mostly syntactic; separating the components prevents the paper from labelling a parison-led result as isocolon narrowly understood.

2026-05-30 -- Treat coordination as a central alternative explanation rather than a footnote. Reason: joint-list and joint-disjunction effects shrink under a joint-only comparison, while adversative-contrast remains positive within the adversative family; the defensible claim is that comparable-set relations attract formal balance, with much of the broad effect carried by coordination-compatible parison.

2026-05-30 -- Use a Rapoport-style charitable frame throughout the manuscript. Reason: rare isocolon is compatible with figures being selective resources and with ordinary writers missing rhetorically useful opportunities; the paper should report a distributional baseline, not imply that low frequency refutes rhetorical theory or pedagogy. The introduction, theory section, results, interpretation, and conclusion should state the strongest rhetorician-friendly reading before narrowing the corpus inference.

2026-05-30 -- Estimate the isocolon length-balance component with mean-length control but without maximum-length control. Reason: mean and maximum length nearly determine the token length-balance formula, so including both controls mechanically suppresses the length-balance outcome. Composite, parison, and lexical models can retain the full structural control set.

2026-05-30 -- Treat the current antithesis result as label-mismatch evidence, not a final semantic-antithesis test. Reason: the 80-row audit has only eight `adversative-antithesis` rows and no classical-antithesis field; a targeted hand-coded decomposition is needed to separate eRST label mismatch from a surface-measure blind spot for semantic opposition.

2026-05-30 -- Run the antithesis decomposition only after coding the full 343-row `adversative-antithesis` worksheet. Reason: the eight audited rows are useful examples but too sparse for the reviewer-critical subset test; the decisive contrast is whether hand-marked classical antitheses inside the full eRST label set show elevated parison.

2026-05-30 -- State the language scope explicitly as English-only. Reason: the corpus evidence comes from English GUM/eRST and GENTLE rows, and does not license claims about how isocolon, parison, prosody, segmentation, or rhetorical training behave in Ancient Greek, Modern Japanese, or other languages.

2026-05-30 -- Target venue: Language and Literature (SAGE) first. Reason: it covers corpus and computational stylistics of literary and non-literary language, which matches the paper's rhetorical-figure-plus-corpus shape.

2026-05-30 -- Easify the four densest spots for a stylistics (non-statistical) audience. Reason: the prose was carrying too much statistical load per sentence for Language and Literature readers. Split Corpus and measurement into four subsections; added a worked balance-formula example and inline glosses for edit similarity, Jaccard, AUC, and precision/recall/lift (one worked example per metric); added a plain-language Length-vs-Isocolon paragraph at Table 6; reframed each robustness check as "one explanation removed." Easify not shorten (877 to 952 lines), no aphoristic phrasing, all statistics unchanged.

2026-05-31 -- Write methods and results for a Language and Literature reader who knows stylistics but may not know discourse annotation or regression diagnostics. Reason: the target journal invites corpus/computational stylistics, but readers should not need background in eRST, DISRPT exports, fixed effects, clustered intervals, or permutation nulls. Added local glosses for discourse-relation pairs, GENTLE, explicit/implicit relations, adjacency exclusions, target-label prefixes, document controls, positive/negative adjusted differences, null distributions, and annotation-layer limitations.

2026-05-31 -- Anchor the 4.1-point headline effect against the 19-point restatement-repetition control rather than against the 0--100 scale, and call it "small but steady." Reason: an earlier gloss explained 4.1 by restating it ("about four points higher") and by noting it is 4% of 100, neither of which tells a reader whether the effect is large; the repetition control gives a concrete in-paper yardstick (the comparison families shift the score about a fifth as far as verbatim repetition does), and the size verdict is consistent with "modest but stable" already in Results. Open question flagged to Brett: whether the size judgment belongs in methods or only in Results.

2026-05-31 -- Ban pseudo-glossing throughout: no defining jargon with jargon and no house-style filler verbs (captures, reflects, underlies) standing in for a mechanism. Reason: the easification pass introduced several glosses that produced "explanatory sound" without explaining (empirical-Bayes "borrow strength", "a regression method for average differences", "not a tree-alignment measure"); each was rewritten to say what the operation does in the reader's own vocabulary.

2026-05-31 -- Treat the late-stage editorial pass as a rhetoric/stylistics crossover calibration, while leaving the venue choice open against the earlier Language and Literature target. Reason: the current paper leans toward rhetoric history/theory with corpus evidence, so it needs enough methodological scaffolding for rhetoricians without expanding every computational detail as if for a general audience.

2026-05-31 -- Keep the pending RST Signalling Corpus out of the abstract and frame it only as later triangulation. Reason: mentioning unavailable corpus data in the abstract makes the paper sound unfinished; the current GUM/eRST analysis stands on its own.

2026-05-31 -- Treat eRST `syn-prl` validation as a proxy for relation-level syntactic parallelism, not an exact cross-unit validation. Reason: local eRST signal spans are relation-level `parallel_syntactic_construction` annotations, but their token ranges can cover both linked units, one span, or several spans.

2026-05-31 -- Use displayed examples rather than a cramped table for the qualitative audit illustrations. Reason: the paper is about paired formal structure, so readers need to see the two units as paired units rather than compressed table text.

2026-05-31 -- Stop adding rhetorical jokes and keep only the earned, argument-bearing figure deployment. Reason: the prose now has enough self-aware figural play; adding more would distract from the empirical limitation around antithesis.

2026-05-31 -- Use a generic AI-assistance acknowledgement rather than listing model-version names. Reason: model names go stale quickly, and the acknowledgement only needs to disclose assistance plus author responsibility unless a journal asks for exact tool/version metadata.

2026-06-01 -- Send Rency Luan the full draft before the exploratory call. Reason: Rency replied that the project sounds intriguing and asked to read the draft before meeting, so the collaboration track has moved from initial invitation to informed discussion. Brett explicitly flagged that self-deprecating footnotes should be removed if she joins as co-author, asked about possible RST Signalling Corpus (`LDC2015T10`) access, and offered Thursday 2026-06-04 for a call.

2026-06-04 -- Make rhetorical-theory and rubric refinement the first Rency collaboration step, before bulk coding the 343 `adversative-antithesis` rows. Reason: in the exploratory call, Rency's strongest recommendation was to read the antithesis/isocolon/parison theory first, especially Harris, Fahnestock, and other figure-theory sources, then use that literature to revise the coding categories. This keeps the empirical coding from prematurely freezing Brett's provisional categories.

2026-06-04 -- Treat additional human coders/collaborators as possible but not yet committed. Reason: Rency may contact Cathal in Ireland, who she described as strong on rhetorical figures, isocolon, and parison, and Zoya, who works on construction grammar and figures. Their roles should remain open until they express interest and scope is clear.

2026-06-17 -- Treat LDC corpus data as protected out-of-band material and enforce that boundary with repo policy, ignored quarantine paths, a restricted-data scanner, and a pre-commit hook. Reason: the U of T LDC General License permits non-commercial research/education use but prohibits distribution, web posting, third-party platform ingestion, and AI-chatbot ingestion of the data.

2026-06-17 -- Keep `LDC2015T10` as the target LDC corpus for RST Signalling work; do not substitute nearby SharePoint items merely because they are visible. Reason: `LDC2015T10` is the RST Signalling Corpus requested for this project, while the currently downloaded `LDC99T42`/`LDC2015T08` materials are only protected provisional resources and `LDC2005T01` is Chinese Treebank material outside the current English RST path.

2026-06-17 -- Use deterministic local Python aggregation, not LLM judgment, for the first RST Signalling Corpus pass. Reason: the LDC license forbids third-party/AI-chatbot ingestion of the data, and the immediate need is mechanical inventory and aggregate signal counts; any interpretive mapping from signal labels to isocolon, parison, or antithesis categories should remain a Brett/Rency/human judgment.

2026-06-17 -- Import DiD-paper guardrails as methodological hygiene for the RST Signalling Corpus work, but not DiD machinery. Reason: this paper is not making a shock/counterfactual causal claim, but it still needs the same discipline about target quantity, measurement unit, aggregation unit, feature roles, composition/measurement artifacts, and pre-specified downgrade rules.

2026-06-18 -- Use an offline human judgment interface for the RST-SC label crosswalk. Reason: the interpretive step is deciding what aggregate signal labels can do for the paper, not asking an LLM to judge restricted corpus content. A static local app can collect Brett/Rency judgments over aggregate label names and counts while keeping raw LDC material out of the repo and out of AI tools.
