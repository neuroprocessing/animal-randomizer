#define MyAppName "Neuroprocessing Randomizer"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Neuroprocessing"
#define MyAppURL "https://github.com/neuroprocessing/animal-randomizer"
#define MyAppExeName "NeuroprocessingRandomizer.exe"

[Setup]
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
OutputBaseFilename=NeuroprocessingRandomizer-Setup-v1.0.0
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
Source: "dist\NeuroprocessingRandomizer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Neuroprocessing Randomizer"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Neuroprocessing Randomizer"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Neuroprocessing Randomizer"; Flags: nowait postinstall skipifsilent
