; Inno Setup script for the Nuitka standalone build of DelftDashboard.
;
; Prerequisites:
;   1. Build the standalone exe first:
;        cd installer
;        python build_delftdashboard.py
;      -> produces installer\dist_nuitka\start_ddb.dist\ (DelftDashboard.exe + DLLs + data)
;   2. Install Inno Setup 6 (https://jrsoftware.org/isdl.php  or  winget install JRSoftware.InnoSetup)
;
; Compile:
;   - Open this file in the Inno Setup Compiler and press Build, or
;   - iscc delftdashboard_nuitka.iss
;   -> produces installer\dist_innosetup\DelftDashboard_Setup_<ver>.exe
;
; Layout produced by the installer:
;   {app}\bin\DelftDashboard.exe        (the compiled program + all DLLs/data)
;   {app}\bin\delftdashboard.pth        (pointer file: path to the data folder)
;   <data folder>\data\ , \server\ , delftdashboard.ini   (created by the app)
;
; The wizard asks the user WHERE the data folder should live (a chosen,
; accessible location - recommended - or the per-user application-data folder).
; That choice is written to {app}\bin\delftdashboard.pth, which the frozen exe
; reads at startup (env var DELFTDASHBOARD_DATA overrides it). The app then
; stores everything it downloads/creates under that folder, NOT under {app},
; so the (possibly large) data survives uninstall and can sit on any drive.

#define MyAppName "DelftDashboard"
; The version is passed on the ISCC command line by package_ddb.bat, which
; reads it from src\delftdashboard\__init__.py (the single source of truth):
;   iscc /DMyAppVersion=x.y.z delftdashboard_nuitka.iss
; The fallback below only applies when compiling this script by hand.
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#define MyAppPublisher "Deltares"
#define MyAppURL "https://github.com/Deltares-research/DelftDashboard"
#define MyAppExeName "DelftDashboard.exe"
; Folder produced by Nuitka (named after the entry script start_ddb.py).
#define DistDir "dist_nuitka\start_ddb.dist"

[Setup]
AppId={{FAED70FA-2639-4D3E-943C-DEB34AD469F6}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
; Per-user install: writable, no admin prompt. {autopf} would need admin AND a
; separate writable data location (not yet implemented in the app).
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
; Always show the install-location page. The Inno default (auto) silently
; skips it when the same AppId is already installed (upgrade), which makes it
; look like the installer "stopped asking" where the program should go.
DisableDirPage=no
DisableProgramGroupPage=yes
OutputDir=dist_innosetup
OutputBaseFilename={#MyAppName}_Setup_{#MyAppVersion}
; lzma2/fast keeps the ~1.7 GB dist compression down to minutes. For release
; builds, consider lzma2/max or ultra64 (smaller setup exe, much slower build).
Compression=lzma2/fast
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
SetupIconFile=..\src\delftdashboard\config\images\deltares.ico
UninstallDisplayIcon={app}\bin\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional options:"; Flags: unchecked

[Files]
; Copy the entire Nuitka dist into {app}\bin. ignoreversion is important so
; that same-named DLLs are always overwritten on upgrade.
Source: "{#DistDir}\*"; DestDir: "{app}\bin"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\bin\{#MyAppExeName}"; WorkingDir: "{app}\bin"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\bin\{#MyAppExeName}"; WorkingDir: "{app}\bin"; Tasks: desktopicon

[Run]
Filename: "{app}\bin\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Only remove the pointer file we generate. The user's data folder (which may
; live on another drive and hold downloaded data + their models) is deliberately
; left untouched on uninstall.
Type: files; Name: "{app}\bin\delftdashboard.pth"

[Code]
var
  DataChoicePage: TInputOptionWizardPage;
  DataDirPage: TInputDirWizardPage;

procedure InitializeWizard;
begin
  { Page 1: how to store data - a chosen folder (recommended) or app data. }
  DataChoicePage := CreateInputOptionPage(wpSelectDir,
    'Data location',
    'Where should DelftDashboard keep its data?',
    'DelftDashboard downloads bathymetry, tide models and other data (this can grow to several GB). Choose where to store it, then click Next.',
    True, False);
  DataChoicePage.Add('A folder I choose  (recommended - accessible and easy to back up)');
  DataChoicePage.Add('Application data folder  (' + ExpandConstant('{localappdata}\{#MyAppName}') + ')');
  DataChoicePage.SelectedValueIndex := 0;

  { Page 2: pick the folder (only used when option 1 is selected). }
  DataDirPage := CreateInputDirPage(DataChoicePage.ID,
    'Data folder',
    'Select the folder where DelftDashboard should store its data.',
    'A "data" sub-folder (plus a "server" folder and settings file) will be created inside it. Click Next to continue.',
    False, '');
  DataDirPage.Add('');
  DataDirPage.Values[0] := ExpandConstant('{sd}\{#MyAppName}');
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  { Skip the folder-picker page when the user chose the application-data folder. }
  Result := (PageID = DataDirPage.ID) and (DataChoicePage.SelectedValueIndex <> 0);
end;

function GetDataFolder(): String;
begin
  if DataChoicePage.SelectedValueIndex = 0 then
    Result := DataDirPage.Values[0]
  else
    Result := ExpandConstant('{localappdata}\{#MyAppName}');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  DataFolder: String;
begin
  if CurStep = ssPostInstall then
  begin
    { Create the data folder and write the pointer file the exe reads at startup. }
    DataFolder := GetDataFolder();
    ForceDirectories(DataFolder);
    SaveStringToFile(ExpandConstant('{app}\bin\delftdashboard.pth'), DataFolder + #13#10, False);
  end;
end;
