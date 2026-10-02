#!/usr/bin/env python3
"""Merge pasted returns from ``rater_app/antithesis_coding.html``.

Coders copy their codes as TSV and paste them into an email. Save each return
as a ``.tsv`` (or ``.txt``) file in ``rater_app/responses/antithesis/``, which is
ignored by Git. The script joins returns to the batch manifest, keeps each
coder's latest judgment per item, and writes agreement summaries.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JUDGMENTS = ["classical_antithesis", "semantic_opposition", "parallel_opposition"]
CATEGORIES = ["yes", "no", "uncertain"]
LONG_COLUMNS = [
    "coder",
    "batch",
    "code_id",
    "genre",
    *JUDGMENTS,
    "antithesis_notes",
    "figure_label",
    "rubric_note",
    "coded_at",
    "source_file",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_return(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    """Read one pasted return. Tolerates email quoting ('> ') and stray blank lines."""
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.lstrip("> ").rstrip()
        if line:
            lines.append(line)
    comments = [line.split("\t", 1)[1] for line in lines if line.startswith("# general_comment\t")]
    body = [line for line in lines if not line.startswith("#")]
    start = next((i for i, line in enumerate(body) if line.startswith("coder\t")), None)
    if start is None:
        raise ValueError(f"{path}: no header line starting with 'coder'")
    header = body[start].split("\t")
    rows = []
    for line in body[start + 1 :]:
        parts = line.split("\t")
        if len(parts) != len(header):
            raise ValueError(f"{path}: expected {len(header)} fields, got {len(parts)}: {line[:80]}")
        rows.append(dict(zip(header, parts)))
    return rows, comments


def fleiss_kappa(table: list[list[int]]) -> float | None:
    """Fleiss' kappa for items each rated by the same number of coders."""
    if not table:
        return None
    n_raters = sum(table[0])
    if n_raters < 2 or any(sum(row) != n_raters for row in table):
        return None
    n_items = len(table)
    p_j = [sum(row[j] for row in table) / (n_items * n_raters) for j in range(len(table[0]))]
    p_i = [(sum(c * c for c in row) - n_raters) / (n_raters * (n_raters - 1)) for row in table]
    p_bar = sum(p_i) / n_items
    p_e = sum(p * p for p in p_j)
    if p_e == 1:
        return None
    return (p_bar - p_e) / (1 - p_e)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--responses", default="rater_app/responses/antithesis")
    parser.add_argument("--manifest", default="rater_app/antithesis_items.tsv")
    parser.add_argument("--out-dir", default="data/derived")
    args = parser.parse_args()

    manifest = {row["code_id"]: row for row in read_tsv(ROOT / args.manifest)}
    response_dir = ROOT / args.responses
    paths = sorted([*response_dir.glob("*.tsv"), *response_dir.glob("*.txt")])
    if not paths:
        print(f"No returns found in {args.responses}")
        return

    latest: dict[tuple[str, str], dict[str, object]] = {}
    comments: list[dict[str, str]] = []
    unknown = 0
    for path in paths:
        rows, general = parse_return(path)
        coder = rows[0]["coder"].strip() if rows else path.stem
        comments.extend({"coder": coder, "comment": text, "source_file": path.name} for text in general)
        for row in rows:
            code_id = row.get("code_id", "")
            if code_id not in manifest:
                unknown += 1
                continue
            key = (row["coder"].strip(), code_id)
            record = {**row, "coder": key[0], "genre": manifest[code_id]["genre"], "source_file": path.name}
            if key not in latest or str(record.get("coded_at", "")) >= str(latest[key].get("coded_at", "")):
                latest[key] = record

    out_dir = ROOT / args.out_dir
    long_rows = sorted(latest.values(), key=lambda r: (str(r["code_id"]), str(r["coder"])))
    write_tsv(out_dir / "antithesis_codes_long.tsv", LONG_COLUMNS, long_rows)
    write_tsv(out_dir / "antithesis_general_comments.tsv", ["coder", "comment", "source_file"], comments)

    coders = sorted({str(r["coder"]) for r in long_rows})
    by_item: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    for row in long_rows:
        by_item[str(row["code_id"])][str(row["coder"])] = row

    agreement_rows = []
    disagreement_rows = []
    for judgment in JUDGMENTS:
        pair_hits = pair_total = 0
        table = []
        distribution = Counter()
        for code_id, coded in by_item.items():
            values = {c: str(r[judgment]) for c, r in coded.items() if r[judgment] in CATEGORIES}
            distribution.update(values.values())
            for a, b in combinations(sorted(values), 2):
                pair_total += 1
                pair_hits += values[a] == values[b]
            if len(values) == len(coders) and len(coders) >= 2:
                table.append([sum(v == cat for v in values.values()) for cat in CATEGORIES])
            if len(set(values.values())) > 1:
                disagreement_rows.append(
                    {
                        "code_id": code_id,
                        "judgment": judgment,
                        "genre": manifest[code_id]["genre"],
                        "values": "; ".join(f"{c}={v}" for c, v in sorted(values.items())),
                        "unit1_text": manifest[code_id]["unit1_text"],
                        "unit2_text": manifest[code_id]["unit2_text"],
                    }
                )
        kappa = fleiss_kappa(table)
        agreement_rows.append(
            {
                "judgment": judgment,
                "coders": len(coders),
                "items_coded": sum(1 for coded in by_item.values() if any(r[judgment] in CATEGORIES for r in coded.values())),
                "items_all_coders": len(table),
                "pairwise_agreement": f"{pair_hits / pair_total:.3f}" if pair_total else "",
                "fleiss_kappa": f"{kappa:.3f}" if kappa is not None else "",
                **{f"n_{cat}": distribution[cat] for cat in CATEGORIES},
            }
        )

    write_tsv(
        out_dir / "antithesis_agreement.tsv",
        ["judgment", "coders", "items_coded", "items_all_coders", "pairwise_agreement", "fleiss_kappa", *[f"n_{c}" for c in CATEGORIES]],
        agreement_rows,
    )
    write_tsv(
        out_dir / "antithesis_disagreements.tsv",
        ["code_id", "judgment", "genre", "values", "unit1_text", "unit2_text"],
        disagreement_rows,
    )

    print(f"Read {len(paths)} returns from {len(coders)} coders: {', '.join(coders)}")
    if unknown:
        print(f"Skipped {unknown} rows with code_ids not in the manifest")
    for row in agreement_rows:
        print(
            f"{row['judgment']}: {row['items_coded']} items coded, "
            f"pairwise agreement {row['pairwise_agreement'] or 'n/a'}, Fleiss kappa {row['fleiss_kappa'] or 'n/a'}"
        )
    print(f"Wrote antithesis_codes_long.tsv, antithesis_agreement.tsv, antithesis_disagreements.tsv, antithesis_general_comments.tsv to {args.out_dir}")


if __name__ == "__main__":
    main()
