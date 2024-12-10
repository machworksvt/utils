clc
%Script to run vspaero on differnt wing geometries, moving each .stab file to the output folder
%while plotting Cl, Cd, Lift, L/D vs AoA and outputing coefficent tables to command window for each version 

%--------------------------------------------------------------------------------------------------------------------------------
%Things you need to change beofore running on your computer

% File Paths (CHANGE FOR YOUR PATHS)
vspscriptPath = 'C:\Users\stevi\AeroGit\OpenVSP-3.41.1-win64\vspscript.exe'; %path to vspscript.exe
vspaeroExePath = 'C:\Users\stevi\AeroGit\OpenVSP-3.41.1-win64\vspaero.exe'; %vspaero.exe file path
originalFile = 'C:\Users\stevi\AeroGit\geometry\testicuras_DegenGeom.stab'; % path to original .stab file(must run vspaero to get)
%.stab and plots output location (In my version I save them to an output folder in Aerodynamics, I would 
% recomend it for orginization it but its not needed)
outputLocation = 'C:\Users\stevi\AeroGit\Aerodynamics\output\';

%These are in the Git (-> Aerodynamics) need to download them then use your own paths
scriptFilePath = 'C:\Users\stevi\AeroGit\Aerodynamics\UpdatingParams.vspscript'; % Path to .vspscript script
vsp3FilePath = 'C:\Users\stevi\AeroGit\geometry\testicuras.vsp3'; %path to .vsp3 file
aeropath = "C:\Users\stevi\AeroGit\geometry\testicuras_DegenGeom.vspaero"; %path to degen geom file (must be .vspaero)
aeropathForCMD = "C:\Users\stevi\AeroGit\geometry\testicuras_DegenGeom"; % literaly the exact same path as above just delete the .vspaero from the end


%--------------------------------------------------------------------------------------------------------------------------------
% These are the ranges of parameters to run through (CHANGE THESE FOR WHAT YOU WANT)
chord = 0.2;
span = 2:6:8;
sweep = 8;

run = 0; %run number (dont change this)

%--------------------------------------------------------------------------------------------------------------------------------
%Start of loop
for c = chord
    for s = span 
        for sw = sweep

%New parameters we want
newChord = c; 
newSpan = s; 
newSweep = sw;

%--------------------------------------------------------------------------------------------------------------------------------
%Design Subteam code to change and save openVSP params

% The UpdatingParams.vspscript does the brunt of the work using the openVSP API this is
% just changing the parameters in the .vspscript then running it through
% vsp using the command window

% Importing the .vspscript to MATLAB
fileID = fopen(scriptFilePath, 'r');
scriptLines = {};
tline = fgetl(fileID);
while ischar(tline)
    scriptLines{end+1} = tline;
    tline = fgetl(fileID);
end
fclose(fileID);

% Changing the parameter values to the new ones wanted
for i = 1:length(scriptLines)
    if contains(scriptLines{i}, 'SetParmVal( span_id,')
        scriptLines{i} = ['SetParmVal( span_id, ', num2str(newSpan), ' );'];
    elseif contains(scriptLines{i}, 'SetParmVal( chord_id,')
        scriptLines{i} = ['SetParmVal( chord_id, ', num2str(newChord), ' );'];
    elseif contains(scriptLines{i}, 'SetParmVal( sweep_id,')
        scriptLines{i} = ['SetParmVal( sweep_id, ', num2str(newSweep), ' );'];
    end
end

% Saving back to original UpdatingParams.vspscript file
fileID = fopen(scriptFilePath, 'w');
for i = 1:length(scriptLines)
    fprintf(fileID, '%s\n', scriptLines{i});
end
fclose(fileID);
disp('Script updated successfully.');


% Running the .vspscript in openVSP using the command window
cmd = sprintf('"%s" -script "%s" "%s"', vspscriptPath, scriptFilePath, vsp3FilePath);

% Just an output to check if it works (it does)
[status, ~] = system(cmd);
if status == 0
    disp('Executed successfully');
else
    disp('Failed')
end
%--------------------------------------------------------------------------------------------------------------------------------
%This updates the testicuras_DegenGeom.vspaero file with the new geometry (This is needed to run Dynamics subteam code)
%(Note: definitly a better way to do this might wanna change for later versions of script) 

% Define the new values for Sref, Cref, and Bref (rounds to 6th decimal place)
Sref = sprintf('%.6f', round(0.9040166667*newChord*newSpan, 6)); %Eqation for Wing Area
Cref = sprintf('%.6f', round(newChord,6)); %chord
Bref = sprintf('%.6f', round(newSpan,6)); %wing span

% Imports DegenGeom file to MATLAB
fileID = fopen(aeropath, 'r');
fileLines = {};
tline = fgetl(fileID);
while ischar(tline)
    fileLines{end+1} = tline;
    tline = fgetl(fileID);
end
fclose(fileID);

% Changed Sref, Cref, and Bref for what we want
for i = 1:length(fileLines)
    if contains(fileLines{i}, 'Sref')
        fileLines{i} = ['Sref = ', num2str(Sref)];
    end

    if contains(fileLines{i}, 'Cref')
        fileLines{i} = ['Cref = ', num2str(Cref)];
    end

    if contains(fileLines{i}, 'Bref')
        fileLines{i} = ['Bref = ', num2str(Bref)];
    end
end

% Saving the original DegenGeom file
fileID = fopen(aeropath, 'w');
for i = 1:length(fileLines)
    fprintf(fileID, '%s\n', fileLines{i});
end
fclose(fileID);

disp('File updated successfully.'); %output for completion

%--------------------------------------------------------------------------------------------------------------------------------
%Dynamics Subteam code to run vspaero and update .stab file for new params. 

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

vspaero_command = sprintf('"%s" -omp 4 -stab -dokt "%s"', vspaeroExePath, aeropathForCMD);

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

%--------------------------------------------------------------------------------------------------------------------------------
%That was the end of the openVSP portion the rest is just making the
%tables, plots, and saving .stab files for each run

%--------------------------------------------------------------------------------------------------------------------------------
%Saving the .stab files for each run 

run = run+1; %updating run number (Note: there is no run0) 

% Check if the file exists
if ~isfile(originalFile)
    error('The file "%s" does not exist.', originalFile);
end

% Create new .stab file for run
newFileName = sprintf('%stesticuras_DegenGeom00%d.stab', outputLocation, run);
       
% copying .stab file
fileContent = fileread(originalFile);
        
% pasting to new .stab file
fid = fopen(newFileName, 'w');
if fid == -1
   error('Error opening file "%s" for writing.', newFileName);
end
fwrite(fid, fileContent);
fclose(fid);
    
% Output to say it worked
fprintf('Created file: %s\n', newFileName);

%end of loop
        end
    end
end

%--------------------------------------------------------------------------------------------------------------------------------
%Ouputs Coeffs and Lift vs AoA tables for each run and plots Cl, CD,
%Lift, L/D vs AoA 

%loops through runs
for i = 1:run
filePath = sprintf("%stesticuras_DegenGeom00%d.stab",outputLocation,i);

% Initialize variables
AoA_values = [];
aoa_data_values = [];
data_table = [];
coeff_matrix = [];
row_headers = {};
col_headers = {};
is_reading_coeff = false;

% Import runs .stab file to MATLAB
fid = fopen(filePath, 'r');
while ~feof(fid)
    line = strtrim(fgetl(fid));

    % Check for AoA values
    if contains(line, 'AoA_')
        % Extract the AoA value
        part = strsplit(line);
        AoA = str2double(part{2});
        AoA_values = [AoA_values; AoA]; % Append the AoA value
    end
    
    % Check for alpha data values
    if contains(line, 'Alpha                  ')
        partz = strsplit(line);
        aoa_data = str2double(partz(4:15)); % Extract data from columns 4 to 15
        aoa_data_values = [aoa_data_values; aoa_data]; % Append the data row
    end

    % Detect column headers (e.g., 'Coef          Total Alpha Beta ...')
    if contains(line, 'Coef          ')
        parts = strsplit(line);
        col_headers = parts(2:end); % Extract the column headers dynamically
        is_reading_coeff = true; % Set the flag to start reading coefficient values
        continue; % Skip to the next line
    end
  
end

% Close the file
fclose(fid);

% Create the main data table
headers = {'CFx', 'CFy', 'CFz', 'CMx', 'CMy', 'CMz', 'CL', 'CD', 'CS', 'CMl', 'CMm', 'CMn'};
data_table = array2table(aoa_data_values, 'VariableNames', headers);
data_table.AoA = AoA_values;

% Reorder columns to place AoA as the first column
data_table = movevars(data_table, 'AoA', 'Before', 'CFx');

% Calculate Lift for Each AoA
density = 1.089; % at sea level (kg/m^3)
weight = 12.6; % Aircraft weight (kg)
A = 0.56126; % Wing area
v = 102.9; % Velocity (m/s)
L = 0.5 * density * v^2 * A .* data_table.CL; % Calculate Lift for each AoA

% Add Lift and Weight Difference Columns
data_table.LiftForce = L; % Add Lift force column
data_table.Weight = repmat(weight, height(data_table), 1); % Add weight column
data_table.Difference = data_table.LiftForce - data_table.Weight; % Add lift-weight difference column

% Display the updated table
disp(data_table);

%Plotting the coeffs

% Getting coeffs and AoAs from table
AoA = data_table.AoA;
Cl = data_table.CL;
Cd = data_table.CD;
L = data_table.LiftForce;

% Calculate Cl/Cd
Cl_Cd = Cl ./ Cd;

% AoA vs Cl plot
figure(1);
hold on; % Retain previous data for overlapping plots
plot(AoA, Cl, 'LineWidth', 1.5, 'DisplayName', sprintf('Run %d', i));

% AoA vs Cd plot
figure(2);
hold on;
plot(AoA, Cd, 'LineWidth', 1.5, 'DisplayName', sprintf('Run %d', i));

% AoA vs Lift plot
figure(3);
hold on;
plot(AoA, L, 'LineWidth', 1.5, 'DisplayName', sprintf('Run %d', i));

% AoA vs L/D plot
figure(4);
hold on;
plot(AoA, Cl_Cd, 'LineWidth', 1.5, 'DisplayName', sprintf('Run %d', i));

end

%Plot atributes (need to be outside of loop)
figure(1);
xlabel('AoA [deg]');
ylabel('C_L');
title('AoA vs C_L');
grid on;
legend show;

figure(2);
legend show;
xlabel('AoA [deg]');
ylabel('C_D');
title('AoA vs C_D');
grid on;

figure(3);
legend show;
xlabel('AoA [deg]');
ylabel('Lift Force (L) [N]');
title('AoA vs Lift');
grid on;

figure(4);
legend show;
xlabel('AoA [deg]');
ylabel('C_L / C_D');
title('AoA vs C_L / C_D');
grid on;