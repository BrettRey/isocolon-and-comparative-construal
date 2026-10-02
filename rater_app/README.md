# RST-SC signal-crosswalk app

`rst_signal_crosswalk.html` is a self-contained offline coding interface for
human judgments about RST Signalling Corpus labels. It contains only aggregate
label names, counts, and candidate memberships generated from local aggregate
inventories.

## Running it

Double-click `rst_signal_crosswalk.html`, or open it from a browser with
`file://`. No server, Python runtime, network connection, or AI service is used.

## What a coder does

1. Enter name or initials.
2. For each aggregate signal label, choose one paper-facing role:
   parison-like form, lexical echo, comparison reference, semantic opposition,
   exclude/control, or unresolved.
3. Choose whether the label can be direct evidence, context only, or excluded.
4. Set confidence, optional flags, and notes.
5. Download the JSON response file and put it in `rater_app/responses/`.

Do not paste restricted corpus text, examples, screenshots containing corpus
text, or raw LDC material into the notes.

## Collecting responses

Downloaded JSON files belong in `rater_app/responses/`, which is intentionally
ignored by Git. To merge responses into aggregate local outputs:

```bash
python3 scripts/ingest_rst_signal_judgments.py
```

The ingester writes:

- `data/derived/rst_signal_crosswalk_judgments.tsv`
- `data/derived/rst_signal_crosswalk_judgment_summary.tsv`

Those outputs are local derived files and remain ignored unless deliberately
reviewed for publication safety.

## Regenerating the app

```bash
python3 scripts/build_rst_signal_judgment_app.py
```

The builder reads only `data/derived/rst_sc_formal_signal_candidate_summary.tsv`
and `data/derived/rst_sc_feature_slot_inventory.tsv`.

# Antithesis calibration coding page

`antithesis_coding.html` is the coding page for the `adversative-antithesis`
decomposition. It uses only the public GUM/GENTLE eRST release; no LDC
material. Published copy: https://claude.ai/artifact/1cQ9rfxGTQjfjumdKSrQ8D
(private until shared from its Share menu).

- Batch: 40 calibration items, the first 40 non-reddit rows of
  `outputs/audit/adversative_antithesis_full_classical_coding.tsv`. The 26
  reddit rows are excluded because the corpus distributes them redacted.
  Manifest: `antithesis_items.tsv`. The two profane GENTLE threat letters
  (AA012, AA013) are shown last (`--defer`); batch membership is unchanged.
- Each item shows the sentence before, the sentence(s) containing the two
  units (A and B highlighted), and the sentence after, then asks the three
  codebook judgments plus "what would you call it?" and "where does the rubric
  fail?".
- Coders' work stays in their browser. "Copy my codes" puts a TSV block on the
  clipboard for pasting into email.

To collect: save each pasted return as a `.tsv` or `.txt` file in
`rater_app/responses/antithesis/` (ignored by Git; email quoting `> ` is
tolerated), then run `make antithesis-codes`. Outputs in `data/derived/`:
`antithesis_codes_long.tsv`, `antithesis_agreement.tsv` (pairwise agreement
and Fleiss' kappa per judgment), `antithesis_disagreements.tsv`, and
`antithesis_general_comments.tsv`.

To rebuild after editing `antithesis_coding_template.html`: `make
antithesis-app`, then republish the same file path to keep the URL.
