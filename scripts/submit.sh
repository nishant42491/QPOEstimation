#!/bin/bash
#
#SBATCH --job-name=test
#
#SBATCH --ntasks=1
#SBATCH --time=3:00:00
#SBATCH --mem-per-cpu=1G

#srun python sliding_window.py ${1} ${2} 0
#srun python sliding_window.py ${1} ${2} 1

# Candidate runs
srun python sliding_window.py ${1} 0
srun python sliding_window.py ${1} 1
