#!/bin/bash

################################################################################
# Description:
# This script performs certain instructions based on the specified runtype.
# It allows running the first step instructions or fix n band instructions.
# The instructions include creating a new directory, copying cell files,
# running Python scripts, and more.
#
# Example usage:
# Run first step instructions:
# ./your_bash_file.sh -d /path/to/storage_directory -e 10 -k 5 -p 1 -c /path/to/cell_file_directory -r first_step_only -t /path/to/all_ternary_compounds.csv La Ru Bi
#
# Run fix n band instructions:
# ./your_bash_file.sh -d /path/to/storage_directory -e 10 -k 5 -p 1 -c /path/to/cell_file_directory -r fix_n_band -t /path/to/all_ternary_compounds.csv La Ru Bi
#
# Options:
#   -d: Path to the storage directory
#   -e: Cutoff energy value
#   -k: Number of k-points
#   -p: Pressure value
#   -c: Path to the cell file directory
#   -r: Runtype (first_step_only or fix_n_band)
#   -t: Path to the all_ternary_compounds.csv file
#   Followed by the array of input elements and their stoichiometries (e.g. La Ru Bi 12)
#
################################################################################

echo "starting reading_inputs"

# Parse input flags
while getopts ":d:e:k:p:c:r:t:" opt; do
  case $opt in
    d) storage_directory=$OPTARG ;;
    e) cutoff_energy=$OPTARG ;;
    k) kpoints=$OPTARG ;;
    p) pressure=$OPTARG ;;
    c) cell_file_directory=$OPTARG ;;
    r) runtype=$OPTARG ;;
    t) all_ternaries_file_name=$OPTARG ;;
    \?) echo "Invalid option -$OPTARG" >&2 ;;
  esac
done

shift $((OPTIND -1))
input_elements=("$@")  # Array of input elements

elements_string=""
for element in "${input_elements[@]}"
do
   elements_string+=$element
done

path_to_tools="/home/gridsan/tmackey/MyTools/CASTEP_Scripts"
path_to_templates="/home/gridsan/tmackey/MyTools/CASTEP_Templates"

echo "finished reading_inputs"

echo "start defining functions"

read_file() {
    filename=$1
    file_read=$(<$filename)
    echo "$file_read"
}

#make new_directory_name
new_directory_name="$storage_directory/$elements_string-$cutoff_energy-$kpoints-$pressure/"
echo "$new_directory_name"

if [[ $runtype == "init" ]]; then

    echo "Running initialization instructions"

    mkdir -p "$storage_directory"  # Create the storage directory (previous one can be removed from jupyter notebook)

    rm -rf "$new_directory_name"  # Remove the new directory if it already exists
    
    mkdir "$new_directory_name"  # Create the new directory

elif [[ $runtype == "first_step_only" ]]; then
    echo "Running first step only instructions"

    cd "$new_directory_name"
    mkdir error
    mkdir output
    
    # Run the necessary Python scripts with appropriate arguments
    echo "Running generate_params.py"
    python3 "$path_to_tools/generate_params.py" "$new_directory_name" "$cutoff_energy"

    echo "Running generate_sbatch.py"
    python3 "$path_to_tools/generate_sbatch.py" --input_dir "$new_directory_name" --kiss
    
elif [[ $runtype == "fix_n_band" ]]; then
    echo "Running fix n band instructions"
    cd "$new_directory_name"
    python3 "$path_to_tools/fix_nextra_bands.py" "$new_directory_name"

elif [[ $runtype == "continuation" ]]; then
    echo "Running continuation"
    cd "$new_directory_name"
    python3 "$path_to_tools/check_completion_resubmit.py" "$new_directory_name"

elif [[ $runtype == "collect" ]]; then
    echo "Running collect"
    
    python3 "$path_to_tools/collect.py" "$new_directory_name"

elif [[ $runtype == "display" ]]; then
    echo "Running display"
    python3 "$path_to_tools/display.py" "$new_directory_name"

else
  echo "Invalid runtype specified"
fi
