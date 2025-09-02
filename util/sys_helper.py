import multiprocessing

# Get the number of CPUs allocated to the job
def get_hpc_cpu_count():
    return multiprocessing.cpu_count()