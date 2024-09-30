

sfc = 0.15; %kg/N*h
%N/Ns
tsfc = sfc * 9.81 / 3600;

runtime = 20 * 60; % 20 minutes
thrust = 97 / 2; %half thrust

weightFuel = thrust * runtime * tsfc;

consumptionFullLoad = 275; %ml/min
consumptionIdle = 95;
avConsumption = (consumptionIdle + consumptionFullLoad)/2;
massConsumption = 0.82 * avConsumption; %g/min
totalFuel = massConsumption * 20; %20 minutes
totalFuelN = totalFuel/1000 * 9.81;

mFuel = 4*0.82; %kg
mPP = 1.45 + 0.25; 
mStruct = (mFuel + mPP)/75 * 25;
mAvionics = (mStruct + mPP + mFuel)/95 * 5;
TOGm = mFuel + mPP + mStruct + mAvionics; %kg
mCruise = mPP + mStruct + mAvionics + 0.5*mFuel;

q = 0.5*1.225*44.7^2;
S = 1 * 0.25;

wCruise = mCruise*9.81;

CL = wCruise/(q*S); 




