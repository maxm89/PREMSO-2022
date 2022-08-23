#!/bin/bash
#SBATCH --ntasks=1 --nodes=1 --exclusive
#SBATCH --ntasks-per-core=1
#SBATCH --time=00:00:01
#SBATCH --job-name=empty_job



# sbatch does not work without partition=..., when there is no default partition
### SBATCH --partition=k40
### SBATCH --gres=gpu:k40:2AK) partition
