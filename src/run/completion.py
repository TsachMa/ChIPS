import os
import sys

def check_completion_and_warning(folder_paath):
    file_names = os.listdir(folder_paath)
    for files in file_names:
        if files[-6:] == "castep":
            castep_file = open(folder_paath+files[:-7]+".castep", "r")
            castep_file_text = castep_file.read()
            if "warning" in castep_file_text:
                print("warning: " + files)
                warning_file = open(folder_paath + files, "r")
                warning_file_lines = warning_file.readlines()
                for line in warning_file_lines:
                    if "warning" in line.lower():
                        print(line)
            if "successfully" not in castep_file_text:
                print("unfinished: " + files)
            castep_file.close()

def check_completion_and_resubmit(folder_paath):
    file_names = os.listdir(folder_paath)
    for files in file_names:
        if files[-6:] == "castep":
            castep_file = open(folder_paath+files[:-7]+".castep", "r")
            castep_file_text = castep_file.read()
            if "successfully" not in castep_file_text:
                param_file_read = open(folder_paath + files[:-7] + ".param", "r")
                param_file_read_text = param_file_read.read()
                param_file = open(folder_paath + files[:-7] + ".param", "a")
                if "continuation" not in param_file_read_text:
                    param_file.write("\ncontinuation: default\n")
                param_file_read.close()
                param_file.close()
                batch_script_file = open(folder_paath + "sbatch_" + files[:-7] + ".sh", "r")
                new_batch_script_file = open(folder_paath + "new_sbatch_" + files[:-7] + ".sh", "w")
                batch_script_file_lines = batch_script_file.readlines()
                for line in batch_script_file_lines:
                    if "--time" in line:
                        line = "#SBATCH --time=12:00:00\n"
                    if "#SBATCH -n" in line:
                        line = "#SBATCH -n 16\n"
                    if "mpirun -np" in line:
                        line = "mpirun -np 16 castep.mpi " + files[:-7]
                    new_batch_script_file.write(line)
                batch_script_file.close()
                new_batch_script_file.close()
                os.system("mv " + folder_paath + "new_sbatch_" + files[:-7] + ".sh " + sys.argv[1] + "sbatch_" + files[:-7] + ".sh")
                os.system("sbatch " + folder_paath + "sbatch_" + files[:-7] + ".sh")
            castep_file.close()

if __name__ == '__main__':
    check_completion_and_resubmit(sys.argv[1])