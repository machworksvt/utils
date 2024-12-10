import casadi.*;
%{
    Inlet Geometry Creation/Analysis Tool
    Author: Nathan Collins
    Contributors:

    Date Created: 12/9/24

    This script takes parameters of the H20PRO engine and chooses an
    optimal geometry. Consult Docs for more explanation
%}

%Engine parameters
rho = 1.1798; % Air density (kg/m3)
mdot_engine = 300 * 0.001 * rho; % 300 L/s -> m3/s
r_engine_intake = 38.5 * 0.001; %radius of intake zone of engine
r_engine = 111 * 0.001; % radius of outer case of engine

%Aircraft parameters
V_max = 100; %m/s
W = 12.46 * 9.81; % weight from mass estimate
S = 0.555; % wing area from VSP model
CLmax = 1.4; % this is for sure wrong! lol

V_stall = sqrt(2 * W /(rho * S * CLmax));
V_TO = 1.2 * V_stall;
V_av_TO = 0.7 * V_TO;

d = SX.sym('d'); % Parameter for algorithm to decide
A_bypass = pi * ((r_engine + d)^2 - r_engine^2); % Area of bypass layer, depends on d
A_inlet = SX.sym('Ai'); % Single inlet face area
m_dot_total_TO = 2 * A_inlet * V_av_TO * rho; %total mass flow through system at TO
m_dot_total_MAX = 2 * A_inlet * V_max * rho; %total mass flow through system at TO
V_dot_total_TO = 2 * A_inlet * V_av_TO; % total volume flow through system at TO

m_dot_bypass_TO = m_dot_total_TO - mdot_engine; %mass flow through bypass at TO
m_dot_bypass_MAX = m_dot_total_MAX - mdot_engine;%mass flow through bypass at Vmax

V_dot_bypass_TO = m_dot_bypass_TO / rho; %volume flow through bypass at TO
V_bypass_TO = m_dot_bypass_TO / (rho * A_bypass); %speed through bypass at vmax
V_bypass_MAX = m_dot_bypass_MAX / (rho * A_bypass); %speed through bypass at vmax

T_TO = -2*V_av_TO*A_inlet*rho + m_dot_bypass_TO*V_bypass_TO % "Net thrust" from intake configuration

nlp = struct;
nlp.x = [A_inlet, d];
nlp.f = A_inlet;
nlp.g = [V_bypass_MAX, d, V_dot_bypass_TO, V_dot_total_TO];

lbg = [0, 0.01, 150*0.001, 450 * 0.001];
ubg = [0.7*343, inf, inf, inf];

F = nlpsol('F', 'ipopt', nlp);
sol = F('x0', [0.05, 0.01], 'ubg', ubg, 'lbg', lbg);

fprintf("Results:\n")
fprintf("Single Inlet Area (m^2): %f\n", full(sol.x(1,1)));
fprintf("Bypass Width (m): %f\n", full(sol.x(1,2)));
fprintf("Bypass Layer Velocity at Max Speed (m/s): %f\n", full(sol.g(1,1)));
fprintf("Bypass Layer Volume Flow at TO (L/s): %f\n", 1000*full(sol.g(1,3)));
fprintf("Total Volume Flow at TO (L/s): %f\n", 1000*full(sol.g(1,4)));












