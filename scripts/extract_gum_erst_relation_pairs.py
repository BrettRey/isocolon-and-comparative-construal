#!/usr/bin/env python3
"""Extract first-pass GUM/eRST relation-pair candidates with balance fields."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

VALID_REL_TYPES = {"explicit", "implicit"}


def clean_text(value: str | None) -> str:
    return " ".join((value or "").split())


def span_numbers(span_text: str) -> list[int]:
    numbers: list[int] = []
    for part in span_text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            try:
                start = int(start_text)
                end = int(end_text)
            except ValueError:
                continue
            if end >= start:
                numbers.extend(range(start, end + 1))
        else:
            try:
                numbers.append(int(part))
            except ValueError:
                continue
    return numbers


def span_intervals(span_text: str) -> list[tuple[int, int]]:
    intervals: list[tuple[int, int]] = []
    for part in span_text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            try:
                start = int(start_text)
                end = int(end_text)
            except ValueError:
                continue
            if end >= start:
                intervals.append((start, end))
        else:
            try:
                value = int(part)
            except ValueError:
                continue
            intervals.append((value, value))
    return intervals


def interval_status(
    intervals1: list[tuple[int, int]], intervals2: list[tuple[int, int]]
) -> tuple[str, str, int]:
    if not intervals1 or not intervals2:
        return "", "", 0
    for start1, end1 in intervals1:
        for start2, end2 in intervals2:
            if start1 <= end2 and start2 <= end1:
                return "overlap", "", 0

    unit1_min = min(start for start, _ in intervals1)
    unit1_max = max(end for _, end in intervals1)
    unit2_min = min(start for start, _ in intervals2)
    unit2_max = max(end for _, end in intervals2)
    if unit1_max < unit2_min:
        gap = unit2_min - unit1_max - 1
        return "1_before_2", str(gap), int(gap == 0)
    if unit2_max < unit1_min:
        gap = unit1_min - unit2_max - 1
        return "2_before_1", str(gap), int(gap == 0)
    return "interleaved", "", 0


def cell(row: dict[str, str | None], key: str) -> str:
    return row.get(key) or ""


def doc_parts(doc: str) -> tuple[str, str]:
    pieces = doc.split("_", 2)
    if len(pieces) >= 2:
        return pieces[0], pieces[1]
    return "", ""


def split_file_parts(path: Path) -> tuple[str, str]:
    parts = path.name.split(".")
    if len(parts) >= 4:
        return parts[1], parts[2]
    return "", ""


def balance(n1: int, n2: int) -> str:
    if n1 <= 0 or n2 <= 0:
        return ""
    return f"{1 - abs(n1 - n2) / max(n1, n2):.4f}"


def relation_rows(corpus_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rels_path in sorted((corpus_root / "rst" / "disrpt").glob("eng.erst.*.rels")):
        framework, partition = split_file_parts(rels_path)
        with rels_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                rel_type = cell(row, "rel_type")
                label = cell(row, "label")
                orig_label = cell(row, "orig_label")
                if rel_type not in VALID_REL_TYPES or not label or not orig_label:
                    continue

                unit1_nums = span_numbers(cell(row, "unit1_toks"))
                unit2_nums = span_numbers(cell(row, "unit2_toks"))
                unit1_intervals = span_intervals(cell(row, "unit1_toks"))
                unit2_intervals = span_intervals(cell(row, "unit2_toks"))
                if unit1_nums and unit2_nums:
                    unit1_min = min(unit1_nums)
                    unit1_max = max(unit1_nums)
                    unit2_min = min(unit2_nums)
                    unit2_max = max(unit2_nums)
                    doc_order, gap, adjacent = interval_status(unit1_intervals, unit2_intervals)
                else:
                    unit1_min = unit1_max = unit2_min = unit2_max = ""
                    gap = ""
                    adjacent = 0
                    doc_order = ""

                unit1_text = clean_text(cell(row, "u1_raw") or cell(row, "unit1_txt"))
                unit2_text = clean_text(cell(row, "u2_raw") or cell(row, "unit2_txt"))
                collection, genre = doc_parts(cell(row, "doc"))
                rows.append(
                    {
                        "source_file": rels_path.name,
                        "framework": framework,
                        "partition": partition,
                        "doc": cell(row, "doc"),
                        "collection": collection,
                        "genre": genre,
                        "label": label,
                        "orig_label": orig_label,
                        "rel_type": rel_type,
                        "direction": cell(row, "dir"),
                        "doc_order": doc_order,
                        "adjacent": adjacent,
                        "token_gap": gap,
                        "unit1_toks": cell(row, "unit1_toks"),
                        "unit2_toks": cell(row, "unit2_toks"),
                        "unit1_min": unit1_min,
                        "unit1_max": unit1_max,
                        "unit2_min": unit2_min,
                        "unit2_max": unit2_max,
                        "unit1_len": len(unit1_nums),
                        "unit2_len": len(unit2_nums),
                        "token_balance": balance(len(unit1_nums), len(unit2_nums)),
                        "same_sentence": int(clean_text(cell(row, "unit1_sent")) == clean_text(cell(row, "unit2_sent"))),
                        "unit1_ends_colon": int(unit1_text.endswith(":")),
                        "unit1_ends_semicolon": int(unit1_text.endswith(";")),
                        "unit1_text": unit1_text,
                        "unit2_text": unit2_text,
                    }
                )
    return rows


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", default="data/raw/gum-erst")
    parser.add_argument("--out-dir", default="data/derived")
    args = parser.parse_args()

    rows = relation_rows(Path(args.corpus_root))
    fieldnames = [
        "source_file",
        "framework",
        "partition",
        "doc",
        "collection",
        "genre",
        "label",
        "orig_label",
        "rel_type",
        "direction",
        "doc_order",
        "adjacent",
        "token_gap",
        "unit1_toks",
        "unit2_toks",
        "unit1_min",
        "unit1_max",
        "unit2_min",
        "unit2_max",
        "unit1_len",
        "unit2_len",
        "token_balance",
        "same_sentence",
        "unit1_ends_colon",
        "unit1_ends_semicolon",
        "unit1_text",
        "unit2_text",
    ]
    out_dir = Path(args.out_dir)
    write_tsv(out_dir / "gum_erst_relation_pairs.tsv", fieldnames, rows)
    write_tsv(
        out_dir / "gum_erst_adjacent_relation_pairs.tsv",
        fieldnames,
        [row for row in rows if row["adjacent"] == 1],
    )


if __name__ == "__main__":
    main()
