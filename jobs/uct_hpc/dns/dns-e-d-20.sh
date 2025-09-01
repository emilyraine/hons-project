#!/bin/sh
#SBATCH --account=compsci
#SBATCH --partition=ada
#SBATCH --time=60:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --job-name="dns-e-d-20"
#SBATCH --output=/scratch/rnxemi001/jobs/dns-e-d-20.out 
#SBATCH --error=/scratch/rnxemi001/jobs/dns-e-d-20.err 
#SBATCH --mail-user=rnxemi001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/rnxemi001/hons-project 

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-01
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-02
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-03
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-04
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-05
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-06
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-07
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-08
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-09
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-10
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-11
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-12
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-13
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-14
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-15
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-16
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-17
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-18
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-19
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/dns/dns-difficult_maze-easy.properties dns-e-d-20

conda deactivate

