import os
import sys

def check_for(folder_path)
    file_names = os.listdir(folder_path)
    for files in file_names:
        if files[-3:] == "cif":
            calc_param_file = open(folder_path+ files, "r")
            files_lines = calc_param_file.readlines()
            if string in  str(files_lines[6]):
                print(files_lines[6])
                os.remove(folder_path + files)
            calc_param_file.close()
            
if __name__ == '__main__':
    check_for(sys.argv[1])