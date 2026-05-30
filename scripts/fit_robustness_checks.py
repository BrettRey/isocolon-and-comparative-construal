#!/usr/bin/env python3
"""Run targeted robustness checks for the formal-balance analysis."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd


OUTCOMES = ["isocolon_score", "length_score", "syntax_score", "lexical_score"]

TARGETS = {
    "broad": {"adversative-antithesis", "adversative-contrast", "joint-disjunction", "joint-list"},
    "narrow": {"adversative-antithesis", "adversative-contrast"},
    "joint_list": {"joint-list"},
    "joint_disjunction": {"joint-disjunction"},
    "adversative_contrast": {"adversative-contrast"},
    "adversative_antithesis": {"adversative-antithesis"},
    "adversative_concession": {"adversative-concession"},
    "restatement_repetition": {"restatement-repetition"},
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


def controls(frame: pd.DataFrame, *, length_controls: str = "mean_max") -> np.ndarray:
    columns = [
        np.ones(len(frame)),
        frame["rel_type"].eq("explicit").astype(float).to_numpy(),
        frame["same_sentence"].astype(float).to_numpy(),
        frame["unit1_ends_colon"].astype(float).to_numpy(),
        frame["unit1_ends_semicolon"].astype(float).to_numpy(),
    ]
    mean_length = standardize(np.log1p((frame["word_len_1"] + frame["word_len_2"]) / 2))
    max_length = standardize(np.log1p(np.maximum(frame["word_len_1"], frame["word_len_2"])))
    if length_controls == "mean_max":
        columns.extend([mean_length, max_length])
    elif length_controls == "mean_only":
        columns.append(mean_length)
    elif length_controls == "none":
        pass
    else:
        raise ValueError(f"Unknown length control mode: {length_controls}")
    numeric = np.column_stack(columns)
    doc_dummies = pd.get_dummies(frame["doc"], drop_first=True, dtype=float).to_numpy()
    return np.column_stack([numeric, doc_dummies])


def fit_residualized(
    frame: pd.DataFrame,
    target: np.ndarray,
    outcome: str,
    *,
    length_controls: str = "mean_max",
) -> dict[str, float] | None:
    target_n = int(target.sum())
    if target_n < 20 or len(target) - target_n < 20:
        return None

    x_controls = controls(frame, length_controls=length_controls)
    q_controls, _ = np.linalg.qr(x_controls, mode="reduced")
    target_resid = target - q_controls @ (q_controls.T @ target)
    denom = float(target_resid @ target_resid)
    df = len(frame) - q_controls.shape[1] - 1
    if denom <= 1e-8 or df <= 0:
        return None

    y = frame[outcome].astype(float).to_numpy()
    y_resid = y - q_controls @ (q_controls.T @ y)
    estimate = float((target_resid @ y_resid) / denom)
    residuals = y_resid - target_resid * estimate
    sigma2 = float((residuals @ residuals) / df)
    se = float(np.sqrt(sigma2 / denom))

    cluster_scores = pd.DataFrame(
        {
            "doc": frame["doc"].to_numpy(),
            "score": target_resid * residuals,
        }
    ).groupby("doc", sort=False)["score"].sum()
    g = len(cluster_scores)
    n = len(frame)
    k = q_controls.shape[1] + 1
    correction = (g / (g - 1)) * ((n - 1) / (n - k)) if g > 1 and n > k else 1.0
    cluster_var = correction * float((cluster_scores.to_numpy() @ cluster_scores.to_numpy()) / (denom**2))
    cluster_se = float(np.sqrt(max(cluster_var, 0.0)))

    return {
        "target_n": target_n,
        "comparison_n": int(len(target) - target_n),
        "estimate": estimate,
        "se": se,
        "ci_low": estimate - 1.96 * se,
        "ci_high": estimate + 1.96 * se,
        "cluster_se": cluster_se,
        "cluster_ci_low": estimate - 1.96 * cluster_se,
        "cluster_ci_high": estimate + 1.96 * cluster_se,
    }


def add_row(
    rows: list[dict[str, object]],
    frame: pd.DataFrame,
    *,
    check: str,
    target_name: str,
    labels: set[str],
    outcome: str,
    length_controls: str,
    note: str,
) -> None:
    target = frame["orig_label"].isin(labels).astype(float).to_numpy()
    result = fit_residualized(
        frame,
        target,
        outcome,
        length_controls=length_controls,
    )
    if result is None:
        return
    rows.append(
        {
            "check": check,
            "target": target_name,
            "outcome": outcome,
            "n_rows": len(frame),
            "n_docs": frame["doc"].nunique(),
            "n_genres": frame["genre"].nunique(),
            "target_n": result["target_n"],
            "comparison_n": result["comparison_n"],
            "estimate": result["estimate"],
            "ci_low": result["ci_low"],
            "ci_high": result["ci_high"],
            "cluster_se": result["cluster_se"],
            "cluster_ci_low": result["cluster_ci_low"],
            "cluster_ci_high": result["cluster_ci_high"],
            "controls": (
                "document fixed effects; explicitness; same_sentence; colon; semicolon"
                + ("; log mean length" if length_controls in {"mean_only", "mean_max"} else "")
                + ("; log max length" if length_controls == "mean_max" else "")
            ),
            "length_controls": length_controls,
            "note": note,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out", default="data/derived/robustness_checks.tsv")
    args = parser.parse_args()

    frame = pd.read_csv(args.input, sep="\t")
    rows: list[dict[str, object]] = []

    for target_name, labels in TARGETS.items():
        for outcome in OUTCOMES:
            add_row(
                rows,
                frame,
                check="document_clustered",
                target_name=target_name,
                labels=labels,
                outcome=outcome,
                length_controls="mean_max",
                note="Same specification as main analysis, with document-clustered uncertainty.",
            )

    for target_name, labels in TARGETS.items():
        add_row(
            rows,
            frame,
            check="length_with_mean_control",
            target_name=target_name,
            labels=labels,
            outcome="length_score",
            length_controls="mean_only",
            note="Length-balance outcome with log mean length but without log max length.",
        )

    for target_name, labels in TARGETS.items():
        add_row(
            rows,
            frame,
            check="length_without_length_controls",
            target_name=target_name,
            labels=labels,
            outcome="length_score",
            length_controls="none",
            note="Length-balance outcome without log mean/max length controls.",
        )

    joint = frame[frame["orig_label"].str.startswith("joint-")].copy()
    for target_name, labels in {
        "joint_list_vs_other_joint": {"joint-list"},
        "joint_disjunction_vs_other_joint": {"joint-disjunction"},
        "joint_list_or_disjunction_vs_other_joint": {"joint-list", "joint-disjunction"},
    }.items():
        for outcome in OUTCOMES:
            add_row(
                rows,
                joint,
                check="coordination_matched",
                target_name=target_name,
                labels=labels,
                outcome=outcome,
                length_controls="mean_max",
                note="Only joint-* relations; comparison rows are other joint relations.",
            )

    adversative = frame[frame["orig_label"].str.startswith("adversative-")].copy()
    for target_name, labels in {
        "adversative_contrast_vs_other_adversative": {"adversative-contrast"},
        "adversative_antithesis_vs_other_adversative": {"adversative-antithesis"},
    }.items():
        for outcome in OUTCOMES:
            add_row(
                rows,
                adversative,
                check="adversative_matched",
                target_name=target_name,
                labels=labels,
                outcome=outcome,
                length_controls="mean_max",
                note="Only adversative relations; comparison rows are other adversative relations.",
            )

    write_tsv(Path(args.out), rows)


if __name__ == "__main__":
    main()
