# Developer Guide

## Package layout

- `models.py`: data contracts
- `randomization.py`: algorithms and constraints
- `service.py`: application orchestration
- `project_io.py`: `.nprj` persistence
- `report.py`: HTML report generation
- `io_handlers.py`: import/export + interoperability bundle
- `ui/app.py`: branded startup + Welcome window
- `ui/main_window.py`: PyQt6 wizard GUI
- `validation.py`: schema validation + QC gate

## Running tests

```bash
python -m pytest -q
```

## Design notes

- All randomization methods are seed-driven.
- Hashing uses canonical JSON for deterministic signatures.
- Business logic is isolated from UI for future integration.
- GUI supports automated list generation and constrained manual editing.
- Export layer targets Excel, Prism, and Origin interoperability.
- QC gate blocks incompatible/missing metadata before randomization runs.
- Blinding exports provide experimenter-facing and restricted key files.
