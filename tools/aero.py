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
    while True:
        input_name = console.input(f"{OperatingPoint._prefix} Name: ").strip()
        if input_name != "":
            break
        else:
            console.print(f"{OperatingPoint._prefix} Empty input. Try again.")
    op = OperatingPoint(input_name)
    config.addOperatingPoint(op)
    return True

def listOperatingPoints(args):
    table = Table(title="Operating Points")

    table.add_column("Name", justify="left", style="cyan", no_wrap=True)

    for op in config.operatingPoints:
        table.add_row(op.name)

    console.print(table)
    for op in config.operatingPoints:
        table = Table(title=f"Operating Point: {op.name}")

        table.add_column("Parameter", justify="left", style="cyan", no_wrap=True)
        table.add_column("Value", justify="left", style="magenta")

        for param, value in op.__dict__.items():
            table.add_row(param, str(value))

        console.print(table)
def deleteOperatingPoint(args):
    raise NotImplementedError

def executeOperatingPoint(args):
    raise NotImplementedError

def editOperatingPoint(args):
    raise NotImplementedError