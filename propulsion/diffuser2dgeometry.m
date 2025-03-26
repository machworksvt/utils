% Parameters of diffuser
length_of_diffuser = 120;           % Length of outer shell (mm)
final_outer_diameter = 91;            % End of outer diameter (mm)
initial_outer_diameter = 51;             % Initial outer diameter (mm)
inner_diameter = 45;     % Initial inner diameter (mm)
length_flow_separation = 80;   % Length of flow separation (mm)

% Coordinates of the outside of the diffuser
outer_x = [length_of_diffuser, length_of_diffuser, 0, 0];   % Vertical positions of outer part of diffuser
outer_y = [-final_outer_diameter/2, final_outer_diameter/2, initial_outer_diameter/2, -initial_outer_diameter/2];  % Horizontal positions of the outer part of the diffuser

% Plot the diffuser
figure;
hold on;
fill(outer_x, outer_y, 'cyan', 'FaceAlpha', 0.5);

% Coordinates of flow separation part
flow_separation_x = [0, 0, length_flow_separation];  % Vertical side of flow separation part
flow_separation_y = [-inner_diameter/2, inner_diameter/2, 0];  % Horizontal side of flow separation part

% Plot the flow separation part
fill(flow_separation_x, flow_separation_y, 'r', 'FaceAlpha', 0.7);

% Set axis and labels
axis equal;
xlabel('Length (mm)');
ylabel('Width (mm)');
title('Diffuser Geometry');

hold off;
