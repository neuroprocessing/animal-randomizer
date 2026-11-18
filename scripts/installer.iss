#define MyAppName "Neuroprocessing Randomizer"
#define MyAppVersion "1.2.1-rc1"
#define MyAppPublisher "Neuroprocessing"
#define MyAppURL "https://github.com/neuroprocessing/animal-randomizer"
#define MyAppExeName "NeuroprocessingRandomizer.exe"

[Setup]
; Resolve input and output paths from the project root, not scripts/.
SourceDir=..
AppId={{E1B0D23D-3D4E-47AE-9A9F-3A9E4E2A9F10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\Neuroprocessing\Neuroprocessing Randomizer
DefaultGroupName=Neuroprocessing Randomizer
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=dist\installer
OutputBaseFilename=NeuroprocessingRandomizer-Setup-v1.2.1-rc1
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; The entire PyInstaller onedir output is required: EXE plus DLLs and _internal assets.
; Compile only after scripts/build_windows.ps1 has produced this folder.
Source: "dist\NeuroprocessingRandomizer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Distribute license, attribution and build/source instructions alongside binaries.
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "docs\windows_release.md"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Neuroprocessing Randomizer"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Neuroprocessing Randomizer"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Neuroprocessing Randomizer"; Flags: nowait postinstall skipifsilent
