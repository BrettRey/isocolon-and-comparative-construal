#!/usr/bin/env python3
"""Fit transparent observed-data baselines for GUM/eRST isocolonicity."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TARGET_DEFINITIONS = {
    "narrow": {"adversative-antithesis", "adversative-contrast"},
    "broad": {
        "adversative-antithesis",
        "adversative-contrast",
        "joint-disjunction",
        "joint-list",
    },
    "joint_list": {"joint-list"},
    "adversative_contrast": {"adversative-contrast"},
    "adversative_antithesis": {"adversative-antithesis"},
    "adversative_concession": {"adversative-concession"},
}

OUTCOMES = ["isocolon_score", "length_score", "syntax_score", "lexical_score"]

WRITTEN_CORE_GENRES = {
    "academic",
    "bio",
    "court",
    "essay",
    "fiction",
    "letter",
    "news",
    "reddit",
    "speech",
    "textbook",
    "voyage",
    "whow",
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


def subset_frames(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "all_adjacent": frame,
        "gum_only": frame[frame["collection"].eq("GUM")],
        "no_dictionary_poetry": frame[~frame["genre"].isin({"dictionary", "poetry"})],
        "same_sentence": frame[frame["same_sentence"].eq(1)],
        "colon_or_semicolon": frame[
            frame["unit1_ends_colon"].eq(1) | frame["unit1_ends_semicolon"].eq(1)
        ],
        "written_core": frame[frame["genre"].isin(WRITTEN_CORE_GENRES)],
    }


def fit_one(
    frame: pd.DataFrame,
    target_name: str,
    outcome: str,
) -> dict[str, object] | None:
    labels = TARGET_DEFINITIONS[target_name]
    target = frame["orig_label"].isin(labels).astype(float).to_numpy()
    target_n = int(target.sum())
    if target_n < 20 or len(frame) - target_n < 20:
        return None

    controls = build_controls(frame)
    q_controls, _ = np.linalg.qr(controls, mode="reduced")
    target_resid = target - q_controls @ (q_controls.T @ target)
    denom = float(target_resid @ target_resid)
    df = len(frame) - q_controls.shape[1] - 1
    if denom <= 1e-8 or df <= 0:
        return None

    y = frame[outcome].astype(float).to_numpy()
    y_resid = y - q_controls @ (q_controls.T @ y)
    estimate = float((target_resid @ y) / denom)
    residuals = y_resid - target_resid * estimate
    sigma2 = float((residuals @ residuals) / df)
    se = float(np.sqrt(sigma2 / denom))
    return {
        "subset": "",
        "outcome": outcome,
        "target": target_name,
        "n_rows": len(frame),
        "n_docs": frame["doc"].nunique(),
        "n_genres": frame["genre"].nunique(),
        "target_n": target_n,
        "target_prevalence": target_n / len(frame),
        "target_mean": float(frame.loc[target.astype(bool), outcome].mean()),
        "other_mean": float(frame.loc[~target.astype(bool), outcome].mean()),
        "raw_difference": float(
            frame.loc[target.astype(bool), outcome].mean()
            - frame.loc[~target.astype(bool), outcome].mean()
        ),
        "adjusted_estimate": estimate,
        "se": se,
        "ci_low": estimate - 1.96 * se,
        "ci_high": estimate + 1.96 * se,
        "df": df,
        "controls": "document fixed effects; explicitness; same_sentence; colon; semicolon; log mean length; log max length",
    }


def fit_all(frame: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for subset_name, subset in subset_frames(frame).items():
        subset = subset.copy()
        for outcome in OUTCOMES:
            for target_name in TARGET_DEFINITIONS:
                result = fit_one(subset, target_name, outcome)
                if result is None:
                    continue
                result["subset"] = subset_name
                rows.append(result)
    return rows


def plot_effects(results: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    subset = results[
        results["outcome"].eq("isocolon_score")
        & results["target"].isin(["broad", "narrow"])
    ].copy()
    subset["label"] = subset["subset"] + " / " + subset["target"]
    subset = subset.sort_values(["target", "subset"])
    y = np.arange(len(subset))

    fig, ax = plt.subplots(figsize=(7.5, max(4.0, 0.35 * len(subset))))
    ax.axvline(0, color="0.55", linewidth=1)
    ax.errorbar(
        subset["adjusted_estimate"],
        y,
        xerr=[
            subset["adjusted_estimate"] - subset["ci_low"],
            subset["ci_high"] - subset["adjusted_estimate"],
        ],
        fmt="o",
        color="black",
        ecolor="0.35",
        capsize=3,
    )
    ax.set_yticks(y)
    ax.set_yticklabels(subset["label"])
    ax.set_xlabel("Adjusted target effect on isocolonicity score")
    ax.grid(axis="x", color="0.9", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out", default="data/derived/observed_isocolon_effects.tsv")
    parser.add_argument("--fig", default="outputs/figures/observed_isocolon_effects.png")
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    rows = fit_all(frame)
    write_tsv(Path(args.out), rows)
    plot_effects(pd.DataFrame(rows), Path(args.fig))


if __name__ == "__main__":
    main()
