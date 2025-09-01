#!/bin/sh
#SBATCH --account=compsci
#SBATCH --partition=ada
#SBATCH --time=36:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --job-name="ssga-e-d-20"
#SBATCH --output=/scratch/rnxemi001/jobs/ssga-e-d-20.out 
#SBATCH --error=/scratch/rnxemi001/jobs/ssga-e-d-20.err 
#SBATCH --mail-user=rnxemi001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/rnxemi001/hons-project 

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-01
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-02
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-03
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-04
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-05
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-06
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-07
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-08
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-09
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-10
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-11
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-12
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-13
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-14
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-15
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-16
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-17
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-18
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-19
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-20

conda deactivate

