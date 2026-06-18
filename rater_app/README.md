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
