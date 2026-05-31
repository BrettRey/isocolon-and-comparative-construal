#!/usr/bin/env python3
"""Test whether hand-marked classical antitheses have higher formal balance."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd


CODE_FIELDS = ["classical_antithesis", "semantic_opposition", "parallel_opposition"]
OUTCOMES = [
    ("formal_balance", "isocolon_score"),
    ("isocolon_length", "length_score"),
    ("parison_syntax", "syntax_score"),
    ("lexical_echo", "lexical_score"),
]
VALID_CODES = {"yes", "no", "uncertain", "uncoded"}


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def normalize_codes(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    for field in CODE_FIELDS:
        if field not in frame:
            raise ValueError(f"Missing coding field: {field}")
        frame[field] = frame[field].fillna("uncoded").astype(str).str.strip().str.lower()
        bad = sorted(set(frame[field]) - VALID_CODES)
        if bad:
            raise ValueError(f"{field} has invalid values: {', '.join(bad)}")
    return frame


def load_coded(coding_path: str, scores_path: str | None) -> pd.DataFrame:
    coded = pd.read_csv(coding_path, sep="\t")
    coded = normalize_codes(coded)

    if all(score_col in coded for _, score_col in OUTCOMES):
        return coded

    if scores_path is None:
        raise ValueError("Coding file lacks score columns; pass --scores to merge them.")

    scores = pd.read_csv(scores_path, sep="\t").reset_index(names="source_row")
    score_columns = [
        "source_row",
        "doc",
        "genre",
        "orig_label",
        "isocolon_score",
        "length_score",
        "syntax_score",
        "lexical_score",
    ]
    merged = coded.merge(scores[score_columns], on="source_row", how="left", suffixes=("", "_scorefile"))
    if merged["isocolon_score"].isna().any():
        missing = int(merged["isocolon_score"].isna().sum())
        raise ValueError(f"{missing} coded rows failed to merge with score data on source_row.")
    return merged


def difference_row(
    frame: pd.DataFrame,
    field: str,
    outcome_label: str,
    outcome: str,
    *,
    rng: np.random.Generator,
    permutations: int,
) -> dict[str, object]:
    coded = frame[frame[field].isin({"yes", "no"})].copy()
    yes = coded[coded[field].eq("yes")][outcome].astype(float).to_numpy()
    no = coded[coded[field].eq("no")][outcome].astype(float).to_numpy()

    base = {
        "field": field,
        "outcome": outcome_label,
        "score_column": outcome,
        "n_coded_yes_no": len(coded),
        "n_yes": len(yes),
        "n_no": len(no),
    }
    if len(yes) == 0 or len(no) == 0:
        return {
            **base,
            "mean_yes_points": "",
            "mean_no_points": "",
            "diff_points": "",
            "ci_low_points": "",
            "ci_high_points": "",
            "permutation_p": "",
            "status": "insufficient yes/no-coded rows",
        }

    mean_yes = float(100 * yes.mean())
    mean_no = float(100 * no.mean())
    diff = mean_yes - mean_no

    ci_low = ""
    ci_high = ""
    if len(yes) > 1 and len(no) > 1:
        se = 100 * np.sqrt(yes.var(ddof=1) / len(yes) + no.var(ddof=1) / len(no))
        ci_low = float(diff - 1.96 * se)
        ci_high = float(diff + 1.96 * se)

    values = coded[outcome].astype(float).to_numpy()
    labels = coded[field].eq("yes").to_numpy()
    observed = float(values[labels].mean() - values[~labels].mean())
    exceedances = 0
    for _ in range(permutations):
        permuted = rng.permutation(labels)
        permuted_diff = float(values[permuted].mean() - values[~permuted].mean())
        if abs(permuted_diff) >= abs(observed):
            exceedances += 1
    p_value = (exceedances + 1) / (permutations + 1)

    return {
        **base,
        "mean_yes_points": mean_yes,
        "mean_no_points": mean_no,
        "diff_points": diff,
        "ci_low_points": ci_low,
        "ci_high_points": ci_high,
        "permutation_p": p_value,
        "status": "ok",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="outputs/audit/adversative_antithesis_full_classical_coding.tsv",
    )
    parser.add_argument("--scores", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out", default="data/derived/antithesis_decomposition.tsv")
    parser.add_argument("--permutations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260530)
    args = parser.parse_args()

    frame = load_coded(args.input, args.scores)
    rng = np.random.default_rng(args.seed)
    rows: list[dict[str, object]] = []
    for field in CODE_FIELDS:
        for outcome_label, outcome in OUTCOMES:
            rows.append(
                difference_row(
                    frame,
                    field,
                    outcome_label,
                    outcome,
                    rng=rng,
                    permutations=args.permutations,
                )
            )

    write_tsv(Path(args.out), rows)

    statuses = pd.Series([row["status"] for row in rows]).value_counts().to_dict()
    coded_counts = {
        field: frame[field].value_counts().reindex(["yes", "no", "uncertain", "uncoded"], fill_value=0).to_dict()
        for field in CODE_FIELDS
    }
    print(f"Wrote {len(rows)} rows to {args.out}")
    print(f"Statuses: {statuses}")
    print(f"Coding counts: {coded_counts}")


if __name__ == "__main__":
    main()
