import os
import csv
import statistics as stat
import matplotlib.pyplot as plt
import numpy as np

def mean_flatten(array):
    output = []
    for i in range(len(array)):
        output.append(stat.mean(array[i]))
    return output

def read_morph_results(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        data = {
            'generations': [],
            'fitness': {'mean': [], 'max': []},
            'morphology': {'mean': [], 'max': []},
            'capture': {'mean': [], 'max': []}
        }
        
        for row in reader:
            data['generations'].append(int(row['gen']))
            data['fitness']['mean'].append(float(row['fit-avg']))
            data['fitness']['max'].append(float(row['fit-max']))
            data['morphology']['mean'].append(float(row['mrph-avg']))
            data['morphology']['max'].append(float(row['mrph-max']))
            data['capture']['mean'].append(float(row['cap-avg']))
            data['capture']['max'].append(float(row['cap-max']))
    return data

def graph(variant, runs=20, generations=200):
    """
    Generate evolution plots for morphological experiments.
    
    Parameters:
    - variant: str, either "morph" or "fixed" for the respective results
    - runs: int, maximum number of runs to process
    - generations: int, number of generations to plot
    """
    # Define directory and prefix based on variant
    if variant == "morph":
        base_dir = "output/morph-results/"
        prefix = "morph-icemud-e"
    elif variant == "fixed":
        base_dir = "output/fixed-results/"
        prefix = "ice-mud-easy-15-fixed"
    else:
        raise ValueError(f"Unsupported variant: {variant}")
        
    if not os.path.exists(base_dir + prefix):
        print(f"Directory not found: {base_dir + prefix}")
        return
            
    # Get all run folders
    folders = [(base_dir + prefix + "/" + folder) 
              for folder in os.listdir(base_dir + prefix) 
              if folder.startswith("run_")]
              
    if len(folders) > runs:
        folders = folders[:runs]
        
    # Initialize aggregation arrays
    agg_data = {
        'fitness': {'mean': [], 'max': []},
        'morphology': {'mean': [], 'max': []},
        'capture': {'mean': [], 'max': []}
    }
    
    # Process each run
    processed_runs = 0
    for folder in folders:
        results_file = folder + "/results.csv"
        if os.path.exists(results_file):
            run_data = read_morph_results(results_file)
            
            # Initialize arrays on first run
            if not agg_data['fitness']['mean']:
                for metric in agg_data:
                    agg_data[metric]['mean'] = [[] for _ in run_data['generations']]
                    agg_data[metric]['max'] = [[] for _ in run_data['generations']]
            
            # Aggregate data
            for i in range(len(run_data['generations'])):
                for metric in ['fitness', 'morphology', 'capture']:
                    agg_data[metric]['mean'][i].append(run_data[metric]['mean'][i])
                    agg_data[metric]['max'][i].append(run_data[metric]['max'][i])
            processed_runs += 1
    
    if processed_runs == 0:
        print("No valid results files found")
        return
        
    # Flatten aggregated data
    for metric in agg_data:
        agg_data[metric]['mean'] = mean_flatten(agg_data[metric]['mean'])
        agg_data[metric]['max'] = mean_flatten(agg_data[metric]['max'])
    
    # Create plots
    metrics = {
        'fitness': 'Task Performance',
        'morphology': 'Morphological Complexity',
        'capture': 'Capture Ratio'
    }
    
    for i, (metric, title) in enumerate(metrics.items()):
        plt.figure(i+1, figsize=(10, 6))
        plt.plot(agg_data[metric]['mean'], label='Mean', color='blue', linestyle='-')
        plt.plot(agg_data[metric]['max'], label='Maximum', color='red', linestyle='--')
        
        plt.title(f'Evolution of {title}', fontsize=12, pad=20)
        plt.xlabel('Generation', fontsize=10)
        plt.ylabel(title, fontsize=10)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend(fontsize=10)
        
        # Save plot
        plt.savefig(f'output/{metric}-evolution-{variant}.png', 
                   bbox_inches='tight', 
                   dpi=300,
                   pad_inches=0.2)
        plt.close()
            
    print(f"Results plotted for {processed_runs} run(s) of {prefix}")
    print(f"Plots saved as [metric]-evolution-{variant}.png")
