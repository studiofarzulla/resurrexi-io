# Papers Official — GitHub Copilot Instructions

**Repository:** `studiofarzulla/resurrexi-io` (papers-official subdirectory)  
**Template Version:** dissensus-preprint v3.0.0  
**Master Index:** `CLAUDE.md`

## Repository Structure

This is an academic research papers repository organized by research programme:

- **I. Consent Mechanics** — consent theory, sovereignty, stakes without voice
- **II. Economic Pharmakon** — crypto regulation, CBDC, AML paradoxes
- **III. Crypto Microstructure** — market analysis, sentiment, ABM simulations
- **IV. Process Philosophy** — ROM flagship, identity thesis, consciousness
- **V. Computational Cognition** — trauma models, autonomous systems, vision

Each paper folder contains:
- LaTeX source files (`.tex`)
- References (`.bib`)
- Code (Python, R, JS) in `code/` subdirectories
- Archived versions in `_archive/`
- Frozen submission packages in `*-submission/` directories

## Build & Test Commands

### LaTeX Papers

Standard build (4-pass for proper citations):
```bash
cd <paper-folder>/paper  # or wherever main.tex lives
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

If `Makefile` exists (e.g., `asri/paper/Makefile`):
```bash
make          # Full 4-pass build
make quick    # Single pass, no bibliography
make clean    # Remove build artifacts
make check    # Validate BibTeX entries
```

### Python Projects

Projects with `pyproject.toml` (e.g., `asri/code/`):
```bash
cd <paper>/code
pip install -e .               # Install in editable mode
pip install -e ".[dev]"        # Install with dev dependencies
pytest                          # Run all tests
pytest tests/test_calculator.py # Run single test file
ruff check .                   # Lint code
mypy src/                      # Type checking
```

Projects with `requirements.txt` (e.g., `event-study/code/`, `whitepaper-claims/code/`):
```bash
cd <paper>/code
pip install -r requirements.txt
pytest  # or python -m pytest
```

### JavaScript Projects

Frontend projects (e.g., `asri/code/frontend/`):
```bash
cd <paper>/code/frontend
npm install
npm run dev      # Development server
npm run build    # Production build
npm test         # Run tests
```

### R Projects

Some papers include R analysis scripts. Check for `.R` files in `code/` directories.

## Key Conventions

### Paper Numbering & Canonical Files

- **Source of Truth:** `systems-ac/papers.json` (external reference)
- **Canonical Files:** Listed in `CLAUDE.md` — always edit the canonical version
- **Paper IDs:** Folder names may differ from `papers.json` IDs (see mapping in `CLAUDE.md`)
- **Self-citations:** Use `farzulla-self-citations.bib` for cross-referencing papers

### Frozen Submission Directories

**DO NOT MODIFY:**
- `springer-submission/`
- `digital-finance-canon/`
- `ai-ethics-submission/`
- `ethics-it-submission/`
- `hssc-submission*.zip`

These are frozen submission packages for journals. Make changes in the canonical files only.

### Archive Directories

- `_archive/` contains old versions — DO NOT reference as canonical
- Archive files are kept for history, not for active editing

### Template Usage

- **Template:** `~/Resurrexi/projects/papers/templates/dissensus-preprint/main.tex`
- **Version:** v3.0.0
- **Exception:** `event-study/digital-finance-canon/` uses Springer `sn-article` class
- **Exception:** `trauma-training-data` stays in old format (permanent Research Square preprint)

### LaTeX Conventions

- Use `\citet{}` and `\citep{}` for author-year citations (natbib)
- Cross-paper references go in `farzulla-self-citations.bib`
- Keep preamble minimal — template handles most styling
- Tables and figures in separate files when large

### Code Organization

Python projects follow:
- `src/<project-name>/` — source code
- `tests/` — pytest test suites
- `pyproject.toml` — dependencies, linting, type checking
- `ruff` for linting (not black/flake8)
- `mypy` in strict mode
- Type hints required

### Git Workflow

- Branch structure: Typically direct commits to `master` (small team)
- Commit frozen submissions: Yes, for reproducibility
- Large files: Use Git LFS for datasets over 50MB
- Submodules: Not used currently

### Paper Status Tracking

Paper statuses (from `CLAUDE.md`):
- **arXiv:XXXX.XXXXX** — Published on arXiv
- **Under Review @ Journal** — Submitted, awaiting decision
- **With Editor @ Journal** — Accepted, in production
- **Zenodo** — Preprint/working paper
- **SSRN** — Social Science Research Network

## Common Pitfalls

1. **Don't edit submission directories** — They're frozen snapshots
2. **Check canonical file** — CLAUDE.md lists the authoritative version
3. **Archive isn't canonical** — Old versions are in `_archive/` for history only
4. **Python imports** — Use `pip install -e .` for local development
5. **LaTeX compilation** — Always run 4 passes for proper citations/cross-refs
6. **BibTeX warnings** — Check for missing DOIs with `make check` if Makefile exists

## Development Workflow

1. Check `CLAUDE.md` for canonical file location
2. Edit canonical file (not archived or submission versions)
3. For LaTeX: Run 4-pass compilation to verify
4. For Python: Run tests with `pytest` and linting with `ruff`
5. Commit changes with descriptive message referencing paper ID (e.g., "DAI-2508: Fix whitepaper model specification")

## External References

- **Papers JSON:** `systems-ac/papers.json` (canonical paper registry)
- **Lean Formalizations:** `LEAN_FORMALIZATION_MAP.md` tracks which papers have formal proofs
- **Website Content:** Some papers synced to `resurrexi.io` content management

## Testing Strategy

### LaTeX
- Build successfully without errors
- Check citation warnings
- Verify figure/table references resolve
- Word count validation (if journal has limits)

### Python
- Unit tests: Individual functions, classes
- Integration tests: Pipeline end-to-end
- Validation tests: Statistical properties, data sanity checks
- Coverage target: 80%+ for publication-critical code

### Data
- Check reproducibility scripts in `code/` directories
- Validate data provenance and transformations
- Ensure figure-generating scripts match paper content
