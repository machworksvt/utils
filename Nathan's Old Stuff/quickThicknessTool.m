%F-22 uses:
%NACA 64A 0.592 -> 0.429
%My model current runs from 0 to 79.512/2 span

span = 79.512;
rootTC = 0.0592;
tipTC = 0.0429;

tc = @(x) rootTC + ((tipTC-rootTC)/(span/2)) * x;

sectSpans = [11.158 1.789 21.8 5];
tSpans = [sectSpans(1) sectSpans(2:end)+cumsum(sectSpans(1:end-1))];

tcV = tc(tSpans);

