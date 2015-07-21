[Setup]
AppName=INSTEAD Manager
AppVerName=INSTEAD Manager 1.0beta
DefaultDirName={pf}\InsteadManager
DefaultGroupName=Games
UninstallDisplayIcon={app}\instead-manager-tk.exe
OutputDir=.\temp
OutputBaseFilename=instead-manager-1.0beta
AllowNoIcons=true
SetupIconFile=resources\images\logo.ico
ChangesAssociations=yes

[Languages]
Name: en; MessagesFile: compiler:Default.isl
Name: ru; MessagesFile: compiler:Languages\Russian.isl

[Files]
Source: dist\*; DestDir: {app}; Flags: replacesameversion recursesubdirs

[CustomMessages]
CreateDesktopIcon=Create a &desktop icon
LaunchGame=Launch INSTEAD &Manager
UninstallMsg=Uninstall INSTEAD Manager
RmSettingsMsg=Would you like to remove settings?

[Tasks]
Name: desktopicon; Description: {cm:CreateDesktopIcon}

[Run]
Filename: {app}\instead-manager-tk.exe; Description: {cm:LaunchGame}; WorkingDir: {app}; Flags: postinstall

[Icons]
Name: {commondesktop}\INSTEAD Manager; Filename: {app}\instead-manager-tk.exe; WorkingDir: {app}; Tasks: desktopicon
Name: {group}\INSTEAD Manager; Filename: {app}\instead-manager-tk.exe; WorkingDir: {app}
Name: {group}\{cm:UninstallMsg}; Filename: {uninstallexe}

[UninstallDelete]
Name: {app}; Type: dirifempty

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  case CurUninstallStep of
    usPostUninstall:
      begin
        if MsgBox(CustomMessage('RmSettingsMsg'), mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = idYes then
        begin
          // remove settings and saved games manually
          DelTree(ExpandConstant('{localappdata}\instead\manager'), True, True, True);
        end;
      end;
  end;
end;
