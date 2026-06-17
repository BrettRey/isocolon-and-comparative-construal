# Data Policy

This project may use corpus data with different redistribution rules. The most restrictive source controls the workflow for any file derived from it.

## LDC General License

Linguistic Data Consortium materials available through the University of Toronto are restricted to University of Toronto faculty, students, or staff, including permanent, temporary, contract, and visiting appointments.

Permitted use is limited to non-commercial research or education. Results may be published with limited parts of the data or derivatives, but not enough to reproduce the data. Publications and presentations must cite and acknowledge the data source. For uncertainty about how much material can be included, contact the University of Toronto Map & Data Library.

Do not:

- distribute LDC data to anyone outside the University of Toronto;
- post LDC data on a website or web platform;
- ingest LDC data into third-party platforms, including AI chatbots such as ChatGPT, Codex, Claude, Gemini, or Copilot;
- share LDC data externally by email or any other means;
- serve or distribute a competing product in any format;
- use LDC data to create a commercial product;
- use LDC data in a commercial, internship, co-op, or other professional setting.

## Project Boundary

Raw LDC data must stay outside this repository. Do not symlink from this repository into LDC data directories.

Allowed tracked material:

- citations and acknowledgments;
- aggregate counts, coefficients, figures, and tables that do not reproduce the data;
- publication-safe excerpts explicitly cleared by Brett;
- code and documentation that let an authorized local user reproduce the analysis without bundling the data.

Disallowed tracked material:

- raw LDC files;
- row-level exports containing LDC text;
- prompts containing LDC text;
- AI or audit outputs that quote LDC text;
- derivatives that would let a reader reconstruct substantial LDC data.

## Workflow

Use a local protected path such as `~/RestrictedCorpora/LDC/...` and pass it to scripts through an environment variable such as `LDC_ROOT`.

Any LDC-facing script should write row-level text only to ignored quarantine paths such as `outputs/restricted/`. Only aggregate or publication-cleared results may be copied into tracked files.

Run this before committing or sending any file to an AI tool:

```bash
make policy-check
```

If the scanner flags a file, move it to an ignored local path, remove the restricted material, or explicitly verify that the file is an aggregate, non-reconstructive derivative.
