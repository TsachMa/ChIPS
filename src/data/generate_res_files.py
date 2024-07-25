import os
import sys
file_names = os.listdir(sys.argv[1])
for files in file_names:
	if files[-6:] == "castep":
		os.system("castep2res " + files[:-7] + " > " + files[:-7] + ".res")
