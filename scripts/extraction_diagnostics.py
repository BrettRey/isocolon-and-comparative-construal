#!/usr/bin/env python3
"""Summarize interval-level diagnostics for GUM/eRST relation extraction."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd


TARGET_LABELS = {
    "adversative-antithesis",
    "adversative-contrast",
    "joint-disjunction",
    "joint-list",
}


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def row(name: str, value: object, note: str) -> dict[str, object]:
    return {"diagnostic": name, "value": value, "note": note}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-pairs", default="data/derived/gum_erst_relation_pairs.tsv")
    parser.add_argument("--adjacent-pairs", default="data/derived/gum_erst_adjacent_relation_pairs.tsv")
    parser.add_argument("--out", default="data/derived/extraction_diagnostics.tsv")
    args = parser.parse_args()

    all_pairs = pd.read_csv(args.all_pairs, sep="\t", dtype=str).fillna("")
    adjacent = pd.read_csv(args.adjacent_pairs, sep="\t", dtype=str).fillna("")
    non_adjacent = all_pairs[~all_pairs["adjacent"].eq("1")].copy()
    duplicate_keys = adjacent[["doc", "unit1_toks", "unit2_toks"]].agg("\t".join, axis=1)
    duplicate_counts = duplicate_keys.value_counts()
    discontinuous_all = all_pairs["unit1_toks"].str.contains(",", regex=False) | all_pairs[
        "unit2_toks"
    ].str.contains(",", regex=False)
    discontinuous_adjacent = adjacent["unit1_toks"].str.contains(",", regex=False) | adjacent[
        "unit2_toks"
    ].str.contains(",", regex=False)

    rows = [
        row("valid_relation_rows", len(all_pairs), "Explicit or implicit eRST rows with labels and token spans."),
        row("adjacent_relation_rows", len(adjacent), "Rows whose token intervals are adjacent in document order."),
        row("non_adjacent_excluded_rows", len(non_adjacent), "Valid relation rows excluded from the adjacent-pair analysis."),
        row(
            "interleaved_excluded_rows",
            int(non_adjacent["doc_order"].eq("interleaved").sum()),
            "Excluded rows whose token intervals interleave rather than form an adjacent pair.",
        ),
        row(
            "gapped_excluded_rows",
            int(non_adjacent["doc_order"].eq("1_before_2").sum()),
            "Excluded rows with unit 1 before unit 2 but at least one intervening token.",
        ),
        row("adjacent_documents", adjacent["doc"].nunique(), "Distinct documents in the adjacent-pair analysis."),
        row("adjacent_genres", adjacent["genre"].nunique(), "Distinct extracted document-genre labels."),
        row("adjacent_gum_rows", int(adjacent["collection"].eq("GUM").sum()), "Adjacent rows from the GUM collection."),
        row(
            "adjacent_gentle_rows",
            int(adjacent["collection"].eq("GENTLE").sum()),
            "Adjacent rows from the GENTLE out-of-domain challenge set.",
        ),
        row(
            "adjacent_explicit_rows",
            int(adjacent["rel_type"].eq("explicit").sum()),
            "Adjacent rows marked explicit in eRST.",
        ),
        row(
            "adjacent_implicit_rows",
            int(adjacent["rel_type"].eq("implicit").sum()),
            "Adjacent rows marked implicit in eRST.",
        ),
        row(
            "discontinuous_valid_rows",
            int(discontinuous_all.sum()),
            "Valid rows where at least one unit has a comma-separated token interval.",
        ),
        row(
            "discontinuous_adjacent_rows",
            int(discontinuous_adjacent.sum()),
            "Adjacent rows where at least one unit has a comma-separated token interval.",
        ),
        row(
            "duplicate_adjacent_span_pairs",
            int((duplicate_counts > 1).sum()),
            "Exact duplicate doc/unit1_toks/unit2_toks keys after adjacency filtering.",
        ),
        row(
            "rows_in_duplicate_adjacent_span_pairs",
            int(duplicate_counts[duplicate_counts > 1].sum()),
            "Rows participating in exact duplicate adjacent span-pair keys.",
        ),
    ]

    for label in sorted(TARGET_LABELS | {"adversative-concession", "restatement-repetition"}):
        rows.append(
            row(
                f"adjacent_{label}_rows",
                int(adjacent["orig_label"].eq(label).sum()),
                f"Adjacent rows with orig_label={label}.",
            )
        )

    write_tsv(Path(args.out), rows)


if __name__ == "__main__":
    main()
