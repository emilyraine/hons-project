#!/bin/sh
#SBATCH --account=compsci
#SBATCH --partition=ada
#SBATCH --time=13:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --constraint=small
#SBATCH --job-name="ssga_first_m_d"
#SBATCH --output=/scratch/rnxemi001/jobs/ssga_first_m_d.out 
#SBATCH --error=/scratch/rnxemi001/jobs/ssga_first_m_d.err 
#SBATCH --mail-user=rnxemi001@myuct.ac.za
#SBATCH --mail-type=ALL

ulimit -s unlimited

module purge
module load python/miniconda3-py3.9 

eval "$(conda shell.bash hook)"

conda activate roborobo

cd /scratch/rnxemi001/hons-project3

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-medium.properties ssga-e-m-01
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python run.py -s config/ssga/ssga-easy_maze-difficult.properties ssga-e-d-01


conda deactivate

