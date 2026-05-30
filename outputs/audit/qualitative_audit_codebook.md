# Qualitative Isocolon Audit Codebook

## Unit Of Analysis

Each row is one adjacent eRST relation pair. Code the relation between
`unit1_text` and `unit2_text`, not the whole document and not the source label
alone.

Primary question:

> Do these two adjacent units form a rhetorically relevant isocolonic or
> formally parallel pair?

Use the automatic score only as background. It should not decide the human
code.

For this audit, a `colon` means a rhetorically construable member of a paired
or serial construction. It does not have to be a full independent clause. A
colon can be a phrase, predicate, fragment, short elliptical answer, or
dialogue turn if it functions as one member of the figure.

## Primary Code

### `human_isocolonic`

Allowed values: `yes`, `no`, `uncertain`

Code `yes` when the two units show a recognizable formal parallelism that
could plausibly do rhetorical work. The best cases usually have a shared
syntactic frame, balanced length, matched slots, or a clear parallel rhythm.
Formal parallelism can be phonological, morphological, syntactic, lexical,
constructional, or some combination of these.

Code `no` when similarity is mainly accidental, purely local, caused by exact
repetition, caused by formatting, or too fragmentary to count as a rhetorical
parallel construction.

Code `uncertain` when the pair may be parallel but context, segmentation, or
redaction makes the judgment unstable.

## Secondary Codes

### `formal_parallelism`

Allowed values: `none`, `weak`, `moderate`, `strong`

- `none`: no systematic matching of form.
- `weak`: one local similarity, such as matched length or one repeated word,
  but no clear parallel frame.
- `moderate`: recognizable parallel phrase or clause structure, but with
  uneven length, missing slots, or partial mismatch.
- `strong`: clear matched frame, balanced units, repeated syntactic pattern,
  or obvious slot substitution.

This field describes form only. Exact repetition can be `strong` here but
still `human_isocolonic = no` if it is not a rhetorically meaningful parallel
pair.

### `rhetorically_relevant`

Allowed values: `yes`, `no`, `uncertain`

Code `yes` when the parallelism appears to help organize, contrast, compare,
coordinate, intensify, or make memorable the relation between the units.

Code `no` when the similarity is just a repeated formula, heading pattern,
metadata artifact, dialogue repair, or accidental short-unit match.

Apposition or identity can be rhetorically relevant as clarification even when
it is not comparison and not isocolon.

### `genuine_comparison_or_coordination`

Allowed values: `yes`, `no`, `uncertain`

Code `yes` when the pair sets two items, alternatives, actions, qualities, or
states beside each other in a list, contrast, disjunction, comparison, or
antithesis.

Code `no` for pure repetition, restatement, attribution, phatic exchange,
question-answer residue, or elaboration without a paired comparison.

Identity and apposition are not comparison for this study, even if they are
rhetorically useful.

## False-Positive Flags

For each false-positive column, use `yes`, `no`, or `uncertain`.

These flags diagnose why a high automatic score may not be a genuine
rhetorical isocolon. A flag can be `yes` even if the pair has some formal
parallelism.

### `false_positive_repetition`

Use `yes` when the score is high mainly because the units are exact or near
exact repeats: `Thank you.` / `Thank you.`, repeated names, repeated fragments,
or capitalization variants.

### `false_positive_list_formatting`

Use `yes` when the score is high mainly because the pair consists of headings,
list entries, menu-like items, index labels, proof bullets, or other formatting
patterns rather than a rhetorical paired construction.

Do not automatically penalize all lists. A list can still be a genuine
isocolonic pair if the wording itself creates a rhetorical parallel structure.

### `false_positive_dialogue_formula`

Use `yes` for backchannels, repairs, short answers, repeated politeness
formulae, or ordinary turn-taking that looks parallel only because dialogue
turns are short.

Do not automatically mark dialogue as a false positive. Dialogic echo can
count as isocolonic if the turn pair creates a rhetorically meaningful parallel
or contrastive structure, even when the speakers differ. The false-positive
flag is for merely formulaic echo, backchanneling, or turn-taking residue.

### `false_positive_template_or_quote`

Use `yes` when a template, boilerplate, copied title pattern, or quoted source
is the main reason for the match and the current discourse relation is not
itself doing rhetorical parallel work.

Quoted language can still be genuinely isocolonic if the quoted text itself is
the rhetorical figure being evaluated. Note that in `notes`.

### `bad_segmentation`

Allowed values: `yes`, `no`, `uncertain`

Use `yes` when the relation arguments are split so badly that the units cannot
be judged as a pair: one unit is only a stray complement, punctuation has
broken the construction, or a crucial element is outside the row.

Use `uncertain` for heavy redaction, markup, or fragments where the pair might
be interpretable with more context.

## Confidence

Allowed values: number from `0` to `1`.

- `0.90-1.00`: clear judgment.
- `0.70-0.89`: likely judgment with minor uncertainty.
- `0.50-0.69`: genuinely difficult or context-sensitive.
- below `0.50`: avoid unless the row is almost uncodable.

## Decision Rules

1. Exact repetition is usually `human_isocolonic = no`, `formal_parallelism =
   strong`, and `false_positive_repetition = yes`.

2. Very short pairs, such as one- or two-word units, need a clear rhetorical
   contrast, list, or antithesis to count as `yes`. Otherwise use `no` or
   `uncertain`.

3. A semicolon, colon, or line break does not by itself make a pair
   isocolonic.

4. Matched syntax matters more than matched length alone. Balanced fragments
   with unrelated functions are not enough.

4a. Phonological patterning can contribute to `formal_parallelism`, especially
    when it aligns with a syntactic or constructional relation.

5. If a pair is a true list/contrast construction and also has matched wording,
   code it as `yes` even if it came from a list-like genre.

6. If the pair is grammatically parallel but rhetorically inert, code
   `formal_parallelism` as appropriate and `human_isocolonic = no` or
   `uncertain`.

7. If source labels and your judgment conflict, trust the text. The audit is
   checking the operationalization, not confirming the corpus label.

8. `genuine_comparison_or_coordination = yes` does not force
   `human_isocolonic = yes`. A pair can express comparison, contrast,
   alternation, or coordination without enough formal parallelism to count as
   isocolon.

## Short Examples From The Sample

Clear yes:

- `You can use this on twist outs.` / `You can use this on braid outs.`
  Shared frame with slot substitution.
- `They're bringing drugs.` / `They're bringing crime.`
  Strong repeated syntactic frame with rhetorical accumulation.

Likely yes, with note:

- `I am the master of my fate,` / `I am the captain of my soul.`
  Quoted, but the quoted language itself is a clear parallel figure.

Likely no:

- `Thank you.` / `Thank you.`
  Exact repetition, not a paired construction.
- `stop.` / `Stop`
  Repetition/capitalization artifact.

Likely uncertain:

- Redacted strings or fragments where the relation cannot be interpreted
  without missing text.
