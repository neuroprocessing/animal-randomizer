# Changelog

All notable changes to this project will be documented in this file.

This project follows semantic versioning: **MAJOR.MINOR.PATCH**

---

## [0.3.0] - 2026-02-18
### Added
- Modular MVP architecture across core engine, I/O, reporting, and UI layers.
- Dataclass-based domain models for animal metadata, study configuration, assignments, and project state.
- Randomization methods: simple, balanced, stratified, and block randomization.
- Cage-aware constraints and weight-bin balancing controls.
- Statistical validation module (group size, weight mean/SD, sex/cage distribution, Cohen's d, warnings).
- Seed management and SHA256 integrity hashing for input/config/output reproducibility checks.
- JSON audit event logging and `.nprj` project save/load support.
- Export support for allocation tables (`.csv`, `.xlsx`) and HTML reports.
- PyQt6 multi-step wizard GUI for full workflow execution.
- Example dataset and generated example outputs.
- Unit tests for randomization reproducibility, balancing behavior, and service outputs.

### Changed
- Updated package metadata and CLI workflow for metadata-driven study runs.
- Updated README and docs to reflect implemented MVP scope and current workflow.

## [0.1.0] - 2026-02-17
### Added
- Initial repository structure
- Reproducible randomization workflow concept
- CLI-based interface (planned)
- CSV export format specification
- Citation support via CITATION.cff
