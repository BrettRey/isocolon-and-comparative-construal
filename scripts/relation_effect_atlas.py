#!/usr/bin/env python3
"""Estimate adjusted isocolonicity effects for each eRST original relation label."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUTCOMES = ["isocolon_score", "length_score", "syntax_score", "lexical_score"]


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
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


def build_controls(frame: pd.DataFrame) -> np.ndarray:
    numeric = np.column_stack(
        [
            np.ones(len(frame)),
            frame["rel_type"].eq("explicit").astype(float).to_numpy(),
            frame["same_sentence"].astype(float).to_numpy(),
            frame["unit1_ends_colon"].astype(float).to_numpy(),
            frame["unit1_ends_semicolon"].astype(float).to_numpy(),
            standardize(np.log1p((frame["word_len_1"] + frame["word_len_2"]) / 2)),
            standardize(np.log1p(np.maximum(frame["word_len_1"], frame["word_len_2"]))),
        ]
    )
    doc_dummies = pd.get_dummies(frame["doc"], drop_first=True, dtype=float).to_numpy()
    return np.column_stack([numeric, doc_dummies])


def residualized_outcomes(frame: pd.DataFrame) -> tuple[np.ndarray, dict[str, np.ndarray], int]:
    controls = build_controls(frame)
    q_controls, _ = np.linalg.qr(controls, mode="reduced")
    y_resids = {}
    for outcome in OUTCOMES:
        y = frame[outcome].astype(float).to_numpy()
        y_resids[outcome] = y - q_controls @ (q_controls.T @ y)
    return q_controls, y_resids, len(frame) - q_controls.shape[1] - 1


def effect_for_label(
    frame: pd.DataFrame,
    q_controls: np.ndarray,
    y_resids: dict[str, np.ndarray],
    label: str,
    outcome: str,
    df: int,
) -> dict[str, object] | None:
    target = frame["orig_label"].eq(label).astype(float).to_numpy()
    target_n = int(target.sum())
    if target_n < 20 or len(frame) - target_n < 20:
        return None
    target_resid = target - q_controls @ (q_controls.T @ target)
    denom = float(target_resid @ target_resid)
    if denom <= 1e-8 or df <= 0:
        return None

    y_resid = y_resids[outcome]
    estimate = float((target_resid @ y_resid) / denom)
    residuals = y_resid - target_resid * estimate
    sigma2 = float((residuals @ residuals) / df)
    se = float(np.sqrt(sigma2 / denom))
    target_mask = target.astype(bool)
    return {
        "outcome": outcome,
        "orig_label": label,
        "coarse_label": frame.loc[target_mask, "label"].mode().iat[0],
        "n_rows": len(frame),
        "target_n": target_n,
        "target_prevalence": target_n / len(frame),
        "target_mean": float(frame.loc[target_mask, outcome].mean()),
        "other_mean": float(frame.loc[~target_mask, outcome].mean()),
        "raw_difference": float(
            frame.loc[target_mask, outcome].mean() - frame.loc[~target_mask, outcome].mean()
        ),
        "adjusted_estimate": estimate,
        "se": se,
        "ci_low": estimate - 1.96 * se,
        "ci_high": estimate + 1.96 * se,
    }


def relation_atlas(frame: pd.DataFrame, min_n: int) -> list[dict[str, object]]:
    q_controls, y_resids, df = residualized_outcomes(frame)
    labels = sorted(
        label
        for label, count in frame["orig_label"].value_counts().items()
        if count >= min_n
    )
    rows: list[dict[str, object]] = []
    for label in labels:
        for outcome in OUTCOMES:
            result = effect_for_label(frame, q_controls, y_resids, label, outcome, df)
            if result is not None:
                rows.append(result)
    return rows


def plot_atlas(results: pd.DataFrame, path: Path, top_n: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = results[results["outcome"].eq("isocolon_score")].copy()
    data = data.reindex(data["adjusted_estimate"].abs().sort_values(ascending=False).index).head(top_n)
    data = data.sort_values("adjusted_estimate")
    y = np.arange(len(data))

    colors = np.where(data["adjusted_estimate"] >= 0, "#2f6f9f", "#9f4f45")
    fig, ax = plt.subplots(figsize=(8.0, max(5.0, 0.32 * len(data))))
    ax.axvline(0, color="0.55", linewidth=1)
    ax.errorbar(
        data["adjusted_estimate"],
        y,
        xerr=[
            data["adjusted_estimate"] - data["ci_low"],
            data["ci_high"] - data["adjusted_estimate"],
        ],
        fmt="none",
        ecolor="0.35",
        linewidth=1,
        capsize=2,
    )
    ax.scatter(data["adjusted_estimate"], y, c=colors, s=28, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(data["orig_label"])
    ax.set_xlabel("Adjusted effect on composite isocolonicity score")
    ax.grid(axis="x", color="0.9", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out", default="data/derived/observed_relation_effect_atlas.tsv")
    parser.add_argument("--fig", default="outputs/figures/observed_relation_effect_atlas.png")
    parser.add_argument("--min-n", type=int, default=75)
    parser.add_argument("--top-n", type=int, default=35)
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    rows = relation_atlas(frame, args.min_n)
    write_tsv(Path(args.out), rows)
    plot_atlas(pd.DataFrame(rows), Path(args.fig), args.top_n)


if __name__ == "__main__":
    main()
