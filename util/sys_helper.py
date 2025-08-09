import os
import multiprocessing

# Get the number of CPUs allocated to the job
def get_hpc_cpu_count():
    try: 
      pbs_cpus = os.environ.get("PBS_NCPUS")
      if pbs_cpus:
         return int(pbs_cpus)
      
      slurm_cpus = os.environ.get("SLURM_JOB_CPUS_PER_NODE")
      if slurm_cpus:
        return int(slurm_cpus.strip().split('(')[0]) # Single-node job
      
      return multiprocessing.cpu_count()
    except ValueError:
      return multiprocessing.cpu_count()