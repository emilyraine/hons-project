import torch
import util.calculate as calculate
import numpy as np
import util.globals as globals
from controller.radar import RadarSensor
from torch import nn
from PIL import Image
import random

torch.manual_seed(0) # ensure bias is consistent


class DogController:

  def __init__(self, agent):
    self.agent = agent
    self.agent.set_color(*[255, 0, 0])
    self.target_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
    self.target_radius = globals.config.get("pTargetZoneRadius", "int")
    self.arena_width = globals.config.get("gArenaWidth", "int")
    self.arena_height = globals.config.get("gArenaHeight", "int")
    self.sensor_fov = (globals.config.get("dSensorLeftFOV", "int"), globals.config.get("dSensorRightFOV", "int"))
    self.sensor_range = globals.config.get("dSensorRange", "int")
    self.dog_sensor = RadarSensor(self.agent, "dog", self.sensor_range, self.sensor_fov)
    self.sheep_sensor = RadarSensor(self.agent, "sheep", self.sensor_range, self.sensor_fov)
    self.wall_sensor = RadarSensor(self.agent, "wall", self.sensor_range, self.sensor_fov)
    self.network = NeuralNetwork(globals.config.get("dInputNodes", "int"), globals.config.get("dHiddenNodes", "int"), globals.config.get("dOutputNodes", "int"))
    self.genome = None
    self.max_target_distance = calculate.max_distance_from_target_zone(self.target_coords, self.target_radius, self.arena_width, self.arena_height)

    #Load environment image once for all dogs
    if not hasattr(DogController, "env_img"):
        env_img_path = globals.config.get("gForegroundImageFilename", "str")
        DogController.env_img = Image.open(env_img_path).convert("RGB")
        DogController.env_img_width, DogController.env_img_height = DogController.env_img.size
    #Ice and mud RGB values (used to detect if dog is on ice/mud pixel)
    DogController.ICE_RGB = (50, 130, 246)
    DogController.MUD_RGB = (120, 67, 21)

  def reset(self):
    pass

  def step(self):
    if globals.config.get("pSwarmFitnessAlgorithm", "str") == "MINGLE":
      globals.ds_interaction_monitor.track(self.agent)
    input = torch.FloatTensor(self.get_inputs().reshape((1, globals.config.get("dInputNodes", "int"))))
    output = self.network(input)
    max_translation_speed = globals.config.get("dMaxTranslationSpeed", "float")

    #check if ice or mud pixel
    x, y = int(self.agent.absolute_position[0]), int(self.agent.absolute_position[1])
    x = max(0, min(x, DogController.env_img_width - 1))
    y = max(0, min(y, DogController.env_img_height - 1))
    pixel = DogController.env_img.getpixel((x, y))
    on_ice = pixel == DogController.ICE_RGB
    on_mud = pixel == DogController.MUD_RGB

    translation = output[0,0] * max_translation_speed
    rotation = output[0,1]

    if on_ice:
        #add slip(rotation) and reduce speed
        ice_factor = 0.75
        translation *= ice_factor
        if random.random() < globals.config.get("pIceSlipProbability", "float"):
          slip_angle = globals.config.get("pIceSlipAngle", "float")
          rotation += slip_angle
    elif on_mud:
        #reduce speed only
        mud_factor = 0.60
        translation *= mud_factor

    rotation = max(-1.0, min(1.0, rotation))
    self.agent.set_translation(translation)
    self.agent.set_rotation(rotation)

  def get_inputs(self):
    # distance inputs are normalised between 0 and 1 (where 0 is undetected and 1 is as close as possible)
    # angle inputs are normalised between -1 and 1 (where -1 is -180 degrees and 1 is 180 degrees)
    bias = [1]
    wall_detection = self.wall_sensor.detect()
    dog_detection = self.dog_sensor.detect()
    sheep_detection = self.sheep_sensor.detect()
    landmark_distance = 1 - (calculate.distance_from_target_zone(self.agent.absolute_position, self.target_coords, self.target_radius) / self.max_target_distance)
    landmark_angle = self.agent.get_closest_landmark_orientation()
    landmark_detection = [landmark_distance, landmark_angle]
    return np.concatenate((bias, wall_detection, dog_detection, sheep_detection, landmark_detection))

  def set_genome(self, genome):
    self.genome = genome
    self.network.set_weights(genome)


class NeuralNetwork(nn.Module):
  
  def __init__(self, nb_inputs, nb_hiddens, nb_outputs):
    super(NeuralNetwork, self).__init__()
    self.nb_inputs = nb_inputs
    self.nb_hiddens = nb_hiddens
    self.nb_outputs = nb_outputs
    self.flatten = nn.Flatten()
    self.network = nn.Sequential(
      nn.Linear(nb_inputs, nb_hiddens),
      nn.Tanh(),
      nn.Linear(nb_hiddens, nb_outputs),
      nn.Tanh(),
    )

  def forward(self, input):
    input = self.flatten(input)
    return self.network(input)

  def set_weights(self, weights):
    with torch.no_grad():
      for hidden_node in range(self.nb_hiddens):
        start_idx = hidden_node * self.nb_inputs
        end_idx = start_idx + self.nb_inputs
        self.network[0].weight[hidden_node] = nn.Parameter(torch.FloatTensor(weights[start_idx:end_idx]))
      for output_node in range(self.nb_outputs):
        start_idx = (self.nb_inputs * self.nb_hiddens) + output_node * self.nb_hiddens
        end_idx = start_idx + self.nb_hiddens
        self.network[2].weight[output_node] = nn.Parameter(torch.FloatTensor(weights[start_idx:end_idx]))
