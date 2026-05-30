#!/usr/bin/env python3
"""Sensitivity of observed effects to isocolon-score component weights."""

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
}

COMPONENTS = ["length_score", "syntax_score", "lexical_score"]

NAMED_WEIGHTS = {
    "current": (0.40, 0.45, 0.15),
    "equal": (1 / 3, 1 / 3, 1 / 3),
    "length_only": (1.0, 0.0, 0.0),
    "syntax_only": (0.0, 1.0, 0.0),
    "lexical_only": (0.0, 0.0, 1.0),
    "length_syntax": (0.5, 0.5, 0.0),
    "syntax_lexical": (0.0, 0.5, 0.5),
    "length_lexical": (0.5, 0.0, 0.5),
    "length_heavy": (0.65, 0.25, 0.10),
    "syntax_heavy": (0.20, 0.65, 0.15),
    "lexical_heavy": (0.25, 0.30, 0.45),
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


def weight_grid(step: float) -> dict[str, tuple[float, float, float]]:
    n_steps = round(1 / step)
    weights: dict[str, tuple[float, float, float]] = {}
    for length_i in range(n_steps + 1):
        for syntax_i in range(n_steps - length_i + 1):
            lexical_i = n_steps - length_i - syntax_i
            length = length_i / n_steps
            syntax = syntax_i / n_steps
            lexical = lexical_i / n_steps
            name = f"grid_l{length:.1f}_s{syntax:.1f}_x{lexical:.1f}"
            weights[name] = (length, syntax, lexical)
    return weights


def fit_target(
    frame: pd.DataFrame,
    target_name: str,
    weights: dict[str, tuple[float, float, float]],
) -> list[dict[str, object]]:
    labels = TARGET_DEFINITIONS[target_name]
    target = frame["orig_label"].isin(labels).astype(float).to_numpy()
    target_n = int(target.sum())
    if target_n < 20 or len(frame) - target_n < 20:
        return []

    controls = build_controls(frame)
    q_controls, _ = np.linalg.qr(controls, mode="reduced")
    target_resid = target - q_controls @ (q_controls.T @ target)
    denom = float(target_resid @ target_resid)
    df = len(frame) - q_controls.shape[1] - 1
    if denom <= 1e-8 or df <= 0:
        return []

    component_values = frame[COMPONENTS].astype(float).to_numpy()
    component_effects = {}
    component_ses = {}
    for index, component in enumerate(COMPONENTS):
        y = component_values[:, index]
        y_resid = y - q_controls @ (q_controls.T @ y)
        estimate = float((target_resid @ y) / denom)
        residuals = y_resid - target_resid * estimate
        sigma2 = float((residuals @ residuals) / df)
        component_effects[component] = estimate
        component_ses[component] = float(np.sqrt(sigma2 / denom))

    rows: list[dict[str, object]] = []
    for name, (length_w, syntax_w, lexical_w) in weights.items():
        y = component_values @ np.array([length_w, syntax_w, lexical_w])
        y_resid = y - q_controls @ (q_controls.T @ y)
        estimate = float((target_resid @ y) / denom)
        residuals = y_resid - target_resid * estimate
        sigma2 = float((residuals @ residuals) / df)
        se = float(np.sqrt(sigma2 / denom))
        rows.append(
            {
                "target": target_name,
                "weight_spec": name,
                "weight_family": "named" if name in NAMED_WEIGHTS else "grid",
                "length_weight": length_w,
                "syntax_weight": syntax_w,
                "lexical_weight": lexical_w,
                "n_rows": len(frame),
                "n_docs": frame["doc"].nunique(),
                "n_genres": frame["genre"].nunique(),
                "target_n": target_n,
                "target_prevalence": target_n / len(frame),
                "adjusted_estimate": estimate,
                "se": se,
                "ci_low": estimate - 1.96 * se,
                "ci_high": estimate + 1.96 * se,
                "df": df,
                "length_component_effect": component_effects["length_score"],
                "syntax_component_effect": component_effects["syntax_score"],
                "lexical_component_effect": component_effects["lexical_score"],
                "controls": "document fixed effects; explicitness; same_sentence; colon; semicolon; log mean length; log max length",
            }
        )
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    frame = pd.DataFrame(rows)
    summaries: list[dict[str, object]] = []
    for (target, family), group in frame.groupby(["target", "weight_family"]):
        estimates = group["adjusted_estimate"].astype(float)
        summaries.append(
            {
                "target": target,
                "weight_family": family,
                "n_weight_specs": len(group),
                "min_estimate": float(estimates.min()),
                "p10_estimate": float(estimates.quantile(0.10)),
                "median_estimate": float(estimates.median()),
                "p90_estimate": float(estimates.quantile(0.90)),
                "max_estimate": float(estimates.max()),
                "share_positive": float((estimates > 0).mean()),
                "share_ci_excludes_zero_positive": float((group["ci_low"].astype(float) > 0).mean()),
                "length_component_effect": float(group["length_component_effect"].iat[0]),
                "syntax_component_effect": float(group["syntax_component_effect"].iat[0]),
                "lexical_component_effect": float(group["lexical_component_effect"].iat[0]),
            }
        )
    return summaries


def plot_sensitivity(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame = frame[
        frame["target"].isin(["broad", "narrow"])
        & frame["weight_family"].eq("grid")
    ].copy()

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8), sharey=True, constrained_layout=True)
    for ax, target in zip(axes, ["broad", "narrow"]):
        subset = frame[frame["target"].eq(target)]
        scatter = ax.scatter(
            subset["syntax_weight"],
            subset["adjusted_estimate"],
            c=subset["length_weight"],
            s=34,
            cmap="viridis",
            edgecolor="none",
            alpha=0.85,
        )
        ax.axhline(0, color="0.55", linewidth=1)
        current = pd.DataFrame(rows)
        current = current[
            current["target"].eq(target)
            & current["weight_spec"].eq("current")
        ]
        if not current.empty:
            ax.scatter(
                current["syntax_weight"],
                current["adjusted_estimate"],
                marker="D",
                s=54,
                color="black",
                label="current",
                zorder=3,
            )
        ax.set_title(target)
        ax.set_xlabel("Syntax weight")
        ax.grid(color="0.9", linewidth=0.8)
    axes[0].set_ylabel("Adjusted target effect")
    axes[1].legend(frameon=False, fontsize=8)
    cbar = fig.colorbar(scatter, ax=axes, shrink=0.82)
    cbar.set_label("Length weight")
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--grid-step", type=float, default=0.1)
    parser.add_argument("--out", default="data/derived/score_weight_sensitivity.tsv")
    parser.add_argument("--summary-out", default="data/derived/score_weight_sensitivity_summary.tsv")
    parser.add_argument("--fig", default="outputs/figures/score_weight_sensitivity.png")
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    weights = {**NAMED_WEIGHTS, **weight_grid(args.grid_step)}
    rows: list[dict[str, object]] = []
    for target_name in TARGET_DEFINITIONS:
        rows.extend(fit_target(frame, target_name, weights))
    write_tsv(Path(args.out), rows)
    write_tsv(Path(args.summary_out), summarize(rows))
    plot_sensitivity(rows, Path(args.fig))


if __name__ == "__main__":
    main()
