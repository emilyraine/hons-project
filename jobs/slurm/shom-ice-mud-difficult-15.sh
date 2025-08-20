#!/bin/sh
#SBATCH --account=maths
#SBATCH --partition=ada
#SBATCH --time=50:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --constraint=small
#SBATCH --job-name="shom-ice-mud-difficult-15"
#SBATCH --output=/scratch/khnnah001/jobs/shom-ice-mud-difficult-15.out 
#SBATCH --error=/scratch/khnnah001/jobs/shom-ice-mud-difficult-15.err 
#SBATCH --mail-user=khnnah001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/khnnah001/hons-project-1

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_1
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_2
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_3
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_4
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_5
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_6
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_7
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_8
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_9
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_10
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_11
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_12
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_13
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_14
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_15
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_16
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_17
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_18
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_19
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-ice-mud-difficult-15.properties ice-mud-difficult-15_20


conda deactivate