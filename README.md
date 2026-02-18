# Neuroprocessing Randomizer

**Tagline:** Reproducible Animal Group Allocation

Neuroprocessing Randomizer is an open-source tool for rigorous, reproducible, and auditable group allocation in laboratory animal studies.

## Current Status

- Version: `1.0.0`
- Stage: Production Release
- Interfaces: CLI + PyQt6 wizard GUI
- Project format: `.nprj` (JSON)

## What's New in v1.0.0

- Promoted the project from MVP to a publishable `1.0.0` release.
- Upgraded the desktop interface with a professional website-aligned visual design.
- Added branded startup experience for Windows builds:
  - application icon
  - splash screen
  - packaged app assets for distributable builds
- Added Windows release pipeline with PyInstaller:
  - build script: `scripts/build_windows.ps1`
  - build spec: `scripts/animal-randomizer.spec`
  - Inno Setup script: `scripts/installer.iss`
  - release guide: `docs/windows_release.md`
- Added product-level workflow improvements:
  - separate Welcome window before entering main app
  - citation text displayed directly from `CITATION.cff`
  - in-app Help button with step-specific guidance
  - automated animal list generation (count + ID pattern + species + sex defaults)
  - dropdown fields for list-based parameters (`Sex`, `Species`)
  - calendar date picker for `Date of arrival`
  - export summary dialog with method-specific manuscript guidance

## Implemented v1.0.0 Features

- Randomization methods:
  - `simple`
  - `balanced`
  - `stratified` (`sex`, `cage`, `weight`, `age`)
  - `block` (fixed or random block sizes)
- Bias-control constraints:
  - max animals per cage per group
  - cage clustering minimization
  - weight-bin balancing
- Reproducibility and auditability:
  - user-provided or auto-generated seed
  - SHA256 hashes for input/config/output
  - software + algorithm version tracking
  - JSON audit events in project state
- Validation outputs:
  - per-group `N`
  - weight mean / SD
  - sex distribution
  - cage distribution
  - Cohen's d for weight between groups
  - imbalance warnings
- Export outputs:
  - allocation table (`.csv`, `.xlsx`, `.tsv`)
  - Prism-friendly grouped tables (`*_grouped_for_prism.csv`, `*_weights_for_prism.csv`)
  - HTML report
  - full project snapshot (`.nprj`)

## Wizard GUI (Implemented)

`src/animal_randomizer/ui/main_window.py` provides a 5-step workflow:

1. Create Study
2. Import Animals
3. Configure Strategy
4. Run Randomization
5. Review and Export

Includes editable animal table, theme toggle (dark/light), run summary, and export actions.
Also includes a pre-app Welcome window, auto-list generation for animal metadata, dropdown/date controls, and context help.

## Architecture

- `src/animal_randomizer/models.py`: Dataclasses for animals, study/config, assignments, project state.
- `src/animal_randomizer/randomization.py`: Allocation engine and constraints.
- `src/animal_randomizer/stats.py`: Validation metrics and warnings.
- `src/animal_randomizer/service.py`: Orchestrates validation, randomization, stats, hashing, audit.
- `src/animal_randomizer/project_io.py`: Save/load `.nprj` files.
- `src/animal_randomizer/io_handlers.py`: CSV/XLSX import and allocation export.
- `src/animal_randomizer/report.py`: HTML report generation.
- `src/animal_randomizer/cli.py`: CLI workflow.
- `src/animal_randomizer/ui/app.py`: branded startup + Welcome window.
- `src/animal_randomizer/ui/main_window.py`: PyQt6 wizard interface.

## Installation

```bash
pip install -e .
```

## Windows Release Build

Build a Windows distributable executable:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
```

Output:

- `dist\NeuroprocessingRandomizer\NeuroprocessingRandomizer.exe`
- `dist\installer\NeuroprocessingRandomizer-Setup-v1.0.0.exe` (if built via Inno Setup)

Full guide: `docs/windows_release.md`

## CLI Example

```bash
animal-randomizer \
  --input examples/example_dataset.csv \
  --study-id NP-2026-001 \
  --title "Cognitive Rescue Pilot" \
  --researcher "Dr. N. Process" \
  --institution "Neuroprocessing Lab" \
  --method stratified \
  --groups Control,DrugA,DrugB \
  --stratify-by sex,cage,weight \
  --random-block-sizes 4,6,8 \
  --max-cage-per-group 1 \
  --seed 20260217 \
  --export-bundle \
  --out-alloc examples/example_allocation.csv \
  --out-report examples/example_report.html \
  --out-project examples/example_project.nprj
```

`--export-bundle` creates Excel/TSV/Prism-compatible companion files for downstream analysis tools such as Excel, GraphPad Prism, and Origin.

## GUI

```bash
animal-randomizer-gui
```

Alternative:

```bash
python -m animal_randomizer.ui.app
```

## Docs and Examples

- User guide: `docs/user_guide.md`
- Developer guide: `docs/developer_guide.md`
- Example dataset: `examples/example_dataset.csv`
- Example report: `examples/example_report.html`
- Example project: `examples/example_project.nprj`

## Testing

```bash
python -m pytest -q
```

## Roadmap

### v1.1 (planned)

- PDF report export
- richer GUI validation/QA panels
- improved statistical threshold controls

### v1.5 (planned)

- optimization-driven constrained randomization (MILP/SAT)
- protocol templates by species/strain
- power-analysis helper integration

### v2.0 (planned)

- integration with Neuroprocessing Animal Study Manager
- shared data backend
- role-based permissions and e-signature flow
