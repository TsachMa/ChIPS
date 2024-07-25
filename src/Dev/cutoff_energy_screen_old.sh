#!/bin/bash

echo "starting reading_inputs"

storage_directory=$1
cutoff_energy=$2
kpoints=$3
pressure=$4
cell_file_directory=$5

time_for_first_step=5
time_for_second_step=5
time_for_third_step=11

path_to_tools="/home/riesel/Tsach/tsach276/New/Tools/CASTEP_Scripts"
path_to_templates="/home/riesel/Tsach/tsach276/New/Tools/CASTEP_Templates"

echo "finished reading_inputs"

echo "start defining functions"

write_to_log() {
    echo "$1" >> "$2/log_file.txt"
}

move_folders() {
    cell_file_directory_name=$1
    
    cell_file_directory_folders=()
    cd "$cell_file_directory_name"
    for folder in */; do
        # Go into the folder
        folder="${folder%/}"
        cd "$folder"

        cell_file_directory_folders+=("$folder/")
        cd ..
    done

    printf "%s\n" "${cell_file_directory_folders[@]}"
}

read_file() {
    filename=$1
    file_read=$(<$filename)
    echo "$file_read"
}

check_everything_completed() {
    local everything_completed=true

    for folder in "${folder_array[@]}"; do
        cd "$new_directory_name/$folder"
        file_names=(*)

        # For every file in that folder
        for file_name in "${file_names[@]}"; do
            # If that file is a castep file
            if [[ $file_name == *"castep" ]]; then
                # If the n extra bands error is in the castep file or "successfully" is not in the castep file
                castep_file_text=$(read_file "$file_name")
                if [[ $castep_file_text == *"Recommend using nextra_bands"* || $castep_file_text != *"successfully"* ]]; then
                    # Reset the fix n bands error file to just "False"
                    everything_completed=false
                fi
            fi
        done
    done

    echo "$everything_completed"
}

wait_until_completed_or_timeout() {
    local max_wait_time=$1
    local start_time=$(date +%s)

    # Function to check if the maximum waiting time has passed
    has_time_passed() {
        local now=$(date +%s)
        [ $((now - start_time)) -ge $max_wait_time ]
    }

    # Loop until everything is completed or the maximum waiting time has passed
    while true; do
        result=$(check_everything_completed)
        if [ "$result" == "true" ]; then
            echo "Everything Completed!"
            break
        fi

        if has_time_passed; then
            echo "Time limit reached ($((max_wait_time / 3600)) hours)."
            break
        fi

        # Wait for a short duration before checking again
        sleep 60  # Wait for 1 minute before checking again
    done
}

echo "finish defining functions"

#make new_directory_name

echo "definining the directory name"
new_directory_name="$storage_directory/LaRu4Bi12-$cutoff_energy-$kpoints-$pressure"
echo $new_directory_name


mkdir "$storage_directory"
rm -r "$new_directory_name" 
mkdir "$new_directory_name" 

echo "Make a log file that holds general print statements"
write_to_log "Start" "$new_directory_name"

echo "definining the cell directory folder variable"
read -r cell_file_directory_folders <<< $(move_folders "$cell_file_directory")
echo $cell_file_directory_folders

IFS=" " read -r -a folder_array <<< "$cell_file_directory_folders"

echo "Make a log file that holds whether or not the first step has run"
echo "False" >> "$new_directory_name/first_step_completed.txt"

echo "keep the first step completed file inside of the new directory file to avoid overlap"
first_step_completed=$(read_file "$new_directory_name/first_step_completed.txt")

echo "If the first step was not completed"

if [[ $first_step_completed != *"True"* ]]; then
    echo "Copy the cell files over into each cutoff energy directory"
    cd "$cell_file_directory"
    cp -r * "$new_directory_name"

    for folder in "${folder_array[@]}"; do
        cd "$new_directory_name/$folder"
        python "$path_to_tools/edit_cell.py" "$new_directory_name/$folder" "$cutoff_energy" "$pressure"
        python "$path_to_tools/generate_params.py" "$new_directory_name/$folder" "$cutoff_energy"
        python "$path_to_tools/generate_sbatch.py" "$new_directory_name/$folder"
        python "$path_to_tools/submit_sbatch.py" "$new_directory_name/$folder"
    done
fi

# After the sbatch files have been submitted for all cutoff energies, add "True" to first_step_completed
echo "True" > "$new_directory_name/first_step_completed.txt"
write_to_log "First Step Started" "$new_directory_name"

# Usage example: Wait for 4.5 hours (16200 seconds) or until everything is completed
wait_until_completed_or_timeout 16200

#############################################################################################################

# Create some files to hold whether n bands have been finished and whether to start continuations
echo 'False' >> "$new_directory_name/start_continuations.txt"
echo 'False' >> "$new_directory_name/fix_n_bands_completed.txt"

fix_n_bands_completed=$(read_file "$new_directory_name/fix_n_bands_completed.txt")

# If the value "True" is not in fix_n_bands_completed
if [[ $fix_n_bands_completed != *"True"* ]]; then
    for folder in "${folder_array[@]}"; do
        cd "$new_directory_name/$folder"
        python "$path_to_tools/fix_nextra_bands.py" "$new_directory_name/$folder"
    done

    # Output an announcement to the log file
    write_to_log 'Fix N bands Started'

    # Wait for 4.5 hours
    now=$(date +%s)
    launch_time=$((now + (time_for_second_step * 3600)))
    sleep "$((launch_time - now))"
    
    python /home/riesel/Tsach/tsach276/New/Tools/CASTEP_Scripts/n_bands_tracker.py
else
    echo "True" > "$new_directory_name/start_continuations.txt"
fi

# This set of code checks whether the fix n bands have completed
if [[ $fix_n_bands_completed != *"True"* ]]; then
    # Reset the file so that only "True" is output
    echo "True" > "$new_directory_name/fix_n_bands_completed.txt"
    
    file_names=(*)

    # For every file in that folder
    for file_name in "${file_names[@]}"; do
        # If that file is a castep file
        if [[ $file_name == *"castep" ]]; then
            # If the n extra bands error is in the castep file
            castep_file_text=$(read_file "$file_name")
            if [[ $castep_file_text == *"Recommend using nextra_bands"* ]]; then
                # Reset the fix n bands error file to just "False"
                echo 'False' > "$new_directory_name/fix_n_bands_completed.txt"
            fi
        fi
    done
    
fi

#############################################################################################################

start_continuations=$(read_file "$new_directory_name/start_continuations.txt")
fix_n_bands_completed=$(read_file "$new_directory_name/fix_n_bands_completed.txt")

# If you are ready to start continuations
if [[ $start_continuations == *"True"* && $fix_n_bands_completed == *"True"* ]]; then
    for folder in "${folder_array[@]}"; do
        cd "$new_directory_name/$folder"
        python "$path_to_tools/check_completion_resubmit.py" "$new_directory_name/$folder"
    done

    # Wait for 11.5 hours
    now=$(date +%s)
    launch_time=$((now + (time_for_third_step * 3600)))
    sleep "$((launch_time - now))"
fi


everything_completed=true

for folder in "${folder_array[@]}"; do
    cd "$new_directory_name/$folder"
    file_names=(*)

    # For every file in that folder
    for file_name in "${file_names[@]}"; do
        # If that file is a castep file
        if [[ $file_name == *"castep" ]]; then
            # If the n extra bands error is in the castep file or "successfully" is not in the castep file
            castep_file_text=$(read_file "$file_name")
            if [[ $castep_file_text == *"Recommend using nextra_bands"* || $castep_file_text != *"successfully"* ]]; then
                # Reset the fix n bands error file to just "False"
                everything_completed=false
            fi
        fi
    done
done

if $everything_completed; then
    write_to_log "fix_n_bands_completed.txt" "$new_directory_name"
else
    sbatch "$path_to_templates/sbatch_launcher.sh"
fi

