#!/usr/bin/env python3
"""Validate the computed isocolonicity score against gold eRST syn-prl signals."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCORE_COLUMNS = [
    "isocolon_score",
    "length_score",
    "syntax_score",
    "lexical_score",
    "word_token_balance",
    "char_balance",
    "syllable_balance",
    "upos_similarity",
    "xpos_similarity",
    "deprel_similarity",
]


def auc_from_scores(labels: np.ndarray, scores: np.ndarray) -> float:
    positives = labels == 1
    n_pos = int(positives.sum())
    n_neg = int((~positives).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    order = np.argsort(scores)
    ranks = np.empty(len(scores), dtype=float)
    ranks[order] = np.arange(1, len(scores) + 1)

    sorted_scores = scores[order]
    start = 0
    while start < len(scores):
        end = start + 1
        while end < len(scores) and sorted_scores[end] == sorted_scores[start]:
            end += 1
        if end - start > 1:
            ranks[order[start:end]] = ranks[order[start:end]].mean()
        start = end

    rank_sum_pos = float(ranks[positives].sum())
    return (rank_sum_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def score_summary(frame: pd.DataFrame) -> list[dict[str, object]]:
    labels = frame["has_gold_syn_prl"].astype(int).to_numpy()
    rows = []
    for score_col in SCORE_COLUMNS:
        scores = frame[score_col].astype(float).to_numpy()
        pos = frame.loc[frame["has_gold_syn_prl"].eq(1), score_col].astype(float)
        neg = frame.loc[frame["has_gold_syn_prl"].eq(0), score_col].astype(float)
        rows.append(
            {
                "score": score_col,
                "n": len(frame),
                "gold_syn_prl_n": int(labels.sum()),
                "gold_syn_prl_prevalence": float(labels.mean()),
                "auc": auc_from_scores(labels, scores),
                "mean_gold": float(pos.mean()),
                "mean_non_gold": float(neg.mean()),
                "mean_difference": float(pos.mean() - neg.mean()),
                "median_gold": float(pos.median()),
                "median_non_gold": float(neg.median()),
            }
        )
    return rows


def threshold_summary(frame: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    n_gold = int(frame["has_gold_syn_prl"].sum())
    for percentile in [50, 60, 70, 80, 85, 90, 95, 97.5, 99]:
        threshold = float(frame["isocolon_score"].quantile(percentile / 100))
        selected = frame[frame["isocolon_score"].ge(threshold)]
        selected_gold = int(selected["has_gold_syn_prl"].sum())
        rows.append(
            {
                "percentile": percentile,
                "threshold": threshold,
                "selected_n": len(selected),
                "selected_gold_syn_prl_n": selected_gold,
                "precision": selected_gold / len(selected) if len(selected) else 0.0,
                "recall": selected_gold / n_gold if n_gold else 0.0,
                "lift_over_base_rate": (selected_gold / len(selected)) / (n_gold / len(frame))
                if len(selected) and n_gold
                else 0.0,
            }
        )
    return rows


def example_rows(frame: pd.DataFrame, per_group: int) -> list[dict[str, object]]:
    groups = {
        "top_gold_syn_prl": frame[frame["has_gold_syn_prl"].eq(1)].sort_values(
            "isocolon_score", ascending=False
        ),
        "top_non_gold": frame[frame["has_gold_syn_prl"].eq(0)].sort_values(
            "isocolon_score", ascending=False
        ),
        "low_gold_syn_prl": frame[frame["has_gold_syn_prl"].eq(1)].sort_values(
            "isocolon_score", ascending=True
        ),
        "top_project_labels": frame[
            frame["orig_label"].isin(
                [
                    "joint-list",
                    "joint-disjunction",
                    "adversative-contrast",
                    "adversative-antithesis",
                    "adversative-concession",
                ]
            )
        ].sort_values("isocolon_score", ascending=False),
    }
    keep_cols = [
        "doc",
        "genre",
        "label",
        "orig_label",
        "rel_type",
        "isocolon_score",
        "length_score",
        "syntax_score",
        "lexical_score",
        "has_gold_syn_prl",
        "unit1_text",
        "unit2_text",
    ]
    rows: list[dict[str, object]] = []
    for group_name, subset in groups.items():
        for rank, (_, row) in enumerate(subset.head(per_group).iterrows(), 1):
            record = {"example_group": group_name, "rank": rank}
            record.update({col: row[col] for col in keep_cols})
            rows.append(record)
    return rows


def plot_validation(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    gold = frame[frame["has_gold_syn_prl"].eq(1)]["isocolon_score"].astype(float)
    non_gold = frame[frame["has_gold_syn_prl"].eq(0)]["isocolon_score"].astype(float)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    bins = np.linspace(0, 1, 41)
    axes[0].hist(non_gold, bins=bins, density=True, alpha=0.55, label="no gold syn-prl")
    axes[0].hist(gold, bins=bins, density=True, alpha=0.65, label="gold syn-prl")
    axes[0].set_xlabel("Composite isocolonicity score")
    axes[0].set_ylabel("Density")
    axes[0].legend(frameon=False, fontsize=8)
    axes[0].grid(color="0.9", linewidth=0.8)

    threshold_rows = pd.DataFrame(threshold_summary(frame))
    axes[1].plot(threshold_rows["percentile"], threshold_rows["precision"], marker="o", label="precision")
    axes[1].plot(threshold_rows["percentile"], threshold_rows["recall"], marker="o", label="recall")
    axes[1].set_xlabel("Score percentile threshold")
    axes[1].set_ylabel("Gold syn-prl rate")
    axes[1].set_ylim(-0.02, 1.02)
    axes[1].legend(frameon=False, fontsize=8)
    axes[1].grid(color="0.9", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out-dir", default="data/derived")
    parser.add_argument("--fig", default="outputs/figures/isocolon_score_validation.png")
    parser.add_argument("--examples-per-group", type=int, default=20)
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    out_dir = Path(args.out_dir)
    write_tsv(out_dir / "isocolon_score_validation_summary.tsv", score_summary(frame))
    write_tsv(out_dir / "isocolon_score_thresholds.tsv", threshold_summary(frame))
    write_tsv(
        out_dir / "isocolon_score_validation_examples.tsv",
        example_rows(frame, args.examples_per_group),
    )
    plot_validation(frame, Path(args.fig))


if __name__ == "__main__":
    main()
