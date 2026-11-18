# Windows Release Guide (v1.2.1-rc1)

> **Release candidate:** These steps describe how to build and verify a Windows
> installer; they do **not** certify that a specific installer has passed testing.
> Publish a binary only after completing the checks below and reviewing its
> bundled third-party licences and corresponding source.

## Build executable

```powershell
cd <path-to-cloned-repository>\animal-randomizer
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
```

Generated output:

- `dist\NeuroprocessingRandomizer\NeuroprocessingRandomizer.exe`
- The **complete** `dist\NeuroprocessingRandomizer\` directory, including
  its supporting DLLs, libraries and `_internal` files, must be retained.

Before compiling the installer, verify the required inputs from the project root:

```powershell
$required = @(
  'dist\NeuroprocessingRandomizer\NeuroprocessingRandomizer.exe',
  'LICENSE',
  'THIRD_PARTY_NOTICES.md',
  'README.md',
  'docs\windows_release.md'
)
$missing = $required | Where-Object { -not (Test-Path -LiteralPath $_) }
if ($missing) { throw "Missing installer inputs: $($missing -join ', ')" }
```

## Build installer (.exe setup)

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ".\scripts\installer.iss"
```

Generated setup:

- `dist\installer\NeuroprocessingRandomizer-Setup-v1.2.1-rc1.exe`

The Inno Setup script uses `SourceDir=..` because it resides in `scripts/`.
It installs the *entire* PyInstaller output folder, displays `LICENSE` in
Setup and includes `LICENSE`, `THIRD_PARTY_NOTICES.md`, `README.md`, and this
build/source guide under the installed application directory.

## Release checklist

1. Validate startup flow (splash -> Welcome window -> Enter Application).
2. Validate GUI workflow (all 5 steps + export).
3. Validate automated animal list generation and editable table behavior.
4. Validate export summary window and output files.
5. Validate CLI sample command.
6. Run tests in a clean environment (PowerShell):

   ```powershell
   $env:PYTHONPATH = "src"
   $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
   python -m pytest -q
   ```

7. Install the setup file on a clean Windows test machine or disposable VM.
   Check first launch, the welcome screen, the five-step GUI, and exports using
   synthetic data only. Verify that DLLs and `_internal` assets were installed.
8. Verify the GPL license page in Setup and that `LICENSE`,
   `THIRD_PARTY_NOTICES.md`, and `docs\windows_release.md` are installed.
   Test uninstallation and confirm unrelated user data is not removed.
9. Check that the source archive is the **exact** commit/tag used to build the
   binary, and that source/build instructions and covered third-party source
   obligations are met.
10. Package setup/ZIP assets for GitHub Releases only after these checks pass.
11. Attach release notes from the changelog (if present) and README "What's New".
    Label `v1.2.1-rc1` as a **pre-release**.

## Notes on build environment

- Prefer a clean Python environment for packaging.
- Exclude unrelated Qt/Torch stacks from bundling via spec file.

## Optional hardening

- `.ico` app icon is already configured in `scripts/animal-randomizer.spec`.
- Code-sign the executable and installer.
- Add MSIX packaging for enterprise deployment.


## Source Code and Licensing

Neuroprocessing Randomizer **v1.2.1-rc1** is intended for distribution under
**GNU GPL v3.0 only (`GPL-3.0-only`)** for the project's own code, provided
that the release has been duly authorised by the rights holder(s).

Copyright (C) 2026 Ali Mirzakhani (for original code where ownership is held).
The complete GPLv3 text is in the repository's `LICENSE` file. Third-party
components keep their respective copyrights and licences.

### Corresponding source for each binary release

Project repository:
https://github.com/neuroprocessing/animal-randomizer

For a **published** binary, use the matching release tag, commit identifier
and release/source archive on the GitHub Releases page. Do not rely solely on
an unversioned `main` branch when identifying the source of a specific setup.

The corresponding source package needs to include, as applicable:

- Original application Python source, project files, images/assets needed to
  build it, and the exact licence/copyright notices.
- `scripts/build_windows.ps1`, `scripts/animal-randomizer.spec`, and
  `scripts/installer.iss`, plus relevant installation/build instructions.
- The versions and configuration of dependencies that actually entered the
  distributed build (record a dependency manifest and Python/build versions).
- Source or valid source-access arrangements required for GPL-covered bundled
  dependencies, including modified third-party code, if any.

Under GPLv3 section 6, people receiving a binary must be given appropriate
access to its **Complete Corresponding Source**. If offering binaries online,
provide equivalent access to source with clear directions next to each binary.
A GitHub-generated source ZIP alone is not proof that all bundled dependency
source obligations are satisfied; review the final Windows distribution.

### Rebuilding the application

1. Download the exact source archive corresponding to the published binary.
2. Install the Python and build dependencies documented for that release.
3. In an isolated environment, install project dependencies, then run tests:

   ```powershell
   python -m pip install -e ".[dev]"
   $env:PYTHONPATH = "src"
   $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
   python -m pytest -q
   ```

4. Build the application:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
   ```

5. Confirm all installer inputs exist (see the check near the top of this
   document), then build with Inno Setup 6:

   ```powershell
   & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ".\scripts\installer.iss"
   ```

6. Test the compiled program, Setup and uninstall on Windows. Record build
   versions, SHA-256 checksums and observed test results.

### Third-party components

The application uses **PyQt6** (Riverbank Computing) under its GPLv3 path for
this distribution, rather than a Riverbank commercial licence. Other
packages, including the bundled Qt libraries and any dependencies packaged
into the Windows build, require their own licence/notice review.

See `THIRD_PARTY_NOTICES.md`. Before shipping a binary, audit its **actual
bundled** versions and distribute the applicable notices and source materials
or compliant source-access instructions.

### Release boundary

- Publishing this **source-only** release does not imply that a Windows EXE
  or installer has been built, tested, or distributed.
- Do not upload any Windows binary until its own test results and GPLv3
  section 6 obligations have been verified.
- This release candidate was developed after the study's original animal
  allocation; do not describe it as the exact software used for that historic
  allocation.
