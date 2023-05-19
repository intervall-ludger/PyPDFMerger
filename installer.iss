[Setup]
AppName=PyPDFMerger
AppVersion=1.0
DefaultDirName={pf}\PyPDFMerger
OutputDir=userdocs:Inno Setup Examples Output
OutputBaseFilename=setup
SetupIconFile=icon.ico
Compression=lzma
LicenseFile=LICENSE
SolidCompression=yes

[Files]
Source: "dist\pypdfmerger\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PyPDFMerger"; Filename: "{app}\pypdfmerger.exe"

[Run]
Filename: "{app}\pdf_merger.exe"; Description: "Launch PyPDFMerger"; Flags: nowait postinstall skipifsilent
