import openvsp as vsp
from rich.console import Console
from rich.table import Table
from config_manager import ConfigurationManager
from config_manager import OperatingPoint
from config_manager import PowerPlant

config = ConfigurationManager()

console = None

def listPropulsionConfigurations(args):
    """List propulsion configurations as defined."""
    raise NotImplementedError

def createPropulsionConfiguration(args):
    """Create a new propulsion configuration."""
    input_name = console.input(f"{PowerPlant._prefix} Enter a name for the new propulsion configuration: ")
    if input_name == "":
        console.print(f"{PowerPlant._prefix} Name cannot be empty.")
        return True
    propconfig = PowerPlant(name=input_name)

    raise NotImplementedError

def deletePropulsionConfiguration(args):
    """Delete a propulsion configuration."""
    raise NotImplementedError