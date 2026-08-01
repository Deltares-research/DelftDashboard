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
; Layout: ONE DelftDashboard folder, chosen on the single directory page:
;   {app}\bin\DelftDashboard.exe        (the compiled program + all DLLs/data)
;   {app}\bin\delftdashboard.pth        (pointer file, contains {app})
;   {app}\data\ , {app}\server\ , {app}\working_directory\ ,
;   {app}\delftdashboard.ini            (created by the app on first run)
;
; The pointer file tells the exe that its DelftDashboard folder is {app}
; (env var DELFTDASHBOARD_DATA overrides it). Downloads can grow to several
; GB, so the default install location is an accessible, writable folder
; (C:\DelftDashboard), not Program Files. Uninstall removes only bin\ -
; data and user files under {app} are left untouched.

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
; Per-user install: writable, no admin prompt. The app writes data next to
; bin\, so the whole folder must be writable - hence NOT Program Files.
PrivilegesRequired=lowest
DefaultDirName={sd}\{#MyAppName}
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

[Messages]
; Make clear that the chosen folder is the ONE DelftDashboard folder: the
; program goes into bin\ and downloaded data (which can grow to several GB)
; is stored right next to it.
SelectDirDesc=Where should [name] be installed?
SelectDirLabel3=Setup will install [name] into the following folder. The program is placed in a "bin" sub-folder; downloaded data (bathymetry, tide models, ...) will also be stored in this folder, so choose a location with sufficient disk space.

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
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    { The DelftDashboard folder (data, server, working_directory, ini) is the
      install folder itself. Write the pointer file the exe reads at startup. }
    SaveStringToFile(ExpandConstant('{app}\bin\delftdashboard.pth'),
      ExpandConstant('{app}') + #13#10, False);
  end;
end;
