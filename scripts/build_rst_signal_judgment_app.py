#!/usr/bin/env python3
"""Build an offline human judgment app for RST-SC signal-label crosswalks.

The input is the aggregate-only formal-signal inventory produced by
``inspect_rst_signalling.py`` and summarized by ``summarize_rst_signalling.py``.
This builder does not read protected corpus files and does not emit raw text,
row-level records, prompts, or examples.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED_DIR = ROOT / "data" / "derived"
OUTDIR = ROOT / "rater_app"
SETNAME = "rst_signal_crosswalk_v1"
SPLIT = "Full_Annotation"
SLOT_INDEX = 4

ROLE_OPTIONS = [
    {
        "value": "parison_or_syntactic_parallelism",
        "label": "Parison-like form",
        "description": "Formal or syntactic parallelism relevant to isocolon or parison.",
    },
    {
        "value": "lexical_echo",
        "label": "Lexical echo",
        "description": "Repetition, lexical-chain, synonymy, or other lexical recurrence.",
    },
    {
        "value": "comparison_reference",
        "label": "Comparison reference",
        "description": "Explicit comparative-reference signalling, not necessarily formal balance.",
    },
    {
        "value": "semantic_opposition",
        "label": "Semantic opposition",
        "description": "Antonymy or contrast-like semantic opposition.",
    },
    {
        "value": "exclusion_control",
        "label": "Exclude/control",
        "description": "Useful as a control or exclusion, but not paper-facing evidence.",
    },
    {
        "value": "unresolved",
        "label": "Unresolved",
        "description": "Cannot be safely mapped without more annotation context.",
    },
]

USE_OPTIONS = [
    {
        "value": "direct_evidence",
        "label": "Direct evidence",
        "description": "Can support a paper-facing claim after ordinary caveats.",
    },
    {
        "value": "context_only",
        "label": "Context only",
        "description": "Can describe the annotation environment but not confirm the phenomenon.",
    },
    {
        "value": "exclude",
        "label": "Exclude",
        "description": "Should not be used in the paper's quantitative interpretation.",
    },
]

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>RST-SC signal crosswalk</title>
<style>
:root {
  color-scheme: light;
  --ink: #1f2933;
  --muted: #64748b;
  --line: #cbd5e1;
  --panel: #f8fafc;
  --accent: #2563eb;
  --accent-soft: #dbeafe;
  --ok: #047857;
  --warn: #b45309;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  line-height: 1.45;
  background: #ffffff;
}
main {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px;
}
h1, h2 {
  margin: 0 0 12px;
  font-weight: 650;
  letter-spacing: 0;
}
h1 { font-size: 1.65rem; }
h2 { font-size: 1.28rem; }
p { margin: 0 0 14px; }
button, input, textarea {
  font: inherit;
}
.topline {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 18px;
}
.muted { color: var(--muted); }
.small { font-size: .9rem; }
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px;
}
.notice {
  border-left: 4px solid var(--warn);
  background: #fff7ed;
  padding: 12px 14px;
  margin: 16px 0;
}
.field {
  display: grid;
  gap: 8px;
  margin: 16px 0;
}
input[type="text"] {
  width: min(100%, 360px);
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 6px;
}
textarea {
  width: 100%;
  min-height: 86px;
  resize: vertical;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 6px;
}
.bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
}
.bar > div {
  height: 100%;
  background: var(--accent);
}
.label-card {
  margin: 18px 0;
  padding: 20px;
  border: 1px solid var(--line);
  border-radius: 8px;
}
.signal {
  overflow-wrap: anywhere;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 1.35rem;
  line-height: 1.35;
  margin: 8px 0 14px;
}
.facts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 12px 0;
}
.fact {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 10px;
}
.fact strong {
  display: block;
  font-size: .82rem;
  color: var(--muted);
  font-weight: 600;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0 0;
}
.chip {
  border: 1px solid #bfdbfe;
  background: var(--accent-soft);
  color: #1e3a8a;
  border-radius: 999px;
  padding: 4px 9px;
  font-size: .85rem;
  overflow-wrap: anywhere;
}
.option-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 10px 0 18px;
}
.option {
  width: 100%;
  min-height: 86px;
  text-align: left;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  color: var(--ink);
  cursor: pointer;
  padding: 12px;
}
.option:hover {
  border-color: var(--accent);
  background: #f8fbff;
}
.option.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
  box-shadow: inset 0 0 0 1px var(--accent);
}
.option b {
  display: block;
  margin-bottom: 4px;
}
.segmented {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0 18px;
}
.segmented button {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 999px;
  padding: 9px 12px;
  cursor: pointer;
}
.segmented button.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
  color: #1e3a8a;
}
.checks {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin: 8px 0 18px;
}
.checks label { cursor: pointer; }
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-top: 18px;
}
.primary, .secondary {
  border-radius: 7px;
  padding: 10px 16px;
  cursor: pointer;
}
.primary {
  border: 1px solid var(--accent);
  background: var(--accent);
  color: #fff;
}
.secondary {
  border: 1px solid var(--line);
  background: #fff;
  color: var(--ink);
}
button:disabled {
  opacity: .45;
  cursor: default;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 14px;
  font-size: .92rem;
}
th, td {
  border-bottom: 1px solid #e2e8f0;
  padding: 8px;
  text-align: left;
  vertical-align: top;
}
@media (max-width: 720px) {
  main { padding: 18px; }
  .topline { display: block; }
  .facts, .option-grid { grid-template-columns: 1fr; }
  .signal { font-size: 1.12rem; }
}
</style>
</head>
<body>
<main id="app"></main>
<script>
const ITEMS = __ITEMS__;
const ROLE_OPTIONS = __ROLE_OPTIONS__;
const USE_OPTIONS = __USE_OPTIONS__;
const META = __META__;
const app = document.getElementById("app");
const $ = id => document.getElementById(id);
let coder = "";
let idx = 0;
let responses = {};

function cleanId(value) {
  return value.replace(/[^A-Za-z0-9_-]/g, "");
}
function storageKey() {
  return "rst_signal_crosswalk_" + META.set + "_" + cleanId(coder);
}
function save() {
  if (!coder) return;
  try {
    localStorage.setItem(storageKey(), JSON.stringify({idx, responses}));
  } catch (err) {}
}
function restore() {
  try {
    const raw = localStorage.getItem(storageKey());
    if (!raw) return false;
    const parsed = JSON.parse(raw);
    idx = Number.isInteger(parsed.idx) ? parsed.idx : 0;
    responses = parsed.responses || {};
    return true;
  } catch (err) {
    return false;
  }
}
function currentItem() {
  return ITEMS[idx];
}
function responseFor(item) {
  const stored = responses[item.item_id] || {};
  return {
    item_id: item.item_id,
    role: "",
    use_level: "",
    confidence: "",
    flags: {
      broad_label: false,
      combined_label_needs_care: item.combined_label,
      needs_rency: false
    },
    notes: "",
    ...stored,
    flags: {
      broad_label: false,
      combined_label_needs_care: item.combined_label,
      needs_rency: false,
      ...(stored.flags || {})
    }
  };
}
function setResponse(item, patch) {
  const current = responseFor(item);
  responses[item.item_id] = {...current, ...patch, item_id: item.item_id, updated_at: new Date().toISOString()};
  save();
}
function completeCount() {
  return ITEMS.filter(item => {
    const r = responses[item.item_id];
    return r && r.role && r.use_level && r.confidence;
  }).length;
}
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
}
function optionButtons(options, selected, kind) {
  return options.map(opt => `<button class="option ${selected === opt.value ? "selected" : ""}" data-${kind}="${escapeHtml(opt.value)}"><b>${escapeHtml(opt.label)}</b><span>${escapeHtml(opt.description)}</span></button>`).join("");
}
function confidenceButtons(selected) {
  return [1, 2, 3].map(n => {
    const labels = {1: "Low", 2: "Medium", 3: "High"};
    return `<button class="${String(selected) === String(n) ? "selected" : ""}" data-confidence="${n}">${n} - ${labels[n]}</button>`;
  }).join("");
}
function startScreen() {
  app.innerHTML = `<h1>RST-SC signal crosswalk</h1>
    <p class="muted">Offline human coding interface for aggregate signal-label judgments.</p>
    <div class="notice">This app contains aggregate label names and counts only. Do not paste corpus text, examples, screenshots with restricted text, or raw LDC files into the notes.</div>
    <div class="panel">
      <p>Classify each RST Signalling Corpus label into the role it can safely play in the isocolon paper. The task is not to judge passages or infer rhetorical intent from examples. It is a label-level crosswalk.</p>
      <p>Responses stay in this browser until downloaded as JSON. No network, server, or AI service is used.</p>
      <div class="field">
        <label for="coder"><b>Name or initials</b></label>
        <input type="text" id="coder" placeholder="e.g. BR or Rency" autofocus>
      </div>
      <button class="primary" id="begin">Begin</button>
    </div>`;
  $("begin").onclick = begin;
  $("coder").onkeydown = event => {
    if (event.key === "Enter") begin();
  };
}
function begin() {
  const value = $("coder").value.trim();
  if (!value) return;
  coder = value;
  restore();
  instructionsScreen();
}
function instructionsScreen() {
  app.innerHTML = `<h1>Instructions</h1>
    <div class="panel">
      <p>For each aggregate label, choose one paper-facing role, one use level, and a confidence rating.</p>
      <p>Use <b>Direct evidence</b> only when the label can support the paper's formal-balance or comparison claim without needing row-level examples. Use <b>Context only</b> when the label is informative about the annotation scheme but too broad or indirect for confirmation. Use <b>Exclude</b> when it should stay out of interpretation.</p>
      <p>Combined labels count as one aggregate label here. Treat broad labels such as lexical chains cautiously; the count can reflect annotation design rather than a rhetorical pattern.</p>
    </div>
    <div class="actions">
      <button class="primary" id="start">${completeCount() ? "Resume" : "Start"} coding</button>
      <button class="secondary" id="download">Download current JSON</button>
    </div>
    <p class="muted small">${ITEMS.length} aggregate labels in ${META.split}, slot ${META.slot_index}.</p>`;
  $("start").onclick = itemScreen;
  $("download").onclick = download;
}
function itemScreen() {
  if (idx >= ITEMS.length) return reviewScreen();
  const item = currentItem();
  const response = responseFor(item);
  const progress = Math.round((idx / ITEMS.length) * 100);
  app.innerHTML = `<div class="topline">
      <div>
        <h1>Signal label ${idx + 1} of ${ITEMS.length}</h1>
        <p class="muted">${completeCount()} complete</p>
      </div>
      <button class="secondary" id="download">Download JSON</button>
    </div>
    <div class="bar"><div style="width:${progress}%"></div></div>
    <section class="label-card">
      <div class="muted small">Aggregate label value</div>
      <div class="signal">${escapeHtml(item.value)}</div>
      <div class="facts">
        <div class="fact"><strong>Count</strong>${item.n}</div>
        <div class="fact"><strong>Slot share</strong>${item.pct_of_slot_labels}%</div>
        <div class="fact"><strong>Combined label</strong>${item.combined_label ? "yes" : "no"}</div>
      </div>
      <div class="muted small">Candidate memberships</div>
      <div class="chips">${item.candidate_groups.map(group => `<span class="chip">${escapeHtml(group)}</span>`).join("")}</div>
    </section>

    <h2>Paper-facing role</h2>
    <div class="option-grid" id="roles">${optionButtons(ROLE_OPTIONS, response.role, "role")}</div>

    <h2>Use level</h2>
    <div class="option-grid" id="uses">${optionButtons(USE_OPTIONS, response.use_level, "use")}</div>

    <h2>Confidence</h2>
    <div class="segmented" id="confidence">${confidenceButtons(response.confidence)}</div>

    <h2>Flags</h2>
    <div class="checks">
      <label><input type="checkbox" id="broad" ${response.flags.broad_label ? "checked" : ""}> broad label</label>
      <label><input type="checkbox" id="combined" ${response.flags.combined_label_needs_care ? "checked" : ""}> combined label needs care</label>
      <label><input type="checkbox" id="rency" ${response.flags.needs_rency ? "checked" : ""}> needs Rency/Brett follow-up</label>
    </div>

    <div class="field">
      <label for="notes"><b>Notes</b> <span class="muted">(label-level only; no restricted text)</span></label>
      <textarea id="notes">${escapeHtml(response.notes || "")}</textarea>
    </div>

    <div class="actions">
      <button class="secondary" id="prev" ${idx === 0 ? "disabled" : ""}>Previous</button>
      <button class="primary" id="next">${idx + 1 === ITEMS.length ? "Review" : "Next"}</button>
      <button class="secondary" id="finish">Review all</button>
    </div>`;
  $("download").onclick = download;
  $("prev").onclick = () => {
    captureFreeText();
    idx = Math.max(0, idx - 1);
    save();
    itemScreen();
  };
  $("next").onclick = () => {
    captureFreeText();
    idx += 1;
    save();
    itemScreen();
  };
  $("finish").onclick = () => {
    captureFreeText();
    idx = ITEMS.length;
    save();
    reviewScreen();
  };
  document.querySelectorAll("[data-role]").forEach(button => {
    button.onclick = () => {
      setResponse(item, {role: button.dataset.role});
      itemScreen();
    };
  });
  document.querySelectorAll("[data-use]").forEach(button => {
    button.onclick = () => {
      setResponse(item, {use_level: button.dataset.use});
      itemScreen();
    };
  });
  document.querySelectorAll("[data-confidence]").forEach(button => {
    button.onclick = () => {
      setResponse(item, {confidence: button.dataset.confidence});
      itemScreen();
    };
  });
  ["broad", "combined", "rency"].forEach(id => {
    $(id).onchange = () => {
      const flags = {
        broad_label: $("broad").checked,
        combined_label_needs_care: $("combined").checked,
        needs_rency: $("rency").checked
      };
      setResponse(item, {flags});
    };
  });
  $("notes").oninput = () => captureFreeText();
}
function captureFreeText() {
  if (idx >= ITEMS.length) return;
  const item = currentItem();
  const notes = $("notes") ? $("notes").value : responseFor(item).notes;
  const flags = {
    broad_label: $("broad") ? $("broad").checked : responseFor(item).flags.broad_label,
    combined_label_needs_care: $("combined") ? $("combined").checked : responseFor(item).flags.combined_label_needs_care,
    needs_rency: $("rency") ? $("rency").checked : responseFor(item).flags.needs_rency
  };
  setResponse(item, {notes, flags});
}
function reviewScreen() {
  idx = ITEMS.length;
  save();
  const rows = ITEMS.map((item, i) => {
    const response = responseFor(item);
    const done = response.role && response.use_level && response.confidence;
    return `<tr>
      <td>${i + 1}</td>
      <td><code>${escapeHtml(item.value)}</code></td>
      <td>${escapeHtml(response.role || "")}</td>
      <td>${escapeHtml(response.use_level || "")}</td>
      <td>${escapeHtml(response.confidence || "")}</td>
      <td>${done ? "complete" : "missing"}</td>
    </tr>`;
  }).join("");
  app.innerHTML = `<div class="topline">
      <div>
        <h1>Review</h1>
        <p class="muted">${completeCount()} of ${ITEMS.length} labels complete.</p>
      </div>
      <button class="primary" id="download">Download JSON</button>
    </div>
    <div class="actions">
      <button class="secondary" id="back">Back to last item</button>
      <button class="secondary" id="firstMissing">First missing</button>
    </div>
    <table>
      <thead><tr><th>#</th><th>Label</th><th>Role</th><th>Use</th><th>Confidence</th><th>Status</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
  $("download").onclick = download;
  $("back").onclick = () => {
    idx = Math.max(0, ITEMS.length - 1);
    save();
    itemScreen();
  };
  $("firstMissing").onclick = () => {
    const missing = ITEMS.findIndex(item => {
      const response = responses[item.item_id];
      return !(response && response.role && response.use_level && response.confidence);
    });
    idx = missing >= 0 ? missing : 0;
    save();
    itemScreen();
  };
}
function download() {
  const responseArray = ITEMS.map(item => {
    const response = responseFor(item);
    return {
      ...response,
      item_value: item.value,
      n: item.n,
      pct_of_slot_labels: item.pct_of_slot_labels,
      candidate_groups: item.candidate_groups
    };
  });
  const payload = {
    coder,
    set: META.set,
    generated_from: META.generated_from,
    saved_at: new Date().toISOString(),
    n_items: ITEMS.length,
    n_complete: completeCount(),
    responses: responseArray
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], {type: "application/json"});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "rst_signal_crosswalk_" + cleanId(coder || "coder") + "_" + new Date().toISOString().slice(0, 10) + ".json";
  document.body.appendChild(link);
  link.click();
  link.remove();
}
startScreen();
</script>
</body>
</html>
"""


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def slot_total(slot_rows: list[dict[str, str]], split: str, slot_index: int) -> int:
    return sum(
        int(row["n"])
        for row in slot_rows
        if row["split"] == split and int(row["slot_index"]) == slot_index
    )


def pct(value: int, total: int) -> str:
    if total <= 0:
        return ""
    return f"{100 * value / total:.2f}"


def build_items(derived_dir: Path) -> list[dict[str, object]]:
    candidate_rows = read_tsv(derived_dir / "rst_sc_formal_signal_candidate_summary.tsv")
    slot_rows = read_tsv(derived_dir / "rst_sc_feature_slot_inventory.tsv")
    total = slot_total(slot_rows, SPLIT, SLOT_INDEX)

    grouped: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidate_rows:
        if row["split"] != SPLIT or int(row["slot_index"]) != SLOT_INDEX:
            continue
        grouped[row["value"]].append(row)

    items = []
    for ordinal, (value, rows) in enumerate(
        sorted(grouped.items(), key=lambda item: (-max(int(row["n"]) for row in item[1]), item[0])),
        1,
    ):
        count = max(int(row["n"]) for row in rows)
        candidate_groups = sorted({row["candidate_group"] for row in rows})
        items.append(
            {
                "item_id": f"rstsc_s{SLOT_INDEX}_{ordinal:03d}",
                "split": SPLIT,
                "slot_index": SLOT_INDEX,
                "value": value,
                "n": count,
                "pct_of_slot_labels": pct(count, total),
                "candidate_groups": candidate_groups,
                "combined_label": value.startswith("(") and "+" in value,
                "source": "data/derived/rst_sc_formal_signal_candidate_summary.tsv",
            }
        )
    return items


def write_items_tsv(path: Path, items: list[dict[str, object]]) -> None:
    fieldnames = [
        "item_id",
        "split",
        "slot_index",
        "value",
        "n",
        "pct_of_slot_labels",
        "candidate_groups",
        "combined_label",
        "source",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for item in items:
            row = dict(item)
            row["candidate_groups"] = ";".join(item["candidate_groups"])
            writer.writerow(row)


def write_html(path: Path, items: list[dict[str, object]]) -> None:
    metadata = {
        "set": SETNAME,
        "split": SPLIT,
        "slot_index": SLOT_INDEX,
        "generated_from": [
            "data/derived/rst_sc_formal_signal_candidate_summary.tsv",
            "data/derived/rst_sc_feature_slot_inventory.tsv",
        ],
        "policy": "aggregate label names and counts only; no raw LDC text or row-level records",
    }
    html = (
        TEMPLATE.replace("__ITEMS__", json.dumps(items, ensure_ascii=False))
        .replace("__ROLE_OPTIONS__", json.dumps(ROLE_OPTIONS, ensure_ascii=False))
        .replace("__USE_OPTIONS__", json.dumps(USE_OPTIONS, ensure_ascii=False))
        .replace("__META__", json.dumps(metadata, ensure_ascii=False))
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--derived-dir", default=str(DERIVED_DIR))
    parser.add_argument("--outdir", default=str(OUTDIR))
    args = parser.parse_args()

    derived_dir = Path(args.derived_dir)
    outdir = Path(args.outdir)
    items = build_items(derived_dir)
    if not items:
        raise SystemExit("No aggregate RST-SC candidate labels found. Run scripts/inspect_rst_signalling.py first.")

    html_path = outdir / "rst_signal_crosswalk.html"
    items_path = outdir / "rst_signal_crosswalk_items.tsv"
    write_html(html_path, items)
    write_items_tsv(items_path, items)

    print(f"Wrote {html_path.relative_to(ROOT)}")
    print(f"Wrote {items_path.relative_to(ROOT)}")
    print(f"Included {len(items)} aggregate label items; no raw corpus text was read or exported.")


if __name__ == "__main__":
    main()
