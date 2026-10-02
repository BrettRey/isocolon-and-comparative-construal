#!/usr/bin/env python3
"""Build the human coding page for the adversative-antithesis decomposition.

Reads the randomized 343-row worksheet, drops rows whose text is redacted
(GUM reddit documents ship as underscores), takes the first N remaining rows
as a fixed calibration batch, and recovers each pair's surrounding sentences
from the public GUM/GENTLE eRST release in ``data/raw/gum-erst``. Writes:

- ``rater_app/antithesis_items.tsv``: the batch manifest (one row per item)
- ``rater_app/antithesis_coding.html``: a self-contained coding page

The page keeps judgments in the coder's browser and exports them as TSV to the
clipboard. ``scripts/ingest_antithesis_codes.py`` merges pasted returns.
No LDC material is read.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DISRPT = ROOT / "data" / "raw" / "gum-erst" / "rst" / "disrpt"
TEMPLATE = ROOT / "rater_app" / "antithesis_coding_template.html"

MANIFEST_COLUMNS = [
    "code_id",
    "batch",
    "source_row",
    "doc",
    "collection",
    "genre",
    "rel_type",
    "doc_order",
    "word_len_1",
    "word_len_2",
    "unit1_text",
    "unit2_text",
    "context_found",
    "highlight_found",
]


def clean_text(value: str | None) -> str:
    return " ".join((value or "").split())


def is_redacted(text: str) -> bool:
    letters = [ch for ch in text if not ch.isspace()]
    return bool(letters) and sum(ch == "_" for ch in letters) / len(letters) > 0.5


def read_conllu_sentences(path: Path) -> dict[str, list[dict[str, object]]]:
    """Per document: sentences with raw text, speaker, and doc-level token span."""
    docs: dict[str, list[dict[str, object]]] = {}
    doc_id = ""
    tok_counter = 0
    meta: dict[str, str] = {}
    first_tok = None
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line.startswith("# newdoc id = "):
                doc_id = line.split("=", 1)[1].strip()
                docs[doc_id] = []
                tok_counter = 0
                continue
            if line.startswith("# text = "):
                meta["text"] = line.split("=", 1)[1].strip()
                continue
            if line.startswith("# speaker = "):
                meta["speaker"] = line.split("=", 1)[1].strip()
                continue
            if line.startswith("#"):
                continue
            if not line:
                if first_tok is not None:
                    docs[doc_id].append(
                        {
                            "text": meta.get("text", ""),
                            "speaker": meta.get("speaker", ""),
                            "start": first_tok,
                            "end": tok_counter,
                        }
                    )
                first_tok = None
                meta = {}
                continue
            tok_id = line.split("\t", 1)[0]
            if "-" in tok_id or "." in tok_id:
                continue
            tok_counter += 1
            if first_tok is None:
                first_tok = tok_counter
    return docs


def read_rels(path: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t", quoting=csv.QUOTE_NONE)
        return {(row["doc"], row["unit1_toks"], row["unit2_toks"]): row for row in reader}


def span_bounds(span_text: str) -> tuple[int, int]:
    numbers: list[int] = []
    for part in span_text.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            numbers.extend([int(lo), int(hi)])
        elif part:
            numbers.append(int(part))
    return min(numbers), max(numbers)


def segment_context(context: str, u1: str, u2: str) -> tuple[list[dict[str, str]], bool]:
    """Split context into plain / unit-a / unit-b runs. Returns (runs, found).

    Discontinuous eRST units arrive as fragments joined by ``<*>``; each
    fragment is located in order and highlighted separately.
    """
    hits = []
    for key, unit in (("a", u1), ("b", u2)):
        fragments = [frag.strip() for frag in unit.split("<*>") if frag.strip()]
        if not fragments:
            return [{"t": context, "k": ""}], False
        cursor = 0
        for frag in fragments:
            idx = context.find(frag, cursor)
            if idx < 0:
                return [{"t": context, "k": ""}], False
            hits.append((idx, idx + len(frag), key))
            cursor = idx + len(frag)
    hits.sort()
    if any(prev[1] > nxt[0] for prev, nxt in zip(hits, hits[1:])):
        return [{"t": context, "k": ""}], False
    runs: list[dict[str, str]] = []
    cursor = 0
    for start, end, key in hits:
        if start > cursor:
            runs.append({"t": context[cursor:start], "k": ""})
        runs.append({"t": context[start:end], "k": key})
        cursor = end
    if cursor < len(context):
        runs.append({"t": context[cursor:], "k": ""})
    return runs, True


def build_items(
    coding_path: Path, scores_path: Path, batch_size: int, defer: tuple[str, ...] = ()
) -> tuple[list[dict], int]:
    coding = pd.read_csv(coding_path, sep="\t")
    scores = pd.read_csv(scores_path, sep="\t")
    redacted = coding.apply(lambda r: is_redacted(str(r["unit1_text"]) + str(r["unit2_text"])), axis=1)
    usable = coding[~redacted].reset_index(drop=True)
    batch = usable.head(batch_size)
    # Deferred items stay in the batch but are shown last (e.g. profane threat letters,
    # so the page doesn't open on one). Membership of the batch is unchanged.
    deferred = batch["code_id"].isin(defer)
    batch = pd.concat([batch[~deferred], batch[deferred]])

    sentences: dict[str, dict[str, list[dict[str, object]]]] = {}
    rels: dict[str, dict[tuple[str, str, str], dict[str, str]]] = {}

    items = []
    for _, row in batch.iterrows():
        score_row = scores.loc[int(row["source_row"])]
        assert score_row["doc"] == row["doc"], row["code_id"]
        rels_file = str(score_row["source_file"])
        conllu_file = rels_file.replace(".rels", ".conllu")
        if rels_file not in rels:
            rels[rels_file] = read_rels(DISRPT / rels_file)
            sentences[conllu_file] = read_conllu_sentences(DISRPT / conllu_file)
        rel = rels[rels_file].get((row["doc"], str(score_row["unit1_toks"]), str(score_row["unit2_toks"])))

        u1 = clean_text(rel["u1_raw"]) if rel else clean_text(str(row["unit1_text"]))
        u2 = clean_text(rel["u2_raw"]) if rel else clean_text(str(row["unit2_text"]))

        doc_sents = sentences[conllu_file].get(row["doc"], [])
        lo = min(span_bounds(str(score_row["unit1_toks"]))[0], span_bounds(str(score_row["unit2_toks"]))[0])
        hi = max(span_bounds(str(score_row["unit1_toks"]))[1], span_bounds(str(score_row["unit2_toks"]))[1])
        covering = [i for i, s in enumerate(doc_sents) if s["end"] >= lo and s["start"] <= hi]
        context_found = bool(covering)
        before, core, after = [], [], []
        if covering:
            first, last = covering[0], covering[-1]
            before = doc_sents[max(0, first - 1) : first]
            core = doc_sents[first : last + 1]
            after = doc_sents[last + 1 : last + 2]

        def label(sent: dict[str, object]) -> str:
            return f"{sent['speaker']}: " if sent["speaker"] else ""

        core_text = " ".join(f"{label(s)}{s['text']}" for s in core)
        runs, highlight_found = segment_context(core_text, u1, u2)
        items.append(
            {
                "id": row["code_id"],
                "doc": row["doc"],
                "genre": row["genre"],
                "collection": row["collection"],
                "order": str(score_row["doc_order"]),
                "u1": u1,
                "u2": u2,
                "w1": int(row["word_len_1"]),
                "w2": int(row["word_len_2"]),
                "before": " ".join(f"{label(s)}{s['text']}" for s in before),
                "core": runs,
                "after": " ".join(f"{label(s)}{s['text']}" for s in after),
                "_source_row": int(row["source_row"]),
                "_rel_type": row["rel_type"],
                "_context_found": int(context_found),
                "_highlight_found": int(highlight_found),
            }
        )
    return items, int(redacted.sum())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coding", default="outputs/audit/adversative_antithesis_full_classical_coding.tsv")
    parser.add_argument("--scores", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    parser.add_argument("--batch-size", type=int, default=40)
    parser.add_argument("--batch-name", default="calibration")
    parser.add_argument(
        "--defer",
        default="AA012,AA013",
        help="Comma-separated code_ids to show at the end of the batch (default: the two profane GENTLE threat letters)",
    )
    parser.add_argument("--manifest-out", default="rater_app/antithesis_items.tsv")
    parser.add_argument("--html-out", default="rater_app/antithesis_coding.html")
    args = parser.parse_args()

    defer = tuple(code.strip() for code in args.defer.split(",") if code.strip())
    items, n_redacted = build_items(ROOT / args.coding, ROOT / args.scores, args.batch_size, defer)

    manifest_rows = [
        {
            "code_id": it["id"],
            "batch": args.batch_name,
            "source_row": it["_source_row"],
            "doc": it["doc"],
            "collection": it["collection"],
            "genre": it["genre"],
            "rel_type": it["_rel_type"],
            "doc_order": it["order"],
            "word_len_1": it["w1"],
            "word_len_2": it["w2"],
            "unit1_text": it["u1"],
            "unit2_text": it["u2"],
            "context_found": it["_context_found"],
            "highlight_found": it["_highlight_found"],
        }
        for it in items
    ]
    manifest_path = ROOT / args.manifest_out
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(manifest_rows)

    page_items = [{k: v for k, v in it.items() if not k.startswith("_")} for it in items]
    payload = json.dumps({"batch": args.batch_name, "items": page_items}, ensure_ascii=False)
    payload = payload.replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__ITEMS__*/null", payload)
    (ROOT / args.html_out).write_text(html, encoding="utf-8")

    no_context = sum(1 for it in items if not it["_context_found"])
    no_highlight = sum(1 for it in items if not it["_highlight_found"])
    print(f"Excluded {n_redacted} redacted rows; built {len(items)} '{args.batch_name}' items")
    print(f"Context not recovered: {no_context}; unit highlighting not located: {no_highlight}")
    print(f"Wrote {args.manifest_out} and {args.html_out}")


if __name__ == "__main__":
    main()
