#!/usr/bin/env python3
"""Summarize human and agent validation for the qualitative audit batches."""

from __future__ import annotations

import csv
from collections import Counter
from itertools import combinations
from pathlib import Path

import pandas as pd


OUT_DIR = Path("outputs/audit")
REVIEW_DIR = OUT_DIR / "agent_reviews"
BOOLEAN_VALUES = {"yes", "no", "uncertain"}
PARALLELISM_VALUES = {"none", "weak", "moderate", "strong"}
EXPECTED_AGENT_COLUMNS = [
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

BATCHES = [
    {
        "batch": "batch1",
        "human": OUT_DIR / "isocolon_qualitative_audit_40.csv",
        "agents": [
            ("codex_1", REVIEW_DIR / "codex_1_audit.tsv"),
            ("codex_2", REVIEW_DIR / "codex_2_audit.tsv"),
            ("opus_1", REVIEW_DIR / "opus_1_audit.tsv"),
            ("opus_2", REVIEW_DIR / "opus_2_audit.tsv"),
        ],
    },
    {
        "batch": "batch2",
        "human": OUT_DIR / "isocolon_qualitative_audit_batch2_40.csv",
        "agents": [
            ("codex_batch2_1", REVIEW_DIR / "codex_batch2_1.tsv"),
            ("codex_batch2_2", REVIEW_DIR / "codex_batch2_2.tsv"),
            ("opus_batch2_1", REVIEW_DIR / "opus_batch2_1.tsv"),
            ("opus_batch2_2", REVIEW_DIR / "opus_batch2_2.tsv"),
        ],
    },
]


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        if not rows:
            handle.write("")
            return
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def load_human(path: Path, batch: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {
        "audit_id",
        "stratum",
        "genre",
        "orig_label",
        "isocolon_score",
        "unit1_text",
        "unit2_text",
        "human_isocolonic",
        "formal_parallelism",
        "rhetorically_relevant",
        "genuine_comparison_or_coordination",
        "bad_segmentation",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{path} missing columns {missing}")
    values = set(frame["human_isocolonic"].dropna())
    if not values <= BOOLEAN_VALUES:
        raise ValueError(f"{path} has invalid human_isocolonic values {sorted(values)}")
    frame = frame.copy()
    frame["batch"] = batch
    return frame


def load_agent(path: Path, agent: str, expected_ids: list[str], batch: str) -> pd.DataFrame:
    frame = pd.read_csv(path, sep="\t")
    if list(frame.columns) != EXPECTED_AGENT_COLUMNS:
        raise ValueError(f"{path} has unexpected columns {list(frame.columns)}")
    if frame["audit_id"].tolist() != expected_ids:
        raise ValueError(f"{path} audit_id order does not match human file")
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
    frame = frame.copy()
    frame["batch"] = batch
    return frame


def cohen_kappa(left: list[str], right: list[str], categories: list[str]) -> tuple[float, float]:
    if len(left) != len(right):
        raise ValueError("rating vectors must have the same length")
    n = len(left)
    observed = sum(a == b for a, b in zip(left, right)) / n
    left_counts = Counter(left)
    right_counts = Counter(right)
    expected = sum((left_counts[c] / n) * (right_counts[c] / n) for c in categories)
    if expected == 1:
        return observed, float("nan")
    return observed, (observed - expected) / (1 - expected)


def majority(values: list[str]) -> tuple[str, int]:
    counts = Counter(values)
    top_n = max(counts.values())
    top = sorted(value for value, count in counts.items() if count == top_n)
    return "/".join(top), top_n


def human_summary(human: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for keys, group in human.groupby(["batch", "stratum"], sort=False):
        batch, stratum = keys
        counts = group["human_isocolonic"].value_counts().reindex(["yes", "no", "uncertain"], fill_value=0)
        rows.append(
            {
                "batch": batch,
                "stratum": stratum,
                "n_rows": len(group),
                "human_yes": int(counts["yes"]),
                "human_no": int(counts["no"]),
                "human_uncertain": int(counts["uncertain"]),
                "mean_isocolon_score": round(float(group["isocolon_score"].mean()), 4),
            }
        )
    for batch, group in human.groupby("batch", sort=False):
        counts = group["human_isocolonic"].value_counts().reindex(["yes", "no", "uncertain"], fill_value=0)
        rows.append(
            {
                "batch": batch,
                "stratum": "ALL",
                "n_rows": len(group),
                "human_yes": int(counts["yes"]),
                "human_no": int(counts["no"]),
                "human_uncertain": int(counts["uncertain"]),
                "mean_isocolon_score": round(float(group["isocolon_score"].mean()), 4),
            }
        )
    counts = human["human_isocolonic"].value_counts().reindex(["yes", "no", "uncertain"], fill_value=0)
    rows.append(
        {
            "batch": "combined",
            "stratum": "ALL",
            "n_rows": len(human),
            "human_yes": int(counts["yes"]),
            "human_no": int(counts["no"]),
            "human_uncertain": int(counts["uncertain"]),
            "mean_isocolon_score": round(float(human["isocolon_score"].mean()), 4),
        }
    )
    return rows


def agent_summary(agents: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for keys, group in agents.groupby(["batch", "agent"], sort=False):
        batch, agent = keys
        counts = group["is_isocolonic"].value_counts().reindex(["yes", "no", "uncertain"], fill_value=0)
        rows.append(
            {
                "batch": batch,
                "agent": agent,
                "n_rows": len(group),
                "agent_yes": int(counts["yes"]),
                "agent_no": int(counts["no"]),
                "agent_uncertain": int(counts["uncertain"]),
                "mean_confidence": round(float(group["confidence"].astype(float).mean()), 4),
            }
        )
    return rows


def agreement_summary(human: pd.DataFrame, agents: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    human_lookup = human.set_index(["batch", "audit_id"])["human_isocolonic"].to_dict()
    for keys, group in agents.groupby(["batch", "agent"], sort=False):
        batch, agent = keys
        h = [human_lookup[(batch, audit_id)] for audit_id in group["audit_id"]]
        a = group["is_isocolonic"].tolist()
        three_agree, three_kappa = cohen_kappa(h, a, ["yes", "no", "uncertain"])
        h_binary = ["yes" if value == "yes" else "not_yes" for value in h]
        a_binary = ["yes" if value == "yes" else "not_yes" for value in a]
        binary_agree, binary_kappa = cohen_kappa(h_binary, a_binary, ["yes", "not_yes"])
        rows.append(
            {
                "batch": batch,
                "rater_pair": f"human__{agent}",
                "n_rows": len(group),
                "three_way_agreement": round(three_agree, 4),
                "three_way_kappa": round(three_kappa, 4),
                "binary_agreement": round(binary_agree, 4),
                "binary_kappa": round(binary_kappa, 4),
            }
        )
    for batch, group in agents.groupby("batch", sort=False):
        by_agent = {agent: g for agent, g in group.groupby("agent", sort=False)}
        for left, right in combinations(by_agent, 2):
            left_values = by_agent[left]["is_isocolonic"].tolist()
            right_values = by_agent[right]["is_isocolonic"].tolist()
            three_agree, three_kappa = cohen_kappa(left_values, right_values, ["yes", "no", "uncertain"])
            left_binary = ["yes" if value == "yes" else "not_yes" for value in left_values]
            right_binary = ["yes" if value == "yes" else "not_yes" for value in right_values]
            binary_agree, binary_kappa = cohen_kappa(left_binary, right_binary, ["yes", "not_yes"])
            rows.append(
                {
                    "batch": batch,
                    "rater_pair": f"{left}__{right}",
                    "n_rows": len(left_values),
                    "three_way_agreement": round(three_agree, 4),
                    "three_way_kappa": round(three_kappa, 4),
                    "binary_agreement": round(binary_agree, 4),
                    "binary_kappa": round(binary_kappa, 4),
                }
            )
    return rows


def row_summary(human: pd.DataFrame, agents: pd.DataFrame) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    disagreement_rows: list[dict[str, object]] = []
    grouped_agents = {
        key: group
        for key, group in agents.groupby(["batch", "audit_id"], sort=False)
    }
    for _, hrow in human.iterrows():
        key = (hrow["batch"], hrow["audit_id"])
        group = grouped_agents[key]
        labels = group["is_isocolonic"].tolist()
        maj, maj_n = majority(labels)
        counts = Counter(labels)
        agent_codes = "; ".join(
            f"{row.agent}:{row.is_isocolonic}"
            for row in group[["agent", "is_isocolonic"]].itertuples(index=False)
        )
        differs = [row for row in group.itertuples(index=False) if row.is_isocolonic != hrow["human_isocolonic"]]
        row = {
            "batch": hrow["batch"],
            "audit_id": hrow["audit_id"],
            "stratum": hrow["stratum"],
            "human_isocolonic": hrow["human_isocolonic"],
            "agent_yes": counts["yes"],
            "agent_no": counts["no"],
            "agent_uncertain": counts["uncertain"],
            "agent_majority": maj,
            "agent_majority_n": maj_n,
            "n_agent_disagreements": len(differs),
            "agent_codes": agent_codes,
            "unit1_text": hrow["unit1_text"],
            "unit2_text": hrow["unit2_text"],
        }
        rows.append(row)
        if differs:
            disagreement_rows.append(row)
    return rows, disagreement_rows


def main() -> None:
    human_frames: list[pd.DataFrame] = []
    agent_frames: list[pd.DataFrame] = []
    for config in BATCHES:
        human = load_human(config["human"], config["batch"])
        expected_ids = human["audit_id"].tolist()
        human_frames.append(human)
        for agent, path in config["agents"]:
            agent_frames.append(load_agent(path, agent, expected_ids, config["batch"]))

    human = pd.concat(human_frames, ignore_index=True)
    agents = pd.concat(agent_frames, ignore_index=True)
    rows, disagreements = row_summary(human, agents)

    write_tsv(OUT_DIR / "qualitative_validation_human_summary.tsv", human_summary(human))
    write_tsv(REVIEW_DIR / "qualitative_validation_agent_summary.tsv", agent_summary(agents))
    write_tsv(REVIEW_DIR / "qualitative_validation_agreement.tsv", agreement_summary(human, agents))
    write_tsv(REVIEW_DIR / "qualitative_validation_row_summary.tsv", rows)
    write_tsv(REVIEW_DIR / "qualitative_validation_disagreements.tsv", disagreements)


if __name__ == "__main__":
    main()
