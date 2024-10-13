

% function output = dragOutput(parameters)
%   output = equaiton;
% end'
pi =3.14;

function diff_p = hydroEq(rho,g,hg)
    diff_p = -rho*g*diff(hg); %(dhg = differential of altitude)
end

% isothermal ratio in standard atmosphere
function T = tempIsothermalRatio(T1,ar,h,h1)
    T = T1 + ar*(h-h1);
end

function  rho_DIV_rho1 = desntiyIsothermalRatio(e,g,R,T,h,h1) 
rho_DIV_rho1 = e^(-(g/(R*T))*(h - h1)); % = rho/rho1
end

function p_DIV_p1 = pressureIsothermalRatio(T,T1,g,ar,R)
p_DIV_p1 = (T/T1)^(-g/(ar*R)); % = p/p1
end

function rho_DIV_rho1 = densityIsothermalRatioTemp(T,T1,g,ar,R)
rho_DIV_rho1 = (T/T1)^(-g/(ar*R)+1); % = rho/rho1
end

%Compressable in flow

%continutity eq
function rho1_TIMES_A1_TIMES_V1 = contComp(rho2,A2,V2)
rho1_TIMES_A1_TIMES_V1 = rho2*A2*V2; % = rho1*A1*V1
end

% momentum
function dp = momentComp(rho,V) 
    dp = -rho*V*diff(V);
end

%energy
function cp_TIMES_T1_PLUS_0_POINT_5_TIMES_V1_POWER_2 = energy(cp,T2,V2)
cp_TIMES_T1_PLUS_0_POINT_5_TIMES_V1_POWER_2 = cp*T2 + 0.5*V2^2; % = cp*T1 + 0.5*V1^2
end

%Incompressible Flow

%continutity eq
function A1_TIMES_V1 = contIncomp(A2,V2)
A1_TIMES_V1 = A2*V2; % =A1*V1
end

% momentum
function p1_PLUS_rhoV1_POWER_2_DIV_2= momentIncomp(p2,rho,V2)
p1_PLUS_rhoV1_POWER_2_DIV_2 = p2 + rho((V2^2)/2); % =p1 + roh((V1^2)/2)
end

%Bernoullis Eq
function P2_DIV_P1 = Bernoullis(rho2,rho1,lamba)
P2_DIV_P1 = (rho2/rho1)^(lamba); % = P2/P1 = (T2/T1)^(gamma/(gamma-1));
end


%speed of sound
function a = speedOfSoundIsen(p,rho)
    a = (diff(p)/diff(rho))^(1/2); %isentropic
end

function a = speedOfSoundPgas(gamma,R,T)
    a = (gamma*R*T)^(1/2); %perfect gas
end

%speed of gas flow
function V1 = speedOfGasIncomp(P0,P1,rho)
    V1 = ((2*(P0-P1))/rho)^(1/2); %(incompressable)
end

function V1 = speedOfGasComp(a1,gamma,p0,p1)
    V1 = (((2*a1^2)/(gamma-1))*(((p0/p1)^((gamma-1)/gamma)-1))^(1/2)); %(compressable)
end

%isentropic area velocity relation
function dA_DIV_A = IsenAVRelation(M,V)
    dA_DIV_A = (M^2-1)*(diff(V)/V); % =dA/A
end

%Isentropic flow of a gas
function T0_DIV_T1 = TempIsenFlow(gamma,M1)
    T0_DIV_T1 = 1+((gamma-1)/2)*M1^2; % =T0/T1
end

function p0_DIV_p1 = PresIsenFlow(gamma,M1)
    p0_DIV_p1 = (1+((gamma-1)/2)*M1^2)^(gamma/(gamma-1)); % =p0/p1
end

function rho0_DIV_rho1 = DensIsenFlow(gamma,M1)
    rho0_DIV_rho1 = (1+((gamma-1)/2)*M1^2)^(1/(gamma-1));
end

%Shear Sterss
function t = shearStress(mue,V,y)
    t = mue*(diff(V)/diff(y)); %y=0
end

%laminar incompressable boundary layer
function Rex = LamIncompBLlocal(rho,V,x,meu)
    Rex = (rho*V*x)*meu; % local
end

function Rel = LamIncompBLplate(rho,V,length,meu)
    Rel = (rho*V*length)*meu; %plate
end

function delta = lamIncompBL(x,Rex) 
    delta = 5.2*x/((Rex)^(1/2)); 
end

function Cf = totalSkinFricLam(Rel)
    Cf = 1.328/((Rel)^(1/2)); %total skin friction
end

%turbulent incompressable boundary layer

function delta = turbIncompBL(x,Rex) 
    delta = .37*x/((Rex)^(0.2)); 
end

function Cf = totalSkinFricTurb(Rel)
    Cf = 0.074*((Rel)^(0.2)); %total skin friction
end

function Rexcr = critRe(rho,V,xcr)
    Rexcr = (rho*V*xcr)*meu; % critical
end

%L D and M coeffiencts
% q = dynamic pressure
function CL = liftCoeff(L,q,S)
    CL = L/(q*S); %finite
end

function CD = dragCoeff(D,q,S)
    CD = D/(q*S); %profile drag coefficent
end

function CD = totalDragCoeff(Cd,CL,pi,e,AR)
    CD = Cd +(CL^2/(pi*e*AR)); %total finite (e=constant)
end

% CL^2/(pi*e*A*R) = induced drag ceofficent
function CM = MomentCoeff(M,q,S,c) 
    CM = M/(q*S*c); %total finite (e=constant)
end

%p coeffient
function Cp = pressureCoeff(p,pinf,rho,V)
    Cp = (p-pinf)/(1/2*rho*V^2); %consecptual
end

function Cp = pressureSubCoeff(Cp0,M)
    Cp = Cp0/((1-M^2)^(1/2)); % subsonic flow / prandtl glauert
    %Cp0 = incompressable pressure coeff
end

function cl = liftSubCoeff(Cl0,M)
    cl = Cl0/((1-M^2)^(1/2)); % subsonic flow
    %Cl0 = incompressable lift coeff
end


%Mach number
function meu = machNum(M)
    meu = arcsin(1/M);
end

%Lift slope
function a = liftSlope(a0,pi,e1,AR)
    a = a0/(1+57.3*((a0)/(pi*e1*AR))); % a0 = infinit wing
    %ao lift slope for incomp flow
end

%drag polar
function CD = dragPolar(CD0,CL,pi,e,AR)
    CD = CD0+(CL^2/(pi*e*AR)); %CD0 = zero lift dtag coefficent
    %CD0 zere lift drag coeff
end

%thrust required (unaccelerated flow)
function TR = thrustReq(W,L,D)
    TR = W/(L/D);
end

%Power required
function PR = powerReq(W,CD,rho,S,CL)
    PR = ((2*(W^3)*(CD^2))/(rho*S*CL^3))^(1/2);
end

%Rate of climb 
function R_DIV_C = rateOfClimb(T,V,DV,W,g,t)
    R_DIV_C = (T*V-DV*V)/W - (V/g)*(diff(V)/diff(t)); % =R/C =diff(h)/diff(t)
end

%the specific ecess power Ps
function Ps = specExcessPower(T,V,DV,W)
    Ps = (T*V-DV*V)/W; 
end

% for unaccelerated come dV/dt=0 so R/C = (T*V-DV*V)/W

%glide angle
function theta = glideAngle(L,D) 
    theta = arctan(1/(L/D));
end

%for jet
function R = range(rho,S,Ct,CL,W0,W1)
    R = 2*(2/(rho*S))^(1/2)*(1/Ct)*((CL^1/2)/CD)*((W0^1/2)-W1^(1/2)); % range
end

function E = endurance(Ct,CL,CD,W0,W1)
    E = 1/(Ct)*(CL/CD)*(ln(W0/W1)); %endurance
end

%at maxs
function CL_POWER_3_DIV_2_DIV_CD = CL3_DIV_2CD(Cdo,pi,e,AR)
    CL_POWER_3_DIV_2_DIV_CD =((3*Cdo*pi*e*AR)^(3/4))/(4*Cdo); % =CL^(3/2))/CD
end

function CDo = CL1_DIV_2_DIV_CD_CD0_EQUALS_CDi(CDi)
    CDo= (1/3)*CDi; %same
end

function L_DIV_CD = lift_DIV_DragCoeff(Cdo,pi,e,AR)
    L_DIV_CD = ((Cdo*pi*e*AR)^(1/2))/(2*Cdo); % =L/CD and CDo =CDi 
end

function CL_POWER_1_DIV_2_DIV_CD = CD0_EQUALS_3CDi(Cdo,pi,e,AR)
    CL_POWER_1_DIV_2_DIV_CD = (((1/3)*Cdo*pi*e*AR)^(1/4))/((4/3)*Cdo); % =CL^(1/2)/CD and CDo =3*CDi 
end

%ground roll

%take off ground roll
function SLo = TKgrndRoll(W,g,rho,S,CLmax,T,D,meur,L)
    SLo = (1.44*W^2)/(g*rho*S*CLmax*(T-(D+meur(W-L)))); % at point avg
end

%landing ground roll
function Sl = LDgrndRoll(W,g,rho,S,CLmax,D,meur,L)
    Sl = (1.69*W^2)/(g*rho*S*CLmax*((D+meur(W-L)))); % at point of 0.7*VT
end


%load factor
function n = loadFactor(L,W)
    n = L/W;
end

%Turn radius
function R = turnRad(V,g,n)
    R = V^2/(g*(sqrt(n^2-1)));
end

%turn rate
function omega = turnRat(g,n,V)
    omega = g*(sqrt(n^2-1))/V;
end

%energy height
function He = energyH(h,V,g)
    He = h+V^2/(2*g);
end


%laungitudinal sattic stability
function CMo = laungSatStability(CM_aC_web,Vh,at,It,epsolon0)
    CMo = CM_aC_web + Vh*at*It+(epsolon0);
end

%
function diff_CM_cgs_DIV_diff_alpha_a = ElvDefPitchM(a,h,hac_web,VH,at,epsolon,alpha)
    diff_CM_cgs_DIV_diff_alpha_a = a(h-hac_web-VH*at/a*(1-diff(epsolon)/diff(alpha))); %diff(CM_cgs)/diff(alpha_a)
end

%tail volume ratio
function VH = tailVolRatio(lt,St,c,S)
    VH = lt*St/(c*S);
end

%neutral point
function hn = neutPoint(hac_web,VH,at,a,epsolon,alpha)
    hn = hac_web+VH*at/a*(1-diff(epsolon)/diff(alpha));
end

%Elevator delection on pitching monent of Cog
function CM_cg = ElvDefPitchMCog(CM_ac_web,CL_wb,h,hac,VH,at,alpha_t,CLt,delta_t,delta_e) 
    CM_cg = CM_ac_web + CL_wb*(h-hac)-VH(at*alpha_t+(diff(CLt)/diff(delta_t))*delta_e);
end

%elevator deflaction to trim an airplane
function delta_trim = ElvDefTrim(CM0,Cm_cg,Alpha_a,alpha_n,VH,CL_t,Delta_e)
    delta_trim = (CM0+(diff(Cm_cg)/diff(Alpha_a)*(alpha_n)))/(VH*(diff(CL_t)/diff(Delta_e)));
end

%thrust eq
function T = thrustEq(m_air,m_feul,Ve,V,pe,p,Ae)
    T = ((diff(m_air)+diff(m_feul))*Ve-diff(m_air)*V+(pe-p)*Ae);
end








