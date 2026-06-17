#!/usr/bin/env python3
"""Write aggregate inventories for the local RST Signalling Corpus.

This script is deliberately aggregate-only. It reads protected local files but
does not export document text, annotation notes, examples, or row-level records.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Iterable


ANNOTATION_DIR = Path("data") / "Annotations"
DEFAULT_OUT_DIR = Path("data") / "derived"
SPLIT_NAMES = {"Training_Annotation", "Test_Annotation", "Full_Annotation"}
CATEGORY_ATTRIBUTES = {
    "category",
    "direction",
    "kind",
    "nuclearity",
    "rel",
    "relation",
    "relname",
    "signal",
    "signalled",
    "source_rel",
    "status",
    "subtype",
    "type",
}
FEATURE_VECTOR_ATTRIBUTE = "features"
RELATION_ATTRIBUTES = {"rel", "relation", "relname", "source_rel"}
TYPE_ATTRIBUTES = {"type", "signal"}
SUBTYPE_ATTRIBUTES = {"subtype", "category"}
STATUS_ATTRIBUTES = {"status", "signalled"}
LABEL_PATTERN = re.compile(r"^[A-Za-z0-9_.:/;|,+() -]+$")
FORMAL_SIGNAL_PATTERNS = {
    "family_graphical": re.compile(r"graphical"),
    "family_lexical": re.compile(r"lexical"),
    "family_morphological": re.compile(r"morphological"),
    "family_numerical": re.compile(r"numerical"),
    "family_reference": re.compile(r"reference"),
    "family_semantic": re.compile(r"semantic"),
    "family_syntactic": re.compile(r"syntactic"),
    "subtype_antonymy": re.compile(r"antonymy"),
    "subtype_comparative_reference": re.compile(r"comparative_reference"),
    "subtype_lexical_chain": re.compile(r"lexical_chain"),
    "subtype_meronymy": re.compile(r"meronymy"),
    "subtype_parallel_syntactic_constructions": re.compile(r"parallel_syntactic_constructions"),
    "subtype_repetition": re.compile(r"repetition"),
    "subtype_synonymy": re.compile(r"synonymy"),
}


def write_tsv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_ldc_root(repo_root: Path) -> Path | None:
    local_pointer = repo_root / ".ldc-root"
    if local_pointer.is_file():
        value = local_pointer.read_text(encoding="utf-8").strip()
        if value:
            return Path(value).expanduser()
    env_value = os.environ.get("LDC_ROOT", "").strip()
    if env_value:
        return Path(env_value).expanduser()
    return None


def candidate_roots(repo_root: Path) -> list[Path]:
    roots: list[Path] = []
    env_value = os.environ.get("RST_SC_ROOT", "").strip()
    if env_value:
        roots.append(Path(env_value).expanduser())
    ldc_root = read_ldc_root(repo_root)
    if ldc_root is not None:
        roots.extend(
            [
                ldc_root / "LDC2015T10" / "RST_Signalling_Corpus",
                ldc_root / "RST_Signalling_Corpus",
            ]
        )
    return roots


def resolve_corpus_root(repo_root: Path, explicit: str | None) -> Path:
    candidates = [Path(explicit).expanduser()] if explicit else candidate_roots(repo_root)
    for candidate in candidates:
        root = candidate.resolve()
        if (root / ANNOTATION_DIR).is_dir():
            return root
    tried = "\n  - ".join(str(path) for path in candidates) or "(no candidates)"
    raise SystemExit(f"Could not find RST Signalling Corpus annotations. Tried:\n  - {tried}")


def split_name(path: Path) -> str:
    for part in path.parts:
        if part in SPLIT_NAMES:
            return part
    return "unknown"


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def safe_label(value: str) -> str:
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return ""
    if len(cleaned) > 80 or cleaned.count(" ") > 5 or not LABEL_PATTERN.match(cleaned):
        return "__redacted_nonlabel_value__"
    return cleaned


def category_value(attrs: dict[str, str], names: set[str]) -> str:
    for name in names:
        if name in attrs:
            return safe_label(attrs[name])
    return ""


def file_inventory(corpus_root: Path) -> list[dict[str, object]]:
    counts: Counter[tuple[str, str]] = Counter()
    annotation_root = corpus_root / ANNOTATION_DIR
    for path in annotation_root.rglob("*"):
        if path.is_file():
            suffix = path.suffix.lower().lstrip(".") or "(none)"
            counts[(split_name(path), suffix)] += 1
    return [
        {"split": split, "extension": extension, "n": n}
        for (split, extension), n in sorted(counts.items())
    ]


def xml_inventory(corpus_root: Path) -> tuple[
    Counter[tuple[str, str]],
    Counter[tuple[str, str, str]],
    Counter[tuple[str, str, str, str]],
    Counter[tuple[str, str, str, str, str]],
    Counter[tuple[str, int, str]],
    Counter[tuple[str, int]],
    Counter[str],
]:
    tag_counts: Counter[tuple[str, str]] = Counter()
    attr_counts: Counter[tuple[str, str, str]] = Counter()
    category_counts: Counter[tuple[str, str, str, str]] = Counter()
    relation_signal_counts: Counter[tuple[str, str, str, str, str]] = Counter()
    feature_slot_counts: Counter[tuple[str, int, str]] = Counter()
    feature_vector_length_counts: Counter[tuple[str, int]] = Counter()
    parse_errors: Counter[str] = Counter()

    for path in sorted((corpus_root / ANNOTATION_DIR).rglob("*.xml")):
        split = split_name(path)
        try:
            for _event, elem in ET.iterparse(path, events=("end",)):
                tag = local_name(elem.tag)
                tag_counts[(split, tag)] += 1
                attrs = {local_name(key): value for key, value in elem.attrib.items()}
                for attr_name, attr_value in attrs.items():
                    attr_counts[(split, tag, attr_name)] += 1
                    if attr_name in CATEGORY_ATTRIBUTES:
                        label = safe_label(attr_value)
                        if label:
                            category_counts[(split, tag, attr_name, label)] += 1

                feature_vector = attrs.get(FEATURE_VECTOR_ATTRIBUTE, "")
                if feature_vector:
                    feature_values = feature_vector.split(";")
                    feature_vector_length_counts[(split, len(feature_values))] += 1
                    for index, value in enumerate(feature_values, start=1):
                        label = safe_label(value)
                        if label:
                            feature_slot_counts[(split, index, label)] += 1

                relation = category_value(attrs, RELATION_ATTRIBUTES)
                signal_type = category_value(attrs, TYPE_ATTRIBUTES)
                signal_subtype = category_value(attrs, SUBTYPE_ATTRIBUTES)
                status = category_value(attrs, STATUS_ATTRIBUTES)
                if relation or signal_type or signal_subtype or status:
                    relation_signal_counts[(split, tag, relation, signal_type, signal_subtype)] += 1

                elem.clear()
        except ET.ParseError:
            parse_errors[split] += 1

    return (
        tag_counts,
        attr_counts,
        category_counts,
        relation_signal_counts,
        feature_slot_counts,
        feature_vector_length_counts,
        parse_errors,
    )


def child_text(element: ET.Element, child_name: str) -> str:
    for child in element:
        if local_name(child.tag) == child_name and child.text:
            return safe_label(child.text)
    return ""


def feature_schema_inventory(corpus_root: Path) -> list[dict[str, object]]:
    counts: Counter[tuple[str, str, str]] = Counter()
    for path in sorted((corpus_root / ANNOTATION_DIR).rglob("*.xml")):
        split = split_name(path)
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            continue
        for feature in tree.iter():
            if local_name(feature.tag) != "FEATURE":
                continue
            feature_name = child_text(feature, "NAME")
            if not feature_name:
                continue
            states = []
            for state in feature.iter():
                if local_name(state.tag) == "STATE":
                    state_name = child_text(state, "NAME")
                    if state_name:
                        states.append(state_name)
            if states:
                for state_name in states:
                    counts[(split, feature_name, state_name)] += 1
            else:
                counts[(split, feature_name, "")] += 1
    return [
        {"split": split, "feature": feature, "state": state, "n": n}
        for (split, feature, state), n in sorted(counts.items())
    ]


def manifest_rows(corpus_root: Path, parse_errors: Counter[str]) -> list[dict[str, object]]:
    annotation_root = corpus_root / ANNOTATION_DIR
    rows: list[dict[str, object]] = [
        {"key": "corpus_root", "value": str(corpus_root)},
        {"key": "annotation_root", "value": str(annotation_root)},
        {"key": "raw_text_exported", "value": "no"},
        {"key": "row_level_records_exported", "value": "no"},
    ]
    for split in sorted(SPLIT_NAMES):
        split_root = annotation_root / split
        rows.append({"key": f"{split}.exists", "value": str(split_root.is_dir()).lower()})
        rows.append({"key": f"{split}.xml_files", "value": len(list(split_root.rglob("*.xml"))) if split_root.is_dir() else 0})
        rows.append({"key": f"{split}.txt_files", "value": len(list(split_root.rglob("*.txt"))) if split_root.is_dir() else 0})
        rows.append({"key": f"{split}.parse_errors", "value": parse_errors.get(split, 0)})
    return rows


def counter_rows(counter: Counter[tuple[object, ...]], fields: list[str]) -> list[dict[str, object]]:
    rows = []
    for key, n in sorted(counter.items()):
        row = {field: value for field, value in zip(fields, key)}
        row["n"] = n
        rows.append(row)
    return rows


def formal_signal_summary(feature_slot_counts: Counter[tuple[str, int, str]]) -> list[dict[str, object]]:
    rows = []
    for (split, slot_index, value), n in sorted(feature_slot_counts.items()):
        for group, pattern in FORMAL_SIGNAL_PATTERNS.items():
            if pattern.search(value):
                rows.append(
                    {
                        "split": split,
                        "candidate_group": group,
                        "slot_index": slot_index,
                        "value": value,
                        "n": n,
                    }
                )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", default=None, help="Path to RST_Signalling_Corpus")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    corpus_root = resolve_corpus_root(repo_root, args.corpus_root)
    out_dir = Path(args.out_dir)

    (
        tag_counts,
        attr_counts,
        category_counts,
        relation_signal_counts,
        feature_slot_counts,
        feature_vector_length_counts,
        parse_errors,
    ) = xml_inventory(corpus_root)

    write_tsv(out_dir / "rst_sc_manifest.tsv", ["key", "value"], manifest_rows(corpus_root, parse_errors))
    write_tsv(out_dir / "rst_sc_file_inventory.tsv", ["split", "extension", "n"], file_inventory(corpus_root))
    write_tsv(out_dir / "rst_sc_xml_tag_inventory.tsv", ["split", "tag", "n"], counter_rows(tag_counts, ["split", "tag"]))
    write_tsv(
        out_dir / "rst_sc_xml_attribute_inventory.tsv",
        ["split", "tag", "attribute", "n"],
        counter_rows(attr_counts, ["split", "tag", "attribute"]),
    )
    write_tsv(
        out_dir / "rst_sc_category_inventory.tsv",
        ["split", "tag", "attribute", "value", "n"],
        counter_rows(category_counts, ["split", "tag", "attribute", "value"]),
    )
    write_tsv(
        out_dir / "rst_sc_relation_signal_inventory.tsv",
        ["split", "tag", "relation", "signal_type", "signal_subtype", "n"],
        counter_rows(relation_signal_counts, ["split", "tag", "relation", "signal_type", "signal_subtype"]),
    )
    write_tsv(
        out_dir / "rst_sc_feature_vector_length_inventory.tsv",
        ["split", "feature_count", "n"],
        counter_rows(feature_vector_length_counts, ["split", "feature_count"]),
    )
    write_tsv(
        out_dir / "rst_sc_feature_slot_inventory.tsv",
        ["split", "slot_index", "value", "n"],
        counter_rows(feature_slot_counts, ["split", "slot_index", "value"]),
    )
    write_tsv(
        out_dir / "rst_sc_feature_schema_inventory.tsv",
        ["split", "feature", "state", "n"],
        feature_schema_inventory(corpus_root),
    )
    write_tsv(
        out_dir / "rst_sc_formal_signal_candidate_summary.tsv",
        ["split", "candidate_group", "slot_index", "value", "n"],
        formal_signal_summary(feature_slot_counts),
    )

    print(f"Wrote aggregate RST-SC inventories to {out_dir}")
    print("No raw text or row-level records were exported.")


if __name__ == "__main__":
    main()
