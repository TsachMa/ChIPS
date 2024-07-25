#!/bin/bash
#SBATCH -N 1
#SBATCH -n 4
#SBATCH --array=1
#SBATCH --mem=4500
#SBATCH --time=04:00:00
#SBATCH --output="output/%j_output.txt"
#SBATCH --error="error/%j_error.txt"

echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"

export OMPI_MCA_btl_openib_allow_ib=1

mpirun --mca btl self,openib -np 12 castep.mpi