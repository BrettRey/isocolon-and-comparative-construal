#!/usr/bin/env python3
"""Create the third targeted qualitative audit sample."""

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
BROAD_NON_NARROW = {"joint-disjunction", "joint-list"}
NARROW_LABELS = {"adversative-antithesis", "adversative-contrast"}
RESTATEMENT_LABELS = {"restatement-repetition"}
DIALOGUE_GENRES = {"conversation", "interview", "podcast", "vlog"}
DIALOGUE_LABELS = {
    "topic-question",
    "organization-phatic",
    "restatement-partial",
    "elaboration-additional",
    "attribution-positive",
}

STRATA = [
    ("high_broad_target", 6),
    ("mid_broad_target", 6),
    ("narrow_antithesis_contrast", 8),
    ("dialogue_echo_candidate", 6),
    ("comparative_concession", 5),
    ("high_non_target_artifact", 5),
    ("restatement_repetition_control", 4),
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


def load_excluded(paths: list[str]) -> set[int]:
    excluded: set[int] = set()
    for path_text in paths:
        path = Path(path_text)
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        if "source_row" in frame:
            excluded.update(int(value) for value in frame["source_row"].dropna())
    return excluded


def candidate_frame(frame: pd.DataFrame, stratum: str) -> pd.DataFrame:
    score = frame["isocolon_score"].astype(float)
    if stratum == "high_broad_target":
        base = frame["orig_label"].isin(BROAD_NON_NARROW)
        cutoff = score[base].quantile(0.85)
        return frame[base & score.ge(cutoff)].copy()
    if stratum == "mid_broad_target":
        base = frame["orig_label"].isin(BROAD_NON_NARROW)
        low = score[base].quantile(0.50)
        high = score[base].quantile(0.75)
        return frame[base & score.between(low, high)].copy()
    if stratum == "narrow_antithesis_contrast":
        base = frame["orig_label"].isin(NARROW_LABELS)
        low = score[base].quantile(0.40)
        return frame[base & score.ge(low)].copy()
    if stratum == "dialogue_echo_candidate":
        base = (
            frame["genre"].isin(DIALOGUE_GENRES)
            & frame["orig_label"].isin(DIALOGUE_LABELS)
            & ~frame["orig_label"].isin(BROAD_LABELS | RESTATEMENT_LABELS)
        )
        cutoff = score[base].quantile(0.85)
        return frame[base & score.ge(cutoff)].copy()
    if stratum == "comparative_concession":
        base = frame["orig_label"].eq("adversative-concession")
        low = score[base].quantile(0.55)
        return frame[base & score.ge(low)].copy()
    if stratum == "high_non_target_artifact":
        base = ~frame["orig_label"].isin(BROAD_LABELS | RESTATEMENT_LABELS | DIALOGUE_LABELS)
        cutoff = score[base].quantile(0.95)
        return frame[base & score.ge(cutoff)].copy()
    if stratum == "restatement_repetition_control":
        base = frame["orig_label"].isin(RESTATEMENT_LABELS)
        cutoff = score[base].quantile(0.75)
        return frame[base & score.ge(cutoff)].copy()
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
    if stratum.startswith("high") or stratum == "restatement_repetition_control":
        candidates = candidates.sort_values(["isocolon_score", "_rand"], ascending=[False, True])
        pool = candidates.head(max(n * 6, n))
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
        chosen_ids = {int(item["source_row"]) for item in chosen}
        for _, row in pool.iterrows():
            if int(row["source_row"]) in chosen_ids:
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
    out.insert(0, "audit_id", [f"QC{index:03d}" for index in range(1, len(out) + 1)])
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
    path.write_text(
        "\n".join(
            [
                "# Qualitative Isocolon Audit Batch 3",
                "",
                f"Sample: `{sample_tsv}`",
                "",
                "Use the current codebook and dictionary:",
                "",
                "- `outputs/audit/qualitative_audit_codebook.md`",
                "- `outputs/audit/qualitative_audit_dictionary.tsv`",
                "",
                "This batch continues the boundary-focused validation sample after",
                "batches 1 and 2. It excludes previously sampled `source_row` values",
                "and targets high and mid broad targets, narrow antithesis/contrast,",
                "dialogue echo candidates, comparative concession, high-scoring",
                "non-target artifacts, and restatement controls.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[
            "outputs/audit/isocolon_qualitative_audit_40.csv",
            "outputs/audit/isocolon_qualitative_audit_batch2_40.csv",
        ],
    )
    parser.add_argument("--out-tsv", default="outputs/audit/isocolon_qualitative_audit_batch3_40.tsv")
    parser.add_argument("--out-csv", default="outputs/audit/isocolon_qualitative_audit_batch3_40.csv")
    parser.add_argument("--rubric", default="outputs/audit/qualitative_audit_batch3_rubric.md")
    parser.add_argument("--seed", type=int, default=20260601)
    args = parser.parse_args()

    frame = add_source_row(pd.read_csv(args.input, sep="\t"))
    rng = random.Random(args.seed)
    selected_rows = load_excluded(args.exclude)
    samples = [
        pick_rows(frame, stratum, n, rng, selected_rows)
        for stratum, n in STRATA
    ]
    sample = pd.concat(samples, ignore_index=True)
    export_sample(sample, Path(args.out_tsv), Path(args.out_csv))
    write_rubric(Path(args.rubric), Path(args.out_tsv))


if __name__ == "__main__":
    main()
