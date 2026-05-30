#!/usr/bin/env python3
"""Validate and summarize available agent ratings for qualitative audit batch 3."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import pandas as pd


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
DEFAULT_AGENTS = [
    "codex_batch3_1",
    "codex_batch3_2",
    "opus_batch3_1",
    "opus_batch3_2",
]


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        if not rows:
            handle.write("")
            return
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def validate_agent(path: Path, agent: str, expected_ids: list[str]) -> pd.DataFrame:
    frame = pd.read_csv(path, sep="\t")
    if list(frame.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"{path} has unexpected columns {list(frame.columns)}")
    if frame["audit_id"].tolist() != expected_ids:
        raise ValueError(f"{path} audit_id order does not match batch 3 sample")
    if set(frame["agent"]) != {agent}:
        raise ValueError(f"{path} has unexpected agent values {sorted(frame['agent'].unique())}")
    for column in [
        "is_isocolonic",
        "rhetorically_relevant",
        "genuine_comparison_or_coordination",
        "bad_segmentation",
    ]:
        values = set(frame[column].dropna())
        if not values <= BOOLEAN_VALUES:
            raise ValueError(f"{path} has invalid {column} values {sorted(values)}")
    values = set(frame["formal_parallelism"].dropna())
    if not values <= PARALLELISM_VALUES:
        raise ValueError(f"{path} has invalid formal_parallelism values {sorted(values)}")
    confidence = frame["confidence"].astype(float)
    if not ((confidence >= 0) & (confidence <= 1)).all():
        raise ValueError(f"{path} confidence outside [0,1]")
    return frame


def majority(values: list[str]) -> tuple[str, int]:
    counts = Counter(values)
    top_n = max(counts.values())
    top = sorted(value for value, count in counts.items() if count == top_n)
    return "/".join(top), top_n


def summarize_agents(ratings: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for agent, group in ratings.groupby("agent", sort=False):
        counts = group["is_isocolonic"].value_counts().reindex(["yes", "no", "uncertain"], fill_value=0)
        rows.append(
            {
                "agent": agent,
                "n_rows": len(group),
                "yes": int(counts["yes"]),
                "no": int(counts["no"]),
                "uncertain": int(counts["uncertain"]),
                "mean_confidence": round(float(group["confidence"].astype(float).mean()), 4),
            }
        )
    return rows


def summarize_rows(sample: pd.DataFrame, ratings: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for audit_id, group in ratings.groupby("audit_id", sort=False):
        labels = group["is_isocolonic"].tolist()
        maj, maj_n = majority(labels)
        counts = Counter(labels)
        source = sample[sample["audit_id"].eq(audit_id)].iloc[0]
        rows.append(
            {
                "audit_id": audit_id,
                "stratum": source["stratum"],
                "genre": source["genre"],
                "orig_label": source["orig_label"],
                "isocolon_score": source["isocolon_score"],
                "unit1_text": source["unit1_text"],
                "unit2_text": source["unit2_text"],
                "agent_yes": counts["yes"],
                "agent_no": counts["no"],
                "agent_uncertain": counts["uncertain"],
                "agent_majority": maj,
                "agent_majority_n": maj_n,
                "agent_codes": "; ".join(
                    f"{row.agent}:{row.is_isocolonic}"
                    for row in group[["agent", "is_isocolonic"]].itertuples(index=False)
                ),
            }
        )
    return rows


def summarize_strata(row_summary: list[dict[str, object]]) -> list[dict[str, object]]:
    frame = pd.DataFrame(row_summary)
    rows: list[dict[str, object]] = []
    for stratum, group in frame.groupby("stratum", sort=False):
        rows.append(
            {
                "stratum": stratum,
                "n_rows": len(group),
                "majority_yes": int(group["agent_majority"].eq("yes").sum()),
                "majority_no": int(group["agent_majority"].eq("no").sum()),
                "majority_uncertain": int(group["agent_majority"].eq("uncertain").sum()),
                "split_or_tied": int(group["agent_majority"].str.contains("/").sum()),
                "mean_agent_yes_votes": round(float(group["agent_yes"].mean()), 4),
                "mean_agent_no_votes": round(float(group["agent_no"].mean()), 4),
                "mean_agent_uncertain_votes": round(float(group["agent_uncertain"].mean()), 4),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", default="outputs/audit/isocolon_qualitative_audit_batch3_40.csv")
    parser.add_argument("--review-dir", default="outputs/audit/agent_reviews")
    parser.add_argument("--agents", nargs="*", default=DEFAULT_AGENTS)
    parser.add_argument("--agent-summary-out", default="outputs/audit/agent_reviews/batch3_agent_summary.tsv")
    parser.add_argument("--row-summary-out", default="outputs/audit/agent_reviews/batch3_agent_consensus.tsv")
    parser.add_argument("--stratum-summary-out", default="outputs/audit/agent_reviews/batch3_agent_stratum_summary.tsv")
    args = parser.parse_args()

    sample = pd.read_csv(args.sample)
    expected_ids = sample["audit_id"].tolist()
    frames: list[pd.DataFrame] = []
    missing: list[str] = []
    for agent in args.agents:
        path = Path(args.review_dir) / f"{agent}.tsv"
        if not path.exists():
            missing.append(agent)
            continue
        frames.append(validate_agent(path, agent, expected_ids))
    if not frames:
        raise FileNotFoundError("No batch 3 agent files found")

    ratings = pd.concat(frames, ignore_index=True)
    agent_rows = summarize_agents(ratings)
    if missing:
        agent_rows.append(
            {
                "agent": "MISSING",
                "n_rows": 0,
                "yes": 0,
                "no": 0,
                "uncertain": 0,
                "mean_confidence": ";".join(missing),
            }
        )
    row_rows = summarize_rows(sample, ratings)
    stratum_rows = summarize_strata(row_rows)

    write_tsv(Path(args.agent_summary_out), agent_rows)
    write_tsv(Path(args.row_summary_out), row_rows)
    write_tsv(Path(args.stratum_summary_out), stratum_rows)


if __name__ == "__main__":
    main()
