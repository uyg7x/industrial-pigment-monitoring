; ═══════════════════════════════════════════════════════════════════════════
; Inno Setup Script — Pigment Process Control System
; Builds a professional Windows installer: PigmentPCS_Setup.exe
; ═══════════════════════════════════════════════════════════════════════════

#define AppName      "Pigment Process Control System"
#define AppShortName "PigmentPCS"
#define AppVersion   "3.1"
#define AppPublisher "Your Company Name"
#define AppURL       "https://yourcompany.com"
#define AppExeName   "PigmentPCS.exe"
#define AppIcon      "app_icon.ico"

[Setup]
; ── Identity ─────────────────────────────────────────────────────────────────
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; ── Installation paths ────────────────────────────────────────────────────────
DefaultDirName={autopf}\{#AppShortName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=PigmentPCS_Setup
SetupIconFile={#AppIcon}
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

; ── Appearance ────────────────────────────────────────────────────────────────
WizardStyle=modern
WizardResizable=no
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=yes

; ── Privileges ────────────────────────────────────────────────────────────────
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; ── Uninstaller ───────────────────────────────────────────────────────────────
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
CreateUninstallRegKey=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "Create a desktop shortcut";          GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "quicklaunch";   Description: "Create a Quick Launch shortcut";     GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "startmenuicon"; Description: "Create a Start Menu shortcut";       GroupDescription: "Shortcuts:";

[Files]
; Main application (all files from PyInstaller dist folder)
Source: "dist\{#AppShortName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Include the Excel batch entry template
Source: "Pigment_Batch_Entry_Template.xlsx"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\Pigment_Batch_Entry_Template.xlsx'))

; Include sample data
Source: "sample_data.csv"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\sample_data.csv'))

; Create exports directory
Source: "run.py"; DestDir: "{app}\exports"; Flags: ignoreversion; AfterInstall: CreateExportsDir

[Dirs]
Name: "{app}\exports"
Name: "{userappdata}\{#AppShortName}"

[Icons]
; Start Menu
Name: "{group}\{#AppName}";            Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Batch Entry Template";  Filename: "{app}\Pigment_Batch_Entry_Template.xlsx"; Check: FileExists(ExpandConstant('{app}\Pigment_Batch_Entry_Template.xlsx'))
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\{#AppName}";     Filename: "{app}\{#AppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#AppExeName}"

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunch

[Registry]
; Register app so Windows knows about it
Root: HKCU; Subkey: "Software\{#AppPublisher}\{#AppShortName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletesubkey
Root: HKCU; Subkey: "Software\{#AppPublisher}\{#AppShortName}"; ValueType: string; ValueName: "Version";     ValueData: "{#AppVersion}"

; Associate .csv files with the app (optional — comment out if not wanted)
; Root: HKCU; Subkey: "Software\Classes\.csv\OpenWithList\{#AppExeName}"; Flags: uninsdeletekey

[Run]
; Launch app after install
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\exports"
Type: dirifempty;     Name: "{app}"

[Code]
procedure CreateExportsDir();
begin
  // Handled by [Dirs] section
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
end;
