import re
import itertools
import os
import sys
import csv
import multiprocessing
import shutil

# Dictionaries for each property
def get_periodic_table():
    """
    Get the periodic table of elements.

    """    

    #read in a csv of elemental properties 
    with open("/home/gridsan/tmackey/Data/PeriodicTableofElements.csv", "r", encoding='latin-1') as file:

        #get the index of the Element, Period, Atomic Radius, and Type columns 
        element_index = 0
        period_index = 0
        atomic_radius_index = 0
        type_index = 0

        #read the csv file
        csv_reader = csv.reader(file, delimiter = ",")
        header_row = next(csv_reader)

        for i in range(len(header_row)):
            if header_row[i] == "Symbol":
                element_index = i
            elif header_row[i] == "Period":
                period_index = i
            elif header_row[i] == "Atomic Radius":
                atomic_radius_index = i
            elif header_row[i] == "Type":
                type_index = i
            else:
                continue
        
        #create a dictionary of the elements and their properties
        #key: element symbol
        #value: list of properties

        periodic_dictionary = {}
        
        for row in csv_reader:
            periodic_dictionary[row[element_index]] = [(row[period_index]), (row[atomic_radius_index]), row[type_index]]

        #change non-"" period and atomic radiusvalues to floats

        for key, value in periodic_dictionary.items():
            
            #there shouldn't be any empty strings for the period 
            periodic_dictionary[key][0] = float(value[0])
            
            #if the atomic radius is an empty string, set it to 3.3 (max AR, of Ce)
            if value[1] != "":
                periodic_dictionary[key][1] = float(value[1])
            else: 
                periodic_dictionary[key][1] = 3.3

        #manually add "D" to the dictionary
        #set the list of "D" values equal to what the list of values was for element "H"
        periodic_dictionary["D"] = periodic_dictionary["H"]

        return periodic_dictionary

def get_structure_type(csv_file_name, code):
    """
    Get the structure type for the given compound code from the CSV file.

    Args:
        csv_file_name (str): Name of the CSV file containing the structure types.
        code (str): Code associated with the compound of interest.

    Returns:
        str: Structure type of the compound.
    """
    structure_type = ""

    with open(csv_file_name, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            if row[2] == code:
                structure_type = row[0]
                break

    return structure_type

def get_elements(file_name):
    """
    Read a file and extract unique element symbols from the atomic coordinate information.

    Args:
        file_name (str): Name of the file to read.

    Returns:
        list: List of unique element symbols.
    """
    f_in = open(file_name, "r")
    cell_file_lines = f_in.readlines()

    within_positions_block = False
    positions_block_concatenated = ""

    for line_index in range(len(cell_file_lines)):
        if "%BLOCK POSITIONS_FRAC" in cell_file_lines[line_index]:
            within_positions_block = True
        elif within_positions_block and "%ENDBLOCK POSITIONS_FRAC" not in cell_file_lines[line_index]:
            positions_block_concatenated += cell_file_lines[line_index]
        else:
            within_positions_block = False

    elements = re.findall('[a-zA-Z]+', positions_block_concatenated)
    #print(elements)

    # Remove duplicates
    elements = list(dict.fromkeys(elements))

    return elements

def get_volume_ratio_with_covalent_radius(old_elements, new_elements):
    """
    Calculate the volume ratio between the total volumes of old elements and new elements.

    Args:
        old_elements (list): List of old element symbols.
        new_elements (list): List of new element symbols.

    Returns:
        float: Volume ratio between new elements and old elements.
    """

    total_volume_new_elements = 0
    total_volume_old_elements = 0

    for element in old_elements:
        try:
            radius_of_element = periodic_dictionary[re.sub(r'\d+', '', element)][1]
            #print("Radius of element {}: {}".format(element, radius_of_element))
            radius_of_element = float(radius_of_element)
            volume_of_element = radius_of_element**3
            #print("Volume of element {}: {}".format(element, volume_of_element))
            total_volume_old_elements += volume_of_element
        except:
            print("Error calculating volume for old element:", element)

    for element in new_elements:
        try:
            radius_of_element = periodic_dictionary[re.sub(r'\d+', '', element)][1]
            #print("Radius of element {}: {}".format(element, radius_of_element))
            radius_of_element = float(radius_of_element)
            volume_of_element = radius_of_element**3
            #print("Volume of element {}: {}".format(element, volume_of_element))
            total_volume_new_elements += volume_of_element
        except:
            print("Error calculating volume for new element:", element)

    ratio = (total_volume_new_elements / total_volume_old_elements)

    #print("Volume ratio:", ratio)

    return ratio

def criteria_for_structure_type(element_mapping):
    """
    Check if the element mapping satisfies the specified criteria.

    Args:
        element_mapping (dict): Dictionary representing an element mapping.

    Returns:
        bool: True if the mapping satisfies the criteria, False otherwise.
    """
    for key, value in element_mapping.items():

        
        processed_key = re.sub(r'\d+', '', key)
        processed_value = re.sub(r'\d+', '', value)

        if key != 'D' and key!= 'M':
            try: 
                key_block = periodic_dictionary[processed_key][2]
            
            except:
                print("Error processing key:", key)
                key_block = "err"
            try:
                value_block = periodic_dictionary[processed_value][2]
            except:
                print("Error processing value:", value)
                value_block = "err"

            #repeat but for the row
            try:
                key_row = periodic_dictionary[processed_key][0]

            except:
                print("Error processing key:", key)
                key_row = "err"
            try:
                value_row = periodic_dictionary[processed_value][0]
            except:
                print("Error processing value:", value)
                value_row = "err"

            if key_block != "err" and value_block != "err" and key_row != "err" and value_row != "err":
                row_criterion = (abs(key_row - value_row) < 2)            

                block_criterion = (key_block == value_block)

            else: 
                return False

        else:
            return False
        #key_group = mendeleev.element(processed_key).group
        #value_group = mendeleev.element(processed_value).group
        #group_criterion = (abs(key_group - value_group) < 5)

        #key_row = mendeleev.element(processed_key).row
        #value_row = mendeleev.element(processed_value).row
        #row_criterion = (abs(key_row - value_row) < 2)

        #if key == 'D' or not block_criterion or not group_criterion or not row_criterion:
        #    return False
        

        if not block_criterion or not row_criterion:
            return False 
        else:
            continue

    return True

ry(all_ternaries_file_name, code, elements_to_swap_in):
    """
    Check if a structure type should be attempted. Only returns False if there are no compounds in the structure type for which the structure is valid.

    Args:
        dictionary (dict): Dictionary representing an element mapping.
        all_ternaries_file_name (str): Name of the CSV file containing all ternary compounds.
        code (str): Code associated with the compound of interest.

    Returns:
        bool: True if the structure type should be attempted, False otherwise.
    """

    with open(all_ternaries_file_name, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            if row[2] == code:
                structure_type = row[0]
                break
        else:
            #print("Error: code not found in all_ternaries.csv")
            #returns True to err on the safe side and consider more than less compound
            return True 
            
    compounds_with_same_structure = []
    
    with open(all_ternaries_file_name, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            if row[0] == structure_type:
                compounds_with_same_structure.append(row[1])

    for compound in compounds_with_same_structure:
        elements = re.findall('[a-zA-Z]+', compound)
        elements = list(set(elements))

        list_of_mappings = []

        for mapping in itertools.permutations(elements_to_swap_in, 3):
            current_mapping = dict(zip(elements, mapping))

            #only keep the current mapping if it is new 
            if current_mapping not in list_of_mappings:
                list_of_mappings.append(current_mapping)
        

        for mapping in list_of_mappings:
            #print("Mapping:", mapping)
            if criteria_for_structure_type(mapping):
                #print("Criteria for structure type satisfied")
                return True

    return False

def read_file(file_name):
    """
    Read the contents of a file and return it as a string.
    """
    cell_file_read = open(file_name, "r")
    cell_file_read_text = cell_file_read.read()
    cell_file_read.close()
    cell_file_lines_file = open(file_name, "r")
    cell_file_lines = cell_file_lines_file.readlines()
    cell_file_lines_file.close()
    return cell_file_read_text, cell_file_lines

def criteria_for_permutations(element_mapping):
    """
    Calculate a metric for the given element mapping.

    Args:
        element_mapping (dict): Dictionary representing an element mapping.

    Returns:
        float: Metric value for the element mapping.
    """

    return criteria_for_structure_type(element_mapping)
    

def get_element_mapping(old_elements, elements_to_swap_in, all_ternaries_file_name, code):
    """
    Generate possible element mappings between old elements and new elements.

    Args:
        old_elements (list): List of old element symbols.
        elements_to_swap_in (list): List of new element symbols to swap in.
        all_ternaries_file_name (str): Name of the CSV file containing all ternary compounds.
        code (str): Code associated with the compound of interest.

    Returns:
        list: List of dictionaries representing valid element mappings.
    """

    element_mapping = []
    
    element_mapping_metrics = []

    if to_try(all_ternaries_file_name, code, elements_to_swap_in):

        for mapping in itertools.permutations(elements_to_swap_in, 3):
            dictionary = dict(zip(old_elements, mapping))

            if criteria_for_permutations(dictionary):
                #print("Dictionary:", dictionary)
                element_mapping.append(dictionary)            

    return element_mapping

def adjust_pressure(file_name, pressure):
    """
    Adjust the pressure in a cell file.
    
    """
    pressure = str(pressure)
    cell_file_read_text, cell_file_lines = read_file(file_name)

    if "BLOCK EXTERNAL_PRESSURE" not in cell_file_read_text:
        cell_file = open(file_name, "a")
        cell_file.write("\n%BLOCK EXTERNAL_PRESSURE\n" + pressure + " 0 0\n" + pressure + " 0\n" + pressure + "\n%ENDBLOCK EXTERNAL_PRESSURE")
        cell_file.close()
    else:
        new_cell_file = open(file_name + "_new", "w")
        for cell_line in cell_file_lines:
            if "BLOCK EXTERNAL_PRESSURE" in cell_line:
                new_cell_file.write("\nBLOCK EXTERNAL_PRESSURE\n" + sys.argv[2] + " 0 0\n" + sys.argv[2] + " 0\n" + sys.argv[2] + "\n%ENDBLOCK EXTERNAL_PRESSURE")
                break
            new_cell_file.write(cell_line)
        new_cell_file.close()
        os.system("mv " + file_name + "_new" + " " + file_name)

def adjust_kpoint_spacing(file_name, kpoint_spacing):
    """
    Adjust the kpoint spacing in a cell file.
    """
    new_lines = []
    with open(file_name, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if 'KPOINTS_MP_SPACING' not in line:
            new_lines.append(line)
        if '%ENDBLOCK POSITIONS_FRAC' in line:
            new_lines.append("\nKPOINTS_MP_SPACING {}".format(str(kpoint_spacing)))

    with open(file_name + "_new", 'w') as f:
        f.writelines(new_lines)

    os.rename(file_name + "_new", file_name)

def eliminate_symmetry(file_name):
    # Open the original file for reading
    with open(file_name, "r") as f_in:
        cell_file_lines = f_in.readlines()

    inside_block = False
    new_file_name = f"{file_name}_new"

    # Open the new file for writing
    with open(new_file_name, "w") as f_out:
        for line in cell_file_lines:
            if "%BLOCK SYMMETRY_OPS" in line:
                inside_block = True
            elif "%ENDBLOCK SYMMETRY_OPS" in line:
                inside_block = False
                continue  # skip this line as well
            if not inside_block:
                f_out.write(line)

    # Replace the original file with the new file
    shutil.move(new_file_name, file_name)

# #test on the code 20381
# #should return a cell file with no symmetry
# eliminate_symmetry(folder_1_file_file_path)

# %%
def scale_the_line(text, volume_ratio):
    #print("Before: " + str(cell_file_lines[adjusted_line_index]))
    
    proxy = ""
    radius_ratio = volume_ratio ** (1. / 3)
    #split_line = array of text (string) bits
    split_line = text.split()

    # we don't want to skip the first one 

    #pulling from the split line
    adjusted_array = [float(split_line[i]) for i in range(len(split_line))]


    #scaling by the desired amount
    adjusted_array = [radius_ratio * adjusted_array[i] for i in range(len(adjusted_array))]        

    proxy = ""
    for number in adjusted_array:
        #round number to 5 decimal places
        number = round(number, 7)
        proxy += "  {0:.15f}".format(number)
        
    return proxy
    #print("After: " + proxy)

def decorate(file_name, elements_to_swap_in, all_ternaries_file_name, code, pressure, kpoint_spacing, output_directory):
    """
    Decorate a file by swapping elements and modifying the lattice.

    Args:
        file_name (str): Name of the file to decorate.
        elements_to_swap_in (list): List of new element symbols to swap in.
        all_ternaries_file_name (str): Name of the CSV file containing all ternary compounds.
        code (str): Code associated with the compound of interest.
    """
 
    old_elements = get_elements(file_name)
    try:
        old_elements = [old_elements[0], old_elements[1], old_elements[2]]
    except:
        #add an "incomplete " tag to the name
        newfilename = file_name.replace(".cell", "_incomplete.cell")
        os.rename(file_name, newfilename)

        print("Elements array for filename {} is not length 3".format(file_name))
        
        return 
    
    volume_ratio = get_volume_ratio_with_covalent_radius(old_elements, elements_to_swap_in)

    element_mapping = get_element_mapping(old_elements, elements_to_swap_in, all_ternaries_file_name, code)
    #print(element_mapping)
    mapping_array_for_naming = [
        ("Synth_" + code + "_" + '{}.cell'.format(str(element_mapping[i]).replace(" ", "").replace("{", "").replace(",", "").replace("'", "").replace(":", "").replace("}", ""))) for i in range(len(element_mapping))]
    #print(mapping_array_for_naming)
    with open(file_name, "r") as f_in:
        cell_file_lines = f_in.readlines()
    
    for i, output_file in enumerate(mapping_array_for_naming):
        #print(element_mapping[i].items())
        #print("Output file:", output_file)

        path_to_output_file = os.path.join(output_directory, output_file)
        output_file = path_to_output_file

        f_out = open(output_file, "w")
        
        mapping_dictionary = element_mapping[i]

        new_cell_file_lines = cell_file_lines.copy()

        for line_index in range(len(cell_file_lines)):
        
            # Adjust the lattice parameters
            if "%BLOCK LATTICE_CART" in cell_file_lines[line_index]:
                index_adjustment = 1
                adjusted_line_index = line_index + index_adjustment
                while "%ENDBLOCK LATTICE_CART" not in cell_file_lines[line_index + index_adjustment]:                
                    #check if there's a number in the line
                    if any(char.isdigit() for char in cell_file_lines[adjusted_line_index]):
                        adjusted_line = cell_file_lines[adjusted_line_index]
                        new_cell_file_lines[adjusted_line_index] = scale_the_line(adjusted_line, volume_ratio) + "\n"
                    
                    index_adjustment += 1
                    adjusted_line_index = line_index + index_adjustment

            # Adjust the fractional coordinates
            elif "%BLOCK POSITIONS_FRAC" in cell_file_lines[line_index]:
                index_adjustment = 1
                adjusted_line_index = line_index + index_adjustment
                while "%ENDBLOCK POSITIONS_FRAC" not in cell_file_lines[line_index + index_adjustment]:                
                    #check if there's a number in the line
                    if any(char.isdigit() for char in cell_file_lines[adjusted_line_index]):
                        #print("Before: " + str(cell_file_lines[adjusted_line_index]))
                        radius_ratio = volume_ratio ** (1. / 3)

                        split_line = cell_file_lines[adjusted_line_index].split()
                        element_symbol = split_line[0]  # preserve the element symbol

                        for old_element, new_element in mapping_dictionary.items():
                            if old_element in element_symbol:
                                element_symbol = element_symbol.replace(old_element, new_element)

                        #if the element symbol is 1 letter long, add a space
                        if len(element_symbol) == 1:
                            element_symbol = element_symbol + " "

                        # PLEASE BE AWARE THAT I ORIGINALLY SCALED THE FRACTIONAL COORDINATES
                        # BUT I HAVE SINCE ADJUSTED THE SCALING FACTOR TO BE 1 , IE LEAVE IT UNCHANGED

                        array = [float(split_line[i]) for i in range(1, len(split_line))]    
                        
                        adjusted_array = [num * 1 for num in array]

                        proxy = ""
                        for number in adjusted_array:
                            #round number to 5 decimal places
                            number = round(number, 7)
                            proxy += "   {0:.15f}".format(number)

                        #print("After: " + element_symbol + "  " + proxy)
                        new_cell_file_lines[adjusted_line_index] = element_symbol + proxy + "\n"
                    index_adjustment += 1
                    adjusted_line_index = line_index + index_adjustment

            # Adjust the fractional coordinates
            elif "%BLOCK SPECIES_POT" in cell_file_lines[line_index]:
                index_adjustment = 1
                adjusted_line_index = line_index + index_adjustment
                while "%ENDBLOCK SPECIES_POT" not in cell_file_lines[line_index + index_adjustment]:                
                    
                    for old_element, new_element in mapping_dictionary.items():
                        if old_element in cell_file_lines[adjusted_line_index]:
                            replaced_line = cell_file_lines[adjusted_line_index].replace(old_element, new_element)
                            new_cell_file_lines[adjusted_line_index] = replaced_line
                    
                    index_adjustment += 1
                    adjusted_line_index = line_index + index_adjustment
                                    

        f_out.writelines(new_cell_file_lines)
        f_out.close()

        adjust_pressure(output_file, pressure)
        adjust_kpoint_spacing(output_file, kpoint_spacing)
        eliminate_symmetry(output_file)

    f_in.close()

def process_file(folder_name, file_name, pressure, kpoint_spacing, elements_to_swap_in, all_ternaries_file_name, output_directory, counter):
    if file_name[-4:] == "cell" and "Synth_" not in file_name:

        #print(counter/2879)
        #print("Processing file:", file_name)
        code = file_name[:-5]  # Extract the code from the file name
        #print("Code:", code)
        file_name = os.path.join(folder_name, file_name)
        decorate(file_name, elements_to_swap_in, all_ternaries_file_name, code, pressure, kpoint_spacing, output_directory)

def process_file_wrapper(list_of_arguments):
    """ 
    Wrapper function for multiprocessing.

    """
    #print("List of arguments:", list_of_arguments)
    return process_file(list_of_arguments[0], list_of_arguments[1], list_of_arguments[2], list_of_arguments[3], list_of_arguments[4], list_of_arguments[5], list_of_arguments[6], list_of_arguments[7])

def edit_all_cell_files(folder_name, pressure, kpoint_spacing, elements_to_swap_in, all_ternaries_file_name, output_directory):
    
    """
    Edit all cell files in a folder by adjusting pressure, kpoint spacing, eliminating symmetry, and decorating.

    Args:
        folder_name (str): Name of the folder containing the cell files.
        pressure (float): Pressure value to adjust.
        kpoint_spacing (float): Kpoint spacing value to adjust.
        elements_to_swap_in (list): List of new element symbols to swap in.
        all_ternaries_file_name (str): Name of the CSV file containing all ternary compounds.
        output_directory (str): Path to the output directory.
    """

    num_cores = multiprocessing.cpu_count()
    file_names = os.listdir(folder_name)

    #print(file_names)

    # Create a list of arguments to pass to the process_file function
    list_of_arguments = []
    counter = 0
    for file_name in file_names:
        list_of_arguments.append((folder_name, file_name, pressure, kpoint_spacing, elements_to_swap_in, all_ternaries_file_name, output_directory, counter))
        counter += 1
    #print("List of arguments:", list_of_arguments)
    # Create a multiprocessing Pool
    with multiprocessing.Pool(num_cores) as pool:
        # Use the Pool's map function to apply the process_file function to every file name
        pool.map(process_file_wrapper, list_of_arguments)

def init_csv(csv_file_name, output_directory):
    #get the csv file path 
    csv_file_path = os.path.join(output_directory, csv_file_name)

    #overwriting whatever the user puts in for the filename - will fix function later
    csv_file_name = os.path.join(output_directory, "checkpoint.csv")

    csv_file_name = csv_file_path

    csv_file = open(csv_file_name, "w") 

    #write a header
    csv_file.write("code,structure type,permutation,completion,error,error_type\n")

    csv_file.close()

def write_csv(csv_file_name, all_ternaries_file_name, code, file_name, output_directory, elements_to_swap_in):
    
    structure_type = get_structure_type(all_ternaries_file_name, code)

    permutations = get_element_mapping(get_elements(file_name), elements_to_swap_in, all_ternaries_file_name, code)

    #get the csv file path 
    csv_file_path = os.path.join(output_directory, csv_file_name)

    #overwriting whatever the user puts in for the filename - will fix function later
    csv_file_name = csv_file_path

    csv_columns = ["code", "structure type", "permutation", "completion", "error", "error_type"]

    csv_file = open(csv_file_name, "a") 

    #overwriting whatever the user puts in for the filename - will fix function later
    csv_file_name = os.path.join(output_directory, "checkpoint.csv")

    completion = "just made"
    error = ""
    error_type = ""
    
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)

    for permutation in permutations:
        writer.writerow({
            "code": code,
            "structure type": structure_type,
            "permutation": str(permutation),
            "completion": completion,
            "error": error,
            "error_type": error_type
        })

    csv_file.close()
if __name__ == '__main__':
    if len(sys.argv) < 7:
        print("Invalid number of arguments. Expected at least 6 arguments: folder_name pressure kpoint_spacing elements_to_swap_in all_ternaries_file_name output_directory")
    else:
        folder_name = sys.argv[1]
        pressure = sys.argv[2]
        kpoint_spacing = sys.argv[3]
        elements_to_swap_in = sys.argv[4:-2]  # All arguments between kpoint_spacing and all_ternaries_file_name are elements
        all_ternaries_file_name = sys.argv[-2]
        output_directory = sys.argv[-1]
        
        print("Input Cells Folder name:", folder_name)
        print("Pressure:", pressure)
        print("Kpoint spacing:", kpoint_spacing)
        print("Elements to swap in:", elements_to_swap_in)
        print("All ternaries file name:", all_ternaries_file_name)
        print("Output directory:", output_directory)

        edit_all_cell_files(folder_name, pressure, kpoint_spacing, elements_to_swap_in, all_ternaries_file_name, output_directory)
        
        init_csv("checkpoint.csv", output_directory)

        codes = [file_name[:-5] for file_name in os.listdir(folder_name) if file_name[-4:] == "cell" and "Synth_" not in file_name and "incomplete" not in file_name]
        for code in codes:
            write_csv("checkpoint.csv", all_ternaries_file_name, code, os.path.join(folder_name, code + ".cell"), output_directory, elements_to_swap_in)


