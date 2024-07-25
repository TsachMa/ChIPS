import os
import sys
home = "/home/gridsan/tmackey/MyTools/CASTEP_Scripts/TestFolder/fix_nextra_bands" 
castep_file = "Synth_La3MnBi5.castep"

matching_files = [castep_file]

os.system("cp /home/gridsan/tmackey/MyTools/CASTEP_Scripts/TestFolder/Collect_testing/Folder3/* /home/gridsan/tmackey/MyTools/CASTEP_Scripts/TestFolder/fix_nextra_bands/")

def process_files(directory):
	file_names = os.listdir(directory)
	matching_files = []  # List to store the matching file names
	for file_name in file_names:
		if file_name.endswith("castep"):
			if has_nextra_bands_warning(directory, file_name):
				matching_files.append(file_name)
				process_castep_file(directory, file_name)
	create_file_with_matching_files(matching_files, home, "nbands")  # Create a file with matching file names
	template_dir = "/home/gridsan/tmackey/MyTools/CASTEP_Templates"
	create_job_array(template_dir, directory, "nbands")  # Create a job array file
	os.chdir(directory)  # Change to the directory
	os.system("chmod +x job_array.sh")  # Make the job array file executable
	os.system("sbatch job_array.sh")  # Submit the job array file

def has_nextra_bands_warning(directory, file_name):
    file_path = os.path.join(directory, file_name)
    with open(file_path, "r") as file:
        file_content = file.read()
    return "Recommend using nextra_bands" in file_content


def create_file_with_matching_files(matching_files, home, type):

	if type == "nbands":
		naming_string = "nbands"
	elif type == "continuation":
		naming_string = "continuation"
	else:
		naming_string = ""

	output_file_path = f"{naming_string}_files.txt"  # File to store the matching file names
	full_output_file_path = os.path.join(home, output_file_path)

	with open(full_output_file_path, "w") as file:

		file.write("\n".join(matching_files))

	print("Matching file names written to:", output_file_path)

def process_castep_file(directory, file_name):

	#initialize the max number to 0 
	max_number = 0

	#join the directory and file name to get the full path
	castep_file_path = os.path.join(directory, file_name)
	#read in the castep text lines
	castep_file_lines_text = read_file_lines(castep_file_path)
	#read in the castep text
	castep_file_text = read_file(castep_file_path)

	#if the calc has nextrabands warning, then find the max number
	if "Recommend using nextra_bands" in castep_file_text:
		#for every line in the castep file
		for line in castep_file_lines_text:
			#extract the numbers in the line
			numbers_in_line = extract_numbers(line)
			#if the line has numbers and the line has the warning
			if "Recommend using nextra_bands" in line and numbers_in_line:
				#find the max number
				max_number = max(max_number, max(numbers_in_line))

		
		print("nextra_bands warning: " + file_name)
		print(max_number)


		#get the param file path, lines and text 
		param_file_path = os.path.join(directory, file_name[:-7] + ".param")
		param_file_lines = read_file_lines(param_file_path)
		param_file_text = read_file(param_file_path)


		#if nextra_bands is not in the param file, then add it
		if "nextra_bands" not in param_file_text and  "PERC_EXTRA_BANDS" not in param_file_text:
			print("INCORRECT")
			#update the param file
			with open(param_file_path, "a") as file:
				file.write("nextra_bands : " + str(max_number * 2) + "\n")

		else:

			#get the existing nextra_bands
			existing_nextra_bands = get_existing_nextra_bands(param_file_lines)

			#if the existing nextra_bands is less than the max number, then update the param file
			if existing_nextra_bands < max_number:
				#nextra_bands         : 40 

				param_file_text.replace("nextra_bands         : " + str(existing_nextra_bands), "nextra_bands         : " + str(max_number * 2))
				
				#update the param file
				with open(param_file_path, "w") as file:
					file.write(param_file_text)
		remove_files(directory, file_name)

def read_file(file_path):
    with open(file_path, "r") as file:
        file_text = file.read()
    return file_text

def read_file_lines(file_path):
    with open(file_path, "r") as file:
        file_lines = file.readlines()
    return file_lines

def extract_numbers(line):
    numbers = []
    for item in line.replace(".", " ").split():
        if item.isdigit():
            numbers.append(int(item))
    return numbers

def get_existing_nextra_bands(file_lines):
    existing_nextra_bands = 0
    for line in file_lines:
        if "nextra_bands" in line:
            for item in line.split():
                if item.isdigit():
                    existing_nextra_bands = int(item)
    return existing_nextra_bands

def remove_files(directory, file_name):
	castep_file_path = os.path.join(directory, file_name[:-7] + ".castep")

	try:
		os.remove(castep_file_path)
	except OSError:
		print("Error removing file:", castep_file_path)

	check_file_path = os.path.join(directory, file_name[:-7] + ".check")
	try:
		os.remove(check_file_path)
	except OSError:
		print("Error removing file:", check_file_path)

	castep_bin_file_path = os.path.join(directory, file_name[:-7] + ".castep_bin")
	try:
		os.remove(castep_bin_file_path)
	except OSError:
		print("Error removing file:", castep_bin_file_path)

	out_cell_file_path = os.path.join(directory, file_name[:-7] + "-out.cell")
	try:
		os.remove(out_cell_file_path)
	except OSError:
		print("Error removing file:", out_cell_file_path)

	#remove any filename with the following pattern .000{digit}.err
	error_file_pattern = " /home/gridsan/tmackey/MyTools/CASTEP_Scripts/TestFolder/fix_nextra_bands/" + file_name[:-7] + ".000" + "[0-9]" + ".err"
	try:
		os.remove(error_file_pattern)
	except OSError:
		print("Error removing file:", error_file_pattern)

def read_global_params():
    with open("/home/gridsan/tmackey/MyTools/CASTEP_Templates/job_array_nbands.sh", "r") as global_param_file:
        global_param_files_lines = global_param_file.readlines()
    return global_param_files_lines

def create_job_array(input_dir, output_dir, type):
	
	if type == "nbands":
		naming_string = "nbands"
	elif type == "continuation":
		naming_string = "continuation"
	else:
		naming_string = ""

	#look inside the nextra_bands_files.txt file to get the matching files
	nbands_files = []

	with open(f"{output_dir}/{naming_string}_files.txt", "r") as file:
				
		nbands_files = file.read().splitlines()
		
	number_of_input_files = len(nbands_files)

	#read the job_array.sh file
	with open(f"{input_dir}/job_array_from_file.sh", "r") as file:
		global_param_files_lines = file.readlines()

	with open(f"{output_dir}/job_array_{naming_string}.sh", "w") as calc_param_file:
		for line in global_param_files_lines:
			if line.startswith("#SBATCH --array="):
				line = f"#SBATCH --array=1-{number_of_input_files}\n"

			if line.startswith("mapfile -t file_names"):
				line = f"mapfile -t file_names < {naming_string}_files.txt\n"

			calc_param_file.write(line)
				
if __name__ == "__main__":
    process_files(sys.argv[1])
    
