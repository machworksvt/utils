clc
%Script to set and save paramaters in openVSP then run vspaero to get  

%--------------------------------------------------------------------------------------------------------------------------------
%Things you need to change beofore running on your computer

% File Paths (CHANGE FOR YOUR PATHS)
vspscriptPath = 'C:\Users\stevi\AeroGit\OpenVSP-3.41.1-win64\vspscript.exe'; %path to vspscript.exe
vspaeroExePath = 'C:\Users\stevi\AeroGit\OpenVSP-3.41.1-win64\vspaero.exe'; %vspaero.exe file path

%These are in the Git (-> Aerodynamics) need to download them then use your own paths
scriptFilePath = 'C:\Users\stevi\AeroGit\Aerodynamics\UpdatingParams.vspscript'; % Path to .vspscript script
vsp3FilePath = 'C:\Users\stevi\AeroGit\geometry\testicuras.vsp3'; %path to .vsp3 file
aeropath = 'C:\Users\stevi\AeroGit\geometry\testicuras_DegenGeom.vspaero'; %path to degen geom file (must be .vspaero)
aeropathForCMD = "C:\Users\stevi\AeroGit\geometry\testicuras_DegenGeom"; % Need to delete the .vspaero from the end of the aeropath file


%--------------------------------------------------------------------------------------------------------------------------------
%These are varibale to change (we will be replacing this with the nested loop to go through all versions)

% Define new values
newChord = 0.2; % New value for chord
newSpan = 3.0;  % New value for span
newSweep = 6; % New value for sweep

%--------------------------------------------------------------------------------------------------------------------------------
%Design Subteam code to change and save openVSP params

% Read the contents of the .vspscript file into a cell array, each cell is a line
fileID = fopen(scriptFilePath, 'r');
scriptLines = {};
tline = fgetl(fileID);
while ischar(tline)
    scriptLines{end+1} = tline; % Add each line to the cell array
    tline = fgetl(fileID);
end
fclose(fileID);

% Loop through the lines and modify the varibale lines based on the line number
for i = 1:length(scriptLines)
    % Check if this line contains span or chord, and update accordingly
    if contains(scriptLines{i}, 'SetParmVal( span_id,')
        scriptLines{i} = ['SetParmVal( span_id, ', num2str(newSpan), ' );'];
    elseif contains(scriptLines{i}, 'SetParmVal( chord_id,')
        scriptLines{i} = ['SetParmVal( chord_id, ', num2str(newChord), ' );'];
    elseif contains(scriptLines{i}, 'SetParmVal( sweep_id,')
        scriptLines{i} = ['SetParmVal( sweep_id, ', num2str(newSweep), ' );'];
    end
end

% Write the updated lines back to the file
fileID = fopen(scriptFilePath, 'w');
for i = 1:length(scriptLines)
    fprintf(fileID, '%s\n', scriptLines{i});
end
fclose(fileID);

disp('Script updated successfully.');


% Construct the system command using the variables
cmd = sprintf('"%s" -script "%s" "%s"', vspscriptPath, scriptFilePath, vsp3FilePath);

% Run the command
[status, ~] = system(cmd);
if status == 0
    disp('Executed successfully');
else
    disp('Failed')
end
%--------------------------------------------------------------------------------------------------------------------------------
%This updates the Degen Geom file (aeropath) with the new geometry (This is needed to run Dynamics subteam code)

% Define the new values for Sref, Cref, and Bref (rounds to 6th decimal place)
Sref = sprintf('%.6f', round(0.9040166667*newChord*newSpan, 6)); %Eqation for Wing Area
Cref = sprintf('%.6f', round(newChord,6));
Bref = sprintf('%.6f', round(newSpan,6));

% Read the contents of the file into a cell array, each cell is a line
fileID = fopen(aeropath, 'r');
fileLines = {};
tline = fgetl(fileID);
while ischar(tline)
    fileLines{end+1} = tline; % Add each line to the cell array
    tline = fgetl(fileID);
end
fclose(fileID);

% Loop through the lines and modify the values for Sref, Cref, and Bref
for i = 1:length(fileLines)
    % Update Sref
    if contains(fileLines{i}, 'Sref')
        fileLines{i} = ['Sref = ', num2str(Sref)];
    end
    
    % Update Cref
    if contains(fileLines{i}, 'Cref')
        fileLines{i} = ['Cref = ', num2str(Cref)];
    end
    
    % Update Bref
    if contains(fileLines{i}, 'Bref')
        fileLines{i} = ['Bref = ', num2str(Bref)];
    end
end

% Write the updated lines back to the file
fileID = fopen(aeropath, 'w');
for i = 1:length(fileLines)
    fprintf(fileID, '%s\n', fileLines{i});
end
fclose(fileID);

disp('File updated successfully.');

%--------------------------------------------------------------------------------------------------------------------------------
%Dynamics Subteam code to run vspaero and output the stability derivatives, Coefficents, etc. 

%Calling OpenVSP Within a Script

% Define location of icarus vspaero file to be opened

% in order to have this code run on your computer, find the location of the
% icarus .vspaero file, right click and there should be an option saying
% "COPY AS PATH" then, head over to matlab and CTRL+V, or paste, onto the
% icaruspath command" 

%aeropath = 'C:\Users\stevi\AeroGit\geometry\icarus_mk2_VSPGeom.vspaero'; (moved up top)

% Use the same process as above to indicate location of vspaero.exe and
% icarus_mk2 2_DegenGeom.vspaero in the line below.
% "-stab" extension can be deleted to remove stability derivatives from
% analysis if required

vspaero_command = sprintf('"%s" -omp 4 -dokt "%s"', vspaeroExePath, aeropathForCMD);

% Input desired angles of attack to be tested
desiredAoAs = [-10 -5 0 5 10];

% Opens .vspaero file
fid = fopen(aeropath,'r+');

% Sorts text into cell array
C = textscan(fid,'%s','delimiter','\n');

% Creates new text line for AoA
newAoA = num2str(desiredAoAs,' %.6f,');
C{1,1}{8,1} = append('AoA = ',newAoA(1:end-1));

% Rewrite .vspaero file with new line in place and close file
writecell(C{1,1},aeropath,'FileType','text','QuoteStrings','none')
fclose(fid);

% Run the vspaero command using system() function
[status1, cmdout] = system(vspaero_command);

% Check if the command executed successfully
if status == 0
    disp('VSPAERO executed successfully');
    disp(cmdout);  % Displays the output of the command in MATLAB
else
    disp('Error running VSPAERO');
    disp(cmdout);  % Displays any error messages
end
