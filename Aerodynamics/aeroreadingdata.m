%% MATLAB Code for Reading Aero Data
% Created by: Thomas Turon
% Date: 11/22/2024
%%

clear;
close all;
clc;

% Define the file path
filePath = "E:\MACHWORKS\Programs\OpenVSP-3.37.1-win64\airfoil\icarus_mk2 2_DegenGeom.stab";

% Initialize variables
AoA_values = [];
aoa_data_values = [];
data_table = [];
coeff_matrix = [];
row_headers = {};
col_headers = {};
is_reading_coeff = false;

% Open the file
fid = fopen(filePath, 'r');
if fid == -1
    error('File not found: %s', filePath);
end

% Read the file line by line
while ~feof(fid)
    line = strtrim(fgetl(fid)); % Read the current line and trim spaces

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

% Visualize the comparison
figure;
plot(data_table.AoA, data_table.LiftForce, '-o', 'DisplayName', 'Lift Force');
hold on;
yline(weight, '--r', 'DisplayName', 'Weight');
xlabel('Angle of Attack (AoA)');
ylabel('Force (kg)');
title('Lift Force Compared to Weight');
legend;
grid on;

% Interpolation to find AoA where LiftForce equals weight
AoA = data_table.AoA; % Extract AoA values
LiftForce = data_table.LiftForce; % Extract Lift Force values

% Find AoA where LiftForce = weight (e.g., 12.6 kg)
AoA_at_intersection = interp1(LiftForce, AoA, weight, 'linear', NaN);

% Add marker for intersection point
if ~isnan(AoA_at_intersection)
    scatter(AoA_at_intersection, weight, 100, 'filled', 'DisplayName', 'Intersection');
    text(AoA_at_intersection, weight + 0.5, sprintf('AoA = %.2f', AoA_at_intersection), 'HorizontalAlignment', 'center');
end
hold off;
