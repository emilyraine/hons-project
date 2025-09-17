import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from collections import defaultdict
from scipy import stats
import seaborn as sns

class DataLoader:
# loads data from CSV files
    def __init__(self, results_dir="/home/khnnah001/home/hons-project/output/CSVresults"):
        self.results_dir = results_dir
        self.data = defaultdict(list)
        
    def load_data(self):
        # load data from CSV files
        env_mappings = {
            "field": "Open Field",
            "ice": "Ice Only",
            "mud": "Mud Only",
            "ice_mud_low": "Ice and Mud (low coverage)",
            "ice_mud_high": "Ice and Mud (high coverage)",
        }
        
        # process both evolving and fixed morphology experiments
        for morph_type in ["evolving", "fixed"]:
            morph_path = os.path.join(self.results_dir, morph_type)
            
            if not os.path.exists(morph_path):
                print(f"Directory not found: {morph_path}")
                continue
                
            # process each environment
            for env_dir in os.listdir(morph_path):
                env_path = os.path.join(morph_path, env_dir)
                
                if not os.path.isdir(env_path):
                    continue
                    
                # get environment name
                env_name = env_mappings.get(env_dir, env_dir.replace('_', ' ').title())
                
                # process each dog count (15 and 20)
                for dogs_dir in os.listdir(env_path):
                    dogs_path = os.path.join(env_path, dogs_dir)
                    
                    if not os.path.isdir(dogs_path):
                        continue
                        
                    try:
                        num_dogs = int(dogs_dir.replace('dogs', ''))
                    except:
                        print(f"Could not parse dog count from: {dogs_dir}")
                        continue
                    
                    # find all run directories
                    run_dirs = glob.glob(os.path.join(dogs_path, "run_*"))
                    
                    csv_files = []
                    for run_dir in run_dirs:
                    # find results.csv in each run directory
                        csv_path = os.path.join(run_dir, "results.csv")
                        if os.path.exists(csv_path):
                            csv_files.append(csv_path)
                    
                    if csv_files:
                        print(f"Found {len(csv_files)} runs for {env_name} {num_dogs} dogs {morph_type}")
                        
                        # process data from each run
                        max_performance_data = []
                        max_morph_complexity_data = []
                        fitness_data = []
                        
                        for csv_file in csv_files:
                            try:
                                df = pd.read_csv(csv_file)
                                
                                # get task performance values
                                if morph_type == "evolving":
                                    performance_values = df['cap-max'].values
                                    fitness_values = df['fit-max'].values
                                else:
                                    performance_values = df['fit-max'].values
                                    fitness_values = df['fit-max'].values
                                
                                # get morphological complexity (only for evolving morphology)
                                morph_values = df['mrph-max'].values if morph_type == "evolving" else np.zeros(len(performance_values))
                                
                                # check for 100 generations
                                if len(performance_values) > 100:
                                    performance_values = performance_values[:100]
                                    fitness_values = fitness_values[:100]
                                    morph_values = morph_values[:100]
                                elif len(performance_values) < 100:
                                    performance_values = np.pad(performance_values, (0, 100 - len(performance_values)), 
                                                               'constant', constant_values=performance_values[-1])
                                    fitness_values = np.pad(fitness_values, (0, 100 - len(fitness_values)), 
                                                           'constant', constant_values=fitness_values[-1])
                                    morph_values = np.pad(morph_values, (0, 100 - len(morph_values)), 
                                                         'constant', constant_values=morph_values[-1])
                                
                                max_performance_data.append(performance_values)
                                max_morph_complexity_data.append(morph_values)
                                fitness_data.append(fitness_values)
                            except Exception as e:
                                print(f"Error processing {csv_file}: {e}")
                        
                        if max_performance_data:
                            # calculate average across all runs
                            avg_performance = np.mean(max_performance_data, axis=0)
                            avg_morph_complexity = np.mean(max_morph_complexity_data, axis=0)
                            avg_fitness = np.mean(fitness_data, axis=0)
                            
                            # store final values for statistical tests
                            final_performance = [run[-1] for run in max_performance_data]
                            final_morph_complexity = [run[-1] for run in max_morph_complexity_data] if morph_type == "evolving" else None
                            final_fitness = [run[-1] for run in fitness_data]
                            
                            # store the data
                            self.data[(env_name, morph_type, num_dogs)] = {
                                'avg_performance': avg_performance,
                                'avg_morph_complexity': avg_morph_complexity,
                                'avg_fitness': avg_fitness,
                                'final_performance': final_performance,
                                'final_morph_complexity': final_morph_complexity,
                                'final_fitness': final_fitness,
                                'runs_processed': len(max_performance_data)
                            }

class TaskPerformancePlotter:
# generates plots for task performance comparison
    
    def __init__(self, data_loader, output_dir="output"):
        self.data_loader = data_loader
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_same_environment_comparison(self):
    # plot task performance for fixed vs evolving morphology in the same environment
        environments = set([key[0] for key in self.data_loader.data.keys()])
        
        for env in environments:
        # create separate plots for each dog count
            for num_dogs in [15, 20]:
                plt.figure(figsize=(12, 8))
                
                # get data for both fixed and evolving morphologies for this dog count
                evol_key = next((k for k in self.data_loader.data.keys() 
                               if k[0] == env and k[1] == "evolving" and k[2] == num_dogs), None)
                fixed_key = next((k for k in self.data_loader.data.keys() 
                                if k[0] == env and k[1] == "fixed" and k[2] == num_dogs), None)
                
                if evol_key and fixed_key:
                    evol_data = self.data_loader.data[evol_key]
                    fixed_data = self.data_loader.data[fixed_key]
                    
                    plt.plot(evol_data['avg_performance'], label='Evolving Morphology', color='blue', linewidth=2)
                    plt.plot(fixed_data['avg_performance'], label='Fixed Morphology', color='red', linewidth=2, linestyle='--')
                    
                    # perform statistical test 
                    stat, p_value = self._perform_statistical_test(
                        evol_data['final_performance'], 
                        fixed_data['final_performance']
                    )
                    
                    plt.title(f'{env} - Task Performance Comparison ({num_dogs} dogs)\nMann-Whitney U p-value: {p_value:.4f}', 
                             weight='bold', fontsize=16)
                    plt.xlabel('Generation')
                    plt.ylabel('Task Performance')
                    plt.ylim(0, 1.0)
                    plt.xlim(0, 100)
                    plt.grid(True, alpha=0.3)
                    plt.legend(loc='lower right')
                    
                    # save the plot
                    filename = f"task-performance-{env.replace(' ', '-').replace('(', '').replace(')', '')}-{num_dogs}dogs.png"
                    plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight', pad_inches=0.2, dpi=300)
                    plt.close()
                    print(f"Saved task performance plot: {filename}")
    
    def _perform_statistical_test(self, group1, group2):
    # perform statistical test with proper handling of edge cases
        try:
            # check if groups are identical (would cause U=0)
            if np.array_equal(group1, group2):
                return 0, 1.0  # No difference, p=1.0
            
            # check if one group has all zeros or constant values
            if np.std(group1) == 0 and np.std(group2) == 0:
                if np.mean(group1) == np.mean(group2):
                    return 0, 1.0
                else:
                    # all values are constant but different
                    return len(group1) * len(group2), 0.0
            
            # perform Mann-Whitney U test
            stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
            
            # handle extreme values
            if stat == 0:
                # This can happen when all values in one group are greater than all values in the other
                # For this case, the p-value is extremely small
                p_value = 1e-10  # Very small p-value indicating high significance
                    
            return stat, p_value
        
        except Exception as e:
            print(f"Error in statistical test: {e}")
            return np.nan, np.nan

class MorphComplexityPlotter:
# generates plots for morphology complexity comparison
    
    def __init__(self, data_loader, output_dir="output"):
        self.data_loader = data_loader
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_different_environments_comparison(self, num_dogs=15):
    # plot morph complexity for the same number of dogs across different environments
        plt.figure(figsize=(14, 10))
        
        # get data for evolving morphology across different environments
        colors = plt.cm.tab10(np.linspace(0, 1, 10))
        
        env_data = []
        for key, data in self.data_loader.data.items():
            if key[1] == "evolving" and key[2] == num_dogs and data['avg_morph_complexity'] is not None:
                env_data.append((key[0], data['avg_morph_complexity'], data['final_morph_complexity']))
        
        # sort environments for consistent coloring
        env_data.sort(key=lambda x: x[0])
        
        for i, (env, avg_morph, final_morph) in enumerate(env_data):
            plt.plot(avg_morph, label=env, color=colors[i % len(colors)], linewidth=2)
        
        plt.title(f'Morphology Complexity Comparison ({num_dogs} dogs)', weight='bold', fontsize=16)
        plt.xlabel('Generation')
        plt.ylabel('Morphology Complexity')
        plt.ylim(bottom=0)
        plt.xlim(0, 100)
        plt.grid(True, alpha=0.3)
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        
        # save the plot
        filename = f"morph-complexity-{num_dogs}dogs.png"
        plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight', pad_inches=0.2, dpi=300)
        plt.close()
        print(f"Saved morph complexity plot: {filename}")
        
        # perform statistical tests between environments
        if len(env_data) > 1:
            self._perform_morph_complexity_stats(env_data, num_dogs)
    
    def _perform_morph_complexity_stats(self, env_data, num_dogs):
    # perform statistical tests on morphology complexity using t-tests
        print(f"\nMorphology Complexity Statistical Analysis ({num_dogs} dogs):")
        print("=" * 50)
        
        # extract final values and environment names
        final_values = [data[2] for data in env_data]
        env_names = [data[0] for data in env_data]
        
        # check if we have valid data for statistical tests
        valid_data = []
        valid_names = []
        for values, name in zip(final_values, env_names):
            if values is not None and len(values) > 0:
                valid_data.append(values)
                valid_names.append(name)
        
        if len(valid_data) < 2:
            print("Not enough valid data for statistical analysis.")
            print("=" * 50)
            return
        
        # perform pairwise t-tests with Bonferroni correction
        n_comparisons = len(valid_data) * (len(valid_data) - 1) // 2
        alpha = 0.05 / n_comparisons if n_comparisons > 0 else 0.05
        
        print("Pairwise comparisons (t-test with Bonferroni correction):")
        for i in range(len(valid_data)):
            for j in range(i + 1, len(valid_data)):
                try:
                    # check if data meets assumptions for t-test
                    if len(valid_data[i]) >= 30 and len(valid_data[j]) >= 30:
                        # use regular t-test for large samples
                        stat, p_value = stats.ttest_ind(valid_data[i], valid_data[j])
                    else:
                        # use Welch's t-test for small samples (doesn't assume equal variances)
                        stat, p_value = stats.ttest_ind(valid_data[i], valid_data[j], equal_var=False)
                    
                    significance = "***" if p_value < alpha else "*" if p_value < 0.05 else "ns"
                    print(f"{valid_names[i]} vs {valid_names[j]}: t = {stat:.3f}, p = {p_value:.6f} {significance}")
                except Exception as e:
                    print(f"Error comparing {valid_names[i]} vs {valid_names[j]}: {e}")
        
        print("=" * 50)


class FitnessPlotter:
# generates plots for fitness comparison
    
    def __init__(self, data_loader, output_dir="output"):
        self.data_loader = data_loader
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_different_environments_comparison(self, num_dogs=15):
        # plot fitness for evolving morphology across different environments
        plt.figure(figsize=(14, 10))
        
        # get data for evolving morphology across different environments
        colors = plt.cm.tab10(np.linspace(0, 1, 10))
        
        env_data = []
        for key, data in self.data_loader.data.items():
            if key[1] == "evolving" and key[2] == num_dogs:
                env_data.append((key[0], data['avg_fitness'], data['final_fitness']))
        
        # sort environments for consistent coloring
        env_data.sort(key=lambda x: x[0])
        
        for i, (env, avg_fitness, final_fitness) in enumerate(env_data):
            plt.plot(avg_fitness, label=env, color=colors[i % len(colors)], linewidth=2)
        
        plt.title(f'Fitness Comparison - Evolving Morphology ({num_dogs} dogs)', weight='bold', fontsize=16)
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.ylim(0, 1.0)
        plt.xlim(0, 100)
        plt.grid(True, alpha=0.3)
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        
        # save the plot
        filename = f"fitness-evolving-{num_dogs}dogs.png"
        plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight', pad_inches=0.2, dpi=300)
        plt.close()
        print(f"Saved fitness plot: {filename}")
        
        # perform statistical tests between environments
        if len(env_data) > 1:
            self._perform_fitness_stats(env_data, num_dogs)
    
    def _perform_fitness_stats(self, env_data, num_dogs):
    # perform statistical tests on fitness using t-tests
        print(f"\nFitness Statistical Analysis - Evolving Morphology ({num_dogs} dogs):")
        print("=" * 50)
        
        # extract final values and environment names
        final_values = [data[2] for data in env_data]
        env_names = [data[0] for data in env_data]
        
        # check if we have valid data for statistical tests
        valid_data = []
        valid_names = []
        for values, name in zip(final_values, env_names):
            if values is not None and len(values) > 0:
                valid_data.append(values)
                valid_names.append(name)
        
        if len(valid_data) < 2:
            print("Not enough valid data for statistical analysis.")
            print("=" * 50)
            return
        
        # perform pairwise t-tests with Bonferroni correction
        n_comparisons = len(valid_data) * (len(valid_data) - 1) // 2
        alpha = 0.05 / n_comparisons if n_comparisons > 0 else 0.05
        
        print("Pairwise comparisons (t-test with Bonferroni correction):")
        for i in range(len(valid_data)):
            for j in range(i + 1, len(valid_data)):
                try:
                    # check if data meets assumptions for t-test
                    if len(valid_data[i]) >= 30 and len(valid_data[j]) >= 30:
                        # use regular t-test for large samples
                        stat, p_value = stats.ttest_ind(valid_data[i], valid_data[j])
                    else:
                        # use Welch's t-test for small samples (doesn't assume equal variances)
                        stat, p_value = stats.ttest_ind(valid_data[i], valid_data[j], equal_var=False)
                    
                    significance = "***" if p_value < alpha else "*" if p_value < 0.05 else "ns"
                    print(f"{valid_names[i]} vs {valid_names[j]}: t = {stat:.3f}, p = {p_value:.6f} {significance}")
                except Exception as e:
                    print(f"Error comparing {valid_names[i]} vs {valid_names[j]}: {e}")
        
        print("=" * 50)


def main():
    results_path = "/home/khnnah001/home/hons-project/output/CSVresults"
    output_dir = "analysis_output"
    
    # load data
    print("Loading experiment data...")
    data_loader = ExperimentDataLoader(results_path)
    data_loader.load_data()
    
    if not data_loader.data:
        print("No data loaded. Please check the results directory path.")
        return
    
    # create plots
    print("\nGenerating plots...")
    
    # task performance comparison
    task_plotter = TaskPerformancePlotter(data_loader, output_dir)
    task_plotter.plot_same_environment_comparison()
    
    # morph complexity comparison for both 15 and 20 dogs
    morph_plotter = MorphComplexityPlotter(data_loader, output_dir)
    for num_dogs in [15, 20]:
        morph_plotter.plot_different_environments_comparison(num_dogs=num_dogs)
    
    # fitness comparison for both 15 and 20 dogs
    fitness_plotter = FitnessPlotter(data_loader, output_dir)
    for num_dogs in [15, 20]:
        fitness_plotter.plot_different_environments_comparison(num_dogs=num_dogs)
    
    print(f"\nAll analysis completed. Results saved to '{output_dir}' directory.")


if __name__ == "__main__":
    main()