function [A, B, E] = createLinearizedModel()
    % Goal: Define A, B, xdo st model is:
    % E*xdot = A*x + B*u
    % State vector reduced to [Vt beta alpha phi theta psi Ps Qs Rs]'
    % Control vector reduced to [th d_e d_a d_r]'

    load("initial extra 300 stab analysis.mat");
    m = 5;

    VTe = data.Vinf;

    %% Collect nondimensional relevant derivatives

    derivatives = data.Derivatives{:,2:12};

    % Change (dCfz/dalphadot) considered to be - (dCfz/dq)
    Zalphadot = data.Derivatives;

    % E = - Jacobian of xdot wrt xdot

    E = sparse(9,9);
    A = sparse(9,9);
    B = sparse(9,5);

    E(1,1) = m*1;
    E(2,2) = VTe; 
    E(3,3) = VTe-Zalphadot;







end