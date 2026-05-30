#!/usr/bin/env python3
"""Score first-pass isocolonicity for GUM/eRST adjacent relation pairs."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

CONTENT_UPOS = {"ADJ", "ADV", "NOUN", "NUM", "PROPN", "VERB"}
WORD_UPOS_EXCLUDE = {"PUNCT"}
VOWELS = "aeiouy"


def clean_deprel(value: str) -> str:
    return value.split(":", 1)[0]


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


def ratio_balance(n1: int, n2: int) -> float:
    if n1 <= 0 or n2 <= 0:
        return 0.0
    return 1 - abs(n1 - n2) / max(n1, n2)


def edit_similarity(seq1: list[str], seq2: list[str]) -> float:
    if not seq1 and not seq2:
        return 1.0
    if not seq1 or not seq2:
        return 0.0
    previous = list(range(len(seq2) + 1))
    for i, item1 in enumerate(seq1, 1):
        current = [i]
        for j, item2 in enumerate(seq2, 1):
            current.append(
                min(
                    current[j - 1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (item1 != item2),
                )
            )
        previous = current
    return 1 - previous[-1] / max(len(seq1), len(seq2))


def jaccard(items1: set[str], items2: set[str]) -> float:
    if not items1 and not items2:
        return 0.0
    union = items1 | items2
    if not union:
        return 0.0
    return len(items1 & items2) / len(union)


def approx_syllables(form: str) -> int:
    word = re.sub(r"[^a-z]", "", form.lower())
    if not word:
        return 0
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    if len(word) > 3 and word.endswith("e") and not word.endswith(("le", "ye")):
        count -= 1
    return max(1, count)


def parse_conllu(path: Path) -> dict[int, dict[str, str | int]]:
    tokens: dict[int, dict[str, str | int]] = {}
    global_id = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 10 or "-" in fields[0] or "." in fields[0]:
                continue
            global_id += 1
            tokens[global_id] = {
                "global_id": global_id,
                "form": fields[1],
                "lemma": fields[2].lower(),
                "upos": fields[3],
                "xpos": fields[4],
                "deprel": clean_deprel(fields[7]),
                "misc": fields[9],
            }
    return tokens


def word_tokens(tokens: list[dict[str, str | int]]) -> list[dict[str, str | int]]:
    return [token for token in tokens if str(token["upos"]) not in WORD_UPOS_EXCLUDE]


def score_pair(
    row: dict[str, str],
    docs: dict[str, dict[int, dict[str, str | int]]],
    dep_dir: Path,
) -> dict[str, object]:
    doc = row["doc"]
    if doc not in docs:
        docs[doc] = parse_conllu(dep_dir / f"{doc}.conllu")
    doc_tokens = docs[doc]

    unit1 = [doc_tokens[num] for num in span_numbers(row["unit1_toks"]) if num in doc_tokens]
    unit2 = [doc_tokens[num] for num in span_numbers(row["unit2_toks"]) if num in doc_tokens]
    unit1_words = word_tokens(unit1)
    unit2_words = word_tokens(unit2)

    unit1_forms = [str(token["form"]) for token in unit1_words]
    unit2_forms = [str(token["form"]) for token in unit2_words]
    unit1_lemmas = [str(token["lemma"]) for token in unit1_words]
    unit2_lemmas = [str(token["lemma"]) for token in unit2_words]
    unit1_upos = [str(token["upos"]) for token in unit1_words]
    unit2_upos = [str(token["upos"]) for token in unit2_words]
    unit1_xpos = [str(token["xpos"]) for token in unit1_words]
    unit2_xpos = [str(token["xpos"]) for token in unit2_words]
    unit1_deprels = [str(token["deprel"]) for token in unit1_words]
    unit2_deprels = [str(token["deprel"]) for token in unit2_words]

    unit1_syllables = sum(approx_syllables(form) for form in unit1_forms)
    unit2_syllables = sum(approx_syllables(form) for form in unit2_forms)
    unit1_chars = sum(len(re.sub(r"\W+", "", form, flags=re.UNICODE)) for form in unit1_forms)
    unit2_chars = sum(len(re.sub(r"\W+", "", form, flags=re.UNICODE)) for form in unit2_forms)

    token_balance = ratio_balance(len(unit1_words), len(unit2_words))
    char_balance = ratio_balance(unit1_chars, unit2_chars)
    syllable_balance = ratio_balance(unit1_syllables, unit2_syllables)
    length_score = (token_balance + char_balance + syllable_balance) / 3

    upos_similarity = edit_similarity(unit1_upos, unit2_upos)
    xpos_similarity = edit_similarity(unit1_xpos, unit2_xpos)
    deprel_similarity = edit_similarity(unit1_deprels, unit2_deprels)
    syntax_score = (upos_similarity + xpos_similarity + deprel_similarity) / 3

    lemma_sequence_similarity = edit_similarity(unit1_lemmas, unit2_lemmas)
    content1 = {
        str(token["lemma"])
        for token in unit1_words
        if str(token["upos"]) in CONTENT_UPOS and str(token["lemma"]) != "_"
    }
    content2 = {
        str(token["lemma"])
        for token in unit2_words
        if str(token["upos"]) in CONTENT_UPOS and str(token["lemma"]) != "_"
    }
    content_lemma_jaccard = jaccard(content1, content2)
    lexical_score = (lemma_sequence_similarity + content_lemma_jaccard) / 2

    isocolon_score = 0.40 * length_score + 0.45 * syntax_score + 0.15 * lexical_score
    has_gold_syn_prl = any("syn-prl" in str(token["misc"]) for token in unit1 + unit2)

    scored = dict(row)
    scored.update(
        {
            "word_len_1": len(unit1_words),
            "word_len_2": len(unit2_words),
            "char_len_1": unit1_chars,
            "char_len_2": unit2_chars,
            "syllable_len_1": unit1_syllables,
            "syllable_len_2": unit2_syllables,
            "word_token_balance": f"{token_balance:.4f}",
            "char_balance": f"{char_balance:.4f}",
            "syllable_balance": f"{syllable_balance:.4f}",
            "length_score": f"{length_score:.4f}",
            "upos_similarity": f"{upos_similarity:.4f}",
            "xpos_similarity": f"{xpos_similarity:.4f}",
            "deprel_similarity": f"{deprel_similarity:.4f}",
            "syntax_score": f"{syntax_score:.4f}",
            "lemma_sequence_similarity": f"{lemma_sequence_similarity:.4f}",
            "content_lemma_jaccard": f"{content_lemma_jaccard:.4f}",
            "lexical_score": f"{lexical_score:.4f}",
            "isocolon_score": f"{isocolon_score:.4f}",
            "has_gold_syn_prl": int(has_gold_syn_prl),
        }
    )
    return scored


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", default="data/derived/gum_erst_adjacent_relation_pairs.tsv")
    parser.add_argument("--dep-dir", default="data/raw/gum-erst/dep")
    parser.add_argument("--out", default="data/derived/gum_erst_adjacent_isocolon_scores.tsv")
    args = parser.parse_args()

    docs: dict[str, dict[int, dict[str, str | int]]] = {}
    with Path(args.pairs).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = [score_pair(row, docs, Path(args.dep_dir)) for row in reader]

    fieldnames = list(rows[0].keys()) if rows else []
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
