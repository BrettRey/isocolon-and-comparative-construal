#!/usr/bin/env python3
"""Empirical-Bayes shrinkage for genre-varying target effects."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def normal_cdf(value: float, mean: float = 0.0, sd: float = 1.0) -> float:
    if sd <= 0:
        return float(value >= mean)
    z = (value - mean) / (sd * math.sqrt(2))
    return 0.5 * (1 + math.erf(z))


def marginal_loglik(beta: np.ndarray, se: np.ndarray, tau: float) -> tuple[float, float]:
    variance = se * se + tau * tau
    weights = 1 / variance
    mu = float(np.sum(weights * beta) / np.sum(weights))
    loglik = float(-0.5 * np.sum(np.log(variance) + ((beta - mu) ** 2) / variance))
    return loglik, mu


def fit_eb(group: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    beta = group["adjusted_estimate"].to_numpy(dtype=float)
    se = group["se"].to_numpy(dtype=float)
    tau_grid = np.r_[0.0, np.logspace(-4, -0.6, 300)]
    best_loglik = -np.inf
    best_tau = 0.0
    best_mu = 0.0
    for tau in tau_grid:
        loglik, mu = marginal_loglik(beta, se, float(tau))
        if loglik > best_loglik:
            best_loglik = loglik
            best_tau = float(tau)
            best_mu = mu

    if best_tau <= 1e-12:
        posterior_mean = np.repeat(best_mu, len(group))
        posterior_sd = np.zeros(len(group))
        shrinkage_weight = np.zeros(len(group))
    else:
        prior_precision = 1 / (best_tau * best_tau)
        likelihood_precision = 1 / (se * se)
        posterior_var = 1 / (likelihood_precision + prior_precision)
        posterior_mean = posterior_var * (beta * likelihood_precision + best_mu * prior_precision)
        posterior_sd = np.sqrt(posterior_var)
        shrinkage_weight = posterior_var * likelihood_precision

    out = group.copy()
    out["eb_mu"] = best_mu
    out["eb_tau"] = best_tau
    out["shrunk_estimate"] = posterior_mean
    out["posterior_sd"] = posterior_sd
    out["shrunk_ci_low"] = posterior_mean - 1.96 * posterior_sd
    out["shrunk_ci_high"] = posterior_mean + 1.96 * posterior_sd
    out["prob_positive"] = [1 - normal_cdf(0, mean, sd) for mean, sd in zip(posterior_mean, posterior_sd)]
    out["shrinkage_weight_on_observed"] = shrinkage_weight

    summary = {
        "target": group["target"].iat[0],
        "n_genres": len(group),
        "eb_mu": best_mu,
        "eb_tau": best_tau,
        "marginal_loglik": best_loglik,
        "mean_observed_effect": float(beta.mean()),
        "sd_observed_effect": float(beta.std(ddof=1)) if len(beta) > 1 else 0.0,
        "min_observed_effect": float(beta.min()),
        "max_observed_effect": float(beta.max()),
    }
    return out, summary


def plot_effects(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plot_targets = [target for target in ["broad", "narrow"] if target in set(frame["target"])]
    if not plot_targets:
        return
    fig, axes = plt.subplots(
        1,
        len(plot_targets),
        figsize=(6.5 * len(plot_targets), 6.0),
        sharex=True,
    )
    if len(plot_targets) == 1:
        axes = [axes]
    for ax, target in zip(axes, plot_targets):
        subset = frame[frame["target"].eq(target)].copy()
        subset = subset.sort_values("shrunk_estimate")
        y = np.arange(len(subset))
        ax.axvline(0, color="0.55", linewidth=1)
        ax.errorbar(
            subset["adjusted_estimate"],
            y + 0.12,
            xerr=[
                subset["adjusted_estimate"] - subset["ci_low"],
                subset["ci_high"] - subset["adjusted_estimate"],
            ],
            fmt="o",
            color="0.65",
            ecolor="0.75",
            capsize=2,
            label="observed",
            markersize=4,
        )
        ax.errorbar(
            subset["shrunk_estimate"],
            y - 0.12,
            xerr=[
                subset["shrunk_estimate"] - subset["shrunk_ci_low"],
                subset["shrunk_ci_high"] - subset["shrunk_estimate"],
            ],
            fmt="o",
            color="#2f6f9f",
            ecolor="#2f6f9f",
            capsize=2,
            label="shrunk",
            markersize=4,
        )
        ax.set_yticks(y)
        ax.set_yticklabels(subset["genre"])
        ax.set_title(target)
        ax.set_xlabel("Genre-specific target effect")
        ax.grid(axis="x", color="0.9", linewidth=0.8)
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/genre_sensitivity_effects.tsv")
    parser.add_argument("--out", default="data/derived/genre_varying_effects.tsv")
    parser.add_argument("--summary-out", default="data/derived/genre_varying_summary.tsv")
    parser.add_argument("--fig", default="outputs/figures/genre_varying_effects.png")
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    rows: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    for _, group in frame.groupby("target"):
        fitted, summary = fit_eb(group)
        rows.extend(fitted.to_dict(orient="records"))
        summaries.append(summary)
    write_tsv(Path(args.out), rows)
    write_tsv(Path(args.summary_out), summaries)
    plot_effects(pd.DataFrame(rows), Path(args.fig))


if __name__ == "__main__":
    main()
