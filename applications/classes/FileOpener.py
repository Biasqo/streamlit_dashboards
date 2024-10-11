import json
import yaml
from yaml.loader import SafeLoader

class FileOpener:

    def __init__(self):
        pass

    def json_open(self, path) -> "json":
        with open(path, 'r') as f:
            return json.load(f)

    def sql_open(self, path) -> "sql":
        with open(path, 'r') as f:
            return f.read()

    def yaml_open(self, path) -> "yaml":
        with open(path, 'r') as f:
            return yaml.load(f, Loader=SafeLoader)

    def txt_open(self, path) -> list:
        with open(path, 'r') as f:
            return [line.rstrip() for line in f]