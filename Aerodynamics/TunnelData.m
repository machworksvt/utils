%% Open Jet Wind Tunnel Data Extraction
% Koral Hatipkarasulu - 2025

clear;clc

% Script takes folder of wind tunnel data and organizes into an array in
% which the columns are, in order;
% Fan RPM, AoA, Probe x, Probe y, Probe z, Uref, Tref, Pref, Pstat, Pstag,
% all of which are in base SI units except AoA, which is in degrees.
% Individual files MUST be .txt format and follow the naming convention
% NAME_(RPM)_(AoA)_aoa_(pos/neg)_(displacement)(axis).txt

%% Open folder and sort files

% Prompt user to select file containing data
dataFolder = uigetdir;

% Organize files from selected folder
filePattern = fullfile(dataFolder,'*.txt');
fileList = dir(filePattern);
fileCount = size(fileList);

%% Analyze each file

% Create empty array to store data in
Array = zeros([fileCount(1) 10]);

for k = 1 : length(fileList)
    % Store name of file into variables with and without file path
    baseFileName = fileList(k).name;
    fullFileName = fullfile(fileList(k).folder, baseFileName);
    
    % Print which file is currently being processed
    fprintf('Now processing %s\n', baseFileName);

    % Split filename into components
    nameCells = regexp(baseFileName,'_','split');
    cellCount = size(nameCells);

    % Extract RPM and store in Array column 1
    RPMstr = erase(nameCells(2),'RPM');
    RPM = str2double(RPMstr);
    Array(k,1) = RPM;

    % Extract AoA
    AoA = str2double(nameCells(3));
    Array(k,2) = AoA;

    % Check if position data is included in title
    if cellCount(2) > 4
        % Extract position values
        posText = string(nameCells(6));
        position = erase(posText,'.txt');

        % Check whether position is positive or negative
        if string(nameCells(5)) == "neg"
            sign = -1;
        else
            sign = 1;
        end

        % Check which axis has a position value
        if contains(position,'x')
            % Extract x coordinate (if present) and add to array
            xpstr = erase(position,'x');
            xpos = sign*str2double(xpstr)*0.0254;
            Array(k,3) = xpos;

        elseif contains(position,'y')
            % Extract y coordinate (if present) and add to array
            ypstr = erase(position,'y');
            ypos = sign*str2double(ypstr)*0.0254;
            Array(k,4) = ypos;

        elseif contains(position,'z')
            % Extract z coordinate (if present) and add to array
            zpstr = erase(position,'z');
            zpos = sign*str2double(zpstr)*0.0254;
            Array(k,5) = zpos;
        end
    end

    % Opens text file and sorts text into cell array
    fid = fopen(fullFileName);
    fileContent = textscan(fid,'%s','delimiter','\n');

    % Extract line of reference values and split apart
    refLine = fileContent{1,1}{5,1};
    refValues = regexp(refLine,' ','split');

    % Extract reference velocity and add to array
    refVelocity = str2double(refValues(1));
    Array(k,6) = refVelocity;

    % Extract ambient temperature, convert to K, and add to array
    ambientTemp = str2double(refValues(2)) + 273.15;
    Array(k,7) = ambientTemp;

    % Extract ambient pressure, convert to Pa, and add to array
    ambientPress = str2double(refValues(3))*100;
    Array(k,8) = ambientPress;

    % Extract static pressure, convert to Pa, and add to array
    staticLine = fileContent{1,1}{50,1};
    staticLineVals = regexp(staticLine,' ','split');
    staticDiff = str2double(staticLineVals(2))*248.843;
    Array(k,9) = ambientPress + staticDiff;

    % Extract stagnation pressure, convert to Pa, and add to array
    stagLine = fileContent{1,1}{51,1};
    stagLineVals = regexp(stagLine,' ','split');
    stagDiff = str2double(stagLineVals(2))*248.843;
    Array(k,10) = ambientPress + stagDiff;
end

% Display success message if analysis is fully completed
fprintf('Successfully processed %d files.\n',fileCount(1))