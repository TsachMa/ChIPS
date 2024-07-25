import os
import sys
import re
import itertools
import mendeleev
import numpy as np

def get_elements(file_name):
    #read in a file as file-lines
    f_in = open(file_name, "r")
    cell_file_lines = f_in.readlines()
    
    within_positions_block = False
    positions_block_concatenated = ""
    #get the atomic coordinate information as a giant string by concatenating line strings of interest
    for line_idex in range(len(cell_file_lines)):
        if "%BLOCK POSITIONS_FRAC" in cell_file_lines[line_idex]:
            within_positions_block = True
        elif within_positions_block and "%ENDBLOCK POSITIONS_FRAC" not in cell_file_lines[line_idex]:
            positions_block_concatenated += cell_file_lines[line_idex]
        else:
            within_positions_block = False
            
    elements = re.findall('[a-zA-Z]+', positions_block_concatenated)
    elements = list(set(elements))
    
    return elements

def to_del(dict):
    for key, value in dict.items():
        processed_key = re.sub(r'\d+', '', key)
        processed_value = re.sub(r'\d+', '', value)
        
        key_block = mendeleev.element(processed_key).block
        value_block = mendeleev.element(processed_value).block
        block_criterion = (key_block == value_block)
        
        key_group = mendeleev.element(processed_key).group
        value_group = mendeleev.element(processed_value).group
        group_criterion = (abs(key_group-value_group) < 5)
        
        
        key_row = mendeleev.element(processed_key).row
        value_row = mendeleev.element(processed_value).row
        row_criterion = (abs(key_row-value_row) < 2)
        
        
        if key =='D' or not block_criterion or not group_criterion or not row_criterion:
            return True
        
    return False

def new_dict(dict_array):
    return [dict for dict in dict_array if not to_del(dict)]

def get_volume_ratio(old_elements):
    total_volume = 0
    for element in old_elements: 
        try: 
            total_volume += mendeleev.element(re.sub(r'\d+', '', element)).atomic_volume
        except: 
            print(old_elements)
    La_volume = mendeleev.element('La').atomic_volume
    Ru_volume = mendeleev.element('Ru').atomic_volume
    Bi_volume = mendeleev.element('Bi').atomic_volume
    
    ratio  = (La_volume+Ru_volume+Bi_volume)/total_volume
    return ratio 

def get_element_mapping(old_elements, elements_to_swap_in):
        element_mapping = []

        for mapping in itertools.permutations(elements_to_swap_in, 3):
                element_mapping.append(dict(zip(old_elements, mapping)))

        newelement_mapping = new_dict(element_mapping)
        
        return newelement_mapping 

def write_file(files, output_files, element_mapping, volume_ratio):
    f_in = open(sys.argv[1] + files, "r")
    cell_file_lines = f_in.readlines()

    symmetry = False
    for i, output_file in enumerate(output_files):
        print("Sucess output" +  output_file)
        f_out = open(output_file, "w")
        for line_index in range(len(cell_file_lines)):
            for old_element, new_element in element_mapping[i].items():
                if not "%" in cell_file_lines[line_index]: 
                    cell_file_lines[line_index] = cell_file_lines[line_index].replace(old_element + " ", new_element)
            if "%BLOCK LATTICE_CART" in cell_file_lines[line_index]:  
                proxy = ""
                for k in range(3):
                    radius_ratio = volume_ratio ** (1. / 3)
                    proxy += "   " + str((np.array(cell_file_lines[line_index+k].split()).astype(float)*radius_ratio)[k])

                cell_file_lines = proxy + "\n"
            if "SYMMETRY_OPS" in cell_file_lines[line_index]: 
                symmetry = True 
            if symmetry == False:
                f_out.write(cell_file_lines[line_index])
        f_out.close()
    f_in.close()

def write_incomplete(file_name, text):
    incomplete_log_file = open(file_name, "w")
    incomplete_log_file.write(text)
    incomplete_log_file.close()
            

def better_edit_cell_file(original_cell_file_folder, deposit_folder, elements_to_swap_in):
    file_names = os.listdir(original_cell_file_folder)
    for files in file_names:
        if files[-4:] == "cell":
            try:
                
                old_elements = get_elements(sys.argv[1] + files)
                old_elements = [old_elements[0], old_elements[1], old_elements[2]]
                volume_ratio = get_volume_ratio(old_elements)
                
                element_mapping = get_element_mapping(old_elements, elements_to_swap_in)
                volujme_ratio = get_volume_ratio(old_elements)
                
                code = files[:-4] 
                mapping_array_for_naming = [(deposit_folder + '{}.cell'.format(str(element_mapping[i]).replace(" ", "").replace("{", "").replace(",", "").replace("'", "").replace(":", "").replace("}", "")) ) for i in range(len(element_mapping))]
                output_files = [(code+mapping) for mapping in mapping_array_for_naming]

                write_file(files, output_files, element_mapping, volume_ratio)	
            except:
                write_incomplete(files, "incomplete")

if __name__ == '__main__':
    better_edit_cell_file(sys.argv[1], sys.argv[2], sys.argv[3])
    
    

