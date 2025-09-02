import pickle
import scipy.stats as stats
import statistics as stat
import process.project_archive as prja
import os
import util.mapelites as mapelites
import math
from util.config_reader import ConfigReader

def calculate(variant, statistic, gen=100, runs=20):

  MAX_RUNS = runs

  if variant == "ssga-dns":
    AGGREGATE_PREFIXES = ["ssga-e-nm", "ssga-d-nm", "ssga-e-e", "ssga-d-e", "ssga-e-m", "ssga-d-m", "ssga-e-d", "ssga-d-d", "dns-e-nm",  "dns-d-nm",  "dns-e-e",  "dns-d-e",  "dns-e-m",  "dns-d-m",  "dns-e-d",  "dns-d-d"]
  elif variant == "ssga-nsslc":
    AGGREGATE_PREFIXES = ["ssga-e-nm", "ssga-d-nm", "ssga-e-e", "ssga-d-e", "ssga-e-m", "ssga-d-m", "ssga-e-d", "ssga-d-d", "nsslc-e-nm",  "nsslc-d-nm",  "nsslc-e-e",  "nsslc-d-e",  "nsslc-e-m",  "nsslc-d-m",  "nsslc-e-d",  "nsslc-d-d"]  
  elif variant == "nsslc-dns":
    AGGREGATE_PREFIXES = ["nsslc-e-nm", "nsslc-d-nm", "nsslc-e-e", "nsslc-d-e", "nsslc-e-m", "nsslc-d-m", "nsslc-e-d", "nsslc-d-d", "dns-e-nm",  "dns-d-nm",  "dns-e-e",  "dns-d-e",  "dns-e-m",  "dns-d-m",  "dns-e-d",  "dns-d-d"]

  AGGREGATE_DICT = {}

  for prefix in AGGREGATE_PREFIXES:

    folders = [("output/" + folder) for folder in os.listdir("output") if folder.startswith("run_" + prefix)]

    if len(folders) > MAX_RUNS:
      folders = folders[:MAX_RUNS]

    AGGREGATE_ARRAY = []

    folder_count = 0

    for folder in folders:
      CHECKPOINT_FILENAME = folder + "/checkpoints/gen_" + str(gen) + ".pkl"
      if os.path.exists(CHECKPOINT_FILENAME):
        with open(CHECKPOINT_FILENAME, "rb") as cp_file:
          CHECKPOINT = pickle.load(cp_file)
        if statistic == "fitness-mean":
          LOGBOOK = CHECKPOINT["log"]
          if "fitness" in LOGBOOK.chapters:
            results = LOGBOOK.chapters["fitness"].select("avg")
          else:
            results = LOGBOOK.select("avg")
          AGGREGATE_ARRAY.append(results[gen-1])
        elif statistic == "fitness-max":
          LOGBOOK = CHECKPOINT["log"]
          if "fitness" in LOGBOOK.chapters:
            results = LOGBOOK.chapters["fitness"].select("max")
          else:
            results = LOGBOOK.select("max")
          index = len(results)-1 if gen > len(results) else gen-1 # addresses bug for runs that were started with old logging and then resumed with new logging
          AGGREGATE_ARRAY.append(results[index])
        elif statistic in ["solutions", "qdscore"]:
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
          solution_count = 0
          qd_score = 0
          for x in range(len(fitness_grid)):
            for y in range(len(fitness_grid[x])):
              for z in range(len(fitness_grid[x][y])):
                if not math.isnan(fitness_grid[x][y][z]):
                  solution_count += 1
                  qd_score += fitness_grid[x][y][z][0]
          if statistic == "solutions":
            AGGREGATE_ARRAY.append(solution_count)
          else:
            AGGREGATE_ARRAY.append(qd_score)
        elif statistic == "swarm": # unique behaviours in swarm
          with open(CHECKPOINT_FILENAME, "rb") as cp_file:
            CHECKPOINT = pickle.load(cp_file)
          POPULATION = CHECKPOINT["pop"]
          swarm_sizes = []
          for individual in POPULATION:
            swarm_sizes.append(len(set(individual)))
          AGGREGATE_ARRAY.append(stat.mean(swarm_sizes))
        folder_count += 1
      else:
        print("Skipping run: " + CHECKPOINT_FILENAME + " is missing.")

    AGGREGATE_DICT[prefix] = AGGREGATE_ARRAY

  for env in ["nm", "e", "m", "d"]:
    for difficulty in ["e", "d"]:
      if variant == "ssga-dns":
        group_a = f"ssga-{difficulty}-{env}"
        group_b = f"dns-{difficulty}-{env}"
      elif variant == "ssga-nsslc":
        group_a = f"ssga-{difficulty}-{env}"
        group_b = f"nsslc-{difficulty}-{env}"      
      elif variant == "nsslc-dns":
        group_a = f"nsslc-{difficulty}-{env}"
        group_b = f"dns-{difficulty}-{env}"

      result = stats.ttest_ind(AGGREGATE_DICT[group_a], AGGREGATE_DICT[group_b])
      print(group_a + " vs. " + group_b)
      print("*****************")
      print(group_a + " values: " + str(AGGREGATE_DICT[group_a]) + ", mean = " + str(stat.mean(AGGREGATE_DICT[group_a])))
      print(group_b + " values: " + str(AGGREGATE_DICT[group_b]) + ", mean = " + str(stat.mean(AGGREGATE_DICT[group_b])))
      print("t-test result: p=" + str(result.pvalue) + " (" + ("SIGNIFICANT" if result.pvalue < 0.05 else "NOT SIGNIFICANT") + ")")
      print()
