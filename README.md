# Isocolon and comparative construal

Working repository for Brett Reynolds's corpus-based rhetoric paper:

> Isocolon and comparative construal: A corpus test of rhetorical balance

## Project

The project tests a production-side version of a claim raised by Gini Fahnestock at Rhetoricon, University of Waterloo, on 2026-05-29: isocolon may make comparison more salient, pointed, explicit, or forceful.

The initial empirical claim is narrower:

> Isocolon is preferentially associated with comparative construal in production, beyond what is predicted by general parallel syntax.

## Build

This project uses XeLaTeX and Biber:

```bash
make
```

Do not use LuaLaTeX; it can damage the PDF text layer.

## Data Policy

Raw corpus data should stay out of Git unless the license explicitly allows redistribution. Use `data/raw/` for local source files and `data/derived/` for reproducible derived tables that can be shared.

## License

Unless otherwise noted, the manuscript, notes, and project documentation are licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). See `LICENSE`.
