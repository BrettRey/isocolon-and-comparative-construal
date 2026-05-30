# Qualitative Audit

## Purpose

The quantitative score finds formal similarity, but the paper needs to know
whether high-scoring pairs are actually rhetorical isocolon or mainly artifacts
such as repetition, dialogue formulas, list formatting, and bad segmentation.

The first qualitative audit uses 40 sampled rows.

Command:

```bash
scripts/sample_qualitative_audit.py
```

Sample and coding materials:

- `outputs/audit/isocolon_qualitative_audit_40.tsv`
- `outputs/audit/isocolon_qualitative_audit_40.csv`
- `outputs/audit/qualitative_audit_codebook.md`
- `outputs/audit/qualitative_audit_dictionary.tsv`

The sample strata are:

- 10 high-scoring broad non-narrow cases
- 6 typical broad non-narrow cases
- 6 narrow cases
- 8 high-scoring non-target cases
- 5 high-scoring restatement-repetition controls
- 5 low/mid non-target baselines

## Reviewers

Four reviewer files were validated:

- `outputs/audit/agent_reviews/codex_1_audit.tsv`
- `outputs/audit/agent_reviews/codex_2_audit.tsv`
- `outputs/audit/agent_reviews/opus_1_audit.tsv`
- `outputs/audit/agent_reviews/opus_2_audit.tsv`

The Opus runs were completed manually after the local CLI attempt was blocked.
The second Codex pass was then completed locally. One schema repair was made to
`codex_2_audit.tsv`: `formal_parallelism = uncertain` was changed to `weak` on
QA017 because the codebook allows only `none`, `weak`, `moderate`, and `strong`.

Command:

```bash
scripts/summarize_qualitative_audit.py
```

Outputs:

- `outputs/audit/agent_reviews/all_agent_ratings.tsv`
- `outputs/audit/agent_reviews/agent_rating_summary.tsv`
- `outputs/audit/agent_reviews/audit_consensus.tsv`
- `outputs/audit/agent_reviews/audit_stratum_summary.tsv`

## Agent-Level Counts

`is_isocolonic` counts:

- codex_1: 9 yes, 27 no, 4 uncertain
- codex_2: 8 yes, 28 no, 4 uncertain
- opus_1: 10 yes, 25 no, 5 uncertain
- opus_2: 8 yes, 27 no, 5 uncertain

Common failure modes are stable across reviewers:

- repetition
- dialogue formula
- bad segmentation
- list formatting
- template or quotation artifacts

## Consensus Results

Majority consensus across the four reviewers:

- 8 yes
- 27 no
- 3 uncertain
- 2 split or tied

The clean majority-yes rows are:

- QA002: `You can use this on twist outs.` / `You can use this on braid outs.`
- QA003: `They made their case with intellect.` / `They made their case with evidence`
- QA004: `Somebody can manage to be a teacher.` / `Somebody can manage to be a cop.`
- QA005: `Matter tells spacetime how to curve;` / `spacetime tells matter how to move.`
- QA008: `I am the master of my fate,` / `I am the captain of my soul.`
- QA009: `They'll talk about the party,` / `they'll talk about the crash,`
- QA010: `They're bringing drugs.` / `They're bringing crime.`
- QA025: `Getting the Material Right` / `Getting the Delivery Right`

The split/tied rows are:

- QA007: `Three days.` / `Four days.`
- QA015: `having not only aesthetic value,` / `but also acoustic.`

## Stratum Pattern

The high broad non-narrow stratum has 7 majority-yes rows out of 10, with one
additional split row. The typical broad stratum has no clean majority-yes rows.
The narrow stratum has no majority-yes rows. The high non-target stratum has
one majority-yes row, QA025, which is an unplanned positive example under a
`joint-sequence` label. The restatement controls and baseline non-targets are
all rejected.

## Interpretation

The qualitative audit supports the main quantitative pattern but narrows its
interpretation. Very high-scoring broad list/disjunction cases often are
genuine rhetorical parallelism. Typical broad cases and narrow antithesis cases
are much less convincing. Restatement-repetition is confirmed as a strong false
positive family, not as the rhetorical target.

For the paper, the safest claim is that the score identifies a useful high-end
signal for rhetorical parallelism in list/disjunction/contrast-like
constructions, but the score should not be treated as a direct binary
classifier for isocolon without human filtering or a stronger supervised
calibration step.

## Targeted Adjudication

After the human pass, the codebook was revised to clarify five points:

- a colon need not be an independent clause;
- phonological parallelism can count as formal parallelism;
- dialogic echo can count when it creates a meaningful parallel or contrastive
  structure;
- apposition or identity can be rhetorically relevant without being comparison
  or isocolon;
- comparison or coordination can be present without enough formal parallelism
  to count as isocolon.

The targeted adjudication then asked two Codex and two Opus passes to stress
test 11 disputed rows under the revised codebook. The surviving Opus outputs
were written as `_review.tsv` files rather than the requested exact filenames,
so the combined summary uses the actual on-disk files:

- `outputs/audit/agent_reviews/codex_adjudicator_1.tsv`
- `outputs/audit/agent_reviews/codex_adjudicator_2.tsv`
- `outputs/audit/agent_reviews/opus_adjudicator_1_review.tsv`
- `outputs/audit/agent_reviews/opus_adjudicator_2_review.tsv`

Combined outputs:

- `outputs/audit/agent_reviews/targeted_adjudication_all_ratings.tsv`
- `outputs/audit/agent_reviews/targeted_adjudication_summary.tsv`

Adjudicator majority by row:

- QA007: uncertain, 4 uncertain
- QA011: yes, 3 yes and 1 uncertain
- QA013: no, 3 no and 1 uncertain
- QA014: yes, 4 yes
- QA016: yes, 2 yes, 1 no, and 1 uncertain
- QA018: split, 2 yes and 2 no
- QA019: no, 4 no
- QA021: uncertain, 4 uncertain
- QA028: no, 3 no and 1 uncertain
- QA030: no, 4 no
- QA040: no, 4 no

The adjudication leaves QA018 as the main unresolved theoretical case: the
human annotation treats phonological and infinitival patterning as enough for a
weak isocolonic yes, while two adjudicators still reject it because the phrase
types differ. QA019, QA030, and QA040 are the strongest challenges to the human
yes labels, with all four adjudicators preferring no. QA007 and QA021 should be
treated as context-dependent uncertain cases unless the paper gives a broader
definition of minimal or fragmentary cola.

## Second Audit Batch

A second targeted 40-row batch was sampled to stress the measurement boundary.
The batch included high and mid broad targets, narrow antithesis or contrast
cases, dialogue echo candidates, comparative/concessive cases, high-scoring
non-target artifacts, and restatement/repetition controls.

Human coding for the second batch is now frozen:

- yes: 14;
- no: 23;
- uncertain: 3.

The strongest human-positive stratum was high broad targets, with 6 yes labels
out of 6. Mid broad targets had 3 yes and 3 no labels. Narrow
antithesis/contrast cases had 3 yes and 5 no labels. Dialogue echo candidates
were mostly not strict isocolon, with 4 no and 2 uncertain labels. The
restatement/repetition control again produced no human-isocolonic cases.

Two Codex and two Opus reviewers under the revised codebook completed
independent reviews of all 40 rows:

- `outputs/audit/agent_reviews/codex_batch2_1.tsv`: 10 yes, 23 no, 7 uncertain;
- `outputs/audit/agent_reviews/codex_batch2_2.tsv`: 12 yes, 25 no, 3 uncertain;
- `outputs/audit/agent_reviews/opus_batch2_1.tsv`: 10 yes, 23 no, 7 uncertain;
- `outputs/audit/agent_reviews/opus_batch2_2.tsv`: 11 yes, 25 no, 4 uncertain.

All four files were validated as complete 40-row reviews. Human-agent agreement
was high in this batch. Three-way Cohen's kappas were 0.824, 0.811, 0.824, and
0.767 for Codex 1, Codex 2, Opus 1, and Opus 2 respectively. Binary yes versus
not-yes kappas were 0.765, 0.886, 0.765, and 0.827.

Inter-agent reliability was also high. With four agents, batch 2 had 36/40
unanimous three-way labels and 38/40 unanimous binary labels. Fleiss's kappa was
0.886 for three-way labels and 0.926 for binary labels. Krippendorff's alpha was
0.887 and 0.926 respectively. Across both 40-row batches, pooled inter-agent
alpha is now 0.821 for three-way labels and 0.865 for binary labels.

The remaining batch-2 pressure points are not coding errors. They are boundary
cases:

- QB010: human yes; all four agents uncertain;
- QB011: human yes; all four agents uncertain;
- QB017: human yes; three agents uncertain and one agent yes.

All three involve genuine rhetorical contrast or coordination with weak formal
matching. The final human coding keeps them as yes. QB021 and QB026 remain
human uncertain; two agents marked each uncertain, and two marked each no.
QB007 is effectively resolved as a weak yes/uncertain boundary case: two agents
marked it yes, and two marked it uncertain.

Combined validation outputs were written to:

- `outputs/audit/qualitative_validation_human_summary.tsv`;
- `outputs/audit/agent_reviews/qualitative_validation_agent_summary.tsv`;
- `outputs/audit/agent_reviews/qualitative_validation_agreement.tsv`;
- `outputs/audit/agent_reviews/qualitative_validation_row_summary.tsv`;
- `outputs/audit/agent_reviews/qualitative_validation_disagreements.tsv`.

Across the two human-coded batches, the audit now contains 80 rows: 33 yes, 43
no, and 4 uncertain. The combined sample should be treated as a pilot
validation set, not as a final supervised gold standard.

## Gemini External Check

Brett also ran the full 80-row validation file through Gemini using Antigravity
CLI 1.0.3 with Gemini 3.5 Flash (Medium). The run is recorded separately from
the balanced four-agent Codex/Opus panel because it is a single 80-row pass and
because it did not use the `uncertain` label at all.

Do not use the Gemini outputs in the primary machine-coding evaluation. Keep
them as a documented external check only. The quality is lower for this task:
Gemini is overly reluctant to use boundary categories, gives no uncertain
labels, and the Pro rerun reproduced the Flash coding exactly apart from the
`agent` field. The main agent evidence should therefore remain the balanced
Codex/Opus panel.

Inputs and outputs:

- `outputs/audit/isocolon_qualitative_audit_80.csv`;
- `outputs/audit/agent_reviews/gemini_80_prompt.txt`;
- `outputs/audit/agent_reviews/gemini_80.tsv`;
- `outputs/audit/agent_reviews/gemini_80_summary.tsv`;
- `outputs/audit/agent_reviews/gemini_80_disagreements.tsv`.

Gemini coded 26 yes, 54 no, and 0 uncertain. Against the human labels, it had
three-way agreement of 0.850 with Cohen's kappa 0.702, and binary yes versus
not-yes agreement of 0.887 with kappa 0.760.

Gemini is stricter than the Codex/Opus panel. It rejects several human yes
boundary cases that had already surfaced as pressure points, including QA018,
QA019, QA030, QA040, QB007, QB010, QB011, and QB017. It also converts the human
uncertain labels QA013, QB021, and QB026 to no, while converting QB032 to yes.
This pattern supports the measurement interpretation: model families are
mostly stable on clear cases, but differ in how much weak formal parallelism,
dialogic echo, and formulaic biographical/list structure should count.

Brett then reran the same 80-row task under Antigravity with Gemini 3.1 Pro
(High), writing `outputs/audit/agent_reviews/gemini_pro_80.tsv`. The file
validated cleanly and had the same 26 yes, 54 no, and 0 uncertain labels. A
row-by-row comparison found no substantive differences from the Gemini Flash
file: the only changed field was the `agent` value. The comparison is recorded
in `outputs/audit/agent_reviews/gemini_model_comparison.tsv`. For analysis, the
Pro rerun should therefore be treated as an identical rerun, not as an
independent additional rater.

## Machine Coding Evaluation

Following a Gelman-style measurement approach, the automatic score and agent
codes should be treated as noisy measurements rather than ground truth. The
right question is not a single accuracy number. The right questions are where
the machine coding works, where it fails, and how much the substantive result
changes under different measurement assumptions.

For the paper, evaluate the machine coding by stratum rather than overall:

- high-scoring broad targets;
- typical broad targets;
- narrow antithesis or contrast cases;
- high-scoring non-targets;
- restatement or repetition controls;
- baseline non-targets.

Use the machine score as a continuous measurement where possible. A binary
machine label would hide the main uncertainty, especially the distinction
between strict isocolon and broader comparative or coordinative parallelism.

The working measurement categories are:

- strict isocolon;
- broader comparative or coordinative parallelism;
- rhetorical but non-isocolonic relation;
- artifact, including repetition, dialogue formula, list formatting, and bad
  segmentation.

The two 40-row human audits are enough for a pilot validation section and for
motivating these measurement categories. They are not enough to treat agent
coding as ground truth.

## Remaining Validation

Agent coding should remain in the pipeline as triage, sensitivity evidence, and
disagreement evidence. It should not replace human coding.

For each remaining validation or qualitative-audit batch, use a four-agent
panel: two Codex reviewers and two Opus reviewers. Four is not a magic number;
it is the smallest balanced replicated panel for this design. Two agents make
disagreement hard to interpret. Three agents force an unbalanced model-family
design and can make a 2--1 split look more settled than it is. Four gives two
draws from each model family, supports within-family and cross-family agreement
checks, and preserves 2--2 ties as useful item-difficulty signals. More agents
would mainly narrow uncertainty around the agent panel, while the real
bottleneck remains human or expert adjudication and codebook clarity.

The four-agent labels should not be collapsed into ground truth. Keep the raw
ratings, report reliability and disagreement by stratum, and treat unanimous
agent disagreement with the human code as evidence of a theoretical boundary or
possible codebook issue rather than automatic human error.

The second targeted human-coded batch has now been completed. For a short paper
or methods pilot, the current 80-row audit is enough to report cautious
stratum-level validation patterns. For firmer performance estimates, add more
human coding:

- 80--120 more rows if the paper needs firmer performance estimates.

## Third Audit Batch

A third boundary-focused 40-row batch has been sampled from previously
unsampled rows:

- `outputs/audit/isocolon_qualitative_audit_batch3_40.csv`;
- `outputs/audit/isocolon_qualitative_audit_batch3_40.tsv`;
- `outputs/audit/qualitative_audit_batch3_rubric.md`.

The batch uses IDs QC001--QC040 and has no `source_row` overlap with batches 1
or 2. It repeats the batch-2 stratum design: high and mid broad targets, narrow
antithesis/contrast, dialogue echo candidates, comparative concession,
high-scoring non-target artifacts, and restatement/repetition controls.

The full four-agent panel has been completed and validated:

- `outputs/audit/agent_reviews/codex_batch3_1.tsv`: 11 yes, 27 no, 2 uncertain;
- `outputs/audit/agent_reviews/codex_batch3_2.tsv`: 12 yes, 26 no, 2 uncertain.
- `outputs/audit/agent_reviews/opus_batch3_1.tsv`: 10 yes, 26 no, 4 uncertain;
- `outputs/audit/agent_reviews/opus_batch3_2.tsv`: 8 yes, 29 no, 3 uncertain.

Inter-agent reliability is lower than in batch 2, which is expected for a
harder boundary sample. The four-agent panel has 30/40 unanimous three-way
labels and 30/40 unanimous binary labels. Fleiss's kappa is 0.657 for
three-way labels and 0.617 for binary yes versus not-yes labels.
Krippendorff's alpha is 0.659 and 0.620 respectively.

The main pressure rows are:

- QC004: roster/list enumeration, 2 yes / 1 no / 1 uncertain;
- QC008 and QC010: Codex yes, Opus no, both involving to-infinitival material;
- QC015: Codex no, Opus yes on a contrastive biography sentence;
- QC019: all four uncertain on bare Spanish numerals `Ocho.` / `Seis.`;
- QC024 and QC026: dialogue-echo boundary cases;
- QC030: all four uncertain on fully redacted material.

Full-batch human coding is paused after the first 80 rows, so batch 3 should
not be used as a full human-anchored validation set. Brett adjudicated the
eight pressure rows only:

- `outputs/audit/isocolon_qualitative_audit_batch3_disagreement_8.csv`;
- `outputs/audit/agent_reviews/batch3_targeted_human_adjudication.tsv`.

The targeted human adjudication marked 7 no and 1 yes. The sole human yes is
QC026 (`it's the event horizon of our knowledge?` / `This is kind of the event
horizon.`), where Brett treats the metaphor echo as rhetorically relevant even
though the agent majority was no. The seven no labels include the roster/list
case QC004, the to-infinitival cases QC008 and QC010, the biography contrast
QC015, the bare Spanish numerals QC019, the dialogue formula QC024, and the
fully redacted case QC030. Batch 3 should therefore be treated as an
agent-first stress test with targeted human adjudication, not as a full
validation batch.

A manuscript-facing validation summary has been drafted in
`notes/paper-facing-validation-summary.md`.

The current batch-3 panel summary files are:

- `outputs/audit/agent_reviews/batch3_agent_summary.tsv`;
- `outputs/audit/agent_reviews/batch3_agent_consensus.tsv`;
- `outputs/audit/agent_reviews/batch3_agent_stratum_summary.tsv`.

Any further sample should concentrate on the measurement boundary:

- high-scoring broad targets not already sampled;
- mid-scoring broad targets;
- narrow antithesis or contrast cases;
- high-scoring non-targets;
- dialogue echo cases;
- comparative or concessive cases like QA019 and QA040;
- restatement and repetition controls.

The goal of the next batch is to estimate how often the automatic score finds
strict isocolon, broader parallelism, rhetorical non-isocolon, and artifacts.
The goal is not to force the agents and human coding into full agreement.
