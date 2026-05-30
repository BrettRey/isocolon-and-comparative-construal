#!/usr/bin/env python3
"""Create a reproducible qualitative audit sample for isocolon scoring."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import pandas as pd


BROAD_LABELS = {
    "adversative-antithesis",
    "adversative-contrast",
    "joint-disjunction",
    "joint-list",
}
NARROW_LABELS = {"adversative-antithesis", "adversative-contrast"}
BROAD_NON_NARROW = BROAD_LABELS - NARROW_LABELS
RESTATEMENT_LABELS = {"restatement-repetition"}

STRATA = [
    ("high_broad_non_narrow", 10),
    ("typical_broad_non_narrow", 6),
    ("narrow_mixed", 6),
    ("high_non_target", 8),
    ("restatement_high_control", 5),
    ("baseline_non_target", 5),
]

EXPORT_COLUMNS = [
    "audit_id",
    "stratum",
    "source_row",
    "doc",
    "collection",
    "genre",
    "orig_label",
    "rel_type",
    "same_sentence",
    "unit1_ends_colon",
    "unit1_ends_semicolon",
    "isocolon_score",
    "length_score",
    "syntax_score",
    "lexical_score",
    "word_len_1",
    "word_len_2",
    "unit1_text",
    "unit2_text",
    "human_isocolonic",
    "formal_parallelism",
    "rhetorically_relevant",
    "genuine_comparison_or_coordination",
    "false_positive_repetition",
    "false_positive_list_formatting",
    "false_positive_dialogue_formula",
    "false_positive_template_or_quote",
    "bad_segmentation",
    "notes",
]


def add_source_row(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.insert(0, "source_row", range(1, len(frame) + 1))
    return frame


def candidate_frame(frame: pd.DataFrame, stratum: str) -> pd.DataFrame:
    score = frame["isocolon_score"].astype(float)
    if stratum == "high_broad_non_narrow":
        base = frame["orig_label"].isin(BROAD_NON_NARROW)
        cutoff = score[base].quantile(0.85)
        return frame[base & score.ge(cutoff)].copy()
    if stratum == "typical_broad_non_narrow":
        base = frame["orig_label"].isin(BROAD_NON_NARROW)
        low = score[base].quantile(0.40)
        high = score[base].quantile(0.60)
        return frame[base & score.between(low, high)].copy()
    if stratum == "narrow_mixed":
        return frame[frame["orig_label"].isin(NARROW_LABELS)].copy()
    if stratum == "high_non_target":
        base = ~frame["orig_label"].isin(BROAD_LABELS | RESTATEMENT_LABELS)
        cutoff = score[base].quantile(0.95)
        return frame[base & score.ge(cutoff)].copy()
    if stratum == "restatement_high_control":
        base = frame["orig_label"].isin(RESTATEMENT_LABELS)
        cutoff = score[base].quantile(0.75)
        return frame[base & score.ge(cutoff)].copy()
    if stratum == "baseline_non_target":
        base = ~frame["orig_label"].isin(BROAD_LABELS | RESTATEMENT_LABELS)
        low = score[base].quantile(0.20)
        high = score[base].quantile(0.60)
        return frame[base & score.between(low, high)].copy()
    raise ValueError(f"Unknown stratum: {stratum}")


def pick_rows(
    frame: pd.DataFrame,
    stratum: str,
    n: int,
    rng: random.Random,
    selected_rows: set[int],
) -> pd.DataFrame:
    candidates = candidate_frame(frame, stratum)
    candidates = candidates[~candidates["source_row"].isin(selected_rows)].copy()
    if len(candidates) < n:
        raise ValueError(f"Only {len(candidates)} candidates available for {stratum}; need {n}")

    candidates["_rand"] = [rng.random() for _ in range(len(candidates))]
    if stratum.startswith("high") or stratum == "restatement_high_control":
        candidates = candidates.sort_values(["isocolon_score", "_rand"], ascending=[False, True])
        pool = candidates.head(max(n * 4, n))
    else:
        pool = candidates.sort_values("_rand")

    chosen = []
    used_docs: set[str] = set()
    for _, row in pool.iterrows():
        if row["doc"] in used_docs:
            continue
        chosen.append(row)
        used_docs.add(row["doc"])
        if len(chosen) == n:
            break
    if len(chosen) < n:
        for _, row in pool.iterrows():
            if int(row["source_row"]) in {int(item["source_row"]) for item in chosen}:
                continue
            chosen.append(row)
            if len(chosen) == n:
                break

    out = pd.DataFrame(chosen).drop(columns=["_rand"], errors="ignore")
    selected_rows.update(int(value) for value in out["source_row"])
    out.insert(1, "stratum", stratum)
    return out


def clean_text(value: object) -> str:
    return str(value).replace("\r", " ").replace("\n", " ").strip()


def export_sample(sample: pd.DataFrame, tsv_path: Path, csv_path: Path) -> None:
    out = sample.copy()
    out.insert(0, "audit_id", [f"QA{index:03d}" for index in range(1, len(out) + 1)])
    for column in [
        "human_isocolonic",
        "formal_parallelism",
        "rhetorically_relevant",
        "genuine_comparison_or_coordination",
        "false_positive_repetition",
        "false_positive_list_formatting",
        "false_positive_dialogue_formula",
        "false_positive_template_or_quote",
        "bad_segmentation",
        "notes",
    ]:
        out[column] = ""
    for text_col in ["unit1_text", "unit2_text"]:
        out[text_col] = out[text_col].map(clean_text)
    out = out[EXPORT_COLUMNS]

    tsv_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(tsv_path, sep="\t", index=False, quoting=csv.QUOTE_MINIMAL)
    out.to_csv(csv_path, index=False, quoting=csv.QUOTE_MINIMAL)


def write_rubric(path: Path, sample_tsv: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Qualitative Isocolon Audit Rubric",
                "",
                f"Sample: `{sample_tsv}`",
                "",
                "Primary coding question:",
                "",
                "- `human_isocolonic`: yes / no / uncertain",
                "",
                "Use `yes` when the two adjacent units show formally parallel structure that",
                "would plausibly matter rhetorically, not just because they happen to be short.",
                "",
                "Secondary fields:",
                "",
                "- `formal_parallelism`: none / weak / moderate / strong",
                "- `rhetorically_relevant`: yes / no / uncertain",
                "- `genuine_comparison_or_coordination`: yes / no / uncertain",
                "- false-positive flags: yes / no for repetition, list formatting, dialogue",
                "  formula, template/quotation, and bad segmentation",
                "",
                "Notes should briefly say what made the case count or not count.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--out-tsv", default="outputs/audit/isocolon_qualitative_audit_40.tsv")
    parser.add_argument("--out-csv", default="outputs/audit/isocolon_qualitative_audit_40.csv")
    parser.add_argument("--rubric", default="outputs/audit/qualitative_audit_rubric.md")
    parser.add_argument("--seed", type=int, default=20260530)
    args = parser.parse_args()

    frame = add_source_row(pd.read_csv(args.input, sep="\t"))
    rng = random.Random(args.seed)
    selected_rows: set[int] = set()
    samples = [
        pick_rows(frame, stratum, n, rng, selected_rows)
        for stratum, n in STRATA
    ]
    sample = pd.concat(samples, ignore_index=True)
    export_sample(sample, Path(args.out_tsv), Path(args.out_csv))
    write_rubric(Path(args.rubric), Path(args.out_tsv))


if __name__ == "__main__":
    main()
