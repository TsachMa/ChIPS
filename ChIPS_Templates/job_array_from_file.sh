#!/bin/bash
#SBATCH --partition=xeon-p8
#SBATCH -N <NUM_FILES>
#SBATCH -n 8
#SBATCH --mem=4500
#SBATCH --time=04:00:00
#SBATCH --output="output/%A_output_%a.txt"
#SBATCH --error="error/%A_error_%a.txt"

echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"

module add mpi/openmpi-4.1.3

mapfile -t file_names < <FILE_NAME>  # Read file names from nbands_files.txt

file=${file_names[$SLURM_ARRAY_JOB_ID-1]}

echo "Running job ${SLURM_ARRAY_JOB_ID}.${SLURM_ARRAY_TASK_ID}"
echo "File: $file"
echo "Compound: "${file: 0:-7}"

mpirun -np 8 castep.mpi ${file: 0:-7}
