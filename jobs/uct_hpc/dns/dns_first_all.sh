#!/bin/sh
#SBATCH --account=compsci
#SBATCH --partition=ada
#SBATCH --time=20:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --constraint=small
#SBATCH --job-name="dns_first_all"
#SBATCH --output=/scratch/rnxemi001/jobs/dns_first_all.out 
#SBATCH --error=/scratch/rnxemi001/jobs/dns_first_all.err 
#SBATCH --mail-user=rnxemi001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/rnxemi001/hons-project3

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_no-maze.properties dns-e-nm-01
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-easy.properties dns-e-e-01
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-01
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-difficult.properties dns-e-d-01


conda deactivate

