from pyroborobo import Pyroborobo, CircleObject
import util.globals as globals

# Represents a sinkhole used in the Medium Level
class SinkholeObject(CircleObject):
  def __init__(self, id, data):
    CircleObject.__init__(self, id)
    lifetime_num = globals.config.get("pSimulationLifetime", "int")
    self.one_quarter = 0.25*lifetime_num*5
    self.half = 0.5*lifetime_num*5
    self.three_quarters = 0.75*lifetime_num*5
    self.hide()
    self.unregister()
    self.is_visible = False # Visibility status of sinkhole

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
