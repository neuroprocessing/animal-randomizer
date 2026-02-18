# Developer Guide

## Package layout

- `models.py`: data contracts
- `randomization.py`: algorithms and constraints
- `service.py`: application orchestration
- `project_io.py`: `.nprj` persistence
- `report.py`: HTML report generation
- `ui/main_window.py`: PyQt6 desktop GUI

## Running tests

```bash
pytest -q
```

## Design notes

- All randomization methods are seed-driven.
- Hashing uses canonical JSON for deterministic signatures.
- Business logic is isolated from UI for future integration.
