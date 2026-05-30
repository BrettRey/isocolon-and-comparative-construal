#!/usr/bin/env python3
"""Estimate observed isocolonicity effects by genre for target relations."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TARGET_DEFINITIONS = {
    "broad": {
        "adversative-antithesis",
        "adversative-contrast",
        "joint-disjunction",
        "joint-list",
    },
    "narrow": {"adversative-antithesis", "adversative-contrast"},
    "joint_list": {"joint-list"},
    "adversative_contrast": {"adversative-contrast"},
}


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


def fit_target(frame: pd.DataFrame, target_name: str) -> dict[str, object] | None:
    target_labels = TARGET_DEFINITIONS[target_name]
    target = frame["orig_label"].isin(target_labels).astype(float).to_numpy()
    target_n = int(target.sum())
    other_n = len(frame) - target_n
    if target_n < 20 or other_n < 50 or frame["doc"].nunique() < 3:
        return None

    controls = build_controls(frame)
    q_controls, _ = np.linalg.qr(controls, mode="reduced")
    df = len(frame) - q_controls.shape[1] - 1
    if df <= 0:
        return None

    target_resid = target - q_controls @ (q_controls.T @ target)
    denom = float(target_resid @ target_resid)
    if denom <= 1e-8:
        return None

    y = frame["isocolon_score"].astype(float).to_numpy()
    y_resid = y - q_controls @ (q_controls.T @ y)
    estimate = float((target_resid @ y_resid) / denom)
    residuals = y_resid - target_resid * estimate
    sigma2 = float((residuals @ residuals) / df)
    se = float(np.sqrt(sigma2 / denom))
    target_mask = target.astype(bool)
    return {
        "target": target_name,
        "n_rows": len(frame),
        "n_docs": frame["doc"].nunique(),
        "target_n": target_n,
        "target_prevalence": target_n / len(frame),
        "target_mean": float(frame.loc[target_mask, "isocolon_score"].mean()),
        "other_mean": float(frame.loc[~target_mask, "isocolon_score"].mean()),
        "raw_difference": float(
            frame.loc[target_mask, "isocolon_score"].mean()
            - frame.loc[~target_mask, "isocolon_score"].mean()
        ),
        "adjusted_estimate": estimate,
        "se": se,
        "ci_low": estimate - 1.96 * se,
        "ci_high": estimate + 1.96 * se,
        "df": df,
    }


def fit_genres(frame: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for genre, subset in sorted(frame.groupby("genre")):
        for target_name in TARGET_DEFINITIONS:
            result = fit_target(subset.copy(), target_name)
            if result is None:
                continue
            result["genre"] = genre
            rows.append(result)
    return rows


def plot_genres(results: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = results[results["target"].isin(["broad", "narrow"])].copy()
    if data.empty:
        return
    data["label"] = data["genre"] + " / " + data["target"]
    data = data.sort_values(["target", "adjusted_estimate"])
    y = np.arange(len(data))
    colors = np.where(data["target"].eq("broad"), "#2f6f9f", "#9f4f45")

    fig, ax = plt.subplots(figsize=(8.0, max(5.0, 0.33 * len(data))))
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
    ax.set_yticklabels(data["label"])
    ax.set_xlabel("Within-genre adjusted effect on isocolonicity")
    ax.grid(axis="x", color="0.9", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out", default="data/derived/genre_sensitivity_effects.tsv")
    parser.add_argument("--fig", default="outputs/figures/genre_sensitivity_effects.png")
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    rows = fit_genres(frame)
    write_tsv(Path(args.out), rows)
    plot_genres(pd.DataFrame(rows), Path(args.fig))


if __name__ == "__main__":
    main()
