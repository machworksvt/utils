%setting variable ranges
chord = 0.27300:0.001:0.33100 ;
span = 1.90000:0.01:2.31000;

%itterating through each version
for c = chord
    for s = span

        system('"C:\Users\stevi\Downloads\OpenVSP-3.40.1-win64-Python3.11 (2)\OpenVSP-3.40.1-win64\vsp.exe" -des param.des -v "C:\Users\stevi\Downloads\OpenVSP-3.40.1-win64-Python3.11 (2)\OpenVSP-3.40.1-win64\icarus_mk2 2.vsp3"');
 %input into vspgeo file
    end
end