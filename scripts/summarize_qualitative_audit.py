#!/usr/bin/env python3
"""Validate and summarize qualitative audit agent ratings."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import pandas as pd


AGENTS = ["codex_1", "codex_2", "opus_1", "opus_2"]
EXPECTED_COLUMNS = [
    "audit_id",
    "agent",
    "is_isocolonic",
    "formal_parallelism",
    "rhetorically_relevant",
    "genuine_comparison_or_coordination",
    "false_positive_flags",
    "bad_segmentation",
    "confidence",
    "short_reason",
]
BOOLEAN_VALUES = {"yes", "no", "uncertain"}
PARALLELISM_VALUES = {"none", "weak", "moderate", "strong"}


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def validate_agent(path: Path, agent: str, expected_ids: list[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path, sep="\t")
    if list(frame.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"{path} has unexpected columns: {list(frame.columns)}")
    if frame["audit_id"].tolist() != expected_ids:
        raise ValueError(f"{path} audit_id order mismatch")
    if set(frame["agent"]) != {agent}:
        raise ValueError(f"{path} has agent values {sorted(frame['agent'].unique())}")
    for column in [
        "is_isocolonic",
        "rhetorically_relevant",
        "genuine_comparison_or_coordination",
        "bad_segmentation",
    ]:
        values = set(frame[column].dropna())
        if not values <= BOOLEAN_VALUES:
            raise ValueError(f"{path} has invalid {column} values {sorted(values)}")
    if not set(frame["formal_parallelism"].dropna()) <= PARALLELISM_VALUES:
        raise ValueError(f"{path} has invalid formal_parallelism values")
    confidence = frame["confidence"].astype(float)
    if not ((confidence >= 0) & (confidence <= 1)).all():
        raise ValueError(f"{path} confidence outside [0,1]")
    return frame


def majority(values: list[str]) -> tuple[str, int]:
    counts = Counter(values)
    top_count = max(counts.values())
    top_values = sorted([value for value, count in counts.items() if count == top_count])
    return "/".join(top_values), top_count


def flag_counter(values: pd.Series) -> Counter[str]:
    counts: Counter[str] = Counter()
    aliases = {
        "exact_repetition": "repetition",
        "template": "template_or_quote",
        "quote": "template_or_quote",
    }
    for value in values.fillna("none"):
        for flag in str(value).split(";"):
            flag = flag.strip()
            flag = aliases.get(flag, flag)
            if flag and flag not in {"none", "bad_segmentation"}:
                counts[flag] += 1
    return counts


def summarize(
    sample: pd.DataFrame,
    ratings: pd.DataFrame,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    agent_rows: list[dict[str, object]] = []
    for agent, group in ratings.groupby("agent"):
        flags = flag_counter(group["false_positive_flags"])
        bad_seg = int(group["bad_segmentation"].eq("yes").sum())
        if bad_seg:
            flags["bad_segmentation"] = bad_seg
        counts = group["is_isocolonic"].value_counts().reindex(["yes", "no", "uncertain"], fill_value=0)
        agent_rows.append(
            {
                "agent": agent,
                "n_rows": len(group),
                "yes": int(counts["yes"]),
                "no": int(counts["no"]),
                "uncertain": int(counts["uncertain"]),
                "mean_confidence": float(group["confidence"].astype(float).mean()),
                "top_failure_modes": "; ".join(f"{k}:{v}" for k, v in flags.most_common(6)),
            }
        )

    consensus_rows: list[dict[str, object]] = []
    for audit_id, group in ratings.groupby("audit_id", sort=False):
        yes_votes = int(group["is_isocolonic"].eq("yes").sum())
        no_votes = int(group["is_isocolonic"].eq("no").sum())
        uncertain_votes = int(group["is_isocolonic"].eq("uncertain").sum())
        maj, maj_n = majority(group["is_isocolonic"].tolist())
        parallelism, parallelism_n = majority(group["formal_parallelism"].tolist())
        rhet, rhet_n = majority(group["rhetorically_relevant"].tolist())
        coord, coord_n = majority(group["genuine_comparison_or_coordination"].tolist())
        bad, bad_n = majority(group["bad_segmentation"].tolist())
        flags = flag_counter(group["false_positive_flags"])
        source = sample[sample["audit_id"].eq(audit_id)].iloc[0]
        consensus_rows.append(
            {
                "audit_id": audit_id,
                "stratum": source["stratum"],
                "genre": source["genre"],
                "orig_label": source["orig_label"],
                "isocolon_score": source["isocolon_score"],
                "unit1_text": source["unit1_text"],
                "unit2_text": source["unit2_text"],
                "yes_votes": yes_votes,
                "no_votes": no_votes,
                "uncertain_votes": uncertain_votes,
                "majority_is_isocolonic": maj,
                "majority_votes": maj_n,
                "majority_formal_parallelism": parallelism,
                "parallelism_votes": parallelism_n,
                "majority_rhetorically_relevant": rhet,
                "rhetorically_relevant_votes": rhet_n,
                "majority_comparison_or_coordination": coord,
                "comparison_or_coordination_votes": coord_n,
                "majority_bad_segmentation": bad,
                "bad_segmentation_votes": bad_n,
                "top_false_positive_flags": "; ".join(f"{k}:{v}" for k, v in flags.most_common()),
            }
        )

    stratum_rows: list[dict[str, object]] = []
    consensus = pd.DataFrame(consensus_rows)
    for stratum, group in consensus.groupby("stratum", sort=False):
        stratum_rows.append(
            {
                "stratum": stratum,
                "n_rows": len(group),
                "majority_yes": int(group["majority_is_isocolonic"].eq("yes").sum()),
                "majority_no": int(group["majority_is_isocolonic"].eq("no").sum()),
                "majority_uncertain": int(group["majority_is_isocolonic"].eq("uncertain").sum()),
                "split_or_tied": int(group["majority_is_isocolonic"].str.contains("/").sum()),
                "mean_yes_votes": float(group["yes_votes"].mean()),
                "mean_no_votes": float(group["no_votes"].mean()),
                "mean_uncertain_votes": float(group["uncertain_votes"].mean()),
            }
        )
    return agent_rows, consensus_rows, stratum_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", default="outputs/audit/isocolon_qualitative_audit_40.tsv")
    parser.add_argument("--review-dir", default="outputs/audit/agent_reviews")
    parser.add_argument("--ratings-out", default="outputs/audit/agent_reviews/all_agent_ratings.tsv")
    parser.add_argument("--agent-summary-out", default="outputs/audit/agent_reviews/agent_rating_summary.tsv")
    parser.add_argument("--consensus-out", default="outputs/audit/agent_reviews/audit_consensus.tsv")
    parser.add_argument("--stratum-summary-out", default="outputs/audit/agent_reviews/audit_stratum_summary.tsv")
    args = parser.parse_args()

    sample = pd.read_csv(args.sample, sep="\t")
    expected_ids = sample["audit_id"].tolist()
    frames = []
    for agent in AGENTS:
        frames.append(validate_agent(Path(args.review_dir) / f"{agent}_audit.tsv", agent, expected_ids))
    ratings = pd.concat(frames, ignore_index=True)
    ratings.to_csv(args.ratings_out, sep="\t", index=False)

    agent_rows, consensus_rows, stratum_rows = summarize(sample, ratings)
    write_tsv(Path(args.agent_summary_out), agent_rows)
    write_tsv(Path(args.consensus_out), consensus_rows)
    write_tsv(Path(args.stratum_summary_out), stratum_rows)


if __name__ == "__main__":
    main()
