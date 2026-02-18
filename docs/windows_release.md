# Windows Release Guide (v1.0.0)

## Build executable

```powershell
cd C:\Users\Ali\Documents\GitHub\animal-randomizer
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
```

Generated output:

- `dist\NeuroprocessingRandomizer\NeuroprocessingRandomizer.exe`

## Build installer (.exe setup)

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ".\scripts\installer.iss"
```

Generated setup:

- `dist\installer\NeuroprocessingRandomizer-Setup-v1.0.0.exe`

## Release checklist

1. Validate startup flow (splash -> Welcome window -> Enter Application).
2. Validate GUI workflow (all 5 steps + export).
3. Validate automated animal list generation and editable table behavior.
4. Validate export summary window and output files.
5. Validate CLI sample command.
6. Run tests: `python -m pytest -q`.
7. Package setup/zip assets for GitHub Releases.
8. Attach release notes from `Changelog.md` and README "What's New".

## Notes on build environment

- Prefer a clean Python environment for packaging.
- Exclude unrelated Qt/Torch stacks from bundling via spec file.

## Optional hardening

- `.ico` app icon is already configured in `scripts/animal-randomizer.spec`.
- Code-sign the executable and installer.
- Add MSIX packaging for enterprise deployment.
