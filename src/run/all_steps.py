import os
import sys
import shutil
import subprocess

def main():
    
    """
    Main function to perform the instructions based on the specified runtype.
    """
    # Parse command-line arguments
    args = parse_arguments()
    storage_directory = args['-d']
    cutoff_energy = args['-e']
    kpoints = args['-k']
    pressure = args['-p']
    cell_file_directory = args['-c']
    runtype = args['-r']
    input_elements = args['input_elements']

    path_to_tools = "/home/riesel/Tsach/tsach276/New/Tools/CASTEP_Scripts"
    #path_to_templates = "/home/riesel/Tsach/tsach276/New/Tools/CASTEP_Templates"


    # Make new_directory_name
    new_directory_name = f"{storage_directory}/{input_elements}-{cutoff_energy}-{kpoints}-{pressure}/"

    if runtype == "first_step_only":
        print("Running first step only instructions")
        os.makedirs(storage_directory, exist_ok=True)  # Create the storage directory
        if os.path.exists(new_directory_name):
            shutil.rmtree(new_directory_name)  # Remove the new directory if it already exists
        os.makedirs(new_directory_name)  # Create the new directory

        print("Copy the cell files over into each cutoff energy directory")
        shutil.copytree(cell_file_directory, new_directory_name)  # Copy all files from the cell file directory to the new directory

        os.chdir(new_directory_name)

        # Run the necessary Python scripts with appropriate arguments
        subprocess.run(['python', f"{path_to_tools}/decoration_and_initialization.py", new_directory_name, pressure, kpoints, *input_elements, all_ternaries_file_name])
        subprocess.run(['python', f"{path_to_tools}/generate_params.py", new_directory_name, cutoff_energy])
        subprocess.run(['python', f"{path_to_tools}/generate_sbatch.py", new_directory_name])
        subprocess.run(['python', f"{path_to_tools}/submit_sbatch.py", new_directory_name])

    elif runtype == "fix_n_band":
        print("Running fix n band instructions")
        os.chdir(new_directory_name)
        subprocess.run(['python', f"{path_to_tools}/fix_nextra_bands.py", new_directory_name])

    elif runtype == "continuation":
        print("Running continuation")
        os.chdir(new_directory_name)
        subprocess.run(['python', f"{path_to_tools}/check_completion_resubmit.py", new_directory_name])

    elif runtype == "collect":
        print("Running collect")
        os.chdir(new_directory_name)
        subprocess.run(['python', f"{path_to_tools}/collect.py", new_directory_name])

    elif runtype == "display":
        print("Running display")
        subprocess.run(['python', f"{path_to_tools}/display.py", new_directory_name])

    else:
        print("Invalid runtype specified")

    # Run the necessary Python scripts with appropriate arguments
    subprocess.run(['python', f"{path_to_tools}/decoration_and_initialization.py", new_directory_name, pressure, kpoints, *input_elements, all_ternaries_file_name])

def parse_arguments():
    """
    Parses the command-line arguments.

    Returns:
        dict: Dictionary containing the parsed arguments.
    """
    args = {}
    args['input_elements'] = []

    # Read command-line arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "-d":
            args['-d'] = sys.argv[i+1]
            i += 2
        elif arg == "-e":
            args['-e'] = sys.argv[i+1]
            i += 2
        elif arg == "-k":
            args['-k'] = sys.argv[i+1]
            i += 2
        elif arg == "-p":
            args['-p'] = sys.argv[i+1]
            i += 2
        elif arg == "-c":
            args['-c'] = sys.argv[i+1]
            i += 2
        elif arg == "-r":
            args['-r'] = sys.argv[i+1]
            i += 2
        else:
            args['input_elements'].append(arg)
            i += 1

    return args

# Call the main() function from another function in another Python script (via import)
def another_function():
    # Specify the required arguments
    arguments = {
        '-d': '/path/to/storage_directory',
        '-e': '10',
        '-k': '5',
        '-p': '1',
        '-c': '/path/to/cell_file_directory',
        '-r': 'first_step_only',
        'input_elements': ['La', 'Ru', 'Bi', '12']
    }

    # Set the command-line arguments
    sys.argv = ['your_script_name.py'] + [f"{key} {value}" for key, value in arguments.items()]

    # Call the main() function
    main()

# Call the main() function from the terminal
# Example usage:
# python your_script_name.py -d /path/to/storage_directory -e 10 -k 5 -p 1 -c /path/to/cell_file_directory -r first_step_only La Ru Bi 12

if __name__ == '__main__':
    main()
