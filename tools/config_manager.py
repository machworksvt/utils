import json
import os
from pathlib import Path
from rich.console import Console
import openvsp as vsp
import pandas as pd
import numpy as np

console = None

class ConfigurationManager:
    """Manages configuration of the program"""

    _instance = None
    _prefix = "[bold cyan]\t<config>[/bold cyan]"
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
            "type":"IV"
        }
        self.operating_points = []
        self.isLoaded = False
        self.massConfigurations = []
        self.powerplant = None

    # Import/export configuration
    def to_dict(self):
        """Export configuration as dictionary."""
        return {
            "vsp3_file": self.vsp3_file,
            "settings": self.settings,
            #"operating_points": [op.to_dict() for op in self.operating_points],
            "massConfigurations": [mc.to_dict() for mc in self.massConfigurations],
        }

    def from_dict(self, data):
        """Load configuration from a dictionary."""
        self.vsp3_file = data.get("vsp3_file")
        self.settings.update(data.get("settings", {}))
        #self.operating_points = [OperatingPoint.from_dict(op) for op in data.get("operating_points", [])]
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
        self.operating_points.append(op)
    
    def getControls():
        vsp.GetNumControlSurfaceGroups

    #Mass part
    def addMassConfiguration(self, massConfig):
        self.massConfigurations.append(massConfig)
        console.print(f"\t{self._prefix} Mass configuration added")

    def removeMassConfiguration(self, idx):
        mconfig = self.massConfigurations.pop(idx)
        console.print(f"{self._prefix} Mass config {idx}, {mconfig.name} removed.")

    def getControls(self):
        console.print(f"{self._prefix} Getting control surface groups...")
        numgroups = vsp.GetNumControlSurfaceGroups()
        console.print(f"\tNumber of control surface groups: {numgroups}")
        controls = {}
        for i in range(numgroups):
            group_id = i
            group_name = vsp.GetVSPAEROControlGroupName(i)
            surface_names = vsp.GetActiveCSNameVec(group_id)
            num_surfaces = len(surface_names)
            controls[group_id] = {
                "id": group_id,
                "name": group_name,
                "num_surfaces": num_surfaces,
                "surface_names": surface_names
            }
        return controls



config = ConfigurationManager()

class PowerPlant:
    """Represents the turbojet powerplant of a vehicle"""

    #TODO: Implement

    _prefix = "[bold orange]\t<powerplant>[/bold orange]"

    def __init__(self, name="Powerplant"):
        self.name = name
        self.tsfc = 0
        self.tmax = 0

class MassConfiguration:
    """Represents the mass configuration of the vehicle"""

    _prefix = "[bold magenta]\t<mass>[/bold magenta]"


    def __init__(self, name="Mass Configuration", cg=[0.0, 0.0, 0.0], mass=0.0,inertia_matrix=np.zeros((3, 3))):
        self.name = name
        self.cg = cg
        self.mass = mass
        self.inertia_matrix = inertia_matrix

    def to_dict(self):
        """Serialize the mass configuration to a dictionary."""
        return {
            "name": self.name,
            "cg": self.cg.tolist(),
            "mass": self.mass,
            "inertia_matrix": self.inertia_matrix.tolist()
        }

    @classmethod
    def from_dict(cls, data):
        """Create a mass configuration from a dictionary."""
        return cls(
            name=data["name"],
            cg=data["cg"],
            mass=data["mass"],
            inertia_matrix=data["inertia_matrix"],
        )


    def __str__(self):
        return (f"MassConfiguration(name={self.name}, mass={self.mass:.2f}, cg={self.cg}, "
                f"inertia_matrix={self.inertia_matrix}")
        
class OperatingPoint:
    """Most generic definition of an operating point possible. Just enough to run a vspaero analysis"""

    TEMPLATE_TYPES = {
        "cruise": {"altitude", "velocity"}
    }

    _prefix = "[bold cyan]\t<op>[/bold cyan]"

    """
        TODO: create dicts of the template type cruise
            refine from_dict and to_dict function
    
    """

    def __init__(self, name, parameters=None):   
        self.name = name
        self.settings = {
            "stab": False,
            "dyn": False
        }
        self.parameters = parameters if not parameters is None else {
            "airspeed": None,
            "loadfac": None,
            "bank_angle": None,
            "altitude": None,
            "midx": None,
            "Rec": None,
            "Mach": None,
            "Rate of Climb": None,
            "Flight Path Angle": None,
            "Rate of Turn": None,
            "Density": None,
        }
        self.variables = {
            "alpha":0.0,
            "beta":0.0,
            "roll_rate":0.0,
            "pitch_rate":0.0,
            "yaw_rate":0.0,
            "CL":0.0,
            "CY":0.0,
            "Cl":0.0,
            "Cm":0.0,
            "Cn":0.0,
        }
        
        self.constraints = {}
        self.controls = config.getControls() #TODO: Implement

    
    def __str__(self):
        """Display operating point in readable format"""
        execString = "[executed]" if self.analysiscomplete else "[not executed]"
        return (f"'{self.name}': {execString}\n"
                f"\t\tAlpha (deg): {self.alpha}\n"
                f"\t\tBeta (deg): {self.beta}\n"
                f"\t\tMach: {self.Mach}\n"
                f"\t\tRe: {self.Re}\n")
    
    def isReady(self):
        """Check if the operating point is ready to be executed"""
        raise NotImplementedError
    
    def isGeometryComputed(self):
        """Check if the geometry has been computed"""
        raise NotImplementedError
    
    def computeGeometry(self):
        """Compute the geometry for the operating point"""
        raise NotImplementedError

    def exec(self):
        """Execute the operating point"""
        raise NotImplementedError

    def to_dict(self):
        return {
            "name": self.name,
            "settings": self.settings,
            "parameters": self.parameters,
            "variables": self.variables,
            "constraints": self.constraints
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            settings=data["settings"],
            parameters=data["parameters"],
            variables=data["variables"],
            constraints=data["constraints"]
        )