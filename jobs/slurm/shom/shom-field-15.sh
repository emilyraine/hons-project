#!/bin/sh
#SBATCH --account=maths
#SBATCH --partition=ada
#SBATCH --time=46:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --constraint=small
#SBATCH --job-name="shom-field-15_fixed"
#SBATCH --output=/scratch/khnnah001/jobs/shom-field-15_fixed.out 
#SBATCH --error=/scratch/khnnah001/jobs/shom-field-15_fixed.err 
#SBATCH --mail-user=khnnah001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/khnnah001/hons-project

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_1
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_2
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_3
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_4
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_5
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_6
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_7
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_8
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_9
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_10
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_11
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_12
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_13
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_14
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_15
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_16
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_17
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_18
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_19
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/shom/shom-field-15.properties field-15-fixed_20


conda deactivate
