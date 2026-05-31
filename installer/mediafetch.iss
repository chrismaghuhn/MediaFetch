; MediaFetch Inno Setup script
; Compile: iscc installer\mediafetch.iss /DMyAppVersion=1.0.0

#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

#define MyAppName "MediaFetch"
#define MyAppPublisher "MediaFetch"
#define MyAppURL "https://github.com/ChrismagHuhn/MediaFetch"
#define MyAppExeName "MediaFetch.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=MediaFetch-{#MyAppVersion}-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\resources\icons\mediafetch.ico
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\MediaFetch.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\resources\bin\ffmpeg.exe"; DestDir: "{app}\bin"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\..\resources\bin\ffmpeg.exe'))
Source: "..\resources\bin\yt-dlp.exe"; DestDir: "{app}\bin"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\..\resources\bin\yt-dlp.exe'))

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "UninstallString"; ValueData: """{uninstallexe}"""; Flags: uninsdeletekey

[Code]
var
  KeepUserData: Boolean;

function InitializeUninstall(): Boolean;
begin
  KeepUserData := MsgBox(
    'Möchten Sie Einstellungen und Download-Chronik behalten? / Keep settings and download history?',
    mbConfirmation,
    MB_YESNO or MB_DEFBUTTON1
  ) = IDYES;
  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if not KeepUserData then
    begin
      AppDataPath := ExpandConstant('{userappdata}\MediaFetch');
      if DirExists(AppDataPath) then
        DelTree(AppDataPath, True, True, True);
    end;
  end;
end;

function FileExists(FileName: String): Boolean;
begin
  Result := FileOrDirExists(FileName);
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}\bin"
