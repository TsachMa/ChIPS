import os
import sys
import re
import datetime
import time
import os
import subprocess

import sys
import decoration_and_initialization as deco

#defining cutoffenergy and kpoing spacing arrays 
cutoff_energies = [600]

kpoint_spacings = [0.04]

pressures = [0, 4, 8]

elements = ["La", "N", "Bi"]

volume_scaling_factor = 2.0

#confirm choices
print("Cutoff energies: ", cutoff_energies)
print("Kpoint Spacings: ", kpoint_spacings)
print("Pressures: ", pressures)
print("Elements: ", elements)
print("Volume Scaling Factor: ", volume_scaling_factor)

name_of_project = "New_System_First_Test_All_Cells"

#defining storage and cell file directories
#remember no / at the end of the storage directory or cell file directory or castep tools directory
current_directory = os.getcwd()
storage_directory = current_directory + "/" + name_of_project
cell_file_directory = "/home/gridsan/tmackey/Data/KISS_cell_files_First_Test"
CASTEP_tools_directory = "/home/gridsan/tmackey/MyTools/CASTEP_Scripts"
all_steps_script = CASTEP_tools_directory + "/" + "all_steps.sh"
all_ternary_compounds_directory = "/home/gridsan/tmackey/Data/all_ternary_compounds.csv"
output_dir = storage_directory + "/" + elements[0] + elements[1] + elements[2] + "-" + str(cutoff_energies[0]) + "-" + str(kpoint_spacings[0]) + "-" + str(pressures[0]) 
"/pool001/riesel/New_System_First_Test_All_Cells/LaNBi-600-0.04-0"
deco.edit_all_cell_files(cell_file_directory, pressures[0], kpoint_spacings[0], elements, all_ternary_compounds_directory, output_dir)
