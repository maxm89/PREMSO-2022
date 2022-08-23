#!/bin/bash
#SBATCH --output linkern_pp.%N.%j.out # stdout and stderr
#SBATCH --partition hpc3          # partition (queue)
#SBATCH --cpus-per-task 32
#SBATCH --mem 10G
#SBATCH --time 71:00:00              # (format D-HH:MM:SS)
