import util.calculate as calculate
import util.categorise as categorise
import util.globals as globals

class IndividualFitnessMonitor:

  def __init__(self, method):
    if method == "REGCNT":
      self.monitor = RegularCountFitnessMonitor()
    elif method == "SUPCNT":
      self.monitor = SuperCountFitnessMonitor()
    elif method == "SUPDST":
      self.monitor = SuperDistanceFitnessMonitor()
    else:
      raise Exception("Unsupported method code for measuring individual fitness")

  def report(self):
    print("*" * 10, "Individual Fitness Report", "*" * 10)
    self.monitor.report()

  def score(self, dog):
    return self.monitor.score(dog)

  def avg_score(self):
    return self.monitor.avg_score()

  def track(self, sheep):
    self.monitor.track(sheep)

  def reset(self):
    self.monitor.reset()


class RegularCountFitnessMonitor:

  def __init__(self):
    self.dogs = categorise.get_dogs()
    self.target_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
    self.target_radius = globals.config.get("pTargetZoneRadius", "int")
    self.avoidance_radius = globals.config.get("sDogAvoidanceRadius", "float")
    self.tracking = {}
    self.history = {}
    self.morph_complexity_history = {}
    self.p_max = 1
    self.n_max = 1

  def report(self):
    for dog in self.dogs:
      if dog.id in self.history:
        history = self.history[dog.id]
      else:
        history = {'p': 0, 'n': 0}
      #calculate and record morphological complexity
      morph_complexity = self.get_morphological_complexity(dog)
      if dog.id not in self.morph_complexity_history:
        self.morph_complexity_history[dog.id] = []
      self.morph_complexity_history[dog.id].append(morph_complexity)
      print("Dog #" + str(dog.id) + ": History = " + str(history) + ", Fitness = " + str(self.score(dog)) + ", Morphological Complexity = " + str(morph_complexity))
    for dog_id, values in self.morph_complexity_history.items():
      print(f"Dog #{dog_id}: {values}")

#p: number of positive movements(towards target zone)
#n: number of negative movements(away from target zone)
  def score(self, dog):
    if dog.id in self.history:
      p = self.history[dog.id]["p"]
      n = self.history[dog.id]["n"]
      # Fi = (1 + P / Pmax - N / Nmax) / 2
      behaviour_fitness = (1 + (p / self.p_max) - (n / self.n_max)) / 2
    else:
      behaviour_fitness = 0.5
    morphology_params = dog.morphology.normalise()
    speed = morphology_params['max_translation_speed']
    sensor_range = morphology_params['sensor_range']
    fov = morphology_params['sensor_fov']
    #energy usage implemented in dog controller, penalty: dogs stop moving
    morphological_fitness = ( speed + sensor_range + abs(fov[0]) + fov[1] )/ 4

    return (behaviour_fitness + morphological_fitness) / 2

  def get_morphological_complexity(self, dog, w_speed=1.0, w_range=1.0, w_fov=1.0):
    morphology_params = dog.morphology.normalise()
    speed = morphology_params['max_translation_speed']
    sensor_range = morphology_params['sensor_range']
    fov = morphology_params['sensor_fov']
    return w_speed * speed + w_range * sensor_range + w_fov * ((fov[0] + fov[1]) / 2)
    
  def avg_score(self):
    total_fitness = 0
    for dog in self.dogs:
      total_fitness += self.score(dog)
    return total_fitness / len(self.dogs)

  def track(self, sheep):
    for dog in self.dogs:
      trackable = calculate.distance_between_points(sheep.absolute_position, dog.absolute_position) <= self.avoidance_radius
      if sheep.id in self.tracking and dog.id in self.tracking[sheep.id]:
        if trackable:
          self.update_tracking(dog.id, sheep.id, sheep.absolute_position)
        else:
          self.end_tracking(dog.id, sheep.id)
      elif trackable:
        self.start_tracking(dog.id, sheep.id, sheep.absolute_position)

  def start_tracking(self, dog_id, sheep_id, start_coords):
    data = {"start": start_coords, "last": start_coords}
    if sheep_id in self.tracking:
      self.tracking[sheep_id][dog_id] = data
    else:
      self.tracking[sheep_id] = {dog_id: data}

  def update_tracking(self, dog_id, sheep_id, current_coords):
    if sheep_id in self.tracking and dog_id in self.tracking[sheep_id]:
      self.tracking[sheep_id][dog_id]["last"] = current_coords

  def end_tracking(self, dog_id, sheep_id):
    if sheep_id in self.tracking and dog_id in self.tracking[sheep_id]:
      start_coords = self.tracking[sheep_id][dog_id]["start"]
      end_coords = self.tracking[sheep_id][dog_id]["last"]
      start_dist = calculate.distance_from_target_zone(start_coords, self.target_coords, self.target_radius)
      end_dist = calculate.distance_from_target_zone(end_coords, self.target_coords, self.target_radius)
      if start_dist > end_dist:
        self.record_positive_movement(dog_id)
      elif end_dist > start_dist:
        self.record_negative_movement(dog_id)
      del self.tracking[sheep_id][dog_id]
      if len(self.tracking[sheep_id]) == 0:
        del self.tracking[sheep_id]

  def record_positive_movement(self, dog_id):
    if dog_id in self.history:
      self.history[dog_id]["p"] += 1
    else:
      self.history[dog_id] = {"p": 1, "n": 0}
    self.p_max = max(self.p_max, self.history[dog_id]["p"])

  def record_negative_movement(self, dog_id):
    if dog_id in self.history:
      self.history[dog_id]["n"] += 1
    else:
      self.history[dog_id] = {"p": 0, "n": 1}
    self.n_max = max(self.n_max, self.history[dog_id]["n"])

  def reset(self):
    self.tracking = {}
    self.history = {}
    self.p_max = 1
    self.n_max = 1


class SuperCountFitnessMonitor:

  def __init__(self):
    self.dogs = categorise.get_dogs()
    self.target_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
    self.target_radius = globals.config.get("pTargetZoneRadius", "int")
    self.avoidance_radius = globals.config.get("sDogAvoidanceRadius", "float")
    self.tracking = {}
    self.history = {}
    self.c_p = 10
    self.c_n = 10
    self.p_max = 1
    self.n_max = 1

  def report(self):
    for dog in self.dogs:
      if dog.id in self.history:
        history = self.history[dog.id]
      else:
        history = {'p_0': 0, 'p_s': 0, 'n_0': 0, 'n_s': 0}
      print("Dog #" + str(dog.id) + ": History = " + str(history) + ", Fitness = " + str(self.score(dog)))

  def score(self, dog):
    if dog.id in self.history:
      p_0 = self.history[dog.id]["p_0"]
      p_s = self.history[dog.id]["p_s"]
      n_0 = self.history[dog.id]["n_0"]
      n_s = self.history[dog.id]["n_s"]
      # Fi = (1 + (P0 + CP * P+) / Pmax - (N0 + CN * N+) / Nmax) / 2
      return (1 + ((p_0 + self.c_p * p_s) / self.p_max) - ((n_0 + self.c_n * n_s) / self.n_max)) / 2
    else:
      return 0.5

  def avg_score(self):
    total_fitness = 0
    for dog in self.dogs:
      total_fitness += self.score(dog)
    return total_fitness / len(self.dogs)

  def track(self, sheep):
    for dog in self.dogs:
      trackable = calculate.distance_between_points(sheep.absolute_position, dog.absolute_position) <= self.avoidance_radius
      if sheep.id in self.tracking and dog.id in self.tracking[sheep.id]:
        if trackable:
          self.update_tracking(dog.id, sheep.id, sheep.absolute_position)
        else:
          self.end_tracking(dog.id, sheep.id)
      elif trackable:
        self.start_tracking(dog.id, sheep.id, sheep.absolute_position)

  def start_tracking(self, dog_id, sheep_id, start_coords):
    data = {"start": start_coords, "last": start_coords}
    if sheep_id in self.tracking:
      self.tracking[sheep_id][dog_id] = data
    else:
      self.tracking[sheep_id] = {dog_id: data}

  def update_tracking(self, dog_id, sheep_id, current_coords):
    if sheep_id in self.tracking and dog_id in self.tracking[sheep_id]:
      self.tracking[sheep_id][dog_id]["last"] = current_coords

  def end_tracking(self, dog_id, sheep_id):
    if sheep_id in self.tracking and dog_id in self.tracking[sheep_id]:
      start_coords = self.tracking[sheep_id][dog_id]["start"]
      end_coords = self.tracking[sheep_id][dog_id]["last"]
      start_dist = calculate.distance_from_target_zone(start_coords, self.target_coords, self.target_radius)
      end_dist = calculate.distance_from_target_zone(end_coords, self.target_coords, self.target_radius)
      if start_dist > end_dist:
        if end_dist != 0:
          self.record_regular_positive_movement(dog_id)
        elif end_dist == 0:
          self.record_super_positive_movement(dog_id)
      elif end_dist > start_dist:
        if start_dist != 0:
          self.record_regular_negative_movement(dog_id)
        elif start_dist == 0:
          self.record_super_negative_movement(dog_id)
      del self.tracking[sheep_id][dog_id]
      if len(self.tracking[sheep_id]) == 0:
        del self.tracking[sheep_id]

  def record_regular_positive_movement(self, dog_id):
    if dog_id in self.history:
      self.history[dog_id]["p_0"] += 1
    else:
      self.history[dog_id] = {"p_0": 1, "p_s": 0, "n_0": 0, "n_s": 0}
    p = self.history[dog_id]["p_0"] + self.c_p * self.history[dog_id]["p_s"]
    self.p_max = max(self.p_max, p)

  def record_super_positive_movement(self, dog_id):
    if dog_id in self.history:
      self.history[dog_id]["p_s"] += 1
    else:
      self.history[dog_id] = {"p_0": 0, "p_s": 1, "n_0": 0, "n_s": 0}
    p = self.history[dog_id]["p_0"] + self.c_p * self.history[dog_id]["p_s"]
    self.p_max = max(self.p_max, p)

  def record_regular_negative_movement(self, dog_id):
    if dog_id in self.history:
      self.history[dog_id]["n_0"] += 1
    else:
      self.history[dog_id] = {"p_0": 0, "p_s": 0, "n_0": 1, "n_s": 0}
    n = self.history[dog_id]["n_0"] + self.c_n * self.history[dog_id]["n_s"]
    self.n_max = max(self.n_max, n)

  def record_super_negative_movement(self, dog_id):
    if dog_id in self.history:
      self.history[dog_id]["n_s"] += 1
    else:
      self.history[dog_id] = {"p_0": 0, "p_s": 0, "n_0": 0, "n_s": 1}
    n = self.history[dog_id]["n_0"] + self.c_n * self.history[dog_id]["n_s"]
    self.n_max = max(self.n_max, n)

  def reset(self):
    self.tracking = {}
    self.history = {}
    self.p_max = 1
    self.n_max = 1


class SuperDistanceFitnessMonitor:

  def __init__(self):
    self.dogs = categorise.get_dogs()
    self.target_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
    self.target_radius = globals.config.get("pTargetZoneRadius", "int")
    self.avoidance_radius = globals.config.get("sDogAvoidanceRadius", "float")
    self.tracking = {}
    self.history = {}
    self.c_p = 100
    self.c_n = 100
    self.p_max = 0.00000001
    self.n_max = 0.00000001

  def report(self):
    p_total = 0
    n_total = 0
    for dog in self.dogs:
      if dog.id in self.history:
        history = self.history[dog.id]
      else:
        history = {'p_0': 0, 'p_s': 0, 'n_0': 0, 'n_s': 0}
      p_total += history['p_0']
      n_total += history['n_0']
      print("Dog #" + str(dog.id) + ": History = " + str(history) + ", Fitness = " + str(self.score(dog)))
    print("Total positive distance = " + str(p_total))
    print("Total negative distance = " + str(n_total))

  def score(self, dog):
    if dog.id in self.history:
      p_0 = self.history[dog.id]["p_0"]
      p_s = self.history[dog.id]["p_s"]
      n_0 = self.history[dog.id]["n_0"]
      n_s = self.history[dog.id]["n_s"]
      # Fi = (1 + sum(Pi) / Pmax - sum(Ni) / Nmax) / 2
      return (1 + ((p_0 + self.c_p * p_s) / self.p_max) - ((n_0 + self.c_n * n_s) / self.n_max)) / 2
    else:
      return 0.5

  def avg_score(self):
    total_fitness = 0
    for dog in self.dogs:
      total_fitness += self.score(dog)
    return total_fitness / len(self.dogs)

  def track(self, sheep):
    for dog in self.dogs:
      trackable = calculate.distance_between_points(sheep.absolute_position, dog.absolute_position) <= self.avoidance_radius
      if sheep.id in self.tracking and dog.id in self.tracking[sheep.id]:
        if trackable:
          self.update_tracking(dog.id, sheep.id, sheep.absolute_position)
        else:
          self.end_tracking(dog.id, sheep.id)
      elif trackable:
        self.start_tracking(dog.id, sheep.id, sheep.absolute_position)

  def start_tracking(self, dog_id, sheep_id, start_coords):
    data = {"start": start_coords, "last": start_coords}
    if sheep_id in self.tracking:
      self.tracking[sheep_id][dog_id] = data
    else:
      self.tracking[sheep_id] = {dog_id: data}

  def update_tracking(self, dog_id, sheep_id, current_coords):
    if sheep_id in self.tracking and dog_id in self.tracking[sheep_id]:
      self.tracking[sheep_id][dog_id]["last"] = current_coords

  def end_tracking(self, dog_id, sheep_id):
    if sheep_id in self.tracking and dog_id in self.tracking[sheep_id]:
      start_coords = self.tracking[sheep_id][dog_id]["start"]
      end_coords = self.tracking[sheep_id][dog_id]["last"]
      start_dist = calculate.distance_from_target_zone(start_coords, self.target_coords, self.target_radius)
      end_dist = calculate.distance_from_target_zone(end_coords, self.target_coords, self.target_radius)
      diff_dist = abs(start_dist - end_dist)
      if start_dist > end_dist:
        if end_dist != 0:
          self.record_regular_positive_movement(dog_id, diff_dist)
        elif end_dist == 0:
          self.record_super_positive_movement(dog_id, diff_dist)
      elif end_dist > start_dist:
        if start_dist != 0:
          self.record_regular_negative_movement(dog_id, diff_dist)
        elif start_dist == 0:
          self.record_super_negative_movement(dog_id, diff_dist)
      del self.tracking[sheep_id][dog_id]
      if len(self.tracking[sheep_id]) == 0:
        del self.tracking[sheep_id]

  def record_regular_positive_movement(self, dog_id, distance):
    if dog_id in self.history:
      self.history[dog_id]["p_0"] += distance
    else:
      self.history[dog_id] = {"p_0": distance, "p_s": 0, "n_0": 0, "n_s": 0}
    p = self.history[dog_id]["p_0"] + self.c_p * self.history[dog_id]["p_s"]
    self.p_max = max(self.p_max, p)

  def record_super_positive_movement(self, dog_id, distance):
    if dog_id in self.history:
      self.history[dog_id]["p_0"] += distance
      self.history[dog_id]["p_s"] += distance
    else:
      self.history[dog_id] = {"p_0": distance, "p_s": 1, "n_0": 0, "n_s": 0}
    p = self.history[dog_id]["p_0"] + self.c_p * self.history[dog_id]["p_s"]
    self.p_max = max(self.p_max, p)

  def record_regular_negative_movement(self, dog_id, distance):
    if dog_id in self.history:
      self.history[dog_id]["n_0"] += distance
    else:
      self.history[dog_id] = {"p_0": 0, "p_s": 0, "n_0": distance, "n_s": 0}
    n = self.history[dog_id]["n_0"] + self.c_n * self.history[dog_id]["n_s"]
    self.n_max = max(self.n_max, n)

  def record_super_negative_movement(self, dog_id, distance):
    if dog_id in self.history:
      self.history[dog_id]["n_0"] += distance
      self.history[dog_id]["n_s"] += 1
    else:
      self.history[dog_id] = {"p_0": 0, "p_s": 0, "n_0": distance, "n_s": 1}
    n = self.history[dog_id]["n_0"] + self.c_n * self.history[dog_id]["n_s"]
    self.n_max = max(self.n_max, n)

  def reset(self):
    self.tracking = {}
    self.history = {}
    self.p_max = 0.00000001
    self.n_max = 0.00000001


# TODO: Consider sheep start trajectory and end trajectory (facing in direction towards target zone centre is better than facing away or tangential)