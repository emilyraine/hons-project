import util.globals as globals
import util.categorise as categorise

class MorphologyMonitor:

    def __init__(self):
        self.dogs = categorise.get_dogs()

    def get_morphological_complexity(self):
        # Find the first dog controller with a morphology attribute
        for base_controller in self.dogs:
            dog_controller = getattr(base_controller, "controller", None)
            if hasattr(dog_controller, "morphology"):
                morphology_params = dog_controller.morphology.normalise()
                speed = morphology_params['max_translation_speed']
                sensor_range = morphology_params['sensor_range']
                fov = morphology_params['sensor_fov']
                return speed + sensor_range + ((fov[0] + fov[1]) / 2)
        return 0