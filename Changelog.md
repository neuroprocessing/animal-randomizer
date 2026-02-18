# Changelog

All notable changes to this project will be documented in this file.

This project follows semantic versioning: **MAJOR.MINOR.PATCH**

---

## [1.0.0] - 2026-02-18
### Added
- Professional Windows-focused desktop UI refresh aligned with Neuroprocessing website style.
- Branded app startup assets:
  - application icon
  - splash screen
- Windows executable packaging pipeline:
  - `scripts/build_windows.ps1`
  - `scripts/animal-randomizer.spec`
  - `requirements-windows-build.txt`
  - `docs/windows_release.md`
- PyInstaller configuration to bundle app assets and use branded `.ico` executable icon.
- Pre-app Welcome window with team/support overview and direct citation content loaded from `CITATION.cff`.
- In-app Help button with step-specific guidance (instead of static inline panels).
- Automated animal list generator (count, ID pattern, species, sex pattern, default stable fields).
- Enhanced table input controls:
  - dropdowns for list-based fields (`Sex`, `Species`)
  - calendar date picker for `Date of arrival`
- Extended interop exports for analysis tools:
  - CSV, XLSX, TSV
  - Prism-grouped IDs and weights files
- Export Summary dialog with generated-file overview, file-type guidance, and method-specific manuscript wording guidance.
- Inno Setup installer script: `scripts/installer.iss`.

### Changed
- Updated documentation and website docs page for `v1.0.0` release status and Windows release workflow.
- Updated package/application version markers to `1.0.0`.

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
