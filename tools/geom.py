import openvsp as vsp
from rich.console import Console
from rich.table import Table
from config_manager import ConfigurationManager
from config_manager import MassConfiguration
import numpy as np
import pandas as pd


console = None
config = ConfigurationManager()

def listMassConfigurations(_):
    if len(config.massConfigurations) == 0:
        console.print("\t[yellow]No mass configurations currently defined. Use 'new'.[/yellow]")
        return True

    # Display configuration settings
    table = Table(title="Mass Configurations", show_lines=True)
    table.add_column("ID", justify="left", style="white", no_wrap=True)
    table.add_column("Name", justify="left", style="white", no_wrap=True)
    table.add_column("Mass", justify="left", style="white")
    table.add_column("CG", justify="left", style="white", no_wrap=True)
    table.add_column("Inertia", justify="left", style="white")

    # Populate the table with component data
    for (i, mconfig) in enumerate(config.massConfigurations):
        name = mconfig.name
        mass = mconfig.mass
        cg = mconfig.cg
        inertia_matrix = mconfig.inertia_matrix
        table.add_row(f"{i}", name, f"{mass}", f"{cg}", f"{inertia_matrix}")
    
    console.print(table)
    return True

def createMassConfiguration(_): 
    # Choose name
    while True:
        input_name = console.input(f"{MassConfiguration._prefix} Name: ").strip()
        if input_name != "":
            break
        else:
            console.print(f"{MassConfiguration._prefix} Empty input. Try again.")
    
    # Input mass
    while True:
        input_mass = console.input(f"{MassConfiguration._prefix} Mass (kg): ").strip()
        try:
            mass = float(input_mass)
            if mass > 0:
                break
            else:
                console.print(f"{MassConfiguration._prefix} Mass must be positive. Try again.")
        except ValueError:
            console.print(f"{MassConfiguration._prefix} Invalid input. Please enter a numeric value.")
    
    # Input CG location
    while True:
        input_cg = console.input(f"{MassConfiguration._prefix} CG Location (x,y,z) separated by spaces (m): ").strip().split()
        if len(input_cg) == 3:
            try:
                cg = np.array([float(i) for i in input_cg])
                break
            except ValueError:
                console.print(f"{MassConfiguration._prefix} Invalid input. Please enter numeric values.")
        else:
            console.print(f"{MassConfiguration._prefix} Please enter exactly three values separated by spaces.")
    
    # Input inertia
    while True:
        input_Ixxyyzz = console.input(f"{MassConfiguration._prefix} Input moments of inertia (Ixx,Iyy,Izz) separated by spaces (kgm^2): ").strip().split()
        input_Ixz = console.input(f"{MassConfiguration._prefix} Input product of inertia Ixz (kgm^2): ").strip()
        if len(input_Ixxyyzz) == 3:
            try:
                inertia_input = np.array([
                    [float(input_Ixxyyzz[0]), 0, float(input_Ixz)],
                    [0, float(input_Ixxyyzz[1]), 0],
                    [float(input_Ixz), 0, float(input_Ixxyyzz[2])]
                ])
                break
            except ValueError:
                console.print(f"{MassConfiguration._prefix} Invalid input. Please enter numeric values.")
        else:
            console.print(f"{MassConfiguration._prefix} Please enter exactly three values for moments of inertia separated by spaces.")
    
    newConfig = MassConfiguration(input_name, cg, mass, inertia_input)
    config.addMassConfiguration(newConfig)
    return True

def deleteMassConfiguration(args):
    if not len(args) == 1:
        return False
    if not args[0].isnumeric() or not (0 <= int(args[0]) < len(config.massConfigurations)):
        console.print("\t[red]No index or invalid index[/red]")
        return True
    idx = int(args[0])
    config.removeMassConfiguration(idx)
    return True

def generateMassConfiguration(args):
    """Generate a mass configuration from a VSP mass-props analysis"""
    raise NotImplementedError
