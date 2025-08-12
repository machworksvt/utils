# Holds the functions for doing vsp operations that are useful. 

import Scripts.vsp_api as vsp
import Scripts.tools as tl
import Scripts.streamline_math_tools as smt

import os
import re
import numpy as np
from Scripts.settings import Settings # This an the line underneath are neded to access settings in the file
from Scripts.vsp_constants import get_vsp_constant

from sympy import symbols, Eq, solve, sin, pi
from sympy.core.sympify import SympifyError
from scipy.optimize import minimize

from rich.table import Table
from rich.console import Console

settings = Settings()

def initialize(clear_console=True):
    if clear_console:
        tl.clear()
    tl.sprint("===STREAMLINE V2=== ")

def open_gui():
    if not vsp.IsGUIBuild():
        # Can also be triggered if openvsp_config was not set
        tl.sprint("OpenVSP GUI is not available in this build.", -2)
        return False
    vsp.InitGUI()
    vsp.EnableStopGUIMenuItem()
    tl.sprint("Opening GUI...", 2)
    vsp.StartGUI()
    return True

def new_wing_section(**kwargs):
    return wing_section(**kwargs)

def add_fuselage(name="Fuselage", length=10.0):
    fid = vsp.AddGeom("FUSELAGE")
    tl.value_check(length, "double", False, False)
    vsp.SetParmVal( vsp.FindParm( fid, "Design", "Length" ), length )
    tl.sprint(f"Created fuselage geometry with length {length}. ", 2)
    tl.sprint(f"{tl.indent()}Complete: geom_id = {fid}", 3)
    vsp.Update()
    return fid

def vsp_constant(name):
    return get_vsp_constant(name)

def add_wing(name="Wing", span=20.0, chord=3.0):
    # !!! This needs lots of work
    wid = vsp.AddGeom("WING")
    # self.set_param( self.find_param(wid, "Plan", "TotalSpan"), span)
    # self.set_param( self.find_param(wid, "Plan", "TotalChord"), chord)
    # self.geoms[name] = wid

    # self.tl.sprint(f"Created wing geometry with span {span} and chord {chord}. ", 1, False)
    tl.sprint(f"geom_id = {wid}", 2)

    return wid

def save_vsp(name=settings.get("default_vsp_name"), dir=""):
    if not dir:
        dir = settings.get("base_directory")
    
    # Strip extension if already present
    if '.' in name:
        name = name.split('.')[0]
    
    # Replace invalid characters with underscores
    # Windows invalid chars: \ / : * ? " < > |
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', name).strip()
    
    # Ensure name is not empty after cleanup
    if not safe_name:
        safe_name = settings.get("default_vsp_name")

    # Final path
    path = os.path.join(dir, safe_name + ".vsp3")
    
     # Extracts directory and checks if it exists
    if not os.path.exists(os.path.dirname(path)):
        tl.sprint(f"The directory {path} does not exist. Cannot export.", -1, lead_func = True)
        return False
    # Optional: warn if overwriting an existing file
    if os.path.exists(path):
        tl.sprint(f"Overwriting existing file: {path}", -2, lead_func = True)
    
    tl.sprint(f"Saving to: {path}", 1, lead_func = True)
    
    try:
        vsp.WriteVSPFile(path)
        tl.sprint(f"Successfully saved VSP file to: {path}", 0)
    except Exception as e:
        tl.sprint(f"Failed to save file. Error: {e}", -1, lead_func = True)

def calculate_parasite_drag(input):
    """
    Run Parasite Drag analysis on the given geometry ID and return total CD.
    
    Parameters:
    gid (str): Geometry ID to analyze
    ref_area (float): Reference area [ft^2] to be used in the analysis

    Returns:
    float: Total parasite drag coefficient (CD_total)

    Parameters:
    ('AltLengthUnit', 'Altitude', 'DeltaTemp', 'Density', 'DynaVisc', 'ExportSubCompFlag', 'FileName', 'FreestreamPropChoice', 'GeomSet', 'KineVisc', 
    'LamCfEqnChoice', 'LengthUnit', 'Mach', 'ModeID', 'PresUnit', 'Pressure', 'Re_L', 'RecomputeGeom', 'RefFlag', 'SpecificHeatRatio', 'Sref', 'TempUnit', 
    'Temperature', 'TurbCfEqnChoice', 'UseModeFlag', 'VelocityUnit', 'Vinf', 'WingID')

    Vinf = 'Vinf' ('VelocityUnit')
    Alt = 'Altitude' ('AltLengthUnit')
    Temp = 'Temperature' ('TempUnit')
    dTemp = 'DeltaTemp' ('TempUnit')
    Pres = 'Pressure' ('PresUnit')
    Density = 'Density'
    Gamma = 'SpecificHeatRatio'
    Dyn Visc = 'DynaVisc'
    Re/L = 'Re_L'
    Mach = 'Mach'
    (LengthUnit)

    input = {
    'Vinf': X,
    'Altitude': X,
    'Temperature': X,
    DeltaTemp: X,
    'Pressure': X,
    'Density': X,
    'SpecificHeatRatio': X,
    'DynaVisc': X,
    'Re_L': X,
    'Mach': X,

    'Sref': X,

    'model': X
    }
    """

    # === Step 1: Find Parasite Drag Analysis Container ===
    pd_con = vsp.FindContainer("ParasiteDragSettings", 0)
    groupname = "ParasiteDrag"

    length_unit = vsp.GetIntAnalysisInput(groupname, "LengthUnit")
    vinf_unit = vsp.GetIntAnalysisInput(groupname, "VelocityUnit")
    alt_unit = vsp.GetIntAnalysisInput(groupname, "AltLengthUnit")
    temp_unit = vsp.GetIntAnalysisInput(groupname, "TempUnit")
    pres_unit = vsp.GetIntAnalysisInput(groupname, "PresUnit")

    length_unit[0] = vsp_constant("m")
    vinf_unit[0] = vsp_constant("m/s")
    alt_unit[0] = vsp_constant("m")
    temp_unit[0] = vsp_constant("k")
    pres_unit[0] = vsp_constant("pa")

    vsp.SetIntAnalysisInput(groupname, "LengthUnit", length_unit)
    vsp.SetIntAnalysisInput(groupname, "VelocityUnit", vinf_unit)
    vsp.SetIntAnalysisInput(groupname, "AltLengthUnit", alt_unit)
    vsp.SetIntAnalysisInput(groupname, "TempUnit", temp_unit)
    vsp.SetIntAnalysisInput(groupname, "PresUnit", pres_unit)

    length_unit = vsp.GetIntAnalysisInput("ParasiteDrag", "LengthUnit")
    length_unit[0] = vsp_constant("m")
    vsp.SetIntAnalysisInput("ParasiteDrag", "LengthUnit", length_unit)

    vsp.SetDoubleAnalysisInput("ParasiteDrag", "Sref", [input["Sref"]])

    atmos_selection = vsp.GetIntAnalysisInput("ParasiteDrag", "FreestreamPropChoice")
    atmos_selection[0] = vsp_constant(input["model"])
    vsp.SetIntAnalysisInput("ParasiteDrag", "FreestreamPropChoice", atmos_selection)

    match(input["model"]):
        case "herrington": # USAF 1966
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Vinf", [ input["Vinf"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Altitude", [ input["Altitude"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "DeltaTemp", [ input["DeltaTemp"] ])
        case "us_standard": # US Standard Atmosphere 1976
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Vinf", [ input["Vinf"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Altitude", [ input["Altitude"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "DeltaTemp", [ input["DeltaTemp"] ])
        case "manual-pr": #Pres + Density Control
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Vinf", [ input["Vinf"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Pressure", [ input["Pressure"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Density", [ input["Density"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "SpecificHeatRatio", [ input["SpecificHeatRatio"] ])
        case "manual-pt": #Pres + Temp Control
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Vinf", [ input["Vinf"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Temperature", [ input["Temperature"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Pressure", [ input["Pressure"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "SpecificHeatRatio", [ input["SpecificHeatRatio"] ])
        case "manual-rel": #Re/L + Mach Control
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "SpecificHeatRatio", [ input["SpecificHeatRatio"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Re_L", [ input["Re_L"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Mach", [ input["Mach"] ])
        case "manual-rt": # Density + Temp Control
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Vinf", [ input["Vinf"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Temperature", [ input["Temperature"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "Density", [ input["Density"] ])
            vsp.SetDoubleAnalysisInput("ParasiteDrag", "SpecificHeatRatio", [ input["SpecificHeatRatio"] ])

    # === Step 3: Execute Analysis ===
    res_id = vsp.ExecAnalysis("ParasiteDrag")

    # === Step 4: Extract Result ===
    results = vsp.GetDoubleResults(res_id, "Total_CD_Total", 0)

    if not results or len(results) == 0:
        tl.sprint("Error: No results returned from Parasite Drag analysis", -1, lead_func=True)
        return None

    total_cd = results[0]
    tl.sprint(f"Total parasite drag coefficient: {total_cd:.6f}", 1, lead_func=True)
    return total_cd

def open_vsp(path):
    vsp.ReadVSPFile(path)

# class non_linear_function:
#     def __init__(self)

class wing_section:
    # !!! Has to be a check in here to make sure tip chord does not become negative
    def __init__(self, wid, num=1, geom_input=None, sweep_loc=0, sec_sw_loc=1, twist=0, twist_loc=0.25, 
                 dihedral=0, num_u=6, rt_cluster=1, tip_cluster=1):

        self.wid = wid
        if num <= 0:
            tl.sprint(f"Wing sections must be 1 or higher.", -1, lead_func=True)
        self.num = num

        if not geom_input:
            tl.sprint(f"Wing input dictionary 'geom_input' cannot be empty.", -1, lead_func=True)

        if "sweep" in geom_input:
            geom_input["tan_sweep"] = np.tan( np.deg2rad( geom_input["sweep"] ) )
        if "back_sweep" in geom_input:
            geom_input["tan_back_sweep"] = np.tan( np.deg2rad( geom_input["back_sweep"] ) )

        equations = {
            "span*tan_sweep + tip_chord - root_chord - span*tan_back_sweep = 0",
            "avg_chord - tip_chord/2 - root_chord/2 = 0",
            "aspect_ratio = span/avg_chord",
            "area = span * avg_chord",
            "taper = tip_chord/root_chord"
        }
        knowns = [str(k) for k in geom_input.keys()]
        self.eqs = smt.EquationSet(equations, knowns)
        self.solved_dict = self.eqs.evaluate(geom_input)

        self.AR = self.solved_dict["aspect_ratio"]
        self.span = self.solved_dict["span"]
        self.area = self.solved_dict["area"]
        self.taper = self.solved_dict["taper"]
        self.avg_chord = self.solved_dict["avg_chord"]
        self.root_chord = self.solved_dict["root_chord"]
        self.tip_chord = self.solved_dict["tip_chord"]
        self.sec_sweep = smt.wrap_to_90( np.rad2deg( np.atan(self.solved_dict["tan_back_sweep"]) ) )
        self.sweep = smt.wrap_to_90( np.rad2deg( np.atan(self.solved_dict["tan_sweep"]) ) )

        if self.tip_chord < smt.eps():
            tl.sprint("Tip chord cannot become negative", -1, lead_func=True)

        self.sweep_loc = sweep_loc
        self.sec_sw_loc = sec_sw_loc
        self.twist = twist
        self.twist_loc = twist_loc
        self.dihedral = dihedral
        self.num_u = num_u
        self.rt_cluster = rt_cluster
        self.tip_cluster = tip_cluster

        self.xsec_surf = vsp.GetXSecSurf(wid)
        self.xsec = vsp.GetXSec(self.xsec_surf, num)

        # There are not the same strings! Use the ones in get_driver_map
        self.driving_parameters_names = {"Span", "Root_Chord", "Tip_Chord"}
        self.driver_map = None
    def check_drivers(self):
        if self.xsec is False: return False

        # --- Driver selection ---
        driver_map = self.get_driver_map()

        driving_parameters = [
            drv for key, (val, drv) in driver_map.items()
            if key in self.driving_parameters_names
        ]

        tl.sprint(f"Checking driving parameters: {driving_parameters}", 2)

        if len(driving_parameters) != 3:
            tl.sprint("Number of driving parameters must be 3", -2)
            return False
        
        tl.sprint(f"Setting driver group: {driving_parameters} to XSEC {self.xsec}", 2)
        vsp.SetDriverGroup(self.wid, self.num, *driving_parameters)
        return True
    def get_driver_map(self):
        # if self.driver_map is None:
            driver_map = {
                "Aspect":      self.AR,
                "Span":        self.span,
                "Area":        self.area,
                "Taper":       self.taper,
                "Avg_Chord":   self.avg_chord,
                "Root_Chord":  self.root_chord,
                "Tip_Chord":   self.tip_chord,
                "Sec_Sweep":   self.sec_sweep,
            }
            
            self.driver_map =  {
                name: (value, vsp.get_driver_number(name))
                for name, value in driver_map.items()
            }
            return self.driver_map
    def update(self):
        if not self.check_drivers():
            return False
        driver_map = self.get_driver_map()
        # --- Set driving parameter values ---
        for key, (value, _) in driver_map.items():
            if key in self.driving_parameters_names:
                pid = vsp.GetXSecParm(self.xsec, key)
                vsp.SetParmVal(pid, value)

        # --- Set fixed parameters ---
        fixed_params = {
            "Sweep": self.sweep,
            "Sweep_Location": self.sweep_loc,
            "Sec_Sweep_Location": self.sec_sw_loc,
            "Twist": self.twist,
            "Twist_Location": self.twist_loc,
            "Dihedral": self.dihedral,
            "SectTess_U": self.num_u,
            "InCluster": self.rt_cluster,
            "OutCluster": self.tip_cluster
        }

        for key, val in fixed_params.items():
            if val is not None:
                pid = vsp.GetXSecParm(self.xsec, key)
                vsp.SetParmVal(pid, val)

        vsp.Update()
        return True
    def display_properties(self):
        console = Console()
        table = Table(title="Wing Properties", show_header=True, header_style="bold magenta")
        
        table.add_column("Parameter", style="cyan", justify="right")
        table.add_column("Value", style="green", justify="left")

        props = {
            "Aspect Ratio": self.AR,
            "Span": self.span,
            "Area": self.area,
            "Taper": self.taper,
            "Avg Chord": self.avg_chord,
            "Root Chord": self.root_chord,
            "Tip Chord": self.tip_chord,
            "Sweep (deg)": self.sweep,
            "Sec Sweep (deg)": self.sec_sweep,
            "Twist (deg)": self.twist,
            "Twist Location": self.twist_loc,
            "Sweep Location": self.sweep_loc,
            "Secondary Sweep Location": self.sec_sw_loc,
            "Dihedral (deg)": self.dihedral,
            "Num U": self.num_u,
            "Root Cluster": self.rt_cluster,
            "Tip Cluster": self.tip_cluster,
            "Section Index": self.num
        }

        for key, val in props.items():
            val_str = f"{val:.4g}" if isinstance(val, (float, int)) else str(val)
            table.add_row(key, val_str)

        console.print(table)