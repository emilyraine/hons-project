from pyroborobo import Pyroborobo, SquareObject
import util.globals as globals
from util.sys_helper import get_hpc_cpu_count

# Represents a dynamic block used in the Difficult Level
class BlockObject(SquareObject):
  def __init__(self, id, data):
    SquareObject.__init__(self, id)
    simulation_lifetime = globals.config.get("pSimulationLifetime", "int")
    population_size = globals.config.get("pPopulationSize", "int")
    evaluation_trials = globals.config.get("pEvaluationTrials", "int")
    # Calculate total steps for each simulation window, adjusting for parallelism (CPU count)
    total_steps_per_sim_square = int((population_size/get_hpc_cpu_count())*simulation_lifetime*evaluation_trials)
    self.one_quarter = int(0.25 * total_steps_per_sim_square)
    self.half = int(0.5 * total_steps_per_sim_square)
    self.three_quarters = int(0.75 * total_steps_per_sim_square)
    self.hide()
    self.unregister()
    self.my_id = id
    self.is_visible = False # Visibility status of block

  def appear(self):
    self.show()
    self.register()
    self.is_visible = True

  def step(self):
    current_time = Pyroborobo.get().iterations
    should_be_visible = ((self.one_quarter <= current_time < self.half) or (self.three_quarters <= current_time))
    if (should_be_visible and not self.is_visible):
      self.appear()
    elif (not should_be_visible and self.is_visible):
      self.disappear()

  def disappear(self):
    self.is_visible = False
    self.hide() 
    self.unregister()
