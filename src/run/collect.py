import os
import sys
import csv
import glob
def get_compounds(calculations_directory):
    """
    Get a list of all file names ending with ".cell" and starting with "Synth"

    Args: Takes the directory of the files as an argument

    """

    # Real Code
    files = os.listdir(calculations_directory)

    result = [f for f in files if f.startswith("Synth") and f.endswith(".cell")]

    return result


def log_file_exists(calculations_directory):
    """
    Check to see if a log file exists in the calculations directory.
    """
    log_file_path = os.path.join(calculations_directory, "log.csv")
    return os.path.isfile(log_file_path)

def create_log_file(calculations_directory):
    """
    Create a log file in the calculations directory. 
    """
    log_file_path = os.path.join(calculations_directory, "log.csv")

    with open(log_file_path, "w", newline='') as file:
        writer = csv.writer(file)
        header_row = ['name', 'n-bands round', 'n-bands error', 'suggested extra bands']
        writer.writerow(header_row)

def get_n_bands_round(filename, calculations_directory):
    """

    Return the n-bands round value to be input for this particular time when the informaiton is called. 
    Essentially the n-bands round is the order in which this collect call has been pushed. 
    Every time this collect call is pushed, the n-bands round will increase by one and the data will be appended to the csv

    Therefore to determine the current n-bands round, we look through the csv column for the last entry. If there are none, nbands round = 0 
    If there is on nbands round = prev + 1
    
    Args: 
        filename: The name of the file we are looking for. 
        calculations_directory: The directory of the calculations. 

    Returns: 
        The n-bands round value to be input for this particular time when the informaiton is called. 
    """    
    
    #get the path to the log file 
    log_file_path = os.path.join(calculations_directory, "log.csv")

    #open the log file
    with open(log_file_path, "r") as file:

        #read the log file
        reader = csv.reader(file)

        #skip the header row 
        header_row = next(reader)
        
        #get the index of the n-bands round column
        nbands_round_index = header_row.index("n-bands round")
        filename_index = header_row.index("name")

        #initialize nbands round to 0
        nbands_round = 0

        #loop through the remaining rows in the log file
        for row in reader:
            # if the filename matches the filename we are looking for
            if row[filename_index] == filename:
                #increment the nbands_round value
                 
                nbands_round += 1

    return nbands_round

# #get the n-bands round for folder 2 Synth_20381_LaLaInBiSN
# #should be 1
# n_bands_round_for_folder_2 = get_n_bands_round("Synth_20381_LaLaInBiSN.cell", test_folder_2)
# print("The n-bands round for folder 2 is: {}".format(n_bands_round_for_folder_2))

# #get the n-bands round for folder 1 Synth_20381_LaLaInBiSN
# #should be 0 
# n_bands_round_for_folder_1 = get_n_bands_round("Synth_20381_LaLaInBiSN.cell", test_folder_1)
# print("The n-bands round for folder 1 is: {}".format(n_bands_round_for_folder_1))

def get_nbands_error_and_max_suggested_nbands(filename, calculations_directory):

    """
    
    Get the n-bands error for a particular calculation (pull from .castep) corresponding
    to a cell file (the input argument)

    Args: a cell file name (not full) and the calculations directory 

    Returns: the n-bands error for that calculation as either a string "N/A" or an integer 
    
    """

    #figure out if there is a castep file corresonding to that cell file
    castep_file_path = os.path.join(calculations_directory, filename.replace(".cell", ".castep"))
    calc_started = os.path.isfile(castep_file_path)

    is_nbands = 0

    #if the calculation has started 
    if calc_started:

        #open the castep file
        with open(castep_file_path, "r") as castep_file: 

            max_suggested_nbands = 0 

            castep_file_lines = castep_file.readlines()

            for line in castep_file_lines:
                
                if "Recommend using nextra_bands" in line:

                    is_nbands = 1

                    numbers_in_line = []

                    for item in line.replace(".", " ").split():
                        
                        if item.isdigit():

                            numbers_in_line.append(int(item))

                    if max_suggested_nbands < max(numbers_in_line):

                        max_suggested_nbands = max(numbers_in_line)

        return 0, max_suggested_nbands

    else: 
        return "N/A", "N/A"
    

# #get the n-bands error for folder 3
# #should be 20
# cell_file_name = "La3MnBi5.cell"
# n_bands_error_for_folder_3, max_suggested_nbands_for_folder_3 = get_nbands_error_and_max_suggested_nbands(cell_file_name, test_folder_3)
# print("The n-bands error for folder 3 is: {}".format(n_bands_error_for_folder_3))
# print("The max suggested n-bands for folder 3 is: {}".format(max_suggested_nbands_for_folder_3)) 


def collect_log_data(calculations_directory):

    """
    Get the latest information from the .catep files about the nbands status of the compounds. 
    Maybe more information can be collected right now but I think this is what's most important at the moment 

    Args: calculations directory, does not need to have the "/" at the end.
    
    Returns: a list of dictionaries that contain the following information:
        - name 
        - n-bands round
        - n-bands error
        - suggested extra bands

    """

    #look for cells that have "Synth" in the name and end with ".cell"
    
    synth_cell_file_names = get_compounds(calculations_directory)  
    print(synth_cell_file_names)

    #create a list of dictionaries to store the information
    log_data = []
    
    #loop through the calculations
    for filename in synth_cell_file_names:        
        #reset the dictionary for each calculation
        dictionary = {}

        #set the name of the calculation
        dictionary["name"] = filename

        #get the n-bands round
        n_bands_round = get_n_bands_round(filename, calculations_directory)
        dictionary["n-bands round"] = n_bands_round

        #get the n-bands error and max suggested bands
        n_bands_error, max_suggested_extra_bands = get_nbands_error_and_max_suggested_nbands(filename, calculations_directory)
        dictionary["n-bands error"] = n_bands_error
        dictionary["suggested extra bands"] = max_suggested_extra_bands

        print(dictionary)

        #append the dictionary to the list
        log_data.append(dictionary)
    
    return log_data
    
def collect_checkpoint_data(calculations_directory):
    """

    We want to get the completion, error, and error type informaiton for every compound now 

    Args: calculations directory, does not need to have the "/" at the end.

    Returns: a list of dictionaries that contain the following information:
        - name 
        - completion
        - error
        - error type

    """

    list_of_checkpoint_data = []

    synth_cell_file_names = get_compounds(calculations_directory)
    print(synth_cell_file_names)

    for filename in synth_cell_file_names:
        dictionary = {}

        dictionary["name"] = filename

        #get the path to the castep file
        castep_file_path = os.path.join(calculations_directory, filename.replace(".cell", ".castep"))
        cacl_started = os.path.isfile(castep_file_path)

        #get the path to the out cell file
        out_cell_file_path = os.path.join(calculations_directory, filename.replace(".cell", "-out.cell"))
        out_cell_file_exists = os.path.isfile(out_cell_file_path)

        #get the error filepath        
        error_file_path = os.path.join(calculations_directory, filename.replace(".cell", ".000*.err"))
        error_files = glob.glob(error_file_path)

        if error_files:
            dictionary["completion"] = "error"
            dictionary["error"] = True
            # Read all error files and concatenate the messages
            error_messages = []
            for error_file in error_files:
                with open(error_file, 'r') as ef:
                    error_messages.append(ef.read())
            # Add error messages to 'error_type' column
            dictionary["error type"] = ' '.join(error_messages)

        elif out_cell_file_exists:
            dictionary["completion"] = "complete"
            dictionary["error"] = False
            dictionary["error type"] = "N/A"
        
        elif cacl_started:
            dictionary["completion"] = "incomplete"
            dictionary["error"] = False
            dictionary["error type"] = "N/A"
        
        else:
            dictionary["completion"] = "not started"
            dictionary["error"] = False
            dictionary["error type"] = "N/A"
        
        list_of_checkpoint_data.append(dictionary)
    
    return list_of_checkpoint_data 

def update_log_file(calculations_directory, log_data):
    """
    Append the log file with the latest information.

    Args: 
        calculations_directory: The directory of the calculations. 
        log_data: The log data to be updated.

    """

    #get the path to the log file
    log_file_path = os.path.join(calculations_directory, "log.csv")

    #open the log file
    with open(log_file_path, "a") as file:
            
        #create a writer object
        writer = csv.writer(file)

        #loop through the log data
        for dictionary in log_data:
            #create a row
            row = [dictionary["name"], dictionary["n-bands round"], dictionary["n-bands error"], dictionary["suggested extra bands"]]
            #write the row
            writer.writerow(row)

def update_checkpoint_file(calculations_directory, checkpoint_data):
    """

    Adjust the checkpoint file with the latest information. Read through the existing checkpoint file 
    and for every row, check to see if Synth + code + the string version of the permutation matches. If so, update with the appropriate data 

    Args: 
        calculations_directory: The directory of the calculations. 
        checkpoint_data: The checkpoint data to be updated.

    """

    #get the path to the checkpoint file
    checkpoint_file_path = os.path.join(calculations_directory, "checkpoint.csv")

    #open the checkpoint file
    with open(checkpoint_file_path, "r") as file:
        
        #read the checkpoint file
        reader = csv.reader(file)

        #read in the lines 
        lines = list(reader)
        print(lines)

        for line in lines: 
            #get the code and permutation from the line
            code = line[0]
            permutation = line[2] 
            
            #create the filename
            file_name = ("Synth_" + code + "_" + '{}.cell'.format((permutation).replace(" ", "").replace("{", "").replace(",", "").replace("'", "").replace(":", "").replace("}", "")))

            print(file_name)

            #loop through the checkpoint data
            for dictionary in checkpoint_data:
                #if the file name matches the name in the dictionary
                if dictionary["name"] == file_name:
                    #update the line
                    line[3] = dictionary["completion"]
                    line[4] = dictionary["error"]
                    line[5] = dictionary["error type"]
    
    #write the updated lines to the checkpoint file
    with open(checkpoint_file_path, "w") as file:
        writer = csv.writer(file)
        writer.writerows(lines)

def main(calculations_directory):

    #check to see if a log file exists, if it doesn't, create one 
    log_file_status = log_file_exists(calculations_directory)
    print(log_file_status)

    if not log_file_status:
        #create the log file 
        create_log_file(calculations_directory)

    #get the latest information relevant forthe log file 
    log_data = collect_log_data(calculations_directory)
    print(log_data)
    #get the latest information relevant for the checkpoint file
    checkpoint_data = collect_checkpoint_data(calculations_directory)
    print(checkpoint_data)
    #update the log file with time-of-search information 
    update_log_file(calculations_directory, log_data)
    
    #update the checkpoint file 
    update_checkpoint_file(calculations_directory, checkpoint_data)

if __name__ == "__main__":
    main(sys.argv[1])