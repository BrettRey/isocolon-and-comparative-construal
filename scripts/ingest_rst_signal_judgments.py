#!/usr/bin/env python3
"""Merge downloaded RST-SC signal-crosswalk response JSON files.

Expected input files are the JSON downloads from ``rater_app/rst_signal_crosswalk.html``.
The script joins responses to the aggregate item manifest and writes derived
summary tables. It does not read the protected corpus.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RATER_APP = ROOT / "rater_app"
DERIVED_DIR = ROOT / "data" / "derived"


def read_items(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["item_id"]: row for row in csv.DictReader(handle, delimiter="\t")}


def response_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.glob("*.json"))


def read_payload(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or "responses" not in payload:
        raise ValueError(f"{path} is not an RST signal-crosswalk response JSON")
    return payload


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def flatten_responses(paths: list[Path], items: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in paths:
        payload = read_payload(path)
        coder = str(payload.get("coder", "")).strip()
        set_name = str(payload.get("set", "")).strip()
        saved_at = str(payload.get("saved_at", "")).strip()
        for response in payload.get("responses", []):
            if not isinstance(response, dict):
                continue
            item_id = str(response.get("item_id", ""))
            item = items.get(item_id, {})
            flags = response.get("flags", {})
            if not isinstance(flags, dict):
                flags = {}
            rows.append(
                {
                    "source_file": path.name,
                    "coder": coder,
                    "set": set_name,
                    "saved_at": saved_at,
                    "item_id": item_id,
                    "value": item.get("value", response.get("item_value", "")),
                    "n": item.get("n", response.get("n", "")),
                    "pct_of_slot_labels": item.get("pct_of_slot_labels", response.get("pct_of_slot_labels", "")),
                    "candidate_groups": item.get(
                        "candidate_groups",
                        ";".join(response.get("candidate_groups", []))
                        if isinstance(response.get("candidate_groups", []), list)
                        else response.get("candidate_groups", ""),
                    ),
                    "role": response.get("role", ""),
                    "use_level": response.get("use_level", ""),
                    "confidence": response.get("confidence", ""),
                    "broad_label": int(bool(flags.get("broad_label", False))),
                    "combined_label_needs_care": int(bool(flags.get("combined_label_needs_care", False))),
                    "needs_rency": int(bool(flags.get("needs_rency", False))),
                    "notes": response.get("notes", ""),
                    "updated_at": response.get("updated_at", ""),
                }
            )
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_value: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_value[str(row["item_id"])].append(row)

    summary = []
    for item_id, item_rows in sorted(by_value.items()):
        role_counts = Counter(str(row["role"]) for row in item_rows if row["role"])
        use_counts = Counter(str(row["use_level"]) for row in item_rows if row["use_level"])
        confidence_counts = Counter(str(row["confidence"]) for row in item_rows if row["confidence"])
        first = item_rows[0]
        summary.append(
            {
                "item_id": item_id,
                "value": first["value"],
                "n": first["n"],
                "candidate_groups": first["candidate_groups"],
                "n_coders": len({row["coder"] for row in item_rows if row["coder"]}),
                "roles": ";".join(f"{role}={count}" for role, count in sorted(role_counts.items())),
                "use_levels": ";".join(f"{level}={count}" for level, count in sorted(use_counts.items())),
                "confidence": ";".join(f"{level}={count}" for level, count in sorted(confidence_counts.items())),
                "needs_rency_n": sum(int(row["needs_rency"]) for row in item_rows),
                "complete_n": sum(1 for row in item_rows if row["role"] and row["use_level"] and row["confidence"]),
            }
        )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--responses", default=str(RATER_APP / "responses"))
    parser.add_argument("--items", default=str(RATER_APP / "rst_signal_crosswalk_items.tsv"))
    parser.add_argument("--outdir", default=str(DERIVED_DIR))
    args = parser.parse_args()

    paths = response_files(Path(args.responses))
    if not paths:
        raise SystemExit(f"No response JSON files found in {args.responses}")

    items = read_items(Path(args.items))
    rows = flatten_responses(paths, items)
    summary_rows = summarize(rows)
    outdir = Path(args.outdir)

    write_tsv(
        outdir / "rst_signal_crosswalk_judgments.tsv",
        [
            "source_file",
            "coder",
            "set",
            "saved_at",
            "item_id",
            "value",
            "n",
            "pct_of_slot_labels",
            "candidate_groups",
            "role",
            "use_level",
            "confidence",
            "broad_label",
            "combined_label_needs_care",
            "needs_rency",
            "notes",
            "updated_at",
        ],
        rows,
    )
    write_tsv(
        outdir / "rst_signal_crosswalk_judgment_summary.tsv",
        [
            "item_id",
            "value",
            "n",
            "candidate_groups",
            "n_coders",
            "roles",
            "use_levels",
            "confidence",
            "needs_rency_n",
            "complete_n",
        ],
        summary_rows,
    )

    print(f"Read {len(paths)} response file(s).")
    print(f"Wrote {outdir / 'rst_signal_crosswalk_judgments.tsv'}")
    print(f"Wrote {outdir / 'rst_signal_crosswalk_judgment_summary.tsv'}")
    print("No protected corpus files were read.")


if __name__ == "__main__":
    main()
