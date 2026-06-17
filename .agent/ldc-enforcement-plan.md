# LDC License Enforcement Plan
This plan makes the LDC General License enforceable in the project workflow. The point is not only to remind us of the rule, but to make accidental misuse hard.
## Enforcement Standard
Treat any LDC material as restricted unless it has been converted into a publication-safe result. Restricted material includes raw corpus files, row-level text exports, prompts containing corpus examples, model outputs that quote corpus examples, local annotations that reproduce the text, and any derivative that would let someone reconstruct a substantial part of the data.

Allowed material in the repo:

- Bibliographic citations and acknowledgments.

- Aggregate counts, coefficients, summaries, figures, and tables that do not reproduce the data.

- Small publication-safe excerpts that Brett has explicitly cleared for inclusion.

- Code, schemas, and documentation that describe how local authorized users can reproduce the analysis without bundling the data.


Disallowed material in the repo or AI tools:

- Raw LDC files.

- Symlinks from the repo into LDC data directories.

- Row-level exports containing LDC text.

- Prompt files containing LDC text.

- Agent/audit outputs that quote LDC text.

- Any upload, paste, or third-party ingestion of LDC data, including ChatGPT, Codex, Claude, Gemini, Copilot, or web platforms.

## Concrete Controls
First, put LDC data outside the project tree. Use a local protected path such as `~/RestrictedCorpora/LDC/...`. The repo may contain code that reads from an environment variable such as `LDC_ROOT`, but it should not contain the data, a symlink to the data, or a committed path that reveals more than necessary.

Second, extend `.gitignore` to block obvious restricted locations and local manifests:

- `restricted/`

- `ldc/`

- `LDC*/`

- `data/raw/*`

- `data/ldc/*`

- `outputs/restricted/*`

- local files such as `.ldc-root`, `.restricted-data.json`, and `.env`


Third, add a versioned policy check, for example `scripts/check_restricted_data.py`, and call it from both `make policy-check` and the existing `.git/hooks/pre-commit`. The check should inspect only staged or repo-local files and print filenames plus reasons, not copied data. It should fail closed when it sees likely restricted material.

The checker should block:

- Staged files in restricted paths or with LDC-style filenames.

- Staged symlinks pointing into restricted corpus directories.

- Staged text files containing markers such as `Linguistic Data Consortium`, `LDC20`, `LDC Catalog`, known LDC corpus IDs, or a local `source_corpus=LDC` field.

- Prompt/output files under `outputs/audit/agent_reviews/` when they contain row-level text from a restricted workflow.

- Large newly staged `.txt`, `.tsv`, `.csv`, `.jsonl`, or `.xml` files unless they are explicitly allowlisted as aggregate outputs.


Fourth, make all LDC-facing scripts produce only aggregate or suppressed outputs by default. Any script that reads `LDC_ROOT` should refuse to write row-level text unless passed an explicit local-only flag, and that flag should write only to ignored quarantine paths such as `outputs/restricted/`.

Fifth, create a publication excerpt ledger. Any LDC example that appears in `main.tex`, notes intended for publication, slides, or a table should have a companion entry recording source, quantity, license status, citation, and why the excerpt is publication-safe. The ledger can be committed only if it contains metadata and the final approved excerpt text, not bulk extracts.

Sixth, add the rule to `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` so every agent sees the same boundary:

> Do not paste, upload, summarize, transform, or analyze raw LDC data with AI tools. If an analysis requires LDC material, use local scripts run by an authorized UofT user and pass only aggregate, non-reconstructive results to agents.
## Operational Workflow
Before any LDC analysis:

1. Confirm the source is LDC-restricted.

2. Put raw data outside the repo.

3. Run local scripts with `LDC_ROOT` set.

4. Write row-level restricted outputs only to ignored quarantine paths.

5. Export only aggregate or publication-cleared results into tracked project files.

6. Run `make policy-check` before committing or sending material to any AI tool.


Before any commit:

1. The pre-commit hook runs the restricted-data scanner.

2. If it flags a file, the commit stops.

3. Brett either removes the file, moves it to a local ignored path, or explicitly allowlists a derived aggregate after checking that it is non-reconstructive.


Before any AI-assisted review:

1. Run `make policy-check`.

2. Do not send raw corpus text, row-level examples, or prompt files from LDC workflows.

3. Send only counts, coefficients, summaries, code, or publication-safe excerpts.

## What This Cannot Enforce
No repo hook can stop a deliberate copy-paste into a chatbot or an upload outside Git. The enforceable part is local: path isolation, ignored quarantine folders, staged-file blocking, scripted aggregate outputs, and explicit excerpt review. The non-automated part is a hard interaction rule: if a request asks an agent to process LDC text, the agent refuses and asks for aggregate or cleared material instead.
## Proposed Implementation
I would implement this in one small pass:

1. Add `DATA_POLICY.md` with the LDC rule and project workflow.

2. Update `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` with the AI-ingestion prohibition.

3. Extend `.gitignore` with restricted-data quarantine paths.

4. Add `scripts/check_restricted_data.py`.

5. Add `make policy-check` and optionally `make install-hooks`.

6. Update `.git/hooks/pre-commit` to run the scanner before the existing doc-sync logic.

7. Run the scanner against the current repo and report any existing risky files without printing restricted content.
