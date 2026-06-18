#!/usr/bin/env python3
"""Summarize aggregate-only RST Signalling Corpus inventories.

Inputs are the TSV inventories produced by ``inspect_rst_signalling.py``.
This script does not read the protected corpus itself and does not write raw
text, row-level records, prompts, or examples.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


SPLIT_ORDER = ["Full_Annotation", "Training_Annotation", "Test_Annotation"]
BRIDGE_GROUPS = {
    "parison_or_syntactic_parallelism": {"subtype_parallel_syntactic_constructions"},
    "lexical_echo": {"subtype_lexical_chain", "subtype_repetition", "subtype_synonymy"},
    "comparison_reference": {"subtype_comparative_reference"},
    "semantic_opposition": {"subtype_antonymy"},
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def n(row: dict[str, str]) -> int:
    return int(row.get("n", "0") or 0)


def pct(value: int, total: int) -> str:
    if total <= 0:
        return ""
    return f"{100 * value / total:.2f}"


def split_sort_key(row: dict[str, object]) -> tuple[int, object, object]:
    split = str(row.get("split", ""))
    try:
        split_rank = SPLIT_ORDER.index(split)
    except ValueError:
        split_rank = len(SPLIT_ORDER)
    return (split_rank, row.get("sort_value", 0), row.get("candidate_group", ""))


def split_summary(file_rows: list[dict[str, str]], vector_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    files = {(row["split"], row["extension"]): n(row) for row in file_rows}
    vector_totals: defaultdict[str, int] = defaultdict(int)
    vector_lengths: defaultdict[str, list[str]] = defaultdict(list)
    for row in vector_rows:
        split = row["split"]
        count = n(row)
        vector_totals[split] += count
        vector_lengths[split].append(f"{row['feature_count']}={count}")

    rows = []
    for split in SPLIT_ORDER:
        rows.append(
            {
                "split": split,
                "text_files": files.get((split, "txt"), 0),
                "xml_files": files.get((split, "xml"), 0),
                "annotation_feature_vectors": vector_totals.get(split, 0),
                "feature_vector_lengths": "; ".join(vector_lengths.get(split, [])),
            }
        )
    return rows


def slot_totals(slot_rows: list[dict[str, str]]) -> dict[tuple[str, int], int]:
    totals: defaultdict[tuple[str, int], int] = defaultdict(int)
    for row in slot_rows:
        totals[(row["split"], int(row["slot_index"]))] += n(row)
    return dict(totals)


def formal_family_summary(
    candidate_rows: list[dict[str, str]], totals: dict[tuple[str, int], int]
) -> list[dict[str, object]]:
    counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    for row in candidate_rows:
        if row["slot_index"] != "3" or not row["candidate_group"].startswith("family_"):
            continue
        family = row["candidate_group"].removeprefix("family_")
        counts[(row["split"], family)] += n(row)

    rows = []
    for (split, family), count in counts.items():
        rows.append(
            {
                "split": split,
                "signal_family": family,
                "n": count,
                "pct_of_slot3_labels": pct(count, totals.get((split, 3), 0)),
                "sort_value": -count,
            }
        )
    rows.sort(key=split_sort_key)
    for row in rows:
        row.pop("sort_value")
    return rows


def formal_subtype_summary(
    candidate_rows: list[dict[str, str]], totals: dict[tuple[str, int], int]
) -> list[dict[str, object]]:
    counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    for row in candidate_rows:
        if row["slot_index"] != "4" or not row["candidate_group"].startswith("subtype_"):
            continue
        subtype = row["candidate_group"].removeprefix("subtype_")
        counts[(row["split"], subtype)] += n(row)

    rows = []
    for (split, subtype), count in counts.items():
        rows.append(
            {
                "split": split,
                "signal_subtype": subtype,
                "n": count,
                "pct_of_slot4_labels": pct(count, totals.get((split, 4), 0)),
                "sort_value": -count,
            }
        )
    rows.sort(key=split_sort_key)
    for row in rows:
        row.pop("sort_value")
    return rows


def bridge_summary(
    candidate_rows: list[dict[str, str]], totals: dict[tuple[str, int], int]
) -> list[dict[str, object]]:
    counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    for row in candidate_rows:
        if row["slot_index"] != "4":
            continue
        for bridge_group, candidate_groups in BRIDGE_GROUPS.items():
            if row["candidate_group"] in candidate_groups:
                counts[(row["split"], bridge_group)] += n(row)

    rows = []
    for (split, bridge_group), count in counts.items():
        rows.append(
            {
                "split": split,
                "bridge_group": bridge_group,
                "n": count,
                "pct_of_slot4_labels": pct(count, totals.get((split, 4), 0)),
                "note": "membership counts; groups can overlap on combined labels",
                "sort_value": -count,
            }
        )
    rows.sort(key=split_sort_key)
    for row in rows:
        row.pop("sort_value")
    return rows


def top_values(candidate_rows: list[dict[str, str]], totals: dict[tuple[str, int], int], limit: int) -> list[dict[str, object]]:
    rows = []
    for row in candidate_rows:
        split = row["split"]
        slot = int(row["slot_index"])
        count = n(row)
        rows.append(
            {
                "split": split,
                "slot_index": slot,
                "candidate_group": row["candidate_group"],
                "value": row["value"],
                "n": count,
                "pct_of_slot_labels": pct(count, totals.get((split, slot), 0)),
                "sort_value": -count,
            }
        )
    rows.sort(key=split_sort_key)

    limited: list[dict[str, object]] = []
    for split in SPLIT_ORDER:
        split_rows = [row for row in rows if row["split"] == split]
        limited.extend(split_rows[:limit])
    for row in limited:
        row.pop("sort_value")
    return limited


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def write_markdown(
    path: Path,
    split_rows: list[dict[str, object]],
    family_rows: list[dict[str, object]],
    subtype_rows: list[dict[str, object]],
    bridge_rows: list[dict[str, object]],
) -> None:
    full_family = [row for row in family_rows if row["split"] == "Full_Annotation"]
    full_subtype = [row for row in subtype_rows if row["split"] == "Full_Annotation"]
    full_bridge = [row for row in bridge_rows if row["split"] == "Full_Annotation"]

    text = "\n\n".join(
        [
            "# RST Signalling Corpus Aggregate Summary",
            "Generated from aggregate TSV inventories only. This report does not contain raw corpus text, row-level records, prompts, or examples.",
            "## Method Guardrails",
            "\n".join(
                [
                    "These guardrails are adapted from the corpus-methods DiD paper as general methodological hygiene, not as causal DiD machinery.",
                    "",
                    "- Target quantity: the RST-SC pass asks how existing signal labels can triangulate formal-balance categories. It does not estimate a treatment effect, reader response, or population-level causal effect.",
                    "- Unit separation: keep the linguistic figure, the annotation signal, the counted feature-vector label, and the document split distinct. A signal-label count is not an isocolon count unless a human crosswalk licenses that interpretation.",
                    "- Feature roles: assign each label one job before interpretation: parison-like form, lexical echo, comparison reference, semantic opposition, exclusion/control, or unresolved. Do not let one label silently serve as both outcome and explanation.",
                    "- Aggregation: treat the reported numbers as non-disjoint label memberships. Combined labels can contribute to more than one bridge group, so percentages are descriptive memberships, not mutually exclusive event rates.",
                    "- Artifact checks: before using a label as evidence, ask whether its frequency could reflect annotation design, split duplication, lexical-chain breadth, or a measurement convention rather than a rhetorical pattern in the text.",
                    "- Downgrade rules: if the crosswalk is ambiguous, if a bridge group is dominated by a broad label such as `lexical_chain`, or if Rency/Brett judge the label theoretically mismatched, report the result as annotation-context only, not rhetorical confirmation.",
                ]
            ),
            "## Split Inventory",
            markdown_table(
                split_rows,
                ["split", "text_files", "xml_files", "annotation_feature_vectors", "feature_vector_lengths"],
            ),
            "## Full Annotation Signal Families",
            "These are slot-3 label memberships. Combined labels can contribute to more than one family.",
            markdown_table(full_family, ["signal_family", "n", "pct_of_slot3_labels"]),
            "## Full Annotation Candidate Subtypes",
            "These are slot-4 label memberships for formal or comparison-relevant candidate labels.",
            markdown_table(full_subtype, ["signal_subtype", "n", "pct_of_slot4_labels"]),
            "## Project Bridge Candidates",
            "These group label memberships into candidate bridges for human/Rency interpretation. They are not automatic isocolon judgments.",
            markdown_table(full_bridge, ["bridge_group", "n", "pct_of_slot4_labels", "note"]),
            "## Next Interpretive Question",
            "The safe next step is to decide which candidate labels, especially `parallel_syntactic_constructions`, `repetition`, `lexical_chain`, `antonymy`, and `comparative_reference`, should count as evidence for parison-like form, lexical echo, semantic opposition, or comparison in this paper.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--derived-dir", default="data/derived")
    parser.add_argument("--report", default="notes/rst-signalling-aggregate-summary.md")
    parser.add_argument("--top-values", type=int, default=30)
    args = parser.parse_args()

    derived_dir = Path(args.derived_dir)
    file_rows = read_tsv(derived_dir / "rst_sc_file_inventory.tsv")
    vector_rows = read_tsv(derived_dir / "rst_sc_feature_vector_length_inventory.tsv")
    slot_rows = read_tsv(derived_dir / "rst_sc_feature_slot_inventory.tsv")
    candidate_rows = read_tsv(derived_dir / "rst_sc_formal_signal_candidate_summary.tsv")

    totals = slot_totals(slot_rows)
    split_rows = split_summary(file_rows, vector_rows)
    family_rows = formal_family_summary(candidate_rows, totals)
    subtype_rows = formal_subtype_summary(candidate_rows, totals)
    bridge_rows = bridge_summary(candidate_rows, totals)
    top_rows = top_values(candidate_rows, totals, args.top_values)

    write_tsv(
        derived_dir / "rst_sc_split_summary.tsv",
        ["split", "text_files", "xml_files", "annotation_feature_vectors", "feature_vector_lengths"],
        split_rows,
    )
    write_tsv(
        derived_dir / "rst_sc_signal_family_summary.tsv",
        ["split", "signal_family", "n", "pct_of_slot3_labels"],
        family_rows,
    )
    write_tsv(
        derived_dir / "rst_sc_signal_subtype_summary.tsv",
        ["split", "signal_subtype", "n", "pct_of_slot4_labels"],
        subtype_rows,
    )
    write_tsv(
        derived_dir / "rst_sc_project_bridge_summary.tsv",
        ["split", "bridge_group", "n", "pct_of_slot4_labels", "note"],
        bridge_rows,
    )
    write_tsv(
        derived_dir / "rst_sc_top_formal_signal_values.tsv",
        ["split", "slot_index", "candidate_group", "value", "n", "pct_of_slot_labels"],
        top_rows,
    )
    write_markdown(Path(args.report), split_rows, family_rows, subtype_rows, bridge_rows)

    print(f"Wrote aggregate RST-SC summaries to {derived_dir}")
    print(f"Wrote aggregate Markdown report to {args.report}")
    print("No raw text or row-level records were read or exported.")


if __name__ == "__main__":
    main()
