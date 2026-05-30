#!/usr/bin/env python3
"""Fit a single adjusted shrinkage model for eRST relation-label effects."""

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


def relation_groups(labels: pd.Series, min_n: int) -> pd.Series:
    counts = labels.value_counts()
    keep = set(counts[counts >= min_n].index)
    return labels.where(labels.isin(keep), "__rare__")


def residualize(matrix: np.ndarray, q_controls: np.ndarray) -> np.ndarray:
    return matrix - q_controls @ (q_controls.T @ matrix)


def fit_ridge(
    x: np.ndarray,
    y: np.ndarray,
    lambdas: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float, float, float]:
    xtx = x.T @ x
    xty = x.T @ y
    best = None
    for lam in lambdas:
        penalty = lam * np.eye(xtx.shape[0])
        inv = np.linalg.inv(xtx + penalty)
        beta = inv @ xty
        fitted = x @ beta
        residuals = y - fitted
        rss = float(residuals @ residuals)
        df_eff = float(np.trace(xtx @ inv))
        gcv = rss / max((len(y) - df_eff) ** 2, 1e-8)
        if best is None or gcv < best[0]:
            best = (gcv, lam, beta, inv, residuals, df_eff, rss)
    assert best is not None
    _, lam, beta, inv, residuals, df_eff, rss = best
    sigma2 = rss / max(len(y) - df_eff, 1)
    posterior_cov = sigma2 * inv
    return beta, posterior_cov, float(lam), float(df_eff), float(sigma2)


def fit_outcome(
    frame: pd.DataFrame,
    relation_group_col: str,
    outcome: str,
    q_controls: np.ndarray,
    lambdas: np.ndarray,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    relation_matrix = pd.get_dummies(frame[relation_group_col], dtype=float)
    relation_names = relation_matrix.columns.tolist()
    x = residualize(relation_matrix.to_numpy(), q_controls)
    y = frame[outcome].astype(float).to_numpy()
    y_resid = residualize(y[:, None], q_controls).ravel()

    beta, cov, lam, df_eff, sigma2 = fit_ridge(x, y_resid, lambdas)
    se = np.sqrt(np.diag(cov))
    rows = []
    for idx, relation in enumerate(relation_names):
        mask = frame[relation_group_col].eq(relation)
        coarse_mode = frame.loc[mask, "label"].mode()
        rows.append(
            {
                "outcome": outcome,
                "relation_group": relation,
                "coarse_label": coarse_mode.iat[0] if len(coarse_mode) else "",
                "n": int(mask.sum()),
                "raw_mean": float(frame.loc[mask, outcome].mean()),
                "raw_sd": float(frame.loc[mask, outcome].std()),
                "shrunk_adjusted_effect": float(beta[idx]),
                "posterior_se": float(se[idx]),
                "ci_low": float(beta[idx] - 1.96 * se[idx]),
                "ci_high": float(beta[idx] + 1.96 * se[idx]),
                "lambda": lam,
                "effective_df": df_eff,
                "sigma": float(np.sqrt(sigma2)),
            }
        )
    summary = {
        "outcome": outcome,
        "lambda": lam,
        "effective_df": df_eff,
        "sigma": float(np.sqrt(sigma2)),
        "n_relation_groups": len(relation_names),
        "n_rows": len(frame),
    }
    return rows, summary


def plot_effects(results: pd.DataFrame, path: Path, top_n: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = results[results["outcome"].eq("isocolon_score")].copy()
    data = data[~data["relation_group"].eq("__rare__")]
    data = data.reindex(data["shrunk_adjusted_effect"].abs().sort_values(ascending=False).index).head(top_n)
    data = data.sort_values("shrunk_adjusted_effect")
    y = np.arange(len(data))
    colors = np.where(data["shrunk_adjusted_effect"] >= 0, "#2f6f9f", "#9f4f45")

    fig, ax = plt.subplots(figsize=(8, max(5, 0.33 * len(data))))
    ax.axvline(0, color="0.55", linewidth=1)
    ax.errorbar(
        data["shrunk_adjusted_effect"],
        y,
        xerr=[
            data["shrunk_adjusted_effect"] - data["ci_low"],
            data["ci_high"] - data["shrunk_adjusted_effect"],
        ],
        fmt="none",
        ecolor="0.35",
        linewidth=1,
        capsize=2,
    )
    ax.scatter(data["shrunk_adjusted_effect"], y, c=colors, s=28, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(data["relation_group"])
    ax.set_xlabel("Shrunk adjusted relation effect on isocolonicity")
    ax.grid(axis="x", color="0.9", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out", default="data/derived/relation_shrinkage_effects.tsv")
    parser.add_argument("--summary-out", default="data/derived/relation_shrinkage_summary.tsv")
    parser.add_argument("--fig", default="outputs/figures/relation_shrinkage_effects.png")
    parser.add_argument("--min-n", type=int, default=75)
    parser.add_argument("--top-n", type=int, default=35)
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    frame["relation_group"] = relation_groups(frame["orig_label"], args.min_n)
    controls = build_controls(frame)
    q_controls, _ = np.linalg.qr(controls, mode="reduced")
    lambdas = np.logspace(-4, 4, 81)

    rows: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    for outcome in OUTCOMES:
        outcome_rows, summary = fit_outcome(frame, "relation_group", outcome, q_controls, lambdas)
        rows.extend(outcome_rows)
        summaries.append(summary)

    write_tsv(Path(args.out), rows)
    write_tsv(Path(args.summary_out), summaries)
    plot_effects(pd.DataFrame(rows), Path(args.fig), args.top_n)


if __name__ == "__main__":
    main()
