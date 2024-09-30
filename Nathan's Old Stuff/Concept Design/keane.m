%% Constraint Diagram - Keane Approach

u = symunit;
disp('Design Brief Performance/Constraints: ')
GrossWeight_kg = 28 * double(unitConversionFactor(u.lb, u.kg));
disp([' Gross Weight (kg): ' num2str(GrossWeight_kg)]);

GroundRun_ft = 300;
TakeOffSpeed_kts = 30 * double(unitConversionFactor(u.mph, u.kts));
TakeOffElevation = 0;

disp([' Ground Run (ft): ' num2str(GroundRun_ft)]);
disp([' Takeoff Speed (kts): ' num2str(TakeOffSpeed_kts)]);
disp([' Takeoff Elevation (ft): ' num2str(TakeOffElevation)]);


CruiseAlt_ft = 350;
CruiseSpeed_kts = 100 * double(unitConversionFactor(u.fps,u.kts));
MaxSpeed_kts = 0.3 * double(unitConversionFactor(u.mach,u.kts));

disp([' Cruise Altitude (ft): ' num2str(CruiseAlt_ft)]);
disp([' Cruise Speed (kts): ' num2str(CruiseSpeed_kts)]);
disp([' Max Speed w/o AB (kts): ' num2str(MaxSpeed_kts)]);

ClimbSpeed_kts = CruiseSpeed_kts * 0.8;
ROC_fpm = 300;
ROCAlt_ft = 0;

disp([' Climb Speed (kts): ' num2str(ClimbSpeed_kts)]);
disp([' Rate of Climb (ft/s): ' num2str(ROC_fpm)]);
disp([' ROC Altitude (ft): ' num2str(ROCAlt_ft)]);

n_cvt = 3.5; %load factor for turn

disp([' Load Factor for Constant Velocity Turn: ' num2str(n_cvt)]);

ServiceCeiling_ft = 400; %irrelevant

disp([' Service Ceiling (ft): ' num2str(ServiceCeiling_ft)]);

ApproachSpeed_kts = 28 * double(unitConversionFactor(u.mph, u.kts));
StallReserveFactor = 1.1;
StallSpeedApproachConfiguration_kts = ApproachSpeed_kts/StallReserveFactor;
TopOfFinalApproach_ft = 60;

disp([' Approach Speed (kts): ' num2str(ApproachSpeed_kts)]);
disp([' Stall Speed Approach (kts): ' num2str(StallSpeedApproachConfiguration_kts)]);
disp([' Top of Final Approach (ft): ' num2str(TopOfFinalApproach_ft)]);

AspectRatio = 3;
CDmin = 0.04; %important estimation
%Tmax_lb;

disp('Geometry Initial Guesses')
disp([' Aspect Ratio: ' num2str(AspectRatio)]);
disp([' CD0: ' num2str(CDmin)]);

CLTO = 0.97; %important estimation(s)
CDTO = 0.09;
muTO = 0.17; %rolling friction parameter

disp([' CL Takeoff: ' num2str(CLTO)]);
disp([' CD Takeoff: ' num2str(CDTO)]);
disp([' Friction Coeff: ' num2str(muTO)]);

[T_TO, a_TO, P_TO, rho_TO] = atmosisa(TakeOffElevation);
[T_C, a_C, P_C, rho_C] = atmosisa(CruiseAlt_ft);







