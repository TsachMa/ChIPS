#!/bin/bash
#SBATCH -N 1
#SBATCH -n 48
#SBATCH --array=1-<NUM_FILES>
#SBATCH --time=04:00:00
#SBATCH --output="output/%A_output_%a.txt"
#SBATCH --error="error/%A_error_%a.txt"

echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"

module add mpi/openmpi-4.1.3

file_names=(Synth_*.cell)

file=${file_names[$SLURM_ARRAY_TASK_ID-1]}

echo "Running job ${SLURM_ARRAY_JOB_ID}.${SLURM_ARRAY_TASK_ID}"
echo "File: $file"
echo "Compound: "${file: 0:-5}

mpirun -np 48 castep.mpi ${file: 0:-5}