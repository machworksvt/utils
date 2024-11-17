mass_flow_max = 0.36; %kg/s
mass_flow_min = 0.075; %kg/s
inlet_ref_diameter = 76; %mm
inlet_ref_area = pi * (76/1000)^2;
isa_density = 1.225;
inlet_max_speed = mass_flow_max / (isa_density * inlet_ref_area) %m/s