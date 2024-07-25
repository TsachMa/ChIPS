import os
import sys

file_names = os.listdir(sys.argv[1])
job_array_arg = f"1-{len(file_names)}"

for files in file_names:
    if files.endswith("cell"):
        sbatch_file = sys.argv[1] + "sbatch_" + files[:-5] + ".sh"
        sbatch_command = f"sbatch --array={job_array_arg} {sbatch_file}"
        print(sbatch_command)
        os.system(sbatch_command)


import os
import sys

file_directory = sys.argv[1]

# Create the combined sbatch file
combined_sbatch_file = file_directory + "combined_sbatch.sh"

# Generate the sbatch commands for each file
sbatch_commands = []
file_names = os.listdir(file_directory)

for file in file_names:
    if file.endswith(".cell"):
        sbatch_file = file_directory + "sbatch_" + file[:-5] + ".sh"
        sbatch_commands.append(f"sbatch {sbatch_file}")

# Write the combined sbatch script
with open(combined_sbatch_file, 'w') as f:
    f.write("#!/bin/bash\n")
    f.write('\n'.join(sbatch_commands))

# Make the combined sbatch script executable
os.chmod(combined_sbatch_file, 0o755)

# Submit the job array using the combined sbatch script
os.system(f"sbatch {combined_sbatch_file}")
