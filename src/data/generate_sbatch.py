import os
import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Process .cell files.")
    parser.add_argument('--kiss', action='store_true',
                        help='only process files starting with "Synth"')
    parser.add_argument('--input_dir', type=str, default=os.getcwd(),
                        help='directory to read input files (default: current directory)')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='directory to store output and error files (default: same as input directory)')
    args = parser.parse_args()
    return args

def read_global_params():
    with open("/home/gridsan/tmackey/MyTools/CASTEP_Templates/job_array.sh", "r") as global_param_file:
        global_param_files_lines = global_param_file.readlines()
    return global_param_files_lines

def process_files(input_dir, output_dir, global_param_files_lines, kiss):
    file_names = os.listdir(input_dir)

    files_that_start_with_Synth_and_end_with_cell = [file_name for file_name in file_names if file_name.startswith("Synth") and file_name.endswith(".cell")]
    number_of_input_files = len(files_that_start_with_Synth_and_end_with_cell)

    if number_of_input_files == 0:
        print("No input files found.")
        return

    max_jobs = 240
    #sat the number of input files = 390 
        
    last_one = min(number_of_input_files, max_jobs)
    #minimum = 240 

    #if there are too many input files 
    if number_of_input_files > max_jobs:
        
        #set the additional jobs equal to the difference between the number of input files and max jobs

        additional_jobs = number_of_input_files - max_jobs
        extra_tag = 1
        
        #while there are still additional jobs 
        while additional_jobs > 0:
        
            #create a new job array file
            extra_output_file = f"{output_dir}job_array_{extra_tag}.sh"
        
            with open(extra_output_file, "w") as calc_param_file:

                for line in global_param_files_lines:
                 
                    #change the array 
                    if line.startswith("#SBATCH --array="):
                        #test the array equal to last one + 1 to last one + max jobs 
                        if additional_jobs > max_jobs:
                            line = f"#SBATCH --array={last_one+1}-{last_one+max_jobs}\n"
                        else: 
                            line = f"#SBATCH --array={last_one+1}-{last_one+additional_jobs}\n"
                        
                    #write the lines to the parameter file 
                    calc_param_file.write(line)
                    
                #increment the number of array jobs by max jobs 
                last_one += max_jobs

                #decrement additional_jobs by max jobs 
                additional_jobs -= max_jobs

                #increment the tag by 1
                extra_tag += 1

    #write the first job array file        
    with open(f"{output_dir}job_array.sh", "w") as calc_param_file:
        for line in global_param_files_lines:
            if line.startswith("#SBATCH --array="):
                line = f"#SBATCH --array=1-{240}\n"
            calc_param_file.write(line)


def main():
    args = parse_args()
    global_param_files_lines = read_global_params()
    input_dir = args.input_dir
    output_dir = args.output_dir if args.output_dir else input_dir
    process_files(input_dir, output_dir, global_param_files_lines, args.kiss)

if __name__ == "__main__":
    main()
