vsp_path = '..\OpenVSP-3.39.1-win64\vsp.exe';
vspaero_path = '..\OpenVSP-3.39.1-win64\vspaero.exe';

%{
VSPAERO v.6.4.8 --- Compiled on: May 14 2024 at 20:20:00 PST --- Options: OpenMP

Usage: vspaero [options] <FileName>

Options:
 -omp <N>                           Use 'N' processes.
 -stab                              Calculate stability derivatives.

 -pstab                             Calculate unsteady roll  rate stability derivative analysis.
 -qstab                             Calculate unsteady pitch rate stability derivative analysis.
 -rstab                             Calculate unsteady yaw   rate stability derivative analysis.

 -fs <M> END <A> END <B> END        Set/Override freestream Mach, Alpha, and Beta. note: M, A, and B are space delimited lists.
 -save                              Save restart file.
 -restart                           Restart analysis.
 -geom                              Process and write geometry without solving.
 -hilift                            Process the geometry and write out a default high lift setup file.
 -nowake <N>                        No wake for first N iterations.
 -fem                               Load in FEM deformation file.
 -write2dfem                        Write out 2D FEM load file.
 -groundheight <H>                  Do ground effects analysis with cg set to <H> height above the ground.
 -rotor <RPM>                       Do a rotor analysis, with specified rotor RPM.
 -qrotor                            Run a quasi-steady state rotor analysis, assumes .groups file is setup!
 -unsteady                          Run an unsteady analysis, assumes .groups file is setup!
 -fromsteadystate                   Run an unsteady analysis... after converging a steady analysis. Assumes .groups file is setup!
 -hoverramp <ih> <fs>               Start unsteady solution with free stream fs, and reduce down to actual free stream starting at time step ih.
 -nospanload                        Turn off calculation of span wise loading... this is here in case this feature is breaking stuff...

 -dokt                              Turn on the 2nd order Karman-Tsien Mach number correction.
 -jacobi                            Use Jacobi matrix preconditioner for GMRES solve.
 -ssor                              Use SSOR matrix preconditioner for GMRES solve.

 -noise                             Post process and existing solution to setup files for psu-wopwop noise analysis
 -noise -steady                     Output steady state data to psu-wopwop, default is unsteady, periodic.
 -noise -english                    Assumes your model is in english (feet) units, will convert to SI for psu-wopwop
 -noise -flyby                      Set up flyby analysis for psu-wopwop
 -noise -footprint                  Set up fot print analysis for psu-wopwop

 -opt -optfunction <#>              This is an optimization solve... solve the Aero equations and write out all information needed for adjoint solver.
 -opt -adjoint   -optfunction <#>   This is an optimization solve... solve Adjoint equations for optfunction #. Only used with the ADJOINT solver.
 -opt -gradients -optfunction <#>   This is an optimization solve... solve for the gradients for optfunction #.  Only used with the ADJOINT solver.
 -complextest                       This runs the complex step gradient test case... you have to use this with the complex step version and -opt, -optfunction
 -interrogate                       Reload an existing solution, and interrogate the data using survey points list.
 -interrogate -unsteady             Reload an existing unsteady solution, and interrogate the data using survey points list.

 -2d                                Turn off trailing wakes and approximate 2D flow

 -setup                             Write template *.vspaero file, can specify parameters below:
     -sref  <S>                     Reference area S.
     -bref  <b>                     Reference span b.
     -cref  <c>                     Reference chord c.
     -cg  <X Y Z>                   Moment reference point.
     -mach <M> END                  Freestream Mach number. M is a space delimited list of mach values.
     -aoa  <A> END                  Angle of attack. A is a space delimited list of aoa values.
     -beta <B> END                  Sideslip angle. B is a space delimited list of beta values.
     -wakeiters <N>                 Number of wake iterations to calculate.
     -symx                          Symetry flag - vehicle is symetric at x=0.
     -symy                          Symetry flag - vehicle is symetric at y=0 (this is the most common).
     -symz                          Symetry flag - vehicle is symetric at z=0.

EXAMPLES:
Example: Creating a setup file for testModel with mach and alpha sweep matrix
vspaero -setup -sref 10 -bref 10 -cref 1 -cg 0.1 0 0.1 -mach 0 0.1 0.3 END -aoa 1 5.5 10 END -beta 0 END testModel_DegenGeom

Example: Solve testModel with 4 threads
vspaero -omp 4 testModel_DegenGeom

Example: Solve testModel with 4 threads and freestream overrides
vspaero -omp 4 -fs 0.05 0.15 0.35 END 1 5.5 10 END 0 END testModel_DegenGeom


          Vehicle Sketch Pad 3.39.1
-----------------------------------------------------------
Usage: vsp [inputfile.vsp3]               Run interactively
     : vsp -script <vspscriptfile>        Run script
-----------------------------------------------------------

VSP command line options listed below:
  -help              This message
  -des <desfile>     Set variables according to *.des file
  -xddm <xddmfile>   Set variables according to *.xddm file

-----------------------------------------------------------
%}

%% Priorities for you guys right now
%{
    
    We need the code that underpins running vsp and vspaero from matlab
    This really involved making a few functions such as
        writeSetupFile(...) which takes in location of the geometry file,
        the type of analysis you want to do, ranges, etc. -> creates a
        .vspaero file
        runAnalysis(...) uses the setup files from before to call
        vspaero.exe to run
        readStabilityData(...) the .stab files
        readPolarData(...) the .polar files
        readStructuralData(...) the . 
%}

