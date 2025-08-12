# Holds wrappers for the VSP functions and any functions that need to access openvsp (to get variables)
import openvsp_config
openvsp_config.LOAD_GRAPHICS = True
openvsp_config.LOAD_FACADE = False

import openvsp as vsp #This should only be initialized in this class
import Scripts.tools as tl

def AddGeom(type):
    tl.sprint(f"Adding geometry of type '{type}'", 2, lead_func = True)
    tl.value_check(type, "string")
    id = vsp.AddGeom(type)
    tl.sprint(f"{tl.indent()}Complete. ID = '{id}'", 3, lead_func = True)
    return id #Returns the geometry ID
def GetXSecSurf(id_in, num=0):
    #!!! Not sure why VSP asks for the second input when it seems to always be 0
    tl.sprint(f"Looking for XSEC_SURF in geometry with id '{id_in}'", 3, lead_func = True)
    tl.value_check(id_in, "string")
    id_out = vsp.GetXSecSurf( id_in, 0 )
    if id_out is None:
        tl.sprint(f"Failed. Can't Find Parm", -1)
        return False
    else:
        tl.sprint(f"{tl.indent()}Found. ID = '{id_out}'", 3)
        return id_out
def GetNumXSec(xsec_surf_id):
    tl.sprint(f"Counting number of sections for XSEC_SURF: '{xsec_surf_id}'", 3, False, lead_func = True)
    tl.value_check(xsec_surf_id, "string")
    total = vsp.GetNumXSec(xsec_surf_id)
    tl.sprint(f" : Total = '{total}'", 3)
    return total
def GetXSecParm(sec_id, key):
    tl.sprint(f"Looking for parameter '{key}' in XSEC '{sec_id}", 3, lead_func = True)
    tl.value_check([sec_id, key], "string")
    pid = vsp.GetXSecParm(sec_id, key)
    tl.sprint(f"{tl.indent()}Found with ID = {pid}", 3)
    return pid
def GetXSec(xsec_surf_id, num):
    tl.sprint(f"Looking for XSEC {num} in XSEC_SURF with id '{xsec_surf_id}'", 3, lead_func = True)
    tl.value_check(xsec_surf_id, "string")
    tl.value_check(num, "int")
    num_sec = vsp.GetNumXSec(xsec_surf_id)
    if num > num_sec:
        tl.sprint(f"Failed: XSEC_SURF only has {num_sec}. Cannot fetch section {num}.", -1)
        return False
    else:
        id_out = vsp.GetXSec( xsec_surf_id, num )
        tl.sprint(f"{tl.indent()}Found. ID = '{id_out}'", 3)
        return id_out
def WriteVSPFile(path):
    tl.sprint(f"Writing {path}", 2, lead_func = True)
    tl.value_check(path, "string")
    vsp.WriteVSPFile(path)
    return True
def Update():
    tl.sprint(f"Updating active file.", 2, lead_func = True)
    vsp.Update()
    return True
def IsGUIBuild():
    tl.sprint(f"Checking if VSP build can support GUI.", 3, False, lead_func = True)
    status = vsp.IsGUIBuild()
    tl.sprint(f" Status = {status}", 3)
    return status
def InitGUI():
    tl.sprint(f"Initializing GUI. ", 3, lead_func = True)
    vsp.InitGUI()
    return True
def EnableStopGUIMenuItem():
    tl.sprint(f"", 3, lead_func = True)
    vsp.EnableStopGUIMenuItem()
    return True
def StartGUI():
    tl.sprint(f"Starting GUI", 2, lead_func = True)
    vsp.StartGUI()
    return True
def ClearVSPModel():
    tl.sprint(f"Clearing model", 2, lead_func = True)
    vsp.ClearVSPModel()
    return True
def FindParm(gid, tab, name):
    tl.sprint(f"Looking for parameter '{name}' in tab '{tab}' for geometry ID '{gid}'", 3, lead_func = True)
    tl.value_check([gid, tab, name], "string")
    pid = vsp.FindParm(gid, name, tab)
    if not pid:  # vsp returns empty string on failure
        tl.sprint(f"Failed: Could not find parameter. VSP returned an empty string. ", level=-1)
    tl.sprint(f"{tl.indent()}Found parameter with ID '{pid}'", 3)
    return pid
def GetParmName(pid):
    tl.sprint(f"Finding name of parameter with ID = '{pid}'", 3, lead_func = True)
    tl.value_check(pid, "string")
    name = vsp.GetParmName(pid)
    if not name:
        tl.sprint(f"Could not find name of parameter '{pid}'", -1, lead_func = True)
    tl.sprint(f"{tl.indent()}Name = {name}", 3)
    return name
def SetParmVal(pid, value):
    name = GetParmName(pid)
    tl.sprint(f"Setting parameter with ID = '{pid}' and name = '{name}' to {value} ", 2, lead_func = True)
    tl.value_check(pid, "string")
    tl.value_check(value, can_be_negative=False)
    vsp.SetParmVal( pid, value )
    return True
def SetDriverGroup(id, num, dparam1, dparam2, dparam3):
    tl.sprint(f"Setting driver group for geometry with ID = {id} and Section {num} to [{dparam1}, {dparam2}, {dparam3}]", 2, lead_func = True)
    tl.value_check([num, dparam1, dparam2, dparam3], "int")
    tl.value_check(id, "string")
    vsp.SetDriverGroup(id, num, dparam1, dparam2, dparam3)
    return True

def InsertXSec( fid, sec_num, vsp_section_type ):
    #XS_ROUNDED_RECTANGLE is a possble vsp_section_type
    vsp.InsertXSec( fid, sec_num, vsp_section_type )
def CopyXSec( fid, sec_num):
    vsp.CopyXSec( fid, sec_num)
def PasteXSec( fid, sec_num):
    vsp.PasteXSec( fid, sec_num)
def CutXSec( fid, sec_num):
    vsp.CutXSec( fid, sec_num)
def SetXSecContinuity( xsec, sec_num): #Set Continuity At Cross Section
    vsp.SetXSecContinuity( xsec, sec_num)
def SetXSecTanAngles(xsec, sec_pos, sec_num): #Set Tangent Angles At Cross Section
    #XSEC_BOTH_SIDES -> possible sec_pos type
    vsp.SetXSecTanAngles(xsec, sec_pos, sec_num)
def SetXSecTanStrengths(xsec, sec_pos, sec_num): #Set Tangent Strengths At Cross Section
    #XSEC_BOTH_SIDES -> possible sec_pos type
    vsp.SetXSecTanStrengths(xsec, sec_pos, sec_num)
def ComputeCompGeom( set, half_mesh=False, file_export_types=0 ):
    #SET_ALL -> set example type
    mesh_id = vsp.ComputeCompGeom( set, half_mesh, file_export_types ) #string
    return mesh_id
def FindLatestResultsID(result_string):
    #"Comp_Geom" -> result_string example
    comp_res_id = vsp.FindLatestResultsID( "Comp_Geom" ); #string
    return comp_res_id
def GetDoubleResults(result_id, result_string, index=0):
    #comp_res_id -> result_id example
    #"Wet_Area" -> result_string example
    double_arr = vsp.GetDoubleResults( result_id, result_string, index ); #string
    return double_arr
def SetGeomName(gid, name):
    vsp.SetGeomName( gid, name )
def FindContainer(container_name, index):
    # string PDcon = FindContainer( "ParasiteDragSettings", 0 );
    PDcon = vsp.FindContainer( container_name, index )
    return PDcon

def GetIntAnalysisInput(analysis, name, index=0):
    # array<int> vinfUnitInput = GetIntAnalysisInput( "ParasiteDrag", "VelocityUnit" );
    tl.sprint(f"Searching in '{analysis}' for '{name}' (index = '{index}').", 3, lead_func=True)
    fileNameInput = list(vsp.GetIntAnalysisInput(analysis, name, index))
    tl.empty_check(fileNameInput)
    tl.sprint(f"Result: {fileNameInput}", 3, lead_func=True)
    return fileNameInput

def GetStringAnalysisInput(analysis, name, index=0):
    # array<string> fileNameInput = GetStringAnalysisInput( "ParasiteDrag", "FileName" );
    tl.sprint(f"Searching in '{analysis}' for '{name}' (index = '{index}').", 3, lead_func=True)
    fileNameInput = list(vsp.GetStringAnalysisInput(analysis, name, index))
    tl.empty_check(fileNameInput)
    tl.sprint(f"Result: {fileNameInput}", 3, lead_func=True)
    return fileNameInput

def GetDoubleAnalysisInput(analysis, name, index=0):
    # array<double> vinfFCinput = GetDoubleAnalysisInput( "ParasiteDrag", "Vinf" );
    tl.sprint(f"Searching in '{analysis}' for '{name}' (index = '{index}').", 3, lead_func=True)
    fileNameInput = list(vsp.GetDoubleAnalysisInput(analysis, name, index))
    tl.empty_check(fileNameInput)
    tl.sprint(f"Result: {fileNameInput}", 3, lead_func=True)
    return fileNameInput

def SetStringAnalysisInput(analysis, name, indata, index=0):
    #SetStringAnalysisInput( "ParasiteDrag", "FileName", fileNameInput );
    tl.sprint(f"Setting parameter '{name} in '{analysis}' to '{indata}' (index = '{index}').", 3, lead_func=True)
    vsp.SetStringAnalysisInput( analysis, name, indata, index )
def SetIntAnalysisInput(analysis, name, indata, index=0):
    #array<int> vinfUnitInput = GetIntAnalysisInput( "ParasiteDrag", "VelocityUnit" );
    tl.sprint(f"Setting parameter '{name} in '{analysis}' to '{indata}' (index = '{index}').", 3, lead_func=True)
    vsp.SetIntAnalysisInput( analysis, name, indata, index )
def SetDoubleAnalysisInput(analysis, name, indata, index=0):
    #array<double> vinfFCinput = GetDoubleAnalysisInput( "ParasiteDrag", "Vinf" );
    tl.sprint(f"Setting parameter '{name} in '{analysis}' to '{indata}' (index = '{index}').", 3, lead_func=True)
    vsp.SetDoubleAnalysisInput( analysis, name, indata, index )
def ReadVSPFile(path):
    vsp.ReadVSPFile(path)
def FindGeom(name, index=0):
    vsp.FindGeom(name, index)
def ExecAnalysis(analysis):
    res_id = vsp.ExecAnalysis( analysis )
    return res_id
def UpdateParasiteDrag():
    vsp.UpdateParasiteDrag()
def GetAnalysisInputNames(analysis):
    return vsp.GetAnalysisInputNames(analysis)


def get_driver_number(name):
    tl.sprint(f"Getting driver number for key '{name}'", 3, lead_func=True)
    # !!! Not sure if the non-precise names should be included so the error can be caught earlier
    driver_name_map = {
        "AR": vsp.AR_WSECT_DRIVER,
        "Aspect Ratio": vsp.AR_WSECT_DRIVER,
        "Aspect": vsp.AR_WSECT_DRIVER,
        "Span": vsp.SPAN_WSECT_DRIVER,
        "Area": vsp.AREA_WSECT_DRIVER,
        "Taper": vsp.TAPER_WSECT_DRIVER,
        "Taper Ratio": vsp.TAPER_WSECT_DRIVER,
        "Average Chord": vsp.AVEC_WSECT_DRIVER,
        "Avg_Chord": vsp.AVEC_WSECT_DRIVER,
        "Root Chord": vsp.ROOTC_WSECT_DRIVER,
        "Root_Chord": vsp.ROOTC_WSECT_DRIVER,
        "Tip Chord": vsp.TIPC_WSECT_DRIVER,
        "Tip_Chord": vsp.TIPC_WSECT_DRIVER,
        "Section Sweep": vsp.SECSWEEP_WSECT_DRIVER,
        "Sec_Sweep": vsp.SECSWEEP_WSECT_DRIVER,
    }

    key = name.strip().title().replace("_", " ")
    if name in driver_name_map:
        num = driver_name_map[name]
    elif key in driver_name_map:
        num = driver_name_map[key]
    else:
        tl.sprintf(f"ValueError: Unkown driver name: {name}", -1)
        return False
    tl.sprint(f"Number = {num}", 3)
    return num

def get_constant(name):
    """
    Fast lookup for OpenVSP constants with fallback support.
    Prioritizes speed: direct dict access, avoids getattr unless needed.
    """
    # Canonical constant map — fast lookup
    constants = {
        # Velocity units
        "V_UNIT_M_S": vsp.V_UNIT_M_S,
        "V_UNIT_FT_S": vsp.V_UNIT_FT_S,
        "V_UNIT_KTAS": vsp.V_UNIT_KTAS,
        "V_UNIT_MACH": vsp.V_UNIT_MACH,

        # Turbulent Cf equations
        "CF_LAM_BLASIUS ": vsp.CF_LAM_BLASIUS,
        "CF_TURB_POWER_LAW": vsp.CF_TURB_POWER_LAW_BLASIUS,
        "CF_TURB_IMPLICIT_KARMAN_SCHOENHERR": vsp.CF_TURB_IMPLICIT_KARMAN_SCHOENHERR,

        # Form factor equations
        "FF_W_DATCOM": vsp.FF_W_DATCOM,
        "FF_B_SCHEMENSKY_BODY": vsp.FF_B_SCHEMENSKY_BODY,
        "FF_W_JENKINSON_TAIL": vsp.FF_W_JENKINSON_TAIL,

        # Excrescence types
        "EXCRESCENCE_COUNT": vsp.EXCRESCENCE_COUNT,
        "EXCRESCENCE_CD": vsp.EXCRESCENCE_CD,
        "EXCRESCENCE_PERCENT_GEOM": vsp.EXCRESCENCE_PERCENT_GEOM,

        # Wing section
        "AR_WSECT_DRIVER": vsp.AR_WSECT_DRIVER,
        "SPAN_WSECT_DRIVER": vsp.SPAN_WSECT_DRIVER,
        "AREA_WSECT_DRIVER": vsp.AREA_WSECT_DRIVER,
        "TAPER_WSECT_DRIVER": vsp.TAPER_WSECT_DRIVER,
        "AVEC_WSECT_DRIVER": vsp.AVEC_WSECT_DRIVER,
        "ROOTC_WSECT_DRIVER": vsp.ROOTC_WSECT_DRIVER,
        "TIPC_WSECT_DRIVER": vsp.TIPC_WSECT_DRIVER,
        "SECSWEEP_WSECT_DRIVER": vsp.SECSWEEP_WSECT_DRIVER
    }

    # Aliases for more readable or shorthand inputs
    aliases = {
        # Velocity
        "m/s": "V_UNIT_M_S",
        "ft/s": "V_UNIT_FT_S",
        "ktas": "V_UNIT_KTAS",
        "mach": "V_UNIT_MACH",

        # Turbulent Cf
        "blasius": "CF_LAM_BLASIUS",
        "powerlaw": "CF_TURB_POWER_LAW",
        "karman": "CF_TURB_IMPLICIT_KARMAN_SCHOENHERR",

        # Form factors
        "datcom": "FF_W_DATCOM",
        "schemensky": "FF_B_SCHEMENSKY_BODY",
        "jenkinson": "FF_W_JENKINSON_TAIL",

        # Excrescence types
        "count": "EXCRESCENCE_COUNT",
        "cd": "EXCRESCENCE_CD",
        "percent": "EXCRESCENCE_PERCENT_GEOM",

        # Wing section driver aliases
        "aspect": "AR_WSECT_DRIVER",
        "aspectratio": "AR_WSECT_DRIVER",
        "ar": "AR_WSECT_DRIVER",

        "span": "SPAN_WSECT_DRIVER",
        "area": "AREA_WSECT_DRIVER",
        "taper": "TAPER_WSECT_DRIVER",
        "taper ratio": "TAPER_WSECT_DRIVER",

        "average chord": "AVEC_WSECT_DRIVER",
        "avg chord": "AVEC_WSECT_DRIVER",
        "ave chord": "AVEC_WSECT_DRIVER",
        "avgc": "AVEC_WSECT_DRIVER",

        "root chord": "ROOTC_WSECT_DRIVER",
        "rootc": "ROOTC_WSECT_DRIVER",

        "tip chord": "TIPC_WSECT_DRIVER",
        "tipc": "TIPC_WSECT_DRIVER",

        "sweep": "SECSWEEP_WSECT_DRIVER",
        "section sweep": "SECSWEEP_WSECT_DRIVER",
        "secsweep": "SECSWEEP_WSECT_DRIVER"
    }

    key = name.strip().upper()

    # Handle alias lookups
    if key in aliases:
        key = aliases[key]

    # Fastest path: direct dict access
    if key in constants:
        return constants[key]

    # Optional: try vsp direct lookup (slower, only if needed)
    try:
        tl.sprint(f"VSP Constant '{name}' is not included in dictionary. Please add.",-2)
        return getattr(vsp, key)
    except AttributeError:
        tl.sprint(f"Unknown constant: '{name}'", -1, lead_func=True)
        return None
