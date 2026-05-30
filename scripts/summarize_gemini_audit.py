#!/usr/bin/env python3
"""Validate and summarize the Gemini 80-row qualitative audit pass."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


HUMAN_PATH = Path("outputs/audit/isocolon_qualitative_audit_80.csv")
GEMINI_PATH = Path("outputs/audit/agent_reviews/gemini_80.tsv")
SUMMARY_OUT = Path("outputs/audit/agent_reviews/gemini_80_summary.tsv")
DISAGREEMENTS_OUT = Path("outputs/audit/agent_reviews/gemini_80_disagreements.tsv")

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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        if not rows:
            handle.write("")
            return
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def cohen_kappa(left: list[str], right: list[str], categories: list[str]) -> tuple[float, float]:
    n = len(left)
    observed = sum(a == b for a, b in zip(left, right)) / n
    left_counts = Counter(left)
    right_counts = Counter(right)
    expected = sum((left_counts[c] / n) * (right_counts[c] / n) for c in categories)
    return observed, (observed - expected) / (1 - expected)


def binary(value: str) -> str:
    return "yes" if value == "yes" else "not_yes"


def validate(human: list[dict[str, str]], gemini: list[dict[str, str]]) -> None:
    if len(human) != 80:
        raise ValueError(f"{HUMAN_PATH} has {len(human)} rows, expected 80")
    if len(gemini) != 80:
        raise ValueError(f"{GEMINI_PATH} has {len(gemini)} rows, expected 80")
    if list(gemini[0].keys()) != EXPECTED_COLUMNS:
        raise ValueError(f"{GEMINI_PATH} has unexpected columns: {list(gemini[0].keys())}")
    expected_ids = [row["audit_id"] for row in human]
    actual_ids = [row["audit_id"] for row in gemini]
    if actual_ids != expected_ids:
        raise ValueError("Gemini audit_id order does not match the 80-row human file")
    if {row["agent"] for row in gemini} != {"gemini_80"}:
        raise ValueError("Gemini agent column must contain only gemini_80")
    for row in gemini:
        for column in [
            "is_isocolonic",
            "rhetorically_relevant",
            "genuine_comparison_or_coordination",
            "bad_segmentation",
        ]:
            if row[column] not in BOOLEAN_VALUES:
                raise ValueError(f"{row['audit_id']} has invalid {column}: {row[column]}")
        if row["formal_parallelism"] not in PARALLELISM_VALUES:
            raise ValueError(f"{row['audit_id']} has invalid formal_parallelism: {row['formal_parallelism']}")
        confidence = float(row["confidence"])
        if not 0 <= confidence <= 1:
            raise ValueError(f"{row['audit_id']} has confidence outside [0,1]")


def main() -> None:
    human = read_csv(HUMAN_PATH)
    gemini = read_tsv(GEMINI_PATH)
    validate(human, gemini)

    human_by_id = {row["audit_id"]: row for row in human}
    human_labels = [row["human_isocolonic"] for row in human]
    gemini_labels = [row["is_isocolonic"] for row in gemini]
    three_agree, three_kappa = cohen_kappa(human_labels, gemini_labels, ["yes", "no", "uncertain"])
    binary_agree, binary_kappa = cohen_kappa(
        [binary(value) for value in human_labels],
        [binary(value) for value in gemini_labels],
        ["yes", "not_yes"],
    )

    counts = Counter(gemini_labels)
    summary = [
        {
            "agent": "gemini_80",
            "model_reported": "Gemini 3.5 Flash (Medium), Antigravity CLI 1.0.3",
            "n_rows": len(gemini),
            "yes": counts["yes"],
            "no": counts["no"],
            "uncertain": counts["uncertain"],
            "three_way_agreement": round(three_agree, 4),
            "three_way_kappa": round(three_kappa, 4),
            "binary_agreement": round(binary_agree, 4),
            "binary_kappa": round(binary_kappa, 4),
        }
    ]

    disagreements: list[dict[str, object]] = []
    for row in gemini:
        human_row = human_by_id[row["audit_id"]]
        if row["is_isocolonic"] != human_row["human_isocolonic"]:
            disagreements.append(
                {
                    "audit_id": row["audit_id"],
                    "batch": human_row["batch"],
                    "stratum": human_row["stratum"],
                    "human_isocolonic": human_row["human_isocolonic"],
                    "gemini_isocolonic": row["is_isocolonic"],
                    "gemini_formal_parallelism": row["formal_parallelism"],
                    "gemini_rhetorically_relevant": row["rhetorically_relevant"],
                    "gemini_comparison_or_coordination": row["genuine_comparison_or_coordination"],
                    "gemini_false_positive_flags": row["false_positive_flags"],
                    "gemini_confidence": row["confidence"],
                    "gemini_reason": row["short_reason"],
                    "unit1_text": human_row["unit1_text"],
                    "unit2_text": human_row["unit2_text"],
                }
            )

    write_tsv(SUMMARY_OUT, summary)
    write_tsv(DISAGREEMENTS_OUT, disagreements)


if __name__ == "__main__":
    main()
