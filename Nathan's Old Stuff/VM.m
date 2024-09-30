%% Testing Wing Lift -> Spar Analysis

q = 0.5 * rho * V_inf^2;

Sl = chords.*widths;

Lifts = CLs.*q.*Sl;

subplot(2,2,1);
plot(x,CLs);
title("CLs vs x");
subplot(2,2,2);
plot(x,Lifts);
hold on;
title("L vs x");

lboundary = min(x); % M at boundary is zero
[rboundary, rindex] = max(x); % M at boundary is zero
[centerValue, centerIndex] = min(abs(x)); % V at boundary is zero

shears = zeros(rindex - centerIndex,1);
for i = (centerIndex+1):rindex

    startIndex = i;
    shears(i-centerIndex) = sum(Lifts(startIndex:rindex));


end

plot(x((centerIndex+1):rindex), shears);
