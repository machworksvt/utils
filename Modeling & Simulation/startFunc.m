% Pull all relevant data the model needs

%% Aerodynamics

%% Prop

%% Structures

% Pull calculated values from inertia spreadsheet
CG0 = readmatrix("Inertial Props.xlsx",'Sheet','Static Line Items','Range','U3:W3')
M0 = readmatrix("Inertial Props.xlsx",'Sheet','Static Line Items','Range','T1:T1')
I0 = readmatrix("Inertial Props.xlsx",'Sheet','Static Line Items','Range','U7:W9')

