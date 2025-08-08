#!/bin/sh
#SBATCH --account=compsci
#SBATCH --partition=ada
#SBATCH --time=40:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --constraint=small
#SBATCH --job-name="dns-e-m-15"
#SBATCH --output=/scratch/rnxemi001/jobs/dns-e-m-15.out 
#SBATCH --error=/scratch/rnxemi001/jobs/dns-e-m-15.err 
#SBATCH --mail-user=rnxemi001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/rnxemi001/hons-project3

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-02
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-03
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-04
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-05
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-06
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-07
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-08
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-09
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-10
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-11
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-12
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-13
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-14
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-easy_maze-medium.properties dns-e-m-15

conda deactivate

