#!/bin/sh
#SBATCH --account=compsci
#SBATCH --partition=ada
#SBATCH --time=60:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --job-name="nsslc-e-nm-20"
#SBATCH --output=/scratch/rnxemi001/jobs/nsslc-e-nm-20.out 
#SBATCH --error=/scratch/rnxemi001/jobs/nsslc-e-nm-20.err 
#SBATCH --mail-user=rnxemi001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/rnxemi001/hons-project 

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-01
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-02
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-03
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-04
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-05
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-06
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-07
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-08
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-09
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-10
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-11
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-12
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-13
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-14
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-15
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-16
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-17
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-18
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-19
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/nsslc/nsslc-easy_no-maze.properties nsslc-e-nm-20

conda deactivate

