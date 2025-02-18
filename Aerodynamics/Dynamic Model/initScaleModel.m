
maneuver = CRUISE


coeffMatrix = [0.027 0.121 0 0 0 0 0 0 0 0;
                     0 0     -0.393 0 -0.075 0 0.214 0 0 0.187;
                     0.307 4.41 0 1.7 0 3.9 0 0 0.43 0;
                     0 0 -0.0923 0 -0.484 0 0.0798 0.229 0 0.0147;
                     0.04 -0.613 0 -7.27 0 -12.4 0 0 -1.122 0;
                     0 0 0.0587 0 -0.0278 0 -0.0937 -0.0216 0 -0.0645];
CG = [-0.065 0 0];
CP = [-0.36*0.205 0 0];
SM = (CG(1)-CP(1))/0.205;

CT = 3.5*9.81; %Guess for maximum thrust??

mass = 3.5; %guess for weight of model, kg

inertia = [0.29 0 0; 0 0.3 0; 0 0 0.57]; %first guess based on scaling real C182 by mass ratio