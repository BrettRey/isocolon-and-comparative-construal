#!/usr/bin/env python3
"""Prepare audited adversative-antithesis rows for classical-antithesis coding."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd


KEEP_COLUMNS = [
    "batch",
    "audit_id",
    "stratum",
    "source_row",
    "doc",
    "genre",
    "orig_label",
    "isocolon_score",
    "length_score",
    "syntax_score",
    "lexical_score",
    "unit1_text",
    "unit2_text",
    "human_isocolonic",
    "formal_parallelism",
    "rhetorically_relevant",
    "genuine_comparison_or_coordination",
    "notes",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="outputs/audit/isocolon_qualitative_audit_80.csv")
    parser.add_argument("--out", default="outputs/audit/adversative_antithesis_classical_audit.tsv")
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    subset = frame[frame["orig_label"].eq("adversative-antithesis")].copy()
    subset = subset[KEEP_COLUMNS]
    subset["classical_antithesis"] = ""
    subset["semantic_opposition"] = ""
    subset["parallel_opposition"] = ""
    subset["antithesis_notes"] = ""

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subset.to_csv(out_path, sep="\t", index=False, quoting=csv.QUOTE_MINIMAL)


if __name__ == "__main__":
    main()
