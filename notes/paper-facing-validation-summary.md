# Paper-Facing Validation Summary

## Status

Use this note as the source text for the manuscript's qualitative-validation
paragraphs. The primary validation evidence is the 80-row human-coded set from
batches 1 and 2. Batch 3 is an agent-first stress test with targeted human
adjudication of eight disagreement rows. Gemini outputs are documented but
excluded from the primary evaluation.

## Draft Prose

The automatic score is best treated as a noisy measure of formal balance, not
as a binary detector of isocolon. I therefore checked the score against a
stratified qualitative audit. The primary human-coded validation set contains
80 adjacent unit pairs sampled from high-scoring broad targets, mid-scoring
targets, narrow antithesis or contrast cases, dialogue echo candidates,
comparative or concessive cases, high-scoring non-target artifacts,
restatement controls, and low or mid non-target baselines.

In the 80 human-coded rows, 33 were coded as isocolonic, 43 as non-isocolonic,
and 4 as uncertain. The strongest positive stratum was the high-scoring broad
target group: 14 of 16 high broad target rows were human-coded as isocolonic
across the first two batches. The restatement/repetition controls behaved as
negative controls: 0 of 9 were human-coded as isocolonic, despite very high
formal scores. This confirms that exact repetition can produce high surface
similarity without satisfying the rhetorical target.

The audit also shows where the score is less direct. Mid-scoring broad targets
and narrow antithesis/contrast cases include both genuine rhetorical
parallelism and cases where comparison or coordination is present without
enough formal balance to count as isocolon. Dialogue echo is especially
unstable: it can be rhetorically relevant, but many cases are better treated as
turn-taking, repair, or formulaic repetition. Apposition and identity can be
rhetorically relevant clarification without being comparison or isocolon.

The agent coding was used as replicated noisy measurement rather than ground
truth. In batch 1, before the codebook boundary cases were clarified, four
agents had Krippendorff's alpha of 0.748 for three-way yes/no/uncertain labels
and 0.794 for binary yes versus not-yes labels. In batch 2, after the codebook
clarifications, the four-agent panel had alpha of 0.887 for three-way labels
and 0.926 for binary labels. Human-agent agreement was also substantially
higher in batch 2, with binary Cohen's kappas from 0.765 to 0.886.

A third 40-row batch was used as a stress test rather than a full
human-anchored validation set. Its four-agent reliability was lower
(alpha 0.659 three-way; 0.620 binary), as expected for a deliberately harder
boundary sample. Brett then adjudicated the eight rows where the agents split
or marked uncertainty. Seven were coded no, and one was coded yes. The single
yes, QC026, was a metaphor-echo case: `it's the event horizon of our
knowledge?` / `This is kind of the event horizon.` That row is useful because
it shows that rhetorically relevant echo can be isocolonic without serving the
paper's central comparative-construal target.

The validation supports a restrained interpretation. The score is useful as a
ranking device for finding candidate rhetorical parallelism, especially among
high-scoring list and disjunction relations. It is not a stand-alone binary
classifier for isocolon. The substantive analysis should therefore use the
score continuously, report sensitivity to stricter and broader definitions, and
distinguish strict isocolon from broader comparison, coordination, rhetorical
echo, and artifacts.

## Numbers To Report

- Primary human-coded validation set: 80 rows.
- Human labels: 33 yes, 43 no, 4 uncertain.
- High broad target rows: 14/16 yes.
- Restatement/repetition controls: 0/9 yes.
- Batch 1 inter-agent alpha: 0.748 three-way, 0.794 binary.
- Batch 2 inter-agent alpha: 0.887 three-way, 0.926 binary.
- Batch 3 stress-test alpha: 0.659 three-way, 0.620 binary.
- Batch 3 targeted adjudication: 8 rows, 7 no and 1 yes.

## Wording Guardrails

- Say the audit validates the score as a ranking or triage measure.
- Do not call the score a binary classifier.
- Do not treat agent majority vote as ground truth.
- Keep Gemini out of the primary evaluation.
- Use batch 3 only as a boundary stress test unless the remaining 32 rows are
  human-coded later.
