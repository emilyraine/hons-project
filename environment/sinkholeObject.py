from pyroborobo import Pyroborobo, CircleObject
import util.globals as globals

# Represents a sinkhole used in the Medium Level
class SinkholeObject(CircleObject):
  def __init__(self, id, data):
    CircleObject.__init__(self, id)
    simulation_lifetime = globals.config.get("pSimulationLifetime", "int")
    population_size = globals.config.get("pPopulationSize", "int")
    evaluation_trials = globals.config.get("pEvaluationTrials", "int")
    total_steps_per_sim_square = (population_size/4)*simulation_lifetime*evaluation_trials
    self.one_quarter = 0.25 * total_steps_per_sim_square
    self.half = 0.5 * total_steps_per_sim_square
    self.three_quarters = 0.75 * total_steps_per_sim_square
    self.hide()
    self.unregister()
    self.is_visible = False # Visibility status of sinkhole
    self.my_id = id
    self.x = globals.config.get(f"physicalObject[{self.my_id}].x", "int")             # x-coordinate of centre of sinkhole
    self.y = globals.config.get(f"physicalObject[{self.my_id}].y", "int")             # y-coordinate of centre of sinkhole
    self.radius = globals.config.get(f"physicalObject[{self.my_id}].radius", "int")   # radius of sinkhole
    self.number_of_robots = globals.config.get("gInitialNumberOfRobots", "int")

  def appear(self):
      self.show()
      self.register()
      self.is_visible = True
      simulator = Pyroborobo.get()
      for robot_id in range(self.number_of_robots):
        base_controller = simulator.controllers[robot_id]
        inner_controller = base_controller.controller  # Dog or Sheep controller
        robot_x = inner_controller.agent.absolute_position[0]
        robot_y = inner_controller.agent.absolute_position[1]
        distance_x = robot_x - self.x
        distance_y = robot_y - self.y
        if ((distance_x * distance_x + distance_y * distance_y) <= (self.radius * self.radius)):
          self.is_walked(robot_id)

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

  def is_walked(self, robot_id):
      simulator = Pyroborobo.get()
      base_controller = simulator.controllers[robot_id]
      inner_controller = base_controller.controller  # Dog or Sheep controller
      inner_controller.remove()
