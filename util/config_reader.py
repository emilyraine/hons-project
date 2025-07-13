from configparser import ConfigParser

class ConfigReader:

  def __init__(self, config_filename):
    self.config_filename = config_filename
    self.config_parser = ConfigParser()
    with open(self.config_filename) as stream:
      self.config_parser.read_string("[root]\n" + stream.read())

  def get(self, parameter, type):
    value = self.config_parser.get("root", parameter)
    value = value.split("#")[0].strip()
    if type == "int":
      return int(value)
    elif type == "float":
      return float(value)
    elif type == "bool":
      return value == "true"
    elif type == "[str]":
      if len(value[1:-1].strip()) == 0:
        return []
      else:
        return list(map(lambda s: s.strip(), value[1:-1].split(",")))
    else:
      return str(value)

# Updates the in-memory config with dynamic changes
  def set(self, parameter, new_value):
    if (isinstance(new_value, bool)):
      value_string = "true" if new_value else "false"
    else:
      value_string = str(new_value)
    self.config_parser.set("root", parameter, value_string)