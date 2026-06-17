#!/usr/bin/env python3
"""Block likely restricted corpus data from entering the repo.

The script reports only paths and risk reasons. It does not print matched
content, so running it locally does not create another copy of protected data.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_SCAN_BYTES = 2_000_000
LARGE_DATA_BYTES = 2_000_000

POLICY_DOCS = {
    ".agent/ldc-enforcement-plan.md",
    ".githooks/pre-commit",
    "AGENTS.md",
    "CLAUDE.md",
    "DATA_POLICY.md",
    "GEMINI.md",
    "references.bib",
    "scripts/check_restricted_data.py",
}

ALLOWED_RAW_PLACEHOLDERS = {
    "data/raw/README.md",
}

BLOCKED_PREFIXES = (
    "data/ldc/",
    "outputs/restricted/",
    "restricted/",
)

DATA_EXTENSIONS = {
    ".ann",
    ".bio",
    ".cha",
    ".conll",
    ".conllu",
    ".csv",
    ".eaf",
    ".iob",
    ".json",
    ".jsonl",
    ".rels",
    ".rs4",
    ".sgm",
    ".sgml",
    ".tab",
    ".text",
    ".trs",
    ".tsv",
    ".txt",
    ".vrt",
    ".xml",
}

LDC_MARKERS = (
    re.compile(rb"\bLinguistic Data Consortium\b", re.IGNORECASE),
    re.compile(rb"\bLDC\s+Catalog\b", re.IGNORECASE),
    re.compile(rb"\bLDC\d{4}[A-Z]\d+\b"),
    re.compile(rb"\bsource[_-]?corpus\s*[:=]\s*['\"]?LDC\b", re.IGNORECASE),
    re.compile(rb"\blicense[_-]?class\s*[:=]\s*['\"]?LDC\b", re.IGNORECASE),
)

RESTRICTED_PATH_MARKERS = (
    re.compile(r"(^|/|\\)RestrictedCorpora(/|\\|$)", re.IGNORECASE),
    re.compile(r"(^|/|\\)LDC\d{4}[A-Z]\d+(/|\\|$)"),
    re.compile(r"(^|/|\\)ldc(/|\\|$)", re.IGNORECASE),
)
LDC_CATALOG_PATH_PATTERN = re.compile(r"\bLDC\d{4}[A-Z]\d+\b")


@dataclass
class Finding:
    path: str
    reason: str


def git(args: list[str], *, check: bool = True) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        raise SystemExit(result.returncode)
    return result.stdout


def split_nul(data: bytes) -> list[str]:
    return [item.decode("utf-8", errors="replace") for item in data.split(b"\0") if item]


def staged_paths() -> list[str]:
    return split_nul(git(["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMRT"]))


def repo_paths() -> list[str]:
    return split_nul(git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"]))


def staged_mode(path: str) -> str | None:
    rows = git(["ls-files", "-s", "--", path], check=False).decode("utf-8", errors="replace").splitlines()
    if not rows:
        return None
    return rows[0].split(maxsplit=1)[0]


def staged_blob(path: str) -> bytes:
    return git(["show", f":{path}"], check=False)


def staged_size(path: str) -> int:
    out = git(["cat-file", "-s", f":{path}"], check=False).strip()
    if not out:
        return 0
    try:
        return int(out)
    except ValueError:
        return 0


def worktree_blob(path: str, limit: int = MAX_SCAN_BYTES) -> bytes:
    full_path = REPO_ROOT / path
    try:
        with full_path.open("rb") as handle:
            return handle.read(limit)
    except OSError:
        return b""


def worktree_size(path: str) -> int:
    try:
        return (REPO_ROOT / path).stat().st_size
    except OSError:
        return 0


def is_symlink(path: str, *, staged: bool) -> bool:
    if staged:
        return staged_mode(path) == "120000"
    return (REPO_ROOT / path).is_symlink()


def symlink_target(path: str, *, staged: bool) -> str:
    if staged:
        return staged_blob(path).decode("utf-8", errors="replace").strip()
    try:
        return os.readlink(REPO_ROOT / path)
    except OSError:
        return ""


def normalize(path: str) -> str:
    return path.replace(os.sep, "/")


def path_findings(path: str, *, staged: bool) -> list[Finding]:
    path = normalize(path)
    findings: list[Finding] = []
    parts = path.split("/")
    lower_parts = [part.lower() for part in parts]

    if path.startswith("data/raw/") and path not in ALLOWED_RAW_PLACEHOLDERS:
        findings.append(Finding(path, "raw data path is not tracked"))

    for prefix in BLOCKED_PREFIXES:
        if path.startswith(prefix):
            findings.append(Finding(path, f"restricted path prefix `{prefix}`"))

    if any(part in {"ldc", "restricted", "restricted-data", "restricted_data"} for part in lower_parts):
        findings.append(Finding(path, "restricted/LDC path component"))

    if any(LDC_CATALOG_PATH_PATTERN.search(part) for part in parts):
        findings.append(Finding(path, "LDC catalog-style path component"))

    if is_symlink(path, staged=staged):
        target = symlink_target(path, staged=staged)
        if any(pattern.search(target) for pattern in RESTRICTED_PATH_MARKERS):
            findings.append(Finding(path, "symlink points toward a restricted corpus path"))

    return findings


def should_scan_content(path: str) -> bool:
    if path in POLICY_DOCS:
        return False
    suffix = Path(path).suffix.lower()
    return suffix in DATA_EXTENSIONS or "prompt" in Path(path).name.lower() or "/agent_reviews/" in path


def content_findings(path: str, *, staged: bool) -> list[Finding]:
    path = normalize(path)
    if not should_scan_content(path):
        return []

    size = staged_size(path) if staged else worktree_size(path)
    suffix = Path(path).suffix.lower()
    findings: list[Finding] = []

    if suffix in DATA_EXTENSIONS and size > LARGE_DATA_BYTES:
        findings.append(Finding(path, "large data-like file requires explicit aggregate review"))

    blob = staged_blob(path)[:MAX_SCAN_BYTES] if staged else worktree_blob(path)
    if b"\0" in blob:
        return findings

    if any(pattern.search(blob) for pattern in LDC_MARKERS):
        findings.append(Finding(path, "contains an LDC marker in a data-like or prompt-like file"))

    prompt_like = "prompt" in Path(path).name.lower() or "/agent_reviews/" in path
    if prompt_like and re.search(rb"\b(unit1_text|unit2_text|sentence|utterance|transcript)\b", blob, re.IGNORECASE):
        if re.search(rb"\b(LDC|RestrictedCorpora|restricted corpus)\b", blob, re.IGNORECASE):
            findings.append(Finding(path, "prompt/output appears to mix row-level text with restricted-source markers"))

    return findings


def unique_findings(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str]] = set()
    unique: list[Finding] = []
    for finding in findings:
        key = (finding.path, finding.reason)
        if key not in seen:
            seen.add(key)
            unique.append(finding)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="check only staged files")
    args = parser.parse_args()

    paths = staged_paths() if args.staged else repo_paths()
    findings: list[Finding] = []

    for path in paths:
        norm_path = normalize(path)
        findings.extend(path_findings(norm_path, staged=args.staged))
        findings.extend(content_findings(norm_path, staged=args.staged))

    findings = unique_findings(findings)

    if not findings:
        mode = "staged files" if args.staged else "tracked and unignored files"
        print(f"[DATA POLICY] OK: no restricted-data signals found in {mode}.")
        return 0

    print("[DATA POLICY] Blocked likely restricted corpus material:")
    for finding in findings:
        print(f"  - {finding.path}: {finding.reason}")
    print()
    print("Move restricted material to an ignored local path, remove the data,")
    print("or commit only aggregate/publication-cleared derivatives.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
