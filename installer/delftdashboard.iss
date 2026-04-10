[Setup]
AppName=DelftDashboard
AppVersion=0.1.0
AppPublisher=Deltares
AppPublisherURL=https://github.com/Deltares-research/DelftDashboard
DefaultDirName={userdocs}\DelftDashboard
DefaultGroupName=DelftDashboard
OutputDir=dist_innosetup
OutputBaseFilename=DelftDashboard_Setup_0.1.0
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupLogging=yes
DisableProgramGroupPage=yes
WizardStyle=modern
; Estimated required space (uncompressed)
ExtraDiskSpaceRequired=3000000000

[Files]
; Bundle the conda-pack archive
Source: "dist\delftdashboard_env.tar.gz"; DestDir: "{tmp}"; Flags: deleteafterinstall nocompression

[Run]
; Extract the environment
Filename: "tar"; Parameters: "-xzf ""{tmp}\delftdashboard_env.tar.gz"" -C ""{app}"""; StatusMsg: "Extracting Python environment (this may take a few minutes)..."; Flags: runhidden waituntilterminated
; Fix path prefixes
Filename: "{app}\Scripts\conda-unpack.exe"; StatusMsg: "Finalizing installation..."; Flags: runhidden waituntilterminated
; Launch after install (optional)
Filename: "{app}\delftdashboard.bat"; Description: "Launch DelftDashboard"; Flags: nowait postinstall skipifsilent shellexec

[Icons]
Name: "{group}\DelftDashboard"; Filename: "{app}\delftdashboard.bat"; WorkingDir: "{userdocs}"; IconFilename: "{app}\python.exe"
Name: "{commondesktop}\DelftDashboard"; Filename: "{app}\delftdashboard.bat"; WorkingDir: "{userdocs}"; IconFilename: "{app}\python.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional options:";

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  BatContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    { Create the launcher batch file }
    BatContent := '@echo off' + #13#10 +
                  'call "' + ExpandConstant('{app}') + '\Scripts\activate.bat"' + #13#10 +
                  'cd /d "%USERPROFILE%"' + #13#10 +
                  'python -c "import delftdashboard; delftdashboard.start()"' + #13#10;
    SaveStringToFile(ExpandConstant('{app}\delftdashboard.bat'), BatContent, False);
  end;
end;


