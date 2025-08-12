# Gotta love the main file

import Scripts.tools as tl
import Scripts.vsp_api as vsp
import Scripts.vsp_base as base
import numpy as np

from Scripts.settings import Settings # This an the line underneath are neded to access settings in the file
settings = Settings()

# primary_dir =   "C:\\Users\\jfile\\Documents\\MyDocuments\\CODING\\GitWorkingDirectory\\StreamlineV2"

#!!! Script is still not behaving as expected. Time for bed.

base.initialize(clear_console=True)

# IMPORT A MODEL
# base.open_vsp("C:\\Users\\jfile\\Documents\\MyDocuments\\CODING\\GitWorkingDirectory\\StreamlineV2\\Working Files\\sample_fuselage.vsp3")

# MAKE A FUSELAGE
vsp.ClearVSPModel()
fuse_id = base.add_fuselage("Custom Fuselage", 8)

#====MAKE A WING SECTION
# wid = base.add_wing("Custom Wing", 20, 3)
# input = {"sweep": 5, "back_sweep": -15, "span": 10, "root_chord": 4}
# sec_1 = base.new_wing_section(wid=wid, geom_input=input)
# sec_1.display_properties()
# sec_1.update()


# PARASITE DRAG
input = {
    'Vinf': 150,
    'Altitude': 1000,
    'DeltaTemp': 0,

    'Sref': 100,

    'model': 'us_standard'
} 
pars_drag = base.calculate_parasite_drag(input)
tl.sprint(f"Parasite drag calc = {pars_drag}", 0)

# print(result)

# tl.timeit(func=lambda: tl.value_check("Test", "double"), number=1000, inner_loop_number=1000, silence=True)

base.open_gui()

