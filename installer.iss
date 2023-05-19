[Setup]
AppId={{3F96B359-E707-4242-42B0-427B28D4242A}}
AppName=PyPDFMerger
AppVersion=1.0
;AppVerName=Image Converter 1.0
AppPublisher=Karl Ludger Radke
DefaultDirName={pf}\PyPDFMerger
DefaultGroupName=PyPDFMerger
OutputBaseFilename=PyPDFMergerSetup
Compression=lzma
LicenseFile=LICENSE
SolidCompression=yes
SetupIconFile=icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\pypdfmerger\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\PyPFMerger"; Filename: "{app}\ImageConverter.exe"
Name: "{commondesktop}\PyPDFMerger"; Filename: "{app}\pypdfmerger.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\pypdfmerger.exe"; Description: "{cm:LaunchProgram,Image Converter}"; Flags: nowait postinstall skipifsilent
