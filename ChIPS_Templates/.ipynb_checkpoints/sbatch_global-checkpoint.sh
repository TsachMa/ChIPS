#!/bin/bash
#SBATCH -p sched_mit_hill
#SBATCH -N 1
#SBATCH -n 4
#SBATCH --array=1
#SBATCH --time=04:00:00
#SBATCH --output=output_%j.txt
#SBATCH --error=error_%j.txt

module add gcc/6.2.0
module add fftw/3.3.8 openblas/0.3.6 openmpi/3.0.4

echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"

mpirun -np 4 castep.mpi
