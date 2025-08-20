#!/bin/sh
#SBATCH --account=maths
#SBATCH --partition=ada
#SBATCH --time=50:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --constraint=small
#SBATCH --job-name="shom-mud-20"
#SBATCH --output=/scratch/khnnah001/jobs/shom-mud-20.out 
#SBATCH --error=/scratch/khnnah001/jobs/shom-mud-20.err 
#SBATCH --mail-user=khnnah001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/khnnah001/hons-project-1

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_1
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_2
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_3
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_4
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_5
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_6
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_7
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_8
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_9
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_10
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_11
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_12
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_13
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_14
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_20
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_16
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_17
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_18
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_19
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-mud-20.properties mud-20_20


conda deactivate