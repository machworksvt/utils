import openvsp as vsp
from rich.console import Console
from rich.table import Table

console = Console()


def testVSPAERO():
    # Step 1: Load the VSP model
    vsp.ClearVSPModel()
    vsp.ReadVSPFile("local.vsp3")

    # Step 2: Export geometry for analysis
    compGeom = "VSPAEROComputeGeometry"
    vsp.SetAnalysisInputDefaults(compGeom)
    vsp.SetIntAnalysisInput(compGeom, "AnalysisMethod", [vsp.VORTEX_LATTICE])
    vsp.SetIntAnalysisInput(compGeom, "GeomSet", [1])

    print("Checking geometry for analysis...")
    vsp.PrintAnalysisInputs(compGeom)
    compGeom_results = vsp.ExecAnalysis(compGeom)
    vsp.PrintResults(compGeom_results)

    geom_ids = vsp.FindGeoms()
    for geom_id in geom_ids:
        name = vsp.GetGeomName(geom_id)
        in_set_0 = vsp.GetSetFlag(geom_id, 1)  # Check if in Set 0
        print(f"Geom ID: {geom_id}, Name: {name}, In Set 0: {in_set_0}")

    # Step 3: Set up VSPAERO analysis
    myAnalysis = "VSPAEROSweep"
    vsp.SetAnalysisInputDefaults(myAnalysis)

    # Reference geometry and freestream conditions
    vsp.SetIntAnalysisInput(myAnalysis, "GeomSet", [1])  # Use Set 0
    vsp.SetDoubleAnalysisInput(myAnalysis, "MachStart", [0.1])
    vsp.SetDoubleAnalysisInput(myAnalysis, "AlphaStart", [0.0])
    vsp.SetDoubleAnalysisInput(myAnalysis, "AlphaEnd", [1.0])
    vsp.SetIntAnalysisInput(myAnalysis, "AlphaNpts", [2])  # Number of alpha points
    vsp.SetDoubleAnalysisInput(myAnalysis, "ReCref", [1e6])  # Reynolds number

    # Analysis method
    vsp.SetIntAnalysisInput(myAnalysis, "AnalysisMethod", [vsp.VORTEX_LATTICE])

    # Update and execute
    vsp.Update()
    vsp.PrintAnalysisInputs(myAnalysis)
    allResults = vsp.ExecAnalysis(myAnalysis)

    # Save results
    vsp.WriteResultsCSVFile(allResults, "Results.csv")

    # Step 4: Clean up
    vsp.ClearVSPModel()


def list_CS_groups(_):
    vsp.ReadVSPFile("local.vsp3")

    numgroups = vsp.GetNumControlSurfaceGroups()
    print(f"Number of control surface groups: {numgroups}")
    print(f"Type: {type(numgroups)}")

    if numgroups == 0:
        console.print("\t[yellow]No control surface groups found in the model.[/yellow]")
        return True
    
    table = Table(title="Control Surface Groups", show_lines=True)
    table.add_column("Group ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Group Name", justify="left", style="green")
    table.add_column("Num Surfaces", justify="center", style="yellow")
    
    container_id = vsp.FindContainer("VSPAEROSettings", 0)

    parm_ids = vsp.FindContainerParmIDs( container_id )

    for i in range(len(parm_ids)):

        name_id = vsp.GetParmName( parm_ids[i] ) + ": " + parm_ids[i] + "\n"

        print( name_id )

    deflection_gains = []
    for i in range(numgroups):
        group_name = vsp.GetVSPAEROControlGroupName(i)
        surfaces = vsp.GetActiveCSNameVec(i)
        for surface in surfaces:
            parm_id_vec = vsp.GetSubSurfID(surface)
            for parm_id in parm_id_vec:
                deflection_gain0 = vsp.FindParm(container_id, "Surf_ "+ parm_id + "_0_Gain", "ControlSurfaceGroup")
                deflection_gain1 = vsp.FindParm(container_id, "Surf_ "+ parm_id + "_1_Gain", "ControlSurfaceGroup")
                print(f"Deflection Gain 0: {deflection_gain0}")
                print(f"Deflection Gain 1: {deflection_gain1}")
        
        # Check if the deflection gains have opposite signs
        table.add_row(str(i), group_name, str(surfaces))

    console.print(table)


list_CS_groups(None)
