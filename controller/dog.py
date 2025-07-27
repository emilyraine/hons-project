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
    self.morphology = DogMorphology()
    self.sensor_range = self.morphology.sensor_range
    self.sensor_fov = self.morphology.sensor_fov
    self.dog_sensor = RadarSensor(self.agent, "dog", self.sensor_range, self.sensor_fov)
    self.sheep_sensor = RadarSensor(self.agent, "sheep", self.sensor_range, self.sensor_fov)
    self.wall_sensor = RadarSensor(self.agent, "wall", self.sensor_range, self.sensor_fov)
    self.network = NeuralNetwork(globals.config.get("dInputNodes", "int"), globals.config.get("dHiddenNodes", "int"), globals.config.get("dOutputNodes", "int"))
    self.genome = None
    self.max_target_distance = calculate.max_distance_from_target_zone(self.target_coords, self.target_radius, self.arena_width, self.arena_height)

    #Load environment image once for all dogs
    if not hasattr(DogController, "env_img"):
        env_img_path = globals.config.get("gEnvironmentImageFilename", "str")
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

    #Get agent position in image coordinates
    x, y = int(self.agent.absolute_position[0]), int(self.agent.absolute_position[1])
    x = max(0, min(x, DogController.env_img_width - 1))
    y = max(0, min(y, DogController.env_img_height - 1))
    pixel = DogController.env_img.getpixel((x, y))
    on_ice = pixel == DogController.ICE_RGB
    on_mud = pixel == DogController.MUD_RGB

    translation = output[0,0] * self.morphology.max_translation_speed
    rotation = output[0,1]

    if on_ice:
        #add random slip to rotation and reduce speed
        ice_factor = 0.25
        translation *= ice_factor
        slip_angle = random.uniform(-0.25, 0.25)
        rotation += slip_angle
    elif on_mud:
        #reduce speed only
        mud_factor = 0.5
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
    neural_weights = genome[:-4]
    morphology_params = genome[-4:]
    self.morphology = DogMorphology.denormalise_from_genome(morphology_params)
    self.network.set_weights(neural_weights)


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

class DogMorphology:

    def __init__(self, max_translation_speed=None, sensor_range=None, sensor_fov=None):
        if max_translation_speed is None and sensor_range is None and sensor_fov is None:
            self.sensor_fov = (globals.config.get("dSensorLeftFOV", "int"), globals.config.get("dSensorRightFOV", "int"))
            self.sensor_range = globals.config.get("dSensorRange", "int")
            self.max_translation_speed = globals.config.get("dMaxTranslationSpeed", "float")
        else:
            self.max_translation_speed = max_translation_speed
            self.sensor_range = sensor_range
            self.sensor_fov = sensor_fov

    @staticmethod
    def denormalise_from_genome(genome_segment):
        return DogMorphology(
            max_translation_speed=genome_segment[0],
            sensor_range=genome_segment[1] * 100,
            sensor_fov=(int(genome_segment[2] * -180), int(genome_segment[3] * 180))
        )

    def normalise(self):
        return {
            'max_translation_speed': self.max_translation_speed,
            'sensor_range': float(self.sensor_range / 100),
            'sensor_fov': (float(self.sensor_fov[0] / -180), float(self.sensor_fov[1] / 180))
        }
