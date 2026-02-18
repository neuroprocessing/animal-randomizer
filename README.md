# Neuroprocessing Randomizer

**Tagline:** Reproducible Animal Group Allocation

Neuroprocessing Randomizer is an open-source tool for rigorous, reproducible, and auditable group allocation in laboratory animal studies.

## Current Status

- Version: `0.3.0`
- Stage: MVP (functional)
- Interfaces: CLI + PyQt6 wizard GUI
- Project format: `.nprj` (JSON)

## What's New in v0.3.0

- Added a full modular MVP architecture (core logic separated from UI and I/O).
- Added four randomization strategies: `simple`, `balanced`, `stratified`, and `block`.
- Added cage-aware and weight-balancing constraints for bias reduction.
- Added reproducibility controls: fixed/auto seed + SHA256 integrity hashes.
- Added statistical validation outputs and imbalance warnings (including Cohen's d).
- Added `.nprj` project save/load with auditable JSON event logs.
- Added export pipeline for allocation tables (`.csv`, `.xlsx`) and HTML reports.
- Added PyQt6 5-step wizard GUI for non-programmer lab workflows.
- Added example dataset, example outputs, and unit tests for the randomization engine.

## Implemented MVP Features

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
  - allocation table (`.csv`, `.xlsx`)
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

## Architecture

- `src/animal_randomizer/models.py`: Dataclasses for animals, study/config, assignments, project state.
- `src/animal_randomizer/randomization.py`: Allocation engine and constraints.
- `src/animal_randomizer/stats.py`: Validation metrics and warnings.
- `src/animal_randomizer/service.py`: Orchestrates validation, randomization, stats, hashing, audit.
- `src/animal_randomizer/project_io.py`: Save/load `.nprj` files.
- `src/animal_randomizer/io_handlers.py`: CSV/XLSX import and allocation export.
- `src/animal_randomizer/report.py`: HTML report generation.
- `src/animal_randomizer/cli.py`: CLI workflow.
- `src/animal_randomizer/ui/main_window.py`: PyQt6 wizard interface.

## Installation

```bash
pip install -e .
```

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
  --out-alloc examples/example_allocation.csv \
  --out-report examples/example_report.html \
  --out-project examples/example_project.nprj
```

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

### v1.0 (planned)

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
