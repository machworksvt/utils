clc

%Script to set parameters (like Span, Chord, ect.) to the Icuras OpenVsp geometry  

%loading/reading design file
filename = 'C:\Users\stevi\AeroGit\Aerodynamics\param.des'; % Path to the .des file
fileID = fopen(filename, 'r');
data = textscan(fileID, '%s', 'Delimiter', '\n');
fclose(fileID);

lines = data{1}; % Each line of the file

% Define new values
newChord = 3; % New value for chord
newSpan = 0.5;  % New value for span
newSweep = 15; % New value for sweep

%Chaning parameter values
for i = 1:length(lines)
    if contains(lines{i}, 'TotalChord') % Check if the line contains 'chord'
        lines{i} = ['KFFTUWAMWNE:MainWing:WingGeom:TotalChord: ', num2str(newChord)]; % Update the line with the new value
    elseif contains(lines{i}, 'TotalSpan') % Check if the line contains 'span'
        lines{i} = ['FAKAJYYYEXH:MainWing:WingGeom:TotalSpan: ', num2str(newSpan)]; % Update the line with the new value
    elseif contains(lines{i}, 'Sweep') % Check if the line contains 'span'
        lines{i} = ['IHHUCGZTHFP:MainWing:XSec_1:Sweep: ', num2str(newSweep)]; % Update the line with the new value
    end
end

%saving to design file
fileID = fopen(filename, 'w');
for i = 1:length(lines)
    fprintf(fileID, '%s\n', lines{i}); % Write each modified line back to the file
end
fclose(fileID);

%Line for command window 
geo_command = '"C:\Users\stevi\AeroGit\OpenVSP-3.39.1-win64\vsp.exe" -des "param.des" "C:\Users\stevi\AeroGit\geometry\icarus_mk2.vsp3" &';


%--------------------------------------------------------------------------------------------------------------------------------

%Calling OpenVSP Within a Script

% Define location of icarus vspaero file to be opened

% in order to have this code run on your computer, find the location of the
% icarus .vspaero file, right click and there should be an option saying
% "COPY AS PATH" then, head over to matlab and CTRL+V, or paste, onto the
% icaruspath command" 

aeropath = 'C:\Users\stevi\AeroGit\geometry\icarus_mk2_VSPGeom.vspaero';

% Use the same process as above to indicate location of vspaero.exe and
% icarus_mk2 2_DegenGeom.vspaero in the line below.
% "-stab" extension can be deleted to remove stability derivatives from
% analysis if required

vspaero_command = 'C:\Users\stevi\AeroGit\OpenVSP-3.39.1-win64\vspaero.exe -omp 4 -dokt "C:\Users\stevi\AeroGit\geometry\icarus_mk2_VSPGeom"';

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

%--------------------------------------------------------------------------------------------------------------------------------

%Opening Icarus and applying modified design file
system(geo_command)
system('"C:\Users\stevi\AeroGit\OpenVSP-3.39.1-win64\vsploads.exe" -save "C:\Users\stevi\AeroGit\geometry\testicuras.vsp3"');


%run DegenGeom

% Run the vspaero command using system() function
[status, cmdout] = system(vspaero_command);

%---------------------------------------------------------------------------------------------------------------------------------

% Check if the command executed successfully

if status == 0
    disp('VSPAERO executed successfully');
    disp(cmdout);  % Displays the output of the command in MATLAB
else
    disp('Error running VSPAERO');
    disp(cmdout);  % Displays any error messages
end
