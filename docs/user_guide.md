# User Quick Guide

## Startup Flow

1. Launch app (`animal-randomizer-gui`).
2. Review Welcome window (team, citation, support).
3. Click `Enter Application`.

## Core Workflow

1. Create Study metadata.
2. Import animals from CSV/XLSX, or generate list automatically.
3. Configure groups, method, and constraints.
4. Run randomization and review warnings/hashes.
5. Export allocation/report/project files.

## Fast Animal List Generation

In `Import Animals`, use `Auto Generate Animal List` with:

- number of animals
- ID prefix/start/padding
- species
- sex pattern (alternating/all male/all female/unknown)
- default stable fields (strain/source/cage/arrival date)

Generated rows stay editable.

## Input Rules

- Required: `Animal ID` (unique)
- `Sex`: `M/F/Male/Female` (case-insensitive), unknown allowed
- `Weight`: numeric > 0
- `Age`: numeric
- `Date of arrival`: calendar selector, saved as `YYYY-MM-DD`
- `Species` and `Sex`: dropdown + editable text

## Export Outputs

- `allocation.csv` (Excel-friendly UTF-8 BOM)
- `allocation.xlsx`
- `allocation.tsv` (Origin/general pipelines)
- `allocation_grouped_for_prism.csv`
- `allocation_weights_for_prism.csv`
- `allocation_report.html`
- `study.nprj`

After export, the app shows an Export Summary window with:

- file-type guidance
- method-specific article wording guidance
