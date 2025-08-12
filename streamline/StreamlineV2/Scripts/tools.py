# Purely useful functions that do not interact with math/vsp/aircraft

from rich import print
from rich.console import Console
from datetime import datetime
import os, sys, traceback, time, statistics
from collections.abc import Iterable

from Scripts.settings import Settings # This an the line underneath are neded to access settings in the file
settings = Settings()
console = Console()

def clear():
    os.system('cls')
def sprint(text, level=0, newline=True, raw=False, lead_func=False):
    #!!! Should all non 0 level prints have lead_func = true?
    """
    Level -3 : Log for issues that likely will not effect performance or function
    Level -2 : Warning for issues that may effect performance or function
    Level -1 : Error for issues signficantly effects performance or function
    Level 0 : Standard printing required for the gui (key information)
    Level 1 : Extra information not strictly neccessary but useful
    Level 2 : Another level of extra information to track most program actions
    Level 3 : Signicant amount of info primary only needed for debugging

    If the newline tag is set to False, the following print statement will not
    be on a new line. Useful for appending standard text statements with extra info

    If the raw tag is set to True, standard colors/fonts/log times will not be applied,
    This relies on the user applying the correct rich colors. This is NOT reccommended
    for consistency
    """

    silence = settings.get("silence")
    if silence == 1:
        return

    print_level = settings.get("print_level")
    error_level = settings.get("error_level")

    # Suppress based on configured levels
    if level < -1 and -level > abs(error_level): #Excluding -1. Always showing errors (IMPORTANT FOR FATAL ERRORS)
        return
    if level >= 1 and level > print_level: #Excluding 0. Always showing base text
        return
    
    if raw: # Skip pass the formatting if the raw flag is true
        output = text
    else:
        
        #Stores the possible msg colors
        msg_color = {
            -3: "#f29d1d",
            -2: "#fffb00",
            -1: "#ff0000",
            0: "#35d6e8",
            1: "#1c56e8",
            2: "#ba2ec7",
            3: "#aaaaaa",
        }.get(level, "#ff0000")

        stack = traceback.extract_stack()[:-1]  # Exclude the current line (sprint itself)

        if lead_func:
            text = f"({stack[-1].name}) {text}" 

        # Only assign label for errors/warnings
        if level < 0:
            label = {
                -3: f"[{msg_color}][bold]WR [/bold][/]",  # Low-priority warning
                -2: f"[{msg_color}][bold]WR [/bold][/]",  # Medium-priority warning
                -1: f"[{msg_color}][bold]ER [/bold][/]",  # Fatal error
            }.get(level, "[#ff0000][bold]?? [/bold][/]")

            now = datetime.now().strftime("%H:%M:%S")

           
            trace = " > ".join(
                f"{os.path.basename(f.filename)}:{f.lineno} ({f.name})" for f in stack[-5:]
            )
            output = f"[dim]{now}[/dim] {label} [{msg_color}]{text}\n{indent()} {trace}[/{msg_color}]"
        else:
            # Setup for non error/warning messages (standard messages)
            output = f"[{msg_color}]{text}[/{msg_color}]"
        

    # Choose ending
    end = "\n" if newline else ""
    console.print(output, end=end, soft_wrap=True)

    # Exit the program if there was a critical error
    if level == -1:
        sys.exit(1)
def empty_check(value):
    if not value and value != 0:
        sprint(f"Value '{value}' cannot be empty, None, or 0.", -1, lead_func=True)
        return

    # Now process the container’s items (if applicable)
    if isinstance(value, Iterable) and not isinstance(value, str):
        for v in value:
            if not v and v != 0:
                sprint(f"Value '{v}' cannot be empty, None, or 0.", -1, lead_func=True)
                return

    sprint(f"Values ( {value} ) have been validated.", 3, lead_func=True)
def value_check(value, expected_type="double", can_be_zero=True, can_be_negative=False):
    """
    Validates a value or a list of values based on type and constraints.
    
    Parameters:
    - value: Single value or iterable (e.g., list, tuple, np.array)
    - expected_type: 'double', 'int', 'string', 'bool'
    - can_be_zero: For numbers, whether 0 is valid
    - can_be_negative: For numbers, whether negatives are allowed
    """

    # Normalize input to iterable
    values = value if isinstance(value, Iterable) and not isinstance(value, str) else [value]

    for v in values:
        # None or empty check
        if v is None or (isinstance(v, str) and v.strip() == ""):
            sprint(f"Value '{v}' cannot be empty or None.", -1, lead_func=True)
            return False

        if expected_type == "double" or expected_type == "int":
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                sprint(f"Value '{v}' is not a number.", -1, lead_func=True)
                return False
            if not can_be_zero and v == 0:
                sprint(f"Value '{v}' cannot be zero.", -1, lead_func=True)
                return False
            if not can_be_negative and v < 0:
                sprint(f"Value '{v}' cannot be negative.", -1, lead_func=True)
                return False
            if isinstance(v, float) and expected_type == "int":
                sprint(f"Value '{v}' cannot must be an integer.", -1, lead_func=True)
                return False

        elif expected_type == "string":
            if not isinstance(v, str):
                sprint(f"Value '{v}' is not a string.", -1, lead_func=True)
                return False
            if v.strip() == "":
                sprint(f"String value '{v}' cannot be empty or whitespace.", -1, lead_func=True)
                return False

        elif expected_type == "bool":
            if not isinstance(v, bool):
                sprint(f"Value '{v}' is not a Boolean.", -1, lead_func=True)
                return False

        else:
            sprint(f"Unknown expected_type '{expected_type}' provided.", -1, lead_func=True)
            return False
    sprint(f"Values ( {value} ) have been validated. ", 3, lead_func=True)
    return True
def indent(): #!!! Issue in sprint in how this interacts with preends. Maybe have an integer number of indents passed in
    return "     "
def timeit(func=None, code=None, setup=None, number=100, inner_loop_number=1, silence=True):
    """
    Measure mean and std dev of execution time over `number` runs.
    
    Provide either:
    - func: a callable (function) to time (with no args), OR
    - code: a string of code to exec (single statement or expression),
      optionally with a setup string (imports, defs) executed once.
    
    Returns:
        mean_time, std_dev_time (both in seconds)

    sprint (silenced): Mean time = 3.2644e-07 seconds. Standard deviation = 3.5177e-08 seconds. Function can run 3.063e+06 times a second.
    sprint (unsilenced): Mean time = 1.1163e-03 seconds. Standard deviation = 7.0860e-04 seconds. Function can run 8.958e+02 times a second
    value_check: Mean time = 1.1059e-06 seconds. Standard deviation = 2.9765e-07 seconds. Function can run 9.042e+05 times a second.
    """
    sprint(f"Running time anaylisis. Running the function {inner_loop_number} times, averaging, and looping {number} times ({number*inner_loop_number:0.3e} total calls). STD on the outer loop.", 1)
    initial_silence_setting = settings.get("silence")
    if silence:
        settings.set("silence", 1)

    if func is None and code is None:
        raise ValueError("Provide either func or code to time.")

    times = []

    if func is not None:
        # Time the function call repeatedly
        for _ in range(number):
            i = 0
            start = time.perf_counter()
            for _ in range(inner_loop_number):
                func()
            end = time.perf_counter()
            times.append( (end - start)/inner_loop_number)
    else:
        # Prepare environment for exec/timeit
        global_env = {}
        if setup:
            exec(setup, global_env)
        for _ in range(number):
            start = time.perf_counter()
            exec(code, global_env)
            end = time.perf_counter()
            times.append(end - start)

    mean_time = statistics.mean(times)
    std_time = statistics.stdev(times) if number > 1 else 0.0
    name = getattr(func, '__name__', repr(func))

    if silence:
        settings.set("silence", initial_silence_setting)
    sprint(f"Time anaylisis complete. Mean time = {mean_time:0.4e} seconds. Standard deviation = {std_time:0.4e} seconds. Function can run {1/mean_time:0.3e} times a second.")

    return mean_time, std_time