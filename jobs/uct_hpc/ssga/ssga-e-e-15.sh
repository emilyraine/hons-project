#!/bin/sh
#SBATCH --account=compsci
#SBATCH --partition=ada
#SBATCH --time=25:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --job-name="ssga-e-e-15"
#SBATCH --output=/scratch/rnxemi001/jobs/ssga-e-e-15.out 
#SBATCH --error=/scratch/rnxemi001/jobs/ssga-e-e-15.err 
#SBATCH --mail-user=rnxemi001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/rnxemi001/hons-project

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-easy.properties ssga-e-e-06
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-easy.properties ssga-e-e-07
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-easy.properties ssga-e-e-08
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-easy.properties ssga-e-e-09
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-easy.properties ssga-e-e-10
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-easy.properties ssga-e-e-12
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-easy.properties ssga-e-e-13
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-easy.properties ssga-e-e-14
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-easy.properties ssga-e-e-15

conda deactivate

