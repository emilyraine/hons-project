#!/bin/sh
#SBATCH --account=compsci
#SBATCH --partition=ada
#SBATCH --time=40:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --constraint=small
#SBATCH --job-name="dns-d-nm-15"
#SBATCH --output=/scratch/rnxemi001/jobs/dns-d-nm-15.out 
#SBATCH --error=/scratch/rnxemi001/jobs/dns-d-nm-15.err 
#SBATCH --mail-user=rnxemi001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/rnxemi001/hons-project3 

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-01
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-02
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-03
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-04
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-05
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-06
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-07
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-08
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-09
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-10
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-11
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-12
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-13
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-14
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_no-maze.properties dns-d-nm-15

conda deactivate

