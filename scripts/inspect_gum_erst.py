#!/usr/bin/env python3
"""Inspect the local GUM/eRST checkout and write derived inventory tables."""

from __future__ import annotations

import argparse
import csv
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

VALID_REL_TYPES = {"explicit", "implicit"}


def git_value(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    return result.stdout.strip()


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def split_file_parts(path: Path) -> tuple[str, str]:
    parts = path.name.split(".")
    if len(parts) >= 4:
        return parts[1], parts[2]
    return "", ""


def cell(row: dict[str, str | None], key: str) -> str:
    return row.get(key) or ""


def doc_parts(doc: str) -> tuple[str, str]:
    pieces = doc.split("_", 2)
    if len(pieces) >= 2:
        return pieces[0], pieces[1]
    return "", ""


def relation_inventory(corpus_root: Path) -> list[dict[str, object]]:
    counts: Counter[tuple[str, str, str, str, str, str]] = Counter()
    for rels_path in sorted((corpus_root / "rst" / "disrpt").glob("*.rels")):
        framework, partition = split_file_parts(rels_path)
        with rels_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                rel_type = cell(row, "rel_type")
                if rel_type not in VALID_REL_TYPES:
                    continue
                key = (
                    rels_path.name,
                    framework,
                    partition,
                    cell(row, "label"),
                    cell(row, "orig_label"),
                    rel_type,
                )
                counts[key] += 1
    return [
        {
            "source_file": source_file,
            "framework": framework,
            "partition": partition,
            "label": label,
            "orig_label": orig_label,
            "rel_type": rel_type,
            "n": n,
        }
        for (source_file, framework, partition, label, orig_label, rel_type), n in sorted(counts.items())
    ]


def disrpt_row_counts(corpus_root: Path) -> tuple[int, int]:
    valid = 0
    skipped = 0
    for rels_path in sorted((corpus_root / "rst" / "disrpt").glob("*.rels")):
        with rels_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                if cell(row, "rel_type") in VALID_REL_TYPES:
                    valid += 1
                else:
                    skipped += 1
    return valid, skipped


def signal_inventory(corpus_root: Path) -> list[dict[str, object]]:
    counts: Counter[tuple[str, str, str, str, str, str, str, str]] = Counter()
    for rs4_path in sorted((corpus_root / "rst" / "rstweb").glob("*.rs4")):
        collection, genre = doc_parts(rs4_path.stem)
        root = ET.parse(rs4_path).getroot()
        elements = {
            element.attrib["id"]: element
            for element in root.findall("./body/*")
            if element.tag in {"segment", "group"} and "id" in element.attrib
        }
        for signal in root.findall("./body/signals/signal"):
            source_id = signal.attrib.get("source", "")
            source_element = elements.get(source_id)
            source_tag = source_element.tag if source_element is not None else ""
            source_rel = source_element.attrib.get("relname", "") if source_element is not None else ""
            status = signal.attrib.get("status", "")
            key = (
                collection,
                genre,
                source_tag,
                source_rel,
                signal.attrib.get("type", ""),
                signal.attrib.get("subtype", ""),
                status,
                rs4_path.name,
            )
            counts[key] += 1
    return [
        {
            "collection": collection,
            "genre": genre,
            "source_element": source_element,
            "source_relation": source_relation,
            "signal_type": signal_type,
            "signal_subtype": signal_subtype,
            "status": status,
            "source_file": source_file,
            "n": n,
        }
        for (
            collection,
            genre,
            source_element,
            source_relation,
            signal_type,
            signal_subtype,
            status,
            source_file,
        ), n in sorted(counts.items())
    ]


def manifest_rows(corpus_root: Path) -> list[dict[str, object]]:
    root = corpus_root.resolve()
    valid_rels_rows, skipped_rels_rows = disrpt_row_counts(root)
    counts = {
        "dep_conllu_files": len(list((root / "dep").glob("*.conllu"))),
        "rstweb_rs4_files": len(list((root / "rst" / "rstweb").glob("*.rs4"))),
        "rst_dependency_rsd_files": len(list((root / "rst" / "dependencies").glob("*.rsd"))),
        "disrpt_rels_files": len(list((root / "rst" / "disrpt").glob("*.rels"))),
        "disrpt_conllu_files": len(list((root / "rst" / "disrpt").glob("*.conllu"))),
        "valid_disrpt_relation_rows": valid_rels_rows,
        "skipped_disrpt_rows": skipped_rels_rows,
    }
    rows = [
        {"key": "corpus_root", "value": str(root)},
        {"key": "git_tag", "value": git_value(root, "describe", "--tags", "--exact-match")},
        {"key": "git_commit", "value": git_value(root, "rev-parse", "HEAD")},
        {"key": "sparse_checkout", "value": ";".join(git_value(root, "sparse-checkout", "list").splitlines())},
    ]
    rows.extend({"key": key, "value": value} for key, value in counts.items())
    rows.append({"key": "rst_signalling_corpus", "value": "not_found_locally; LDC/Dataverse files are access restricted"})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", default="data/raw/gum-erst")
    parser.add_argument("--out-dir", default="data/derived")
    args = parser.parse_args()

    corpus_root = Path(args.corpus_root)
    out_dir = Path(args.out_dir)
    if not (corpus_root / "rst" / "rstweb").is_dir():
        raise SystemExit(f"Missing GUM/eRST rstweb directory: {corpus_root}")

    write_tsv(
        out_dir / "gum_erst_manifest.tsv",
        ["key", "value"],
        manifest_rows(corpus_root),
    )
    write_tsv(
        out_dir / "gum_erst_relation_inventory.tsv",
        ["source_file", "framework", "partition", "label", "orig_label", "rel_type", "n"],
        relation_inventory(corpus_root),
    )
    write_tsv(
        out_dir / "gum_erst_signal_inventory.tsv",
        [
            "collection",
            "genre",
            "source_element",
            "source_relation",
            "signal_type",
            "signal_subtype",
            "status",
            "source_file",
            "n",
        ],
        signal_inventory(corpus_root),
    )


if __name__ == "__main__":
    main()
