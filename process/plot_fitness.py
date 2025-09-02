import pickle
import os
import math
import util.mapelites as mapelites
import statistics as stat
import matplotlib.pyplot as plt
from util.config_reader import ConfigReader

def mean_flatten(array):
  output = []
  for i in range(len(array)):
    output.append(stat.mean(array[i]))
  return output

def graph(variant, runs=20, generations=100):

  MAX_RUNS = runs

  if variant == "all-nm":
    AGGREGATE_PREFIXES = ["dns-e-nm", "dns-d-nm", "nsslc-e-nm", "nsslc-d-nm", "ssga-e-nm", "ssga-d-nm"] 
  elif variant == "all-e":
    AGGREGATE_PREFIXES = ["dns-e-e", "dns-d-e", "nsslc-e-e", "nsslc-d-e", "ssga-e-e", "ssga-d-e"] 
  elif variant == "all-m":
    AGGREGATE_PREFIXES = ["dns-e-m", "dns-d-m", "nsslc-e-m", "nsslc-d-m", "ssga-e-m", "ssga-d-m"]
  elif variant == "all-d":
    AGGREGATE_PREFIXES = ["dns-e-d", "dns-d-d", "nsslc-e-d", "nsslc-d-d", "ssga-e-d", "ssga-d-d"]

  for prefix in AGGREGATE_PREFIXES:
    folder_count = 0
    folders = [("output/" + folder) for folder in os.listdir("output") if folder.startswith("run_" + prefix)]
    if not folders:
      continue

    if len(folders) > MAX_RUNS:
      folders = folders[:MAX_RUNS]

    AGGREGATE_MEAN_ARRAY = None
    AGGREGATE_MAX_ARRAY = None


    for folder in folders:
      if os.path.exists(folder + "/checkpoints/gen_" + str(generations) + ".pkl"):
        flag = AGGREGATE_MEAN_ARRAY is None
        if flag:
          AGGREGATE_MEAN_ARRAY = []
          AGGREGATE_MAX_ARRAY = []
        for i in range(1, generations+1):
          if flag:
            AGGREGATE_MEAN_ARRAY.append([])
            AGGREGATE_MAX_ARRAY.append([])
          CHECKPOINT_FILENAME = folder + "/checkpoints/gen_" + str(i) + ".pkl"
          if "ssga" in folder or "dns" in folder or "nsslc" in folder:
            with open(CHECKPOINT_FILENAME, "rb") as cp_file:
              CHECKPOINT = pickle.load(cp_file)
            POPULATION = CHECKPOINT["pop"]
            total = 0
            max = 0
            sum = 0
            for ind in POPULATION:
              fitness = ind.fitness.values[0]
              total += 1
              sum += fitness
              if fitness > max:
                max = fitness
          else:
            with open(CHECKPOINT_FILENAME, "rb") as cp_file:
              CHECKPOINT = pickle.load(cp_file)
            POPULATION = CHECKPOINT["pop"]
            CONFIG_FILENAME = CHECKPOINT["cfg"]
            CONFIG = ConfigReader(CONFIG_FILENAME)
            mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]"), POPULATION)
            fitness_grid = mapelites.grid.quality_array
            total = 0
            max = 0
            sum = 0
            for x in range(len(fitness_grid)):
              for y in range(len(fitness_grid[x])):
                for z in range(len(fitness_grid[x][y])):
                  if not math.isnan(fitness_grid[x][y][z]):
                    fitness = fitness_grid[x][y][z][0]
                    total += 1
                    sum += fitness
                    if fitness > max:
                      max = fitness
          AGGREGATE_MEAN_ARRAY[i-1].append(sum/total)
          AGGREGATE_MAX_ARRAY[i-1].append(max)
        folder_count += 1
      else:
        print("Skipping run: " + (folder + "/checkpoints/gen_" + str(generations) + ".pkl") + " is missing.")

    AGGREGATE_MEAN_ARRAY = mean_flatten(AGGREGATE_MEAN_ARRAY)   
    AGGREGATE_MAX_ARRAY = mean_flatten(AGGREGATE_MAX_ARRAY)

    parts = prefix.split('-')
    dif_level = parts[1]
    algorithm = parts[0]
    style = "-" if dif_level == "d" else "--"

    if algorithm == "dns":
        color = "r"
    elif algorithm == "ssga":
        color = "b"
    elif algorithm == "nsslc": 
        color = "g"

    plt.figure(1)
    plt.plot(AGGREGATE_MEAN_ARRAY, label=prefix, c=color, ls=style)

    plt.figure(2)
    plt.plot(AGGREGATE_MAX_ARRAY, label=prefix, c=color, ls=style)

    print("Results plotted for " + str(folder_count) + " run(s).")

  variant_parts = variant.split("-")
  if variant_parts[1] == "nm":
      title = "No Maze"
  elif variant_parts[1] == "e":
      title = "Easy Maze"
  elif variant_parts[1] == "m": 
      title = "Medium Maze"
  elif variant_parts[1] == "d": 
      title = "Difficult Maze"

  plt.figure(1)
  plt.suptitle(title, weight="bold")
  plt.xlabel("Generation")
  plt.ylabel("Average mean fitness")
  plt.xlim(0, generations)
  plt.ylim(bottom=0, top=0.5)
  plt.legend(loc="upper left")
  plt.savefig("output/fitness-mean-" + variant + ".png", bbox_inches='tight', pad_inches=0.2)

  plt.figure(2)
  plt.suptitle(title, weight="bold")
  plt.xlabel("Generation")
  plt.ylabel("Average max fitness")
  plt.xlim(0, generations)
  plt.ylim(bottom=0, top=1.0)
  plt.legend(loc="upper left")
  plt.savefig("output/fitness-max-" + variant + ".png", bbox_inches='tight', pad_inches=0.2)