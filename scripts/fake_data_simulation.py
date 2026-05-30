#!/usr/bin/env python3
"""Run fake-data recovery checks for the isocolon relation effect."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
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
}


@dataclass
class ResidualizedDesign:
    target: np.ndarray
    target_resid: np.ndarray
    q_controls: np.ndarray
    denom: float
    df: int


def parse_float_list(value: str) -> list[float]:
    return [float(part.strip()) for part in value.split(",") if part.strip()]


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


def residualize_design(frame: pd.DataFrame, target_definition: str) -> ResidualizedDesign:
    if target_definition not in TARGET_DEFINITIONS:
        known = ", ".join(sorted(TARGET_DEFINITIONS))
        raise SystemExit(f"Unknown target definition {target_definition!r}; expected one of {known}")

    controls = build_controls(frame)
    q_controls, _ = np.linalg.qr(controls, mode="reduced")
    target = frame["orig_label"].isin(TARGET_DEFINITIONS[target_definition]).astype(float).to_numpy()
    target_resid = target - q_controls @ (q_controls.T @ target)
    denom = float(target_resid @ target_resid)
    if denom <= 1e-8:
        raise SystemExit(f"Target definition {target_definition!r} is collinear with controls")
    df = len(frame) - q_controls.shape[1] - 1
    return ResidualizedDesign(target, target_resid, q_controls, denom, df)


def make_base(frame: pd.DataFrame) -> np.ndarray:
    same_sentence = frame["same_sentence"].astype(float).to_numpy()
    explicit = frame["rel_type"].eq("explicit").astype(float).to_numpy()
    colon = frame["unit1_ends_colon"].astype(float).to_numpy()
    semicolon = frame["unit1_ends_semicolon"].astype(float).to_numpy()
    mean_len_z = standardize(np.log1p((frame["word_len_1"] + frame["word_len_2"]) / 2))
    max_len_z = standardize(np.log1p(np.maximum(frame["word_len_1"], frame["word_len_2"])))
    base = (
        0.30
        + 0.020 * same_sentence
        + 0.012 * explicit
        + 0.018 * colon
        + 0.028 * semicolon
        + 0.010 * mean_len_z
        - 0.006 * max_len_z
    )
    return base


def simulate_outcomes(
    frame: pd.DataFrame,
    observed_target: np.ndarray,
    true_beta: float,
    label_error: float,
    n_sims: int,
    noise_sd: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = len(frame)
    doc_codes, doc_uniques = pd.factorize(frame["doc"], sort=True)
    genre_codes, genre_uniques = pd.factorize(frame["genre"], sort=True)

    doc_effects = rng.normal(0.0, 0.045, size=(len(doc_uniques), n_sims))[doc_codes]
    genre_effects = rng.normal(0.0, 0.025, size=(len(genre_uniques), n_sims))[genre_codes]
    errors = rng.normal(0.0, noise_sd, size=(n, n_sims))

    observed = observed_target.astype(bool)[:, None]
    if label_error > 0:
        flips = rng.random(size=(n, n_sims)) < label_error
        true_target = np.logical_xor(observed, flips).astype(float)
    else:
        true_target = observed.astype(float)

    y_raw = make_base(frame)[:, None] + doc_effects + genre_effects + true_beta * true_target + errors
    y = np.clip(y_raw, 0.0, 1.0)
    clipped_low = (y_raw < 0.0).mean(axis=0)
    clipped_high = (y_raw > 1.0).mean(axis=0)
    return y, clipped_low, clipped_high


def fit_target_effect(y: np.ndarray, design: ResidualizedDesign) -> tuple[np.ndarray, np.ndarray]:
    y_resid = y - design.q_controls @ (design.q_controls.T @ y)
    estimates = (design.target_resid @ y) / design.denom
    residuals = y_resid - design.target_resid[:, None] * estimates[None, :]
    sigma2 = (residuals * residuals).sum(axis=0) / design.df
    ses = np.sqrt(sigma2 / design.denom)
    return estimates, ses


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def summarize(draws: pd.DataFrame) -> pd.DataFrame:
    grouped = draws.groupby(["target_definition", "label_error", "true_beta"], as_index=False)
    return grouped.agg(
        n_sims=("estimate", "size"),
        mean_estimate=("estimate", "mean"),
        sd_estimate=("estimate", "std"),
        mean_se=("se", "mean"),
        bias=("bias", "mean"),
        rmse=("squared_error", lambda x: float(np.sqrt(np.mean(x)))),
        coverage_95=("covered_95", "mean"),
        power_95=("excludes_zero_95", "mean"),
        sign_rate=("sign_correct", "mean"),
        mean_clipped_low=("clipped_low", "mean"),
        mean_clipped_high=("clipped_high", "mean"),
    )


def plot_power(summary: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    target_defs = list(summary["target_definition"].drop_duplicates())
    fig, axes = plt.subplots(1, len(target_defs), figsize=(5.0 * len(target_defs), 3.6), sharey=True)
    if len(target_defs) == 1:
        axes = [axes]
    for ax, target_definition in zip(axes, target_defs):
        subset = summary[summary["target_definition"] == target_definition]
        for label_error, group in subset.groupby("label_error"):
            group = group.sort_values("true_beta")
            ax.plot(group["true_beta"], group["power_95"], marker="o", label=f"label error {label_error:g}")
        ax.axhline(0.8, color="0.75", linestyle="--", linewidth=1)
        ax.set_title(target_definition)
        ax.set_xlabel("True target effect")
        ax.set_ylim(-0.02, 1.02)
        ax.grid(color="0.9", linewidth=0.8)
    axes[0].set_ylabel("95% interval excludes 0")
    axes[-1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out-dir", default="data/derived")
    parser.add_argument("--fig-dir", default="outputs/figures")
    parser.add_argument("--target-definitions", default="broad,narrow")
    parser.add_argument("--effects", default="0,0.02,0.04,0.06,0.08")
    parser.add_argument("--label-errors", default="0,0.1,0.2")
    parser.add_argument("--n-sims", type=int, default=200)
    parser.add_argument("--noise-sd", type=float, default=0.12)
    parser.add_argument("--seed", type=int, default=20260530)
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    target_definitions = [item.strip() for item in args.target_definitions.split(",") if item.strip()]
    effects = parse_float_list(args.effects)
    label_errors = parse_float_list(args.label_errors)
    rng = np.random.default_rng(args.seed)

    design_rows: list[dict[str, object]] = []
    draw_rows: list[dict[str, object]] = []
    observed_sd = float(frame["isocolon_score"].astype(float).std())
    observed_mean = float(frame["isocolon_score"].astype(float).mean())

    for target_definition in target_definitions:
        design = residualize_design(frame, target_definition)
        target_count = int(design.target.sum())
        design_rows.append(
            {
                "target_definition": target_definition,
                "n_rows": len(frame),
                "n_docs": frame["doc"].nunique(),
                "n_genres": frame["genre"].nunique(),
                "target_count": target_count,
                "target_prevalence": f"{target_count / len(frame):.4f}",
                "observed_isocolon_mean": f"{observed_mean:.4f}",
                "observed_isocolon_sd": f"{observed_sd:.4f}",
                "noise_sd": args.noise_sd,
                "n_sims_per_scenario": args.n_sims,
                "controls": "document fixed effects; explicitness; same_sentence; colon; semicolon; log mean length; log max length",
            }
        )

        for label_error in label_errors:
            for true_beta in effects:
                y, clipped_low, clipped_high = simulate_outcomes(
                    frame,
                    design.target,
                    true_beta,
                    label_error,
                    args.n_sims,
                    args.noise_sd,
                    rng,
                )
                estimates, ses = fit_target_effect(y, design)
                ci_low = estimates - 1.96 * ses
                ci_high = estimates + 1.96 * ses
                for sim_id, estimate in enumerate(estimates, 1):
                    se = float(ses[sim_id - 1])
                    low = float(ci_low[sim_id - 1])
                    high = float(ci_high[sim_id - 1])
                    covered = low <= true_beta <= high
                    excludes_zero = low > 0 or high < 0
                    sign_correct = estimate > 0 if true_beta > 0 else not excludes_zero
                    draw_rows.append(
                        {
                            "target_definition": target_definition,
                            "label_error": label_error,
                            "true_beta": true_beta,
                            "sim_id": sim_id,
                            "estimate": float(estimate),
                            "se": se,
                            "ci_low": low,
                            "ci_high": high,
                            "bias": float(estimate - true_beta),
                            "squared_error": float((estimate - true_beta) ** 2),
                            "covered_95": int(covered),
                            "excludes_zero_95": int(excludes_zero),
                            "sign_correct": int(sign_correct),
                            "clipped_low": float(clipped_low[sim_id - 1]),
                            "clipped_high": float(clipped_high[sim_id - 1]),
                        }
                    )

    out_dir = Path(args.out_dir)
    write_tsv(out_dir / "fake_data_simulation_design.tsv", design_rows)
    write_tsv(out_dir / "fake_data_simulation_draws.tsv", draw_rows)
    summary = summarize(pd.DataFrame(draw_rows))
    summary_path = out_dir / "fake_data_simulation_summary.tsv"
    summary.to_csv(summary_path, sep="\t", index=False)
    plot_power(summary, Path(args.fig_dir) / "fake_data_recovery_power.png")


if __name__ == "__main__":
    main()
