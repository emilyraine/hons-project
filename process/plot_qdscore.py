import pickle
import math
import util.mapelites as mapelites
import os
import statistics as stat
import matplotlib.pyplot as plt
import process.project_archive as prja
from util.config_reader import ConfigReader

def mean_flatten(array):
  output = []
  for i in range(len(array)):
    output.append(stat.mean(array[i]))
  return output

def graph(variant, runs=20, generations=100):
  MAX_QDSCORE = 17.493333333333336
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

    folders = [("output/" + folder) for folder in os.listdir("output") if folder.startswith("run_" + prefix)]

    if not folders:
      continue

    if len(folders) > MAX_RUNS:
      folders = folders[:MAX_RUNS]

    AGGREGATE_ARRAY = None

    folder_count = 0

    for folder in folders:
      if os.path.exists(folder + "/checkpoints/gen_" + str(generations) + ".pkl"):
        flag = AGGREGATE_ARRAY is None
        if flag:
          AGGREGATE_ARRAY = []
        for i in range(1, generations+1):
          if flag:
            AGGREGATE_ARRAY.append([])
          CHECKPOINT_FILENAME = folder + "/checkpoints/gen_" + str(i) + ".pkl"
          if "ssga" in folder or "dns" in folder or "nsslc" in folder:
            grid = prja.project(CHECKPOINT_FILENAME)
            fitness_grid = grid.quality_array
          else:
            with open(CHECKPOINT_FILENAME, "rb") as cp_file:
              CHECKPOINT = pickle.load(cp_file)
            POPULATION = CHECKPOINT["pop"]
            CONFIG_FILENAME = CHECKPOINT["cfg"]
            CONFIG = ConfigReader(CONFIG_FILENAME)
            mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]"), POPULATION)
            fitness_grid = mapelites.grid.quality_array
          qd_score = 0
          for x in range(len(fitness_grid)):
            for y in range(len(fitness_grid[x])):
              for z in range(len(fitness_grid[x][y])):
                if not math.isnan(fitness_grid[x][y][z]):
                  qd_score += fitness_grid[x][y][z][0]
          AGGREGATE_ARRAY[i-1].append(qd_score)
        folder_count += 1
      else:
        print("Skipping run: " + (folder + "/checkpoints/gen_" + str(generations) + ".pkl") + " is missing.")

    AGGREGATE_ARRAY = mean_flatten(AGGREGATE_ARRAY)
    AGGREGATE_ARRAY = [val / MAX_QDSCORE for val in AGGREGATE_ARRAY]
    parts = prefix.split('-')
    env_code = parts[2] if len(parts) > 2 else None
    dif_level = parts[1]
    algorithm = parts[0]
    style = "-" if dif_level == "d" else "--"

    if algorithm == "dns":
        color = "r"
    elif algorithm == "ssga":
        color = "b"
    elif algorithm == "nsslc": 
        color = "g"

    plt.plot(AGGREGATE_ARRAY, label=prefix, c=color, ls=style)

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

  plt.gcf().subplots_adjust(top=0.92)
  plt.suptitle(title, fontsize=18, weight="bold", y=0.98)
  plt.xlabel("Generation", fontsize=14)
  plt.ylabel("Average QD score (normalised)", fontsize=14)
  plt.xlim(0, generations)
  plt.ylim(0, 1)
  plt.xticks(fontsize=14)
  plt.yticks(fontsize=14)
  plt.legend(loc="upper left", fontsize=10)
  plt.savefig("output/qdscore-" + variant + ".png", bbox_inches='tight', pad_inches=0.2)