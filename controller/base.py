import multiprocessing
from pyroborobo import Pyroborobo, Controller
import util.globals as globals
from controller.dog import DogController
from controller.sheep import SheepController
import util.categorise as categorise
import util.calculate as calculate

class BaseController(Controller):

  def __init__(self, world_model):
    Controller.__init__(self, world_model) # mandatory call to super constructor
    self.target_switched = False
    if categorise.is_dog(self.get_id()):
      self.controller = DogController(self)
    else:
      self.controller = SheepController(self)
    
    simulation_lifetime = globals.config.get("pSimulationLifetime", "int")
    population_size = globals.config.get("pPopulationSize", "int")
    evaluation_trials = globals.config.get("pEvaluationTrials", "int")
    # Calculate total steps for each simulation window, adjusting for parallelism (CPU count)
    total_steps_per_sim_square = (population_size/multiprocessing.cpu_count())*simulation_lifetime*evaluation_trials
    self.half = 0.5 * total_steps_per_sim_square
    self.easy_bool = globals.config.get("pEasyLevel", "bool")

  def reset(self):
    self.controller.reset()

  def step(self):  # step is called at each time step
    globals.current_time = Pyroborobo.get().iterations
    if self.get_id() == 1:
      # For Easy Level: Target zone switches corners mid-simulation
      if (globals.current_time == self.half and self.easy_bool and self.target_switched == False):
        new_x = 491
        new_y = 488
        target_zone_radius = globals.config.get("pTargetZoneRadius", "int") + 2

        # Move sheep from the area where the target zone will appear
        for sheep in categorise.get_sheep():
          buffer = 8
          if (calculate.distance_between_points(sheep.absolute_position, (new_x, new_y)) <= (target_zone_radius + buffer)):
            sheep.set_position(460, 325) 

        globals.config.set("pTargetZoneCoordX", new_x)              # Set gathering pen x-coordinate (bottom-right corner)
        globals.config.set("pTargetZoneCoordY", new_y)              # Set gathering pen y-coordinate (bottom-right corner)
        globals.simulator.landmarks[0].set_coordinates(new_x,new_y)   # Update landmark to new coordinates
        globals.pen_behaviour_monitor.refresh()
        globals.fitness_monitor.refresh()
        for dog in categorise.get_dogs():
          dog.controller.refresh()
        self.target_switched = True

      globals.fitness_monitor.track()
      behaviour_features = globals.config.get("pBehaviourFeatures", "[str]")
      if "PEN" in behaviour_features:
        globals.pen_behaviour_monitor.track()
      if "DOG" in behaviour_features:
        globals.dog_behaviour_monitor.track()
      if "SHEEP" in behaviour_features:
        globals.sheep_behaviour_monitor.track()
    self.controller.step()
