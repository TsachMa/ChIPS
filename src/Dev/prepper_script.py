import os
import sys
import re
import datetime
import time

#!/bin/bash

storage_directory=sys.argv[1]
cutoff_energy=sys.argv[2]
kpoints=sys.argv[3]
pressure=sys.argv[4]

new_directory_name = storage_directory+ "/LaRu4Bi12"+ "-" +cutoff_energy+ "-" +kpoints +"-"+pressure+"/"

"""
os.system("rm -r " + new_directory_name + "first_step_completed.txt")

os.system("rm -r " + new_directory_name + "fix_n_bands_completed.txt")

os.system("rm -r " + new_directory_name + "start_continuations.txt") """


