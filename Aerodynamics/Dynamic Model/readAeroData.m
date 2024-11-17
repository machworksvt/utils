function data = readAeroData()
    spec = fileread('Processed_Extra_300_DegenGeom.stab');
    rawData = fscanf('Extra_300_DegenGeom.stab', spec);
    data = struct();
    data.Sref = rawData(1);
    data.Cref = rawData(2);
    data.Bref = rawData(3);
    data.CG = rawData(4:6);
    data.Mach = rawData(7);
    data.AoA = rawData(8);
    data.AoS = rawData(9);
    data.rho = rawData(10);
    data.Vinf = rawData(11);
    data.P = rawData(12);
    data.Q = rawData(13);
    data.R = rawData(14);
    Cases = ["Base";"Alpha";"Beta";"P";"Q";"R";"Mach";"Ailerons";"Elevators";"Rudder"];
    Delta = [0;1;1;1;1;1;0.1;1;1;1];
    Units = ["N/A";"deg";"deg";"rad/s";"rad/s";"rad/s";"Mach #";"deg";"deg";"deg"];
    coeffs = reshape(rawData(15:134),12,10)';
    CFx = coeffs(:,1);
    CFy = coeffs(:,2);
    CFz = coeffs(:,3);
    CMx = coeffs(:,4);
    CMy = coeffs(:,5);
    CMz = coeffs(:,6);
    CL = coeffs(:,7);
    CD = coeffs(:,8);
    CS = coeffs(:,9);
    CMl = coeffs(:,10);
    CMm = coeffs(:,11);
    CMn = coeffs(:,12);
    data.Cases = table(Cases, Delta, Units, CFx, CFy, CFz, CMx, CMy, CMz, CL, CD, CS, CMl, CMm, CMn);

    derivs = reshape(rawData(135:266), 11, 12)';
    Coeff = ["CFx";"CFy";"CFz";"CMx";"CMy";"CMz";"CL";"CD";"CS";"CMl";"CMm";"CMn"];
    Base = derivs(:,1);
    Alpha = derivs(:,2);
    Beta = derivs(:,3);
    P = derivs(:,4);
    Q = derivs(:,5);
    R = derivs(:,6);
    Mach = derivs(:,7);
    U = derivs(:,8);
    d_Ail = derivs(:,9);
    d_Elev = derivs(:,10);
    d_Rud = derivs(:,11);

    data.Derivatives = table(Coeff, Base, Alpha, Beta, P, Q, R, Mach, U, d_Ail, d_Elev, d_Rud);

    data.SM = rawData(267);
    data.X_NP = rawData(268);
    % Close the file
    fclose(fid);
end