import openvsp as vsp
import os
import contextlib
import io
import tempfile
import subprocess
import json
from config_manager import ConfigurationManager
from rich.console import Console
from rich.table import Table

# Utility functions to do basic things with the VSP api
config = ConfigurationManager()
console = None


# BUG: Something's fucked when you try to save from exit

def load(args):
    """Load a VSP3 file and a configuration"""
    if len(args) != 1:
        return False
    file_path = args[0]
    if not os.path.isfile(file_path):
        console.print(f"\t[red]Error: '{file_path}' is not a valid path, or file does not exist.[/red]")
        return False
    else:
        console.print(f"\t[blue]Loading model with path: [/blue]", file_path)
        if config.isModelLoaded():
            confirm = console.input("\t[yellow]A model is already loaded. Do you want to overwrite it? (y/n): [/yellow]").strip().lower()
            if confirm != "y":
                console.print("\t[yellow]Load cancelled.[/yellow]")
                return True
            config.clear_model()
    try:
        config.load_files(file_path)
        print(f"\tSuccessfully loaded file: {file_path}")
        return True
    except Exception as e:
        print(f"\tError loading file: {e}")
        model_loaded = False

def save(args):
    """Save the VSP3 file and its configuration"""
    try:
        file_path = args[0] if len(args) == 1 else None
        config.save_files(file_path)
        return True
    except Exception as e:
        console.print(f"\t[red]Failed to save file: {e}[/red]")
        return False

def info(args):
    """Print out some basic information about the configuration and openvsp model"""
    if not config.isLoaded:
        console.print("\t[yellow]No model/config currently loaded.[/yellow]")
        return True
    try:
        # Name

        console.print(f"\n[bold cyan]Loaded File: {config.vsp3_file}[/cyan bold]")
        

        # Display configuration settings
        settings_table = Table(title="Configuration Settings", show_lines=True)
        settings_table.add_column("Setting", justify="left", style="cyan", no_wrap=True)
        settings_table.add_column("Value", justify="left", style="green")

        for key, value in config.settings.items():
            settings_table.add_row(key, str(value))

        console.print(settings_table)
        component_ids = vsp.FindGeoms()

        #Display components in the model
        if not component_ids:
            console.print("\t[yellow]No Components found in currently model.[/yellow]")
            return True
        else:
            table = Table(title="Model Components", show_lines=True)

              # Define columns
        table.add_column("Name", justify="left", style="cyan", no_wrap=True)
        table.add_column("Type", justify="left", style="magenta")
        table.add_column("ID", justify="center", style="green")
        table.add_column("Aerodynamic Surface", justify="center", style="yellow")

        # Populate the table with component data
        for comp_id in component_ids:
            name = vsp.GetGeomName(comp_id)
            geom_type = vsp.GetGeomTypeName(comp_id)
            aero_surface = "Yes" if vsp.GetSetFlag(comp_id, 1) else "No"
            table.add_row(name, geom_type, comp_id, aero_surface)
        
        console.print(table)
    except Exception as e:
        print(f"Error retreiving body information: {e}")
    return True

def clear_model():
    """Clear the currently loaded model."""
    if not config.isModelLoaded():
        console.print("\t[yellow]No model loaded.[/yellow]")
        return True
    config.clear_model()    

def check_set_rules(args):
    print("\tBest practices for this tool:")
    print("\t\t1) Set_0 should be your aerodynamic surfaces, the ones you want included in this analysis.")
    print("\t\t2) Set_1 should be your inertial elements, ie. things you want included in mass/inertia calculations.")
    confirm = input("\t Do you want to auto-apply these rules to your loaded model? May have unintended effects (y/n): ")
    if not confirm == "y":
        return True
    vsp.SetSetName(1, "Aerodynamic Surfaces")
    vsp.SetSetName(2, "Inertial Components")
    return True

def init_settings():
    """Set up VSP api settings for convenient use"""
    vsp.SetSetName(1, "Aerodynamic Surfaces")
    vsp.SetSetName(2, "Inertial Components")

def show_vehicle(_):
    """Open a visualization of the vehicle using OpenVSP's GUI in read-only mode."""
    try:
        # Check if a model is loaded
        if not config.isModelLoaded():
            print("\tNo model currently loaded.")
            return True

        vsp_executable = "../OpenVSP-3.41.1-win64/vsp.exe"

        # Create a temporary file for visualization
        with tempfile.NamedTemporaryFile(suffix=".vsp3", delete=False) as temp_file:
            temp_file_path = temp_file.name
            vsp.WriteVSPFile(temp_file_path)

        # Open the temporary file in OpenVSP GUI
        print(f"\tLaunching OpenVSP visualization for read-only viewing...")
        subprocess.run([vsp_executable, temp_file_path], check=False)

        # Cleanup: Remove the temporary file after viewing
        os.remove(temp_file_path)
        print("\tVisualization session closed.")
    except Exception as e:
        print(f"\tError displaying vehicle: {e}")
    return True

def list_CS_groups(_):
    if not config.isModelLoaded():
        console.print("\t[yellow]No model loaded.[/yellow]")
        return True
    
    numgroups = vsp.GetNumControlSurfaceGroups()

    if numgroups == 0:
        console.print("\t[yellow]No control surface groups found in the model.[/yellow]")
        return True
    
    table = Table(title="Control Surface Groups", show_lines=True)
    table.add_column("Group ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Group Name", justify="left", style="green")
    table.add_column("Num Surfaces", justify="center", style="yellow")
    table.add_column("Symmetric", justify="center", style="magenta")

    for i in range(numgroups):
        group_name = vsp.GetControlSurfaceGroupName(i)
        num_surfaces = vsp.GetNumControlSurfaces(i)
        deflection_gains = []
        for j in range(num_surfaces):
            # Get the deflection gain for each surface
            gain_id = vsp.FindParm(vsp.FindContainer("VSPAEROSettings", 0), f"Surf_{j}_Gain", f"ControlSurfaceGroup_{i}")
            deflection_gain = vsp.GetParmVal(gain_id)
            deflection_gains.append(deflection_gain)

        # Check if the deflection gains have opposite signs
        is_symmetric = any(g1 * g2 < 0 for g1 in deflection_gains for g2 in deflection_gains if g1 != g2)
        symmetry_type = "Symmetric" if is_symmetric else "Asymmetric"
        symmetric = "Yes" if vsp.GetControlSurfaceGroupSymFlag(i) else "No"
        table.add_row(str(i), group_name, str(num_surfaces), symmetric)
