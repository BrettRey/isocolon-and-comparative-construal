#!/usr/bin/env python3
"""Run leave-one-genre influence checks for selected formal-balance effects."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from fit_robustness_checks import fit_residualized  # noqa: E402


SPECS = [
    {
        "spec": "broad_main",
        "labels": {"adversative-antithesis", "adversative-contrast", "joint-disjunction", "joint-list"},
        "subset": "all",
        "outcome": "isocolon_score",
        "length_controls": "mean_max",
    },
    {
        "spec": "list_or_disjunction_within_joint",
        "labels": {"joint-disjunction", "joint-list"},
        "subset": "joint",
        "outcome": "isocolon_score",
        "length_controls": "mean_max",
    },
    {
        "spec": "contrast_within_adversative",
        "labels": {"adversative-contrast"},
        "subset": "adversative",
        "outcome": "isocolon_score",
        "length_controls": "mean_max",
    },
    {
        "spec": "contrast_within_adversative_parison",
        "labels": {"adversative-contrast"},
        "subset": "adversative",
        "outcome": "syntax_score",
        "length_controls": "mean_max",
    },
]


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def select_subset(frame: pd.DataFrame, name: str) -> pd.DataFrame:
    if name == "all":
        return frame
    if name == "joint":
        return frame[frame["orig_label"].str.startswith("joint-")].copy()
    if name == "adversative":
        return frame[frame["orig_label"].str.startswith("adversative-")].copy()
    raise ValueError(f"Unknown subset: {name}")


def add_fit_row(rows: list[dict[str, object]], frame: pd.DataFrame, spec: dict[str, object], omitted_genre: str) -> None:
    target = frame["orig_label"].isin(spec["labels"]).astype(float).to_numpy()
    result = fit_residualized(
        frame,
        target,
        spec["outcome"],
        length_controls=spec["length_controls"],
    )
    if result is None:
        return
    rows.append(
        {
            "spec": spec["spec"],
            "omitted_genre": omitted_genre,
            "subset": spec["subset"],
            "outcome": spec["outcome"],
            "n_rows": len(frame),
            "n_docs": frame["doc"].nunique(),
            "n_genres": frame["genre"].nunique(),
            "target_n": result["target_n"],
            "comparison_n": result["comparison_n"],
            "estimate": result["estimate"],
            "cluster_ci_low": result["cluster_ci_low"],
            "cluster_ci_high": result["cluster_ci_high"],
            "length_controls": spec["length_controls"],
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out", default="data/derived/influence_checks.tsv")
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    rows: list[dict[str, object]] = []
    for spec in SPECS:
        subset = select_subset(frame, str(spec["subset"]))
        add_fit_row(rows, subset, spec, "none")
        for genre in sorted(subset["genre"].unique()):
            add_fit_row(rows, subset[~subset["genre"].eq(genre)].copy(), spec, genre)

    write_tsv(Path(args.out), rows)
    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
