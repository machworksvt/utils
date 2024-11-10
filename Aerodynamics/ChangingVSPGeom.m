clc
%Script to set parameters (like Span, Chord, ect.) to the Icuras OpenVsp geometry  

%loading/reading design file
filename = 'C:\Users\stevi\AeroGit\Aerodynamics\param.des'; % Path to the .des file
fileID = fopen(filename, 'r');
data = textscan(fileID, '%s', 'Delimiter', '\n');
fclose(fileID);

lines = data{1}; % Each line of the file

% Define new values
newChord = 0.5; % New value for chord
newSpan = 3.0;  % New value for span
newSweep = 6; % New value for sweep

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

%Opening Icarus and applying modified design file
system('"C:\Users\stevi\AeroGit\OpenVSP-3.39.1-win64\vsp.exe" -des "param.des" "C:\Users\stevi\AeroGit\geometry\icarus_mk2.vsp3"');

