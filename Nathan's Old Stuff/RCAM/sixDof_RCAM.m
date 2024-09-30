function xdot = sixDof_RCAM(x, u)
    %% Setup States and Controls
    x1 = x(1); % u, Vx in Fb
    x2 = x(2); % v, Vy
    x3 = x(3); % w, Vz
    x4 = x(4); % p, wx in Fb
    x5 = x(5); % q, wy
    x6 = x(6); % r, wz
    x7 = x(7); % phi, bank euler angle
    x8 = x(8); % theta, pitch
    x9 = x(9); % psi, yaw

    u1 = u(1); % d_A (aileron)
    u2 = u(2); % d_T (stabilizer)
    u3 = u(3); % d_R (rudder)
    u4 = u(4); % d_th1 (throttle 1)
    u5 = u(5); % d_th1 (throttle 2)

    %% Vehicle Constants
    m = 120000; %total A/C mass, kg

    cbar = 6.6; % MAC (m)
    lt = 24.8; % Dist CG -> AC tail (m)
    S = 260; % Planform area of wing (m^2)
    St = 64; % Planform area of tail/elevator (m^2)

    Xcg = 0.23*cbar; %x position of CoG in Fm (m)
    Ycg = 0;         %y position of CoG in Fm (m) 
    Zcg = 0.10*cbar; %z position of CoG in Fm (m)

    Xac = 0.12*cbar; %x position of AC in Fm (m)
    Yac = 0;         %y
    Zac = 0;         %z

    Xapt1 = 0;       %x position of Engine 1 force in Fm (m)
    Yapt1 = -7.94;   %y
    Zapt1 = -1.9;    %z

    Xapt2 = 0;       %x position of Engine 2 force in Fm (m)
    Yapt2 = 7.94;    %y
    Zapt2 = -1.9;    %z

    rho = 1.225;     %air density (kg/m^3)
    g = 9.81;        %gravitational acceleration (m/s^2)
    depsda = 0.25;   %change in downwash wrt alpha (rad/rad)
    alpha_LO = -11.5 * (pi/180); % zero lift alpha
    n = 5.5;         %change in Clwb wrt Alpha, for linear region
    a3 = -786.5;     %coeff alpha^3
    a2 = 609.2;      %coeff alpha^2
    a1 = -155.2;     %coeff alpha^1
    a0 = 15.212;     %coeff alpha^0
    alpha_switch = 14.5 * (pi/180); % alpha where stall behavior begins

    %% Intermediate Semi-States

    Va = sqrt(x1^2 + x2^2 + x3^2); %airspeed

    alpha = atan2(x3, x1); %AoA
    beta = asin(x2/Va); %Beta

    Q = 0.5*rho*Va^2; %Dynamic Pressure

    wbe_b = [x4;x5;x6]; %Angular velocity vector in body frame
    V_b = [x1;x2;x3]; %Linear velocity vector in the body frame

    %% Aerodynamic Force Coefficients

    %Calc lift coeff of WB
    if alpha <= alpha_switch
        CL_wb = n*(alpha-alpha_LO);
    else
        CL_wb = a3*alpha^3 + a2*alpha^2 + a1*alpha + a0;
    end

    %Calculate lift coeff of tail
    epsilon = depsda*(alpha - alpha_LO);
    alpha_t = alpha - epsilon + u2 + 1.3*x5*lt/Va;
    CL_t = 3.1*(St/S)*alpha_t; %note normalized for characteristic wing area

    %Total lift coeff
    CL = CL_wb + CL_t;

    %Total Drag Force coeff
    CD = 0.13 + 0.07*(5.5*alpha + 0.654)^2;

    %Total Sideforce coeff
    CY = -1.6*beta + 0.24*u3;

    %% Dimensional Aerodynamic Forces
    FA_s = [-CD*Q*S;
            CY*Q*S;
            -CL*Q*S]; %Actual aerodynamic forces in Stability Acess

    C_bs = [cos(alpha) 0 -sin(alpha);
            0          1 0;
            sin(alpha) 0 cos(alpha)]; %Rotate Fs -> Fb thru alpha

    FA_b = C_bs * FA_s; %aerodynamic forces in Fb

    %% Aerodynamic Moment Coefficient about AC

    %calculate moments in Fb.
    eta11 = -1.4*beta;
    eta21 = -0.59 - (3.1*(St*lt)/(S*cbar))*(alpha - epsilon);
    eta31 = (1 - alpha*(180/(15*pi)))*beta;

    eta = [eta11;eta21;eta31];

    dCMdx = (cbar/Va)*[-11 0 5;
                       0 (-4.03*(St*lt^2)/(S*cbar)) 0;
                       1.7 0 -11.5];

    dCMdu = [-0.6 0 0.22;
             0 (-3.1*(St*lt)/(S*cbar)) 0;
             0 0 -0.63];

    CMac_b = eta + dCMdx*wbe_b + dCMdu*[u1;u2;u3];

    %% Dimensional Aerodynamic Moment about AC
    MAac_b = CMac_b*Q*S*cbar;

    %% Aerodynamic Moment about CG

    rcg_b = [Xcg;Ycg;Zcg];
    rac_b = [Xac;Yac;Zac];
    MAcg_b = MAac_b + cross(FA_b, rcg_b - rac_b); %Moment transfe*r

    %% Engine Force and Moment

    %Engine Thrust
    F1 = u4*m*g;
    F2 = u5*m*g;

    %Assume Engine thrust aligned with Fb
    FE1_b = [F1;0;0];
    FE2_b = [F2;0;0];

    FE_b = FE1_b + FE2_b;

    mew1 = [Xcg-Xapt1;
            Yapt1-Ycg;
            Zcg-Zapt1];

    mew2 = [Xcg-Xapt2;
            Yapt2-Ycg;
            Zcg-Zapt2];

    MEcg1_b = cross(mew1,FE1_b);
    MEcg2_b = cross(mew2,FE2_b);

    MEcg_b = MEcg1_b + MEcg2_b;

    %% Gravity Affects

    g_b = [-g*sin(x8);
           g*cos(x8)*sin(x7);
           g*cos(x8)*cos(x7)];

    Fg_b = m*g_b;

    %% State Derivatives

    Ib = m*[40.04 0 -2.0923;
            0 64 0;
            -2.0923 0 99.92];

    invIb = (1/m)*[0.0249836 0 0.000523151;
                   0 0.015625 0;
                   0.000523151 0 0.010019];

    %Add all forces together and calculate accelerations
    F_b = Fg_b + FE_b + FA_b;
    x1to3dot = (1/m)*F_b - cross(wbe_b,V_b); %haha this is a - wXr lol

    %Add all moments together, abt CG in FB, calculate angular acclerations
    Mcg_b = MAcg_b + MEcg_b;
    x4to6dot = invIb*(Mcg_b - cross(wbe_b,Ib*wbe_b));

    %Calculate euler angle derivatives

    H_phi = [1 sin(x7)*tan(x8) cos(x7)*tan(x8);
             0 cos(x7) -sin(x7);
             0 sin(x7)/cos(x8) cos(x7)/cos(x8)];

    x7to9dot = H_phi*wbe_b;

    xdot = [x1to3dot;x4to6dot;x7to9dot];

end