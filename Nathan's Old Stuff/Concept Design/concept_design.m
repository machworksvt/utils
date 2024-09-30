%% Design Point - Max Speed Cruise
import casadi.*;


CD0 = 0.03;
WTO = 12.6 * 9.81;
WCr = 11 * 9.81;
Wfuel = 3.69 * 9.81; %kg
WLand = WTO - 0.95*Wfuel;
rho_TO = 1.1638; %kg/m^3
rho_Cr = 1.1298;
rho_climb = 1.14;
Vcruise = 103; %m/s
qcruise = 0.5 * Vcruise^2 * rho_Cr;
e = 0.9;

%Decision variables
b = SX.sym('wingspan');
croot = SX.sym('cr');
ctip = SX.sym('ct');
clmax = 1.2;

cbar = (croot + ctip)/2;

% Some intermediates
S = 0.68;
AR = 5;

CLcruise = WCr/(qcruise*S);
CDcruise = CD0 + (CLcruise^2)/(pi*e*AR);

%Costs
Vstall = sqrt(2*WTO/(rho_TO*S*clmax));
LDcruise = CLcruise/CDcruise;

%Setup for constraints
VTO = 1.2*Vstall;
VL = 1.3*Vstall;

FeffTO = 0.9 * 97; 
%assume 90% ssl thrust is effective force
FeffL = 60; %assume we can produce 60N back force between braking and spoilers(?)

STO = (1.44*WTO^2)/(9.81*rho_TO*S*clmax*FeffTO);
SL = (1.69*WLand^2)/(9.81*rho_TO*S*clmax*FeffL);

DCruise = CDcruise*qcruise*S;

ct = 0.15*9.81; %N/Nh
E = (1/ct)*LDcruise*log(WCr/WLand);

f = -LDcruise;
x = [b; croot; ctip];
g = [STO; SL; E; AR];

x0 = [1.4377; 0.3048; 0.1778];
lbx = [0.762; 0.2794; 0.127];
ubx = [1.778; 0.33; 0.2286];

    % Wingspan between 30 inches and 70 inches
    % root chord between 11 inches and 13 inches
    % tip chord between 5 inches and 9 inches
    % sweep angle between 0 and 30 degrees
    % clmax less than 3

lbg = [-inf; -inf; 0.33; 3];
ubg = [70; 70; inf; 5];

    % Rate of climb at cruise not less than 100 ft/min
    % Takeoff and Land distances of not more than 70 meters
    % Endurance (cruise) not less than 20 minutes
    % Effective Aspect ratio between 3 and 5

problem = struct('x', x, 'f', f, ...
                 'g', g);
solver = nlpsol('S', 'ipopt', problem);

res = solver('x0', x0, ...
              'lbx', lbx, ...
              'ubx', ubx, ...
              'lbg', lbg, ...
              'ubg', ubg);

solx = full(res.x);
solf = full(res.f);
solg = full(res.g);

disp("Wing Characteristics:");
fprintf("Wingspan: %fm\n", solx(1));
fprintf("Root Chord: %fm\n", solx(2));
fprintf("Tip Chord: %fm\n", solx(3));
fprintf("Clmax: %f\n", clmax);

Vstall = sqrt(2*WTO/(rho_TO*S*clmax));

fprintf("Stall Speed: %f\n", Vstall);

fprintf("Lift to Drag Ratio at Cruise: %f\n", 1/solf);

fprintf("Takeoff Run: %fm\n", solg(1));
fprintf("Landing Run: %fm\n", solg(2));
fprintf("Endurance: %fhr\n", solg(3));
fprintf("Aspect Ratio: %f\n", solg(4));







