import openvsp as vsp
from rich.console import Console
from rich.table import Table
import pandas as pd

console = Console()


readLast = False



def testSetControlSurfaceAngles():
    wid = vsp.AddGeom( "WING", "" )                             # Add Wing

    aileron_id = vsp.AddSubSurf( wid, vsp.SS_CONTROL )                      # Add Control Surface Sub-Surface

    #==== Add Vertical tail and set some parameters =====//
    vert_id = vsp.AddGeom( "WING" )

    vsp.SetGeomName( vert_id, "Vert" )

    vsp.SetParmValUpdate( vert_id, "TotalArea", "WingGeom", 10.0 )
    vsp.SetParmValUpdate( vert_id, "X_Rel_Location", "XForm", 8.5 )
    vsp.SetParmValUpdate( vert_id, "X_Rel_Rotation", "XForm", 90 )

    rudder_id = vsp.AddSubSurf( vert_id, vsp.SS_CONTROL )                      # Add Control Surface Sub-Surface

    vsp.AutoGroupVSPAEROControlSurfaces()

    vsp.Update()

    print( "COMPLETE\n" )
    control_group_settings_container_id = vsp.FindContainer( "VSPAEROSettings", 0 )   # auto grouping produces parm containers within VSPAEROSettings

    #==== Set Control Surface Group Deflection Angle ====//
    print( "\tSetting control surface group deflection angles..." )

    # subsurfaces get added to groups with "CSGQualities_[geom_name]_[control_surf_name]"
    # subsurfaces gain parm name is "Surf[surfndx]_Gain" starting from 0 to NumSymmetricCopies-1

    deflection_gain_id = vsp.FindParm( control_group_settings_container_id, "Surf_" + aileron_id + "_0_Gain", "ControlSurfaceGroup_0" )
    deflection_gain_id = vsp.FindParm( control_group_settings_container_id, "Surf_" + aileron_id + "_1_Gain", "ControlSurfaceGroup_0" )

    #  deflect aileron
    deflection_angle_id = vsp.FindParm( control_group_settings_container_id, "DeflectionAngle", "ControlSurfaceGroup_0" )
    print(vsp.GetParmDescript( deflection_angle_id ))


def testAero():
    # Step 1: Load the VSP model
    vsp.ClearVSPModel()
    vsp.ReadVSPFile("local.vsp3")

    if not readLast:
        # Step 2: Export geometry for analysis
        compGeom = "VSPAEROComputeGeometry"
        vsp.SetAnalysisInputDefaults(compGeom)
        vsp.SetIntAnalysisInput(compGeom, "AnalysisMethod", [vsp.VORTEX_LATTICE])
        vsp.SetIntAnalysisInput(compGeom, "GeomSet", [1])

        print("Checking geometry for analysis...")
        vsp.PrintAnalysisInputs(compGeom)
        compGeom_results = vsp.ExecAnalysis(compGeom)
        outputFileName = vsp.GetStringResults(compGeom_results, "DegenGeomFileName")
        timeToComplete = vsp.GetDoubleResults(compGeom_results, "Analysis_Duration_Sec")[0]
        print(timeToComplete)
        console.print(f"Geometry computed for operating point 'none' in {timeToComplete:.2f} seconds. File saved as '{outputFileName}'")
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
        vsp.SetIntAnalysisInput(myAnalysis, "AlphaNpts", [1])  # Number of alpha points
        vsp.SetDoubleAnalysisInput(myAnalysis, "ReCref", [1e6])  # Reynolds number

        vsp.SetIntAnalysisInput(myAnalysis, "NumWakeNodes", [16])
        vsp.SetIntAnalysisInput(myAnalysis, "WakeNumIter", [3])
        # Analysis method
        vsp.SetIntAnalysisInput(myAnalysis, "AnalysisMethod", [vsp.VORTEX_LATTICE])
        vsp.SetIntAnalysisInput(myAnalysis, "UnsteadyType", [vsp.STABILITY_DEFAULT])
        # Update and execute
        vsp.SetStringAnalysisInput(myAnalysis, "RedirectFile", ["log.txt"])
        vsp.SetIntAnalysisInput(myAnalysis, "NCPU", [16])
        vsp.Update()
        vsp.PrintAnalysisInputs(myAnalysis)

        allResults = vsp.ExecAnalysis(myAnalysis)
        timeToSolve = vsp.GetDoubleResults(allResults, "Analysis_Duration_Sec")[0]
        print(f"Analysis completed in {timeToSolve:.2f} seconds.")

        stab_results = vsp.FindLatestResultsID("VSPAERO_Stab")

        vsp.PrintResults(stab_results)
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn

console = Console()

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn

console = Console()

def visualize_static_margin_with_bar(sm):
    # Define ranges and labels
    segments = [
        {"range": (-5, 0), "label": "Unstable", "color": "red"},
        {"range": (0, 5), "label": "Marginally Stable", "color": "yellow"},
        {"range": (5, 15), "label": "Good Stability", "color": "green"},
        {"range": (15, 20), "label": "Overstable", "color": "cyan"},
    ]

    # Find the segment containing the static margin
    label, color = "Unreasonable", "white"
    for segment in segments:
        if segment["range"][0] <= sm <= segment["range"][1]:
            label = segment["label"]
            color = segment["color"]
            break

    # Normalize the static margin value to a 0-100 scale for the progress bar
    total_range = segments[-1]["range"][1] - segments[0]["range"][0]
    normalized_sm = ((sm - segments[0]["range"][0]) / total_range) * 100

    # Create the progress bar
    with Progress(
        TextColumn(f"[{color} bold]\tStatic Margin: {sm:.1f}% ({label}) [/{color} bold]"),
        BarColumn(bar_width=40, complete_style=color),
        console=console,
        expand=True
    ) as progress:
        task = progress.add_task("", total=100)
        progress.update(task, completed=normalized_sm)

# Example
visualize_static_margin_with_bar(25)


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






