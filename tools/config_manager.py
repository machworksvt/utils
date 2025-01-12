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
import io
import sys
import psutil


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

    def getMassConfiguration(self, idx):
        return self.massConfigurations[idx] if 0 <= idx < len(self.massConfigurations) else None

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

    _prefix = "[bold orange]\t<powerplant>[/bold orange]"

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

    def __init__(self, name, settings=None, parameters=None, inputs=None, outputs=None, controls=None, hasResults=False, modifiedSinceLastExec=False, isConverged=False, results=None):   
        self.name = name
        self.settings = settings if not settings is None else {
            "max_iterations": 5,
            "tolerance": 1e-4
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
        """
            Inputs (incl controls) can be FIXED or DRIVEN
            Outputs can be DRIVERS/FIXED or FREE
        """
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
        self.geometryComputed = False
        self.isConverged = isConverged
        self.hasResults = hasResults
        self.modifiedSinceLastExec = modifiedSinceLastExec
        self.results = results

    def __str__(self):
        """Display operating point in readable format"""
        execString = "[executed]" if self.analysiscomplete else "[not executed]"
        return (f"'{self.name}': {execString}\n"
                f"\t\tAlpha (deg): {self.alpha}\n"
                f"\t\tBeta (deg): {self.beta}\n"
                f"\t\tMach: {self.Mach}\n"
                f"\t\tRe: {self.Re}\n")
    
    def print(self):
        """Print the operating point in a formatted manner to rich console"""
        titlestr = f"[bold] Operating Point: '{self.name}'"
        titlestr+=" >> " + ("[green]**READY**[/green]" if self.isReady() else "[red]**NOT READY**[/red]")
        titlestr+=" >> " + ("[green]**UNMODIFIED**[/green]" if not self.modifiedSinceLastExec else "[red]**MODIFIED**[/red]")
        titlestr+=" >> " + ("[green]**CONVERGED**[/green]" if self.isConverged else "[red]**NOT CONVERGED**[/red]")
        titlestr+=" >> " + ("[green]**RESULTS**[/green]" if self.hasResults else "[red]**NO RESULTS**[/red]")
        titlestr+="[/bold]"
        console.print(titlestr)


        #TODO: Create a separate thing for the mass configuration bc it doesn't really work like the rest of the parameters
        # Create Tables
        table1 = Table(title="Parameters")
        table1.add_column("Parameter", style="cyan")
        table1.add_column("Value", style="magenta")
        for key in self.parameters.keys():
            value = self.getParameter(key)
            if value is None:
                valprint = "---"
            elif key == "massconfig_index":
                valprint = f"{value}"
            elif 1e-3 < value < 1e4:
                valprint = f"{value:.3f}"
            else:
                valprint = f"{value:.3e}"
            if self._getCalculated(key):
                valprint = f"[yellow]{valprint}[/yellow]"
            table1.add_row(key, valprint)

        table2 = Table(title="Inputs")
        table2.add_column("Var", style="green")
        table2.add_column("--", style="yellow")
        table2.add_column("Driver", style="blue")
        for key, value in self.inputs.items():
            firstColumn = f"{key}"
            secondColumn = "==" if value["driver"] == "fixed" else "=>"
            thirdColumn = value["value"] if value["driver"] == "fixed" else value["driver"]
            table2.add_row(firstColumn, secondColumn, f"{thirdColumn}") #TODO implement driver

        for key, value in self.controls.items():
            firstColumn = f"{key}"
            secondColumn = "==" if value["driver"] == "fixed" else "=>"
            thirdColumn = value["value"] if value["driver"] == "fixed" else value["driver"]
            table2.add_row(firstColumn, secondColumn, f"{thirdColumn}")

        table3 = Table(title="Outputs")
        table3.add_column("Var", style="green")
        table3.add_column("--", style="yellow")
        table3.add_column("Value", style="green")
        for key, value in self.outputs.items():
            #either fixed or free
            firstColumn = f"{key}"
            secondColumn = "=="
            thirdColumn = value["value"] if value["driver"] == "fixed" else value["driver"]
            if value["driver"] == "fixed" and not self.isDriven(key):
                thirdColumn = f"[red]{thirdColumn}[/red]"
            table3.add_row(firstColumn, secondColumn, f"{thirdColumn}")


        if not self.parameters["massconfig_index"]["value"] is None:
            massConfig = config.getMassConfiguration(self.getParameter("massconfig_index"))
            table4 = Table(title="Mass Configuration")
            table4.add_column("Parameter", style="cyan")
            table4.add_column("Value", style="magenta")
            table4.add_row("Name", massConfig.name)
            table4.add_row("Mass (kg)", f"{massConfig.mass:.3f}")
            table4.add_row("CG (x, y, z) (m)", f"{massConfig.cg[0]:.3f}, {massConfig.cg[1]:.3f}, {massConfig.cg[2]:.3f}")
            table4.add_row("Inertia Matrix", f"{massConfig.inertia_matrix[0, 0]:.3f}, {massConfig.inertia_matrix[0, 1]:.3f}, {massConfig.inertia_matrix[0, 2]:.3f}")
            table4.add_row("", f"{massConfig.inertia_matrix[1, 0]:.3f}, {massConfig.inertia_matrix[1, 1]:.3f}, {massConfig.inertia_matrix[1, 2]:.3f}")
            table4.add_row("", f"{massConfig.inertia_matrix[2, 0]:.3f}, {massConfig.inertia_matrix[2, 1]:.3f}, {massConfig.inertia_matrix[2, 2]:.3f}")
            # Indent Tables
            indented_table1 = Padding(table1, (0, 0, 0, 8))
            indented_table2 = Padding(table2, (0, 0, 0, 4))
            indented_table3 = Padding(table3, (0, 0, 0, 4))
            indented_table4 = Padding(table4, (0, 0, 0, 4))

            # Print Tables Side by Side
            console.print(Columns([indented_table1, indented_table2, indented_table3, indented_table4]))
        else:
            # Indent Tables
            indented_table1 = Padding(table1, (0, 0, 0, 8))
            indented_table2 = Padding(table2, (0, 0, 0, 4))
            indented_table3 = Padding(table3, (0, 0, 0, 4))

            # Print Tables Side by Side
            console.print(Columns([indented_table1, indented_table2, indented_table3]))
    
    def isReady(self):
        """Check if the operating point is ready to be executed"""
        all(self.isDriven(output) for output in self.outputs.keys())
        return all([self.getParameter(key) is not None for key in self.parameters.keys()])
    
    def isDriven(self, output):
        """Check if an output is driven by an input"""
        return any([input_data["driver"] == output for input_data in self.inputs.values()]) or any([control_data["driver"] == output for control_data in self.controls.values()])

    def computeGeometry(self):
        #TODO: Improve this to handle errors, also eventually add panel method
        """Compute the geometry for the operating point"""
        analysisString = "VSPAEROComputeGeometry"
        console.print(f"{self._prefix} Computing geometry for operating point '{self.name}' ... ", end="")
        vsp.SetAnalysisInputDefaults(analysisString)
        vsp.SetIntAnalysisInput(analysisString, "AnalysisMethod", [vsp.VORTEX_LATTICE])
        vsp.SetIntAnalysisInput(analysisString, "GeomSet", [1])
        vsp.Update()
        allResults = vsp.ExecAnalysis(analysisString)
        outputFileName = vsp.GetStringResults(allResults, "DegenGeomFileName")[0]
        timeToComplete = vsp.GetDoubleResults(allResults, "Analysis_Duration_Sec")[0]
        console.print(f"Done in {timeToComplete:.2f} seconds. File saved as '{outputFileName}'")
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
            self._printResults()
            #Print some results
        else: #Trimming failed
            console.print(f"{self._prefix} Trimming failed. Adjust your settings or try again.")
            self.hasResults = False

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
            table.add_row(*[f"{val:.2f}" if pd.notna(val) else "..." for val in row.values])
        return table

    def _setInitialGuess(self):
        """Set initial guess for inputs with no value and initialize the history dataframe"""
        self._historyDF["Iteration"] = [0]
        self._historyDF["CompTime"] = [None]
        for key in self.inputs.keys():
            if self.inputs[key]["value"] is None:
                self._historyDF[key] = [self._referenceDict[key]["initial_guess"]]
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
        
        # Set static parameters
        vsp.SetIntAnalysisInput(analysisString, "GeomSet", [1])  # Use Set 0
        vsp.SetDoubleAnalysisInput(analysisString, "MachStart", [self.getParameter("Mach")])
        vsp.SetDoubleAnalysisInput(analysisString, "ReCref", [self.getParameter("Rec")]) 
        vsp.SetDoubleAnalysisInput(analysisString, "Vinf", [self.getParameter("velocity")])
        vsp.SetDoubleAnalysisInput(analysisString, "Vref", [self.getParameter("velocity")])
        vsp.SetDoubleAnalysisInput(analysisString, "Rho", [self.getParameter("density")])
        mconfig = config.getMassConfiguration(self.getParameter("massconfig_index"))
        vsp.SetDoubleAnalysisInput(analysisString, "Xcg", [mconfig.cg[0]])
        vsp.SetDoubleAnalysisInput(analysisString, "Ycg", [mconfig.cg[1]])
        vsp.SetDoubleAnalysisInput(analysisString, "Zcg", [mconfig.cg[2]])


        vsp.SetStringAnalysisInput(analysisString, "RedirectFile", [""])

        vsp.SetIntAnalysisInput(analysisString, "AnalysisMethod", [vsp.VORTEX_LATTICE])
        vsp.SetIntAnalysisInput(analysisString, "NCPU", [config.settings["num_procs"]])
        vsp.SetIntAnalysisInput(analysisString, "UnsteadyType", [vsp.STABILITY_DEFAULT])
        vsp.SetIntAnalysisInput(analysisString, "2DFEMFlag", [0])


        # Set inputs that change from iteration to iteration
        vsp.SetDoubleAnalysisInput(analysisString, "AlphaStart", [self._getNextInput("alpha")])
        vsp.SetDoubleAnalysisInput(analysisString, "BetaStart", [self._getNextInput("beta")])
        control_group_settings_container = vsp.FindContainer("VSPAEROSettings",0)
        for key in self.controls.keys():
            #need to get ID of control group
            group_id = self.controls[key]["details"]["id"]
            deflection_angle_id = vsp.FindParm(control_group_settings_container, "DeflectionAngle", f"ControlSurfaceGroup_{group_id}")
            vsp.SetParmVal(deflection_angle_id, self._getNextInput(key))

        #TODO: There are so many more inputs I can set. need to investigate further
        #TODO: Can add multiple levels of fidelity depending on how far from convergence we are (currently does not need to be so high)
        
        #Actually run VSPAERO
        try:
            self._recentResultID = vsp.ExecAnalysis("VSPAEROSweep")
        except Exception as e:
            console.print(f"{self._prefix} Error during simulation: {e}")
            self._recentResultID = None
 
    def _processTrimResults(self):
        """Process the stability results"""
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
        base_case_stability_axes = pd.DataFrame(columns=[*self.outputs.keys()], dtype=float)
        for col in base_case_stability_axes.columns:
            result_name = f"{prefix}_{self._getVSPAEROName(col)}"
            result_value = float(vsp.GetDoubleResults(stab_results_id, result_name)[0])
            base_case_stability_axes.loc[0, col] = result_value

        base_case_body_axes = pd.DataFrame(columns=["CFx", "CFy", "CFz", "CMx", "CMy", "CMz"])
        for col in base_case_body_axes.columns:
            result_name = f"{prefix}_{col}"
            result_value = float(vsp.GetDoubleResults(stab_results_id, result_name)[0])
            base_case_body_axes.loc[0, col] = result_value
        
        #Pull derivatives matrix (stability axes)
        derivs_stability_axes = pd.DataFrame(columns=[*self.inputs.keys(), *self.controls.keys(), "p", "q", "r", "U", "Mach"], index=[*self.outputs.keys()], dtype=float)
        for input in derivs_stability_axes.columns:
            for i, output in enumerate(self.outputs.keys()):
                derivativename = f"{self._getVSPAEROName(output)}_{self._getVSPAEROName(input)}"
                #console.print(f"{derivativename}")
                if not (input == "U" or input == "Mach"):
                    derivs_stability_axes.loc[output, input] = np.deg2rad(vsp.GetDoubleResults(stab_results_id, derivativename)[0])
                else:
                    derivs_stability_axes.loc[output, input] = float(vsp.GetDoubleResults(stab_results_id, derivativename)[0])

        derivs_body_axes = pd.DataFrame(columns=[*self.inputs.keys(), *self.controls.keys(), "p", "q", "r", "U", "Mach"], index=["CFx", "CFy", "CFz", "CMx", "CMy", "CMz"], dtype=float)
        for input in derivs_body_axes.columns:
            for output in derivs_body_axes.index:
                derivativename = f"{output}_{self._getVSPAEROName(input)}"
                #console.print(f"{derivativename}")
                if not (input == "U" or input == "Mach"):
                    derivs_body_axes.loc[output, input] = np.deg2rad(vsp.GetDoubleResults(stab_results_id, derivativename)[0])
                else:
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
            "parameters": self.parameters,
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
        if parameter in self.parameters:
            return self.parameters[parameter]["value"]
        else:
            console.print(f"{self._prefix} Invalid parameter name.")

    def _setParameter(self, parameter, value):
        if parameter in self.parameters:
            self.parameters[parameter]["value"] = value
        else:
            console.print(f"{self._prefix} Invalid parameter name.")

    def _setCalculated(self, parameter, value):
        if parameter in self.parameters:
            self.parameters[parameter]["calculated"] = value
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
        
        if parameter == "velocity":
            if not value.isnumeric():
                console.print(f"{self._prefix} Velocity must be a number.")
                return False
            if float(value) < 0:
                console.print(f"{self._prefix} Velocity must be positive.")
                return False
            self._setParameter("velocity", float(value))
            self._setCalculated("velocity", False)
        elif parameter == "altitude":
            if not value.isnumeric():
                console.print(f"{self._prefix} Altitude must be a number.")
                return False
            if float(value) < 0:
                console.print(f"{self._prefix} Altitude must be positive.")
                return False
            self._setParameter("altitude", float(value))
            self._setCalculated("altitude", False)
            console.print(f"{self._prefix} Altitude set to {value} m.")
            confirm = console.input(f"{self._prefix} Set density, viscosity and speed of sound to ISA standard at {value} m? (y/n): ").strip().lower()
            if confirm == "y":
                atmosphere = Atmosphere(float(value))
                self._setParameter("density", atmosphere.density[0])
                self._setCalculated("density", True)
                self._setParameter("dynamic_viscosity", atmosphere.dynamic_viscosity[0])
                self._setCalculated("dynamic_viscosity", True)
                self._setParameter("speed_of_sound", atmosphere.speed_of_sound[0])
                self._setCalculated("speed_of_sound", True)
                console.print(f"{self._prefix} Density, viscosity and speed of sound set to ISA standard at {value} m.")
        elif parameter == "load_factor": #TODO: check against maximum load factor
            if not value.isnumeric():
                console.print(f"{self._prefix} Load factor must be a number.")
                return False
            if float(value) < 0:
                console.print(f"{self._prefix} Load factor must be positive.")
                return False
            self._setParameter("load_factor", float(value))
            self._setCalculated("load_factor", False)
        elif parameter == "bank_angle":
            if not value.isnumeric():
                console.print(f"{self._prefix} Bank angle must be a number.")
                return False
            if float(value) < 0:
                console.print(f"{self._prefix} Bank angle must be positive.")
                return False
            if float(value) > 89:
                console.print(f"{self._prefix} Bank angle seems unrealistic. Please check the value. Use degrees.")
                return False
            self._setParameter("bank_angle", float(value))
            self._setCalculated("bank_angle", False)
        elif parameter == "massconfig_index":
            if not value.isnumeric():
                console.print(f"{self._prefix} Mass configuration index must be a number.")
                return False
            if not (0 <= int(value) < len(config.massConfigurations)):
                console.print(f"{self._prefix} Invalid mass configuration index.")
                return False
            self._setParameter("massconfig_index", int(value))
            self._setCalculated("massconfig_index", False)
        elif parameter == "Rec":
            if not value.isnumeric():
                console.print(f"{self._prefix} Reynolds number must be a number.")
                return False
            if float(value) < 0:
                console.print(f"{self._prefix} Reynolds number must be positive.")
                return False
            self._setParameter("Rec", float(value))
            self._setCalculated("Rec", False)
        elif parameter == "Mach":
            if not value.isnumeric():
                console.print(f"{self._prefix} Mach number must be a number.")
                return False
            if float(value) < 0:
                console.print(f"{self._prefix} Mach number must be positive.")
                return False
            if 0.7 < float(value) < 1.25: #TODO: Add/integrate 2D transonic analysis capability from xfoil
                console.print(f"{self._prefix} [yellow]Warning: Transonic analysis (Mach 0.7 - 1.25) is not supported and may not work correctly.[/yellow]")
            self._setParameter("Mach", float(value))
            self._setCalculated("Mach", False)
        elif parameter == "rate_of_climb":
            if not value.isnumeric():
                console.print(f"{self._prefix} Rate of climb must be a number.")
                return False
            self._setParameter("rate_of_climb", float(value))
            self._setCalculated("rate_of_climb", False)
        elif parameter == "flight_path_angle":
            if not value.isnumeric():
                console.print(f"{self._prefix} Flight path angle must be a number.")
                return False
            if float(value) < -90 or float(value) > 90:
                console.print(f"{self._prefix} Flight path angle must be between -90 and 90 degrees.")
                return False
            self._setParameter("flight_path_angle", float(value))
            self._setCalculated("flight_path_angle", False)
        elif parameter == "rate_of_turn":
            if not value.isnumeric():
                console.print(f"{self._prefix} Rate of turn must be a number.")
                return False
            self._setParameter("rate_of_turn", float(value))
            self._setCalculated("rate_of_turn", False)
        elif parameter == "density":
            if not value.isnumeric():
                console.print(f"{self._prefix} Density must be a number.")
                return False
            if float(value) <= 0:
                console.print(f"{self._prefix} Density must be positive.")
                return False
            self._setParameter("density", float(value))
            self._setCalculated("density", False)
        else:
            console.print(f"{self._prefix} Invalid parameter name.")
            return False
        
        #TODO: Improve this system here
        if self.getParameter("velocity") is not None and self.getParameter("altitude") is not None:
            atmosphere = Atmosphere(self.getParameter("altitude"))
            density = atmosphere.density[0]
            dynamic_viscosity = atmosphere.dynamic_viscosity[0]
            speed_of_sound = atmosphere.speed_of_sound[0]
            self._setParameter("density", density)
            self._setCalculated("density", True)
            self._setParameter("dynamic_viscosity", dynamic_viscosity)
            self._setCalculated("dynamic_viscosity", True)
            self._setParameter("speed_of_sound", speed_of_sound)
            self._setCalculated("speed_of_sound", True)
            console.print(f"{self._prefix} Updated density, viscosity, and speed of sound based on altitude {self.getParameter('altitude')} m.")
        if self.getParameter("velocity") is not None and self.getParameter("density") is not None and self.getParameter("dynamic_viscosity") is not None:
            refs = config.getReferenceQuantities()
            refChord = refs["refChord"]
            Recalc = self.getParameter("velocity") * refChord * self.getParameter("density") / self.getParameter("dynamic_viscosity")
            console.print(f"{self._prefix} Reynolds number computed using reference chord {refChord} m")
            console.print(f"{self._prefix} Reynolds number set to '{Recalc}'. Override with 'Rec <value>'")
            self._setParameter("Rec", Recalc)
            self._setCalculated("Rec", True)
        if self.getParameter("velocity") is not None and self.getParameter("speed_of_sound") is not None:
            Mach = self.getParameter("velocity") / self.getParameter("speed_of_sound")
            console.print(f"{self._prefix} Mach number computed using speed of sound {self.getParameter('speed_of_sound')} m/s")
            console.print(f"{self._prefix} Mach number set to '{Mach}'. Override with 'Mach <value>'")
            self._setParameter("Mach", Mach)
            self._setCalculated("Mach", True)
        if self.getParameter("bank_angle") is not None:
            bank_angle_rad = np.radians(self.getParameter("bank_angle"))
            load_factor = 1 / np.cos(bank_angle_rad)
            self._setParameter("load_factor", load_factor)
            self._setCalculated("load_factor", True)
            console.print(f"{self._prefix} Load factor computed using bank angle {self.getParameter('bank_angle')} degrees")
            console.print(f"{self._prefix} Load factor set to '{load_factor}'. Override with 'load_factor <value>'")
        if self.getParameter("rate_of_climb") is not None and self.getParameter("velocity") is not None:
            velocity = self.getParameter("velocity")
            rate_of_climb = self.getParameter("rate_of_climb")
            flight_path_angle_rad = np.arcsin(rate_of_climb / velocity)
            flight_path_angle_deg = np.degrees(flight_path_angle_rad)
            self._setParameter("flight_path_angle", flight_path_angle_deg)
            self._setCalculated("flight_path_angle", True)
            console.print(f"{self._prefix} Flight path angle computed using rate of climb {rate_of_climb} m/s and velocity {velocity} m/s")
            console.print(f"{self._prefix} Flight path angle set to '{flight_path_angle_deg}'. Override with 'flight_path_angle <value>'")

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
            if self.getParameter("velocity") is not None and self.getParameter("density") is not None and self.getParameter("massconfig_index") is not None and self.getParameter("load_factor") is not None:
                refs = config.getReferenceQuantities()
                refArea = refs["refArea"]
                totalmass = config.getMassConfiguration(self.getParameter("massconfig_index")).mass
                CL = 2 * totalmass * self.getParameter("load_factor") * constants.g / (self.getParameter("velocity") ** 2 * refArea * self.getParameter("density"))
                self.outputs["CL"]["value"] = CL
                console.print(f"{self._prefix} Calculated CL: {CL:.3f}")
                return True
        
        return False

    def analyzeStability(self):
        if not self.hasResults:
            console.print(f"{self._prefix} Operating point '{self.name}' has no results to analyze.")
            return False
    
        #Dimensionalize quantities

        q_inf = 0.5 * self.getParameter("density") * self.getParameter("velocity") ** 2
        refArea = config.getReferenceQuantities()["refArea"]
        refSpan = config.getReferenceQuantities()["refSpan"]
        refChord = config.getReferenceQuantities()["refChord"]
        console.print(f"{self._prefix} q_inf: {q_inf:.3f} Pa")
        console.print(f"{self._prefix} Reference Area: {refArea:.3f} m^2")
        console.print(f"{self._prefix} Reference Span: {refSpan:.3f} m")
        console.print(f"{self._prefix} Reference Chord: {refChord:.3f} m")

        nd_derivs_modified = self.results["stability"]["derivs_body_axes"].copy().drop(columns=["Mach"])
        # Convert alpha, beta, p, q, r, derivatives to per radian from per degree
        # THEYRE DERIVATVES SO THEY LOOK LIKE THEYRE BEING CONVERTED BACKWARDS!!!!
        nd_derivs_modified["alpha"] = np.rad2deg(nd_derivs_modified["alpha"])
        nd_derivs_modified["beta"]  = np.rad2deg(nd_derivs_modified["beta"])
        nd_derivs_modified["p"]     = np.rad2deg(nd_derivs_modified["p"])
        nd_derivs_modified["q"]     = np.rad2deg(nd_derivs_modified["q"])
        nd_derivs_modified["r"]     = np.rad2deg(nd_derivs_modified["r"])

        

        nd_derivs_modified["W"] = nd_derivs_modified["alpha"] / self.getParameter("velocity") #create w-derivative
        nd_derivs_modified["V"] = nd_derivs_modified["beta"] / self.getParameter("velocity") #create v-derivative
        console.print(f"{self._prefix} Modified non-dimensional derivatives:")
        console.print(nd_derivs_modified)
        #already have u derivatives
        #console.print(nd_derivs_modified)
        #convert to dimensional derivatives
        d_derivs_modified = pd.DataFrame(columns=nd_derivs_modified.columns, index=["X", "Y", "Z", "L", "M", "N"], dtype=float)
        d_derivs_modified.loc["X"] = nd_derivs_modified.loc["CFx"] * q_inf * refArea
        d_derivs_modified.loc["Y"] = nd_derivs_modified.loc["CFy"] * q_inf * refArea
        d_derivs_modified.loc["Z"] = -nd_derivs_modified.loc["CFz"] * q_inf * refArea
        d_derivs_modified.loc["L"] = nd_derivs_modified.loc["CMx"] * q_inf * refArea * refSpan
        d_derivs_modified.loc["M"] = nd_derivs_modified.loc["CMy"] * q_inf * refArea * refChord
        d_derivs_modified.loc["N"] = -nd_derivs_modified.loc["CMz"] * q_inf * refArea * refSpan
        
        d_derivs_modified["p"] = d_derivs_modified["p"] * refSpan / (2*self.getParameter("velocity"))
        d_derivs_modified["q"] = d_derivs_modified["q"] * refChord / (2*self.getParameter("velocity"))
        d_derivs_modified["r"] = d_derivs_modified["r"] * refSpan / (2*self.getParameter("velocity"))

        console.print(f"{self._prefix} Dimensional derivatives:")
        console.print(d_derivs_modified)

        console.print(f"{self._prefix} FPA: {self.getParameter('flight_path_angle')}")
        console.print(f"{self._prefix} Alpha: {self.results['stability']['final_inputs'].loc[0, 'alpha']}")
        theta0 = np.deg2rad(self.getParameter("flight_path_angle") + self.results['stability']['final_inputs'].loc[0, 'alpha'])
        console.print(f"{self._prefix} Body-Angle theta: {np.degrees(theta0):.3f} degrees")
        # Make state matrices

        Iyy = config.getMassConfiguration(self.getParameter("massconfig_index")).inertia_matrix[1,1]
        console.print(f"{self._prefix} Iyy: {Iyy:.3f} kg*m^2")
        m = config.getMassConfiguration(self.getParameter("massconfig_index")).mass
        console.print(f"{self._prefix} Mass: {m:.3f} kg")
        g = constants.g
        ueq = self.getParameter("velocity")
        console.print(f"{self._prefix} g: {g:.3f} m/s^2")
        X_u = float(d_derivs_modified.loc["X", "U"])
        X_w = float(d_derivs_modified.loc["X", "W"])
        X_q = float(d_derivs_modified.loc["X", "q"])
        Z_u = float(d_derivs_modified.loc["Z", "U"])
        Z_w = float(d_derivs_modified.loc["Z", "W"])
        Z_q = float(d_derivs_modified.loc["Z", "q"])
        M_u = float(d_derivs_modified.loc["M", "U"])
        M_w = float(d_derivs_modified.loc["M", "W"])
        M_q = float(d_derivs_modified.loc["M", "q"])

        #NOTE: W-Dot/etc derivatives not included (can they be approximated??)

        A_long = np.array([[X_u/m, X_w/m, X_q/m, -g*np.cos(theta0)],
                           [Z_u/m, Z_w/m, Z_q/m, -g*np.sin(theta0)],
                           [M_u/Iyy, M_w/Iyy, M_q/Iyy, 0.0],
                           [0.0, 0.0, 1.0, 0.0]])

        eigvals_long, eigvecs_long = np.linalg.eig(A_long)
        console.print(f"{self._prefix} Longitudinal Eigenvalues and Eigenvectors:")
        for i, eigval in enumerate(eigvals_long):
            console.print(f"Eigenvalue {i+1}: {eigval:.3f}")
            console.print(f"Eigenvector {i+1}: {eigvecs_long[:, i]}")


        omega_short_period_approx = np.sqrt((1/(m*Iyy)*Z_w*M_q - (ueq/Iyy)*M_w))
        zeta_short_period_approx = - (1/(2*m*omega_short_period_approx)) * (Z_w/m + (1/Iyy)*(M_q))

        omega_phugoid_approx = np.sqrt(- (Z_u*g)/(m*ueq))
        zeta_phugoid_approx = - X_u / (2 * omega_phugoid_approx * m)

        console.print(f"{self._prefix} Short Period Approximation:")
        console.print(f"{self._prefix} Omega: {omega_short_period_approx:.3f}")
        console.print(f"{self._prefix} Zeta: {zeta_short_period_approx:.3f}")
        console.print(f"{self._prefix} Phugoid Approximation:")
        console.print(f"{self._prefix} Omega: {omega_phugoid_approx:.3f}")
        console.print(f"{self._prefix} Zeta: {zeta_phugoid_approx:.3f}")

        
        

    def displayStabilityResults(self):
        pass      

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            settings=data["settings"],
            parameters=data["parameters"],
            inputs=data["inputs"],
            outputs=data["outputs"],
            controls=data["controls"],
            hasResults = data["hasResults"],
            modifiedSinceLastExec = data["modifiedSinceLastExec"],
            isConverged = data["isConverged"],
            results = OperatingPoint.results_from_dict(data["results"])
        )
    
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