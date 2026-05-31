#!/usr/bin/env python3
"""Prepare adversative-antithesis rows for classical-antithesis coding."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd


ANTITHESIS_LABEL = "adversative-antithesis"

CODE_COLUMNS = [
    "classical_antithesis",
    "semantic_opposition",
    "parallel_opposition",
    "antithesis_notes",
]

SCORED_COLUMNS = [
    "code_id",
    "source_row",
    "doc",
    "collection",
    "genre",
    "framework",
    "partition",
    "orig_label",
    "rel_type",
    "same_sentence",
    "unit1_ends_colon",
    "unit1_ends_semicolon",
    "word_len_1",
    "word_len_2",
    "isocolon_score",
    "length_score",
    "syntax_score",
    "lexical_score",
    "unit1_text",
    "unit2_text",
]

CODING_COLUMNS = [
    "code_id",
    "source_row",
    "doc",
    "collection",
    "genre",
    "rel_type",
    "same_sentence",
    "word_len_1",
    "word_len_2",
    "unit1_text",
    "unit2_text",
    *CODE_COLUMNS,
]

AUDIT_COLUMNS = [
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


def write_tsv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, sep="\t", index=False, quoting=csv.QUOTE_MINIMAL)


def blank_code_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["classical_antithesis"] = "uncoded"
    frame["semantic_opposition"] = "uncoded"
    frame["parallel_opposition"] = "uncoded"
    frame["antithesis_notes"] = "needs_human_decomposition"
    return frame


def load_full_antithesis(scores_path: str) -> pd.DataFrame:
    scores = pd.read_csv(scores_path, sep="\t")
    scores = scores.reset_index(names="source_row")
    subset = scores[scores["orig_label"].eq(ANTITHESIS_LABEL)].copy()
    subset.insert(0, "code_id", [f"AA{i:03d}" for i in range(1, len(subset) + 1)])
    subset = blank_code_columns(subset)
    return subset


def load_audit_subset(audit_path: str) -> pd.DataFrame:
    audit = pd.read_csv(audit_path)
    subset = audit[audit["orig_label"].eq(ANTITHESIS_LABEL)].copy()
    subset = subset[AUDIT_COLUMNS]
    subset = blank_code_columns(subset)
    return subset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--audit", default="outputs/audit/isocolon_qualitative_audit_80.csv")
    parser.add_argument("--audited-out", default="outputs/audit/adversative_antithesis_classical_audit.tsv")
    parser.add_argument(
        "--full-out",
        default="outputs/audit/adversative_antithesis_full_classical_audit.tsv",
    )
    parser.add_argument(
        "--coding-out",
        default="outputs/audit/adversative_antithesis_full_classical_coding.tsv",
    )
    parser.add_argument("--seed", type=int, default=20260530)
    args = parser.parse_args()

    audited = load_audit_subset(args.audit)
    write_tsv(Path(args.audited_out), audited)

    full = load_full_antithesis(args.scores)
    write_tsv(Path(args.full_out), full[SCORED_COLUMNS + CODE_COLUMNS])

    coding = full[CODING_COLUMNS].sample(frac=1, random_state=args.seed).reset_index(drop=True)
    write_tsv(Path(args.coding_out), coding)

    print(f"Wrote {len(audited)} audited rows to {args.audited_out}")
    print(f"Wrote {len(full)} full scored rows to {args.full_out}")
    print(f"Wrote {len(coding)} randomized coding rows to {args.coding_out}")


if __name__ == "__main__":
    main()
