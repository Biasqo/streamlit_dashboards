import json

class FileWriter:

    def __init__(self):
        pass

    def write_to_json(self, path: str, data: json) -> None:
        with open(path, 'w+') as jsonFile:
            json.dump(data, jsonFile)