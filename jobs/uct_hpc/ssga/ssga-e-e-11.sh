#!/bin/sh
#SBATCH --account=compsci
#SBATCH --partition=ada
#SBATCH --time=10:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --job-name="ssga-e-e-11"
#SBATCH --output=/scratch/rnxemi001/jobs/ssga-e-e-11.out 
#SBATCH --error=/scratch/rnxemi001/jobs/ssga-e-e-11.err 
#SBATCH --mail-user=rnxemi001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/rnxemi001/hons-project

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-easy.properties ssga-e-e-11

conda deactivate

