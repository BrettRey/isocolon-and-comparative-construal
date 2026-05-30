#!/usr/bin/env python3
"""Fit document/length/punctuation-stratified permutation nulls."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd


TARGETS = {
    "broad": {"adversative-antithesis", "adversative-contrast", "joint-disjunction", "joint-list"},
    "list_or_disjunction": {"joint-disjunction", "joint-list"},
    "adversative_contrast": {"adversative-contrast"},
}


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def standardize(values: pd.Series) -> np.ndarray:
    array = values.to_numpy(dtype=float)
    std = array.std()
    if std == 0:
        return np.zeros_like(array)
    return (array - array.mean()) / std


def controls(frame: pd.DataFrame) -> np.ndarray:
    columns = [
        np.ones(len(frame)),
        frame["rel_type"].eq("explicit").astype(float).to_numpy(),
        frame["same_sentence"].astype(float).to_numpy(),
        frame["unit1_ends_colon"].astype(float).to_numpy(),
        frame["unit1_ends_semicolon"].astype(float).to_numpy(),
        standardize(np.log1p((frame["word_len_1"] + frame["word_len_2"]) / 2)),
        standardize(np.log1p(np.maximum(frame["word_len_1"], frame["word_len_2"]))),
    ]
    doc_dummies = pd.get_dummies(frame["doc"], drop_first=True, dtype=float).to_numpy()
    return np.column_stack(columns + [doc_dummies])


def residualized_estimate(
    q_controls: np.ndarray,
    y_resid: np.ndarray,
    target: np.ndarray,
) -> float:
    target_resid = target - q_controls @ (q_controls.T @ target)
    denom = float(target_resid @ target_resid)
    if denom <= 1e-12:
        return float("nan")
    return float((target_resid @ y_resid) / denom)


def stratum_indices(frame: pd.DataFrame) -> list[np.ndarray]:
    mean_len = (frame["word_len_1"] + frame["word_len_2"]) / 2
    frame = frame.copy()
    frame["mean_len_bin"] = pd.qcut(mean_len.rank(method="first"), 4, labels=False)
    strata = [
        "doc",
        "rel_type",
        "same_sentence",
        "unit1_ends_colon",
        "unit1_ends_semicolon",
        "mean_len_bin",
    ]
    return [group.index.to_numpy() for _, group in frame.groupby(strata, sort=False)]


def movable_summary(indices: list[np.ndarray], target: np.ndarray) -> tuple[int, int, int]:
    movable_strata = 0
    movable_rows = 0
    movable_targets = 0
    for idx in indices:
        total = float(target[idx].sum())
        if 0 < total < len(idx):
            movable_strata += 1
            movable_rows += len(idx)
            movable_targets += int(total)
    return movable_strata, movable_rows, movable_targets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out", default="data/derived/stratified_nulls.tsv")
    parser.add_argument("--permutations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260530)
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    q_controls, _ = np.linalg.qr(controls(frame), mode="reduced")
    y = frame["isocolon_score"].astype(float).to_numpy()
    y_resid = y - q_controls @ (q_controls.T @ y)
    indices = stratum_indices(frame)
    rng = np.random.default_rng(args.seed)
    rows: list[dict[str, object]] = []

    for target_name, labels in TARGETS.items():
        target = frame["orig_label"].isin(labels).astype(float).to_numpy()
        observed = residualized_estimate(q_controls, y_resid, target)
        movable_strata, movable_rows, movable_targets = movable_summary(indices, target)
        draws = []
        for _ in range(args.permutations):
            shuffled = target.copy()
            for idx in indices:
                if len(idx) > 1:
                    shuffled[idx] = rng.permutation(shuffled[idx])
            draws.append(residualized_estimate(q_controls, y_resid, shuffled))
        draw_array = np.array(draws, dtype=float)
        draw_array = draw_array[~np.isnan(draw_array)]
        empirical_p = (1 + np.sum(np.abs(draw_array) >= abs(observed))) / (len(draw_array) + 1)
        rows.append(
            {
                "target": target_name,
                "outcome": "isocolon_score",
                "target_n": int(target.sum()),
                "comparison_n": int(len(target) - target.sum()),
                "observed_estimate": observed,
                "null_mean": float(draw_array.mean()),
                "null_sd": float(draw_array.std(ddof=1)),
                "null_q025": float(np.quantile(draw_array, 0.025)),
                "null_q975": float(np.quantile(draw_array, 0.975)),
                "empirical_p_two_sided": float(empirical_p),
                "permutations": len(draw_array),
                "movable_strata": movable_strata,
                "movable_rows": movable_rows,
                "movable_target_rows": movable_targets,
                "strata": (
                    "doc; explicitness; same_sentence; colon; semicolon; "
                    "quartile of mean word length"
                ),
                "controls": (
                    "document fixed effects; explicitness; same_sentence; colon; "
                    "semicolon; log mean length; log max length"
                ),
            }
        )

    write_tsv(Path(args.out), rows)


if __name__ == "__main__":
    main()
