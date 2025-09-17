from deap import base, creator, tools
from util.config_reader import ConfigReader
from util.result_logger import ResultLogger
import util.convert as convert
import util.evaluator as evaluator
import numpy as np
import time
import multiprocessing
import pickle
import random
import sys
import os
import util.mapelites as mapelites
import process.aggregate_archive as agga
import process.plot_solutions as plts
import process.plot_fitness as pltf
import process.plot_archive as plta
import process.plot_archives as pltb
import process.plot_qdscore as pltq
import process.calc_ttest as clct

# create fitness and individual objects
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

if __name__ == "__main__":

  try:

    # get command type flag
    COMMAND_FLAG = sys.argv[1]

    if COMMAND_FLAG not in ["-a", "-p"]:

      # load configuration and checkpoint files
      if COMMAND_FLAG == "-s":
        CHECKPOINT_FILENAME = None
        CHECKPOINT = None
        RUN_ID = sys.argv[3] if len(sys.argv) == 4 else str(int(time.time()))
        CONFIG_FILENAME = sys.argv[2]
        START_GENERATION = 1
      else:
        CHECKPOINT_FILENAME = sys.argv[2]
        with open(CHECKPOINT_FILENAME, "rb") as cp_file:
          CHECKPOINT = pickle.load(cp_file)
        RUN_ID = CHECKPOINT["rid"]
        CONFIG_FILENAME = CHECKPOINT["cfg"]
        START_GENERATION = CHECKPOINT["gen"] + 1
      CONFIG = ConfigReader(CONFIG_FILENAME)
    
      # get neural network dimensions (increased genome size for morphological parameter inclusion)
      NB_INPUTS = CONFIG.get("dInputNodes", "int")
      NB_HIDDENS = CONFIG.get("dHiddenNodes", "int")
      NB_OUTPUTS = CONFIG.get("dOutputNodes", "int")
      NEURAL_WEIGHTS_SIZE = (NB_INPUTS * NB_HIDDENS) + (NB_HIDDENS * NB_OUTPUTS)
      MORPHOLOGY_SIZE = 4
      GENOME_SIZE = NEURAL_WEIGHTS_SIZE + MORPHOLOGY_SIZE
      if CONFIG.get("pEvolutionAlgorithm", "str").startswith("A"):
        GENOME_SIZE = CONFIG.get("pNumberOfDogs", "int")
        ARCHIVE_FILENAME = CONFIG.get("pSolutionArchiveFilename", "str")
        with open(ARCHIVE_FILENAME, "rb") as ar_file:
          ARCHIVE = pickle.load(ar_file)
        CONTROLLERS = ARCHIVE["sol"]
      elif CONFIG.get("pEvolutionAlgorithm", "str").endswith("HET"):
        GENOME_SIZE = GENOME_SIZE * CONFIG.get("pNumberOfDogs", "int")

      # define genetic operators to use
      toolbox = base.Toolbox()
      if CONFIG.get("pEvolutionAlgorithm", "str").startswith("A"):
        toolbox.register("attribute", random.randint, a=0, b=len(CONTROLLERS)-1)
      else:
        # toolbox.register("attribute", random.uniform, a=-1, b=1)
        def init_individual(icls):
          weights = [random.uniform(-1, 1) for _ in range(NEURAL_WEIGHTS_SIZE)]
          morphology = [
            random.uniform(0, 1), # max_translation_speed
            random.uniform(0, 1), # sensor_range
            random.uniform(0, 1), # sensor_fov_left
            random.uniform(0, 1)  # sensor_fov_right
          ]
          return icls(weights + morphology)
      toolbox.register("individual", init_individual, creator.Individual)
      toolbox.register("population", tools.initRepeat, list, toolbox.individual)

      # toolbox.register("mate", tools.cxTwoPoint)
      # custom morphology crossover 
      def crossover_morphology(individual1, individual2):
        operation = random.choice(["exchange", "average"])
        i1 = int(random.uniform(NEURAL_WEIGHTS_SIZE, len(individual1) - 1))
        i2 = int(random.uniform(NEURAL_WEIGHTS_SIZE, len(individual2) - 1))
        if operation == "exchange":
          individual1[i1], individual2[i2] = individual2[i2], individual1[i1]
        elif operation == "average":
          avg = (individual1[i1] + individual2[i2]) / 2
          individual1[i1], individual2[i2] = avg, avg
        return individual1, individual2
        
      # neural weight crossover using DEAP  
      def crossover_weights(individual1, individual2):
        tools.cxTwoPoint(individual1, individual2)
        return individual1, individual2

      # combined crossover operator
      def crossover_individuals(individual1, individual2):
        crossover_weights(individual1[:NEURAL_WEIGHTS_SIZE], individual2[:NEURAL_WEIGHTS_SIZE])
        crossover_morphology(individual1, individual2)
        return individual1, individual2
      toolbox.register("mate", crossover_individuals)

      if CONFIG.get("pEvolutionAlgorithm", "str").startswith("A"):
        toolbox.register("mutate", tools.mutUniformInt, low=0, up=len(CONTROLLERS)-1, indpb=0.1)
      else:
        # neural weight mutation using DEAP
        def mutate_weights(individual):
          individual = tools.mutGaussian(individual[:NEURAL_WEIGHTS_SIZE], mu=0, sigma=1, indpb=0.05)
          return individual[0:NEURAL_WEIGHTS_SIZE]

        # custom morphology mutation
        def mutate_morphology(individual):
          i = int(random.uniform(NEURAL_WEIGHTS_SIZE, len(individual) - 1))
          individual[i] += random.gauss(0, 0.5)
          individual[i] = max(0, min(1, individual[i]))
          return individual[NEURAL_WEIGHTS_SIZE:]

        # combined mutation operator
        def mutate_individual(individual):
          mutate_weights(individual)
          mutate_morphology(individual) 
          return individual
        
        toolbox.register("mutate", mutate_individual)
      toolbox.register("select", tools.selTournament, tournsize=3)
      toolbox.register("evaluate", evaluator.execute)

      # define statistics to track
      stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
      stats_pen = tools.Statistics(lambda ind: ind.features[0])
      stats_dog = tools.Statistics(lambda ind: ind.features[1])
      stats_shp = tools.Statistics(lambda ind: ind.features[2])
      stats_mrph = tools.Statistics(lambda ind: ind.features[3])
      stats_cap = tools.Statistics(lambda ind: ind.features[4] if len(ind.features) > 4 else None)
      mstats = tools.MultiStatistics(fitness=stats_fit, pen=stats_pen, dog=stats_dog, sheep=stats_shp, morph=stats_mrph, capture=stats_cap)
      mstats.register("avg", np.mean)
      mstats.register("std", np.std)
      mstats.register("min", np.min)
      mstats.register("max", np.max)

    # start a new evolution simulation
    if COMMAND_FLAG == "-s":
      population         = toolbox.population(n=CONFIG.get("pPopulationSize", "int"))
      hall_of_fame       = tools.HallOfFame(maxsize=1)
      logbook            = tools.Logbook()
      if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M"):
        mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]")) 

    # resume a previous evolution simulation
    elif COMMAND_FLAG == "-r":
      population         = CHECKPOINT["pop"]
      hall_of_fame       = CHECKPOINT["hof"]
      logbook            = CHECKPOINT["log"]
      random.setstate(CHECKPOINT["rnd"])
      if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M"):
        mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]"), population)

    # export all statistic results from checkpoint
    elif COMMAND_FLAG == "-e":
      logbook = CHECKPOINT["log"]
      results_gen = logbook.select("gen")
      results_fit = logbook.chapters["fitness"].select("avg", "std", "min", "max")
      results_pen = logbook.chapters["pen"].select("avg", "std", "min", "max")
      results_dog = logbook.chapters["dog"].select("avg", "std", "min", "max")
      results_shp = logbook.chapters["sheep"].select("avg", "std", "min", "max")
      
      # check if morphology and capture data exists
      has_morph = "morph" in logbook.chapters
      has_capture = "capture" in logbook.chapters
      
      if has_morph:
          results_mrph = logbook.chapters["morph"].select("avg", "std", "min", "max")
      if has_capture:
          results_cap = logbook.chapters["capture"].select("avg", "std", "min", "max")
      # build headers list based on available data
      headers = [
          "gen", 
          "fit-avg", "fit-std", "fit-min", "fit-max", 
          "pen-avg", "pen-std", "pen-min", "pen-max", 
          "dog-avg", "dog-std", "dog-min", "dog-max", 
          "shp-avg", "shp-std", "shp-min", "shp-max"
      ]
      if has_morph:
          headers.extend(["mrph-avg", "mrph-std", "mrph-min", "mrph-max"])
      if has_capture:
          headers.extend(["cap-avg", "cap-std", "cap-min", "cap-max"])
      
      logger = ResultLogger(RUN_ID, "results", headers)
      
      for i in range(len(results_gen)):
          row = [
              results_gen[i],
              results_fit[0][i], results_fit[1][i], results_fit[2][i], results_fit[3][i],
              results_pen[0][i], results_pen[1][i], results_pen[2][i], results_pen[3][i],
              results_dog[0][i], results_dog[1][i], results_dog[2][i], results_dog[3][i],
              results_shp[0][i], results_shp[1][i], results_shp[2][i], results_shp[3][i]
          ]
          if has_morph:
              row.extend([results_mrph[0][i], results_mrph[1][i], results_mrph[2][i], results_mrph[3][i]])
          if has_capture:
              row.extend([
                  results_cap[0][i] if results_cap[0][i] is not None else 0,
                  results_cap[1][i] if results_cap[1][i] is not None else 0,
                  results_cap[2][i] if results_cap[2][i] is not None else 0,
                  results_cap[3][i] if results_cap[3][i] is not None else 0
              ])
          logger.append(row)
      print("Results exported.")
      exit(0)

    # aggregate archives from multiple runs into a swarm-map
    elif COMMAND_FLAG == "-a":
      AGGREGATE_PREFIX = sys.argv[2]
      AGGREGATE_GENERATION = sys.argv[3]
      agga.aggregate(AGGREGATE_PREFIX, AGGREGATE_GENERATION)
      exit(0)

    # plot results in figures
    elif COMMAND_FLAG == "-p":
      GRAPH_TYPE = sys.argv[2] # archive, fitness, solutions
      if GRAPH_TYPE == "archive":
        AGGREGATE_PREFIX = sys.argv[3]
        plta.graph(AGGREGATE_PREFIX)
      elif GRAPH_TYPE == "archives":
        pltb.graph()
      elif GRAPH_TYPE == "fitness":
        VARIANT_CODE = sys.argv[3]
        pltf.graph(VARIANT_CODE)
      elif GRAPH_TYPE == "solutions":
        VARIANT_CODE = sys.argv[3]
        plts.graph(VARIANT_CODE)
      elif GRAPH_TYPE == "qdscore":
        VARIANT_CODE = sys.argv[3]
        pltq.graph(VARIANT_CODE)
      elif GRAPH_TYPE == "ttest":
        VARIANT_CODE = sys.argv[3]
        STATISTIC_CODE = sys.argv[4]
        clct.calculate(VARIANT_CODE, STATISTIC_CODE)
      exit(0)

    # view simulation of elite individual from a checkpoint
    elif COMMAND_FLAG == "-v":
      TEMP_FILENAME = "config/temp.properties"
      with open(CHECKPOINT["cfg"], "r") as orig_file, open(TEMP_FILENAME, "w") as temp_file:
        for line in orig_file:
          if line.find("gBatchMode") >= 0:
            temp_file.write("gBatchMode = false\n")
          elif line.find("pEvaluationTrials") >= 0:
            temp_file.write("pEvaluationTrials = 1\n")
          else:
            temp_file.write(line)
      elite = CHECKPOINT["hof"].items[0]
      manager = multiprocessing.Manager()
      process_output = manager.dict()
      is_homogenous = CONFIG.get("pEvolutionAlgorithm", "str").endswith("HOM")
      is_allocation = CONFIG.get("pEvolutionAlgorithm", "str").startswith("A")
      process = evaluator.IndividualEvaluator(0, TEMP_FILENAME, CHECKPOINT["rid"], 1, [elite], process_output, is_homogenous, is_allocation)
      process.start()
      process.join()
      print(end='\x1b[2K') # clear line
      print("Fitness: " + str(process_output[0][0][0]))
      os.remove(TEMP_FILENAME)
      exit(0)

  except SystemExit:
    exit(0)

  except Exception as e:
    print("*" * 10, "Error Message", "*" * 10)
    print(e)
    print("*" * 10, "Usage Instructions", "*" * 10)
    print("Start Evolution:\tpython run.py -s <config file> <run id>")
    print("Resume Evolution:\tpython run.py -r <checkpoint file>")
    print("Export Results:\t\tpython run.py -e <checkpoint file>")
    print("Aggregate Archives:\tpython run.py -a <aggregate prefix> <generation>")
    print("Plot Figures:\t\tpython run.py -p <graph type> [variant options]")
    print("View Simulation:\tpython run.py -v <checkpoint file>")
    exit(1)

  # run all generation simulations
  NB_GENERATIONS = CONFIG.get("pSimulationGenerations", "int")
  for generation in range(START_GENERATION, NB_GENERATIONS + 1):

    # start generation
    generation_start = time.time()
    print("*" * 10, generation, "*" * 10)
    if CONFIG.get("pDynamicProgressOutput", "bool"):
      print("Starting...", end="\r", flush=True)

    # select the next generation individuals
    if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M") and generation != 1:
      offspring = toolbox.select(mapelites.grid, CONFIG.get("pPopulationSize", "int"))
    else:
      offspring = toolbox.select(population, CONFIG.get("pPopulationSize", "int"))

    # clone the selected individuals
    offspring = list(map(toolbox.clone, offspring))

    # apply crossover on the offspring
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
      if random.random() < CONFIG.get("pCrossoverProbability", "float"):
        toolbox.mate(child1, child2)
        del child1.fitness.values
        del child2.fitness.values

    # apply mutation on the offspring
    for mutant in offspring:
      if random.random() < CONFIG.get("pMutationProbability", "float"):#im doing a mutation probability in the morphology mutation operator too so change that if results r looking
        toolbox.mutate(mutant)
        del mutant.fitness.values

    # evaluate all individuals
    fitnesses = toolbox.evaluate(offspring, CONFIG_FILENAME, RUN_ID, NB_GENERATIONS, START_GENERATION, generation)
    for ind, fit in zip(offspring, fitnesses):
      if isinstance(fit, tuple) and len(fit) == 2:
        ind.fitness.values = fit[0]
        ind.features = fit[1]
      else:
        ind.fitness.values = fit
        ind.features = None

    # update the MAP-Elites grid or replace population with offspring
    if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M"):
      mapelites.grid.update(offspring)
    else:
      population[:] = offspring

    # record stats
    if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M"):
      hall_of_fame.update(mapelites.grid)
      record = mstats.compile(mapelites.grid)
    else:
      hall_of_fame.update(population)
      record = mstats.compile(population)
    logbook.record(gen=generation, **record)
    if CONFIG.get("pDynamicProgressOutput", "bool"):
      print(end='\x1b[2K') # clear line
    print("Average Fitness: " + str(record["fitness"]["avg"]))
    print("Maximum Fitness: " + str(record["fitness"]["max"]))
    print("Average Pen Distance: " + str(record["pen"]["avg"]))
    print("Maximum Pen Distance: " + str(record["pen"]["max"]))
    print("Average Dog Distance: " + str(record["dog"]["avg"]))
    print("Maximum Dog Distance: " + str(record["dog"]["max"]))
    print("Average Sheep Distance: " + str(record["sheep"]["avg"]))
    print("Maximum Sheep Distance: " + str(record["sheep"]["max"]))
    if "morph" in record and record["morph"]["avg"] is not None:
      print("Average Morphological Complexity: " + str(record["morph"]["avg"]))
      print("Maximum Morphological Complexity: " + str(record["morph"]["max"]))
    # Add capture ratio output if available
    if "capture" in record and record["capture"]["avg"] is not None:
      print("Average Sheep Capture Ratio: " + str(record["capture"]["avg"]))
      print("Maximum Sheep Capture Ratio: " + str(record["capture"]["max"]))

    # save checkpoint
    if generation % CONFIG.get("pCheckpointInterval", "int") == 0:
      cp = dict(
        rid=RUN_ID,
        pop=(mapelites.grid if CONFIG.get("pEvolutionAlgorithm", "str").startswith("M") else population), 
        gen=generation, 
        hof=hall_of_fame, 
        log=logbook,
        rnd=random.getstate(), 
        cfg=CONFIG_FILENAME
      )
      cp_dir = "./output/run_" + RUN_ID + "/checkpoints"
      if not os.path.exists(cp_dir):
        os.makedirs(cp_dir)
      with open(cp_dir + "/gen_" + str(generation) + ".pkl", "wb") as cp_file:
        pickle.dump(cp, cp_file)

    # end generation
    print("Elapsed Time: " + convert.seconds_to_readable_duration(time.time() - generation_start))