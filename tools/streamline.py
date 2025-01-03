import openvsp as vsp
import os

import vsp_utils as utils
import aero
import geom
import config_manager
from rich.console import Console
from rich.table import Table

config = config_manager.ConfigurationManager()
console = Console()
config_manager.console = console
utils.console = console
aero.console = console
geom.console = console

current_menu = "main"


def help(_):
    """Display a help table for the current menu."""
    menu = menustructure.get(current_menu, {})
    commands = menu.get("commands", {})

    # Create a Rich table
    table = Table(title=f"Commands for {menu.get('prefix', 'Menu')}")

    # Add table columns
    table.add_column("Command", justify="left", style="cyan", no_wrap=True)
    table.add_column("Description", justify="left", style="green")
    table.add_column("Usage", justify="left", style="magenta")

    # Populate table rows with command info
    for cmd, details in commands.items():
        desc = details.get("desc", "No description available")
        usage = details.get("usage", cmd)  # Default to command name if usage is missing
        table.add_row(cmd, desc, usage)

    # Display the table
    console.print(table)
    return True

def cleanExit(args):
    if config.isModelLoaded:
        console.print("\t[yellow]A configuration is loaded. Do you want to save before exiting?")
        confirm = None
        while not (confirm == "y" or confirm == "n"):
            confirm = console.input("\t[yellow](y/n): ")
        if confirm == "y":
            utils.save()
    console.print("\tExiting...")
    exit()

def enterGeomMenu(_):
    global current_menu
    prefix = menustructure[current_menu]["prefix"]
    if not config.isModelLoaded():
        console.print(f"\t{prefix} [red]No configuration set.[/red]")
        return True
    console.print(f"\t{prefix} Entering geom menu.")
    current_menu = "geom"
    return True

def enterAeroMenu(_):
    global current_menu
    prefix = menustructure[current_menu]["prefix"]
    if not config.isModelLoaded():
        console.print(f"\t{prefix} [red]No configuration set.[/red]")
        return True
    console.print(f"\t{prefix} Entering aero menu.")
    current_menu = "aero"
    return True

def raiseMenu():
    global current_menu
    if current_menu == "main":
        return True
    current_menu = menustructure[current_menu]["parent"]
    return True

menustructure = {
    "main":{
        "prefix":"[bold]main[/bold]",
        "commands": {
            "load": {
                "desc":"Load a .vsp3 file",
                "action": utils.load,
                "usage": "load <path_to_.vsp3_file>"
            },
            "save": {
                "desc":"Save to path of currently loaded .vsp3 file, or to another path",
                "action": utils.save,
                "usage": "save <path_to_save (optional)>"
            },
            "rules": {
                "desc": "See the best practices within OpenVSP to work well with this tool",
                "action": utils.check_set_rules
            },
            "info": {
                "desc": "See basic information about the loaded VSP model",
                "action": utils.info
            },
            "help": {
                "desc": "List available commands",
                "action": help
            },
            "show": {
                "desc": "Show the vehicle in VSP. Read-only. Changes made in the GUI will not affect loaded model.",
                "action": utils.show_vehicle
            },
            "exit": {
                "desc": "Exit the tool",
                "action": cleanExit
            }, 
            "geom": {
                "desc": "Enter the geometry menu",
                "action": enterGeomMenu
            }, 
            "aero": {
                "desc": "Enter aerodynamics menu",
                "action": enterAeroMenu
            },
        }
    },
    "aero":{
        "prefix":"[bold cyan]aero[/bold cyan]",
        "parent":"main",
        "commands":{
            "help": {
                "desc": "List available commands",
                "action": help
            },
            "list":{
                "desc":"List operating points",
                "action":aero.listOperatingPoints
            },
            "edit": {
                "desc": "Edit operating point by index",
                "action": aero.editOperatingPoint,
                "usage": "edit <index>"
            },
            "new":{
                "desc":"Create new operating point",
                "action":aero.createOperatingPoint
            },
            "delete":{
                "desc":"Remove operating point by index",
                "action":aero.deleteOperatingPoint,
                "usage":"delete <index>"
            },
            "execute":{
                "desc":"Execute operating point by index",
                "action":aero.executeOperatingPoint,
                "usage":"execute <index>"
            }
        }
    },
    "geom":{
        "prefix":"[bold magenta]geom[/bold magenta]",
        "parent":"main",
        "commands": {
            "help":{
                "desc":"List available commands",
                "action":help
            },
            "list":{
                "desc":"List mass configurations",
                "action":geom.listMassConfigurations
            },
            "new":{
                "desc":"Create new mass configuration from known numbers",
                "action":geom.createMassConfiguration
            },
            "delete":{
                "desc":"Remove mass configuration by index",
                "action":geom.deleteMassConfiguration,
                "usage":"delete <index>"
            }
        }
    }
}

# action functions should return true to success false on failure/incorrect usage

def main():
    """Run the interactive command-line interface."""
    streamline_art = """
    ███████╗████████╗██████╗ ███████╗ █████╗ ███╗   ███╗██╗     ██╗███╗   ██╗███████╗
    ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗████╗ ████║██║     ██║████╗  ██║██╔════╝
    ███████╗   ██║   █████╔═╝█████╗  ███████║██╔████╔██║██║     ██║██╔██╗ ██║█████╗ 
    ╚════██║   ██║   ██║  ██╗██╔══╝  ██╔══██║██║╚██╔╝██║██║     ██║██║╚██╗██║██╔══╝  
    ███████║   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║███████╗██║██║ ╚████║███████╗ 
    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝
    """

    # Print the logo with the requested colors
    console.print(streamline_art.replace(">", "[cyan]>" + "[/cyan]").replace("█", "[green]█" + "[/green]"))

    console.print("[bold green]Welcome to Streamline. Type 'help' for commands, 'exit' to quit.[/bold green]")
    while True:
        try:
            menu = menustructure[current_menu] #pull current menu dictionary
            prefix = menu["prefix"] #get menu prefix
            prompt_string = "[bold green]Streamline >> [/bold green]" + prefix + "[bold green] >> [/bold green]"
            user_input = console.input(prompt_string)
            args = user_input.split()
            if not args:
                raiseMenu()
                continue
            command = args.pop(0)
            if command in menu["commands"]: #recognized command
                action = menu["commands"][command]["action"]
                if not action(args): #action function did not return true
                    console.print("[red]Usage:", menu["commands"][command].get("usage", command)) #bro I hate python
            else: #non recognized command
                console.print("[red]Unknown command. Type 'help' to see commands.[/red]")
        except KeyboardInterrupt:
            console.print()
            cleanExit(None)
            break
        except EOFError:
            cleanExit(None)
            break

if __name__ == "__main__":
    main()