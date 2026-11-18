Copyright (C) 2026 Ali Mirzakhani

SPDX-License-Identifier: GPL-3.0-only

# Neuroprocessing Randomizer

**Tagline:** Reproducible Animal Group Allocation

Neuroprocessing Randomizer is an open-source tool for rigorous, reproducible, and auditable group allocation in laboratory animal studies.

## Current Status

- Version: `1.2.1-rc1`
- Stage: Release candidate; public DOI pending
- Interfaces: CLI + PyQt6 wizard GUI
- Project format: `.nprj` (JSON)

## What's New in v1.2.1-rc1

- Added pre-randomization QC gate tied to selected stratification and constraint settings.
- Added blinding workflow exports:
  - `*_blinded.csv` (experimenter-facing coded groups)
  - `*_blinding_key.csv` (restricted unblinding key)
- Added methods-ready text section to HTML report for manuscript workflow.
- Added deterministic blinding export support in CLI and GUI export bundle.
- Version markers are aligned to `1.2.1-rc1` for this release candidate.
- Fail-closed validation for malformed configurations and impossible cage constraints.
- Stable handling of multiple Animal ID aliases and missing dates (no silent current-date default).
- Shared cage-constraint accounting across strata and blocks.
- Sample-SD-based descriptive weight diagnostics and explicit effect-size definition.
- Study-specific allocation records are deliberately excluded; examples are synthetic only.
- HTML reports escape study/user values, and methods text distinguishes requested
  constraints from constraints verified by the QC gate.

## What's New in 1.2.1-rc1

- Promoted the project from MVP to a publishable `1.2.1-rc1` release.
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

## Implemented features

- Randomization methods:
  - `simple`
  - `balanced`
  - `stratified` (`sex`, `cage`, `weight`, `age`)
  - `block` (fixed or random block sizes)
- Bias-control constraints:
  - max animals per cage per group
  - cage clustering minimization
  - weight-bin balancing

Constraints are checked as hard post-allocation invariants when configured. If a
constraint is infeasible, the run stops with an explicit error. `simple` without
constraints is a seeded shuffle followed by deterministic round-robin labels; it
must not be described as covariate-balanced. A constrained `simple` run uses the
same fail-closed allocator as `balanced`.
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
  - descriptive weight means/SDs and Cohen's d (pooled sample SD; uncorrected)
  - imbalance warnings
- Export outputs:
  - allocation table (`.csv`, `.xlsx`, `.tsv`)
  - Prism-friendly grouped tables (`*_grouped_for_prism.csv`, `*_weights_for_prism.csv`)
  - blinded outputs (`*_blinded.csv`, `*_blinding_key.csv`)
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
- `dist\installer\NeuroprocessingRandomizer-Setup-v1.2.1-rc1.exe` (if built via Inno Setup)

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
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider
```

PowerShell equivalent:

```powershell
$env:PYTHONPATH = "src"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest -q -p no:cacheprovider
```

For release verification, install the project in a clean environment and run
the test command above. The source package does not include a release CI
workflow. No study allocation or private animal metadata is required to run
the suite. Windows build scripts are provided; this source release does not
include a prebuilt Randomizer executable or installer.

## Roadmap

### v1.3 (planned)

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


## License

Neuroprocessing Randomizer v1.2.1-rc1 is distributed under the GNU General Public License version 3.0 only (GPL-3.0-only).

See the LICENSE file for the complete terms.

The application uses PyQt6, which is available under GPLv3 or a commercial license from Riverbank Computing. Third-party components remain subject to their respective licenses and copyright notices.

See THIRD_PARTY_NOTICES.md for dependency attribution.

The corresponding application source code and installation instructions are available in this repository.

Earlier releases remain subject to the licenses under which they were originally distributed.

## Citation

Please use the citation information in CITATION.cff.
