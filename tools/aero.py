import openvsp as vsp
from rich.console import Console
from rich.table import Table
from config_manager import ConfigurationManager
from config_manager import OperatingPoint


# Aerodynamics-related functions
console = None
config = ConfigurationManager()

def createOperatingPoint(args):
    """Create a new operating point"""
    # Choose name
    result = OperatingPoint.new()
    if not result is False:
        config.addOperatingPoint(result)
    return True

def listOperatingPoints(args):
    numOperatingPoints = len(config.operating_points)
    if numOperatingPoints == 0:
        console.print("\t[yellow]No operating points currently defined. Use 'new'.[/yellow]")
        return True
    for i, op in enumerate(config.operating_points):
        console.print(f"\t({i+1}/{numOperatingPoints})", end="")
        op.print()
    return True
        
def deleteOperatingPoint(args):
    if len(args) != 1:
        return False
    elif not args[0].isnumeric():
        return False
    elif not (0 <= int(args[0]) < len(config.operating_points)):
        console.print(f"{OperatingPoint._prefix} Invalid operating point index.")
        return True
    
    op = config.getOperatingPoint(int(args[0]))
    if op is None:
        console.print(f"{OperatingPoint._prefix} Operating point not found.")
        return True

    config.removeOperatingPoint(op)
    return True

def executeOperatingPoint(args):
    if len(args) != 1:
        return False
    elif not args[0].isnumeric():
        return False
    elif not (0 <= int(args[0]) < len(config.operating_points)):
        console.print(f"{OperatingPoint._prefix} Invalid operating point index.")
        return True
    
    op = config.getOperatingPoint(int(args[0]))
    if op is None:
        console.print(f"{OperatingPoint._prefix} Operating point not found.")
        return True

    op.exec()
    return True

def editOperatingPoint(args):
    """Edit an existing operating point"""
    if len(args) != 1:
        return False
    elif not args[0].isnumeric():
        return False
    elif not (0 <= int(args[0]) < len(config.operating_points)):
        console.print(f"{OperatingPoint._prefix} Invalid operating point index.")
        return True
    
    op = config.getOperatingPoint(int(args[0]))

    if op is None:
        console.print(f"{OperatingPoint._prefix} Operating point not found.")
        return True

    op.print()

    console.print(f"{OperatingPoint._prefix} Editing operating point: '{op.name}'\n\tType full name of parameter to edit, followed by new value (eg. 'altitude 1000'). <return> to exit.\n\tAlternatively, alter input/output values/contraints by ex: \n\t\t 'drive alpha cl auto' to calculate CL from params and find trim alpha.\n\t\t 'set beta 5' to force beta to 5 degrees.\n\t\t 'drive elevator Cm 0' for trimming elevator deflection.")
    while True:
        input_text = console.input(f"\t> ").strip().split()
        if len(input_text) == 0:
            break
        if input_text[0] in op.generic_parameters.keys() or input_text[0] in op.freestream_parameters.keys() or input_text[0] in op.type_parameters.keys() :
            param_name = input_text[0]
            param_value = input_text[1]
            if not op.updateParameter(param_name, param_value):
                console.print(f"{OperatingPoint._prefix} Invalid parameter name or value. Try again.")
                continue
        elif input_text[0] == "drive":
            if len(input_text) != 4:
                console.print(f"{OperatingPoint._prefix} Invalid input. Try again.")
                continue
            drive_input = input_text[1]
            drive_output = input_text[2]
            drive_value = input_text[3]
            if not op.driveVariable(drive_input, drive_output, drive_value):
                console.print(f"{OperatingPoint._prefix} Couldn't understand command. Try again.")
                continue
            
        elif input_text[0] == "set":
            if len(input_text) != 3:
                console.print(f"{OperatingPoint._prefix} Invalid input. Try again.")
                continue
            set_var = input_text[1]
            set_value = input_text[2]
            if not op.setVariable(set_var, set_value):
                console.print(f"{OperatingPoint._prefix} Couldn't understand command. Try again.")
                continue
        else:
            console.print(f"{OperatingPoint._prefix} Couldn't understand command. Try again.")
            continue
        op.print()
    return True

def analyzeStability(args):
    if len(args) != 1:
        return False
    elif not args[0].isnumeric():
        return False
    elif not (0 <= int(args[0]) < len(config.operating_points)):
        console.print(f"{OperatingPoint._prefix} Invalid operating point index.")
        return True
    
    op = config.getOperatingPoint(int(args[0]))
    if op is None:
        console.print(f"{OperatingPoint._prefix} Operating point not found.")
        return True
    
    if not op.hasResults:
        console.print(f"{OperatingPoint._prefix} Operating point has no results. Run it first.")
        return True

    op._printResults()
    op.analyzeStability()
    return True