%Code to set ranges and convert into preliminary dimentions
%Work as a feedback loop based on simulink data compared to ranges and
%change dimentions to be reinput to openVSP

%Ranges


%Dimetions

%Current Elevator GEO 
rootChordElv = 0.17780; %m
spanElv = 0.22860; %m
tipChordElv = 0.10160; %m

%Current VTail GEO
rootChordVt = 0.17780; %m
tipChordVt = 0.10160; %m
spanVt = 0.17780; %m
sweepVt = 30; %deg

%Current Wing GEO
rootChordWing = 0.4; %m
tipChordWing = 0.33337; %m
spanWing = 0.13018; %m
sweepWing = 8; %deg

chord = 0.27300:0.001:0.33100 ;
span = 1.90000:0.01:2.31000;

for c = chord
    for s = span

        system('"C:\Users\stevi\Downloads\OpenVSP-3.40.1-win64-Python3.11 (2)\OpenVSP-3.40.1-win64\vsp.exe" -des param.des -v "C:\Users\stevi\Downloads\OpenVSP-3.40.1-win64-Python3.11 (2)\OpenVSP-3.40.1-win64\icarus_mk2 2.vsp3"');
 %input into vspgeo file
    end
end
