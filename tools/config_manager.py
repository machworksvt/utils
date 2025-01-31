import json
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.padding import Padding
from rich.columns import Columns
from rich.live import Live
from rich.progress import BarColumn, Progress
from rich.text import Text
import openvsp as vsp
import pandas as pd
import numpy as np
from ambiance import Atmosphere
from scipy import constants
import pandas as pd
import threading
import matplotlib.pyplot as plt


console = None

"""
TODO:
    Fix CD results giving NaN
    Finish implementing the hi-lift operating point
    Actually fix the dynamic system matrix generation
    Implement the powerplant class
    Improve the mass configuration class
"""

class ConfigurationManager:
    """Manages configuration of the program"""

    _instance = None
    _prefix = "[bold green]\t<config>[/bold green]"
    CONFIG_SUFFIX = ".config.json"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initializes the configuration manager"""
        if self._initialized:
            return
        self._initialized = True
        self.vsp3_file = None
        self.settings = {
            "vsp_path":"../OpenVSP-3.41.1-win64/vsp.exe",
            "type":"IV",
            "num_procs":16,
        }
        self.operating_points = []
        self.isLoaded = False
        self.massConfigurations = []
        self.powerplant = None
        self.refs = None

    # Import/export configuration
    def to_dict(self):
        """Export configuration as dictionary."""
        return {
            "vsp3_file": self.vsp3_file,
            "settings": self.settings,
            "operating_points": [op.to_dict() for op in self.operating_points],
            "massConfigurations": [mc.to_dict() for mc in self.massConfigurations],
        }

    def from_dict(self, data):
        """Load configuration from a dictionary."""
        self.vsp3_file = data.get("vsp3_file")
        self.settings.update(data.get("settings", {}))
        self.operating_points = [OperatingPoint.from_dict(op) for op in data.get("operating_points", [])]
        self.massConfigurations = [MassConfiguration.from_dict(mc) for mc in data.get("massConfigurations", [])]

    # Interact/edit configuration
    def _get_config_path(self):
        """Returns the config file path"""
        if not self.vsp3_file:
            return None
        return str(Path(self.vsp3_file).with_suffix(self.CONFIG_SUFFIX))

    def load_files(self, file_path):
        """Load the .vsp3 file and it's associated configuration"""
        console.print(self._prefix, f"Loading {file_path}...")
        self.vsp3_file = file_path
        vsp.ReadVSPFile(self.vsp3_file)
        self.isLoaded = True
        self.load_config()
        console.print(self._prefix, f"Load complete.")
    
    def save_files(self, file_path=None): #TODO: Check for .vsp3 ending or not when file path supplied
        """Saves the VSP model and it's configuration"""
        if not file_path:
            file_path = self.vsp3_file
        if not file_path:
            console.print(self._prefix, "[red]Nothing loaded - nothing to save.")
            return True
        console.print(self._prefix, f"Saving VSP3 file: {file_path}...")
        vsp.WriteVSPFile(file_path)
        self.vsp3_file = file_path
        self.save_config()
        console.print(self._prefix, f"[green]Saved VSP3 file: {file_path}[/green]")
        return True

    def load_config(self):
        """Loads the config associated with the current .vsp3 file"""
        config_path = self._get_config_path()
        if not config_path or not os.path.exists(config_path):
            console.print(self._prefix, "[yellow]No config file found. Using defaults.")
            return True
        try:
            with open(config_path, "r") as f:
                self.from_dict(json.load(f)) #needs fix for operating points n shit too
            console.print(self._prefix, f"[green]Loaded configuration: {config_path}[/green]")
        except Exception as e:
            console.print(self._prefix, f"[red]Error loading configuration: {e}[/red]")
        return True

    def save_config(self):
        """Saves current configuration to a file associated with the .vsp3 file"""
        config_path = self._get_config_path()
        if not config_path:
            console.print(self._prefix, "[red]No associated .vsp3 file. Cannot save configuration.[/red]")
            return True
        try:
            with open(config_path, "w") as f:
                json.dump(self.to_dict(), f, indent=1)
            console.print(self._prefix, f"[green]Saved configuration: {config_path}[/green]")
        except Exception as e:
            console.print(self._prefix, f"[red]Error saving configuration: {e}[/red]")
        return True
    
    def set_vsp_path(self, path):
        """Set path to OpenVSP executable."""
        self.settings["vsp_path"] = path
        console.print(self._prefix, f"Set VSP executable path to: {path}")
    
    #Operational part
    def clear_model(self):
        vsp.ClearVSPModel()
        self.isLoaded = False
        console.print(self._prefix, "Cleared currently loaded model.")
        
    def isModelLoaded(self):
        return self.isLoaded
        
    def addOperatingPoint(self, op):
        if op is None:
            console.print(f"{self._prefix} Could not add operating point.")
        else:
            self.operating_points.append(op)
            console.print(f"{self._prefix} Operating point added. Have {len(self.operating_points)} total.")

    #Mass part
    def addMassConfiguration(self, massConfig):
        self.massConfigurations.append(massConfig)
        console.print(f"\t{self._prefix} Mass configuration added")

    def removeMassConfiguration(self, idx):
        mconfig = self.massConfigurations.pop(idx)
        console.print(f"{self._prefix} Mass config {idx}, {mconfig.name} removed.")

    def getMassConfiguration(self, idx):
        return self.massConfigurations[idx] if 0 <= idx < len(self.massConfigurations) else None

    def getControls(self):
        numgroups = vsp.GetNumControlSurfaceGroups()
        controls = {}
        for i in range(numgroups):
            group_id = i
            group_name = vsp.GetVSPAEROControlGroupName(i)
            surface_names = vsp.GetActiveCSNameVec(group_id)
            num_surfaces = len(surface_names)
            controls[group_name] = {
                "id": group_id,
                "num_surfaces": num_surfaces,
                "surface_names": surface_names
            }
        return controls

    def getOperatingPoint(self, idx):
        return self.operating_points[idx] if 0 <= idx < len(self.operating_points) else None

    def removeOperatingPoint(self, op):
        self.operating_points.remove(op)
        console.print(f"{self._prefix} Operating point '{op.name}' removed.")
    
    def getReferenceQuantities(self):
        """Get reference quantities for the vehicle"""
        if self.refs:
            return self.refs
        
        #Determine what VSPAERO is gonna use as reference quantities
        vsp.SetAnalysisInputDefaults("VSPAEROSweep")
        refArea = float(vsp.GetDoubleAnalysisInput("VSPAEROSweep", "Sref")[0])
        refSpan = float(vsp.GetDoubleAnalysisInput("VSPAEROSweep", "bref")[0])
        refChord = float(vsp.GetDoubleAnalysisInput("VSPAEROSweep", "cref")[0])
        self.refs =  {
            "refArea": refArea,
            "refSpan": refSpan,
            "refChord": refChord
        }
        return self.refs

config = ConfigurationManager()

class PowerPlant:
    """Represents the turbojet powerplant of a vehicle"""

    #TODO: Implement

    _prefix = "[bold dark_orange3]\t<powerplant>[/bold dark_orange3]"

    def __init__(self, name="Powerplant"):
        self.name = name
        self.tsfc = 0
        self.tmax = 0

class MassConfiguration:
    """Represents the mass configuration of the vehicle"""

    _prefix = "[bold magenta]\t<mass>[/bold magenta]"


    def __init__(self, name="Mass Configuration", cg=[0.0, 0.0, 0.0], mass=0.0, inertia_matrix=np.zeros((3, 3))):
        self.name = name
        self.cg = np.array(cg)
        self.mass = mass
        self.inertia_matrix = np.array(inertia_matrix)

    def to_dict(self):
        """Serialize the mass configuration to a dictionary."""
        return {
            "name": self.name,
            "cg": self.cg.tolist() if isinstance(self.cg, np.ndarray) else self.cg,
            "mass": self.mass,
            "inertia_matrix": self.inertia_matrix.tolist() if isinstance(self.inertia_matrix, np.ndarray) else self.inertia_matrix
        }

    @classmethod
    def from_dict(cls, data):
        """Create a mass configuration from a dictionary."""
        return cls(
            name=data["name"],
            cg=np.array(data["cg"]),
            mass=data["mass"],
            inertia_matrix=np.array(data["inertia_matrix"]),
        )


    def __str__(self):
        return (f"MassConfiguration(name={self.name}, mass={self.mass:.2f}, cg={self.cg}, "
                f"inertia_matrix={self.inertia_matrix}")

# Where most of the business happens vv      
class OperatingPoint:
    """Most generic definition of an operating point possible. Just enough to run a vspaero analysis"""

    _prefix = "[bold cyan]\t<op>[/bold cyan]"


    """
        TODO: create dicts of the template type cruise
            refine from_dict and to_dict function
    
    """

    _referenceDict = {
        "alpha": {
            "alias": "A",
            "units": "deg",
            "description": "Angle of attack",
            "initial_guess": 0.0,
            "vspaero_name": "Alpha"
        },
        "beta": {
            "alias": "B",
            "units": "deg",
            "description": "Sideslip angle",
            "initial_guess": 0.0,
            "vspaero_name":"Beta"
        },
        "CL": {
            "alias": "L",
            "units": "",
            "description": "Lift coefficient",
            "initial_guess": 0.0,
            "vspaero_name": "CL"

        },
        "CD": {
            "alias":"D",
            "units":"",
            "description": "Drag coefficient",
            "initial_guess": None,
            "vspaero_name": "CD"
        },
        "CY": {
            "alias": "Y",
            "units": "",
            "description": "Side force coefficient",
            "initial_guess": 0.0,
            "vspaero_name": "CS"
        },
        "Cl": {
            "alias": "l",
            "units": "",
            "description": "Roll moment coefficient",
            "initial_guess": 0.0,
            "vspaero_name": "CMl"
        },
        "Cm": {
            "alias": "m",
            "units": "",
            "description": "Pitch moment coefficient",
            "initial_guess": 0.0,
            "vspaero_name": "CMm"
        },
        "Cn": {
            "alias": "n",
            "units": "",
            "description": "Yaw moment coefficient",
            "initial_guess": 0.0,
            "vspaero_name": "CMn"
        },
        "p":{ 
            "vspaero_name": "p" 
        },
        "q":{
            "vspaero_name": "q"
        },
        "r":{
            "vspaero_name": "r"
        },
        "U":{
            "vspaero_name": "U"
        },
        "Mach": {
            "vspaero_name": "Mach"
        }
    }

    """
        Rework update/change parameters functions to more flexibly use differnent types
        Calculation system should now just always overwrite other things

        
        Leverage default functionality for unitless quanitites
    """
    _freestream_parameters_defaults = {
        "velocity":{
            "value": None,
            "calculated": False,
            "units": "m/s",
            "required":True,
            "limits":(0, -1)
        },
        "density":{
            "value": 1.225,
            "calculated": False,
            "units": "kg/m^3",
            "required":True,
            "limits":(0, -1)
        },
        "dynamic_viscosity": {
            "value": None, #TODO: Put sea-level value in here
            "calculated": False,
            "units": "bruh", #put units in here
            "required":True,
            "limits":(0, -1)
        },
        "speed_of_sound":{
            "value": 343,
            "calculated": False,
            "units": "m/s",
            "required":True,
            "limits": (0, -1)
        },
        "altitude":{
            "value":0,
            "calculated":False,
            "units":"m MSL",
            "required":False,
            "limits": (-1, -1)
        },
        "pressure":{
            "value":101.3*10**3,
            "calculated":False,
            "units":"Pa",
            "required":True,
            "limits": (0, -1)
        },
        "temperature":{
            "value":288.15,
            "calculated":False,
            "units":"K",
            "required":True,
            "limits": (0, -1)
        }
    }
    _generic_parameters_defaults = {
        "load_factor": {
            "value":None,
            "calculated": False,
            "units":"",
            "required":True,
            "limits": (0, -1)
        },
        "Re":{
            "value":None,
            "calculated":False,
            "units":"",
            "required":True,
            "limits": (0, -1)
        },
        "Mach":{
            "value":None,
            "calculated":False,
            "units":"",
            "required":True,
            "limits":(0, -1)
        },
        "massconfig_index":{
            "value":None,
            "calculated":False,
            "units":"",
            "required":True,
            "limits":[-1, -1]
        }
    }
    _OPERATING_POINT_TEMPLATES = {
        "cruise":{
            "description" : "Simple steady wing-level nonclimbing flight. Also use this for specific tests.",
            "required_parameters": {}
        },
        "climb":{
            "description": "Wings-level climb/descend",
            "required_parameters": {
                "flight_path_angle": {"value": None, "calculated":False, "units":"deg", "required":True, "limits": (-1, -1)},
                "rate_of_climb": {"value":None, "calculated":False, "units":"m/s", "required":True, "limits": (-1, -1)}
            }
        },
        "turn":{
            "description": "Level turning flight",
            "required_parameters":{
                "turn_radius":{"value":None, "calculated":False, "units":"m","required":True, "limits": (0, -1)},
                "rate_of_turn":{"value":None, "calculated":False, "units":"deg/s","required":True, "limits": (0, -1)},
                "bank_angle":{"value":None, "calculated":False, "units":"deg","required":True, "limits": (0, 90)}
            }
        },
        "hilift":{ #TODO There's the hi-lift options in vspaero I could think about adding functionality to
            "description": "High-lift configuration (CL treated as CLmax)",
            "required_parameters": {
                "ground_effect_distance":{"value":None,"calculated":False,"units":"m","required":True, "limits": (0,-1)},
                "rolling_friction_coeff":{"value":None,"calculated":False,"units":"","required":True, "limits": (0,-1)},
                "runway_length":{"value":None,"calculated":False,"units":"m","required":True, "limits": (0,-1)},
            }
        }
    }

    def __init__(self, name, type):
        self.name = name
        self.settings = {
            "max_iterations": 5,
            "tolerance": 1e-4,
            "type": type
        }
        self.freestream_parameters = None
        self.generic_parameters = None
        self.type_parameters = None
        self.inputs = None
        self.outputs = None

        self.isConverged = False
        self.hasResults = False
        self.modifiedSinceLastExec = True
        self.results = None

    """
    def __init__(self, name, type, settings=None, parameters=None, inputs=None, outputs=None, controls=None, hasResults=False, modifiedSinceLastExec=False, isConverged=False, results=None):   
        self.name = name
        self.settings = settings if not settings is None else {
            "max_iterations": 5,
            "tolerance": 1e-4,
            "type": type
        }
        #TODO: Move mach and reynolds to inputs and force auto-calculation
        #TODO: Divide parameters into climbing, cruising, turning, etc.
        #TODO: Add nickname for parameters to make it easier to input
        self.parameters = parameters if not parameters is None else {
            "velocity": { "value": None, "calculated": False },
            "load_factor": { "value": None, "calculated": False },
            "bank_angle": { "value": None, "calculated": False },
            "altitude": { "value": None, "calculated": False },
            "massconfig_index": { "value": None, "calculated": False },
            "Rec": { "value": None, "calculated": False },
            "Mach": { "value": None, "calculated": False },
            "rate_of_climb": { "value": None, "calculated": False },
            "flight_path_angle": { "value": None, "calculated": False },
            "rate_of_turn": { "value": None, "calculated": False },
            "density": { "value": None, "calculated": False },
            "dynamic_viscosity": { "value": None, "calculated": False },
            "speed_of_sound": { "value": None, "calculated": False }
        }
        
            Inputs (incl controls) can be FIXED or DRIVEN
            Outputs can be DRIVERS/FIXED or FREE
    
        self.inputs = inputs if not inputs is None else {
            "alpha":{
                "value": 0.0,
                "driver":"fixed"
            },
            "beta":{
                "value": 0.0,
                "driver":"fixed"
            }
        }
        self.outputs = outputs if not outputs is None else {
            "CL": {
            "value": None,
            "driver": "free"
            },
            "CY": {
            "value": None,
            "driver": "free"
            },
            "Cl": {
            "value": None,
            "driver": "free"
            },
            "Cm": {
            "value": None,
            "driver": "free"
            },
            "Cn": {
            "value": None,
            "driver": "free"
            }
        }
        if controls is None:
            self.controls = {}
            controls_data = config.getControls()
            for group_name in controls_data.keys():
                self.controls[group_name] = {
                    "value": 0.0,
                    "driver": "fixed",
                    "details": controls_data[group_name]
                }
        else:
            self.controls = controls
        
        self.isConverged = isConverged
        self.hasResults = hasResults
        self.modifiedSinceLastExec = modifiedSinceLastExec
        self.results = results
    """
    
    def print(self):
        """Print the operating point in a formatted manner to rich console"""
        titlestr = f"[bold] Operating Point: '{self.name}' of type '{self.settings['type']}'"
        titlestr+=" >> " + ("[green]**READY**[/green]" if self.isReady() else "[red]**NOT READY**[/red]")
        titlestr+=" >> " + ("[green]**UNMODIFIED**[/green]" if not self.modifiedSinceLastExec else "[red]**MODIFIED**[/red]")
        titlestr+=" >> " + ("[green]**CONVERGED**[/green]" if self.isConverged else "[red]**NOT CONVERGED**[/red]")
        titlestr+=" >> " + ("[green]**RESULTS**[/green]" if self.hasResults else "[red]**NO RESULTS**[/red]")
        titlestr+="[/bold]"
        console.print(titlestr)

        #console.print(self.generic_parameters)
        #console.print(self.freestream_parameters)
        #console.print(self.type_parameters)

        tableList = []
        #TODO: Create a separate thing for the mass configuration bc it doesn't really work like the rest of the parameters
        # Create Tables
        genparmstable = Table(title="Generic Parameters",show_header=False,box=None)
        genparmstable.add_column("Parameter", style="cyan")
        genparmstable.add_column("Value", style="magenta")
        for name, param in self.generic_parameters.items():
            firstColumn = f"{name}{'*' if param['required'] else ''}"
            if param['units'] != "":
                firstColumn += f" ({param['units']})"
            secondColumn = f"{param['value']:.3g}" if not (param['value'] is None) else '---'
            if param['calculated']:
                secondColumn = "[green]" + secondColumn + "[/green]"
            genparmstable.add_row(firstColumn, secondColumn)

        tableList.append(genparmstable)

        fsparmstable = Table(title="Freestream Parameters",show_header=False,box=None)
        fsparmstable.add_column("Parameter", style="cyan")
        fsparmstable.add_column("Value", style="magenta")
        for name, param in self.freestream_parameters.items():
            firstColumn = f"{name}{'*' if param['required'] else ''}"
            if param['units'] != "":
                firstColumn += f" ({param['units']})"
            secondColumn = f"{param['value']:.3g}" if not (param['value'] is None) else '---'
            if param['calculated']:
                secondColumn = "[green]" + secondColumn + "[/green]"
            fsparmstable.add_row(firstColumn, secondColumn)

        tableList.append(fsparmstable)

        if not len(self.type_parameters.keys()) == 0:
            typeparmstable = Table(title=f"{self.settings['type']} Parameters",show_header=False,box=None)
            typeparmstable.add_column("Parameter", style="cyan")
            typeparmstable.add_column("Value", style="magenta")
            for name, param in self.type_parameters.items():
                firstColumn = f"{name}{'*' if param['required'] else ''}"
                if param['units'] != "":
                    firstColumn += f" ({param['units']})"
                secondColumn = f"{param['value']:.3g}" if not (param['value'] is None) else '---'
                if param['calculated']:
                    secondColumn = "[green]" + secondColumn + "[/green]"
                typeparmstable.add_row(firstColumn, secondColumn)
            tableList.append(typeparmstable)

        inputstable = Table(title="Inputs",show_header=False,box=None)
        inputstable.add_column("Var", style="green")
        inputstable.add_column("--", style="yellow")
        inputstable.add_column("Driver", style="blue")
        for key, value in self.inputs.items():
            firstColumn = f"{key}"
            secondColumn = "==" if value["driver"] == "fixed" else "=>"
            thirdColumn = f"{value['value']:.3g}" if value["driver"] == "fixed" else value["driver"]
            inputstable.add_row(firstColumn, secondColumn, f"{thirdColumn}") #TODO implement driver
        for key, value in self.controls.items():
            firstColumn = f"{key}"
            secondColumn = "==" if value["driver"] == "fixed" else "=>"
            thirdColumn = f"{value['value']:.3g}" if value["driver"] == "fixed" else value["driver"]
            inputstable.add_row(firstColumn, secondColumn, f"{thirdColumn}")
        tableList.append(inputstable)

        outputstable = Table(title="Outputs", show_header=False,box=None)
        outputstable.add_column("Var", style="green")
        outputstable.add_column("--", style="yellow")
        outputstable.add_column("Value", style="green")
        for key, value in self.outputs.items():
            #either fixed or free
            firstColumn = f"{key}"
            secondColumn = "=="
            thirdColumn = f"{value['value']:.3g}" if value["driver"] == "fixed" else value["driver"]
            if value["driver"] == "fixed" and not self.isDriven(key):
                thirdColumn = f"[red]{thirdColumn}[/red]"
            outputstable.add_row(firstColumn, secondColumn, f"{thirdColumn}")
        tableList.append(outputstable)


        if not self.getParameter("massconfig_index")["value"] is None:
            massConfig = config.getMassConfiguration(self.getParameter("massconfig_index")["value"])
            table4 = Table(title="Mass Configuration",box=None)
            table4.add_column("Parameter", style="cyan")
            table4.add_column("Value", style="magenta")
            table4.add_row("Name", massConfig.name)
            table4.add_row("Mass (kg)", f"{massConfig.mass:.3f}")
            table4.add_row("CG (x, y, z) (m)", f"{massConfig.cg[0]:.3f}, {massConfig.cg[1]:.3f}, {massConfig.cg[2]:.3f}")
            table4.add_row("Inertia Matrix", f"{massConfig.inertia_matrix[0, 0]:.3f}, {massConfig.inertia_matrix[0, 1]:.3f}, {massConfig.inertia_matrix[0, 2]:.3f}")
            table4.add_row("", f"{massConfig.inertia_matrix[1, 0]:.3f}, {massConfig.inertia_matrix[1, 1]:.3f}, {massConfig.inertia_matrix[1, 2]:.3f}")
            table4.add_row("", f"{massConfig.inertia_matrix[2, 0]:.3f}, {massConfig.inertia_matrix[2, 1]:.3f}, {massConfig.inertia_matrix[2, 2]:.3f}")
            tableList.append(table4)

        console.print(Padding(Columns(tableList, padding=(0, 1)), (0, 0, 0, 8)))
    
    def isReady(self):
        """Check if the operating point is ready to be executed"""
        return not any(parm['required'] and parm['value'] is None for key, parm in {**self.generic_parameters,**self.freestream_parameters,**self.type_parameters}.items())
    
    def isDriven(self, output):
        """Check if an output is driven by an input"""
        return any([input_data["driver"] == output for input_data in self.inputs.values()]) or any([control_data["driver"] == output for control_data in self.controls.values()])

    def computeGeometry(self):
        #TODO: Improve this to handle errors, also eventually add panel method
        """Compute the geometry for the operating point"""
        analysisString = "VSPAEROComputeGeometry"
        console.print(f"{self._prefix} Computing geometry for operating point '{self.name}' ... ")
        # Set static parameters
        console.print(f"{self._prefix} Including Geometries:")
        geom_ids = vsp.FindGeoms()
        table = Table(title="Geometries", show_header=False, box=None)
        table.add_column("Name", style="magenta")
        table.add_column("Geom ID", style="cyan")
        for geom_id in geom_ids:
            name = vsp.GetGeomName(geom_id)
            in_set_0 = vsp.GetSetFlag(geom_id, 1)  # Check if in Set 0
            if in_set_0:
                table.add_row(name, geom_id)

        console.print(Padding(table, (0, 0, 0, 12)))
        vsp.SetAnalysisInputDefaults(analysisString)
        vsp.SetIntAnalysisInput(analysisString, "AnalysisMethod", [vsp.VORTEX_LATTICE])
        vsp.SetIntAnalysisInput(analysisString, "GeomSet", [1])
        vsp.Update()
        allResults = vsp.ExecAnalysis(analysisString)
        outputFileName = vsp.GetStringResults(allResults, "DegenGeomFileName")[0]
        timeToComplete = vsp.GetDoubleResults(allResults, "Analysis_Duration_Sec")[0]
        console.print(f"{self._prefix} Done in {timeToComplete:.2f} seconds. File saved as '{outputFileName}'")
        return True

    def exec(self):
        """Execute the operating point"""
        if not self.isReady():
            console.print(f"{self._prefix} Operating point '{self.name}' is not ready to be executed")
            return False
        if self.hasResults and (not self.modifiedSinceLastExec):
            confirm = console.input(f"{self._prefix} Operating point '{self.name}' has results and was not modified since last execution. Re-execute? (y/n): ").strip().lower()
            if confirm != "y":
                console.print(f"{self._prefix} Execution aborted.")
                return False
        if vsp.IsGUIBuild() and vsp.IsGUIRunning():
            console.print(f"{self._prefix} GUI Locked during duration of execution.")
            vsp.Lock()
        console.print(f"{self._prefix}[bold] Executing operating point '{self.name}'[/bold]")
        self.computeGeometry()
        console.print(f"{self._prefix} Starting trimming process: '{self.name}' ... (this is unfortunately extremely slow and may take a few minutes for a complex operating point :/)")
        self._historyDF = pd.DataFrame(columns=["Iteration", "CompTime", *self.inputs.keys(), *self.controls.keys(), *self.outputs.keys()])
        self._setInitialGuess()
        self.isConverged = False
        self.hasResults = False

        maxIterations = self.settings["max_iterations"]
        self._lastIterStartTime = pd.Timestamp.now()

        with Live(self.render_process()) as live:  # Start live update
            # Run a single iteration of the simulation, dispatching in another thread to speed up the process
            while self._historyDF.shape[0] < maxIterations:
                self._lastIterStartTime = pd.Timestamp.now()
                #Run the simulation
                thread = threading.Thread(target=self._simulate)
                thread.start()

                while thread.is_alive():
                    last_index = self._historyDF.index[-1]
                    timeSinceIterStart = (pd.Timestamp.now() - self._lastIterStartTime).total_seconds()
                    self._historyDF.loc[last_index, "CompTime"] = timeSinceIterStart
                    live.update(self.render_process())  # Access the live object to update the rendering

                thread.join() #wait for complete
                #Check for convergence
                #if self._checkConvergence():
                #    break
                self._processTrimResults()
                self._newtonRaphson()
                live.update(self.render_process())  # Access the live object to update the rendering
                if self.isConverged:
                    break


        if self.isConverged: #Trimming succeeded
            console.print(f"{self._prefix} Trimming successful. Results stored")
            self.hasResults = True
            self._collectAllResults()
            #self._printResults()
            #Print some results
        else: #Trimming failed
            console.print(f"{self._prefix} Trimming failed. Adjust your settings or try again.")
            self.hasResults = False

        if vsp.IsGUIBuild() and vsp.IsGUIRunning():
            console.print(f"{self._prefix} GUI Unlocked")
            vsp.Unlock()

        # Run parasite drag analysis

        self.modifiedSinceLastExec = False

        """
        where the magic happens
            while under max iteration count:
                run the next iteration using vspaero -> update history dataframe with this iteration's coefficient results
                check if we have met the convergence criteria -> if yes, exit loop
                if not:
                    extract the stability/control derivatives matrix
                    calculate the next set of inputs using newton raphson method
                    update history dataframe with new inputs
        
        """
        #Go from here...
    
    def render_process(self):
        """Render the table of results"""
        table = Table(box=None)
        for col in self._historyDF.columns:
            table.add_column(col)
        for _, row in self._historyDF.iterrows():
            table.add_row(*[f"{val:.3f}" if pd.notna(val) else "..." for val in row.values])
        return Padding(table, (0, 0, 0, 12))

    def _setInitialGuess(self):
        """Set initial guess for inputs with no value and initialize the history dataframe"""
        self._historyDF["Iteration"] = [0]
        self._historyDF["CompTime"] = [None]
        for key in self.inputs.keys():
            if self.inputs[key]["value"] is None:
                self._historyDF[key] = [self._referenceDict[key]["initial_guess"]]
                if key == "alpha" and self.inputs['alpha']['driver'] != 'fixed' and self.outputs['CL']['value'] is not None:
                    #Special alpha->CL relationship guess ideal lift slope of 2pi (often over-guesses but that's fine)
                    self._historyDF[key] = [self.outputs['CL']['value']/(180)]
            else: 
                self._historyDF[key] = [self.inputs[key]["value"]]
        for key in self.controls.keys():
            if self.controls[key]["value"] is None:
                self._historyDF[key] = [0.0]
            else:
                self._historyDF[key] = [self.controls[key]["value"]]
        for key in self.outputs.keys():
            self._historyDF[key] = [None]

    def _getVSPAEROName(self, key):
        """Get the VSPAERO name for a given key"""
        if key in self._referenceDict:
            return self._referenceDict[key]["vspaero_name"]
        elif key in self.controls:
            return key
        else:
            console.print(f"{self._prefix} Invalid key")
            return None

    def _getNextInput(self, key):
        """Get the next input value for a given key"""
        return self._historyDF[key].iloc[-1]
        
    def _getLastOutput(self, key):
        """Get the last output value for a given key"""
        return self._historyDF.tail(1)[key].values[0]

    def _newtonRaphson(self):
        """Perform a single iteration of the Newton-Raphson method"""
        # Calculate the next set of inputs based on jacobian extraction

        #Reduce jacobian
        #Get subset of derivs matrix with fixed output rows and driver input columns
        control_angles = [key for key, val in self.inputs.items() if val.get("driver") != "fixed"]
        control_deflections = [key for key, val in self.controls.items() if val.get("driver") != "fixed"]
        control_inputs = control_angles + control_deflections

        controlled_outputs = [key for key, val in self.outputs.items() if val.get("driver") == "fixed"]

        reduced_jacobian = self.jacobian.loc[controlled_outputs, control_inputs].to_numpy()
        #print(self.results["jacobian"])
        # Get error vector in all outputs that are constrained

        lastResults = self._historyDF.tail(1).iloc[0]

        desired_outputs_vector = np.array([self.outputs[key]["value"] for key in controlled_outputs])

        current_outputs_vector = np.array([lastResults[key] for key in controlled_outputs])

        error_vector = desired_outputs_vector - current_outputs_vector

        #check if we are converged
        if np.linalg.norm(error_vector) < self.settings["tolerance"]:
            self.isConverged = True
            return True

        reduced_jacobian_inverse = np.linalg.pinv(reduced_jacobian)

        input_adjust_vector = reduced_jacobian_inverse @ error_vector
        
        # Update the inputs and controls with the new values
        historyDF_lastindex = self._historyDF.index[-1]
        for i, key in enumerate(control_inputs):
            self._historyDF.loc[historyDF_lastindex+1, key] = self._historyDF.loc[historyDF_lastindex, key] + input_adjust_vector[i]

        fixed_angles = [key for key, val in self.inputs.items() if val.get("driver") == "fixed"]
        fixed_deflections = [key for key, val in self.controls.items() if val.get("driver") == "fixed"]
        fixed_inputs = fixed_angles + fixed_deflections

        for i, key in enumerate(fixed_inputs):
            self._historyDF.loc[historyDF_lastindex+1, key] = self._historyDF.loc[historyDF_lastindex, key]

        self._historyDF.loc[historyDF_lastindex+1, "Iteration"] = self._historyDF.loc[historyDF_lastindex, "Iteration"] + 1

        #TODO: Check for divergence
        #TODO: Check if a driver has very little control over it's output
        #TODO: This should be gradient descent not newton raphson but no use doing that until vspaero is updated
        """
        console.print(f"{self._prefix} Outputs from the last iteration and their errors:")
        for i, key in enumerate(controlled_outputs):
            error = error_vector[i]
            console.print(f"\t{key}: {error}")
        # Print the adjustments
        console.print(f"{self._prefix} Input adjustments:")
        for i, key in enumerate(control_inputs):
            adjustment = input_adjust_vector[i]
            console.print(f"\t{key}: {adjustment:.6f}")
        """
        
    def _simulate(self):
        """Single iteration of simulation"""
        analysisString = "VSPAEROSweep"
        vsp.SetAnalysisInputDefaults(analysisString)
        vsp.SetIntAnalysisInput(analysisString, "UseModeFlag", [False])
        vsp.SetIntAnalysisInput(analysisString, "GeomSet", [1])  # Use Set 0
        vsp.SetDoubleAnalysisInput(analysisString, "MachStart", [self.getParameter("Mach")['value']])
        vsp.SetIntAnalysisInput(analysisString, "MachNpts", [1])
        vsp.SetDoubleAnalysisInput(analysisString, "MachEnd", [self.getParameter("Mach")['value']])
        vsp.SetDoubleAnalysisInput(analysisString, "Machref", [self.getParameter("Mach")['value']])

        vsp.SetDoubleAnalysisInput(analysisString, "ReCref", [self.getParameter("Re")['value']]) 
        vsp.SetDoubleAnalysisInput(analysisString, "ReCrefNpts", [1])
        vsp.SetDoubleAnalysisInput(analysisString, "ReCrefEnd", [self.getParameter("Re")['value']]) 

        vsp.SetDoubleAnalysisInput(analysisString, "Vinf", [self.getParameter("velocity")['value']])
        vsp.SetDoubleAnalysisInput(analysisString, "Vref", [self.getParameter("velocity")['value']])
        vsp.SetDoubleAnalysisInput(analysisString, "Rho", [self.getParameter("density")['value']])
        mconfig = config.getMassConfiguration(self.getParameter("massconfig_index")['value'])
        vsp.SetDoubleAnalysisInput(analysisString, "Xcg", [mconfig.cg[0]])
        vsp.SetDoubleAnalysisInput(analysisString, "Ycg", [mconfig.cg[1]])
        vsp.SetDoubleAnalysisInput(analysisString, "Zcg", [mconfig.cg[2]])

        if self.settings["type"] == "hilift":
            vsp.SetIntAnalysisInput(analysisString, "GroundEffectToggle", [True])
            vsp.SetDoubleAnalysisInput(analysisString, "GroundEffect", [self.getParameter("ground_effect_distance")['value']])


        vsp.SetStringAnalysisInput(analysisString, "RedirectFile", ["log.txt"])

        vsp.SetIntAnalysisInput(analysisString, "AnalysisMethod", [vsp.VORTEX_LATTICE])
        vsp.SetIntAnalysisInput(analysisString, "NCPU", [config.settings["num_procs"]])
        vsp.SetIntAnalysisInput(analysisString, "UnsteadyType", [vsp.STABILITY_DEFAULT])
        vsp.SetIntAnalysisInput(analysisString, "2DFEMFlag", [False])
        

        # Set inputs that change from iteration to iteration
        vsp.SetDoubleAnalysisInput(analysisString, "AlphaStart", [self._getNextInput("alpha")])
        vsp.SetIntAnalysisInput(analysisString, "AlphaNpts", [1])
        vsp.SetDoubleAnalysisInput(analysisString, "AlphaEnd", [self._getNextInput("alpha")])

        vsp.SetDoubleAnalysisInput(analysisString, "BetaStart", [self._getNextInput("beta")])
        vsp.SetIntAnalysisInput(analysisString, "BetaNpts", [1])
        vsp.SetDoubleAnalysisInput(analysisString, "BetaEnd", [self._getNextInput("beta")])
        #vsp.PrintAnalysisInputs(analysisString)
        control_group_settings_container = vsp.FindContainer("VSPAEROSettings",0)
        for key in self.controls.keys():
            #need to get ID of control group
            group_id = self.controls[key]["details"]["id"]
            deflection_angle_id = vsp.FindParm(control_group_settings_container, "DeflectionAngle", f"ControlSurfaceGroup_{group_id}")
            vsp.SetParmVal(deflection_angle_id, self._getNextInput(key))

        #vsp.PrintAnalysisInputs(analysisString)

        #TODO: There are so many more inputs I can set. need to investigate further
        #TODO: Can add multiple levels of fidelity depending on how far from convergence we are (currently does not need to be so high)
        
        #Actually run VSPAERO
        try:
            self._recentResultID = vsp.ExecAnalysis("VSPAEROSweep")
        except Exception as e:
            console.print(f"{self._prefix} Error during simulation: {e}")
            self._recentResultID = None

        """
           [input_name]                  [type]         [#]     [current values-->]
            2DFEMFlag                     boolean        1
            ActuatorDiskFlag              boolean        1
            AlphaEnd                      double         1       10.000000 
            AlphaNpts                     integer        1       3 
            AlphaStart                    double         1       0.000000 
            AlternateInputFormatFlag      boolean        1
            AnalysisMethod                integer        1       0 
            AutoTimeNumRevs               integer        1       5 
            AutoTimeStepFlag              boolean        1
            BetaEnd                       double         1       0.000000 
            BetaNpts                      integer        1       1 
            BetaStart                     double         1       0.000000 
            CGDegenSet                    integer        1       -1 
            CGGeomSet                     integer        1       1 
            CGModeID                      string         1        
            Clmax                         double         1       -1.000000 
            ClmaxToggle                   integer        1       0
            FarDist                       double         1       -1.000000
            FarDistToggle                 boolean        1
            FixedWakeFlag                 boolean        1
            FromSteadyState               boolean        1
            GeomSet                       integer        1       1
            GroundEffect                  double         1       -1.000000
            GroundEffectToggle            boolean        1
            HoverRamp                     double         1       0.000000
            HoverRampFlag                 boolean        1
            KTCorrection                  boolean        1
            MACFlag                       boolean        1
            MachEnd                       double         1       0.000000
            MachNpts                      integer        1       1 
            MachStart                     double         1       0.000000
            Machref                       double         1       0.300000
            ManualVrefFlag                boolean        1
            MassSliceDir                  integer        1       0
            MaxTurnAngle                  double         1       -1.000000
            MaxTurnToggle                 boolean        1
            ModeID                        string         1
            NCPU                          integer        1       4
            NoiseCalcFlag                 boolean        1
            NoiseCalcType                 integer        1       0
            NoiseUnits                    integer        1       0
            NumMassSlice                  integer        1       10
            NumTimeSteps                  integer        1       25
            NumWakeNodes                  integer        1       64
            Precondition                  integer        1       0
            ReCref                        double         1       10000000.000000
            ReCrefEnd                     double         1       20000000.000000
            ReCrefNpts                    integer        1       1 
            RedirectFile                  string         1       stdout
            RefFlag                       integer        1       0
            Rho                           double         1       0.002377
            RotateBladesFlag              boolean        1
            ScurveFlag                    boolean        1
            Sref                          double         1       100.000000
            Symmetry                      boolean        1
            TimeStepSize                  double         1       0.001000
            UnsteadyType                  integer        1       0 
            UseCGModeFlag                 boolean        1
            UseModeFlag                   boolean        1
            Vinf                          double         1       100.000000
            Vref                          double         1       100.000000
            WakeNumIter                   integer        1       3
            WingID                        boolean        1
            Xcg                           double         1       0.000000
            Ycg                           double         1       0.000000
            Zcg                           double         1       0.000000
            bref                          double         1       1.000000
            cref                          double         1       1.000000
            """
 
    def _processTrimResults(self):
        """Process the stability results"""
        #resultsNames = vsp.GetAllResultsNames()
        #for name in resultsNames:
        #    console.print(f"{self._prefix} {name}")
        stab_results = vsp.FindLatestResultsID("VSPAERO_Stab")
        #Pull the base case results
        #console.print(f"{self._prefix} SM: {SM}, X_NP: {X_NP}")

        #vsp.PrintResults(stab_results)

        # Collect base case results in pandas dataframe
        #TODO: I can actually record the results of each of the runs, not just the base case
        #TODO: This might let me run the trim with fewer actual calls to VSPAERO which would make it much faster
        #like if the value I want skips over between base and perturbed for a particular control I know it's "within the linear region (ish)" and I shouldn't have to call VSPAERO again
        historyDF_lastindex = self._historyDF.index[-1]
        prefix = "Base_Aero_"
        for key in self.outputs.keys():
            suffix = self._getVSPAEROName(key)
            val_string = prefix + suffix
            val = float(vsp.GetDoubleResults(stab_results, val_string)[0])
            self._historyDF.loc[historyDF_lastindex, key] = val

        #Pull derivatives matrix
        derivs = pd.DataFrame(columns=[*self.inputs.keys(), *self.controls.keys()], index=[*self.outputs.keys()],dtype=float)
        for input in derivs.columns:
            for i, output in enumerate(self.outputs.keys()):
                derivativename = f"{self._getVSPAEROName(output)}_{self._getVSPAEROName(input)}"
                #console.print(f"{derivativename}")
                derivs.loc[output, input] = np.deg2rad(vsp.GetDoubleResults(stab_results, derivativename)[0])

        self.jacobian = derivs
        # Update history DF

    def _collectAllResults(self):
        """Collect all VSPAERO stability, loading, etc. data"""
        # Steady Aero/Stability Results
        stab_results_id = vsp.FindLatestResultsID("VSPAERO_Stab")

        # Record static margin and neutral point
        SM = float(vsp.GetDoubleResults(stab_results_id, "SM")[0])
        X_NP = float(vsp.GetDoubleResults(stab_results_id, "X_np")[0])


        # Record angles and deflections in final iteration
        final_inputs = pd.DataFrame(columns=[*self.inputs.keys(), *self.controls.keys()], dtype=float)
        lastHistoryRow = self._historyDF.tail(1).iloc[0]
        for col in lastHistoryRow.index:
            if col in final_inputs.columns:
                final_inputs.loc[0, col] = lastHistoryRow[col]

        # Record outputs in stability axes
        prefix = "Base_Aero"
        base_case_stability_axes = pd.DataFrame(columns=["CD", "CY", "CL", "Cl", "Cm", "Cn"], dtype=float)
        for col in base_case_stability_axes.columns:
            result_name = f"{prefix}_{self._getVSPAEROName(col)}"
            result_value = float(vsp.GetDoubleResults(stab_results_id, result_name)[0])
            base_case_stability_axes.loc[0, col] = result_value

        base_case_body_axes = pd.DataFrame(columns=["CFx", "CFy", "CFz", "CMx", "CMy", "CMz"], dtype=float)
        for col in base_case_body_axes.columns:
            result_name = f"{prefix}_{col}"
            result_value = float(vsp.GetDoubleResults(stab_results_id, result_name)[0])
            base_case_body_axes.loc[0, col] = result_value
        
        #Pull derivatives matrix (stability axes)
        derivs_stability_axes = pd.DataFrame(columns=[*self.inputs.keys(), *self.controls.keys(), "p", "q", "r", "U", "Mach"], index=["CD", "CY", "CL", "Cl", "Cm", "Cn"], dtype=float)
        for input in derivs_stability_axes.columns:
            for i, output in enumerate(["CD", "CY", "CL", "Cl", "Cm", "Cn"]):
                derivativename = f"{self._getVSPAEROName(output)}_{self._getVSPAEROName(input)}"
                #console.print(f"{derivativename}")
                derivs_stability_axes.loc[output, input] = float(vsp.GetDoubleResults(stab_results_id, derivativename)[0])

        derivs_body_axes = pd.DataFrame(columns=[*self.inputs.keys(), *self.controls.keys(), "p", "q", "r", "U", "Mach"], index=["CFx", "CFy", "CFz", "CMx", "CMy", "CMz"], dtype=float)
        for input in derivs_body_axes.columns:
            for output in derivs_body_axes.index:
                derivativename = f"{output}_{self._getVSPAEROName(input)}"
                #console.print(f"{derivativename}")
                derivs_body_axes.loc[output, input] = float(vsp.GetDoubleResults(stab_results_id, derivativename)[0])
        
        
        # TODO: Loading Results

        self.results = {
            "stability":{
                "SM":SM,
                "X_NP":X_NP,
                "final_inputs":final_inputs,
                "base_case_stability_axes":base_case_stability_axes,
                "derivs_stability_axes":derivs_stability_axes,
                "base_case_body_axes":base_case_body_axes,
                "derivs_body_axes":derivs_body_axes
            }
        }

    def _printResults(self):
        """Print the results of the operating point"""
        console.print(f"{self._prefix} Base Case Stability Results:")
        console.print(f"{self._prefix} Static Margin: {self.results['stability']['SM']:.3f}")
        console.print(f"{self._prefix} Neutral Point: {self.results['stability']['X_NP']:.3f}")
        console.print(f"{self._prefix} Final Inputs:")
        console.print(self.results['stability']['final_inputs'])
        console.print(f"{self._prefix} Base Case Stability Axes:")
        console.print(self.results['stability']['base_case_stability_axes'])
        console.print(f"{self._prefix} Base Case Body Axes:")
        console.print(self.results['stability']['base_case_body_axes'])
        console.print(f"{self._prefix} Derivatives Matrix (Stability Axes):")
        console.print(self.results['stability']['derivs_stability_axes'])
        console.print(f"{self._prefix} Derivatives Matrix (Body Axes):")
        console.print(self.results['stability']['derivs_body_axes'])

    def to_dict(self):
        return {
            "name": self.name,
            "settings": self.settings,
            "genparms": self.generic_parameters,
            "fsparms": self.freestream_parameters,
            "tparms": self.type_parameters,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "controls": self.controls,
            "hasResults": self.hasResults,
            "modifiedSinceLastExec": self.modifiedSinceLastExec,
            "isConverged": self.isConverged,
            "results": self.results_to_dict()
        }
    
    def results_to_dict(self):
        """
        Convert the full results structure, including nested dictionaries and DataFrames, into a pure dictionary.
        
        Parameters:
            results (dict): Original results structure containing scalars, nested dictionaries, and DataFrames.

        Returns:
            dict: Dictionary with all DataFrames converted to dictionary format.
        """
        if self.results == None:
            return None
        def convert(value):
            if isinstance(value, pd.DataFrame):
                return value.to_dict(orient="split")  # Convert DataFrame to dictionary
            elif isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}  # Recursively convert nested dictionaries
            else:
                return value  # Scalars remain unchanged

        return {key: convert(val) for key, val in self.results.items()}
    
    def getParameter(self, parameter):
        if parameter in self.generic_parameters:
            return self.generic_parameters[parameter]
        elif parameter in self.freestream_parameters:
            return self.freestream_parameters[parameter]
        elif parameter in self.type_parameters:
            return self.type_parameters[parameter]
        else:
            return False

    def _setParameter(self, parameter, value):
        if parameter in self.generic_parameters:
            self.generic_parameters[parameter]["value"] = value
        elif parameter in self.freestream_parameters:
            self.freestream_parameters[parameter]["value"] = value
        elif parameter in self.type_parameters:
            self.type_parameters[parameter]["value"] = value
        else:
            console.print(f"{self._prefix} Invalid parameter name.")

    def _setCalculated(self, parameter, value):
        if parameter in self.generic_parameters:
            self.generic_parameters[parameter]["calculated"] = value
        elif parameter in self.freestream_parameters:
            self.freestream_parameters[parameter]["calculated"] = value
        elif parameter in self.type_parameters:
            self.type_parameters[parameter]["calculated"] = value
        else:
            console.print(f"{self._prefix} Invalid parameter name.")

    def _getCalculated(self, parameter):
        if parameter in self.parameters:
            return self.parameters[parameter]["calculated"]
        else:
            console.print(f"{self._prefix} Invalid parameter name")
    
    def updateParameter(self, parameter, value): #TODO: Fix the parameter update functions
        """
            TODO:
                - Add turning calculations
        """

        if not self.getParameter(parameter):
            return False
        
        try:
            vf = float(value)
        except ValueError:
            return False

        # Check limits on input parameters
        limits = self.getParameter(parameter)['limits']
        if not ((limits[0] == -1 or vf >= limits[0]) and (limits[1] == -1 or vf <= limits[1])):
            return False

        # Mass config special case can probably isolate this
        if parameter == "massconfig_index":
            if not (0 <= int(value) < len(config.massConfigurations)):
                console.print(f"{self._prefix} Invalid mass configuration index.")
                return False
            vf = int(value)
            
        # Safe to run internal method set parameter
        self._setParameter(parameter, vf)
        self._setCalculated(parameter, False)

        # Now treat special cases
        #TODO: Check values
        if parameter == "altitude":
            confirm = console.input(f"{self._prefix} Set density, viscosity, speed of sound, ambient pressure and temperature to ISA standard at {value} m? (y/n): ").strip().lower()
            if confirm == "y":
                atmosphere = Atmosphere(float(value))
                self._setParameter("density", atmosphere.density[0])
                self._setCalculated("density", True)
                self._setParameter("dynamic_viscosity", atmosphere.dynamic_viscosity[0])
                self._setCalculated("dynamic_viscosity", True)
                self._setParameter("speed_of_sound", atmosphere.speed_of_sound[0])
                self._setCalculated("speed_of_sound", True)
                self._setParameter("pressure", atmosphere.pressure[0])
                self._setCalculated("pressure", True)
                self._setParameter("temperature", atmosphere.temperature[0])
                self._setCalculated("temperature", True)
                console.print(f"{self._prefix} Density, viscosity, speed of sound, ambient pressure and temperature set to ISA standard at {value} m.")
        elif parameter == "Mach":
            if 0.7 < float(value) < 1.25: #TODO: Add/integrate 2D transonic analysis capability from xfoil
                console.print(f"{self._prefix} [yellow]Warning: Transonic analysis (Mach 0.7 - 1.25) is not supported and may not work correctly.[/yellow]")
        elif parameter == "rate_of_turn":
            if not self.getParameter("velocity")['value'] is None:
                rate_of_turn = self.getParameter("rate_of_turn")['value']
                velocity = self.getParameter("velocity")['value']
                bank_angle_deg = np.rad2deg(np.atan(np.deg2rad(rate_of_turn)*velocity/constants.g))
                self._setParameter("bank_angle", bank_angle_deg)
                self._setCalculated("bank_angle", True)
                turn_radius = (velocity**2)/(constants.g * np.tan(bank_angle_deg))
                self._setParameter("turn_radius", turn_radius)
                self._setCalculated("turn_radius", True)
        elif parameter == "turn_radius":
            if not self.getParameter("velocity")['value'] is None:
                turn_radius = self.getParameter("turn_radius")['value']
                velocity = self.getParameter("velocity")['value']
                bank_angle_deg = np.rad2deg(np.atan(turn_radius*constants.g/(velocity**2)))
                self._setParameter("bank_angle", bank_angle_deg)
                self._setCalculated("bank_angle", True)
                rate_of_turn = constants.g/velocity * np.rad2deg(np.tan(np.deg2rad(bank_angle_deg)))
                self._setParameter("rate_of_turn", rate_of_turn)
                self._setCalculated("rate_of_turn", True)
        elif parameter == "bank_angle":
            if not self.getParameter("velocity")['value'] is None:
                bank_angle_deg = self.getParameter("bank_angle")['value']
                velocity = self.getParameter("velocity")['value']
                turn_radius = (velocity**2)/(constants.g * np.tan(np.deg2rad(bank_angle_deg)))
                self._setParameter("turn_radius", turn_radius)
                self._setCalculated("turn_radius", True)
                rate_of_turn = constants.g/velocity * np.rad2deg(np.tan(np.deg2rad(bank_angle_deg)))
                self._setParameter("rate_of_turn", rate_of_turn)
                self._setCalculated("rate_of_turn", True)
        elif parameter == "flight_path_angle":
            if not self.getParameter("velocity")['value'] is None:
                console.print("got here")
                velocity = self.getParameter("velocity")['value']
                fpa = self.getParameter("flight_path_angle")['value']
                load_factor = np.cos(np.deg2rad(fpa))
                self._setParameter("load_factor", load_factor)
                self._setCalculated("load_factor", True)
                roc = velocity*np.sin(np.deg2rad(fpa))
                self._setParameter("rate_of_climb", roc)
                self._setCalculated("rate_of_climb", True)
        elif parameter == "rate_of_climb":
            if not self.getParameter("velocity")['value'] is None:
                velocity = self.getParameter("velocity")['value']
                roc = self.getParameter("rate_of_climb")['value']
                fpa = np.asin(roc/velocity)
                self._setParameter("flight_path_angle", np.rad2deg(fpa))
                self._setCalculated("flight_path_angle", True)
                load_factor = np.cos(fpa)
                self._setParameter("load_factor", load_factor)
                self._setCalculated("load_factor", True)




        
        #TODO: Improve this system here
        if all(not (self.getParameter(param)['value'] is None) for param in ["velocity","density","dynamic_viscosity"]): #Auto-calculate Reynold's number
            refs = config.getReferenceQuantities()
            refChord = refs["refChord"]
            Recalc = self.getParameter("velocity")['value'] * refChord * self.getParameter("density")['value'] / self.getParameter("dynamic_viscosity")['value']
            console.print(f"{self._prefix} Reynolds number computed using reference chord {refChord} m")
            console.print(f"{self._prefix} Reynolds number set to '{Recalc}'. Override with 'Rec <value>'")
            self._setParameter("Re", Recalc)
            self._setCalculated("Re", True)
        if all(not (self.getParameter(param)['value'] is None) for param in ["velocity","speed_of_sound"]): #Auto-calculate Mach number
            Mach = self.getParameter("velocity")['value'] / self.getParameter("speed_of_sound")['value']
            console.print(f"{self._prefix} Mach number computed using speed of sound {self.getParameter('speed_of_sound')['value']} m/s")
            console.print(f"{self._prefix} Mach number set to '{Mach}'. Override with 'Mach <value>'")
            self._setParameter("Mach", Mach)
            self._setCalculated("Mach", True)
        if self.settings['type'] == "turn" and self.getParameter("bank_angle")['value'] is not None:
            bank_angle_rad = np.deg2rad(self.getParameter("bank_angle")['value'])
            load_factor = 1 / np.cos(bank_angle_rad)
            self._setParameter("load_factor", load_factor)
            self._setCalculated("load_factor", True)
        """
        if self.getParameter("rate_of_climb") is not None and self.getParameter("velocity") is not None:
            pass
            velocity = self.getParameter("velocity")
            rate_of_climb = self.getParameter("rate_of_climb")
            flight_path_angle_rad = np.arcsin(rate_of_climb / velocity)
            flight_path_angle_deg = np.degrees(flight_path_angle_rad)
            self._setParameter("flight_path_angle", flight_path_angle_deg)
            self._setCalculated("flight_path_angle", True)
            console.print(f"{self._prefix} Flight path angle computed using rate of climb {rate_of_climb} m/s and velocity {velocity} m/s")
            console.print(f"{self._prefix} Flight path angle set to '{flight_path_angle_deg}'. Override with 'flight_path_angle <value>'")
        """
        

        self.modifiedSinceLastExec = True
        return True

    def setVariable(self, variable, value):
        if variable in self.inputs:
            self.inputs[variable]["value"] = float(value)
            self.inputs[variable]["driver"] = "fixed"
            self.modifiedSinceLastExec = True
            return True
        elif variable in self.outputs:
            if value == "free":
                #TODO: check if the variable can be auto calculated otherwise fre
                self.outputs[variable]["value"] = None
                self.outputs[variable]["driver"] = "free"
            else:
                self.outputs[variable]["value"] = float(value)
                self.outputs[variable]["driver"] = "fixed"
            if not self.isDriven(variable):
                console.print(f"{self._prefix} Warning: Outputs cannot be arbitrarily chosen and must be driven by at least one input.")
            self.modifiedSinceLastExec = True
            return True
        elif variable in self.controls:
            self.controls[variable]["value"] = float(value)
            self.controls[variable]["driver"] = "fixed"
            self.modifiedSinceLastExec = True
            return True
        else:
            console.print(f"{self._prefix} Invalid variable name.")
            return False
        
    def driveVariable(self, variable, driver, value):
        if not (variable in self.inputs) and not (variable in self.controls):   
            console.print(f"{self._prefix} Invalid variable/control name.")
            return False
        if not driver in self.outputs:
            console.print(f"{self._prefix} Invalid driver name.")
            return False
        if variable in self.inputs:
            if value == "auto":
                if self.autoCalc(driver): #Check if the output can be auto-calculated
                    self.inputs[variable]["value"] = None #Updates the input parameter as driven
                    self.inputs[variable]["driver"] = driver
                    self.outputs[driver]["driver"] = "fixed"
                    console.print(f"{self._prefix} {variable} driven by {driver} with value {value}")
                    self.modifiedSinceLastExec = True
                    return True
                else:
                    console.print(f"{self._prefix} Cannot auto-calculate {driver}.")
                    return False
            else:
                self.inputs[variable]["value"] = None #Updates the input parameter as driven
                self.inputs[variable]["driver"] = driver
                self.outputs[driver]["value"] = float(value)
                self.outputs[driver]["driver"] = "fixed"
                console.print(f"{self._prefix} {variable} driven by {driver} with value {value}")
            self.modifiedSinceLastExec = True
            return True
        elif variable in self.controls:
            if value == "auto":
                if self.autoCalc(driver): #Check if the output can be auto-calculated
                    self.controls[variable]["value"] = None #Updates the input parameter as driven
                    self.controls[variable]["driver"] = driver
                    self.outputs[driver]["driver"] = "fixed"
                    console.print(f"{self._prefix} {variable} driven by {driver} with value {value}")
                    self.modifiedSinceLastExec = True
                    return True
                else:
                    console.print(f"{self._prefix} Cannot auto-calculate {driver}.")
                    return False
            else:
                self.controls[variable]["value"] = None
                self.controls[variable]["driver"] = driver
                self.outputs[driver]["value"] = float(value)
                self.outputs[driver]["driver"] = "fixed"
                console.print(f"{self._prefix} {variable} driven by {driver} with value {value}")
                self.modifiedSinceLastExec = True
                return True
    
    def autoCalc(self, output):
        """Update the operating point"""
        # Check if an output can be auto-calculated (just CL really)
        # TODO: Are there other things that can be auto-calculated?
        if output == "CL":
            if all(not (self.getParameter(param)['value'] is None) for param in ["velocity","density","massconfig_index", "load_factor"]): #Auto-calculate CL
                refs = config.getReferenceQuantities()
                refArea = refs["refArea"]
                totalmass = config.getMassConfiguration(self.getParameter("massconfig_index")['value']).mass
                CL = 2 * totalmass * self.getParameter("load_factor")['value'] * constants.g / (self.getParameter("velocity")['value'] ** 2 * refArea * self.getParameter("density")['value'])
                self.outputs["CL"]["value"] = CL
                console.print(f"{self._prefix} Calculated CL: {CL:.3f}")
                return True
        
        return False

    def analyzeStability(self):
        if not self.hasResults:
            console.print(f"{self._prefix} Operating point '{self.name}' has no results to analyze.")
            return False
    
        #Dimensionalize quantities

        q_inf = 0.5 * self.getParameter("density")['value'] * self.getParameter("velocity")['value'] ** 2
        refArea = config.getReferenceQuantities()["refArea"]
        refSpan = config.getReferenceQuantities()["refSpan"]
        refChord = config.getReferenceQuantities()["refChord"]
        # Print out in table form
        console.print(f"{self._prefix} Operating Point '{self.name}' Stability Analysis:")
        refstable = Table(show_header=False, header_style="bold magenta", box=None, title="Reference Quantities")
        refstable.add_column("Parameter", style="cyan", no_wrap=True)
        refstable.add_column("Value", style="magenta", no_wrap=True)
        refstable.add_row("q_inf", f"{q_inf:.3f} Pa")
        refstable.add_row("Sref", f"{refArea:.3f} m^2")
        refstable.add_row("bref", f"{refSpan:.3f} m")
        refstable.add_row("cref", f"{refChord:.3f} m")
        refstable.add_row("X_NP", f"{self.results['stability']['X_NP']:.3f} m")

        # Pull out static and dynamic derivatives and evaluate them
        # Cm alpha, Cmq, Cn beta, Cn r, C l p
        nd_derivs_modified = self.results["stability"]["derivs_body_axes"].copy().drop(columns=["Mach"])
        # Convert alpha, beta, p, q, r, derivatives to per radian from per degree
        # THEYRE DERIVATVES SO THEY LOOK LIKE THEYRE BEING CONVERTED BACKWARDS!!!!

        nd_derivs_modified["W"] = nd_derivs_modified["alpha"] / self.getParameter("velocity")['value'] #create w-derivative
        nd_derivs_modified["V"] = nd_derivs_modified["beta"] / self.getParameter("velocity")['value'] #create v-derivative

        Cm_alpha = self.results['stability']['derivs_stability_axes'].loc['Cm', 'alpha']
        Cm_q = self.results['stability']['derivs_stability_axes'].loc['Cm', 'q']
        Cn_beta = self.results['stability']['derivs_stability_axes'].loc['Cn', 'beta']
        Cl_beta = self.results['stability']['derivs_stability_axes'].loc['Cl', 'beta']
        Cn_r = self.results['stability']['derivs_stability_axes'].loc['Cn', 'r']
        Cl_p = self.results['stability']['derivs_stability_axes'].loc['Cl', 'p']
        Cl_r = self.results['stability']['derivs_stability_axes'].loc['Cl', 'r']


        def rating(quantity, lower, higher):
            if quantity < lower:
                perc = 0
            elif quantity > higher:
                perc = 100
            else:
                perc = 100*(1 - np.exp(-2*quantity / (higher-lower)))

            color = f"rgb({int(min(255, 2 * 255 * (100 - perc)/100))},{int(min(255, 2 * 255 * (perc/100)))},0)"
            #color = "green" if perc > 70 else "yellow" if perc > 25 else "red"
            return f"[{color}]{'█' * max(int(perc/4), 1)}[/{color}]"
        
        def ratingColor(quantity, lower, higher):
            if quantity < lower:
                perc = 0
            elif quantity > higher:
                perc = 100
            else:
                perc = 100*(1 - np.exp(-2*quantity / (higher-lower)))

            return f"rgb({int(min(255, 2 * 255 * (100 - perc)/100))},{int(min(255, 2 * 255 * (perc/100)))},0)"


        stabtable = Table(show_header=False, header_style="bold magenta", box=None, title="Stability Derivatives (1/rad)", title_justify="center")
        stabtable.add_column("Derivative", style="cyan", no_wrap=True)
        stabtable.add_column("Value", style="magenta", no_wrap=True)
        stabtable.add_column("Expected Range", style="green", no_wrap=True)
        stabtable.add_column("Rating", no_wrap=True)
        stabtable.add_row("Static Margin", f"{self.results['stability']['SM']*100:.1f}%", "10% ~ 30%", rating(self.results['stability']['SM'], 0.1, 0.3),  style=ratingColor(self.results['stability']['SM'], 0.1, 0.3))
        stabtable.add_row("Cm alpha", f"{Cm_alpha:.3f}", "-1.5 ~ -0.3", rating(-Cm_alpha, 0.3, 1), style=ratingColor(-Cm_alpha, 0.3, 1))
        stabtable.add_row("Cm q", f"{Cm_q:.3f}", "-40 ~ -5", rating(-Cm_q, 5, 40), style=ratingColor(-Cm_q, 5, 40))
        stabtable.add_row("Cn beta", f"{Cn_beta:.3f}", "0.05 ~ 0.4", rating(Cn_beta, 0.05, 0.4), style=ratingColor(Cn_beta, 0.05, 0.4))
        stabtable.add_row("Cn r", f"{Cn_r:.3f}", "-1 ~ -0.1", rating(-Cn_r, 0.1, 1), style=ratingColor(-Cn_r, 0.1, 1))
        stabtable.add_row("Cl beta", f"{Cl_beta:.3f}", "< 0", rating(-Cl_beta, 0, 0.2), style=ratingColor(-Cl_beta, 0, 0.2))
        stabtable.add_row("Cl p", f"{Cl_p:.3f}", "< -0.2", rating(-Cl_p, 0.2, 0.4), style=ratingColor(-Cl_p, 0.2, 0.4))
        stabtable.add_row("Cl r", f"{Cl_r:.3f}", "> 0.1", rating(-Cl_r, 0.1, 0.3), style=ratingColor(-Cl_r, 0.1, 0.3))

        modes_table = self._calculateDynamicModes()


        console.print(Padding(Columns([refstable, stabtable, modes_table], padding=(0, 0, 0, 4)), (0, 0, 0, 8)))

        #console.print(f"{self._prefix} Modified non-dimensional derivatives:")
        #console.print(nd_derivs_modified)

        fpa = 0 if not self.getParameter('flight_path_angle') else self.getParameter('flight_path_angle')['value']

        console.print(f"{self._prefix} FPA: {fpa}")
        console.print(f"{self._prefix} Alpha: {self.results['stability']['final_inputs'].loc[0, 'alpha']}")
        theta0 = np.deg2rad(fpa + self.results['stability']['final_inputs'].loc[0, 'alpha'])
        console.print(f"{self._prefix} Body-Angle theta: {np.degrees(theta0):.3f} degrees")

    def _calculateDynamicModes(self):
        rho = self.getParameter("density")['value']
        u0 = self.getParameter("velocity")['value']
        q_inf = 0.5 * self.getParameter("density")['value'] * self.getParameter("velocity")['value'] ** 2
        refArea = config.getReferenceQuantities()["refArea"]
        refSpan = config.getReferenceQuantities()["refSpan"]
        refChord = config.getReferenceQuantities()["refChord"]
        Cw0 = config.getMassConfiguration(self.getParameter("massconfig_index")['value']).mass * constants.g / (q_inf * refArea)

        CD0 = self.results['stability']['base_case_stability_axes'].loc[0, 'CD']
        CL0 = self.results['stability']['base_case_stability_axes'].loc[0, 'CL']

        fpa = 0 if not self.getParameter('flight_path_angle') else self.getParameter('flight_path_angle')['value']
        theta0 = np.deg2rad(fpa + self.results['stability']['final_inputs'].loc[0, 'alpha']) #Body angle

        CT0 = CD0 + Cw0*np.sin(theta0)
        CTu = -3*CT0
        #console.print(f"{self._prefix} CT0: {CT0}, CTu: {CTu}")
        CDu = self.results['stability']['derivs_stability_axes'].loc['CD', 'U']
        CL_u = self.results['stability']['derivs_stability_axes'].loc['CL', 'U']

        CD_alpha = self.results['stability']['derivs_stability_axes'].loc['CD', 'alpha']
        CL_alpha = self.results['stability']['derivs_stability_axes'].loc['CL', 'alpha']
        CLq = self.results['stability']['derivs_stability_axes'].loc['CL', 'q']
        Cmu = self.results['stability']['derivs_stability_axes'].loc['Cm', 'U']
        Cmalpha = self.results['stability']['derivs_stability_axes'].loc['Cm', 'alpha']
        Cmq = self.results['stability']['derivs_stability_axes'].loc['Cm', 'q']

        # TODO: Do something about this
        CL_alphadot = 0 
        Cm_alphadot = 0

        Xu = (1/2)*rho*u0*refArea*(2*(-CD0+CT0) + (-CDu + CTu))
        Xw = (1/2)*rho*u0*refArea*(-CD_alpha + CL0)
        Zu = (1/2)*rho*u0*refArea*(-2*CL0 - CL_u)
        Zw = (1/2)*rho*u0*refArea*(-CD0 - CL_alpha)
        Zq = (1/4)*rho*u0*refChord*refArea*(-CLq)
        Zwdot = (1/4)*rho*refChord*refArea*(-CL_alphadot)
        Mu = (1/2)*rho*u0*refChord*refArea*Cmu
        Mw = (1/2)*rho*u0*refChord*refArea*Cmalpha
        Mq = (1/4)*rho*u0*(refChord**2)*refArea*Cmq
        Mwdot = (1/4)*rho*(refChord**2)*refArea*Cm_alphadot

        g = constants.g
        m = config.getMassConfiguration(self.getParameter("massconfig_index")['value']).mass
        Iy = config.getMassConfiguration(self.getParameter("massconfig_index")['value']).inertia_matrix[1,1]

        AL = [
                [Xu/m,         Xw/m,         0,                     -g*np.cos(theta0)],
                [Zu/(m-Zwdot), Zw/(m-Zwdot), (Zq + m*u0)/(m-Zwdot), -(m*g*np.sin(theta0))/(m-Zwdot)],
                [(Mu + (Mwdot*Zu)/(m-Zwdot))/Iy, (Mw + (Mwdot*Zw)/(m-Zwdot))/Iy, (Mq + (Mwdot*(Zq+m*u0))/(m-Zwdot))/Iy, ((Mwdot*(-m*g*np.sin(theta0)))/(m-Zwdot))/Iy],
                [0, 0, 1, 0]
             ]
        
        #Lateral stability
        CYbeta = self.results['stability']['derivs_stability_axes'].loc['CY', 'beta']
        CYp = self.results['stability']['derivs_stability_axes'].loc['CY', 'p']
        CYr = self.results['stability']['derivs_stability_axes'].loc['CY', 'r']
        Clbeta = self.results['stability']['derivs_stability_axes'].loc['Cl', 'beta']
        Clp = self.results['stability']['derivs_stability_axes'].loc['Cl', 'p']
        Clr = self.results['stability']['derivs_stability_axes'].loc['Cl', 'r']
        Cnbeta = self.results['stability']['derivs_stability_axes'].loc['Cn', 'beta']
        Cnp = self.results['stability']['derivs_stability_axes'].loc['Cn', 'p']
        Cnr = self.results['stability']['derivs_stability_axes'].loc['Cn', 'r']
        
        Yv = (1/2)*rho*u0*refArea*CYbeta
        Yp = (1/4)*rho*u0*refSpan*refArea*CYp
        Yr = (1/4)*rho*u0*refSpan*refArea*CYr
        Lv = (1/2)*rho*u0*refSpan*refArea*Clbeta
        Lp = (1/4)*rho*u0*(refSpan**2)*refArea*Clp
        Lr = (1/4)*rho*u0*(refSpan**2)*refArea*Clr
        Nv = (1/2)*rho*u0*refSpan*refArea*Cnbeta
        Np = (1/4)*rho*u0*(refSpan**2)*refArea*Cnp
        Nr = (1/4)*rho*u0*(refSpan**2)*refArea*Cnr

        Ix = config.getMassConfiguration(self.getParameter("massconfig_index")['value']).inertia_matrix[0,0]
        Iz = config.getMassConfiguration(self.getParameter("massconfig_index")['value']).inertia_matrix[2,2]
        Ixz = config.getMassConfiguration(self.getParameter("massconfig_index")['value']).inertia_matrix[0,2]
        xi = Ix*Iz-Ixz**2

        ALD = [
                [Yv/m, Yp/m, (Yr/m - u0), g*np.cos(theta0)],
                [(1/xi)*(Iz*Lv + Ixz*Nv), (1/xi)*(Iz*Lp + Ixz*Np), (1/xi)*(Iz*Lr + Ixz*Nr), 0],
                [(1/xi)*(Ixz*Lv + Ix*Nv), (1/xi)*(Ixz*Lp + Ix*Np), (1/xi)*(Ixz*Lr + Ix*Nr), 0],
                [0, 1, np.tan(theta0), 0]
               ]

        eigenvaluesL, eigenvectorsL = np.linalg.eig(AL)
        eigenvaluesLD, eigenvectorsD = np.linalg.eig(ALD)

        modes_table = Table(show_header=True, header_style="bold magenta", box=None, title="Dynamic Modes")
        modes_table.add_column("Mode", style="cyan", no_wrap=True)
        modes_table.add_column("λ", style="magenta", no_wrap=True)
        modes_table.add_column("ωd (Hz)", style="magenta", no_wrap=True)
        modes_table.add_column("ωn (Hz)", style="magenta", no_wrap=True)
        modes_table.add_column("ζ", style="magenta", no_wrap=True)
        modes_table.add_column("τ (s)", style="magenta", no_wrap=True)
        modes_table.add_column("Type", style="magenta", no_wrap=True)
        """
            For longitudinal modes:1
                - bigger magnitude complex pair: short period
                - smaller magnitude complex pair: phugoid
        """
        sorted_eigs_L = sorted(eigenvaluesL, key=lambda x: abs(x), reverse=True)

        # Process short period mode
        short_period = sorted_eigs_L[:2]
        sp_wd = np.abs(np.imag(short_period[0])) # rad/s
        sp_wn = np.abs(short_period[0]) # rad/s
        sp_zeta = -np.real(short_period[0])/np.abs(short_period[0])
        sp_timehalf = np.log(2)/np.abs(np.real(short_period[0])) # s
        if sp_wd >= 1 and 0.35 < sp_zeta < 1.3:
            sp_level = "I"
            sp_color = "green"
        elif sp_wd >= 0.6 and 0.25 < sp_zeta < 2.0:
            sp_level = "II"
            sp_color = "yellow"
        elif 0.15 < sp_zeta < 0.7:
            sp_level = "III"
            sp_color = "dark_orange3"
        else:
            sp_level = ":warning:"
            sp_color = "red"
        modes_table.add_row("Short Period", f"{short_period[0]:.2f}", f"{sp_wd/(2*np.pi):.2f}", f"{sp_wn/(2*np.pi):.2f}", f"{sp_zeta:.2f}", f"{sp_timehalf:.2f}", sp_level, style = sp_color)
        
        # Process phugiod mode
        phugoid = sorted_eigs_L[2:]
        ph_wd = np.abs(np.imag(phugoid[0])) # rad/s
        ph_wn = np.abs(phugoid[0]) # rad/s
        ph_zeta = -np.real(phugoid[0])/np.abs(phugoid[0])
        ph_timehalf = np.log(2)/np.abs(np.real(phugoid[0])) # s
        if ph_zeta > 0.04:
            ph_level = "I"
            ph_color = "green"
        elif ph_zeta > 0:
            ph_level = "II"
            ph_color = "yellow"
        elif ph_timehalf >= 55:
            ph_level = "III"
            ph_color = "dark_orange3"
        else:
            ph_level = ":warning:"
            ph_color = "red"
        modes_table.add_row("Phugoid", f"{phugoid[0]:.2f}", f"{ph_wd/(2*np.pi):.2f}", f"{ph_wn/(2*np.pi):.2f}", f"{ph_zeta:.2f}", f"{ph_timehalf:.2f}", ph_level, style = ph_color)

        #Process spiral mode
        sorted_eigns_LD = sorted(eigenvaluesLD, key = lambda x: abs(x))
        spiral = sorted_eigns_LD.pop(0) # Usually the smallest eigenvalue, and real
        sr_timehalf = np.log(2)/np.abs(np.real(spiral)) # s
        if sr_timehalf > 12:
            spiral_level = "I"
            spiral_color = "green"
        elif sr_timehalf > 8:
            spiral_level = "II"
            spiral_color = "yellow"
        elif sr_timehalf > 4:
            spiral_level = "III"
            spiral_color = "dark_orange3"
        else:
            spiral_level = ":warning:"
            spiral_color = "red"
        modes_table.add_row("Spiral", f"{spiral:.2f}", "--", "--", "--", f"{sr_timehalf:.2f}", spiral_level, style = spiral_color)

        # Find the pure real eigenvalue that's left -> roll mode
        for i, eig in enumerate(sorted_eigns_LD):
            if np.isreal(eig):
                roll = sorted_eigns_LD.pop(i)
                break
        
        roll_timehalf = np.log(2)/np.abs(np.real(roll)) # s
        roll_timeconst = 1/np.abs(np.real(roll))
        if roll_timeconst < 1.0 and np.real(roll) < 0:
            roll_level = "I"
            roll_color = "green"
        elif roll_timeconst < 1.4 and np.real(roll) < 0:
            roll_level = "II"
            roll_color = "yellow"
        elif roll_timeconst < 10 and np.real(roll) < 0:
            roll_level = "III"
            roll_color = "dark_orange3"
        else:
            roll_level = ":warning:"
            roll_color = "red"
        modes_table.add_row("Roll", f"{roll:.2f}", "--", "--", "--", f"{roll_timehalf:.2f}", roll_level, style = roll_color)

        # Process dutch roll
        dutch_roll = sorted_eigns_LD[0]
        dr_wd = np.abs(np.imag(dutch_roll))
        dr_wn = np.abs(dutch_roll)
        dr_zeta = -np.real(dutch_roll)/np.abs(dutch_roll)
        dr_timehalf = np.log(2)/np.abs(np.real(dutch_roll))
        if (dr_wn*dr_zeta) > 0.4 and dr_zeta > 0.04 and dr_wn > 1:
            dr_level = "I"
            dr_color = "green"
        elif (dr_wn*dr_zeta) > 0.05 and dr_zeta > 0.02 and dr_wn > 0.4:
            dr_level = "II"
            dr_color = "yellow"
        elif dr_zeta > 0 and dr_wn > 0.4:
            dr_level = "III"
            dr_color = "dark_orange3"
        else:
            dr_level = ":warning:"
            dr_color = "red"
        modes_table.add_row("Dutch Roll", f"{dutch_roll:.2f}", f"{dr_wd/(2*np.pi):.2f}", f"{dr_wn/(2*np.pi):.2f}", f"{dr_zeta:.2f}", f"{dr_timehalf:.2f}", dr_level, style=dr_color)


        # Create the plot
        fig, ax = plt.subplots()

        # Plot eigenvalues in the complex plane
        ax.scatter(eigenvaluesL.real, eigenvaluesL.imag, color='b', label='Eigenvalues Longitudinal')
        ax.scatter(eigenvaluesLD.real, eigenvaluesLD.imag, color='r', label='Eigenvalues Lateral')

        # Plot axes
        ax.axhline(0, color='black', linestyle='--', linewidth=0.5)
        ax.axvline(0, color='black', linestyle='--', linewidth=0.5)

        # Labels and title
        ax.set_xlabel('Real Axis')
        ax.set_ylabel('Imaginary Axis')
        ax.set_title('Eigenvalue Plot')
        ax.legend()
        ax.grid(True)

        # Show the plot
        plt.show(block=False)
        plt.savefig('eigs.png')

        return modes_table

    @classmethod
    def from_dict(cls, data):
        op = cls(data["name"], data["settings"]["type"])
        op.settings = data["settings"]
        op.generic_parameters = data["genparms"]
        op.freestream_parameters = data["fsparms"]
        op.type_parameters = data["tparms"]
        op.inputs = data['inputs']
        op.outputs = data['outputs']
        op.controls = data['controls']
        op.isConverged = data['isConverged']
        op.hasResults = data['hasResults']
        op.modifiedSinceLastExec = data['modifiedSinceLastExec']
        op.results = OperatingPoint.results_from_dict(data['results'])
        return op
    
    @classmethod
    def results_from_dict(cls, results_dict):
        """
        Convert a dictionary back into the original results structure, including DataFrames and nested dictionaries.
        
        Parameters:
            results_dict (dict): Dictionary with DataFrames as dictionaries.

        Returns:
            dict: Original results structure with DataFrames restored.
        """
        if results_dict == None:
            return None
        def convert(value):
            if isinstance(value, dict) and "data" in value and "columns" in value:  # Check for DataFrame-like dictionary
                return pd.DataFrame(**value)  # Convert back to DataFrame
            elif isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}  # Recursively convert nested dictionaries
            else:
                return value  # Scalars remain unchanged

        return {key: convert(val) for key, val in results_dict.items()}
    
    @classmethod
    def new(cls):
        """Walk user through creating a new operating point"""
        types = cls._OPERATING_POINT_TEMPLATES.keys()
        #Choose operating point name
        input_name = console.input(f"{cls._prefix} Enter operating point name: ")
        if input_name == "":
            console.print(f"{cls._prefix} Cancelled.")
            return False

        # Choose operating point type
        console.print(f"{cls._prefix} Choose operating point type:")
        table = Table(box=None, show_header=False)
        table.add_column("Name", style="blue")
        table.add_column("Desc", style="green")
        for key, val in cls._OPERATING_POINT_TEMPLATES.items():
            table.add_row(f"{key}", f"{val['description']}")
        indented_table = Padding(table, pad=[0,0,0,12])
        console.print(indented_table)
        while True:
            input_type = console.input(f"{cls._prefix} Enter type name: ")
            if input_type == "":
                console.print(f"{cls._prefix} Cancelled.")
                return False
            if input_type in cls._OPERATING_POINT_TEMPLATES.keys():
                type = input_type
                break

        console.print(f"{cls._prefix} Creating operating point with name '{input_name}' and type '{input_type}' ...", end="")
        op = OperatingPoint(name=input_name, type=input_type)
        console.print(f" Done.")
        console.print(f"{cls._prefix} Initializing parameter dictionaries ...", end="")
        op.initialize_parameter_dictionaries()
        console.print(" Done. ")
        console.print(f"{cls._prefix} Initializing IOC dictionaries ...", end="")
        op.initialize_IOC()
        console.print(f" Done. Found {len(op.controls.keys())} control groups.")
        return op

    def initialize_parameter_dictionaries(self):
        type = self.settings["type"]
        self.freestream_parameters = self._freestream_parameters_defaults.copy()
        self.generic_parameters = self._generic_parameters_defaults.copy()
        self.type_parameters = self._OPERATING_POINT_TEMPLATES[type]["required_parameters"].copy()

    def initialize_IOC(self): #better to initialize by type and auto-apply constraints
        self.inputs = {
            "alpha":{
                "value": 0.0,
                "driver":"fixed"
            },
            "beta":{
                "value": 0.0,
                "driver":"fixed"
            }
        }
        self.outputs = {
            "CL": {
            "value": None,
            "driver": "free"
            },
            "CY": {
            "value": None,
            "driver": "free"
            },
            "Cl": {
            "value": None,
            "driver": "free"
            },
            "Cm": {
            "value": None,
            "driver": "free"
            },
            "Cn": {
            "value": None,
            "driver": "free"
            }
        }
        self.controls = {}
        controls_data = config.getControls()
        for group_name in controls_data.keys():
            self.controls[group_name] = {
                "value": 0.0,
                "driver": "fixed",
                "details": controls_data[group_name]
            }

        if self.settings['type'] == "cruise":
            self.updateParameter("load_factor", 1)