# Corpus Acquisition Notes

## 2026-05-30

The project now has stable local access paths for the existing UD English
corpora and the richer GUM/eRST layers:

- `data/raw/ud-english` links to `../../../../corpora/ud-english`.
- `data/raw/gum-erst` links to `../../../../corpora/gum-erst`.

The central `gum-erst` directory is a sparse checkout of the official GUM
repository at tag `V12.1.0`, commit
`22fdf87f9c71c96bcc771461d06e689b1f90020d`, with `dep` and `rst` checked
out. It includes 301 dependency `.conllu` files, 301 eRST `.rs4` files,
301 RST dependency `.rsd` files, 8 DISRPT `.rels` files, and 8 DISRPT
`.conllu` files.

`scripts/inspect_gum_erst.py` writes local inventories under
`data/derived/`:

- `gum_erst_manifest.tsv`
- `gum_erst_relation_inventory.tsv`
- `gum_erst_signal_inventory.tsv`

`scripts/extract_gum_erst_relation_pairs.py` writes first-pass relation-pair
tables:

- `gum_erst_relation_pairs.tsv`
- `gum_erst_adjacent_relation_pairs.tsv`

`scripts/score_gum_isocolon.py` writes first-pass isocolonicity scores:

- `gum_erst_adjacent_isocolon_scores.tsv`

The first inventory pass found 50,735 valid explicit/implicit DISRPT
relation rows and 1,299 skipped rows with nonstandard or malformed relation
fields. For eRST labels, the main available contrasts include elaboration,
conjunction, temporal, organization, explanation, attribution, frame,
causal, comment, contrast, concession, purpose, reformulation, mode,
condition, query, and alternation. The original eRST relation labels include
`adversative-contrast`, `adversative-antithesis`,
`adversative-concession`, `joint-list`, `joint-sequence`, `joint-other`,
and `joint-disjunction`.

The eRST signal inventory contains gold `syntactic /
parallel_syntactic_construction` signals. In the first count, these occur
mostly with `joint-list`, with smaller counts for `joint-disjunction`,
`adversative-contrast`, `adversative-antithesis`, `joint-other`, and a few
other relations. This makes GUM/eRST immediately usable for a corpus-only
test of whether formal parallelism is preferentially associated with
comparison-like and adversative/joint construals, though the exact mapping
from rhetorical comparison to eRST labels still needs to be defined before
modeling.

The first relation-pair extraction produced 34,976 valid eRST relation rows
and 17,456 strictly adjacent rows after excluding overlapping or interleaved
discontinuous spans. The adjacent table currently includes 482 cases where
the first unit ends in a colon and 141 where it ends in a semicolon; mean
token-balance score is 0.6023. Among adjacent rows, the largest coarse labels are
elaboration, conjunction, attribution, organization, temporal, purpose,
explanation, causal, concession, contrast, mode, reformulation, comment,
condition, frame, query, and alternation. Adjacent original labels relevant
to the current project include `joint-list` (1,690),
`adversative-concession` (679), `joint-sequence` (429),
`adversative-antithesis` (343), `adversative-contrast` (262),
`joint-disjunction` (167), and `joint-other` (160).

The RST Signalling Corpus was not found locally. Public metadata records
exist for LDC2015T10, but the data files are access-restricted under LDC
terms. It should not be downloaded or redistributed without authenticated
institutional access.
