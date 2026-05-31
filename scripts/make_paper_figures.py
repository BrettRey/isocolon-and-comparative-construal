#!/usr/bin/env python3
"""Generate manuscript figures from derived result tables."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


FIG_DIR = Path("outputs/figures")
ROBUSTNESS_PATH = Path("data/derived/robustness_checks.tsv")
NULLS_PATH = Path("data/derived/stratified_nulls.tsv")

TARGET_LABELS = {
    "broad": "Broad family",
    "narrow": "Narrow adversative",
    "joint_list": "joint-list",
    "joint_disjunction": "joint-disjunction",
    "adversative_contrast": "adversative-contrast",
    "adversative_antithesis": "adversative-antithesis",
    "adversative_concession": "adversative-concession",
}

COMPONENT_LABELS = {
    "formal": "Formal balance",
    "isocolon": "Isocolon (length)",
    "parison": "Parison (syntax)",
    "lexical": "Lexical echo",
}

COLORS = {
    "formal": "#111111",
    "isocolon": "#0072B2",
    "parison": "#D55E00",
    "lexical": "#009E73",
}


def setup_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlelocation": "left",
            "figure.dpi": 150,
            "savefig.dpi": 300,
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


def component_rows(robustness: pd.DataFrame) -> pd.DataFrame:
    targets = list(TARGET_LABELS)
    rows: list[dict[str, object]] = []

    for target in targets:
        for component, check, outcome in [
            ("formal", "document_clustered", "isocolon_score"),
            ("isocolon", "length_with_mean_control", "length_score"),
            ("parison", "document_clustered", "syntax_score"),
            ("lexical", "document_clustered", "lexical_score"),
        ]:
            subset = robustness[
                robustness["target"].eq(target)
                & robustness["check"].eq(check)
                & robustness["outcome"].eq(outcome)
            ]
            if subset.empty:
                continue
            row = subset.iloc[0]
            rows.append(
                {
                    "target": target,
                    "target_label": TARGET_LABELS[target],
                    "component": component,
                    "component_label": COMPONENT_LABELS[component],
                    "estimate": 100 * float(row["estimate"]),
                    "low": 100 * float(row["cluster_ci_low"]),
                    "high": 100 * float(row["cluster_ci_high"]),
                }
            )
    return pd.DataFrame(rows)


def plot_component_effects(robustness: pd.DataFrame) -> None:
    frame = component_rows(robustness)
    targets = list(TARGET_LABELS)
    target_positions = {target: i for i, target in enumerate(reversed(targets))}
    offsets = {"formal": 0.27, "isocolon": 0.09, "parison": -0.09, "lexical": -0.27}

    fig, ax = plt.subplots(figsize=(7.1, 4.8))
    ax.axvline(0, color="0.55", linewidth=0.9, zorder=0)

    for component in ["formal", "isocolon", "parison", "lexical"]:
        subset = frame[frame["component"].eq(component)]
        y = subset["target"].map(target_positions).to_numpy(dtype=float) + offsets[component]
        x = subset["estimate"].to_numpy(dtype=float)
        xerr = np.vstack([x - subset["low"].to_numpy(dtype=float), subset["high"].to_numpy(dtype=float) - x])
        ax.errorbar(
            x,
            y,
            xerr=xerr,
            fmt="o",
            markersize=4.2,
            linewidth=1.1,
            capsize=2.5,
            color=COLORS[component],
            ecolor=COLORS[component],
            label=COMPONENT_LABELS[component],
        )
        for point_x, point_y in zip(x, y, strict=True):
            label_offset = 0.18 if point_x >= 0 else -0.18
            ax.text(
                point_x + label_offset,
                point_y,
                f"{point_x:.1f}",
                va="center",
                ha="left" if point_x >= 0 else "right",
                fontsize=7.5,
                color=COLORS[component],
                bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.35, "alpha": 0.82},
            )

    ax.set_yticks([target_positions[target] for target in reversed(targets)])
    ax.set_yticklabels([TARGET_LABELS[target] for target in reversed(targets)])
    ax.set_xlabel("Score-point difference")
    ax.set_xlim(-5.5, 13.5)
    ax.grid(axis="x", color="0.90", linewidth=0.8)
    ax.legend(frameon=False, ncol=2, loc="lower right", handletextpad=0.4, columnspacing=1.0)
    save_figure(fig, "paper_component_effects")


def robustness_rows(robustness: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "Broad, main",
            "document_clustered",
            "broad",
            "isocolon_score",
        ),
        (
            "List/disjunction, within joint",
            "coordination_matched",
            "joint_list_or_disjunction_vs_other_joint",
            "isocolon_score",
        ),
        (
            "Contrast, within adversative",
            "adversative_matched",
            "adversative_contrast_vs_other_adversative",
            "isocolon_score",
        ),
        (
            "Broad length balance",
            "length_with_mean_control",
            "broad",
            "length_score",
        ),
        (
            "Contrast length balance",
            "length_with_mean_control",
            "adversative_contrast",
            "length_score",
        ),
    ]
    rows: list[dict[str, object]] = []
    for label, check, target, outcome in specs:
        subset = robustness[
            robustness["check"].eq(check)
            & robustness["target"].eq(target)
            & robustness["outcome"].eq(outcome)
        ]
        if subset.empty:
            continue
        row = subset.iloc[0]
        rows.append(
            {
                "label": label,
                "estimate": 100 * float(row["estimate"]),
                "low": 100 * float(row["cluster_ci_low"]),
                "high": 100 * float(row["cluster_ci_high"]),
            }
        )
    return pd.DataFrame(rows)


def plot_robustness_and_nulls(robustness: pd.DataFrame, nulls: pd.DataFrame) -> None:
    robust = robustness_rows(robustness)
    null_labels = {
        "broad": "Broad family",
        "list_or_disjunction": "List/disjunction",
        "adversative_contrast": "Contrast",
    }
    nulls = nulls.copy()
    nulls["label"] = nulls["target"].map(null_labels)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.1, 5.2))

    y1 = np.arange(len(robust))[::-1]
    x1 = robust["estimate"].to_numpy(dtype=float)
    xerr1 = np.vstack([x1 - robust["low"].to_numpy(dtype=float), robust["high"].to_numpy(dtype=float) - x1])
    ax1.axvline(0, color="0.55", linewidth=0.9, zorder=0)
    ax1.errorbar(
        x1,
        y1,
        xerr=xerr1,
        fmt="o",
        markersize=4.5,
        color="#111111",
        ecolor="#111111",
        capsize=2.5,
        linewidth=1.1,
    )
    for x, y in zip(x1, y1, strict=True):
        ax1.text(
            x + 0.18,
            y,
            f"{x:.1f}",
            va="center",
            ha="left",
            fontsize=8,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.4, "alpha": 0.85},
        )
    ax1.set_yticks(y1)
    ax1.set_yticklabels(robust["label"])
    ax1.set_xlabel("Score-point difference")
    ax1.set_title("A. Targeted comparisons")
    ax1.set_xlim(-1, 10.7)
    ax1.grid(axis="x", color="0.90", linewidth=0.8)

    y2 = np.arange(len(nulls))[::-1]
    for i, (_, row) in enumerate(nulls.iterrows()):
        y = y2[i]
        ax2.plot(
            [100 * row["null_q025"], 100 * row["null_q975"]],
            [y, y],
            color="0.55",
            linewidth=4.5,
            solid_capstyle="butt",
            label="Null 95% interval" if i == 0 else None,
        )
        ax2.plot(
            100 * row["null_mean"],
            y,
            marker="|",
            markersize=11,
            color="0.25",
            label="Null mean" if i == 0 else None,
        )
        ax2.plot(
            100 * row["observed_estimate"],
            y,
            marker="o",
            markersize=4.8,
            color="#111111",
            label="Observed" if i == 0 else None,
        )
        ax2.text(
            100 * row["observed_estimate"] + 0.08,
            y,
            f"{100 * row['observed_estimate']:.1f}",
            va="center",
            ha="left",
            fontsize=8,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.4, "alpha": 0.85},
        )
    ax2.axvline(0, color="0.80", linewidth=0.8, zorder=0)
    ax2.set_yticks(y2)
    ax2.set_yticklabels(nulls["label"])
    ax2.set_xlabel("Composite score-point difference")
    ax2.set_title("B. Stratified permutation nulls")
    ax2.set_xlim(-0.5, 5.8)
    ax2.grid(axis="x", color="0.90", linewidth=0.8)
    ax2.legend(
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.24),
        ncol=3,
        fontsize=8,
        handlelength=1.8,
    )

    fig.tight_layout(h_pad=1.6)
    save_figure(fig, "paper_robustness_nulls")


def main() -> None:
    setup_matplotlib()
    robustness = pd.read_csv(ROBUSTNESS_PATH, sep="\t")
    nulls = pd.read_csv(NULLS_PATH, sep="\t")
    plot_component_effects(robustness)
    plot_robustness_and_nulls(robustness, nulls)


if __name__ == "__main__":
    main()
