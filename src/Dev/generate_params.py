import os
import sys
file_names = os.listdir(sys.argv[1])
cutoffenergy = sys.argv[2]
print(file_names)
global_param_files = open("/home/gridsan/tmackey/MyTools/CASTEP_Templates/global_param.param")
global_param_files_lines = global_param_files.readlines()
global_param_files.close()
print("starting_loop")
for files in file_names:
	if files[-4:] == "cell":
		print(files)
		calc_param_file = open(sys.argv[1]+files[:-5]+".param", "w")
		for line in global_param_files_lines:
			print(line)
			calc_param_file.write(line)
		calc_param_file.write('\ncut_off_energy       : {} \n'.format(str(cutoffenergy)))
		calc_param_file.close()
