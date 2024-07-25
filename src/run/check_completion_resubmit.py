import os
import sys
import subprocess

test_folder = "/home/gridsan/tmackey/MyTools/CASTEP_Scripts/TestFolder/Continue_testing/"

def get_filenames_starting_with_Synth_and_ending_with_castep(directory):
    """
    Get a list of all file names ending with ".castep" and starting with "Synth"

    Args: Takes the directory of the files as an argument
    """

    # Real Code
    files = os.listdir(directory)
    result = [f for f in files if f.startswith("Synth") and f.endswith(".castep")]

    result.sort()  # Sort the list before returning

    return result

get_filenames_starting_with_Synth_and_ending_with_castep(test_folder)

def get_completion_status(filename):
    """
    Checks to see if a file with the same name pre-file extension but ending with “-out.cell” exists in the folder.
   
    Args: Takes the full filename as an argument
   
   """

    # Real Code
    base_filename = os.path.splitext(filename)[0]  # Get the base filename (without extension)
    out_cell_filename = base_filename + "-out.cell"  # Construct the corresponding -out.cell filename
    return os.path.exists(os.path.join(os.path.dirname(filename), out_cell_filename))  # Check if the -out.cell file exists

	
def already_continuation_files(filename):
    """
	Checks to see if a file with the same name pre-file extension but starting with “continuation” exists in the folder.
	
    Args: Takes the full filename as an argument
    """
    
    # Real Code
    directory = os.path.dirname(filename)
    basename = os.path.basename(filename)[:-7]
    
    files = os.listdir(directory)
    result = any(f.startswith("continuation") and f.endswith(basename + ".sh") for f in files)
    
    return result

def modifying_params_file(input_castep_file):
    """
    If running_continuation_files(input_filename) is False,
    it identifies the corresponding param file and writes to the end "continuation: default."

    Args: Takes the full filename as an argument
    """

    #Real code

    param_file_path = os.path.join(input_castep_file[:-7] + ".param")
    output_filename = os.path.join(input_castep_file[:-7] + "_out.param")

    directory = os.path.dirname(input_castep_file)
    files = os.listdir(directory)

    basename = os.path.basename(input_castep_file)[:-7]

    if not already_continuation_files(input_castep_file):
        print("not already continuation files")
        with open(param_file_path, "r") as f:
            content = f.read()

        with open(output_filename, "w") as f:
            f.write(content + "\ncontinuation         : default")

        os.rename(output_filename, param_file_path)

def process_batch_script_file(directory, castep_file_name):

    """

    Modifies the batch script of all non-continuation sbatch files 

    Args: 
        
        directory: the directory where the batch script file is located

        castep_file_name: filename without the directory path and including the file extension

    Returns:
        Nothing, but modifies the batch script

    """

    #get the path to the batch script file 
    batch_script_file_path = os.path.join(directory, "sbatch_" + castep_file_name[:-7] + ".sh")

    #add a continuation tag to the start of the filename
    new_batch_script_file_path = os.path.join(directory, "continuation_" + "sbatch_" + castep_file_name[:-7] + ".sh")

    #open the batch script file and read the lines
    with open(batch_script_file_path, "r") as batch_script_file:
        
        batch_script_file_lines = batch_script_file.readlines()

        #create a new list to hold the updated lines 
        updated_lines = []

        #for every line in the old lines 
        for line in batch_script_file_lines:
            #if the line contains the string "--time"
            if "--time" in line:

                #replace the line with the new line
                line = "#SBATCH --time=12:00:00\n"
            # if the line has the string SBATCH -n 
            elif "#SBATCH -n" in line:
                #replace the line with the new line adding more processors 
                line = "#SBATCH -n 16\n"

            # if the line has the string mpirun -np in it
            elif "mpirun " in line:

                #replace the line with the new line adding more processors
                line = "mpirun -np 16 castep.mpi " + castep_file_name[:-7]
            
            #add the line (which may be edited) to the updates lines list
            updated_lines.append(line)

    #open the new batch script file and write the updated lines to it
    with open(new_batch_script_file_path, "w") as new_batch_script_file:

        new_batch_script_file.writelines(updated_lines)

process_batch_script_file(test_folder, "Synth_20381_InNSBiLaLa.castep")

def create_file_with_matching_files(matching_files, home):

	output_file_path = "continuation_files.txt"  # File to store the matching file names
	full_output_file_path = os.path.join(home, output_file_path)

	with open(full_output_file_path, "w") as file:

		file.write("\n".join(matching_files))

	print("Matching file names written to:", output_file_path)

def create_job_array(input_dir, output_dir):

    #look inside the nextra_bands_files.txt file to get the matching files
    nbands_files = []
    with open(f"{output_dir}/continuation_files.txt", "r") as file:
                
        nbands_files = file.read().splitlines()
        
    number_of_input_files = len(nbands_files)

    #read the job_array.sh file
    with open(f"{input_dir}/job_array_from_file.sh", "r") as file:
        global_param_files_lines = file.readlines()

    with open(f"{output_dir}/job_array_continuation.sh", "w") as calc_param_file:
        for line in global_param_files_lines:
            if line.startswith("#SBATCH --array="):
                line = f"#SBATCH --array=1-{number_of_input_files}\n"

            if line.startswith("mapfile -t file_names"):
                line = f"mapfile -t file_names < continuation_files.txt\n"

            calc_param_file.write(line)

def main(directory):

    filenames = get_filenames_starting_with_Synth_and_ending_with_castep(directory)
    #will return something like ["Synth_20381_InBiSNLaLa.castep", "Synth_20381_InNSBiLaLa.castep", "Synth_La3ScBi5.castep"]

    list_of_files_to_submit = []

    for file in filenames:
        
        full_castep_filepath = os.path.join(directory, file)
        
        completion_status = get_completion_status(full_castep_filepath)

        if not completion_status: 

            if already_continuation_files(full_castep_filepath):
                
                list_of_files_to_submit.append(file)
                
            else:

                #add the continuation argument to the end of the param file
                modifying_params_file(full_castep_filepath)

                #increase the processors and time for the batch script file
                #rename the batch script file to have the continuation tag at the start
                process_batch_script_file(directory, file)

                #add the file to the list of files to submit
                list_of_files_to_submit.append(file)

    template_dir = "/home/gridsan/tmackey/MyTools/CASTEP_Templates" 

    #create the array job 
    create_file_with_matching_files(list_of_files_to_submit, directory)  # Create a file with matching file names
    create_job_array(template_dir, directory)  # Create a job array file
   
    os.chdir(directory)  # Change to the directory

    os.system("sbatch job_array_continuation.sh")  # Submit the job array file

if __name__ == '__main__':
    directory = sys.argv[1]
    main(directory)


