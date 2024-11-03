clc

filename = 'param.des';

%data = readtable(filename,".des",);

chord = 0.3;
span = 0.2;

%param{1,"VarName5"} = chord;
%param{2,"VarName5"} = span;


vsp_fileLocation = "C:\Users\stevi\Downloads\OpenVSP-3.40.1-win64-Python3.11 (2)\OpenVSP-3.40.1-win64\vsp.exe";
design_fileName = "param.des";
icuras_fileLocation = "C:\Users\stevi\Downloads\OpenVSP-3.40.1-win64-Python3.11 (2)\OpenVSP-3.40.1-win64\icarus_mk2 2.vsp3";


%vsp.exe -des <desfile> <filename.vsp3>
%system(vsp_fileLocation + ' -des' + design_fileName + ' -v  ' + icuras_fileLocation);

%should look like
system('"C:\Users\stevi\Downloads\OpenVSP-3.40.1-win64-Python3.11 (2)\OpenVSP-3.40.1-win64\vsp.exe" -des param.des -v "C:\Users\stevi\Downloads\OpenVSP-3.40.1-win64-Python3.11 (2)\OpenVSP-3.40.1-win64\icarus_mk2 2.vsp3"');
